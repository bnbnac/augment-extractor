import subprocess
import os

# ['00:00:35', '00:00:47', '00:03:21', '00:03:30', '00:06:51', '00:06:51']
# https://youtu.be/3lm-v1zP43c?si=dAx1RY6CQRSmWsY5


def cut_video_segments(time_intervals: list[str], input_video_path, ext, post_id):
    complete = []
    for i in range(0, len(time_intervals), 2):
        input_path = input_video_path + "." + ext
        start_time = time_intervals[i]
        end_time = time_intervals[i + 1]
        start_time_without_colons = start_time.replace(":", "")
        end_time_without_colons = end_time.replace(":", "")

        output_path = f"/Users/hongseongjin/code/augment-extractor/downloads/{post_id}/{start_time_without_colons}_{end_time_without_colons}.mp4"

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-ss", start_time,
                "-to", end_time,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path
            ]
            subprocess.run(cmd)
            complete.append(start_time_without_colons)
            complete.append(end_time_without_colons)

        except Exception:
            print(f"cut video failed: cut number #{i // 2 + 1}")

    return complete


# timestamps = ['00:00:35', '00:00:47', '00:03:21',
#               '00:03:30', '00:06:51', '00:06:52']
# input_video_path = "/Users/hongseongjin/code/augment-extractor/downloads/high/hello.webm"

# cut_video_segments(timestamps, input_video_path)
