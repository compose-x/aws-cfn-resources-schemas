"""
Testing basic functions
"""
import json

import pytest
from aws_cfn_resources_schemas import (
    get_resource_schema,
    validate_resource_against_definition,
)


@pytest.fixture()
def dynamodb_table():
    """
    Table from AWS Docs examples
    """
    return {
        "AttributeDefinitions": [
            {"AttributeName": "Album", "AttributeType": "S"},
            {"AttributeName": "Artist", "AttributeType": "S"},
            {"AttributeName": "Sales", "AttributeType": "N"},
            {"AttributeName": "NumberOfSongs", "AttributeType": "N"},
        ],
        "KeySchema": [
            {"AttributeName": "Album", "KeyType": "HASH"},
            {"AttributeName": "Artist", "KeyType": "RANGE"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        "TableName": "myTableName",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "myGSI",
                "KeySchema": [
                    {"AttributeName": "Sales", "KeyType": "HASH"},
                    {"AttributeName": "Artist", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "NonKeyAttributes": ["Album", "NumberOfSongs"],
                    "ProjectionType": "INCLUDE",
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
            {
                "IndexName": "myGSI2",
                "KeySchema": [
                    {"AttributeName": "NumberOfSongs", "KeyType": "HASH"},
                    {"AttributeName": "Sales", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "NonKeyAttributes": ["Album", "Artist"],
                    "ProjectionType": "INCLUDE",
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
        ],
        "LocalSecondaryIndexes": [
            {
                "IndexName": "myLSI",
                "KeySchema": [
                    {"AttributeName": "Album", "KeyType": "HASH"},
                    {"AttributeName": "Sales", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "NonKeyAttributes": ["Artist", "NumberOfSongs"],
                    "ProjectionType": "INCLUDE",
                },
            }
        ],
    }


def test_resource_schema_import():
    assert isinstance(get_resource_schema("AWS::ECS::Cluster", raw=True), str)
    schema_definition = get_resource_schema("AWS::ECS::Cluster")
    assert (
        json.loads(get_resource_schema("AWS::ECS::Cluster", raw=True))
        == schema_definition
    )


def test_resource_schema(dynamodb_table):
    validate_resource_against_definition("AWS::DynamoDB::Table", dynamodb_table)
