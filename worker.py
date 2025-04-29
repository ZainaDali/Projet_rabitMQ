import pika
import json
import time
import random
import sys

if len(sys.argv) != 2:
    print("Utilisation : python worker.py [add|sub|mul|div]")
    sys.exit(1)

operation_type = sys.argv[1]
if operation_type not in ['add', 'sub', 'mul', 'div']:
    print("Erreur : opération non reconnue.")
    sys.exit(1)

print(f"[*] Worker pour : {operation_type}")

credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('infoexpertise.hopto.org', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Exchange et queue spécifiques
channel.exchange_declare(exchange='calculs_exchange', exchange_type='direct')
queue_name = f'calcul_{operation_type}'
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange='calculs_exchange', queue=queue_name, routing_key=operation_type)

# Queue des résultats
channel.queue_declare(queue='calcul_results_ZI_DZ')

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        n1 = data.get('n1')
        n2 = data.get('n2')
        request_id = data.get('request_id')

        wait_time = random.randint(5, 15)
        print(f"[x] {operation_type.upper()} {n1} et {n2}... ({wait_time}s)")
        time.sleep(wait_time)

        if operation_type == 'add':
            result = n1 + n2
        elif operation_type == 'sub':
            result = n1 - n2
        elif operation_type == 'mul':
            result = n1 * n2
        elif operation_type == 'div':
            result = n1 / n2 if n2 != 0 else 'DivisionByZero'

        response = {
            "n1": n1,
            "n2": n2,
            "op": operation_type,
            "result": result,
            "request_id": request_id
        }

        channel.basic_publish(
            exchange='',
            routing_key='calcul_results_ZI_DZ',
            body=json.dumps(response)
        )
        print(f"[✓] Résultat envoyé : {response}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("[!] Erreur:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=callback)
print(f"[*] En attente de messages dans la queue '{queue_name}'...")
channel.start_consuming()

