#!/usr/bin/env python

import boto3
import unittest
from mock import patch
from moto import mock_s3

import s3_response_time


class S3TestCase(unittest.TestCase):
    def setUp(self):
        pass

    @patch("boto3.resource")
    def test_auth(self, fake_boto3_resource):
        s3_response_time.s3_auth("fake", "fake", "fake.site")

    @mock_s3
    def test_bucket(self):
        s3 = boto3.resource("s3", region_name="us-west-2")
        bucket_config = {"LocationConstraint": "us-west-2"}

        # Test creating a bucket
        bucket = s3_response_time.create_bucket(s3, "test-bucket", bucket_config)
        self.assertEqual(bucket.name, "test-bucket")

        # Test ParamValidationError when creating bucket
        with self.assertRaises(SystemExit) as se:
            s3_response_time.create_bucket(s3, "test bucket", bucket_config)
        self.assertEqual(se.exception.code, 2)

        # Test ClientError when creating bucket
        with self.assertRaises(SystemExit) as se:
            s3_response_time.create_bucket(s3, "test-bucket", bucket_config)
        self.assertEqual(se.exception.code, 2)

        # Test TypeError when creating bucket
        with self.assertRaises(SystemExit) as se:
            s3_response_time.create_bucket(s3, 1, bucket_config)
        self.assertEqual(se.exception.code, 2)

        # Test deleting a bucket
        s3_response_time.delete_bucket(bucket)
        num_buckets = len([bucket.name for bucket in s3.buckets.all()])
        self.assertEqual(num_buckets, 0)

        # Test deleting a bucket that doesn't exist
        with self.assertRaises(SystemExit) as se:
            s3_response_time.delete_bucket(bucket)
        self.assertEqual(se.exception.code, 2)

    @mock_s3
    def test_object(self):
        s3 = boto3.resource("s3", region_name="us-east-1")

        bucket = s3_response_time.create_bucket(s3, "test-bucket")

        # Test uploading an object
        uploaded_object = s3_response_time.upload_object(
            s3, "test-bucket", "md5.txt", "./tests/test_files"
        )
        self.assertEqual(uploaded_object.key, "md5.txt")

        # Test FileNotFoundError when uploading an object
        with self.assertRaises(SystemExit) as se:
            s3_response_time.upload_object(s3, "test-bucket", "md5.txt")
        self.assertEqual(se.exception.code, 2)

        # Test ClientError when uploading an object
        with self.assertRaises(SystemExit) as se:
            s3_response_time.upload_object(
                s3, "missing-bucket", "md5.txt", "./tests/test_files"
            )
        self.assertEqual(se.exception.code, 2)

        # Test getting the etag of an object
        etag = s3_response_time.get_object_etag(s3, "test-bucket", "md5.txt")
        self.assertEqual(etag, "ddb4502f21d869c1059d4adba77bee6d")

        # Test ClientError when getting the etag of an object
        with self.assertRaises(SystemExit) as se:
            s3_response_time.get_object_etag(s3, "test-bucket", "fake.txt")
        self.assertEqual(se.exception.code, 2)

        # Test downloading an object
        s3_response_time.download_object(s3, "test-bucket", "md5.txt", "test-md5.txt")

        # Test ClientError when downloading an object
        with self.assertRaises(SystemExit) as se:
            s3_response_time.download_object(
                s3, "missing-bucket", "md5.txt", "test-md5.txt"
            )
        self.assertEqual(se.exception.code, 2)

        # Test deleting an object
        s3_response_time.delete_object(uploaded_object)
        num_objects = len([obj.key for obj in bucket.objects.all()])
        self.assertEqual(num_objects, 0)

        # Test ClientError when deleting an object
        with self.assertRaises(SystemExit) as se:
            bad_object = s3.Object("bucket_name", "key")
            s3_response_time.delete_object(bad_object)
        self.assertEqual(se.exception.code, 2)
