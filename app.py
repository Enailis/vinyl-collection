### TODO
# make it pretty

from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

DISCOGS_API_URL = "https://api.discogs.com/"
DISCOGS_API_KEY = os.getenv("DISCOGS_API_KEY")


def create_json_files():
    files_to_create = ["./data/main_collection.json"]
    for file_path in files_to_create:
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump([], file)
            print(f"File {file_path} created.")
        else:
            print(f"File {file_path} already exists.")


# Load JSON files
def load_json(filename):
    with open(filename, "r+") as file:
        return json.load(file)


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# Fetch album info from Discogs API
def get_album_data_by_upc(upc):
    url = f"{DISCOGS_API_URL}database/search?barcode={upc}&token={DISCOGS_API_KEY}"
    response = requests.get(url)
    return response.json()


def get_album_tracklist_by_id(id):
    url = f"{DISCOGS_API_URL}releases/{id}"
    response = requests.get(url)
    tracklist = []
    for track in response.json()["tracklist"]:
        tracklist.append(track["title"])
    return tracklist


def get_album_data_by_name_artist(album_name, artist_name):
    url = f"{DISCOGS_API_URL}database/search?q={album_name}&artist={artist_name}&token={DISCOGS_API_KEY}"
    response = requests.get(url)
    return response.json()


def check_already_exists(filename, upc):
    with open(filename, "r") as f:
        albums = json.load(f)
        for album in albums:
            if album["upc"] == upc:
                return True


# Main page route
@app.route("/")
def index():
    albums = load_json("data/main_collection.json")
    albums.sort(key=lambda x: (x["artist"].lower(), x["release_date"]))
    return render_template("index.html", albums=albums)


# Add album to collection using UPC
@app.route("/add_album", methods=["POST"])
def add_album():
    upc = request.form["upc"]
    album_data = get_album_data_by_upc(upc)
    if check_already_exists("./data/main_collection.json", upc):
        return (
            jsonify({"status": "error", "message": "Album already in collection"}),
            400,
        )
    # get id, cover, album name, artist name, release date and UPC
    album = {
        "id": album_data["results"][0]["id"],
        "cover": album_data["results"][0]["cover_image"],
        "name": album_data["results"][0]["title"].split(" - ")[1],
        "artist": album_data["results"][0]["title"].split(" - ")[0],
        "release_date": album_data["results"][0]["year"],
        "upc": upc,
    }
    # get tracklist using the id
    tracklist = get_album_tracklist_by_id(album["id"])
    album["tracklist"] = tracklist
    albums = load_json("data/main_collection.json")
    albums.append(album)
    save_json("data/main_collection.json", albums)
    return jsonify({"status": "success"})


# Sort albums by criteria
@app.route("/sort_albums", methods=["GET"])
def sort_albums():
    sort_by = request.args.get("sort_by")
    albums = load_json("data/main_collection.json")

    if sort_by == "release_date_asc":
        albums.sort(key=lambda x: x["release_date"])
    elif sort_by == "release_date_desc":
        albums.sort(key=lambda x: x["release_date"], reverse=True)
    elif sort_by == "artist_asc":
        albums.sort(key=lambda x: x["artist"].lower())
    elif sort_by == "album_name_asc":
        albums.sort(key=lambda x: x["name"].lower())
    elif sort_by == "artist_release_date":
        albums.sort(key=lambda x: (x["artist"].lower(), x["release_date"]))

    return jsonify(albums)


@app.route("/delete_album", methods=["POST"])
def delete_album():
    album_id = request.form.get("album_id")
    if not album_id:
        return jsonify({"status": "error", "message": "Album ID is required"}), 400

    album_id = int(album_id)

    # Delete from the main collection
    with open("./data/main_collection.json", "r") as f:
        albums = json.load(f)

    # Find and remove the album by ID
    for album in albums:
        if album['id'] == album_id:
            albums.pop(albums.index(album))
            with open("./data/main_collection.json", "w") as f:
                json.dump(albums, f)
            return jsonify({"status": "success", "message": "Album deleted"})

    return jsonify({"status": "error", "message": "Album not found"}), 404


if __name__ == "__main__":
    create_json_files()
    app.run(debug=True)
