from flask import Flask, request, render_template
from dotenv import load_dotenv
import os
from requests import post, get
import base64
import json

app = Flask(__name__)

load_dotenv()
client_id = os.getenv("Client_id")
client_secret = os.getenv("Client_secret")

if not client_id or not client_secret:
    raise ValueError("Missing CLIENT_ID or CLIENT_SECRET in .env file")
# this token only works for 10 - 30 min after being generated
def gen_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")  # use for byte code which is 8 bits
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")  # Corrected encoding

    url = "https://accounts.spotify.com/api/token"  # Fixed URL

    # for creating the dictionary because python only accesses dictionary data
    headers = {
        "Authorization": f"Basic {auth_base64}",  # Corrected authorization
        "Content-Type": "application/x-www-form-urlencoded"  # i see that thing from the spotify website
    }
    data = {"grant_type": "client_credentials"}  # instance of data
    result = post(url, headers=headers, data=data)  # all data in JSON format

    # if anything goes wrong with the server side
    if result.status_code != 200:
        print(f"Error: {result.status_code}, {result.text}")
        return None

    json_result = json.loads(result.content)
    return json_result.get("access_token")

# head authorization
def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}  # don't ask me about bearer its work on authentication server-side

# this function is used for searching a song
def search_song(song_name, token):
    # this format I saw in Spotify documentation
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    params = {
        "q": song_name,
        "type": "track",  # Fixed type
        "limit": 5  # top 5 matches
    }

    response = get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return None

    json_result = response.json()
    tracks = json_result.get("tracks", {}).get("items", [])

    if not tracks:
        return []

    results = []
    # that part for URL append status
    for track in tracks:
        results.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "preview_url": track.get("preview_url", None),
            "spotify_url": track["external_urls"]["spotify"]
        })

    return results

@app.route("/", methods=["GET", "POST"])
def index():
    songs = []
    if request.method == "POST":
        song_name = request.form.get("song_name", "").strip()
        if not song_name:
            return render_template("index.html", songs=[], error="Please enter a song name.")

        token = gen_token()
        if not token:
            return render_template("index.html",  songs=[], error="Failed to authenticate with Spotify.")

        songs = search_song(song_name, token)

    return render_template("index.html", songs=songs)

