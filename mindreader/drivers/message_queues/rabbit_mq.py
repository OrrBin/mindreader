import pika

from mindreader.drivers.encoders.pb_encoder import PBEncoder

# docker run -d -p 5672:5672 rabbitmq


class RabbitMQ:
    prefix = 'rabbitmq'

    def __init__(self, host, port):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))

    def publish(self, topic, message):
        connection = self.connection
        channel = connection.channel()
        channel.exchange_declare(exchange=topic, exchange_type='fanout')
        channel.basic_publish(exchange=topic, routing_key='', body=message)
        connection.close()
        print('Message sent to queue')

    def consume(self, topic, callback):
        connection = self.connection
        channel = connection.channel()
        channel.exchange_declare(exchange=topic, exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='snapshot', queue=queue_name)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print('Waiting for messages')
        channel.start_consuming()
