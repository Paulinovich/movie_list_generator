import database as db, random_list_users as rlu, random_selection_db as rsdb
import sqlite3
#import os.path

# to connect to the DB with the absolute path without errors. 
#base_dir = os.path.dirname(os.path.abspath(__file__))
#db_path = os.path.join(base_dir, "movie_db.sqlite") 

#conn=sqlite3.connect(db_path)
#cur=conn.cursor()


def create_update():
    """
    (none) --> none
    
    Asks the user if they want to create a new database or update the existing one and executes the functions doing so.
    """
    state=False
    print("to create a new movie database\n-->type 1\n\n")
    print("to update your movie database\n-->type 2\n\n")
    while state == False:
        option=input("your choice: ")
        if option=='1':
            db.create_mdb()
            db.fill_examles_mdb()
            state=True
            
        elif option=='2': 
            #start function to update the DB
            state=True
    
        else:
            print("wrong input")


def selection_programm():
    """
    (none) --> none
    
    Runs the selection programm: 
        - asking names of the spectators
        - asking about maximum duration of movie
        - selecting movies with these criteria
        - printing these movies and information
    """
    list_names=rlu.get_users_shuffled()
    length=rsdb.maxlengthfilm()
    list_movies=rsdb.select_movies(list_names, length)
    rsdb.movie_info_selection(list_movies)
    rlu.print_users(list_names)


print("\nto create or update the movie database\n--> type 1\n\n")
print("to generate a movie list\n-->type 2\n\n")

state = False
while state == False:
    option=input("your choice: ")
    if option=='1':
        create_update()
        state=True
        
        
    elif option=='2': 
        selection_programm()
        state=True
        
        #start random input_list_users.py funktion to generate a random list of viewers
    else:
        print("wrong input")
        


#create_update()

 
