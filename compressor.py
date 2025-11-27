import os
import asyncio
import ffmpeg
from utils import get_file_size, format_bytes

QUALITY_PRESETS = {
    '240p': {
        'resolution': '426:240',
        'bitrate': '300k',
        'crf': 40,
        'name': '240p (Máxima compresión)'
    },
    '360p': {
        'resolution': '640:360',
        'bitrate': '600k',
        'crf': 38,
        'name': '360p (Alta compresión)'
    },
    '480p': {
        'resolution': '854:480',
        'bitrate': '1000k',
        'crf': 36,
        'name': '480p (Compresión media)'
    },
    '720p': {
        'resolution': '1280:720',
        'bitrate': '2000k',
        'crf': 34,
        'name': '720p (Buena calidad)'
    },
    'original': {
        'resolution': None,
        'bitrate': None,
        'crf': 38,
        'name': 'Original (Solo codec)'
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
            
            try:
                probe = ffmpeg.probe(input_path)
                duration = float(probe['format'].get('duration', 0))
                if duration <= 0:
                    duration = 1
            except Exception as e:
                print(f"Error probing video: {e}")
                duration = 1
            
            preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS['360p'])
            
            output_args = {
                'vcodec': 'libx264',
                'crf': preset['crf'],
                'preset': 'ultrafast',
                'acodec': 'copy',
                'movflags': '+faststart',
                'threads': 0,
                'g': '250'
            }
            
            if preset['resolution']:
                output_args['vf'] = f"scale={preset['resolution']}:flags=fast_bilinear"
            else:
                output_args['vf'] = 'scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=fast_bilinear'
            
            if preset['bitrate']:
                output_args['video_bitrate'] = preset['bitrate']
            
            process = (
                ffmpeg
                .input(input_path)
                .output(output_path, **output_args)
                .global_args('-progress', 'pipe:1', '-y', '-loglevel', 'error')
            )
            
            cmd = process.compile()
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            last_update = 0
            while True:
                if self.should_cancel(user_id):
                    proc.kill()
                    await proc.wait()
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return None
                
                line = await proc.stdout.readline()
                if not line:
                    break
                
                line = line.decode('utf-8').strip()
                
                if line.startswith('out_time_ms='):
                    try:
                        time_ms = int(line.split('=')[1])
                        time_s = time_ms / 1000000.0
                        progress = min(time_s / duration, 1.0)
                        
                        if progress_callback and (progress - last_update >= 0.01 or progress >= 0.99):
                            await progress_callback(progress)
                            last_update = progress
                    except:
                        pass
            
            await proc.wait()
            
            if proc.returncode == 0 and os.path.exists(output_path):
                try:
                    probe_out = ffmpeg.probe(output_path)
                    out_duration = float(probe_out['format'].get('duration', 0))
                except:
                    out_duration = 0
                
                original_size = get_file_size(input_path)
                compressed_size = get_file_size(output_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
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
