from flask import request, jsonify, Blueprint
from src.worker.shared import process_queue
from src.worker.video_worker import find_position

bp = Blueprint('api', __name__, url_prefix='/')


@bp.route('/analysis', methods=['POST'])
def create():
    try:
        data = request.json
        video_id = data.get('videoId')
        post_id = str(data.get('postId'))
        init_queue_size = process_queue.qsize()

        process_queue.put([video_id, post_id, init_queue_size])
        return '', 200

    except:
        return jsonify({"error": "Invalid JSON data"}), 400


@bp.route('/position', methods=['GET'])
def get_position():
    try:
        post_id = request.args.get('id')
        initial, current = find_position(post_id)

        return jsonify({"current": current, "initial": initial}), 200

    except:
        return jsonify({"error": "invalid post ID"}), 400

# @bp.route('/analysis', methods=['DELETE'])
# def delete():
#     json = request.get_json()
#     question_id = json.get('question_id')

#     # ok = deleter.delete(question_id)
#     response = {'ok': 'ok'}
#     return jsonify(response)
