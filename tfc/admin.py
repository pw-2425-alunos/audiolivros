from django.contrib import admin
from django.utils.html import format_html
from .models import Membro, AudioLivro, Comentario, Familia

class FamiliaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'foto_preview')
    search_fields = ('nome', 'email')
    ordering = ('nome',)

    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', obj.foto.url)
        return "Sem foto"
    foto_preview.short_description = 'Foto'


class MembroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'idade', 'familia', 'foto_preview')
    ordering = ('nome',)
    search_fields = ('nome', 'familia__nome')
    list_filter = ('familia',)

    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', obj.foto.url)
        return "Sem foto"
    foto_preview.short_description = 'Foto'


class AudioLivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'faixa_etaria', 'duracao_formatado', 'gravado_por', 'capa_imagem', 'descricao_tipo')
    ordering = ('titulo',)
    search_fields = ('titulo', 'autor', 'categoria', 'gravado_por__nome')
    list_filter = ('categoria', 'faixa_etaria')

    def duracao_formatado(self, obj):
        return obj.duracao_formatada
    duracao_formatado.short_description = 'Duração'

    def capa_imagem(self, obj):
        if obj.capa:
            return format_html('<img src="{}" style="width: 75px; height: 75px;" />', obj.capa.url)
        return "Sem capa"
    capa_imagem.short_description = 'Capa'

    def descricao_tipo(self, obj):
        if obj.descricaoAudio:
            return "Áudio"
        elif obj.descricao:
            return "Texto"
        return "Indefinido"
    descricao_tipo.short_description = 'Descrição'


class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor_nome', 'audio_livro_titulo', 'data', 'tipo')
    ordering = ('data',)
    search_fields = ('titulo', 'autor__nome', 'audio_livro__titulo')
    list_filter = ('data', 'autor')

    def autor_nome(self, obj):
        return obj.autor.nome
    autor_nome.short_description = 'Autor'

    def audio_livro_titulo(self, obj):
        return obj.audio_livro.titulo
    audio_livro_titulo.short_description = 'Áudio Livro'

    def tipo(self, obj):
        if obj.audio:
            return "Áudio"
        elif obj.texto:
            return "Texto"
        return "Indefinido"
    tipo.short_description = 'Tipo'


admin.site.register(Membro, MembroAdmin)
admin.site.register(AudioLivro, AudioLivroAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Familia, FamiliaAdmin)