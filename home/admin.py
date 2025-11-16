from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Workshop, 
    InscricaoWorkshop, 
    VagaVoluntariado, 
    CandidaturaVoluntariado, 
    NewsletterSubscriber, 
    Noticia
)


# ========================================
# WORKSHOP ADMIN
# ========================================

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 
        'nivel', 
        'data_inicio', 
        'data_fim', 
        'get_vagas_ocupadas',
        'vagas_totais', 
        'get_vagas_disponiveis',
        'status_visual',
    ]
    list_filter = ['status', 'nivel', 'gratuito']
    search_fields = ['titulo', 'descricao']
    date_hierarchy = 'data_inicio'
    readonly_fields = [
        'criado_em', 
        'atualizado_em', 
        'get_vagas_disponiveis', 
        'get_vagas_ocupadas',
        'get_percentual_ocupacao'
    ]
    # ❌ REMOVIDO 'status' de list_editable - estava causando conflito
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'imagem', 'nivel')
        }),
        ('Datas e Carga Horária', {
            'fields': ('data_inicio', 'data_fim', 'carga_horaria', 'numero_encontros')
        }),
        ('Vagas e Preço', {
            'fields': (
                'vagas_totais', 
                'get_vagas_ocupadas',
                'get_vagas_disponiveis',
                'get_percentual_ocupacao',
                'preco', 
                'gratuito'
            )
        }),
        ('Status', {
            'fields': ('status', 'criado_em', 'atualizado_em')
        }),
    )
    
    actions = [
        'marcar_disponivel', 
        'marcar_esgotado', 
        'marcar_em_breve', 
        'marcar_encerrado'
    ]
    
    # ✅ MÉTODOS PARA EXIBIR PROPRIEDADES CALCULADAS
    @admin.display(description='Vagas Disponíveis')
    def get_vagas_disponiveis(self, obj):
        """Exibe vagas disponíveis calculadas"""
        vagas = obj.vagas_disponiveis
        cor = '#10B981' if vagas > 0 else '#EF4444'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', 
            cor, 
            vagas
        )
    
    @admin.display(description='Vagas Ocupadas')
    def get_vagas_ocupadas(self, obj):
        """Exibe vagas ocupadas calculadas"""
        return obj.vagas_ocupadas
    
    @admin.display(description='Ocupação')
    def get_percentual_ocupacao(self, obj):
        """Exibe percentual de ocupação"""
        percentual = obj.percentual_ocupacao
        if percentual >= 80:
            cor = '#EF4444'
        elif percentual >= 50:
            cor = '#F59E0B'
        else:
            cor = '#10B981'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>', 
            cor, 
            percentual
        )
    
    @admin.display(description='Status')
    def status_visual(self, obj):
        cores = {
            'disponivel': ('#10B981', '✅ Disponível'),
            'esgotado': ('#EF4444', '❌ Esgotado'),
            'em_breve': ('#3B82F6', '🕐 Em Breve'),
            'encerrado': ('#6B7280', '📦 Encerrado'),
        }
        cor, texto = cores.get(obj.status, ('#6B7280', obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, texto)
    
    # ✅ ACTIONS
    @admin.action(description="✅ Marcar como Disponível")
    def marcar_disponivel(self, request, queryset):
        updated = queryset.update(status='disponivel')
        self.message_user(request, f"✅ {updated} workshop(s) marcado(s) como Disponível.")
    
    @admin.action(description="❌ Marcar como Esgotado")
    def marcar_esgotado(self, request, queryset):
        updated = queryset.update(status='esgotado')
        self.message_user(request, f"❌ {updated} workshop(s) marcado(s) como Esgotado.")
    
    @admin.action(description="🕐 Marcar como Em Breve")
    def marcar_em_breve(self, request, queryset):
        updated = queryset.update(status='em_breve')
        self.message_user(request, f"🕐 {updated} workshop(s) marcado(s) como Em Breve.")
    
    @admin.action(description="📦 Marcar como Encerrado")
    def marcar_encerrado(self, request, queryset):
        updated = queryset.update(status='encerrado')
        self.message_user(request, f"📦 {updated} workshop(s) encerrado(s).")


# ========================================
# INSCRIÇÃO WORKSHOP ADMIN
# ========================================

@admin.register(InscricaoWorkshop)
class InscricaoWorkshopAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'workshop', 'experiencia', 'status_badge', 'inscrito_em']
    list_filter = ['workshop', 'experiencia', 'status', 'inscrito_em']
    search_fields = ['nome', 'email', 'telefone']
    date_hierarchy = 'inscrito_em'
    readonly_fields = ['inscrito_em']
    # ❌ REMOVIDO list_editable - estava causando conflito
    
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
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        cores = {
            'pendente': ('#F59E0B', '⏳ Pendente'),
            'confirmado': ('#10B981', '✅ Confirmado'),
            'recusado': ('#EF4444', '❌ Recusado'),
        }
        cor, texto = cores.get(obj.status, ('#6B7280', obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, texto)
    
    @admin.action(description='✅ Confirmar inscrições selecionadas')
    def confirmar_inscricoes(self, request, queryset):
        count = queryset.update(status='confirmado')
        self.message_user(request, f'✅ {count} inscrição(ões) confirmada(s).')
    
    @admin.action(description='❌ Recusar inscrições selecionadas')
    def recusar_inscricoes(self, request, queryset):
        count = queryset.update(status='recusado')
        self.message_user(request, f'❌ {count} inscrição(ões) recusada(s).')
    
    @admin.action(description='⏳ Marcar como pendente')
    def marcar_pendente(self, request, queryset):
        count = queryset.update(status='pendente')
        self.message_user(request, f'⏳ {count} inscrição(ões) marcada(s) como pendente.')


# ========================================
# VAGA VOLUNTARIADO ADMIN
# ========================================

@admin.register(VagaVoluntariado)
class VagaVoluntariadoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'local', 'horas_semanais', 'vagas_disponiveis', 'vagas_totais', 'status_badge', 'criada_em']
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
            'fields': ('vagas_totais', 'vagas_disponiveis', 'status', 'total_candidaturas')
        }),
        ('Datas', {
            'fields': ('criada_em', 'atualizada_em')
        }),
    )
    
    actions = ['abrir_vagas', 'fechar_vagas', 'pausar_vagas']
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        cores = {
            'aberta': ('#10B981', '✅ Aberta'),
            'fechada': ('#EF4444', '❌ Fechada'),
            'pausada': ('#F59E0B', '⏸️ Pausada'),
        }
        cor, texto = cores.get(obj.status, ('#6B7280', obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, texto)
    
    @admin.display(description='Candidaturas')
    def total_candidaturas(self, obj):
        count = obj.candidaturas.count()
        ativos = obj.candidaturas.exclude(status='recusado').count()
        return format_html(
            '<span style="font-weight: bold;">{} total ({} ativos)</span>', 
            count, 
            ativos
        )
    
    @admin.action(description='✅ Abrir vagas')
    def abrir_vagas(self, request, queryset):
        count = queryset.update(status='aberta')
        self.message_user(request, f'✅ {count} vaga(s) aberta(s).')
    
    @admin.action(description='❌ Fechar vagas')
    def fechar_vagas(self, request, queryset):
        count = queryset.update(status='fechada')
        self.message_user(request, f'❌ {count} vaga(s) fechada(s).')
    
    @admin.action(description='⏸️ Pausar vagas')
    def pausar_vagas(self, request, queryset):
        count = queryset.update(status='pausada')
        self.message_user(request, f'⏸️ {count} vaga(s) pausada(s).')


# ========================================
# CANDIDATURA VOLUNTARIADO ADMIN
# ========================================

@admin.register(CandidaturaVoluntariado)
class CandidaturaVoluntariadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'vaga', 'status_badge', 'candidatou_em']
    list_filter = ['status', 'vaga', 'candidatou_em']
    search_fields = ['nome', 'email', 'telefone', 'vaga__titulo']
    date_hierarchy = 'candidatou_em'
    readonly_fields = ['candidatou_em']
    # ❌ REMOVIDO list_editable
    
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
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        cores = {
            'pendente': ('#F59E0B', '⏳ Pendente'),
            'em_analise': ('#3B82F6', '🔍 Em Análise'),
            'aprovado': ('#10B981', '✅ Aprovado'),
            'recusado': ('#EF4444', '❌ Recusado'),
        }
        cor, texto = cores.get(obj.status, ('#6B7280', obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, texto)
    
    @admin.action(description='✅ Aprovar candidaturas selecionadas')
    def aprovar_candidaturas(self, request, queryset):
        count = queryset.update(status='aprovado')
        self.message_user(request, f'✅ {count} candidatura(s) aprovada(s).')
    
    @admin.action(description='❌ Recusar candidaturas selecionadas')
    def recusar_candidaturas(self, request, queryset):
        count = queryset.update(status='recusado')
        self.message_user(request, f'❌ {count} candidatura(s) recusada(s).')
    
    @admin.action(description='🔍 Colocar em análise')
    def analisar_candidaturas(self, request, queryset):
        count = queryset.update(status='em_analise')
        self.message_user(request, f'🔍 {count} candidatura(s) em análise.')


# ========================================
# NOTÍCIA ADMIN
# ========================================

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'status_publicacao', 'data_publicacao', 'destaque_badge', 'visualizacoes', 'autor']
    list_filter = ['categoria', 'publicado', 'destaque', 'data_publicacao']
    search_fields = ['titulo', 'conteudo', 'autor']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'data_publicacao'
    # ❌ REMOVIDO list_editable
    readonly_fields = ['visualizacoes', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('titulo', 'subtitulo', 'slug', 'conteudo', 'imagem', 'categoria')
        }),
        ('Publicação', {
            'fields': ('publicado', 'data_publicacao', 'destaque', 'autor'),
            'description': '⏰ A notícia será publicada automaticamente na data/hora definida'
        }),
        ('Estatísticas', {
            'fields': ('visualizacoes', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publicar_agora', 'marcar_como_rascunho', 'marcar_como_destaque', 'desmarcar_destaque']
    
    @admin.display(description='Destaque')
    def destaque_badge(self, obj):
        if obj.destaque:
            return format_html('<span style="color: #F59E0B; font-weight: bold;">⭐ Sim</span>')
        return format_html('<span style="color: #6B7280;">☆ Não</span>')
    
    @admin.display(description='Status')
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
    
    @admin.action(description="📢 Publicar agora")
    def publicar_agora(self, request, queryset):
        updated = queryset.update(publicado=True, data_publicacao=timezone.now())
        self.message_user(request, f"✅ {updated} notícia(s) publicada(s)!")
    
    @admin.action(description="⚫ Marcar como rascunho")
    def marcar_como_rascunho(self, request, queryset):
        updated = queryset.update(publicado=False)
        self.message_user(request, f"⚫ {updated} notícia(s) como rascunho.")
    
    @admin.action(description="⭐ Marcar como destaque")
    def marcar_como_destaque(self, request, queryset):
        updated = queryset.update(destaque=True)
        self.message_user(request, f"⭐ {updated} notícia(s) como destaque.")
    
    @admin.action(description="☆ Desmarcar destaque")
    def desmarcar_destaque(self, request, queryset):
        updated = queryset.update(destaque=False)
        self.message_user(request, f"☆ {updated} notícia(s) desmarcada(s).")
    
    def save_model(self, request, obj, form, change):
        """Envia newsletter ao criar nova notícia em destaque"""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        if is_new and obj.destaque and obj.publicado:
            from .views import enviar_newsletter_nova_noticia
            try:
                enviar_newsletter_nova_noticia(obj)
                self.message_user(request, "✅ Newsletter enviada para todos os inscritos!", level='success')
            except Exception as e:
                self.message_user(request, f"⚠️ Notícia salva, mas erro ao enviar newsletter: {e}", level='warning')


# ========================================
# NEWSLETTER ADMIN
# ========================================

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'data_inscricao', 'ativo_badge')
    list_filter = ('ativo', 'data_inscricao')
    search_fields = ('email', 'nome')
    date_hierarchy = 'data_inscricao'
    readonly_fields = ('token', 'data_inscricao')
    actions = ['ativar_inscritos', 'desativar_inscritos', 'enviar_email_teste']
    
    @admin.display(description='Status')
    def ativo_badge(self, obj):
        if obj.ativo:
            return format_html('<span style="color: #10b981; font-weight: bold;">✅ Ativo</span>')
        return format_html('<span style="color: #ef4444; font-weight: bold;">❌ Inativo</span>')

    @admin.action(description="✅ Ativar inscritos selecionados")
    def ativar_inscritos(self, request, queryset):
        count = queryset.update(ativo=True)
        self.message_user(request, f"✅ {count} inscrito(s) ativado(s).")

    @admin.action(description="❌ Desativar inscritos selecionados")
    def desativar_inscritos(self, request, queryset):
        count = queryset.update(ativo=False)
        self.message_user(request, f"❌ {count} inscrito(s) desativado(s).")
    
    @admin.action(description="📧 Enviar email de boas-vindas")
    def enviar_email_teste(self, request, queryset):
        from .views import enviar_email_boas_vindas
        count = 0
        for inscrito in queryset.filter(ativo=True):
            try:
                enviar_email_boas_vindas(inscrito.email)
                count += 1
            except Exception as e:
                self.message_user(request, f"❌ Erro ao enviar para {inscrito.email}: {e}", level='error')
        
        self.message_user(request, f"📧 Email de teste enviado para {count} inscrito(s).")