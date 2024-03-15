import cmd
from rich.console import Console
from rich.table import Table
from rich.text import Text
from pathlib import Path
from .get_weather_module import get_weather, format_weather
from .AddressBook import (
    AddressBook,
    PickleStorage,
    Record,
    Name,
    Phone,
    Birthday,
    Email,
    Country,
    Note,
    Tag,
)
from .main_sort import main
from .game import GuessNumberGame

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[0;33m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


class GameHandler:
    def play_game(self):
        game = GuessNumberGame()
        game.play()
        console = Console()
        console.print("Дякуємо за гру!", style="bold green")


class FileHandler:
    def sort_files(self, folder_path):
        try:
            main(folder_path.resolve())
            console = Console()
            console.print(
                f"Файли за шляхом {folder_path} були відсортовані.", style="italic blue"
            )
        except Exception as e:
            console = Console()
            console.print(f"An error occurred: {e}", style="italic red")

    def save(self, file_name, book):
        book.save(file_name)
        console = Console()
        console.print(
            f"Книгу контактів збережено в файлі {file_name}.bin", style="bold green"
        )

    def load(self, file_name, book):
        book.load(file_name)
        console = Console()
        console.print(
            f"Книгу контактів завантажено з файлу {file_name}.bin", style="bold green"
        )


class ContactHandler:
    def __init__(self, book):
        self.book = book

    def add_contact(self, record):
        self.book.add(record)

    def remove_contact(self, pattern):
        return self.book.remove(pattern)

    def get_contact_data(self):
        return self.book.data

    def edit_contact(self, contact_name, parameter, new_value):
        return self.book.edit(contact_name, parameter, new_value)

    def congratulate(self):
        return self.book.congratulate()

    def search_by_tags(self, pattern):
        return self.book.search_by_tags(pattern)

    def search(self, pattern, category):
        return self.book.search(pattern, category)


class WeatherHandler:
    def get_weather(self, city):
        api_key = "16bfe776fb8afe007ed1f21a6277aba2"
        try:
            weather_data = get_weather(city, api_key)
            weather_report = format_weather(weather_data)
            console = Console()
            console.print(weather_report, style="bold blue")
        except Exception as e:
            console = Console()
            console.print(f"Error: {str(e)}", style="bold red")


class AddressBookCLI(cmd.Cmd):
    intro = f"{BLUE}Щоб побачити доступні команди наберіть {YELLOW}help{BLUE} чи {YELLOW}?{BLUE}.\nЩоб побачити інформацію про конкретну команду наберіть {YELLOW}help [назва_команди]"
    prompt = f"{BLUE}>>>>>>>  {YELLOW}"
    console = Console()

    def __init__(
        self, contact_handler, file_handler, game_handler, weather_handler, book
    ):
        super().__init__()
        self.contact_handler = contact_handler
        self.file_handler = file_handler
        self.game_handler = game_handler
        self.weather_handler = weather_handler
        self.book = book
        self.console = Console()

    def default(self, line):
        self.stdout.write(f"{RED}Невідома команда: {MAGENTA}{line}\n{YELLOW}")

    def do_play_game(self, arg):
        'Запустити гру "Вгадай число": play_game'
        self.game_handler.play_game()

    def do_sort_files(self, args):
        "Відсортувати файли в папці по вказаному шляху: sort_files"
        folder_path = input(
            f"{BLUE}Будь ласка вкажіть шлях до папки\nв якій необхідно відсортувати файли: {YELLOW}"
        )
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            console = Console()
            console.print(
                "Вказано невірний шлях. Спробуйте ще раз.", style="italic red"
            )
            return
        self.file_handler.sort_files(folder_path)

    def do_add(self, arg):
        "Додати новий контакт: add"
        name = Name(input(f"{BLUE}Ім'я: {YELLOW}")).value.strip()
        country = Country().value.capitalize()
        phones = Phone().value
        birth = Birthday().value
        email = Email().value.strip()
        note = Note(input(f"{BLUE}Нотатка: {YELLOW}")).value
        tags_input = input(f"{BLUE}Теги (через пробіл): {YELLOW}")
        tags = [Tag(tag.strip()).value for tag in tags_input.split()]
        record = Record(name, country, phones, birth, email, note, tags)
        self.contact_handler.add_contact(record)
        self.console.print("Контакт успішно додано.", style="bold green")

    def do_search(self, arg):
        "Пошук за категоріями: search"
        print(
            f"{BLUE}Є наступні категорії: \nName \nCountry \nPhones \nBirthday \nEmail \nNote \nTags{YELLOW}"
        )
        category = input(f"{BLUE}Пошук за категорією: {YELLOW}")
        pattern = input(f"{BLUE}Введіть текст для пошуку: {YELLOW}")

        results = self.contact_handler.search(pattern, category)

        if results:
            console = Console()
            table = self._create_table(results)
            console.print(table)
        else:
            self.console.print(
                "Такий контакт відсутній в книзі контактів!", style="bold red"
            )

    def do_edit(self, arg):
        "Редагування контакту: edit"
        contact_name = input(f"{BLUE}Ім'я контакту: {YELLOW}")
        parameter = input(
            f"{BLUE}Оберіть параметр для редагування\n(name, country, phones, birthday, email, note): {YELLOW}"
        ).strip()
        new_value = input(f"{BLUE}Нове значення: {YELLOW}")
        self.contact_handler.edit_contact(contact_name, parameter, new_value)

    def do_remove(self, arg):
        "Видалення контакту: remove"
        pattern = input(f"{BLUE}Видалити (ім'я контакту чи номер телефону): {YELLOW}")
        success = self.contact_handler.remove_contact(pattern)
        console = Console()

        if success:
            console.print("Контакт успішно видалено.", style="bold green")
        else:
            console.print("Контакт не знайдено.", style="bold red")

    def do_save(self, arg):
        "Зберегти книгу контактів в файл: save"
        file_name = input(f"{BLUE}Ім'я файла: {YELLOW}")
        self.file_handler.save(file_name, self.book)

    def do_load(self, arg):
        "Завантажити книгу контактів з файлу: load"
        file_name = input(f"{BLUE}Ім'я файла: {YELLOW}")
        self.file_handler.load(file_name, self.book)

    def do_congratulate(self, arg):
        "Перевірити в яких контактів день народження на цьому тижні: congratulate"
        console = Console()
        console.print(self.contact_handler.congratulate(), style="bold magenta")

    def do_view(self, arg):
        "Переглянути книгу контактів: view"
        console = Console()
        table = self._create_table(self.contact_handler.get_contact_data())
        console.print(table)

    def do_weather(self, arg):
        "Дізнатись погоду в місті: weather [city_name]"
        city = arg or input(f"{BLUE}Введіть назву міста: {YELLOW}")
        self.weather_handler.get_weather(city)

    def do_exit(self, arg):
        "Вихід з програми: exit"
        return True

    def _create_table(self, data):
        table = Table(show_header=True, header_style="bold white")
        table.add_column("Ім'я")
        table.add_column("Країна")
        table.add_column("Телефон")
        table.add_column("Дата народження", justify="right")
        table.add_column("Електронна пошта", justify="right")
        table.add_column("Примітка", justify="right")
        table.add_column("Теги", justify="right")

        for account in data:
            name = Text(account["name"], style="blue")
            country = Text(account["country"], style="yellow")
            phone = Text(
                ", ".join(account["phones"]) if account["phones"] else "", style="blue"
            )
            birth = Text(
                account["birthday"].strftime("%d.%m.%Y") if account["birthday"] else "",
                style="yellow",
            )
            email = Text(account["email"], style="blue")
            note = Text(account["note"], style="yellow")
            tags = Text(
                ", ".join(account["tags"]) if account["tags"] else "", style="bold blue"
            )

            table.add_row(name, country, phone, birth, email, note, tags)

        return table


if __name__ == "__main__":
    book = AddressBook(PickleStorage())
    contact_handler = ContactHandler(book)
    file_handler = FileHandler()
    game_handler = GameHandler()
    weather_handler = WeatherHandler()
    AddressBookCLI(
        contact_handler, file_handler, game_handler, weather_handler, book
    ).cmdloop()
