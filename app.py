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
    #     i = {"firstname":firstname,"lastname":lastname,"email":email,"password":password,"date":date,"friends":friends}
        
    #     mongo.db.users.delete_one({"email":"sumeet.mehra@gmail.com"})
    #     mongo.db.users.insert_one(i)
    #     break
    
    return render_template("index.html")

@app.route("/home")
def homepage():
    if "email" in session:
        user = mongo.db.users.find_one({"email":session["email"]})

        allposts = []
        colors = ["success","primary","info","danger","warning"]

        for i in mongo.db.posts.find():
            #print(i)
            i["color"] = random.choice(colors)
            allposts.append(i)
            
        
        allposts.reverse()

        #print("ehhlo",allposts[0]["email"])
        return render_template("home.html",username=user["firstname"],posts=allposts)#,postcontent=allposts[0]["post"],posttime=allposts[0]["time"])


    else:
        return redirect("/login")

@app.route("/register",methods=["GET","POST"])
def register():
    if (request.method == "GET"):
        return render_template("register.html")
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
        
        mongo.db.users.insert_one({"firstname":firstname,"lastname":lastname,"email":email,"password":password,"date":date,"friends":[email]})
        
        return redirect("/login")


@app.route("/login",methods=["GET","POST"])
def login():
    #print(session)
    if "email" in session:
        return redirect("/home")
    else:
        if (request.method == "GET"):
            return render_template("login.html")
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
            return render_template("createpost.html")
        else:
            givenpost = request.form["post"]
            #print(len(givenpost))
            mongo.db.posts.insert_one({"email":session["email"],"post":givenpost,"time":datetime.now().strftime("%B %d %Y %I:%M %p")})
            return redirect("/home")

    
    return redirect("/login")





if __name__ == "__main__":
    app.run()