from flask import Flask, render_template, request, session, flash, redirect, url_for
import sqlite3 as sql
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a more secure key in production

# Initialize the databases
def init_db():
    with sql.connect("agricultureuser.db") as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS agriuser (
                        id INTEGER AUTO INCREMENT,
                        name TEXT NOT NULL,
                        phono TEXT NOT NULL,
                        email TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        district TEXT NOT NULL)''')
        con.commit()
    
    with sql.connect("industryuser.db") as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS industryuser (
                        id INTEGER AUTO INCREMENT ,
                        name TEXT NOT NULL,
                        phono TEXT NOT NULL,
                        email TEXT NOT NULL,
                        username TEXT NOT NULL ,
                        password TEXT NOT NULL,
                        district TEXT NOT NULL)''')
        con.commit()

    with sql.connect("equipment.db") as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS equipment (
                        equipment_id INTEGER,
                        equipment_name TEXT NOT NULL,
                        price_per_day REAL NOT NULL,
                        available_date TEXT NOT NULL,
                        total_equipments INTEGER NOT NULL,
                        available_equipments INTEGER NOT NULL,
                        industry_id text)''')
        con.commit()

init_db()

# Login required decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash("You need to log in first.")
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Preserve the function name
    return wrapper

# Route to the home page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/allfarmers', methods=['GET'])
def all_farmers():
    with sql.connect("agricultureuser.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM agriuser")
        farmers = cur.fetchall()
    
    return render_template('allfarmers.html', farmers=farmers)

# User sign-up
@app.route('/enternew', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        try:
            nm = request.form['Name']
            phonno = request.form['MobileNumber']
            email = request.form['email']
            unm = request.form['Username']
            passwd = request.form['password']
            district = request.form['district']
            hashed_passwd = generate_password_hash(passwd)
            with sql.connect("agricultureuser.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO agriuser(name, phono, email, username, password, district) VALUES(?, ?, ?, ?, ?, ?)",
                            (nm, phonno, email, unm, hashed_passwd, district))
                con.commit()
                msg = "User record successfully added"
        except sql.IntegrityError:
            msg = "Username already exists"
        except Exception as e:
            msg = f"Error: {str(e)}"
        return render_template("result.html", msg=msg)
    return render_template('signup.html')

# Industry sign-up
@app.route('/enterindustry', methods=['GET', 'POST'])
def new_industry_user():
    if request.method == 'POST':
        try:
            nm = request.form['Name']
            phonno = request.form['MobileNumber']
            email = request.form['email']
            unm = request.form['Username']
            passwd = request.form['password']
            district = request.form['district']
            hashed_passwd = generate_password_hash(passwd)
            with sql.connect("industryuser.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO industryuser(name, phono, email, username, password, district) VALUES(?, ?, ?, ?, ?, ?)",
                            (nm, phonno, email, unm, hashed_passwd, district))
                con.commit()
                msg = "Account Created Succussfully"
        except sql.IntegrityError:
            msg = "Industry username already exists"
        except Exception as e:
            msg = f"Error: {str(e)}"
        return render_template("result.html", msg=msg)
    return render_template('industry_signup.html')

# User login
@app.route('/userlogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        usrname = request.form['username']
        passwd = request.form['password']
        with sql.connect("agricultureuser.db") as con:
            cur = con.cursor()
            cur.execute("SELECT username, email, phono, password, district FROM agriuser WHERE username=?", (usrname,))
            account = cur.fetchone()
            if account and check_password_hash(account[3], passwd):
                session['logged_in'] = True
                session['username'] = account[0]
                session['email'] = account[1]
                session['phone'] = account[2]
                session['district'] = account[4]
                return redirect(url_for('farmershome'))
            else:
                flash("Invalid user credentials")
                return render_template('login.html')
    return render_template("login.html")

@app.route('/farmershome')

def farmershome():
    return render_template('farmershome.html')

# Industry login
@app.route('/industrylogin', methods=['GET', 'POST'])
def industry_login():
    if request.method == 'POST':
        usrname = request.form['username']
        passwd = request.form['password']
        with sql.connect("industryuser.db") as con:
            cur = con.cursor()
            cur.execute("SELECT username, email, phono, password, district FROM industryuser WHERE username=?", (usrname,))
            account = cur.fetchone()
            if account and check_password_hash(account[3], passwd):
                session['logged_in'] = True
                session['username'] = account[0]
                session['email'] = account[1]
                session['phone'] = account[2]
                session['district'] = account[4]
                return redirect(url_for('industry_home'))
            else:
                flash("Invalid industry credentials")
                return render_template('industry_login.html')
    return render_template("industry_login.html")

@app.route('/industry_home')

def industry_home():
    return render_template('industry_home.html')

@app.route('/adminlogin')

def adminlogin():
    return render_template('adminlogin.html')

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'sridevi'

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
             
            return render_template('admin_dashboard.html')
    return render_template('adminlogin.html')

@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template('admin_dashboard.html')


# User profile
@app.route('/profile')

def profile():
    return render_template('profile.html', username=session['username'], email=session['email'], phone=session['phone'], district=session['district'])

# Industry profile
@app.route('/industry_profile')

def industry_profile():
    return render_template('industry_profile.html', username=session['username'], email=session['email'], phone=session['phone'], district=session['district'])

# Add equipment route
@app.route('/add_equipment', methods=['GET', 'POST'])

def add_equipment():
    if request.method == 'POST':
        try:
            equipment_id = request.form.get('equipment_id')  # Ensure this matches the form input name
            equipment_name = request.form.get('equipment_name')
           # Ensure you have this set in the session after login
            price_per_day = request.form.get('price_per_day')
            available_date = request.form.get('available_date')
            total_equipments = request.form.get('total_equipments')
            available_equipments = request.form.get('available_equipments')
            industry_id = request.form.get('industry_id')

            # Validate input
            if not all([equipment_id, equipment_name, price_per_day, available_date, total_equipments, available_equipments,industry_id]):
                flash("All fields are required.")
                return render_template("add_equipment.html")

            with sql.connect("equipment.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO equipment (equipment_id, equipment_name, price_per_day, available_date, total_equipments, available_equipments, industry_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (equipment_id, equipment_name, price_per_day, available_date, total_equipments, available_equipments, industry_id))

                con.commit()
                flash("Equipment added successfully")
                return redirect(url_for('view_equipment'))  # Redirect to the equipment list page

        except Exception as e:
            flash(f"Error: {str(e)}")
            return render_template("result.html", msg=str(e))

    return render_template("add_equipment.html")

@app.route('/view_industries', methods=['GET'])
def view_industries():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    with sql.connect("industryuser.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM industryuser")
        industry_list = cur.fetchall()

    return render_template('view_industries.html', industry_list=industry_list)

# View equipment route
@app.route('/view_equipment')

def view_equipment():
    with sql.connect("equipment.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM equipment")
        equipment_list = cur.fetchall()
    return render_template("view_equipment.html", equipment_list=equipment_list)

# Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('phone', None)
    session.pop('district', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))

# Main execution
if __name__ == '__main__':
    app.run(debug=True)
