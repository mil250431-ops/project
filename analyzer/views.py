import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import TextSample, LexicalAnalysis, SentimentScore
from .forms import TextAnalysisForm
from .services import (
    split_into_paragraphs,
    calculate_flesch_reading_ease,
    interpret_flesch_score,
    get_word_frequency,
    analyze_paragraphs,
    get_synonyms_datamuse,
)

def index(request):
    form = TextAnalysisForm()
    return render(request, 'analyzer/index.html', {
        'title': 'Цифровой книжный критик',
        'form': form
    })

def analyze(request):
    if request.method != 'POST':
        return redirect('index')
    
    form = TextAnalysisForm(request.POST)
    
    if not form.is_valid():
        messages.error(request, 'Пожалуйста, введите корректный текст для анализа')
        return redirect('index')
    
    text_content = form.cleaned_data['text_content']
    title = form.cleaned_data['title'] or "Без названия"
    
    if len(text_content) > 50000:
        text_content = text_content[:50000]
        messages.warning(request, 'Текст был обрезан до 50000 символов')
    
    try:
        with transaction.atomic():
            text_sample = TextSample(
                user=request.user if request.user.is_authenticated else None,
                title=title,
                content=text_content
            )
            text_sample.save()
            
            word_freq = get_word_frequency(text_content, top_n=50)
            flesch_score = calculate_flesch_reading_ease(text_content)
            words = text_content.split()
            unique_words = len(set(w.lower() for w in words))
            
            lexical = LexicalAnalysis(
                text_sample=text_sample,
                word_count=len(words),
                unique_words=unique_words,
                flesch_reading_ease=flesch_score,
                word_frequency=word_freq
            )
            lexical.save()
            
            paragraphs = split_into_paragraphs(text_content)
            sentiment_results = analyze_paragraphs(paragraphs)
            
            for result in sentiment_results:
                SentimentScore.objects.create(
                    text_sample=text_sample,
                    paragraph_index=result['index'],
                    paragraph_text=result['full_text'][:500],
                    positive_score=result['positive'],
                    negative_score=result['negative'],
                    neutral_score=result['neutral'],
                    compound_score=result['compound']
                )
            
            request.session['last_analysis_id'] = text_sample.id
            
    except Exception as e:
        messages.error(request, f'Ошибка при анализе: {str(e)}')
        return redirect('index')
    
    return redirect('result', analysis_id=text_sample.id)

def result(request, analysis_id):
    text_sample = get_object_or_404(TextSample, id=analysis_id)
    
    if text_sample.user and text_sample.user != request.user:
        messages.error(request, 'У вас нет доступа к этому анализу')
        return redirect('index')
    
    try:
        lexical = text_sample.lexical
        sentiments = text_sample.sentiments.all()
    except:
        messages.error(request, 'Данные анализа не найдены')
        return redirect('index')
    
    flesch_interpretation, flesch_color = interpret_flesch_score(lexical.flesch_reading_ease)
    
    chart_data = {
        'paragraphs': [s.paragraph_index + 1 for s in sentiments],
        'scores': [float(s.compound_score) for s in sentiments],
        'labels': [f"Абзац {s.paragraph_index + 1}" for s in sentiments],
        'texts': [s.paragraph_text[:100] + '...' if len(s.paragraph_text) > 100 else s.paragraph_text for s in sentiments]
    }
    
    wordcloud_data = [{'word': word, 'weight': count} for word, count in lexical.word_frequency.items()]
    
    context = {
        'title': f'Результаты анализа: {text_sample.title}',
        'text_sample': text_sample,
        'lexical': lexical,
        'sentiments': sentiments,
        'flesch_interpretation': flesch_interpretation,
        'flesch_color': flesch_color,
        'chart_data': json.dumps(chart_data, ensure_ascii=False),
        'wordcloud_data': json.dumps(wordcloud_data, ensure_ascii=False),
    }
    
    return render(request, 'analyzer/result.html', context)

@login_required
def dashboard(request):
    analyses = TextSample.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'analyzer/dashboard.html', {
        'title': 'Личный кабинет',
        'analyses': analyses
    })

@login_required
def delete_analysis(request, analysis_id):
    text_sample = get_object_or_404(TextSample, id=analysis_id, user=request.user)
    if request.method == 'POST':
        title = text_sample.title
        text_sample.delete()
        messages.success(request, f'Анализ "{title}" удалён')
    return redirect('dashboard')

@csrf_exempt
def get_synonyms(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        word = data.get('word', '').strip()
        if word:
            synonyms = get_synonyms_datamuse(word)
            return JsonResponse({'success': True, 'synonyms': synonyms})
    return JsonResponse({'success': False, 'synonyms': []})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'analyzer/register.html', {'form': form, 'title': 'Регистрация'})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'analyzer/login.html', {'form': form, 'title': 'Вход'})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')