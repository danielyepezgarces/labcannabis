# Setup Guide - Analysis Types Not Appearing

If you're experiencing issues where the analysis types are not appearing in the form, follow these steps:

## Problem
The analysis types checkboxes are not showing up in the inline sample form when creating/editing orders.

## Solution

### Step 1: Ensure Database is Migrated
```bash
python manage.py migrate
```

### Step 2: Populate Analysis Types (REQUIRED)
This is the most important step. You must run this command to create the 14 analysis types in the database:

```bash
python manage.py populate_analysis_types
```

This command will create:

**Físicos (6 types):**
- Apariencia
- % Humedad
- Actividad de agua
- Materia extraña
- Cenizas totales
- Cenizas insolubles en ácido

**Químicos (6 types):**
- Potencia cannabinoides
- Terpenos
- Pesticidas
- Metales pesados
- Impurezas elementales
- Solventes residuales

**Microbiológicos (2 types):**
- Microbiología general
- Micotoxinas

### Step 3: Verify Analysis Types Were Created
```bash
python manage.py shell
```

Then in the Python shell:
```python
from solicitudes.models import TipoAnalisis
print(f"Total analysis types: {TipoAnalisis.objects.count()}")
# Should print: Total analysis types: 14

# List all analysis types
for tipo in TipoAnalisis.objects.all():
    print(f"  - {tipo.get_categoria_display()}: {tipo.nombre}")
```

### Step 4: Restart Your Server
After populating the data, restart your Django server:
```bash
python manage.py runserver
```

### Step 5: Clear Browser Cache
Sometimes the form might be cached. Clear your browser cache or do a hard refresh (Ctrl+F5 or Cmd+Shift+R).

## For Production Deployment

If you're deploying to production (e.g., labcannabis.dyepezg.dev), make sure to run these commands on the production server:

```bash
# 1. Run migrations
python manage.py migrate

# 2. Populate analysis types (CRITICAL)
python manage.py populate_analysis_types

# 3. Create user groups
python manage.py create_groups

# 4. Create superuser
python manage.py createsuperuser

# 5. Collect static files
python manage.py collectstatic --noinput
```

## Troubleshooting

### The checkboxes still don't appear
1. Check if the analysis types exist:
   ```bash
   python manage.py shell -c "from solicitudes.models import TipoAnalisis; print(TipoAnalisis.objects.count())"
   ```
   
2. If the count is 0, run `python manage.py populate_analysis_types` again

3. Check browser console for JavaScript errors

4. Verify you're logged in as a user with proper permissions

### I see an error about missing tables
Run migrations first:
```bash
python manage.py migrate
```

### I'm on production and it's not working
SSH into your production server and run:
```bash
cd /path/to/your/project
source venv/bin/activate  # if using virtual environment
python manage.py populate_analysis_types
sudo systemctl restart your-service  # restart your application service
```

## Expected Result

After following these steps, when you create or edit a "Solicitud" in the admin interface:
1. Click "Add another Muestra" (sample)
2. Scroll to the "Análisis Solicitados" field
3. You should see 14 checkboxes organized by category:
   - 6 Físicos
   - 6 Químicos
   - 2 Microbiológicos

Each checkbox represents one analysis type that can be selected for the sample.
