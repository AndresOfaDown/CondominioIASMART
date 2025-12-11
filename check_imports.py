import sys
import os

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcondominioia.settings')

try:
    import django
    django.setup()
    
    # Try importing each app's models
    print("Importando modelos de users...")
    from users import models as users_models
    print("✓ Users models OK")
    
    print("Importando modelos de finance...")
    from finance import models as finance_models
    print("✓ Finance models OK")
    
    print("Importando modelos de areas...")
    from areas import models as areas_models
    print("✓ Areas models OK")
    
    print("Importando modelos de communication...")
    from communication import models as communication_models
    print("✓ Communication models OK")
    
    print("Importando modelos de security...")
    from security import models as security_models
    print("✓ Security models OK")
    
    print("\n¡Todas las importaciones exitosas!")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
