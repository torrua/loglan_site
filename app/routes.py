from flask import jsonify,  render_template, request, send_from_directory
from loglan_db.model_html import HTMLExportWord as Word
from app import app


"""
@app.route("/", defaults={"js": "plain"})
@app.route("/<any(plain, jquery, fetch):js>")
def index(js):
    return render_template(f"{js}.html", js=js)
"""


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/how_to_read")
def how_to_read():
    return render_template("reading.html")


@app.route("/get_loglan_word", methods=["POST"])
def get_loglan_word():
    word = request.form.get("word", "", type=str)
    word_obj = Word.by_name(word).first()
    name = f"<b>{word_obj.name}</b>,"
    meaning = word_obj.meaning(style="ultra")
    tech = meaning.get("technical", "")
    definitions_list = meaning.get("definitions", list())
    definitions = "".join(definitions_list)
    used_in = f'Used in: {meaning.get("used_in", "")}'

    res_text = "<br>".join([name, tech, definitions, used_in])
    return jsonify(result=res_text)

