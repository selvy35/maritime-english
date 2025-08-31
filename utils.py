import threading, time, os

def delete_file_later(filepath, delay=10):
    def _delete():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
    threading.Thread(target=_delete, daemon=True).start()