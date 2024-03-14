import shutil
from src.worker.shared import LOCAL_DIR


def delete_local_directory(member_id, post_id):
    path = f'{LOCAL_DIR}/downloads/{member_id}/{post_id}'

    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' successfully deleted.")
    except OSError as e:
        print(f"Error deleting directory '{path}': {e}")
