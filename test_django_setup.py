import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcondominioia.settings')

try:
    print("Iniciando Django setup...")
    django.setup()
    print("✅ Django setup exitoso")
    
    print("\nVerificando imports de apps...")
    from users import models as users_models
    print("✅ users.models")
    
    from finance import models as finance_models
    print("✅ finance.models")
    
    from areas import models as areas_models
    print("✅ areas.models")
    
    from communication import models as communication_models
    print("✅ communication.models")
    
    from security import models as security_models
    print("✅ security.models")
    
    print("\n✅ Todas las apps se cargaron correctamente")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    import traceback
    print("\nTraceback completo:")
    traceback.print_exc()
