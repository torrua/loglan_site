# -*- coding: utf-8 -*-
"""
App's routes module
"""

import distutils.util
import os

from flask import jsonify, render_template, request
from loglan_db.model import Event
from loglan_db.model_html import HTMLExportWord as Word

from app import app
from functions import get_data

DEFAULT_SEARCH_LANGUAGE = os.getenv("DEFAULT_SEARCH_LANGUAGE", "log")
DEFAULT_HTML_STYLE = os.getenv("DEFAULT_HTML_STYLE", "normal")

"""
@app.route("/", defaults={"js": "plain"})
@app.route("/<any(plain, jquery, fetch):js>")
def index(js):
    return render_template(f"{js}.html", js=js)
"""


@app.route("/articles")
def articles():
    article_block = get_data("http://www.loglan.org/")["content"]
    content = article_block.find("a", attrs={"name": "articles"}).find_parent('h2').find_next("ol")
    return render_template("articles.html", articles=content)


@app.route('/Articles/<variable>', methods=['GET', 'POST'])
def daily_post(variable):
    url = f"http://www.loglan.org/Articles/{variable}"
    content = get_data(url)["content"].body

    for bq in content.findAll("blockquote"):
        bq['class'] = "blockquote"

    name_of_article = content.h1.extract().get_text()
    return render_template("article.html", name_of_article=name_of_article, article=content)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/dictionary")
def dictionary():
    events = {event.id: event.name for event in reversed(Event.get_all())}
    return render_template("dictionary.html", events=events)


@app.route("/how_to_read")
def how_to_read():
    return render_template("reading.html")


@app.route("/submit_search", methods=["POST"])
def submit_search():
    search_language = request.form.get('search_lang', DEFAULT_SEARCH_LANGUAGE)
    word = request.form.get("word", "")
    current_event_id = request.form.get("current_event_id", Event.latest().id)
    is_case_sensitive = bool(distutils.util.strtobool(request.form.get("case_sensitive", False)))
    is_partial_results = bool(distutils.util.strtobool(request.form.get("partial_results", False)))

    if not word:
        return jsonify(result="<div></div>")

    nothing = """
<div class="alert alert-secondary" role="alert" style="text-align: center;">
  %s
</div>
    """

    if search_language == "log":
        result = Word.html_all_by_name(
            name=word, style=DEFAULT_HTML_STYLE,
            event_id=current_event_id,
            case_sensitive=is_case_sensitive,
            partial_results=is_partial_results)

        if not result:
            result = nothing % f"There is no word <b>{word}</b> in Loglan. Try switching to English" \
                               f"{' or disable Case sensitive search' if is_case_sensitive else ''}."

    elif search_language == "eng":
        result = Word.translation_by_key(word, style=DEFAULT_HTML_STYLE)
        if not result:
            result = nothing % f"There is no word <b>{word}</b> in English. Try switching to Loglan" \
                               f"{' or disable Case sensitive search' if is_case_sensitive else ''}."
    else:
        result = nothing % f"Sorry, but nothing was found for <b>{word}</b>."

    return jsonify(result=result)
