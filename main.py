import json
from flask import Flask, render_template, redirect, url_for, request, Response
import requests
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import whoosh.index as index
from whoosh.qparser import MultifieldParser
import whoosh.highlight as highlight
from whoosh.query import SpanNear
import time
import re


app = Flask(__name__)


def search_motcle(mot, slop=10):
    results_list = []
    ix = index.open_dir("indexWhoosh")
    with ix.searcher() as searcher:
        # Split the search query into individual words
        words = mot.split()
        print(words)

        # Create a SpanNear query with a specified slop (proximity)
        span_near_query = SpanNear.phrase("text", words, slop=slop)
        print("Query Object:", span_near_query)
        res = searcher.search(span_near_query, limit=None)
        res.fragmenter = highlight.WholeFragmenter()

        # Define colors for highlighting
        colors = ["red", "blue", "green", "orange", "purple", "pink", "cyan", "yellow"]

        for hit in res:
            # Get highlighted text for each hit
            highlighted_text = hit.highlights("text", minscore=0)

            # Apply HTML formatting to the highlighted text, with different classes for each word
            for i, word in enumerate(words):
                highlighted_text = highlighted_text.replace(
                    word,
                    f'<span class="match-{i % len(colors)}">{word}</span>',
                )
                highlighted_text = highlighted_text.replace(
                    word.title(),
                    f'<span class="match-{i % len(colors)}">{word.title()}</span>',
                )

            results_list.append(
                {
                    "title": hit["title"],
                    "keywordsmanual": hit["keywordsmanual"],
                    "filename": hit["filename"],
                    "authors": hit["authors"],
                    "doi_link": hit["doi_link"],
                    "text": highlighted_text,
                }
            )
    return results_list


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/searchCategory", methods=["POST", "GET"])
def searchCategory():
    if request.method == "GET":
        t = time.time()
        q = request.args.get("q")
        sp = request.args.get("sp")
        res = search_sp(q, sp)
        return render_template(
            "res.html", res=res, n=len(res), tm=round(time.time() - t, 2, query=q)
        )


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        t = time.time()
        q = request.args.get("q")
        res = search_motcle(q)
        return render_template(
            "res.html", res=res, n=len(res), tm=round(time.time() - t, 2), query=q
        )


if __name__ == "__main__":
    app.run(debug=True)
