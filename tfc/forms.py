from django import forms
from .models import AudioLivro, Membro, Comentario

class AudioLivroForm(forms.ModelForm):
    class Meta:
        model = AudioLivro
        exclude = ['publicado', 'gravado_por']
        widgets = {
            'descricao': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escreva aqui a descrição do audiolivro...',
                'class': 'form-control'
            }),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = '__all__'

class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = '__all__'

