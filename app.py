from flask import Flask, redirect, render_template, request, session
from flask_session.__init__ import Session
import database as db, random_selection_db as rsdb
import random

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
    #reset all names if user goes back to index: decided to use emty list instead of pop due to the many errorhandlings with the last
    session["names"]=[]
    return render_template("index.html")


@app.route("/dbsetup", methods=["GET", "POST"])
def dbsetup():
    if request.method == "GET":
        return render_template("dbsetup.html")

    elif request.method =="POST":
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
                        session["names"].append(name)
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
            # TODO: find out what datatype this returns
            # TODO: solve problem when no maxlength is given.
            maxlength=request.form.get("maxlength")
            session["maxlength"]=maxlength
            return redirect("/movieselector")

    return render_template("criteria.html", names=session["names"], names_set=names_set)


@app.route("/movieselector")
def movieselector():
    return render_template("movieselector.html", data=session)

if __name__ == "__main__":
    app.run(debug=True)