from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
import databases
import json
from authlib.integrations.flask_client import OAuth
import config
from loginpass import create_flask_blueprint, Google
from flask_wtf.csrf import CSRFProtect
import uuid
from datetime import datetime

creds = json.load(open('config.json'))
app= Flask(__name__)
app.config.from_pyfile('config.py')
csrf = CSRFProtect(app)

oauth = OAuth(app)
database = databases.Database()
backends = [Google]

@app.route('/')
def home():
    if 'user' in session:
        return render_template('user.html', user=session['user'])
    return render_template('index.html')

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('home'))

@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == "GET":
        return render_template("new.html")
    ingredients = []
    steps = []
    recipe = request.form.to_dict()
    for i in recipe:
        if 'ingredients' in i and 'Amt' not in i and 'Scale' not in i:
            num = i.split("#")[1]
            ing = {
                "name": recipe[i],
                "amount": recipe["ingredientsAmt#" + num],
                "scale": recipe["ingredientsScale#" + num]
            }
            ingredients.append(ing)
        elif "step" in i:
            steps.append(recipe[i])
    recipe = {
        "_id": str(uuid.uuid4()),
        "title": recipe['title'],
        "description": recipe['description'],
        "ingredients": ingredients,
        "steps": steps,
        "type": recipe['type'],
        "tags": recipe['tags'].split(" "),
        "by": session['user']['_id'],
        "likes": [],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    database.addRecipe(recipe)
    return redirect(url_for('home'))

@app.route("/recipe/<id>")
def recipe(id):
    recipe = database.getRecipe(id)
    return render_template("recipe.html", recipe=recipe)         

def handle_authorize(remote, token, user_info):
    if not database.userExists(user_info['email']):
        database.addUser(user_info['email'])
    session['user'] = database.getUserWithMail(user_info['email'])
    return redirect(url_for('home'))

bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
