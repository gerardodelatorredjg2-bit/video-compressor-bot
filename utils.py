import os
import asyncio
import aiofiles
from datetime import datetime

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def get_file_size(file_path):
    return os.path.getsize(file_path)

async def cleanup_file(file_path):
    try:
        if os.path.exists(file_path):
            await asyncio.sleep(1)
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error cleaning up {file_path}: {e}")
    return False

def generate_filename(original_name, suffix="_compressed"):
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}{suffix}_{timestamp}{ext}"

async def create_progress_bar(current, total, prefix="", suffix="", length=20):
    percent = current / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '░' * (length - filled_length)
    percent_display = percent * 100
    return f"{prefix} |{bar}| {percent_display:.1f}% {suffix}"
