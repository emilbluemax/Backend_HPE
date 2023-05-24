# amqps://nhvdbbep:iGsHFJV-ZTyrOJElcDt8xHnVSAQLLOzQ@puffin.rmq2.cloudamqp.com/nhvdbbep
# amqps://nhvdbbep:iGsHFJV-ZTyrOJElcDt8xHnVSAQLLOzQ@puffin.rmq2.cloudamqp.com/nhvdbbep
import pika, json

params = pika.URLParameters('amqps://nhvdbbep:iGsHFJV-ZTyrOJElcDt8xHnVSAQLLOzQ@puffin.rmq2.cloudamqp.com/nhvdbbep')

connection = pika.BlockingConnection(params)

channel = connection.channel()

def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)