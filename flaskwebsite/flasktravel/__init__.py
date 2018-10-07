from flask import Flask
app = Flask(__name__, static_url_path='/static')
from flasktravel import views

