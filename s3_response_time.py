#!/usr/bin/env python

import argparse
import boto3
import botocore
import hashlib
import json
import logging
import os
import sys
import time
import uuid

from distutils import util
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def write_to_influxdb(_url, _token, _org, _bucket, _host, _seconds):
    """
    Write the response time to Influxdb
    :param _url: Influxdb server URL as string
    :param _token: Influxdb auth token as string
    :param _org: Influxdb organization as string
    :param _bucket: Influxdb bucket as string
    :param _host: Name of the host being as string
    :param _seconds: Response time in seconds as float
    :return: None
    """
    point = Point("response_time").tag("host", _host).field("seconds", _seconds)

    try:
        client = InfluxDBClient(url=_url, token=_token, org=_org, verify_ssl=False)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=_bucket, record=point)
        client.close()
    except Exception as e:
        print("CRITICAL - Failed to write to influxdb: %s" % e)
        sys.exit(2)

    return None


def remove_file(_path):
    """
    Remove file
    :param _path: Path to file as string
    :return: None
    """
    try:
        os.remove(_path)
    except Exception as e:
        print("CRITICAL - Remove file error: %s" % e)
        sys.exit(2)

    return None


def create_random_file(_path, _file_size):
    """
    Create a random file
    :param _path: Path to file as string
    :param _file_size: Size of the random file in MB as int
    :return: None
    """
    try:
        with open(_path, "wb") as random_file:
            random_file.write(os.urandom(1024 * 1024 * _file_size))
        random_file.close()
    except Exception as e:
        print("CRITICAL - Create random file error: %s" % e)
        sys.exit(2)

    return None


def md5(_path):
    """
    Compute the md5 hash of a local file
    :param _path: local path to file as string
    :return: md5 hash of file as string
    """
    hash_md5 = hashlib.md5()
    try:
        with open(_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        print("CRITICAL - MD5 error: %s" % e)
        sys.exit(2)

    return hash_md5.hexdigest()


def get_object_etag(_s3, _bucket_name, _object_name):
    """
    Get the etag (md5 hash) of an object
    :param _s3: S3 boto3 resource
    :param _bucket_name: Name of the bucket where the object is stored as string
    :param _object_name: Name of the object as string
    :return: etag as string
    """
    try:
        etag = _s3.meta.client.head_object(Bucket=_bucket_name, Key=_object_name)[
            "ETag"
        ].replace('"', "")
    except botocore.exceptions.ClientError as e:
        print("CRITICAL - S3 ClientError: %s" % e)
        sys.exit(2)

    return etag


def delete_object(_object):
    """
    Delete and object from S3
    :param _object: boto3 object object
    :return: None
    """
    try:
        _object.delete()
        print("delete_object: Ok")
    except botocore.exceptions.ClientError as e:
        print("CRITICAL - S3 ClientError: %s" % e)
        sys.exit(2)

    return None


def download_object(_s3, _bucket_name, _object_name, _download_name, _path="/tmp"):
    """
    Download an object from S3
    :param _s3: S3 boto3 resource
    :param _bucket_name: Name of the bucket where the object is stored as string
    :param _object_name: Name of the object as string
    :param _download_name: Local filename of the downloaded object as string
    :param _path: Local path to store the downloaded object as string
    :return: None
    """
    try:
        _s3.Object(_bucket_name, _object_name).download_file(
            "%s/%s" % (_path, _download_name)
        )
    except botocore.exceptions.ClientError as e:
        print("CRITICAL - S3 ClientError: %s" % e)
        sys.exit(2)

    return None


def upload_object(_s3, _bucket_name, _object_name, _path="/tmp"):
    """
    Upload object to S3
    :param _s3: S3 boto3 resource
    :param _bucket_name: Name of the bucket to store the object as string
    :param _object_name: Filename of the object as string
    :param _path: Local path to the object as string
    :return: Boto3 object object
    """
    try:
        _s3.Object(_bucket_name, _object_name).put(
            Body=open("%s/%s" % (_path, _object_name), "rb")
        )
        uploaded_object = _s3.Object(_bucket_name, _object_name)
    except botocore.exceptions.ClientError as e:
        print("CRITICAL - S3 ClientError: %s" % e)
        sys.exit(2)
    except FileNotFoundError as e:
        print("CRITICAL - FileNotFoundError: %s" % e)
        sys.exit(2)

    return uploaded_object


def create_bucket(_s3, _name, configuration=None):
    """
    Create a S3 bucket
    :param _s3: S3 boto3 resource
    :param _name: name of bucket to create as string
    :param configuration: CreateBucketConfiguration as dict
    :return: S3 boto3 bucket object
    """
    try:
        if configuration is None:
            bucket = _s3.create_bucket(Bucket=_name)
        else:
            bucket = _s3.create_bucket(
                Bucket=_name, CreateBucketConfiguration=configuration
            )
        print("create_bucket: Ok")
    except botocore.exceptions.ParamValidationError as e:
        print("CRITICAL - S3 ParamValidationError: %s" % e)
        sys.exit(2)
    except botocore.exceptions.ClientError as e:
        print("CRITICAL - S3 ClientError: %s" % e)
        sys.exit(2)
    except TypeError as e:
        print("CRITICAL - S3 bucket TypeError: %s" % e)
        sys.exit(2)

    return bucket


def delete_bucket(_bucket):
    """
    Delete a S3 bucket
    :param _bucket: boto3 Bucket object
    :return: None
    """
    try:
        _bucket.delete()
        print("delete_bucket: Ok")
    except botocore.exceptions.ClientError as e:
        print("CRITICAL - S3 ClientError: %s" % e)
        sys.exit(2)

    return None


def read_configuration(_path):
    """
    Read the configuration JSON file
    :param _path: local path to configuration JSON file as string
    :return: Decoded contents of path as hash
    """
    default_configuration = {
        "s3_host": "https://localhost:443",
        "aws_access_key_id": "",
        "aws_secret_access_key": "",
        "addressing_style": "auto",
        "object_size": "1",
        "create_bucket": "True",
        "bucket_name": "",
        "influxdb_enabled": "False",
        "influxdb_url": "http://localhost:8086",
        "influxdb_token": "",
        "influxdb_org": "",
        "influxdb_bucket": "",
        "influxdb_host": "",
    }

    # Read the configuration file
    try:
        with open(_path, "r") as f:
            file_configuration = json.load(f)
    except FileNotFoundError as e:
        print("CRITICAL - No Credentials Found: %s" % e)
        sys.exit(2)
    except json.decoder.JSONDecodeError as e:
        print("CRITICAL - Could Not Decode Credentials JSON: %s" % e)
        sys.exit(2)

    # Merge the default config with the file config
    configuration = {**default_configuration, **file_configuration}

    return configuration


def s3_auth(
    _aws_access_key_id, _aws_secret_access_key, _s3_host, _addressing_style="auto"
):
    """
    Authenticate to S3
    :param _aws_access_key_id: AWS access key
    :param _aws_secret_access_key: AWS secret key
    :param _s3_host: S3 host
    :param _addressing_style: S3 addressing style: 'auto', 'path' or 'virtual'
    :return: S3 boto3 resource object
    """
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=_aws_access_key_id,
        aws_secret_access_key=_aws_secret_access_key,
        endpoint_url=_s3_host,
        config=botocore.client.Config(
            signature_version="s3", s3={"addressing_style": _addressing_style}
        ),
    )

    return s3


def parse_arguments(_args):
    """
    Parse Commandline Arguments
    :param _args: *args positional arguments
    :return: Commandline arguments parsed by argparse
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        metavar="configuration_file",
        dest="configuration_file",
        help="File that contains the configuration.",
        required=True,
    )

    return parser.parse_args(_args)


def main():
    # Set the default logger. Use logging.DEBUG for connection details
    boto3.set_stream_logger("", logging.INFO)

    args = parse_arguments(sys.argv[1:])

    configuration = read_configuration(args.configuration_file)

    if configuration["bucket_name"] == "":
        bucket_name = str(uuid.uuid4())
    else:
        bucket_name = configuration["bucket_name"]
    object_name = str(uuid.uuid4())
    download_name = "%s-downloaded" % object_name
    object_size = int(configuration["object_size"])

    start_time = time.time()

    aws_access_key_id = configuration["aws_access_key_id"]
    aws_secret_access_key = configuration["aws_secret_access_key"]
    s3_host = configuration["s3_host"]
    addressing_style = configuration["addressing_style"]

    s3 = s3_auth(aws_access_key_id, aws_secret_access_key, s3_host, addressing_style)

    # Create the s3 bucket if create_bucket is True
    if bool(util.strtobool(configuration["create_bucket"])):
        bucket = create_bucket(s3, bucket_name)

    # Create random file
    create_random_file("/tmp/%s" % object_name, object_size)

    # Get md5 hash of the random file
    local_md5sum = md5("/tmp/%s" % object_name)

    # Upload the random file
    uploaded_object = upload_object(s3, bucket_name, object_name)

    # Get the etag of the uploaded random file
    etag = get_object_etag(s3, bucket_name, object_name)

    # Verify the original and s3 md5 hashes match
    if local_md5sum == etag:
        print("upload_object: Ok")
    else:
        print("CRITICAL - Upload Object Failed: %s %s" % (local_md5sum, etag))
        sys.exit(2)

    # Remove random file
    remove_file("/tmp/%s" % object_name)

    # Download the object
    download_object(s3, bucket_name, object_name, download_name)

    # Get md5 hash of the downloaded file
    download_md5sum = md5("/tmp/%s" % download_name)

    # Verify the original and downloaded md5 hashes match
    if local_md5sum == download_md5sum:
        print("download_object: Ok")
    else:
        print("CRITICAL - Download Object Failed: %s %s" % (local_md5sum, etag))
        sys.exit(2)

    # Remove downloaded file
    remove_file("/tmp/%s" % download_name)

    # Delete Object
    delete_object(uploaded_object)

    # Delete Bucket if create_bucket is True
    if bool(util.strtobool(configuration["create_bucket"])):
        delete_bucket(bucket)

    # Calculate the total time
    end_time = time.time()
    total_time = end_time - start_time

    # If influxdb_enabled is True in the config file the write the response
    # time to influxdb
    if bool(util.strtobool(configuration["influxdb_enabled"])):
        write_to_influxdb(
            configuration["influxdb_url"],
            configuration["influxdb_token"],
            configuration["influxdb_org"],
            configuration["influxdb_bucket"],
            configuration["influxdb_host"],
            total_time,
        )

    print("OK - total_time: %s" % total_time)
    return 0


if __name__ == "__main__":
    sys.exit(main())
