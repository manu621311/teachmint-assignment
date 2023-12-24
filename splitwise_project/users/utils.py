'''Utility file for users app'''
from splitwise_project.utils import ProjectUtils
import splitwise_project.constants as constants

db_handle, _ = ProjectUtils.get_db_handle('splitwise')

class UsersUtils:
    '''
    Utility class containing utility functions for users app
    '''
    @staticmethod
    def send_weekly_email():
        '''
        Function that can be called to triggered to send weekly mail.
        '''
        users_collection = db_handle["users"]
        user_data = list(users_collection.find({},{'name':1,'email':1,'balances':1}))
        userid_to_name_map = {
            str(user['_id']): user['name']
            for user in user_data
        }

        #Send mail to every user in background
        for user in user_data:
            dues_list = []
            for user_id,amount in user['balances'].items():
                if amount > 0:
                    dues_list.append(f"- {userid_to_name_map[user_id]}: Rs.{amount}")
            
            #If dues are present send mail
            if dues_list:
                dues_list_text = '\n'.join(dues_list)
                ProjectUtils.send_email(
                    subject = constants.WEEKLY_EMAIL_SUBJECT_TEMPLATE,
                    message = constants.WEEKLY_EMAIL_BODY_TEMPLATE.format(
                            recipient = user['name'],
                            dues_list = dues_list_text),
                    recipient_list = [user['email']]
                )
