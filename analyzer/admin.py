from django.contrib import admin
from .models import TextSample, LexicalAnalysis, SentimentScore


@admin.register(TextSample)
class TextSampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)


@admin.register(LexicalAnalysis)
class LexicalAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_sample', 'word_count', 'unique_words', 'flesch_reading_ease')
    search_fields = ('text_sample__title',)


@admin.register(SentimentScore)
class SentimentScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_sample', 'paragraph_index', 'positive_score', 'negative_score', 'compound_score')
    list_filter = ('compound_score',)
    search_fields = ('text_sample__title', 'paragraph_text')