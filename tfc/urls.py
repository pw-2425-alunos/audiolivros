from django.urls import path
from . import views
from .views import toggle_like

app_name = 'tfc'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('biblioteca/', views.biblioteca_view, name='biblioteca'),
    path('audiolivro/<int:audiolivro_id>/', views.detalhe_audiolivro_view, name='detalhe_audiolivro'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registo/', views.registo_view, name="registo"),
    path('perfil/', views.perfil_familia_view, name='perfilFamilia'),
    path('perfil/<int:familia_id>/', views.perfil_familia_view, name='perfilFamilia'),
    path('membro/<int:membro_id>/', views.perfil_membro_view, name='perfilMembro'),
    path('perfil/editar/', views.editar_perfil_familia_view, name='editarPerfilFamilia'),
    path('membro/<int:membro_id>/editar/', views.editar_perfil_membro_view, name='editarPerfilMembro'),
    path('addMembro/<int:familia_id>/', views.add_membro, name='addMembro'),
    path('removerMembro/<int:membro_id>/', views.remover_membro_view, name='removerMembro'),
    path('audiolivro/novo', views.criarAudiolivro_view, name='criarAudiolivro'),
    path('audiolivro/<int:audiolivro_id>/comentario/novo', views.criarComentario_view, name='criarComentario'),
    path('gravar/', views.gravar_view, name='gravar'),
    path('audiolivro/<int:audiolivro_id>/comentar', views.criarComentarioInline, name='criarComentarioInline'),
    path('audiolivro/<int:id>/editar/', views.editar_audiolivro, name='editar_audiolivro'),
    path('audiolivro/<int:audiolivro_id>/publicar/', views.publicar_audiolivro_view, name='publicar_audiolivro'),
    path('audiolivro/criar_inline/', views.criarAudiolivroInline, name='criarAudiolivroInline'),
    path('audiolivro/<int:audiolivro_id>/like/', toggle_like, name='toggle_like'),
    path('audiolivro/<int:audiolivro_id>/bookmark/', views.get_bookmark, name='get_bookmark'),
    path('audiolivro/<int:audiolivro_id>/bookmark/set/', views.set_bookmark, name='set_bookmark'),
]
