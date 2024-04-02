# Производитель с шифрованием
import pika
from cryptography.fernet import Fernet

# Генерация или чтение ключа шифрования
try:
    with open('key.key', 'rb') as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open('key.key', 'wb') as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='notifications_exchange', exchange_type='direct')


def send_notification(message, severity):
    message = cipher_suite.encrypt(message.encode())
    channel.basic_publish(exchange='notifications_exchange', routing_key=severity, body=message)
    print("Отправлено зашифрованное сообщение с уровнем: %r" % severity)


send_notification("New order placed", "info")
send_notification("Product on sale", "warning")

connection.close()
