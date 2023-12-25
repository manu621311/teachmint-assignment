
# SPLITWISE PROJECT

The backend of splitwise is based on django.
The project is divided into two apps :
1)User - For actions related to users
2)Spliwise/Expense - For actions related to expense, splits, emails and simplification






## Schema

The schema is kept plain so it can be easily understood and scaled. 
It uses MongoDb as its current database. The data will be stored in two colledctions.
1) Expense - It will store all details about an expense.
2) Users - It will store all details about a user

![schema](https://github.com/manu621311/teachmint-assignment/assets/60875787/72553238-a528-4c0e-b3a9-48d2458318fe)

## Architecture

Basic Flow of a API Request:
1) Request in received through serialiizers
2) Processed in views
3) Saved in database majorly through common utilities.


Some Important Points and Conventions:
1) Positive Balance means user will get money
2) Negative Balance means user will give money

Ex. In the above diagram, an entry is there inside users collection. Its balances key states: user1 will get Rs.45 from current user. user 2 will give Rs.95 to cuurent user.


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`MONGO_URL`: For connecting to mongo database

`EMAIL_HOST_PASSWORD`: For sending emails

`EMAIL_HOST_USER` : Email ID of sender

Note - Secret Key is included in the project itself
## Installation

Clone the repo. Run the following commands

```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip3 install -r requirements.txt
  cd splitwise_project
  python3 manage.py runserver
```
The Django server will be available at :
`http://127.0.0.1:8000/`


## API Reference

#### Create User
Returns ID of the created user for further use
```http
  POST /users
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`      | `string` | **Required**. Name of user |
| `email`      | `string` | **Required**. Email of user |
| `phone`      | `string` | **Required**. Phone of user |

#### Get all details of a user

```http
  GET /users
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `userId` | `string` | **Required**. UserId of a user |
| `simplify` | `bool` | **Optional**. Gives a simplified view of transactions to be done among users |

#### Create/Split a new expense

```http
  POST /splitwise
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `expenseType` | `string` | **Required**. One of the three : ("EQUAL", "EXACT", "PERCENT") |
| `payer` | `string` | **Required**. ID of user who paid |
| `amount` | `float` | **Required**. Total amount paid by this user |
| `split` | `object` | **Required**. Split between users. Example,structure and explanation given below ||
| `name` | `string` | **Required**. Name of this expense/split |
| `note` | `string` | **Optional**. Note on this split/expense |
| `acquaintance` | `object` | **Optional**. Family and friends involved with the users. Example,structure and explanation given below |

For `acquaintance` array of objects is expected. `userId` and `numberOfPeople` are the required keys in an object

Example : "acquaintance":[{
        "userId":"id1",
        "numberOfPeople":2
        },
        {
        "userId":"id2",
        "numberOfPeople":1
        }]

For `split`  again an array of objects is expected.
If the selected 'expenseType' is EQUAL or EXACT. `userId` and `amount` are expected keys in an object.

Example:"split": [
        {
        "userId": "id1",
        "amount": 100
        },
        {
        "userId": "id3",
        "amount": 200
        }]

If the selected 'expenseType' is PERCENT. `userId` and `percent` are expected keys in an object.

Example:"split": [
        {
        "userId": "id1",
        "percent": 90
        },
        {
        "userId": "id3",
        "percent": 10
        }]

NOTE: If the payer is also a part of the expense, he is to be included in `split` with his share mentioned in `amount` or `percent`. With the total ranging to 100(percent) or amount mentioned.

Example: 

'amount' : 300, 
'payer' : 'superid1',
"split": [
        {
        "userId": "superid1",
        "amount": 10
        },
        {
        "userId": "id2",
        "amount": 190
        },
        {
        "userId": "id3",
        "amount": 100
        }],

#### Use simplification algo on specific users

```http
  POST /splitwise/simplify
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `userIds` | `string` | **Required**. UserIds of users in string array |

Example payload : {
    "userIds":[
        "id1",
        "id2"
    ]
}

#### Get all balances of all users using simplification algo

```http
  GET /splitwise/simplify
```



=================================================
