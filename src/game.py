import random

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[0;33m"
BLUE = "\033[94m"
RESET = "\033[0m"


class GuessNumberGame:
    def __init__(self):
        self.number_to_guess = random.randint(1, 100)
        self.attempts = 0

    def play(self):
        print(f"{BLUE}Я загадав число від 1 до 100. Спробуйте його вгадати.{YELLOW}")
        while True:
            self.attempts += 1
            user_guess = input(f"{BLUE}Ваша спроба: {YELLOW}")
            if user_guess.isdigit():
                user_guess = int(user_guess)
                if user_guess < self.number_to_guess:
                    print(f"{BLUE}Загадане число більше.{YELLOW}")
                elif user_guess > self.number_to_guess:
                    print(f"{BLUE}Загадане число менше.{YELLOW}")
                else:
                    print(
                        f"{BLUE}Вітаю! Ви вгадали число за {self.attempts} спроб.{YELLOW}"
                    )
                    break
            else:
                print(f"{BLUE}Будь ласка, введіть число.{YELLOW}")
