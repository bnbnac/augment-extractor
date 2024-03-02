from flask import request, jsonify
from downloader import downloader
from analyzer.analyzer import VideoAnalyzer
from cutter import cutter

from routes import bp


@bp.route('/augment', methods=['POST'])
def create():
    url = request.args.get('url')
    question_id = "okk"

    video_path_low, ext_low = downloader.download_low_qual(url, question_id)
    video_path_high, ext_high = downloader.download_high_qual(url, question_id)

    analyzer = VideoAnalyzer()
    time_intervals = analyzer.analyze_video(video_path_low, ext_low)
    cutter.cut_video_segments(time_intervals, video_path_high, ext_high)


@bp.route('/augment', methods=['DELETE'])
def delete():
    json = request.get_json()
    question_id = json.get('question_id')

    # ok = deleter.delete(question_id)
    response = {'ok': 'ok'}
    return jsonify(response)
