from flask import Flask,render_template,redirect,request
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")#connect to mongoDB server
myclient.drop_database('mydatabase')#drop if any database exist with same name
db = myclient["mydatabase"]#create database "db"
mycol = db["customers"]#create table mycol
app = Flask(__name__)#inform flask that web app name is "app" which is used later as "@app"

mydict = { "name": "Sanjeev", "designation": "CEO","rman":"None" ,'under':[]}
x = mycol.insert(mydict)#adding the first employee (top of hierarchy)

def make_list(l,down,index):
    k = index#current employee index {for CEO=0}
    emp = mycol.find_one({'_id':l[index]})#get the Complete Object of current Object
    down.append(len(emp['under']))#count of employees under current employee
    for e in emp['under']:#for each Object id in "under" Field 
        l.append(e) #append it to list "l"
        k = make_list(l,down,k+1)#recursively call funtion and keep updating the index for next iteration in DFS logic 
    return k#it will update the parent recursive call index (increment by one if no employee under current employee) 
@app.route('/list')
def my_list():
    emp = mycol.find_one({'designation':"CEO"})#start with the CEO for displaying the Hierarchy
    lis=[]#initiasing the empty list to store the object ID's of the employee
    lis.append(emp['_id'])#append CEO id
    down=[]#initiasing the empty list to store the count of the employee under each employee
    make_list(lis,down,0)#function will update the list(both "lis" and "down") with by traversing the employees in depth first search
    #above "0" is used to start with CEO
    gg=[]#store the details of employee to pass to HTML page to display
    for l in lis:#for each Object Id in lis list fetch the whole object and append the "gg" list with details of each employee
        h = mycol.find_one({'_id':l})#return the complete Object with given Id
        gg.append([h['name'],h['designation']])#only name and designation are appended each Employee
    return render_template("list.html",gg=gg,down=down)#gg is passed as gg and down is passed as down
#render template is used to redirect to given page with required parameters
	
@app.route('/input', methods=['GET','POST'])
def my_form_post():
    if request.method=='POST':
        name = request.form['name']
        designation = request.form['desig']
        rman = request.form['rman']
        mydict = { "name": name, "designation":designation,"rman":rman,"under":[] }#object with data from FORM
        if rman=="None":#for the first employee no reporting manager will be there so enter "None"
       	    mycol.insert(mydict)#add to database's table
       	else:
       	    man = mycol.find_one({"name":rman})#check if reporting manager exist or not
       	    if man:#if true
       	        g=mycol.insert(mydict)#add to database's table
       	        k=man['under'] #copy the list of employees in the reporting manager "under" field
       	        k.append(g)#append the reporting manager "under" field with new employee ObjectID
       	        mycol.update_one({'_id':man['_id']},{'$set':{'under':k}})#update the reporting manager "under" field
       	    else:
       	        return render_template("input.html",error="True")#if False then pass "error" as True to alert 
        return redirect("/")#after submitting the detail , redirect to Home page
    return render_template("input.html",error=False)#if request is GET that is just to open "input.html"

@app.route("/")
def hello():
    return render_template("home.html")
