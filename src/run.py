import pathmagic
import argparse

from src.data.get_data_from_db import get_weekly_data
from src.model.prob import calc_probs_process
from src.model.predict import calc_quality_process


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_path', default=None)
    parser.add_argument(
        '--data_path', default=None)
    parser.add_argument(
        '--from_date', default=None)

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    # get_weekly_data(from_date=args.from_date)
    calc_probs_process(args.data_path)
    calc_quality_process(args.model_path)
