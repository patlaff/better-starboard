import os
from helpers.helpers import createLogger
from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableServiceClient

class DbService:

    def __init__(self):
        self.credential = AzureNamedKeyCredential(os.getenv("STORAGE_ACCOUNT_NAME"), os.getenv("STORAGE_ACCOUNT_KEY"))
        self.logger = createLogger('db')
    
    def create_tables(self, tables = []):
        
        with TableServiceClient(endpoint=os.getenv("STORAGE_ACCOUNT_TABLE_ENDPOINT"), credential=self.credential) as table_service_client:
            for table in tables:
                try:
                    table_client = table_service_client.create_table_if_not_exists(table_name=table)
                    self.logger.info("Table name: {}".format(table_client.table_name))
                except Exception as e:
                    self.logger.error(e)
    
    def 