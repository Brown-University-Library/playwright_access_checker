"""
Checks measurement boundaries and evidence classification with made-up events.
"""

import unittest

from lib.measurement import analyze, classify_response, planned_times, safe_url, select_items


class TestMeasurement(unittest.TestCase):
    def test_selection(self) -> None:
        """
        Checks both starting positions, repeated links, shorter lists, and the item limit.
        """
        urls = [str(index) for index in range(1, 51)]
        self.assertEqual([row['position'] for row in select_items(urls, 1, 20)], list(range(1, 40, 2)))
        self.assertEqual([row['position'] for row in select_items(urls, 2, 20)], list(range(2, 41, 2)))
        self.assertEqual(
            select_items(['a', 'a', 'b', 'c'], 1, 20), [{'position': 1, 'url': 'a'}, {'position': 3, 'url': 'c'}]
        )
        self.assertEqual(select_items(['a'], 2, 20), [])

    def test_repeatable_timing(self) -> None:
        """
        Checks repeatable independent timing sequences within requested bounds.
        """
        first = planned_times(42, 20, 1, 0.1, 5, 0.5)
        self.assertEqual(first, planned_times(42, 20, 1, 0.1, 5, 0.5))
        self.assertNotEqual(first, planned_times(43, 20, 1, 0.1, 5, 0.5))
        self.assertTrue(all(0.9 <= value <= 1.1 for value in first['opening_intervals']))
        self.assertTrue(all(4.5 <= value <= 5.5 for value in first['viewing_durations']))

    def test_url_privacy(self) -> None:
        """
        Checks removal of credentials, token values, and fragments while keeping listing settings.
        """
        url = safe_url('https://user:secret@example.test/item?token=hidden&page=1&per_page=50#private')
        for secret in ('user', 'secret', 'hidden', 'private'):
            self.assertNotIn(secret, url)
        self.assertIn('page=1&per_page=50', url)

    def test_verification_token_paths_are_removed(self) -> None:
        """
        Checks that verification-session tokens in URL paths are not retained.
        """
        for url in [
            'https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/secret-token',
            'https://example.test/cdn-cgi/challenge-platform/h/g/secret-token',
            'https://challenges.cloudflare.com/turnstile/v0/g/secret-token/api.js',
        ]:
            self.assertNotIn('secret-token', safe_url(url))
        self.assertEqual(
            safe_url('https://challenges.cloudflare.com/turnstile/v0/api.js'),
            'https://challenges.cloudflare.com/turnstile/v0/api.js',
        )

    def test_response_causes(self) -> None:
        """
        Checks that a Ray ID and HTTP 403 alone do not establish a Cloudflare cause.
        """
        self.assertIsNone(classify_response(200, {'cf-ray': 'example'}))
        self.assertEqual(classify_response(403, {'cf-ray': 'example'})['source'], 'unknown')
        self.assertEqual(classify_response(200, {'cf-mitigated': 'challenge'})['reason'], 'challenge')
        self.assertEqual(classify_response(429, {})['reason'], 'too_many_requests')
        self.assertEqual(classify_response(503, {})['reason'], 'http_error')

    def test_exact_boundaries_and_partial_periods(self) -> None:
        """
        Checks open lower boundaries, included zero, partial history, and unavailable marks.
        """
        events = [
            {
                'kind': 'request',
                'request_id': str(index),
                'elapsed': value,
                'included_host': True,
                'resource_type': 'document',
                'tab_id': None,
            }
            for index, value in enumerate([0, 12, 12.001, 30, 42, 42.1])
        ]
        result = analyze(events, 42)
        self.assertEqual(result['preceding_periods'][0]['all_bdr_requests'], 3)
        self.assertEqual(result['preceding_periods'][1]['all_bdr_requests'], 5)
        self.assertTrue(result['preceding_periods'][1]['partial'])
        self.assertEqual(result['totals_at_marks']['30']['all_bdr_requests'], 4)
        self.assertIsNone(result['totals_at_marks']['60'])
        result = analyze(events, 30)
        self.assertEqual(result['preceding_periods'][0]['all_bdr_requests'], 3)
        self.assertEqual(result['totals_at_marks']['30']['all_bdr_requests'], 4)

    def test_success_cutoff_and_request_rebinding(self) -> None:
        """
        Checks late success, unopened selections, tab attribution, and post-stop exclusion.
        """
        events = [
            {'kind': 'item_open', 'attempt_id': 'one', 'elapsed': 1},
            {'kind': 'item_ready', 'attempt_id': 'one', 'elapsed': 32},
            {
                'kind': 'request',
                'request_id': 'r1',
                'tab_id': None,
                'elapsed': 2,
                'included_host': True,
                'resource_type': 'image',
            },
            {'kind': 'request_tab', 'request_id': 'r1', 'tab_id': 'tab-2', 'elapsed': 5},
            {
                'kind': 'request',
                'request_id': 'r2',
                'tab_id': 'tab-2',
                'elapsed': 3,
                'included_host': True,
                'resource_type': 'image',
                'after_stop': True,
            },
        ]
        result = analyze(events, 30)
        self.assertEqual(result['totals']['item_attempts'], 1)
        self.assertEqual(result['totals']['item_successes'], 0)
        self.assertEqual(result['totals']['all_bdr_requests'], 1)
        self.assertEqual(result['breakdowns']['tab_id'], {'tab-2': 1})
        self.assertIsNone(result['opening_statistics'])

    def test_verification_keeps_real_counts_and_separates_later_browsing(self) -> None:
        """
        Checks verification traffic stays on the real timeline and later browsing is reported separately.
        """
        events = [
            {'kind': 'request', 'elapsed': 0, 'request_id': 'r1', 'included_host': True, 'resource_type': 'document'},
            {'kind': 'verification_start', 'elapsed': 0.1, 'local_time': 'verification start'},
            {'kind': 'request', 'elapsed': 1, 'request_id': 'r2', 'included_host': True, 'resource_type': 'fetch'},
            {'kind': 'verification_end', 'elapsed': 5.1, 'local_time': 'verification end', 'completed': True},
            {'kind': 'item_open', 'elapsed': 5.2, 'attempt_id': 'item-1'},
            {'kind': 'request', 'elapsed': 5.3, 'request_id': 'r3', 'included_host': True, 'resource_type': 'document'},
            {'kind': 'item_ready', 'elapsed': 5.4, 'attempt_id': 'item-1'},
            {'kind': 'stop', 'elapsed': 6, 'reason': 'workflow_complete'},
        ]
        result = analyze(events, 6)
        verification = result['initial_verification']
        self.assertEqual(result['totals']['all_bdr_requests'], 3)
        self.assertEqual(verification['duration_seconds'], 5)
        self.assertEqual(verification['requests_during_wait']['all_bdr_requests'], 1)
        self.assertEqual(verification['after_verification']['all_bdr_requests'], 1)
        self.assertEqual(verification['after_verification']['item_successes'], 1)
        self.assertAlmostEqual(verification['after_verification']['observed_seconds'], 0.9)
