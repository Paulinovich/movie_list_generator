from flask import Flask, redirect, render_template, request, session, url_for
from flask_session.__init__ import Session
import database as db, random_selection_db as rsdb
import random
import json

app = Flask(__name__)
app.config.from_object(__name__)
# TODO: read more about secret keys and actually make a good one
app.secret_key = 'secretterces'
# TODO: check the best session type for app and change if neccesary.
app.config['SESSION_TYPE'] = 'filesystem'
sess=Session()
sess.init_app(app)


@app.route("/")
def index():
    #reset all names if user goes back to index: decided to use empty list instead of pop due to the many errorhandlings with the last
    session["names"]=[]
    return render_template("index.html")


@app.route("/dbsetup", methods=["GET", "POST"])
def dbsetup():
    if request.method == "GET":
        return render_template("dbsetup.html")

    elif request.method =="POST":
        # create db and drop if exists to fill new. 
        topDir=request.form.get("directory")
        db.create_mdb()
        db.descend_directories(topDir)

        # 1. make the data base (in the meanwhile alert user to be patient), 
        # 2. create a popup if all went well to inform user
        # 3. return to index.html
        return redirect("/")

@app.route("/criteria", methods=["GET", "POST"])
def criteria():
    names_set=False

    if request.method == "POST":
        # when name is added
        if "add" in request.form:
            name=request.form.get("name")
            #only append if input isn't empty
            if name != '':
                    # if the variable names already exists inside the session
                    if session["names"]:
                        session["names"].append(name.rstrip('\n'))
                    # create a new variable names in the session
                    else:
                        names=[name]
                        session["names"]=names

        # erase all names
        elif "start_over" in request.form:
            session["names"]=[]

        # submit the names: set in random order and show lenght criteria
        elif "submit_names" in request.form:
            random.shuffle(session["names"])
            names_set=True
        
        # submit all criteria: send all criteria to movieselector page to make movie list
        elif "submit_all" in request.form:
            if len(request.form.get("hours"))>0:
                if len(request.form.get("minutes"))>0:
                    maxlength = int(request.form.get("minutes"))+(int(request.form.get("hours"))*60)    
                else:
                    maxlength = int(request.form.get("hours"))*60
            else: 
                if len(request.form.get("minutes"))>0:
                    maxlength = int(request.form.get("minutes"))
                else: 
                    maxlength = None
            session["maxlength"] = maxlength
            return redirect(url_for("movieselector"))
    return render_template("criteria.html", names=session.get("names"), names_set=names_set)


@app.route("/movieselector")
def movieselector():
    names = session.get("names")
    maxlength = session.get("maxlength")
    list_movies = rsdb.select_movies(names, maxlength)
    information = json.dumps(rsdb.movie_info_selection(list_movies))
    return render_template("movieselector.html", names=names, information=information)

if __name__ == "__main__":
    app.run(debug=True)