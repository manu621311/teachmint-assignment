'''Models to be used in users app'''

class User:
    '''
    Model class for user(Response)
    '''
    def __init__(self, user_id, name, email, phone, net_balance, balances, simplified_balance, expenses):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.net_balance = net_balance
        self.balances = balances
        self.expenses = expenses
        self.simplified_balance = simplified_balance

    def to_dict(self):
        return {
            'userId': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'netBalance':self.net_balance,
            'balances': self.balances,
            'expenses': self.expenses,
            'simplifiedBalance': self.simplified_balance
        }
