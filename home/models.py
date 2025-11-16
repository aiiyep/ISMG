from django.db import models
from django.utils import timezone

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
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    imagem = models.ImageField(upload_to='workshops/', blank=True, null=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    carga_horaria = models.IntegerField(help_text="Carga horária em horas")
    numero_encontros = models.IntegerField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    vagas_totais = models.IntegerField()
    vagas_ocupadas = models.IntegerField(default=0)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gratuito = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Workshop'
        verbose_name_plural = 'Workshops'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.titulo
    
    @property
    def vagas_disponiveis(self):
        if self.vagas_totais is None or self.vagas_ocupadas is None:
            return 0
        return self.vagas_totais - self.vagas_ocupadas
    
    @property
    def percentual_ocupacao(self):
        if self.vagas_totais is None or self.vagas_totais == 0:
            return 0
        if self.vagas_ocupadas is None:
            return 0
        return int((self.vagas_ocupadas / self.vagas_totais) * 100)
    
    def esta_disponivel(self):
        return self.status == 'disponivel' and self.vagas_disponiveis > 0


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
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    idade = models.IntegerField(blank=True, null=True)
    experiencia = models.CharField(max_length=20, choices=EXPERIENCIA_CHOICES)
    motivacao = models.TextField(blank=True)
    inscrito_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    class Meta:
        verbose_name = 'Inscrição em Workshop'
        verbose_name_plural = 'Inscrições em Workshops'
        ordering = ['-inscrito_em']
        unique_together = ['workshop', 'email']
    
    def __str__(self):
        return f"{self.nome} - {self.workshop.titulo}"


class VagaVoluntariado(models.Model):
    TIPO_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('pausada', 'Pausada'),
        ('encerrada', 'Encerrada'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    requisitos = models.TextField(help_text="Um requisito por linha")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    local = models.CharField(max_length=200, blank=True)
    horas_semanais = models.IntegerField()
    duracao_minima = models.CharField(max_length=100, help_text="Ex: 3 meses, 6 meses, flexível")
    vagas_disponiveis = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Vaga de Voluntariado'
        verbose_name_plural = 'Vagas de Voluntariado'
        ordering = ['-criada_em']
    
    def __str__(self):
        return self.titulo
    
    def esta_aberta(self):
        return self.status == 'aberta' and self.vagas_disponiveis > 0


class CandidaturaVoluntariado(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]
    
    vaga = models.ForeignKey(VagaVoluntariado, on_delete=models.CASCADE, related_name='candidaturas')
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    idade = models.IntegerField(blank=True, null=True)
    profissao = models.CharField(max_length=200, blank=True)
    experiencia = models.TextField(blank=True)
    motivacao = models.TextField()
    disponibilidade = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    candidatou_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Candidatura de Voluntariado'
        verbose_name_plural = 'Candidaturas de Voluntariado'
        ordering = ['-candidatou_em']
    
    def __str__(self):
        return f"{self.nome} - {self.vaga.titulo}"

# ✅ Manager customizado ANTES do modelo
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
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    conteudo = models.TextField(verbose_name='Conteúdo')
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name='Imagem')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='noticia', verbose_name='Categoria')
    
    publicado = models.BooleanField(default=False, verbose_name='Publicado')
    destaque = models.BooleanField(default=False, verbose_name='Destaque')
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
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = slugify(self.titulo) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_publicada(self):
        return self.publicado and self.data_publicacao <= timezone.now()


class Newsletter(models.Model):
    email = models.EmailField(unique=True, verbose_name='E-mail')
    data_inscricao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Inscrição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Inscrito Newsletter'
        verbose_name_plural = 'Inscritos Newsletter'
        ordering = ['-data_inscricao']

    def __str__(self):
        return self.email
