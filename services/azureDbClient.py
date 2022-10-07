import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey, exceptions

class AzureDbClient:
    def __init__(self) :
        self.database_client = {}
        config = {
        "endpoint": "https://awsuserextractor.documents.azure.com:443/",
        "primarykey" : ""
        }
        
        database_name = "awsextractordb" 
        client = cosmos_client.CosmosClient(url=config["endpoint"], credential=config["primarykey"])
        try:
            self.database_client  = client.create_database(database_name)
        except exceptions.CosmosResourceExistsError:
            self.database_client = client.get_database_client(database_name)
    
    def get_container(self, container_name):    
        container = {}
        try:
            container =  self.database_client.create_container(id=container_name, partition_key=PartitionKey(path="/id"))
        except exceptions.CosmosResourceExistsError:
            container = self.database_client.get_container_client(container_name)
        except exceptions.CosmosHttpResponseError:
            raise
        
        return container;
    
    def fetch_all_users(self):
        users = []
        users_container = self.get_container("users");
        for item in users_container.query_items(
            query='SELECT * FROM users', enable_cross_partition_query=True):
            users.append(item)
        
        return users
            
    def delete_user(self, username) :
        container = self.get_container('users')
        query = f'SELECT * FROM users u WHERE u.id="{username}"'
        for item in container.query_items( query= query ,enable_cross_partition_query=True):
            container.delete_item(item, partition_key=username)

    def insert_user(self, username, groups, policies, attachedPolices, keys, creationDate, lastLogin):
        users_container = self.get_container("users");
        #username = user.get('UserName')
        users_container.upsert_item({
            'id': username,
            'name': username,
            'groups': groups,
            'policies': policies,
            'attachedPolicies': attachedPolices,
            'keys': keys,
            'created': creationDate,
            'last_login': lastLogin  
            })
    
