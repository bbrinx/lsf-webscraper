"""Web server which handles incoming requests to scrape room occupation from LSF"""

import re
from flask import Flask, request, jsonify
import room_occupied
APP = Flask(__name__)

@APP.route('/')
def get_room_occupation():
    """Parse room from query params and look up its occupation."""
    room = request.args.get('room')
    if room:
        room_args = re.split('([0-9]+)', room)
        if '' in room_args:
            room_args.remove('')
        if len(room_args) == 2:
            occupied = room_occupied.main(room_args)
            return jsonify(occupied=occupied)
        return jsonify(error='Wrong room format. Room must have format C355.'), 400
    return jsonify(error='Please provide a room in the query parameters.'), 400
