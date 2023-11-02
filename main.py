import vk_api

class VkBot:
    def __init__(self, login, password, token, app_id):
        self.login = login
        self.password = password
        self.token = token
        self.app_id = app_id
        self.session = vk_api.VkApi(app_id=self.app_id, login=self.login, password=self.password, token=self.token)
        self.api = self.session.get_api()

    def auth(self):
        try:
            self.session.auth()
            print(f"Бот в сети: {self.login}.")
        except vk_api.AuthError as error_msg:
            print(f"Ошибка авторизации для аккаунта {self.login}: {error_msg}")

bot_objects = []

if __name__ == "__main__":
    accounts = []

    with open("accounts.txt", "r") as file:
        for line in file:
            login, password, token = line.strip().split(":")
            app_id = "2685278"
            accounts.append({"login": login, "password": password, "token": token, "app_id": app_id})

    for account_data in accounts:
        bot = VkBot(account_data["login"], account_data["password"], account_data["token"], account_data["app_id"])
        bot_objects.append(bot)
        bot.auth()
