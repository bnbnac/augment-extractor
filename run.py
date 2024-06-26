from src.app import create_app
import sys
import threading
from src.worker.video_worker import process_video_task
from src.worker.shared import EXTRACTOR_SERVER


app = create_app()


processing_thread = threading.Thread(target=process_video_task)
processing_thread.start()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5050
        
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)