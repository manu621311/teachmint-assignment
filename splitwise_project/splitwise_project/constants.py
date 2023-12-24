"""Module containg commonly used constants and templates"""

EXPENSE_SUBJECT = "NEW EXPENSE"
EXPENSE_EMAIL_BODY_TEMPLATE = "Dear {recipient},\n\nYou have been added to an expense. The total amount you owe is Rs.{amount} .\n\nThanks,\nTeam Django"
WEEKLY_EMAIL_BODY_TEMPLATE = "Dear {recipient},\n\nThis is to remind you that you owe following amount to following people:\n\n{dues_list}\n\n.\nRequesting you to clear your dues as soon as possible.\n\nThanks,\nTeam Django"
WEEKLY_EMAIL_SUBJECT_TEMPLATE = "DUES REMINDER"
