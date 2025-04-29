import pika
import json
import time
import random
import sys

# Vérifier qu'une opération a été donnée en argument
if len(sys.argv) != 2:
    print("Utilisation : python worker.py [add|sub|mul|div]")
    sys.exit(1)

operation_type = sys.argv[1]
if operation_type not in ['add', 'sub', 'mul', 'div']:
    print("Erreur : opération non reconnue. Utiliser add, sub, mul ou div.")
    sys.exit(1)

print(f"[*] Worker démarré pour traiter l'opération : {operation_type.upper()}")

# Connexion à RabbitMQ
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('infoexpertise.hopto.org', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Déclarer les queues
channel.queue_declare(queue='calculsZI_DZ')
channel.queue_declare(queue='calcul_results_ZI_DZ')

def callback(ch, method, properties, body):
    try:
        print("[x] Message reçu :", body)

        data = json.loads(body)

        n1 = data.get('n1')
        n2 = data.get('n2')
        op = data.get('op', 'add')

        if n1 is None or n2 is None:
            print("[!] Erreur : n1 ou n2 manquant.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Si ce worker ne traite pas cette opération, il ignore
        if op != operation_type:
            print(f"[!] Opération ignorée")
            # print(f"[!] Opération {op} ignorée par ce worker {operation_type}.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Simuler un calcul complexe
        wait_time = random.randint(5, 15)
        print(f"[x] {operation_type.upper()} en cours pendant {wait_time} secondes...")
        time.sleep(wait_time)

        # Effectuer le calcul
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
            "result": result
        }

        # Envoyer le résultat dans la queue de résultats
        channel.basic_publish(
            exchange='',
            routing_key='calcul_results_ZI_DZ',
            body=json.dumps(response)
        )

        print(f"[✓] Résultat envoyé : {response}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("[!] Erreur lors du traitement :", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Consommer
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='calculsZI_DZ', on_message_callback=callback)

print(f"[*] En attente de calculs pour opération {operation_type.upper()}...")
channel.start_consuming()
