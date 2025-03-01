import json
from typing import List, TypedDict


class usr:
    def __init__(self, user_id: int, send_after_rec: bool) -> None:
        self.user_id = user_id
        self.send_after_rec = send_after_rec

    def toggle_send_after_rec(self):
        self.send_after_rec = not self.send_after_rec
        return self


class db:
    def __init__(self):
        try:
            with open("db.json", "r", encoding="utf-8") as f:
                row_data = json.load(f)
            self.users: List[usr] = []
            for i in row_data:
                user = usr(i["user_id"], i["send_after_rec"])
                self.users.append(user)
        except FileNotFoundError:
            self.users = []
            self.save()

    def save(self):
        class User(TypedDict):
            user_id: int
            send_after_rec: bool

        data: List[User] = []

        for user in self.users:
            data.append(
                {
                    "user_id": user.user_id,
                    "send_after_rec": user.send_after_rec,
                }
            )

        with open("db.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_user(self, user_id: int, send_after_rec: bool):
        self.users.append(user := usr(user_id, send_after_rec))
        self.save()
        return user

    def remove_user(self, user_id: int):
        for user in self.users:
            if user.user_id == user_id:
                self.users.remove(user)
                self.save()
                return

    def find_user(self, user_id: int):
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None
