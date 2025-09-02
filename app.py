from flask import Flask, redirect, session, url_for, render_template, request
from spotify_auth import create_spotify_oauth, get_spotify_client
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        return render_template("error.html", error="Token inválido.")

    session["token_info"] = token_info
    return redirect(url_for('dashboard'))



@app.route('/dashboard')
def dashboard():
    try:
        token_info = session.get("token_info", None)
        if not token_info:
            return redirect(url_for("login"))

        sp = get_spotify_client(token_info)
        user = sp.current_user()
        user_name = user["display_name"]

        tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')

        return render_template("dashboard.html", user=user_name, tracks=tracks)

    except Exception as e:
        return f"Erro no dashboard: {(e)}", 500
