from django.db import models

# Create your models here.
class User:
    def __init__(self, user_id, name, email, phone, balance):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.balance = balance

    def to_dict(self):
        return {
            'userId': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'balance':self.balance
        }
