# Cómo Crear Roles (Grupos) en el Sistema

## Métodos para Crear Roles

Hay dos formas principales de crear roles en el sistema Lab Cannabis:

---

## Método 1: Usando el Comando de Django (Recomendado)

El sistema ya tiene un comando personalizado que crea automáticamente los 4 roles principales:

```bash
python manage.py create_groups
```

Este comando creará los siguientes grupos con sus permisos:

### 1. **Solicitante**
- Puede crear solicitudes de análisis
- Puede ver sus propias solicitudes
- Puede agregar muestras
- **Permisos:**
  - `add_solicitud`
  - `view_solicitud`
  - `add_muestra`
  - `view_muestra`

### 2. **Recepcionista** (Recepción)
- Puede ver todas las solicitudes
- Puede recibir y verificar muestras
- **Permisos:**
  - `view_solicitud`
  - `view_muestra`
  - `add_recepcionmuestra`
  - `change_recepcionmuestra`
  - `view_recepcionmuestra`
  - `can_receive_samples`

### 3. **Analista**
- Puede ver y modificar solicitudes
- Puede analizar muestras
- Puede completar análisis
- **Permisos:**
  - `view_solicitud`
  - `change_solicitud`
  - `view_muestra`
  - `change_muestra`
  - `can_analyze_samples`
  - `can_complete_orders`

### 4. **Administrador**
- Acceso completo a todo el sistema
- Puede crear, editar y eliminar registros
- Puede gestionar usuarios y grupos
- **Permisos:**
  - Todos los permisos de Solicitud
  - Todos los permisos de Muestra
  - Todos los permisos de RecepcionMuestra
  - Todos los permisos especiales

**Ubicación del comando:** `solicitudes/management/commands/create_groups.py`

---

## Método 2: Manualmente a través del Admin Panel

Si necesitas crear roles adicionales o personalizados:

### Paso 1: Acceder al Admin Panel
1. Inicia sesión como **superusuario** o **Administrador**
2. Ve a: **Administración → Grupos**

### Paso 2: Crear un Nuevo Grupo
1. Haz clic en **"Agregar Grupo"**
2. Ingresa el nombre del grupo (por ejemplo: "Supervisor", "Auditor")

### Paso 3: Asignar Permisos
En la sección **"Permisos disponibles"**, selecciona los permisos que deseas asignar:

#### Permisos Comunes por Modelo:

**Solicitud (solicitudes | solicitud)**
- `add_solicitud` - Crear solicitudes
- `change_solicitud` - Modificar solicitudes
- `delete_solicitud` - Eliminar solicitudes
- `view_solicitud` - Ver solicitudes

**Muestra (solicitudes | muestra)**
- `add_muestra` - Crear muestras
- `change_muestra` - Modificar muestras
- `delete_muestra` - Eliminar muestras
- `view_muestra` - Ver muestras

**RecepcionMuestra (solicitudes | recepcion muestra)**
- `add_recepcionmuestra` - Crear recepciones
- `change_recepcionmuestra` - Modificar recepciones
- `delete_recepcionmuestra` - Eliminar recepciones
- `view_recepcionmuestra` - Ver recepciones

**Permisos Especiales:**
- `can_receive_samples` - Puede recibir muestras
- `can_analyze_samples` - Puede analizar muestras
- `can_complete_orders` - Puede completar órdenes

### Paso 4: Guardar el Grupo
Haz clic en **"Guardar"**

---

## Asignar Usuarios a Grupos

### Opción A: Automático (para nuevos usuarios)
Los nuevos usuarios se asignan automáticamente al grupo **Solicitante** cuando se crean.

### Opción B: Manual (cambiar grupo de un usuario)
1. Ve a: **Administración → Usuarios**
2. Selecciona el usuario que deseas modificar
3. En la sección **"Permisos"**, busca **"Grupos"**
4. Mueve los grupos deseados de "Grupos disponibles" a "Grupos elegidos"
5. Haz clic en **"Guardar"**

---

## Verificar Grupos Existentes

Para ver qué grupos ya existen en el sistema:

### Usando el Admin Panel:
1. Ve a: **Administración → Grupos**
2. Verás la lista de todos los grupos configurados

### Usando Django Shell:
```python
python manage.py shell

from django.contrib.auth.models import Group

# Listar todos los grupos
groups = Group.objects.all()
for group in groups:
    print(f"Grupo: {group.name}")
    print(f"  Permisos: {group.permissions.count()}")
```

---

## Ejemplo: Crear un Rol Personalizado "Supervisor"

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from solicitudes.models import Solicitud, Muestra

# Crear el grupo
supervisor = Group.objects.create(name='Supervisor')

# Obtener permisos
solicitud_ct = ContentType.objects.get_for_model(Solicitud)
muestra_ct = ContentType.objects.get_for_model(Muestra)

# Asignar permisos
permisos = Permission.objects.filter(
    content_type__in=[solicitud_ct, muestra_ct],
    codename__in=['view_solicitud', 'change_solicitud', 'view_muestra']
)

supervisor.permissions.set(permisos)
print(f"Grupo '{supervisor.name}' creado con {supervisor.permissions.count()} permisos")
```

---

## Permisos por Grupo (Matriz RBAC)

| Permiso                  | Solicitante | Recepcionista | Analista | Administrador |
|--------------------------|-------------|---------------|----------|---------------|
| Crear solicitudes        | ✓           | ✗             | ✗        | ✓             |
| Ver solicitudes          | ✓ (propias) | ✓ (todas)     | ✓        | ✓             |
| Modificar solicitudes    | ✗           | ✗             | ✓        | ✓             |
| Eliminar solicitudes     | ✗           | ✗             | ✗        | ✓             |
| Crear muestras           | ✓           | ✗             | ✗        | ✓             |
| Ver muestras             | ✓ (propias) | ✓ (todas)     | ✓        | ✓             |
| Modificar muestras       | ✗           | ✗             | ✓        | ✓             |
| Recibir muestras         | ✗           | ✓             | ✗        | ✓             |
| Analizar muestras        | ✗           | ✗             | ✓        | ✓             |
| Completar análisis       | ✗           | ✗             | ✓        | ✓             |
| Gestionar usuarios       | ✗           | ✗             | ✗        | ✓             |
| Modificar estado directamente | ✗      | ✗             | ✗        | ✓             |

---

## Consejos y Mejores Prácticas

1. **Usa el comando `create_groups`** la primera vez para configurar los roles básicos
2. **No elimines los grupos principales** (Solicitante, Recepcionista, Analista, Administrador)
3. **Asigna solo los permisos necesarios** siguiendo el principio de menor privilegio
4. **Documenta roles personalizados** si creas nuevos grupos
5. **Revisa periódicamente** los permisos asignados a cada grupo
6. **Usa grupos en lugar de permisos individuales** para facilitar la gestión

---

## Solución de Problemas

### Problema: "El grupo no aparece en la lista"
**Solución:** Ejecuta `python manage.py create_groups` para crear los grupos base.

### Problema: "El usuario no puede ver ciertas secciones"
**Solución:** Verifica que el usuario esté asignado al grupo correcto y que el grupo tenga los permisos necesarios.

### Problema: "Error al crear usuarios nuevos"
**Solución:** Asegúrate de que el grupo "Solicitante" exista, ya que se asigna automáticamente.

---

## Resumen Rápido

Para configurar el sistema por primera vez:

```bash
# 1. Crear grupos base
python manage.py create_groups

# 2. Crear un superusuario
python manage.py createsuperuser

# 3. Asignar el superusuario al grupo Administrador (opcional, ya tiene todos los permisos)
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='admin')
>>> admin_group = Group.objects.get(name='Administrador')
>>> user.groups.add(admin_group)
```

¡Listo! El sistema de roles está configurado y funcionando.
