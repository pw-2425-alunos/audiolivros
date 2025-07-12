from django import forms
from .models import AudioLivro, Membro, Comentario

class AudioLivroForm(forms.ModelForm):
    class Meta:
        model = AudioLivro
        exclude = ["faixa_etaria",]
        #fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'título do livro...'}),
            'autor': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'nome do autor...'}),
            'audio': forms.FileInput(attrs={'class': 'input-field'}),
            'capa': forms.FileInput(attrs={'class': 'input-field'}),
            'descricao': forms.Textarea(attrs={'class': 'input-field', 'placeholder': 'Este livro fala sobre...'}),
            'link_informacoes': forms.URLInput(attrs={'class': 'input-field'}),
            'descricaoAudio': forms.FileInput(attrs={'class': 'input-field'}),
            'categoria': forms.Select(attrs={'class': 'input-field'}),
           # 'faixa_etaria': forms.Select(attrs={'class': 'input-field'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = '__all__'

class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = '__all__'

