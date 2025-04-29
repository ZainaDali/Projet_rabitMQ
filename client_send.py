import pika
import json
import random
import time
import uuid

credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('infoexpertise.hopto.org', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Déclarer l'exchange direct
channel.exchange_declare(exchange='calculs_exchange', exchange_type='direct')

OPERATIONS = ['add', 'sub', 'mul', 'div']

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
    channel.basic_publish(
        exchange='calculs_exchange',
        routing_key=message['op'],  # Utilise add/sub/mul/div comme routing key
        body=json.dumps(message)
    )
    print(f"Envoyé: {message}")
    time.sleep(random.uniform(2, 5))
