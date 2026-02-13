from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Solicitud, Muestra, TipoAnalisis, RecepcionMuestra, HistorialCambios


class MuestraInline(TabularInline):
    """Inline admin for Muestra"""
    model = Muestra
    extra = 1
    fields = [
        'nombre_producto', 'numero_lote', 'tipo_muestra', 'prioridad',
        'fecha_fabricacion', 'fecha_vencimiento', 'tipo_analisis'
    ]
    autocomplete_fields = ['analisis_solicitados']


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
    list_display = [
        'codigo', 'solicitante_nombre', 'solicitante_area', 
        'estado_badge', 'fecha_solicitud', 'get_num_muestras'
    ]
    list_filter = ['estado', 'solicitante_area', 'fecha_solicitud']
    search_fields = ['codigo', 'solicitante_nombre', 'solicitante_email']
    readonly_fields = ['codigo', 'fecha_solicitud', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [MuestraInline]
    
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
        if not change:  # New object
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


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

