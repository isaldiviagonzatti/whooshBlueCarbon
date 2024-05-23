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


app = Flask(__name__)


def search_motcle(mot):
    results_list = []
    ix = index.open_dir("indexWhoosh")
    with ix.searcher() as searcher:
        # Use a MultifieldParser to search across multiple fields
        query = MultifieldParser(
            [
                "title",
                "keywordsmanual",
                "filename",
                # "keywords",
                # "category",
                "authors",
                # "abstract",
                "doi_link",
                "text",
            ],
            schema=ix.schema,
        ).parse(mot)
        res = searcher.search(query, limit=None)
        # Use ContextFragmenter to show only the text around the keywords
        # res.fragmenter = highlight.ContextFragmenter(
        #     surround=20
        # )
        res.fragmenter = highlight.WholeFragmenter()
        for hit in res:
            results_list.append(
                {
                    "title": hit["title"],
                    "keywordsmanual": hit["keywordsmanual"],
                    "filename": hit["filename"],
                    # "keywords": hit["keywords"],
                    # "category": hit["category"],
                    "authors": hit["authors"],
                    # "abstract": hit["abstract"],
                    "doi_link": hit["doi_link"],
                    "text": hit.highlights(
                        "text",
                        minscore=0,
                    ),  # Top specifies the number of fragments to show
                }
            )
    return results_list


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/search", methods=["POST", "GET"])
# def search():
#     if request.method == "GET":
#         t = time.time()
#         q = request.args.get("q")
#         res = search_motcle(q)
#         return render_template(
#             "res.html", res=res, n=len(res), tm=round(time.time() - t, 2)
#         )


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
