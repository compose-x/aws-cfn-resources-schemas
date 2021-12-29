#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille <john@compose-x.io>

"""Top-level package for AWS CFN Resources Schemas."""

__author__ = """John Preston"""
__email__ = "john@compose-x.io"
__version__ = "2021.12.29"

import json
import warnings
from os import path

try:
    from importlib_resources import files as pkg_files

    HERE = path.abspath(pkg_files("aws_cfn_resources_schemas").joinpath(""))
except ImportError:
    warnings.warn("Using strictly relative paths")
    HERE = path.abspath(path.dirname(__file__))


with open(f"{HERE}/aws_cfn_resources_schemas.json", "r") as schemas_mappings_fd:
    SCHEMAS_MAPPINGS = json.loads(schemas_mappings_fd.read())


def get_resource_schema(resource_type, raw=False):
    """
    Function to get the schema definition for a given CFN Resource

    :param str resource_type: The AWS resource type, i.e. AWS::ECS::Cluster
    :param bool raw: If true, returns the JSON file content, does not json.loads() for return.
    :return: The schema definition.
    """
    if resource_type not in SCHEMAS_MAPPINGS:
        raise KeyError(
            f"{resource_type} not found in AWS Resources schemas. Available",
            SCHEMAS_MAPPINGS.keys(),
        )
    resource_schema_file = SCHEMAS_MAPPINGS[resource_type]
    with open(f"{HERE}/{resource_schema_file}") as resource_fd:
        if raw:
            return resource_fd.read()
        return json.loads(resource_fd.read())


def validate_resource_against_definition(resource_type: str, resource_definition: str):
    """
    Function to validate a given AWS CFN resource definition against the schema

    :param str resource_type:
    :param str resource_definition:
    """
    try:
        from jsonschema import validate
    except ImportError:
        warnings.warn("Install JSON schema to use schema validations functions")
        return
    schema = get_resource_schema(resource_type)
    validate(instance=resource_definition, schema=schema)
