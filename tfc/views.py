import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import AudioLivro, Membro, Familia, Comentario, Like, Bookmark
from .forms import AudioLivroForm, ComentarioForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.core.files.base import ContentFile
from django.http import HttpResponseForbidden
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import uuid


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('nome')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tfc:biblioteca')
        else:
            return render(request, 'tfc/login.html', {'error': 'Credenciais inválidas'})

    return render(request, 'tfc/login.html')


def is_image(file):
    mime = file.content_type
    return mime.startswith('image/')

def is_audio(file):
    mime = file.content_type
    return mime.startswith('audio/')

@csrf_exempt
def registo_view(request):
    context = {}

    if request.method == "POST":
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')
        apresentacao_familia = request.FILES.get('apresentacao_familia')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Verificações de existência
        if Familia.objects.filter(nome=nome).exists():
            context['error'] = 'Família já se encontra registada.'
            return render(request, 'tfc/registo.html', context)

        if Familia.objects.filter(email=email).exists():
            context['error'] = 'Email já foi utilizado por outra conta.'
            return render(request, 'tfc/registo.html', context)

        # Validação de tipo de ficheiro
        if foto and not is_image(foto):
            context['error'] = 'A fotografia deve ser um ficheiro de imagem válido.'
            return render(request, 'tfc/registo.html', context)

        if apresentacao_familia and not is_audio(apresentacao_familia):
            context['error'] = 'A apresentação da família deve ser um ficheiro de áudio válido.'
            return render(request, 'tfc/registo.html', context)

        familia = Familia.objects.create(
            nome=nome,
            email=email,
            password=password,
            foto=foto,
            apresentacao_familia=apresentacao_familia
        )

        user = User.objects.create_user(username=nome, email=email, password=password)
        user.save()

        return redirect('tfc:perfilFamilia', familia_id=familia.id)

    return render(request, 'tfc/registo.html', context)


def logout_view(request):
    logout(request)
    return redirect('tfc:login')


@csrf_exempt
def recuperar_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        familia = Familia.objects.filter(email=email).first()

        if not familia:
            return render(request, "tfc/recuperar_password.html", {"error": "Email não encontrado."})

        nova_password = get_random_string(length=8)
        familia.password = nova_password
        familia.save()

        user = User.objects.filter(username=familia.nome).first()
        if user:
            user.set_password(nova_password)
            user.save()

        send_mail(
            subject="Recuperação de Password",
            message=f"A sua nova password temporária é: {nova_password}",
            from_email='beeaudiolivros@gmail.com',
            recipient_list=[email],
        )

        return render(request, "tfc/recuperar_password.html", {"success": "Nova password enviada para o email."})

    return render(request, "tfc/recuperar_password.html")


@login_required
def alterar_password_view(request):
    if request.method == "POST":
        atual = request.POST.get("password_atual")
        nova = request.POST.get("nova_password")
        confirmar = request.POST.get("confirmar_password")

        if not atual or not nova or not confirmar:
            messages.error(request, "Todos os campos são obrigatórios.")
            return redirect("tfc:alterar_password")

        if nova != confirmar:
            messages.error(request, "As novas passwords não coincidem.")
            return redirect("tfc:alterar_password")

        user = authenticate(username=request.user.username, password=atual)
        if user is None:
            messages.error(request, "Password atual incorreta.")
            return redirect("tfc:alterar_password")

        user.set_password(nova)
        user.save()
        messages.success(request, "Password alterada com sucesso.")
        return redirect("tfc:login")

    return render(request, "tfc/alterar_password.html")


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
        novo_nome = request.POST.get("nome", familia.nome)
        familia.email = request.POST.get("email", familia.email)

        if "foto" in request.FILES:
            familia.foto = request.FILES["foto"]

        if "apresentacao_familia" in request.FILES:
            familia.apresentacao_familia = request.FILES["apresentacao_familia"]

        familia.nome = novo_nome
        familia.save()

        # Atualizar também o username do utilizador autenticado
        user = request.user
        user.username = novo_nome
        user.save()

        return redirect("tfc:perfilFamilia", familia.id)

    return render(request, "tfc/editarPerfilFamilia.html", {"familia": familia})


@login_required
def editar_perfil_membro_view(request, membro_id):
    membro = get_object_or_404(Membro, id=membro_id)
    familia = membro.familia

    if request.method == "POST":
        membro.nome = request.POST.get("nome", membro.nome)
        membro.idade = request.POST.get("idade", membro.idade)

        if "foto" in request.FILES:
            membro.foto = request.FILES["foto"]

        membro.save()
        return redirect("tfc:perfilFamilia", membro.familia.id)

    return render(request, "tfc/editarPerfilMembro.html", {"membro": membro, "familia":familia})

@login_required
def add_membro(request, familia_id):
    familia = get_object_or_404(Familia, id=familia_id)
    context = {'familia': familia}

    if request.method == "POST":
        nome = request.POST.get("nome")
        idade = request.POST.get("idade")
        foto = request.FILES.get("foto")
        apresentacao_audio = request.FILES.get("apresentacao_audio")

        if foto and not is_image(foto):
            context['error'] = 'A fotografia deve ser um ficheiro de imagem válido.'
            return render(request, 'tfc/addMembro.html', context)

        if apresentacao_audio and not is_audio(apresentacao_audio):
            context['error'] = 'A apresentação do membro deve ser um ficheiro de áudio válido.'
            return render(request, 'tfc/addMembro.html', context)

        membro = Membro.objects.create(
            nome=nome,
            idade=idade,
            foto=foto,
            apresentacao_audio=apresentacao_audio,
            familia=familia
        )

        return redirect('tfc:perfilFamilia', familia_id=familia.id)

    return render(request, 'tfc/addMembro.html', context)

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

@login_required
def remover_audiolivro_view(request, pk):
    audiolivro = get_object_or_404(AudioLivro, pk=pk)

    if not audiolivro.gravado_por or audiolivro.gravado_por.nome != request.user.username:
        messages.error(request, "Ação não permitida pelo user")
        return redirect("tfc:perfilFamilia")

    if request.method == "POST":
        audiolivro.delete()
        messages.success(request, "Audiolivro removido com sucesso.")
        return redirect("tfc:perfilFamilia")

    return render(request, 'tfc/removerAudiolivro.html', {'audiolivro': audiolivro})


def biblioteca_view(request):
    query = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    audiolivros = AudioLivro.objects.filter(publicado=True)

    if query:
        familia = Familia.objects.filter(nome__iexact=query).first()
        if familia:
            audiolivros = audiolivros.filter(gravado_por=familia)
        else:
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
        familia_user = Familia.objects.filter(nome=request.user.username).first()
        if familia_user:
            for bm in Bookmark.objects.filter(familia=familia_user):
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
    audio_temp_url = request.GET.get('audio_temp')
    form = AudioLivroForm()

    if request.method == 'POST':
        form = AudioLivroForm(request.POST, request.FILES)
        if form.is_valid():
            audiolivro = form.save(commit=False)
            audiolivro.publicado = False

            familia_user = get_object_or_404(Familia, nome=request.user.username)
            audiolivro.gravado_por = familia_user

            if audio_temp_url and not request.FILES.get('audio'):
                # Copiar ficheiro do temp para o campo audio
                filename = os.path.basename(audio_temp_url)
                temp_path = os.path.join('media', 'temp_audios', filename)
                if os.path.exists(temp_path):
                    with open(temp_path, 'rb') as f:
                        audiolivro.audio.save(filename, ContentFile(f.read()), save=False)
                    os.remove(temp_path)  # Limpa depois de usar!
            audiolivro.save()
            return redirect('tfc:perfilFamilia')
    context = {
        'form': form,
        'audio_temp_url': audio_temp_url,
    }
    return render(request, 'tfc/criarAudiolivro.html', context)



@login_required
def publicar_audiolivro_view(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, pk=audiolivro_id, gravado_por__nome=request.user.username)
    campos_obrigatorios = [audiolivro.titulo, audiolivro.autor, audiolivro.audio, audiolivro.capa,
                           audiolivro.descricao, audiolivro.categoria,audiolivro.faixa_etaria
                           ]
    if all(campos_obrigatorios):
        audiolivro.publicado = True
        audiolivro.save()
        messages.success(request, "Audiolivro publicado com sucesso!")
    else:
        messages.error(request, "Para publicar tem de preencher todos os campos obrigatórios.")
    return redirect('tfc:perfilFamilia')



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
            return JsonResponse({'success': False, 'error': "É necessário gravar um áudio."})

        novo_livro.save()
        edit_url = reverse('tfc:editar_audiolivro', kwargs={'id': novo_livro.id})
        return JsonResponse({'success': True, 'edit_url': edit_url})

    return JsonResponse({'success': False, 'error': "Método inválido."})




@login_required
def criarComentarioInline(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        audio = request.FILES.get("audio")
        desenho = request.FILES.get("desenho")
        familia = get_object_or_404(Familia, nome=request.user.username)

        if not texto and not audio and not desenho:
            messages.error(request, "Tens de escrever algo ou submeter um áudio para comentar.")
            return redirect('tfc:detalhe_audiolivro', audiolivro_id=audiolivro.id)

        comentario = Comentario(
            texto=texto,
            audio_livro=audiolivro,
            autor=familia
        )

        if audio:
            comentario.audio = audio

        if desenho:
            comentario.desenho = desenho

        comentario.save()
        messages.success(request, "Comentário adicionado com sucesso!")

    return redirect('tfc:detalhe_audiolivro', audiolivro_id=audiolivro.id)


@login_required
def editar_audiolivro(request, id):
    audiolivro = get_object_or_404(AudioLivro, id=id, gravado_por__nome=request.user.username)

    if request.method == 'POST':
        form = AudioLivroForm(request.POST, request.FILES, instance=audiolivro)

        descricao_audio = request.FILES.get('descricao_audio')
        if descricao_audio and not is_audio(descricao_audio):
            form.add_error('descricao_audio', 'O ficheiro deve ser um áudio válido.')
        elif form.is_valid():
            audio = form.save(commit=False)
            audio.gravado_por = Familia.objects.get(nome=request.user.username)
            audio.save()
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


@login_required
def despublicar_audiolivro_view(request, audiolivro_id):
    audiolivro = get_object_or_404(AudioLivro, id=audiolivro_id)

    if request.method == 'POST':
        audiolivro.publicado = False
        audiolivro.save()
        return redirect('tfc:perfilFamilia')

    return redirect('tfc:perfilFamilia')

def home_view(request):
    return render(request, 'tfc/home.html')

def sobre_aplicacao_view(request):
    return render(request, 'tfc/sobre_aplicacao.html')


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


@login_required
def apagar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    familia = get_object_or_404(Familia, nome=request.user.username)

    if comentario.autor != familia:
        return HttpResponseForbidden("Não tens permissão para apagar este comentário.")

    audiolivro_id = comentario.audio_livro.id
    comentario.delete()
    messages.success(request, "Comentário apagado com sucesso.")
    return redirect('tfc:detalhe_audiolivro', audiolivro_id=audiolivro_id)


@require_POST
@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(
        Comentario,
        id=comentario_id,
        autor__nome=request.user.username
    )
    novo_texto = request.POST.get('texto', '').strip()
    if not novo_texto:
        return JsonResponse({'success': False, 'error': 'Texto vazio.'}, status=400)
    comentario.texto = novo_texto
    comentario.save()
    return JsonResponse({'success': True, 'texto': comentario.texto})


def tutorial_view(request):
    contexto = {
        'video_embed_url': 'https://www.youtube.com/embed/SEU_VIDEO_ID_AQUI'
    }
    return render(request, 'tfc/tutorial.html', contexto)




@csrf_exempt
def upload_temp_audio(request):
    if request.method == "POST":
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'success': False, 'error': 'Ficheiro não recebido'})
        filename = f"temp_{uuid.uuid4()}.webm"
        temp_path = os.path.join('media', 'temp_audios')
        os.makedirs(temp_path, exist_ok=True)
        filepath = os.path.join(temp_path, filename)
        with open(filepath, 'wb+') as dest:
            for chunk in audio_file.chunks():
                dest.write(chunk)
        audio_url = f"/media/temp_audios/{filename}"
        return JsonResponse({'success': True, 'audio_url': audio_url})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

