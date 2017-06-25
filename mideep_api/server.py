import uuid
from flask import Flask, request
app = Flask(__name__)


@app.route("/hello_world")
def hello():
    user = request.args.get("user")
    return "user {} is visited, return random id: {}".format(user, uuid.uuid1())


if __name__ == "__main__":
    app.run(port=7777)
