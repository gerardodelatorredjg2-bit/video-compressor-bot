# Telegram Video Compressor Bot

## Overview
Un bot de Telegram profesional para comprimir videos usando Pyrogram y FFmpeg. Permite comprimir videos de cualquier tamaño incluyendo archivos mayores de 4GB con barra de progreso, sistema de cola, y cancelación de operaciones.

## Recent Changes
- **2025-11-27**: Optimizado para videos de 4GB+
  - Subprocess directo para FFmpeg (mejor manejo de memory)
  - Timeout de seguridad en lectura de output
  - Mejor manejo de errores para archivos muy grandes
  - Soporte para archivos >4GB en Render
  - Puerto dinámico compatible con Render

## Features
- ✅ Compresión ultra agresiva con HEVC (70-90% en 240p)
- ✅ Soporte para archivos mayores de 4GB
- ✅ Barra de progreso en tiempo real (cada 5%)
- ✅ Sistema de cola para múltiples solicitudes
- ✅ Cancelación de operaciones en curso
- ✅ Reporte de reducción de tamaño
- ✅ Limpieza automática de archivos temporales
- ✅ Soporte para múltiples formatos (MP4, AVI, MOV, MKV, FLV, WMV)
- ✅ 5 presets de calidad (240p, 360p, 480p, 720p, original)
- ✅ Nombres de video preservados
- ✅ Keep-alive web server para hosting 24/7 gratis

## Project Architecture
```
/
├── bot.py                 # Main bot with Pyrogram + aiohttp server
├── config.py              # Configuration and environment variables
├── compressor.py          # Video compression with FFmpeg (HEVC codec)
├── queue_manager.py       # Queue system for managing requests
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── Procfile               # Render deployment config
├── Dockerfile             # Docker deployment config
├── fly.toml               # Fly.io deployment config
├── RENDER_SETUP.md        # Render deployment guide
└── .env                   # Environment variables (not in git)
```

## Dependencies
- Python 3.11+
- Pyrogram (Telegram MTProto client)
- TgCrypto (encryption for Pyrogram)
- FFmpeg 7.1.1+ (video processing with libx265)
- ffmpeg-python (Python wrapper)
- aiofiles (async file operations)
- aiohttp (async web server for keep-alive)

## Commands
- `/start` - Mostrar bienvenida
- `/help` - Ayuda detallada
- `/quality` - Cambiar calidad predeterminada
- `/stats` - Ver estadísticas y optimizaciones activas
- `/cancel` - Cancelar compresión actual

## Quality Presets & Expected Performance
- **240p**: ~70-90% reducción (máxima compresión)
- **360p**: ~60-80% reducción ⭐ (recomendado)
- **480p**: ~50-70% reducción
- **720p**: ~30-50% reducción
- **Original**: Máxima velocidad

## Optimizations Applied
- ✅ Codec HEVC (libx265) - Mejor compresión que H.264
- ✅ Preset ultrafast - Máxima velocidad
- ✅ Copia directa de audio - Sin recodificación
- ✅ Escalado fast_bilinear - Algoritmo ultra-rápido
- ✅ Barra de progreso cada 5% - Balance speed/feedback
- ✅ FFmpeg loglevel error - Solo errores críticos
- ✅ Multi-threading habilitado - Máximo rendimiento
- ✅ Subprocess directo - Mejor manejo de memoria para 4GB+
- ✅ Timeouts de seguridad - Evita procesos atrapados
- ✅ Keep-alive web server - 24/7 en hosting gratis

## Deployment
- **Render**: Free tier 24/7 con UptimeRobot keep-alive
- **Railway**: Free tier alternativo
- **Fly.io**: Configuración disponible

## User Preferences
- Language: Spanish
- Bot username: @Compresor_minimisador_bot
- Barra de progreso: Cada 5%
- Calidad predeterminada: 360p
- GitHub: https://github.com/gerardodelatorredjg2-bit/video-compressor-bot

## 24/7 Setup (Render + UptimeRobot)
1. Render deploy: https://render.com (selecciona Free plan)
2. UptimeRobot: https://uptimerobot.com (crea monitor HTTP en /health cada 5 min)
3. Bot correrá 24/7 sin costo ✅
