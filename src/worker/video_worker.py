import time
import datetime
from src.worker.shared import process_queue, current_processing_info, LOCAL_DIR, TESSERACT_CMD, SPRING_SERVER
from src.downloader.downloader import Downloader
from src.analyzer.analyzer import VideoAnalyzer
from src.cutter import cutter
import requests
from src.analyzer.analyzer import RequestedQuitException
from src.deleter.deleter import delete_local_directory
from src.remote.remote import query_remove_remote_directory, query_remove_remote_question, query_rsync


def process_video_task():
    while True:
        time.sleep(5)
        if not (process_queue.empty()):
            video_id, member_id, post_id, _ = process_queue.get()
            current_processing_info.post_id.value = post_id
            process_video(video_id, member_id, post_id)
            current_processing_info.done()

# 이 함수는 크게 [다운로드, 분석, 컷, 작업물전송, 응답] 으로 나뉨
def process_video(video_id, member_id, post_id):

    start_time = datetime.datetime.now()
    print("DOWNLOAD Start time:", start_time, flush=True)
    # download
    downloader = Downloader()
    try:
        ext_low, ext_high = downloader.download(video_id, member_id, post_id)
    except RequestedQuitException:
        print('quit requested', flush=True)
        return
    except Exception as e:
        print(f'unexpected err: {e}', flush=True)
        return
    end_time = datetime.datetime.now()
    print("DOWNLOAD End time:", end_time, flush=True)

    start_time = datetime.datetime.now()
    print("ANALYSIS Start time:", start_time, flush=True)

    # alalysis
    analyzer = VideoAnalyzer(tesseract_cmd=TESSERACT_CMD)
    try:
        video_path_low = f'{LOCAL_DIR}/downloads/{member_id}/{post_id}/low'
        time_intervals = analyzer.analyze(
            video_path_low, ext_low, member_id, post_id)
    except RequestedQuitException:
        print('quit requested', flush=True)
        return
    except Exception as e:
        print(f'unexpected err: {e}', flush=True)
        return
    end_time = datetime.datetime.now()
    print("ANALYSIS End time:", end_time, flush=True)

    start_time = datetime.datetime.now()
    print("CUT Start time:", start_time, flush=True)

    # cut
    try:
        video_path_high = f'{LOCAL_DIR}/downloads/{member_id}/{post_id}/high'
        complete = cutter.cut_video_segments(
            time_intervals, video_path_high, ext_high, member_id, post_id)
    except RequestedQuitException:
        print('quit requested', flush=True)
        return
    except Exception as e:
        print(f'unexpected err: {e}', flush=True)
        return
    end_time = datetime.datetime.now()
    print("CUT End time:", end_time, flush=True)

    # rsync
    result = []
    for i in range(0, len(complete), 2):
        start_time_without_colons = complete[i]
        end_time_without_colons = complete[i + 1]
        query_rsync(member_id, post_id, start_time_without_colons,
                    end_time_without_colons, result)
    delete_local_directory(member_id, post_id)

    # response
    external_server_url = f'{SPRING_SERVER}/extractor/complete'
    payload = {"result": result, "postId": post_id}
    try:
        response = requests.post(external_server_url, json=payload)
        response.raise_for_status()

        print(f"External server response: {response.text}", flush=True)

        # current_processing_info.done() 하기 전에 delete 요청이 올 수 있다.
        # return 하기 전 delete 요청이 온 적 있는지 최종 확인
        current_processing_info.state.value = 'sending resopnse after local data deleted'
        if current_processing_info.quit_flag.value == 1:
            query_remove_remote_directory(member_id, post_id)
            return

    except requests.exceptions.RequestException as e:
        print(f"Error sending request to external server: {e}", flush=True)


def delete_by_post_id(member_id, post_id):
    if current_processing_info.is_current_job(post_id):
        current_processing_info.quit_flag.value = 1
        return 'QUIT current job'

    _, position = process_queue.find_position(post_id)
    if (position > 0):
        process_queue.remove_nth_element(position)
        return 'job in the queue REMOVED'

    query_remove_remote_directory(member_id, post_id)
    return 'the video on the storage REMOVED'
