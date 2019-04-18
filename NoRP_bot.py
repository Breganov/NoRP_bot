import vk_api
import json
import time
import requests
from vk_api.longpoll import VkLongPoll
import telebot
from telebot import apihelper

# инициализирую всё, что нужно для бота Телеграма
token = '871642712:AAHyhf9X3FleO9t2g-CEuuFb_3Jq9b7q8Ps'
channel_id = '-1001362117188'
bot = telebot.TeleBot(token)
apihelper.proxy = {'https':'https://88.204.154.155:8080'}

# инициализирую всё, что нужно для группы
NORP_ID = "114070332"
MY_ID = "614415"
APP_ID = "6949282"
SERVICE_TOKEN = "705354bd705354bd705354bd2570395d1f77053705354bd2ce4708acd336b0c624d1868"
GROUP_TOKEN = "8938e1543970e565e8c61c9fa462ac3444a0d340d037fa7f4eb85ff06730c1531dd364f7c670039beaf92"
connection = {'key':'', 'server':'', 'ts':''}

def getapi(token, app_id):
    # поключаемся к VK API
    # token — используемый нами токен: service или group
    # app_id — всегда пока только APP_ID, т.к. другого 
    # приложения пока нет.
    # отдаёт:
    #   vk — содержит готовое API vk_session по данным токенам
    #   longpoll — запрос на долгое ожидание того или иного запроса.
    vk_session = vk_api.VkApi(token=token, app_id=app_id, api_version=5.95)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    return vk, longpoll

def LongPoll(group_id, key, ts):
    connection = vk.groups.getLongPollServer(group_id=group_id, key=key, ts=ts)
    return connection
    
vk, longpoll = getapi(GROUP_TOKEN, APP_ID)
connection = LongPoll(NORP_ID, connection['key'], connection['ts'])

while True:
    data = requests.get('{}?act=a_check&key={}&ts={}&wait=25'.format(connection['server'], connection['key'], connection['ts'])).json()
    connection['ts'] = data['ts']
    if 'failed' not in data:
        if 'updates' in data:
            for update in data['updates']:
                if update['type'] == 'wall_post_new':
                    bot.send_message(channel_id, 'https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))

#                 if update['type'] == 'wall_repost':
#                     print('Репост: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))

#                 if update['type'] == 'wall_reply_delete':
#                     print('Удалил: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))

#                 if update['type'] == 'wall_reply_new':
#                     print('Новый комментарий: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))
    else:
        connection = LongPoll(NORP_ID, connection['key'], connection['ts'])
    time.sleep(25)