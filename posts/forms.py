from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '¿Qué te apasiona hoy?',
                'class': 'form-textarea',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Escribe un comentario...',
                'class': 'comment-input',
                'autocomplete': 'off',
                'maxlength': 500,
            }),
        }
        labels = {'content': ''}
