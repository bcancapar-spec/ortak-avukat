# -*- coding: utf-8 -*-
"""P0-4 (v0.5.5) — --zorla artık gerekçe zorunlu + kayıpsız şerh dosyası.

`--zorla` tek başına artık yetmez: `--zorla-gerekce` (≥30 karakter) EŞ
bayrağı zorunludur. Bastırılan engel/uyarı METNİ TAMAMEN (400-karakter kesme
KALDIRILDI) hem durum.json `serh_tarihcesi`'nde hem ayrı bir
`_oa/defter/serh/<ts>.md` dosyasında KAYIPSIZ saklanır.
"""
import hashlib
import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"


def _load():
    spec = importlib.util.spec_from_file_location("tam_tur_zorla", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tt = _load()


def _sha(icerik):
    return hashlib.sha256(icerik.encode("utf-8")).hexdigest()[:16]


def _kunye_yaz(kok, kayitlar):
    metin_dizin = pathlib.Path(kok) / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": len(kayitlar), "kayitlar": kayitlar}, ensure_ascii=False),
        encoding="utf-8")
    for k in kayitlar:
        (pathlib.Path(kok) / k["kaynak"]).write_text("x", encoding="utf-8")


def _cikti_birak(kok, ad="01-parca.md", icerik="çalışma evrakı"):
    d = pathlib.Path(kok) / "_oa" / "cikti"
    d.mkdir(parents=True, exist_ok=True)
    (d / ad).write_text(icerik, encoding="utf-8")


UZUN_GEREKCE = "Bu test için bilinçli olarak zorlama uygulanıyor (>=30 karakter)."


# ── (1) --zorla gerekçesiz → exit 1 ─────────────────────────────────────────

def test_zorla_gerekcesiz_exit1(tmp_path, capsys):
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    kod = tt.cmd_kaydet(str(tmp_path), zorla=True, zorla_gerekce=None)
    assert kod == 1
    cikti = capsys.readouterr().err
    assert "--zorla-gerekce" in cikti


def test_zorla_gerekce_kisa_exit1(tmp_path):
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    kod = tt.cmd_kaydet(str(tmp_path), zorla=True, zorla_gerekce="çok kısa")
    assert kod == 1


# ── (2) 2000+ karakterlik engel listesi serh/ dosyasında BYTE-KAYIPSIZ ─────

def test_uzun_engel_listesi_serh_dosyasinda_kayipsiz(tmp_path):
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    # (iv-b) yutma denetimini tetikle: snapshot sonrası YENİ bir evrak GELİŞME'de
    # anılmadan eklenir — uzun bir tekrar deseniyle 2000+ karakter üretir.
    yeni_kayitlar = [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}]
    for i in range(80):
        ad = f"ek-{i:03d}.pdf"
        yeni_kayitlar.append({"kaynak": ad, "sha": _sha(f"v{i}")})
    _kunye_yaz(tmp_path, yeni_kayitlar)

    kod = tt.cmd_kaydet(str(tmp_path), zorla=True, zorla_gerekce=UZUN_GEREKCE)
    assert kod == 0

    durum_json = json.loads((tmp_path / "_oa" / "analiz" / "dosya-analiz.json")
                             .read_text(encoding="utf-8"))
    serhler = durum_json.get("serh_tarihcesi") or []
    assert serhler, "serh_tarihcesi boş olmamalı"
    son_serh = serhler[-1]
    assert son_serh.get("gerekce") == UZUN_GEREKCE
    tam_dosya_goreli = son_serh.get("tam_dosya")
    assert tam_dosya_goreli, "tam_dosya alanı eksik"

    tam_dosya = tmp_path / tam_dosya_goreli
    assert tam_dosya.is_file()
    serh_metni = tam_dosya.read_text(encoding="utf-8")
    assert len(serh_metni) >= 200  # gerçek içerik var, boş şablon değil
    for k in yeni_kayitlar[1:]:  # tüm yeni dosyalar kayıpsız listelenmiş olmalı
        assert k["kaynak"] in serh_metni or k["kaynak"] in " ".join(
            son_serh.get("aciklamalar", []))


# ── (3) gerekçe hem json hem md'de görünür ──────────────────────────────────

def test_gerekce_json_ve_md_de_gorunur(tmp_path):
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])
    kod = tt.cmd_kaydet(str(tmp_path), zorla=True, zorla_gerekce=UZUN_GEREKCE)
    assert kod == 0

    durum_json = json.loads((tmp_path / "_oa" / "analiz" / "dosya-analiz.json")
                             .read_text(encoding="utf-8"))
    assert durum_json["serh_tarihcesi"][-1]["gerekce"] == UZUN_GEREKCE

    md = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert UZUN_GEREKCE in md
    assert "Tam kayıpsız döküm" in md


# ── (4) mevcut test_tam_tur*.py geçmeye devam eder — ayrı invoke ile ────────
# (bkz. tests/test_tam_tur.py — bu paketin bir parçası olarak zaten koşulur)
