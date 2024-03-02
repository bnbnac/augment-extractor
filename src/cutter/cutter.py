import subprocess

# ['00:00:35', '00:00:47', '00:03:21', '00:03:30', '00:06:51', '00:06:51']
# https://youtu.be/3lm-v1zP43c?si=dAx1RY6CQRSmWsY5


def cut_video_segments(timestamps, input_video_path, ext):
    for i in range(0, len(timestamps), 2):
        input_path = input_video_path + "." + ext

        start_time = timestamps[i]
        end_time = timestamps[i + 1]
        output_path = f"/Users/hongseongjin/code/augment-extractor/downloads/cut{i // 2 + 1}.mp4 "
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


# timestamps = ['00:00:35', '00:00:47', '00:03:21',
#               '00:03:30', '00:06:51', '00:06:52']
# input_video_path = "/Users/hongseongjin/code/augment-extractor/downloads/high/hello.webm"

# cut_video_segments(timestamps, input_video_path)
