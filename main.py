import os

# from .src.Assistant_bot import AddressBookCLI
from src.Assistant_bot import (
    AddressBookCLI,
    ContactHandler,
    FileHandler,
    GameHandler,
    WeatherHandler,
)
from src.AddressBook import AddressBook, PickleStorage
from rich.console import Console


# def main():
if __name__ == "__main__":
    console = Console()

    book = AddressBook(PickleStorage())
    contact_handler = ContactHandler(book)
    file_handler = FileHandler()
    game_handler = GameHandler()
    weather_handler = WeatherHandler()

    console.print("Привіт! Я Ваш помічник з контактами.", style="bold blue")
    console.print(
        "Я можу зберігати і редагувати Ваші контакти, і ще багато чого цікавого...",
        style="bold yellow",
    )

    cli = AddressBookCLI(
        contact_handler, file_handler, game_handler, weather_handler, book
    )

    # file_path = os.path.join('', 'auto_save.bin')
    file_path = os.path.join("src", "auto_save.bin")

    # Перевіряємо, чи існує файл перед його завантаженням
    if os.path.exists(file_path):
        cli.book.load("auto_save")
        console.print("Завантажено існуючу адресну книгу.", style="italic green")
    else:
        console.print(
            "Жодної збереженої адресної книги не знайдено. Починаємо з порожньої книги.",
            style="italic red",
        )

    cli.cmdloop()

    # Зберігаємо адресну книгу при виході
    cli.book.save("auto_save")
    console.print("До побачення!", style="bold magenta")
