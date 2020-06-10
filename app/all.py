from flask import Blueprint
import os
from .tasks import process_image
from flask import request
bp = Blueprint("all", __name__)

@bp.route("/")
def index():
    return "Hello!"

@bp.route("/<string:jobid>/<string:modelid>")
def makefile(jobid,modelid):
    #fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    task = process_image.delay(jobid,modelid)
    return task.id#f"Find your file @ <code>{fpath}</code>"

@bp.route('/image-data-async', methods=['POST'])
def post_image_data():
    req_data = request.get_json()
    print(req_data["job_id"] + " " + req_data["model_id"])
    task = process_image.delay(req_data["job_id"],req_data["model_id"])
    return task.id