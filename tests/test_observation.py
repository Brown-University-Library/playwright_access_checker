"""
Checks verification time limits using a controlled monotonic clock.
"""

import tempfile
import unittest
from unittest.mock import Mock, patch

from lib.config import Settings
from lib.observation import Observer, TrialStopped
from lib.results import Recorder


class TestObservation(unittest.TestCase):
    def setUp(self) -> None:
        """
        Checks the observer with local output and no browser or network calls.
        """
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        settings = Settings(
            output_dir=self.temp.name,
            workflow='tabs',
            max_duration_seconds=4,
            navigation_timeout_seconds=2,
            verification_timeout_seconds=5,
        )
        self.recorder = Recorder(settings)
        self.addCleanup(self.recorder.stream.close)
        self.observer = Observer(Mock(), settings, self.recorder)
        self.recorder.started = 100
        self.observer.verification_started = 101

    def test_wait_does_not_consume_trial_or_navigation_budget(self) -> None:
        """
        Checks active waiting preserves both budgets even beyond the normal trial limit.
        """
        self.observer.verification_page = Mock()
        with patch('lib.observation.time.monotonic', return_value=105):
            self.observer.guard()
            self.assertEqual(self.observer.active_seconds(), 1)
            self.assertEqual(self.observer.timeout_ms(), 2000)
        self.assertIsNone(self.recorder.stopped)

    def test_completed_wait_extends_limit_without_changing_event_clock(self) -> None:
        """
        Checks completed verification is excluded from the limit and retained in elapsed time.
        """
        self.observer.verification_ended = 106
        with patch('lib.observation.time.monotonic', return_value=108):
            self.observer.guard()
            self.assertEqual(self.observer.active_seconds(), 3)
            self.assertEqual(self.observer.timeout_ms(), 1000)
        with patch('lib.observation.time.monotonic', return_value=109), self.assertRaises(TrialStopped):
            self.observer.guard()
        self.assertEqual(self.recorder.metadata['stop_reason'], 'time_limit')
        self.assertEqual(self.recorder.metadata['observed_seconds'], 9)

    def test_verification_has_its_own_limit(self) -> None:
        """
        Checks the verification deadline stops the wait with the original response evidence.
        """
        self.observer.verification_page = Mock()
        self.observer.verification_evidence = {'status': 200, 'request_id': 'request-1'}
        with patch('lib.observation.time.monotonic', return_value=106), self.assertRaises(TrialStopped):
            self.observer.guard()
        self.assertEqual(self.recorder.metadata['stop_reason'], 'verification_timeout')
        self.assertEqual(self.recorder.metadata['stop']['request_id'], 'request-1')
