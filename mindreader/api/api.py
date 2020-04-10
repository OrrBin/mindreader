import json
import datetime as dt

from flask import Flask, jsonify, send_file
from mindreader.drivers import Database

serv = Flask(__name__)
db = None


def run_api_server(host, port, database_url):
    global db
    db = Database(database_url)
    serv.run(host, int(port))


@serv.route('/users', methods=['GET'])
def get_users():
    users = db.get_users()
    users = [{'user_id': user['user_id'], 'username': user['username']} for user in users]
    return jsonify(users)


@serv.route('/users/<int:user_id>')
def get_user_by_id(user_id):
    user = db.get_user_by_id(user_id)
    return jsonify(user)


@serv.route('/users/<int:user_id>/snapshots')
def get_snapshots_by_user_id(user_id):
    snapshots = db.get_snapshots_by_user_id(user_id)
    snapshots = [{'snapshot_id': snapshot['snapshot_id'], 'date': snapshot['timestamp']}
                 for snapshot in snapshots]
    return jsonify(snapshots)


@serv.route('/users/<int:user_id>/snapshots/<snapshot_id>')
def get_snapshot_by_id(user_id, snapshot_id):
    snapshot = db.get_snapshot_by_id(user_id, snapshot_id)
    results = list(snapshot['results'].keys())
    ret = {'snapshot_id': snapshot['snapshot_id'], 'date': snapshot['timestamp'], 'results': results}
    return jsonify(ret)


@serv.route('/users/<int:user_id>/snapshots/<snapshot_id>/<result_name>')
def get_snapshot_result(user_id, snapshot_id, result_name):
    result = db.get_snapshot_by_id(user_id, snapshot_id)['results'][result_name]
    return jsonify(result)


@serv.route('/users/<int:user_id>/snapshots/<snapshot_id>/<result_name>/data')
def get_snapshot_result_data(user_id, snapshot_id, result_name):
    path = db.get_snapshot_by_id(user_id, snapshot_id)['results'][result_name]['data_path']
    return send_file(path)
