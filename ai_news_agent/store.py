# -*- coding: utf-8 -*-
"""ذاكرة الأخبار المرسلة — تمنع تكرار نفس الخبر.

تُحفظ في ملف JSON على القرص، فحتى لو أعدت تشغيل البوت ما يعيد إرسال القديم.
كل مفتاح ينتهي تلقائيًا بعد عدد أيام (TTL) عشان الملف ما يكبر بلا نهاية.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

# صيغة الملف — لو تغيّرت طريقة المفاتيح نرفع الرقم فيبدأ الملف من جديد بأمان
FORMAT_VERSION = 2


def fingerprint(key: str) -> str:
    """بصمة قصيرة للمفتاح — الروابط تجي طويلة جدًا (Google News ~500 حرف)."""
    return hashlib.blake2b(key.encode("utf-8"), digest_size=8).hexdigest()


class SeenStore:
    def __init__(self, path: str | Path, ttl_days: int = 7):
        self.path = Path(path)
        self.ttl = ttl_days * 86400
        self._data: dict[str, float] = {}
        self._load()

    # -- تحميل / حفظ -------------------------------------------------------
    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or raw.get("version") != FORMAT_VERSION:
                # صيغة قديمة — نبدأ من جديد (بيُعاد "التصفير" بدل إرسال أخبار قديمة)
                self._data = {}
                return
            entries = raw.get("entries", {})
            cutoff = time.time() - self.ttl
            self._data = {k: v for k, v in entries.items() if isinstance(v, (int, float)) and v > cutoff}
        except FileNotFoundError:
            self._data = {}
        except Exception as e:
            print(f"[!] ملف الذاكرة تالف ({e}) — بنبدأ من جديد")
            self._data = {}

    def save(self) -> None:
        """كتابة ذرّية: نكتب ملف مؤقت ثم نستبدل — ما يخرب الملف لو انقطع التشغيل."""
        payload = {"version": FORMAT_VERSION, "entries": self._data}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            os.replace(tmp, self.path)
        except Exception as e:
            print(f"[!] فشل حفظ الذاكرة: {e}")
            if os.path.exists(tmp):
                os.unlink(tmp)

    # -- الاستخدام ---------------------------------------------------------
    def has(self, key: str) -> bool:
        return fingerprint(key) in self._data

    def add(self, key: str) -> None:
        if key:
            self._data[fingerprint(key)] = time.time()

    def add_many(self, keys) -> None:
        now = time.time()
        for k in keys:
            if k:
                self._data[fingerprint(k)] = now

    @property
    def is_empty(self) -> bool:
        return not self._data

    def __len__(self) -> int:
        return len(self._data)
