from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
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


@app.route("/movieselector")
def movieselector():
    return render_template("movieselector.html")


if __name__ == "__main__":
    app.run(debug=True)