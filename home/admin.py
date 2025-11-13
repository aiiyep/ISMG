from django.contrib import admin
from .models import Workshop, InscricaoWorkshop, VagaVoluntariado, CandidaturaVoluntariado, Newsletter


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data_inicio', 'data_fim', 'nivel', 'vagas_disponiveis', 'status', 'preco_display']
    list_filter = ['status', 'nivel', 'gratuito', 'data_inicio']
    search_fields = ['titulo', 'descricao']
    date_hierarchy = 'data_inicio'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'imagem', 'nivel')
        }),
        ('Datas e Carga Horária', {
            'fields': ('data_inicio', 'data_fim', 'numero_encontros', 'carga_horaria')
        }),
        ('Vagas', {
            'fields': ('vagas_totais', 'vagas_ocupadas', 'status')
        }),
        ('Preço', {
            'fields': ('preco', 'gratuito')
        }),
    )
    
    def preco_display(self, obj):
        return 'Gratuito' if obj.gratuito else f'R$ {obj.preco}'
    preco_display.short_description = 'Preço'
    
    def vagas_disponiveis(self, obj):
        return f'{obj.vagas_disponiveis}/{obj.vagas_totais}'
    vagas_disponiveis.short_description = 'Vagas Disponíveis'


@admin.register(InscricaoWorkshop)
class InscricaoWorkshopAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'workshop', 'experiencia', 'inscrito_em', 'confirmado']
    list_filter = ['workshop', 'experiencia', 'confirmado', 'inscrito_em']
    search_fields = ['nome', 'email', 'telefone']
    date_hierarchy = 'inscrito_em'
    readonly_fields = ['inscrito_em']
    
    fieldsets = (
        ('Participante', {
            'fields': ('nome', 'email', 'telefone', 'idade')
        }),
        ('Workshop', {
            'fields': ('workshop', 'experiencia', 'motivacao')
        }),
        ('Status', {
            'fields': ('confirmado', 'inscrito_em')
        }),
    )
    
    actions = ['confirmar_inscricoes', 'cancelar_inscricoes']
    
    def confirmar_inscricoes(self, request, queryset):
        queryset.update(confirmado=True)
        self.message_user(request, f'{queryset.count()} inscrições confirmadas.')
    confirmar_inscricoes.short_description = 'Confirmar inscrições selecionadas'
    
    def cancelar_inscricoes(self, request, queryset):
        queryset.update(confirmado=False)
        self.message_user(request, f'{queryset.count()} inscrições canceladas.')
    cancelar_inscricoes.short_description = 'Cancelar inscrições selecionadas'


@admin.register(VagaVoluntariado)
class VagaVoluntariadoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'horas_semanais', 'vagas_disponiveis', 'status', 'criada_em']
    list_filter = ['status', 'tipo', 'criada_em']
    search_fields = ['titulo', 'descricao', 'requisitos']
    date_hierarchy = 'criada_em'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'requisitos')
        }),
        ('Detalhes da Vaga', {
            'fields': ('tipo', 'local', 'horas_semanais', 'duracao_minima')
        }),
        ('Vagas e Status', {
            'fields': ('vagas_disponiveis', 'status')
        }),
    )
    
    actions = ['abrir_vagas', 'pausar_vagas', 'encerrar_vagas']
    
    def abrir_vagas(self, request, queryset):
        queryset.update(status='aberta')
        self.message_user(request, f'{queryset.count()} vagas abertas.')
    abrir_vagas.short_description = 'Abrir vagas selecionadas'
    
    def pausar_vagas(self, request, queryset):
        queryset.update(status='pausada')
        self.message_user(request, f'{queryset.count()} vagas pausadas.')
    pausar_vagas.short_description = 'Pausar vagas selecionadas'
    
    def encerrar_vagas(self, request, queryset):
        queryset.update(status='encerrada')
        self.message_user(request, f'{queryset.count()} vagas encerradas.')
    encerrar_vagas.short_description = 'Encerrar vagas selecionadas'


@admin.register(CandidaturaVoluntariado)
class CandidaturaVoluntariadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'vaga', 'status', 'candidatou_em']
    list_filter = ['status', 'vaga', 'candidatou_em']
    search_fields = ['nome', 'email', 'telefone', 'profissao']
    date_hierarchy = 'candidatou_em'
    readonly_fields = ['candidatou_em']
    
    fieldsets = (
        ('Candidato', {
            'fields': ('nome', 'email', 'telefone', 'idade', 'profissao')
        }),
        ('Vaga', {
            'fields': ('vaga',)
        }),
        ('Informações da Candidatura', {
            'fields': ('experiencia', 'motivacao', 'disponibilidade')
        }),
        ('Status', {
            'fields': ('status', 'candidatou_em')
        }),
    )
    
    actions = ['aprovar_candidaturas', 'reprovar_candidaturas', 'analisar_candidaturas']
    
    def aprovar_candidaturas(self, request, queryset):
        queryset.update(status='aprovado')
        self.message_user(request, f'{queryset.count()} candidaturas aprovadas.')
    aprovar_candidaturas.short_description = 'Aprovar candidaturas selecionadas'
    
    def reprovar_candidaturas(self, request, queryset):
        queryset.update(status='recusado')
        self.message_user(request, f'{queryset.count()} candidaturas recusadas.')
    reprovar_candidaturas.short_description = 'Recusar candidaturas selecionadas'
    
    def analisar_candidaturas(self, request, queryset):
        queryset.update(status='em_analise')
        self.message_user(request, f'{queryset.count()} candidaturas em análise.')
    analisar_candidaturas.short_description = 'Colocar em análise'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'inscrito_em', 'ativo']
    list_filter = ['ativo', 'inscrito_em']
    search_fields = ['email']
    date_hierarchy = 'inscrito_em'
    readonly_fields = ['inscrito_em']
    
    actions = ['ativar_inscricoes', 'desativar_inscricoes']
    
    def ativar_inscricoes(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, f'{queryset.count()} inscrições ativadas.')
    ativar_inscricoes.short_description = 'Ativar inscrições selecionadas'
    
    def desativar_inscricoes(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, f'{queryset.count()} inscrições desativadas.')
    desativar_inscricoes.short_description = 'Desativar inscrições selecionadas'