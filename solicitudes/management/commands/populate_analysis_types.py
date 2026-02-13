from django.core.management.base import BaseCommand
from solicitudes.models import TipoAnalisis


class Command(BaseCommand):
    help = 'Populate initial analysis types (Tipos de Análisis)'

    def handle(self, *args, **options):
        # Physical analysis types
        fisicos = [
            'Apariencia',
            '% Humedad',
            'Actividad de agua',
            'Materia extraña',
            'Cenizas totales',
            'Cenizas insolubles en ácido',
        ]
        
        # Chemical analysis types
        quimicos = [
            'Potencia cannabinoides',
            'Terpenos',
            'Pesticidas',
            'Metales pesados',
            'Impurezas elementales',
            'Solventes residuales',
        ]
        
        # Microbiological analysis types
        microbiologicos = [
            'Microbiología general',
            'Micotoxinas',
        ]
        
        created_count = 0
        
        # Create physical types
        for nombre in fisicos:
            _, created = TipoAnalisis.objects.get_or_create(
                nombre=nombre,
                categoria='FISICO',
                defaults={'descripcion': f'Análisis físico: {nombre}'}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {nombre}'))
        
        # Create chemical types
        for nombre in quimicos:
            _, created = TipoAnalisis.objects.get_or_create(
                nombre=nombre,
                categoria='QUIMICO',
                defaults={'descripcion': f'Análisis químico: {nombre}'}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {nombre}'))
        
        # Create microbiological types
        for nombre in microbiologicos:
            _, created = TipoAnalisis.objects.get_or_create(
                nombre=nombre,
                categoria='MICROBIOLOGICO',
                defaults={'descripcion': f'Análisis microbiológico: {nombre}'}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {nombre}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully created {created_count} analysis types'
        ))
