import datetime as dt
from flask import Flask, request
import json
import uuid

from mindreader.drivers.context import Context
from mindreader.drivers.encoders import PBEncoder
from mindreader.drivers.encoders import JSONEncoder
from mindreader.drivers import MessageQueue
from mindreader.objects.snapshot import Snapshot
from mindreader.objects.user import User


serv = Flask(__name__)
message_handler = None
url = None
protocol_encoder = PBEncoder()  # encoder for the client-server protocol
json_encoder = JSONEncoder()  # encoder for the server-parser protocol


def run_server(host, port, publish=None, mq_url=None):
    if publish:
        global message_handler
        message_handler = publish
    else:
        global url
        url = mq_url
    serv.run(host, int(port))


@serv.route('/snapshot', methods=['POST'])
def post_snapshot():
    message_bytes = request.get_data()
    user, snapshot = protocol_encoder.message_decode(message_bytes)  # convert from bytes to pb objects

    color_image_data = snapshot.color_image.data
    depth_image_data = json.dumps(list(snapshot.depth_image.data))

    user, snapshot = _convert_objects_format(user, snapshot)  # convert objects format to a JSON-supported one
    context = Context(user.user_id, snapshot.snapshot_id)
    snapshot.color_image_path = context.save('color_image', color_image_data)
    snapshot.depth_image_path = context.save('depth_image', depth_image_data)

    if message_handler:  # run_server was invoked through API
        message_handler(message_bytes)
        return ""  # return status code 200

    snapshot_md = _generate_snapshot_metadata(user, snapshot)
    snapshot = json_encoder.snapshot_encode(snapshot)
    user = json_encoder.user_encode(user)

    try:
        mq = MessageQueue(url)
        mq.publish('snapshot', snapshot)
        mq.publish('snapshot_md', snapshot_md)
        mq.publish('user', user)
    except ConnectionError:
        raise ConnectionError("Server failure: received a message from client, but couldn't connect to queue")

    return ""


def _generate_snapshot_metadata(user, snapshot):
    return json.dumps({'user_id': user.user_id,
                       'snapshot_id': snapshot.snapshot_id,
                       'timestamp': snapshot.timestamp})


def _convert_objects_format(user, snapshot):  # converts user and snapshot from protobuf format to self-created format
    snapshot_id = str(uuid.uuid4())
    datetime = dt.datetime.fromtimestamp(snapshot.datetime / 1000).strftime('%d/%m/%Y, %H:%M:%S:%f')
    snapshot = Snapshot(user.user_id, snapshot_id, datetime, snapshot.pose, '', snapshot.color_image.width,
                        snapshot.color_image.height, '', snapshot.depth_image.width, snapshot.depth_image.height,
                        snapshot.feelings)
    gender = 'male' if user.gender == 0 else 'female' if user.gender == '1' else 'unknown'
    datetime = dt.datetime.fromtimestamp(user.birthday).strftime('%d/%m/%Y')
    user = User(user.user_id, user.username, datetime, gender)
    return user, snapshot
