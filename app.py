from flask import Flask, render_template, request, redirect, url_for, flash, session
import databases
from flask_wtf.csrf import CSRFProtect

app= Flask(__name__)
app.config['SECRET_KEY'] = 'DaCookbook'
database = databases.Database()
csrf = CSRFProtect(app)

@app.route('/')
def index():
    if 'user' in session:
        return render_template('user.html', user=session['user'])
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('index'))
        return render_template('login.html', err='')
    password = request.form['password']
    email = request.form['email']
    if password == '' or email == '':
        return render_template('login.html', err='Please fill in all fields')
    login = database.loginUser(email, password)
    if login:
        session['user'] = database.getUser(email)
        return redirect(url_for('index'))
    return render_template('login.html', err="Invalid email or password/Account doesn't Exist")
    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('index'))
        return render_template('register.html', err='')
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    if username == '' or password == '' or email == '':
        return render_template('register.html', err='Please fill in all fields')
    register = database.registerUser(username, email, password) 
    if register:
        session['user'] = database.getUser(email)
        return redirect('/')
    return render_template('register.html', err='Error: User Already Exist/Wrong Email Format') 
    
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)
