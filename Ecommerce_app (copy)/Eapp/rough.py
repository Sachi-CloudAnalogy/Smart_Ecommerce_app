from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def do():
    return render_template("show_added_item.html")

if __name__ == "__main__":
    app.run(debug=True)