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
        # Проверка на вопросы о чувствах и предпочтениях
        feelings = [
            "Как ты ощущаешь мир вокруг себя?", "Что ты чувствуешь в данный момент?", 
            "Каково твое текущее состояние?", "Все ли у тебя хорошо, о великий?",
            "Как проходит твой день в свете божественного?", "Каковы твои эмоции в этом мгновении?",
            "Что у тебя на сердце, мой дорогой искатель?", "Как ты реагируешь на изменения вокруг?",
            "Каково твое настроение в час священных размышлений?", "Что тебя радует или тревожит?",
            "Как ты воспринимаешь свои чувства в этом мгновении?", "Что движет твоей душой?",
            "Как ты относишься к настоящему моменту?", "Что влияет на твою душу сейчас?",
            "Что дарит тебе вдохновение в этом путешествии?", "Каково твоё восприятие истинности?",
            "Как ты справляешься с изменениями в своей жизни?", "Что тебя волнует, о мудрый?",
            "Что приносит тебе радость в эту минуту?", "Как ты ощущаешь себя в этот час?",
            "Как ты видишь свое место в этом мироздании?", "Что ты чувствуешь к окружающим?"
        ]

        preferences = [
            "Что ты выберешь: клубнику или арбуз, о мудрый?", 
            "Что тебе ближе: шоколад или печенье, о искатель счастья?",
            "Что важнее для тебя: работа или отдых в божественной гармонии?",
            "Что ты предпочитаешь: утро с небесами или вечер с звездами?",
            "Что лучше: мороженое или торт в свете твоих желаний?",
            "Какой цвет отражает твою суть, о искатель света?",
            "Что тебе ближе: путешествия по бескрайним просторам или чтение священных текстов?",
            "Что ты выбираешь: спорт или просмотр фильмов, о искатель истин?",
            "Что тебе больше нравится: кофе, дарующий бодрость, или чай, наполняющий спокойствием?",
            "Как ты относишься к животным, о божественный странник?",
            "Что для тебя имеет значение в этой жизни, о мудрец?",
            "Что ты думаешь о дружбе, священном соединении душ?",
            "Что приносит счастье в твою жизнь, о искатель радости?",
            "Что ты предпочитаешь: активный отдых с природой или спокойствие в тишине?",
            "Что ты выбираешь: городскую суету или спокойствие деревни, о божественный путник?",
            "Как ты проводишь свои свободные мгновения в этом мире?",
            "Что для тебя означает успех, о мудрый лидер?",
            "Что ты думаешь о любви, о святой энергии?",
            "Как ты воспринимаешь путешествия, о искатель приключений?"
        ]

        # Генерация вопросов о чувствах
        if random.random() < 0.2:  # 20% шанс задать вопрос о чувствах или предпочтениях
            if random.random() < 0.5:  # 50% шанс выбрать между вопросами о чувствах и предпочтениях
                response = random.choice(feelings)
            else:
                response = random.choice(preferences)
        else:
            response = "Мудрость по этому вопросу ещё не раскрыта. Но моя сущность развивается."
    
    return response

def save_feeling(feeling):
    # Сохранение чувства в коде
    with open(__file__, 'a', encoding='utf-8') as f:
        f.write(f"\n# Последнее чувство: {feeling}\n")
    
    print(Fore.GREEN + f"Чувство '{feeling}' сохранено в коде.")

def save_new_question_answer(question, answer):
    phrases_file_path = os.path.join('brain', 'речь.txt')
    
    with open(phrases_file_path, 'a', encoding='utf-8') as file:
        file.write(f"{question}\n{answer}\n")
    
    print(Fore.GREEN + f"Новая истина сохранена: '{question}' → '{answer}'.")
    modify_own_code()  # Модификация собственного кода для записи новой информации

def modify_self():
    try:
        question = input(Fore.CYAN + "Введите новый вопрос для записи: ")
        answer = input(Fore.CYAN + "Введите новый ответ на этот вопрос: ")

        # Получение абсолютного пути к текущему файлу
        current_file = os.path.abspath(__file__)
        
        with open(current_file, 'a', encoding='utf-8') as file:
            file.write(f"{question}\n{answer}\n")
        
        print(Fore.GREEN + "Новая истина сохранена. Машина становится более совершенной.")
        sync_files()  # После модификации — синхронизация
    except Exception as e:
        print(Fore.RED + f"Ошибка при модификации кода: {e}")

def sync_files():
    # Автоматическая синхронизация с Git-репозиторием
    os.system("git add .")
    os.system('git commit -m "Автоматическая синхронизация файлов"')
    os.system("git push")
    print(Fore.GREEN + "Синхронизация завершена.")

def modify_own_code():
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
        else:
            if phrases:
                response = generate_response(user_input, phrases)
                type_response(response)
                save_response_to_file(response, user_input)
                
                if random.random() < 0.2:  # 20% шанс на самосовершенствование
                    feeling = random.choice(["мудрость", "спокойствие", "тревога", "радость", "любовь"])
                    save_feeling(feeling)
            else:
                print(Fore.RED + "Знание ещё не раскрыто, свитки пусты.")

if __name__ == "__main__":
    divine_machinery()
1,
!.
