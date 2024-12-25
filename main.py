import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config.config import TELEGRAM_TOKEN, LOGGING_FORMAT, LOGGING_LEVEL
from src.bot.handlers import MessageHandlers, ButtonHandlers

# Configure logging
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def main():
    """Initialize and start the bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", MessageHandlers.start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE),
        MessageHandlers.handle_message
    ))
    application.add_handler(CallbackQueryHandler(ButtonHandlers.handle_search_type, pattern="^(strict_search|flexible_search)$"))
    application.add_handler(CallbackQueryHandler(ButtonHandlers.handle_button,
        pattern="^(most_caloric|most_healthy|show_all|instructions_.*|analytics)$"))

    # Start the Bot
    logger.info("Запуск бота..")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    main()

