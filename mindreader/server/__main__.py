import click
from mindreader.server.server import run_server as run


@click.group()
def cli():
    pass


@cli.command()
@click.option('-h', '--host', default='127.0.0.1', help="Server host")
@click.option('-p', '--port', default='8000', help="Server port")
@click.option('-d', '--data-dir', default='', help="Directory to save data generated by the server into")
@click.argument('mq_url')
def run_server(host, port, data_dir, mq_url):
    try:
        run(host, port, mq_url=mq_url, data_dir=data_dir)
    except Exception as error:
        print(f'Server ERROR: {error}')
        return 1


if __name__ == '__main__':
    cli(prog_name='server')
