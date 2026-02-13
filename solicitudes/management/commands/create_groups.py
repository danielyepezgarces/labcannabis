from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from solicitudes.models import Solicitud, Muestra, RecepcionMuestra


class Command(BaseCommand):
    help = 'Create user groups and assign permissions for RBAC'

    def handle(self, *args, **options):
        # Define groups and their permissions
        groups_permissions = {
            'Solicitante': [
                'add_solicitud',
                'view_solicitud',
                'add_muestra',
                'view_muestra',
            ],
            'Recepcion': [
                'view_solicitud',
                'view_muestra',
                'add_recepcionmuestra',
                'change_recepcionmuestra',
                'view_recepcionmuestra',
                'can_receive_samples',
            ],
            'Analista': [
                'view_solicitud',
                'change_solicitud',
                'view_muestra',
                'change_muestra',
                'can_analyze_samples',
                'can_complete_orders',
            ],
            'Administrador': [
                # Full permissions on all models
                'add_solicitud',
                'change_solicitud',
                'delete_solicitud',
                'view_solicitud',
                'add_muestra',
                'change_muestra',
                'delete_muestra',
                'view_muestra',
                'add_recepcionmuestra',
                'change_recepcionmuestra',
                'delete_recepcionmuestra',
                'view_recepcionmuestra',
                'can_receive_samples',
                'can_analyze_samples',
                'can_complete_orders',
            ],
        }
        
        for group_name, permission_codenames in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(f'Group already exists: {group_name}')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Assign permissions
            for codename in permission_codenames:
                try:
                    # Try to find permission
                    permission = Permission.objects.get(codename=codename)
                    group.permissions.add(permission)
                    self.stdout.write(f'  + Added permission: {codename}')
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ! Permission not found: {codename}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully configured user groups and permissions'))
