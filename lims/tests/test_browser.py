"""Test LIMS browser interface."""

import re

from playwright.sync_api import expect


def test_has_title(page):
    page.goto("http://127.0.0.1:5000/")
    expect(page).to_have_title(re.compile("LIMS"))
