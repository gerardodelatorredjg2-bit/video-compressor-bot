# Telegram Video Compressor Bot

## Overview
Bot profesional de Telegram para comprimir videos con Pyrogram y FFmpeg. Soporta videos hasta 2GB con compresión ultra-rápida (velocidad empresarial), barra de progreso en tiempo real con estadísticas, sistema de cola, y cancelación de operaciones.

## Status
✅ **PRODUCCIÓN LISTA** - El bot funciona al 100%

## Recent Changes (2025-11-28)
- **Compresión ultra-rápida**: Preset veryfast + CRF agresivo (36-38)
- **Panel de estadísticas**: Muestra tiempo transcurrido, velocidad (MB/s) y tamaño en tiempo real
- **Descarga robusta**: Manejo automático de archivos .temp
- **Límite de 2GB**: Revertido de 3GB por estabilidad
- **Barra de progreso cada 2%**: Actualizaciones suave sin errores Telegram
- **Envío de videos**: Se envía correctamente con metadatos de duración

## Features
- ✅ Compresión agresiva HEVC (70-90% en 240p)
- ✅ Soporte para videos hasta 2GB
- ✅ Barra de progreso en tiempo real (actualiza cada 2%)
- ✅ **Panel de estadísticas en vivo**: ⏱️ Tiempo, 🎛️ Velocidad, 📦 Tamaño
- ✅ Sistema de cola para múltiples solicitudes
- ✅ Cancelación de operaciones en curso
- ✅ Reporte de reducción de tamaño
- ✅ Limpieza automática de archivos temporales
- ✅ 5 presets de calidad (240p, 360p, 480p, 720p, original)
- ✅ Keep-alive web server para hosting 24/7 gratis

## Project Architecture
```
/
├── bot.py                 # Main bot - Pyrogram + aiohttp + progress tracking
├── config.py              # Config: BOT_TOKEN, API_ID, API_HASH, MAX_FILE_SIZE=2GB
├── compressor.py          # Video compression con FFmpeg (HEVC ultrafast)
├── queue_manager.py       # Queue system para múltiples usuarios
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── Procfile               # Render deployment
├── Dockerfile             # Docker deployment
├── fly.toml               # Fly.io deployment
└── downloads/             # Carpeta temporal de trabajo
```

## Dependencies
- Python 3.11+
- Pyrogram 2.0.106 (Telegram MTProto)
- TgCrypto 1.2.5 (encryption)
- FFmpeg 7.1.1+ (libx265 codec)
- python-dotenv 1.0.0
- aiofiles 23.2.1 (async file ops)
- aiohttp 3.9.1 (keep-alive server)

## Commands
- `/start` - Bienvenida y botones
- `/help` - Ayuda detallada
- `/quality` - Cambiar calidad predeterminada (240p/360p/480p/720p/original)
- `/stats` - Ver optimizaciones activas
- `/cancel` - Cancelar compresión actual

## Quality Presets & Performance
- **240p**: ~70-90% reducción (máxima compresión)
- **360p**: ~60-80% reducción ⭐ (recomendado, rápido)
- **480p**: ~50-70% reducción
- **720p**: ~30-50% reducción
- **Original**: Solo cambia codec, máxima velocidad

## Optimizations Active
- ✅ Codec HEVC (libx265) - Mejor compresión
- ✅ Preset veryfast - Velocidad empresarial
- ✅ Copia directa de audio - Sin recodificación
- ✅ CRF 36-38 - Máxima agresividad en compresión
- ✅ Escalado fast_bilinear - Ultra-rápido
- ✅ Barra de progreso cada 2% - Sin errores Telegram
- ✅ Manejo robusto de .temp files - Descarga segura
- ✅ Estadísticas en vivo - Tiempo, velocidad, tamaño
- ✅ Keep-alive web server - 24/7 en free tier

## Deployment (Render Free Tier + UptimeRobot)
1. Deploy en Render.com (Free plan)
2. Configura UptimeRobot para monitor HTTP /health cada 5 min
3. Bot corre 24/7 sin costo ✅

## Max File Size
- **Límite**: 2GB (estable)
- **Configuración**: `config.py` -> `MAX_FILE_SIZE = 2000 * 1024 * 1024`

## User Preferences
- Language: Spanish
- Bot: @Compresor_minimisador_bot
- Barra de progreso: Cada 2%
- Calidad default: 360p
- GitHub: https://github.com/gerardodelatorredjg2-bit/video-compressor-bot

## Known Limitations
- Max 2GB por video (trade-off entre estabilidad y tamaño)
- Free tier CPU compartido (40-80% uso durante compresión)
- Descarga Pyrogram puede ser lenta en archivos muy grandes

## Testing Status
✅ Todos los flujos testeados:
- Descarga de videos
- Compresión correcta
- Envío de video comprimido
- Barra de progreso con estadísticas
- Cancelación de operaciones
- Manejo de errores

## Ready for Production ✅
El bot está completamente funcional y listo para producción 24/7 en Render.
