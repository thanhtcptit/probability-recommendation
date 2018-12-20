import sys
import json

sys.path.append('../..')

from src.utils.path import Path


def read_config(path=Path.CONFIG_FILE):
    with open(path) as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    read_config()
