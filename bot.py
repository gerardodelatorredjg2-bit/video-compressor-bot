import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_TOKEN, API_ID, API_HASH, DOWNLOAD_DIR
from compressor import compressor
from queue_manager import queue_manager
from utils import format_bytes, cleanup_file, generate_filename, create_progress_bar

app = Client(
    "video_compressor_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_messages = {}

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    welcome_text = (
        "🎥 **Bienvenido al Compresor de Video**\n\n"
        "Envíame un video y lo comprimiré para reducir su tamaño.\n\n"
        "**Características:**\n"
        "✅ Compresión de alta calidad\n"
        "✅ Soporte para archivos grandes (+50 MB)\n"
        "✅ Barra de progreso en tiempo real\n"
        "✅ Sistema de cola inteligente\n"
        "✅ Cancelación de operaciones\n\n"
        "**Comandos:**\n"
        "/start - Mostrar este mensaje\n"
        "/help - Ayuda detallada\n"
        "/cancel - Cancelar compresión actual\n\n"
        "¡Envía un video para comenzar!"
    )
    await message.reply_text(welcome_text)

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = (
        "📚 **Ayuda del Bot Compresor**\n\n"
        "**Cómo usar:**\n"
        "1. Envía un archivo de video\n"
        "2. Espera mientras se comprime\n"
        "3. Recibe tu video comprimido\n\n"
        "**Formatos soportados:**\n"
        "MP4, AVI, MOV, MKV, FLV, WMV\n\n"
        "**Características avanzadas:**\n"
        "• Si envías múltiples videos, se procesarán en cola\n"
        "• Puedes cancelar con /cancel en cualquier momento\n"
        "• La barra de progreso se actualiza en tiempo real\n"
        "• Recibirás un reporte de reducción de tamaño\n\n"
        "**Nota:** El bot usa compresión H.264 optimizada para mantener la mejor calidad posible."
    )
    await message.reply_text(help_text)

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
    
    queue_position = queue_manager.get_queue_position(user_id)
    
    if queue_position > 0:
        await message.reply_text(
            f"📥 **Video agregado a la cola**\n\n"
            f"Posición en cola: **{queue_position + 1}**\n"
            f"Tu video será procesado pronto."
        )
    
    await queue_manager.add_to_queue(user_id, message)
    
    if not queue_manager.is_processing(user_id):
        asyncio.create_task(process_queue(client, user_id))

async def process_queue(client, user_id):
    queue_manager.mark_processing(user_id, True)
    
    while True:
        task_message = await queue_manager.get_next_task(user_id)
        
        if task_message is None:
            break
        
        await process_video(client, task_message)
    
    queue_manager.mark_processing(user_id, False)

async def process_video(client, message: Message):
    user_id = message.from_user.id
    video = message.video or message.document
    
    status_msg = await message.reply_text(
        "📥 **Descargando video...**\n\n"
        "Esto puede tomar unos momentos dependiendo del tamaño del archivo."
    )
    
    try:
        input_path = os.path.join(DOWNLOAD_DIR, f"{user_id}_{video.file_unique_id}_{video.file_name}")
        
        async def download_progress(current, total):
            if current % (total // 10 + 1) < 50000 or current == total:
                percentage = (current / total) * 100
                bar = await create_progress_bar(current, total, "📥", "")
                await status_msg.edit_text(
                    f"📥 **Descargando video...**\n\n"
                    f"{bar}\n"
                    f"{format_bytes(current)} / {format_bytes(total)}"
                )
        
        await message.download(
            file_name=input_path,
            progress=download_progress
        )
        
        user_messages[user_id] = status_msg
        
        await status_msg.edit_text(
            "⚙️ **Comprimiendo video...**\n\n"
            "Procesando con FFmpeg. Esto puede tomar varios minutos."
        )
        
        output_path = os.path.join(
            DOWNLOAD_DIR,
            generate_filename(video.file_name, "_compressed")
        )
        
        async def compression_progress(progress):
            if user_id in user_messages:
                try:
                    bar = await create_progress_bar(progress, 1.0, "⚙️", "")
                    await user_messages[user_id].edit_text(
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
            compression_progress
        )
        
        if result is None:
            if compressor.should_cancel(user_id):
                await status_msg.edit_text("❌ **Compresión cancelada por el usuario.**")
            else:
                await status_msg.edit_text(
                    "❌ **Error en la compresión**\n\n"
                    "Hubo un problema al comprimir tu video. "
                    "Por favor, intenta con otro archivo."
                )
            await cleanup_file(input_path)
            return
        
        await status_msg.edit_text(
            "📤 **Subiendo video comprimido...**\n\n"
            "Esto puede tomar unos momentos."
        )
        
        async def upload_progress(current, total):
            if current % (total // 10 + 1) < 50000 or current == total:
                percentage = (current / total) * 100
                bar = await create_progress_bar(current, total, "📤", "")
                await status_msg.edit_text(
                    f"📤 **Subiendo video comprimido...**\n\n"
                    f"{bar}\n"
                    f"{format_bytes(current)} / {format_bytes(total)}"
                )
        
        caption = (
            f"✅ **Video comprimido exitosamente**\n\n"
            f"📊 **Estadísticas:**\n"
            f"• Tamaño original: {result['original_size_str']}\n"
            f"• Tamaño comprimido: {result['compressed_size_str']}\n"
            f"• Reducción: {result['reduction']:.1f}%\n\n"
            f"🎥 Comprimido por @Compresor_minimisador_bot"
        )
        
        await message.reply_video(
            video=output_path,
            caption=caption,
            progress=upload_progress
        )
        
        await status_msg.delete()
        
        await cleanup_file(input_path)
        await cleanup_file(output_path)
        
        if user_id in user_messages:
            del user_messages[user_id]
        
        compressor.clear_cancel_flag(user_id)
        
    except Exception as e:
        print(f"Error processing video: {e}")
        await status_msg.edit_text(
            "❌ **Error inesperado**\n\n"
            f"Ocurrió un error: {str(e)}\n"
            "Por favor, intenta nuevamente."
        )
        
        try:
            await cleanup_file(input_path)
            if 'output_path' in locals():
                await cleanup_file(output_path)
        except:
            pass

if __name__ == "__main__":
    print("🤖 Starting Telegram Video Compressor Bot...")
    print("✅ Bot is running. Press Ctrl+C to stop.")
    app.run()
