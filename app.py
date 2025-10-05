from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def welcome():
    return render_template("welcome.html")

if __name__ == "__main__":
    # debug=True so you see live reloads while we build
    app.run(debug=True)
