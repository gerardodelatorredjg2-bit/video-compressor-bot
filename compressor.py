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
        'crf': 28,
        'name': '480p (Compresión media)'
    },
    '720p': {
        'codec': 'libx265',
        'resolution': '1280:720',
        'bitrate': '1800k',
        'crf': 26,
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
            
            # Build FFmpeg command for streaming compression
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vcodec', preset['codec'],
                '-crf', str(preset['crf']),
                '-preset', 'ultrafast',
                '-acodec', 'copy',
                '-movflags', '+faststart',
                '-threads', '0',
                '-g', '250',
                '-x265-params', 'log-level=error',
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
                    line = await asyncio.wait_for(proc.stdout.readline(), timeout=120)
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
                            await progress_callback(progress)
                            last_update = progress
                    except:
                        pass
            
            await proc.wait()
            
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
