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

def descend_directories(top):
    """
    (string) --> None

    recursively descend the given directory tree and calling the add_movie function for each film file.
    """
    movie_extensions = (".AVI", ".avi", ".FLV", ".flv", ".WMV", ".wmv", ".MOV", ".mov", ".mkv", ".MKV", ".m4v", ".M4V", ".MP4", ".mp4")

    for item in os.listdir(top):
        # does this automatically add the \ or / to the path?
        pathname = os.path.join(top, item)
        mode = os.stat(pathname)[ST_MODE]
        # if item is directory, recurse into it
        if S_ISDIR(mode):
            descend_directories(pathname)
        # if item is a regular file: check if it is a film file
        elif S_ISREG(mode):
            if pathname.endswith(movie_extensions) and not item.startswith("._"):
                # figure out it's length in Minutes
                ## TODO: check if ffpobe option which would be faster (https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python)
                clip = VideoFileClip(pathname)
                # clip.duration is in seconds: converting to minutes and rounding up
                duration = math.ceil((clip.duration)/60)
                add_movie(item, duration)

def add_movie(file, duration):
    """
    (string, int) ---> None

    Checks the correctness of the title from a movie, searches additional information 
    (original title, title, year, countries of production, directors, genres, duration, image link and plot) and stores these in the DB.

    The file name should have one of the following structures:
            - movie title with a space, _ or - for word separation 
                e.g. ''Seven Samurai', 'Seven_Samurai'
            - a movie title following the criteria of the structure above followed by the year and quality (or other information) separated by a space.
                e.g. 'Rashomon 1959 1080p', 'Seven Samurai 1954 1080p'

    This data is collected with an API to an online database of The Movie DB and is saved in the local movie database.
    """
    name = file[:-4]
    # replace all '_' or'-' with whitespaces
    name = name.replace('_', ' ')
    name = name.replace('-', ' ')

    # if file name has following structure: 'title year quality' e.g. 'Rashomon 1959 1080p'
    # slice untill second empty space character from the right.
    name_dennis_syntax = name[:(name.rfind(' ', 0, (name.rfind(' '))))]

    parameters_search1 = {"api_key" : APIKey, "query" : name}
    parameters_search2 = {"api_key" : APIKey, "query" : name_dennis_syntax}
    # try first with the filename structure with more information
    res_search = requests.get("https://api.themoviedb.org/3/search/movie", params=parameters_search2)

    if res_search:
        res_search_json = res_search.json()
        # results for res not for res_search_json
        if res_search_json["total_results"] != 0:
            API_movie(res_search_json, name_dennis_syntax, duration)
        else:       
            # search with other file name structure (only movie title)
            res_search = requests.get("https://api.themoviedb.org/3/search/movie", params=parameters_search1)
            res_search_json = res_search.json()
            if res_search_json["total_results"] != 0:
                API_movie(res_search_json, name, duration)
            else: 
                print("movie not found")
    else:   
        print("no API connection")
                
def API_movie(results_json, name, duration):
    """
    (json, string, int) --> None

    Reads information from the API-results and stores it in the data base with function save_in_db().
    """
    information = {"countries" : [], "directors" : [], "genres" : []}

    for res in results_json["results"]:
        print(name)
        # we check with fuzzywuzzy if the matching ratio is above 90% to allow some typos but to be strict
        match_ratio = fuzz.ratio(name, res["title"])
        print(match_ratio)
        if match_ratio > 90:
            movie_id = res["id"]
            # get more info about movie by it's id
            res_movie = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id, APIKey))
            res_movie_json = res_movie.json()
            duration_res=  res_movie_json["runtime"]
            # we check if the length of the movie fits the length of our file but give it a bit buffer (7 Minutes?)
            if duration_res ==None or (duration_res >= duration-10 and duration_res <= duration+10):
                information["duration"] = duration_res
                information["original_title"] = res["original_title"]
                information["title"] = res["title"]
                information["plot"] = res["overview"]
                # only get year and turn string into int
                if res["release_date"] != None:
                    information["year"] = int((res["release_date"])[:4])
                for genre in res_movie_json["genres"]:
                    information["genres"].append(genre["name"])
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
                save_in_db(information)
                return
            else:
                print("duration doesn't match")
        else: 
            print("title doesn't match")


def save_in_db(info):
    """
    (dictionary) --> None

    Saves the retrieved information (stored in a dictionary)from The Movie DB in the local SQLite3 DB.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 
    conn=sqlite3.connect(db_path)
    cur=conn.cursor()

    # TODO: get out all repetitions in the code
    cur.execute("INSERT OR IGNORE INTO year (year) VALUES(?)",(info["year"], ))
    cur.execute("SELECT y_id FROM year WHERE year=?",(info["year"], ))
    y_id = cur.fetchone()[0]
    # clean the strings to work with sql
    plot_cleaned, title_cleaned, or_title_cleaned = sqlite_string([info["plot"], info["title"], info["original_title"]])
    cur.execute("INSERT OR IGNORE INTO movie (original_title, title, duration, image_link, plot, y_id) VALUES(?, ?, ?, ?, ?, ?)",(or_title_cleaned, title_cleaned, info["duration"], info["image_link"], plot_cleaned, y_id))
    cur.execute("SELECT m_id FROM movie WHERE title=?",(title_cleaned, ))
    m_id = cur.fetchone()[0]
    for genre in info["genres"]:
        cur.execute("INSERT OR IGNORE INTO genre (name_genre) VALUES(?)",(genre, ))
        cur.execute("SELECT g_id FROM genre WHERE name_genre=?",(genre, ))
        g_id = cur.fetchone()[0]
        cur.execute("INSERT INTO defined_as VALUES(?, ?)",(m_id, g_id))
    for country in info["countries"]:
        cur.execute("INSERT OR IGNORE INTO country (abbreviation_country) VALUES(?)",(country, ))
        cur.execute("SELECT c_id FROM country WHERE abbreviation_country=?",(country, ))
        c_id = cur.fetchone()[0]
        cur.execute("INSERT INTO produced_in VALUES(?, ?)",(m_id, c_id))
    for director in info["directors"]:
        cur.execute("INSERT OR IGNORE INTO director (name_director) VALUES(?)",(director, ))
        cur.execute("SELECT d_id FROM director WHERE name_director=?",(director, ))
        d_id = cur.fetchone()[0]
        cur.execute("INSERT INTO directed_by VALUES(?, ?)",(m_id, d_id))
    conn.commit()
    conn.close()


def sqlite_string(strings):
    """
    (list) --> string

    Doubles every single-quote (') character for safe use as a string value with SQL.
    """
    for string in strings:
        string.replace("'", "''")
    return strings[0], strings[1], strings[2]