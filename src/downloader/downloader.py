from yt_dlp import YoutubeDL
import os


def download_low_qual(url, member_id, post_id):
    dir = f'/Users/hongseongjin/code/augment-extractor/downloads/{member_id}/{post_id}'
    if not os.path.exists(dir):
        os.makedirs(dir)

    ydl_opts = {
        'outtmpl': f'{dir}/low.%(ext)s',
        'format': 'worstvideo[height>=480]'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_ext = info_dict['ext']
        ydl.download([url])

    video_path = f'{dir}/low'
    return video_path, video_ext


def download_high_qual(url, member_id, post_id):
    dir = f'/Users/hongseongjin/code/augment-extractor/downloads/{member_id}/{post_id}'
    if not os.path.exists(dir):
        os.makedirs(dir)

    ydl_opts = {
        'outtmpl': f'{dir}/high.%(ext)s',
        'format': 'worstvideo[height>=1080]+bestaudio'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_ext = info_dict['ext']
        ydl.download([url])

    video_path = f'{dir}/high'
    return video_path, video_ext


# # dot split -1
# print(download_low_qual("https://www.youtube.com/watch?v=3lm-v1zP43c", "hihi4"))
