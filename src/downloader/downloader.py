from yt_dlp import YoutubeDL


def download_low_qual(url, question_id):
    ydl_opts = {
        'outtmpl': f'../../downloads/low/{question_id}.%(ext)s',
        'format': 'worstvideo[height>=360]'
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    video_path = f'downloads/low/{question_id}.ext'
    return video_path


def download_high_qual(url, question_id):
    ydl_opts = {
        'outtmpl': f'../../downloads/high/{question_id}.%(ext)s',
        'format': 'bestvideo[height<=1080]+bestaudio'
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    video_path = f'downloads/high/{question_id}.ext'
    return video_path


# dot split -1
download_high_qual("https://www.youtube.com/watch?v=3lm-v1zP43c", "hihi2")
