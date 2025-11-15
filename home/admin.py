from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html
from django.utils import timezone
from .models import Workshop, InscricaoWorkshop, VagaVoluntariado, CandidaturaVoluntariado, Newsletter, Noticia


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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)
    
    def confirmar_inscricoes(self, request, queryset):
        count = 0
        for inscricao in queryset:
            inscricao.status = 'confirmado'
            inscricao.save()
            count += 1
        self.message_user(request, f'{count} inscrição(ões) confirmada(s).')
    confirmar_inscricoes.short_description = '✅ Confirmar inscrições selecionadas'
    
    def recusar_inscricoes(self, request, queryset):
        count = 0
        for inscricao in queryset:
            inscricao.status = 'recusado'
            inscricao.save()
            count += 1
        self.message_user(request, f'{count} inscrição(ões) recusada(s). Vagas liberadas!')
    recusar_inscricoes.short_description = '❌ Recusar inscrições selecionadas'
    
    def marcar_pendente(self, request, queryset):
        count = 0
        for inscricao in queryset:
            inscricao.status = 'pendente'
            inscricao.save()
            count += 1
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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
    
    def aprovar_candidaturas(self, request, queryset):
        count = 0
        for candidatura in queryset:
            candidatura.status = 'aprovado'
            candidatura.save()
            count += 1
        
        self.message_user(request, f'{count} candidatura(s) aprovada(s).')
    aprovar_candidaturas.short_description = '✅ Aprovar candidaturas selecionadas'
    
    def recusar_candidaturas(self, request, queryset):
        count = 0
        for candidatura in queryset:
            candidatura.status = 'recusado'
            candidatura.save()
            count += 1
        
        self.message_user(request, f'{count} candidatura(s) recusada(s). Vagas liberadas automaticamente!')
    recusar_candidaturas.short_description = '❌ Recusar candidaturas selecionadas'
    
    def analisar_candidaturas(self, request, queryset):
        count = 0
        for candidatura in queryset:
            candidatura.status = 'em_analise'
            candidatura.save()
            count += 1
        
        self.message_user(request, f'{count} candidatura(s) em análise.')
    analisar_candidaturas.short_description = '🔍 Colocar em análise'


# ========================================
# ✅ ADMIN DE NOTÍCIAS COM PREVIEW DA IMAGEM
# ========================================

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
            'description': '⏰ A notícia será publicada automaticamente na data/hora definida em "Data de Publicação"'
        }),
    )
    
    # ✅ Método para exibir o status visual
    def status_publicacao(self, obj):
        agora = timezone.now()
        
        if not obj.publicado:
            return format_html(
                '<span style="color: #666; font-weight: bold;">⚫ Rascunho</span>'
            )
        elif obj.data_publicacao > agora:
            tempo_restante = obj.data_publicacao - agora
            dias = tempo_restante.days
            horas = tempo_restante.seconds // 3600
            
            if dias > 0:
                tempo_txt = f"{dias}d {horas}h"
            else:
                tempo_txt = f"{horas}h"
            
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">🕐 Agendada (em {})</span>',
                tempo_txt
            )
        else:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✅ Publicada</span>'
            )
    
    status_publicacao.short_description = 'Status'
    
    # ✅ Ações personalizadas
    actions = ['publicar_agora', 'marcar_como_rascunho', 'marcar_como_destaque']
    
    def publicar_agora(self, request, queryset):
        """Publica imediatamente as notícias selecionadas"""
        updated = queryset.update(publicado=True, data_publicacao=timezone.now())
        self.message_user(request, f"✅ {updated} notícia(s) publicada(s) imediatamente!")
    
    publicar_agora.short_description = "📢 Publicar agora"
    
    def marcar_como_rascunho(self, request, queryset):
        updated = queryset.update(publicado=False)
        self.message_user(request, f"⚫ {updated} notícia(s) marcada(s) como rascunho.")
    
    marcar_como_rascunho.short_description = "⚫ Marcar como rascunho"
    
    def marcar_como_destaque(self, request, queryset):
        updated = queryset.update(destaque=True)
        self.message_user(request, f"⭐ {updated} notícia(s) marcada(s) como destaque.")
    
    marcar_como_destaque.short_description = "⭐ Marcar como destaque"
    
    # ✅ PREVIEW DA IMAGEM NO ADMIN (USANDO format_html)
    @admin.display(description='Preview da Imagem')
    def imagem_preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<img src="{}" style="max-width: 320px; max-height: 180px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.imagem.url
            )
        return "Nenhuma imagem"
    
    def publicar_noticias(self, request, queryset):
        updated = queryset.update(publicado=True)
        self.message_user(request, f'{updated} notícia(s) publicada(s).')
    publicar_noticias.short_description = '✅ Publicar notícias selecionadas'
    
    def despublicar_noticias(self, request, queryset):
        updated = queryset.update(publicado=False)
        self.message_user(request, f'{updated} notícia(s) despublicada(s).')
    despublicar_noticias.short_description = '❌ Despublicar notícias selecionadas'
    
    def marcar_destaque(self, request, queryset):
        updated = queryset.update(destaque=True)
        self.message_user(request, f'{updated} notícia(s) marcada(s) como destaque.')
    marcar_destaque.short_description = '⭐ Marcar como destaque'
    
    def desmarcar_destaque(self, request, queryset):
        updated = queryset.update(destaque=False)
        self.message_user(request, f'{updated} notícia(s) desmarcada(s) de destaque.')
    desmarcar_destaque.short_description = '☆ Desmarcar destaque'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'data_inscricao', 'ativo']
    list_filter = ['ativo', 'data_inscricao']
    search_fields = ['email']
    list_editable = ['ativo']
    date_hierarchy = 'data_inscricao'
    
    actions = ['exportar_emails', 'marcar_como_ativo', 'marcar_como_inativo']
    
    def exportar_emails(self, request, queryset):
        """Exportar e-mails ativos"""
        emails = queryset.filter(ativo=True).values_list('email', flat=True)
        emails_texto = ', '.join(emails)
        
        self.message_user(request, f"📧 E-mails ativos ({queryset.filter(ativo=True).count()}): {emails_texto}")
    
    exportar_emails.short_description = "📤 Exportar e-mails selecionados"
    
    def marcar_como_ativo(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f"✅ {updated} inscrito(s) marcado(s) como ativo(s).")
    
    marcar_como_ativo.short_description = "✅ Marcar como ativo"
    
    def marcar_como_inativo(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f"❌ {updated} inscrito(s) marcado(s) como inativo(s).")
    
    marcar_como_inativo.short_description = "❌ Marcar como inativo"