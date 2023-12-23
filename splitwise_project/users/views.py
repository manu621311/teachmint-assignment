from urllib.request import Request
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from splitwise_project.utils import MongoDatabase
from .models import User
from .serializers import  UserSerializer
from bson import ObjectId

import json

db_handle, _ = MongoDatabase.get_db_handle('splitwise', 'localhost', 27017,"","")

# Create your views here.

class UsersView(APIView):
    def post(self,request: Request):
        serializer = UserSerializer(data = json.loads(request.body))
        if serializer.is_valid():
            users_collection = db_handle["users"]
            users_collection.insert_one(serializer.validated_data)
            return Response(serializer.validated_data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: Request):
        user_id = request.GET.get('userId')
        users_collection = db_handle["users"]
        result = users_collection.find_one({'_id':ObjectId(user_id)})
        user = User(
            user_id=user_id,
            name = result.get("name"),
            email = result.get("email"),
            phone = result.get("phone"),
            balance= result.get("balance",0)
        )
        return Response(user.to_dict())
