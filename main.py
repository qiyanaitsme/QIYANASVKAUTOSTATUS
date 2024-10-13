import vk_api
import time
from datetime import datetime

def vk_auth(token):
    try:
        vk_session = vk_api.VkApi(token=token)
        return vk_session.get_api()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return None

def get_avatar_likes(vk):
    try:
        user_id = vk.users.get()[0]['id']
        photos = vk.photos.get(owner_id=user_id, album_id='profile', rev=1, count=1)
        if photos['items']:
            photo_id = photos['items'][0]['id']
            likes = vk.likes.getList(type='photo', owner_id=user_id, item_id=photo_id)
            return likes['count']
    except Exception as e:
        print(f"Ошибка при получении лайков аватара: {e}")
    return 0

def get_dialogs_count(vk):
    try:
        return vk.messages.getConversations()['count']
    except Exception as e:
        print(f"Ошибка при получении количества диалогов: {e}")
    return 0

def get_unread_count(vk):
    try:
        return vk.messages.getConversations(filter='unread')['count']
    except Exception as e:
        print(f"Ошибка при получении количества непрочитанных: {e}")
    return 0

def get_online_friends(vk):
    try:
        return len(vk.friends.getOnline())
    except Exception as e:
        print(f"Ошибка при получении количества друзей онлайн: {e}")
    return 0

def get_last_message(vk):
    try:
        conversations = vk.messages.getConversations(count=1)
        if conversations['items']:
            return conversations['items'][0]['last_message']['text'][:20]
    except Exception as e:
        print(f"Ошибка при получении последнего сообщения: {e}")
    return "Нет сообщений"

def get_blacklist_count(vk):
    try:
        return vk.account.getBanned()['count']
    except Exception as e:
        print(f"Ошибка при получении количества в ЧС: {e}")
    return 0

def get_followers_count(vk):
    try:
        return vk.users.getFollowers()['count']
    except Exception as e:
        print(f"Ошибка при получении количества подписчиков: {e}")
    return 0


def create_status(vk, template_number):
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d.%m.%Y")
    avatar_likes = get_avatar_likes(vk)
    dialogs_count = get_dialogs_count(vk)
    unread_count = get_unread_count(vk)
    online_friends = get_online_friends(vk)
    last_message = get_last_message(vk)
    blacklist_count = get_blacklist_count(vk)
    followers_count = get_followers_count(vk)

    templates = [
        f"📆 {current_date} | 💌 На аве: {avatar_likes} ❤ | 🍰 Вечный Онлайн 🍰 | ✉ Диалогов {dialogs_count} | 📨 Непрочитанных {unread_count}",
        f"⏳ Время: {current_time} | 💌 На аве: {avatar_likes} ❤ | 📆 Дата:{current_date} |",
        f"•⌛{current_time}(😒) | Друзей онлайн✔: {online_friends}| На аве: {avatar_likes}❤ | 💬Диалогов: {dialogs_count} | Последний 💌 с: {last_message} | ⛔ В чс: {blacklist_count} | Day: {datetime.now().day} 😳•",
        f"• ⌛ {current_time} 😃 | На аве: {avatar_likes} ❤ | 💬 Непрочитанных: {unread_count} | Последний 💌 с: {last_message} | Day: {datetime.now().day} 😃 | 😃 •",
        f"🔥Вечный онлайн🔥 | На аве: {avatar_likes} ❤ | 💬Диалогов: {dialogs_count} | ✘Online friends: {online_friends} | ⚡My followers: {followers_count} ✔",
        f"|⌛|{current_time}(😻) Аватар: {avatar_likes}❤ |📅| {current_date}(😘)\n(😘) | Онлайн: {online_friends} из {vk.friends.get()['count']} | ⛔ В чс: {blacklist_count} | (😻)"
    ]

    status = templates[template_number - 1]
    return f"{status} | Created by QIYANA"


def update_status(vk, status):
    try:
        vk.status.set(text=status)
        print(f"Статус обновлен: {status}")
    except Exception as e:
        print(f"Ошибка при обновлении статуса: {e}")


def main():
    token = 'ТУТ ТОКЕН'
    vk = vk_auth(token)
    if not vk:
        return

    while True:
        print("\nВыберите шаблон статуса (1-6) или 0 для выхода:")
        for i in range(6):
            print(f"{i + 1}. Шаблон {i + 1}")

        choice = input("Ваш выбор: ")
        if choice == '0':
            print("Выход из программы.")
            break

        try:
            template_number = int(choice)
            if 1 <= template_number <= 6:
                status = create_status(vk, template_number)
                update_status(vk, status)
                print(f"Статус будет обновляться каждую минуту. Нажмите Ctrl+C для остановки.")

                try:
                    while True:
                        time.sleep(60)
                        status = create_status(vk, template_number)
                        update_status(vk, status)
                except KeyboardInterrupt:
                    print("\nОбновление статуса остановлено.")
            else:
                print("Неверный выбор. Пожалуйста, выберите число от 1 до 6.")
        except ValueError:
            print("Неверный ввод. Пожалуйста, введите число.")


if __name__ == "__main__":
    main()
