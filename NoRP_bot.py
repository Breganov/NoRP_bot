import vk_api
import json
import time
import os
import requests
import telegram
from telegram.ext import Updater
from vk_api.longpoll import VkLongPoll

# инициализирую всё, что нужно для бота Телеграма
token = '871642712:AAHyhf9X3FleO9t2g-CEuuFb_3Jq9b7q8Ps'
PORT = int(os.environ.get('PORT', '8443'))
updater = Updater(token)
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=token)
updater.bot.set_webhook("https://infinite-dusk-92685.herokuapp.com/" + token)
updater.idle()
channel_id = '-1001362117188'
pp = telegram.utils.request.Request(proxy_url='https://88.204.154.155:8080')
bot = telegram.Bot(token=token, request=pp)

# инициализирую всё, что нужно для группы
NORP_ID = "114070332"
MY_ID = "614415"
GROUP_TOKEN = "8938e1543970e565e8c61c9fa462ac3444a0d340d037fa7f4eb85ff06730c1531dd364f7c670039beaf92"
connection = {'key':'', 'server':'', 'ts':''}

def getapi(token):
    vk_session = vk_api.VkApi(token=token, api_version=5.95)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    return vk, longpoll

def LongPoll(group_id, key, ts):
    connection = vk.groups.getLongPollServer(group_id=group_id, key=key, ts=ts)
    return connection

vk, longpoll = getapi(GROUP_TOKEN)
connection = LongPoll(NORP_ID, connection['key'], connection['ts'])

bot.send_message("144635221", "I've started working.")

while True:
    data = requests.get('{}?act=a_check&key={}&ts={}&wait=25'.format(connection['server'], connection['key'], connection['ts'])).json()
    if 'failed' not in data:
        if 'updates' in data:
            connection['ts'] = data['ts']
            for update in data['updates']:
                if update['type'] == 'wall_post_new':
                    bot.send_message(channel_id, 'https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))
                    bot.send_message('144635221', 'Новый пост в NoRP: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))

                if update['type'] == 'wall_repost':
                    bot.send_message('144635221','Репост: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))

                if update['type'] == 'wall_reply_delete':
                    bot.send_message('144635221','Удалил: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))

                if update['type'] == 'wall_reply_new':
                    bot.send_message('144635221','Новый комментарий: https://vk.com/wall{}_{}'.format(update['object']['owner_id'], str(update['object']['id'])))
    
    else:
        bot.send_message('144635221','Ошибка: {}'.format(data))
        connection = LongPoll(NORP_ID, connection['key'], connection['ts'])
    time.sleep(25)