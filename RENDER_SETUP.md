# Setup del Bot en Render (24/7 Gratis)

## Paso 1: Prepara tu código en GitHub

```bash
git add .
git commit -m "Add keep-alive server for Render"
git push origin main
```

## Paso 2: Deploy en Render

1. Ve a [render.com](https://render.com)
2. Haz login/signup
3. Click en "New +"
4. Selecciona "Web Service"
5. Conecta tu GitHub
6. Configura:
   - **Name**: video-compressor-bot
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Environment**: Python 3.11
   - **Plan**: Free

7. Añade Variables de Entorno (Environment):
   - `BOT_TOKEN` = tu token
   - `API_ID` = tu API ID
   - `API_HASH` = tu API Hash

8. Click "Create Web Service"

## Paso 3: Configura Keep-Alive con UptimeRobot (GRATIS)

Para que **no se apague** cuando no hay actividad:

1. Ve a [uptimerobot.com](https://uptimerobot.com)
2. Sign up gratis
3. Click "Add New Monitor"
4. Selecciona "HTTP(s)"
5. Configura:
   - **URL**: `https://tu-app.onrender.com/health`
   - **Monitoring Interval**: 5 minutos
   - **Alert Contacts**: Tu email
6. Click "Create Monitor"

## ¡Listo! ✅

- Tu bot estará en Render 24/7
- El servidor web responde a pings cada 5 minutos
- Render nunca lo apagará
- **Completamente gratis**

## URL de tu bot
`https://tu-app.onrender.com` (cambia "tu-app" por el nombre de tu servicio en Render)

## Endpoints disponibles:
- `GET /health` - Estado del bot
- `GET /` - También funciona

Respuesta:
```json
{
  "status": "ok",
  "bot": "Video Compressor Bot",
  "message": "Bot is running 24/7 ✅"
}
```

---

**Nota**: El bot tardará ~30 segundos en iniciar después de la primera llamada (cold start de Render gratis).
