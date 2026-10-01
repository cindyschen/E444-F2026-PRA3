from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)

def valid_uoft_email(form, field):
    if 'utoronto' not in field.data.lower():
        raise ValidationError('Please use your UofT email.')

class Form(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField(
        'What is your UofT Email address?',
        validators=[DataRequired(), valid_uoft_email]
    )
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        email = session.get('email')
        session['email'] = form.email.data
        session['name'] = form.name.data
        return redirect(url_for('chat'))
    return render_template('index.html',
        form = form, name = session.get('name'), email = session.get('email'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name, current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if 'name' not in session or 'email' not in session:
        flash('Please submit your name and UofT email first.')
        return redirect(url_for('index'))

    if request.method == "GET":
        return render_template("chat.html", name=session.get('name'))

    message = request.json["message"]

    if "my favourite colour is " in message.lower():
        colour = message.lower().replace("my favourite colour is ", "")
        session['colour'] = colour
        reply = "Noted!"

    elif "what is my favourite colour" in message.lower():
        colour = session.get('colour')

        if colour:
            reply = f"Your favourite colour is {colour}."
        else:
            reply = "I don't know your favourite colour."

    elif "hello" in message.lower():
        reply = "Hello!"

    else:
        reply = "I don't understand."

    return {"reply": reply}

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))