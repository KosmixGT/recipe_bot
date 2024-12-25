import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
from src.services.translator import translate_to_russian

def create_nutrition_comparison(recipes):
    """Bar chart comparing calories and health scores"""
    df = pd.DataFrame(recipes)
    plt.figure(figsize=(10, 6))
    x = range(len(df))
    width = 0.35
    
    plt.bar(x, df['calories'], width, label='Калории', color='salmon')
    plt.bar([i + width for i in x], df['healthScore'], width, label='Полезность', color='lightgreen')
    
    plt.xlabel('Рецепты')
    plt.ylabel('Значение')
    plt.title('Сравнение калорийности и полезности рецептов')
    plt.legend()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_health_distribution(recipes):
    """Pie chart showing health score distribution"""
    df = pd.DataFrame(recipes)
    plt.figure(figsize=(12, 8))
    
    health_bins = ['0-25', '26-50', '51-75', '76-100']
    df['health_category'] = pd.cut(df['healthScore'], bins=[0, 25, 50, 75, 100], labels=health_bins)
    health_dist = df['health_category'].value_counts()
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(health_dist)))
    wedges, texts, autotexts = plt.pie(health_dist, labels=health_dist.index, 
                                      autopct='%1.1f%%', colors=colors,
                                      textprops={'fontsize': 12},
                                      pctdistance=0.85)
    
    # Make percentage labels white and larger
    plt.setp(autotexts, size=14, weight="bold", color="white")
    # Make category labels larger
    plt.setp(texts, size=12)
    
    plt.title('Распределение рецептов по уровню полезности', pad=20, size=14)
    
    # Add legend
    plt.legend(wedges, health_dist.index,
              title="Уровни полезности",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_calorie_ranges(recipes):
    """Horizontal bar chart showing calorie ranges"""
    df = pd.DataFrame(recipes)
    plt.figure(figsize=(10, 6))
    
    calorie_bins = ['0-300', '301-600', '601-900', '900+']
    df['calorie_category'] = pd.cut(df['calories'], bins=[0, 300, 600, 900, float('inf')], labels=calorie_bins)
    calorie_dist = df['calorie_category'].value_counts()
    
    plt.barh(calorie_dist.index, calorie_dist.values, color='lightcoral')
    plt.xlabel('Количество рецептов')
    plt.ylabel('Диапазон калорий')
    plt.title('Распределение рецептов по калорийности')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_price_analysis(recipes):
    """Create visualization for recipe prices"""
    plt.figure(figsize=(12, 6))
    
    # Exchange rate USD to RUB (можно обновлять при необходимости)
    usd_to_rub = 99.91
    
    prices = []
    names = []
    for recipe in recipes:
        if 'pricePerServing' in recipe:
            # Convert cents to rubles
            price_in_rubles = (recipe['pricePerServing']/100) * usd_to_rub
            prices.append(price_in_rubles)
            names.append(recipe['title'])
    
    if prices:
        bars = plt.bar(range(len(prices)), prices, color='teal')
        plt.xticks(range(len(names)), names, rotation=45, ha='right')
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}₽',
                    ha='center', va='bottom')
    
    plt.xlabel('Рецепты')
    plt.ylabel('Цена за порцию (₽)')
    plt.title('Сравнение стоимости рецептов')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def create_ingredients_analysis(recipes):
    """Analyze most common ingredients"""
    all_ingredients = []
    for recipe in recipes:
        if 'extendedIngredients' in recipe:
            ingredients = recipe['extendedIngredients']
            # Translate each ingredient name to Russian
            all_ingredients.extend([translate_to_russian(ing['name']) for ing in ingredients])
    
    if all_ingredients:
        plt.figure(figsize=(12, 6))
        ingredient_counts = pd.Series(all_ingredients).value_counts()
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(ingredient_counts[:10])))
        bars = plt.bar(range(len(ingredient_counts[:10])), ingredient_counts[:10].values, color=colors)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.xticks(range(len(ingredient_counts[:10])), ingredient_counts[:10].index,
                  rotation=45, ha='right')
        plt.title('Топ-10 часто используемых ингредиентов')
        plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def generate_analytics(recipes):
    return {
        'nutrition_comparison': create_nutrition_comparison(recipes),
        'health_distribution': create_health_distribution(recipes),
        'calorie_ranges': create_calorie_ranges(recipes),
        'price_analysis': create_price_analysis(recipes),
        'ingredients_analysis': create_ingredients_analysis(recipes)
    }
