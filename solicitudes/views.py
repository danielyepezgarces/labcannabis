from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Solicitud, Muestra


def dashboard_callback(request, context):
    """Dashboard callback for Django Unfold"""
    
    # Calculate metrics
    total_ordenes = Solicitud.objects.count()
    total_muestras = Muestra.objects.count()
    
    # Orders by state
    ordenes_por_estado = Solicitud.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Orders by priority
    ordenes_por_prioridad = Muestra.objects.values('prioridad').annotate(
        count=Count('id')
    ).order_by('prioridad')
    
    # Orders by area
    ordenes_por_area = Solicitud.objects.values('solicitante_area').annotate(
        count=Count('id')
    ).order_by('solicitante_area')
    
    # Recent orders (last 30 days)
    fecha_inicio = timezone.now() - timedelta(days=30)
    ordenes_recientes = Solicitud.objects.filter(
        fecha_solicitud__gte=fecha_inicio
    ).count()
    
    # Add custom metrics to context
    context.update({
        'total_ordenes': total_ordenes,
        'total_muestras': total_muestras,
        'ordenes_por_estado': list(ordenes_por_estado),
        'ordenes_por_prioridad': list(ordenes_por_prioridad),
        'ordenes_por_area': list(ordenes_por_area),
        'ordenes_recientes': ordenes_recientes,
    })
    
    return context

