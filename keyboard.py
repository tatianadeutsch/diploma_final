from main import bot
import json


def get_button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


keyboard = {
    "one_time": False,
    "buttons": [
        [get_button('Новый поиск', 'primary')],
        [get_button('Следующая анкета', 'secondary')]
    ]
}


def sender(user_id, text):
    bot.vk.method('messages.send', {'user_id': user_id,
                                    'message': text,
                                    'random_id': 0,
                                    'keyboard': keyboard})


keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))
