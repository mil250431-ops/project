from django import forms

class TextAnalysisForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        required=False,
        label='Название отрывка',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: Глава 1. Знакомство'
        })
    )
    text_content = forms.CharField(
        label='Текст для анализа',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 12,
            'placeholder': 'Вставьте сюда ваш текст (до 50 000 символов)...'
        }),
        max_length=50000,
        error_messages={
            'required': 'Пожалуйста, введите текст для анализа.'
        }
    )