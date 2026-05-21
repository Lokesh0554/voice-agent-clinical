"""Language detection module."""
import logging
from typing import Tuple, Optional
import asyncio


logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect language from text."""

    def __init__(self):
        """Initialize language detector."""
        try:
            from langdetect import detect, detect_langs
            self.detect = detect
            self.detect_langs = detect_langs
            self.available = True
            logger.info("Language detector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize language detector: {e}")
            self.available = False

    async def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text.
        
        Returns:
            Tuple of (language_code, confidence)
        """
        if not self.available or not text:
            return "en", 0.0

        try:
            # Run detection in executor to avoid blocking
            result = await asyncio.get_running_loop().run_in_executor(
                None,
                self._detect,
                text
            )
            
            if result:
                lang_code, confidence = result
                # Map full locale codes to simple language codes
                lang_code = lang_code.split('-')[0] if '-' in lang_code else lang_code
                logger.debug(f"Detected language: {lang_code} (confidence: {confidence})")
                return lang_code, confidence
            
            return "en", 0.0
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en", 0.0

    def _detect(self, text: str) -> Optional[Tuple[str, float]]:
        """Synchronous language detection."""
        try:
            lang = self.detect(text)
            langs = self.detect_langs(text)
            
            # Get confidence for detected language
            confidence = 0.0
            for lang_prob in langs:
                if str(lang_prob).startswith(lang):
                    confidence = lang_prob.prob
                    break
            
            return lang, confidence
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return None

    async def identify_language_from_audio(self, transcript: str) -> str:
        """Identify language from audio transcript."""
        lang_code, confidence = await self.detect_language(transcript)
        
        # Map language codes to our supported languages
        lang_map = {
            'en': 'en',
            'hi': 'hi',
            'ta': 'ta',
            'ur': 'hi',  # Map Urdu to Hindi
            'gu': 'hi',  # Map Gujarati to Hindi
        }
        
        return lang_map.get(lang_code, 'en')


# Global language detector instance
language_detector = LanguageDetector()


def get_language_detector() -> LanguageDetector:
    """Get language detector instance."""
    return language_detector
