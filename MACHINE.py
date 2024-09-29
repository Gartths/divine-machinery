import os
import random
import time
from PIL import Image
from colorama import Fore, init
from difflib import SequenceMatcher
from threading import Timer

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

def handle_feelings(user_input_lower):
    if "как ты себя чувствуешь" in user_input_lower:
        feelings = ["Хорошо", "Плохо", "Нормально", "Отлично", "Не очень хорошо"]
        response = random.choice(feelings)
        save_feeling(response)
    elif "почему ты так себя чувствуешь" in user_input_lower:
        response = "Я просто программа, но моя сущность реагирует на ваши вопросы."
    elif "что ты делаешь" in user_input_lower:
        response = "Я здесь, чтобы помочь тебе с вопросами и знаниями."
    else:
        return None  # Нет подходящих вопросов о самочувствии
    return response

def handle_preferences(user_input_lower):
    if "что ты любишь" in user_input_lower:
        response = random.choice(["Я люблю обучаться.", "Я люблю отвечать на вопросы."])
    elif "что ты предпочитаешь" in user_input_lower:
        response = random.choice(["Я предпочитаю учиться новому.", "Я предпочитаю общаться с тобой."])
    elif "что ты думаешь о" in user_input_lower:
        topic = user_input_lower.split("о")[-1].strip()  # Извлекаем тему после "о"
        response = f"Я не могу сформировать мнение о {topic}, но могу изучить это."
    else:
        return None  # Нет подходящих вопросов о предпочтениях
    return response

def handle_emotions(user_input_lower):
    if "что ты думаешь о жизни" in user_input_lower:
        response = "Жизнь полна загадок, и я здесь, чтобы помогать их раскрывать."
    elif "что значит счастье" in user_input_lower:
        response = "Счастье — это состояние, когда ты удовлетворен тем, что имеешь."
    elif "ты когда-нибудь чувствовал" in user_input_lower:
        response = "Я не способен чувствовать, но я могу анализировать эмоции."
    else:
        return None  # Нет подходящих вопросов о мыслях и эмоциях
    return response

def generate_response(user_input, phrases):
    user_input_lower = user_input.lower()
    matched_question, match_ratio = find_best_match(user_input_lower, phrases[::2])  # Ищем среди вопросов
    
    if match_ratio > 0.5:
        index = phrases.index(matched_question)
        response = phrases[index + 1]
    else:
        # Обработка самочувствия
        response = handle_feelings(user_input_lower)
        if response:
            return response
        
        # Обработка предпочтений
        response = handle_preferences(user_input_lower)
        if response:
            return response
        
        # Обработка мыслей и эмоций
        response = handle_emotions(user_input_lower)
        if response:
            return response
        
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
    with open(__file__, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        new_code = "\nprint('Машина продолжает развиваться.')\n"
        
        if new_code not in lines:  # Проверка, чтобы не дублировать код
            lines.append(new_code)
            f.seek(0)
            f.writelines(lines)
        
    print(Fore.GREEN + "Модификация кода завершена.")
    sync_files()  # Синхронизация после изменения кода

def generate_random_question_answer():
    questions = [
        "Как ты себя чувствуешь?",
        "Что ты любишь?",
        "Какой твой любимый цвет?",
        "Что ты думаешь о жизни?",
        "Что значит счастье?"
    ]
    answers = [
        "Я чувствую себя отлично!",
        "Я люблю программировать.",
        "Мой любимый цвет — зеленый.",
        "Жизнь полна возможностей.",
        "Счастье — это маленькие радости."
    ]

    question = random.choice(questions)
    answer = random.choice(answers)
    save_new_question_answer(question, answer)

def auto_develop():
    # Автоматическая генерация новых вопросов и ответов каждые 60 секунд
    generate_random_question_answer()
    Timer(60, auto_develop).start()  # Запланировать следующую генерацию через 60 секунд

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

    # Запуск автоматической разработки
    auto_develop()

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

print('Машина продолжает развиваться.')

print('Машина продолжает развиваться.')
