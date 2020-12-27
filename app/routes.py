from flask import jsonify,  render_template, request
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


@app.route("/dictionary")
def search():
    return render_template("dictionary.html")


@app.route("/how_to_read")
def how_to_read():
    return render_template("reading.html")


@app.route("/get_loglan_word", methods=["POST"])
def get_loglan_word():
    search_language = request.form.getlist('search_lang')[0]
    word = request.form.get("word", "", type=str)

    if not word:
        return jsonify(result="<div></div>")

    nothing = """
<div class="alert alert-secondary" role="alert" style="text-align: center;">
  %s
</div>
    """

    if search_language == "log":
        result = Word.html_all_by_name(word, style="normal")
        if not result:
            result = nothing % f"There is no word <b>{word}</b> in Loglan. Try switching to English."
    elif search_language == "eng":
        result = Word.translation_by_key(word, style="normal")
        if not result:
            result = nothing % f"There is no word <b>{word}</b> in English. Try switching to Loglan."
    else:
        result = nothing % f"Sorry, but nothing was found for <b>{word}</b>."

    return jsonify(result=result)
