from flask import Flask, render_template, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
import json
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = "3627227"
with open("config.JSON", "r") as f:
    param = json.load(f)["key"]


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = param["gmail-admin"]
app.config["MAIL_PASSWORD"] = param["gmail-password"]  # MUST be App Password
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = param["local-uri"]
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)


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
             subject=name + " 🎉 Your Registration for the E.V.O.L.V.E Program is Successful!",
    
                      body=
                    "Hi " + name + ",\n"
                  "Thank you for registering for the E.V.O.L.V.E (Via Online Learning & Virtual Evolution) Internship & Volunteer Program.\n"
                "We are happy to let you know that your registration has been received successfully.\n\n"
 
                 "Here are your details:\n"
                 "- Email ID: " + emailid + "\n"
                   "- Contact Number: " + contact + "\n"
                "- School: " + college + "\n"
              "- Class: " + course + "\n"
               "- Registration Date: " + date + "\n\n"

              "What Happens Next?\n"
              "Our E.V.O.L.V.E team will review your details and contact you soon with the next steps.\n"
              "Please keep checking your email and phone for updates.\n\n"

              "A Little Motivation for You:\n"
              "By joining E.V.O.L.V.E, you are taking a wonderful step toward learning, growing, "
              "and exploring your potential. Stay curious, stay confident — great opportunities "
              "are waiting for you!\n\n"

              "If you have any questions, feel free to reply to this email.\n\n"
    
              "Warm regards,\n"
              "Team E.V.O.L.V.E\n"
              "Empowering Visionaries, Offering Leadership, Value & Excellence\n"

              "------------------------------\n"
                "📩 Contact Support:\n"
                  "Email: " + param["gmail-main-admin"] + "\n"
                  "Phone: +91-8853080716\n"
                  "Website: https://yourwebsite.com\n"

                   "------------------------------",
    
            sender=param["gmail-admin"],
            recipients=[emailid]
)
             # ----- ADMIN NOTIFICATION EMAIL -----

             admin_msg = Message(
             subject="📥 New Registration Received - " + name,
    
            body=
             "Hello Sunil,\n\n"
             "A new student has successfully registered for the E.V.O.L.V.E Program.\n\n"
             "Here are the details:\n"
             "- Name: " + name + "\n"
             "- Email ID: " + emailid + "\n"
             "- Contact Number: " + contact + "\n"
             "- School: " + college + "\n"
                      "- Class: " + course + "\n"
             "- Registration Date: " + date + "\n\n"
    
             "Please check the admin panel for more information.\n\n"
             "Regards,\n"
              "Sunil Singh\n"
              "CTO – E.V.O.L.V.E (Via Online Learning & Virtual Evolution)\n"
             "E.V.O.L.V.E System",
    
              sender=param["gmail-admin"],
              recipients=[param["gmail-admin"]]       # Admin को भेजेगा
)
           
             try:
                mail.send(msg)
                mail.send(admin_msg)
             except Exception as e:
                 print("Email Error:", e)
                 flash("You are registered, but email could not be sent due to a server issue.", "warning")
                 return redirect('/')  
             flash("You are successfully register here","success")
             return redirect('/')
    except Exception as e:
        flash("This email is already registered or an error occur" ,"warning")
        return redirect('/')         
    
    return render_template('register.html')



@app.route('/registeredlist')
def registeredlist():
    if 'admin' not in session:
        flash("Please login first!", "warning")
        return redirect('/admin')

    contents = Backend.query.all()
    return render_template('registeredlist.html', contents=contents)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if email == param["email-admin"]:
            # hashed password verify
            if param["password-admin"] ==password:
                
                # session set
                session['admin'] = True
                session['email'] = email

                flash("You are successfully logged in!", "success")
                return redirect('/registeredlist')
            else:
                flash("Invalid password!", "danger")
                return redirect('/admin')
        else:
            flash("Invalid admin email!", "danger")
            return redirect('/admin')

    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out!", "info")
    return redirect('/admin')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



app.run(debug=True)