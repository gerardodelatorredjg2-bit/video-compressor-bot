import os
import asyncio
import aiofiles
import glob
from datetime import datetime

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def get_file_size(file_path):
    return os.path.getsize(file_path)

async def wait_for_file(file_path, timeout=30, check_interval=0.5):
    """
    Robustly wait for a file to exist, handling .temp file renames
    Returns the actual path to the file, or None if timeout
    """
    start_time = asyncio.get_event_loop().time()
    base_path = file_path.rstrip('.temp')
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        # Check main path
        if os.path.exists(base_path):
            return base_path
        
        # Check .temp path
        temp_path = base_path + ".temp"
        if os.path.exists(temp_path):
            try:
                os.rename(temp_path, base_path)
                return base_path
            except:
                await asyncio.sleep(check_interval)
                continue
        
        await asyncio.sleep(check_interval)
    
    # Last attempt: search for partial matches
    dir_path = os.path.dirname(base_path) or "."
    base_name = os.path.basename(base_path)
    
    for file in glob.glob(os.path.join(dir_path, f"*{base_name}*")):
        if not file.endswith('.temp'):
            return file
    
    return None

async def cleanup_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        # Also try to clean up .temp files
        temp_path = file_path + ".temp"
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as e:
        print(f"Error cleaning up {file_path}: {e}")
    return False

def sanitize_filename(filename):
    if not filename:
        return "video.mp4"
    
    base = os.path.basename(filename)
    base = base.replace('..', '')
    base = ''.join(c for c in base if c.isalnum() or c in '._- ')
    
    if not base or base.startswith('.'):
        return "video.mp4"
    
    return base[:255]

def generate_filename(original_name, suffix="_compressed"):
    sanitized = sanitize_filename(original_name)
    name, ext = os.path.splitext(sanitized)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}{suffix}_{timestamp}{ext}"

async def create_progress_bar(current, total, prefix="", suffix="", length=20):
    percent = current / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '░' * (length - filled_length)
    percent_display = percent * 100
    return f"{prefix} |{bar}| {percent_display:.1f}% {suffix}"
