import pika
import json

# Connexion à RabbitMQ
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('infoexpertise.hopto.org', 5672, '/', credentials)
# parameters = pika.ConnectionParameters('localhost', 5673)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Déclarer la queue des résultats
channel.queue_declare(queue='calcul_results_ZI_DZ')

def callback(ch, method, properties, body):
    print("[x] Résultat brut reçu :", body,flush=True)

    try:
        # Décoder le message JSON
        data = json.loads(body)
        n1 = data.get('n1')
        n2 = data.get('n2')
        op = data.get('op')
        result = data.get('result')

        if n1 is None or n2 is None or op is None or result is None:
            print("[!] Message incomplet reçu :", data,flush=True)
        else:
            if result == 'DivisionByZero':
                print(f"==> {n1} {op} {n2} = Erreur : Division par zéro",flush=True)
            else:
                print(f"==> {n1} {op} {n2} = {result}")
            print("-" * 40)

    except Exception as e:
        print("[!] Erreur lors du décodage du message :", str(e),flush=True)

    # Confirmer que le message a été traité
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consommer la queue des résultats
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='calcul_results_ZI_DZ', on_message_callback=callback)

print("[*] En attente des résultats de calculs...",flush=True)
channel.start_consuming()
