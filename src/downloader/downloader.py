from yt_dlp import YoutubeDL
import os
from src.exception.exception import RequestedQuitException
from src.deleter.deleter import delete_local_directory
from src.worker.shared import current_processing_info, LOCAL_DIR


class Downloader:
    def __init__(self):
        self.youtube_prefix = 'https://www.youtube.com/watch?v='

    def download(self, video_id, member_id, post_id):
        current_processing_info.state = 'video downloading'

        low_ext = self.download_low_qual(video_id, member_id, post_id)
        if current_processing_info.quit_flag == 1:
            delete_local_directory(member_id, current_processing_info.post_id)
            raise RequestedQuitException

        high_xet = self.download_high_qual(video_id, member_id, post_id)
        if current_processing_info.quit_flag == 1:
            delete_local_directory(member_id, current_processing_info.post_id)
            raise RequestedQuitException

        return low_ext, high_xet

    def download_low_qual(self, video_id, member_id, post_id):
        url = f'{self.youtube_prefix}{video_id}'

        download_dir = f'{LOCAL_DIR}/downloads/{member_id}/{post_id}'
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        ydl_opts = {
            'outtmpl': f'{download_dir}/low.%(ext)s',
            'format': 'worstvideo[height>=480][vcodec!*=av01]'
        }
        video_ext = self.ydl_download(url, ydl_opts)

        return video_ext

    def download_high_qual(self, video_id, member_id, post_id):
        url = f'{self.youtube_prefix}{video_id}'

        download_dir = f'{LOCAL_DIR}/downloads/{member_id}/{post_id}'
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        ydl_opts = {
            'outtmpl': f'{download_dir}/high.%(ext)s',
            'format': 'worstvideo[height>=1080][vcodec!*=av01]+bestaudio'
        }
        video_ext = self.ydl_download(url, ydl_opts)

        return video_ext

    def ydl_download(self, url, ydl_opts):
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_ext = info_dict['ext']
            ydl.download([url])

        return video_ext
