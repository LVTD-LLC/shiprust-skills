import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
installer = load('installer', 'scripts/install.py')
api = load('api', 'skills/shiprust/scripts/shiprust_api.py')

class InstallerTests(unittest.TestCase):
    def test_idempotent_and_dry_run(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'skill'
            installer.install(dest, True)
            self.assertFalse(dest.exists())
            count = installer.install(dest)
            self.assertGreater(count, 4)
            self.assertEqual(installer.install(dest), count)
            self.assertTrue((dest / 'references/agents.md').is_file())
    def test_conflicts_are_preflighted(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            (dest / 'SKILL.md').write_text('custom')
            with self.assertRaises(ValueError): installer.install(dest)
            self.assertEqual(list(dest.iterdir()), [dest / 'SKILL.md'])
    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'elsewhere').mkdir()
            (base / 'skill').symlink_to(base / 'elsewhere', target_is_directory=True)
            with self.assertRaises(ValueError): installer.install(base / 'skill')

class RequestTests(unittest.TestCase):
    def test_auth_header_stays_in_request_not_url(self):
        with patch.dict(os.environ, {'SHIPRUST_API_KEY': 'sr_test'}), patch.object(api.urllib.request, 'build_opener') as opener:
            api.request('GET', '/api/v1/me')
            req = opener.return_value.open.call_args.args[0]
            self.assertEqual(req.full_url, 'https://shiprust.com/api/v1/me')
            self.assertEqual(req.headers['Authorization'], 'Bearer sr_test')
            self.assertEqual(opener.return_value.open.call_args.kwargs['timeout'], 60)
    def test_public_options_need_no_key(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(api.urllib.request, 'build_opener') as opener:
            api.request('GET', '/api/v1/options', authenticated=False)
            self.assertNotIn('Authorization', opener.return_value.open.call_args.args[0].headers)
    def test_missing_key_and_external_path_rejected_before_network(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(api.urllib.request, 'build_opener') as opener:
            for path in ['/api/v1/me', 'https://evil.example', '//evil.example', '/api/v1/../me']:
                with self.assertRaises(ValueError): api.request('GET', path)
            opener.assert_not_called()
    def test_credentials_cannot_follow_redirect(self):
        req = Request('https://shiprust.com/api/v1/me', headers={'Authorization': 'Bearer sr_test'})
        self.assertIsNone(api.NoRedirect().redirect_request(req, None, 302, '', {}, 'https://evil.example'))
    def test_uuid_validation(self):
        with self.assertRaises(ValueError): api.project_id('../other')
        self.assertEqual(api.project_id('12345678-1234-1234-1234-123456789abc'), '12345678-1234-1234-1234-123456789abc')
    def test_delete_requires_confirmation(self):
        from argparse import Namespace
        with patch.object(api, 'request') as request:
            with self.assertRaises(ValueError): api.run(Namespace(command='delete', id='12345678-1234-1234-1234-123456789abc', confirm_delete=False))
            request.assert_not_called()
    def test_download_refuses_overwrite(self):
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as temp, patch.object(api, 'request') as request:
            path = Path(temp) / 'app.zip'; path.write_bytes(b'original')
            with self.assertRaises(ValueError): api.run(Namespace(command='download', id='12345678-1234-1234-1234-123456789abc', output=path))
            self.assertEqual(path.read_bytes(), b'original'); request.assert_not_called()
    def test_delete_handles_empty_body(self):
        from argparse import Namespace
        with patch.object(api, 'request') as request, contextlib.redirect_stdout(io.StringIO()) as output:
            request.return_value.__enter__.return_value.status = 204
            api.run(Namespace(command='delete', id='12345678-1234-1234-1234-123456789abc', confirm_delete=True))
            self.assertIn('deleted', output.getvalue())

class ContractTests(unittest.TestCase):
    def test_codex_bundle_matches_canonical_source(self):
        bundle = ROOT/'plugins/shiprust-skills'
        for source in (ROOT/'skills').rglob('*'):
            if source.is_file() and '__pycache__' not in source.parts:
                self.assertEqual(source.read_bytes(), (bundle/source.relative_to(ROOT)).read_bytes())
        self.assertEqual((ROOT/'configs/codex.mcp.json').read_bytes(), (bundle/'.mcp.json').read_bytes())
    def test_json_and_no_real_keys(self):
        for path in ROOT.rglob('*.json'):
            if '.git' in path.parts: continue
            json.loads(path.read_text())
        for path in ROOT.rglob('*'):
            if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts: continue
            self.assertIsNone(re.search(r'sr_[a-f0-9]{64}', path.read_text()), str(path))
    def test_client_specific_interpolation(self):
        expected = {'claude.mcp.json':'${SHIPRUST_API_KEY}', 'cursor.mcp.json':'${env:SHIPRUST_API_KEY}', 'opencode.json':'{env:SHIPRUST_API_KEY}', 'openclaw.json':'${SHIPRUST_API_KEY}'}
        for name, placeholder in expected.items():
            self.assertIn(placeholder, (ROOT/'configs'/name).read_text())
        codex = json.loads((ROOT/'configs/codex.mcp.json').read_text())
        self.assertEqual(codex['mcpServers']['shiprust']['bearer_token_env_var'], 'SHIPRUST_API_KEY')
    def test_manifest_paths(self):
        for name in ['plugins/shiprust-skills/.codex-plugin', '.claude-plugin', '.cursor-plugin']:
            manifest = json.loads((ROOT/name/'plugin.json').read_text())
            self.assertEqual(manifest['name'], 'shiprust-skills')
            for key in ['skills', 'mcpServers']:
                if key in manifest: self.assertTrue((ROOT/name).parent.joinpath(manifest[key]).exists())
    def test_relative_markdown_links(self):
        for path in ROOT.rglob('*.md'):
            if '.git' in path.parts: continue
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/target.split('#')[0]).exists(), f'{path}: {target}')
    def test_openapi_contract(self):
        spec = json.loads((ROOT/'openapi.json').read_text())
        self.assertEqual(spec['servers'], [{'url':'https://shiprust.com'}])
        self.assertEqual(spec['components']['schemas']['CreateProject']['required'], ['name'])
        self.assertEqual(spec['paths']['/api/v1/options']['get']['security'], [])
        self.assertTrue(spec['paths']['/api/v1/projects/{id}']['delete']['x-openai-isConsequential'])
        self.assertEqual(len(spec['paths']), 5)

if __name__ == '__main__': unittest.main()
