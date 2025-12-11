import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcondominioia.settings')
django.setup()

# Obtener todas las tablas
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        AND tablename NOT LIKE 'sql_%'
    """)
    tables = cursor.fetchall()
    
    print(f"Eliminando {len(tables)} tablas...")
    
    # Eliminar todas las tablas
    for table in tables:
        table_name = table[0]
        print(f"  - Eliminando {table_name}")
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
    
    print("\n✅ Todas las tablas eliminadas correctamente")
