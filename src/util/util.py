import shutil


def delete_local_directory(directory, member_id, post_id):
    path = f'{member_id}/{directory}/{post_id}'
    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' successfully deleted.")
    except OSError as e:
        print(f"Error deleting directory '{path}': {e}")
