import os
from yt_dlp import YoutubeDL

def download(url, question_id):
    ydl_opts = {
        'outtmpl': 'downloads/{}.%(ext)s'.format(question_id),
        'format': 'worstvideo[height>=360]'
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])