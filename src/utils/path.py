import os
from datetime import datetime


class Path:
    PROJECT_ROOT = os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir)
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    MODEL_DIR = os.path.join(PROJECT_ROOT, 'model')
    SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
    CONFIG_FILE = os.path.join(SRC_DIR, 'config.json')
    RESULT_FILE = os.path.join(DATA_DIR, 'stone-quality-rec.csv')

    def choose_newest_folder(path):
        newest_folder = None
        for folder in os.listdir(path):
            folder_date = datetime.date(datetime.strptime(folder, '%Y-%m-%d'))
            if not newest_folder:
                newest_folder = folder_date
            elif folder_date > newest_folder:
                newest_folder = folder_date
        if not newest_folder:
            print("[x] Error: Can't find any folder in ", path)
            exit(0)
        folder_path = os.path.join(path, str(newest_folder))
        return folder_path
