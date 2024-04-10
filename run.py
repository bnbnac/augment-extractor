from src.app import create_app
import threading
from src.worker.video_worker import process_video_task


app = create_app()


processing_thread = threading.Thread(target=process_video_task)
processing_thread.start()

if __name__ == '__main__':
    app.run(host='192.168.1.11', port=5050, debug=True, use_reloader=False)
