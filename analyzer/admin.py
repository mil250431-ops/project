from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TextSample, LexicalAnalysis, SentimentScore

admin.site.register(TextSample)
admin.site.register(LexicalAnalysis)
admin.site.register(SentimentScore)