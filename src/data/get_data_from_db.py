import pathmagic
import sys
import pymongo
import time
import collections
import os
import shutil

from datetime import datetime
from tqdm import tqdm
from calendar import timegm

from src.utils.path import Path


def date2utc(date, ts_format='%Y-%m-%d'):
    return timegm(time.strptime(date, ts_format))


def utc2date(utc):
    return datetime.utcfromtimestamp(float(utc))


def write_collection(path, iter_obj, endl='\n'):
    with open(path, 'w') as f:
        f.write(endl.join(iter_obj))


DAY_IN_SECS = 60 * 60 * 24
TIME_BETWEEN_SESSION = 3600


def connect_mongo(addr='mongodb://reader:reader@192.168.1.131:27017/'):
    try:
        client = pymongo.MongoClient(addr)
        return client
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s" % e)


def get_weekly_data(from_date=None,
                    db_name='countly',
                    collection='select_product_option_quality',
                    period=7):
    client = connect_mongo()
    db = client[db_name]
    coll = db[collection]

    total_instances = 0
    total_valid_instances = 0
    stones = set()
    qualities = set()

    epoch_time = int(time.time()) if not from_date else date2utc(from_date)
    today_curr_secs = epoch_time % DAY_IN_SECS
    today_utc = epoch_time - today_curr_secs
    day_start = today_utc - period * DAY_IN_SECS

    folder_name = str(datetime.date(datetime.now())) \
        if not from_date else from_date
    storage_path = os.path.join(Path.DATA_DIR, folder_name)
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)
    os.makedirs(storage_path)
    chunks_per_day = 2

    store_events = collections.defaultdict(list)
    device_last_events = collections.defaultdict(list)
    stone_mapping = collections.defaultdict()

    print('- Get the lastest 7 days data from MongoDB.')
    with open(os.path.join(
            storage_path, 'get_data_log.txt'), 'w') as f:
        for i in range(chunks_per_day * period):
            day_end = day_start + int((1 / chunks_per_day) * DAY_IN_SECS)
            data = coll.find(
                {'time_stamp': {'$gt': day_start, '$lt': day_end}},
                {'product_id': 1, 'time_stamp': 1, 'device_id': 1,
                    'option': 1, 'current_url': 1, 'store_id': 1}).sort(
                [['time_stamp', 1]])
            num_instances = data.count()
            total_instances += num_instances

            print('{} ({}) - {} ({}):'.format(
                utc2date(day_start), day_start, utc2date(day_end), day_end))
            day_start = day_end
            for i in tqdm(range(num_instances), desc='Instance'):
                instance = data[i]
                option = instance['option'][0]
                if 'quality' not in option:
                    f.write(
                        '[Quality missing] Option: {} - URL: {}\n'.format(
                            option, instance['current_url']))
                    continue
                if 'value_label' not in option:
                    f.write(
                        '[Stone missing] Option: {} - URL: {}\n'.format(
                            option, instance['current_url']))
                    continue

                device_id = instance['device_id']
                if device_id not in device_last_events:
                    device_last_events[device_id] = instance
                    continue
                else:
                    time_window = \
                        instance['time_stamp'] - \
                        device_last_events[device_id]['time_stamp']
                    if time_window < TIME_BETWEEN_SESSION:
                        device_last_events[device_id] = instance
                        continue

                option = device_last_events[device_id]['option'][0]
                if 'option_label' not in option:
                    stone_type = 'null'
                elif option['option_label'] == 'stone/diamonds':
                    stone_type = 'stone1'
                else:
                    stone_type = 'stone2'
                stone_mapping[option['value_label']] = stone_type
                total_valid_instances += 1
                store_events[instance['store_id']].append(
                    [device_last_events[device_id]['product_id'],
                     option['value_label'],
                     option['quality']])
                device_last_events[device_id] = instance

    for device_id, instance in device_last_events.items():
        option = instance['option'][0]
        if 'option_label' not in option:
            stone_type = 'null'
        elif option['option_label'] == 'stone/diamonds':
            stone_type = 'stone1'
        else:
            stone_type = 'stone2'
        stone_mapping[option['value_label']] = stone_type

        total_valid_instances += 1
        store_events[instance['store_id']].append(
            [device_last_events[device_id]['product_id'],
             option['value_label'],
             option['quality']])

    for store, events in store_events.items():
        store_data_path = os.path.join(storage_path, store)
        if not os.path.exists(store_data_path):
            os.makedirs(store_data_path)
        product_data = os.path.join(store_data_path, 'products.csv')
        with open(product_data, 'w') as wf:
            for event in events:
                wf.write('{},{},{}\n'.format(*event))

    with open(os.path.join(storage_path, 'stone_mapping.csv'), 'w') as f:
        for k, v in stone_mapping.items():
            f.write('{},{}\n'.format(k, v))

    print('Total instances: ', total_instances)
    print('Num valid instances: ', total_valid_instances)


if __name__ == '__main__':
    get_weekly_data(from_date='2018-10-30 4:0:55')
