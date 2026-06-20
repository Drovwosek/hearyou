#!/usr/bin/env python3
"""
Audio Preprocessing Module for HearYou STT Service

Applies noise reduction, frequency filtering, and normalization
to improve speech-to-text transcription quality.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional
import tempfile

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """Audio preprocessing for improved STT quality using ffmpeg"""
    
    def __init__(
        self,
        sample_rate: int = 48000,
        channels: int = 1,
        highpass_freq: int = 200,
        lowpass_freq: int = 3000,
        noise_floor: int = -25
    ):
        """
        Initialize audio preprocessor
        
        Args:
            sample_rate: Target sample rate (default 48000)
            channels: Number of channels, 1=mono, 2=stereo (default 1)
            highpass_freq: High-pass filter cutoff in Hz (default 200)
            lowpass_freq: Low-pass filter cutoff in Hz (default 3000)
            noise_floor: Noise reduction floor in dB (default -25)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.highpass_freq = highpass_freq
        self.lowpass_freq = lowpass_freq
        self.noise_floor = noise_floor
        self._verify_ffmpeg()
    
    def _verify_ffmpeg(self) -> None:
        """Verify ffmpeg is installed and accessible"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5,
                check=True
            )
            logger.debug("ffmpeg verification successful")
        except Exception as e:
            logger.error(f"ffmpeg not available: {e}")
            raise RuntimeError(
                "ffmpeg is not installed or not accessible. "
                "Please install: apt-get install -y ffmpeg"
            )
    
    def preprocess(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None
    ) -> str:
        """
        Preprocess audio file for better STT quality
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output file (auto-generated if None)
            sample_rate: Override default sample rate
            channels: Override default channels
            
        Returns:
            Path to processed file (original file if preprocessing fails)
            
        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            logger.error(f"Input file not found: {input_file}")
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            temp_dir = Path(tempfile.gettempdir())
            output_file = str(temp_dir / f"preprocessed_{input_path.stem}.wav")
        
        output_path = Path(output_file)
        target_sample_rate = sample_rate or self.sample_rate
        target_channels = channels or self.channels
        
        logger.info(f"Preprocessing audio: {input_path.name}")
        logger.debug(
            f"Settings: sr={target_sample_rate}, ch={target_channels}, "
            f"hp={self.highpass_freq}Hz, lp={self.lowpass_freq}Hz, nf={self.noise_floor}dB"
        )
        
        # Build ffmpeg command with audio filters
        audio_filters = (
            f"highpass=f={self.highpass_freq},"
            f"lowpass=f={self.lowpass_freq},"
            f"afftdn=nf={self.noise_floor},"
            f"loudnorm"
        )
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', str(input_path),
            '-af', audio_filters,
            '-ar', str(target_sample_rate),
            '-ac', str(target_channels),
            '-c:a', 'pcm_s16le',
            '-y', str(output_path)
        ]
        
        try:
            subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                timeout=300,  # 5 minutes max
                check=True
            )
            
            # Verify output file was created
            if not output_path.exists() or output_path.stat().st_size == 0:
                logger.error("Preprocessing produced empty or missing file")
                return str(input_path)  # Fallback
            
            logger.info(
                f"Preprocessed: {output_path.name} "
                f"({output_path.stat().st_size / (1024*1024):.2f} MB)"
            )
            return str(output_path)
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Preprocessing timeout for {input_path.name}, using original")
            return str(input_path)  # Fallback
            
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else "No error output"
            logger.warning(
                f"Preprocessing failed for {input_path.name}: {stderr[:200]}, using original"
            )
            return str(input_path)  # Fallback
            
        except Exception as e:
            logger.error(f"Unexpected error during preprocessing: {e}, using original")
            return str(input_path)  # Fallback


def preprocess_audio(
    input_file: str,
    output_file: Optional[str] = None,
    sample_rate: int = 48000,
    channels: int = 1
) -> str:
    """
    Preprocess audio file for better STT quality
    
    Convenience wrapper around AudioPreprocessor class.
    
    Args:
        input_file: Path to input audio
        output_file: Path to output (auto if None)
        sample_rate: Target sample rate (default 48000)
        channels: Mono (1) or stereo (2)
    
    Returns:
        Path to processed file (original if preprocessing fails)
    
    Processing steps:
        - Noise reduction (afftdn)
        - High-pass filter (remove low freq noise below 200Hz)
        - Low-pass filter (remove high freq noise above 3000Hz)
        - Loudness normalization
        - Convert to optimal format (WAV PCM 16-bit)
    
    Example:
        >>> processed = preprocess_audio("audio.mp3")
        >>> result = stt.transcribe_sync(processed)
    """
    preprocessor = AudioPreprocessor(sample_rate=sample_rate, channels=channels)
    return preprocessor.preprocess(input_file=input_file, output_file=output_file)
