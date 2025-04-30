import threading
import client_receive

client_receive.set_text_widget(text_requetes)  # text_requetes = zone d’affichage
threading.Thread(target=client_receive.start, daemon=True).start()
