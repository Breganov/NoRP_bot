import os
import sys
import vk_api
import telebot
import configparser
import logging
from telebot.types import InputMediaPhoto

config_path = os.path.join(sys.path[0], 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)
LOGIN = config.get('VK', 'LOGIN')
PASSWORD = config.get('VK', 'PASSWORD')
DOMAIN = config.get('VK', 'DOMAIN')
COUNT = config.get('VK', 'COUNT')
BOT_TOKEN = config.get('Telegram', 'BOT_TOKEN')
CHANNEL = config.get('Telegram', 'CHANNEL')
INCLUDE_LINK = config.getboolean('Settings', 'INCLUDE_LINK')
PREVIEW_LINK = config.getboolean('Settings', 'PREVIEW_LINK')

bot = telebot.TeleBot(BOT_TOKEN)

# Получаем данные из vk.com
def get_data(domain_vk, count_vk):
    vk_session = vk_api.VkApi(LOGIN, PASSWORD)
    vk_session.auth()
    vk = vk_session.get_api()
    # Используем метод wall.get из документации по API vk.com
    response = vk.wall.get(domain=domain_vk, count=count_vk)
    return response

# Проверяем данные по условиям перед отправкой
def check_posts_vk():
    response = get_data(DOMAIN, COUNT)
    response = reversed(response['items'])

    for post in response:

        # Читаем последний извесный id из файла
        id = config.get('Settings', 'LAST_ID')

        # Сравниваем id, пропускаем уже опубликованные
        if int(post['id']) <= int(id):
            continue

        print('------------------------------------------------------------------------------------------------')
        print(post)

        # Текст
        text = post['text']

        # Проверяем есть ли что то прикрепленное к посту
        images = []
        links = []
        attachments = []
        if 'attachments' in post:
            attach = post['attachments']
            for add in attach:
                if add['type'] == 'photo':
                    img = add['photo']
                    images.append(img)
                elif add['type'] == 'audio':
                    # Все аудиозаписи заблокированы везде, кроме оффицальных приложений
                    continue
                elif add['type'] == 'video':
                    video = add['video']
                    if 'player' in video:
                        links.append(video['player'])
                else:
                    for (key, value) in add.items():
                        if key != 'type' and 'url' in value:
                            attachments.append(value['url'])

        if INCLUDE_LINK:
            post_url = "https://vk.com/" + DOMAIN + "?w=wall" + \
                str(post['owner_id']) + '_' + str(post['id'])
            links.insert(0, post_url)
        text = '\n'.join([text] + links)
        send_posts_text(text)

        if len(images) > 0:
            image_urls = list(map(lambda img: max(
                img["sizes"], key=lambda size: size["type"])["url"], images))
            print(image_urls)
            bot.send_media_group(CHANNEL, map(
                lambda url: InputMediaPhoto(url), image_urls))

        # Проверяем есть ли репост другой записи
        if 'copy_history' in post:
            copy_history = post['copy_history']
            copy_history = copy_history[0]
            print('--copy_history--')
            print(copy_history)
            text = copy_history['text']
            send_posts_text(text)

            # Проверяем есть ли у репоста прикрепленное сообщение
            if 'attachments' in copy_history:
                copy_add = copy_history['attachments']
                copy_add = copy_add[0]

                # Если это ссылка
                if copy_add['type'] == 'link':
                    link = copy_add['link']
                    text = link['title']
                    send_posts_text(text)
                    img = link['photo']
                    send_posts_img(img)
                    url = link['url']
                    send_posts_text(url)

                # Если это картинки
                if copy_add['type'] == 'photo':
                    attach = copy_history['attachments']
                    for img in attach:
                        image = img['photo']
                        send_posts_img(image)

        # Записываем id в файл
        config.set('Settings', 'LAST_ID', str(post['id']))
        with open(config_path, "w") as config_file:
            config.write(config_file)

# Текст
def send_posts_text(text):
    if text == '':
        print('no text')
    else:
        # В телеграмме есть ограничения на длину одного сообщения в 4091 символ, разбиваем длинные сообщения на части
        for msg in split(text):
            bot.send_message(CHANNEL, msg, disable_web_page_preview=not PREVIEW_LINK)

def split(text):
    if len(text) >= max_message_length:
        last_index = max(
            map(lambda separator: text.rfind(separator, 0, max_message_length), message_breakers))
        good_part = text[:last_index]
        bad_part = text[last_index + 1:]
        return [good_part] + split(bad_part)
    else:
        return [text]

# Изображения
def send_posts_img(img):
    # Находим картинку с максимальным качеством
    url = max(img["sizes"], key=lambda size: size["type"])["url"]
    bot.send_photo(CHANNEL, url)

if __name__ == '__main__':
    check_posts_vk()