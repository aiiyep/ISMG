from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import CandidaturaVoluntariado


@receiver(pre_save, sender=CandidaturaVoluntariado)
def store_old_status(sender, instance, **kwargs):
    """
    Armazena o status anterior antes de salvar
    """
    if instance.pk:  # Se já existe no banco
        try:
            old_candidatura = CandidaturaVoluntariado.objects.get(pk=instance.pk)
            instance._old_status = old_candidatura.status
            print(f"📝 Status antigo armazenado: '{instance._old_status}'")
        except CandidaturaVoluntariado.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=CandidaturaVoluntariado)
def atualizar_vagas_ao_mudar_status(sender, instance, created, **kwargs):
    """
    Atualiza vagas quando status é alterado no Django Admin
    """
    # Ignorar quando candidatura é criada (tratado na view)
    if created:
        print(f"✅ Nova candidatura criada - status: {instance.status}")
        return
    
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    
    # Se status não mudou, não fazer nada
    if old_status == new_status:
        print(f"ℹ️ Status não mudou ({new_status})")
        return
    
    print(f"🔄 Mudança de status: '{old_status}' → '{new_status}'")
    
    vaga = instance.vaga
    
    # ✅ RECUSAR: Libera vaga (incrementa +1)
    if new_status == 'recusado' and old_status != 'recusado':
        print(f"📊 Antes de recusar: {vaga.vagas_disponiveis} vagas disponíveis")
        
        vaga.vagas_disponiveis += 1
        
        # Reabrir vaga se estava pausada
        if vaga.status == 'pausada' and vaga.vagas_disponiveis > 0:
            vaga.status = 'aberta'
            print(f"🔓 Vaga reaberta (pausada → aberta)")
        
        vaga.save()
        print(f"✅ RECUSADO: Vaga '{vaga.titulo}' liberada! Agora tem {vaga.vagas_disponiveis} vaga(s) disponível(is)")
    
    # ✅ APROVAR: Mantém vaga ocupada
    elif new_status == 'aprovado' and old_status != 'aprovado':
        print(f"ℹ️ APROVADO: Vaga '{vaga.titulo}' mantém {vaga.vagas_disponiveis} vaga(s) (já estava ocupada)")


@receiver(pre_delete, sender=CandidaturaVoluntariado)
def armazenar_status_antes_excluir(sender, instance, **kwargs):
    """
    Armazena status antes de excluir
    """
    instance._status_antes_excluir = instance.status
    instance._vaga_antes_excluir = instance.vaga
    print(f"🗑️ Preparando para excluir candidatura com status: {instance.status}")


@receiver(post_delete, sender=CandidaturaVoluntariado)
def atualizar_vagas_ao_excluir(sender, instance, **kwargs):
    """
    Libera vaga quando candidatura é excluída (exceto se já estava recusada)
    """
    status = getattr(instance, '_status_antes_excluir', None)
    vaga = getattr(instance, '_vaga_antes_excluir', None)
    
    if not vaga:
        return
    
    # Liberar vaga se NÃO estava recusada
    if status in ['pendente', 'aprovado', 'em_analise']:
        vaga.vagas_disponiveis += 1
        
        if vaga.status == 'pausada' and vaga.vagas_disponiveis > 0:
            vaga.status = 'aberta'
        
        vaga.save()
        print(f"🗑️ Candidatura {status} EXCLUÍDA: Vaga '{vaga.titulo}' liberada - {vaga.vagas_disponiveis} vaga(s) disponível(is)")
    else:
        print(f"🗑️ Candidatura RECUSADA excluída: Vaga '{vaga.titulo}' mantém {vaga.vagas_disponiveis} vaga(s)")


@receiver(post_save, sender=CandidaturaVoluntariado)
def enviar_emails_notificacao(sender, instance, created, **kwargs):
    """
    Envia emails quando status muda
    """
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

Encorajamos você a se candidatar para outras oportunidades disponíveis.

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
                print(f"❌ Erro ao enviar email: {e}")