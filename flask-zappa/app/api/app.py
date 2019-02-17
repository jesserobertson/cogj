from flask import Flask, Response

app = Flask(__name__)

@app.route("/")
def hello():
    return Response("Hello, World")