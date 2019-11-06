""" DBHandler to connect to CosmosDB over the MongoDB API """

from pymongo import MongoClient
import json

from Vault_Converter import VaultConverter
import Constants


class DBHandler:
    def __init__(self):
        self.client = MongoClient("mongodb://fuzzy:f0OMRk1z2uwp0Pj2F0Y8MWCx20zmIOxfRyfLsdLNY6qNCYXEn3Vil9fsoJ1ZXMDlZQvksl3tRCIU2zOzRvTpiA==@fuzzy.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")
        # Select the database
        self.db = self.client['FingerprintDB']
        # Select collection
        self.col_fuzzy_vault = self.db['FuzzyVault']

    def list_all_fuzzy_vault(self):
        docs = self.col_fuzzy_vault.find()
        for doc in docs:
            print(doc)

    def insert_fuzzy_vault(self, vault, vault_id):
        self.col_fuzzy_vault.insert_one(VaultConverter.serialize(vault, vault_id))

    def find_fuzzy_vault(self, vault_id, dump=False):
        result_cursor = self.col_fuzzy_vault.find({Constants.JSON_VAULT_ID: vault_id})
        if result_cursor.count() == 0:
            print("No match found with given ID!")
            return None
        elif result_cursor.count() != 1:
            # Collision handling if multiple IDs match IS NOT IMPLEMENTED
            print("More than one result found!")

        result = self.col_fuzzy_vault.find_one({Constants.JSON_VAULT_ID: vault_id})
        if dump:
            del result['_id']
            with open('out/vault_{}.json'.format(vault_id), 'w') as json_file:
                json.dump(result, json_file)
        return VaultConverter.deserialize(result)

    def close_handler(self):
        self.client.close()
