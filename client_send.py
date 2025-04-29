import pika
import json
import random
import time
import uuid

credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('infoexpertise.hopto.org', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='calculsZI_DZ')

OPERATIONS = ['add', 'sub', 'mul', 'div', 'all']

def generate_message():
    n1 = random.randint(1, 100)
    n2 = random.randint(1, 100)
    op = random.choice(OPERATIONS)
    message = {
        'n1': n1,
        'n2': n2,
        'op': op,
        'request_id': str(uuid.uuid4())
    }
    return message

while True:
    message = generate_message()
    channel.basic_publish(exchange='',
                          routing_key='calculs',
                          body=json.dumps(message))
    print(f"Envoyé: {message}")
    time.sleep(random.uniform(2, 5))
