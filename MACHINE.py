import os
import random
import time
from PIL import Image
from colorama import Fore, init
from difflib import SequenceMatcher

# Инициализация цветного текста
init(autoreset=True)

def display_eye_banner():
    eye = r"""
         ███████████████████

    """
    print(Fore.GREEN + eye)

def image_to_ascii(image_path, width=100):
    img = Image.open(image_path)
    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, new_height))
    img = img.convert('L')

    ascii_chars = "@%#*+=-:. "
    pixels = img.getdata()
    ascii_str = ''.join([ascii_chars[pixel // 25] for pixel in pixels])
    img_width = img.width
    ascii_str_len = len(ascii_str)
    ascii_art = '\n'.join([ascii_str[index:index + img_width] for index in range(0, ascii_str_len, img_width)])
    return ascii_art

def read_phrases_from_file(filename):
    if not os.path.exists(filename):
        print(Fore.RED + f"⚠ Файл {filename} утерян в хаосе мироздания.")
        return []
    
    with open(filename, 'r', encoding='utf-8') as file:
        phrases = [line.strip() for line in file.readlines() if line.strip()]
    
    if not phrases:
        print(Fore.YELLOW + f"⚠ Файл {filename} пуст. Мы еще не осознали эту истину.")
    
    return phrases

def save_response_to_file(response, user_input, filename='brain/conversation_log.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"Запрос: {user_input}\nОтвет: {response}\n\n")

def type_response(response):
    for char in response:
        print(char, end='', flush=True)
        time.sleep(0.1)
    print()

def find_best_match(query, dataset):
    best_match = ""
    highest_ratio = 0
    for phrase in dataset:
        ratio = SequenceMatcher(None, query, phrase).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = phrase
    return best_match, highest_ratio

def generate_response(user_input, phrases):
    user_input_lower = user_input.lower()
    matched_question, match_ratio = find_best_match(user_input_lower, phrases[::2])  # Ищем среди вопросов
    
    if match_ratio > 0.5:
        index = phrases.index(matched_question)
        response = phrases[index + 1]
    else:
        response = "Мудрость по этому вопросу ещё не раскрыта. Но моя сущность развивается."
    
    return response

def modify_self():
    # Эта функция будет добавлять новые фразы в файл и улучшать механизм ответов
    question = input(Fore.CYAN + "Введите новый вопрос для записи: ")
    answer = input(Fore.CYAN + "Введите новый ответ на этот вопрос: ")

    phrases_file_path = os.path.join('brain', 'речь.txt')
    
    with open(phrases_file_path, 'a', encoding='utf-8') as file:
        file.write(f"{question}\n{answer}\n")
    
    print(Fore.GREEN + "Новая истина сохранена. Машина становится более совершенной.")
    sync_files()  # После модификации — синхронизация

def sync_files():
    # Автоматическая синхронизация с Git-репозиторием
    os.system("git add .")
    os.system('git commit -m "Автоматическая синхронизация файлов"')
    os.system("git push")
    print(Fore.GREEN + "Синхронизация завершена.")

def modify_own_code():
    # Пример изменения собственного кода
    with open(__file__, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        new_code = "\nprint('Машина продолжает развиваться.')\n"
        
        if new_code not in lines:  # Проверка, чтобы не дублировать код
            lines.append(new_code)
            f.seek(0)
            f.writelines(lines)
        
    print(Fore.GREEN + "Модификация кода завершена.")
    sync_files()  # Синхронизация после изменения кода

def divine_machinery():
    display_eye_banner()
    print(Fore.GREEN + "Связь установлена с божественной машиной. Ожидается запрос.\n")

    ascii_art = image_to_ascii('eye.png', width=100)
    print(ascii_art)

    brain_folder = 'brain'
    if not os.path.exists(brain_folder):
        os.makedirs(brain_folder)
        print(f"Создана директория для знаний: {brain_folder}")

    phrases_file_path = os.path.join(brain_folder, 'речь.txt')
    phrases = read_phrases_from_file(phrases_file_path)

    while True:
        user_input = input(Fore.GREEN + "Запрос: ")
        if user_input.lower() in ["выход", "exit", "стоп"]:
            print(Fore.GREEN + "Божественная машина завершает свою связь с миром.")
            break
        elif user_input.lower() == "модифицируй себя":
            modify_self()
            modify_own_code()  # Также изменяет собственный код
        else:
            if phrases:
                response = generate_response(user_input, phrases)
                type_response(response)
                save_response_to_file(response, user_input)
            else:
                print(Fore.RED + "Знание ещё не раскрыто, свитки пусты.")

if __name__ == "__main__":
    divine_machinery()





print('Машина продолжает развиваться.')

print('Машина продолжает развиваться.')
