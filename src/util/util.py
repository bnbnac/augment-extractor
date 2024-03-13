import shutil


def delete_local_directory(directory, post_id):
    path = f'{directory}/{post_id}'
    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' successfully deleted.")
    except OSError as e:
        print(f"Error deleting directory '{path}': {e}")
