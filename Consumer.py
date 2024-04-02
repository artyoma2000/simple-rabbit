# Потребитель с расшифровкой
import pika
from cryptography.fernet import Fernet

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='notifications_exchange', exchange_type='direct')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='notifications_exchange', queue=queue_name, routing_key='info')
channel.queue_bind(exchange='notifications_exchange', queue=queue_name, routing_key='warning')

# Чтение ключа шифрования из файла
with open('key.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)


def decrypt_message(encrypted_message):
    try:
        decrypted_message = cipher_suite.decrypt(encrypted_message)
        return decrypted_message.decode()
    except Exception as e:
        print("Ошибка при расшифровке сообщения:", e)
        return None


def callback(ch, method, properties, body):
    decrypted_message = decrypt_message(body)
    if decrypted_message:
        print("Получено расшифрованное сообщение с уровнем:  %r" % method.routing_key)
        print("Сообщение: %r" % decrypted_message)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print('Ожидание зашифрованных сообщений. Чтобы выйти, нажмите CTRL+C')
channel.start_consuming()
