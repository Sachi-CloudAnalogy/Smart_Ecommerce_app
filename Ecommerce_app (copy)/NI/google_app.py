from flask import Flask, render_template, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
import json
import requests

app = Flask(__name__)
app_conf = {"OAUTH2_CLIENT_ID": "135553744176-spo97g44ksc0d2nqp88pakpg9f1seauf.apps.googleusercontent.com",
            "OAUTH2_CLIENT_SECRET": "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",
            "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
            "FLASK_SECRET": "secret",
            "FLASK_PORT": 5000}

oauth = OAuth(app)
oauth.register("myApp",
               client_id=app_conf.get("OAUTH2_CLIENT_ID"),
               client_secret=app_conf.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=app_conf.get("OAUTH2_META_URL"),
               client_kwargs={"scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",}
                )

app.secret_key = app_conf.get("FLASK_SECRET")
@app.route("/")
def home():
    return render_template("google.html", session = session.get("user"),
                           data=json.dumps(session.get("user"), indent=4))

@app.route("/google_login")
def google_login():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("google_callback", _external=True))

@app.route("/google_callback")
def google_callback():
    token = oauth.myApp.authorize_access_token()
    person_data_url = "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"
    person_data = requests.get(person_data_url, headers={"Authorization": f"Bearer {token['access_token']}"}).json()
    token["person_data"] = person_data

    session["user"] = token       #contain id token and access token
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

# client id - 135553744176-spo97g44ksc0d2nqp88pakpg9f1seauf.apps.googleusercontent.com
# client secret - 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    







