import pickle
import threading
import time
from random import random

from flask import Flask, jsonify, request, session, redirect, url_for
from Dataset import Dataset

api = Flask(__name__)
api.secret_key = 'your-secret-key'

user_data = {}
threads = {}


def load_measurements(user_id):
    try:
        with open(f'measurementsUser{user_id}.pkl', 'rb') as f:
            return pickle.load(f).dataset
    except FileNotFoundError:
        return None

def save_measurements(user_id):
    with open(f'measurementsUser{user_id}.pkl', 'wb') as f:
        pickle.dump(user_data.get(user_id, Dataset), f)


def add_measurements_periodically(user_id):
    dataset = user_data.get(user_id, Dataset())
    while True:
        acc_x = random()
        acc_y = random()
        acc_z = random()
        bvp = random()
        eda = random()
        temp = random()
        dataset.add(acc_x, acc_y, acc_z, bvp, eda, temp)
        time.sleep(2)


@api.route('/measurements/<user_id>', methods=['GET'])
def get_measurements(user_id):
    dataset = user_data.get(user_id, Dataset())
    return jsonify(dataset.to_dict())


@api.route('/login/<user_id>', methods=['GET'])
def login(user_id):
    session['user_id'] = user_id
    loaded_data = load_measurements(user_id)
    dataset = Dataset()

    if loaded_data:
        data_length = len(loaded_data['acc_x'])
        for i in range(data_length):
            dataset.add(
                loaded_data['acc_x'][i],
                loaded_data['acc_y'][i],
                loaded_data['acc_z'][i],
                loaded_data['bvp'][i],
                loaded_data['eda'][i],
                loaded_data['temp'][i]
            )

    user_data[user_id] = dataset

    stop_event = threading.Event()

    threads[user_id] = threading.Thread(target=add_measurements_periodically, args=(user_id,), daemon=True)
    threads[user_id].start()
    return jsonify({"message": f"User {user_id} logged in"})


@api.route('/logout/<user_id>', methods=['GET'])
def logout(user_id):
    save_measurements(user_id)
    session.pop('user_id', None)
    if user_id in threads:
        threads[user_id].stop()
    return jsonify({"message": f"User {user_id} logged out"})


from flask import jsonify, request, session
import numpy as np
import tensorflow as tf
import json

model = tf.keras.models.load_model('lstm_wit_4_classes.keras')

consecutive_timeline = 15


def reshape_data(input_data):
    """
    Reshape the flat data array into samples of timeline_length.
    """
    return np.array(input_data).reshape(1, consecutive_timeline, 1)

label_mapping = {}

with open("label_mapping.json", "r") as file:
    label_mapping = json.load(file)

reverse_mapping = {v: k for k, v in label_mapping.items()}

@api.route('/predict/<user_id>', methods=['GET'])
def get_prediction(user_id):
    dataset = user_data.get(user_id, Dataset())
    dict_dataset = dataset.to_dict()

    acc_x = dict_dataset.get('acc_x')
    acc_y = dict_dataset.get('acc_y')
    acc_z = dict_dataset.get('acc_z')
    bvp = dict_dataset.get('bvp')
    eda = dict_dataset.get('eda')
    temp = dict_dataset.get('temp')
    if not acc_x or len(acc_x) < consecutive_timeline:
        return jsonify({'error': 'Insufficient data for prediction'}), 400

    input_data = [
        reshape_data(acc_x[-consecutive_timeline:]),
        reshape_data(acc_y[-consecutive_timeline:]),
        reshape_data(acc_z[-consecutive_timeline:]),
        reshape_data(bvp[-consecutive_timeline:]),
        reshape_data(eda[-consecutive_timeline:]),
        reshape_data(temp[-consecutive_timeline:]),
    ]

    prediction = model.predict(input_data)
    predicted_class = reverse_mapping[prediction]

    return jsonify({'user_id': user_id, 'prediction': predicted_class})


def auto_save():
    while True:
        time.sleep(60)
        for user_id in user_data:
            save_measurements(user_id)


threading.Thread(target=auto_save, daemon=True).start()

import atexit

atexit.register(lambda: [save_measurements(user_id) for user_id in user_data])

# Start the server
if __name__ == '__main__':
    api.run(debug=True)
