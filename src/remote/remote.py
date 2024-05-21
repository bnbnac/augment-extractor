from src.worker.shared import current_processing_info, process_queue, LOCAL_DIR, REMOTE_DIR, STORAGE_SERVER, STORAGE_USER
from src.exception.exception import RequestedQuitException
from src.deleter.deleter import delete_local_directory
import subprocess


def query_rsync(member_id, post_id, start_time_without_colons, end_time_without_colons, result):
    current_processing_info.state = 'sending the result data'
    if current_processing_info.quit_flag == 1:
        delete_local_directory(member_id, current_processing_info.post_id)
        raise RequestedQuitException

    file_name = f"{start_time_without_colons}_{end_time_without_colons}.mp4"
    input_path = f"{LOCAL_DIR}/downloads/{member_id}/{post_id}/{file_name}"
    user = STORAGE_USER
    server = STORAGE_SERVER
    remote_directory = f"{REMOTE_DIR}/{member_id}/{post_id}"
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


def query_remove_remote_directory(member_id, post_id):
    user = STORAGE_USER
    server = STORAGE_SERVER
    remote_directory = f"{REMOTE_DIR}/{member_id}/{post_id}"

    try:
        ssh_cmd = ["ssh", "-p", "22022",
                   f"{user}@{server}", "rm", "-rf", remote_directory]

        subprocess.run(ssh_cmd, check=True)
        print(
            f"Remote directory {remote_directory} and its contents successfully removed.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing remote directory: {e}")


def query_remove_remote_question(member_id, post_id, filename):
    user = STORAGE_USER
    server = STORAGE_SERVER
    remote_directory = f"{REMOTE_DIR}/{member_id}/{post_id}"
    remote_question = f"{remote_directory}/{filename}"

    try:
        ssh_cmd = ["ssh", "-p", "22022",
                   f"{user}@{server}", "rm", remote_question]

        subprocess.run(ssh_cmd, check=True)
        print('the video on the storage REMOVED')
        return 'the video on the storage REMOVED'

    except subprocess.CalledProcessError as e:
        print('Error removing remote directory: {e}')
        return 'unexpected error'
