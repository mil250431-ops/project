import re
from collections import Counter
import requests
import os
from dotenv import load_dotenv

# Загружаем ключ из файла .env
load_dotenv()
YANDEX_DICT_API_KEY = os.getenv('YANDEX_DICT_API_KEY', '')

def split_into_paragraphs(text):
    paragraphs = text.split('\n')
    return [p.strip() for p in paragraphs if p.strip()]

def count_syllables_ru(word):
    vowels = 'аеёиоуыэюя'
    return sum(1 for char in word.lower() if char in vowels)

def calculate_flesch_reading_ease(text):
    words = re.findall(r'[а-яА-ЯёЁ]+', text)
    sentences = re.split(r'[.!?;]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(re.findall(r'[а-яА-ЯёЁ]+', s)) > 0]
    
    if not words or not sentences:
        return 0.0
    
    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables_ru(word) for word in words)
    
    asl = total_words / total_sentences
    asw = total_syllables / total_words
    fres = 206.835 - (1.3 * asl) - (60.1 * asw)
    
    return round(max(0, min(100, fres)), 2)

def interpret_flesch_score(score):
    if score >= 90:
        return "Очень легко (уровень 5 класса)", "success"
    elif score >= 80:
        return "Легко (уровень 6 класса)", "success"
    elif score >= 70:
        return "Довольно легко (уровень 7 класса)", "primary"
    elif score >= 60:
        return "Средняя сложность (8-9 класс)", "primary"
    elif score >= 50:
        return "Довольно сложно (10-11 класс)", "warning"
    elif score >= 30:
        return "Сложно (студенческий уровень)", "warning"
    else:
        return "Очень сложно (научный текст)", "danger"

def tokenize_words(text):
    return re.findall(r'[а-яА-ЯёЁ]{3,}', text.lower())

def get_word_frequency(text, top_n=50):
    words = tokenize_words(text)
    counter = Counter(words)
    return dict(counter.most_common(top_n))

def analyze_sentiment(text):
    positive_words = {
        'хороший', 'хорошая', 'хорошее', 'хорошо',
        'отличный', 'отличная', 'отличное', 'отлично',
        'прекрасный', 'прекрасная', 'прекрасное', 'прекрасно',
        'замечательный', 'замечательная', 'замечательное', 'замечательно',
        'радость', 'радостный', 'радостная',
        'счастье', 'счастливый', 'счастливая', 'счастливо',
        'любовь', 'любимый', 'любимая', 'люблю', 'любить',
        'добрый', 'добрая', 'доброе', 'добро',
        'красивый', 'красивая', 'красивое', 'красота',
        'милый', 'милая', 'милое',
        'чудесный', 'чудесная', 'чудесное', 'чудо', 'чудесно',
        'великолепный', 'великолепная', 'великолепное', 'великолепно',
        'успех', 'успешный', 'успешно',
        'победа', 'улыбка', 'улыбаться',
        'солнце', 'солнечный', 'солнечная',
        'тепло', 'тёплый', 'тёплая', 'тёплое',
        'уют', 'уютный', 'уютная', 'уютно',
        'смех', 'смеяться', 'весёлый', 'весёлая', 'весело',
        'праздник', 'подарок',
        'мечта', 'мечтать', 'надежда',
        'нежный', 'нежная', 'нежно',
        'ласковый', 'ласковая', 'ласка',
        'приятный', 'приятная', 'приятно',
        'вкусный', 'вкусная', 'вкусно',
        'яркий', 'яркая', 'ярко',
        'свет', 'светлый', 'светлая',
        'подруга', 'друг',
        'классный', 'классная', 'крутой', 'крутая',
        'грациозный', 'грациозная',
        'дом', 'домашний', 'родной',
        'небо', 'звезды', 'луна',
        'песня', 'музыка', 'танец',
        'весна', 'лето', 'цветы',
    }
    
    negative_words = {
        'плохой', 'плохая', 'плохое', 'плохо',
        'ужасный', 'ужасная', 'ужасное', 'ужасно',
        'грусть', 'грустный', 'грустная', 'грустно',
        'печаль', 'печальный', 'печальная', 'печально',
        'злой', 'злая', 'злое', 'злость', 'злиться',
        'страх', 'страшный', 'страшная', 'страшно',
        'боль', 'больной', 'больная', 'больно',
        'горе', 'горестный',
        'беда', 'проблема',
        'ненависть', 'ненавидеть',
        'холод', 'холодный', 'холодная', 'холодно',
        'тьма', 'тёмный', 'тёмная', 'темно',
        'смерть', 'смертельный',
        'война', 'болезнь',
        'слёзы', 'плакать',
        'тоска', 'тоскливый',
        'одиночество', 'одинокий', 'одинокая',
        'обида', 'обидный', 'обидно',
        'усталость', 'усталый', 'усталая', 'устать',
        'скука', 'скучный', 'скучная', 'скучно',
        'тревога', 'тревожный',
        'ужас', 'ужасный',
        'испортилось', 'испорченный',
        'дождь', 'ливень', 'слякоть',
        'ветер', 'ураган', 'буря',
        'осень', 'зима', 'мороз',
    }
    
    words = tokenize_words(text)
    total = len(words)
    
    if total == 0:
        return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}
    
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    positive = pos_count / total
    negative = neg_count / total
    neutral = max(0, 1.0 - positive - negative)
    compound = positive - negative
    
    return {
        'positive': round(positive, 3),
        'negative': round(negative, 3),
        'neutral': round(neutral, 3),
        'compound': round(compound, 3)
    }

def analyze_paragraphs(paragraphs):
    results = []
    for idx, paragraph in enumerate(paragraphs):
        if len(paragraph.strip()) < 10:
            continue
        sentiment = analyze_sentiment(paragraph)
        results.append({
            'index': idx,
            'text': paragraph[:200] + ('...' if len(paragraph) > 200 else ''),
            'full_text': paragraph,
            'positive': sentiment['positive'],
            'negative': sentiment['negative'],
            'neutral': sentiment['neutral'],
            'compound': sentiment['compound']
        })
    return results

def get_synonyms_datamuse(word, max_results=8):
    """
    Ищет синонимы: сначала через API Яндекса, 
    потом через Datamuse, потом в локальном словаре.
    """
    
    # 1. Яндекс.Словарь (лучшее качество для русского)
    yandex_result = _get_yandex_synonyms(word, max_results)
    if yandex_result:
        return yandex_result
    
    # 2. Datamuse API (бесплатный запасной вариант)
    datamuse_result = _get_datamuse_synonyms(word, max_results)
    if datamuse_result:
        return datamuse_result
    
    # 3. Локальный словарь (если интернета нет)
    return _get_fallback_synonyms(word, max_results)


def _get_yandex_synonyms(word, max_results):
    """Получение синонимов через Яндекс.Словарь."""
    if not YANDEX_DICT_API_KEY:
        return []
    
    try:
        # Пробуем через библиотеку yadict, если она установлена
        from yadict.client import YandexDictionaryClient
        client = YandexDictionaryClient(YANDEX_DICT_API_KEY)
        synonyms = client.synonyms(word, 'ru-ru')
        return synonyms[:max_results]
    except ImportError:
        pass
    
    # Если yadict не установлен — пробуем прямой HTTP-запрос
    try:
        url = "https://dictionary.yandex.net/api/v1/dicservice/lookup"
        params = {
            'key': YANDEX_DICT_API_KEY,
            'lang': 'ru-ru',
            'text': word,
        }
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        synonyms = set()
        
        for def_item in data.get('def', []):
            for tr_item in def_item.get('tr', []):
                if 'text' in tr_item:
                    synonyms.add(tr_item['text'])
                if 'syn' in tr_item:
                    for syn in tr_item['syn']:
                        synonyms.add(syn['text'])
        
        return list(synonyms)[:max_results]
    
    except Exception:
        return []


def _get_datamuse_synonyms(word, max_results):
    """Запасной вариант: Datamuse API."""
    try:
        url = "https://api.datamuse.com/words"
        params = {
            'rel_syn': word,
            'max': max_results
        }
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            return [item['word'] for item in response.json()]
    except Exception:
        pass
    return []


def _get_fallback_synonyms(word, max_results):
    """Локальный словарь-заглушка."""
    demo_synonyms = {
        # Прилагательные
        'хороший': ['отличный', 'прекрасный', 'замечательный', 'добрый', 'качественный', 'славный', 'неплохой'],
        'плохой': ['ужасный', 'скверный', 'дурной', 'отвратительный', 'нехороший', 'мерзкий', 'паршивый'],
        'большой': ['огромный', 'крупный', 'гигантский', 'великий', 'масштабный', 'колоссальный'],
        'маленький': ['крошечный', 'миниатюрный', 'небольшой', 'малый', 'компактный', 'мелкий'],
        'красивый': ['прекрасный', 'великолепный', 'живописный', 'привлекательный', 'симпатичный'],
        'умный': ['разумный', 'мудрый', 'сообразительный', 'интеллектуальный', 'толковый'],
        'быстрый': ['скорый', 'стремительный', 'проворный', 'резвый', 'молниеносный', 'шустрый'],
        'медленный': ['неторопливый', 'тихий', 'размеренный', 'ленивый', 'неспешный'],
        'сильный': ['мощный', 'могучий', 'крепкий', 'стойкий', 'выносливый', 'железный'],
        'слабый': ['бессильный', 'немощный', 'хилый', 'хрупкий', 'уязвимый'],
        'классный': ['крутой', 'отличный', 'потрясающий', 'великолепный', 'восхитительный'],
        'грациозный': ['изящный', 'элегантный', 'пластичный', 'ловкий', 'стройный'],
        'тёплый': ['горячий', 'жаркий', 'ласковый', 'нежный'],
        'холодный': ['ледяной', 'морозный', 'студёный', 'прохладный'],
        'весёлый': ['радостный', 'счастливый', 'задорный', 'беззаботный'],
        'грустный': ['печальный', 'унылый', 'тоскливый', 'мрачный'],
        'чистый': ['свежий', 'опрятный', 'аккуратный', 'прозрачный'],
        'грязный': ['испачканный', 'нечистый', 'запачканный'],
        # Глаголы
        'любить': ['обожать', 'боготворить', 'увлекаться', 'души не чаять'],
        'люблю': ['обожаю', 'боготворю', 'уважаю', 'ценю'],
        'нравится': ['симпатичен', 'приятен', 'по душе', 'импонирует'],
        'считаю': ['полагаю', 'думаю', 'рассуждаю', 'оцениваю'],
        'начать': ['стартовать', 'приступить', 'запустить', 'затеять'],
        'говорить': ['сказать', 'произносить', 'болтать', 'беседовать'],
        'смотреть': ['глядеть', 'наблюдать', 'взирать', 'рассматривать'],
        'идти': ['шагать', 'шествовать', 'направляться', 'двигаться'],
        'бежать': ['мчаться', 'нестись', 'лететь', 'торопиться'],
        'есть': ['кушать', 'питаться', 'вкушать', 'трапезничать'],
        'пить': ['лакать', 'глотать', 'поглощать'],
        'спать': ['дремать', 'отдыхать', 'почивать'],
        'работать': ['трудиться', 'заниматься', 'делать', 'пахать'],
        'думать': ['размышлять', 'полагать', 'рассуждать', 'считать'],
        # Существительные
        'день': ['сутки', 'денёк'],
        'дождь': ['ливень', 'осадки', 'ненастье'],
        'чай': ['напиток', 'заварка'],
        'книга': ['издание', 'том', 'фолиант'],
        'парк': ['сквер', 'сад', 'аллея'],
        'ветер': ['ветерок', 'бриз', 'дуновение'],
        'глаза': ['очи', 'взор', 'взгляд'],
        'руки': ['ладони', 'кисти', 'длани'],
        'дом': ['жилище', 'здание', 'постройка', 'квартира'],
        'машина': ['автомобиль', 'авто', 'тачка'],
        'человек': ['индивид', 'личность', 'господин', 'мужчина'],
        'женщина': ['дама', 'девушка', 'особа'],
        'ребёнок': ['малыш', 'дитя', 'ребятёнок', 'карапуз'],
        'друг': ['приятель', 'товарищ', 'союзник', 'брат'],
        'враг': ['недруг', 'противник', 'неприятель'],
        'любовь': ['страсть', 'привязанность', 'симпатия', 'влечение'],
        'счастье': ['радость', 'благополучие', 'успех', 'везение'],
        'горе': ['беда', 'несчастье', 'печаль', 'страдание'],
        # Дополнительно
        'она': ['девушка', 'подруга', 'дама'],
        'вика': ['виктория'],
        'милая': ['прекрасная', 'симпатичная', 'хорошая', 'добрая'],
        'добрая': ['хорошая', 'отзывчивая', 'ласковая', 'милая'],
        'подруга': ['приятельница', 'товарищ', 'друг'],
        'приехала': ['прибыла', 'добралась', 'пришла', 'заехала'],
        'домой': ['жилище', 'в квартиру', 'к себе'],
        'находится': ['расположен', 'стоит', 'размещается'],
        'екатеринбург': ['город', 'столица Урала'],
    }
    
    word_lower = word.lower()
    if word_lower in demo_synonyms:
        return demo_synonyms[word_lower][:max_results]
    return []