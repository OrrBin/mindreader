## server
The server receives snapshots from the client, and is responsible to handle them.
It can also post them to a message queue, to be consumable by the parsers. 

It provides the following functions:
* `run_server`: starts the server, and handles cognition snapshots received from client. It receives the following arguments:
    * `host`: server host, to listen in
    * `port`: server port
    * `publish`: an handler (function) to the snapshots. Each time a snapshot is received, this function will be called
    with the user (of it) and the snapshot
    
    Example usage:    
    ```pycon
    >>> from mindreader.server import run_server
    >>> def print_snapshot(user, snapshot):
    ...     print(f'User: {user}, Snapshot: {snapshot}')
    >>> run_server(host='127.0.0.1', port=8000, publish=print_snapshot)
    # Listening on 127.0.0.1:8000
    ```
  
    It is also consumable by a CLI, where the host and port are optional (default to the shown here), but instead
    of a handler, it receives a path to a message queue, where it posts the user/snapshot data:
    ```sh
    [mindreader] $ python -m mindreader.server -h/--host '127.0.0.1' -p/--port 8000 \
    'rabbitmq://127.0.0.1:5672/'  # The prefix indicates the message queue type
    ... # Listening on 127.0.0.1:8000, passing messages to rabbit mq at 127.0.0.1:5672 
    ```