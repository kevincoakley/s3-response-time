#!/usr/bin/env python

import sys
import unittest
from mock import patch
from moto import mock_s3

import s3_response_time


class TestMain(unittest.TestCase):
    def setUp(self):
        pass

    @mock_s3
    @patch("s3_response_time.upload_object")
    @patch("s3_response_time.get_object_etag")
    @patch("s3_response_time.md5")
    @patch("boto3.resource")
    @patch("os.remove")
    def test_main(
        self, mock_remove, mock_boto3_resource, mock_md5, mock_etag, mock_upload_object
    ):

        # Mock the remove function
        def mock_remove_function(path):
            if "downloaded" in path:
                return "ekaf"
            else:
                return "fake"

        # Mock the md5 function
        def mock_md5_function(path):
            if "downloaded" in path:
                return "ekaf"
            else:
                return "fake"

        #
        # Test with no issues
        #
        with patch.object(
            sys,
            "argv",
            ["s3_response_time.py", "-c", "./tests/test_files/credentials-good.json"],
        ):

            mock_md5.return_value = "fake"
            mock_etag.return_value = "fake"

            self.assertEqual(s3_response_time.main(), 0)

        #
        # Test uploaded md5 doesn't match etag
        #
        with patch.object(
            sys,
            "argv",
            ["s3_response_time.py", "-c", "./tests/test_files/credentials-good.json"],
        ):

            mock_md5.return_value = "fake"
            mock_etag.return_value = "ekaf"

            with self.assertRaises(SystemExit) as se:
                s3_response_time.main()
            self.assertEqual(se.exception.code, 2)

        #
        # Test uploaded md5 doesn't match downloaded md5
        #
        with patch.object(
            sys,
            "argv",
            ["s3_response_time.py", "-c", "./tests/test_files/credentials-good.json"],
        ):

            mock_md5.side_effect = mock_md5_function
            mock_etag.return_value = "fake"

            with self.assertRaises(SystemExit) as se:
                s3_response_time.main()
            self.assertEqual(se.exception.code, 2)
