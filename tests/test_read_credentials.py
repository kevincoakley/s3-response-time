#!/usr/bin/env python

import unittest

import s3_response_time


class ReadCredentialsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_good_credentials(self):
        credentials = {
            "s3_host": "https://server.com",
            "aws_access_key_id": "abcdefghijklmnopqrstuvwxyz123456",
            "aws_secret_access_key": "1234567890abcdefghijklmnopqrstuv",
        }

        read_credentials = s3_response_time.read_credentials(
            "./tests/test_files/credentials-good.json"
        )
        self.assertEqual(credentials, read_credentials)

    def test_bad_json(self):
        with self.assertRaises(SystemExit) as se:
            s3_response_time.read_credentials("./tests/test_files/credentials-bad.json")
        self.assertEqual(se.exception.code, 2)

    def test_no_file(self):
        with self.assertRaises(SystemExit) as se:
            s3_response_time.read_credentials("./tests/test_files/missing.json")
        self.assertEqual(se.exception.code, 2)
