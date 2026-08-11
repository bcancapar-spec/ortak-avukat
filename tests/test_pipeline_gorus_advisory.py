# -*- coding: utf-8 -*-
"""GÖRÜŞ 2026-08 paketi (semantica uyarlama analizi antitez turu sonucu —
bkz. `_gorus/semantica-uyarlama.md` §4) için testler:

1. `pipeline_kayit.py` içindeki üç yeni advisory bekçi — `_graf_yapisal_
   bosluk_uyarisi`, `_kiyas_bosluk_uyarisi`, `_usul_bosluk_uyarisi` —
   motorların KENDİ `--json` çıktısını salt-okur; yabancı/bozuk dosyada
   sessizce boş döner (advisory renderer alanı, asla çökmez).
2. `_defter_nobetci_uyarisi` — append-only defterin satır sayısı bir önceki
   türetime göre AZALMIŞSA uyarır (kırpılma tespiti); hash-ZİNCİRİ bilerek
   kurulmadı (paralel fan-out append'i zinciri çatallar — antitez bulgusu).
3. `usul_matris.py --json` — yeni opsiyonel bayrak: boşluklu denetimde bile
   (exit 1'den ÖNCE) makine-okur sonuç yazılır.

Bekçiler in-process test edilir (pipeline_kayit importlib ile yüklenir —
scriptin kendi `_oa_metrik_modulu` deseniyle simetrik); usul_matris CLI ile.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PIPELINE = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
            / "scripts" / "pipeline_kayit.py")
USUL = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-usul"
        / "scripts" / "usul_matris.py")


def _pipeline_modul():
    spec = importlib.util.spec_from_file_location("_test_pipeline_kayit", PIPELINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pk():
    return _pipeline_modul()


@pytest.fixture
def kok():
    k = pathlib.Path(tempfile.mkdtemp())
    (k / "_oa" / "cikti").mkdir(parents=True)
    (k / "_oa" / "defter").mkdir(parents=True)
    return k


def _cikti_yaz(kok, ad, veri):
    yol = kok / "_oa" / "cikti" / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def test_scriptler_mevcut():
    assert PIPELINE.is_file()
    assert USUL.is_file()


# ── 1. graf bekçisi ─────────────────────────────────────────────────────────

def test_graf_bekcisi_desteksiz_kenar_ve_cevrim_uyarir(pk, kok):
    _cikti_yaz(kok, "01-illiyet-graf.json", {
        "arac": "grafik_denetim",
        "sema_hatalari": ["Düğüm 'X': 'tip' eksik"],
        "desteksiz_kenarlar": [{"kaynak": "A", "hedef": "B", "tur": "odeme"}],
        "cevrimler": [["A", "B", "A"]],
    })
    uyarilar = pk._graf_yapisal_bosluk_uyarisi(str(kok))
    metin = "\n".join(uyarilar)
    assert len(uyarilar) == 3
    assert "şema hatası" in metin
    assert "desteksiz kenar A→B" in metin
    assert "dairesel illiyet — A → B → A" in metin


def test_graf_bekcisi_yabanci_ve_bozuk_dosyada_sessiz(pk, kok):
    _cikti_yaz(kok, "02-graf-yabanci.json", {"arac": "baska_arac",
                                             "desteksiz_kenarlar": [{"kaynak": "A"}]})
    (kok / "_oa" / "cikti" / "03-graf-bozuk.json").write_text("{bozuk", encoding="utf-8")
    assert pk._graf_yapisal_bosluk_uyarisi(str(kok)) == []


def test_graf_bekcisi_cikti_dizini_yoksa_bos(pk):
    assert pk._graf_yapisal_bosluk_uyarisi(tempfile.mkdtemp()) == []


# ── 2. kıyas bekçisi ────────────────────────────────────────────────────────

def test_kiyas_bekcisi_karsilanmamis_unsur_ve_teyitsiz_ictihat(pk, kok):
    _cikti_yaz(kok, "05-kiyas.json", {
        "arac": "kiyas_denetim",
        "kritik_bosluk": True,
        "teyitsiz_ictihat": ["Yargıtay 9. HD 2020/1 E."],
        "unsur_vakia_eslesme": [
            {"unsur_id": "U1", "unsur_ad": "kusur", "durum": "karsilanmamis"},
            {"unsur_id": "U2", "unsur_ad": "zarar", "durum": "karsilanan_delilli"},
        ],
    })
    uyarilar = pk._kiyas_bosluk_uyarisi(str(kok))
    metin = "\n".join(uyarilar)
    assert len(uyarilar) == 2  # kritik_bosluk ayrıca TEKRAR sayılmaz (bulundu=True)
    assert "unsur 'kusur' KARŞILANMAMIŞ" in metin
    assert "teyitsiz içtihat — Yargıtay 9. HD 2020/1 E." in metin
    assert "zarar" not in metin  # karşılanan unsur uyarı üretmez


def test_kiyas_bekcisi_yalniz_kritik_bayrakta_tek_uyari(pk, kok):
    # eksik bileşen hali: eşleşme listesi boş ama kritik_bosluk=True (norm yok)
    _cikti_yaz(kok, "05-kiyas.json", {
        "arac": "kiyas_denetim", "kritik_bosluk": True,
        "teyitsiz_ictihat": [], "unsur_vakia_eslesme": [],
    })
    uyarilar = pk._kiyas_bosluk_uyarisi(str(kok))
    assert len(uyarilar) == 1
    assert "kritik boşluk işaretli" in uyarilar[0]


# ── 3. usul bekçisi + usul_matris --json ────────────────────────────────────

def test_usul_bekcisi_bosluklari_listeler(pk, kok):
    _cikti_yaz(kok, "02-usul.json", {
        "arac": "usul_matris",
        "bosluklar": ["[G1] I1: tebliğ var ama son_gun yok — oa-sure ile hesapla."],
    })
    uyarilar = pk._usul_bosluk_uyarisi(str(kok))
    assert len(uyarilar) == 1
    assert "[G1]" in uyarilar[0]


def test_usul_matris_json_bayragi_bosluklu_halde_de_yazar(kok):
    """--json, exit 1'den ÖNCE yazılmalı: boşluklu denetimin sonucu da
    makine-okur kalmalı (DURUM.md bekçisi boşlukları ancak buradan görür)."""
    girdi = kok / "dosya_usul.json"
    # NOT: [G1] boşluğu `continue` ile aynı işlemin kalan denetimlerini atlar
    # (karakterizasyon bulgusu) — bu yüzden G1 ve G4 AYRI işlemlerle üretilir.
    girdi.write_text(json.dumps({
        "dosya": "Test 2026/1", "islemler": [
            {"id": "I1", "taraf": "biz", "islem": "cevap",
             "teblig": "2026-03-02"},
            {"id": "I2", "taraf": "biz", "islem": "istinaf",
             "teblig": "2026-04-01", "teblig_belgeli": False,
             "son_gun": "2026-04-15", "fiili_tarih": "2026-04-10",
             "kesin_dil": True},
        ]}, ensure_ascii=False), encoding="utf-8")
    json_yol = kok / "02-usul.json"
    cp = subprocess.run(
        [sys.executable, str(USUL), "--girdi", str(girdi), "--json", str(json_yol)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 1, cp.stdout + cp.stderr  # boşluk → mevcut exit 1 korunur
    veri = json.loads(json_yol.read_text(encoding="utf-8"))
    assert veri["arac"] == "usul_matris"
    assert veri["saglikli"] is False
    assert any("[G1]" in b for b in veri["bosluklar"])
    assert any("[G4]" in b for b in veri["bosluklar"])


def test_usul_matris_json_bayraksiz_eski_davranis_ayni(kok):
    girdi = kok / "dosya_usul.json"
    girdi.write_text(json.dumps({"dosya": "Test", "islemler": []},
                                ensure_ascii=False), encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(USUL), "--girdi", str(girdi)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0
    assert "Boşluk yok" in cp.stdout
    assert "[JSON]" not in cp.stdout  # bayrak verilmedikçe JSON izi yok


# ── 4. defter nöbetçisi ─────────────────────────────────────────────────────

def _defter_yaz(kok, satirlar):
    yol = kok / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    yol.write_text("".join(json.dumps({"tip": "adim", "n": i}) + "\n"
                           for i in range(satirlar)), encoding="utf-8")
    return yol


def test_nobetci_ilk_koVsuda_uyari_yok_durum_dosyasi_yazilir(pk, kok):
    yol = _defter_yaz(kok, 5)
    assert pk._defter_nobetci_uyarisi(str(kok), str(yol)) == []
    durum = json.loads((kok / "_oa" / "defter" / "defter-nobetci.json")
                       .read_text(encoding="utf-8"))
    assert durum["satir"] == 5
    assert len(durum["sha"]) == 16


def test_nobetci_buyume_sessiz_kuculme_uyarir(pk, kok):
    yol = _defter_yaz(kok, 5)
    pk._defter_nobetci_uyarisi(str(kok), str(yol))
    _defter_yaz(kok, 8)  # büyüme (normal append) → sessiz
    assert pk._defter_nobetci_uyarisi(str(kok), str(yol)) == []
    _defter_yaz(kok, 3)  # KÜÇÜLME (kırpılma) → uyarı
    uyarilar = pk._defter_nobetci_uyarisi(str(kok), str(yol))
    assert len(uyarilar) == 1
    assert "DEFTER KÜÇÜLDÜ: 8 → 3 satır" in uyarilar[0]
    # uyarıdan sonra durum güncellenir: aynı küçük boyut ikinci kez uyarmaz
    assert pk._defter_nobetci_uyarisi(str(kok), str(yol)) == []


def test_nobetci_defter_yoksa_sessiz(pk, kok):
    assert pk._defter_nobetci_uyarisi(str(kok), None) == []
    assert pk._defter_nobetci_uyarisi(
        str(kok), str(kok / "_oa" / "defter" / "yok.jsonl")) == []
