"""Создаёт администратора из методички: Conf2027 / Demo77."""
from config import DB_SETTINGS
from db import Database
from repositories import UserRepository

if __name__ == "__main__":
    repo = UserRepository(Database(DB_SETTINGS))
    if not repo.login_exists("Conf2027"):
        repo.create("Conf2027", "Demo77", "Администратор портала",
                    "8(900)000-00-00", "admin@example.ru", role="admin")
        print("Администратор Conf2027 создан.")
    else:
        print("Администратор Conf2027 уже существует.")
