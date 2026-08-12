#!/usr/bin/env python3
"""
Camera Guardian - Motion Detection System
Monitora webcam 24/7 e alerta quando detecta pessoas.
"""

import time
import base64
import requests
from datetime import datetime
from typing import List, Dict

from camera import WebcamCapture
from storage import Database, Detection

import os
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Configuração via variáveis de ambiente
API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
PROJECT_ID = os.getenv("ROBOFLOW_PROJECT_ID", "")
MODEL_VERSION = int(os.getenv("ROBOFLOW_MODEL_VERSION", "2"))
FRAME_INTERVAL = int(os.getenv("FRAME_INTERVAL", "1"))
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "30"))

""" API_KEY = "YHhYv8VymcHjYEUcjdWS"  # Sua private API key
PROJECT_ID = "detect-people-wqfy8"
MODEL_VERSION = 2

FRAME_INTERVAL = 1  # Segundos entre frames
ALERT_COOLDOWN = 30  # Segundos entre alertas da mesma classe """
TARGET_CLASSES = ["person"]  # Classes a monitorar

# Valida configuração
if not API_KEY or not PROJECT_ID:
    print("❌ ERRO: Configure ROBOFLOW_API_KEY e ROBOFLOW_PROJECT_ID no .env")
    exit(1)

class CameraGuardian:
    """Sistema de monitoramento."""

    def __init__(self):
        self.camera = WebcamCapture(frame_interval=FRAME_INTERVAL)
        self.db = Database()
        self.last_alert_time: Dict[str, float] = {}
        self.frame_count = 0
        self.detection_count = 0

    def detect(self, image_bytes: bytes) -> List[Dict]:
        """Chama Roboflow API e retorna detecções."""
        try:
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            url = f"https://detect.roboflow.com/{PROJECT_ID}/{MODEL_VERSION}"
            response = requests.post(
                url,
                data=image_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                params={"api_key": API_KEY},
                timeout=10,
            )

            if response.status_code != 200:
                print(f"⚠️ API error: {response.status_code}")
                return []

            data = response.json()
            predictions = data.get("predictions", [])

            # Filtra por classe e confiança
            detections = []
            for pred in predictions:
                class_name = pred.get("class", "unknown")
                confidence = pred.get("confidence", 0)

                if class_name in TARGET_CLASSES and confidence > 0.5:
                    detections.append({
                        "class": class_name,
                        "confidence": confidence
                    })

            return detections

        except Exception as e:
            print(f"❌ Erro na detecção: {e}")
            return []

    def should_alert(self, class_name: str) -> bool:
        """Verifica se deve enviar alerta (respeitando cooldown)."""
        now = time.time()
        last_alert = self.last_alert_time.get(class_name, 0)

        if now - last_alert >= ALERT_COOLDOWN:
            self.last_alert_time[class_name] = now
            return True

        return False

    def run(self):
        """Loop principal."""
        print("\n" + "=" * 60)
        print("🎥 CAMERA GUARDIAN - 24/7 MONITORING")
        print("=" * 60)
        print(f"Project: {PROJECT_ID}")
        print(f"Model Version: {MODEL_VERSION}")
        print(f"Frame Interval: {FRAME_INTERVAL}s")
        print(f"Alert Cooldown: {ALERT_COOLDOWN}s")
        print(f"Monitoring: {', '.join(TARGET_CLASSES)}")
        print("=" * 60 + "\n")

        if not self.camera.connect():
            print("❌ Falha ao conectar à câmera")
            return False

        try:
            while True:
                # Captura frame
                success, frame_bytes = self.camera.get_frame()

                if success is None:
                    # Intervalo ainda não atingido
                    print(f"Frame {self.frame_count}: {len(detections)} detecções")                    
                    time.sleep(0.1)
                    continue

                if not success:
                    print("⚠️ Erro ao capturar frame")
                    time.sleep(1)
                    continue

                self.frame_count += 1

                # Detecta
                detections = self.detect(frame_bytes)

                if detections:
                    for det in detections:
                        class_name = det["class"]
                        confidence = det["confidence"]
                        self.detection_count += 1

                        # Salva no BD
                        detection_obj = Detection(
                            class_name=class_name,
                            confidence=confidence,
                            timestamp=datetime.now()
                        )
                        det_id = self.db.save_detection(detection_obj)

                        # Alerta
                        if self.should_alert(class_name):
                            print(f"🚨 ALERTA: {class_name.upper()} detectado ({confidence:.1%})")
                        else:
                            print(f"📍 {class_name.upper()} detectado ({confidence:.1%}) - cooldown ativo")

                # Status periódico
                if self.frame_count % 10 == 0:
                    stats = self.db.get_stats()
                    print(f"\n📊 Status: {self.frame_count} frames, {self.detection_count} detecções")
                    if stats["by_class"]:
                        for cls, count in stats["by_class"].items():
                            print(f"   • {cls}: {count}")
                    print()

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n\n✋ Interrupção do usuário")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            return False
        finally:
            self.camera.disconnect()
            stats = self.db.get_stats()
            print("\n" + "=" * 60)
            print(f"✓ Finalizado: {self.frame_count} frames processados")
            print(f"✓ Detecções: {self.detection_count}")
            if stats["by_class"]:
                print("✓ Resumo:")
                for cls, count in stats["by_class"].items():
                    print(f"   • {cls}: {count}")
            print("=" * 60 + "\n")

        return True


if __name__ == "__main__":
    guardian = CameraGuardian()
    guardian.run()