# Telegram Video Compressor Bot

## Overview
Un bot de Telegram profesional para comprimir videos usando Pyrogram y FFmpeg. Permite comprimir videos de cualquier tamaño (incluidos archivos mayores de 50 MB) con barra de progreso, sistema de cola, y cancelación de operaciones.

## Recent Changes
- **2025-11-15**: Bot completamente implementado y funcionando
  - Instalado Python 3.11 y FFmpeg
  - Configurado Pyrogram para soporte de archivos grandes (+50 MB)
  - Implementado sistema de compresión con FFmpeg (H.264, CRF 28)
  - Sistema de cola con un worker por usuario
  - Cancelación robusta con limpieza de banderas
  - Sanitización de nombres de archivo (prevención path traversal)
  - Limpieza garantizada de archivos temporales en todos los casos
  - Barras de progreso en tiempo real para descarga, compresión y subida

## Features
- ✅ Compresión de video con FFmpeg (calidad optimizada)
- ✅ Soporte para archivos mayores de 50 MB usando Pyrogram
- ✅ Barra de progreso en tiempo real
- ✅ Sistema de cola para múltiples solicitudes
- ✅ Cancelación de operaciones en curso
- ✅ Reporte de reducción de tamaño
- ✅ Limpieza automática de archivos temporales
- ✅ Soporte para múltiples formatos (MP4, AVI, MOV, MKV)

## Project Architecture
```
/
├── bot.py                 # Main bot file with Pyrogram client
├── config.py              # Configuration and environment variables
├── compressor.py          # Video compression logic with FFmpeg
├── queue_manager.py       # Queue system for managing requests
├── utils.py               # Utility functions (file size, cleanup)
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in git)
```

## Dependencies
- Python 3.11+
- Pyrogram (Telegram MTProto client)
- TgCrypto (encryption for Pyrogram)
- FFmpeg (video processing)
- ffmpeg-python (Python wrapper)
- aiofiles (async file operations)

## User Preferences
- Language: Spanish
- Bot username: @Compresor_minimisador_bot
