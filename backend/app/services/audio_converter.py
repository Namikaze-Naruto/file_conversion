from pydub import AudioSegment
from gtts import gTTS
import speech_recognition as sr
import os
from typing import Optional

# Optional dependency
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

class AudioConverter:
    """Handles all audio format conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        # Normalize formats
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        # Route to appropriate converter
        conversion_key = f"{source_format}_to_{target_format}"
        
        # Check for special conversions
        if source_format == 'txt' and target_format in ('mp3', 'wav'):
            return await AudioConverter.text_to_speech(input_path, output_path, target_format)
        
        if source_format in ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'webm'):
            return await AudioConverter.video_to_audio(input_path, output_path, target_format)
        
        # Standard audio format conversions
        return await AudioConverter.convert_audio_format(input_path, output_path, source_format, target_format)
    
    @staticmethod
    async def convert_audio_format(input_path: str, output_path: str, 
                                   source_format: str, target_format: str) -> str:
        """Convert between audio formats using pydub"""
        
        # Load audio file
        audio = AudioSegment.from_file(input_path, format=source_format)
        
        # Set export parameters based on target format
        export_params = {
            'format': target_format
        }
        
        # Quality settings
        if target_format == 'mp3':
            export_params['bitrate'] = '320k'
        elif target_format == 'wav':
            export_params['parameters'] = ['-ar', '44100']
        elif target_format == 'flac':
            export_params['parameters'] = ['-ar', '44100', '-sample_fmt', 's16']
        elif target_format == 'ogg':
            export_params['parameters'] = ['-q:a', '10']
        
        # Export audio
        audio.export(output_path, **export_params)
        
        return output_path
    
    @staticmethod
    async def text_to_speech(input_path: str, output_path: str, target_format: str = 'mp3') -> str:
        """Convert text file to speech using gTTS"""
        
        # Read text from file
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            raise ValueError("Input text file is empty")
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save as MP3 first (gTTS only supports MP3)
        temp_mp3 = output_path.replace(f'.{target_format}', '_temp.mp3')
        tts.save(temp_mp3)
        
        # Convert to target format if not MP3
        if target_format.lower() != 'mp3':
            audio = AudioSegment.from_mp3(temp_mp3)
            audio.export(output_path, format=target_format)
            os.remove(temp_mp3)
        else:
            os.rename(temp_mp3, output_path)
        
        return output_path
    
    @staticmethod
    async def audio_to_text(input_path: str, output_path: str) -> str:
        """Convert audio to text using speech recognition"""
        
        recognizer = sr.Recognizer()
        
        # Convert to WAV if not already
        audio_format = os.path.splitext(input_path)[1].lower().replace('.', '')
        wav_path = input_path
        
        if audio_format != 'wav':
            audio = AudioSegment.from_file(input_path, format=audio_format)
            wav_path = input_path.replace(f'.{audio_format}', '_temp.wav')
            audio.export(wav_path, format='wav')
        
        try:
            # Recognize speech
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
            
            # Save to text file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return output_path
            
        finally:
            # Cleanup temp file
            if wav_path != input_path and os.path.exists(wav_path):
                os.remove(wav_path)
    
    @staticmethod
    async def video_to_audio(input_path: str, output_path: str, target_format: str = 'mp3') -> str:
        """Extract audio from video file"""
        if not MOVIEPY_AVAILABLE:
            raise NotImplementedError("Video to audio conversion requires moviepy library")
        
        video = VideoFileClip(input_path)
        audio = video.audio
        
        if audio is None:
            raise ValueError("Video file has no audio track")
        
        # Export audio
        if target_format == 'mp3':
            audio.write_audiofile(output_path, codec='libmp3lame', bitrate='320k', logger=None)
        elif target_format == 'wav':
            audio.write_audiofile(output_path, codec='pcm_s16le', logger=None)
        else:
            audio.write_audiofile(output_path, logger=None)
        
        video.close()
        
        return output_path
    
    @staticmethod
    async def mp3_to_wav(input_path: str, output_path: str) -> str:
        """Convert MP3 to WAV"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'mp3', 'wav')
    
    @staticmethod
    async def wav_to_mp3(input_path: str, output_path: str) -> str:
        """Convert WAV to MP3"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'wav', 'mp3')
    
    @staticmethod
    async def mp3_to_aac(input_path: str, output_path: str) -> str:
        """Convert MP3 to AAC"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'mp3', 'aac')
    
    @staticmethod
    async def mp3_to_ogg(input_path: str, output_path: str) -> str:
        """Convert MP3 to OGG"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'mp3', 'ogg')
    
    @staticmethod
    async def flac_to_mp3(input_path: str, output_path: str) -> str:
        """Convert FLAC to MP3"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'flac', 'mp3')
    
    @staticmethod
    async def m4a_to_mp3(input_path: str, output_path: str) -> str:
        """Convert M4A to MP3"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'm4a', 'mp3')
    
    @staticmethod
    async def wav_to_flac(input_path: str, output_path: str) -> str:
        """Convert WAV to FLAC"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'wav', 'flac')
    
    @staticmethod
    async def opus_to_mp3(input_path: str, output_path: str) -> str:
        """Convert OPUS to MP3"""
        return await AudioConverter.convert_audio_format(input_path, output_path, 'opus', 'mp3')
