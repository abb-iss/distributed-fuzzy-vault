""" Vault Converter that serializes (vault to JSON) and deserializes (JSON to vault) """


from Vault import Vault, VaultElement
import Constants


class VaultConverter:
    @staticmethod
    def serialize(vault: Vault, vault_id, geom_table_flag=False):
        """
        Serializes vault to JSON represented as python dictionary
        :param vault: fuzzy vault
        :param vault_id: ID of vault to be saved in database
        :param geom_table_flag: flag to determine if geom table is stored at DB and included in vault
        :return: dict
        """
        vault_x = []
        vault_y = []
        for vault_element in vault.vault_final_elements_pairs:
            vault_x.append(vault_element.x_rep)
            vault_y.append(vault_element.y_rep)

        result = dict()
        result[Constants.JSON_VAULT_ID] = vault_id
        result[Constants.JSON_VAULT_X] = vault_x
        result[Constants.JSON_VAULT_Y] = vault_y

        if geom_table_flag:
            geom_table_db = []
            # Convert geometric hashing table
            if vault.geom_table:
                for element in vault.geom_table:
                    element_dict = dict()
                    element_dict[Constants.JSON_GEOM_BASIS] = element.basis_rep
                    element_dict[Constants.JSON_GEOM_X] = element.minutiae_rep
                    element_dict[Constants.JSON_GEOM_Y] = element.function_points_rep
                    geom_table_db.append(element_dict.copy())
                    element_dict.clear()
            result[Constants.JSON_VAULT_GEOM] = geom_table_db

        return result

    @staticmethod
    def deserialize(vault_dict):
        """
        Deserializes dict to vault
        :param vault_dict: dictionary from database
        :return: Vault
        """
        new_vault = Vault()
        vault_x = vault_dict[Constants.JSON_VAULT_X]
        vault_y = vault_dict[Constants.JSON_VAULT_Y]
        for i, _ in enumerate(vault_x):
            new_vault.add_vault_element(VaultElement(vault_x[i], vault_y[i]))
        return new_vault
