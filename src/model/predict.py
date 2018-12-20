import os
import sys
import argparse
import collections
import numpy as np

from tqdm import tqdm

sys.path.append('../..')

from src.utils.path import Path


NEG_INF = -99999
QUALITY = ['A', 'AA', 'AAA', 'AAAA']


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_path', default=None,
        help='Path to folder which store the probabilities data')

    return parser.parse_args()


def read_line2line(path):
    with open(path) as f:
        data = f.read().strip().split('\n')
    return data


def load_probs_data(model_path):
    products_prob = collections.defaultdict(float)
    products_stone_prob = collections.defaultdict(dict)
    products_quality_prob = collections.defaultdict(dict)
    item_prob = collections.defaultdict(dict)

    with open(os.path.join(model_path, 'product_prob.csv')) as f:
        for line in f:
            prod, prob = line.strip().split(',')
            products_prob[prod] = np.log(float(prob))

    with open(os.path.join(model_path, 'stone_prob.csv')) as f:
        for line in f:
            prod, stone, prob = line.strip().split(',')
            products_stone_prob[prod][stone] = np.log(float(prob))

    with open(os.path.join(model_path, 'quality_prob.csv')) as f:
        for line in f:
            prod, quality, prob = line.strip().split(',')
            products_quality_prob[prod][quality] = np.log(float(prob))

    with open(os.path.join(model_path, 'item_prob.csv')) as f:
        for line in f:
            stone, quality, prob = line.strip().split(',')
            item_prob[stone][quality] = np.log(float(prob))

    return products_prob, products_stone_prob, products_quality_prob, item_prob


def calc_quality_prob(store_model_path, result_file,
                      products_prob, products_stone_prob,
                      products_quality_prob, item_prob, stone_mapping):
    store_id = os.path.split(store_model_path)[1]
    predict_quality_count = collections.defaultdict(lambda: 0)
    with open(result_file, 'a') as f:
        f.write('product_id,store_id,stone,stone_type,quality\n')
        for prod in products_prob.keys():
            for stone in item_prob.keys():
                if stone not in products_stone_prob[prod]:
                    continue
                qualities_prob = {}
                for quality in QUALITY:
                    if quality not in item_prob[stone]:
                        item_prob[stone][quality] = NEG_INF
                    if quality not in products_quality_prob[prod]:
                        products_quality_prob[prod][quality] = NEG_INF

                    qualities_prob[quality] = \
                        item_prob[stone][quality] + \
                        products_stone_prob[prod][stone] + \
                        products_quality_prob[prod][quality] + \
                        products_prob[prod]
                max_quality, _ = max(
                    qualities_prob.items(), key=lambda x: x[1])
                f.write('{},{},{},{},{}\n'.format(
                    prod, store_id, stone,
                    stone_mapping[stone], max_quality))
                predict_quality_count[max_quality] += 1


def calc_quality_process(from_date, output_path=Path.RESULT_FILE):
    if from_date is None:
        print('[*] Flag --from_date is None - Choose the newest folder')
        model_path = Path.choose_newest_folder(Path.MODEL_DIR)
    else:
        model_path = os.path.join(Path.MODEL_DIR, from_date)
    print('Model folder: ', model_path)

    date = os.path.split(model_path)[1]
    data_path = os.path.join(Path.DATA_DIR, date)

    if os.path.exists(output_path):
        os.remove(output_path)

    stone_mapping = collections.defaultdict()
    with open(os.path.join(data_path, 'stone_mapping.csv')) as f:
        for line in f:
            stone, stone_type = line.strip().split(',')
            stone_mapping[stone] = stone_type

    print('- Calculate quality prob prediction for each store.')
    for store in tqdm(os.listdir(model_path), desc='Store '):
        store_model_path = os.path.join(model_path, store)
        if not os.path.exists(store_model_path):
            print('[x] Error: Probs data not found for ', store_model_path)
            exit()

        products_prob, products_stone_prob, \
            products_quality_prob, item_prob = load_probs_data(
                store_model_path)
        calc_quality_prob(
            store_model_path, output_path,
            products_prob, products_stone_prob,
            products_quality_prob, item_prob, stone_mapping)

    print('- DONE. Result file stored in {}'.format(output_path))


if __name__ == '__main__':
    args = _parse_args()
    calc_quality_process(args.from_date)
