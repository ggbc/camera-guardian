"""Captura de vídeo da webcam."""

import cv2
import time
from typing import Optional, Tuple


class WebcamCapture:
    """Captura frames da webcam."""

    def __init__(self, camera_index: int = 0, frame_interval: int = 3):
        """
        Args:
            camera_index: Índice da câmera (0 = padrão)
            frame_interval: Intervalo em segundos entre capturas
        """
        self.camera_index = camera_index
        self.frame_interval = frame_interval
        self.cap = None
        self.last_frame_time = 0
        self.frame_count = 0

    def connect(self) -> bool:
        """Conecta à webcam."""
        try:
            print(f"📷 Conectando à webcam {self.camera_index}...")
            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                print("❌ Falha ao abrir webcam")
                return False

            print("✓ Webcam conectada")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False

    def get_frame(self) -> Optional[Tuple[bool, bytes]]:
        """
        Captura um frame respeitando intervalo.

        Returns:
            (sucesso, frame_bytes) ou (False, None) ou (None, None) se intervalo não atingido
        """
        if self.cap is None:
            return False, None

        # Respeita intervalo
        now = time.time()
        if now - self.last_frame_time < self.frame_interval:
            return None, None

        try:
            ret, frame = self.cap.read()

            if not ret:
                print("⚠️ Falha ao capturar frame")
                return False, None

            self.last_frame_time = now
            self.frame_count += 1

            # Codifica pra JPEG
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            frame_bytes = buffer.tobytes()

            return True, frame_bytes

        except Exception as e:
            print(f"❌ Erro ao capturar: {e}")
            return False, None

    def disconnect(self):
        """Desconecta da webcam."""
        if self.cap:
            self.cap.release()
            print("✓ Webcam desconectada")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()