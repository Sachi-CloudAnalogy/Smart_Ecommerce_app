from flask import Flask, render_template, redirect, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = "secret"
app.config['SERVER_NAME'] = 'localhost:5000'
oauth = OAuth(app)

@app.route('/')
def home():
    return render_template('google.html')

@app.route('/facebook_login')
def facebook_login():
   
    FACEBOOK_CLIENT_ID = "420884517256810"      
    FACEBOOK_CLIENT_SECRET ="bb9c73950491e8421739789ecf95a7bc"     
    oauth.register(
        name='facebook',
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://www.facebook.com/dialog/oauth',
        authorize_params=None,
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    print("Facebook User ", profile)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)


#"594263754976083" 
#"021b367ffb4c207f90b9c9addf8db09b"     