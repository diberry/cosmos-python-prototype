# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

# All interaction with Cosmos DB starts with an instance of the CosmosClient
# [START create_client]
from azure.cosmos import HTTPFailure, CosmosClient, Container, Database, PartitionKey

import os

url = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
client = CosmosClient(url, key)
# [END create_client]

# Create a database in the account using the CosmosClient,
# specifying that the operation shouldn't throw an exception
# if a database with the given ID already exists.
# [START create_database]
database_name = "testDatabase"
try:
    database = client.create_database(id=database_name)
except HTTPFailure:
    database = client.get_database(database=database_name)
# [END create_database]

# Create a container, handling the exception if a container with the
# same ID (name) already exists in the database.
# [START create_container]
container_name = "products"
try:
    container = database.create_container(
        id=container_name, partition_key=PartitionKey(path="/productName")
    )
except HTTPFailure as e:
    if e.status_code != 409:
        raise
    container = database.get_container(container_name)
# [END create_container]

# Create a container with custom settings. This example
# creates a container with a custom partition key.
# [START create_container_with_settings]
customer_container_name = "customers"
try:
    customer_container = database.create_container(
        id=customer_container_name,
        partition_key=PartitionKey(path="/city"),
        default_ttl=200,
    )
except HTTPFailure as e:
    if e.status_code != 409:
        raise
    customer_container = database.get_container(customer_container_name)
# [END create_container_with_settings]

# Retrieve a container by walking down the resource hierarchy
# (client->database->container), handling the exception generated
# if no container with the specified ID was found in the database.
# [START get_container]
database = client.get_database(database_name)
try:
    container = database.get_container(container_name)
except HTTPFailure as failure:
    if failure.status_code == 404:
        print("Container does not exist.")
    else:
        print(f"Failed to retrieve container. Status code:{failure.status_code}")
# [END get_container]

# [START list_containers]
database = client.get_database(database_name)
for container in database.list_containers():
    print(f"Container ID: {container.id}")
# [END list_containers]

# Insert new items by defining a dict and calling Container.upsert_item
# [START upsert_items]
container = database.get_container(container_name)
for i in range(1, 10):
    container.upsert_item(
        dict(id=f"item{i}", productName="Widget", productModel=f"Model {i}")
    )
# [END upsert_items]

# Modify an existing item in the container
# [START update_item]
item = container.get_item("item2", partition_key="Widget")
item["productModel"] = "DISCONTINUED"
updated_item = container.upsert_item(item)
# [END update_item]

# Query the items in a container using SQL-like syntax. This example
# gets all items whose product model hasn't been discontinued.
# [START query_items]
import json

for item in container.query_items(
    query='SELECT * FROM products p WHERE p.productModel <> "DISCONTINUED"',
    enable_cross_partition_query=True,
):
    print(json.dumps(item, indent=True))
# [END query_items]

# Parameterized queries are also supported. This example
# gets all items whose product model has been discontinued.
# [START query_items_param]
discontinued_items = container.query_items(
    query='SELECT * FROM products p WHERE p.productModel = @model AND p.productName="Widget"',
    parameters=[dict(name="@model", value="DISCONTINUED")],
)
for item in discontinued_items:
    print(json.dumps(item, indent=True))
# [END query_items_param]

# Delete items from the container.
# The Cosmos DB SQL API does not support 'DELETE' queries,
# so deletes must be done with the delete_item method
# on the container.
# [START delete_items]
for item in container.query_items(
    query='SELECT * FROM products p WHERE p.productModel = "DISCONTINUED" AND p.productName="Widget"'
):
    container.delete_item(item, partition_key="Widget")
# [END delete_items]

# Retrieve the properties of a database
# [START get_database_properties]
properties = database.properties
print(json.dumps(properties, indent=True))
# [END get_database_properties]

# Modify the properties of an existing container
# This example sets the default time to live (TTL) for items in the
# container to 3600 seconds (1 hour). An item in container is deleted
# when the TTL has elapsed since it was last edited.
# [START reset_container_properties]
# Set the TTL on the container to 3600 seconds (one hour)
database.reset_container_properties(container, partition_key=PartitionKey(path='/productName'), default_ttl=3600)

# Display the new TTL setting for the container
container_props = database.get_container(container_name).properties
print(f"New container TTL: {json.dumps(container_props['defaultTtl'])}")
# [END reset_container_properties]

# Create a user in the database.
# [START create_user]
try:
    database.create_user(dict(id="Walter Harp"))
except HTTPFailure as failure:
    if failure.status_code == 409:
        print("A user with that ID already exists.")
    else:
        print(f"Failed to create user. Status code:{failure.status_code}")
# [END create_user]
