import time
from src.worker.shared import process_queue, current_processing_info
from src.downloader import downloader
from src.analyzer.analyzer import VideoAnalyzer
from src.cutter import cutter
import requests
import subprocess
from queue import Queue
from src.analyzer.analyzer import RequestedQuitException
from src.util.util import delete_local_directory


def process_video_task():
    while True:
        time.sleep(5)
        if not (process_queue.empty()):
            video_id, member_id, post_id, _ = process_queue.get()

            current_processing_info.post_id = post_id

            process_video(video_id, member_id, post_id)
            current_processing_info.done()


def find_position(post_id):
    initial = 0
    current = 0

    for i, el in enumerate(process_queue.queue):
        if str(el[2]) == str(post_id):
            initial = el[3] + 1
            current = i + 1
            break

    return initial, current


# 이 함수는 크게 [다운로드, 분석, 컷, 작업물전송, 작업물삭제, 응답] 으로 나뉨
def process_video(video_id, member_id, post_id):
    # download
    current_processing_info.state = 'video downloading'
    url = f'https://www.youtube.com/watch?v={video_id}'

    video_path_low, ext_low = downloader.download_low_qual(
        url, member_id, post_id)
    if current_processing_info.quit_flag == 1:
        directory = f'/Users/hongseongjin/code/augment-extractor/downloads'
        delete_local_directory(directory, member_id, post_id)
        return

    video_path_high, ext_high = downloader.download_high_qual(
        url, member_id, post_id)
    if current_processing_info.quit_flag == 1:
        directory = f'/Users/hongseongjin/code/augment-extractor/downloads'
        delete_local_directory(directory, member_id, post_id)
        return

    # alalysis
    analyzer = VideoAnalyzer()
    current_processing_info.state = 'on analysis'
    try:
        time_intervals = analyzer.get_time_interval_from_video(
            video_path_low, ext_low)
    except RequestedQuitException:
        print('quit requested')
        return
    except Exception as e:
        print(f'unexpected err: {e}')
        return

    # cut
    current_processing_info.state = 'cutting'
    if current_processing_info.quit_flag == 1:
        directory = f'/Users/hongseongjin/code/augment-extractor/downloads'
        delete_local_directory(directory, member_id, post_id)
        return
    complete = cutter.cut_video_segments(
        time_intervals, video_path_high, ext_high, member_id, post_id)

    # rsync
    current_processing_info.state = 'sending the result data'
    if current_processing_info.quit_flag == 1:
        directory = f'/Users/hongseongjin/code/augment-extractor/downloads'
        delete_local_directory(directory, member_id, post_id)
        return

    result = []
    for i in range(0, len(complete), 2):
        start_time_without_colons = complete[i]
        end_time_without_colons = complete[i + 1]
        query_rsync(member_id, post_id, start_time_without_colons,
                    end_time_without_colons, result)

    # delete dir
    current_processing_info.state = 'deleting the local data'
    if current_processing_info.quit_flag == 1:
        # 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면?
        # 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면?
        # 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면? 이거보다 아래에서 걸렸다면?
        # 나중에 처리하자꾸나
        directory = f'/Users/hongseongjin/code/augment-extractor/downloads'
        delete_local_directory(directory, member_id, post_id)
        return
    directory = f'/Users/hongseongjin/code/augment-extractor/downloads'
    delete_local_directory(directory, member_id, post_id)

    # response
    external_server_url = f'http://localhost:8080/extractor/complete'
    payload = {"result": result, "postId": post_id}

    try:
        response = requests.post(external_server_url, json=payload)
        response.raise_for_status()

        print(f"External server response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error sending request to external server: {e}")


def query_rsync(member_id, post_id, start_time_without_colons, end_time_without_colons, result):
    file_name = f"{start_time_without_colons}_{end_time_without_colons}.mp4"
    input_path = f"/Users/hongseongjin/code/augment-extractor/downloads/{member_id}/{post_id}/{file_name}"
    user = "bnbnac"
    server = "192.168.1.7"
    remote_directory = f"/mnt/p31/storage/{member_id}/{post_id}"
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


def delete_by_post_id(member_id, post_id):
    if (current_processing_info.post_id == post_id):  # 클래스 안으로 넣어야
        current_processing_info.quit_flag = 1
        return 'QUIT current job'

    _, position = find_position(post_id)

    if (position > 0):
        remove_nth_element(process_queue, position - 1)
        return 'job in the queue REMOVED'

    query_remove_remote_directory(member_id, post_id)
    return 'the video on the storage REMOVED'


def query_remove_remote_directory(member_id, post_id):
    user = "bnbnac"
    server = "192.168.1.7"
    remote_directory = f"/mnt/p31/storage/{member_id}/{post_id}"

    try:
        ssh_cmd = ["ssh", "-p", "22022",
                   f"{user}@{server}", "rm", "-rf", remote_directory]

        subprocess.run(ssh_cmd, check=True)
        print(
            f"Remote directory {remote_directory} and its contents successfully removed.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing remote directory: {e}")


def remove_nth_element(queue, n):
    temp_queue = Queue()

    for _ in range(n):
        if queue.empty():
            raise IndexError("Queue is empty or n is out of range")
        temp_queue.put(queue.get())

    queue.get()

    while not temp_queue.empty():
        queue.put(temp_queue.get())


def query_remove_remote_question(member_id, post_id, filename):
    user = "bnbnac"
    server = "192.168.1.7"
    remote_question = f"/mnt/p31/storage/{member_id}/{post_id}/{filename}"

    try:
        ssh_cmd = ["ssh", "-p", "22022",
                   f"{user}@{server}", "rm", remote_question]

        subprocess.run(ssh_cmd, check=True)
        print('the video on the storage REMOVED')
        return 'the video on the storage REMOVED'

    except subprocess.CalledProcessError as e:
        print('Error removing remote directory: {e}')
        return 'unexpected error'
