from flask import Flask,redirect, url_for, render_template,request,session
#from db_sch import User
from werkzeug.security import generate_password_hash,check_password_hash
import random
from flask_sqlalchemy import SQLAlchemy#import SQLAlchemy class
import func
app = Flask(__name__)
app.secret_key="hello"#T5
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)#create new SQLAlchemy object bind to existing app
#db
def listExistForUser(username,listName):
    currentUserID=getUserIDOf(username)
    ListsBelongsToUser=getListofUserByUserID(currentUserID)
    if not ListsBelongsToUser is None:#check if there are some list for the user
        for l in ListsBelongsToUser:
            if l.name==listName:
                return True
    return False

class User(db.Model): #class user(class)
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password= db.Column(db.String(500))
    def __init__(self,name,password):#get input when instantiation
        self.username=name
        self.password=password
class List(db.Model):#class DerivedClass(BaseClass)???
    __tablename__='lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    user_id = db.Column(db.Integer)  # this ought to be a "foreign key"

    def __init__(self, name, user_id):
        self.name=name
        self.user_id = user_id
class ListItem(db.Model):
    __tablename__='items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    list_id = db.Column(db.Integer)  # this ought to be a "foreign key"

    def __init__(self, name, list_id):
        self.name=name
        self.list_id=list_id
class DBManipulator():
    def getUserIDOf(self,username):
        '''
        1 IP: username
        '''
        targetUser=User.query.filter_by(username=username).first()
        id=targetUser.id
        print(f"id of {username} is {id}")
        return id

    def addUserToDB(self,username,encryptedPw):
        newUser=User(username,encryptedPw)
        db.session.add(newUser)
        db.session.commit()
        print("New User added to User DB")
    def checkPassword(self,username,password):
        #
        userObj=User.query.filter_by(username=username).first()
        if not userObj is None:
            encryptedPw=userObj.password
            if (check_password_hash(encryptedPw,password)):
                return True
        return False


    def getListofUserByUserID(self,userID):
        targetList=List.query.filter_by(user_id=userID).all()
        return targetList
    def getListIDByUsernameAndListName(self,Username,ListName):
        #Assume user do not have 2 list with same listname
        uid=getUserIDOf(Username)
        userLists=self.getListofUserByUserID(uid)
        listId=-1
        for l in userLists:
            #if the name of l equals ListName set l.id as listId
            if l.name==ListName:
                listId=l.id
                print(f"the listId is {listId}")
                break
        if listId==-1:
            print(f"list: {ListName} for user: {Username}not found")
        return listId

    def getItemsByListId(self,ListId):
        return ListItem.query.filter_by(list_id=ListId).all()
    def getItemsOfUser(self,username):#return list of objs with type(ListItem)
        uid=self.getUserIDOf(username)
        items={}#dictionary
        listsNames=[]#["Shopping","Homework"]
        listsId=[]
        #get the List belongs to the user
        ListsBelongsToUser=self.getListofUserByUserID(uid)#[<list1>,<list2>]
        for l in ListsBelongsToUser:
            items[l.name]=[]
            listsNames.append(l.name)
            listsId.append(l.id)
        #append the list inside the dictionary
        print(f"listsNames:{listsNames}")
        print(f"listsId:{listsId}")
        for i,name in enumerate(listsNames):
            #here
            #[(1,"Shopping"),(2,"Homework")]
            #get the items belongs to the listid
            itemObjs=self.getItemsByListId(listsId[i])
            #some issue might happen in getItemsByListId
            print(f"itemObjs is {itemObjs}")
            #check if there is no item for the listID
            if not itemObjs is None:
            #so we have got the itemObjs
                for itemObj in itemObjs:#[<itemObj1>,<itemObj2>]
                    items[name].append(itemObj.name)
            else:
                print(f"there is no object in {name}")
                items[name].append("No Item In Such List")
        return items

    def addNewUserItem(self,username,item,listName):
        list_id=self.getListIDByUsernameAndListName(username,listName)
        newItem=ListItem(item,list_id)
        db.session.add(newItem)
        db.session.commit()
        print(f"item: {item} added to database")
        return
    def addNewListItem(self,username,listName):
    #what do we actually need to add a new list
    #firstly to get the userid for the username
        uid=self.getUserIDOf(username)
        #create new List Name
        newList=List(listName,uid)
        #add the list obj to the SQLALCHEMY_DATABASE_URI
        db.session.add(newList)
        db.session.commit()
    "endof DBManipulator"
DBM=DBManipulator()
def getUserIDOf(username):
    targetUser=User.query.filter_by(username=username).first()
    id=targetUser.id
    print(f"id of {username} is {id}")
    return id
def getListofUserByUserID(userID):
    targetList=List.query.filter_by(user_id=userID).all()
    return targetList
@app.route("/viewDB")
def viewDB():
    return render_template("db.html",Users=User.query.all())

@app.route("/addDum")
def addDum():
    nameList=["Sally","James","Hala","Chloe","Shrimp"]
    listList=["Shopping","Homework"]
    ShoppingList=["Buy Apple","Buy Cereal","Buy Egg","Buy Milk"]
    HomeworkList=["Finish MathHW","Finish PhysicsHW","Finish PsychologyHW"]

    UserInstancesList=func.createUsersList(nameList,"abc")
    db.session.add_all(UserInstancesList)
    db.session.commit()
    ListInstancesList=[]
    for name in nameList:
        userIdInUserTable=User.query.filter_by(username=name).first().id#e.g 1 is Sally
        for listname in listList:
            newListBeCreated=List(listname,userIdInUserTable)
            ListInstancesList.append(newListBeCreated)
    #List.query.filter_by(name="Chores").first().id
    db.session.add_all(ListInstancesList)
    print("add the lists to the list table for all user for all list")
    db.session.commit()
    #add sally items
    name="Sally"
    lName="Shopping"
    #find the list id of sally's shopping
        #find the user id of Sally
    SallyId=User.query.filter_by(username=name).first().id
    SallyShoppingListID=-1
    ShoppingLists=List.query.filter_by(name="Shopping").all()#List of ListObj
    for l in ShoppingLists:
        if l.user_id==SallyId:
            SallyShoppingListID=l.id
            break
    print(f"SallyShoppingListID={SallyShoppingListID}")
    #create list of item object for Sally
    ShoppingObjList=[ListItem("Buy Apple",SallyShoppingListID),ListItem("Buy Milk",SallyShoppingListID)]
    db.session.add_all(ShoppingObjList)
    db.session.commit()
    return redirect(url_for("login"))
    #return render_template("db.html", Users=User.query.all())
@app.route("/")
def default():
    return redirect(url_for("login"))
@app.route("/resetDB")
def resetDB():
    db.drop_all()#remove __tablename__
    db.create_all()
    return render_template("db.html",Users=User.query.all(), Lists=List.query.all(),itemList=ListItem.query.all())
@app.route("/register", methods=["POST","GET"])#default is get
def register():
    if request.method=="POST":#sending data from web to BE
        username=request.form["username"]
        password=request.form["password"]
        encryptedPw=generate_password_hash(password)
        print(f"generated encryptedPassword: {encryptedPw}")#from werkzeug.security import generate_password_hash
        #add the username and encrypted pw into the db
        DBM.addUserToDB(username,encryptedPw)
        session["UsernameFromRegister"]=username
        return redirect(url_for("login"))

    else:#load register.html
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])#default is get
def login():
    session["username"]=""
    session["logged_in"]=False
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        correctPassword=DBM.checkPassword(username,password)
        if(correctPassword):
            session["logged_in"]=True
            print("login successful")
            session["username"]=username
            items=getUserListItem(username)#[item1.name,item2.name.....]
            return redirect(url_for("userList"))
        else:
            print("username or password incorrect")
            return redirect(url_for("login"))

    else:
        return render_template("login.html")

@app.route("/userList",methods=["POST","GET"])
def userList():
    if not session["logged_in"]:
        return redirect(url_for("login"))
    username=session["username"]
    if request.method=="POST":#sending data from web to BE
        newItem=request.form["item"]
        listName=request.form["list name"]
        newList=request.form["newListName"]
        if newItem!="" and listName!="":
            DBM.addNewUserItem(username,newItem,listName)
        if newList!="":
            DBM.addNewListItem(username,newList)


        return redirect(url_for("userList"))
    else:#render the page
        id=getUserIDOf(username)
        UserLists=getListofUserByUserID(id)#List of listObject
        itemsDict=DBM.getItemsOfUser(username)#dictionary
        return render_template("userListItems.html",username=username,userLists=UserLists,itemsDict=itemsDict)
@app.route("/logout")
def logout():
    session["username"]=""
    session["logged_in"]=False
    return redirect(url_for("login"))
def getUserListItem(usernameFromFE):#Sally
    itemsBelongsToUser=[]
    userID=User.query.filter_by(username=usernameFromFE).first().id
    #find all the list belongs to the userID
    ListofListsBelongsToUser=List.query.filter_by(user_id=userID).all()
    #[list1ofSally,list2ofSally,list3]
    ListIDs=[]
    for l in ListofListsBelongsToUser:
        ListIDs.append(l.id)
    for Listid in ListIDs:#Listid=1
        #get all the item with Listid=1
        items=ListItem.query.filter_by(list_id=Listid).all()
        for i in items:
            itemsBelongsToUser.append(i)
    return itemsBelongsToUser

    #[item1,item2,...]
if __name__=="__main__":

    #db.drop_all()
    db.create_all()
    #addDum()
    app.run(debug=True)
    #debug=True allow us not to re-run
    #the server everytime we changed smth
