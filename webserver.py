import json
import os

import redis
from flask import Flask, render_template, request

from light_emitting_desk.desk import Desk
from light_emitting_desk.utils import conf
from colorsys import hsv_to_rgb

app = Flask(__name__)
app.redis = redis.Redis()

desk_conf = conf["sectors"]
if "TEST_SECTORS" in os.environ:
    desk_conf = json.loads(os.environ["TEST_SECTORS"])

app.desk = Desk(desk_conf)

mode_names = list(map(lambda x: x["name"], conf["modes"]))


@app.route("/", methods=["GET"])
def index():
    """Root endpoint."""
    if request.accept_mimetypes["text/html"]:
        return render_template(
            "index.html",
            title="LED",
            imports=conf["web"]["imports"],
            modes=conf["modes"],
        )

    return {"status": "OK"}


@app.route("/desk/light", methods=["POST"])
def set_colour():
    """Light the desk."""
    app.data = request.get_json()

    hsv_keys = ["hue", "saturation", "value"]
    colour = app.data.get("colour", [255, 0, 0])

    for key in hsv_keys:
        if key in app.data:
            h = app.data.get("hue", 1.0)
            s = app.data.get("saturation", 1.0)
            v = app.data.get("value", 1.0)

            colour = list(map(lambda x: int(x * 255), hsv_to_rgb(h, s, v)))

    mode = app.data.get("mode", "spot-fill")
    direction = app.data.get("direction", "forwards")

    if "flush" in app.data:
        app.redis.flushall()

    return enqueue_and_return({"colour": colour, "mode": mode, "direction": direction})


@app.route("/desk/off", methods=["POST"])
def switch_off():
    """Instantly turn it all off."""
    app.redis.flushall()
    colour = [0, 0, 0]
    app.data = {"colour": colour, "mode": "sector-diverge"}
    return enqueue_and_return(app.data)


@app.route("/desk/stop", methods=["POST"])
def stop():
    """Stop the repeater."""
    return enqueue_and_return({"system": {"repeater": "stop"}})


@app.route("/desk/start", methods=["POST"])
def start():
    """Start the repeater."""
    return enqueue_and_return({"system": {"repeater": "start"}})


@app.route("/desk/colour", methods=["GET"])
def current_desk_colour():
    """Return the desk's colour."""
    try:
        colour = json.loads(app.redis.get("colours/desk"))
        return {"colour": colour, "status": "OK"}

    except TypeError:
        return {"error": "no data for that"}, 404


def enqueue_and_return(data):
    """Light the lights."""
    app.redis.rpush("jobs", json.dumps(data))

    try:
        app.redis.set("colours/desk", json.dumps(data["colour"]))
        return {"colour": data["colour"], "status": "OK"}
    except KeyError:
        return {"status": "OK"}



if __name__ == "__main__":  # nocov
    app.run(host="0.0.0.0", debug=True)
