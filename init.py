import vk_api
from vk_api import VkUpload
from consts import token
import json
import zipfile
from os import listdir


def update_json(data, file):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)


# Запускаем первый раз перед запуском бота
# Чтобы загрузить фото в бота, инициализировать json файла
vk_session = vk_api.VkApi(token=token)
upload = VkUpload(vk_session)
data_per = {"id" : {}}
data_mem = {"file_names" : {}}
update_json(data_per, 'persons.json')
update_json(data_mem, 'memes.json')
data_mem = json.load(open('memes.json'))  # json с инфой по мемам

# Можно загрузить локально папку, а можно этим кодом всё выгрузить из архива в котором сразу файлы, а не папка
path_photo = 'photos'
z = zipfile.ZipFile('photos.zip', 'r')
z.extractall('photos')

# Загружаем себе все мемы в скрытый альбом
images = listdir(path_photo)
for img in images:
    upload_image = upload.photo_messages(photos=f'{path_photo}/{img}')[0]
    file_name = 'photo{}_{}_{}'.format(upload_image['owner_id'], upload_image['id'], upload_image['access_key'])
    data_mem["file_names"][file_name] = {'views': 0, 'likes': 0, 'dislikes': 0}

update_json(data_mem, 'memes.json')


