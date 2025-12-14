# 📦 Guía de Instalación - Smart Condominio IA

## 📋 Requisitos Previos

### 1. Software Necesario
- **Python 3.10+** (recomendado 3.11 o 3.12)
  - Verificar versión: `python --version`
  - Si tienes Python 3.13, puede funcionar pero algunas dependencias podrían tener problemas
- **PostgreSQL 12+** instalado y corriendo
- **Git** para clonar el repositorio
- **pip** actualizado (ver paso de instalación)

### 2. Verificar Instalaciones
```bash
# Verificar Python
python --version

# Verificar PostgreSQL (debe estar corriendo)
psql --version

# Verificar pip
pip --version
```

---

## 🚀 Pasos de Instalación

### Paso 1: Clonar el Proyecto
```bash
cd Desktop
git clone [URL_DEL_REPOSITORIO]
cd CondominioIASMART
```

### Paso 2: Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

> ✅ Deberías ver `(venv)` al inicio de tu línea de comandos

### Paso 3: Actualizar pip
```bash
# IMPORTANTE: Actualizar pip primero
python -m pip install --upgrade pip setuptools wheel
```

### Paso 4: Instalar Dependencias

#### Opción A: Instalación Normal
```bash
pip install -r requirements.txt
```

#### Opción B: Si hay errores con Pillow (como el que viste)
```bash
# Instalar primero las dependencias del sistema para Pillow
# En Windows, Pillow necesita Microsoft C++ Build Tools
# Descargar de: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# O instalar dependencias una por una:
pip install --upgrade pip
pip install Django>=5.0,<6.0
pip install psycopg2-binary==2.9.9
pip install python-decouple==3.8
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.1
pip install django-cors-headers==4.3.1
pip install Pillow  # Sin especificar versión instalará la más reciente compatible
```

### Paso 5: Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo (si existe)
# O crear manualmente el archivo .env

# Crear archivo .env en la raíz del proyecto
```

**Contenido del archivo `.env`:**
```env
# Base de datos
DB_NAME=smartcondo_db
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=tu-clave-secreta-super-larga-y-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Paso 6: Crear Base de Datos en PostgreSQL
```bash
# Abrir psql (línea de comandos de PostgreSQL)
psql -U postgres

# Dentro de psql, ejecutar:
CREATE DATABASE smartcondo_db;
CREATE USER tu_usuario_postgres WITH PASSWORD 'tu_contraseña_postgres';
GRANT ALL PRIVILEGES ON DATABASE smartcondo_db TO tu_usuario_postgres;
\q
```

### Paso 7: Ejecutar Migraciones
```bash
# Aplicar migraciones a la base de datos
python manage.py migrate
```

### Paso 8: Crear Superusuario
```bash
python manage.py createsuperuser
```
> Sigue las instrucciones en pantalla para crear tu usuario administrador

### Paso 9: Ejecutar el Servidor
```bash
python manage.py runserver
```

> ✅ El servidor debería estar corriendo en http://127.0.0.1:8000/

---

## 🔧 Solución de Problemas Comunes

### Error: "Pillow no se puede instalar"
**Síntoma:** Error al compilar Pillow con `KeyError: '__version__'`

**Soluciones:**
1. **Actualizar pip y setuptools:**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Instalar Microsoft C++ Build Tools (Windows):**
   - Descargar: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Instalar "Desktop development with C++"

3. **Instalar versión más reciente de Pillow:**
   ```bash
   pip install --upgrade Pillow
   ```

4. **Si usas Python 3.13:**
   - Considera usar Python 3.11 o 3.12 (más estables con Django)
   - Usa pyenv (Windows: pyenv-win) para gestionar versiones de Python

### Error: "psycopg2 no se puede instalar"
**Solución:**
```bash
# Usar la versión binaria (ya está en requirements.txt)
pip install psycopg2-binary
```

### Error: "No module named 'django'"
**Solución:**
```bash
# Asegúrate de que el entorno virtual esté activado
# Deberías ver (venv) en tu línea de comandos
venv\Scripts\activate

# Reinstalar Django
pip install Django>=5.0,<6.0
```

### Error: "DATABASES not configured"
**Solución:**
- Verifica que el archivo `.env` exista en la raíz del proyecto
- Verifica que las credenciales de PostgreSQL sean correctas
- Verifica que PostgreSQL esté corriendo

### Error: "Port 8000 already in use"
**Solución:**
```bash
# Usar otro puerto
python manage.py runserver 8001

# O encontrar y cerrar el proceso en el puerto 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <número_del_proceso> /F
```

---

## 📱 Verificar la Instalación

### 1. Acceder al Admin de Django
1. Ir a: http://127.0.0.1:8000/admin/
2. Iniciar sesión con el superusuario creado
3. Verificar que puedas ver el panel de administración

### 2. Probar la API
```bash
# Crear un usuario de prueba via API (si está configurado)
# O usar herramientas como Postman para probar endpoints
```

### 3. Verificar las Apps Instaladas
El proyecto debe tener las siguientes apps:
- `users` - Gestión de usuarios
- `areas` - Gestión de áreas comunes
- `finance` - Gestión financiera
- `security` - Control de seguridad
- `communication` - Sistema de comunicaciones

---

## 🎯 Próximos Pasos

Después de la instalación exitosa:
1. ✅ Familiarízate con la estructura del proyecto
2. ✅ Lee la documentación en `README.md`
3. ✅ Prueba crear algunos registros en el admin de Django
4. ✅ Revisa los endpoints de la API en `/api/`

---

## 📞 Soporte

Si encuentras problemas no listados aquí:
1. Verifica el archivo `error_log.txt` en la raíz del proyecto
2. Revisa los logs de Django en la consola
3. Contacta al equipo de desarrollo

---

## 📝 Notas Importantes

- 🔒 **Nunca** compartas tu archivo `.env` en repositorios públicos
- 🔄 Mantén tu entorno virtual activado mientras trabajas en el proyecto
- 📦 Si agregas nuevas dependencias, actualiza `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```
- 🗃️ Haz backup de tu base de datos regularmente

---

**Versión de Python recomendada:** Python 3.11 o 3.12  
**Última actualización:** Diciembre 2025
