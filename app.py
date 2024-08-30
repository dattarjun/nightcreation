from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import yaml

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load MySQL configurations
db_config = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db_config['mysql_host']
app.config['MYSQL_USER'] = db_config['mysql_user']
app.config['MYSQL_PASSWORD'] = db_config['mysql_password']
app.config['MYSQL_DB'] = db_config['mysql_db']

mysql = MySQL(app)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Sign Up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)", (username, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return 'Passwords do not match'
    
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE email = %s", [email])
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            session['user_id'] = user[0]  # Store user_id in session
            return redirect(url_for('profile'))
        else:
            return 'Invalid login credentials'
    return render_template('login.html')

# Profile Route
@app.route('/profile')
def profile():
    if 'user_id' in session:
        username = session['username']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM itineraries WHERE user_id = %s", [session['user_id']])
        itineraries = cursor.fetchall()
        cursor.close()
        
        return render_template('profile.html', username=username, itineraries=itineraries)
    return redirect(url_for('login'))

# Add Trip Route
@app.route('/addtrip', methods=['GET', 'POST'])
def addtrip():
    if 'user_id' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            user_id = session['user_id']
            
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO itineraries(user_id, title, description, start_date, end_date) VALUES(%s, %s, %s, %s, %s)", (user_id, title, description, start_date, end_date))
            mysql.connection.commit()
            cursor.close()
            
            return redirect(url_for('profile'))
        return render_template('addtrip.html')
    return redirect(url_for('login'))

# Blog Route
@app.route('/blog')
def blog():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT posts.id, posts.title, posts.content, users.username, posts.created_at FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.created_at DESC")
    posts = cursor.fetchall()
    cursor.close()
    return render_template('blog.html', posts=posts)

# Create Post Route
@app.route('/createpost', methods=['GET', 'POST'])
def createpost():
    if 'user_id' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            user_id = session['user_id']
            
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO posts(user_id, title, content) VALUES(%s, %s, %s)", (user_id, title, content))
            mysql.connection.commit()
            cursor.close()
            
            return redirect(url_for('blog'))
        return render_template('createpost.html')
    return redirect(url_for('login'))

@app.route('/post_details>', methods=['GET'])
def post_detail(post_id):
    post = post.query.get_or_404(post_id)
    comments = comments.query.filter_by(post_id=post_id).all()
    return render_template('post_details.html', post=post, comments=comments)


# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)  # Also clear user_id from session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
