#!/usr/bin/env python3
"""Validate the standalone Codex workspace; does not execute game workflows."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
import sys
import tomllib

try:
    import yaml
except ImportError:
    raise SystemExit('Missing PyYAML: python -m pip install -r requirements-dev.txt')


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently accepting the last value."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def yaml_load(text):
    return yaml.load(text, Loader=UniqueLoader)


def skill_metadata(text):
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        raise ValueError('missing or malformed skill frontmatter')
    data = yaml_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError('skill frontmatter must be a mapping')
    return data, text[match.end():]


RUNTIME_MARKERS = (
    'AskUserQuestion', '$ARGUMENTS', 'CODEX_SKILL_DIR', 'CODEX_PROJECT_DIR',
    'hookSpecificOutput', 'Grep pattern=', 'Read(offset, limit)',
    'a user decision checkpoint', '`Agent` tool', 'multiSelect:',
    'NEVER use plain text', 'Never plain text', 'Use the structured tool',
    '.claude/', 'docs/ccgs/', 'tools/ccgs/', 'CCGS Skill Testing Framework',
    'Model tier: Opus', 'Model tier: Sonnet', 'Model tier: Haiku',
    'Opus-tier', 'Sonnet-tier', 'Haiku-tier', 'Sonnet model', 'Opus panel',
)
FRAMEWORK_REF = re.compile(
    r'(?:\.agents/skills/|\.codex/agents/|docs/codex-studio/|tools/codex-studio/)'
    r'[A-Za-z0-9_./-]+\.(?:md|sh|py|toml|yaml|yml|gd)(?![A-Za-z0-9_-])'
)


class Verifier:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []
        self.counts: dict[str, int] = {}
        self.metadata: dict[str, dict] = {}

    def error(self, msg):
        self.errors.append(msg)

    def read(self, rel):
        try:
            return (self.root / rel).read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            self.error(f'{rel}: {exc}')
            return ''

    def structured(self, rel, kind='yaml'):
        try:
            return tomllib.loads(self.read(rel)) if kind == 'toml' else yaml_load(self.read(rel))
        except (ValueError, yaml.YAMLError, TypeError) as exc:
            self.error(f'{rel}: parse error: {exc}')
            return None

    def check_skills(self):
        paths = sorted((self.root / '.agents/skills').glob('*/SKILL.md'))
        for path in paths:
            rel = path.relative_to(self.root).as_posix()
            try:
                data, body = skill_metadata(self.read(rel))
            except (ValueError, yaml.YAMLError, TypeError) as exc:
                self.error(f'{rel}: {exc}')
                continue
            name = data.get('name')
            if not isinstance(name, str) or not re.fullmatch(r'codex-[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) >= 64:
                self.error(f'{rel}: expected codex- skill name under 64 characters')
                continue
            if name != path.parent.name:
                self.error(f'{rel}: name does not match directory')
            if name in self.metadata:
                self.error(f'{rel}: duplicate skill name {name}')
            self.metadata[name] = data
            if not isinstance(data.get('description'), str) or not data['description'].strip():
                self.error(f'{rel}: description must be a non-empty string')
            if set(data) - {'name', 'description', 'metadata', 'license', 'compatibility'}:
                self.error(f'{rel}: unsupported skill metadata: {set(data)-{"name","description","metadata","license","compatibility"}}')
            if not body.strip():
                self.error(f'{rel}: empty workflow')
            ui_rel = path.parent.relative_to(self.root) / 'agents/openai.yaml'
            ui = self.structured(ui_rel)
            interface = ui.get('interface', {}) if isinstance(ui, dict) else {}
            if not isinstance(interface, dict):
                self.error(f'{ui_rel}: interface must be a mapping')
                interface = {}
            display = interface.get('display_name', '')
            short = interface.get('short_description', '')
            if not isinstance(display, str) or not display.startswith('Codex '):
                self.error(f'{ui_rel}: display_name must start with Codex')
            if not isinstance(short, str) or not 25 <= len(short) <= 64:
                self.error(f'{ui_rel}: short_description must be 25-64 characters')
            for resource in path.parent.rglob('*.md'):
                for link in re.findall(r'\]\(([^)\s]+)\)', resource.read_text(encoding='utf-8')):
                    if ':' in link or link.startswith(('#', '/')) or any(c in link for c in '<{*$'):
                        continue
                    link = link.split('#')[0]
                    if link and not (resource.parent / link).is_file():
                        self.error(f'{resource.relative_to(self.root)}: missing relative skill resource {link}')
        self.counts['skills'] = len(paths)

    def check_agents(self):
        agents = set()
        for path in sorted((self.root / '.codex/agents').glob('*.toml')):
            rel = path.relative_to(self.root)
            data = self.structured(rel, 'toml')
            if not isinstance(data, dict):
                continue
            for key in ('name', 'description', 'developer_instructions'):
                if not isinstance(data.get(key), str) or not data[key].strip():
                    self.error(f'{rel}: missing non-empty {key}')
            name = data.get('name', '')
            if not isinstance(name, str):
                continue
            if name != path.stem or name in agents:
                self.error(f'{rel}: duplicate/mismatched agent name')
            agents.add(name)
            if 'model' in data and not isinstance(data['model'], str):
                self.error(f'{rel}: model must be a string')
        self.counts['agents'] = len(agents)
        return agents

    def check_catalog(self, agents):
        rel = 'Codex Skill Testing Framework/catalog.yaml'
        data = self.structured(rel)
        if not isinstance(data, dict):
            self.error('missing catalog mapping')
            return
        total = 0
        for kind, expected in (('skills', set(self.metadata)), ('agents', agents)):
            rows = data.get(kind, [])
            if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
                self.error(f'catalog {kind}: expected list of mappings')
                continue
            names = [r.get('name') for r in rows]
            if any(not isinstance(n, str) or not n.strip() for n in names):
                self.error(f'catalog {kind}: names must be non-empty strings')
                continue
            if set(names) != expected:
                self.error(f'catalog {kind}: missing {expected-set(names)}, unknown {set(names)-expected}')
            duplicate = [n for n, count in Counter(names).items() if count != 1]
            if duplicate:
                self.error(f'catalog {kind}: duplicate entries {duplicate}')
            for row in rows:
                spec = row.get('spec')
                if not isinstance(spec, str) or not spec.strip():
                    self.error(f'catalog {row.get("name")}: missing behavioral spec')
                    continue
                path = (self.root / spec).resolve()
                if not path.is_relative_to(self.root) or not path.is_file():
                    self.error(f'catalog {row.get("name")}: spec not a workspace file: {spec}')
            total += len(rows)
        self.counts['catalog'] = total

    def check_project_config(self):
        data = self.structured('project.yaml')
        if not isinstance(data, dict):
            self.error('project.yaml: expected mapping')
            return
        if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
            self.error('project.yaml: expected schema_version: 1')
        framework = data.get('framework')
        if not isinstance(framework, dict) or not isinstance(framework.get('version'), str) or not framework['version'].strip():
            self.error('project.yaml: framework.version must be a non-empty string')
        # An unconfigured template intentionally has no engine, modes or game.
        for section in ('project', 'engine', 'modes', 'docs', 'qa', 'team', 'testing',
                        'performance', 'features', 'naming', 'platform', 'accessibility',
                        'cadence', 'specialists'):
            if section in data and not isinstance(data[section], dict):
                self.error(f'project.yaml: {section} must be a mapping when present')

    def check_artifact(self, artifact, location, depth=0):
        if not isinstance(artifact, dict) or not artifact:
            self.error(f'{location}: artifact must be a non-empty mapping')
            return
        if not any(k in artifact for k in ('glob', 'note', 'any_of')):
            self.error(f'{location}: artifact needs glob, note or any_of')
        for key in ('glob', 'pattern', 'note'):
            if key in artifact and (not isinstance(artifact[key], str) or not artifact[key].strip()):
                self.error(f'{location}: artifact.{key} must be a non-empty string')
        if 'min_count' in artifact and (type(artifact['min_count']) is not int or artifact['min_count'] < 1):
            self.error(f'{location}: artifact.min_count must be a positive integer')
        if 'any_of' in artifact:
            alternatives = artifact['any_of']
            if not isinstance(alternatives, list) or not alternatives or depth >= 4:
                self.error(f'{location}: artifact.any_of must be a non-empty list with bounded nesting')
            else:
                for index, entry in enumerate(alternatives):
                    self.check_artifact(entry, f'{location}.any_of[{index}]', depth+1)

    def check_workflow(self):
        data = self.structured('docs/codex-studio/workflow-catalog.yaml')
        if not isinstance(data, dict):
            self.error('workflow catalog: expected mapping')
            return
        paths, phases = data.get('paths'), data.get('phases')
        if not isinstance(paths, dict) or 'minimal' not in paths:
            self.error('workflow catalog: paths must include minimal')
        if not isinstance(phases, dict) or not phases:
            self.error('workflow catalog: phases must be a non-empty mapping')
        total = 0
        for kind, groups in (('paths', paths), ('phases', phases)):
            if not isinstance(groups, dict):
                continue
            for name, group in groups.items():
                location = f'workflow {kind}.{name}'
                if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
                    self.error(f'{location}: invalid group id')
                if not isinstance(group, dict):
                    self.error(f'{location}: expected mapping')
                    continue
                if not isinstance(group.get('label'), str) or not group['label'].strip():
                    self.error(f'{location}: label must be a non-empty string')
                if kind == 'phases':
                    next_phase = group.get('next_phase')
                    if 'next_phase' not in group or (next_phase is not None and (not isinstance(next_phase, str) or next_phase not in phases)):
                        self.error(f'{location}: next_phase must name a phase or be null')
                steps = group.get('steps')
                if not isinstance(steps, list) or not steps:
                    self.error(f'{location}: steps must be a non-empty list')
                    continue
                seen = set()
                for index, step in enumerate(steps):
                    where = f'{location}.steps[{index}]'
                    if not isinstance(step, dict):
                        self.error(f'{where}: expected mapping')
                        continue
                    step_id = step.get('id')
                    if not isinstance(step_id, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', step_id):
                        self.error(f'{where}: invalid step id')
                    elif step_id in seen:
                        self.error(f'{where}: duplicate step id {step_id}')
                    else:
                        seen.add(step_id)
                    for field in ('name', 'description'):
                        if not isinstance(step.get(field), str) or not step[field].strip():
                            self.error(f'{where}: {field} must be a non-empty string')
                    if type(step.get('required')) is not bool:
                        self.error(f'{where}: required must be a boolean')
                    if 'repeatable' in step and type(step['repeatable']) is not bool:
                        self.error(f'{where}: repeatable must be a boolean')
                    command = step.get('command')
                    # Optional orchestration entries may list several skills in
                    # their description instead of specifying one producer.
                    if 'command' in step or step.get('required') is True:
                        if not isinstance(command, str) or command.split(' ', 1)[0].removeprefix('$') not in self.metadata or not command.startswith('$'):
                            self.error(f'{where}: command must select a known Codex skill')
                    if 'artifact' in step:
                        self.check_artifact(step['artifact'], where)
                total += len(steps)
        self.counts['workflow_steps'] = total

    def check_references(self):
        roots = ['.agents', '.codex', 'docs', 'tools/codex-studio', 'Codex Skill Testing Framework']
        paths = [self.root / n for n in ('AGENTS.md', 'README.md', 'CONTRIBUTING.md', 'SECURITY.md')]
        for rel in roots:
            paths.extend(p for p in (self.root / rel).rglob('*') if p.suffix in {'.md', '.toml', '.sh', '.yaml', '.yml'})
        old_names = {n.removeprefix('codex-') for n in self.metadata}
        refs = set()
        for path in paths:
            if not path.is_file():
                continue
            rel = path.relative_to(self.root)
            text = self.read(rel)
            for marker in RUNTIME_MARKERS:
                if marker in text:
                    self.error(f'{rel}: unsupported runtime marker {marker!r}')
            for name in re.findall(r'\$(codex-[a-z0-9-]+)', text):
                if name not in self.metadata and name not in {'codex-skill-name'}:
                    self.error(f'{rel}: unknown skill selector ${name}')
            for old in re.findall(r'\$([a-z][a-z0-9-]*)', text):
                if old in old_names:
                    self.error(f'{rel}: stale unnamespaced selector ${old}')
            for ref in FRAMEWORK_REF.findall(text):
                refs.add(ref)
                if not (self.root / ref).is_file():
                    self.error(f'{rel}: missing referenced resource {ref}')
        self.counts['references'] = len(refs)

    def run(self):
        manifest = self.structured('codex-studio.toml', 'toml') or {}
        if manifest.get('name') != 'Codex Game Studios' or manifest.get('skill_namespace') != 'codex-':
            self.error('invalid project identity/namespace')
        for rel in ('LICENSE', 'NOTICE.md', 'AGENTS.md', 'requirements-dev.txt', 'docs/codex-studio/runtime.md'):
            if not (self.root / rel).is_file():
                self.error(f'missing required file {rel}')
        for rel in ('.claude', 'docs/ccgs', 'tools/ccgs', 'CCGS Skill Testing Framework', 'tools/codex-studio/hooks'):
            if (self.root / rel).exists():
                self.error(f'legacy runtime path still active: {rel}')
        self.structured('.codex/config.toml', 'toml')
        self.check_skills()
        self.check_project_config()
        self.check_workflow()
        agents = self.check_agents()
        self.check_catalog(agents)
        self.check_references()
        for kind in ('skills', 'agents'):
            expected = manifest.get(kind[:-1]+'_count')
            if self.counts.get(kind) != expected:
                self.error(f'{kind}: manifest expects {expected}, found {self.counts.get(kind)}')
        return not self.errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    verifier = Verifier(args.root)
    ok = verifier.run()
    for kind, count in verifier.counts.items():
        print(f'{kind}: {count}')
    for error in verifier.errors:
        print('ERROR: '+error)
    print(f'{"PASS" if ok else "FAIL"}: Codex Game Studios structural validation ({len(verifier.errors)} errors)')
    print('Scope: metadata, catalogs, references, and runtime markers; game/skill behavior is not inferred.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
