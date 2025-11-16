from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import CandidaturaVoluntariado, InscricaoWorkshop

print("🔧 Arquivo signals.py foi importado!")

# ========================================
# SIGNALS PARA VOLUNTARIADO
# ========================================

@receiver(pre_save, sender=CandidaturaVoluntariado)
def store_old_status_voluntariado(sender, instance, **kwargs):
    """Armazena o status anterior da candidatura"""
    if instance.pk:
        try:
            old_candidatura = CandidaturaVoluntariado.objects.get(pk=instance.pk)
            instance._old_status = old_candidatura.status
            print(f"📝 VOLUNTARIADO - Status antigo: '{instance._old_status}'")
        except CandidaturaVoluntariado.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=CandidaturaVoluntariado)
def atualizar_vagas_voluntariado(sender, instance, created, **kwargs):
    """
    Atualiza vagas baseado nas transições de status:
    - pendente/aprovado/em_analise → recusado: LIBERA vaga (+1)
    - recusado → pendente/aprovado/em_analise: OCUPA vaga (-1)
    """
    if created:
        print(f"✅ VOLUNTARIADO - Nova candidatura criada como '{instance.status}'")
        return
    
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    
    if old_status == new_status:
        return
    
    print(f"🔄 VOLUNTARIADO - Mudança: '{old_status}' → '{new_status}'")
    
    vaga = instance.vaga
    vaga.refresh_from_db()  # ✅ GARANTIR DADOS ATUALIZADOS
    
    # Define quais status OCUPAM vaga
    status_ocupam_vaga = ['pendente', 'aprovado', 'em_analise']
    
    # TRANSIÇÃO: Status que ocupa → Recusado (LIBERA VAGA)
    if old_status in status_ocupam_vaga and new_status == 'recusado':
        print(f"🚀 LIBERANDO VAGA (voluntariado)...")
        
        if vaga.vagas_disponiveis < vaga.vagas_totais:  # ✅ VERIFICA SE NÃO ULTRAPASSA
            vaga.vagas_disponiveis += 1
            print(f"➕ Vagas: {vaga.vagas_disponiveis - 1} → {vaga.vagas_disponiveis}")
            
            # Reabrir vaga se estava fechada
            if vaga.status == 'fechada' and vaga.vagas_disponiveis > 0:
                vaga.status = 'aberta'
                print(f"🔓 Vaga reaberta (fechada → aberta)")
            
            vaga.save()
            print(f"✅ Vaga '{vaga.titulo}' tem {vaga.vagas_disponiveis}/{vaga.vagas_totais} vaga(s) disponível(is)")
    
    # TRANSIÇÃO: Recusado → Status que ocupa (OCUPA VAGA)
    elif old_status == 'recusado' and new_status in status_ocupam_vaga:
        print(f"🚀 OCUPANDO VAGA (voluntariado)...")
        
        if vaga.vagas_disponiveis > 0:
            vaga.vagas_disponiveis -= 1
            print(f"➖ Vagas: {vaga.vagas_disponiveis + 1} → {vaga.vagas_disponiveis}")
            
            # Fechar vaga se esgotou
            if vaga.vagas_disponiveis <= 0:
                vaga.status = 'fechada'
                vaga.vagas_disponiveis = 0
                print(f"🔒 Vaga fechada (aberta → fechada)")
            
            vaga.save()
            print(f"✅ Vaga '{vaga.titulo}' tem {vaga.vagas_disponiveis}/{vaga.vagas_totais} vaga(s) disponível(is)")
        else:
            print(f"⚠️ Não há vagas disponíveis para ocupar!")


@receiver(pre_delete, sender=CandidaturaVoluntariado)
def armazenar_antes_excluir_voluntariado(sender, instance, **kwargs):
    """Armazena dados antes de excluir"""
    instance._status_antes_excluir = instance.status
    instance._vaga_antes_excluir = instance.vaga
    print(f"🗑️ VOLUNTARIADO - Preparando exclusão (status: {instance.status})")


@receiver(post_delete, sender=CandidaturaVoluntariado)
def atualizar_vagas_ao_excluir_voluntariado(sender, instance, **kwargs):
    """Libera vaga ao excluir (se não estava recusada)"""
    status = getattr(instance, '_status_antes_excluir', None)
    vaga = getattr(instance, '_vaga_antes_excluir', None)
    
    if not vaga:
        print(f"⚠️ Vaga não encontrada para liberar")
        return
    
    try:
        # ✅ RECARREGA VAGA DO BANCO
        from .models import VagaVoluntariado
        vaga = VagaVoluntariado.objects.get(pk=vaga.pk)
        
        # Libera vaga se estava ocupando (não recusada)
        if status in ['pendente', 'aprovado', 'em_analise']:
            print(f"🚀 LIBERANDO VAGA (exclusão - status era '{status}')...")
            
            if vaga.vagas_disponiveis < vaga.vagas_totais:
                vaga.vagas_disponiveis += 1
                
                if vaga.status == 'fechada' and vaga.vagas_disponiveis > 0:
                    vaga.status = 'aberta'
                    print(f"🔓 Vaga reaberta")
                
                vaga.save()
                print(f"✅ EXCLUÍDO - Vaga '{vaga.titulo}' agora tem {vaga.vagas_disponiveis}/{vaga.vagas_totais} vaga(s)")
            else:
                print(f"ℹ️ Vaga já estava com total completo: {vaga.vagas_disponiveis}/{vaga.vagas_totais}")
        else:
            print(f"ℹ️ Candidatura recusada excluída - vaga mantém {vaga.vagas_disponiveis}/{vaga.vagas_totais}")
    
    except Exception as e:
        print(f"❌ Erro ao liberar vaga: {e}")


@receiver(post_save, sender=CandidaturaVoluntariado)
def enviar_emails_voluntariado(sender, instance, created, **kwargs):
    """Envia emails quando status muda"""
    if not created:
        old_status = getattr(instance, '_old_status', None)
        new_status = instance.status
        
        # Email de recusa
        if new_status == 'recusado' and old_status != 'recusado':
            from django.core.mail import send_mail
            from django.conf import settings
            
            try:
                send_mail(
                    subject=f'Atualização sobre sua candidatura - {instance.vaga.titulo}',
                    message=f'''Olá {instance.nome},

Obrigado pelo seu interesse em ser voluntário(a) na vaga de "{instance.vaga.titulo}".

Infelizmente, não poderemos prosseguir com sua candidatura neste momento.

Atenciosamente,
Instituto Mulheres do Sul Global
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
                print(f"📧 Email de recusa enviado para {instance.email}")
            except Exception as e:
                print(f"❌ Erro ao enviar email de recusa: {e}")
        
        # Email de aprovação
        elif new_status == 'aprovado' and old_status != 'aprovado':
            from django.core.mail import send_mail
            from django.conf import settings
            
            try:
                send_mail(
                    subject=f'Parabéns! Candidatura aprovada - {instance.vaga.titulo}',
                    message=f'''Olá {instance.nome},

Temos o prazer de informar que sua candidatura para "{instance.vaga.titulo}" foi aprovada!

Entraremos em contato em breve com mais detalhes.

Seja bem-vindo(a) ao nosso time!

Atenciosamente,
Instituto Mulheres do Sul Global
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
                print(f"📧 Email de aprovação enviado para {instance.email}")
            except Exception as e:
                print(f"❌ Erro ao enviar email de aprovação: {e}")


# ========================================
# SIGNALS PARA WORKSHOPS
# ========================================

@receiver(pre_save, sender=InscricaoWorkshop)
def store_old_status_workshop(sender, instance, **kwargs):
    """Armazena o status anterior da inscrição"""
    if instance.pk:
        try:
            old_inscricao = InscricaoWorkshop.objects.get(pk=instance.pk)
            instance._old_status = old_inscricao.status
            print(f"📝 WORKSHOP - Status antigo: '{instance._old_status}'")
        except InscricaoWorkshop.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=InscricaoWorkshop)
def atualizar_vagas_workshop(sender, instance, created, **kwargs):
    """
    Atualiza vagas baseado nas transições de status:
    - pendente/confirmado → recusado: LIBERA vaga
    - recusado → pendente/confirmado: OCUPA vaga
    """
    if created:
        print(f"✅ WORKSHOP - Nova inscrição criada como '{instance.status}'")
        return
    
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    
    if old_status == new_status:
        return
    
    print(f"🔄 WORKSHOP - Mudança: '{old_status}' → '{new_status}'")
    
    workshop = instance.workshop
    workshop.refresh_from_db()  # ✅ GARANTIR DADOS ATUALIZADOS
    
    # Define quais status OCUPAM vaga
    status_ocupam_vaga = ['pendente', 'confirmado']
    
    # TRANSIÇÃO: Status que ocupa → Recusado (LIBERA VAGA)
    if old_status in status_ocupam_vaga and new_status == 'recusado':
        print(f"🚀 LIBERANDO VAGA (workshop)...")
        
        # Verifica se usa vagas_ocupadas ou vagas_disponiveis
        if hasattr(workshop, 'vagas_ocupadas'):
            if workshop.vagas_ocupadas > 0:
                workshop.vagas_ocupadas -= 1
                print(f"➖ Vagas ocupadas: {workshop.vagas_ocupadas + 1} → {workshop.vagas_ocupadas}")
                
                # Reabrir workshop se estava esgotado
                if workshop.status == 'esgotado' and workshop.vagas_ocupadas < workshop.vagas_totais:
                    workshop.status = 'disponivel'
                    print(f"🔓 Workshop reaberto (esgotado → disponível)")
                
                workshop.save()
                print(f"✅ Workshop '{workshop.titulo}' tem {workshop.vagas_disponiveis} vaga(s) disponível(is)")
        else:
            # Usa vagas_disponiveis
            if workshop.vagas_disponiveis < workshop.vagas_totais:
                workshop.vagas_disponiveis += 1
                print(f"➕ Vagas disponíveis: {workshop.vagas_disponiveis - 1} → {workshop.vagas_disponiveis}")
                
                if workshop.status == 'esgotado':
                    workshop.status = 'disponivel'
                    print(f"🔓 Workshop reaberto")
                
                workshop.save()
                print(f"✅ Workshop '{workshop.titulo}' tem {workshop.vagas_disponiveis}/{workshop.vagas_totais} vaga(s)")
    
    # TRANSIÇÃO: Recusado → Status que ocupa (OCUPA VAGA)
    elif old_status == 'recusado' and new_status in status_ocupam_vaga:
        print(f"🚀 OCUPANDO VAGA (workshop)...")
        
        if hasattr(workshop, 'vagas_ocupadas'):
            if workshop.vagas_ocupadas < workshop.vagas_totais:
                workshop.vagas_ocupadas += 1
                print(f"➕ Vagas ocupadas: {workshop.vagas_ocupadas - 1} → {workshop.vagas_ocupadas}")
                
                # Esgotar workshop se atingiu o limite
                if workshop.vagas_ocupadas >= workshop.vagas_totais:
                    workshop.status = 'esgotado'
                    print(f"🔒 Workshop esgotado (disponível → esgotado)")
                
                workshop.save()
                print(f"✅ Workshop '{workshop.titulo}' tem {workshop.vagas_disponiveis} vaga(s) disponível(is)")
        else:
            if workshop.vagas_disponiveis > 0:
                workshop.vagas_disponiveis -= 1
                print(f"➖ Vagas disponíveis: {workshop.vagas_disponiveis + 1} → {workshop.vagas_disponiveis}")
                
                if workshop.vagas_disponiveis <= 0:
                    workshop.status = 'esgotado'
                    workshop.vagas_disponiveis = 0
                    print(f"🔒 Workshop esgotado")
                
                workshop.save()
                print(f"✅ Workshop '{workshop.titulo}' tem {workshop.vagas_disponiveis}/{workshop.vagas_totais} vaga(s)")


@receiver(pre_delete, sender=InscricaoWorkshop)
def armazenar_antes_excluir_workshop(sender, instance, **kwargs):
    """Armazena dados antes de excluir"""
    instance._workshop_antes_excluir = instance.workshop
    instance._status_antes_excluir = instance.status
    print(f"🗑️ WORKSHOP - Preparando exclusão (status: {instance.status})")


@receiver(post_delete, sender=InscricaoWorkshop)
def atualizar_vagas_ao_excluir_workshop(sender, instance, **kwargs):
    """Libera vaga ao excluir (se não estava recusada)"""
    workshop_ref = getattr(instance, '_workshop_antes_excluir', None)
    status = getattr(instance, '_status_antes_excluir', None)
    
    if not workshop_ref:
        print(f"⚠️ Workshop não encontrado para liberar")
        return
    
    try:
        # ✅ RECARREGA WORKSHOP DO BANCO
        from .models import Workshop
        workshop = Workshop.objects.get(pk=workshop_ref.pk)
        
        # Libera vaga se estava ocupando (não recusada)
        if status in ['pendente', 'confirmado']:
            print(f"🚀 LIBERANDO VAGA (exclusão - status era '{status}')...")
            
            if hasattr(workshop, 'vagas_ocupadas'):
                if workshop.vagas_ocupadas > 0:
                    workshop.vagas_ocupadas -= 1
                    
                    if workshop.status == 'esgotado' and workshop.vagas_ocupadas < workshop.vagas_totais:
                        workshop.status = 'disponivel'
                        print(f"🔓 Workshop reaberto")
                    
                    workshop.save()
                    print(f"✅ EXCLUÍDO - Workshop '{workshop.titulo}' tem {workshop.vagas_disponiveis} vaga(s)")
            else:
                if workshop.vagas_disponiveis < workshop.vagas_totais:
                    workshop.vagas_disponiveis += 1
                    
                    if workshop.status == 'esgotado':
                        workshop.status = 'disponivel'
                        print(f"🔓 Workshop reaberto")
                    
                    workshop.save()
                    print(f"✅ EXCLUÍDO - Workshop '{workshop.titulo}' agora tem {workshop.vagas_disponiveis}/{workshop.vagas_totais} vaga(s)")
        else:
            print(f"ℹ️ Inscrição recusada excluída - workshop mantém vagas inalteradas")
    
    except Exception as e:
        print(f"❌ Erro ao liberar vaga: {e}")


@receiver(post_save, sender=InscricaoWorkshop)
def enviar_emails_workshop(sender, instance, created, **kwargs):
    """Envia emails quando status muda"""
    if not created:
        old_status = getattr(instance, '_old_status', None)
        new_status = instance.status
        
        # Email de recusa
        if new_status == 'recusado' and old_status != 'recusado':
            from django.core.mail import send_mail
            from django.conf import settings
            
            try:
                send_mail(
                    subject=f'Atualização sobre sua inscrição - {instance.workshop.titulo}',
                    message=f'''Olá {instance.nome},

Obrigado pelo seu interesse no workshop "{instance.workshop.titulo}".

Infelizmente, não poderemos confirmar sua inscrição neste momento.

Atenciosamente,
Instituto Mulheres do Sul Global
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
                print(f"📧 Email de recusa enviado para {instance.email}")
            except Exception as e:
                print(f"❌ Erro ao enviar email: {e}")
        
        # Email de confirmação
        elif new_status == 'confirmado' and old_status != 'confirmado':
            from django.core.mail import send_mail
            from django.conf import settings
            
            try:
                send_mail(
                    subject=f'Inscrição confirmada - {instance.workshop.titulo}',
                    message=f'''Olá {instance.nome},

Sua inscrição no workshop "{instance.workshop.titulo}" foi confirmada!

Aguarde mais informações em breve.

Atenciosamente,
Instituto Mulheres do Sul Global
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
                print(f"📧 Email de confirmação enviado para {instance.email}")
            except Exception as e:
                print(f"❌ Erro ao enviar email: {e}")


print("✅ Todos os signals foram registrados com sucesso!")