import time
from src.worker.shared import process_queue
from src.downloader import downloader
from src.analyzer.analyzer import VideoAnalyzer
from src.cutter import cutter
import requests
import subprocess


def process_video_task():
    while True:
        time.sleep(5)
        if not (process_queue.empty()):
            video_id, post_id, _ = process_queue.get()
            process_video(video_id, post_id)


def process_video(video_id, post_id):
    url = f'https://www.youtube.com/watch?v={video_id}'

    video_path_low, ext_low = downloader.download_low_qual(url, post_id)
    video_path_high, ext_high = downloader.download_high_qual(url, post_id)

    analyzer = VideoAnalyzer()
    time_intervals = analyzer.get_time_interval_from_video(
        video_path_low, ext_low)
    complete = cutter.cut_video_segments(
        time_intervals, video_path_high, ext_high, post_id)

    result = []
    for i in range(0, len(complete), 2):
        start_time_without_colons = complete[i]
        end_time_without_colons = complete[i + 1]
        query_rsync(post_id, start_time_without_colons,
                    end_time_without_colons, result)

    external_server_url = f'http://localhost:8080/extractor/complete'
    payload = {"result": result, "postId": post_id}

    try:
        response = requests.post(external_server_url, json=payload)
        response.raise_for_status()

        print(f"External server response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error sending request to external server: {e}")
