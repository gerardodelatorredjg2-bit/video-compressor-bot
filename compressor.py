import os
import asyncio
import subprocess
import json
from utils import get_file_size, format_bytes

QUALITY_PRESETS = {
    '240p': {
        'codec': 'libx265',
        'resolution': '426:240',
        'bitrate': '250k',
        'crf': 32,
        'name': '240p (Máxima compresión)'
    },
    '360p': {
        'codec': 'libx265',
        'resolution': '640:360',
        'bitrate': '500k',
        'crf': 30,
        'name': '360p (Alta compresión) ⭐'
    },
    '480p': {
        'codec': 'libx265',
        'resolution': '854:480',
        'bitrate': '900k',
        'crf': 26,
        'name': '480p (Compresión media)'
    },
    '720p': {
        'codec': 'libx265',
        'resolution': '1280:720',
        'bitrate': '1800k',
        'crf': 24,
        'name': '720p (Buena calidad)'
    },
    'original': {
        'codec': 'libx265',
        'resolution': None,
        'bitrate': None,
        'crf': 30,
        'name': 'Original (Máxima velocidad)'
    }
}

class VideoCompressor:
    def __init__(self):
        self.cancel_flag = {}
        self.user_quality = {}
    
    def set_cancel_flag(self, user_id, value=True):
        self.cancel_flag[user_id] = value
    
    def should_cancel(self, user_id):
        return self.cancel_flag.get(user_id, False)
    
    def clear_cancel_flag(self, user_id):
        if user_id in self.cancel_flag:
            del self.cancel_flag[user_id]
    
    def set_user_quality(self, user_id, quality):
        self.user_quality[user_id] = quality
    
    def get_user_quality(self, user_id):
        return self.user_quality.get(user_id, '360p')
    
    async def compress_video(self, input_path, output_path, user_id, quality='360p', progress_callback=None):
        try:
            if self.should_cancel(user_id):
                return None
            
            # Get original file size first (before any processing)
            original_size = get_file_size(input_path)
            
            try:
                result = await asyncio.create_subprocess_exec(
                    'ffprobe', '-v', 'error', '-show_format', '-of', 'json', input_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await result.communicate()
                probe = json.loads(stdout)
                duration = float(probe['format'].get('duration', 0))
                if duration <= 0:
                    duration = 1
            except Exception as e:
                print(f"Error probing video: {e}")
                duration = 1
            
            preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS['360p'])
            
            # Build FFmpeg command - VELOCIDAD MÁXIMA con calidad aceptable
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vcodec', preset['codec'],
                '-crf', str(preset['crf']),
                '-preset', 'ultrafast',
                '-acodec', 'copy',
                '-threads', '0',
                '-g', '30',
                '-x265-params', 'log-level=error:aq-mode=0',
            ]
            
            if preset['resolution']:
                cmd.extend(['-vf', f"scale={preset['resolution']}:flags=fast_bilinear"])
            else:
                cmd.extend(['-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=fast_bilinear'])
            
            if preset['bitrate']:
                cmd.extend(['-b:v', preset['bitrate']])
            
            cmd.extend([
                '-progress', 'pipe:1',
                '-y',
                '-loglevel', 'error',
                output_path
            ])
            
            # Use subprocess for better control on large files
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            last_update = 0
            start_time = asyncio.get_event_loop().time()
            while True:
                if self.should_cancel(user_id):
                    proc.kill()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=2)
                    except:
                        pass
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    return None
                
                try:
                    line = await asyncio.wait_for(proc.stdout.readline(), timeout=300)
                except asyncio.TimeoutError:
                    print("Compression timeout - killing process")
                    proc.kill()
                    return None
                    
                if not line:
                    break
                
                try:
                    line = line.decode('utf-8').strip()
                except:
                    continue
                
                if line.startswith('out_time_ms='):
                    try:
                        time_ms = int(line.split('=')[1])
                        time_s = time_ms / 1000000.0
                        progress = min(time_s / duration, 1.0)
                        
                        if progress_callback and (progress - last_update >= 0.02 or progress >= 0.99):
                            current_time = asyncio.get_event_loop().time()
                            elapsed = int(current_time - start_time)
                            current_size = get_file_size(output_path) if os.path.exists(output_path) else 0
                            
                            # Calcular velocidad de compresión
                            speed_mbs = (current_size / (1024 * 1024)) / max(elapsed, 1) if elapsed > 0 else 0
                            
                            # Mostrar en consola
                            print(f"🎬 Comprimiendo... {progress*100:.1f}% | ⏱️ {elapsed}s | 🎛️ {speed_mbs:.2f} MB/s | 📦 {format_bytes(current_size)}")
                            
                            await progress_callback(progress, elapsed, current_size)
                            last_update = progress
                    except:
                        pass
            
            await proc.wait()
            
            # Log final de compresión
            final_time = asyncio.get_event_loop().time() - start_time
            if os.path.exists(output_path):
                final_size = get_file_size(output_path)
                final_speed = (final_size / (1024 * 1024)) / max(final_time, 1)
                print(f"✅ Compresión completada | ⏱️ {int(final_time)}s | 🎛️ {final_speed:.2f} MB/s | 📦 {format_bytes(final_size)}")
            
            if proc.returncode == 0 and os.path.exists(output_path):
                out_duration = 0
                try:
                    result = await asyncio.create_subprocess_exec(
                        'ffprobe', '-v', 'error', '-show_format', '-of', 'json', output_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, _ = await result.communicate()
                    probe_out = json.loads(stdout)
                    out_duration = float(probe_out['format'].get('duration', 0))
                except:
                    out_duration = 0
                
                compressed_size = get_file_size(output_path)
                reduction = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0
                
                return {
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction': reduction,
                    'original_size_str': format_bytes(original_size),
                    'compressed_size_str': format_bytes(compressed_size),
                    'duration': out_duration,
                    'quality': preset['name']
                }
            else:
                return None
                
        except Exception as e:
            print(f"Compression error: {e}")
            return None

compressor = VideoCompressor()
