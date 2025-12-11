import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcondominioia.settings')
django.setup()

# Intentar ejecutar makemigrations programáticamente
from django.core.management import call_command

try:
    call_command('makemigrations', verbosity=3)
except Exception as e:
    import traceback
    print(f"\n{'='*60}")
    print("ERROR COMPLETO:")
    print(f"{'='*60}")
    traceback.print_exc()
    print(f"{'='*60}")
