#!/usr/bin/env python

import unittest

import s3_response_time


class ReadConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_good_credentials(self):
        configuration = {
            "s3_host": "https://server.com",
            "aws_access_key_id": "abcdefghijklmnopqrstuvwxyz123456",
            "aws_secret_access_key": "1234567890abcdefghijklmnopqrstuv",
            "object_size": "1",
            "bucket_name": "",
            "influxdb_enabled": "False",
            "influxdb_url": "http://localhost:8086",
            "influxdb_token": "",
            "influxdb_org": "",
            "influxdb_bucket": "",
            "influxdb_host": "",
        }

        read_configuration = s3_response_time.read_configuration(
            "./tests/test_files/configuration-good.json"
        )
        self.assertEqual(configuration, read_configuration)

    def test_bad_json(self):
        with self.assertRaises(SystemExit) as se:
            s3_response_time.read_configuration(
                "./tests/test_files/configuration-bad.json"
            )
        self.assertEqual(se.exception.code, 2)

    def test_no_file(self):
        with self.assertRaises(SystemExit) as se:
            s3_response_time.read_configuration("./tests/test_files/missing.json")
        self.assertEqual(se.exception.code, 2)
