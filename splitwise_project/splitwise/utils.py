"""Utility class"""
from decimal import Decimal, ROUND_DOWN
from pymongo import UpdateOne
from splitwise_project.utils import ProjectUtils
from bson import ObjectId
from concurrent.futures import ThreadPoolExecutor
import splitwise_project.constants as constants

db_handle, _ = ProjectUtils.get_db_handle("splitwise")

class SplitwiseUtil:
    """
    Utility Class for splitwise app
    """

    @staticmethod
    def create_amount_list(
        split,
        payer,
        entity,
        base_entity_value,
        default_entity_value,
        split_amount=0,
        remaining_amount=0,
        user_to_acquaintance_dict={},
        multiplication_factor=1,
    ):
        '''
        Function which calculates the absolute amount owed/paid for every user involved in
        an expense
        '''
        split_list = []
        for user in split:
            user_id = user.get("userId")

            #base user amount
            user_amount = (
                (base_entity_value - float(user.get(entity, default_entity_value)))
                if user_id == payer
                else -float(user.get(entity, default_entity_value))
            ) * multiplication_factor

            #user amount adjusting among all
            user_amount = (
                user_amount
                - ((1 + user_to_acquaintance_dict.get(user_id, 0)) * split_amount)
                - remaining_amount
            )
            remaining_amount = 0

            #Created a list representing user and his amount involved in this expense
            split_list.append(
                {
                    "user_id": ObjectId(user_id),
                    "amount": float(
                        Decimal(user_amount).quantize(
                            Decimal("0.00"), rounding=ROUND_DOWN
                        )
                    ),
                }
            )

        return split_list

    @staticmethod
    def update_user_balance(split_list: list, payer: str, amount: float):
        '''
        Function to update user's net balance and its pending transactions with others
        '''
        update_operations = []
        users_collection = db_handle["users"]
        if ObjectId(payer) not in [user["user_id"] for user in split_list]:
            split_list.append({"user_id": ObjectId(payer), "amount": float(amount)})

        #Create a list of user fields which are to be updates
        for user in split_list:
            user_id = user["user_id"]
            amount = user["amount"]
            balance_dict = {}
            if user_id == ObjectId(payer):
                #To update connected transactions of a user
                for connected_user in split_list:
                    if user != connected_user:
                        balance_dict[
                            f'balances.{connected_user["user_id"]}'
                        ] = connected_user["amount"]
            else:
                balance_dict[f"balances.{payer}"] = -user["amount"]

            balance_dict["netBalance"] = amount
            # An update operation for each participant
            update_operation = UpdateOne({"_id": user_id}, {"$inc": balance_dict})

            update_operations.append(update_operation)
        # Update_many to apply all update operations
        users_collection.bulk_write(update_operations)

    @staticmethod
    def save_expense(split_list, payer, amount, name="", note=""):
        '''
        Save the new expense in database along with its participants
        '''
        expense_collection = db_handle["expenses"]
        expense = {
            "name": name,
            "payer": ObjectId(payer),
            "participants": split_list,
            "note": note,
            "amount":amount
        }
        expense_collection.insert_one(expense)

    @staticmethod
    def simplify_expenses(user_balance_list, amount_key):
        '''
        Algorithm for simplfying transactions
        '''
        simplified_balances = []
        for user_data in user_balance_list:
            balance = user_data[amount_key]
            user_id = str(user_data["_id"])
            payee_list = []
            for other_user_data in user_balance_list:
                # If the user owes money, find users who will collect that money
                if balance < 0:
                    other_user_id = str(other_user_data["_id"])
                    if (other_user_id != user_id) and (
                        (other_balance := other_user_data[amount_key]) > 0
                    ):
                        # Calculate the max exchangable amount
                        simplify_amount = min(abs(balance), abs(other_balance))

                        # Update balances
                        user_data[amount_key] += simplify_amount
                        other_user_data[amount_key] -= simplify_amount
                        balance += simplify_amount
                        # Update simplified balances
                        payee_list.append(
                            {
                                "userId": other_user_id,
                                "name": other_user_data["name"],
                                "amount": simplify_amount,
                            }
                        )
                else:
                    break
            if payee_list:
                simplified_balances.append(
                    {"userId": user_id, "name": user_data["name"], "toUser": payee_list}
                )
        return simplified_balances

    @staticmethod
    def send_email_to_users(split_list, payer):
        '''
        Function which sends mail to members of an expense
        '''
        user_ids = [user["user_id"] for user in split_list]
        users_collection = db_handle["users"]
        results = list(
            users_collection.find({"_id": {"$in": user_ids}}, {"name": 1, "email": 1})
        )
        executor = ThreadPoolExecutor(max_workers=3)

        #Create mail for every user and send them asynchronously
        for user_data, amount_data in zip(results, split_list):
            if str(user_data["_id"]) != payer:
                message = constants.EXPENSE_EMAIL_BODY_TEMPLATE.format(
                    recipient=user_data["name"], amount=abs(amount_data["amount"])
                )
                recipient = user_data["email"]
                executor.submit(
                    ProjectUtils.send_email,
                    constants.EXPENSE_SUBJECT,
                    message,
                    [recipient],
                )
