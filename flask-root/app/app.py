#!/bin/env python

from flask import Flask
import redis

app = Flask(__name__)

kv = redis.Redis(host="redis", decode_responses=True)


@app.route("/")
@app.route("/index")
def base():
    ## we want to refresh this each time we refresh the page incase it's
    ## not ready on first startup.
    viewer0 = kv.hgetall("viewer0")
    notebookurl = "http://localhost/notebook"
    neuroglancerurl = f"http://localhost/nglancer/v/{viewer0['token']}/"

    ## this just bruteforce dumps html into a return output instead of a polished
    # template but should be fine as a demo.
    return f"""
<html>
    <head>
        <title>Home Page - Neuroglancer</title>
    </head>
    <body>
        <h1>neuroglancercv</h1>
        <h2>Links: </h2>

        <a href={neuroglancerurl} target="_blank"> Nueroglancer Interface </a>
        <br>
        <a href={notebookurl} target="_blank"> iPython Notebooks </a>
    </body>
</html>"""

    # return "PNI Neuroglancer and Cloudvolume demo program"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
