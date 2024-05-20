from flask import request, jsonify, Blueprint
from src.worker.shared import process_queue, current_processing_info
from src.worker.video_worker import delete_by_post_id, query_remove_remote_question

bp = Blueprint('api', __name__, url_prefix='/')


@bp.route('/analysis', methods=['POST'])
def create():
    try:
        data = request.json
        video_id = data.get('videoId')
        member_id = data.get('memberId')
        post_id = str(data.get('postId'))
        init_queue_size = process_queue.qsize()

        process_queue.put([video_id, member_id, post_id, init_queue_size])
        return '', 200

    except:
        return jsonify({"error": "Invalid JSON data"}), 400


@bp.route('/position', methods=['GET'])
def get_position():
    try:
        post_id = request.args.get('id')
        initial_position, cur_position = process_queue.find_position(post_id)
        cur_post_id = current_processing_info.post_id.value
        state = current_processing_info.state.value
        total_frame = current_processing_info.total_frame.value
        cur_frame = current_processing_info.cur_frame.value

        return jsonify({
            "curPosition": cur_position,
            "initialPosition": initial_position,
            "curPostId": cur_post_id,
            "curFrame": cur_frame,
            "totalFrame": total_frame,
            "state": state
            }), 200

    except:
        return jsonify({"error": "invalid post ID"}), 400


@bp.route('/posts', methods=['DELETE'])
def delete_post():
    try:
        member_id = request.args.get('memberId')
        post_id = request.args.get('postId')
        reply = delete_by_post_id(member_id, post_id)

        return jsonify({"extractorReply": reply}), 200

    except:
        return jsonify({"error": "unexpected error"}), 400


@bp.route('/questions', methods=['DELETE'])
def delete_question():
    try:
        member_id = request.args.get('memberId')
        post_id = request.args.get('postId')
        filename = request.args.get('filename')
        reply = query_remove_remote_question(member_id, post_id, filename)

        return jsonify({"extractorReply": reply}), 200

    except:
        return jsonify({"error": "unexpected error"}), 400
