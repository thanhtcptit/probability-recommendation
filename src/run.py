import sys
import os
import argparse

sys.path.append('..')

from src.data.get_data_from_db import get_weekly_data
from src.model.prob import calc_probs_process
from src.model.predict import calc_quality_process
from src.utils.common import read_config
from src.utils.path import Path


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--from_date', default=None,
        help='Set value to None to select today date')

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    config = read_config()
    result_file = os.path.join(Path.PROJECT_ROOT, config['output_path'])

    get_weekly_data(
        from_date=args.from_date,
        mongo_addr=config['mongodb_addr'],
        db_name=config['db_name'],
        collection=config['collection'])
    calc_probs_process(args.from_date)
    calc_quality_process(args.from_date, result_file)
