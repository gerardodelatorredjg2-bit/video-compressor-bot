import os
import asyncio
import ffmpeg
from utils import get_file_size, format_bytes

class VideoCompressor:
    def __init__(self):
        self.cancel_flag = {}
    
    def set_cancel_flag(self, user_id, value=True):
        self.cancel_flag[user_id] = value
    
    def should_cancel(self, user_id):
        return self.cancel_flag.get(user_id, False)
    
    def clear_cancel_flag(self, user_id):
        if user_id in self.cancel_flag:
            del self.cancel_flag[user_id]
    
    async def compress_video(self, input_path, output_path, user_id, progress_callback=None):
        try:
            if self.should_cancel(user_id):
                return None
            
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
            
            process = (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    crf=28,
                    preset='medium',
                    acodec='aac',
                    audio_bitrate='128k',
                    vf='scale=trunc(iw/2)*2:trunc(ih/2)*2'
                )
                .global_args('-progress', 'pipe:1')
                .overwrite_output()
            )
            
            cmd = process.compile()
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
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
                        
                        if progress_callback:
                            await progress_callback(progress)
                    except:
                        pass
            
            await proc.wait()
            
            if proc.returncode == 0 and os.path.exists(output_path):
                original_size = get_file_size(input_path)
                compressed_size = get_file_size(output_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                return {
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction': reduction,
                    'original_size_str': format_bytes(original_size),
                    'compressed_size_str': format_bytes(compressed_size)
                }
            else:
                return None
                
        except Exception as e:
            print(f"Compression error: {e}")
            return None

compressor = VideoCompressor()
