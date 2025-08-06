from flask import Flask, render_template, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
import json
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = "123_secret_key"
with open("config.JSON", "r") as f:
    param = json.load(f)["key"]

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = param["gmail-admin"]
app.config["MAIL_PASSWORD"] = param['gmail-password']
mail = Mail(app)


class Backend(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    emailid = db.Column(db.String(20), unique=True, nullable=False)
    contactno = db.Column(db.String(15), nullable=False)
    college = db.Column(db.String(20), nullable=True)
    course = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(10))


@app.route('/', methods=['GET', 'POST'])
def Home():
    try:
          if (request.method == "POST"):
             name = request.form.get("name")
             emailid = request.form.get("email")
             contact = request.form.get("phone")
             college = request.form.get("college")
             course = request.form.get("course")
             date = datetime.now().strftime("%Y-%m-%d")
             data = Backend(name=name, emailid=emailid, contactno=contact,
                            college=college, course=course, date=date)
             db.session.add(data)
             db.session.commit()
             msg = Message(
                subject=name + " You are Successfully Registerd",
                body=
                "Hi "+name + ",Thank you for registering for the internship."+ "\n"+"Here are your details: "
                +"\n"+ " - Email ID: "+ emailid + "\n" +"Contact Number:  "
                + contact +"\n"+"- College:  "+ college +"\n"+"- Course:  " + course 
                +"\n"+"- Registration Date:  "+date 
                +"\n"+"We’re excited to have you on board and look forward to working with you." 
                +"\n"+"If you have any questions, feel free to reply to this email."
                +"\n"+"Best regards,  " +"\n"+"Internship Team",
                sender=param["gmail-admin"],
                recipients=[emailid]
            )
             
             mail.send(msg)
             flash("You are successfully register here","success")
             return redirect('/')
    except Exception as e:
        flash("This email is already registered or an error occur" ,"warning")
        return redirect('/')         
    
    return render_template('register.html')



@app.route('/registeredlist')
def registered():
    contents = Backend.query.all()
    return render_template('registeredlist.html',contents=contents)

@app.route('/admin',methods=['GET','POST'])
def admin():
    if(request.method=="POST"):
        email=request.form.get('email')
        password=request.form.get('password')
        if(email==param["email-admin"]):
            if(password==param["password-admin"]):
                flash("your are successfully login","success")
                return redirect('/registeredlist')
            else :
                flash("Please enter valid password","danger")
                return redirect('/admin')
        else:
            flash("Admin Email is invalid","danger")
            return redirect('/admin')
      
      
    return render_template('admin.html')



app.run(debug=True)