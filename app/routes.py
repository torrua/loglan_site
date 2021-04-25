# -*- coding: utf-8 -*-
"""
App's routes module
"""

import distutils.util
import os

from flask import jsonify, render_template, request, redirect, url_for
from loglan_db.model import Event
from loglan_db.model_html.html_word import HTMLExportWord as Word

from app import app
from functions import get_data

DEFAULT_SEARCH_LANGUAGE = os.getenv("DEFAULT_SEARCH_LANGUAGE", "log")
DEFAULT_HTML_STYLE = os.getenv("DEFAULT_HTML_STYLE", "normal")
main_site = "http://www.loglan.org/"

"""
@app.route("/", defaults={"js": "plain"})
@app.route("/<any(plain, jquery, fetch):js>")
def index(js):
    return render_template(f"{js}.html", js=js)
"""


@app.route('/Articles/')
def redirect_articles():
    return redirect(url_for('articles'))


@app.route('/Texts/')
def redirect_texts():
    return redirect(url_for('texts'))


@app.route('/Sanpa/')
@app.route('/Lodtua/')
def redirect_columns():
    return redirect(url_for('columns'))


@app.route("/")
@app.route("/home")
def home():
    article = get_data(main_site)["content"].body.find("div", attrs={"id": "content"})
    for bq in article.findAll("blockquote"):
        bq['class'] = "blockquote"

    for img in article.findAll("img"):
        # del(img["alt"])
        img['src'] = main_site + img['src']
    return render_template("home.html", article="")


@app.route("/articles")
def articles():
    article_block = get_data(main_site)["content"]
    title = article_block.find("a", attrs={"name": "articles"}).find_parent('h2')
    content = title.find_next("ol")
    return render_template("articles.html", articles=content, title=title.get_text())


@app.route("/texts")
def texts():
    article_block = get_data(main_site)["content"]
    title = article_block.find("a", attrs={"name": "texts"}).find_parent('h2')
    content = title.find_next("ol")
    return render_template("articles.html", articles=content, title=title.get_text())


@app.route("/columns")
def columns():
    article_block = get_data(main_site)["content"]
    title = article_block.find("a", attrs={"name": "columns"}).find_parent('h2')
    content = title.find_next("ul")
    return render_template("articles.html", articles=content, title=title.get_text())


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
        result = Word.translation_by_key(
            key=word, style=DEFAULT_HTML_STYLE,
            case_sensitive=is_case_sensitive,
            partial_results=is_partial_results)

        if not result:
            result = nothing % f"There is no word <b>{word}</b> in English. Try switching to Loglan" \
                               f"{' or disable Case sensitive search' if is_case_sensitive else ''}."
    else:
        result = nothing % f"Sorry, but nothing was found for <b>{word}</b>."

    return jsonify(result=result)


@app.route('/<string:section>/', methods=['GET', 'POST'])
@app.route('/<string:section>/<string:article>', methods=['GET', 'POST'])
def test(section: str = "", article: str = ""):
    url = f"{main_site}{section}/{article}"
    content = get_data(url)["content"].body

    for bq in content.findAll("blockquote"):
        bq['class'] = "blockquote"

    for img in content.findAll("img"):
        # del(img["alt"])
        img['src'] = main_site + section + "/" + img['src']

    name_of_article = content.h1.extract().get_text()
    return render_template("article.html", name_of_article=name_of_article, article=content, title=section)
