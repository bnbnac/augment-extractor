from yt_dlp import YoutubeDL


def download_low_qual(url, question_id):
    ydl_opts = {
        'outtmpl': f'downloads/low/{question_id}.%(ext)s',
        'format': 'worstvideo[height>=480]'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_ext = info_dict['ext']
        ydl.download([url])

    video_path = f'downloads/low/{question_id}'
    return video_path, video_ext


def download_high_qual(url, question_id):
    ydl_opts = {
        'outtmpl': f'downloads/high/{question_id}.%(ext)s',
        'format': 'bestvideo[height<=1080]+bestaudio'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_ext = info_dict['ext']
        ydl.download([url])

    video_path = f'downloads/high/{question_id}'
    return video_path, video_ext


# # dot split -1
# print(download_low_qual("https://www.youtube.com/watch?v=3lm-v1zP43c", "hihi4"))
