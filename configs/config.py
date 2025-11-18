import os

class Config:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.TOKEN_FILE: str = os.path.join(self.project_root, "instance", "token.txt")
        self.TOKEN: str = self.get_token()
        self.BASE_URL: str = self.get_baseurl()
        self.DB_FILE: str = os.path.join(self.project_root, "instance", "database.db")

        self.DELAY: float = 5
        self.TIMEOUT: float = 1
        self.LIMIT: float = 0.5

        self.make_dirctorys()

    def get_token(self) -> str:
        with open(self.TOKEN_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
        return data

    def get_baseurl(self) -> str:
        return f"https://api.telegram.org/bot{self.TOKEN}"

    def make_dirctorys(self):
        os.makedirs(os.path.join(self.project_root, "models"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "configs"), exist_ok=True)
