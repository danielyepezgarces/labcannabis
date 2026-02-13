from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from solicitudes.models import Solicitud, Muestra, TipoAnalisis
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create sample data for demonstration'

    def handle(self, *args, **options):
        # Get or create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@labcannabis.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Get analysis types
        humedad = TipoAnalisis.objects.get(nombre='% Humedad')
        potencia = TipoAnalisis.objects.get(nombre='Potencia cannabinoides')
        terpenos = TipoAnalisis.objects.get(nombre='Terpenos')
        
        # Create sample solicitudes
        solicitud1 = Solicitud.objects.create(
            solicitante_nombre='María González',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Jefe de Producción',
            solicitante_email='maria.gonzalez@example.com',
            creado_por=admin
        )
        
        # Add samples to solicitud1
        muestra1 = Muestra.objects.create(
            solicitud=solicitud1,
            nombre_producto='Cannabis Flower Premium',
            numero_lote='CF-2026-001',
            fecha_fabricacion=date.today() - timedelta(days=7),
            fecha_vencimiento=date.today() + timedelta(days=358),
            numero_muestras_enviadas=3,
            cantidad_por_muestra='50g',
            tipo_muestra='FLOR',
            condiciones_almacenamiento='AMBIENTE',
            fecha_entrega_laboratorio=date.today(),
            tipo_analisis='LIBERACION_LOTE',
            prioridad='URGENTE',
            requiere_coa=True,
            especificaciones='Según especificación interna EI-001',
            observaciones='Primera cosecha del año'
        )
        muestra1.analisis_solicitados.add(humedad, potencia, terpenos)
        
        solicitud2 = Solicitud.objects.create(
            solicitante_nombre='Carlos Rodríguez',
            solicitante_area='ASEGURAMIENTO_CALIDAD',
            solicitante_cargo='Analista de Calidad',
            solicitante_email='carlos.rodriguez@example.com',
            creado_por=admin
        )
        
        muestra2 = Muestra.objects.create(
            solicitud=solicitud2,
            nombre_producto='Extracto CBD Aislado',
            numero_lote='EXT-2026-005',
            fecha_fabricacion=date.today() - timedelta(days=3),
            fecha_vencimiento=date.today() + timedelta(days=362),
            numero_muestras_enviadas=2,
            cantidad_por_muestra='10g',
            tipo_muestra='AISLADO',
            condiciones_almacenamiento='REFRIGERACION',
            fecha_entrega_laboratorio=date.today(),
            tipo_analisis='ESTABILIDAD',
            prioridad='NORMAL',
            requiere_coa=False,
            especificaciones='Protocolo de estabilidad EST-002',
            observaciones='Estudio de estabilidad acelerada'
        )
        muestra2.analisis_solicitados.add(potencia)
        
        solicitud3 = Solicitud.objects.create(
            solicitante_nombre='Ana Martínez',
            solicitante_area='AGRONOMIA',
            solicitante_cargo='Ingeniera Agrónoma',
            solicitante_email='ana.martinez@example.com',
            creado_por=admin
        )
        
        muestra3 = Muestra.objects.create(
            solicitud=solicitud3,
            nombre_producto='Cannabis Sativa L. - Cultivo A',
            numero_lote='CS-2026-012',
            fecha_fabricacion=date.today() - timedelta(days=1),
            fecha_vencimiento=date.today() + timedelta(days=364),
            numero_muestras_enviadas=5,
            cantidad_por_muestra='100g',
            tipo_muestra='FLOR',
            condiciones_almacenamiento='AMBIENTE',
            fecha_entrega_laboratorio=date.today(),
            tipo_analisis='EN_PROCESO',
            prioridad='CRITICO',
            requiere_coa=False,
            especificaciones='Control de proceso - Floración',
            observaciones='Verificar niveles antes de cosecha'
        )
        muestra3.analisis_solicitados.add(humedad, potencia)
        
        # Progress some solicitudes through states
        solicitud1.enviar_a_recepcion()
        solicitud1.save()
        
        solicitud2.enviar_a_recepcion()
        solicitud2.recibir_conforme()
        solicitud2.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created 3 sample solicitudes:'))
        self.stdout.write(f'  - {solicitud1.codigo} (Estado: {solicitud1.get_estado_display()})')
        self.stdout.write(f'  - {solicitud2.codigo} (Estado: {solicitud2.get_estado_display()})')
        self.stdout.write(f'  - {solicitud3.codigo} (Estado: {solicitud3.get_estado_display()})')
