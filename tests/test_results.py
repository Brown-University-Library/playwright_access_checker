"""
Checks report privacy, interrupted records, and offline reconstruction.
"""

import json
import tempfile
import unittest

from lib.config import Settings
from lib.results import Recorder, rebuild_report


class TestResults(unittest.TestCase):
    def setUp(self) -> None:
        """
        Checks report writing in an isolated directory without any network requests.
        """
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        settings = Settings(
            output_dir=self.temp.name,
            collection_id='bdr:nz9qn2kb',
            workflow='tabs',
            cf_settings_label='test',
            cf_settings_notes='unknown',
        )
        self.recorder = Recorder(settings)
        self.addCleanup(self.recorder.stream.close)

    def test_selected_but_unopened_urls_are_not_checked(self) -> None:
        """
        Checks selected but unopened URLs do not appear in the checked-URL report.
        """
        recorder = self.recorder
        unopened = 'https://example.test/studio/item/bdr:unopened/'
        recorder.metadata['selected'] = [{'position': 1, 'url': unopened}]
        recorder.emit(
            'collection_open',
            visit_id='collection-1',
            tab_id='tab-1',
            url='https://example.test/studio/collections/bdr:nz9qn2kb/?page=1&per_page=50',
        )
        recorder.stop('user_interrupted')
        recorder.save()
        report = (recorder.directory / 'summary.md').read_text()
        self.assertNotIn(unopened, report)
        self.assertIn('unfinished at stop', report)
        self.assertIn('Known unknowns and evidence limits', report)
        self.assertIn('unavailable', report)

    def test_rebuild_handles_truncated_tail_and_recovers_selection(self) -> None:
        """
        Checks a partial final event preserves prior records and recovers a late selection.
        """
        recorder = self.recorder
        selected = [{'position': 1, 'url': 'https://example.test/studio/item/bdr:1/'}]
        recorder.emit('selection', selected=selected, available_count=1, duration=0.1, scrolls=0, reason='end_of_listing')
        recorder.emit('tab_created', tab_id='tab-1', url='about:blank')
        recorder.stream.write('{"kind":')
        recorder.stream.flush()
        data = rebuild_report(recorder.directory)
        self.assertEqual(data['selected'], selected)
        self.assertEqual(data['stop_reason'], 'incomplete_saved_events')
        self.assertEqual(len(data['tabs']), 1)
        self.assertIn('lower bound', data['known_unknowns'][-1])

    def test_first_stop_wins_and_later_events_are_marked(self) -> None:
        """
        Checks a later failure cannot replace the first interference or its count cutoff.
        """
        recorder = self.recorder
        recorder.stop('challenge', elapsed=2, request_id='request-1')
        recorder.emit('request_failed', request_id='request-1')
        recorder.stop('network_error')
        recorder.save()
        data = json.loads((recorder.directory / 'run.json').read_text())
        self.assertEqual(data['stop_reason'], 'challenge')
        self.assertEqual(data['observed_seconds'], 2)
        self.assertTrue(recorder.events[-1]['after_stop'])

    def test_rebuild_recovers_unfinished_verification(self) -> None:
        """
        Checks verification survives an interrupted log without its ending event.
        """
        recorder = self.recorder
        recorder.emit('verification_start', elapsed=1, tab_id='tab-1', status=200)
        recorder.save()
        recorder.emit('page_observed', elapsed=4, tab_id='tab-1')
        recorder.stream.write('{"kind":')
        recorder.stream.flush()
        data = rebuild_report(recorder.directory)
        verification = data['analysis']['initial_verification']
        self.assertEqual(data['stop_reason'], 'incomplete_saved_events')
        self.assertEqual(verification['duration_seconds'], 3)
        self.assertFalse(verification['completed'])
        self.assertIsNone(verification['after_verification'])
        self.assertIn('not completed (3.000s)', (recorder.directory / 'summary.md').read_text())
