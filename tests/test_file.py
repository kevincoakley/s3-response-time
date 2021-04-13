#!/usr/bin/env python

import errno
import os
import unittest
from mock import patch

import s3_response_time


class FileTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_file(self):
        # Test create_random_file with no issues
        s3_response_time.create_random_file("/tmp/fake", 1)
        self.assertEqual(os.path.getsize("/tmp/fake"), 1048576)

        # Test remove_file with no issues
        s3_response_time.remove_file("/tmp/fake")
        self.assertFalse(os.path.isfile("/tmp/fake"))

        #
        # Test create_random_file with an io exception
        #
        with patch("builtins.open", create=True) as mock_open:
            mock_open.side_effect = OSError(
                errno.EIO, os.strerror(errno.EIO), "io_error"
            )

            with self.assertRaises(SystemExit) as se:
                s3_response_time.create_random_file("/tmp/fake", 1)
            self.assertEqual(se.exception.code, 2)

        #
        # Test remove_file with an io exception
        #
        with patch("os.remove") as mock_remove:
            mock_remove.side_effect = OSError(
                errno.EIO, os.strerror(errno.EIO), "io_error"
            )

            with self.assertRaises(SystemExit) as se:
                s3_response_time.remove_file("/tmp/fake")
            self.assertEqual(se.exception.code, 2)

        # Test the md5 hash calculation on an actual file
        md5_hash = s3_response_time.md5("./tests/test_files/md5.txt")
        self.assertEqual(md5_hash, "ddb4502f21d869c1059d4adba77bee6d")

        #
        # Test create_random_file with an io exception
        #
        with patch("builtins.open", create=True) as mock_open:
            mock_open.side_effect = OSError(
                errno.EIO, os.strerror(errno.EIO), "io_error"
            )

            with self.assertRaises(SystemExit) as se:
                s3_response_time.md5("/tmp/fake")
            self.assertEqual(se.exception.code, 2)
