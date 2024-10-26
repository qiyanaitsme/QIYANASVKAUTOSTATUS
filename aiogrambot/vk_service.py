import vk_api
from datetime import datetime

def vk_auth(token):
    try:
        vk_session = vk_api.VkApi(token=token)
        return vk_session.get_api()
    except vk_api.AuthError:
        return None

async def create_status(vk, template_number):
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d.%m.%Y")

    try:
        user_id = vk.users.get()[0]['id']
        photos = vk.photos.get(owner_id=user_id, album_id='profile', rev=1, count=1)
        avatar_likes = vk.likes.getList(type='photo', owner_id=user_id, item_id=photos['items'][0]['id'])['count'] if photos['items'] else 0
        dialogs_count = vk.messages.getConversations()['count']
        unread_count = vk.messages.getConversations(filter='unread')['count']
        online_friends = len(vk.friends.getOnline())
        total_friends = vk.friends.get()['count']
        followers_count = vk.users.getFollowers()['count']
        blacklist_count = vk.account.getBanned()['count']

        conversations = vk.messages.getConversations(count=1)
        last_message = conversations['items'][0]['last_message']['text'][:20] if conversations['items'] else "Нет сообщений"

        templates = [
            f"📆 {current_date} | 💌 На аве: {avatar_likes} ❤ | 🍰 Вечный Онлайн 🍰 | ✉ Диалогов {dialogs_count} | 📨 Непрочитанных {unread_count}",
            f"⏳ Время: {current_time} | 💌 На аве: {avatar_likes} ❤ | 📆 Дата:{current_date} |",
            f"•⌛{current_time}(😒) | Друзей онлайн✔: {online_friends}| На аве: {avatar_likes}❤ | 💬Диалогов: {dialogs_count} | Последний 💌 с: {last_message} | ⛔ В чс: {blacklist_count} | Day: {datetime.now().day} 😳•",
            f"• ⌛ {current_time} 😃 | На аве: {avatar_likes} ❤ | 💬 Непрочитанных: {unread_count} | Последний 💌 с: {last_message} | Day: {datetime.now().day} 😃 | 😃 •",
            f"🔥Вечный онлайн🔥 | На аве: {avatar_likes} ❤ | 💬Диалогов: {dialogs_count} | ✘Online friends: {online_friends} | ⚡My followers: {followers_count} ✔",
            f"|⌛|{current_time}(😻) Аватар: {avatar_likes}❤ |📅| {current_date}(😘)\n(😘) | Онлайн: {online_friends} из {total_friends} | ⛔ В чс: {blacklist_count} | (😻)"
        ]

        status = f"{templates[template_number - 1]} | Created by QIYANA"
        vk.status.set(text=status)
        return status
    except Exception as e:
        print(f"Error updating status: {e}")
        return None
