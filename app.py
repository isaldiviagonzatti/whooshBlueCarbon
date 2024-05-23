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
from whoosh.query import And, Term, Or
from whoosh.qparser import OrGroup


app = Flask(__name__)


def search_Near(words, slop=10):
    results_list = []
    ix = index.open_dir("indexWhoosh")
    with ix.searcher() as searcher:
        # Split the search query into individual words
        words = words.split()

        # Create a SpanNear query with a specified slop (proximity)
        span_near_query = SpanNear.phrase("text", words, slop=slop)
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


# def search_by_category(text_query, categories):
#     results_list = []
#     ix = index.open_dir("indexWhoosh")

#     with ix.searcher() as searcher:
#         # Create the category filter query
#         if categories:
#             if len(categories) > 1:
#                 cat_q = Or([Term("keywordsmanual", x) for x in categories])
#             else:
#                 cat_q = Term("keywordsmanual", next(iter(categories)))

#         else:
#             cat_q = None

#         # Create the text query
#         parser = MultifieldParser(["text"], ix.schema, group=OrGroup)
#         query = parser.parse(text_query)

#         if cat_q is None:
#             # No category filter, just search the text query
#             results = searcher.search(query, limit=None)
#             results.fragmenter = highlight.WholeFragmenter()
#         else:
#             # Use the category filter
#             results = searcher.search(And([cat_q, query]), limit=None)
#             results.fragmenter = highlight.WholeFragmenter()
#         for hit in results:
#             results_list.append(
#                 {
#                     "title": hit["title"],
#                     "keywordsmanual": hit["keywordsmanual"],
#                     "filename": hit["filename"],
#                     "authors": hit["authors"],
#                     "doi_link": hit["doi_link"],
#                 }
#             )
#     return results_list


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/searchCategory")
def searchCategory():
    return render_template("searchCategory.html")


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        t = time.time()
        q = request.args.get("q")
        res = search_Near(q)
        return render_template(
            "res.html", res=res, n=len(res), tm=round(time.time() - t, 2), query=q
        )


@app.route("/searchR2", methods=["POST", "GET"])
def searchR2():
    if request.method == "GET":
        t = time.time()
        q = request.args.get("q")
        category = request.args.get("categories")
        res = search_by_category(q, category)
        return render_template(
            "res.html", res=res, n=len(res), tm=round(time.time() - t, 2)
        )


if __name__ == "__main__":
    app.run(debug=True)
