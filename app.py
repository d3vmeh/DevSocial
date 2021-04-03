from flask import Flask, render_template, request, redirect, session, flash
from flask_pymongo import PyMongo
import os
from passlib.hash import pbkdf2_sha256 as pbk



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
    return render_template("index.html")

@app.route("/home")
def homepage():
    if "email" in session:
        user = mongo.db.users.find_one({"email":session["email"]})
        return render_template("home.html",username=user["firstname"])
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
        mongo.db.users.insert_one({"firstname":firstname,"lastname":lastname,"email":email,"password":password,"date":date})
        
        return redirect("/login")


@app.route("/login",methods=["GET","POST"])
def login():
    print(session)
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
                    print(session)
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




if __name__ == "__main__":
    app.run(debug=True)