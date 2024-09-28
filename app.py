from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import otp
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="25315",
    database="hari"
)
@app.route('/')
def index():
    return render_template('index.html')
# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']  # Email field from signup form
        password = request.form['password']
        role = request.form['role']
        
        cursor = db.cursor()

        # Check if username (email) already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  # Changed from 'email' to 'username'
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return render_template('signup.html')

        # Store user details in the session temporarily
        session['signup_details'] = {
            'name': name,
            'username': username,
            'password': password,
            'role': role
        }

        # Send OTP to the user's email
        otp.send_otp(username)

        #flash("Sign-up successful! Please enter the OTP sent to your email.", "success")
        return redirect(url_for('otp_page', email=username))

    return render_template('signup.html')

@app.route('/otp')
def otp_page():
    # Ensure you are retrieving and passing the correct key
    email = request.args.get('email')  # This should match the key used in the redirect
    if not email:
        flash("Email is missing. Please try again.", "danger")
        return redirect(url_for('signup'))
    return render_template('getotp.html', email=email)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = request.form.get('email')  # Safely retrieve the email field
    if not email:
        flash('Email is missing in the form submission. Please try again.', 'danger')
        return redirect(url_for('otp_page'))  # Redirect or handle as needed

    otp_code = ''.join([
        request.form.get('otp1', ''), 
        request.form.get('otp2', ''), 
        request.form.get('otp3', ''), 
        request.form.get('otp4', ''), 
        request.form.get('otp5', ''), 
        request.form.get('otp6', '')
    ])
    if otp.verify_otp(email, otp_code):
        # Retrieve signup details from session
        signup_details = session.get('signup_details')

        if signup_details:
            cursor = db.cursor()

            # Insert user details into the database
            cursor.execute("INSERT INTO users (name, username, password, role) VALUES (%s, %s, %s, %s)", 
                           (signup_details['name'], signup_details['username'], signup_details['password'], signup_details['role']))
            db.commit()
            cursor.close()

            # Clear the signup details from the session
            session.pop('signup_details', None)

            #flash('OTP Verified Successfully! Signup is now complete.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Signup details not found. Please try signing up again.', 'danger')
            return redirect(url_for('signup'))
    else:
        flash('Invalid OTP, please try again', 'danger')
        return redirect(url_for('otp_page', email=email))
# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Check user credentials and fetch role from the database
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['user'] = {
                'id': user[0],  # Assuming 'id' is the first column in the 'users' table
                'name': user[1],  # Assuming 'name' is the second column
                'username': user[2],  # Assuming 'username' is the third column
                'role': user[4]  # Assuming 'role' is the fifth column
            }

            role = session['user']['role']
            
            if role == 'athlete':
                return redirect(url_for('athlete_dashboard'))
            elif role == 'academy':
                return redirect(url_for('academy_dashboard'))
        else:
            # Check if username exists but password is incorrect
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Incorrect password. Please try again.", "danger")
            else:
                flash("Incorrect username or email. Please try again.", "danger")
            return render_template('login.html')  # Render the same page with the error message

    return render_template('login.html')
@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
# Navigation Bar User Info
@app.route('/user_info')
def user_info():
    if 'user' in session:
        return render_template('user_info.html', user=session['user'])
    else:
        flash("Please log in to view your information.", "danger")
        return redirect(url_for('login'))
# Athlete Dashboard Route
@app.route('/athlete')
def athlete_dashboard():
    if 'user' in session and session['user']['role'] == 'athlete':
        return render_template('athlete.html')
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))
        
@app.route('/academy')
def academy_dashboard():
    if 'user' in session and session['user']['role'] == 'academy':
        return render_template('aca.html')
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

# Redirection Route for Calorie, Exercise, and Sports
@app.route('/redirect', methods=['GET', 'POST'])
def handle_redirection():
    if 'username' in session:
        option = request.args.get('option')
        if option == 'calorie':
            return redirect(url_for('calorie_intake'))
        elif option == 'exercise':
            return redirect(url_for('exercise_page'))
        elif option == 'challenge':
            return redirect(url_for('challenge_page'))
        elif option == 'stress':
            return redirect(url_for('stress_buster'))
        elif option == 'sports':
            return redirect(url_for('sports_selection'))
    else:
        
        return redirect(url_for('login')),400
# Calorie Intake Page
@app.route('/calorie')
def calorie_intake():
    return render_template('calorie.html')
@app.route('/streak')
def streak():
    return render_template('streak.html')
# Exercise Page
@app.route('/exercise')
def exercise_page():
    return render_template('exercise.html')
# Sports Selection Page
@app.route('/sports')
def sports_selection():
    return render_template('spa.html')
@app.route('/challenge')
def challenge_page():
    return render_template('cha.html')  # Render cha.html when redirected
@app.route('/stress')
def stress_buster():
    return render_template('str.html')
@app.route('/search_sport', methods=['POST'])
def search_sport():
    
    sport = request.form.get('sport')
    
    
    cursor = db.cursor(dictionary=True)
# Query to find coaches with the selected sport as their specialization
    cursor.execute("""
        SELECT a.name AS academy_name, a.address, a.phone AS academy_phone, a.email AS academy_email,
               c.name AS coach_name, c.specialization, c.phone AS coach_phone, c.email AS coach_email, c.achievements, c.certifications
        FROM academies a
        JOIN coaches c ON a.id = c.academy_id
        WHERE c.specialization = %s
    """, (sport,))
    
    result = cursor.fetchall()
    cursor.close()

    if result:
        return render_template('sport_results.html', sport=sport, data=result)
    else:
        flash(f"No academy or coach found specializing in {sport}")
        return redirect(url_for('sports_selection'))

# Result page to show matching academies and coaches
@app.route('/sport_results')
def sport_results():
    return render_template('sport_results.html')
# Add this route to your existing code
# Add this route to your existing code

@app.route('/select_academy', methods=['POST'])
def select_academy():
    academy_id = request.form.get('academy_id')

    # Fetch the selected academy's details
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM academies WHERE id = %s", (academy_id,))
    academy = cursor.fetchone()
    cursor.close()

    # Store the selected academy in the session
    session['selected_academy'] = academy

    # Redirect to the sport page
    return redirect(url_for('sport_page'))

@app.route('/sport')
def sport_page():
    # Fetch the selected academy details from session if necessary
    selected_academy = session.get('selected_academy', {})
    
    # Fetch the user's details from session
    user = session.get('user', {})

    # Pass both the selected academy and user details to the template
    return render_template('sport.html', academy=selected_academy, user=user)



@app.route('/submit_academy', methods=['POST'])
def submit_academy():
    academy_name = request.form.get('academyName')
    academy_address = request.form.get('academyAddress')
    academy_phone = request.form.get('academyPhone')
    academy_email = request.form.get('academyEmail')
    num_coaches = int(request.form.get('numCoaches'))
    
    cursor = db.cursor()
    
    # Insert academy details into the database
    cursor.execute("INSERT INTO academies (name, address, phone, email) VALUES (%s, %s, %s, %s)",
                   (academy_name, academy_address, academy_phone, academy_email))
    academy_id = cursor.lastrowid
    
    # Insert coach details into the database
    for i in range(1, num_coaches + 1):
        coach_name = request.form.get(f'coachName{i}')
        coach_specialization = request.form.get(f'coachSpecialization{i}')
        coach_achievements = request.form.get(f'coachAchievements{i}')
        coach_phone = request.form.get(f'coachPhone{i}')
        coach_email = request.form.get(f'coachEmail{i}')
        coach_certifications = request.form.get(f'coachCertifications{i}')
        coach_gender = request.form.get(f'coachGender{i}')
        
        cursor.execute("INSERT INTO coaches (academy_id, name, specialization, achievements, phone, email, certifications, gender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (academy_id, coach_name, coach_specialization, coach_achievements, coach_phone, coach_email, coach_certifications, coach_gender))
    
    db.commit()
    cursor.close()

    # Redirect to the submit.html page after successful registration
    return redirect(url_for('submit_page'))

# Submit Page Route
@app.route('/submit')
def submit_page():
    return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True)