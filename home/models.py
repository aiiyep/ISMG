from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid

# ========================================
# WORKSHOP
# ========================================

class Workshop(models.Model):
    NIVEL_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('todos', 'Todos os níveis'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Vagas Disponíveis'),
        ('esgotado', 'Esgotado'),
        ('em_breve', 'Em Breve'),
        ('encerrado', 'Encerrado'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    imagem = models.ImageField(upload_to='workshops/', blank=True, null=True, verbose_name="Imagem")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    carga_horaria = models.IntegerField(verbose_name="Carga horária (horas)")
    numero_encontros = models.IntegerField(verbose_name="Número de Encontros")
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, verbose_name="Nível")
    vagas_totais = models.IntegerField(verbose_name="Total de Vagas")
    vagas_ocupadas = models.IntegerField(default=0, verbose_name="Vagas Ocupadas")
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Preço")
    gratuito = models.BooleanField(default=False, verbose_name="Gratuito")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel', verbose_name="Status")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = 'Workshop'
        verbose_name_plural = 'Workshops'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.titulo
    
    @property
    def vagas_disponiveis(self):
        """Calcula vagas disponíveis em tempo real baseado nas inscrições não recusadas"""
        inscricoes_ativas = self.inscricoes.exclude(status='recusado').count()
        vagas_livres = self.vagas_totais - inscricoes_ativas
        return max(0, vagas_livres)
    
    
    @property
    def percentual_ocupacao(self):
        """Calcula percentual de ocupação"""
        if self.vagas_totais is None or self.vagas_totais == 0:
            return 0
        # Calcula vagas ocupadas baseado nas inscrições
        inscricoes_ativas = self.inscricoes.exclude(status='recusado').count()
        return int((inscricoes_ativas / self.vagas_totais) * 100)
    
    def esta_disponivel(self):
        """Verifica se workshop está disponível"""
        return self.status == 'disponivel' and self.vagas_disponiveis > 0
    
    def atualizar_status(self):
        """Atualiza status baseado nas vagas disponíveis"""
        if self.vagas_disponiveis <= 0:
            self.status = 'esgotado'
        elif self.vagas_disponiveis > 0 and self.status == 'esgotado':
            self.status = 'disponivel'
        self.save(update_fields=['status'])


class InscricaoWorkshop(models.Model):
    EXPERIENCIA_CHOICES = [
        ('nenhuma', 'Nenhuma experiência'),
        ('basica', 'Básica'),
        ('intermediaria', 'Intermediária'),
        ('avancada', 'Avançada'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('recusado', 'Recusado'),
    ]
    
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='inscricoes')
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    idade = models.IntegerField(blank=True, null=True, verbose_name="Idade")
    experiencia = models.CharField(max_length=20, choices=EXPERIENCIA_CHOICES, verbose_name="Experiência")
    motivacao = models.TextField(blank=True, verbose_name="Motivação")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    inscrito_em = models.DateTimeField(auto_now_add=True, verbose_name="Inscrito em")
    
    class Meta:
        verbose_name = 'Inscrição em Workshop'
        verbose_name_plural = 'Inscrições em Workshops'
        ordering = ['-inscrito_em']
        unique_together = ['workshop', 'email']
    
    def __str__(self):
        return f"{self.nome} - {self.workshop.titulo} ({self.status})"


# ========================================
# VOLUNTARIADO
# ========================================

class VagaVoluntariado(models.Model):
    TIPO_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('fechada', 'Fechada'),
        ('pausada', 'Pausada'),
        ('encerrada', 'Encerrada'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    requisitos = models.TextField(verbose_name="Requisitos", help_text="Um requisito por linha")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    local = models.CharField(max_length=200, blank=True, verbose_name="Local")
    horas_semanais = models.IntegerField(verbose_name="Horas Semanais")
    duracao_minima = models.CharField(max_length=100, verbose_name="Duração Mínima", help_text="Ex: 3 meses, 6 meses, flexível")
    vagas_totais = models.IntegerField(verbose_name="Total de Vagas")
    vagas_ocupadas = models.IntegerField(default=0, verbose_name="Vagas Ocupadas")
    vagas_disponiveis = models.IntegerField(verbose_name="Vagas Disponíveis")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta', verbose_name="Status")
    criada_em = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    atualizada_em = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")
    
    class Meta:
        verbose_name = 'Vaga de Voluntariado'
        verbose_name_plural = 'Vagas de Voluntariado'
        ordering = ['-criada_em']
    
    def __str__(self):
        return self.titulo
    
    vagas_totais = models.IntegerField(verbose_name="Total de Vagas")  # ✅ DEVE EXISTIR
    vagas_disponiveis = models.IntegerField(verbose_name="Vagas Disponíveis")
    
    def esta_aberta(self):
        """Verifica se vaga está aberta"""
        return self.status == 'aberta' and self.vagas_disponiveis > 0
    
    def atualizar_vagas(self):
        """Atualiza vagas baseado em candidaturas ativas"""
        candidaturas_ativas = self.candidaturas.exclude(status='recusado').count()
        vagas_livres = self.vagas_totais - candidaturas_ativas
        self.vagas_disponiveis = max(0, vagas_livres)
        
        if self.vagas_disponiveis <= 0:
            self.status = 'fechada'
        elif self.status == 'fechada' and self.vagas_disponiveis > 0:
            self.status = 'aberta'
        
        self.save(update_fields=['vagas_disponiveis', 'status'])


class CandidaturaVoluntariado(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]
    
    vaga = models.ForeignKey(VagaVoluntariado, on_delete=models.CASCADE, related_name='candidaturas')
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    idade = models.IntegerField(blank=True, null=True, verbose_name="Idade")
    profissao = models.CharField(max_length=200, blank=True, verbose_name="Profissão")
    experiencia = models.TextField(blank=True, verbose_name="Experiência")
    motivacao = models.TextField(verbose_name="Motivação")
    disponibilidade = models.TextField(blank=True, verbose_name="Disponibilidade")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    candidatou_em = models.DateTimeField(auto_now_add=True, verbose_name="Candidatou em")
    
    class Meta:
        verbose_name = 'Candidatura de Voluntariado'
        verbose_name_plural = 'Candidaturas de Voluntariado'
        ordering = ['-candidatou_em']
    
    def __str__(self):
        return f"{self.nome} - {self.vaga.titulo} ({self.status})"


# ========================================
# NOTÍCIAS - MANAGER CUSTOMIZADO
# ========================================

class NoticiaManager(models.Manager):
    def publicadas(self):
        """Retorna apenas notícias publicadas e com data <= agora"""
        return self.filter(
            publicado=True,
            data_publicacao__lte=timezone.now()
        )
    
    def agendadas(self):
        """Retorna notícias agendadas para o futuro"""
        return self.filter(
            publicado=True,
            data_publicacao__gt=timezone.now()
        )
    
    def destaques(self):
        """Retorna notícias em destaque publicadas"""
        return self.publicadas().filter(destaque=True)


class Noticia(models.Model):
    CATEGORIA_CHOICES = [
        ('evento', 'Evento'),
        ('projeto', 'Projeto'),
        ('conquista', 'Conquista'),
        ('parceria', 'Parceria'),
        ('noticia', 'Notícia Geral'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name='Título')
    subtitulo = models.CharField(max_length=300, blank=True, verbose_name='Subtítulo')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='Slug')
    conteudo = models.TextField(verbose_name='Conteúdo')
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name='Imagem')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='noticia', verbose_name='Categoria')
    
    publicado = models.BooleanField(default=False, verbose_name='Publicado')
    destaque = models.BooleanField(default=False, verbose_name='Destaque')
    visualizacoes = models.IntegerField(default=0, verbose_name='Visualizações')
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    data_publicacao = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Publicação',
        help_text='Data e hora em que a notícia será publicada automaticamente'
    )
    autor = models.CharField(max_length=100, blank=True, verbose_name='Autor')
    
    objects = NoticiaManager()
    
    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'
        ordering = ['-data_publicacao']
    
    def save(self, *args, **kwargs):
        # Gera slug automaticamente se não existir
        if not self.slug:
            base_slug = slugify(self.titulo)
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        
        # Verifica se é nova notícia
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Envia newsletter apenas para novas notícias em destaque
        if is_new and self.destaque and self.publicado:
            from .views import enviar_newsletter_nova_noticia
            try:
                enviar_newsletter_nova_noticia(self)
            except Exception as e:
                print(f"Erro ao enviar newsletter: {e}")
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_publicada(self):
        """Verifica se notícia está publicada"""
        return self.publicado and self.data_publicacao <= timezone.now()


# ========================================
# NEWSLETTER
# ========================================

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="E-mail")
    nome = models.CharField(max_length=100, blank=True, verbose_name="Nome")
    data_inscricao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Inscrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    token = models.CharField(max_length=100, unique=True, blank=True, verbose_name="Token de Confirmação")

    class Meta:
        verbose_name = "Inscrito na Newsletter"
        verbose_name_plural = "Inscritos na Newsletter"
        ordering = ['-data_inscricao']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)