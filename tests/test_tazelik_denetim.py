# -*- coding: utf-8 -*-
"""tazelik_denetim.py (v0.5.8 P6+P7 — graft 'Sources@hash' deseni) testleri.

Saha kanıtı (Çal 1079): analiz ürünleri külliyat %20'deyken doğdu, külliyat
büyüdü, ürünler sessizce eskidi — delta ihtiyacını insan gözcü yakaladı.
Bu denetçi o gözcünün otomasyonu: advisory, HER ZAMAN exit 0.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
          / "scripts" / "tazelik_denetim.py")


def _sha8(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def _kok_kur():
    kok = pathlib.Path(tempfile.mkdtemp())
    (kok / "_oa" / "metin").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    kaynak = kok / "_oa" / "metin" / "00-kunye.json"
    kaynak.write_text('{"toplam_evrak": 10}', encoding="utf-8")
    return kok, kaynak


def _urun_yaz(kok, ad, kaynak_goreli, sha):
    (kok / "_oa" / "cikti" / ad).write_text(
        f"<!-- kaynaklar: {kaynak_goreli}@{sha} -->\n"
        "<!-- besledigi: 08-dilekce -->\n"
        "<!-- uretim: 2026-08-12T10:00Z · test -->\n\n# Ürün\niçerik\n",
        encoding="utf-8")


def _cli(kok, *ek):
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--kok", str(kok), *ek],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def test_taze_urun_sessiz_ve_exit0():
    kok, kaynak = _kok_kur()
    _urun_yaz(kok, "04-strateji.md", "metin/00-kunye.json", _sha8(kaynak))
    kod, out = _cli(kok)
    assert kod == 0 and "TAZE" in out and "BAYAT" not in out


def test_kaynak_degisince_bayat_advisory_ama_exit0():
    kok, kaynak = _kok_kur()
    _urun_yaz(kok, "04-strateji.md", "metin/00-kunye.json", _sha8(kaynak))
    kaynak.write_text('{"toplam_evrak": 3795}', encoding="utf-8")  # külliyat büyüdü
    kod, out = _cli(kok)
    assert kod == 0  # advisory — asla bloklamaz
    assert "BAYAT" in out and "delta" in out


def test_eksik_kaynak_ve_json_cikti():
    kok, kaynak = _kok_kur()
    _urun_yaz(kok, "04-strateji.md", "metin/yok-boyle-dosya.json", "deadbeef")
    kod, out = _cli(kok, "--json")
    assert kod == 0
    r = json.loads(out)
    assert r["eksik"] and r["eksik"][0]["urun"] == "04-strateji.md"


def test_bloksuz_urun_denetim_disi():
    kok, _ = _kok_kur()
    (kok / "_oa" / "cikti" / "eski-urun.md").write_text("# blok yok\n",
                                                        encoding="utf-8")
    kod, out = _cli(kok)
    assert kod == 0 and "1 bloksuz" in out
