from django.urls import path
from . import views

app_name = 'tfc'

urlpatterns = [
    path('', views.biblioteca_view, name='biblioteca'),
    path('audiolivro/<int:audiolivro_id>/', views.detalhe_audiolivro_view, name='detalhe_audiolivro'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registo/', views.registo_view, name="registo"),
    path('perfil/', views.perfil_familia_view, name='perfilFamilia'),
    path('membro/<int:membro_id>/', views.perfil_membro_view, name='perfilMembro'),
    path('perfil/editar/', views.editar_perfil_familia_view, name='editarPerfilFamilia'),
    path('membro/<int:membro_id>/editar/', views.editar_perfil_membro_view, name='editarPerfilMembro'),
    path('addMembro/<int:familia_id>/', views.add_membro, name='addMembro'),
    path('removerMembro/<int:membro_id>/', views.remover_membro_view, name='removerMembro'),
    path('audiolivro/novo', views.criarAudiolivro_view, name='criarAudiolivro'),
    path('audiolivro/<int:audiolivro_id>/comentario/novo', views.criarComentario_view, name='criarComentario'),
    path('gravar/', views.gravar_view, name='gravar'),
    path('upload_audio/', views.upload_audio_view, name='upload_audio'),
    path('audiolivro/<int:audiolivro_id>/comentar', views.criarComentarioInline, name='criarComentarioInline'),
    path('audiolivro/<int:id>/editar/', views.editar_audiolivro, name='editar_audiolivro'),
    path('audiolivro/<int:audiolivro_id>/publicar/', views.publicar_audiolivro_view, name='publicar_audiolivro'),

]
