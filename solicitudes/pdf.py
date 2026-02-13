from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.http import HttpResponse
from .models import Solicitud, Muestra


def generar_pdf_solicitud(solicitud_id):
    """Generate PDF for a solicitud (analysis order)"""
    try:
        solicitud = Solicitud.objects.prefetch_related(
            'muestras__analisis_solicitados'
        ).get(id=solicitud_id)
    except Solicitud.DoesNotExist:
        return None
    
    # Create buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    # Title
    elements.append(Paragraph("ORDEN DE ANÁLISIS", title_style))
    elements.append(Paragraph(f"Código: {solicitud.codigo}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Estado badge
    estado_text = f"<b>Estado:</b> {solicitud.get_estado_display()}"
    elements.append(Paragraph(estado_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Bloque 1 - Datos del Solicitante
    elements.append(Paragraph("1. DATOS DEL SOLICITANTE", heading_style))
    
    solicitante_data = [
        ['Nombre completo:', solicitud.solicitante_nombre],
        ['Área/Departamento:', solicitud.get_solicitante_area_display()],
        ['Cargo:', solicitud.solicitante_cargo],
        ['Correo electrónico:', solicitud.solicitante_email],
        ['Fecha de solicitud:', solicitud.fecha_solicitud.strftime('%Y-%m-%d %H:%M')],
    ]
    
    solicitante_table = Table(solicitante_data, colWidths=[2*inch, 4*inch])
    solicitante_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(solicitante_table)
    elements.append(Spacer(1, 20))
    
    # Muestras
    elements.append(Paragraph("2. MUESTRAS", heading_style))
    
    for idx, muestra in enumerate(solicitud.muestras.all(), 1):
        elements.append(Paragraph(f"<b>Muestra {idx}</b>", styles['Heading3']))
        elements.append(Spacer(1, 8))
        
        # Trazabilidad
        muestra_data = [
            ['Producto:', muestra.nombre_producto],
            ['Número de lote:', muestra.numero_lote],
            ['Tipo de muestra:', muestra.get_tipo_muestra_display()],
            ['Fecha fabricación:', muestra.fecha_fabricacion.strftime('%Y-%m-%d')],
            ['Fecha vencimiento:', muestra.fecha_vencimiento.strftime('%Y-%m-%d')],
            ['Cantidad:', muestra.cantidad_por_muestra],
            ['Almacenamiento:', muestra.get_condiciones_almacenamiento_display()],
            ['Fecha entrega lab:', muestra.fecha_entrega_laboratorio.strftime('%Y-%m-%d')],
        ]
        
        muestra_table = Table(muestra_data, colWidths=[2*inch, 4*inch])
        muestra_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(muestra_table)
        elements.append(Spacer(1, 10))
        
        # Análisis solicitados
        analisis_list = [a.nombre for a in muestra.analisis_solicitados.all()]
        if analisis_list:
            elements.append(Paragraph("<b>Análisis solicitados:</b>", styles['Normal']))
            for analisis in analisis_list:
                elements.append(Paragraph(f"• {analisis}", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Información regulatoria
        reg_data = [
            ['Tipo de análisis:', muestra.get_tipo_analisis_display()],
            ['Prioridad:', muestra.get_prioridad_display()],
            ['Requiere CoA:', 'Sí' if muestra.requiere_coa else 'No'],
            ['Debe devolverse:', 'Sí' if muestra.debe_devolverse else 'No'],
        ]
        
        reg_table = Table(reg_data, colWidths=[2*inch, 4*inch])
        reg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(reg_table)
        elements.append(Spacer(1, 15))
    
    # Recepción
    if hasattr(solicitud, 'recepcion'):
        elements.append(Paragraph("3. RECEPCIÓN", heading_style))
        recepcion = solicitud.recepcion
        
        recepcion_data = [
            ['Fecha recepción:', recepcion.fecha_recepcion.strftime('%Y-%m-%d %H:%M')],
            ['Recibido por:', recepcion.recibido_por.get_full_name() or recepcion.recibido_por.username],
            ['Condición:', recepcion.get_condicion_display()],
            ['Observaciones:', recepcion.observaciones or 'N/A'],
        ]
        
        recepcion_table = Table(recepcion_data, colWidths=[2*inch, 4*inch])
        recepcion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d5f4e6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(recepcion_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf


def download_pdf_solicitud(request, solicitud_id):
    """View to download PDF"""
    pdf = generar_pdf_solicitud(solicitud_id)
    
    if pdf is None:
        from django.http import Http404
        raise Http404("Solicitud no encontrada")
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="solicitud_{solicitud_id}.pdf"'
    response.write(pdf)
    
    return response
