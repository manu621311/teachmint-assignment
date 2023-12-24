'''This module conatins views of splitwise/expense app'''

from urllib.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from splitwise_project.utils import ProjectUtils
from decimal import Decimal, ROUND_DOWN
from rest_framework import status
from .serializers import ExpenseSerialzer, SimplifySplitSerializer
from .utils import SplitwiseUtil
from bson import ObjectId

import json

db_handle, _ = ProjectUtils.get_db_handle("splitwise")

class SplitWiseView(APIView):
    '''
    Class containing view functions for splitting expenses
    '''
    util = SplitwiseUtil

    def post(self, request: Request):
        '''
        Post Request function for saving/splitting a new expense
        '''
        serializer = ExpenseSerialzer(json.loads(request.body))
        expense_type = serializer.data.get("expenseType")
        amount = float(serializer.data["amount"])
        payer = serializer.data.get("payer")    #Person who paid the amount
        split = serializer.data.get("split")    #The users who are involved in split

        #Process on the basis of selected expense type
        if expense_type == "EXACT":

            #Total sum which is split among members
            splitted_owed_sum = sum(float(user["amount"]) for user in split)
            if not amount == splitted_owed_sum:
                return Response(
                    {"errors": {"BadRequest": "Invalid amount entered"}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            #Calling a utility function which creates a list of net balances of each user
            split_list = self.util.create_amount_list(
                split=split,
                payer=payer,
                base_entity_value=amount,   #Total amount/Total Percentage
                entity="amount",            #Entity type - Amount or Percent
                default_entity_value=0,
            )

        elif expense_type == "PERCENT":
            #Total sum which is split among members
            splitted_owed_sum = sum(float(user["percent"]) for user in split)
            if not (splitted_owed_sum == 100):
                return Response(
                    {"errors": {"BadRequest": "Invalid amount entered"}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            multiplication_factor = amount / 100    #For calculating value through percent
            split_list = split_list = self.util.create_amount_list(
                split=split,
                payer=payer,
                entity="percent",
                base_entity_value=100,      #100 percent is to be divided among users
                default_entity_value=100,
                multiplication_factor=multiplication_factor,
            )

        else:
            users_for_split = len(split)
            extra_members = sum(            #Friends of user/users
                acq["numberOfPeople"] for acq in serializer.data.get("acquaintance")
            )
            user_to_acquaintance_dict = {   #Which user has how many accompanying friends
                acq_user["userId"]: acq_user["numberOfPeople"]
                for acq_user in serializer.data.get("acquaintance")
            }
            num_of_people = users_for_split + extra_members

            #Equal split between total members
            split_amount = float(           
                (Decimal(amount) / Decimal(num_of_people)).quantize(
                    Decimal("0.00"), rounding=ROUND_DOWN
                )
            )
            #Amount remaining after a non-terminating division Ex. 10/3
            remaining_amount = float(amount - (split_amount * num_of_people))   

            split_list = self.util.create_amount_list(
                split=split,
                payer=payer,
                entity="amount",
                base_entity_value=amount,
                default_entity_value=0,
                split_amount=split_amount,
                remaining_amount=remaining_amount,
                user_to_acquaintance_dict=user_to_acquaintance_dict,
            )
        #Update netbalnce of every user and their pending transactions with other user
        self.util.update_user_balance(split_list, payer, amount)

        #Send mail to users involved in this expense
        self.util.send_email_to_users(split_list, payer)

        #Finally save this expense
        self.util.save_expense(
            split_list=split_list,
            payer=payer,
            amount=amount,
            name=serializer.data.get("name"),
            note=serializer.data.get("note"),
        )
        return Response({"result": "Expense Divided and Saved"})


class SimplifySplitView(APIView):
    '''
    Class for simplify complex payment branches
    '''
    users_collection = db_handle["users"]

    def post(self, request: Request):
        '''
        Fucntion which takes user ids as input and simplifies the complex transaction
        branch system into a simpler one
        '''
        serializer = SimplifySplitSerializer(json.loads(request.body))
        user_ids = [ObjectId(user_id) for user_id in serializer.data.get("userIds")]

        #Get balances of inputted user ids
        if len(user_ids) > 0:
            user_data = list(
                self.users_collection.find(
                    {"_id": {"$in": user_ids}}, {"name": 1, "netBalance": 1}
                )
            )

            #Apply simplifying algorithm on users balances
            if user_data:
                simplified_balances = SplitwiseUtil.simplify_expenses(
                    user_balance_list=user_data, amount_key="netBalance"
                )
                #Return simplified transactions
                return Response(simplified_balances)
            
        return Response(
            {"errors": {"BadRequest": "Invalid data given"}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self):
        '''
        Function that simplifies transactions between all users of the database
        '''
        user_data = list(self.users_collection.find({}, {"name": 1, "netBalance": 1}))
        if user_data:
            simplified_balances = SplitwiseUtil.simplify_expenses(
                user_balance_list=list(user_data), amount_key="netBalance"
            )
            #Return simplified transactions
            return Response(simplified_balances)
        return Response({"Message": "No entries in databse"})
