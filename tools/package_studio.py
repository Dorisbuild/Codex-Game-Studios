#!/usr/bin/env python3
"""Export a validated, standalone project without Git history or local state."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re
import sys
import tomllib
import zipfile
from verify_codex_studio import Verifier

# If a maintainer intentionally adds a ``samples/`` tree later, package it as
# an optional top-level sample. The current framework checkout contains no game;
# keeping this boundary explicit prevents sample runtime files from being
# mixed into the shared ``src``/``production`` trees.
DIRECTORIES = {'.agents', '.codex', '.github', 'samples', 'design', 'docs', 'production', 'src',
               'tools', 'tests', 'Codex Skill Testing Framework'}
FILES = {'AGENTS.md', 'README.md', 'LICENSE', 'NOTICE.md', 'CONTRIBUTING.md',
         'SECURITY.md', 'project.yaml', 'codex-studio.toml', 'requirements-dev.txt',
         '.gitattributes', '.gitignore', 'VERIFICATION.txt'}
# Keep editor/import caches out of a release even when an optional game sample
# was opened locally before packaging. Names are compared case-insensitively.
EXCLUDED_PARTS = {'.git', '.scratch', '__pycache__', '.pytest_cache', 'node_modules',
                  'session-state', 'session-logs', 'results', 'dist', '.env',
                  '.backups', 'backups', '.godot', 'library', 'temp', 'logs',
                  'obj', 'bin', 'build', 'builds', 'exports'}
EXCLUDED_NAMES = {'project.local.yaml', 'config.local.toml', 'agents.override.md',
                 'credentials.json', 'secrets.json', 'auth.json'}
EXCLUDED_PREFIXES = {('tests', 'sandboxes')}
EXCLUDED_SUFFIXES = {'.pyc', '.log', '.key', '.pem', '.tmp', '.temp', '.swp', '.swo',
                    '.bak', '.backup'}
ARCHIVE_SUFFIXES = ('.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz',
                    '.txz', '.rar', '.7z')
BACKUP_NAME = re.compile(r'(?:^|[._ -])(?:backup|snapshot)s?(?:[._ -]|$)')


def export_files(root):
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if rel.parts[0] not in DIRECTORIES and rel.as_posix() not in FILES:
            continue
        parts = tuple(part.casefold() for part in rel.parts)
        if any(part in EXCLUDED_PARTS for part in parts):
            continue
        if any(parts[:len(prefix)] == prefix for prefix in EXCLUDED_PREFIXES):
            continue
        if path.is_symlink():
            raise ValueError(f'symlink not supported in distribution: {rel}')
        name = path.name.casefold()
        if not path.is_file() or name in EXCLUDED_NAMES:
            continue
        if name.startswith('.env') or name.endswith('~') or path.suffix.casefold() in EXCLUDED_SUFFIXES:
            continue
        # Do not blanket-filter archives: skills may ship required binary or
        # zipped test fixtures. Only explicit backup/snapshot names are local.
        if name.endswith(ARCHIVE_SUFFIXES) and BACKUP_NAME.search(name):
            continue
        yield path


def package(root, output, force=False):
    root, output = root.resolve(), output.resolve()
    if output.exists() and not force:
        raise FileExistsError(f'{output} exists; use --force to replace the generated archive')
    verifier = Verifier(root)
    if not verifier.run():
        raise ValueError('validation failed:\n'+'\n'.join(verifier.errors))
    slug = tomllib.loads((root/'codex-studio.toml').read_text(encoding='utf-8'))['slug']
    if slug != 'Codex-Game-Studios':
        raise ValueError('unexpected package root slug')
    sources = list(export_files(root))
    if output in sources:
        raise ValueError('output overlaps a source file')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix+'.tmp')
    if temporary.exists():
        raise FileExistsError(temporary)
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        for source in sources:
            info = zipfile.ZipInfo(slug+'/'+source.relative_to(root).as_posix(), (2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if source.suffix == '.sh' else 0o100644) << 16
            archive.writestr(info, source.read_bytes())
    temporary.replace(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix+'.sha256').write_text(digest+'  '+output.name+'\n',encoding='utf-8')
    return len(sources), digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,default=Path('dist/Codex-Game-Studios.zip'))
    parser.add_argument('--force',action='store_true')
    args=parser.parse_args()
    try:
        count,digest=package(args.root,args.output,args.force)
    except (OSError,ValueError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 1
    print(f'PACKAGED: {args.output.resolve()}\nFiles: {count}\nSHA256: {digest}')
    return 0


if __name__=='__main__':
    sys.exit(main())
