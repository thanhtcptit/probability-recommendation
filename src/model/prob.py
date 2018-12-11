import pathmagic
import os
import argparse
import shutil
import collections
import sys

from datetime import datetime
from tqdm import tqdm

from src.utils.path import Path


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_path', default=None,
        help='Path to folder that contains products.csv. '
        'Leave at "None" to select the newest folder.')

    return parser.parse_args()


def calc_product_prob(path, products_count, total_product):
    with open(path, 'w') as f:
        for k, v in products_count.items():
            f.write('{},{}\n'.format(k, v / total_product))


def calc_stone_and_quality_prob_given_product(
        stone_prob_path, quality_prob_path, products):
    with open(stone_prob_path, 'w') as sf:
        with open(quality_prob_path, 'w') as qf:
            for prod, stone_quality_list in products.items():
                stones_count = collections.defaultdict(lambda: 0)
                qualities_count = collections.defaultdict(lambda: 0)

                for s, q in stone_quality_list:
                    stones_count[s] += 1
                    qualities_count[q] += 1
                total_count = sum(stones_count.values())

                for stone, stone_count in stones_count.items():
                    sf.write('{},{},{}\n'.format(
                        prod, stone, stone_count / total_count))
                for quality, quality_count in qualities_count.items():
                    qf.write('{},{},{}\n'.format(
                        prod, quality, quality_count / total_count))


def calc_item_prob_given_stone_and_quality(
        item_prob_path, stone_quality_count, total_product):
    with open(item_prob_path, 'w') as f:
        for stone, quality_list in stone_quality_count.items():
            for quality, count in quality_list.items():
                f.write('{},{},{}\n'.format(
                    stone, quality, count / total_product))


def calc_probs(store_probs_dir, store_data_path):
    total_product = 0
    products_count = collections.defaultdict(lambda: 0)
    stone_quality_count = collections.defaultdict(dict)
    products = collections.defaultdict(list)
    with open(os.path.join(store_data_path, 'products.csv')) as f:
        for line in tqdm(f, desc='Product'):
            pid, stone, quality = line.strip().split(',')
            total_product += 1
            products_count[pid] += 1
            products[pid].append([stone, quality])
            if quality not in stone_quality_count[stone]:
                stone_quality_count[stone][quality] = 1
            else:
                stone_quality_count[stone][quality] += 1

    product_prob_path = os.path.join(store_probs_dir, 'product_prob.csv')
    stone_prob_path = os.path.join(store_probs_dir, 'stone_prob.csv')
    quality_prob_path = os.path.join(store_probs_dir, 'quality_prob.csv')
    item_prob_path = os.path.join(store_probs_dir, 'item_prob.csv')

    calc_product_prob(product_prob_path, products_count, total_product)
    calc_stone_and_quality_prob_given_product(
        stone_prob_path, quality_prob_path, products)
    calc_item_prob_given_stone_and_quality(
        item_prob_path, stone_quality_count, total_product)


def calc_probs_process(data_path):
    if data_path is None:
        print('[*] Flag --data_path is None - Choose the newest folder')
        data_path = Path.choose_newest_folder(Path.DATA_DIR)
    print('Data folder: ', data_path)

    folder_date = os.path.split(data_path)[1]
    probs_dir = os.path.join(Path.MODEL_DIR, folder_date)
    if os.path.exists(probs_dir):
        shutil.rmtree(probs_dir)
    os.makedirs(probs_dir)

    print('- Calculate various probs for each store.')
    for store in tqdm(os.listdir(data_path), desc='Store '):
        store_data_path = os.path.join(data_path, store)
        store_probs_dir = os.path.join(probs_dir, store)
        if not os.path.isdir(store_data_path):
            continue
        if not os.path.exists(store_probs_dir):
            os.makedirs(store_probs_dir)
        calc_probs(store_probs_dir, store_data_path)


if __name__ == '__main__':
    args = _parse_args()
    calc_probs_process(args.data_path)
