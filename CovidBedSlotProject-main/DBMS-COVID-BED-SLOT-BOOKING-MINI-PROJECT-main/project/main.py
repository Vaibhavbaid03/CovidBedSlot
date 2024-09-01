from flask import Flask, redirect, render_template, flash, request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session



# from flask_mail import Mail
import json


# Initialize the Flask application
app = Flask(__name__)
app.secret_key = "adeshjain"

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Adeshjain%402473@localhost/coviddata'
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load configurations
with open(r'c:\Users\DELL\Desktop\dbsm_covid\backend\config.json', 'r') as c:
    params = json.load(c)["params"]

# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'regular':
        return User.query.get(int(user_id))
    elif session.get('user_type') == 'hospital':
        return Hospitaluser.query.get(int(user_id))
    return None

# Database Models
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50))
    dob = db.Column(db.String(1000))

class Hospitaluser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20))
    email = db.Column(db.String(50))
    password = db.Column(db.String(1000))

class Hospitaldata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    hname = db.Column(db.String(100))
    normalbed = db.Column(db.Integer)
    hicubed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    vbed = db.Column(db.Integer)

class Trig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20))
    normalbed = db.Column(db.Integer)
    hicubed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    vbed = db.Column(db.Integer)
    querys = db.Column(db.String(50))
    date = db.Column(db.String(50))

class Bookingpatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    bedtype = db.Column(db.String(100))
    hcode = db.Column(db.String(20))
    spo2 = db.Column(db.Integer)
    pname = db.Column(db.String(100))
    pphone = db.Column(db.String(100))
    paddress = db.Column(db.String(100))

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/trigers")
def trigers():
    query = Trig.query.all()
    return render_template("trigers.html", query=query)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')
        
        user = User.query.filter_by(srfid=srfid).first()
        emailUser = User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or SRF ID is already taken", "warning")
            return render_template("usersignup.html")
        
        new_user = User(srfid=srfid, email=email, dob=dob)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success. Please Login", "success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        srfid = request.form.get('srf')
        dob = request.form.get('dob')
        user = User.query.filter_by(srfid=srfid).first()
        if user and user.dob == dob:
            login_user(user)
            session['user_type'] = 'regular'
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")

@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_type'] = 'hospital'
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username == params.get('user') and password == params['password']:
            session['user'] = username
            flash("Login success", "info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials", "danger")

    return render_template("admin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # This clears all session data
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/addHospitalUser', methods=['POST', 'GET'])
def hospitalUser():
    if 'user' in session and session['user'] == params['user']:
        if request.method == "POST":
            hcode = request.form.get('hcode')
            email = request.form.get('email')
            password = request.form.get('password')
            encpassword = generate_password_hash(password)  
            hcode = hcode.upper()      
            emailUser = Hospitaluser.query.filter_by(email=email).first()
            if emailUser:
                flash("Email is already taken", "warning")
                return render_template("addHosUser.html")

            query = Hospitaluser(hcode=hcode, email=email, password=encpassword)
            db.session.add(query)
            db.session.commit()

            flash("Data Sent and Inserted Successfully", "warning")
            return render_template("addHosUser.html")
    else:
        flash("Login and try Again", "warning")
        return render_template("addHosUser.html")

# Test if the database is connected
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'

@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logged out", "primary")
    return redirect('/admin')

@app.route("/addhospitalinfo", methods=['POST', 'GET'])
def addhospitalinfo():
    email = current_user.email
    #print(f"Current user email: {current_user.email}")

    posts = Hospitaluser.query.filter_by(email=email).first()
    if posts is None:
        flash("No hospital user found with the provided email.", "warning")
        return redirect(url_for('hospitallogin'))  
    hcode = posts.hcode
    postsdata = Hospitaldata.query.filter_by(hcode=hcode).first()

    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        nbed = request.form.get('normalbed')
        hbed = request.form.get('hicubeds')
        ibed = request.form.get('icubeds')
        vbed = request.form.get('ventbeds')
        hcode = hcode.upper()
        huser = Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser = Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present, you can update it.", "primary")
            return render_template("hospitaldata.html")
        if huser:
            query = Hospitaldata(hcode=hcode, hname=hname, normalbed=nbed, hicubed=hbed, icubed=ibed, vbed=vbed)
            db.session.add(query)
            db.session.commit()
            flash("Data Is Added", "primary")
            return redirect('/addhospitalinfo')
        else:
            flash("Hospital Code does not exist.", "warning")
            return redirect('/addhospitalinfo')

    return render_template("hospitaldata.html", postsdata=postsdata)

@app.route("/hedit/<string:id>", methods=['POST', 'GET'])
@login_required
def hedit(id):
    posts = Hospitaldata.query.filter_by(id=id).first()

    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        nbed = request.form.get('normalbed')
        hbed = request.form.get('hicubeds')
        ibed = request.form.get('icubeds')
        vbed = request.form.get('ventbeds')
        hcode = hcode.upper()
        post = Hospitaldata.query.filter_by(id=id).first()
        post.hcode = hcode
        post.hname = hname
        post.normalbed = nbed
        post.hicubed = hbed
        post.icubed = ibed
        post.vbed = vbed
        db.session.commit()
        flash("Slot Updated", "info")
        return redirect("/addhospitalinfo")

    return render_template("hedit.html", posts=posts)

@app.route("/hdelete/<string:id>", methods=['POST', 'GET'])
@login_required
def hdelete(id):
    post = Hospitaldata.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Data Deleted", "danger")
    return redirect("/addhospitalinfo")

@app.route("/pdetails", methods=['GET'])
@login_required
def pdetails():
    code = current_user.srfid
    print(code)
    data = Bookingpatient.query.filter_by(srfid=code).first()
    return render_template("detials.html", data=data)

@app.route("/slotbooking", methods=['POST', 'GET'])
@login_required
def slotbooking():
    query1 = Hospitaldata.query.all()
    query = Hospitaldata.query.all()

    if request.method == "POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')

        check2 = Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient = Bookingpatient.query.filter_by(srfid=srfid).first()

        if checkpatient:
            flash("SRF ID is already registered.", "warning")
            return render_template("booking.html", query=query, query1=query1)

        if not check2:
            flash("Hospital Code does not exist.", "warning")
            return render_template("booking.html", query=query, query1=query1)

        dbb = Hospitaldata.query.filter_by(hcode=hcode).first()

        if dbb:
            seat = 0
            if bedtype == "NormalBed":
                seat = dbb.normalbed
                if seat > 0:
                    dbb.normalbed = seat - 1
            elif bedtype == "HICUBed":
                seat = dbb.hicubed
                if seat > 0:
                    dbb.hicubed = seat - 1
            elif bedtype == "ICUBed":
                seat = dbb.icubed
                if seat > 0:
                    dbb.icubed = seat - 1
            elif bedtype == "VENTILATORBed":
                seat = dbb.vbed
                if seat > 0:
                    dbb.vbed = seat - 1

            if seat > 0:
                db.session.commit()
            else:
                flash("No available beds of the selected type.", "warning")
                return render_template("booking.html", query=query, query1=query1)

            res = Bookingpatient(srfid=srfid, bedtype=bedtype, hcode=hcode, spo2=spo2, pname=pname, pphone=pphone, paddress=paddress)
            db.session.add(res)
            db.session.commit()
            flash("Slot is booked. Kindly visit the hospital for further procedure.", "success")
            return render_template("booking.html", query=query, query1=query1)
        else:
            flash("Something went wrong.", "danger")
            return render_template("booking.html", query=query, query1=query1)

    return render_template("booking.html", query=query, query1=query1)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
