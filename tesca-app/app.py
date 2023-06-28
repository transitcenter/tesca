import time
import os
from flask import Flask, render_template

from forms import ConfigForm

app = Flask(__name__)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route("/", methods=["GET", "POST"])
def home():
    form = ConfigForm()
    if form.validate_on_submit():
        return "Success"
    return render_template("start.jinja2", form=form, template="form-template")


@app.route("/time")
def get_current_time():
    return {"time": time.time()}
