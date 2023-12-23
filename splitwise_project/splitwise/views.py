from urllib.request import Request
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from splitwise_project.utils import MongoDatabase
from decimal import Decimal, ROUND_DOWN
from rest_framework import status
from .serializers import  ExpenseSerialzer
from .utils import SplitwiseUtil
import json


db_handle, _ = MongoDatabase.get_db_handle('splitwise', 'localhost', 27017,"","")

# Create your views here.
class SplitWiseView(APIView):

    def post(self, request: Request):
        serializer = ExpenseSerialzer(json.loads(request.body))
        expense_type = serializer.data.get("expenseType")
        users_collection = db_handle["users"]
        if expense_type == "EXACT":
            split = serializer.data.get("split")
            splitted_paid_sum = sum(float(user["amount"]) for user in split if user["hasPaid"])
            splitted_owed_sum = sum(float(user["amount"]) for user in split if not user["hasPaid"])
            amount = float(serializer.data["amount"])
            if not (amount == splitted_owed_sum == splitted_paid_sum) :
                return Response({'errors': {"BadRequest":"Invalid amount entered"}}, status=status.HTTP_400_BAD_REQUEST) 

            split_list = SplitwiseUtil().create_amount_list(
                split=split,
                entity="amount",
                default_entity_value=0,
                )
            result = SplitwiseUtil().update_user_balance(split_list)

            print(split_list)
            
        elif expense_type == "PERCENT":

            split = serializer.data.get("split")
            splitted_paid_sum = sum(float(user["percent"]) for user in split if user["hasPaid"])
            splitted_owed_sum = sum(float(user["percent"]) for user in split if not user["hasPaid"])
            amount = float(serializer.data["amount"])
            if not (splitted_owed_sum == splitted_paid_sum) :
                return Response({'errors': {"BadRequest":"Invalid amount entered"}}, status=status.HTTP_400_BAD_REQUEST) 
            multiplication_factor = amount/100
            split_list = split_list = SplitwiseUtil().create_amount_list(
                split=split,
                entity="percent",
                default_entity_value=100,
                multiplication_factor= multiplication_factor,
                )
            result = SplitwiseUtil().update_user_balance(split_list)
            print(result)
        else:

            split = serializer.data.get("split")
            users_for_split = len([user for user in split if user["inSplit"]])
            extra_members = sum(acq["numberOfPeople"] for acq in serializer.data.get("acquaintance"))
            user_to_acquaintance_dict = {acq_user["userId"]: acq_user["numberOfPeople"] for acq_user in serializer.data.get("acquaintance")}
            num_of_people = users_for_split + extra_members
            amount = float(serializer.data["amount"])
            split_amount = float((Decimal(amount) / Decimal(num_of_people)).quantize(Decimal('0.00'), rounding=ROUND_DOWN))
            remaining_amount = float(amount - (split_amount*num_of_people))
            print(split_amount)

            split_list = SplitwiseUtil().create_amount_list(
                split=split,
                entity="amount",
                default_entity_value=0,
                split_amount= split_amount,
                remaining_amount=remaining_amount,
                user_to_acquaintance_dict=user_to_acquaintance_dict
                )
            result = SplitwiseUtil().update_user_balance(split_list)

            print(split_list)
        
        # users_collection.insert_one(serializer.data)
        return Response(serializer.data)
    