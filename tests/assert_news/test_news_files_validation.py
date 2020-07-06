#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
from unittest import TestCase, mock

from mbed_tools_ci_scripts.assert_news import find_news_files, validate_news_files
from mbed_tools_ci_scripts.utils.git_helpers import GitWrapper


class TestFindNewsFiles(TestCase):
    def test_returns_newly_added_news_files(self):
        """Given added files in git, it returns absolute paths to added news files."""
        fake_git_wrapper = mock.Mock(spec_set=GitWrapper)
        fake_git_wrapper.list_files_added_on_current_branch.return_value = [
            "foo/bar.py",
            "news/1234.txt",
            "news/wat.html",
        ]
        news_dir = "news/"
        root_dir = "/root/"

        subject = find_news_files(git=fake_git_wrapper, root_dir=root_dir, news_dir=news_dir, uncommitted=False)

        self.assertEqual(
            subject, [str(pathlib.Path(root_dir, "news/1234.txt")), str(pathlib.Path(root_dir, "news/wat.html"))]
        )

    def test_returns_uncommitted_news_files_as_str(self):
        """Given added files in git, it returns absolute paths to added news files."""
        fake_git_wrapper = mock.Mock(spec_set=GitWrapper)
        fake_git_wrapper.uncommitted_changes_as_str.return_value = [
            "foo/bar.py",
            "news/1234.txt",
            "news/wat.html",
        ]
        news_dir = "news/"
        root_dir = "/root/"

        subject = find_news_files(git=fake_git_wrapper, root_dir=root_dir, news_dir=news_dir, uncommitted=True)

        self.assertEqual(
            subject, [str(pathlib.Path(root_dir, "news/1234.txt")), str(pathlib.Path(root_dir, "news/wat.html"))]
        )


class TestValidateNewsFiles(TestCase):
    @mock.patch("mbed_tools_ci_scripts.assert_news.find_news_files")
    def test_raises_when_theres_no_news_files(self, find_news_files):
        find_news_files.return_value = []
        news_dir = "some/path"

        with self.assertRaises(FileNotFoundError) as cm:
            validate_news_files(
                git=mock.Mock(spec_set=GitWrapper), root_dir="/does-not-matter/", news_dir=news_dir, uncommitted=False
            )

        expected_error_message = f"PR must contain a news file in {news_dir}. See README.md."
        self.assertEqual(str(cm.exception), expected_error_message)

    @mock.patch("mbed_tools_ci_scripts.assert_news.find_news_files")
    @mock.patch("mbed_tools_ci_scripts.assert_news.validate_news_file")
    def test_checks_each_news_file(self, validate_news_file, find_news_files):
        find_news_files.return_value = ["a"]
        git_wrapper = mock.Mock(spec_set=GitWrapper)
        news_dir = "some/dir"
        root_dir = "/does-not-matter"

        validate_news_files(git=git_wrapper, root_dir=root_dir, news_dir=news_dir, uncommitted=False)

        find_news_files.assert_called_once_with(
            git=git_wrapper, root_dir=root_dir, news_dir=news_dir, uncommitted=False
        )
        validate_news_file.assert_called_with("a")
