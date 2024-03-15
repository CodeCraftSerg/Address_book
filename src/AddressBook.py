from abc import ABC, abstractmethod
from datetime import datetime as dt, timedelta
from collections import UserList
import pickle
from .validate import *
import os

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[0;33m"
BLUE = "\033[94m"
RESET = "\033[0m"


class Logger:
    def log(self, message):
        current_time = dt.strftime(dt.now(), "%H:%M:%S")
        log_message = f"[{current_time}] {message}"
        log_path = os.path.join("src", "logs.txt")
        with open(log_path, "a") as file:
            file.write(f"{log_message}\n")


class DataStorage(ABC):
    @abstractmethod
    def save(self, data, file_path):
        pass

    @abstractmethod
    def load(self, file_path):
        pass


class PickleStorage(DataStorage):
    def save(self, data, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(data, file)

    def load(self, file_path):
        if os.path.exists(file_path) and os.stat(file_path).st_size != 0:
            with open(file_path, "rb") as file:
                return pickle.load(file)
        return []


class AddressBook(UserList, Logger):
    def __init__(self, storage: DataStorage):
        super().__init__()
        self.storage = storage
        self.counter = -1

    def add(self, record):
        account = {
            "name": record.name,
            "country": record.country,
            "phones": record.phones,
            "birthday": record.birthday,
            "email": record.email,
            "note": record.note,
            "tags": record.tags,
        }
        self.data.append(account)
        self.log(f"Контакт {record.name} було додано.")

    def save(self, file_name):
        file_path = os.path.join("src", file_name + ".bin")
        self.storage.save(self.data, file_path)
        self.log("Книгу контактів збережено!")

    def load(self, file_name):
        file_path = os.path.join("src", file_name + ".bin")
        self.data = self.storage.load(file_path)
        if self.data:
            self.log("Книгу контактів завантажено!")
        else:
            self.log("Книгу контактів створено!")
        return self.data

    def save(self, file_name):
        file_path = os.path.join("src", file_name + ".bin")
        self.storage.save(self.data, file_path)
        self.log("Книгу контактів збережено!")

    def load(self, file_name):
        file_path = os.path.join("src", file_name + ".bin")
        self.data = self.storage.load(file_path)
        if self.data:
            self.log("Книгу контактів завантажено!")
        else:
            self.log("Книгу контактів створено!")
        return self.data

    def search_by_tags(self, pattern):
        results = []
        for record in self.data:
            if any(tag.lower() == pattern.lower() for tag in record.get("tags", [])):
                results.append(record)
        return results

    def edit(self, contact_name, parameter, new_value):
        names = []
        try:
            for account in self.data:
                names.append(account["name"])
                if account["name"] == contact_name:
                    if parameter == "birthday":
                        new_value = Birthday(new_value).value
                    elif parameter == "email":
                        new_value = Email(new_value).value
                    elif parameter == "country":
                        new_value = Country(new_value).value
                    elif parameter == "phones":
                        new_contact = new_value.split(" ")
                        new_value = []
                        for number in new_contact:
                            new_value.extend(Phone(number).value)
                    if parameter in account.keys():
                        account[parameter] = new_value
                    else:
                        raise ValueError
            if contact_name not in names:
                raise NameError
        except ValueError:
            print(f"{RED}Невірний параметр! Спробуйте знову.{YELLOW}")
        except NameError:
            print(f"{RED}Такого контакту не знайдено!{YELLOW}")
        else:
            self.log(f"Контакт {contact_name} відредаговано!")
            return True
        return False

    def remove(self, pattern):
        flag = False
        for account in self.data:
            if account["name"] == pattern:
                self.data.remove(account)
                self.log(f"Контакт {account['name']} видалено!")
                flag = True
        return flag

    def __get_current_week(self):
        now = dt.now()
        current_weekday = now.weekday()
        if current_weekday < 5:
            week_start = now - timedelta(days=2 + current_weekday)
        else:
            week_start = now - timedelta(days=current_weekday - 5)
        return [week_start.date(), week_start.date() + timedelta(days=7)]

    def congratulate(self):
        result = []
        WEEKDAYS = [
            "Понеділок",
            "Вівторок",
            "Середа",
            "Четвер",
            "П'ятниця",
            "Субота",
            "Неділя",
        ]
        current_year = dt.now().year
        congratulate = {
            "Понеділок": [],
            "Вівторок": [],
            "Середа": [],
            "Четвер": [],
            "П'ятниця": [],
        }
        for account in self.data:
            if account["birthday"]:
                new_birthday = account["birthday"].replace(year=current_year)
                birthday_weekday = new_birthday.weekday()
                if (
                    self.__get_current_week()[0]
                    <= new_birthday
                    < self.__get_current_week()[1]
                ):
                    if birthday_weekday < 5:
                        congratulate[WEEKDAYS[birthday_weekday]].append(account["name"])
                    else:
                        congratulate["Понеділок"].append(account["name"])
        for key, value in congratulate.items():
            if len(value):
                result.append(f"{key}: {' '.join(value)}")
        return "_" * 50 + "\n" + "\n".join(result) + "\n" + "_" * 50

    def search(self, pattern, category):
        result = []
        category_new = category.strip().lower().replace(" ", "")
        pattern_new = pattern.strip().lower().replace(" ", "")

        for account in self.data:
            if category_new == "phones":
                for phone in account["phones"]:
                    if phone.lower().replace(" ", "").startswith(pattern_new):
                        result.append(account)
                        break
            elif category_new == "tags":
                for tag in account.get("tags", []):
                    if tag.lower().replace(" ", "") == pattern_new:
                        result.append(account)
                        break
            elif category_new == "birthday":
                if account["birthday"] and account["birthday"].strftime(
                    "%d.%m.%Y"
                ).replace(" ", "").startswith(pattern_new):
                    result.append(account)
            else:
                if (
                    account.get(category_new, "").lower().replace(" ", "")
                    == pattern_new
                ):
                    result.append(account)

        if not result:
            print(f"{RED}Такого контакту не знайдено!{YELLOW}")
        return result
