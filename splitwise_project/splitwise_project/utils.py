'''File containing base level utilities'''

from pymongo import MongoClient
from django.conf import settings
from django.core.mail import send_mail
from splitwise_project.settings import MONGO_URL

class ProjectUtils:
    '''
    Class for base level utility functions
    '''
    @staticmethod
    def get_db_handle(db_name):
        '''
        Returns a client for given database
        '''
        client = MongoClient(MONGO_URL)
        db_handle = client[db_name]
        return db_handle, client

    @staticmethod
    def send_email(
        subject,
        message,
        recipient_list,
    ):
        '''
        Function which can be called to send mail
        '''
        email_from = settings.EMAIL_HOST_USER
        send_mail( subject, message, email_from, recipient_list )
