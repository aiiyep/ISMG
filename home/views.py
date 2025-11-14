from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Workshop, InscricaoWorkshop, VagaVoluntariado, CandidaturaVoluntariado, Newsletter, Noticia

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


def home(request):
    """View da página inicial"""
    if request.method == 'POST':
        # Inscrição na newsletter
        email = request.POST.get('email')
        if email:
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Obrigado por se inscrever na nossa newsletter!')
            else:
                messages.info(request, 'Este e-mail já está cadastrado.')
        return redirect('home')
    
    # Buscar workshops disponíveis
    workshops_destaque = Workshop.objects.filter(status='disponivel').order_by('data_inicio')[:3]
    
    # Buscar vagas de voluntariado abertas
    vagas_destaque = VagaVoluntariado.objects.filter(status='aberta').order_by('-criada_em')[:3]
    
    # Buscar notícias publicadas (máximo 3 para a home)
    noticias = Noticia.objects.filter(publicado=True).order_by('-destaque', '-data_publicacao')[:3]
    
    context = {
        'workshops_destaque': workshops_destaque,
        'vagas_destaque': vagas_destaque,
        'noticias': noticias,
    }
    return render(request, 'home/home.html', context)


def workshops(request):
    """View da página de workshops"""
    workshops_list = Workshop.objects.filter(status='disponivel').order_by('data_inicio')
    
    context = {
        'workshops': workshops_list,
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


def newsletter_inscricao(request):
    """View para processar inscrição na newsletter"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Obrigado por se inscrever na nossa newsletter!')
            else:
                messages.info(request, 'Este e-mail já está cadastrado.')
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')


# ========================================
# ✅ NOVA VIEW: DETALHES DA NOTÍCIA
# ========================================

def noticia_detalhe(request, id):
    """View para exibir os detalhes completos de uma notícia"""
    noticia = get_object_or_404(Noticia, id=id, publicado=True)
    
    # Buscar notícias relacionadas (mesma categoria, excluindo a atual)
    noticias_relacionadas = Noticia.objects.filter(
        categoria=noticia.categoria,
        publicado=True
    ).exclude(id=noticia.id).order_by('-data_publicacao')[:3]
    
    context = {
        'noticia': noticia,
        'noticias_relacionadas': noticias_relacionadas,
    }
    return render(request, 'home/noticia_detalhe.html', context)



def contato(request):
    """View para processar formulário de contato"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        
        # Enviar email
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