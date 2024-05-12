from flask import Flask
import pymssql
app = Flask(__name__)
app.config['SECRET_KEY'] = '65d7a2d001a0ac6fd0f40f7d'


def connection():
    conn = pymssql.connect("localhost:1433", "sa", "Strong.Pwd-123", "market")
    return conn


from market import routes
