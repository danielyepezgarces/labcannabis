# Lab Cannabis - Sistema de Gestión de Órdenes de Análisis

Sistema web profesional en Django 6+ para gestión de Órdenes de Análisis (OA) en laboratorio de control de calidad (modelo farmacéutico / GxP).

## 🚀 Características

- ✅ Creación de múltiples muestras en una sola orden
- ✅ Máquina de estados controlada con django-fsm
- ✅ Recepción física de muestras
- ✅ Notificaciones automáticas por correo
- ✅ Generación de PDF profesionales
- ✅ Interfaz administrativa con Django Unfold
- ✅ Control de roles (RBAC)
- ✅ Trazabilidad completa y auditoría
- ✅ Código automático de orden (formato QC0001-26)

## 📋 Requisitos

- Python 3.12+
- Django 6.0+
- PostgreSQL (o SQLite para desarrollo)

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/danielyepezgarces/labcannabis.git
cd labcannabis
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar base de datos (opcional, por defecto usa SQLite):
Editar `labcannabis/settings.py` para configurar PostgreSQL si es necesario.

4. Ejecutar migraciones:
```bash
python manage.py migrate
```

5. Poblar datos iniciales:
```bash
python manage.py populate_analysis_types
python manage.py create_groups
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Iniciar servidor de desarrollo:
```bash
python manage.py runserver
```

8. Acceder a la interfaz administrativa:
```
http://localhost:8000/admin/
```

## 📊 Estructura de Datos

### Bloque 1 - Datos del Solicitante
- Nombre completo
- Área/Departamento (Agronomía, Producción, Aseguramiento de Calidad, Comercial)
- Cargo
- Correo electrónico
- Fecha de solicitud (automática)
- Número de solicitud (automático: QC0001-26)

### Bloque 2 - Trazabilidad (por muestra)
- Nombre del producto
- Número de lote
- Fecha fabricación/vencimiento
- Tipo de muestra (Flor, Extracto crudo, Aislado, Destilado)
- Condiciones de almacenamiento
- Fecha entrega laboratorio

### Bloque 3 - Análisis (por muestra)
Categorías disponibles:
- **Físicos**: Apariencia, % Humedad, Actividad de agua, Materia extraña, Cenizas
- **Químicos**: Potencia cannabinoides, Terpenos, Pesticidas, Metales pesados, Solventes residuales
- **Microbiológicos**: Microbiología general, Micotoxinas

### Bloque 4 - Información Regulatoria (por muestra)
- Tipo de análisis (En proceso, Estabilidad, Investigación, Liberación de lote)
- Protocolo analítico
- Requiere CoA (Sí/No)
- Prioridad (Normal, Urgente, Crítico)
- Observaciones

## 🔄 Máquina de Estados

Estados disponibles:
1. **RADICADA** → Solicitud creada
2. **PENDIENTE DE RECEPCIÓN** → Enviada al laboratorio
3. **RECIBIDA** → Muestras recibidas conforme
4. **EN ANÁLISIS** → Análisis en proceso
5. **COMPLETADA** → Análisis finalizado
6. **RECHAZADA** → Muestras no conformes

Flujo permitido:
```
RADICADA → PENDIENTE DE RECEPCIÓN → RECIBIDA → EN ANÁLISIS → COMPLETADA
                                  ↓
                              RECHAZADA (si no conforme)
```

## 👥 Roles y Permisos

### Solicitante
- Crear solicitudes de análisis
- Ver sus propias solicitudes

### Recepción Laboratorio
- Ver solicitudes
- Recibir muestras
- Marcar conformidad/no conformidad

### Analista
- Ver y modificar solicitudes
- Iniciar análisis
- Completar análisis

### Administrador
- Acceso completo a todas las funcionalidades

## 📧 Notificaciones

El sistema envía notificaciones automáticas por correo en los siguientes eventos:

1. **Nueva solicitud radicada** → Destinatario: Laboratorio
2. **Cambio a estado EN ANÁLISIS** → Destinatario: Solicitante
3. **Solicitud completada** → Destinatario: Solicitante
4. **Solicitud rechazada** → Destinatario: Solicitante (con motivo)

## 📄 Generación de PDF

Cada orden de análisis puede exportarse a PDF con:
- Código de orden
- Datos del solicitante
- Información de todas las muestras
- Análisis solicitados
- Estado de recepción
- Resultados (cuando estén disponibles)

Para descargar el PDF de una solicitud:
```
/admin/solicitudes/solicitud/<id>/pdf/
```

## 🛠️ Comandos de Gestión

### Poblar tipos de análisis
```bash
python manage.py populate_analysis_types
```

### Crear grupos de usuarios
```bash
python manage.py create_groups
```

## 🔒 Seguridad

- Control de acceso basado en roles (RBAC)
- Permisos granulares por modelo
- Auditoría de cambios
- Estado protegido (FSM)
- Transacciones atómicas para código único

## 📱 Dashboard

El dashboard administrativo incluye:
- Métricas totales (órdenes, muestras)
- Órdenes por estado
- Órdenes por prioridad
- Órdenes por área solicitante
- Filtros dinámicos

## 🧪 Testing

Para ejecutar las pruebas:
```bash
python manage.py test solicitudes
```

## 📝 Notas de Desarrollo

- El proyecto usa SQLite por defecto para facilitar el desarrollo
- Para producción, se recomienda PostgreSQL
- Django Unfold proporciona una interfaz administrativa moderna
- django-fsm garantiza transiciones de estado seguras
- El sistema está preparado para cumplir con estándares GxP

## 📚 Documentación Adicional

- [Django 6.0 Documentation](https://docs.djangoproject.com/en/6.0/)
- [Django Unfold Documentation](https://github.com/unfoldadmin/django-unfold)
- [django-fsm Documentation](https://github.com/viewflow/django-fsm)

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Daniel Yepez Garces - [@danielyepezgarces](https://github.com/danielyepezgarces)

## 🙏 Agradecimientos

- Django Software Foundation
- Comunidad de Django
- Contribuidores de django-unfold y django-fsm