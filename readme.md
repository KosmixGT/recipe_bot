# Рецепт-бот 🍳

Telegram-бот для поиска рецептов по имеющимся ингредиентам. Поддерживает русский и английский языки.

## Возможности

- Поиск рецептов по ингредиентам
- Два режима поиска:
  - Строгий поиск (должны присутствовать все ингредиенты)
  - Гибкий поиск (любой из ингредиентов)
- Фильтрация рецептов:
  - Самые калорийные
  - Самые полезные 
  - Показать все
- Аналитика рецептов:
  - Сравнение питательной ценности
  - Распределение по уровню полезности
  - Анализ калорийности
  - Анализ стоимости
  - Анализ используемых ингредиентов
- Подробная информация о рецепте:
  - Инструкция приготовления
  - Пищевая ценность
  - Оценка полезности
  - Цена за порцию

## Технологии

- Python 3.9+
- python-telegram-bot
- Spoonacular API
- pandas
- matplotlib
- seaborn
- deep-translator

## Установка

1. Клонировать репозиторий
2. Установить зависимости:
```bash
pip install -r requirements.txt
```
3. Настроить переменные окружения в config/config.py:
* TELEGRAM_TOKEN
* SPOONACULAR_API_KEY

4. Запустить бота:
```bash
python main.py
```
## Использование

1.	Начать чат с @your_recipe_bot
2.	Отправить список ингредиентов (через запятую или пробел)
3.	Выбрать режим поиска
4.	Просмотреть и отфильтровать рецепты
5.	Посмотреть аналитику рецептов
6.	Получить инструкции по приготовлению

## Структура проекта

recipe_bot/
├── config/
│   └── config.py
├── src/
│   ├── bot/
│   │   ├── handlers.py
│   │   └── filters.py
│   ├── services/
│   │   ├── recipe_service.py
│   │   ├── translator.py
│   │   └── analytics_service.py
│   └── utils/
│       └── helpers.py
└── main.py