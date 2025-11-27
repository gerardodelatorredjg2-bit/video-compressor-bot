import os
import asyncio
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiohttp import web
from config import BOT_TOKEN, API_ID, API_HASH, DOWNLOAD_DIR, DOWNLOAD_BLOCK_SIZE
from compressor import compressor, QUALITY_PRESETS
from queue_manager import queue_manager
from utils import format_bytes, cleanup_file, generate_filename, create_progress_bar, sanitize_filename, wait_for_file

app = Client(
    "video_compressor_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    max_concurrent_transmissions=10,
    workers=4,
    connection_pool_size=4,
    workdir=DOWNLOAD_DIR
)


@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    welcome_text = (
        "🎥 **Bienvenido al Compresor de Video**\n\n"
        "Envíame un video y lo comprimiré para reducir su tamaño.\n\n"
        "**Características:**\n"
        "✅ Compresión ultra agresiva (360p por defecto)\n"
        "✅ Múltiples opciones de calidad\n"
        "✅ Soporte para archivos grandes (+50 MB)\n"
        "✅ Barra de progreso mejorada\n"
        "✅ Sistema de cola inteligente\n"
        "✅ Cancelación de operaciones\n\n"
        "¡Envía un video para comenzar!"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚 Ayuda", callback_data="show_help"),
            InlineKeyboardButton("⚙️ Calidad", callback_data="show_quality")
        ],
        [
            InlineKeyboardButton("📊 Estadísticas", callback_data="show_stats"),
            InlineKeyboardButton("❌ Cancelar", callback_data="show_cancel")
        ]
    ])
    await message.reply_text(welcome_text, reply_markup=keyboard)

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = (
        "📚 **Ayuda del Bot Compresor**\n\n"
        "**Cómo usar:**\n"
        "1. Envía un archivo de video\n"
        "2. Selecciona la calidad (o usa 360p por defecto)\n"
        "3. Espera mientras se comprime\n"
        "4. Recibe tu video comprimido\n\n"
        "**Formatos soportados:**\n"
        "MP4, AVI, MOV, MKV, FLV, WMV\n\n"
        "**Calidades disponibles:**\n"
        "• 240p - Máxima compresión (~80-90% reducción)\n"
        "• 360p - Alta compresión (~60-80% reducción) ⭐\n"
        "• 480p - Compresión media (~40-60% reducción)\n"
        "• 720p - Buena calidad (~20-40% reducción)\n"
        "• Original - Solo cambia codec"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Cambiar Calidad", callback_data="show_quality")]
    ])
    await message.reply_text(help_text, reply_markup=keyboard)

@app.on_message(filters.command("quality"))
async def quality_command(client, message: Message):
    user_id = message.from_user.id
    current_quality = compressor.get_user_quality(user_id)
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("240p 🔥", callback_data="quality_240p"),
            InlineKeyboardButton("360p ⭐", callback_data="quality_360p")
        ],
        [
            InlineKeyboardButton("480p 📺", callback_data="quality_480p"),
            InlineKeyboardButton("720p 🎬", callback_data="quality_720p")
        ],
        [
            InlineKeyboardButton("Original 📹", callback_data="quality_original")
        ]
    ])
    
    await message.reply_text(
        f"🎛️ **Configuración de Calidad**\n\n"
        f"Calidad actual: **{QUALITY_PRESETS[current_quality]['name']}**\n\n"
        f"Selecciona la calidad predeterminada para tus videos:\n\n"
        f"• 240p - Máxima compresión (archivos muy pequeños)\n"
        f"• 360p - Alta compresión (recomendado) ⭐\n"
        f"• 480p - Compresión media\n"
        f"• 720p - Buena calidad\n"
        f"• Original - Solo cambia el codec",
        reply_markup=keyboard
    )

@app.on_message(filters.command("cancel"))
async def cancel_command(client, message: Message):
    user_id = message.from_user.id
    
    if queue_manager.is_processing(user_id):
        compressor.set_cancel_flag(user_id, True)
        queue_manager.clear_queue(user_id)
        await message.reply_text("❌ **Operación cancelada**\n\nSe ha detenido la compresión actual.")
    else:
        queue_position = queue_manager.get_queue_position(user_id)
        if queue_position > 0:
            queue_manager.clear_queue(user_id)
            await message.reply_text("❌ **Cola limpiada**\n\nSe han eliminado todos los videos pendientes.")
        else:
            await message.reply_text("ℹ️ No hay ninguna operación en curso para cancelar.")

@app.on_message(filters.command("stats"))
async def stats_command(client, message: Message):
    stats_text = (
        "📊 **Estadísticas del Bot**\n\n"
        "🚀 **Optimizaciones Activas:**\n"
        "✅ Codec HEVC (libx265) - Mejor compresión\n"
        "✅ Preset ultrafast - Máxima velocidad\n"
        "✅ Copia directa de audio - Sin recodificación\n"
        "✅ Escalado rápido - Algoritmo optimizado\n"
        "✅ Barra de progreso en tiempo real\n"
        "✅ Cola inteligente por usuario\n\n"
        "⚡ **Rendimiento Esperado:**\n"
        "• 240p: ~70-90% reducción de tamaño\n"
        "• 360p: ~60-80% reducción de tamaño ⭐\n"
        "• 480p: ~50-70% reducción de tamaño\n"
        "• 720p: ~30-50% reducción de tamaño\n\n"
        "💡 **Tips:**\n"
        "• Usa 240p para máxima compresión\n"
        "• Usa 360p para balance (recomendado)\n"
        "• /quality para cambiar predeterminado"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Cambiar Calidad", callback_data="show_quality")]
    ])
    await message.reply_text(stats_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^show_"))
async def menu_callback(client, callback_query: CallbackQuery):
    action = callback_query.data.split("_")[1]
    
    if action == "help":
        help_text = (
            "📚 **Ayuda del Bot Compresor**\n\n"
            "**Cómo usar:**\n"
            "1. Envía un archivo de video\n"
            "2. Selecciona la calidad\n"
            "3. Espera mientras se comprime\n"
            "4. ¡Recibe tu video!\n\n"
            "**Formatos:** MP4, AVI, MOV, MKV, FLV, WMV\n"
            "**Máximo:** 3GB por video"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Calidad", callback_data="show_quality")]
        ])
        await callback_query.message.edit_text(help_text, reply_markup=keyboard)
    
    elif action == "quality":
        user_id = callback_query.from_user.id
        current_quality = compressor.get_user_quality(user_id)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("240p 🔥", callback_data="quality_240p"),
                InlineKeyboardButton("360p ⭐", callback_data="quality_360p")
            ],
            [
                InlineKeyboardButton("480p 📺", callback_data="quality_480p"),
                InlineKeyboardButton("720p 🎬", callback_data="quality_720p")
            ],
            [InlineKeyboardButton("Original 📹", callback_data="quality_original")]
        ])
        await callback_query.message.edit_text(
            f"🎛️ **Configuración de Calidad**\n\n"
            f"Calidad actual: **{QUALITY_PRESETS[current_quality]['name']}**",
            reply_markup=keyboard
        )
    
    elif action == "stats":
        stats_text = (
            "📊 **Estadísticas y Optimizaciones**\n\n"
            "🚀 **Activas:**\n"
            "✅ HEVC (libx265)\n"
            "✅ Ultrafast preset\n"
            "✅ 10 descargas paralelas\n"
            "✅ 1MB block size\n\n"
            "📈 **Rendimiento:**\n"
            "• 240p: 70-90% reducción\n"
            "• 360p: 60-80% reducción ⭐\n"
            "• 480p: 50-70% reducción\n"
            "• 720p: 30-50% reducción"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Calidad", callback_data="show_quality")]
        ])
        await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
    
    elif action == "cancel":
        await callback_query.answer("Usa /cancel para cancelar operaciones")

@app.on_callback_query(filters.regex("^quality_"))
async def quality_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data_str = str(callback_query.data)
    quality = data_str.split("_")[1]
    
    compressor.set_user_quality(user_id, quality)
    
    await callback_query.answer(f"✅ Calidad cambiada a {QUALITY_PRESETS[quality]['name']}")
    await callback_query.message.edit_text(
        f"✅ **Calidad actualizada**\n\n"
        f"Nueva calidad predeterminada: **{QUALITY_PRESETS[quality]['name']}**\n\n"
        f"Todos tus próximos videos se comprimirán con esta calidad.\n"
        f"Usa /quality para cambiarla nuevamente."
    )

@app.on_message(filters.video | filters.document)
async def handle_video(client, message: Message):
    user_id = message.from_user.id
    
    video = message.video or message.document
    
    if not video:
        await message.reply_text("⚠️ Por favor, envía un archivo de video válido.")
        return
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
    file_name = video.file_name or "video.mp4"
    
    if not any(file_name.lower().endswith(ext) for ext in video_extensions):
        await message.reply_text(
            "⚠️ **Formato no soportado**\n\n"
            "Por favor, envía un archivo de video válido.\n"
            "Formatos: MP4, AVI, MOV, MKV, FLV, WMV"
        )
        return
    
    quality = compressor.get_user_quality(user_id)
    queue_position = queue_manager.get_queue_position(user_id)
    
    # Botones para elegir calidad
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("240p 🔥", callback_data=f"video_quality_240p_{message.message_id}"),
            InlineKeyboardButton("360p ⭐", callback_data=f"video_quality_360p_{message.message_id}")
        ],
        [
            InlineKeyboardButton("480p 📺", callback_data=f"video_quality_480p_{message.message_id}"),
            InlineKeyboardButton("720p 🎬", callback_data=f"video_quality_720p_{message.message_id}")
        ],
        [InlineKeyboardButton("Original 📹", callback_data=f"video_quality_original_{message.message_id}")]
    ])
    
    if queue_position > 0:
        await message.reply_text(
            f"📥 **Video recibido (Posición {queue_position + 1} en cola)**\n\n"
            f"Tamaño: **{format_bytes(video.file_size)}**\n"
            f"Calidad predeterminada: **{QUALITY_PRESETS[quality]['name']}**\n\n"
            f"O elige otra calidad:",
            reply_markup=keyboard
        )
    else:
        await message.reply_text(
            f"🎥 **Video recibido**\n\n"
            f"Tamaño: **{format_bytes(video.file_size)}**\n"
            f"Calidad predeterminada: **{QUALITY_PRESETS[quality]['name']}**\n\n"
            f"O elige otra calidad:",
            reply_markup=keyboard
        )
    
    # Usar calidad por defecto si no se elige una
    await queue_manager.add_to_queue(user_id, (message, quality))
    
    if not queue_manager.is_processing(user_id):
        queue_manager.mark_processing(user_id, True)
        asyncio.create_task(process_queue(client, user_id))

@app.on_callback_query(filters.regex("^video_quality_"))
async def video_quality_callback(client, callback_query: CallbackQuery):
    data_parts = callback_query.data.split("_")
    quality = data_parts[2]
    
    await callback_query.answer(f"✅ Procesando con {QUALITY_PRESETS[quality]['name']}")
    
    try:
        await callback_query.message.delete()
    except:
        pass

async def process_queue(client, user_id):
    try:
        while True:
            task_data = await queue_manager.get_next_task(user_id)
            
            if task_data is None:
                break
            
            message, quality = task_data
            await process_video(client, message, quality)
    finally:
        queue_manager.mark_processing(user_id, False)

async def process_video(client, message: Message, quality='360p'):
    user_id = message.from_user.id
    video = message.video or message.document
    
    status_msg = await message.reply_text(
        f"📥 **Descargando video...**\n\n"
        f"Calidad seleccionada: **{QUALITY_PRESETS[quality]['name']}**\n"
        f"Esto puede tomar unos momentos dependiendo del tamaño del archivo."
    )
    
    input_path = None
    output_path = None
    status_msg_ref = [status_msg]
    
    try:
        safe_filename = sanitize_filename(video.file_name)
        input_path = os.path.join(DOWNLOAD_DIR, safe_filename)
        
        last_download_update = [0]
        
        async def download_progress(current, total):
            percentage = (current / total)
            if percentage - last_download_update[0] >= 0.05 or current == total:
                bar = await create_progress_bar(current, total, "📥", "")
                try:
                    await status_msg_ref[0].edit_text(
                        f"📥 **Descargando video...**\n\n"
                        f"{bar}\n"
                        f"{format_bytes(current)} / {format_bytes(total)}"
                    )
                    last_download_update[0] = percentage
                except:
                    pass
        
        await message.download(
            file_name=input_path,
            progress=download_progress,
            block_size=DOWNLOAD_BLOCK_SIZE
        )
        
        # Verify file was downloaded successfully (with robust retry)
        actual_path = await wait_for_file(input_path, timeout=30)
        if actual_path is None:
            raise FileNotFoundError(f"Downloaded file not found after 30 seconds: {input_path}")
        
        input_path = actual_path
        
        if compressor.should_cancel(user_id):
            await status_msg_ref[0].edit_text("❌ **Descarga cancelada por el usuario.**")
            await cleanup_file(input_path)
            compressor.clear_cancel_flag(user_id)
            return
        
        await status_msg_ref[0].edit_text(
            f"⚙️ **Comprimiendo video...**\n\n"
            f"Calidad: **{QUALITY_PRESETS[quality]['name']}**\n"
            f"Procesando con FFmpeg. Esto puede tomar varios minutos."
        )
        
        # Use simple generic name to avoid issues
        output_path = os.path.join(DOWNLOAD_DIR, "video_compressed.mp4")
        
        async def compression_progress(progress):
            try:
                bar = await create_progress_bar(int(progress * 100), 100, "⚙️", "")
                await status_msg_ref[0].edit_text(
                    f"⚙️ **Comprimiendo video...**\n\n"
                    f"{bar}\n"
                    f"Progreso: {progress * 100:.1f}%"
                )
            except Exception as e:
                print(f"Progress update error: {e}")
        
        result = await compressor.compress_video(
            input_path,
            output_path,
            user_id,
            quality,
            compression_progress
        )
        
        if result is None:
            if compressor.should_cancel(user_id):
                await status_msg_ref[0].edit_text("❌ **Compresión cancelada por el usuario.**")
                compressor.clear_cancel_flag(user_id)
            else:
                await status_msg_ref[0].edit_text(
                    "❌ **Error en la compresión**\n\n"
                    "Hubo un problema al comprimir tu video. "
                    "Por favor, intenta con otro archivo."
                )
            await cleanup_file(input_path)
            if output_path and os.path.exists(output_path):
                await cleanup_file(output_path)
            return
        
        await status_msg_ref[0].edit_text(
            "📤 **Subiendo video comprimido...**\n\n"
            "Esto puede tomar unos momentos."
        )
        
        last_upload_update = [0]
        
        async def upload_progress(current, total):
            percentage = (current / total)
            if percentage - last_upload_update[0] >= 0.05 or current == total:
                bar = await create_progress_bar(current, total, "📤", "")
                try:
                    await status_msg_ref[0].edit_text(
                        f"📤 **Subiendo video comprimido...**\n\n"
                        f"{bar}\n"
                        f"{format_bytes(current)} / {format_bytes(total)}"
                    )
                    last_upload_update[0] = percentage
                except:
                    pass
        
        caption = (
            f"✅ **Video comprimido exitosamente**\n\n"
            f"📊 **Estadísticas:**\n"
            f"• Calidad: {result['quality']}\n"
            f"• Tamaño original: {result['original_size_str']}\n"
            f"• Tamaño comprimido: {result['compressed_size_str']}\n"
            f"• Reducción: {result['reduction']:.1f}%\n\n"
            f"🎥 Comprimido por @Compresor_minimisador_bot"
        )
        
        video_duration = result.get('duration')
        video_kwargs = {
            'video': output_path,
            'caption': caption,
            'progress': upload_progress,
            'supports_streaming': True,
            'thumb': None
        }
        if video_duration and video_duration > 0:
            video_kwargs['duration'] = int(video_duration)
        
        await message.reply_video(**video_kwargs)
        
        try:
            await status_msg_ref[0].delete()
        except:
            pass
        
        await cleanup_file(input_path)
        await cleanup_file(output_path)
        
        compressor.clear_cancel_flag(user_id)
        
    except Exception as e:
        print(f"Error processing video: {e}")
        try:
            await status_msg_ref[0].edit_text(
                "❌ **Error inesperado**\n\n"
                f"Ocurrió un error: {str(e)}\n"
                "Por favor, intenta nuevamente."
            )
        except:
            pass
        
        compressor.clear_cancel_flag(user_id)
        
        try:
            if input_path:
                await cleanup_file(input_path)
            if output_path:
                await cleanup_file(output_path)
        except:
            pass

async def health_check(request):
    """Health check endpoint for keep-alive (Render, UptimeRobot, etc)"""
    return web.json_response({
        "status": "ok",
        "bot": "Video Compressor Bot",
        "message": "Bot is running 24/7 ✅"
    })

async def start_web_server():
    """Start aiohttp web server on PORT (for Render) or 8080 (local)"""
    port = int(os.getenv('PORT', 8080))
    web_app = web.Application()
    web_app.router.add_get('/health', health_check)
    web_app.router.add_get('/', health_check)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server started on http://0.0.0.0:{port}")
    return runner

async def main():
    """Main function to run both web server and bot"""
    print("🤖 Starting Telegram Video Compressor Bot...")
    
    # Start web server
    web_runner = await start_web_server()
    
    try:
        # Start bot
        print("✅ Bot is running. Press Ctrl+C to stop.")
        async with app:
            await app.get_me()
            print("🔗 Bot connected to Telegram!")
            await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting bot services...")
    app.run()
