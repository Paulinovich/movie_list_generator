import sqlite3
import os, sys
from stat import *
from moviepy.video.io.VideoFileClip import VideoFileClip
import math
from fuzzywuzzy import fuzz
import json
import requests

APIKey = '77e4dd567afe0378874460ed456b9aba'

def create_mdb():
    """
    (none) --> none

    Creates the movie database with all the tables from scratch.

    #TO CONSIDER: having option for user to create a new database (even when it already existed)?
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 
    conn=sqlite3.connect(db_path)
    cur=conn.cursor()
    cur.executescript("""
                        DROP TABLE IF EXISTS directed_by;
                        DROP TABLE IF EXISTS produced_in;
                        DROP TABLE IF EXISTS defined_as;
                        DROP TABLE IF EXISTS director;
                        DROP TABLE IF EXISTS country;
                        DROP TABLE IF EXISTS genre;
                        DROP TABLE IF EXISTS movie;
                        DROP TABLE IF EXISTS year;
                        CREATE TABLE year      (y_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              year INTEGER UNIQUE);
                        CREATE TABLE movie     (m_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              original_title VARCHAR(200),
                                                              title VARCHAR(200) NOT NULL,
                                                              duration INTEGER,
                                                              image_link VARCHAR(600), 
                                                              plot VARCHAR(400),
                                                              y_id);
                        CREATE TABLE genre     (g_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              name_genre VARCHAR(30) UNIQUE NOT NULL);
                        CREATE TABLE country   (c_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              abbreviation_country VARCHAR(4) UNIQUE NOT NULL);
                        CREATE TABLE director  (d_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              name_director VARCHAR(30) UNIQUE NOT NULL);
                        CREATE TABLE defined_as (m_id INTEGER, g_id INTEGER, PRIMARY KEY(m_id, g_id));
                        CREATE TABLE produced_in (m_id INTEGER, c_id INTEGER, PRIMARY KEY(m_id, c_id));
                        CREATE TABLE directed_by (m_id INTEGER, d_id INTEGER, PRIMARY KEY(m_id, d_id));
                        """)
    conn.commit()
    conn.close()


def add_movie(file, duration):
    """
    (string, int) ---> None

    Checks the correctness of the title from a movie, searches additional information 
    (original title, title, year, countries of production, directors, genres, duration, image link and plot) and stores these in the DB.

    This data is collected with an API to an online database of The Movie DB and is saved in the local movie database.
    """
    information = {"original_title" : None, "title" : None, "year" : None, "countries" : [], "directors" : [], "genres" : [], "duration": None, "image_link" : None, "plot" : None}
    match = False

    name = file[:-4]
    # replace all '_' or'-' with whitespaces
    name = name.replace('_', ' ')
    name = name.replace('-', ' ')

    parameters_search = {"api_key" : APIKey, "query" : name}
    res_search = requests.get("https://api.themoviedb.org/3/search/movie?api_key=", params=parameters_search)

    if res_search:
        res_search_json = res_search.json()
        for res in res_search_json["results"]:
            # we check with fuzzywuzzy if the matching ratio is above 90% to allow some typos but to be strict
            match_ratio = fuzz.ratio(name, res["title"])
            if match_ratio > 90:
                movie_id = res["id"]
                # get more info about movie by it's id
                res_movie = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id, APIKey))
                res_movie_json = res_movie.json()
                duration_res=  res_movie_json["runtime"]
                # we check if the length of the movie fits the length of our file but give it a bit buffer (7 Minutes?)
                if duration_res >= duration-7 and duration_res <= duration+7:
                    information["duration"] = duration_res
                    information["original_title"] = res["original_title"]
                    information["title"] = res["title"]
                    information["plot"] = res["overview"]
                    # only get year and turn string into int
                    information["year"] = int((res["release_date"])[:4])
                    for genre in res_movie_json["genres"]:
                        information["genre"].append(genre["name"])
                    for country in res_movie_json["production_countries"]:
                        information["countries"].append(country["iso_3166_1"])
                    # get url of first backdrop image and save it
                    res_img = requests.get("https://api.themoviedb.org/3/movie/{}/images?api_key={}".format(movie_id, APIKey))
                    res_img_json = res_img.json()
                    first_img = res_img_json["backdrops"][0]
                    img_path = "https://image.tmdb.org/t/p/w500" + first_img["file_path"]
                    information["image_link"] = img_path
                    # search directing crew and save them
                    res_credits = requests.get("https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(movie_id, APIKey))
                    res_credits_json = res_credits.json()
                    crew = res_credits_json["crew"]
                    for person in crew:
                        if person["job"] == "Director":
                            information["directors"].append(person["name"])
                    match = True
    save_in_db(match, information)


def save_in_db(match, info):
    """
    (boolean, dictionary) --> None

    Saves the retrieved information from The Movie DB in the local SQLite3 DB if a matching movie is found.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 
    conn=sqlite3.connect(db_path)
    cur=conn.cursor()

    # TODO: get out all repetitions in the code
    if match == True:
        cur.execute("INSERT OR IGNORE INTO year (year) VALUES({});".format(info["year"]))
        cur.execute("SELECT y_id FROM year WHERE year={};".format(info["year"]))
        y_id = cur.fetchone()[0]
        # clean the strings to work with sql
        plot_cleaned, title_cleaned, or_title_cleaned = sqlite_string([info["plot"], info["title"], info["original_title"]])
        cur.execute("INSERT OR IGNORE INTO movie (original_title, title, duration, image_link, plot, y_id) VALUES({})".format(or_title_cleaned, title_cleaned, info["duration"], info["image_link"], plot_cleaned, y_id))
        cur.execute("SELECT g_id FROM movie WHERE title={};".format(title_cleaned))
        m_id = cur.fetchone()[0]
        for genre in info["genres"]:
            cur.execute("INSERT OR IGNORE INTO genre (name_genre) VALUES({});".format(genre))
            cur.execute("SELECT g_id FROM genre WHERE name_genre={};".format(genre))
            g_id = cur.fetchone()[0]
            cur.execute("INSERT INTO defined_as VALUES({})".format(m_id, g_id))
        for country in info["countries"]:
            cur.execute("INSERT OR IGNORE INTO country (abbreviation_country) VALUES({});".format(country))
            cur.execute("SELECT g_id FROM genre WHERE name_genre={};".format(country))
            c_id = cur.fetchone()[0]
            cur.execute("INSERT INTO produced_in VALUES({})".format(m_id, c_id))
        for director in info["directors"]:
            cur.execute("INSERT OR IGNORE INTO director (name_director) VALUES({});".format(director))
            cur.execute("SELECT g_id FROM director WHERE name_director={};".format(director))
            d_id = cur.fetchone()[0]
            cur.execute("INSERT INTO directed_by VALUES({})".format(m_id, d_id))
    else: 
        print("Movie is not found.")
    conn.commit()
    conn.close()


def sqlite_string(strings):
    """
    (list) --> string

    Doubles every single-quote (') character for safe use as a string value with SQL.
    """
    for string in strings:
        try: string.replace("'", "''")
    
    return strings[0], strings[1], strings[2]


def descend_directories(top):
    """
    (string) --> None

    recursively descend the given directory tree and calling the add_movie function for each film file.
    """
    movie_extensions = (".AVI", ".avi", ".FLV", ".flv", ".WMV", ".wmv", ".MOV", ".mov", ".MP4", ".mp4")

    for item in os.listdir(top):
        # does this automatically add the \ or / to the path?
        pathname = os.path.join(top, item)
        mode = os.stat(pathname)[ST_MODE]
        # if item is directory, recurse into it
        if S_ISDIR(mode):
            descend_directories(pathname)
        # if item is a regular file: check if it is a film file
        elif S_ISREG(mode):
            if pathname.endswith(movie_extensions):
                # figure out it's length in Minutes
                ## TODO: check if ffpobe option which would be faster (https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python)
                clip = VideoFileClip(pathname)
                # clip.duration is in seconds: converting to minutes and rounding up
                duration = math.ceil((clip.duration)/60)
                add_movie(item, duration)
