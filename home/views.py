from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Workshop, InscricaoWorkshop, VagaVoluntariado, CandidaturaVoluntariado, Newsletter, Noticia
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator


def home(request):
    """View para página inicial"""
    
    # Processar newsletter
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Por favor, informe seu e-mail.')
            return redirect('home')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'E-mail inválido. Por favor, verifique.')
            return redirect('home')
        
        if Newsletter.objects.filter(email=email).exists():
            messages.warning(request, 'Este e-mail já está cadastrado!')
            return redirect('home')
        
        try:
            Newsletter.objects.create(email=email)
            messages.success(request, '🎉 Inscrição realizada com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao processar inscrição.')
        
        return redirect('home')
    
    # ✅ NOVA LÓGICA: Sempre priorizar notícias em DESTAQUE
    # 1. Buscar todas as notícias em destaque primeiro (ordenadas por data)
    noticias_destaque = list(Noticia.objects.publicadas().filter(destaque=True).order_by('-data_publicacao'))
    
    # 2. Se não tiver 4 notícias em destaque, completar com as mais recentes (que NÃO são destaque)
    if len(noticias_destaque) < 4:
        noticias_restantes = Noticia.objects.publicadas().filter(destaque=False).order_by('-data_publicacao')[:4 - len(noticias_destaque)]
        noticias = noticias_destaque + list(noticias_restantes)
    else:
        # Se tiver 4 ou mais em destaque, pegar apenas as 4 primeiras
        noticias = noticias_destaque[:4]
    
    context = {
        'noticias': noticias,
    }
    
    return render(request, 'home/home.html', context)


def noticia_detalhe(request, id):
    """View para exibir detalhes de uma notícia"""
    # ✅ Usar .publicadas() para garantir que só notícias publicadas sejam acessíveis
    noticia = get_object_or_404(Noticia.objects.publicadas(), id=id)
    
    # Buscar notícias relacionadas (mesma categoria, exceto a atual)
    noticias_relacionadas = Noticia.objects.publicadas().filter(
        categoria=noticia.categoria
    ).exclude(id=noticia.id)[:3]
    
    context = {
        'noticia': noticia,
        'noticias_relacionadas': noticias_relacionadas,
    }
    
    return render(request, 'home/noticia_detalhe.html', context)

from django.core.paginator import Paginator

def noticias_lista(request):
    """View para listagem completa de notícias com filtros e paginação"""
    
    # Pegar todas as notícias publicadas
    noticias = Noticia.objects.publicadas()
    
    # Filtro por categoria
    categoria = request.GET.get('categoria')
    if categoria:
        noticias = noticias.filter(categoria=categoria)
    
    # Filtro por ano
    ano = request.GET.get('ano')
    if ano:
        noticias = noticias.filter(data_publicacao__year=ano)
    
    # Filtro por mês
    mes = request.GET.get('mes')
    if mes and ano:
        noticias = noticias.filter(data_publicacao__month=mes)
    
    # Ordenar por data mais recente
    noticias = noticias.order_by('-data_publicacao')
    
    # ✅ PAGINAÇÃO: 9 notícias por página (grid 3x3)
    paginator = Paginator(noticias, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obter anos disponíveis para os filtros
    from django.db.models.functions import ExtractYear
    anos_disponiveis = Noticia.objects.publicadas().annotate(
        ano=ExtractYear('data_publicacao')
    ).values_list('ano', flat=True).distinct().order_by('-ano')
    
    # Categorias disponíveis
    categorias = Noticia.CATEGORIA_CHOICES
    
    # Meses para o select
    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    context = {
        'noticias': page_obj,  # ✅ MUDOU: agora usa page_obj
        'page_obj': page_obj,  # ✅ NOVO: para navegação de páginas
        'categorias': categorias,
        'anos_disponiveis': anos_disponiveis,
        'meses': meses,
        'categoria_selecionada': categoria,
        'ano_selecionado': ano,
        'mes_selecionado': int(mes) if mes else None,
    }
    
    return render(request, 'home/noticias_lista.html', context)


def workshops(request):
    """View da página de workshops com filtros"""
    
    # Por padrão, mostrar apenas workshops disponíveis
    mostrar_todos = request.GET.get('todos', 'false') == 'true'
    nivel = request.GET.get('nivel')
    status = request.GET.get('status')
    
    if mostrar_todos:
        # Mostrar todos os workshops (incluindo esgotados e encerrados)
        workshops_list = Workshop.objects.all()
    else:
        # Mostrar apenas disponíveis e em breve
        workshops_list = Workshop.objects.filter(status__in=['disponivel', 'em_breve'])
    
    # Filtro por nível
    if nivel:
        workshops_list = workshops_list.filter(nivel=nivel)
    
    # Filtro por status
    if status:
        workshops_list = workshops_list.filter(status=status)
    
    # Ordenar por data de início (mais recentes primeiro)
    workshops_list = workshops_list.order_by('-data_inicio')
    
    # Dados para os filtros
    niveis = Workshop.NIVEL_CHOICES
    status_choices = Workshop.STATUS_CHOICES
    
    context = {
        'workshops': workshops_list,
        'niveis': niveis,
        'status_choices': status_choices,
        'mostrar_todos': mostrar_todos,
        'nivel_selecionado': nivel,
        'status_selecionado': status,
    }
    
    return render(request, 'home/workshops.html', context)

def workshops(request):
    """View da página de workshops com filtros"""
    
    # Por padrão, mostrar apenas workshops disponíveis
    mostrar_todos = request.GET.get('todos', 'false') == 'true'
    nivel = request.GET.get('nivel')
    status = request.GET.get('status')
    
    if mostrar_todos:
        # Mostrar todos os workshops (incluindo esgotados e encerrados)
        workshops_list = Workshop.objects.all()
    else:
        # Mostrar apenas disponíveis e em breve
        workshops_list = Workshop.objects.filter(status__in=['disponivel', 'em_breve'])
    
    # Filtro por nível
    if nivel:
        workshops_list = workshops_list.filter(nivel=nivel)
    
    # Filtro por status
    if status:
        workshops_list = workshops_list.filter(status=status)
    
    # Ordenar por data de início (mais recentes primeiro)
    workshops_list = workshops_list.order_by('-data_inicio')
    
    # Dados para os filtros
    niveis = Workshop.NIVEL_CHOICES
    status_choices = Workshop.STATUS_CHOICES
    
    context = {
        'workshops': workshops_list,
        'niveis': niveis,
        'status_choices': status_choices,
        'mostrar_todos': mostrar_todos,
        'nivel_selecionado': nivel,
        'status_selecionado': status,
    }
    
    return render(request, 'home/workshops.html', context)


def workshop_inscricao(request):
    """View para processar inscrição em workshop"""
    if request.method == 'POST':
        workshop_id = request.POST.get('workshop_id')
        workshop = get_object_or_404(Workshop, id=workshop_id)
        
        if not workshop.esta_disponivel():
            messages.error(request, 'Desculpe, este workshop não está mais disponível.')
            return redirect('workshops')
        
        email = request.POST.get('email')
        if InscricaoWorkshop.objects.filter(workshop=workshop, email=email).exists():
            messages.warning(request, 'Você já está inscrito neste workshop.')
            return redirect('workshops')
        
        inscricao = InscricaoWorkshop(
            workshop=workshop,
            nome=request.POST.get('nome'),
            email=email,
            telefone=request.POST.get('telefone'),
            idade=request.POST.get('idade') or None,
            experiencia=request.POST.get('experiencia'),
            motivacao=request.POST.get('motivacao', ''),
        )
        inscricao.save()
        
        workshop.vagas_ocupadas += 1
        if workshop.vagas_ocupadas >= workshop.vagas_totais:
            workshop.status = 'esgotado'
        workshop.save()
        
        try:
            send_mail(
                subject=f'Inscrição confirmada - {workshop.titulo}',
                message=f'''Olá {inscricao.nome},

Sua inscrição no workshop "{workshop.titulo}" foi confirmada com sucesso!

Detalhes do Workshop:
- Data de início: {workshop.data_inicio.strftime("%d/%m/%Y")}
- Data de término: {workshop.data_fim.strftime("%d/%m/%Y")}
- Carga horária: {workshop.carga_horaria}h
- Número de encontros: {workshop.numero_encontros}

Em breve entraremos em contato com mais informações.

Atenciosamente,
Instituto Mulheres do Sul Global
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, f'Inscrição realizada com sucesso no workshop "{workshop.titulo}"! Verifique seu e-mail.')
        return redirect('workshops')
    
    return redirect('workshops')


def voluntariado(request):
    """View da página de voluntariado"""
    vagas_list = VagaVoluntariado.objects.filter(status='aberta').order_by('-criada_em')
    
    context = {
        'vagas': vagas_list,
    }
    return render(request, 'home/voluntariado.html', context)


def voluntariado_candidatura(request):
    """View para processar candidatura de voluntariado"""
    if request.method == 'POST':
        vaga_id = request.POST.get('vaga_id')
        
        try:
            vaga = VagaVoluntariado.objects.get(id=vaga_id)
        except VagaVoluntariado.DoesNotExist:
            messages.error(request, 'Vaga não encontrada.')
            return redirect('voluntariado')
        
        if not vaga.esta_aberta():
            messages.error(request, 'Desculpe, esta vaga não está mais disponível.')
            return redirect('voluntariado')
        
        email = request.POST.get('email')
        if CandidaturaVoluntariado.objects.filter(vaga=vaga, email=email).exists():
            messages.warning(request, 'Você já se candidatou para esta vaga.')
            return redirect('voluntariado')
        
        candidatura = CandidaturaVoluntariado(
            vaga=vaga,
            nome=request.POST.get('nome'),
            email=email,
            telefone=request.POST.get('telefone'),
            idade=request.POST.get('idade') or None,
            profissao=request.POST.get('profissao', ''),
            experiencia=request.POST.get('experiencia', ''),
            motivacao=request.POST.get('motivacao'),
            disponibilidade=request.POST.get('disponibilidade', ''),
            status='pendente'
        )
        candidatura.save()
        
        vaga.vagas_disponiveis -= 1
        
        if vaga.vagas_disponiveis <= 0:
            vaga.status = 'pausada'
            vaga.vagas_disponiveis = 0
        
        vaga.save()
        
        try:
            send_mail(
                subject=f'Candidatura recebida - {vaga.titulo}',
                message=f'''Olá {candidatura.nome},

Recebemos sua candidatura para a vaga de "{vaga.titulo}"!

Nossa equipe irá analisar sua candidatura e entraremos em contato em breve.

Obrigado pelo interesse em fazer parte do nosso time de voluntários!

Atenciosamente,
Instituto Mulheres do Sul Global
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[candidatura.email],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, f'Candidatura enviada com sucesso para a vaga de "{vaga.titulo}"! Entraremos em contato em breve.')
        return redirect('voluntariado')
    
    return redirect('voluntariado')


def contato(request):
    """View para processar formulário de contato"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        
        try:
            send_mail(
                subject=f'[CONTATO] {assunto} - {nome}',
                message=f'''
Nova mensagem de contato recebida:

Nome: {nome}
Email: {email}
Telefone: {telefone}
Assunto: {assunto}

Mensagem:
{mensagem}
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['contato@mulheresdosulglobal.com'],
                fail_silently=False,
            )
            
            messages.success(request, '✅ Mensagem enviada com sucesso! Entraremos em contato em breve.')
        except Exception as e:
            messages.error(request, '❌ Erro ao enviar mensagem. Tente novamente mais tarde.')
        
        return redirect('contato')
    
    return render(request, 'home/contato.html')


def doacao(request):
    """View para página de doação"""
    return render(request, 'home/doacao.html')