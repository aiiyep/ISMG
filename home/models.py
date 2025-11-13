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
        return self.vagas_totais - self.vagas_ocupadas
    
    @property
    def percentual_ocupacao(self):
        if self.vagas_totais == 0:
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
    
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='inscricoes')
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    idade = models.IntegerField(blank=True, null=True)
    experiencia = models.CharField(max_length=20, choices=EXPERIENCIA_CHOICES)
    motivacao = models.TextField(blank=True)
    inscrito_em = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)
    
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


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    inscrito_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Inscrição Newsletter'
        verbose_name_plural = 'Inscrições Newsletter'
        ordering = ['-inscrito_em']
    
    def __str__(self):
        return self.email