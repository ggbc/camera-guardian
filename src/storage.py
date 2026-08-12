"""Armazenamento de detecções em SQLite."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class Detection:
    """Resultado de uma detecção."""

    def __init__(self, class_name: str, confidence: float, timestamp: datetime):
        self.class_name = class_name
        self.confidence = confidence
        self.timestamp = timestamp


class Database:
    """Gerencia banco SQLite."""

    def __init__(self, db_path: str = "./data/detections.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Cria banco e tabelas se não existirem."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON detections(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_class ON detections(class_name)"
        )

        conn.commit()
        conn.close()
        print(f"✓ BD inicializado: {self.db_path}")

    def save_detection(self, detection: Detection) -> int:
        """Salva uma detecção."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO detections (class_name, confidence, timestamp)
                VALUES (?, ?, ?)
                """,
                (detection.class_name, detection.confidence, detection.timestamp.isoformat()),
            )

            conn.commit()
            detection_id = cursor.lastrowid
            conn.close()

            return detection_id

        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return -1

    def get_recent(self, limit: int = 20) -> List[dict]:
        """Retorna detecções recentes."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ Erro ao recuperar: {e}")
            return []

    def get_stats(self) -> dict:
        """Retorna estatísticas."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM detections")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT class_name, COUNT(*) as count FROM detections GROUP BY class_name ORDER BY count DESC"
            )
            by_class = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()
            return {"total": total, "by_class": by_class}

        except Exception as e:
            print(f"❌ Erro ao calcular stats: {e}")
            return {}