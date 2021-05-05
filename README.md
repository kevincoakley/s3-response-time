# s3-response-time

[![Python package](https://github.com/kevincoakley/s3-response-time/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/kevincoakley/s3-response-time/actions/workflows/pythonpackage.yml)
[![Lint](https://github.com/kevincoakley/s3-response-time/actions/workflows/black.yml/badge.svg)](https://github.com/kevincoakley/s3-response-time/actions/workflows/black.yml)
[![Code Coverage](https://codecov.io/gh/kevincoakley/s3-response-time/branch/master/graph/badge.svg)](https://codecov.io/gh/kevincoakley/s3-response-time/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python script to record the time it takes to preform various operations on an
S3 object storage. Errors are reported in Nagios format. Script tested with 
Python 3.6 and 3.8.

Tested S3 operations:

* Create random or specific bucket (optional)
* Upload random object of a specified size (default 1MB)
* Compare original file MD5 hash to Etag 
* Download object
* Compare original file MD5 hash to downloaded file MD5 hash
* Delete random object
* Delete random or specific bucket (optional)

Example command:

    ./s3_response_time.py -c credentials.json

Example configuration file:

    {
      "s3_host": "https://server.com",          # Required
      "aws_access_key_id": "abcdefghijklmnop",  # Required
      "aws_secret_access_key": "1234567890ab",  # Required
                                                # Everything below is optional; defaults shown
      "addressing_style": "auto",               # S3 addressing style, options: 'auto', 'path', 'virtual'
      "object_size": "1",                       # Size of the object upload in MB 
      "create_bucket": "True",                  # Create bucket; if False bucket must already exist
      "bucket_name": "",                        # Omit for random bucket name
      "influxdb_enabled": "False",              # True to enable writing to influxb
      "influxdb_url": "http://localhost:8086",  # Influxdb server url
      "influxdb_token": "",                     # Influxdb auth token
      "influxdb_org": "",                       # Influxdb orgization where the data is saved
      "influxdb_bucket": "",                    # Influxdb bucket where the data is saved
      "influxdb_host": ""                       # Influxdb tag that will be assigned to the data
    }