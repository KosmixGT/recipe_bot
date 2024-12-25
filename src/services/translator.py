from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup

def translate_to_english(text):
    """Translate text from Russian to English."""
    return GoogleTranslator(source='ru', target='en').translate(text)

def translate_to_russian(text):
    """Translate text from English to Russian."""
    if not text:
        return ""
    return GoogleTranslator(source='en', target='ru').translate(text)

def clean_and_translate_instructions(instructions):
    if not instructions:
        return "Инструкции отсутствуют"
    
    steps = instructions.split('\n') if '\n' in instructions else instructions.split('.')
    steps = [step.strip() for step in steps if step.strip()]
    
    return "\n\n".join(f"Шаг {i+1}: {translate_to_russian(step)}" 
                      for i, step in enumerate(steps))


def clean_and_translate_summary(summary):
    """Clean HTML from summary and translate to Russian."""
    if not summary:
        return ""
    clean_text = BeautifulSoup(summary, 'html.parser').get_text()
    return translate_to_russian(clean_text)
