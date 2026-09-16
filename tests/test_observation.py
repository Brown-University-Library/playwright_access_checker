"""
Checks tab matching when initial item requests are absent.
"""

import tempfile
import unittest
from unittest.mock import Mock

from playwright.sync_api import BrowserContext, Page

from lib.config import Settings
from lib.observation import Attempt, Observer
from lib.results import Recorder


class TestObservation(unittest.TestCase):
    def setUp(self) -> None:
        """
        Checks matching with simulated tabs and local event recording.
        """
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.recorder = Recorder(Settings(output_dir=self.temp.name, workflow='tabs'))
        self.addCleanup(self.recorder.stream.close)
        self.observer = Observer(Mock(spec=BrowserContext), Settings(workflow='tabs'), self.recorder)

    def make_page(self, url: str) -> Mock:
        """
        Checks a tab has a known URL and remains open.
        """
        page = Mock(spec=Page)
        page.url = url
        page.is_closed.return_value = False
        self.observer.on_page(page)
        return page

    def test_matches_urls_when_tabs_arrive_out_of_order(self) -> None:
        """
        Checks each item gets its own tab even when a later item loads first.
        """
        first = Attempt('item-1', 'https://example.test/studio/item/bdr:1/', 0)
        second = Attempt('item-2', 'https://example.test/studio/item/bdr:2/', 0)
        self.observer.attempts = [first, second]
        second_page = self.make_page(second.url)
        first_page = self.make_page(first.url)
        self.observer.bind_requests()
        self.observer.bind_requests()
        self.assertIs(first.page, first_page)
        self.assertIs(second.page, second_page)
        self.assertEqual(sum(event['kind'] == 'attempt_tab' for event in self.recorder.events), 2)

    def test_ambiguous_or_closed_tabs_are_not_assigned(self) -> None:
        """
        Checks matching waits for one usable tab instead of guessing between duplicates.
        """
        attempt = Attempt('item-1', 'https://example.test/studio/item/bdr:1/', 0)
        self.observer.attempts = [attempt]
        first = self.make_page(attempt.url)
        second = self.make_page(attempt.url)
        self.observer.bind_requests()
        self.assertIsNone(attempt.page)
        first.is_closed.return_value = True
        self.observer.bind_requests()
        self.assertIs(attempt.page, second)

    def test_does_not_reuse_another_attempts_tab(self) -> None:
        """
        Checks a tab already assigned to one attempt cannot be claimed by another.
        """
        url = 'https://example.test/studio/item/bdr:1/'
        page = self.make_page(url)
        first = Attempt('item-1', url, 0, page=page)
        second = Attempt('item-2', url, 0)
        self.observer.attempts = [first, second]
        self.observer.bind_requests()
        self.assertIsNone(second.page)
