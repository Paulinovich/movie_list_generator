import sqlite3
#import panda as pd
import os, sys
from stat import *



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
    # TODO: add in table for plot
    cur.executescript("""
                        CREATE TABLE IF NOT EXISTS year      (y_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              year INTEGER UNIQUE);
                        CREATE TABLE IF NOT EXISTS movie     (m_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              file_name TEXT UNIQUE NOT NULL,
                                                              title VARCHAR(200) NOT NULL,
                                                              length INTEGER,
                                                              info VARCHAR(400),
                                                              y_id);
                        CREATE TABLE IF NOT EXISTS genre     (g_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              name_genre VARCHAR(30) UNIQUE NOT NULL);
                        CREATE TABLE IF NOT EXISTS country   (c_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              name_country VARCHAR(56) UNIQUE NOT NULL);
                        CREATE TABLE IF NOT EXISTS director  (d_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                                              name_director VARCHAR(30) UNIQUE NOT NULL);
                        CREATE TABLE IF NOT EXISTS defined_as (m_id INTEGER, g_id INTEGER, PRIMARY KEY(m_id, g_id));
                        CREATE TABLE IF NOT EXISTS produced_in (m_id INTEGER, c_id INTEGER, PRIMARY KEY(m_id, c_id));
                        CREATE TABLE IF NOT EXISTS directed_by (m_id INTEGER, d_id INTEGER, PRIMARY KEY(m_id, d_id));
                        """)
    conn.commit()
    conn.close()


def fill_examles_mdb():
    """
    (none --> none)

    Fills the database with some examples to test its attributes and some functions.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 

    conn=sqlite3.connect(db_path)
    cur=conn.cursor()

    cur.executescript("""
                      INSERT INTO year (year) VALUES(2014);
                      INSERT INTO year (year) VALUES(2017);
                      INSERT INTO year (year) VALUES(2015);
                      INSERT INTO movie (file_name, title, length, info, y_id) VALUES('la_grande_bellezza', 'La Grande Bellezza',  141,
                                                                                      'Jep Gambardella has seduced his way through the lavish nightlife of Rome for decades, but after his 65th birthday and a shock from the past, Jep looks past the nightclubs and parties to find a timeless landscape of absurd, exquisite beauty.',
                                                                                      1);
                      INSERT INTO movie (file_name, title, length, info, y_id) VALUES('thesquarefull', 'The Square', 151,
                                                                                      'A prestigious Stockholm museum''s chief art curator finds himself in times of both professional and personal crisis as he attempts to set up a controversial new exhibit.',
                                                                                      2);
                      INSERT INTO movie (file_name, title, length, info, y_id) VALUES('leviathan', 'leviafan', 140,
                                                                                      'In a Russian coastal town, Kolya is forced to fight the corrupt mayor when he is told that his house will be demolished. He recruits a lawyer friend to help, but the man''s arrival brings further misfortune for Kolya and his family.',
                                                                                      3);
                      INSERT INTO genre (name_genre) VALUES('drama');
                      INSERT INTO genre (name_genre) VALUES('comedy');
                      INSERT INTO genre (name_genre) VALUES('crime');
                      INSERT INTO country (name_country) VALUES('Italy');
                      INSERT INTO country (name_country) VALUES('Sweden');
                      INSERT INTO country (name_country) VALUES('Germany');
                      INSERT INTO country (name_country) VALUES('Denmark');
                      INSERT INTO country (name_country) VALUES('Russia');
                      INSERT INTO director (name_director) VALUES('Paolo Sorrentino');
                      INSERT INTO director (name_director) VALUES('Ruben Östlund');
                      INSERT INTO director (name_director) VALUES('Andrey Zvyagintsev');
                      INSERT INTO defined_as (m_id, g_id) VALUES(1,1);
                      INSERT INTO defined_as (m_id, g_id) VALUES(2,1);
                      INSERT INTO defined_as (m_id, g_id) VALUES(2,2);
                      INSERT INTO defined_as (m_id, g_id) VALUES(3,1);
                      INSERT INTO defined_as (m_id, g_id) VALUES(3,3);
                      INSERT INTO produced_in (m_id, c_id) VALUES(1,1);
                      INSERT INTO produced_in (m_id, c_id) VALUES(2,2);
                      INSERT INTO produced_in (m_id, c_id) VALUES(2,3);
                      INSERT INTO produced_in (m_id, c_id) VALUES(2,4);
                      INSERT INTO produced_in (m_id, c_id) VALUES(3,5);
                      INSERT INTO directed_by (m_id, d_id) VALUES(1,1);
                      INSERT INTO directed_by (m_id, d_id) VALUES(2,2);
                      INSERT INTO directed_by (m_id, d_id) VALUES(3,3);
                      """)
    conn.commit()
    conn.close()


def add_movie(file):
    """
    (string) --> none

    saves the names of a file and its length in the local movie database.
    The function assumes that the files have names that refer to the actual movie titles.
    ?? This function can also be used to update the database; it then looks for movies files that have not been added yet.
    """

    # select name from path
    # stripping input of path
    name = file[(len(os.path.basename(file))):-4]

    # stripping input of extension

    # figure out it's length in Minutes
    # https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python


    #also checking if movie was deleted? How could that be done without rewriting the whole db?
    #INSERT OR IGNORE INTO
    #conn.commit()


def descend_directories(top):
    """
    (string) --> none

    recursively descend the given directory tree and calling the add_movie function for each film file.
    """
    movie_extensions = (".AVI", ".avi", ".FLV", ".flv", ".WMV", ".wmv", ".MOV", ".mov", ".MP4", ".mp4")

    for f in os.listdir(top):
        # does this automatically add the \ or / to the path?
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        # if item is directory, recurse into it
        if S_ISDIR(mode):
            descend_directories(pathname)
        # if item is a regular file: check if it is a film file
        elif S_ISREG():
            if pathname.endswith(movie_extensions):
                add_movie()

def fill_info_mdb():
    """
    (none) ---> none

    Checks the correctness of the titles from the movies in the database and searches additional information:
    year, countries, director, genre and plot.

    This data is collected with an API to an online database and is saved in the local movie database.
    """
    # for parse through text and place a \ before all 's

