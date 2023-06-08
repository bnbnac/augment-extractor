from flask import Blueprint, request, jsonify

bp = Blueprint('routes', __name__)

@bp.route('/augment', methods=['POST'])
def create():
    url = request.get_json()
    response = {'received':url}
    return jsonify(response)

@bp.route('/augment', methods=['DELETE'])
def delete():
    url = request.get_json()
    response = {'received':url}
    return jsonify(response)