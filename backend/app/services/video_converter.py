import cv2
import os
from typing import List
import numpy as np

# Optional dependency
try:
    from moviepy.editor import VideoFileClip, ImageSequenceClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

class VideoConverter:
    """Handles all video format conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        if not MOVIEPY_AVAILABLE:
            raise NotImplementedError("Video conversion requires moviepy library. Install with: pip install moviepy")
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        # Check for special conversions
        if target_format == 'gif':
            return await VideoConverter.video_to_gif(input_path, output_path)
        elif target_format in ('mp3', 'wav', 'aac'):
            return await VideoConverter.video_to_audio(input_path, output_path, target_format)
        elif target_format in ('png', 'jpg', 'jpeg'):
            return await VideoConverter.video_to_frames(input_path, output_path, target_format)
        else:
            return await VideoConverter.convert_video_format(input_path, output_path, target_format)
    
    @staticmethod
    async def convert_video_format(input_path: str, output_path: str, target_format: str) -> str:
        """Convert between video formats"""
        
        video = VideoFileClip(input_path)
        
        # Set codec based on format
        codec_map = {
            'mp4': 'libx264',
            'mkv': 'libx264',
            'avi': 'libxvid',
            'webm': 'libvpx',
            'mov': 'libx264',
            'flv': 'flv',
            'wmv': 'wmv2'
        }
        
        codec = codec_map.get(target_format, 'libx264')
        
        # Write video file
        video.write_videofile(
            output_path,
            codec=codec,
            audio_codec='aac',
            logger=None
        )
        
        video.close()
        return output_path
    
    @staticmethod
    async def video_to_gif(input_path: str, output_path: str, 
                          fps: int = 10, scale: float = 0.5) -> str:
        """Convert video to GIF"""
        
        video = VideoFileClip(input_path)
        
        # Reduce size and fps for reasonable GIF size
        if scale != 1.0:
            video = video.resize(scale)
        
        video.write_gif(output_path, fps=fps, logger=None)
        video.close()
        
        return output_path
    
    @staticmethod
    async def video_to_audio(input_path: str, output_path: str, audio_format: str = 'mp3') -> str:
        """Extract audio from video"""
        
        video = VideoFileClip(input_path)
        audio = video.audio
        
        if audio is None:
            raise ValueError("Video file has no audio track")
        
        if audio_format == 'mp3':
            audio.write_audiofile(output_path, codec='libmp3lame', bitrate='320k', logger=None)
        elif audio_format == 'wav':
            audio.write_audiofile(output_path, codec='pcm_s16le', logger=None)
        else:
            audio.write_audiofile(output_path, logger=None)
        
        video.close()
        return output_path
    
    @staticmethod
    async def video_to_frames(input_path: str, output_path: str, 
                             image_format: str = 'png', fps: float = 1.0) -> str:
        """Extract frames from video as images"""
        
        # Create output directory for frames
        frames_dir = output_path.replace(f'.{image_format}', '_frames')
        os.makedirs(frames_dir, exist_ok=True)
        
        video = VideoFileClip(input_path)
        frame_count = 0
        
        # Extract frames at specified fps
        for t in np.arange(0, video.duration, 1.0/fps):
            frame = video.get_frame(t)
            frame_path = os.path.join(frames_dir, f'frame_{frame_count:04d}.{image_format}')
            
            # Save frame using cv2
            if image_format.lower() in ('jpg', 'jpeg'):
                cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), 
                          [cv2.IMWRITE_JPEG_QUALITY, 95])
            else:
                cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            frame_count += 1
        
        video.close()
        
        # Return the directory path
        return frames_dir
    
    @staticmethod
    async def mp4_to_mkv(input_path: str, output_path: str) -> str:
        """Convert MP4 to MKV"""
        return await VideoConverter.convert_video_format(input_path, output_path, 'mkv')
    
    @staticmethod
    async def mp4_to_avi(input_path: str, output_path: str) -> str:
        """Convert MP4 to AVI"""
        return await VideoConverter.convert_video_format(input_path, output_path, 'avi')
    
    @staticmethod
    async def mov_to_mp4(input_path: str, output_path: str) -> str:
        """Convert MOV to MP4"""
        return await VideoConverter.convert_video_format(input_path, output_path, 'mp4')
    
    @staticmethod
    async def flv_to_mp4(input_path: str, output_path: str) -> str:
        """Convert FLV to MP4"""
        return await VideoConverter.convert_video_format(input_path, output_path, 'mp4')
    
    @staticmethod
    async def wmv_to_mp4(input_path: str, output_path: str) -> str:
        """Convert WMV to MP4"""
        return await VideoConverter.convert_video_format(input_path, output_path, 'mp4')
    
    @staticmethod
    async def webm_to_mp4(input_path: str, output_path: str) -> str:
        """Convert WebM to MP4"""
        return await VideoConverter.convert_video_format(input_path, output_path, 'mp4')
