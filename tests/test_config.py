"""
Checks settings precedence, validation, and private values.
"""

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from lib.config import EASTERN, ROOT, public_settings, read_settings
from main import main


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        """
        Checks settings using an isolated outer directory.
        """
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repository'
        self.root.mkdir()
        self.env = {'CF_SETTINGS_LABEL': 'unknown', 'CF_SETTINGS_NOTES': 'Rules not supplied.'}
        self.args = ['bdr:nz9qn2kb', '--workflow', 'tabs']

    def read(self, extra: list[str] | None = None) -> tuple:
        """
        Checks a setting combination against isolated environment values.
        """
        return read_settings(self.args + (extra or []), self.env, self.root)

    def test_precedence_and_explicit_outer_env(self) -> None:
        """
        Checks CLI, environment, outer .env, defaults, and generated seed priority.
        """
        (self.root.parent / '.env').write_text('VIEW_SECONDS=7\nMAX_ITEMS=4\n', encoding='utf-8')
        (self.root / '.env').write_text('MAX_ITEMS=19\n', encoding='utf-8')
        self.env['VIEW_SECONDS'] = '8'
        settings, _ = self.read(['--view-seconds', '9'])
        self.assertEqual((settings.view_seconds, settings.max_items), (9, 4))
        self.assertEqual(settings.sources['view_seconds'], 'command line')
        self.assertEqual(settings.sources['max_items'], '../.env')
        self.assertEqual(settings.sources['seed'], 'generated')
        self.assertEqual(settings.output_dir, '../runs')
        self.assertTrue(settings.collection_url.endswith('/bdr:nz9qn2kb/?page=1&per_page=50'))

    def test_module_move_preserves_repository_root(self) -> None:
        """
        Checks moving settings into lib keeps relative paths anchored to the repository root.
        """
        self.assertEqual(ROOT, Path(__file__).resolve().parent.parent)

    def test_invalid_values(self) -> None:
        """
        Checks invalid limits, timings, proxies, identifiers, and output locations.
        """
        for extra in [
            ['--workflow', 'other'],
            ['--max-items', '21'],
            ['--max-items', '0'],
            ['--selection-start', '3'],
            ['--view-seconds', 'nan'],
            ['--view-seconds', 'inf'],
            ['--view-jitter-seconds', '5'],
            ['--open-jitter-seconds', '-1'],
            ['--max-duration-seconds', '0'],
            ['--max-scroll-actions', '0'],
            ['--navigation-timeout-seconds', '-1'],
            ['--output-dir', '.'],
            ['--output-dir', 'results'],
            ['--proxy-server', 'http://user:secret@localhost:8080'],
            ['--proxy-server', 'localhost:8080'],
            ['--public-ip', 'not-an-ip'],
            ['--cf-settings-since', '2026-01-01T00:00:00'],
        ]:
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.read(extra)
        self.args[0] = '403'
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.read()

    def test_return_unused_and_explicit_timing_rejected(self) -> None:
        """
        Checks unused environment opening settings and rejected explicit CLI timing.
        """
        self.args[-1] = 'return'
        self.env['OPEN_INTERVAL_SECONDS'] = '8'
        settings, _ = self.read()
        self.assertEqual(settings.unused['open_interval_seconds'], {'value': 8, 'source': 'environment'})
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.read(['--open-interval-seconds', '8'])

    def test_secrets_and_timezone(self) -> None:
        """
        Checks credential omission and Eastern conversion across daylight saving changes.
        """
        self.env.update(
            PROXY_SERVER='http://localhost:8080', PROXY_USERNAME='private-user', PROXY_PASSWORD='private-password'
        )
        settings, _ = self.read(['--cf-settings-since', '2026-07-01T12:00:00+00:00'])
        saved = json.dumps(public_settings(settings))
        self.assertNotIn('private-user', saved)
        self.assertNotIn('private-password', saved)
        self.assertIn('080000', settings.cf_settings_since.replace(':', ''))
        self.assertTrue(settings.cf_settings_since.endswith('-0400 EDT'))
        self.assertEqual(datetime(2026, 1, 1, tzinfo=EASTERN).strftime('%z %Z'), '-0500 EST')

    def test_preview_never_launches_browser(self) -> None:
        """
        Checks that settings preview does not launch Chromium or make requests.
        """
        with (
            patch.dict('os.environ', self.env, clear=True),
            patch('sys.argv', ['main.py', *self.args, '--preview']),
            patch('lib.browser_flow.run_trial') as run,
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            main()
        run.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['workflow'], 'tabs')
