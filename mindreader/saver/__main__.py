import click
from . import Saver


@click.group()
def cli():
    pass


@cli.command()
@click.option('-d', '--database', default='mongodb://127.0.0.1:27017')
@click.argument('topic')
@click.argument('path')
def save(database, topic, path):
    try:
        saver = Saver(database)
    except ConnectionError:
        print("Saver error: couldn't connect to database")
        exit(1)

    with open(path, 'r') as f:
        saver.save(topic, f.read())


@cli.command()
@click.argument('db_url')
@click.argument('mq_url')
def run_saver(db_url, mq_url):
    try:
        saver = Saver(db_url)
    except ConnectionError:
        print("Saver error: couldn't connect to database")
        exit(1)

    saver.run_all_savers(mq_url)


if __name__ == '__main__':
    cli(prog_name='saver')
