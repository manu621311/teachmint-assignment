'''Views for Users App'''
import json

from urllib.request import Request
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from bson import ObjectId
from splitwise.utils import SplitwiseUtil
from splitwise_project.utils import ProjectUtils

from .models import User
from .serializers import UserSerializer

db_handle, _ = ProjectUtils.get_db_handle("splitwise")

# Create your views here.


class UsersView(APIView):
    '''
    Class containing User Related views
    '''
    users_collection = db_handle["users"]
    expense_collection = db_handle["expenses"]

    def post(self, request: Request):
        '''
        View function for creating a new user
        '''
        serializer = UserSerializer(data=json.loads(request.body))
        if serializer.is_valid():
            self.users_collection.insert_one(serializer.validated_data)
            return Response(serializer.validated_data)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request: Request):
        '''
        View function for getting details of a user
        '''
        user_id = request.GET.get("userId")
        simplify = request.GET.get("simplify", False)
        result = self.users_collection.find_one({"_id": ObjectId(user_id)})
        balances_with_users = result.get("balances", {})

        #Structuring the payments from other users
        connected_users = []
        if balances_with_users:
            user_ids = [ObjectId(user_id) for user_id in balances_with_users.keys()]
            users_objects = list(
                self.users_collection.find({"_id": {"$in": user_ids}}, {"name": 1})
            )

            for user in users_objects:
                obj_user_id = str(user["_id"])
                if (amount := balances_with_users.get(obj_user_id)) != 0:
                    connected_users.append(
                        {"_id": obj_user_id, "name": user["name"], "amount": amount}
                    )

        #Giving a simplified version of payment branches if its turned on
        simplified_balance = []
        if connected_users and simplify:
            user_data = connected_users
            user_data.append(
                {
                    "_id": user_id,
                    "name": result.get("name"),
                    "amount": result.get("netBalance", 0),
                }
            )
            simplified_balance = SplitwiseUtil.simplify_expenses(
                user_balance_list=user_data, amount_key="amount"
            )

        #Getting all expenses where that user is involved
        expenses = []
        if result.get("netBalance") != 0:
            expense_data = list(
                self.expense_collection.find(
                    {"participants.user_id": ObjectId(user_id)},
                    {"name": 1, "participants": 1},
                )
            )
            expenses = [
                {
                    "name": expense["name"],
                    "amount": next(
                        (
                            participant["amount"]
                            for participant in expense["participants"]
                            if str(participant["user_id"]) == user_id
                        ),
                        0,
                    ),
                }
                for expense in expense_data
            ]

        #Creating the response
        user = User(
            user_id=user_id,
            name=result.get("name"),
            email=result.get("email"),
            phone=result.get("phone"),
            net_balance=result.get("netBalance", 0),
            balances=connected_users,
            expenses=expenses,
            simplified_balance=simplified_balance,
        )
        return Response(user.to_dict())
