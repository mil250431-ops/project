from django.db import models
from django.contrib.auth.models import User

class TextSample(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, default="Без названия")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"

class LexicalAnalysis(models.Model):
    text_sample = models.OneToOneField(TextSample, on_delete=models.CASCADE, related_name='lexical')
    word_count = models.IntegerField(default=0)
    unique_words = models.IntegerField(default=0)
    flesch_reading_ease = models.FloatField(null=True, blank=True)
    word_frequency = models.JSONField(default=dict)

class SentimentScore(models.Model):
    text_sample = models.ForeignKey(TextSample, on_delete=models.CASCADE, related_name='sentiments')
    paragraph_index = models.IntegerField(default=0)
    paragraph_text = models.TextField(blank=True)
    positive_score = models.FloatField(default=0.0)
    negative_score = models.FloatField(default=0.0)
    neutral_score = models.FloatField(default=0.0)
    compound_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ['paragraph_index']