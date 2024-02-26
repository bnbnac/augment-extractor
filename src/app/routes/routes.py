from flask import request, jsonify
from downloader.downloader import download
# from analyzer.analyzer import analyze

from routes import bp


@bp.route('/augment', methods=['POST'])
def create():
    json = request.get_json()
    url = json.get('url')
    question_id = json.get('question_id')

    video_path, ext = download(url, question_id)

)

    # spots = analyze(video_path, ext)
    # generate(spots)

    response = {'path': 'question_path'}

    # downloader failed res
    # analyzer failed res
    # generator failed res

    # success
    return jsonify(response)


@bp.route('/augment', methods=['DELETE'])
def delete():
    json = request.get_json()
    question_id = json.get('question_id')

    # ok = deleter.delete(question_id)
    response = {'ok': 'ok'}
    return jsonify(response)
