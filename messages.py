import vk_api
import subprocess
import time
import random

def send_message(bot_token, user_id, message):
    try:
        session = vk_api.VkApi(token=bot_token)
        vk = session.get_api()
        vk.messages.send(user_id=user_id, message=message,random_id=0)
        print(f"Сообщение отправлено от бота с токеном {bot_token} пользователю {user_id}: {message}")
    except vk_api.exceptions.ApiError as error:
        print(f"Ошибка отправки сообщения: {error}")

def authorize_bots():
    subprocess.run(["python", "main.py"])
    time.sleep(15)
if __name__ == "__main__":
    authorize_bots()


    bot_data_list = []
    with open("accounts.txt", "r") as file:
        for line in file:
            login, password, token = line.strip().split(":")
            app_id = "2685278"
            bot_data_list.append({"token": token, "app_id": app_id})

    user_ids = []
    with open("users.txt", "r") as file:
        for line in file:
            user_id = line.strip()
            user_ids.append(user_id)


    messages = []
    with open("messages.txt", "r", encoding="utf-8") as file:
        for line in file:
            message = line.strip()
            messages.append(message)

    for bot_data in bot_data_list:
        user_id = user_ids.pop(0)
        message = random.choice(messages)
        send_message(bot_data["token"], user_id, message)

time.sleep(300)