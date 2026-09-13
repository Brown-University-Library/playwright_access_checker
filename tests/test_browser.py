"""
Checks complete browser trials against a local website; never contacts BDR.
"""

import contextlib
import io
import json
import tempfile
import unittest
from unittest.mock import PropertyMock, patch

from playwright.sync_api import Page

from lib.browser_flow import run_trial
from lib.config import Settings
from lib.results import rebuild_report
from tests.local_site import LocalSite

ORIGINAL_BRING_TO_FRONT = Page.bring_to_front


def complete_local_verification(page: Page) -> None:
    """
    Clicks the small local test website's button after a simulated user delay.
    Called by: TestBrowser verification tests, through patched Page.bring_to_front()
    """
    ORIGINAL_BRING_TO_FRONT(page)
    button = page.get_by_role('button', name='Complete local verification')
    if button.count():
        page.wait_for_timeout(1100)
        button.click()


def close_local_verification(page: Page) -> None:
    """
    Closes the local verification page to simulate a user closing the browser.
    Called by: TestBrowser.test_verification_window_closed(), through patched Page.bring_to_front()
    """
    page.close()


class TestBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Checks browser workflows against one local HTTP server.
        """
        cls.site = LocalSite()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Checks cleanup by closing the local server and its thread.
        """
        cls.site.shutdown()
        cls.site.server_close()
        cls.site.thread.join()

    def setUp(self) -> None:
        """
        Checks each trial using its own results directory and browser context.
        """
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site.hits = []
        self.site.collection_visits = 0

    def run_case(self, workflow: str = 'tabs', mode: str = 'normal', **changes: object) -> tuple:
        """
        Checks a complete local trial with shortened deterministic timing.
        """
        self.site.mode = mode
        self.site.hits = []
        self.site.collection_visits = 0
        values = {
            'collection_id': 'bdr:nz9qn2kb',
            'workflow': workflow,
            'cf_settings_label': 'local test',
            'cf_settings_notes': 'Made-up responses.',
            'output_dir': self.temp.name,
            'bdr_hosts': '127.0.0.1',
            'seed': 42,
            'max_items': 3,
            'view_seconds': 0.06,
            'view_jitter_seconds': 0,
            'open_interval_seconds': 0.12,
            'open_jitter_seconds': 0,
            'navigation_timeout_seconds': 2,
            'verification_timeout_seconds': 3,
            'max_duration_seconds': 12,
        }
        values.update(changes)
        url = self.site.origin + '/studio/collections/bdr:nz9qn2kb/?page=1&per_page=50'
        with (
            patch.object(Settings, 'collection_url', new_callable=PropertyMock, return_value=url),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            recorder = run_trial(Settings(**values), headless=True)
        self.output = output.getvalue()
        data = json.loads((recorder.directory / 'run.json').read_text())
        return recorder, data

    def test_tabs_overlap_and_first_requests(self) -> None:
        """
        Checks later tabs open during a slow first load, first requests, referrers, and review order.
        """
        recorder, data = self.run_case(mode='slow')
        self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
        self.assertEqual(self.output, '')
        opens = [event for event in recorder.events if event['kind'] == 'item_open']
        ready = [event for event in recorder.events if event['kind'] == 'item_ready']
        views = [event for event in recorder.events if event['kind'] == 'view_start']
        first_ready = next(event for event in ready if event['attempt_id'] == 'item-1')
        self.assertLess(opens[2]['elapsed'], first_ready['elapsed'])
        self.assertGreater(views[0]['elapsed'], opens[-1]['elapsed'])
        self.assertEqual([event['attempt_id'] for event in views], ['item-1', 'item-2', 'item-3'])
        self.assertEqual(len(data['tabs']), 4)
        self.assertEqual(data['analysis']['totals']['completed_views'], 3)
        documents = [
            event for event in recorder.events if event['kind'] == 'request' and event['resource_type'] == 'document'
        ]
        self.assertEqual(len(documents), 4)
        self.assertEqual(documents[0]['elapsed'], 0)
        self.assertTrue(all(event['tab_id'] for event in documents))
        self.assertTrue(all('/studio/collections/' in event['referer'] for event in documents[1:]))
        self.assertTrue(all('page=2' not in hit['path'] for hit in self.site.hits))
        self.assertEqual(
            len({event['request_id'] for event in recorder.events if event['kind'] == 'request'}),
            data['analysis']['totals']['all_bdr_requests'],
        )

    def test_return_preserves_order_and_one_tab(self) -> None:
        """
        Checks the one-tab open/view/actual-link-return sequence through the final return.
        """
        recorder, data = self.run_case('return')
        self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
        self.assertEqual(len(data['tabs']), 1)
        self.assertEqual(self.site.collection_visits, 4)
        actions = [event['kind'] for event in recorder.events if event['kind'] in {'item_open', 'view_start', 'return_open'}]
        self.assertEqual(actions, ['item_open', 'view_start', 'return_open'] * 3)
        self.assertEqual([item['position'] for item in data['selected']], [1, 3, 5])

    def test_return_restores_actual_page_size_control(self) -> None:
        """
        Checks one restoration per return and records the intermediate 20-item listing.
        """
        recorder, data = self.run_case('return', 'reset', max_items=2)
        self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
        self.assertEqual(len([event for event in recorder.events if event['kind'] == 'listing_restore']), 2)
        sizes = [event['per_page'] for event in recorder.events if event['kind'] == 'listing']
        self.assertEqual(sizes, [50, 20, 50, 20, 50])
        self.assertEqual(self.site.collection_visits, 5)

    def test_long_page_scrolling_in_both_workflows(self) -> None:
        """
        Checks total viewing time includes pauses and requests triggered by scrolling.
        """
        for workflow in ('tabs', 'return'):
            with self.subTest(workflow=workflow):
                recorder, data = self.run_case(workflow, 'long', max_items=1, view_seconds=1.2)
                self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
                end = next(event for event in recorder.events if event['kind'] == 'view_end')
                self.assertTrue(end['completed'])
                self.assertFalse(end['bottom_reached'])
                self.assertGreaterEqual(end['scrolls'], 1)
                self.assertLess(end['actual_seconds'], 1.6)
                self.assertTrue(
                    any(event['kind'] == 'request' and '/scroll-data' in event['url'] for event in recorder.events)
                )

    def test_short_view_has_no_scroll(self) -> None:
        """
        Checks a viewing duration shorter than one pause stays on the initial area.
        """
        recorder, data = self.run_case(max_items=1)
        self.assertEqual(data['stop_reason'], 'workflow_complete')
        end = next(event for event in recorder.events if event['kind'] == 'view_end')
        self.assertEqual(end['scrolls'], 0)
        self.assertTrue(end['bottom_reached'])

    def test_interference_stops_all_further_actions(self) -> None:
        """
        Checks challenges in supporting files, background tabs, scrolling, and final returns.
        """
        for mode in ('supporting_challenge', 'background_challenge', 'scroll_challenge', 'final_return', 'denial_page'):
            with self.subTest(mode=mode):
                workflow = 'return' if mode == 'final_return' else 'tabs'
                recorder, data = self.run_case(
                    workflow, mode, view_seconds=1.3, max_items=1 if mode != 'background_challenge' else 3
                )
                self.assertIn(data['stop_reason'], {'challenge', 'denial_page'}, data.get('stop'))
                stop = next(event for event in recorder.events if event['kind'] == 'stop')
                actions = {'item_open', 'return_open', 'tab_switch', 'scroll_start', 'listing_restore'}
                self.assertFalse(
                    any(event['kind'] in actions and event['event_id'] > stop['event_id'] for event in recorder.events)
                )

    def test_errors_save_incomplete_reports(self) -> None:
        """
        Checks empty/changed listings, missing return links, ignored settings, and timeouts.
        """
        cases = [
            ('empty', 'no_eligible_items'),
            ('ignored', 'unexpected_listing'),
            ('changed', 'listing_order_changed'),
            ('missing_return', 'missing_return_link'),
            ('timeout', 'page_opening_timeout'),
        ]
        for mode, expected in cases:
            with self.subTest(mode=mode):
                _, data = self.run_case(
                    'return' if mode in {'changed', 'missing_return'} else 'tabs',
                    mode,
                    max_items=1,
                    navigation_timeout_seconds=0.3 if mode == 'timeout' else 2,
                )
                self.assertEqual(data['stop_reason'], expected, data.get('stop'))

    def test_verification_page_without_challenge_header(self) -> None:
        """
        Checks a Turnstile page at HTTP 200 prompts once and stops at the verification limit.
        """
        recorder, data = self.run_case(mode='turnstile', verification_timeout_seconds=0.25)
        self.assertEqual(data['stop_reason'], 'verification_timeout', data.get('stop'))
        self.assertLess(data['observed_seconds'], 1)
        self.assertEqual(self.output.count('Turnstile detected.'), 1)
        self.assertIn('Complete verification in the browser window.', self.output)
        self.assertFalse(any(event['kind'] == 'item_open' for event in recorder.events))
        self.assertEqual(data['stop']['source'], 'Turnstile verification page; rule unconfirmed')
        verification = data['analysis']['initial_verification']
        self.assertFalse(verification['completed'])
        self.assertGreaterEqual(verification['duration_seconds'], 0.25)
        self.assertEqual(data['analysis'], rebuild_report(recorder.directory)['analysis'])

    def test_manual_verification_resumes_in_same_session(self) -> None:
        """
        Checks both workflows resume after a local button sets a cookie and loads the collection.
        """
        for workflow in ('tabs', 'return'):
            with self.subTest(workflow=workflow), patch.object(Page, 'bring_to_front', complete_local_verification):
                recorder, data = self.run_case(
                    workflow,
                    'turnstile_manual',
                    max_items=1,
                    navigation_timeout_seconds=0.3,
                    max_duration_seconds=5,
                )
            self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
            self.assertEqual(self.output.count('Turnstile detected.'), 1)
            self.assertIn('Continuing the browsing trial.', self.output)
            verification = data['analysis']['initial_verification']
            self.assertTrue(verification['completed'])
            self.assertGreater(verification['duration_seconds'], 1)
            self.assertGreater(data['observed_seconds'], verification['duration_seconds'])
            self.assertEqual(verification['after_verification']['item_attempts'], 1)
            start = next(event for event in recorder.events if event['kind'] == 'verification_start')
            end = next(event for event in recorder.events if event['kind'] == 'verification_end')
            actions = {'item_open', 'scroll_start', 'selection'}
            self.assertFalse(
                any(
                    event['kind'] in actions and start['event_id'] < event['event_id'] < end['event_id']
                    for event in recorder.events
                )
            )
            self.assertEqual(data['analysis']['totals']['completed_views'], 1)
            self.assertEqual(data['analysis'], rebuild_report(recorder.directory)['analysis'])
            summary = (recorder.directory / 'summary.md').read_text()
            self.assertIn('Browsing completed after initial Turnstile verification.', summary)
            self.assertIn('Browsing after verification:', summary)
            self.assertNotIn('No interference observed', summary)
            self.assertNotIn('local_verification=complete', (recorder.directory / 'events.jsonl').read_text())

    def test_verification_can_be_disabled(self) -> None:
        """
        Checks a zero verification limit preserves immediate stopping without a prompt.
        """
        _, data = self.run_case(mode='turnstile', verification_timeout_seconds=0)
        self.assertEqual(data['stop_reason'], 'verification_required')
        self.assertEqual(self.output, '')
        self.assertIsNone(data['analysis']['initial_verification'])

    def test_verification_interrupt_saves_results(self) -> None:
        """
        Checks Ctrl-C during verification saves the wait and its incomplete outcome.
        """
        with patch.object(Page, 'bring_to_front', side_effect=KeyboardInterrupt):
            recorder, data = self.run_case(mode='turnstile')
        self.assertEqual(data['stop_reason'], 'user_interrupted')
        self.assertFalse(data['analysis']['initial_verification']['completed'])
        self.assertEqual(data['analysis'], rebuild_report(recorder.directory)['analysis'])

    def test_verification_window_closed(self) -> None:
        """
        Checks closing the verification window saves a closed-tab outcome.
        """
        with patch.object(Page, 'bring_to_front', close_local_verification):
            _, data = self.run_case(mode='turnstile')
        self.assertEqual(data['stop_reason'], 'tab_closed', data.get('stop'))
        self.assertFalse(data['analysis']['initial_verification']['completed'])

    def test_verification_does_not_accept_another_collection(self) -> None:
        """
        Checks unrelated collection content does not resume the requested trial.
        """
        with patch.object(Page, 'bring_to_front', complete_local_verification):
            _, data = self.run_case(mode='turnstile_wrong_collection', verification_timeout_seconds=1.5)
        self.assertEqual(data['stop_reason'], 'verification_timeout', data.get('stop'))
        self.assertEqual(data['analysis']['totals']['item_attempts'], 0)

    def test_other_interference_still_stops(self) -> None:
        """
        Checks denials, supporting challenges, and later Turnstile pages still stop actions.
        """
        for mode, workflow, reason in (
            ('initial_denial', 'tabs', 'verification_required'),
            ('initial_challenge', 'tabs', 'challenge'),
            ('verification_supporting_challenge', 'tabs', 'challenge'),
            ('item_turnstile', 'tabs', 'verification_required'),
            ('return_turnstile', 'return', 'verification_required'),
        ):
            with self.subTest(mode=mode):
                recorder, data = self.run_case(workflow, mode, max_items=1)
                self.assertEqual(data['stop_reason'], reason, data.get('stop'))
                if mode == 'verification_supporting_challenge':
                    self.assertFalse(data['analysis']['initial_verification']['completed'])
                    self.assertEqual(data['analysis']['totals']['item_attempts'], 0)
                else:
                    self.assertEqual(self.output, '')
                stop = data['stop']
                self.assertFalse(
                    any(
                        event['kind'] in {'item_open', 'return_open', 'scroll_start'}
                        and event['event_id'] > stop['event_id']
                        for event in recorder.events
                    )
                )

    def test_widget_on_accessible_content_is_not_a_denial(self) -> None:
        """
        Checks a Turnstile widget beside expected collection content does not establish denial.
        """
        _, data = self.run_case(mode='turnstile_with_content', max_items=1)
        self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
        self.assertEqual(self.output, '')

    def test_unavailable_restoration_control_stops(self) -> None:
        """
        Checks a return without a usable page-size control saves an incomplete trial.
        """
        _, data = self.run_case('return', 'unsupported_restore', max_items=1)
        self.assertEqual(data['stop_reason'], 'missing_page_size_control', data.get('stop'))

    def test_time_limit_and_rebuild(self) -> None:
        """
        Checks interrupted viewing and identical counts rebuilt from saved events.
        """
        recorder, data = self.run_case(mode='time_limit', max_items=1, view_seconds=5, max_duration_seconds=0.7)
        self.assertEqual(data['stop_reason'], 'time_limit')
        self.assertEqual(data['analysis']['totals']['completed_views'], 0)
        rebuilt = rebuild_report(recorder.directory)
        self.assertEqual(data['analysis'], rebuilt['analysis'])
        self.assertIn('partial observation', (recorder.directory / 'summary.md').read_text())

    def test_user_interrupt_saves_results(self) -> None:
        """
        Checks KeyboardInterrupt preserves evidence and a readable report.
        """
        with patch('lib.browser_flow.view_item', side_effect=KeyboardInterrupt):
            recorder, data = self.run_case(max_items=1)
        self.assertEqual(data['stop_reason'], 'user_interrupted')
        self.assertTrue((recorder.directory / 'summary.md').exists())

    def test_redirect_requests_counted_separately(self) -> None:
        """
        Checks redirects add requests while retaining one item attempt.
        """
        recorder, data = self.run_case(mode='redirect', max_items=1)
        self.assertEqual(data['stop_reason'], 'workflow_complete', data.get('stop'))
        self.assertEqual(data['analysis']['totals']['item_attempts'], 1)
        self.assertEqual(data['analysis']['totals']['page_requests'], 3)
        self.assertTrue(any(event['kind'] == 'request' and event['redirected_from'] for event in recorder.events))
