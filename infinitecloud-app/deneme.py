import webview
import requests
from tkinter import filedialog
import tkinter as tk
import os

UPLOAD_URL = "https://infinitesoft-tr.com/infinitecloud/upload"  # API endpoint

class Api:
    def select_file(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        return file_path

def upload_file(self, password, file_path):
    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f)
            }

            data = {
                "password": password,
                # opsiyonel alanlar:
                # "is_global": "1",
                # "high_lighted": "1"
            }

            r = requests.post(
                "https://infinitesoft-tr.com/infinitecloud/upload",
                files=files,
                data=data,
                timeout=120
            )

        if r.status_code == 200:
            return "✅ Dosya yüklendi"
        else:
            return f"❌ Hata: {r.status_code}"

    except Exception as e:
        return f"❌ {str(e)}"


if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "InfiniteCloud Upload",
        "ui.html",
        js_api=api,
        width=400,
        height=450,
        resizable=False
    )
    webview.start()
