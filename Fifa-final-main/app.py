from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Bisht@321'  # Add your MySQL password if needed
app.config['MYSQL_DB'] = 'flask_app'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']
        first = request.form['first_name']
        last = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        line = request.form['address_line']
        city = request.form['city']
        state = request.form['state']
        pin = request.form['pincode']
        file = request.files['profile_pic']

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        hashed_password = generate_password_hash(password)

        try:
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO users (user_type, first_name, last_name, username, email, password,
                           profile_pic, address_line, city, state, pincode)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                        (user_type, first, last, username, email, hashed_password,
                         filename, line, city, state, pin))
            mysql.connection.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Username already exists or DB error!", "danger")
            print(str(e))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user[6], password):
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    return render_template('dashboard.html', user=user)

@app.route('/doctor/create_blog', methods=['GET', 'POST'])
def create_blog():
    if 'user' not in session or session['user'][1] != 'Doctor':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        summary = request.form['summary']
        content = request.form['content']
        is_draft = 'is_draft' in request.form
        image_file = request.files['image']

        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        else:
            filename = None

        doctor_id = session['user'][0]  # Assuming user[0] is the user ID

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO blogs (doctor_id, title, image, category, summary, content, is_draft)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (doctor_id, title, filename, category, summary, content, is_draft))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('doctor_dashboard'))

    categories = ['Mental Health', 'Heart Disease', 'Covid19', 'Immunization']
    return render_template('create_blog.html', categories=categories)

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'user' not in session or session['user'][1] != 'Doctor':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    doctor_id = session['user'][0]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM blogs WHERE doctor_id = %s", (doctor_id,))
    blogs = cur.fetchall()
    cur.close()

    return render_template('doctor_dashboard.html', blogs=blogs)

@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM blogs WHERE id = %s AND doctor_id = %s", (blog_id, session['user'][0]))
        mysql.connection.commit()
    except Exception as e:
        print(str(e))
    return redirect(url_for('doctor_dashboard'))



@app.route('/patient/blogs')
def patient_blogs():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM blogs WHERE is_draft = 0 ORDER BY category")
        blogs = cur.fetchall()

        # Categorize blogs by category
        categorized_blogs = {}
        for blog in blogs:
            category = blog[4]
            if category not in categorized_blogs:
                categorized_blogs[category] = []
            categorized_blogs[category].append(blog)

        return render_template('patient_blogs.html', categorized_blogs=categorized_blogs)

    except Exception as e:
        print(str(e))
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)