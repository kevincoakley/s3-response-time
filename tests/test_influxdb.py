#!/usr/bin/env python

import influxdb_client
import unittest
import random
from mock import patch

import s3_response_time


class InfluxdbTestCase(unittest.TestCase):
    def setUp(self):
        pass

    @patch.object(influxdb_client.InfluxDBClient, "write_api")
    def test_write(self, fake_client):
        url = "http://fake:8086"
        token = "fake-token"
        org = "fake-org"
        bucket = "fake-bucket"
        host = "fake-host"
        seconds = random.random()

        # Test writing to influxdb
        write = s3_response_time.write_to_influxdb(
            url, token, org, bucket, host, seconds
        )

        self.assertEqual(write, None)

        # Test ApiException when writing to influxdb
        fake_client.side_effect = influxdb_client.rest.ApiException

        with self.assertRaises(SystemExit) as se:
            s3_response_time.write_to_influxdb(url, token, org, bucket, host, seconds)
        self.assertEqual(se.exception.code, 2)
