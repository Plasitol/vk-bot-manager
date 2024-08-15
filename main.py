import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
import vk_api
from concurrent.futures import ThreadPoolExecutor

class VkBot:
    def __init__(self, login, password, token, app_id):
        self.login = login
        self.password = password
        self.token = token
        self.app_id = app_id
        self.session = vk_api.VkApi(app_id=self.app_id, login=self.login, password=self.password, token=self.token)
        self.api = self.session.get_api()
        self.online = False
        self.active = True
        self.user_ids = []
        self.messages = []

    def auth(self):
        if not self.active:
            return
        try:
            self.session.auth()
            self.online = True
            print(f"Бот в сети: {self.login}.")
        except vk_api.AuthError as error_msg:
            self.online = False
            print(f"Ошибка авторизации для аккаунта {self.login}: {error_msg}")

    def stop(self):
        self.active = False
        self.online = False
        print(f"Бот остановлен: {self.login}.")

    def send_message(self, user_id, message):
        if not self.active:
            return
        try:
            self.api.messages.send(user_id=user_id, message=message, random_id=0)
            print(f"Сообщение от {self.login} отправлено пользователю {user_id}: {message}")
        except vk_api.exceptions.ApiError as error:
            print(f"Ошибка отправки сообщения от {self.login}: {error}")

    def start_sending_messages(self):
        if not self.active:
            return
        for user_id in self.user_ids:
            if not self.active:
                break
            for message in self.messages:
                if not self.active:
                    break
                self.send_message(user_id, message)

class BotManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VkBot Manager")

        self.bot_objects = []
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.frame_bots = tk.Frame(root)
        self.frame_bots.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree_bots = ttk.Treeview(self.frame_bots, columns=("Login", "Status", "Users", "Messages"), show='headings', selectmode="extended")
        self.tree_bots.heading("Login", text="Логин")
        self.tree_bots.heading("Status", text="Статус")
        self.tree_bots.heading("Users", text="Пользователи")
        self.tree_bots.heading("Messages", text="Сообщения")
        self.tree_bots.column("Login", width=150)
        self.tree_bots.column("Status", width=80)
        self.tree_bots.column("Users", width=200)
        self.tree_bots.column("Messages", width=200)
        self.tree_bots.pack(fill=tk.BOTH, expand=True)

        self.btn_load_accounts = tk.Button(root, text="Загрузить accounts.txt", command=self.load_accounts)
        self.btn_load_accounts.pack(pady=5)

        self.btn_load_users = tk.Button(root, text="Загрузить users.txt", command=self.load_users)
        self.btn_load_users.pack(pady=5)

        self.btn_load_messages = tk.Button(root, text="Загрузить messages.txt", command=self.load_messages)
        self.btn_load_messages.pack(pady=5)

        self.text_logs = scrolledtext.ScrolledText(root, height=10)
        self.text_logs.pack(padx=10, pady=10)

        self.accounts_file = None
        self.users_file = None
        self.messages_file = None

    def load_accounts(self):
        self.accounts_file = filedialog.askopenfilename(title="Выберите файл accounts.txt", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if self.accounts_file:
            with open(self.accounts_file, "r") as file:
                accounts = [line.strip().split(":") for line in file]
                for login, password, token in accounts:
                    app_id = "2685278"
                    bot = VkBot(login, password, token, app_id)
                    self.bot_objects.append(bot)
                    self.update_bot_list()
                    self.executor.submit(self.auth_bot, bot)

    def load_users(self):
        self.users_file = filedialog.askopenfilename(title="Выберите файл users.txt", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if self.users_file:
            with open(self.users_file, "r") as file:
                user_ids = [line.strip() for line in file]

                selected_items = self.tree_bots.selection()
                for item in selected_items:
                    bot_index = self.tree_bots.index(item)
                    self.bot_objects[bot_index].user_ids = user_ids
            self.log(f"Загружен файл users.txt для выбранных ботов: {self.users_file}")
            self.update_bot_list()

    def load_messages(self):
        self.messages_file = filedialog.askopenfilename(title="Выберите файл messages.txt", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if self.messages_file:
            with open(self.messages_file, "r", encoding="utf-8") as file:
                messages = [line.strip() for line in file]

                selected_items = self.tree_bots.selection()
                for item in selected_items:
                    bot_index = self.tree_bots.index(item)
                    self.bot_objects[bot_index].messages = messages
            self.log(f"Загружен файл messages.txt для выбранных ботов: {self.messages_file}")
            self.update_bot_list()

    def update_bot_list(self):
        for i in self.tree_bots.get_children():
            self.tree_bots.delete(i)
        for bot in self.bot_objects:
            status_color = "green" if bot.online else "red"
            users = ", ".join(bot.user_ids[:3]) + "..." if len(bot.user_ids) > 3 else ", ".join(bot.user_ids)
            messages = ", ".join(bot.messages[:3]) + "..." if len(bot.messages) > 3 else ", ".join(bot.messages)
            self.tree_bots.insert("", tk.END, values=(bot.login, "В сети" if bot.online else "Не в сети", users, messages), tags=(status_color,))
        self.tree_bots.tag_configure('green', foreground='green')
        self.tree_bots.tag_configure('red', foreground='red')

    def auth_bot(self, bot):
        bot.auth()
        self.update_bot_list()
        self.log(f"Авторизация бота: {bot.login}")
        self.executor.submit(self.start_sending_messages, bot)

    def start_sending_messages(self, bot):
        bot.start_sending_messages()

    def stop_bot(self, bot):
        bot.stop()
        self.update_bot_list()
        self.log(f"Бот остановлен: {bot.login}")

    def log(self, message):
        self.text_logs.insert(tk.END, message + "\n")
        self.text_logs.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BotManagerApp(root)
    root.mainloop()
