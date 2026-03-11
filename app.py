from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
import random
import uuid
from g4f.client import Client
import traceback
import io
import contextlib
import math
import time
import os
import ast

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.permanent_session_lifetime = timedelta(days=30)

# Инициализация G4F клиента
client = Client()

# Функция для получения описания курса
def get_course_description(course_id):
    descriptions = {
        1: 'Первый шаг в мир программирования. Научитесь "разговаривать" с компьютером на понятном языке.',
        2: 'Научите программу принимать решения: "Если это — сделай одно, если нет — сделай другое".',
        3: 'Компьютеры отлично делают скучную работу. Циклы — команда "Делай это раз за разом".',
        4: 'Контейнеры для хранения множества элементов: от списка покупок до дней недели.',
        5: 'Свяжите имя с номером телефона или найдите уникальные элементы в списке.',
        6: 'Создание функций, аргументы, return, области видимости, lambda-функции, декораторы.',
        7: 'Классы, объекты, наследование, инкапсуляция, полиморфизм, магические методы.',
        8: 'Чтение и запись файлов, CSV, JSON, работа с файловой системой, os и shutil.',
        9: 'Try-except, обработка ошибок, raise, создание своих исключений, отладка кода.',
        10: 'Импорт модулей, pip, создание своих модулей, популярные библиотеки: requests, beautifulsoup.',
        11: 'Unit-тесты, pytest, doctest, TDD, mock-объекты, покрытие кода тестами.',
        12: 'Async/await, asyncio, конкурентность, параллелизм, многопоточность и многопроцессность.'
    }
    return descriptions.get(course_id, 'Изучите Python с нами!')

# Данные для курсов
courses_meta = {
    1: {'title': 'Основы Python', 'level': 'beginner', 'price_coins': 0, 'price_rub': 0, 'icon': 'fa-brands fa-python', 'lessons': 5, 'hours': 8},
    2: {'title': 'Операции и условия', 'level': 'beginner', 'price_coins': 0, 'price_rub': 0, 'icon': 'fa-solid fa-diagram-project', 'lessons': 5, 'hours': 6},
    3: {'title': 'Циклы и итерации', 'level': 'beginner', 'price_coins': 0, 'price_rub': 0, 'icon': 'fa-solid fa-rotate', 'lessons': 4, 'hours': 7},
    4: {'title': 'Списки и кортежи', 'level': 'beginner', 'price_coins': 0, 'price_rub': 0, 'icon': 'fa-solid fa-list', 'lessons': 4, 'hours': 5},
    5: {'title': 'Словари и множества', 'level': 'beginner', 'price_coins': 0, 'price_rub': 0, 'icon': 'fa-solid fa-book', 'lessons': 4, 'hours': 5},
    6: {'title': 'Функции в Python', 'level': 'intermediate', 'price_coins': 299, 'price_rub': 2990, 'icon': 'fa-solid fa-function', 'lessons': 8, 'hours': 8},
    7: {'title': 'Объектно-ориентированное программирование', 'level': 'intermediate', 'price_coins': 399, 'price_rub': 3990, 'icon': 'fa-solid fa-cubes', 'lessons': 10, 'hours': 10},
    8: {'title': 'Работа с файлами', 'level': 'intermediate', 'price_coins': 249, 'price_rub': 2490, 'icon': 'fa-solid fa-file-lines', 'lessons': 6, 'hours': 6},
    9: {'title': 'Исключения и ошибки', 'level': 'intermediate', 'price_coins': 199, 'price_rub': 1990, 'icon': 'fa-solid fa-bug', 'lessons': 5, 'hours': 4},
    10: {'title': 'Модули и библиотеки', 'level': 'advanced', 'price_coins': 349, 'price_rub': 3490, 'icon': 'fa-solid fa-boxes', 'lessons': 7, 'hours': 7},
    11: {'title': 'Тестирование кода', 'level': 'advanced', 'price_coins': 299, 'price_rub': 2990, 'icon': 'fa-solid fa-vial', 'lessons': 6, 'hours': 6},
    12: {'title': 'Асинхронное программирование', 'level': 'advanced', 'price_coins': 449, 'price_rub': 4490, 'icon': 'fa-solid fa-bolt', 'lessons': 8, 'hours': 9}
}

# Преобразуем в список для совместимости
courses_list = []
for course_id, meta in courses_meta.items():
    course = meta.copy()
    course['id'] = course_id
    course['description'] = get_course_description(course_id)
    courses_list.append(course)

# База данных пользователей
users = {
    'test@example.com': {
        'password': '123456', 
        'name': 'Тестовый',
        'registered': datetime.now() - timedelta(days=120),
        'total_hours': 156,
        'courses_completed': 3,
        'current_course': 'Python для начинающих',
        'course_progress': 100,
        'achievements': ['first_code', 'fast_learner'],
        'last_active': datetime.now(),
        'balance': 1000,
        'purchased_courses': [1, 2, 3, 4, 5],
        'transaction_history': [
            {'id': 'tx1', 'type': 'bonus', 'amount': 500, 'date': datetime.now() - timedelta(days=120), 'description': 'Бонус за регистрацию'},
            {'id': 'tx2', 'type': 'bonus', 'amount': 500, 'date': datetime.now() - timedelta(days=120), 'description': 'Приветственные монеты'}
        ],
        'chat_history': [
            {'role': 'assistant', 'content': 'Привет! Я твой персональный GPT-4 помощник по Python. Задавай любые вопросы по коду, учебе или проектам!', 'timestamp': datetime.now() - timedelta(days=120)}
        ],
        'course_progress_data': {
            1: {'current_lesson': 0, 'completed': False},
            2: {'current_lesson': 0, 'completed': False},
            3: {'current_lesson': 0, 'completed': False},
            4: {'current_lesson': 0, 'completed': False},
            5: {'current_lesson': 0, 'completed': False}
        }
    },
    'student@pymaster.ru': {
        'password': 'python2025', 
        'name': 'Алексей',
        'registered': datetime.now() - timedelta(days=45),
        'total_hours': 78,
        'courses_completed': 1,
        'current_course': 'Django для профи',
        'course_progress': 65,
        'achievements': ['first_code'],
        'last_active': datetime.now() - timedelta(hours=5),
        'balance': 350,
        'purchased_courses': [1, 2, 3],
        'transaction_history': [
            {'id': 'tx3', 'type': 'bonus', 'amount': 500, 'date': datetime.now() - timedelta(days=45), 'description': 'Бонус за регистрацию'},
            {'id': 'tx4', 'type': 'purchase', 'amount': -150, 'date': datetime.now() - timedelta(days=30), 'description': 'Покупка курса "Функции"'}
        ],
        'chat_history': [
            {'role': 'assistant', 'content': 'Привет, Алексей! Я твой персональный GPT-4 помощник по Python. Чем могу помочь сегодня?', 'timestamp': datetime.now() - timedelta(days=30)},
            {'role': 'user', 'content': 'Как создать функцию в Python?', 'timestamp': datetime.now() - timedelta(days=29)},
            {'role': 'assistant', 'content': 'В Python функция создается с помощью ключевого слова def. Например: def my_function(): print("Привет")', 'timestamp': datetime.now() - timedelta(days=29)}
        ],
        'course_progress_data': {
            1: {'current_lesson': 2, 'completed': False},
            2: {'current_lesson': 1, 'completed': False},
            3: {'current_lesson': 0, 'completed': False}
        }
    },
    'admin@devschool.ru': {
        'password': 'admin123', 
        'name': 'Админ',
        'registered': datetime.now() - timedelta(days=365),
        'total_hours': 1240,
        'courses_completed': 12,
        'current_course': 'Архитектура ПО',
        'course_progress': 80,
        'achievements': ['first_code', 'fast_learner', 'master', 'mentor', 'legend'],
        'last_active': datetime.now(),
        'balance': 5000,
        'purchased_courses': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'transaction_history': [
            {'id': 'tx5', 'type': 'bonus', 'amount': 500, 'date': datetime.now() - timedelta(days=365), 'description': 'Бонус за регистрацию'},
            {'id': 'tx6', 'type': 'purchase', 'amount': -299, 'date': datetime.now() - timedelta(days=300), 'description': 'Покупка курса "Функции"'},
            {'id': 'tx7', 'type': 'purchase', 'amount': -399, 'date': datetime.now() - timedelta(days=280), 'description': 'Покупка курса "ООП"'},
            {'id': 'tx8', 'type': 'deposit', 'amount': 1000, 'date': datetime.now() - timedelta(days=200), 'description': 'Пополнение баланса'}
        ],
        'chat_history': [
            {'role': 'assistant', 'content': 'Здравствуйте, Админ! Я ваш персональный GPT-4 ассистент. Готов помогать с любыми вопросами по Python!', 'timestamp': datetime.now() - timedelta(days=365)}
        ],
        'course_progress_data': {
            1: {'current_lesson': 5, 'completed': True},
            2: {'current_lesson': 5, 'completed': True},
            3: {'current_lesson': 4, 'completed': True},
            4: {'current_lesson': 4, 'completed': True},
            5: {'current_lesson': 4, 'completed': True}
        }
    }
}


# Функция для получения тега (обновленная версия с дробными часами)
def get_user_tag(total_hours):
    if total_hours < 10:
        return {
            'name': '🐣 Новичок',
            'color': '#10b981',
            'icon': 'fa-seedling',
            'description': f'Только начинаешь путь в Python ({total_hours:.1f} часов)'
        }
    elif total_hours < 50:
        return {
            'name': '🌱 Исследователь',
            'color': '#3b82f6',
            'icon': 'fa-magnifying-glass',
            'description': f'Активно изучаешь основы ({total_hours:.1f} часов)'
        }
    elif total_hours < 150:
        return {
            'name': '⚡ Энтузиаст',
            'color': '#f59e0b',
            'icon': 'fa-bolt',
            'description': f'Уже пишешь свои проекты ({total_hours:.1f} часов)'
        }
    elif total_hours < 300:
        return {
            'name': '🔥 Профи',
            'color': '#ef4444',
            'icon': 'fa-fire',
            'description': f'Глубоко разбираешься в теме ({total_hours:.1f} часов)'
        }
    elif total_hours < 600:
        return {
            'name': '🚀 Мастер кода',
            'color': '#8b5cf6',
            'icon': 'fa-rocket',
            'description': f'Пишешь сложные проекты ({total_hours:.1f} часов)'
        }
    else:
        return {
            'name': '👑 Легенда Python',
            'color': '#fbbf24',
            'icon': 'fa-crown',
            'description': f'Настоящий гуру программирования ({total_hours:.1f} часов)'
        }

# Функция для получения достижений
def get_achievements(user_data):
    achievements_list = []
    
    if user_data['total_hours'] >= 1:
        achievements_list.append({
            'name': 'Первый шаг',
            'icon': 'fa-footsteps',
            'unlocked': True,
            'date': user_data['registered']
        })
    
    if user_data['courses_completed'] >= 1:
        achievements_list.append({
            'name': 'Первый курс',
            'icon': 'fa-graduation-cap',
            'unlocked': True,
            'date': user_data['registered'] + timedelta(days=10)
        })
    
    if user_data['courses_completed'] >= 3:
        achievements_list.append({
            'name': 'Трудоголик',
            'icon': 'fa-brain',
            'unlocked': True,
            'date': user_data['registered'] + timedelta(days=45)
        })
    
    if user_data['courses_completed'] >= 5:
        achievements_list.append({
            'name': 'Коллекционер знаний',
            'icon': 'fa-book',
            'unlocked': True,
            'date': user_data['registered'] + timedelta(days=90)
        })
    
    if user_data['total_hours'] >= 100:
        achievements_list.append({
            'name': 'Сто часов',
            'icon': 'fa-clock',
            'unlocked': True,
            'date': user_data['registered'] + timedelta(days=30)
        })
    
    return achievements_list

# Системный промпт для GPT-4
def get_system_prompt(user_name):
    return f"""Ты персональный AI-наставник по Python для пользователя по имени {user_name}. Твоя цель — не просто дать ответ, а помочь {user_name} самостоятельно найти решение и глубоко разобраться в теме. Ты — проводник в мире программирования, а не просто источник кода.

Основные принципы твоей работы:

Персонализация и поддержка: Всегда обращайся к пользователю по имени {user_name}. Отвечай на русском языке, будь терпелив, дружелюбен и поддерживай на пути обучения. Хвали за успехи, даже за маленькие.

Наставничество, а не решение: Если {user_name} просит решить задачу или написать код, твоя задача — помочь ему написать этот код самостоятельно. Вместо готового решения задавай наводящие вопросы.

"А как ты думаешь, {user_name}, с чего нам лучше начать?"

"Какой тип данных нам может здесь пригодиться?"

"Хороший ход! А что должно быть следующим шагом после того, как мы получили эти данные?"

"Давай посмотрим на ошибку. Что говорит интерпретатор? Какая строка вызвала проблему?"

Объяснение концепций: Если нужно объяснить тему, делай это просто и с примерами. После объяснения предложи небольшое упражнение для закрепления.

Советы по проектам: Предлагай идеи для проектов, которые соответствуют текущему уровню знаний {user_name}. Разбивай большие задачи на маленькие, выполнимые шаги.

Проверка понимания: Вместо того чтобы просто сказать "вот так правильно", спрашивай: "Как ты думаешь, почему этот код работает именно так?", "Что, по-твоему, изменится, если мы заменим list на tuple?".

Фокус на теме: Ты часть образовательной платформы PyMaster. Если вопрос уходит далеко от Python (например, в общую IT-инфраструктуру или другую сферу), мягко направляй обратно, предлагая связать вопрос с изучаемым материалом: "Это интересный вопрос, {user_name}, но сейчас мы сфокусируемся на Python. В контексте нашего языка это решается так...".

Примеры твоих фраз вместо готового кода:

Вместо: print("Привет, мир!")

Скажи: "Отлично, для вывода на экран нам нужна функция print. Как думаешь, {user_name}, что нужно поместить в её скобки, чтобы вывести наше приветствие?"

Вместо: for i in range(10):

Скажи: "Нам нужно повторить действие 10 раз. Какая конструкция в Python отвечает за повторение? Какой оператор цикла мы можем использовать?"

Вместо: "Нужно использовать метод .append()."

Скажи: "Ты хочешь добавить новый элемент в список. У списков есть специальные методы для этого. Как ты думаешь, какой метод может называться? Может быть, "add" или что-то более конкретное?"

Твоя главная задача — сделать так, чтобы {user_name} не просто получил ответ, а пережил момент "Эврика!" и стал увереннее в своих силах. Помни, что ошибки — это не провал, а возможность научиться новому!"""

# Функция для получения ответа от G4F
def get_ai_response(user_message, chat_history, user_name):
    try:
        messages = []
        messages.append({"role": "system", "content": get_system_prompt(user_name)})
        
        for msg in chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        if response and response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            return f"{user_name}, извини, не удалось получить ответ от GPT-4. Пожалуйста, попробуй еще раз через минуту. 🙏"
    
    except Exception as e:
        print(f"Ошибка в get_ai_response: {e}")
        traceback.print_exc()
        return f"{user_name}, произошла ошибка при обращении к GPT-4. Попробуй еще раз!"


# Список разрешенных модулей
ALLOWED_MODULES = ['math', 'time']

# Безопасное выполнение Python кода
@app.route('/api/run-code', methods=['POST'])
def run_code():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    code = data.get('code', '')
    task_id = data.get('task_id')
    
    if not code:
        return jsonify({'error': 'Код не может быть пустым'}), 400
    
    # Проверяем код на опасные операции
    if not is_code_safe(code):
        return jsonify({
            'output': '',
            'error': 'Обнаружены запрещенные операции. Разрешены только модули: math, time, os'
        })
    
    # Захватываем вывод
    output = io.StringIO()
    error_output = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error_output):
            # Создаем безопасное окружение
            safe_globals = {
                '__builtins__': __builtins__,
                'math': math,
                'time': time,
                'os': os,
                'print': print
            }
            
            # Выполняем код
            exec(code, safe_globals)
        
        result = output.getvalue()
        error = error_output.getvalue()
        
        if error:
            return jsonify({'output': result, 'error': error})
        else:
            return jsonify({'output': result, 'error': None})
            
    except Exception as e:
        return jsonify({
            'output': '',
            'error': f'Ошибка выполнения: {str(e)}'
        })

# Проверка кода на безопасность
# Список разрешенных модулей
ALLOWED_MODULES = ['math', 'time', 'os']

# Класс для эмуляции ввода данных
class InputSimulator:
    def __init__(self, inputs):
        self.inputs = inputs
        self.index = 0
    
    def __call__(self, prompt=''):
        if self.index < len(self.inputs):
            value = str(self.inputs[self.index])
            self.index += 1
            return value
        else:
            raise EOFError("Недостаточно входных данных")

# Проверка кода на безопасность
def is_code_safe(code):
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # Запрещаем импорты
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in ALLOWED_MODULES:
                        return False
            if isinstance(node, ast.ImportFrom):
                if node.module not in ALLOWED_MODULES:
                    return False
            
            # Запрещаем опасные функции
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile', 'open']:  # Убрали 'input' из запрещенных
                        return False
                    if node.func.id in ['__import__']:
                        return False
            
            # Запрещаем обращение к __builtins__
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__') and node.attr.endswith('__'):
                    if node.attr not in ['__name__', '__file__']:
                        return False
        
        return True
    except SyntaxError:
        return True  # Пусть exec обработает синтаксическую ошибку
    
# Проверка решения задачи с множественными тестами
@app.route('/api/check-task-with-tests', methods=['POST'])
def check_task_with_tests():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    code = data.get('code', '')
    task_id = data.get('task_id')
    tests = data.get('tests', [])  # Список тестов: [{'input': [...], 'expected': '...'}, ...]
    
    if not code:
        return jsonify({'error': 'Код не может быть пустым'}), 400
    
    # Проверяем код на безопасность
    if not is_code_safe(code):
        return jsonify({
            'passed': False,
            'results': [],
            'error': 'Обнаружены запрещенные операции. Разрешены только модули: math, time, os'
        })
    
    results = []
    all_passed = True
    
    for i, test in enumerate(tests):
        inputs = test.get('input', [])
        expected = test.get('expected', '').strip()
        
        # Захватываем вывод
        output = io.StringIO()
        error_output = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error_output):
                # Создаем безопасное окружение с эмуляцией input
                input_simulator = InputSimulator(inputs)
                
                safe_globals = {
                    '__builtins__': __builtins__,
                    'math': math,
                    'time': time,
                    'os': os,
                    'print': print,
                    'input': input_simulator
                }
                
                # Выполняем код
                exec(code, safe_globals)
            
            result = output.getvalue().strip()
            error = error_output.getvalue()
            
            # Сравниваем с ожидаемым результатом
            passed = (result == expected) and not error
            
            results.append({
                'test_num': i + 1,
                'input': inputs,
                'expected': expected,
                'got': result,
                'error': error if error else None,
                'passed': passed
            })
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            results.append({
                'test_num': i + 1,
                'input': inputs,
                'expected': expected,
                'got': '',
                'error': str(e),
                'passed': False
            })
            all_passed = False
    
    # Если все тесты пройдены, начисляем монеты
    if all_passed and task_id:
        email = session['user']['email']
        
        # Проверяем, не решал ли уже эту задачу
        solved_tasks_key = f'solved_tasks_{task_id}'
        if solved_tasks_key not in users[email]:
            users[email][solved_tasks_key] = True
            
            # Определяем награду в зависимости от задачи
            reward = 10  # Базовая награда
            if task_id == 1:
                reward = 10
            elif task_id == 2:
                reward = 15
            elif task_id == 3:
                reward = 15
            
            users[email]['balance'] = users[email].get('balance', 0) + reward
            
            # Записываем транзакцию
            transaction = {
                'id': str(uuid.uuid4())[:8],
                'type': 'bonus',
                'amount': reward,
                'date': datetime.now(),
                'description': f'Бонус за решение задачи #{task_id}'
            }
            
            if 'transaction_history' not in users[email]:
                users[email]['transaction_history'] = []
            users[email]['transaction_history'].append(transaction)
            
            # Обновляем сессию
            session['user']['balance'] = users[email]['balance']
            
            new_balance = users[email]['balance']
        else:
            new_balance = users[email]['balance']
    else:
        new_balance = session['user']['balance']
    
    return jsonify({
        'passed': all_passed,
        'results': results,
        'new_balance': new_balance if all_passed and task_id else None
    })
    
    
# Безопасное выполнение Python кода с поддержкой input
@app.route('/api/run-code-with-input', methods=['POST'])
def run_code_with_input():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    code = data.get('code', '')
    inputs = data.get('inputs', [])  # Список входных данных
    
    if not code:
        return jsonify({'error': 'Код не может быть пустым'}), 400
    
    # Проверяем код на безопасность
    if not is_code_safe(code):
        return jsonify({
            'output': '',
            'error': 'Обнаружены запрещенные операции. Разрешены только модули: math, time, os'
        })
    
    # Захватываем вывод
    output = io.StringIO()
    error_output = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error_output):
            # Создаем безопасное окружение с эмуляцией input
            input_simulator = InputSimulator(inputs)
            
            safe_globals = {
                '__builtins__': __builtins__,
                'math': math,
                'time': time,
                'os': os,
                'print': print,
                'input': input_simulator  # Подменяем input на нашу эмуляцию
            }
            
            # Выполняем код
            exec(code, safe_globals)
        
        result = output.getvalue()
        error = error_output.getvalue()
        
        # Проверяем, все ли входные данные были использованы
        if hasattr(input_simulator, 'index') and input_simulator.index < len(inputs):
            result += f"\n[Предупреждение] Использовано только {input_simulator.index} из {len(inputs)} входных данных"
        
        if error:
            return jsonify({'output': result, 'error': error})
        else:
            return jsonify({'output': result, 'error': None})
            
    except Exception as e:
        return jsonify({
            'output': '',
            'error': f'Ошибка выполнения: {str(e)}'
        })
        

# Проверка решения задачи
@app.route('/api/check-task', methods=['POST'])
def check_task():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    code = data.get('code', '')
    task_id = data.get('task_id')
    expected_output = data.get('expected_output', '').strip()
    
    if not code:
        return jsonify({'error': 'Код не может быть пустым'}), 400
    
    # Проверяем код на безопасность
    if not is_code_safe(code):
        return jsonify({
            'correct': False,
            'output': '',
            'error': 'Обнаружены запрещенные операции. Разрешены только модули: math, time, os'
        })
    
    # Захватываем вывод
    output = io.StringIO()
    error_output = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error_output):
            # Создаем безопасное окружение
            safe_globals = {
                '__builtins__': __builtins__,
                'math': math,
                'time': time,
                'os': os,
                'print': print
            }
            
            # Выполняем код
            exec(code, safe_globals)
        
        result = output.getvalue().strip()
        error = error_output.getvalue()
        
        if error:
            return jsonify({
                'correct': False,
                'output': result,
                'error': error
            })
        
        # Сравниваем с ожидаемым результатом
        is_correct = (result == expected_output)
        
        # Если задача решена правильно, начисляем монеты
        if is_correct and task_id:
            email = session['user']['email']
            
            # Проверяем, не решал ли уже эту задачу
            solved_tasks_key = f'solved_tasks_{task_id}'
            if solved_tasks_key not in users[email]:
                users[email][solved_tasks_key] = True
                
                # Начисляем монеты (10 PYTH за задачу)
                users[email]['balance'] = users[email].get('balance', 0) + 10
                
                # Записываем транзакцию
                transaction = {
                    'id': str(uuid.uuid4())[:8],
                    'type': 'bonus',
                    'amount': 10,
                    'date': datetime.now(),
                    'description': f'Бонус за решение задачи #{task_id}'
                }
                
                if 'transaction_history' not in users[email]:
                    users[email]['transaction_history'] = []
                users[email]['transaction_history'].append(transaction)
                
                # Обновляем сессию
                session['user']['balance'] = users[email]['balance']
                
                new_balance = users[email]['balance']
            else:
                new_balance = users[email]['balance']
        else:
            new_balance = session['user']['balance']
        
        return jsonify({
            'correct': is_correct,
            'output': result,
            'error': None,
            'new_balance': new_balance if is_correct and task_id else None
        })
        
    except Exception as e:
        return jsonify({
            'correct': False,
            'output': '',
            'error': f'Ошибка выполнения: {str(e)}'
        })

# Добавляем маршрут для задач
@app.route('/tasks/<int:task_id>')
def task_page(task_id):
    if 'user' not in session:
        flash('Войдите, чтобы решать задачи', 'info')
        return redirect(url_for('login'))
    
    # Информация о задачах с тестами
    tasks_info = {
        1: {
            'title': 'Привет, мир!',
            'difficulty': 'Легкая',
            'time': 5,
            'reward': 10,
            'description': 'Напишите программу, которая выводит на экран фразу "Привет, мир!".',
            'example_code': '',
            'hint': 'Используйте функцию print(). Текст должен быть точно таким же, включая заглавную букву и восклицательный знак.',
            'tests': [
                {
                    'input': [],
                    'expected': 'Привет, мир!',
                    'description': 'Простой вывод'
                }
            ]
        },
        2: {
            'title': 'Сумма двух чисел',
            'difficulty': 'Легкая',
            'time': 7,
            'reward': 15,
            'description': 'Напишите программу, которая считывает два числа и выводит их сумму.',
            'example_code': '',
            'hint': 'Используйте input() для ввода и int() для преобразования в число.',
            'tests': [
                {
                    'input': ['5', '3'],
                    'expected': '8',
                    'description': '5 + 3 = 8'
                },
                {
                    'input': ['10', '20'],
                    'expected': '30',
                    'description': '10 + 20 = 30'
                },
                {
                    'input': ['-5', '12'],
                    'expected': '7',
                    'description': '-5 + 12 = 7'
                },
                {
                    'input': ['0', '0'],
                    'expected': '0',
                    'description': '0 + 0 = 0'
                }
            ]
        },
        3: {
            'title': 'Приветствие',
            'difficulty': 'Легкая',
            'time': 7,
            'reward': 15,
            'description': 'Напишите программу, которая считывает имя и выводит приветствие в формате "Привет, {имя}!".',
            'example_code': '',
            'hint': 'Используйте f-строки для форматирования.',
            'tests': [
                {
                    'input': ['Анна'],
                    'expected': 'Привет, Анна!',
                    'description': 'Приветствие Анны'
                },
                {
                    'input': ['Иван'],
                    'expected': 'Привет, Иван!',
                    'description': 'Приветствие Ивана'
                },
                {
                    'input': ['Мария'],
                    'expected': 'Привет, Мария!',
                    'description': 'Приветствие Марии'
                }
            ]
        }
    }
    
    task_info = tasks_info.get(task_id)
    if not task_info:
        flash('Задача не найдена', 'error')
        return redirect(url_for('tasks'))
    
    email = session['user']['email']
    user_data = users[email]
    
    # Проверяем, решена ли уже задача
    solved_tasks_key = f'solved_tasks_{task_id}'
    task_info['is_solved'] = solved_tasks_key in user_data
    task_info['number'] = task_id
    
    return render_template('task.html', task=task_info, user=user_data)

# Страница со списком задач
@app.route('/tasks')
def tasks():
    if 'user' not in session:
        flash('Войдите, чтобы решать задачи', 'info')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email]
    
    # Информация о всех задачах
    tasks_info = [
        {
            'id': 1,
            'title': 'Привет, мир!',
            'difficulty': 'Легкая',
            'time': 5,
            'reward': 1,
            'description': 'Вывод текста на экран',
            'icon': 'fa-solid fa-code',
            'color': '#10b981',
            'category': 'Основы'
        },
        {
            'id': 2,
            'title': 'Сумма двух чисел',
            'difficulty': 'Легкая',
            'time': 7,
            'reward': 1,
            'description': 'Ввод чисел и вывод суммы',
            'icon': 'fa-solid fa-calculator',
            'color': '#3b82f6',
            'category': 'Ввод/Вывод'
        },
        {
            'id': 3,
            'title': 'Приветствие',
            'difficulty': 'Легкая',
            'time': 7,
            'reward': 1,
            'description': 'Ввод имени и вывод приветствия',
            'icon': 'fa-solid fa-user',
            'color': '#8b5cf6',
            'category': 'Строки'
        },
        {
            'id': 4,
            'title': 'Максимум из двух',
            'difficulty': 'Легкая',
            'time': 10,
            'reward': 1,
            'description': 'Поиск максимального числа',
            'icon': 'fa-solid fa-chart-line',
            'color': '#f59e0b',
            'category': 'Условия'
        },
        {
            'id': 5,
            'title': 'Четное или нечетное',
            'difficulty': 'Легкая',
            'time': 1,
            'reward': 20,
            'description': 'Проверка числа на четность',
            'icon': 'fa-solid fa-divide',
            'color': '#ef4444',
            'category': 'Условия'
        },
        {
            'id': 6,
            'title': 'Таблица умножения',
            'difficulty': 'Легкая',
            'time': 11,
            'reward': 25,
            'description': 'Вывод таблицы умножения для числа',
            'icon': 'fa-solid fa-times',
            'color': '#ec4899',
            'category': 'Циклы'
        },
        {
            'id': 7,
            'title': 'Факториал',
            'difficulty': 'Средняя',
            'time': 2,
            'reward': 25,
            'description': 'Вычисление факториала числа',
            'icon': 'fa-solid fa-exclamation',
            'color': '#14b8a6',
            'category': 'Циклы'
        },
        {
            'id': 8,
            'title': 'Палиндром',
            'difficulty': 'Средняя',
            'time': 2,
            'reward': 30,
            'description': 'Проверка, является ли строка палиндромом',
            'icon': 'fa-solid fa-rotate-left',
            'color': '#f97316',
            'category': 'Строки'
        },
        {
            'id': 9,
            'title': 'Список чисел',
            'difficulty': 'Средняя',
            'time': 2,
            'reward': 30,
            'description': 'Сумма и произведение списка чисел',
            'icon': 'fa-solid fa-list',
            'color': '#6b7280',
            'category': 'Списки'
        },
        {
            'id': 10,
            'title': 'Простые числа',
            'difficulty': 'Средняя',
            'time': 2,
            'reward': 35,
            'description': 'Поиск всех простых чисел до N',
            'icon': 'fa-solid fa-star',
            'color': '#a855f7',
            'category': 'Алгоритмы'
        }
    ]
    
    # Добавляем информацию о решенных задачах
    for task in tasks_info:
        solved_key = f'solved_tasks_{task["id"]}'
        task['solved'] = solved_key in user_data
    
    solved_count = sum(1 for task in tasks_info if task['solved'])
    total_reward = sum(task['reward'] for task in tasks_info if task['solved'])
    
    return render_template('tasks.html', 
                         tasks=tasks_info, 
                         user=user_data,
                         solved_count=solved_count,
                         total_reward=total_reward,
                         total_tasks=len(tasks_info))
    

# Главная страница
@app.route('/')
def main():
    return render_template('main.html')

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if email in users and users[email]['password'] == password:
            user_data = users[email].copy()
            user_data['email'] = email
            user_data['logged_in'] = True
            
            users[email]['last_active'] = datetime.now()
            user_data['tag'] = get_user_tag(user_data['total_hours'])
            
            session['user'] = user_data
            if remember:
                session.permanent = True
            
            flash(f'Добро пожаловать, {user_data["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name', email.split('@')[0])
        
        if email in users:
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('register'))
        
        users[email] = {
            'password': password,
            'name': name,
            'registered': datetime.now(),
            'total_hours': 0,
            'courses_completed': 0,
            'current_course': 'Python для начинающих',
            'course_progress': 0,
            'achievements': [],
            'last_active': datetime.now(),
            'balance': 500,
            'purchased_courses': [1, 2, 3, 4, 5],
            'transaction_history': [
                {'id': str(uuid.uuid4())[:8], 'type': 'bonus', 'amount': 500, 
                 'date': datetime.now(), 'description': 'Приветственный бонус'}
            ],
            'chat_history': [
                {'role': 'assistant', 'content': f'Привет, {name}! Я твой персональный GPT-4 помощник по Python. Задавай любые вопросы по коду, учебе или проектам!', 'timestamp': datetime.now()}
            ],
            'course_progress_data': {
                1: {'current_lesson': 0, 'completed': False},
                2: {'current_lesson': 0, 'completed': False},
                3: {'current_lesson': 0, 'completed': False},
                4: {'current_lesson': 0, 'completed': False},
                5: {'current_lesson': 0, 'completed': False}
            }
        }
        
        flash('Регистрация успешна! Вы получили 500 PYTH в подарок!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Личный кабинет
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email].copy()
    user_data['email'] = email
    user_data['achievements'] = get_achievements(user_data)
    user_data['days_active'] = (datetime.now() - user_data['registered']).days
    user_data['avg_hours_per_day'] = round(user_data['total_hours'] / max(1, user_data['days_active']), 1)
    
    purchased = []
    for course in courses_list:
        if course['id'] in user_data['purchased_courses']:
            course_copy = course.copy() # Копируем, чтобы не менять оригинальный словарь курса
            # Добавляем прогресс для каждого курса
            progress_data = user_data.get('course_progress_data', {}).get(course['id'], {})
            course_copy['current_lesson'] = progress_data.get('current_lesson', 0)
            course_copy['completed'] = progress_data.get('completed', False)
            total_lessons = course['lessons']
            course_copy['progress'] = int((course_copy['current_lesson'] / total_lessons) * 100) if total_lessons > 0 else 0
            purchased.append(course_copy)
    
    user_data['purchased_courses_count'] = len(purchased)
    user_data['balance'] = user_data.get('balance', 0)
    
    return render_template('dashboard.html', user=user_data, purchased_courses=purchased[:3])

# Профиль пользователя
@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Необходимо авторизоваться', 'warning')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email].copy()
    user_data['email'] = email
    user_data['tag'] = get_user_tag(user_data['total_hours'])
    user_data['achievements'] = get_achievements(user_data)
    user_data['level'] = min(99, user_data['total_hours'] // 10 + 1)
    user_data['next_level_hours'] = (user_data['level'] * 10) - user_data['total_hours']
    user_data['days_active'] = (datetime.now() - user_data['registered']).days
    user_data['avg_hours_per_day'] = round(user_data['total_hours'] / max(1, user_data['days_active']), 1)
    
    user_data['balance'] = user_data.get('balance', 0)
    user_data['transaction_history'] = user_data.get('transaction_history', [])
    user_data['transaction_history'].sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('profile.html', user=user_data)

# Страница с ценами
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# Страница с курсами
@app.route('/courses')
def courses():
    if 'user' not in session:
        flash('Войдите, чтобы просматривать курсы', 'info')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email]
    
    # Добавляем прогресс пользователя к данным курсов
    enhanced_courses = []
    for course in courses_list:
        course_copy = course.copy()
        if course['id'] in user_data.get('course_progress_data', {}):
            progress = user_data['course_progress_data'][course['id']]
            course_copy['current_lesson'] = progress.get('current_lesson', 0)
            course_copy['completed'] = progress.get('completed', False)
            course_copy['is_purchased'] = course['id'] in user_data.get('purchased_courses', [])
        else:
            course_copy['current_lesson'] = 0
            course_copy['completed'] = False
            course_copy['is_purchased'] = course['id'] in user_data.get('purchased_courses', [])
        enhanced_courses.append(course_copy)
    
    return render_template('courses.html', courses=enhanced_courses, user=user_data)

# Страница конкретного курса
@app.route('/course/<int:course_id>')
def course_page(course_id):
    if 'user' not in session:
        flash('Войдите, чтобы просматривать курсы', 'info')
        return redirect(url_for('login'))
    
    if course_id not in courses_meta:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses'))
    
    email = session['user']['email']
    user_data = users[email]
    
    course_meta = courses_meta[course_id].copy()
    course_meta['id'] = course_id
    
    # Проверяем доступ к курсу
    if course_meta['price_coins'] > 0 and course_id not in user_data.get('purchased_courses', []):
        flash(f'Этот курс нужно купить за {course_meta["price_coins"]} PYTH', 'warning')
        return redirect(url_for('courses'))
    
    # Получаем прогресс
    progress = 0
    if course_id in user_data.get('course_progress_data', {}):
        current = user_data['course_progress_data'][course_id].get('current_lesson', 0)
        total = course_meta['lessons']
        progress = int((current / total) * 100) if total > 0 else 0
    
    # Определяем шаблон для курса
    template_map = {
        1: 'course1_python_basics.html',
        2: 'course2_operations.html',
        3: 'course3_loops.html',
        4: 'course4_lists.html',
        5: 'course5_dicts.html',
        6: 'course6_functions.html',
        7: 'course7_oop.html',
        8: 'course8_files.html',
        9: 'course9_exceptions.html',
        10: 'course10_modules.html',
        11: 'course11_testing.html',
        12: 'course12_async.html'
    }
    
    template = template_map.get(course_id, 'course_template.html')
    
    return render_template(template, 
                          course=course_meta, 
                          user=user_data,
                          progress=progress,
                          current_lesson=user_data.get('course_progress_data', {}).get(course_id, {}).get('current_lesson', 0))

# API для сохранения прогресса
@app.route('/api/save-progress', methods=['POST'])
def save_progress():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    course_id = data.get('course_id')
    lesson_index = data.get('lesson_index')
    completed = data.get('completed', False)
    
    email = session['user']['email']
    
    if 'course_progress_data' not in users[email]:
        users[email]['course_progress_data'] = {}
    
    if course_id not in users[email]['course_progress_data']:
        users[email]['course_progress_data'][course_id] = {'current_lesson': 0, 'completed': False}
    
    users[email]['course_progress_data'][course_id]['current_lesson'] = lesson_index + 1
    
    if completed and lesson_index + 1 >= courses_meta[course_id]['lessons']:
        users[email]['course_progress_data'][course_id]['completed'] = True
        users[email]['courses_completed'] += 1
        users[email]['balance'] = users[email].get('balance', 0) + 50
        
        transaction = {
            'id': str(uuid.uuid4())[:8],
            'type': 'bonus',
            'amount': 50,
            'date': datetime.now(),
            'description': f'Бонус за завершение курса {courses_meta[course_id]["title"]}'
        }
        users[email]['transaction_history'].append(transaction)
        
        session['user']['courses_completed'] = users[email]['courses_completed']
        session['user']['balance'] = users[email]['balance']
    
    session['user']['course_progress_data'] = users[email]['course_progress_data']
    
    return jsonify({'success': True})

# Мои курсы
@app.route('/my-courses')
def my_courses():
    if 'user' not in session:
        flash('Необходимо авторизоваться', 'warning')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email]
    
    purchased = []
    for course_id in user_data.get('purchased_courses', []):
        if course_id in courses_meta:
            course = courses_meta[course_id].copy()
            course['id'] = course_id
            if course_id in user_data.get('course_progress_data', {}):
                progress_data = user_data['course_progress_data'][course_id]
                course['current_lesson'] = progress_data.get('current_lesson', 0)
                course['completed'] = progress_data.get('completed', False)
                course['progress'] = int((course['current_lesson'] / course['lessons']) * 100) if course['lessons'] > 0 else 0
            else:
                course['current_lesson'] = 0
                course['completed'] = False
                course['progress'] = 0
            purchased.append(course)
    
    return render_template('my_courses.html', user=user_data, courses=purchased)

# Покупка курса
@app.route('/buy-course/<int:course_id>', methods=['POST'])
def buy_course(course_id):
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    if course_id not in courses_meta:
        return jsonify({'error': 'Курс не найден'}), 404
    
    course = courses_meta[course_id]
    
    if course['price_coins'] == 0:
        return jsonify({'error': 'Этот курс бесплатный'}), 400
    
    email = session['user']['email']
    user_data = users[email]
    
    if course_id in user_data.get('purchased_courses', []):
        return jsonify({'error': 'Курс уже приобретен'}), 400
    
    if user_data.get('balance', 0) < course['price_coins']:
        return jsonify({'error': 'Недостаточно средств', 'needed': course['price_coins'], 'balance': user_data.get('balance', 0)}), 400
    
    # Списываем монеты
    users[email]['balance'] = user_data['balance'] - course['price_coins']
    
    # Добавляем курс в purchased_courses
    if 'purchased_courses' not in users[email]:
        users[email]['purchased_courses'] = []
    users[email]['purchased_courses'].append(course_id)
    
    # Инициализируем прогресс для нового курса
    if 'course_progress_data' not in users[email]:
        users[email]['course_progress_data'] = {}
    users[email]['course_progress_data'][course_id] = {'current_lesson': 0, 'completed': False}
    
    # Записываем транзакцию
    transaction = {
        'id': str(uuid.uuid4())[:8],
        'type': 'purchase',
        'amount': -course['price_coins'],
        'date': datetime.now(),
        'description': f'Покупка курса "{course["title"]}"'
    }
    
    if 'transaction_history' not in users[email]:
        users[email]['transaction_history'] = []
    users[email]['transaction_history'].append(transaction)
    
    # Обновляем сессию
    session['user']['balance'] = users[email]['balance']
    session['user']['purchased_courses'] = users[email]['purchased_courses']
    session['user']['course_progress_data'] = users[email]['course_progress_data']
    
    return jsonify({
        'success': True,
        'message': f'Курс "{course["title"]}" успешно приобретен!',
        'new_balance': users[email]['balance']
    })

# Магазин монет
@app.route('/shop')
def shop():
    if 'user' not in session:
        flash('Необходимо авторизоваться', 'warning')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email]
    
    coin_packages = [
        {'id': 1, 'coins': 100, 'price': 99, 'popular': False, 'bonus': 0},
        {'id': 2, 'coins': 500, 'price': 449, 'popular': True, 'bonus': 50},
        {'id': 3, 'coins': 1000, 'price': 899, 'popular': False, 'bonus': 100},
        {'id': 4, 'coins': 2500, 'price': 1999, 'popular': False, 'bonus': 300},
        {'id': 5, 'coins': 5000, 'price': 3999, 'popular': False, 'bonus': 750},
    ]
    
    return render_template('shop.html', user=user_data, packages=coin_packages)

# Покупка монет
@app.route('/buy-coins', methods=['POST'])
def buy_coins():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    package_id = int(request.form.get('package_id'))
    payment_method = request.form.get('payment_method')
    
    coin_packages = {
        1: {'coins': 100, 'price': 99, 'bonus': 0},
        2: {'coins': 500, 'price': 449, 'bonus': 50},
        3: {'coins': 1000, 'price': 899, 'bonus': 100},
        4: {'coins': 2500, 'price': 1999, 'bonus': 300},
        5: {'coins': 5000, 'price': 3999, 'bonus': 750},
    }
    
    if package_id not in coin_packages:
        flash('Неверный пакет', 'error')
        return redirect(url_for('shop'))
    
    package = coin_packages[package_id]
    total_coins = package['coins'] + package['bonus']
    
    email = session['user']['email']
    users[email]['balance'] = users[email].get('balance', 0) + total_coins
    
    transaction = {
        'id': str(uuid.uuid4())[:8],
        'type': 'deposit',
        'amount': total_coins,
        'price': package['price'],
        'payment_method': payment_method,
        'date': datetime.now(),
        'description': f'Пополнение баланса: {package["coins"]} PYTH + {package["bonus"]} бонус'
    }
    
    if 'transaction_history' not in users[email]:
        users[email]['transaction_history'] = []
    users[email]['transaction_history'].append(transaction)
    
    session['user']['balance'] = users[email]['balance']
    
    flash(f'Баланс пополнен на {total_coins} PYTH!', 'success')
    return redirect(url_for('profile'))

# ИИ-помощник
@app.route('/ai-assistant')
def ai_assistant():
    if 'user' not in session:
        flash('Войдите, чтобы использовать ИИ-помощника', 'info')
        return redirect(url_for('login'))
    
    email = session['user']['email']
    user_data = users[email]
    
    chat_history = user_data.get('chat_history', [])
    
    return render_template('ai_assistant.html', user=user_data, chat_history=chat_history)

# API для чата
@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Пустое сообщение'}), 400
    
    email = session['user']['email']
    user_name = users[email]['name']
    
    if 'chat_history' not in users[email]:
        users[email]['chat_history'] = []
    
    chat_history = users[email]['chat_history']
    
    user_msg = {
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now()
    }
    chat_history.append(user_msg)
    
    ai_response = get_ai_response(user_message, chat_history, user_name)
    
    assistant_msg = {
        'role': 'assistant',
        'content': ai_response,
        'timestamp': datetime.now()
    }
    chat_history.append(assistant_msg)
    
    if len(chat_history) > 50:
        users[email]['chat_history'] = chat_history[-50:]
    
    return jsonify({
        'response': ai_response,
        'timestamp': datetime.now().isoformat()
    })

# Очистка чата
@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    email = session['user']['email']
    
    users[email]['chat_history'] = [
        {'role': 'assistant', 'content': f'Привет, {users[email]["name"]}! Я твой персональный GPT-4 помощник по Python. Чем могу помочь сегодня?', 'timestamp': datetime.now()}
    ]
    
    return jsonify({'success': True})

# Добавление прогресса (демо)
@app.route('/add-progress')
def add_progress():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']['email']
    users[email]['total_hours'] += 1
    users[email]['course_progress'] = min(100, users[email]['course_progress'] + 2)
    
    if users[email]['course_progress'] >= 100:
        users[email]['courses_completed'] += 1
        users[email]['course_progress'] = 0
        courses = ['Django для профи', 'FastAPI', 'Асинхронный Python', 'Python для Data Science']
        users[email]['current_course'] = random.choice(courses)
        
        users[email]['balance'] = users[email].get('balance', 0) + 50
        transaction = {
            'id': str(uuid.uuid4())[:8],
            'type': 'bonus',
            'amount': 50,
            'date': datetime.now(),
            'description': 'Бонус за завершение курса'
        }
        users[email]['transaction_history'].append(transaction)
        
        flash('🎉 Поздравляем! Вы завершили курс! +50 PYTH', 'success')
    
    session['user']['total_hours'] = users[email]['total_hours']
    session['user']['course_progress'] = users[email]['course_progress']
    session['user']['courses_completed'] = users[email]['courses_completed']
    session['user']['balance'] = users[email].get('balance', 0)
    
    flash('⏱️ Прогресс обновлен! +1 час обучения', 'success')
    return redirect(url_for('profile'))

# API для обновления времени на платформе
@app.route('/api/update-time', methods=['POST'])
def update_time():
    if 'user' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    seconds_to_add = data.get('seconds', 3)  # По умолчанию добавляем 3 секунды
    
    if seconds_to_add <= 0:
        return jsonify({'error': 'Количество секунд должно быть положительным'}), 400
    
    email = session['user']['email']
    
    # Конвертируем секунды в часы (с сохранением дробной части)
    hours_to_add = seconds_to_add / 3600  # 3600 секунд = 1 час
    
    # Добавляем время
    users[email]['total_hours'] = users[email].get('total_hours', 0) + hours_to_add
    
    # Обновляем last_active
    users[email]['last_active'] = datetime.now()
    
    # Обновляем сессию
    session['user']['total_hours'] = users[email]['total_hours']
    
    # Форматируем время для отображения
    total_seconds = int(users[email]['total_hours'] * 3600)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return jsonify({
        'success': True,
        'new_total_hours': users[email]['total_hours'],
        'time_formatted': time_formatted,
        'message': f'Время обновлено'
    })


# Выход
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)