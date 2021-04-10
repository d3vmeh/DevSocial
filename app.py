from flask import Flask, render_template, request, redirect, session, flash
from flask_pymongo import PyMongo
import os
from passlib.hash import pbkdf2_sha256 as pbk
from datetime import datetime
import random

if os.environ.get("MONGO_URI") == None:
    f = open("connectionstring.txt",'r')
    connectionstring = f.read().strip()

else:
    connectionstring = os.environ.get("MONGO_URI")


app = Flask(__name__)
app.config["MONGO_URI"] = connectionstring
app.config["SECRET_KEY"] = "102102"
print("Connected to Database")
mongo = PyMongo(app)



@app.route("/")
def landingPage():
    #code for adding extra elements by removing accounts
    # for i in mongo.db.users.find():
    #     print(i)
    #     firstname = i["firstname"]
    #     lastname = i["lastname"]
    #     email = i["email"]
    #     password = i["password"]
    #     date = i["date"]
    #     friends = [i["email"]]
    #     requests = []
    #     i = {"firstname":firstname,"lastname":lastname,"email":email,"password":password,"date":date,"friends":friends,"requests":requests}
        
    #     mongo.db.users.delete_one({"email":email})
    #     mongo.db.users.insert_one(i)
    #     print(i)
        
    if "email" in session:
        user = mongo.db.users.find_one({"email":session["email"]})
        return render_template("index.html",requestcount=len(user["requests"]))

    return render_template("index.html",requestcount=0)


@app.route("/home")
def homepage():
    if "email" in session:
        user = mongo.db.users.find_one({"email":session["email"]})

        allposts = []
        colors = ["success","primary","info","danger","warning"]

        for i in mongo.db.posts.find():
            #print(i)
            i["color"] = random.choice(colors)
            if i["email"] in user["friends"]:
                allposts.append(i)
            
        
        allposts.reverse()

        #print("ehhlo",allposts[0]["email"])
        return render_template("home.html",username=user["firstname"],posts=allposts,requestcount=len(user["requests"]))#,postcontent=allposts[0]["post"],posttime=allposts[0]["time"])


    else:
        return redirect("/login")

@app.route("/register",methods=["GET","POST"])
def register():
    if (request.method == "GET"):
        return render_template("register.html",requestcount=0)
    else:
        
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = pbk.hash(request.form["password"])
        date = request.form["date"]
        useraccount = mongo.db.users.find_one({"email":email})
        if useraccount is not None:
            flash("Email already in use","error")
            return redirect("/register")
        
        mongo.db.users.insert_one({"firstname":firstname,"lastname":lastname,"email":email,"password":password,"date":date,"friends":[email],"requests":[]})
        
        return redirect("/logout")


@app.route("/login",methods=["GET","POST"])
def login():
    #print(session)
    if "email" in session:
        return redirect("/home")
    else:
        if (request.method == "GET"):
            if "email" in session:
                user = mongo.db.users.find_one({"email":session["email"]})
                return render_template("login.html",requestcount=len(user["requests"]))
            return render_template("login.html",requestcount=0)
        else:
            givenemail = request.form["email"]
            useraccount = mongo.db.users.find_one({"email":givenemail})
            if useraccount == None:
                flash("Invalid Email","error")
                return redirect("/login")
            else:
                givenpassword = request.form["password"]
                if pbk.verify(givenpassword,useraccount["password"]):
                    flash("Logged in successfully","success")
                    session["email"] = givenemail
                    #print(session)
                    return redirect("/home")
                else:
                    flash("Invalid password","error")
                    return redirect("/login")
    
        
        
@app.route("/logout")
def logout():
    if "email" in session:
        session.pop("email")
        flash("Successfully Logged Out","success")

    return redirect("/login")


@app.route("/createpost",methods=["GET","POST"])
def createpost():
    if "email" not in session:
        #print("not logged in")
        return redirect("/login")
    else:
        if (request.method == "GET"):
            user = mongo.db.users.find_one({"email":session["email"]})
            return render_template("createpost.html",requestcount=len(user["requests"]))
        else:
            givenpost = request.form["post"]
            #print(len(givenpost))
            mongo.db.posts.insert_one({"email":session["email"],"post":givenpost,"time":datetime.now().strftime("%B %d %Y %I:%M %p")})
            return redirect("/home")

    
    return redirect("/login")


@app.route("/addfriend",methods=["GET","POST"])
def addfriend():
    if "email" not in session:
        #print("not logged in")
        return redirect("/login")
    if (request.method == "GET"):
        user = mongo.db.users.find_one({"email":session["email"]})
        return render_template("addfriend.html",requestcount=len(user["requests"]))
    else:
        user = mongo.db.users.find_one({"email":session["email"]})
        requestemail = request.form["email"]
        friendrequested = mongo.db.users.find_one({"email":requestemail})
        #print(friendrequested)
        otherrequests=friendrequested["requests"]

        if requestemail in user["friends"]:
            flash("You are already friends with this user!")
            return redirect("/addfriend")
        
        if user["email"] in friendrequested["requests"]:
            flash("You already sent a friend request to this user!")
            return redirect("/addfriend")

        otherrequests.append(session["email"])
        
        mongo.db.users.update_one({"email":requestemail},{"$set":{"requests":otherrequests}})
        return redirect("/home")
        

@app.route("/requests",methods=["GET","POST"])
def requests():
    if "email" not in session:
        #print("not logged in")
        return redirect("/login")
    if (request.method == "GET"):
        user = mongo.db.users.find_one({"email":session["email"]})

        return render_template("requests.html",requests=user["requests"],requestcount=len(user["requests"]))
    else:
        user = mongo.db.users.find_one({"email":session["email"]})
        myrequests = user["requests"]
        myfriends = user["friends"]
        # requestemail = request.form["email"]
        # friendrequested = mongo.db.users.find_one({"email":requestemail})
        # #print(friendrequested)
        # otherrequests=friendrequested["requests"]
        # otherrequests.append(session["email"])
        
        otheruseremail = request.form["r"]
        otheruser = mongo.db.users.find_one({"email":otheruseremail})
        otherfriends = otheruser["friends"]
        #mongo.db.users.update_one({"email":requestemail},{"$set":{"requests":otherrequests}})
        if (request.form["action"] == "Accept"):
            myfriends.append(otheruseremail)
            myrequests.remove(otheruseremail)
            otherfriends.append(user["email"])
            mongo.db.users.update_one({"email":user["email"]},{"$set":{"requests":myrequests,"friends":myfriends}})
            mongo.db.users.update_one({"email":otheruser["email"]},{"$set":{"friends":otherfriends}})
            
            return redirect("/requests")
        if (request.form["action"] == "Decline"):
            myrequests.remove(otheruseremail)
            mongo.db.users.update_one({"email":user["email"]},{"$set":{"requests":myrequests}})
            return redirect("/requests")

        return redirect("/home")


@app.route("/friends",methods=["GET","POST"])
def friends():
    if "email" not in session:
        #print("not logged in")
        return redirect("/login")
    if (request.method == "GET"):
        user = mongo.db.users.find_one({"email":session["email"]})
        f = user["friends"]
        f.remove(user["email"])
        return render_template("friends.html",requests=user["requests"],requestcount=len(user["requests"]),friends=f)
    else:
        user = mongo.db.users.find_one({"email":session["email"]})
        friendemail = request.form["friendemail"]
        friend = mongo.db.users.find_one({"email":friendemail})
        myfriends = user["friends"]
        myfriends.remove(friendemail)
        friendsfriends = friend["friends"]
        friendsfriends.remove(user["email"])

        mongo.db.users.update_one({"email":user["email"]},{"$set":{"friends":myfriends}})
        mongo.db.users.update_one({"email":friendemail},{"$set":{"friends":friendsfriends}})

        return redirect("/friends")


if __name__ == "__main__":
    app.run()