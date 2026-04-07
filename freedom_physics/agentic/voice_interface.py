"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/voice_interface.py — STT (Whisper) + TTS (ElevenLabs).
All providers from cfg.voice. Mock mode for testing.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


class VoiceInterface:
    def __init__(self, mock: bool = False):
        self.mock         = mock
        self.tts_provider = str(cfg.voice.tts_provider)
        self.stt_provider = str(cfg.voice.stt_provider)
        self.language     = str(cfg.voice.language)
        self.max_words    = int(cfg.voice.max_response_words)

    def stt_mock(self, audio_data) -> str:
        return "Build me a house with Carbon, Silicon, and Aluminum."

    def tts_mock(self, text: str, language: str = None) -> bytes:
        lang = language or self.language
        return f"[MOCK_AUDIO:{lang}:{text[:30]}]".encode()

    def transcribe(self, audio_data) -> str:
        if self.mock: return self.stt_mock(audio_data)
        raise NotImplementedError("Whisper STT requires live API key")

    def speak(self, text: str, language: str = None) -> bytes:
        if self.mock: return self.tts_mock(text, language)
        raise NotImplementedError("ElevenLabs TTS requires live API key")
