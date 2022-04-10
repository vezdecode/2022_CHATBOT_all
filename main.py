from consts import token
from random import choice
import json


# Для функционирования бота
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload

vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)
upload = VkUpload(vk_session)

data_per = json.load(open("persons.json"))  # json с инфой по пользователям
data_mem = json.load(open("memes.json"))  # json с инфой по мемам
attachments = list(data_mem["file_names"].keys())


# Функция создания кнопок
def get_but(type, text, color):
    return {
        "action": {
            "type": f"{type}",
            "payload": "",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


# Различные настройки клавиатуры
keyboards = {
    "stand": {"btn": [[get_but("text", "Мем😄", "positive"), get_but("text", "Статистика📈", "primary")],
                      [get_but("text", "Вопросы❔", "secondary")]],
              "inline": False},
    "quess": {"btn": [[get_but("text", "Вопросы❔", "primary")]],
              "inline": True},
    "memes": {"btn": [[get_but("text",  "👍", "positive"), get_but("text", "👎", "negative")],
                      [get_but("text", "Не хочу", "secondary")]],
              "inline": True},
    "stat": {"btn" : [[get_but("text", "Личная", "primary"), get_but("text", "Глобальная", "primary")],
                       [get_but("text", "Топ 9", "primary")]],
             "inline": True},
    "top": {"btn": [[get_but("text", "Да!", "positive"), get_but("text", "Не, всё", "negative")]],
            "inline": True}
}

# Отдельный словарь для вопросов
questions = {
    1: {"ques": "Как тебе Вездекод?",
        "btn": [[get_but("text", "Просто супер!😇", "positive"), get_but("text", "Ну такое...😑", "negative")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "Хорошо, тогда следующий вопрос",
        "inline": False},
    2: {"ques": "А ты помнишь что такое Вездекод?",
        "btn": [[get_but("text", "Хакатон!👨‍💻", "positive"), get_but("text", "Марафон!!🏃‍♂️", "secondary")],
                [get_but("text", "Ну, конкурс...🌚", "secondary")], [get_but("text", "Остановиться", "secondary")]],
        "ans": "Допустим ты не попался на уловку... Давай дальше",
        "inline": True},
    3: {"ques": "Сколько категорий сделала твоя команда?",
        "btn": [[get_but("text", "7-8🔥", "primary"), get_but("text", "5-6😎", "primary")],
                [get_but("text", "3-4✊", "primary"), get_but("text", "1-2💪", "primary")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "Вы большие молодцы!",
        "inline": True},
    4: {"ques": "Какое место хотите занять?",
        "btn": [[get_but("text", "1, а как иначе?!", "positive")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "Хороший настрой!",
        "inline": False},
    5: {"ques": "Что купишь у нас в магазине?",
        "btn": [[get_but("text", "Новое худи!😍", "positive"), get_but("text", "Свитшот!🤩", "positive")],
                [get_but("text", "Игрушку!😇", "positive"), get_but("text", "Конфет!🍬", "positive")],
                [get_but("text", "Блокноты!📘", "positive"), get_but("text", "Ревью резюме!📃", "positive")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "Отлично, надеюсь у тебя будет много баллов, чтобы ты купил всё!!",
        "inline": True},
    6: {"ques": "Участвовал в наших играх?",
        "btn": [[get_but("text", "Да, мне понравилось!", "positive"), get_but("text", "Не зашло...", "negative")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "Мы постараемся делать их ещё круче!",
        "inline": False},
    7: {"ques": "Где бы хотели провести финал?",
        "btn": [[get_but("text", "Москва", "primary"), get_but("text", "Питер", "primary")],
                [get_but("text", "Челябинск😎", "secondary")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "Круто, учту! Летсгоу дальше",
        "inline": True},
    8: {"ques": "Любишь ботов?)",
        "btn": [[get_but("text", "Обожаю❤️", "positive"), get_but("text", "Конечно💞", "positive")],
                [get_but("text", "Это кто?😢", "negative")],
                [get_but("text", "Остановиться", "secondary")]],
        "ans": "💓💓💓",
        "inline": False},
}

# Обновление json файла
def update_json(data, file):
    with open(file, "w") as outfile:
        json.dump(data, outfile)


# Для работы с файлом json пользователей
def add_new_user(id):
    id = str(id)
    data_per["id"][id] = {"status": "wait", "n_que": 0,"top": 1, "memes": [], "likes": 0, "dislikes": 0}
    update_json(data_per, "persons.json")


def set_val(id, key, val):
    id = str(id)
    if key == "memes":
        if val == []:
            data_per["id"][id][key] = val
        else:
            data_per["id"][id][key].append(val)
    elif key in ["likes", "dislikes"]:
        data_per["id"][id][key] += 1
    else:
        data_per["id"][id][key] = val
    update_json(data_per, "persons.json")


def return_val(id, key):
    id = str(id)
    return data_per["id"][id][key]


# Функция для оценки мема
def rate_meme(id, file, type):
    data_mem["file_names"][file][type] += 1
    update_json(data_mem, "memes.json")


# Отправка сообщения
def send_msg(id, text, btns, inline):
    kb = {
        "one_time": False,
        "buttons": btns,
        "inline": inline
    }
    kb = json.dumps(kb, ensure_ascii=False).encode("utf-8")
    kb = str(kb.decode("utf-8"))
    vk_session.method("messages.send", {"user_id": id, "message": text, "random_id": 0, "keyboard": kb})


# Отравка мема
def send_meme(id):
    memes = return_val(id, "memes")
    if len(memes) == len(attachments):
        send_msg(int(id), "Ты просмотрел все мемы!😳 \n "
                          "Так что я обновлю тебе список, смотри снова. \n Лайки и дизлайки твою запомню, "
                          "так что побей рекорд и залайкай больше всех!", \
                 keyboards["stand"]["btn"], keyboards["stand"]["inline"])
        set_val(id, "memes", [])
    else:
        cc = choice(attachments)
        while True:
            if cc in memes:
                cc = choice(attachments)
            else:
                break


        vk_session.method("messages.send", {"user_id": id, "random_id": 0, "message": "Лови!", "attachment": cc})
        send_msg(id, "Оцени мем, пожалуйста!", keyboards["memes"]["btn"], keyboards["memes"]["inline"])
        data_mem["file_names"][cc]["views"] += 1
        update_json(data_mem, "memes.json")
        set_val(id, "memes", cc)
        set_val(id, "status", "mem")



print("bot is active")
# Начало работы бота
for event in longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text.lower()
        id = event.user_id
        if str(id) not in data_per["id"]:
            add_new_user(id)
        status = return_val(id, "status")
        # Будем отслеживать само сообщение и статус пользователя из json
        # По ним будем смотреть, что боту ответить
        if "привет" in msg or "здравствуйте" in msg:
            send_msg(id, "Привет, Вездекодерам! \n Есть пара интересных вопросов для тебя, нажми кнопку снизу или "
                         "напиши \"Вопросы\"", keyboards["quess"]["btn"], keyboards["quess"]["inline"])
            send_msg(id, "А так у меня ещё мемы и статистика по ним есть)", keyboards["stand"]["btn"],
                     keyboards["stand"]["inline"])
        elif "пока" in msg or "до свидание" in msg:
            send_msg(id, "Пока, Вездекодерам!", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
        elif msg == "вопросы❔" or msg == "вопросы":
            set_val(id, "status", "ques")
            set_val(id, "n_que", 1)
            n_que = return_val(id, "n_que")
            send_msg(id, "Вопросов всего 8, они очень интересные!", [], False)
            send_msg(id, questions[n_que]["ques"], questions[n_que]["btn"], questions[n_que]["inline"])
        elif status == "ques" and msg == "остановиться":
            send_msg(id, "Спасибо, что поотвечал!", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
            set_val(id, "n_que", 0)
            set_val(id, "status", "wait")
        elif status == "ques":
            n_que = return_val(id, "n_que")
            send_msg(id, questions[n_que]["ans"], [], False)
            set_val(id, "n_que", n_que + 1)
            n_que = return_val(id, "n_que")
            if n_que > 8:
                send_msg(id, "Спасибо, ты ответил на все вопросы!", keyboards["stand"]["btn"],
                         keyboards["stand"]["inline"])
                set_val(id, "n_que", 0)
                set_val(id, "status", "wait")
            else:
                send_msg(id, questions[n_que]["ques"], questions[n_que]["btn"], questions[n_que]["inline"])
        elif status != "mem" and ("мем" in msg or msg == "Мем😄"):
            send_meme(id)
        elif status == "mem" and msg in ["👍", "👎"]:
            last_meme = return_val(id, "memes")[-1]
            if msg == "👍":
                rate_meme(id, last_meme, "likes")
                set_val(id, "likes", last_meme)
            else:
                rate_meme(id, last_meme, "dislikes")
                set_val(id, "dislikes", last_meme)
            send_msg(id, "Спасибо за твою оценку! Напиши \"Мем\" или нажми на кнопку снизу, если хочешь ещё мем", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
            set_val(id, "status", "wait")
        elif status == "mem" and msg == "не хочу":
            send_msg(id, "Ну ладно, можешь посмотреть статистику", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
            set_val(id, "status", "wait")
        elif status == "mem":
            send_msg(id, "Оцени мем, пожалуйста!", keyboards["memes"]["btn"], keyboards["memes"]["inline"])
        elif msg == "Статистика📈" or "статистика" in msg:
            send_msg(id, "Какую статистику хочешь?", keyboards["stat"]["btn"], keyboards["stat"]["inline"])
            set_val(id, "status", "stat")
        elif status == "stat":
            if msg == "личная":
                likes = return_val(id, "likes")
                dislikes = return_val(id, "dislikes")
                send_msg(id, f"Твоё количество лайков❤️: {likes} \n Твоё количество дизлайков😞: {dislikes}",
                         keyboards["stand"]["btn"], keyboards["stand"]["inline"])
                set_val(id, "status", "wait")
            elif msg == "глобальная":
                views = sum([data_mem["file_names"][k]["views"] for k in data_mem["file_names"].keys()])
                likes = sum([data_mem["file_names"][k]["likes"] for k in data_mem["file_names"].keys()])
                dislikes = sum([data_mem["file_names"][k]["dislikes"] for k in data_mem["file_names"].keys()])
                send_msg(id, f"Сколько всего просмотров👀: {views}\n"
                             f"Количество всех лайков❤️: {likes}\n"
                             f"Количество всех дизлайков😞: {dislikes}",
                         keyboards["stand"]["btn"], keyboards["stand"]["inline"])
                set_val(id, "status", "wait")
            elif msg == "топ 9":
                data_mem_items = list(data_mem["file_names"].items())
                data_mem_items.sort(key = lambda x: x[1]["likes"], reverse=True)
                top = [i[0] for i in data_mem_items[:9]]
                top_v = return_val(id, "top")
                send_msg(id, "Топ 9 самых смешных мемов😂", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
                vk_session.method("messages.send", {"user_id": id, "random_id": 0, "message": f"{top_v} место", "attachment": top[top_v-1]})
                send_msg(id, "Продолжаем?", keyboards["top"]["btn"], keyboards["top"]["inline"])
                set_val(id, "status", "top")
            else:
                send_msg(id, "Я тебя не понял...", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
                set_val(id, "status", "wait")
        elif status == "top" and (msg == "не, всё" or "не" in msg):
            send_msg(id, "Вот такой вот топ!", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
            set_val(id, "status", "wait")
            set_val(id, "top", 1)
        elif status == "top":
            data_mem_items = list(data_mem["file_names"].items())
            data_mem_items.sort(key = lambda x: x[1]["likes"], reverse=True)
            top = [i[0] for i in data_mem_items[:9]]
            top_v = return_val(id, "top")
            top_v += 1
            vk_session.method("messages.send", {"user_id": id, "random_id": 0, "message": f"{top_v} место", "attachment": top[top_v-1]})
            send_msg(id, "Продолжаем?", keyboards["top"]["btn"], keyboards["top"]["inline"])
            set_val(id, "top", top_v)
        else:
            send_msg(id, "Мои функции снизу!", keyboards["stand"]["btn"], keyboards["stand"]["inline"])
