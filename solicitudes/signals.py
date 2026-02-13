from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Solicitud, RecepcionMuestra


@receiver(post_save, sender=Solicitud)
def notificar_cambio_estado(sender, instance, created, **kwargs):
    """Send email notifications when solicitud state changes"""
    
    if created:
        # 1. Nueva solicitud radicada - notify laboratory
        subject = f'Nueva Solicitud de Análisis - {instance.codigo}'
        message = f"""
        Se ha creado una nueva solicitud de análisis:
        
        Código: {instance.codigo}
        Solicitante: {instance.solicitante_nombre}
        Área: {instance.get_solicitante_area_display()}
        Fecha: {instance.fecha_solicitud.strftime('%Y-%m-%d %H:%M')}
        Estado: {instance.get_estado_display()}
        
        Número de muestras: {instance.muestras.count()}
        """
        
        # Send to laboratory email (placeholder)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['laboratorio@labcannabis.com'],  # Laboratory email
            fail_silently=True,
        )
    
    else:
        # Check if state changed
        if instance.tracker.has_changed('estado'):
            previous_state = instance.tracker.previous('estado')
            current_state = instance.estado
            
            # 2. Estado cambia a EN_ANALISIS - notify requester
            if current_state == 'EN_ANALISIS':
                subject = f'Análisis Iniciado - {instance.codigo}'
                message = f"""
                Estimado/a {instance.solicitante_nombre},
                
                Su solicitud de análisis {instance.codigo} ha pasado al estado "En Análisis".
                
                El laboratorio está trabajando en el análisis de sus muestras.
                
                Saludos,
                Laboratorio de Control de Calidad
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.solicitante_email],
                    fail_silently=True,
                )
            
            # 3. Solicitud completada - notify requester
            elif current_state == 'COMPLETADA':
                subject = f'Análisis Completado - {instance.codigo}'
                message = f"""
                Estimado/a {instance.solicitante_nombre},
                
                Su solicitud de análisis {instance.codigo} ha sido completada.
                
                Los resultados están disponibles para su revisión.
                
                Saludos,
                Laboratorio de Control de Calidad
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.solicitante_email],
                    fail_silently=True,
                )
            
            # 4. Solicitud rechazada - notify requester
            elif current_state == 'RECHAZADA':
                recepcion = getattr(instance, 'recepcion', None)
                motivo = recepcion.observaciones if recepcion else 'No especificado'
                
                subject = f'Solicitud Rechazada - {instance.codigo}'
                message = f"""
                Estimado/a {instance.solicitante_nombre},
                
                Su solicitud de análisis {instance.codigo} ha sido rechazada.
                
                Motivo: {motivo}
                
                Por favor, contacte con el laboratorio para más información.
                
                Saludos,
                Laboratorio de Control de Calidad
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.solicitante_email],
                    fail_silently=True,
                )


# Add tracker to model for change detection
from django.db.models import Model


def add_tracker_to_model():
    """Add simple tracker for estado field"""
    original_init = Solicitud.__init__
    
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.tracker = type('obj', (object,), {
            '_original_estado': self.estado,
            'has_changed': lambda field: getattr(self, field) != self.tracker._original_estado if field == 'estado' else False,
            'previous': lambda field: self.tracker._original_estado if field == 'estado' else None
        })()
    
    Solicitud.__init__ = __init__


add_tracker_to_model()
