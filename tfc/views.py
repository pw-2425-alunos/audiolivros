import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import AudioLivro, Membro, Familia, Comentario
from .forms import AudioLivroForm, ComentarioForm
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        password = request.POST.get('password')

        try:
            familia = Familia.objects.get(nome=nome)
        except ObjectDoesNotExist:
            return render(request, 'tfc/login.html', {'error': 'Nome da família não encontrado'})

        user = authenticate(request, username=familia.nome, password=password)
        if user:
            login(request, user)
            return redirect('tfc:biblioteca')
        else:
            return render(request, 'tfc/login.html', {'error': 'Credenciais inválidas'})

    return render(request, 'tfc/login.html')

@csrf_exempt
def registo_view(request):
    context = {}  # Definindo um dicionário vazio no início

    if request.method == "POST":
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')
        password = request.POST.get('password')
        apresentacao_familia = request.FILES.get('apresentacao_familia')
        email = request.POST.get('email')

        if Familia.objects.filter(nome=nome).exists():
            context['error'] = 'Família já se encontra registada.'
            return render(request, 'tfc/registo.html', context)

        familia = Familia.objects.create(
            nome=nome, email=email, foto=foto,
            password=password, apresentacao_familia=apresentacao_familia
        )
        user = User.objects.create_user(username=nome, email=email, password=password)
        user.save()

        return redirect('tfc:login')

    return render(request, 'tfc/registo.html', context)

def logout_view(request):
    logout(request)
    return redirect('tfc:login')

@login_required
def perfil_familia_view(request):
    familia = get_object_or_404(Familia, nome=request.user.username)
    utilizadores = Membro.objects.filter(familia=familia)
    audiolivros = AudioLivro.objects.filter(gravado_por=familia)

    context = {
        'familia': familia,
        'utilizadores': utilizadores,
        'audiolivros': audiolivros,
    }
    return render(request, "tfc/perfilFamilia.html", context)


@login_required
def editar_perfil_familia_view(request):
    familia = get_object_or_404(Familia, nome=request.user.username)

    if request.method == "POST":
        familia.nome = request.POST.get("nome", familia.nome)
        familia.email = request.POST.get("email", familia.email)

        if "foto" in request.FILES:
            familia.foto = request.FILES["foto"]

        if "apresentacao_familia" in request.FILES:
            familia.apresentacao_familia = request.FILES["apresentacao_familia"]

        familia.save()
        return redirect("tfc:perfilFamilia")

    return render(request, "tfc/editarPerfilFamilia.html", {"familia": familia})


@login_required
def perfil_membro_view(request, membro_id):
    membro = get_object_or_404(Membro, id=membro_id)

    context = {'membro': membro}
    return render(request, 'tfc/perfilMembro.html', context)

@login_required
def editar_perfil_membro_view(request, membro_id):
    membro = get_object_or_404(Membro, id=membro_id)

    if request.method == "POST":
        membro.nome = request.POST.get("nome", membro.nome)
        membro.idade = request.POST.get("idade", membro.idade)

        if "foto" in request.FILES:
            membro.foto = request.FILES["foto"]

        membro.save()
        return redirect("tfc:perfilMembro", membro_id=membro.id)

    return render(request, "tfc/editarPerfilMembro.html", {"membro": membro})

@login_required
def add_membro(request, familia_id):
    familia = get_object_or_404(Familia, id=familia_id)

    if request.method == "POST":
        nome = request.POST.get("nome")
        idade = request.POST.get("idade")
        foto = request.FILES.get("foto")

        membro = Membro.objects.create(
            nome=nome,
            idade=idade,
            foto=foto,
            familia=familia
        )
        membro.save()

        return redirect('tfc:perfilFamilia', familia_id=familia.id)

    return render(request, 'tfc/addMembro.html', {'familia': familia})

@login_required
def remover_membro_view(request, membro_id):
    membro = get_object_or_404(Membro, id=membro_id)

    if membro.familia.nome != request.user.username:
        messages.error(request, "Ação não permitida pelo user")
        return redirect("tfc:perfilFamilia")

    if request.method == "POST":
        membro.delete()
        messages.success(request, "Membro removido com sucesso.")
        return redirect("tfc:perfilFamilia")

    return render(request, 'tfc/removerMembro.html')

def biblioteca_view(request):
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')

    audiolivros = AudioLivro.objects.filter(publicado=True)

    if query:
        audiolivros = audiolivros.filter(titulo__icontains=query)

    if categoria:
        audiolivros = audiolivros.filter(categoria=categoria)

    audiolivros_por_categoria = defaultdict(list)
    for audio in audiolivros:
        audiolivros_por_categoria[audio.categoria].append(audio)

    categorias_ordenadas = sorted(audiolivros_por_categoria.keys())

    audiolivros_por_categoria_ordenado = {
        cat: audiolivros_por_categoria[cat] for cat in categorias_ordenadas
    }

    categorias = [cat[0] for cat in AudioLivro.CATEGORIAS_CHOICES]

    context = {
        'audiolivros_por_categoria': audiolivros_por_categoria_ordenado,
        'categorias': categorias,
        'categoria_selecionada': categoria,
        'query': query,  # Para manter o valor da pesquisa no input
    }

    return render(request, "tfc/biblioteca.html", context)

def detalhe_audiolivro_view(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)
    comentario = Comentario.objects.filter(audio_livro=audiolivro)

    context = {'audiolivro': audiolivro, 'comentario': comentario}
    return render(request, "tfc/detalhe_audiolivro.html", context)

@login_required
def criarAudiolivro_view(request):
    audio_url = request.GET.get('audio')

    if request.method == 'POST':
        form = AudioLivroForm(request.POST, request.FILES)
        if form.is_valid():
            audiolivro = form.save(commit=False)
            audiolivro.publicado = False
            audiolivro.gravado_por = get_object_or_404(Familia, nome=request.user.username)
            audiolivro.save()
            return redirect('tfc:perfilFamilia')
    else:
        initial_data = {'audio': audio_url} if audio_url else {}
        form = AudioLivroForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'tfc/criarAudiolivro.html', context)


def criarComentario_view(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)
    form = ComentarioForm(request.POST or None, request.FILES)

    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.audiolivro = audiolivro
        comentario.save()
        return redirect('tfc:detalhe_audiolivro', audiolivro_id=audiolivro.id)

    context = {'form': form, 'audiolivro': audiolivro}
    return render(request, 'tfc/criarComentario.html', context)



def gravar_view(request):

    return render(request, "tfc/gravar.html")


@csrf_exempt
def upload_audio_view(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, audio_file.name)

        # Salva o arquivo no sistema de arquivos
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # Monta a URL para o arquivo (assegure-se de que MEDIA_URL está configurado)
        audio_url = os.path.join(settings.MEDIA_URL, 'uploads', audio_file.name)
        return JsonResponse({'success': True, 'audio_url': audio_url})

    return JsonResponse({'success': False})


@login_required
def criarComentarioInline(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)

    if not request.user.is_authenticated:
        messages.error(request, "É necessário fazer login para comentar.")
        return redirect('tfc:detalhe_audiolivro', audiolivro_id=audiolivro.id)

    if request.method == "POST":
        texto = request.POST.get("texto")
        familia = get_object_or_404(Familia, nome=request.user.username)

        comentario = Comentario(
            texto=texto,
            audio_livro=audiolivro,
            autor=familia
        )

        if request.FILES.get('audio'):
            comentario.audio = request.FILES.get('audio')

        comentario.save()
        messages.success(request, "Comentário adicionado com sucesso!")

    return redirect('tfc:detalhe_audiolivro', audiolivro_id=audiolivro.id)


@login_required
def editar_audiolivro(request, id):
    audiolivro = get_object_or_404(AudioLivro, id=id, gravado_por__nome=request.user.username)

    if request.method == 'POST':
        form = AudioLivroForm(request.POST, request.FILES, instance=audiolivro)
        if form.is_valid():
            form.save()
            return redirect('tfc:perfilFamilia')
    else:
        form = AudioLivroForm(instance=audiolivro)

    return render(request, 'tfc/editar_audiolivro.html', {'form': form, 'audiolivro': audiolivro})

@login_required
def publicar_audiolivro_view(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)

    if request.method == 'POST':
        audiolivro.publicado = True
        audiolivro.save()
        return redirect('tfc:perfilFamilia')

    return redirect('tfc:perfilFamilia')







