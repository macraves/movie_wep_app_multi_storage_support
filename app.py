"""Backend for the web app."""
import flask

app = flask.Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Hello, world!"


if __name__ == "__main__":
    app.run(debug=True)
