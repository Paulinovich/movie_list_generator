import sqlite3
import os
    
def select_movies(list_names, max_length):
    """
    (list, int) --> list of dictionaries
    
    returns a list dictonaries with information of randomly chosen movies from the database that don't exceed the maximum length given (optional).
    The size of this returned list is one more than the amount of spectators.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 

    conn=sqlite3.connect(db_path)
    # row factory attribute of sqlite3.connection to return the first indexed value in each row instead of the whole tuple.
    conn.row_factory = lambda cursor, row: row[0]
    cur=conn.cursor()
    
    size=len(list_names)+1
    list_movies=[]
    # TODO: would this also return a tuple if we didn't use the row factory attribute?
    length_db = cur.execute('SELECT COUNT(*) FROM movie')
    # when no maximum length is given
    if max_length==None:
        if size <= length_db:
            cur.execute('SELECT m_id FROM movie ORDER BY RANDOM() LIMIT(?)',(size, ))
            for mov in cur:
                list_movies.append(mov)
        else:
            print("There are not enough movies found.\nPlease cluster viewers in groups")
            conn.close()
            exit()
    # selecting based on the maximum length
    else:
        try: 
            cur.execute('SELECT m_id FROM movie WHERE length <= ? ORDER BY RANDOM() LIMIT(?)',(max_length, size))
            for mov in cur:
                list_movies.append(mov)         
        except:
            print("There are not enough movies found with your given criteria.\nPlease cluster viewers in groups or give a higher maximum duration.")
            conn.close()
            exit()
    
    movies = []
    for movie in list_movies:
        movies.append(movie_info_selection(movie))
    
    conn.close() 
    return movies


    
def movie_info_selection(movie):
    """
    (int) --> dict

    Returns the interesting information (title, year, plot, genres, directors and countries) as string values in a dictionary
    about a selected movie from the database of which its primary key m_id is given in a dictionary. 
    """
    # TODO: do we need to setup the connection again (and close it again) or is it still open from the select_movies function?
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "movie_db.sqlite") 
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # TITLE
    cur.execute('SELECT title FROM movie WHERE m_id==?',(movie,))
    title = cur.fetchone()
    # PLOT
    cur.execute('SELECT plot FROM movie WHERE m_id==?',(movie,))
    plot = cur.fetchone()
    # YEAR    
    cur.execute('SELECT year FROM year WHERE y_id IN(SELECT y_id FROM movie WHERE m_id==?)',(movie,))
    year = cur.fetchone()
    # GENRES
    cur.execute('SELECT name_genre FROM genre WHERE g_id IN(SELECT g_id FROM defined_as WHERE m_id==?)',(movie,))
    rows = cur.fetchall()
    genres=''
    for genre in rows:
        #first name without comma
        if len(genres)==0:
            genres+=genre[0]
        else:
            genres+=", "+genre[0]
    # DIRECTORS        
    cur.execute('SELECT name_director FROM director WHERE d_id IN(SELECT d_id FROM directed_by WHERE m_id==?)',(movie,))
    rows=cur.fetchall() 
    directors=''
    for director in rows:
        if len(directors)==0:
            directors+=director[0]
        else:
            directors+=", "+director[0]
    # COUNTRIES        
    cur.execute('SELECT name_country FROM country WHERE c_id IN(SELECT c_id FROM produced_in WHERE m_id==?)',(movie,))
    rows=cur.fetchall()
    countries=''
    for country in rows:
        if len(countries)==0:
            countries+=country[0]
        else:
            countries+=", "+country[0]
    # make dictionary
    return {"title": title, "year": year, "plot": plot, "genres": genres, "directors": directors, "countries": countries}