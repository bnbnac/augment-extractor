import subprocess
import os
from src.worker.shared import LOCAL_DIR, current_processing_info
from src.exception.exception import RequestedQuitException
from src.deleter.deleter import delete_local_directory


def cut_video_segments(time_intervals: list[str], input_video_path, ext, member_id, post_id):
    current_processing_info.state = 'cutting'
    if current_processing_info.quit_flag == 1:
        delete_local_directory(member_id, current_processing_info.post_id)
        raise RequestedQuitException

    complete = []
    for i in range(0, len(time_intervals), 2):
        input = f'{input_video_path}.{ext}'
        start_time = time_intervals[i]
        end_time = time_intervals[i + 1]
        start_time_without_colons = start_time.replace(":", "")
        end_time_without_colons = end_time.replace(":", "")

        output_path = f"{LOCAL_DIR}/downloads/{member_id}/{post_id}/{start_time_without_colons}_{end_time_without_colons}.mp4"
        cmd = [
            "ffmpeg",
            "-i", input,
            "-ss", start_time,
            "-to", end_time,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ]

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            subprocess.run(cmd)
            complete.append(start_time_without_colons)
            complete.append(end_time_without_colons)

        except Exception:
            print(f"cut video failed: cut number #{i // 2 + 1}")

    return complete