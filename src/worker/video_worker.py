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


# 나중에 Work 객체를 만들어서 이것저것 갖고있게?
def find_position(post_id):
    initial = 0
    current = 0

    for i, el in enumerate(process_queue.queue):
        if str(el[1]) == str(post_id):
            initial = el[2] + 1
            current = i + 1
            break

    return initial, current


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


def query_rsync(post_id, start_time_without_colons, end_time_without_colons, result):
    file_name = f"{start_time_without_colons}_{end_time_without_colons}.mp4"
    input_path = f"/Users/hongseongjin/code/augment-extractor/downloads/{post_id}/{file_name}"
    user = "bnbnac"
    server = "192.168.1.7"
    remote_directory = f"/mnt/p31/storage/{post_id}"
    destination_path = f"{user}@{server}:{remote_directory}/{file_name}"

    try:
        mkdir_cmd = ["ssh", "-p", "22022",
                     f"{user}@{server}", "mkdir", "-p", remote_directory]
        subprocess.run(mkdir_cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error creating directory: {e}")

    try:
        rsync_cmd = ["rsync", "-avz", "-e", "ssh -p 22022",
                     input_path, destination_path]
        subprocess.run(rsync_cmd)
        result.append(start_time_without_colons)
        result.append(end_time_without_colons)
    except subprocess.CalledProcessError as e:
        print(f"Error during rsync: {e}")
