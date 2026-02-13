from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django_fsm import FSMField, transition
from datetime import datetime


class TipoAnalisis(models.Model):
    """Model for analysis types (Many-to-Many with Muestra)"""
    CATEGORIA_CHOICES = [
        ('FISICO', 'Físicos'),
        ('QUIMICO', 'Químicos'),
        ('MICROBIOLOGICO', 'Microbiológicos'),
    ]
    
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Tipo de Análisis"
        verbose_name_plural = "Tipos de Análisis"
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nombre}"


class Solicitud(models.Model):
    """Main model for Analysis Order (OA)"""
    AREA_CHOICES = [
        ('AGRONOMIA', 'Agronomía'),
        ('PRODUCCION', 'Producción'),
        ('ASEGURAMIENTO_CALIDAD', 'Aseguramiento de Calidad'),
        ('COMERCIAL', 'Comercial'),
    ]
    
    # Auto-generated code: QC0001-26
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    
    # Bloque 1 - Datos del Solicitante
    solicitante_nombre = models.CharField(max_length=200, verbose_name="Nombre completo")
    solicitante_area = models.CharField(max_length=30, choices=AREA_CHOICES, verbose_name="Área/Departamento")
    solicitante_cargo = models.CharField(max_length=100, verbose_name="Cargo")
    solicitante_email = models.EmailField(verbose_name="Correo electrónico")
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")
    
    # State machine
    ESTADO_CHOICES = [
        ('RADICADA', 'Radicada'),
        ('PENDIENTE_RECEPCION', 'Pendiente de Recepción'),
        ('RECIBIDA', 'Recibida'),
        ('EN_ANALISIS', 'En Análisis'),
        ('COMPLETADA', 'Completada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    estado = FSMField(default='RADICADA', choices=ESTADO_CHOICES, protected=True)
    
    # Metadata
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='solicitudes_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Solicitud de Análisis"
        verbose_name_plural = "Solicitudes de Análisis"
        ordering = ['-fecha_solicitud']
        permissions = [
            ('can_receive_samples', 'Puede recibir muestras'),
            ('can_analyze_samples', 'Puede analizar muestras'),
            ('can_complete_orders', 'Puede completar órdenes'),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.solicitante_nombre}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generate_codigo()
        super().save(*args, **kwargs)
    
    @staticmethod
    def _generate_codigo():
        """Generate unique code in format QC0001-26"""
        with transaction.atomic():
            current_year = datetime.now().year
            year_suffix = str(current_year)[-2:]
            
            # Get last code for current year
            last_solicitud = Solicitud.objects.filter(
                codigo__endswith=f'-{year_suffix}'
            ).order_by('-codigo').first()
            
            if last_solicitud:
                # Extract number from last code
                last_number = int(last_solicitud.codigo.split('-')[0][2:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            return f"QC{new_number:04d}-{year_suffix}"
    
    # State machine transitions
    @transition(field=estado, source='RADICADA', target='PENDIENTE_RECEPCION')
    def enviar_a_recepcion(self):
        """Transition from RADICADA to PENDIENTE_RECEPCION"""
        pass
    
    @transition(field=estado, source='PENDIENTE_RECEPCION', target='RECIBIDA')
    def recibir_conforme(self):
        """Transition from PENDIENTE_RECEPCION to RECIBIDA when samples are received properly"""
        pass
    
    @transition(field=estado, source='PENDIENTE_RECEPCION', target='RECHAZADA')
    def rechazar_recepcion(self):
        """Transition from PENDIENTE_RECEPCION to RECHAZADA when samples are not conforming"""
        pass
    
    @transition(field=estado, source='RECIBIDA', target='EN_ANALISIS')
    def iniciar_analisis(self):
        """Transition from RECIBIDA to EN_ANALISIS"""
        pass
    
    @transition(field=estado, source='EN_ANALISIS', target='COMPLETADA')
    def completar_analisis(self):
        """Transition from EN_ANALISIS to COMPLETADA"""
        pass


class Muestra(models.Model):
    """Model for samples (multiple per Solicitud)"""
    TIPO_MUESTRA_CHOICES = [
        ('FLOR', 'Flor'),
        ('EXTRACTO_CRUDO', 'Extracto crudo'),
        ('AISLADO', 'Aislado'),
        ('DESTILADO', 'Destilado'),
    ]
    
    CONDICIONES_ALMACENAMIENTO_CHOICES = [
        ('AMBIENTE', 'Ambiente'),
        ('REFRIGERACION', 'Refrigeración'),
        ('CONGELACION', 'Congelación'),
    ]
    
    TIPO_ANALISIS_CHOICES = [
        ('EN_PROCESO', 'En proceso'),
        ('ESTABILIDAD', 'Estabilidad'),
        ('INVESTIGACION', 'Investigación'),
        ('LIBERACION_LOTE', 'Liberación de lote'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('NORMAL', 'Normal'),
        ('URGENTE', 'Urgente'),
        ('CRITICO', 'Crítico'),
    ]
    
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='muestras')
    
    # Bloque 2 - Trazabilidad
    nombre_producto = models.CharField(max_length=200, verbose_name="Nombre del producto")
    numero_lote = models.CharField(max_length=100, verbose_name="Número de lote")
    fecha_fabricacion = models.DateField(verbose_name="Fecha de fabricación")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de vencimiento/retest")
    numero_muestras_enviadas = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Número de muestras enviadas"
    )
    cantidad_por_muestra = models.CharField(max_length=100, verbose_name="Cantidad por muestra")
    tipo_muestra = models.CharField(max_length=20, choices=TIPO_MUESTRA_CHOICES, verbose_name="Tipo de muestra")
    condiciones_almacenamiento = models.CharField(
        max_length=20,
        choices=CONDICIONES_ALMACENAMIENTO_CHOICES,
        verbose_name="Condiciones de almacenamiento"
    )
    fecha_entrega_laboratorio = models.DateField(verbose_name="Fecha de entrega al laboratorio")
    
    # Bloque 3 - Análisis (ManyToMany)
    analisis_solicitados = models.ManyToManyField(TipoAnalisis, verbose_name="Análisis solicitados")
    
    # Bloque 4 - Información Regulatoria
    tipo_analisis = models.CharField(max_length=20, choices=TIPO_ANALISIS_CHOICES, verbose_name="Tipo de análisis")
    protocolo_analitico = models.CharField(max_length=200, verbose_name="Protocolo analítico", blank=True)
    requiere_coa = models.BooleanField(default=False, verbose_name="Requiere CoA")
    especificaciones = models.TextField(verbose_name="Especificaciones", blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='NORMAL', verbose_name="Prioridad")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True)
    debe_devolverse = models.BooleanField(default=False, verbose_name="¿Debe devolverse?")
    
    class Meta:
        verbose_name = "Muestra"
        verbose_name_plural = "Muestras"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.solicitud.codigo} - {self.nombre_producto}"


class RecepcionMuestra(models.Model):
    """Model for physical sample reception"""
    CONDICION_CHOICES = [
        ('CONFORME', 'Conforme'),
        ('NO_CONFORME', 'No Conforme'),
    ]
    
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name='recepcion')
    fecha_recepcion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora de recepción")
    recibido_por = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Recibido por")
    condicion = models.CharField(max_length=15, choices=CONDICION_CHOICES, verbose_name="Condición de llegada")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Recepción de Muestra"
        verbose_name_plural = "Recepciones de Muestras"
        ordering = ['-fecha_recepcion']
    
    def __str__(self):
        return f"Recepción {self.solicitud.codigo}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update solicitud state based on condition
        if is_new:
            if self.condicion == 'CONFORME':
                self.solicitud.recibir_conforme()
            else:
                self.solicitud.rechazar_recepcion()
            self.solicitud.save()


class HistorialCambios(models.Model):
    """Model for tracking changes (audit trail)"""
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    campo_modificado = models.CharField(max_length=100)
    valor_anterior = models.TextField()
    valor_nuevo = models.TextField()
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Historial de Cambios"
        verbose_name_plural = "Historial de Cambios"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.solicitud.codigo} - {self.campo_modificado} - {self.fecha}"

