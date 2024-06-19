# Mosaic API

Este proyecto es una API creada con FastAPI que utiliza la API de OpenAI para generar respuestas de texto personalizadas, imágenes y preguntas de opción múltiple basadas en el perfil de usuario. También incluye la funcionalidad para convertir audio a texto y analizar contenido de PDF.

## Requisitos

- Servidor con Ubuntu (o similar) accesible vía SSH
- Python 3.7 o superior
- `pip` para la instalación de dependencias
- Cuenta en OpenAI con una clave API válida
- Acceso al DNS para configurar subdominios
- Permisos de administrador en el servidor

## Pasos de Instalación y Configuración

### 1. Conectar al Servidor SSH

Conéctate a tu servidor utilizando SSH:

```bash
ssh tu_usuario@tu_servidor_ip
```

### 2. Actualizar e Instalar Dependencias Básicas

Actualiza tu sistema e instala Python y pip:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx -y
```

### 3. Configurar el Entorno Virtual

Crea un entorno virtual para el proyecto y actívalo:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Clonar el Repositorio y Navegar a la Carpeta del Proyecto

Clona tu repositorio en el servidor:

```bash
git clone https://github.com/pedcapa/live-learning-api.git
cd live-learning-api
```

### 5. Instalar las Dependencias

Con el entorno virtual activado, instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

### 6. Configurar la Clave API de OpenAI

Crea un archivo `.env` en el directorio raíz del proyecto y añade tu clave API de OpenAI:

```plaintext
OPENAI_API_KEY=tu_clave_api_de_openai
```

### 7. Configurar Nginx para el Subdominio

Edita o crea un archivo de configuración para Nginx:

```bash
sudo nano /etc/nginx/sites-available/live.galliard.mx
```

Añade la siguiente configuración:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Guarda el archivo y crea un enlace simbólico en el directorio `sites-enabled`:

```bash
sudo ln -s /etc/nginx/sites-available/live.galliard.mx /etc/nginx/sites-enabled/
```

Prueba la configuración de Nginx para asegurarte de que no haya errores:

```bash
sudo nginx -t
```

Si todo está bien, reinicia Nginx:

```bash
sudo systemctl restart nginx
```

### 8. Configurar el Subdominio en GoDaddy

1. **Accede a tu cuenta de GoDaddy** y ve a la sección de administración de dominios.
2. **Selecciona tu dominio** `example.com` y ve a la configuración de DNS.
3. **Añade un registro A**:
   - Nombre: `api`
   - Valor: La IP de tu servidor.
   - TTL: Selecciona el valor predeterminado o 1 hora.
4. Guarda los cambios.

### 9. Iniciar la Aplicación FastAPI

Inicia la aplicación usando `uvicorn`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Para ejecutar el servidor en segundo plano y que siga funcionando después de cerrar la sesión SSH, puedes usar `screen` o `nohup`.

#### Usar `screen`:

```bash
sudo apt install screen
screen -S my_fastapi_app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Luego, presiona `Ctrl + A` seguido de `D` para desconectarte de la sesión `screen`.

#### Usar `nohup`:

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
```

### 10. Configurar como Servicio del Sistema (Opcional)

Si prefieres que la aplicación se inicie automáticamente al arrancar el sistema, puedes configurarla como un servicio de `systemd`.

Crea un archivo de servicio para `systemd`:

```bash
sudo nano /etc/systemd/system/fastapi.service
```

Añade la siguiente configuración, ajustando los caminos a tu entorno y aplicación:

```ini
[Unit]
Description=FastAPI service
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/tu-repositorio
ExecStart=/path/to/your/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Reemplaza `/path/to/your/` con la ruta adecuada en tu sistema.

Habilita y arranca el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi.service
sudo systemctl enable fastapi.service
```

## Uso de la API

A continuación se describen los endpoints disponibles en la API.

### 1. Obtener Respuesta Personalizada

**Endpoint:** `POST /api/v1/gpt_response`

**Descripción:** Obtiene una respuesta personalizada que puede incluir texto y prompts para imágenes, basándose en el perfil del usuario.

**Ejemplo de Input JSON:**

```json
{
  "prompt": "Explique el sistema solar.",
  "user_profile": {
    "interests": ["astronomía", "planetas"],
    "learning_style": ["visual"],
    "disability": ["ADHD"]
  }
}
```

**Ejemplo de Response JSON:**

```json
{
  "content": [
    {
      "type": "paragraph",
      "text": "El sistema solar es un grupo de planetas que giran alrededor del sol..."
    },
    {
      "type": "image",
      "description": "Una ilustración del sistema solar con todos los planetas alineados."
    }
  ]
}
```

### 2. Generar Imagen

**Endpoint:** `POST /api/v1/generate_image`

**Descripción:** Genera una imagen basada en un prompt utilizando la API de OpenAI.

**Ejemplo de Input JSON:**

```json
{
  "prompt": "Una ilustración de un bosque encantado.",
  "user_profile": {
    "interests": ["naturaleza", "arte"],
    "learning_style": ["visual"],
    "disability": ["dislexia"]
  }
}
```

**Ejemplo de Response JSON:**

```json
{
  "url": "https://openai.com/image_url_example"
}
```

### 3. Generar Preguntas de Opción Múltiple

**Endpoint:** `POST /api/v1/generate_quizz`

**Descripción:** Genera un conjunto de 5 preguntas de opción múltiple basadas en el contenido proporcionado.

**Ejemplo de Input JSON:**

```json
{
  "content": [{
    "type": "paragraph",
    "text": "El agua es esencial para la vida. Se encuentra en tres estados: sólido, líquido y gaseoso..."
  }]
}
```

**Ejemplo de Response JSON:**

```json
[
  {
    "question_number": 1,
    "question_text": "¿Cuáles son los tres estados del agua?",
    "options": {
      "Sólido, líquido y gaseoso": true,
      "Sólo líquido y gaseoso": false,
      "Sólido y líquido": false
    }
  }
]
```

### 4. Convertir Audio a Texto

**Endpoint:** `POST /api/v1/speech_to_text`

**Descripción:** Convierte un archivo de audio en texto utilizando el modelo Whisper de OpenAI.

**Ejemplo de Input JSON:**

```json
{
  "file": "ruta_al_archivo_de_audio.mp3"
}
```

**Ejemplo de Response JSON:**

```json
{
  "text": "Texto transcrito del audio."
}
```

### 5. Generar Respuesta Basada en PDF

**Endpoint:** `POST /api/v1/generate_via_pdf`

**Descripción:** Genera una respuesta basada en el contenido de un archivo PDF proporcionado.

**Ejemplo de Input JSON:**

```json
{
  "prompt": "ruta_al_archivo.pdf",
  "user_profile": {
    "interests": ["historia", "arte"],
    "learning_style": ["textual"],
    "disability": ["ADHD"]
  }
}
```

**Ejemplo de Response JSON:**

```json
{
  "content": [
    {
      "type": "paragraph",
      "text": "

El archivo PDF contiene información sobre..."
    }
  ]
}
```

### 6. Subir Archivo PDF o de Audio

**Endpoint:** `POST /api/v1/upload_file/`

**Descripción:** Permite subir archivos PDF o de audio al servidor.

**Ejemplo de Input (multipart/form-data):**

- `file`: El archivo que se va a subir.

**Ejemplo de Response JSON:**

```json
{
  "filename": "nombre_del_archivo.pdf",
  "location": "./app/uploads/nombre_del_archivo.pdf"
}
```

## Notas Adicionales

- Asegúrate de configurar correctamente las variables de entorno para la API de OpenAI.
- Para producción, considera usar HTTPS y configurar el servidor detrás de un proxy reverso como Nginx.
- El uso de `screen` o `nohup` es opcional pero recomendado para mantener la aplicación en ejecución en segundo plano.


## Licencia

Este proyecto está licenciado bajo la MIT License. Ver el archivo [LICENSE](LICENSE) para más detalles.
