# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
This module defines the base class for ai_chatter applications.
"""

try:
    from bs4 import BeautifulSoup
    from markdownify import MarkdownConverter, markdownify
    from requests_html import HTMLSession
except ImportError as e:
    from ai_chatter.__about__ import __app_name__

    msg = f"Please install {__app_name__} with the optional web dependencies to enable this module. You can do so, by running `pip install {__app_name__}[web]` from the command line."
    raise ImportError(msg) from e

from ai_chatter.apps.base import Application


def md(soup: BeautifulSoup, **kwargs):
    """Shorthand for HTML -> Markdown conversion."""
    return MarkdownConverter(**kwargs).convert_soup(soup)


class SummarizePage(Application):
    """Summarize the contents of a webpage."""

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        """Scrape a web page and let ChatGPT provide a summary."""
        # get page and render js
        with HTMLSession() as session:
            response = session.get(self.url, allow_redirects=True)
            response.html.render()
            html = response.html.raw_html

        # cleanup content
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find("main")
        if main is not None:
            soup = main
        remove_tags = ["script", "style", "header", "footer", "nav", "input", "textarea", "img"]
        for remove_tag in remove_tags:
            for tag in soup.select(remove_tag):
                tag.decompose()
        for code in soup.select("code"):
            code.unwrap()

        # turn into markdown
        raw_markdown = markdownify(soup.text).strip()

        # filter consecutive empty lines
        lines = []
        was_empty = True
        for line in raw_markdown.splitlines():
            is_empty = line.strip() == ""
            if not (is_empty and was_empty):
                lines.append(line)
            was_empty = is_empty

        markdown = "\n".join(lines)
        print(markdown)  # noqa
