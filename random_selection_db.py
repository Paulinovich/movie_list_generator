import sqlite3
import os
    
def select_movies(list_names, max_length):
    """
    (list, int) --> list
    
    returns a list of randomly id's of movies in the database that don't exceed the maximum length given (optional).
    The size of this returned list is one more than the amount of spectators.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 

    conn=sqlite3.connect(db_path)
    cur=conn.cursor()
    
    size=len(list_names)+1
    list_movies=[]
    cur.execute('SELECT COUNT(*) FROM movie')
    length_db = cur.fetchone()[0]
        #when no maximum length is given
    if max_length==None:
        if size <= length_db:
            cur.execute('SELECT m_id FROM movie ORDER BY RANDOM() LIMIT(?)',(size, ))
            for mov in cur:
                list_movies.append(mov)
        else:
            print("There are not enough movies found.\nPlease cluster viewers in groups")
            conn.close()
            exit()
    #selecting based on the maximum length
    else:
        try: 
            cur.execute('SELECT m_id FROM movie WHERE length<=? ORDER BY RANDOM() LIMIT(?)',(max_length, size))
            for mov in cur:
                list_movies.append(mov)         
        except:
            print("There are not enough movies found with your given criteria.\nPlease cluster viewers in groups or give a higher maximum duration.")
            conn.close()
            exit()
    conn.close() 
    return list_movies
    

def movie_info_selection(list_movies):
    """
    (list) --> list of dictionaries
    
    Returns the needed information about the selected movies from the database.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 

    conn=sqlite3.connect(db_path)
    cur=conn.cursor()
    # we store information for each movie in a dictionary and store these in a list
    all_information = []

    for movie in list_movies:
        information = {}

        cur.execute('SELECT title, original_title, image_link, plot, y_id FROM movie WHERE m_id={}'.format(movie))
        (title, original_title, duration, image_link, plot, y_id) = cur.fetchone()
        # changing double single-quotation marks back to one.
        title, original_title, plot = normal_string([title, original_title, plot])
        information["title"] = title
        information["original_title"] = original_title
        information["image_link"] = image_link
        information["plot"] = plot

        cur.execute('SELECT year FROM year WHERE m_id={}'.format(y_id))
        information["year"] = cur.fetchone()[0]

        # getting genre info
        cur.execute('SELECT g_id FROM defined_as WHERE m_id={}'.format(movie))
        g_id_tuples = cur.fetchall()
        # saving genres in one string
        genres = ''
        for g_id_tuple in g_id_tuples:
            g_id = g_id_tuple[0]
            cur.execute('SELECT name_genre FROM genre WHERE g_id={}'.format(g_id))
            genres = genres + ", "+cur.fetchone()[0]
        # removes comma and space at beginning of string
        information["genres"] = genres.lstrip(", ")
        
        # getting countries info and saving in one string
        cur.execute('SELECT c_id FROM produced_in WHERE m_id={}'.format(movie))
        c_id_tuples = cur.fetchall()
        countries = ''
        for c_id_tuple in c_id_tuples:
            c_id = c_id_tuple[0]
            cur.execute('SELECT abbreviation_country FROM country WHERE c_id={}'.format(c_id))
            countries = countries + ", "+cur.fetchone()[0]
        information["countries"] = countries.lstrip(", ")

        # getting director info and saving in one string
        cur.execute('SELECT d_id FROM directed_by WHERE m_id={}'.format(movie))
        d_id_tuples = cur.fetchall()
        directors = ''
        for d_id_tuple in d_id_tuples:
            d_id = d_id_tuple[0]
            cur.execute('SELECT name_director FROM director WHERE d_id={}'.format(d_id))
            directors = directors + ", "+cur.fetchone()[0]
        information["directors"] = directors.lstrip(", ")

        all_information.append(information)
    conn.close()
    return all_information





def normal_string(strings):
    """
    (list) --> string

    Changes every double single-quote (') character back to the original one.
    """
    for string in strings:
        string.replace("''", "'")
    return strings[0], strings[1], strings[2]
