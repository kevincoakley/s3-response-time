#!/usr/bin/env python

import unittest

import s3_response_time


class ArgumentsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_arguments(self):
        args = s3_response_time.parse_arguments(["-c", "configuration_file.json"])
        self.assertEqual(args.configuration_file, "configuration_file.json")
