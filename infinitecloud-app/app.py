import webview
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image
import sys
import os
import requests
from webview import FileDialog
js_ready = False

window = None
def on_loaded():
    global js_ready
    js_ready = True

class Api:
    def select_file(self):
        r = window.create_file_dialog(FileDialog.OPEN)
        return r[0] if r else None

    def start_upload(self, path, password, is_global):
        if isinstance(path, dict):
            path = path.get("filePaths", [None])[0]
            if not path:
                return

        threading.Thread(
            target=upload_file,
            args=(path, password, is_global),
            daemon=True
        ).start()

def upload_file(path, password, is_global):
    with open(path, "rb") as f:
        file_bytes = f.read()

    data = {
        "password": password
    }

    if is_global:
        data["is_global"] = "1"   # Flask böyle algılar

    r = requests.post(
        "https://seninsite.com/infinitecloud/upload",
        data=data,
        files={"file": (os.path.basename(path), file_bytes)}
    )

    window.evaluate_js("setProgress(100)")

def open_window(icon, item):
    window.show()

def exit_app(icon, item):
    icon.stop()
    sys.exit()

def tray():
    image = Image.open("icon.ico")
    menu = Menu(
        MenuItem("Yükleme Penceresini Aç", open_window, default=True),
        MenuItem("Çıkış", exit_app)
    )
    icon = Icon("InfiniteCloud", image, "InfiniteCloud", menu)
    icon.run()

if __name__ == "__main__":
    threading.Thread(target=tray, daemon=True).start()

    window = webview.create_window(
        "InfiniteCloud Upload",
        "ui.html",
        width=400,
        height=420,
        hidden=True,
        js_api=Api(),
        on_top=False
    )

    window.events.loaded += on_loaded

    webview.start()
