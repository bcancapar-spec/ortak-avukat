# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİRLEME TEPKİ (B-5 + B-1 teslim ucu): teslim zincirinde
«graf kapısı» ADVISORY adımı ve JSON bayatlığının makbuza taşınması.

Fable tutarlılık raporu (2026-10-07) B-5: K2 graf kapısı yalnız `--isle`
anında soruluyordu; sonra çevrim doğan graf yalnız advisory'ydi ve
`teslim_paketi.py` graf/kıyas/vakıa okumuyordu — teslim yeşil kalabiliyordu.
Avukat kararı (2026-10-07): teslimde GÖRÜNÜR UYARI — makbuzda satır; teslimi
DURDURMAZ, karar avukatın. Bu dosya o sözleşmeyi kilitler:
  - yeşil yol: exit 0 KALIR, makbuz `graf_kapisi.durum == "sorun"` + mesaj,
    rapor satırı görünür;
  - RED yol (B4 advisory tamamlanma): `advisory_denetimler.graf_kapisi` dolu;
  - graf denetimi hiç yoksa dürüst «kapı sorulmadı» (temiz İDDİASI yok);
  - B-1: damgalı denetim JSON'unun bayatlığı `tazelik_uyarilari`na girer.

Zincir gerçek alt scriptlerle koşar (dilekce_denetim/kunye_teyit/…); UDF
üretimi `--udf-yok` ile bilinçli atlanır (ortamdan bağımsız ikiz deseni).
Sentetik fikstür — gerçek müvekkil verisi yok (anayasa m.7).
"""
import hashlib
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
TESLIM = SKILLS / "oa-kontrol" / "scripts" / "teslim_paketi.py"

# test_teslim_makbuz.py ile aynı: zorunlu unsurları taşıyan, atıfsız taslak.
TAM_TEMIZ_TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: kurgu-maskeli)
Adres: Örnek Mahallesi No:1 İstanbul

DAVALI: Mehmet Kaya

KONU: Alacağın tahsili talebimizden ibarettir.

AÇIKLAMALAR (VAKIALAR):
1. Taraflar arasındaki ticari ilişkiden doğan alacak vakıası aşağıda özetlenmiştir.
2. Davalı, sözleşme kapsamındaki edimini yerine getirmemiştir.

HUKUKİ SEBEPLER:
İlgili mevzuat hükümleri ve genel hukuk kuralları dayanak alınmıştır.

DELİLLER:
Tanık beyanları, bilirkişi incelemesi ve yazılı belgeler ispat vasıtasıdır.

NETİCE-İ TALEP:
Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini saygılarımla talep ederim.

Tarih: 01.07.2026

Av. Ayşe Yılmaz
Vekil
İmza
"""
EKSIK_TASLAK = "Bu kısa bir taslaktır ve zorunlu unsurları içermez.\n"

CEVRIMLI_GRAF_DENETIMI = {"arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]],
                          "sema_hatalari": [], "denetim_coktu": False}


def _tp(args):
    cp = subprocess.run([sys.executable, str(TESLIM)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _kok_kur(tmp_path, taslak_metni=TAM_TEMIZ_TASLAK):
    kok = tmp_path / "dava"
    (kok / "_oa" / "cikti").mkdir(parents=True)
    taslak = kok / "taslak.md"
    taslak.write_text(taslak_metni, encoding="utf-8")
    return kok, taslak


def _cikti_yaz(kok, ad, veri):
    (kok / "_oa" / "cikti" / ad).write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")


def _makbuz(kok, ad="teslim-makbuz.json"):
    return json.loads((kok / "_oa" / "defter" / ad).read_text(encoding="utf-8"))


def _sha8(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:8]


# ═══════════════ B-5 — graf kapısı advisory adımı ══════════════════════════

def test_cevrimli_graf_denetimi_varken_teslim_makbuzunda_gorunur(tmp_path):
    """Çevrimli (dairesel illiyet) graf denetimi dururken teslim: exit 0 KALIR
    (kapı KAPATMAZ — avukat kararı), makbuz `graf_kapisi` sorunu adıyla
    taşır, rapor satırı görünür."""
    kok, taslak = _kok_kur(tmp_path)
    _cikti_yaz(kok, "01-illiyet-denetim.json", CEVRIMLI_GRAF_DENETIMI)
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod == 0, out
    assert "TESLİME HAZIR" in out
    assert "GRAF KAPISI" in out and "dairesel illiyet" in out, out
    m = _makbuz(kok)
    gk = m["graf_kapisi"]
    assert gk["durum"] == "sorun"
    assert "GRAF KAPISI" in gk["mesaj"] and "01-illiyet-denetim.json" in gk["mesaj"]
    assert "dairesel illiyet" in gk["mesaj"]
    assert gk["denetim_json_sayisi"] == 1


def test_temiz_graf_denetimi_makbuzda_acik(tmp_path):
    kok, taslak = _kok_kur(tmp_path)
    _cikti_yaz(kok, "01-illiyet-denetim.json", {"arac": "grafik_denetim", "cevrimler": [],
                                                 "sema_hatalari": [], "denetim_coktu": False})
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod == 0, out
    gk = _makbuz(kok)["graf_kapisi"]
    assert gk == {"durum": "acik", "mesaj": None, "denetim_json_sayisi": 1}


def test_graf_denetimi_hic_yoksa_kapi_sorulmadi_durust_not(tmp_path):
    """Graf denetimi koşmamışsa 'temiz' DENMEZ — «kapı sorulmadı» notu
    (K2 sözleşmesi: dosya yoksa RET değil; ama yeşil iddiası da yok)."""
    kok, taslak = _kok_kur(tmp_path)
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod == 0, out
    gk = _makbuz(kok)["graf_kapisi"]
    assert gk["durum"] == "acik" and gk["denetim_json_sayisi"] == 0
    assert gk["mesaj"] and "sorulmadı" in gk["mesaj"]


def test_bozuk_graf_denetimi_teslimde_de_gorunur(tmp_path):
    """B-4 × B-5: yarım yazılmış denetim JSON'u teslimde sessiz kalmaz —
    makbuz sorunu 'OKUNAMADI' olarak taşır (yine kapatmaz)."""
    kok, taslak = _kok_kur(tmp_path)
    (kok / "_oa" / "cikti" / "01-illiyet-denetim.json").write_text('{"arac": "grafik_de',
                                                                    encoding="utf-8")
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod == 0, out
    gk = _makbuz(kok)["graf_kapisi"]
    assert gk["durum"] == "sorun" and "OKUNAMADI" in gk["mesaj"]


def test_red_yolunda_advisory_graf_kapisi_dolu(tmp_path):
    """B4 advisory tamamlanma: ilk kapı ((a) dilekçe) kapansa bile graf kapısı
    sorusu sorulur ve RED makbuzunun `advisory_denetimler` alanında durur."""
    kok, taslak = _kok_kur(tmp_path, EKSIK_TASLAK)
    _cikti_yaz(kok, "01-illiyet-denetim.json", CEVRIMLI_GRAF_DENETIMI)
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod != 0
    assert "[ADVISORY] graf kapısı" in out and "dairesel illiyet" in out, out
    m = _makbuz(kok, "teslim-makbuz-RED.json")
    gk = m["advisory_denetimler"]["graf_kapisi"]
    assert gk["durum"] == "sorun" and "dairesel illiyet" in gk["mesaj"]


# ═══════════════ B-1 — JSON bayatlığı teslim makbuzunda ════════════════════

def test_json_denetimi_bayatsa_tazelik_uyarilarina_girer(tmp_path):
    """Künye değişti → damgalı vakıa denetim JSON'u BAYAT → makbuz
    `tazelik_uyarilari` satırı (kapı kapatmaz)."""
    kok, taslak = _kok_kur(tmp_path)
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True)
    kunye = metin / "00-kunye.json"
    kunye.write_text('{"toplam_evrak": 1}', encoding="utf-8")
    _cikti_yaz(kok, "04-vakia.json", {"iddialar": [], "olaylar": []})
    _cikti_yaz(kok, "04-vakia-denetim.json", {
        "arac": "vakia_matris", "ispat_bosluklari": [],
        "kaynaklar": [
            {"rol": "girdi", "yol": "cikti/04-vakia.json",
             "sha8": _sha8(kok / "_oa" / "cikti" / "04-vakia.json")},
            {"rol": "kunye", "yol": "metin/00-kunye.json", "sha8": _sha8(kunye)}]})
    kunye.write_text('{"toplam_evrak": 2}', encoding="utf-8")   # yeni evrak geldi
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod == 0, out
    uyarilar = _makbuz(kok)["tazelik_uyarilari"]
    assert uyarilar and any("BAYAT" in u and "04-vakia-denetim.json" in u for u in uyarilar), uyarilar
    assert any("metin/00-kunye.json" in u for u in uyarilar)


def test_okunamayan_json_tazelik_uyarilarinda_temiz_sayilmaz(tmp_path):
    kok, taslak = _kok_kur(tmp_path)
    (kok / "_oa" / "cikti" / "05-kiyas-denetim.json").write_text("{ bozuk", encoding="utf-8")
    kod, out = _tp([taslak, "--tip", "genel", "--kok", kok, "--udf-yok"])
    assert kod == 0, out
    uyarilar = _makbuz(kok)["tazelik_uyarilari"]
    assert uyarilar and any("OKUNAMADI" in u and "05-kiyas-denetim.json" in u for u in uyarilar)
