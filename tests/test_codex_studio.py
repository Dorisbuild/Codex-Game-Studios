"""Framework regressions, including deliberately broken copies and clean exports."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from verify_codex_studio import Verifier, yaml_load
from package_studio import export_files, package
from restore_snapshot import restore


class VerifierTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='codex validation ')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for source in export_files(ROOT):
            target = self.root/source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

    def edit(self, rel, before, after):
        p=self.root/rel
        text=p.read_text(encoding='utf-8')
        self.assertIn(before,text)
        p.write_text(text.replace(before,after,1),encoding='utf-8')

    def rejected(self, fragment):
        verifier=Verifier(self.root)
        self.assertFalse(verifier.run())
        self.assertTrue(any(fragment in e for e in verifier.errors),verifier.errors)

    def test_actual_project_and_clean_copy_are_valid(self):
        for root in (ROOT,self.root):
            v=Verifier(root)
            self.assertTrue(v.run(),v.errors)
            self.assertEqual((v.counts['skills'],v.counts['agents'],v.counts['catalog']),(75,49,124))
            self.assertEqual(v.counts['workflow_steps'],54)

    def test_project_config_requires_mapping_and_schema(self):
        path=self.root/'project.yaml'
        for contents, message in (('null\n','expected mapping'), ('[]\n','expected mapping'),
                                  ('{}\n','schema_version'),
                                  ('schema_version: true\n','schema_version')):
            with self.subTest(contents=contents):
                path.write_text(contents,encoding='utf-8')
                self.rejected(message)

    def test_configured_project_remains_valid_without_pinning_engine_defaults(self):
        path=self.root/'project.yaml'
        data=yaml_load(path.read_text(encoding='utf-8'))
        data.update(engine={'name':'Godot','version':'4.6'},modes={'rigor':'solo'})
        path.write_text(yaml.safe_dump(data),encoding='utf-8')
        verifier=Verifier(self.root)
        self.assertTrue(verifier.run(),verifier.errors)

    def test_project_sections_require_mappings(self):
        self.edit('project.yaml','schema_version: 1','schema_version: 1\nengine: []')
        self.rejected('engine must be a mapping')

    def test_workflow_requires_paths_and_phases(self):
        path=self.root/'docs/codex-studio/workflow-catalog.yaml'
        for contents, message in (('null\n','expected mapping'), ('[]\n','expected mapping'),
                                  ('paths: {}\nphases: {}\n','paths must include minimal'),
                                  ('paths: {minimal: {}}\nphases: {}\n','phases must be a non-empty mapping')):
            with self.subTest(contents=contents):
                path.write_text(contents,encoding='utf-8')
                self.rejected(message)

    def test_workflow_steps_must_be_nonempty_list_of_mappings(self):
        path=self.root/'docs/codex-studio/workflow-catalog.yaml'
        original=path.read_text(encoding='utf-8')
        for steps, message in (([], 'non-empty list'), ({}, 'non-empty list'),
                               (['not a step'], 'expected mapping')):
            with self.subTest(steps=steps):
                data=yaml_load(original)
                data['paths']['minimal']['steps']=steps
                path.write_text(yaml.safe_dump(data),encoding='utf-8')
                self.rejected(message)

    def test_workflow_step_fields_are_validated(self):
        path=self.root/'docs/codex-studio/workflow-catalog.yaml'
        original=path.read_text(encoding='utf-8')
        mutations=(('command','$codex-missing','command must select'),
                   ('command',None,'command must select'),
                   ('required','true','required must be a boolean'),
                   ('repeatable',1,'repeatable must be a boolean'),
                   ('id',[],'invalid step id'),
                   ('name','','name must be a non-empty string'))
        for field,value,message in mutations:
            with self.subTest(field=field,value=value):
                data=yaml_load(original)
                data['paths']['minimal']['steps'][0][field]=value
                path.write_text(yaml.safe_dump(data),encoding='utf-8')
                self.rejected(message)

    def test_workflow_artifact_shape_is_validated(self):
        path=self.root/'docs/codex-studio/workflow-catalog.yaml'
        original=path.read_text(encoding='utf-8')
        for artifact in ([], {}, {'any_of':[]}, {'any_of':[None]}, {'pattern':'only'},
                         {'glob':'file','min_count':0}, {'glob':'file','min_count':True}):
            with self.subTest(artifact=artifact):
                data=yaml_load(original)
                data['paths']['minimal']['steps'][0]['artifact']=artifact
                path.write_text(yaml.safe_dump(data),encoding='utf-8')
                self.rejected('artifact')

    def test_workflow_duplicate_step_and_unknown_next_phase_are_rejected(self):
        path=self.root/'docs/codex-studio/workflow-catalog.yaml'
        data=yaml_load(path.read_text(encoding='utf-8'))
        data['paths']['minimal']['steps'].append(data['paths']['minimal']['steps'][0].copy())
        data['phases']['concept']['next_phase']='not-a-phase'
        path.write_text(yaml.safe_dump(data),encoding='utf-8')
        self.rejected('duplicate step id')
        self.rejected('next_phase must name a phase')

    def test_invalid_workflow_prevents_packaging(self):
        (self.root/'docs/codex-studio/workflow-catalog.yaml').write_text('[]\n',encoding='utf-8')
        out=self.root/'dist/invalid.zip'
        with self.assertRaisesRegex(ValueError,'workflow catalog: expected mapping'):
            package(self.root,out)
        self.assertFalse(out.exists())

    def test_bad_namespace_is_rejected(self):
        self.edit('.agents/skills/codex-start/SKILL.md','name: codex-start','name: start')
        self.rejected('expected codex- skill name')

    def test_missing_ui_metadata_is_rejected(self):
        (self.root/'.agents/skills/codex-start/agents/openai.yaml').unlink()
        self.rejected('display_name')

    def test_ui_brand_is_checked(self):
        self.edit('.agents/skills/codex-start/agents/openai.yaml','Codex Start','Legacy Start')
        self.rejected('display_name')

    def test_ui_interface_shape_is_checked(self):
        (self.root/'.agents/skills/codex-start/agents/openai.yaml').write_text('interface: []\n',encoding='utf-8')
        self.rejected('interface must be a mapping')

    def test_duplicate_frontmatter_key_is_rejected(self):
        self.edit('.agents/skills/codex-start/SKILL.md','name: codex-start','name: codex-start\nname: codex-start')
        self.rejected('duplicate YAML key')

    def test_foreign_argument_macro_is_rejected(self):
        p=self.root/'.agents/skills/codex-start/SKILL.md'
        p.write_text(p.read_text(encoding='utf-8')+'\nRead $ARGUMENTS.\n',encoding='utf-8')
        self.rejected('unsupported runtime marker')

    def test_foreign_model_routing_is_rejected(self):
        path=self.root/'.agents/skills/codex-start/SKILL.md'
        original=path.read_text(encoding='utf-8')
        for marker in ('Model tier: Opus','Sonnet model','Haiku-tier'):
            with self.subTest(marker=marker):
                path.write_text(original+'\n'+marker+'\n',encoding='utf-8')
                self.rejected('unsupported runtime marker')

    def test_stale_selector_is_rejected(self):
        self.edit('.agents/skills/codex-start/SKILL.md','$codex-brainstorm','$brainstorm')
        self.rejected('stale unnamespaced selector')

    def test_unknown_selector_is_rejected(self):
        self.edit('.agents/skills/codex-start/SKILL.md','$codex-brainstorm','$codex-not-a-real-skill')
        self.rejected('unknown skill selector')

    def test_missing_shared_resource_is_rejected(self):
        (self.root/'docs/codex-studio/runtime.md').unlink()
        self.rejected('missing referenced resource')

    def test_missing_relative_skill_resource_is_rejected(self):
        p=self.root/'.agents/skills/codex-start/SKILL.md'
        p.write_text(p.read_text(encoding='utf-8')+'\nRead [steps](references/missing.md).\n',encoding='utf-8')
        self.rejected('missing relative skill resource')

    def test_empty_catalog_spec_is_rejected(self):
        self.edit('Codex Skill Testing Framework/catalog.yaml',
                  'spec: Codex Skill Testing Framework/skills/utility/codex-settings.md','spec: ""')
        self.rejected('missing behavioral spec')

    def test_catalog_duplicate_is_rejected(self):
        p=self.root/'Codex Skill Testing Framework/catalog.yaml'
        text=p.read_text(encoding='utf-8')
        text=text.replace('skills:\n','skills:\n  - name: codex-start\n    spec: Codex Skill Testing Framework/skills/utility/codex-start.md\n',1)
        p.write_text(text,encoding='utf-8')
        self.rejected('duplicate entries')

    def test_catalog_names_must_be_strings(self):
        self.edit('Codex Skill Testing Framework/catalog.yaml',
                  'name: codex-start','name: [codex-start]')
        self.rejected('names must be non-empty strings')

    def test_malformed_agent_toml_is_rejected(self):
        self.edit('.codex/agents/game-designer.toml','name = "game-designer"','name = [')
        self.rejected('parse error')

    def test_legacy_hook_directory_is_rejected(self):
        (self.root/'tools/codex-studio/hooks').mkdir()
        self.rejected('legacy runtime path still active')

    def test_export_without_git_history_and_local_state(self):
        for rel in ('.git/config','project.local.yaml','production/session-state/active.md',
                    'production/session-logs/private.log','docs/.env','tools/credentials.json'):
            p=self.root/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('LOCAL PRIVATE STATE',encoding='utf-8')
        out=self.root/'dist/studio.zip'
        count,digest=package(self.root,out)
        self.assertGreater(count,500)
        self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(),digest)
        with zipfile.ZipFile(out) as z:
            names=z.namelist()
            self.assertTrue(all(n.startswith('Codex-Game-Studios/') for n in names))
            self.assertFalse(any(n.endswith(('project.local.yaml','private.log','credentials.json','active.md')) or '/.git/' in n or '/.env' in n for n in names))
            dest=self.root/'extracted'
            z.extractall(dest)
        extracted=dest/'Codex-Game-Studios'
        self.assertFalse((extracted/'.git').exists())
        result=subprocess.run([sys.executable,str(extracted/'tools/verify_codex_studio.py')],
                              cwd=extracted/'src',capture_output=True,encoding='utf-8',timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS:',result.stdout)

    def test_export_is_reproducible_and_requires_explicit_overwrite(self):
        first=self.root/'dist/a.zip'
        second=self.root/'dist/b.zip'
        _,one=package(self.root,first)
        _,two=package(self.root,second)
        self.assertEqual(one,two)
        with self.assertRaises(FileExistsError):
            package(self.root,first)
        _,three=package(self.root,first,force=True)
        self.assertEqual(one,three)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='codex recovery ')
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.archive=self.root/'snapshot.zip'
        self.dest=self.root/'restored'

    def archive_files(self,files):
        with zipfile.ZipFile(self.archive,'w') as z:
            for name,contents in files.items(): z.writestr(name,contents)

    def test_restore_verifies_hashes(self):
        data=b'previous uncommitted edits\n'
        self.archive_files({'docs/file.md':data})
        manifest=self.root/'snapshot.sha256.json'
        manifest.write_text(json.dumps({'docs/file.md':hashlib.sha256(data).hexdigest()}),encoding='utf-8')
        self.assertEqual(restore(self.archive,self.dest,manifest),1)
        self.assertEqual((self.dest/'docs/file.md').read_bytes(),data)

    def test_existing_destination_is_never_overwritten(self):
        self.archive_files({'file.md':b'old'})
        self.dest.mkdir()
        (self.dest/'file.md').write_bytes(b'current')
        with self.assertRaises(FileExistsError): restore(self.archive,self.dest)
        self.assertEqual((self.dest/'file.md').read_bytes(),b'current')

    def test_traversal_rejected_before_writing(self):
        for name in ('../escape','C:/escape','/escape','..\\escape'):
            with self.subTest(name=name):
                self.archive_files({name:b'bad'})
                with self.assertRaises(ValueError): restore(self.archive,self.dest)
                self.assertFalse(self.dest.exists())

    def test_bad_hash_rejected_before_writing(self):
        self.archive_files({'file.md':b'changed'})
        manifest=self.root/'manifest.json'
        manifest.write_text(json.dumps({'file.md':'wrong'}),encoding='utf-8')
        with self.assertRaises(ValueError): restore(self.archive,self.dest,manifest)
        self.assertFalse(self.dest.exists())

    def test_case_collisions_are_rejected(self):
        self.archive_files({'A.md':b'one','a.md':b'two'})
        with self.assertRaises(ValueError): restore(self.archive,self.dest)
        self.assertFalse(self.dest.exists())


if __name__=='__main__':
    unittest.main()
