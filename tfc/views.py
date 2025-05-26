import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import AudioLivro, Membro, Familia, Comentario, Like, Bookmark
from .forms import AudioLivroForm, ComentarioForm
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.urls import reverse
from django.core.files.base import ContentFile
from urllib.request import urlopen
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods


@csrf_exempt

def login_view(request):
    if request.method == 'POST':
        username = request.POST['nome']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
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

        if Familia.objects.filter(email=email).exists():
            context['error'] = 'Email já foi utilizado por outra conta.'
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
def perfil_familia_view(request, familia_id=None):

    if familia_id:
        familia = get_object_or_404(Familia, id=familia_id)
    else:
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
        return redirect("tfc:perfilFamilia")

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

    return render(request, 'tfc/removerMembro.html', {'membro': membro})

def biblioteca_view(request):
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')

    if query:
        membro = Membro.objects.filter(nome__iexact=query).first()
        if membro and membro.familia:
            return redirect(f"{reverse('tfc:perfilFamilia')}?id={membro.familia.id}")

    audiolivros = AudioLivro.objects.filter(publicado=True)
    if query:
        audiolivros = audiolivros.filter(titulo__icontains=query)
    if categoria:
        audiolivros = audiolivros.filter(categoria=categoria)

    categorias_dict = defaultdict(list)
    for a in audiolivros:
        categorias_dict[a.categoria].append(a)
    categorias_ordenadas = sorted(categorias_dict.keys())
    audiolivros_por_categoria = {
        cat: categorias_dict[cat] for cat in categorias_ordenadas
    }
    categorias = [c[0] for c in AudioLivro.CATEGORIAS_CHOICES]

    continuar = []
    if request.user.is_authenticated:
        familia = Familia.objects.filter(nome=request.user.username).first()
        if familia:
            for bm in Bookmark.objects.filter(familia=familia):
                dur = bm.audiolivro.duracao or 0
                if bm.position and bm.position < dur - 1:
                    continuar.append((bm.audiolivro, bm.position))

    context = {
        'query': query,
        'categorias': categorias,
        'categoria_selecionada': categoria,
        'audiolivros_por_categoria': audiolivros_por_categoria,
        'continuar': continuar,
    }
    return render(request, "tfc/biblioteca.html", context)


def detalhe_audiolivro_view(request, audiolivro_id):

    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)
    comentarios = Comentario.objects.filter(audio_livro=audiolivro)

    liked = False
    if request.user.is_authenticated:
        familia = Familia.objects.filter(nome=request.user.username).first()
        if familia:
            liked = Like.objects.filter(familia=familia, audiolivro=audiolivro).exists()
    like_count = Like.objects.filter(audiolivro=audiolivro).count()

    context = {
        'audiolivro': audiolivro,
        'comentarios': comentarios,
        'liked': liked,
        'like_count': like_count,
    }
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

            if audio_url and not request.FILES.get('audio'):
                audio_filename = os.path.basename(audio_url)
                response = urlopen(audio_url)
                audiolivro.audio.save(audio_filename, ContentFile(response.read()), save=False)

            audiolivro.save()
            return redirect('tfc:perfilFamilia')
    else:
        form = AudioLivroForm()

    context = {'form': form, 'audio_url': audio_url}
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


@login_required
def criarAudiolivroInline(request):
    if request.method == "POST":
        familia = get_object_or_404(Familia, nome=request.user.username)

        novo_livro = AudioLivro(
            gravado_por=familia,
            publicado=False
        )

        if request.FILES.get('audio'):
            novo_livro.audio = request.FILES.get('audio')
        else:
            messages.error(request, "É necessário gravar um áudio.")
            return redirect('tfc:gravar')

        novo_livro.save()
        messages.success(request, "Gravação criada com sucesso! Complete agora os restantes detalhes.")

        return redirect('tfc:editarAudiolivro', id=novo_livro.id)

    return redirect('tfc:perfilFamilia')


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

def home_view(request):
    return render(request, 'tfc/home.html')


@login_required
@require_POST
def toggle_like(request, audiolivro_id):
    familia = get_object_or_404(Familia, nome=request.user.username)
    livro   = get_object_or_404(AudioLivro, id=audiolivro_id)

    like, created = Like.objects.get_or_create(familia=familia, audiolivro=livro)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    count = Like.objects.filter(audiolivro=livro).count()

    return JsonResponse({'liked': liked, 'count': count})



@login_required
@require_http_methods(["GET"])
def get_bookmark(request, audiolivro_id):
    familia = get_object_or_404(Familia, nome=request.user.username)
    try:
        bm = Bookmark.objects.get(familia=familia, audiolivro_id=audiolivro_id)
        return JsonResponse({'position': bm.position})
    except Bookmark.DoesNotExist:
        return JsonResponse({'position': 0.0})

@login_required
@require_http_methods(["POST"])
def set_bookmark(request, audiolivro_id):
    familia = get_object_or_404(Familia, nome=request.user.username)
    try:
        pos = float(request.POST.get('position', 0))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Posição inválida")

    bm, created = Bookmark.objects.update_or_create(
        familia=familia, audiolivro_id=audiolivro_id,
        defaults={'position': pos}
    )
    return JsonResponse({'position': bm.position})
