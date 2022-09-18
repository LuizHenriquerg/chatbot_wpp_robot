from database import Database
import requests
import json
import time
import re

config = json.loads(open('config.json', 'r').read())
db = Database()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config['token']}",
}
url = f'https://graph.facebook.com/v14.0/{config["id_wpp"]}/messages'

while True:
    print('Verificando se há novas mensagens...')

    cb_messages = list(db.select_col('cb_menssage', 
        {
            'read': False
        }
    ).sort('created_at', -1))

    print(f'{len(cb_messages)} novas mensagens encontradas...')

    for messages in list(cb_messages):
        body = messages['body']

        if messages['type_menssage'] == 'interactive':

            if body['type'] == 'button_reply':
                if str(body['button_reply']['id']) == '1' or str(body['button_reply']['id']) == '2':
                    data = {
                        "messaging_product": "whatsapp",
                        "to": messages['number'],
                        "type": "text",
                        "text": {
                            "body": "Certo! Por favor digite seu CPF para verificar seu cadastro:"
                        }
                    }

                    data = json.dumps(data)
                
                    send = requests.post(url, headers=headers, data=data)

                    db.update('cb_menssage', {'read': True}, {'name': messages['name'], 'number': messages['number'], 'timestamp': messages['timestamp']})
                    continue

                if str(body['button_reply']['id']) == '3':
                    data = {
                        "messaging_product": "whatsapp",
                        "to": messages['number'],
                        "type": "text",
                        "text": {
                            "body": "Certo! Irei comunicar um dos nossos atendentes... Enquanto isso, diga em algumas palavras o que você precisa:"
                        }
                    }

                    data = json.dumps(data)
                
                    send = requests.post(url, headers=headers, data=data)

                    db.update('cb_menssage', {'read': True}, {'name': messages['name'], 'number': messages['number'], 'timestamp': messages['timestamp']})
                    break

        elif messages['type_menssage'] == 'text':
            welcome_message = re.search(r'(ol[a-á])|(oi(e)?)|(hello)', body['body'], flags=re.IGNORECASE)
            cpf_message = re.search(r'(\d{11}|\d{3}\.\d{3}\.\d{3}\-\d{2})', body['body'])

            if welcome_message is not None:
                data = {
                    "messaging_product": "whatsapp",
                    "to": messages['number'],
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": f"Olá, {messages['name']}. Harmony Dentals agradece por entrar em contato. Como podemos lhe ajudar? 😁"
                        },
                        "action": {
                            "buttons": [
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "1",
                                        "title": "Marcar consulta"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "2",
                                        "title": "Remarcar consulta"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "3",
                                        "title": "Falar com atendente" 
                                    }
                                }
                            ] 
                        }
                    }
                }

                data = json.dumps(data)
                
                send = requests.post(url, headers=headers, data=data)
                
                db.update('cb_menssage', {'read': True}, {'name': messages['name'], 'number': messages['number'], 'timestamp': messages['timestamp']})
                break
            
            if cpf_message is not None:
                data = {
                    "messaging_product": "whatsapp",
                    "to": messages['number'],
                    "type": "text",
                    "text": {
                        "body": "Certo! Por favor aguarde enquanto verificamos os dados..."
                    }
                }

                data = json.dumps(data)
            
                send = requests.post(url, headers=headers, data=data)

                db.update('cb_menssage', {'read': True}, {'name': messages['name'], 'number': messages['number'], 'timestamp': messages['timestamp']})
                break
        else:
            print(messages, '84')
    
    time.sleep(5)
