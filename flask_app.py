import vk_api
import pandas as pd

from settings import *
from random import choice
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from flask import Flask, request, json

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Здесь ничего нет.'


# Вместо any_difficult_name лучше придумать какое-то сложное название, чтобы никто не знал, куда отправляюся запросы из группы в ВК
@app.route('/any_difficult_name', methods=['POST'])
def processing():

    #Распаковываем json из пришедшего POST-запроса
    data = request.get_json(force=True, silent=True)

    #Вконтакте в своих запросах всегда отправляет поле типа
    if 'type' not in data.keys():
        return 'not vk'

    if data['type'] == 'confirmation':
        return confirmation_token

    elif data['type'] == 'message_new' and data['object']['text'] in ['Начать', 'начать']:
        user_id = data['object']['from_id']

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Получить ссылку на анкету', color=VkKeyboardColor.POSITIVE)

        vk.messages.send(
                keyboard = keyboard.get_keyboard(),
                random_id=get_random_id(),
                user_id=user_id,
                message='''Вас приветствует лаборатория поведенческой нейродинамики СПбГУ!\n\nВ этом исследовании могу принять участие только лица, не участвовашие ранее в экспериментах лаборатории.\n\nПо кнопке ниже Вы можете получить уникальную ссылку на форму участника. Нажимая на неё, Вы подтверждаете, что ранее не участвовали в наших исследованиях.'''
            )

        return 'ok'

    elif data['type'] == 'message_new' and data['object']['text'] == 'Получить ссылку на анкету':
        user_id = str(data['object']['from_id'])
        has_link = False

        links = {
                 'link_1': set(),
                 'link_2': set(),
                 'link_3': set(),
                 'link_4': set(),
                 'link_5': set()
                }

        for line in pd.read_csv('./data.csv', sep=';', index_col='ID').iterrows():
            ind = str(list(line)[0])
            link = list(line)[1][0]
            links[link].add(ind)
            if user_id == ind:
                has_link = True

        if has_link:
            vk.messages.send(
                random_id=get_random_id(),
                user_id=user_id,
                message='Вы уже получили ссылку, спасибо за интерес к участию в экспериментах :)'
            )

        else:
            key = get_random(user_id, links)
            vk.messages.send(
                random_id=get_random_id(),
                user_id=user_id,
                message='Вот ваша ссылка!\n\n' + key
            )
            with open('./data.csv', 'a', encoding='utf8') as ouf:
                ouf.write('\n{};{}'.format(user_id, key))

        return 'ok'

    return 'ok'

def get_random(user_id, links):
    counts = {key : len(value) for key, value in links.items()}
    keys = []
    minimum = min(counts.values())
    for key, value in counts.items():
        if minimum == value:
            keys.append(key)
    res = choice(keys)
    links[res].add(user_id)
    return res
