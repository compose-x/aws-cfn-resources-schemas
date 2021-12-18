#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@compose-x.io>

import re
import json
import os
import sys
from os import environ, path
from tempfile import TemporaryDirectory
from argparse import ArgumentParser

try:
    import requests
except ImportError:
    print("You need to install requests for this script to work")
    sys.exit(1)

try:
    import zipfile
except ImportError:
    print("Failed to import zipfile. Cannot retrieve latest SAM translator release")
    sys.exit(1)


def download_url(url, save_path, chunk_size=128):
    """
    Pulls RAW using requests

    :param str url:
    :param str save_path:
    :param int chunk_size:
    :return:
    """
    r = requests.get(url, stream=True)
    with open(save_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def generate_resources_mapping(files_path):
    """
    Simple function to create a resource type to schema path mapping

    :param str files_path:
    :return: The mapping between a given AWS Resource and the JSON Schema path for it.
    :rtype: dict
    """
    files = os.listdir(files_path)
    resource_types_mapping = {}
    ignore_py = re.compile(r".*\.(py|pyc)$")
    for file in files:
        if file == "aws_cfn_resources_schemas.json" or ignore_py.match(file):
            continue
        elif not path.isfile(path.abspath(f"{files_path}/{file}")):
            continue
        with open(path.abspath(f"{files_path}/{file}"), "r") as schema_fd:
            content = schema_fd.read()
            try:
                content_dict = json.loads(content)
                resource_type = content_dict["typeName"]
                resource_types_mapping[resource_type] = path.basename(file)
            except KeyError:
                print(file, "No typeName", content_dict.keys())
            except json.JSONDecodeError:
                pass
    return resource_types_mapping


def main(schemas_zip_url):
    """
    Download schemas from AWS Official source and expands to source code

    :param str schemas_zip_url:
    """
    here = path.abspath(path.dirname(__file__))
    tmp_dir = TemporaryDirectory()
    zip_file_path = f"{tmp_dir.name}/schemas.zip"
    download_url(schemas_zip_url, zip_file_path)
    dest_path = path.abspath(f"{here}/aws_cfn_resources_schemas/")
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(dest_path)

    resources_file_mapping = generate_resources_mapping(dest_path)
    with open(f"{dest_path}/aws_cfn_resources_schemas.json", "w") as schemas_fd:
        schemas_fd.write(json.dumps(resources_file_mapping, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser("Initialize AWS CFN Schemas files for library")
    parser.add_argument(
        "--schemas-zip-url",
        type=str,
        default=environ.get(
            "CFN_SCHEMAS_URL",
            "https://schema.cloudformation.eu-west-1.amazonaws.com/CloudformationSchema.zip",
        ),
        required=False,
    )
    args = parser.parse_args()
    main(args.schemas_zip_url)
