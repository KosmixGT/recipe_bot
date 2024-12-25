DEFAULT_RECIPE_IMAGE = "https://lh3.googleusercontent.com/proxy/FgRa3A2R--m9aYq5RLDbnYgxkWuAW3ZMxxJwGEEPduVM7_f_LFAFLTytF6sV8jXUKZ1lt16ujFn_3JatSiTd"  # or any other default image URL

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.recipe_service import get_recipes, _get_recipe_details
from src.services.translator import translate_to_english, clean_and_translate_instructions
from src.bot.filters import recipe_filters
from src.services.analytics_service import generate_analytics

logger = logging.getLogger(__name__)

class MessageHandlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Добро пожаловать в Рецепт-бот! 🍳\n\n"
            "• Отправьте мне список ингредиентов через запятую или пробел\n"
            "• Можно писать на русском или английском языке\n"
            "• Пример: томаты, курица, рис\n"
            "• Example: tomatoes chicken rice\n\n"
            "Я найду для вас подходящие рецепты! 👨‍🍳"
        )

    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        # logger.info(f"Received message: {user_input}")
        
        # Store ingredients in context
        context.user_data['ingredients'] = user_input
        
        # Ask user for search preference
        await update.message.reply_text(
            "Выберите тип поиска:\n\n"
            "🔍 Строгий поиск - найти рецепты, содержащие ВСЕ указанные ингредиенты\n"
            "🔎 Гибкий поиск - найти рецепты, содержащие ЛЮБЫЕ из указанных ингредиентов",
            reply_markup=ButtonHandlers.get_search_type_buttons()
    )
    

class ButtonHandlers:
    @staticmethod
    def get_search_type_buttons():
        buttons = [
            [
                InlineKeyboardButton("Строгий поиск (все ингредиенты)", callback_data="strict_search"),
                InlineKeyboardButton("Гибкий поиск", callback_data="flexible_search")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    @staticmethod
    def get_recipe_buttons(recipe):
        buttons = [
            [
                InlineKeyboardButton("Посмотреть на сайте", url=recipe['url']),
                InlineKeyboardButton("Инструкция приготовления", callback_data=f"instructions_{str(recipe['id'])}")
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_filter_buttons():
        buttons = [
            [InlineKeyboardButton("Самые калорийные", callback_data="most_caloric")],
            [InlineKeyboardButton("Самые полезные", callback_data="most_healthy")],
            [InlineKeyboardButton("Покажи все", callback_data="show_all")],
            [InlineKeyboardButton("📊 Анализ рецептов", callback_data="analytics")]
        ]
        return InlineKeyboardMarkup(buttons)

    
    @staticmethod
    async def handle_search_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data in ["strict_search", "flexible_search"]:
            # Show processing message
            processing_message = await query.message.reply_text(
                "🔍 Ищу рецепты по вашим ингредиентам...\nЭто может занять несколько секунд."
            )
            
            # Get ingredients from context and translate
            ingredients = [translate_to_english(i.strip()) 
                        for i in context.user_data['ingredients'].split(",")]
            
            # Get recipes with appropriate ranking
            ranking = 1 if query.data == "strict_search" else 2
            recipes = get_recipes(ingredients, number=1, ranking=ranking)
            
            # Clean up processing message
            await processing_message.delete()
            
            context.user_data['recipes'] = recipes
            
            if recipes:
                await query.message.reply_text(
                    "Выберите, что вы хотите увидеть:\n" +
                    "Самые калорийные - топ-5 самых калорийных рецептов\n" +
                    "Самые полезные - топ-5 самых полезных рецептов\n" +
                    "Показать все - все найденные рецепты",
                    reply_markup=ButtonHandlers.get_filter_buttons()
                )
            else:
                await query.message.reply_text(
                    "К сожалению, рецепты для данных ингредиентов не найдены."
                )

    @staticmethod
    async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data in ["most_caloric", "most_healthy", "show_all"]:
            recipes = context.user_data.get('recipes', [])
            filtered_recipes = recipe_filters[query.data](recipes)
            
            for recipe in filtered_recipes:
                caption = (
                    f"🍳 {recipe['title']}\n\n"
                    f"📝 {_truncate_text(recipe['summary'])}\n\n"
                    f"🔥 Калории: {recipe['calories']} ккал.\n"
                    f"💪 Полезность: {recipe['healthScore']}/100"
                )
                
                try:
                    await query.message.reply_photo(
                        photo=recipe['image'],
                        caption=caption,
                        reply_markup=ButtonHandlers.get_recipe_buttons(recipe)
                    )
                except:
                    try:
                        await query.message.reply_photo(
                            photo=DEFAULT_RECIPE_IMAGE,
                            caption=caption,
                            reply_markup=ButtonHandlers.get_recipe_buttons(recipe)
                        )
                    except:
                        await query.message.reply_text(
                            caption,
                            reply_markup=ButtonHandlers.get_recipe_buttons(recipe)
                        )

        elif query.data.startswith('instructions_'):
            recipe_id = query.data.split('_')[1]
            recipes = context.user_data.get('recipes', [])
            recipe = next((r for r in recipes if str(r['id']) == recipe_id), None)
            
            if recipe and recipe.get('instructions'):
                truncated_instructions = _truncate_text(recipe['instructions'], max_length=800, add_site_reference=True)
                await query.message.reply_text(truncated_instructions)
            else:
                await query.message.reply_text("Инструкции для этого рецепта недоступны")
        
        elif query.data == "analytics":
            recipes = context.user_data.get('recipes', [])
            if recipes:
                analytics_data = generate_analytics(recipes)
                
                await query.message.reply_photo(
                    photo=analytics_data['nutrition_comparison'],
                    caption="📊 Сравнение калорийности и полезности рецептов"
                )
                
                await query.message.reply_photo(
                    photo=analytics_data['health_distribution'],
                    caption="🥗 Распределение рецептов по уровню полезности"
                )
                
                await query.message.reply_photo(
                    photo=analytics_data['calorie_ranges'],
                    caption="🔥 Распределение рецептов по калорийности"
                )
                
                await query.message.reply_photo(
                    photo=analytics_data['price_analysis'],
                    caption="💰 Анализ стоимости рецептов"
                )
                
                await query.message.reply_photo(
                    photo=analytics_data['ingredients_analysis'],
                    caption="🥘 Анализ используемых ингредиентов"
                )
            else:
                await query.message.reply_text("Сначала найдите рецепты для анализа!")

def _truncate_text(text, max_length=800, add_site_reference=False):
    """Truncate text to fit Telegram limits"""
    site_msg = "\n\nПолную инструкцию смотрите на сайте..." if add_site_reference else "..."
    if len(text) <= max_length:
        return text
    return text[:max_length-len(site_msg)] + site_msg