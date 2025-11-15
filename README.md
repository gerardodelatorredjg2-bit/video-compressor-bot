# 🎥 Bot Compresor de Video para Telegram

Bot profesional de Telegram para comprimir videos con soporte para archivos grandes (más de 50 MB).

## ✨ Características

- ✅ **Compresión de alta calidad** usando FFmpeg con H.264
- ✅ **Archivos grandes** - Soporte para videos de más de 50 MB usando Pyrogram
- ✅ **Barra de progreso** en tiempo real durante descarga, compresión y subida
- ✅ **Sistema de cola** inteligente para múltiples solicitudes
- ✅ **Cancelación** de operaciones en curso con `/cancel`
- ✅ **Reporte de reducción** de tamaño con estadísticas
- ✅ **Limpieza automática** de archivos temporales
- ✅ **Formatos soportados**: MP4, AVI, MOV, MKV, FLV, WMV, M4V

## 📋 Requisitos

- Python 3.11+
- FFmpeg
- Credenciales de Telegram:
  - **BOT_TOKEN** (obtenido de @BotFather)
  - **API_ID** y **API_HASH** (de https://my.telegram.org/apps)

## 🚀 Uso

1. **Busca el bot en Telegram**: @Compresor_minimisador_bot

2. **Envía un video** - El bot lo comprimirá automáticamente

3. **Comandos disponibles**:
   - `/start` - Mostrar mensaje de bienvenida
   - `/help` - Ayuda detallada
   - `/cancel` - Cancelar compresión actual

## 🛠️ Arquitectura

```
├── bot.py              # Cliente Pyrogram con manejadores de comandos
├── config.py           # Configuración y variables de entorno
├── compressor.py       # Lógica de compresión con FFmpeg
├── queue_manager.py    # Sistema de cola para solicitudes
├── utils.py            # Funciones auxiliares
└── requirements.txt    # Dependencias de Python
```

## 🔧 Configuración Técnica

- **Compresión**: H.264 con CRF 28, preset medium
- **Audio**: AAC a 128k
- **Escalado**: Automático con dimensiones pares
- **Seguridad**: Sanitización de nombres de archivo
- **Concurrencia**: Un worker por usuario

## 📊 Ejemplo de Uso

1. Usuario envía video de 150 MB
2. Bot descarga con barra de progreso
3. FFmpeg comprime (reduce ~50-70%)
4. Bot sube video comprimido
5. Usuario recibe estadísticas de reducción

## ⚙️ Características Técnicas

- **Async/await** para operaciones I/O eficientes
- **Sistema de cola** para evitar sobrecarga
- **Manejo robusto de errores** con limpieza garantizada
- **Prevención de path traversal** en nombres de archivo
- **Cancelación segura** sin race conditions
