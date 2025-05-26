from django.db import models
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import os

class Familia(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    foto = models.ImageField(upload_to='familia_photos/', null=True, blank=True)
    apresentacao_familia = models.FileField(upload_to='apresentacoes/', null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nome


class Membro(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.IntegerField(default=0, null=True, blank=True)
    foto = models.ImageField(upload_to='utilizadores/', null=True, blank=True)
    apresentacao_audio = models.FileField(upload_to='apresentacoes/', null=True, blank=True)
    familia = models.ForeignKey(Familia, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome

class AudioLivro(models.Model):
    CATEGORIAS_CHOICES = [
        ('Aventura', 'Aventura'),
        ('Ação', 'Ação'),
        ('Fantasia', 'Fantasia'),
        ('Mistério', 'Mistério'),
        ('Fábula', 'Fábula'),
        ('História', 'História'),
        ('Conto de Fadas', 'Conto de Fadas'),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    capa = models.ImageField(upload_to='capas/', null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    descricaoAudio = models.FileField(upload_to='descricao_audios/', null=True, blank=True)
    categoria = models.CharField(max_length=100, choices=CATEGORIAS_CHOICES)
    faixa_etaria = models.CharField(max_length=50)
    audio = models.FileField(upload_to='audios/')
    gravado_por = models.ForeignKey('Familia', on_delete=models.SET_NULL, null=True, blank=True)
    publicado = models.BooleanField(default=False)

    @property
    def duracao(self):
        if self.audio:
            file_path = self.audio.path
            if os.path.exists(file_path):
                try:
                    if file_path.endswith('.mp3'):
                        audio_file = MP3(file_path)
                    elif file_path.endswith('.wav'):
                        audio_file = WAVE(file_path)
                    else:
                        return None
                    return audio_file.info.length
                except Exception as e:
                    print(f"Erro ao obter duração do áudio: {e}")
                    return None
        return None

    @property
    def duracao_formatada(self):
        duracao = self.duracao
        if duracao:
            minutos = int(duracao // 60)
            segundos = int(duracao % 60)
            return f"{minutos}m {segundos}s"
        return "Desconhecido"

    def __str__(self):
        return f"{self.titulo} ({self.duracao_formatada})"



class Comentario(models.Model):
    titulo = models.CharField(max_length=200)
    texto = models.TextField(null=True, blank=True)
    desenho = models.ImageField(upload_to='desenhocomentario/', null=True, blank=True)
    audio = models.FileField(upload_to='comentarios/', null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='comentarios')
    audio_livro = models.ForeignKey(AudioLivro, on_delete=models.CASCADE, related_name='comentarios')

    def __str__(self):
        return f"Comentário de {self.autor.nome} no livro '{self.audio_livro.titulo}' em {self.data.strftime('%Y-%m-%d')}"


class Like(models.Model):
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='likes')
    audiolivro = models.ForeignKey(AudioLivro, on_delete=models.CASCADE, related_name='likes')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('familia', 'audiolivro')
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.familia.nome} curtiu {self.audiolivro.titulo}"


class Bookmark(models.Model):
    familia     = models.ForeignKey(Familia, on_delete=models.CASCADE)
    audiolivro  = models.ForeignKey(AudioLivro, on_delete=models.CASCADE)
    position    = models.FloatField(help_text="Posição em segundos")
    atualizado  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('familia', 'audiolivro')
        ordering = ['-atualizado']

    def __str__(self):
        return f"{self.familia.nome} @ {self.position:.1f}s em {self.audiolivro.titulo}"
