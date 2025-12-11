import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcondominioia.settings')

try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'check', '--deploy'])
except Exception as e:
    print(f"\n{'='*80}")
    print("ERROR ENCONTRADO:")
    print(f"{'='*80}")
    import traceback
    traceback.print_exc()
    print(f"{'='*80}")
