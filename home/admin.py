from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Workshop, InscricaoWorkshop, VagaVoluntariado, CandidaturaVoluntariado, NewsletterSubscriber, Noticia


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'nivel', 'data_inicio', 'data_fim', 'vagas_ocupadas', 'vagas_totais', 'vagas_disponiveis_display', 'status_visual', 'status']
    list_filter = ['status', 'nivel', 'gratuito']
    search_fields = ['titulo', 'descricao']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['criado_em', 'atualizado_em', 'vagas_disponiveis_display', 'percentual_ocupacao_display']
    list_editable = ['status']
    
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
    
    actions = ['marcar_disponivel', 'marcar_esgotado', 'marcar_em_breve', 'marcar_encerrado', 'reabrir_workshop']
    
    def vagas_disponiveis_display(self, obj):
        return obj.vagas_disponiveis
    vagas_disponiveis_display.short_description = 'Vagas Disponíveis'
    
    def percentual_ocupacao_display(self, obj):
        return f"{obj.percentual_ocupacao}%"
    percentual_ocupacao_display.short_description = 'Ocupação'
    
    @admin.display(description='Status Visual')
    def status_visual(self, obj):
        cores = {
            'disponivel': ('#10B981', '✅ Disponível'),
            'esgotado': ('#EF4444', '❌ Esgotado'),
            'em_breve': ('#3B82F6', '🕐 Em Breve'),
            'encerrado': ('#6B7280', '📦 Encerrado'),
        }
        cor, texto = cores.get(obj.status, ('#6B7280', obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, texto)
    
    def marcar_disponivel(self, request, queryset):
        updated = queryset.update(status='disponivel')
        self.message_user(request, f"✅ {updated} workshop(s) marcado(s) como Disponível.")
    marcar_disponivel.short_description = "✅ Marcar como Disponível"
    
    def marcar_esgotado(self, request, queryset):
        updated = queryset.update(status='esgotado')
        self.message_user(request, f"❌ {updated} workshop(s) marcado(s) como Esgotado.")
    marcar_esgotado.short_description = "❌ Marcar como Esgotado"
    
    def marcar_em_breve(self, request, queryset):
        updated = queryset.update(status='em_breve')
        self.message_user(request, f"🕐 {updated} workshop(s) marcado(s) como Em Breve.")
    marcar_em_breve.short_description = "🕐 Marcar como Em Breve"
    
    def marcar_encerrado(self, request, queryset):
        updated = 0
        for workshop in queryset:
            workshop.status = 'encerrado'
            workshop.vagas_ocupadas = workshop.vagas_totais
            workshop.save()
            updated += 1
        self.message_user(request, f"📦 {updated} workshop(s) encerrado(s) e vagas esgotadas automaticamente.")
    marcar_encerrado.short_description = "📦 Marcar como Encerrado (esgota vagas)"
    
    def reabrir_workshop(self, request, queryset):
        updated = 0
        for workshop in queryset:
            if workshop.status == 'encerrado':
                workshop.status = 'disponivel'
                workshop.vagas_ocupadas = 0
                workshop.save()
                updated += 1
        if updated > 0:
            self.message_user(request, f"♻️ {updated} workshop(s) reaberto(s) com vagas liberadas.")
        else:
            self.message_user(request, "⚠️ Nenhum workshop encerrado foi selecionado.", level='warning')
    reabrir_workshop.short_description = "♻️ Reabrir workshops encerrados"


@admin.register(InscricaoWorkshop)
class InscricaoWorkshopAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'workshop', 'experiencia', 'status', 'inscrito_em']
    list_filter = ['workshop', 'experiencia', 'status', 'inscrito_em']
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
        ('Status e Data', {
            'fields': ('status', 'inscrito_em')
        }),
    )
    
    actions = ['confirmar_inscricoes', 'recusar_inscricoes', 'marcar_pendente']
    
    def confirmar_inscricoes(self, request, queryset):
        count = queryset.update(status='confirmado')
        self.message_user(request, f'{count} inscrição(ões) confirmada(s).')
    confirmar_inscricoes.short_description = '✅ Confirmar inscrições selecionadas'
    
    def recusar_inscricoes(self, request, queryset):
        count = queryset.update(status='recusado')
        self.message_user(request, f'{count} inscrição(ões) recusada(s).')
    recusar_inscricoes.short_description = '❌ Recusar inscrições selecionadas'
    
    def marcar_pendente(self, request, queryset):
        count = queryset.update(status='pendente')
        self.message_user(request, f'{count} inscrição(ões) marcada(s) como pendente.')
    marcar_pendente.short_description = '⏳ Marcar como pendente'


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
        count = queryset.update(status='aprovado')
        self.message_user(request, f'{count} candidatura(s) aprovada(s).')
    aprovar_candidaturas.short_description = '✅ Aprovar candidaturas selecionadas'
    
    def recusar_candidaturas(self, request, queryset):
        count = queryset.update(status='recusado')
        self.message_user(request, f'{count} candidatura(s) recusada(s).')
    recusar_candidaturas.short_description = '❌ Recusar candidaturas selecionadas'
    
    def analisar_candidaturas(self, request, queryset):
        count = queryset.update(status='em_analise')
        self.message_user(request, f'{count} candidatura(s) em análise.')
    analisar_candidaturas.short_description = '🔍 Colocar em análise'


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'status_publicacao', 'data_publicacao', 'destaque', 'autor']
    list_filter = ['categoria', 'publicado', 'destaque', 'data_publicacao']
    search_fields = ['titulo', 'conteudo', 'autor']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'data_publicacao'
    list_editable = ['destaque']
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('titulo', 'subtitulo', 'slug', 'conteudo', 'imagem', 'categoria')
        }),
        ('Publicação', {
            'fields': ('publicado', 'data_publicacao', 'destaque', 'autor'),
            'description': '⏰ A notícia será publicada automaticamente na data/hora definida'
        }),
    )
    
    actions = ['publicar_agora', 'marcar_como_rascunho', 'marcar_como_destaque', 'desmarcar_destaque']
    
    def status_publicacao(self, obj):
        agora = timezone.now()
        if not obj.publicado:
            return format_html('<span style="color: #666; font-weight: bold;">⚫ Rascunho</span>')
        elif obj.data_publicacao > agora:
            tempo_restante = obj.data_publicacao - agora
            dias = tempo_restante.days
            horas = tempo_restante.seconds // 3600
            tempo_txt = f"{dias}d {horas}h" if dias > 0 else f"{horas}h"
            return format_html('<span style="color: #f59e0b; font-weight: bold;">🕐 Agendada (em {})</span>', tempo_txt)
        else:
            return format_html('<span style="color: #10b981; font-weight: bold;">✅ Publicada</span>')
    status_publicacao.short_description = 'Status'
    
    def publicar_agora(self, request, queryset):
        updated = queryset.update(publicado=True, data_publicacao=timezone.now())
        self.message_user(request, f"✅ {updated} notícia(s) publicada(s)!")
    publicar_agora.short_description = "📢 Publicar agora"
    
    def marcar_como_rascunho(self, request, queryset):
        updated = queryset.update(publicado=False)
        self.message_user(request, f"⚫ {updated} notícia(s) como rascunho.")
    marcar_como_rascunho.short_description = "⚫ Marcar como rascunho"
    
    def marcar_como_destaque(self, request, queryset):
        updated = queryset.update(destaque=True)
        self.message_user(request, f"⭐ {updated} notícia(s) como destaque.")
    marcar_como_destaque.short_description = "⭐ Marcar como destaque"
    
    def desmarcar_destaque(self, request, queryset):
        updated = queryset.update(destaque=False)
        self.message_user(request, f"☆ {updated} notícia(s) desmarcada(s).")
    desmarcar_destaque.short_description = "☆ Desmarcar destaque"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'data_inscricao', 'ativo')
    list_filter = ('ativo', 'data_inscricao')
    search_fields = ('email', 'nome')
    actions = ['ativar_inscritos', 'desativar_inscritos']

    def ativar_inscritos(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, f"{queryset.count()} inscritos foram ativados.")
    ativar_inscritos.short_description = "Ativar inscritos selecionados"

    def desativar_inscritos(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, f"{queryset.count()} inscritos foram desativados.")
    desativar_inscritos.short_description = "Desativar inscritos selecionados"