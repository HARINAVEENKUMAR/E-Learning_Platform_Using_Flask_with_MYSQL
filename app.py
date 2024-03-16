from contextlib import closing
import MySQLdb, os
from functools import wraps
from flask import Flask, g
from flask import Flask, render_template, request, redirect, session
from routes import *


app = Flask(__name__)

# Configure MySQL connection parameters
app.config['MYSQL_HOST'] = '127.0.0.1'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'        # Replace with your MySQL username
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MYSQL_PASSWORD'] = ''        # Replace with your MySQL password
app.config['MYSQL_DB'] = 'elearn'        # Replace with your MySQL database name

# Define database connection functions
def get_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def execute_query(query, values=None, fetchall=True):
    with closing(get_db().cursor()) as cursor:
        cursor.execute(query, values)
        if fetchall:
            results = cursor.fetchall()
        else:
            results = cursor.fetchone()
    return results

def get_user_id_from_session_or_request():
    # Get user_id from the session if it exists
    user_id_frs = session.get('user_id')

    if user_id_frs is None : 
    # If user_id is not available, redirect the user to the login page
        return redirect('/login')
    else:
        return user_id_frs

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')  # Redirect to the login route
        return func(*args, **kwargs)
    return decorated_function

def get_a_user_id_from_session_or_request():
    # Get user_id from the session if it exists
    auser_id_frs = session.get('auser_id')

    if auser_id_frs is None : 
    # If user_id is not available, redirect the user to the login page
        return redirect('/alogin')
    else:
        return auser_id_frs

def alogin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'auser_id' not in session:
            return redirect('/alogin')  # Redirect to the login route
        return func(*args, **kwargs)
    return decorated_function

def get_i_user_id_from_session_or_request():
    # Get user_id from the session if it exists
    iuser_id_frs = session.get('iuser_id')

    if iuser_id_frs is None : 
    # If user_id is not available, redirect the user to the login page
        return redirect('/ilogin')
    else:
        return iuser_id_frs

def ilogin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'iuser_id' not in session:
            return redirect('/ilogin')  # Redirect to the login route
        return func(*args, **kwargs)
    return decorated_function

def get_course_details(course_id):
    # Query course details from the database based on course_id
    query_course_details = """
        SELECT course_name, username, lesson_name
        FROM courses
        JOIN instructors ON courses.instructor_id = instructors.instructor_id
        JOIN lessons ON courses.course_id = lessons.course_id
        WHERE courses.course_id = %s
    """
    course_details = execute_query(query_course_details, (course_id,))
    
    # Group lessons by course
    lessons = []
    for row in course_details:
        
        lessons.append({'name': row[2]})
    
    # Extract course name and instructor from the first row
    course_name = course_details[0][0]
    instructor = course_details[0][1]
    
    # Return course details as a dictionary
    return {'course_id': course_id, 'course_name': course_name, 'instructor': instructor, 'lessons': lessons}



# Homepage Routes
@app.route('/')
def index():
    # Render your homepage template
    return render_template('index.html')

# Authentication Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email is already registered
        query_check_email = "SELECT * FROM users WHERE email = %s"
        existing_user = execute_query(query_check_email, (email,), fetchall=False)
        
        if existing_user:
            return render_template('signup.html', error="Email already exists that you tried to register. Please choose another one.")
        
        # Insert the new user into the database
        query_insert_user = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        try:
            # Execute the INSERT query
            execute_query(query_insert_user, (username, email, password), fetchall=False)
            
            # Commit the transaction
            get_db().commit()
            
            return redirect('/login')  # Redirect to the login page after successful registration
        except Exception as e:
            return "Error: {}".format(e)  # Handle any database errors
    else:
        # Render the signup page template
        return render_template('signup.html')



@app.route('/ilogin', methods=['GET', 'POST'])
def ilogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query to check if the user exists with the given email and password
        query = "SELECT * FROM instructors WHERE email = %s AND password = %s"
        
        try:
            # Execute the query
            user = execute_query(query, (email, password), fetchall=False)
            
            if user:
                # Store user_id in session for further use
                session['iuser_id'] = user[0]
                # Redirect to the dashboard or home page upon successful login
                return redirect('/instructor')
            else:
                # Redirect back to login page with an error message
                return render_template('instructor_login.html', error="Invalid email or password.")
        except Exception as e:
            # Handle any errors
            return "Error: {}".format(e)
    else:
        # Render your login page template
        return render_template('instructor_login.html')


@app.route('/alogin', methods=['GET', 'POST'])
def alogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query to check if the user exists with the given email and password
        query = "SELECT * FROM admins WHERE email = %s AND password = %s"
        
        try:
            # Execute the query
            user = execute_query(query, (email, password), fetchall=False)
            
            if user:
                # Store user_id in session for further use
                session['auser_id'] = user[0]
                # Redirect to the dashboard or home page upon successful login
                return redirect('/admin')
            else:
                # Redirect back to login page with an error message
                return render_template('admin_login.html', error="Invalid email or password.")
        except Exception as e:
            # Handle any errors
            return "Error: {}".format(e)
    else:
        # Render your login page template
        return render_template('admin_login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query to check if the user exists with the given email and password
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        
        try:
            # Execute the query
            user = execute_query(query, (email, password), fetchall=False)
            
            if user:
                # Store user_id in session for further use
                session['user_id'] = user[0]
                # Redirect to the dashboard or home page upon successful login
                return redirect('/')
            else:
                # Redirect back to login page with an error message
                return render_template('login.html', error="Invalid email or password.")
        except Exception as e:
            # Handle any errors
            return "Error: {}".format(e)
    else:
        # Render your login page template
        return render_template('login.html')


from flask import session, redirect, url_for

@app.route('/logout')
def logout():
    # Clear session variables related to user
    session['user_id'] = None
    session['auser_id'] = None
    session['iuser_id'] = None

    
    return render_template('logout.html')


# User Profile Routes]
@app.route('/profile')
@login_required
def profile():
    # Get user_id from session (assuming it's stored after login)
    user_id = session.get('user_id')
    print(user_id)
    if user_id:
        # Query user details from the database based on user_id
        query_user_details = "SELECT * FROM users WHERE user_id = %s"
        user_details = execute_query(query_user_details, (user_id,), fetchall=False)
        

        # Query enrolled courses for the user
        query_enrolled_courses = """
            SELECT courses.course_id, courses.course_name
            FROM enrollments
            JOIN courses ON enrollments.course_id = courses.course_id
            WHERE enrollments.user_id = %s
        """

        enrolled_courses = execute_query(query_enrolled_courses, (user_id,))

        
        
        return render_template('profile.html', user=user_details, enrolled_courses=enrolled_courses)
    


    else:
        # If user_id is not found in session, redirect to login page
        return redirect('/login')  # Assuming you have a /login route for login functionality

# Course Routes
@app.route('/courses')
def courses():
    # Query all courses and their categories from the database
    query_courses = """
        SELECT courses.course_id, courses.course_name, courses.description, categories.category_name
        FROM courses
        JOIN coursecategories ON coursecategories.course_id = courses.course_id
        JOIN categories ON coursecategories.category_id = categories.category_id

    """
    all_courses = execute_query(query_courses)
    
    # Render courses page template and pass the course data to the template
    return render_template('courses.html', courses=all_courses)

@app.route('/courses/<int:course_id>')
def course_details(course_id):
    # Fetch course details from the database based on course_id
    course_details = get_course_details(course_id)
    
    # Render course details page template and pass the course details to the template
    

    return render_template('course_details.html', course_details=course_details)

@app.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    # Calling the function to get user_id from session or request
    user_id = get_user_id_from_session_or_request()
    
    # Insert enrollment details into the database
    query_insert_enrollment = "INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)"
    try:
        execute_query(query_insert_enrollment, (user_id, course_id), fetchall=False)
        # Commit the transaction
        get_db().commit()
        # Redirect to a success page or course details page after successful enrollment
        return redirect(f'/courses/{course_id}')
    except Exception as e:
        # Handle any errors
        return f"Error enrolling in course: {e}"

# Lesson Routes
@app.route('/courses/<int:course_id>/lessons')
def lessons(course_id):
    try:
        # Fetch lessons for the specified course ID from the database
        lessons_query = "SELECT lesson_id, lesson_name FROM lessons WHERE course_id = %s"
        lessons_result = execute_query(lessons_query, (course_id,), fetchall=True)

        # Pass the list of lessons to the lessons.html template
        print(lessons_result)
        return render_template('lessons.html', course_id=course_id, lessons=lessons_result)
    except Exception as e:
        # Handle any errors
        return render_template('error.html', message=f"Error fetching lessons: {e}")


@app.route('/courses/<int:course_id>/lessons/<int:lesson_id>')
@login_required
def lesson_details(course_id, lesson_id):

    # Get user_id from session
    user_id = session['user_id']

    # Check if the user is enrolled in the course
    query_check_enrollment = "SELECT * FROM enrollments WHERE user_id = %s AND course_id = %s"
    enrollment = execute_query(query_check_enrollment, (user_id, course_id), fetchall=True)

    if not enrollment:
        # If the user is not enrolled in the course, redirect to a page indicating access denied
        return render_template('access_denied.html')

    # Fetch lesson details from the database
    query_fetch_lesson = "SELECT * FROM lessons WHERE lesson_id = %s"
    lesson = execute_query(query_fetch_lesson, (lesson_id,), fetchall=False)

    if not lesson:
        # If the lesson does not exist, return an error page
        return render_template('error.html', message='Lesson not found')

    # Render lesson details page template for a specific lesson within a course

    print(lesson)
    return render_template('lesson_details.html', course_id=course_id, lesson=lesson)


# Admin Routes
@app.route('/admin')
@alogin_required
def admin_dashboard():
    # Fetch users and instructors from the database
    users = execute_query("SELECT * FROM users")
    instructors = execute_query("SELECT * FROM instructors")
    return render_template('admin_dashboard.html', users=users, instructors=instructors)

@app.route('/admin/add_user', methods=['POST'])
@alogin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Insert the new user into the database
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        execute_query(query, (username, email, password))
        
        # Commit the transaction
        get_db().commit()
        return redirect('/admin')

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@alogin_required
def delete_user(user_id):
    # Delete the user from the database
    query = "DELETE FROM users WHERE user_id = %s"
    execute_query(query, (user_id,))
    # Commit the transaction
    get_db().commit()
    return redirect('/admin')
    
@app.route('/admin/modify_user/<int:user_id>', methods=['GET'])    
@alogin_required
def modify_user_page(user_id):
    # Fetch the instructor details from the database based on the instructor_id
    user = execute_query("SELECT * FROM users WHERE user_id = %s", (user_id,), fetchall=False)
    return render_template('modify_user.html', instructor_or_user=user, instructor_or_user_id=user_id)


@app.route('/admin/modify_user/<int:user_id>', methods=['POST'])
@alogin_required
def modify_user(user_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print("\n" + username + "\n" + email + "\n" + password)
        
        # Update the user in the database
        query = "UPDATE users SET username = %s, email = %s, password = %s WHERE user_id = %s"
        try:
            execute_query(query, (username, email, password, user_id))
            get_db().commit()
            return redirect('/admin')
        except Exception as e:
            print("Error updating user:", e)
            # Handle the error, perhaps by displaying an error message to the user
            return "Error updating user: " + str(e)


@app.route('/admin/add_instructor', methods=['POST'])
@alogin_required
def add_instructor():
    if request.method == 'POST':
        instructor_name = request.form['instructor_name']
        email = request.form['email']
        password = request.form['email']
        # Insert the new instructor into the database
        query = "INSERT INTO instructors (username, email, password) VALUES (%s, %s, %s)"
        execute_query(query, (instructor_name, email, password))
        # Commit the transaction
        get_db().commit()
        return redirect('/admin')
        

@app.route('/admin/delete_instructor/<int:instructor_id>', methods=['POST'])
@alogin_required
def delete_instructor(instructor_id):
    # Delete the instructor from the database
    query = "DELETE FROM instructors WHERE instructor_id = %s"
    execute_query(query, (instructor_id,))
    # Commit the transaction
    get_db().commit()
    return redirect('/admin')

@app.route('/admin/modify_instructor/<int:instructor_id>', methods=['GET'])
@alogin_required
def modify_instructor_page(instructor_id):
    # Fetch the instructor details from the database based on the instructor_id
    instructor = execute_query("SELECT * FROM instructors WHERE instructor_id = %s", (instructor_id,), fetchall=False)
    return render_template('modify_instructor.html', instructor_or_user=instructor, instructor_or_user_id=instructor_id)

@app.route('/admin/modify_instructor/<int:instructor_id>', methods=['POST'])
@alogin_required
def modify_instructor(instructor_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print("\n"+ username +"\n"+ email +"\n"+ password)
        # Update the instructor in the database
        query = "UPDATE instructors SET username = %s, email = %s, password = %s WHERE instructor_id = %s"
        execute_query(query, (username, email, password, instructor_id))
        get_db().commit()
        return redirect('/admin')









@app.route('/instructor')
@ilogin_required
def instructor_dashboard():
    # Fetch users and instructors from the database
    courses = execute_query("SELECT * FROM courses")
    return render_template('instructor_dashboard.html', courses=courses)

@app.route('/instructor/add_course', methods=['POST'])
@ilogin_required
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        description = request.form['description']
        instructor_id = request.form['instructor_id']
        
        # Insert the new course into the database
        query = "INSERT INTO courses (course_name, description, instructor_id) VALUES (%s, %s, %s)"
        execute_query(query, (course_name, description, instructor_id))
        
        # Commit the transaction
        get_db().commit()
        return redirect('/instructor')


@app.route('/instructor/add_lesson/<int:course_id>', methods=['POST'])
@ilogin_required
def add_lesson(course_id):
    if request.method == 'POST':

        lesson_name = request.form['lesson_name']
        content = request.form['content']
        youtube_url = request.form['youtube_url']
        
        # Insert the new course into the database
        query = "INSERT INTO lessons (course_id,lesson_name, content, youtube_url) VALUES (%s, %s, %s, %s)"
        execute_query(query, (course_id, lesson_name, content, youtube_url))
        
        # Commit the transaction
        get_db().commit()
        return redirect('/instructor/modify_course/'+str(course_id))

@app.route('/instructor/delete_course/<int:course_id>', methods=['POST'])
@ilogin_required
def delete_course(course_id):
    # Delete the course from the database
    query = "DELETE FROM courses WHERE course_id = %s"
    execute_query(query, (course_id,))
    # Commit the transaction
    get_db().commit()
    return redirect('/instructor')

@app.route('/instructor/delete_lesson/<int:course_id>/<int:lesson_id>', methods=['POST'])
@ilogin_required
def delete_lesson(course_id,lesson_id):
    # Delete the course from the database
    query = "DELETE FROM lessons WHERE lesson_id = %s"
    execute_query(query, (lesson_id,))
    # Commit the transaction
    get_db().commit()
    return redirect('/instructor/modify_course/'+str(course_id))
    
@app.route('/instructor/modify_course/<int:course_id>', methods=['GET', 'POST'])
@ilogin_required    
def modify_course_page(course_id):
    # Fetch the course details from the database based on the course_id
    course = execute_query("SELECT * FROM courses WHERE course_id = %s", (course_id,), fetchall=False)
    lessons = execute_query("SELECT * FROM lessons WHERE course_id = %s", (course_id,), fetchall=True)
    return render_template('modify_course.html', course=course,lessons=lessons, course_id=course_id)

@app.route('/instructor/modify_lesson/<int:lesson_id>', methods=['GET'])
@ilogin_required    
def modify_lesson_page(lesson_id):
    # Fetch the instructor details from the database based on the instructor_id
    lesson = execute_query("SELECT * FROM lessons WHERE lesson_id = %s", (lesson_id,), fetchall=False)
    return render_template('modify_lesson.html', lesson=lesson, lesson_id=lesson_id)

@app.route('/instructor/modify_lesson/<int:course_id>/<int:lesson_id>', methods=['POST']) 
@ilogin_required
def modify_lesson(course_id,lesson_id):
    if request.method == 'POST':
        lesson_name = request.form['lesson_name']
        youtube_url = request.form['youtube_url']
        content = request.form['content']
        print("\n"+ str(course_id) +"\n"+ lesson_name +"\n"+ content +"\n"+ youtube_url)
        # Update the instructor in the database
        query = "UPDATE `lessons` SET `course_id` = %s, `lesson_name` = %s, `content` = %s, `youtube_url` = %s WHERE `lessons`.`lesson_id` = %s"      
        execute_query(query, (course_id, lesson_name, content, youtube_url, lesson_id))

        get_db().commit()

        return redirect('/instructor/modify_course/' + str(course_id))

@app.route('/instructor/modify_course/<int:course_id>', methods=['POST'])
@ilogin_required
def modify_course(course_id):
    if request.method == 'POST':
        course_name = request.form['course_name']
        description = request.form['description']
        instructor_id = request.form['instructor_id']
        
        # Update the course in the database
        query = "UPDATE courses SET course_name = %s, description = %s, instructor_id = %s WHERE course_id = %s"
        try:
            execute_query(query, (course_name, description, instructor_id, course_id))
            get_db().commit()
            return redirect('/instructor')
        except Exception as e:
            print("Error updating course:", e)
            # Handle the error, perhaps by displaying an error message to the user
            return "Error updating course: " + str(e)


if __name__ == '__main__':
    app.run(debug=True)
