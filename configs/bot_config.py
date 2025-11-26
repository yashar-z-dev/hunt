import os

class BotConfig:
    def __init__(self):
        self.project_root: str = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        self.TOKEN_FILE: str = os.path.join(self.project_root, "instance", "token.txt")
        self.DB_FILE: str = os.path.join(self.project_root, "instance", "database.db")
        self.SECRET_FILE: str = os.path.join(self.project_root, "instance", "secret.txt")

        self.TOKEN: str = self.loader(self.TOKEN_FILE).strip()
        self.SECRET: str = self.loader(self.SECRET_FILE).strip()
        self.BASE_URL: str = self.get_baseurl()
        self.TIMEOUT: float = 60 # long polling
        self.LIMIT: float = 2 # telegram limit every minute we can send 30 message

        # UI
        self.WHEN_no_auth_replay = "You must subscribe to use this robot."

        self.make_dirctorys()

    def loader(self, file: str) -> str:
        with open(file, "r", encoding="utf-8") as f:
            data = f.read().strip()
        return data

    def get_baseurl(self) -> str:
        return f"https://api.telegram.org/bot{self.TOKEN}"

    def make_dirctorys(self):
        return
        # os.makedirs(os.path.join(self.project_root, "models"), exist_ok=True)
        # os.makedirs(os.path.join(self.project_root, "configs"), exist_ok=True)
