from flask import Flask, jsonify
import room_occupied
APP = Flask(__name__)

@APP.route('/')
def getRoomOccupation():
    occupied = room_occupied.main(['C', '335'])
    return jsonify(occupied=occupied)
