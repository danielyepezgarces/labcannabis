from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django import forms
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display
from .models import Solicitud, Muestra, TipoAnalisis, RecepcionMuestra, HistorialCambios
from .pdf import download_pdf_solicitud


class SolicitudAdminForm(forms.ModelForm):
    """Custom form for Solicitud to allow admin to modify estado"""
    
    class Meta:
        model = Solicitud
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make estado field non-required in the form
        # Actual permission-based restrictions are enforced in the admin class
        if 'estado' in self.fields:
            self.fields['estado'].required = False


class MuestraInlineForm(forms.ModelForm):
    """Custom form for Muestra inline to show analysis types properly"""
    
    class Meta:
        model = Muestra
        fields = '__all__'
        widgets = {
            'analisis_solicitados': forms.CheckboxSelectMultiple(
                attrs={'class': 'checkbox-group'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the queryset is set and ordered by category
        if 'analisis_solicitados' in self.fields:
            self.fields['analisis_solicitados'].queryset = TipoAnalisis.objects.all().order_by('categoria', 'nombre')
            self.fields['analisis_solicitados'].help_text = 'Seleccione uno o más análisis requeridos'
            self.fields['analisis_solicitados'].label = 'Análisis Solicitados'


class MuestraInline(StackedInline):
    """Inline admin for Muestra"""
    model = Muestra
    form = MuestraInlineForm
    extra = 1
    fields = [
        ('nombre_producto', 'numero_lote', 'tipo_muestra'),
        ('fecha_fabricacion', 'fecha_vencimiento'),
        ('numero_muestras_enviadas', 'cantidad_por_muestra'),
        ('condiciones_almacenamiento', 'fecha_entrega_laboratorio'),
        'analisis_solicitados',
        ('tipo_analisis', 'prioridad', 'requiere_coa'),
        ('protocolo_analitico', 'especificaciones'),
        ('observaciones', 'debe_devolverse'),
    ]


@admin.register(TipoAnalisis)
class TipoAnalisisAdmin(ModelAdmin):
    """Admin for TipoAnalisis"""
    list_display = ['nombre', 'categoria', 'descripcion']
    list_filter = ['categoria']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'nombre']


@admin.register(Solicitud)
class SolicitudAdmin(ModelAdmin):
    """Admin for Solicitud with inline Muestra"""
    form = SolicitudAdminForm
    list_display = [
        'codigo', 'solicitante_nombre', 'solicitante_area', 
        'estado_badge', 'fecha_solicitud', 'get_num_muestras'
    ]
    list_filter = ['estado', 'solicitante_area', 'fecha_solicitud']
    search_fields = ['codigo', 'solicitante_nombre', 'solicitante_email']
    readonly_fields = ['codigo', 'fecha_solicitud', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [MuestraInline]
    actions = ['enviar_a_recepcion_action', 'iniciar_analisis_action', 'completar_analisis_action']
    
    fieldsets = (
        ('Información de la Solicitud', {
            'fields': ('codigo', 'estado', 'fecha_solicitud')
        }),
        ('Datos del Solicitante', {
            'fields': (
                'solicitante_nombre', 'solicitante_area', 
                'solicitante_cargo', 'solicitante_email', 'creado_por'
            )
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make estado field readonly for non-admin users.
        Administrators can modify estado directly.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        
        # If user is not a superuser and not in Administrador group, make estado readonly
        if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
            if 'estado' not in readonly:
                readonly.append('estado')
        
        return readonly
    
    def get_fields(self, request, obj=None):
        """
        Hide estado field from Solicitante users when creating new requests.
        """
        fields = super().get_fields(request, obj)
        
        # If creating a new object (obj is None) and user is a Solicitante
        if obj is None and not request.user.is_superuser:
            if request.user.groups.filter(name='Solicitante').exists():
                # Remove estado from visible fields for Solicitante
                fields = [f for f in fields if f != 'estado']
        
        return fields
    
    @display(description="Estado", label=True)
    def estado_badge(self, obj):
        colors = {
            'RADICADA': 'info',
            'PENDIENTE_RECEPCION': 'warning',
            'RECIBIDA': 'success',
            'EN_ANALISIS': 'primary',
            'COMPLETADA': 'success',
            'RECHAZADA': 'danger',
        }
        return {
            'value': obj.get_estado_display(),
            'color': colors.get(obj.estado, 'secondary')
        }
    
    @display(description="Muestras")
    def get_num_muestras(self, obj):
        return obj.muestras.count()
    
    def save_model(self, request, obj, form, change):
        """
        Save model with special handling for estado field.
        Allow admins to directly modify estado field bypassing FSM protection.
        """
        if not change:  # New object
            obj.creado_por = request.user
        
        # Check if admin is trying to change estado directly
        if change and 'estado' in form.changed_data:
            # Allow admins and superusers to bypass FSM protection
            if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
                # Use the special admin method to set estado
                new_estado = form.cleaned_data['estado']
                obj.set_estado_admin(new_estado)
                # Save with update_fields to exclude estado from normal save process
                obj.save(update_fields=[f for f in form.changed_data if f != 'estado'])
                return
        
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:solicitud_id>/pdf/',
                self.admin_site.admin_view(download_pdf_solicitud),
                name='solicitud_pdf',
            ),
        ]
        return custom_urls + urls
    
    # Actions for state transitions
    @admin.action(description='Enviar a recepción')
    def enviar_a_recepcion_action(self, request, queryset):
        for solicitud in queryset:
            try:
                solicitud.enviar_a_recepcion()
                solicitud.save()
                messages.success(request, f'{solicitud.codigo} enviada a recepción')
            except Exception as e:
                messages.error(request, f'Error en {solicitud.codigo}: {str(e)}')
    
    @admin.action(description='Iniciar análisis')
    def iniciar_analisis_action(self, request, queryset):
        for solicitud in queryset:
            try:
                solicitud.iniciar_analisis()
                solicitud.save()
                messages.success(request, f'{solicitud.codigo} en análisis')
            except Exception as e:
                messages.error(request, f'Error en {solicitud.codigo}: {str(e)}')
    
    @admin.action(description='Completar análisis')
    def completar_analisis_action(self, request, queryset):
        for solicitud in queryset:
            try:
                solicitud.completar_analisis()
                solicitud.save()
                messages.success(request, f'{solicitud.codigo} completada')
            except Exception as e:
                messages.error(request, f'Error en {solicitud.codigo}: {str(e)}')


@admin.register(Muestra)
class MuestraAdmin(ModelAdmin):
    """Admin for Muestra"""
    list_display = [
        'solicitud', 'nombre_producto', 'numero_lote', 
        'tipo_muestra', 'prioridad', 'tipo_analisis'
    ]
    list_filter = ['tipo_muestra', 'prioridad', 'tipo_analisis', 'condiciones_almacenamiento']
    search_fields = ['nombre_producto', 'numero_lote', 'solicitud__codigo']
    filter_horizontal = ['analisis_solicitados']
    
    fieldsets = (
        ('Solicitud', {
            'fields': ('solicitud',)
        }),
        ('Trazabilidad', {
            'fields': (
                'nombre_producto', 'numero_lote', 
                'fecha_fabricacion', 'fecha_vencimiento',
                'numero_muestras_enviadas', 'cantidad_por_muestra',
                'tipo_muestra', 'condiciones_almacenamiento',
                'fecha_entrega_laboratorio'
            )
        }),
        ('Análisis', {
            'fields': ('analisis_solicitados',)
        }),
        ('Información Regulatoria', {
            'fields': (
                'tipo_analisis', 'protocolo_analitico', 
                'requiere_coa', 'especificaciones',
                'prioridad', 'observaciones', 'debe_devolverse'
            )
        }),
    )


@admin.register(RecepcionMuestra)
class RecepcionMuestraAdmin(ModelAdmin):
    """Admin for RecepcionMuestra"""
    list_display = ['solicitud', 'fecha_recepcion', 'recibido_por', 'condicion']
    list_filter = ['condicion', 'fecha_recepcion']
    search_fields = ['solicitud__codigo', 'recibido_por__username']
    readonly_fields = ['fecha_recepcion']
    
    fieldsets = (
        ('Información de Recepción', {
            'fields': ('solicitud', 'fecha_recepcion', 'recibido_por')
        }),
        ('Condición', {
            'fields': ('condicion', 'observaciones')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.recibido_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(HistorialCambios)
class HistorialCambiosAdmin(ModelAdmin):
    """Admin for HistorialCambios"""
    list_display = ['solicitud', 'usuario', 'fecha', 'campo_modificado']
    list_filter = ['fecha', 'campo_modificado']
    search_fields = ['solicitud__codigo', 'usuario__username', 'descripcion']
    readonly_fields = ['solicitud', 'usuario', 'fecha', 'campo_modificado', 'valor_anterior', 'valor_nuevo']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Unregister the default User admin and register with Unfold
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Custom User admin with Unfold styling and Solicitante default role"""
    
    # Override add_fieldsets to remove usable_password field
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Save user and assign Solicitante group by default for new users"""
        super().save_model(request, obj, form, change)
        
        # If this is a new user (not editing existing), add to Solicitante group
        if not change:
            try:
                solicitante_group = Group.objects.get(name='Solicitante')
                obj.groups.add(solicitante_group)
            except Group.DoesNotExist:
                # Group doesn't exist yet, skip
                pass

