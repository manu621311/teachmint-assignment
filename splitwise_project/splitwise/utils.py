'''Utility class'''
from decimal import Decimal, ROUND_DOWN
from pymongo import UpdateOne
from splitwise_project.utils import MongoDatabase
from bson import ObjectId

db_handle, _ = MongoDatabase.get_db_handle('splitwise', 'localhost', 27017,"","")

class SplitwiseUtil:

    @staticmethod
    def create_amount_list(
              split, 
              entity,
              default_entity_value,
              split_amount = 0 ,
              remaining_amount = 0,
              user_to_acquaintance_dict = {},
              multiplication_factor = 1,
            ):
        
        split_list = []
        for user in split:
            user_id = user.get("userId")
            user_amount = (float(user.get(entity,default_entity_value)) if user.get("hasPaid") else -float(user.get(entity,default_entity_value)))*multiplication_factor

            if user["inSplit"]:
                    user_amount = user_amount - ((1 + user_to_acquaintance_dict.get(user_id,0)) * split_amount) - remaining_amount
                    remaining_amount = 0
            split_list.append({
                "user_id":user_id,
                "amount":float(Decimal(user_amount).quantize(Decimal('0.00'), rounding=ROUND_DOWN))
            })

        return split_list
    
    @staticmethod
    def update_user_balance(
         split_list: list
    ):
         
        update_operations = []
        users_collection = db_handle["users"]
        for user in split_list:
            user_id = user['user_id']
            amount = user['amount']

            # An update operation for each participant
            update_operation = UpdateOne(
                {'_id': ObjectId(user_id)},
                {'$inc': {'netBalance': amount}}
            )

            update_operations.append(update_operation)

        # Update_many to apply all update operations
        result = users_collection.bulk_write(update_operations)
