from flask import Blueprint, request, jsonify

bp = Blueprint('routes', __name__)

@bp.route('/augment', methods=['POST'])
def create():
    json = request.get_json()
    url = json.get("url")
    question_id = json.get("question_id")

    import downloader
    downloader.download(url, question_id)

    response = {'dir':'some dir'}

    return jsonify(response)

@bp.route('/augment', methods=['DELETE'])
def delete():
    url = request.get_json()
    response = {'received':url}
    return jsonify(response)