# Telegram Video Compressor Bot

## Overview
Un bot de Telegram profesional para comprimir videos usando Pyrogram y FFmpeg. Permite comprimir videos de cualquier tamaño (incluidos archivos mayores de 50 MB) con barra de progreso, sistema de cola, y cancelación de operaciones.

## Recent Changes
- **2025-11-27**: Optimizaciones máximas al bot
  - Cambio a codec HEVC (libx265) para mejor compresión (~30-40% adicional)
  - Bitrates y CRF más agresivos para máxima compresión
  - Barra de progreso cada 10% (optimizado)
  - Copia directa de audio (sin recodificación)
  - Escalado ultra-rápido con algoritmo optimizado
  - Comando /stats para ver estadísticas del bot
  - Limpieza instantánea de archivos temporales

## Features
- ✅ Compresión ultra agresiva con HEVC (70-90% en 240p)
- ✅ Soporte para archivos mayores de 50 MB usando Pyrogram
- ✅ Barra de progreso en tiempo real (cada 10%)
- ✅ Sistema de cola para múltiples solicitudes
- ✅ Cancelación de operaciones en curso
- ✅ Reporte de reducción de tamaño
- ✅ Limpieza automática de archivos temporales
- ✅ Soporte para múltiples formatos (MP4, AVI, MOV, MKV, FLV, WMV)
- ✅ 5 presets de calidad (240p, 360p, 480p, 720p, original)
- ✅ Nombres de video y miniatura preservados

## Project Architecture
```
/
├── bot.py                 # Main bot with Pyrogram client
├── config.py              # Configuration and environment variables
├── compressor.py          # Video compression with FFmpeg (HEVC codec)
├── queue_manager.py       # Queue system for managing requests
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in git)
```

## Dependencies
- Python 3.11+
- Pyrogram (Telegram MTProto client)
- TgCrypto (encryption for Pyrogram)
- FFmpeg 7.1.1+ (video processing with libx265)
- ffmpeg-python (Python wrapper)
- aiofiles (async file operations)

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
- ✅ Barra de progreso cada 10% - Menos overhead
- ✅ FFmpeg loglevel error - Solo errores críticos
- ✅ Multi-threading habilitado - Máximo rendimiento

## User Preferences
- Language: Spanish
- Bot username: @Compresor_minimisador_bot
- Barra de progreso: Cada 10%
- Calidad predeterminada: 360p
