#!/usr/bin/env python3
"""Restore a local snapshot into a NEW directory, never overwriting current work."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile


WINDOWS_RESERVED = {'CON', 'PRN', 'AUX', 'NUL', 'CONIN$', 'CONOUT$'} | {
    prefix + number for prefix in ('COM', 'LPT') for number in '123456789\u00b9\u00b2\u00b3'
}


def member_parts(info):
    """Reject aliases before normalization, consistently on Windows and POSIX."""
    name = info.filename
    # An explicit directory may end in one slash; doubled separators, dot
    # segments and Windows trimming/device aliases are not portable file names.
    raw = name[:-1] if info.is_dir() else name
    parts = raw.split('/')
    if (not raw or PurePosixPath(raw).is_absolute()
            or any(part in {'', '.', '..'} for part in parts)):
        raise ValueError(f'unsafe or noncanonical archive member: {name}')
    for part in parts:
        if (part.endswith(('.', ' '))
                or any(ord(char) < 32 or char in '<>:"\\|?*' for char in part)
                or part.split('.', 1)[0].rstrip(' ').upper() in WINDOWS_RESERVED):
            raise ValueError(f'nonportable archive member: {name}')
    return parts


def restore(archive, destination, manifest=None):
    archive, destination=Path(archive).resolve(), Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f'destination must not exist: {destination}')
    expected=json.loads(Path(manifest).read_text(encoding='utf-8')) if manifest else None
    content={}
    seen=set()
    required_directories=set()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name=info.filename
            parts=member_parts(info)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f'archive contains symlink: {name}')
            target=(destination/name).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(f'archive path escapes destination: {name}')
            key=target.relative_to(destination).as_posix().casefold()
            parents={'/'.join(parts[:i]).casefold() for i in range(1, len(parts))}
            if parents & seen:
                raise ValueError(f'archive file/directory conflict: {name}')
            required_directories.update(parents)
            if info.is_dir():
                if key in seen:
                    raise ValueError(f'archive file/directory conflict: {name}')
                required_directories.add(key)
                continue
            if key in seen:
                raise ValueError(f'duplicate archive path: {name}')
            if key in required_directories:
                raise ValueError(f'archive file/directory conflict: {name}')
            seen.add(key)
            content[name]=z.read(info)
    actual={name:hashlib.sha256(data).hexdigest() for name,data in content.items()}
    if expected is not None and actual != expected:
        raise ValueError('snapshot does not match the supplied hash manifest')
    destination.mkdir(parents=True)
    for name,data in content.items():
        target=destination/name
        target.parent.mkdir(parents=True,exist_ok=True)
        # Exclusive creation also protects an unexpected file introduced after
        # preflight. Restoration never opens an existing file for overwrite.
        with target.open('xb') as stream:
            stream.write(data)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=actual[name]:
            raise OSError(f'restored file hash mismatch: {name}')
    return len(content)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('destination',type=Path)
    parser.add_argument('--manifest',type=Path)
    args=parser.parse_args()
    try:
        count=restore(args.archive,args.destination,args.manifest)
    except (OSError,ValueError,zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 1
    print(f'RESTORED: {count} files to {args.destination.resolve()} (original workspace untouched)')
    return 0


if __name__=='__main__':
    sys.exit(main())
