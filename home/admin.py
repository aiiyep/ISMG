from django.contrib import admin
from .models import Workshop, InscricaoWorkshop, VagaVoluntariado, CandidaturaVoluntariado, Newsletter


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'nivel', 'data_inicio', 'data_fim', 'vagas_ocupadas', 'vagas_totais', 'vagas_disponiveis_display', 'status']
    list_filter = ['status', 'nivel', 'gratuito']
    search_fields = ['titulo', 'descricao']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['criado_em', 'atualizado_em', 'vagas_disponiveis_display', 'percentual_ocupacao_display']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'imagem', 'nivel')
        }),
        ('Datas e Carga Horária', {
            'fields': ('data_inicio', 'data_fim', 'carga_horaria', 'numero_encontros')
        }),
        ('Vagas e Preço', {
            'fields': ('vagas_totais', 'vagas_ocupadas', 'vagas_disponiveis_display', 'percentual_ocupacao_display', 'preco', 'gratuito')
        }),
        ('Status', {
            'fields': ('status', 'criado_em', 'atualizado_em')
        }),
    )
    
    def vagas_disponiveis_display(self, obj):
        return obj.vagas_disponiveis
    vagas_disponiveis_display.short_description = 'Vagas Disponíveis'
    
    def percentual_ocupacao_display(self, obj):
        return f"{obj.percentual_ocupacao}%"
    percentual_ocupacao_display.short_description = 'Ocupação'


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
        updated = queryset.update(confirmado=True)
        self.message_user(request, f'{updated} inscrição(ões) confirmada(s).')
    confirmar_inscricoes.short_description = 'Confirmar inscrições selecionadas'
    
    def cancelar_inscricoes(self, request, queryset):
        updated = queryset.update(confirmado=False)
        self.message_user(request, f'{updated} inscrição(ões) cancelada(s).')
    cancelar_inscricoes.short_description = 'Cancelar inscrições selecionadas'


@admin.register(VagaVoluntariado)
class VagaVoluntariadoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'local', 'horas_semanais', 'vagas_disponiveis', 'status', 'criada_em']
    list_filter = ['status', 'tipo', 'criada_em']
    search_fields = ['titulo', 'descricao', 'local']
    date_hierarchy = 'criada_em'
    readonly_fields = ['criada_em', 'atualizada_em', 'total_candidaturas']
    
    fieldsets = (
        ('Informações da Vaga', {
            'fields': ('titulo', 'descricao', 'requisitos', 'tipo')
        }),
        ('Localização e Tempo', {
            'fields': ('local', 'horas_semanais', 'duracao_minima')
        }),
        ('Vagas e Status', {
            'fields': ('vagas_disponiveis', 'status', 'total_candidaturas')
        }),
        ('Datas', {
            'fields': ('criada_em', 'atualizada_em')
        }),
    )
    
    def total_candidaturas(self, obj):
        return obj.candidaturas.count()
    total_candidaturas.short_description = 'Total de Candidaturas'


@admin.register(CandidaturaVoluntariado)
class CandidaturaVoluntariadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'vaga', 'status', 'candidatou_em']
    list_filter = ['status', 'vaga', 'candidatou_em']
    search_fields = ['nome', 'email', 'telefone', 'vaga__titulo']
    date_hierarchy = 'candidatou_em'
    readonly_fields = ['candidatou_em']
    
    fieldsets = (
        ('Candidato', {
            'fields': ('nome', 'email', 'telefone', 'idade', 'profissao')
        }),
        ('Vaga', {
            'fields': ('vaga',)
        }),
        ('Informações Adicionais', {
            'fields': ('experiencia', 'motivacao', 'disponibilidade')
        }),
        ('Status e Data', {
            'fields': ('status', 'candidatou_em')
        }),
    )
    
    actions = ['aprovar_candidaturas', 'recusar_candidaturas', 'analisar_candidaturas']
    
    def aprovar_candidaturas(self, request, queryset):
        updated = queryset.update(status='aprovado')
        self.message_user(request, f'{updated} candidatura(s) aprovada(s). Vagas foram mantidas ocupadas.')
    aprovar_candidaturas.short_description = '✅ Aprovar candidaturas selecionadas'
    
    def recusar_candidaturas(self, request, queryset):
        updated = queryset.update(status='recusado')
        self.message_user(request, f'{updated} candidatura(s) recusada(s). Vagas foram liberadas automaticamente!')
    recusar_candidaturas.short_description = '❌ Recusar candidaturas selecionadas'
    
    def analisar_candidaturas(self, request, queryset):
        updated = queryset.update(status='em_analise')
        self.message_user(request, f'{updated} candidatura(s) em análise.')
    analisar_candidaturas.short_description = '🔍 Colocar em análise'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'inscrito_em', 'ativo']
    list_filter = ['ativo', 'inscrito_em']
    search_fields = ['email']
    date_hierarchy = 'inscrito_em'
    readonly_fields = ['inscrito_em']
    
    actions = ['ativar_inscricoes', 'desativar_inscricoes']
    
    def ativar_inscricoes(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} inscrição(ões) ativada(s).')
    ativar_inscricoes.short_description = 'Ativar inscrições selecionadas'
    
    def desativar_inscricoes(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} inscrição(ões) desativada(s).')
    desativar_inscricoes.short_description = 'Desativar inscrições selecionadas'