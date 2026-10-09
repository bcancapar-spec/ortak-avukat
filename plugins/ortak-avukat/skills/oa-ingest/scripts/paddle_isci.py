#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
paddle_isci.py — PaddleOCR YEREL İŞÇİSİ (OCR planı O-4 · v0.5.18 adayı)

NEDEN AYRI YORUMLAYICI: PaddlePaddle + PaddleOCR (~700 MB; MKL, OpenCV) Ortak
Avukat'ın bağımlılığı OLAMAZ. oa_ingest bu işçiyi yalnız `OA_PADDLE_PY` ile
gösterilen yorumlayıcıda alt süreç olarak çağırır; işçi yoksa/çökerse OA
Tesseract ile sürer ve bunu künyeye "yedeğe düşüldü" diye yazar.

AĞSIZ: model dizinleri (`--model-dizin` altında <det>/ ve <rec>/) yoksa işçi
ÇALIŞMAYI REDDEDER (araç hatası). PaddleX'in ilk koşuda internetten model
indirmesi meslek sırrı ve denetlenebilirlik açısından kabul edilmez; modeller bir
kez, avukatın bilgisiyle resmî kaynaktan indirilip bu dizine konur. Bağlantı
denetimi de kapatılır (PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK).

DETERMİNİZM: cpu_threads=1, MKL-DNN kapalı. Aynı makinede aynı çıktı beklenir;
farklı CPU'da kayan nokta farkı olabilir — bayt eşitliği VAAT EDİLMEZ.

Kullanım:
  python paddle_isci.py --kontrol --model-dizin <dizin>
  python paddle_isci.py --png <yol> --model-dizin <dizin> [--det AD] [--rec AD]
Çıktı: stdout'a TEK satır JSON.
  başarı → {"metin": str, "satirlar": [{"metin","skor","kutu"}], "motor": {...}}
  hata   → {"hata": str} (çıkış kodu 2)
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, os

VARSAYILAN_DET = "PP-OCRv6_medium_det"   # PaddleOCR 3.7: Latin (tr dahil) dilleri için varsayılan
VARSAYILAN_REC = "PP-OCRv6_medium_rec"


def _yaz(d, kod=0):
    print(json.dumps(d, ensure_ascii=False))
    return kod


def _sonuc_alanlari(r):
    """PaddleOCR 3.x sonuç nesnesi (dict benzeri) → (metinler, skorlar, kutular)."""
    try:
        return list(r["rec_texts"]), list(r["rec_scores"]), r["rec_boxes"]
    except Exception:
        d = (getattr(r, "json", None) or {}).get("res", {})
        return d.get("rec_texts") or [], d.get("rec_scores") or [], d.get("rec_boxes")


def _satirlari_diz(metinler, skorlar, kutular):
    """Okuma sırası: üst kenar (satır bandı), sonra sol kenar — deterministik."""
    satirlar = []
    for i, m in enumerate(metinler):
        try:
            k = [int(v) for v in list(kutular[i])[:4]]
        except Exception:
            k = [0, i, 0, i]
        satirlar.append({"metin": str(m), "skor": round(float(skorlar[i]) if i < len(skorlar) else 0.0, 4),
                         "kutu": k})
    satirlar.sort(key=lambda s: (s["kutu"][1] // 12, s["kutu"][0]))
    return satirlar


def main(argv=None):
    ap = argparse.ArgumentParser(description="PaddleOCR yerel işçisi (ağsız)")
    ap.add_argument("--png")
    ap.add_argument("--model-dizin", required=True, dest="model_dizin")
    ap.add_argument("--det", default=VARSAYILAN_DET)
    ap.add_argument("--rec", default=VARSAYILAN_REC)
    ap.add_argument("--kontrol", action="store_true")
    a = ap.parse_args(argv)
    det_dir, rec_dir = os.path.join(a.model_dizin, a.det), os.path.join(a.model_dizin, a.rec)
    eksik = [d for d in (det_dir, rec_dir) if not os.path.isdir(d)]
    if eksik:
        return _yaz({"hata": "model dizini yok (ağsız çalışma — indirme YAPILMAZ): " + "; ".join(eksik)}, 2)
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
    try:
        import paddleocr
        from paddleocr import PaddleOCR
    except Exception as e:
        return _yaz({"hata": "paddleocr yüklenemedi: %s: %s" % (type(e).__name__, str(e)[:200])}, 2)
    try:
        ocr = PaddleOCR(text_detection_model_name=a.det, text_detection_model_dir=det_dir,
                        text_recognition_model_name=a.rec, text_recognition_model_dir=rec_dir,
                        use_doc_orientation_classify=False, use_doc_unwarping=False,
                        use_textline_orientation=False, device="cpu", enable_mkldnn=False, cpu_threads=1)
    except Exception as e:
        return _yaz({"hata": "PaddleOCR başlatılamadı: %s: %s" % (type(e).__name__, str(e)[:200])}, 2)
    motor = {"ad": "paddleocr", "surum": getattr(paddleocr, "__version__", "?"), "det": a.det, "rec": a.rec}
    if a.kontrol:
        return _yaz({"hazir": True, "motor": motor})
    if not a.png or not os.path.isfile(a.png):
        return _yaz({"hata": "png yok: %s" % a.png}, 2)
    try:
        sonuclar = ocr.predict(a.png)
    except Exception as e:
        return _yaz({"hata": "tahmin hatası: %s: %s" % (type(e).__name__, str(e)[:200])}, 2)
    satirlar = []
    for r in sonuclar or []:
        satirlar += _satirlari_diz(*_sonuc_alanlari(r))
    return _yaz({"metin": "\n".join(s["metin"] for s in satirlar), "satirlar": satirlar, "motor": motor})


if __name__ == "__main__":
    _sys.exit(main())
