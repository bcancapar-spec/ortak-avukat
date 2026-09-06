# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP I6: oa-sozlesme İFA SENARYO TESTİ (P2-6 / A-23).

Bulgu: `sozlesme_denetim.py` bir klozun VAR/YOK olduğuna ve risk bandına
bakıyordu; klozun **üç ifa senaryosunda** (normal ifa / gecikme / fesih)
gerçekten işleyip işlemediği hiçbir yerde sınanmıyordu. Sözleşme uyuşmazlık
çıkana kadar test edilmez — zaaf en kötü anda görünür. Bu paket, her kloz
için opsiyonel `senaryo_testi` alanı (kloz × 3 senaryo → calisir / calismaz /
belirsiz) getirir; script nitelendirme YAPMAZ, yalnız alanın dolu/boş/biçimine
bakar ve görünür boşluk satırı üretir. Kapı ASLA bloklamaz (exit sözleşmesi
korunur): senaryo boşluğu uyarıdır, sorun değildir.

Çıpalar (Mevzuat MCP teyit 2026-09-06, TBK 6098): m.117 (ihtarla temerrüt;
belirli vade → günün geçmesiyle), m.118 (gecikme tazminatı), m.123-124 (süre
verme / gerekmeyen hâller), m.125 (seçimlik haklar, dönme), m.126 (sürekli
edimli sözleşmede fesih).

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; repo dosyalarına
dokunulmaz. Fikstürler sentetiktir.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL_KOK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sozlesme"
SCRIPT = SKILL_KOK / "scripts" / "sozlesme_denetim.py"

KATEGORI_SIRASI = [
    "taraflar_temsil_imza_yetkisi", "konu_edimler", "bedel_odeme_ifa",
    "sure_uzama", "temerrut_cezai_sart_faiz", "fesih_tasfiye", "gizlilik",
    "kvkk_veri", "rekabet_yasagi_munhasirlik", "devir_temlik", "mucbir_sebep",
    "bildirim_tebligat", "uyusmazlik_cozumu", "delil_sozlesmesi",
    "butunluk_merger", "sekil_sarti",
]
SENARYOLAR = ("normal", "gecikme", "fesih")


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


@pytest.fixture
def izole_dizin():
    return pathlib.Path(tempfile.mkdtemp())


def _yaz(dizin, veri, ad="sozlesme.json"):
    yol = dizin / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _teyitli_sekil():
    return {"durum": "VAR", "risk": "orta",
            "not": "Mevzuat MCP teyidi: TBK m.583 sorgusu kosuldu",
            "onlem": "el yazili azami miktar metne islendi"}


def _dolu(senaryo=True):
    """TEMİZ geçen asgari dosya. `senaryo=True` → her klozda üç senaryo
    'calisir'; False → alan hiç yok (v0.5.15 saha dosyası biçimi)."""
    d = {
        "mod": "TAHRIR",
        "tip": "hizmet",
        "kategoriler": {
            k: {"durum": "VAR", "risk": "dusuk", "not": "kloz yazildi",
                "onlem": ""}
            for k in KATEGORI_SIRASI
        },
        "kirmizi_cizgiler": [],
        "acik_uclar": [],
        "gecerlilik_katmani": {
            "ehliyet_temsil": "imza sirkuleri goruldu",
            "genel_islem_kosullari": "muzakere edildi, GIK degil"},
    }
    d["kategoriler"]["sekil_sarti"] = _teyitli_sekil()
    if senaryo:
        for v in d["kategoriler"].values():
            v["senaryo_testi"] = {s: "calisir" for s in SENARYOLAR}
    return d


# --------------------------------------------------------------------------
# 1) İSKELET — alan şablonda, varsayılan 'belirsiz'
# --------------------------------------------------------------------------
def test_iskelet_her_kategoride_senaryo_testi_alani_tasir():
    """`--iskelet` her kategoriye `senaryo_testi` {normal, gecikme, fesih}
    ekler; varsayılan 'belirsiz' (sınanmamışlık açıkça görünür — 'calisir'
    varsayılanı sahte kesinlik olurdu)."""
    rc, out, _ = _cli("--iskelet")
    assert rc == 0
    veri = json.loads(out)
    assert list(veri["kategoriler"]) == KATEGORI_SIRASI
    for v in veri["kategoriler"].values():
        assert set(v) == {"durum", "risk", "not", "onlem", "senaryo_testi"}
        assert v["senaryo_testi"] == {s: "belirsiz" for s in SENARYOLAR}


def test_iskelet_hala_dokunulmamis_kapisina_takilir(izole_dizin):
    """B-6 kapısı yeni alandan etkilenmez: boş iskelet hâlâ exit 1."""
    rc0, iskelet_out, _ = _cli("--iskelet")
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, json.loads(iskelet_out)))
    assert rc == 1 and "hiç doldurulmamış" in out


# --------------------------------------------------------------------------
# 2) GERİYE UYUM — eski dosya (alan yok) çökmez, tek satır görünür uyarı
# --------------------------------------------------------------------------
def test_eski_dosya_alan_yok_cokmez_tek_satir_uyari_exit0(izole_dizin):
    """v0.5.15 biçimindeki saha dosyasında hiçbir klozda `senaryo_testi`
    yoktur: script ÇÖKMEZ, exit 0 kalır (fail-closed + görünür uyarı), ama
    TEMİZ hükmü basılmaz — 16 kloz × 3 senaryo sınanmamıştır. Gürültü
    disiplini: 48 satır değil, TEK toplu satır."""
    d = _dolu(senaryo=False)
    rc, out, err = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0 and "Traceback" not in err
    satirlar = [s for s in out.splitlines() if "senaryo testi hiç yapılmamış" in s]
    assert len(satirlar) == 1, out
    assert "16 kloz" in satirlar[0]
    assert "sınanmamış" not in "".join(
        s for s in out.splitlines() if s.strip().startswith("⚠ kloz "))
    assert "KAPSAM DENETİMİ TEMİZ" not in out
    assert "SENARYO DENETİMİ AÇIK" in out


def test_senaryo_testi_bozuk_tip_cokmez_belirsiz_sayilir(izole_dizin):
    """Alan dict değilse (metin/sayı/liste/None) traceback YOK; kloz üç
    senaryoda 'belirsiz' sayılır ve görünür boşluk satırı üretilir."""
    for bozuk in ("calisir", 5, ["calisir"], None):
        d = _dolu()
        d["kategoriler"]["gizlilik"]["senaryo_testi"] = bozuk
        rc, out, err = _cli(
            "--dogrula", _yaz(izole_dizin, d, f"b_{type(bozuk).__name__}.json"))
        assert rc == 0 and "Traceback" not in err, err
        assert "kloz gizlilik: fesih senaryosu sınanmamış" in out, out
        assert "kloz gizlilik: normal senaryosu sınanmamış" in out
        assert "kloz gizlilik: gecikme senaryosu sınanmamış" in out


# --------------------------------------------------------------------------
# 3) BOŞLUK SATIRI — eksik/belirsiz senaryo görünür, ASLA bloklamaz
# --------------------------------------------------------------------------
def test_belirsiz_veya_eksik_senaryo_gorunur_bosluk_satiri_exit0(izole_dizin):
    d = _dolu()
    d["kategoriler"]["fesih_tasfiye"]["senaryo_testi"] = {
        "normal": "calisir", "gecikme": "belirsiz"}  # fesih anahtarı YOK
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0
    assert "kloz fesih_tasfiye: gecikme senaryosu sınanmamış" in out
    assert "kloz fesih_tasfiye: fesih senaryosu sınanmamış" in out
    assert "kloz fesih_tasfiye: normal senaryosu sınanmamış" not in out
    assert "KAPSAM DENETİMİ TEMİZ" not in out
    assert "SENARYO DENETİMİ AÇIK" in out
    assert "2 senaryo boşluğu" in out


def test_gecersiz_senaryo_degeri_bloklamaz_uyarir_belirsiz_sayar(izole_dizin):
    """Tanınmayan değer ('evet') SORUN değildir — exit sözleşmesi korunur;
    ama sessizce 'calisir'e de düşmez: uyarı + belirsiz."""
    d = _dolu()
    d["kategoriler"]["gizlilik"]["senaryo_testi"]["gecikme"] = "evet"
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0
    assert "kloz gizlilik: gecikme senaryosu değeri 'evet' tanınmıyor" in out
    assert "kloz gizlilik: gecikme senaryosu sınanmamış" in out
    assert "KAPSAM BOŞLUĞU" not in out


def test_uc_senaryo_calisir_ise_temiz_ve_bosluk_yok(izole_dizin):
    d = _dolu()
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0
    assert "sınanmamış" not in out
    assert "KAPSAM DENETİMİ TEMİZ" in out
    assert "İFA SENARYO MATRİSİ" in out


def test_senaryo_alani_yok_kloz_icin_uygulanmaz(izole_dizin):
    """Yazılmamış kloz (YOK-GEREKSIZ / YOK-EKSIK) senaryoda sınanamaz:
    matriste '—', boşluk satırı ÜRETİLMEZ (çift kırmızı yasağı — eksiklik
    zaten raporlanır)."""
    d = _dolu()
    d["kategoriler"]["mucbir_sebep"] = {
        "durum": "YOK-GEREKSIZ", "risk": "yok",
        "not": "iliskide mucbir sebep riski yok, taraflar mutabik", "onlem": ""}
    d["kategoriler"]["rekabet_yasagi_munhasirlik"] = {
        "durum": "YOK-EKSIK", "risk": "yok", "not": "", "onlem": ""}
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0
    assert "kloz mucbir_sebep" not in out
    assert "kloz rekabet_yasagi_munhasirlik" not in out
    assert "rekabet_yasagi_munhasirlik: EKSİK" in out


# --------------------------------------------------------------------------
# 4) MATRİS — kloz × 3 senaryo; mod yönü (TAHRİR: çalışmaz / İNCELEME: risk)
# --------------------------------------------------------------------------
def test_matris_tahrir_modunda_calismaz_yeniden_yaz_yonunde(izole_dizin):
    d = _dolu()
    d["kategoriler"]["bildirim_tebligat"]["senaryo_testi"]["fesih"] = "calismaz"
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0
    assert "İFA SENARYO MATRİSİ" in out
    matris = out.split("İFA SENARYO MATRİSİ", 1)[1]
    satir = next(s for s in matris.splitlines() if "bildirim_tebligat" in s)
    assert "ÇALIŞMAZ" in satir
    assert "aleyhine tetik" not in matris
    assert "1 kloz 'calismaz'" in out
    assert "KAPSAM DENETİMİ TEMİZ" not in out  # çalışmayan kloz temiz değil


def test_matris_inceleme_modunda_calismaz_risk_yonunde(izole_dizin):
    """İNCELEME modunda aynı matris RİSK yönünde okunur: 'calismaz' = kloz
    o senaryoda müvekkil aleyhine tetiklenir (karşı vekilin tuzağı)."""
    d = _dolu()
    d["mod"] = "İNCELEME"
    d["kirmizi_cizgiler"] = ["sorumluluk tavani kaldirilamaz"]
    d["kategoriler"]["fesih_tasfiye"]["senaryo_testi"]["gecikme"] = "calismaz"
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 0
    matris = out.split("İFA SENARYO MATRİSİ", 1)[1]
    satir = next(s for s in matris.splitlines() if "fesih_tasfiye" in s)
    assert "RİSK" in satir
    assert "aleyhine tetik" in matris


def test_matris_bloklayan_sorun_varken_de_basilir(izole_dizin):
    """Matris bilgi satırıdır; kapsam boşluğu (exit 1) onu gizlemez —
    avukat blok sebebiyle birlikte senaryo tablosunu da görür."""
    d = _dolu()
    del d["kategoriler"]["gizlilik"]
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 1
    assert "İFA SENARYO MATRİSİ" in out
    assert "kategori tamamen atlanmış: gizlilik" in out


# --------------------------------------------------------------------------
# 5) JSON ÇIKTISI — senaryo_bosluklari (makine-okur; pipeline defteri için)
# --------------------------------------------------------------------------
def test_json_ciktisi_senaryo_bosluklari_ve_matris(izole_dizin):
    d = _dolu()
    d["kategoriler"]["delil_sozlesmesi"]["senaryo_testi"] = {
        "normal": "calisir", "gecikme": "belirsiz", "fesih": "calismaz"}
    js = izole_dizin / "cikti.json"
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d), "--json", js)
    assert rc == 0
    assert "[JSON]" in out
    veri = json.loads(js.read_text(encoding="utf-8"))
    assert veri["senaryo_okuma"] == "tahrir"
    assert veri["senaryo_bosluklari"] == [
        {"kloz": "delil_sozlesmesi", "senaryo": "gecikme", "neden": "belirsiz"}]
    assert veri["senaryo_calismaz"] == [
        {"kloz": "delil_sozlesmesi", "senaryo": "fesih"}]
    assert veri["senaryo_matrisi"]["delil_sozlesmesi"] == {
        "normal": "calisir", "gecikme": "belirsiz", "fesih": "calismaz"}
    assert list(veri["senaryo_matrisi"]) == KATEGORI_SIRASI
    assert veri["sorunlar"] == [] and veri["exit"] == 0


def test_json_eski_dosyada_alan_yok_nedeni_ve_inceleme_okumasi(izole_dizin):
    d = _dolu(senaryo=False)
    d["mod"] = "REDLINE"
    d["kirmizi_cizgiler"] = ["x"]
    js = izole_dizin / "c2.json"
    rc, _, _ = _cli("--dogrula", _yaz(izole_dizin, d), "--json", js)
    assert rc == 0
    veri = json.loads(js.read_text(encoding="utf-8"))
    assert veri["senaryo_okuma"] == "risk"
    assert len(veri["senaryo_bosluklari"]) == 16 * 3
    assert {b["neden"] for b in veri["senaryo_bosluklari"]} == {"alan_yok"}
    assert veri["senaryo_matrisi"]["gizlilik"] == {
        s: "belirsiz" for s in SENARYOLAR}


def test_json_bloklayan_sorunda_da_yazilir_exit_alani_1(izole_dizin):
    """Exit 1'de JSON yine yazılır (pipeline defteri blok sebebini de okur)."""
    d = _dolu()
    d["mod"] = "TAHRIR | INCELEME"
    js = izole_dizin / "c3.json"
    rc, _, _ = _cli("--dogrula", _yaz(izole_dizin, d), "--json", js)
    assert rc == 1
    veri = json.loads(js.read_text(encoding="utf-8"))
    assert veri["exit"] == 1
    assert any("tanınmayan mod" in s for s in veri["sorunlar"])
    assert veri["senaryo_okuma"] == "belirsiz"


# --------------------------------------------------------------------------
# 6) SKILL.md — 7. adım + kategori ilişkisi + teyitli çıpalar
# --------------------------------------------------------------------------
def test_skill_md_tahrir_yedinci_adim_uc_senaryo_ve_cipalar():
    skill = (SKILL_KOK / "SKILL.md").read_text(encoding="utf-8")
    tahrir = skill.split("## TAHRİR modu", 1)[1].split("## İNCELEME", 1)[0]
    assert "7. **Üç senaryo testi" in tahrir
    for parca in ("normal ifa", "gecikme", "fesih", "senaryo_testi",
                  "delil_sozlesmesi", "bildirim_tebligat",
                  "TBK m.117", "m.125", "m.126", "Mevzuat MCP teyit"):
        assert parca in tahrir, parca
    assert "İFA SENARYO MATRİSİ" in skill
    # İNCELEME modunda risk yönü okuması belgelenmiş olmalı
    inceleme = skill.split("## İNCELEME", 1)[1].split("## Aktif çıkarım", 1)[0]
    assert "calismaz" in inceleme and "aleyhine" in inceleme
