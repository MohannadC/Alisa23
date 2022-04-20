from flask import Flask, request
import json
from random import choice
from csv import reader


def get_random_country():
    with open('users.csv', mode='r', encoding='utf-8') as f:
        data = reader(f)
        return choice(list(data)[0])


def start_game():
    global game_in_progress, counter
    game_in_progress = True
    counter = 0


def set_session_storage(user_id, suggests):
    sessionStorage[user_id] = {
        'suggests': suggests
    }


app = Flask(__name__)
countries = {'1521359/72b334a1e03f56b84360': 'Франция', '1533899/c02a5b5c9c0f3ae8908d': 'Россия',
             '1521359/25a2e4cf7a15bc11ee97': 'Испания', '937455/9ce1d6d126956fc1b754': 'Турция',
             '213044/77d21ad83ad3f85df10c': 'Япония', '937455/0d81cf56ccce8ed332df': 'США',
             '213044/7c5e73060219956aca7b': 'Камбоджа', '1540737/e65637265d4b05b895f2': 'Польша',
             '1540737/fad828acfb9c6358c38f': 'Египет', '213044/f7cf26a3047234953875': 'Великобритания',
             '1521359/7e44fb30a4d0e54327e8': 'Куба', '1521359/b22681d266d3be1f339f': 'Греция',
             '937455/c31826f51b0e0d2a9890': 'Италия', '1540737/e79bd2003341cb1f7d56': 'Норвегия',
             '997614/a0cd9427ff7cf9247d76': 'Австрия', '213044/b1413edcf55fec7ff76f': 'Австралия',
             '997614/99ea33abf653a9066367': 'Швеция', '1030494/b6dba31056db9713ccf2': 'Канада',
             '937455/2a7799c2213805c412cc': 'Чехия', '1030494/7b01854e4834e2544141': 'Сингапур',
             '1030494/36ba7798f3a5069ce542': 'Колумбия', '1652229/2cadc2762f267cd29954': 'Индия',
             '1652229/4cf2c2807d02dbffcde1': 'Швейцария', '1540737/5cc83ea3d7876de194da': 'Индонезия',
             }
game_in_progress = False
counter = 0
answer = ''
right_answers = 0
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    return json.dumps(response)


def handle_dialog(req, res):
    global counter, game_in_progress, answer, right_answers, countries
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Хотите сыграть в игру?'
        set_session_storage(user_id, ['Да', 'Нет'])

    elif req['session']['message_id'] == 1:
        if req['request']['original_utterance'].lower() in ['да', 'ок', 'согласен', 'давай']:
            start_game()
            answer = get_random_country()
            res['response']['text'] = ''
            res['response']['card'] = {"type": "BigImage",
                                       "image_id": answer,
                                       "title": "Что за страна?",
                                       }
            set_session_storage(user_id, [])
        else:
            res['response']['text'] = 'Ну нет, так нет.'
            set_session_storage(user_id, ['Давай сыграем'])

    elif req['request']['original_utterance'] == 'Давай сыграем':
        if not game_in_progress:
            start_game()
            answer = get_random_country()
            res['response']['text'] = ''
            res['response']['card'] = {"type": "BigImage",
                                       "image_id": answer,
                                       "title": "Что за страна?",
                                       }
            counter += 1
            set_session_storage(user_id, [])
        else:
            res['response']['text'] = 'Игра уже идёт!'

    elif game_in_progress and req['session']['message_id'] != 1:
        if counter < 4:
            if answer and countries[answer] == req['request']['original_utterance']:
                description = 'Твой предыдущий ответ был верен.'
                right_answers += 1
            else:
                description = f'Твой предыдущий ответ был неверен. Правильный ответ: {countries[answer]}'

            answer = get_random_country()
            res['response']['text'] = ''
            res['response']['card'] = {"type": "BigImage",
                                       "image_id": answer,
                                       "title": "Что за страна?",
                                       "description": description
                                       }
            set_session_storage(user_id, [])
            counter += 1
        else:
            if answer and countries[answer] == req['request']['original_utterance']:
                right_answers += 1
                res['response']['text'] = f'Конец игры, ты угадал {right_answers} из 5 стран.'
            else:
                res['response']['text'] = f'Конец игры, ты угадал {right_answers} из 5 стран.\n' \
                                          f'Твой предыдущий ответ был неверен. Правильный ответ: {countries[answer]}'

            set_session_storage(user_id, ['Давай сыграем'])
            counter = 0
            game_in_progress = False
            right_answers = 0

    else:
        res['response']['text'] = 'Не поняла вас.'

    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': False}
        for suggest in session['suggests'][::]
    ]

    session['suggests'] = session['suggests'][::]
    sessionStorage[user_id] = session

    return suggests


if __name__ == '__main__':
    app.debug = True
    app.run()
