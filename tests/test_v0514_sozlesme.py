# -*- coding: utf-8 -*-
"""v0.5.14 — oa-sozlesme / sozlesme_denetim.py KARAKTERİZASYON + ONARIM testleri.

Bu script v0.5.13'e kadar **hiçbir teste bağlı değildi** (ölçüldü:
`grep -rl sozlesme_denetim tests/` → 0 isabet). Şema planı T12-Faz1 bu yüzden
önce 8 karakterizasyon testiyle mevcut davranışın kilitlenmesini emretti;
onarımlar (B-6, B-7, B-8, B-31, B-32) o zeminin ÜSTÜNE uygulandı.

Aşağıdaki karakterizasyon testlerinden üçü bilinçli olarak GÜNCELLENDİ
(karakterizasyon anı ile onarım sonrası davranış ayrımı her birinin
docstring'inde yazılıdır): `test_mod_kapisi_*` (B-8), `test_yok_gereksiz_*`
(B-6), `test_sekil_sarti_*` (B-7). Kalan beşi onarımlardan etkilenmeden
aynen geçer.

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; repo dosyalarına
dokunulmaz.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sozlesme"
          / "scripts" / "sozlesme_denetim.py")

KATEGORI_SIRASI = [
    "taraflar_temsil_imza_yetkisi", "konu_edimler", "bedel_odeme_ifa",
    "sure_uzama", "temerrut_cezai_sart_faiz", "fesih_tasfiye", "gizlilik",
    "kvkk_veri", "rekabet_yasagi_munhasirlik", "devir_temlik", "mucbir_sebep",
    "bildirim_tebligat", "uyusmazlik_cozumu", "delil_sozlesmesi",
    "butunluk_merger", "sekil_sarti",
]


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
    """B-7 sonrası `sekil_sarti` beyanı MCP teyit izi (madde + sorgu) ister."""
    return {"durum": "VAR", "risk": "orta",
            "not": "Mevzuat MCP teyidi: TBK m.583 sorgusu kosuldu",
            "onlem": "el yazili azami miktar metne islendi"}


def _dolu():
    """Denetimi TEMİZ geçen asgari dosya — her test tek değişkeni izole eder."""
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
    }
    d["kategoriler"]["sekil_sarti"] = _teyitli_sekil()
    return d


# --------------------------------------------------------------------------
# 1) İSKELET ŞEMASI — M1 vetosunun kanıt çıpası
# --------------------------------------------------------------------------
def test_iskelet_ust_seviye_sema_ve_onalti_kategori_exit0():
    """`--iskelet` üst-seviye anahtarları ve 16 kategorinin SIRASI kilitlenir.

    Tam-küme eşitliği BİLEREK kullanılmaz: T12-Faz2 (v0.5.17) yeni bir üst-
    seviye blok ekleyecek; asıl kilit kategori listesinin sırası ve tamlığıdır.
    """
    rc, out, _ = _cli("--iskelet")
    assert rc == 0
    veri = json.loads(out)
    assert {"mod", "tip", "kategoriler", "kirmizi_cizgiler",
            "acik_uclar"} <= set(veri.keys())
    assert list(veri["kategoriler"]) == KATEGORI_SIRASI
    for v in veri["kategoriler"].values():
        assert set(v) == {"durum", "risk", "not", "onlem"}


# --------------------------------------------------------------------------
# 2) MOD KAPISI — B-8
# --------------------------------------------------------------------------
def test_mod_kapisi_turkce_i_ve_redline_yazimlarinda_da_atesler(izole_dizin):
    """B-8 ONARIMI — karakterizasyon anında bu test tersini söylüyordu.

    KIRILAN KARAKTERİZASYON (bilinçli): v0.5.13'te kapı
    `mod.upper().startswith("INCELEME")` idi; ölçüldü →
    `'İNCELEME'.upper().startswith('INCELEME')` **False** (Türkçe İ, ASCII I'ya
    katlanmaz). Yani SKILL.md'nin öğrettiği iki yazım da ('İNCELEME' ve
    'REDLINE') kapıyı sessizce öldürüyordu. Onarım sonrası her ikisi de ateşler.
    Değişmeyen taraf: saf 'TAHRIR' ateşlemez.
    """
    for i, mod in enumerate(("İNCELEME", "INCELEME", "REDLINE",
                             "inceleme / redline", "İnceleme")):
        d = _dolu()
        d["mod"] = mod
        d["kirmizi_cizgiler"] = []
        rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, f"m_{i}.json"))
        assert rc == 1, f"{mod}: kırmızı çizgi kapısı ateşlemedi"
        assert "kırmızı çizgi listesi boş" in out

    d = _dolu()
    d["mod"] = "TAHRIR"
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "m_tahrir.json"))
    assert rc == 0 and "kırmızı çizgi listesi boş" not in out

    d = _dolu()
    d["mod"] = "İNCELEME"
    d["kirmizi_cizgiler"] = ["sorumluluk tavani kaldirilamaz"]
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "m_kc.json"))
    assert rc == 0 and "kırmızı çizgi listesi boş" not in out


def test_taninmayan_mod_sorundur(izole_dizin):
    """B-8 ikinci yarısı: `--iskelet` varsayılanı 'TAHRIR | INCELEME' hiçbir
    moda karşılık gelmiyordu ve sessizce TAHRİR'e düşüyordu — kırmızı çizgi
    kapısı o dosyada yapısal olarak ölüydü. Artık sorundur."""
    d = _dolu()
    d["mod"] = "TAHRIR | INCELEME"
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "m_bilinmez.json"))
    assert rc == 1
    assert "tanınmayan mod" in out


# --------------------------------------------------------------------------
# 3) SESSİZ ATLAMA — M1 vetosunun kanıt testi (onarımlardan etkilenmez)
# --------------------------------------------------------------------------
def test_zorunlu_kategori_anahtari_yoksa_sessiz_atlama_exit1(izole_dizin):
    d = _dolu()
    del d["kategoriler"]["gizlilik"]
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d))
    assert rc == 1
    assert "kategori tamamen atlanmış: gizlilik (sessiz atlama)" in out


# --------------------------------------------------------------------------
# 4) ENUM DENETİMİ + `continue` davranışı (onarımlardan etkilenmez)
# --------------------------------------------------------------------------
def test_gecersiz_durum_ve_risk_enumlari_exit1_ve_continue_davranisi(izole_dizin):
    """Geçersiz `durum` → `continue`: aynı kategorinin risk bandı HİÇ
    denetlenmez (tek satır sorun). Geçersiz `risk` → `continue` YOK."""
    d = _dolu()
    d["kategoriler"]["gizlilik"] = {"durum": "BELKI", "risk": "asiri",
                                   "not": "", "onlem": ""}
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "a.json"))
    assert rc == 1
    assert "gizlilik: geçersiz durum 'BELKI'" in out
    assert "geçersiz risk bandı" not in out

    d2 = _dolu()
    d2["kategoriler"]["gizlilik"]["risk"] = "asiri"
    rc2, out2, _ = _cli("--dogrula", _yaz(izole_dizin, d2, "b.json"))
    assert rc2 == 1
    assert "gizlilik: geçersiz risk bandı 'asiri'" in out2
    assert "'kritik'" in out2 or "kritik" in out2


# --------------------------------------------------------------------------
# 5) YOK-GEREKSIZ eşiği + YOK-EKSIK hükmü — B-6
# --------------------------------------------------------------------------
def test_yok_gereksiz_on_karakter_esigi_ve_yok_eksik_temiz_hukmunu_engeller(izole_dizin):
    """B-6 ONARIMI — karakterizasyon anında ikinci yarısı tersiydi.

    DEĞİŞMEYEN: `YOK-GEREKSIZ` + 10 karakterden kısa gerekçe → SORUN (exit 1).
    KIRILAN KARAKTERİZASYON (bilinçli): v0.5.13'te `YOK-EKSIK` yalnız uyarıydı
    ve ardından **"KAPSAM DENETİMİ TEMİZ."** basılıyordu — 16/16 EKSİK bile
    "temiz" damgası alıyordu (ölçüldü: `--iskelet` → `--dogrula` → EXIT=0 +
    TEMİZ). Artık en az bir EKSİK varken TEMİZ hükmü BASILMAZ; exit kodu
    (advisory) 0 kalır — saha dosyalarını toptan düşürmemek için bilinçli sınır.
    """
    d = _dolu()
    d["kategoriler"]["mucbir_sebep"] = {"durum": "YOK-GEREKSIZ", "risk": "yok",
                                        "not": "kisa", "onlem": ""}
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "kisa.json"))
    assert rc == 1 and "YOK-GEREKSIZ gerekçesiz olamaz" in out

    d2 = _dolu()
    d2["kategoriler"]["mucbir_sebep"] = {
        "durum": "YOK-GEREKSIZ", "risk": "yok",
        "not": "iliskide mucbir sebep riski yok, taraflar mutabik", "onlem": ""}
    rc2, out2, _ = _cli("--dogrula", _yaz(izole_dizin, d2, "uzun.json"))
    assert rc2 == 0 and "YOK-GEREKSIZ gerekçesiz olamaz" not in out2

    d3 = _dolu()
    d3["kategoriler"]["mucbir_sebep"]["durum"] = "YOK-EKSIK"
    rc3, out3, _ = _cli("--dogrula", _yaz(izole_dizin, d3, "eksik.json"))
    assert rc3 == 0
    assert "mucbir_sebep: EKSİK" in out3
    assert "KAPSAM DENETİMİ TEMİZ" not in out3


def test_hic_doldurulmamis_iskelet_temiz_sayilmaz_exit1(izole_dizin):
    """B-6'nın çekirdeği: `--iskelet` çıktısı hiç dokunulmadan doğrulanırsa
    v0.5.13'te 16 uyarı + **TEMİZ** + EXIT=0 veriyordu; "hiç dokunulmamış" ile
    "bilinçli olarak 16 eksik raporlandı" ayırt edilemiyordu. Bir otomasyon
    exit koduna baksa boş iskeleti geçirirdi. Artık SORUN (exit 1)."""
    rc0, iskelet_out, _ = _cli("--iskelet")
    assert rc0 == 0
    yol = _yaz(izole_dizin, json.loads(iskelet_out), "bos_iskelet.json")
    rc, out, _ = _cli("--dogrula", yol)
    assert rc == 1
    assert "hiç doldurulmamış" in out
    assert "KAPSAM DENETİMİ TEMİZ" not in out


def test_kismen_doldurulmus_dosya_iskelet_kapisina_takilmaz(izole_dizin):
    """İskelet kapısı DAR olmalı: tek bir kategori bile doldurulmuşsa
    "hiç doldurulmamış" hükmü verilemez (yanlış pozitif çıpası)."""
    rc0, iskelet_out, _ = _cli("--iskelet")
    veri = json.loads(iskelet_out)
    veri["kategoriler"]["gizlilik"] = {
        "durum": "VAR", "risk": "orta", "not": "gizlilik klozu var",
        "onlem": "sure ve istisna daraltildi"}
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, veri, "kismi.json"))
    assert "hiç doldurulmamış" not in out
    assert rc == 1  # mod hâlâ tanınmayan varsayılan (B-8)


# --------------------------------------------------------------------------
# 6) YÜKSEK RİSK ÖNLEM EŞİĞİ — 15 karakter sınır değeri (onarımdan etkilenmez)
# --------------------------------------------------------------------------
def test_yuksek_risk_onlem_onbes_karakter_sinir_degeri(izole_dizin):
    d = _dolu()
    d["kategoriler"]["gizlilik"].update({"risk": "yuksek", "onlem": "x" * 14})
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "r14.json"))
    assert rc == 1 and "risk=yuksek ama 'onlem' boş" in out

    d2 = _dolu()
    d2["kategoriler"]["gizlilik"].update({"risk": "yuksek", "onlem": "x" * 15})
    rc2, out2, _ = _cli("--dogrula", _yaz(izole_dizin, d2, "r15.json"))
    assert rc2 == 0 and "risk=yuksek ama 'onlem' boş" not in out2

    d3 = _dolu()
    d3["kategoriler"]["gizlilik"].update({"risk": "orta", "onlem": ""})
    rc3, out3, _ = _cli("--dogrula", _yaz(izole_dizin, d3, "orta.json"))
    assert rc3 == 0 and "onlem" not in out3


# --------------------------------------------------------------------------
# 7) ŞEKİL ŞARTI TEYİT KAPISI — B-7
# --------------------------------------------------------------------------
def test_sekil_sarti_teyit_izi_kategorinin_tamamina_baglidir(izole_dizin):
    """B-7 ONARIMI — kapı v0.5.13'te TERS kurulmuştu.

    KIRILAN KARAKTERİZASYON (bilinçli): teyit izi yalnız `durum == "VAR"`
    dalında ve yalnız **uyarı** olarak isteniyordu; asıl pahalı cevap olan
    `YOK-GEREKSIZ` 13 karakterlik "gerek yoktur." gerekçesiyle TEMİZ/EXIT=0
    alıyordu (ölçüldü: tip=kefalet). MCP teyidi (TBK m.583, birebir): kefalet
    sözleşmesi "yazılı şekilde yapılmadıkça ve kefilin sorumlu olacağı azamî
    miktar ile kefalet tarihi belirtilmedikçe geçerli olmaz" — şekil ihlali
    geçersizlik doğurur. Artık teyit izi kategorinin TAMAMINA bağlıdır (VAR ve
    YOK-GEREKSIZ) ve uyarı değil SORUNDUR; gerekçe karakter sayısıyla değil
    madde numarası + 'teyit' izi ile denetlenir.
    """
    for durum in ("VAR", "YOK-GEREKSIZ"):
        d = _dolu()
        d["tip"] = "kefalet"
        d["kategoriler"]["sekil_sarti"] = {
            "durum": durum, "risk": "yok",
            "not": "gerek yoktur, ezberden boyle bilinir", "onlem": ""}
        rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, f"s_{durum}.json"))
        assert rc == 1, f"{durum}: teyitsiz şekil şartı beyanı geçti"
        assert "sekil_sarti" in out and "teyit" in out

    # 'teyit' kelimesi var ama madde numarası yok → yine sorun (ezber çıpası)
    d1 = _dolu()
    d1["kategoriler"]["sekil_sarti"] = {
        "durum": "YOK-GEREKSIZ", "risk": "yok",
        "not": "teyit edildi, sekil sarti aranmiyor", "onlem": ""}
    rc1, out1, _ = _cli("--dogrula", _yaz(izole_dizin, d1, "s_maddesiz.json"))
    assert rc1 == 1 and "sekil_sarti" in out1

    d2 = _dolu()
    d2["tip"] = "kefalet"
    d2["kategoriler"]["sekil_sarti"] = _teyitli_sekil()
    rc2, out2, _ = _cli("--dogrula", _yaz(izole_dizin, d2, "s_teyitli.json"))
    assert rc2 == 0 and "sekil_sarti" not in out2

    # Üçüncü şık (T12 planının düzeltilmiş hâli): anahtar HİÇ yoksa şekil
    # şartı uyarısı DEĞİL, zorunlu kategori kapısı ateşler.
    d3 = _dolu()
    del d3["kategoriler"]["sekil_sarti"]
    rc3, out3, _ = _cli("--dogrula", _yaz(izole_dizin, d3, "s_yok.json"))
    assert rc3 == 1
    assert "kategori tamamen atlanmış: sekil_sarti" in out3
    assert "ezber şekil şartı" not in out3


def test_sekil_sarti_yok_eksik_iken_teyit_istenmez(izole_dizin):
    """Kapı yalnız BEYAN edilen iki durumda (VAR / YOK-GEREKSIZ) ateşler;
    'YOK-EKSIK' zaten eksiklik olarak raporlanır, üstüne teyit istenmez —
    aksi hâlde her yarım dosya çift kırmızı alırdı (gürültü disiplini)."""
    d = _dolu()
    d["kategoriler"]["sekil_sarti"] = {"durum": "YOK-EKSIK", "risk": "yok",
                                       "not": "", "onlem": ""}
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "s_eksik.json"))
    assert rc == 0
    assert "sekil_sarti: EKSİK" in out
    assert "teyit izi" not in out


# --------------------------------------------------------------------------
# 8) CLI KENAR DURUMLARI (onarımlardan etkilenmez)
# --------------------------------------------------------------------------
def test_cli_kenar_durumlari_bayraksiz_exit0_bozuk_girdi_coker(izole_dizin):
    rc, out, _ = _cli()
    assert rc == 0 and "usage" in out.lower()

    bozuk = izole_dizin / "bozuk.json"
    bozuk.write_text("{ bu json degil", encoding="utf-8")
    rc2, _, err2 = _cli("--dogrula", bozuk)
    assert rc2 != 0 and "JSONDecodeError" in err2

    rc3, _, err3 = _cli("--dogrula", izole_dizin / "yok.json")
    assert rc3 != 0 and "FileNotFoundError" in err3


# --------------------------------------------------------------------------
# 9) GEÇERLİLİK KATMANI — B-32 (şekil_sarti emsali: yalnız UYARI)
# --------------------------------------------------------------------------
def test_gecerlilik_katmani_yoksa_yalniz_uyari_exit_degismez(izole_dizin):
    """B-32: ehliyet (TMK m.9/m.15) + genel işlem koşulları (TBK m.20-25)
    ZORUNLU_KATEGORILER'e anahtar olarak EKLENMEZ — M1'in çürütmesi: yeni
    zorunlu anahtar sahadaki tüm mevcut sozlesme.json'ları exit 1 ile düşürür.
    `sekil_sarti` emsali: döngüden SONRA, tek satır UYARI."""
    d = _dolu()  # blok hiç yok — eski saha dosyası
    rc, out, _ = _cli("--dogrula", _yaz(izole_dizin, d, "g_yok.json"))
    assert rc == 0
    assert "geçerlilik katmanı" in out
    assert "ehliyet" in out and "genel işlem" in out

    d2 = _dolu()
    d2["gecerlilik_katmani"] = {
        "ehliyet_temsil": "imza sirkuleri gorULDU, temsil yetkisi kapsamda",
        "genel_islem_kosullari": "standart metin degil, muzakere edildi"}
    rc2, out2, _ = _cli("--dogrula", _yaz(izole_dizin, d2, "g_var.json"))
    assert rc2 == 0
    assert "geçerlilik katmanı" not in out2
    assert "KAPSAM DENETİMİ TEMİZ" in out2


def test_gecerlilik_katmani_bozuk_tip_cokmez_tek_satir_uyari(izole_dizin):
    """Gürültü disiplini (T12 risk #9): blok yok/bozuk/yarım iken alan adları
    DÖKÜLMEZ — tek satır. Bozuk tip traceback üretmez."""
    for bozuk in ("metin", 5, [], None):
        d = _dolu()
        d["gecerlilik_katmani"] = bozuk
        rc, out, err = _cli(
            "--dogrula",
            _yaz(izole_dizin, d, f"gb_{type(bozuk).__name__}.json"))
        assert rc == 0 and "Traceback" not in err
        satirlar = [s for s in out.splitlines() if "geçerlilik katmanı" in s]
        assert len(satirlar) == 1, f"{bozuk!r}: {satirlar}"


def test_iskelet_gecerlilik_katmani_blogunu_tasir_ama_tek_satir_uyarir(izole_dizin):
    """İskelet blokla gelir (keşfedilebilirlik), ama BOŞ geldiği için hükümde
    tek satır uyarı doğurur — 12 satır alan dökümü değil."""
    rc0, iskelet_out, _ = _cli("--iskelet")
    veri = json.loads(iskelet_out)
    assert "gecerlilik_katmani" in veri
    assert set(veri["gecerlilik_katmani"]) == {"ehliyet_temsil",
                                               "genel_islem_kosullari"}
    assert all(v == "" for v in veri["gecerlilik_katmani"].values())


# --------------------------------------------------------------------------
# 10) B-31 — risk bantları oa-sozlesme'nin KENDİ bantlarıdır
# --------------------------------------------------------------------------
def test_risk_bantlari_atfi_oa_stratejiye_baglanmaz():
    """B-31: SKILL.md risk bantlarını (kritik/yuksek/orta/dusuk/yok)
    `oa-strateji` bantlarına atfediyordu; oa-strateji'nin bantları ise
    OLASILIK bantlarıdır (güçlü/dengeli/zayıf/belirsiz) — kırık atıf.
    Ayrıca belgesiz beşinci bant `yok` artık açıkça tanımlıdır."""
    kok = REPO / "plugins" / "ortak-avukat" / "skills"
    skill = (kok / "oa-sozlesme" / "SKILL.md").read_text(encoding="utf-8")
    satirlar = [s for s in skill.splitlines() if "risk bandı" in s]
    assert satirlar, "risk bandı satırı kayboldu"
    assert not any("oa-strateji` bantları" in s for s in satirlar), \
        "kırık atıf geri geldi (oa-strateji OLASILIK bandı tanımlar, RİSK değil)"
    assert "`yok`" in skill, "beşinci bant (yok) hâlâ belgesiz"

    strateji = (kok / "oa-strateji" / "SKILL.md").read_text(encoding="utf-8")
    assert "güçlü / dengeli / zayıf / belirsiz" in strateji, \
        "atfın çürütüldüğü ölçüm çıpası kaydı: oa-strateji bantları OLASILIK"
