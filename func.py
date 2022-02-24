from flask_sqlalchemy import SQLAlchemy
from newlab3 import User
db=SQLAlchemy()

def createUsersList(newUserList,pw):#newUserList is a list of String
    UserInstancesList=[]
    for username in newUserList:
        UserInstancesList.append(User(username,pw))
    return UserInstancesList
#we cannot update the db here
def printDebug():
    print("""


DB:""")
