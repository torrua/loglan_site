# -*- coding: utf-8 -*-
"""
App's routes module
"""

import distutils.util
import os

from flask import jsonify, render_template, request, redirect, url_for
from app.compose.english_item import EnglishItem
from app.compose.loglan_item import LoglanItem, Composer
from loglan_core import Event
from app.engine import Session
from app import app
from functions import get_data

DEFAULT_SEARCH_LANGUAGE = os.getenv("DEFAULT_SEARCH_LANGUAGE", "log")
DEFAULT_HTML_STYLE = os.getenv("DEFAULT_HTML_STYLE", "normal")
main_site = "http://www.loglan.org/"


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
@app.route("/dictionary/")
def dictionary():
    session = Session()
    events = session.query(Event).all()
    events = {event.id: event.name for event in reversed(events)}
    content = generate_content(request.args)
    return render_template("dictionary.html", content=content, events=events)


@app.route("/how_to_read")
def how_to_read():
    return render_template("reading.html")


@app.route("/submit_search", methods=["POST"])
def submit_search():
    return generate_content(request.form)


def generate_content(data):
    session = Session()
    word = data.get("word", str())
    search_language = data.get('language_id', DEFAULT_SEARCH_LANGUAGE)
    event_id = data.get("event_id", 1)
    is_case_sensitive = data.get("case_sensitive", False)

    if not word or not data:
        return jsonify(result="<div></div>")

    nothing = """
<div class="alert alert-secondary" role="alert" style="text-align: center;">
  %s
</div>
    """

    if isinstance(is_case_sensitive, str):
        is_case_sensitive = bool(distutils.util.strtobool(is_case_sensitive))

    if search_language == "log":

        word_statement = LoglanItem.query_select_words(name=word, event_id=event_id, case_sensitive=is_case_sensitive)
        word_result = session.execute(word_statement).scalars().all()
        result = Composer(words=word_result, style=DEFAULT_HTML_STYLE).export_as_html()

        if not result:
            result = nothing % f"There is no word <b>{word}</b> in Loglan. Try switching to English" \
                               f"{' or disable Case sensitive search' if is_case_sensitive else ''}."

    elif search_language == "eng":
        definitions_statement = EnglishItem.select_definitions_by_key(key=word, event_id=event_id, case_sensitive=is_case_sensitive)
        definitions_result = session.execute(definitions_statement).scalars().all()

        result = EnglishItem(definitions=definitions_result, key=word, style=DEFAULT_HTML_STYLE).export_as_html()
        print(result)
        if not result:
            result = nothing % f"There is no word <b>{word}</b> in English. Try switching to Loglan" \
                               f"{' or disable Case sensitive search' if is_case_sensitive else ''}."
    else:
        result = nothing % f"Sorry, but nothing was found for <b>{word}</b>."
    return jsonify(result=result)


@app.route('/<string:section>/', methods=['GET', 'POST'])
@app.route('/<string:section>/<string:article>', methods=['GET', 'POST'])
def proxy(section: str = "", article: str = ""):
    url = f"{main_site}{section}/{article}"
    content = get_data(url)["content"].body

    for bq in content.findAll("blockquote"):
        bq['class'] = "blockquote"

    for img in content.findAll("img"):
        # del(img["alt"])
        img['src'] = main_site + section + "/" + img['src']

    name_of_article = content.h1.extract().get_text()
    return render_template("article.html", name_of_article=name_of_article, article=content, title=section)
