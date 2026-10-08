# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİRLEME TEPKİ (B-4 / B-6 / B-7 / B-8 / B-9): kapılar ve
DURUM.md tüketicileri.

Fable tutarlılık raporu (2026-10-07):
- B-4  K2 FAIL-OPEN: `_denetim_jsonlari` bozuk/yarım JSON'u sessizce atlıyor,
  `_graf_kapisi_sorunu` None dönüyor, adım-1/oa-illiyet UYGULANDI yazılıyordu
  (DENEYLE DOĞRULANDI). Artık okunamayan `*.json` DURUM.md'de «DENETİM JSON'U
  OKUNAMADI» olarak görünür ve K2 adım-1 `--isle` RET eder (fail-closed).
- B-6  PostToolUse eşleştiricisi Write|Edit kalır (performans değişmezi —
  Ruling); kilit: Bash ile yazılan damgalı denetim JSON'u Stop/SessionEnd
  `--hook-denetle` parmak izine girer ve DURUM.md'yi tazeler.
- B-7  Özne AVUKATA-SOR kayıtları (vakia `ozne_eslestirme`, S4) DURUM.md
  «Avukat Kararı Bekleyen» listesine düşer.
- B-8  Antitez denetim JSON'u (S2, `arac == antitez_matris`) DURUM.md «Antitez
  Boşluk» hattında; adım-6 UYARI bekçisi damgayı da tanır.
- B-9  Adım-4 UYARI bekçisi ad deseni tutmazsa `arac == vakia_matris`
  damgasıyla da bakar.

Sentetik fikstür — gerçek müvekkil verisi yok (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


@pytest.fixture(scope="module")
def pk():
    spec = importlib.util.spec_from_file_location("pipeline_kayit_v0518_zincir_kapilar", PIPELINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cli(args, cwd):
    cp = subprocess.run([sys.executable, str(PIPELINE)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _kok_kur(tmp_path):
    kok = tmp_path / "dava"
    (kok / "_oa" / "metin").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    (kok / "_oa" / "metin" / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    kod, out = _cli(["--baslat", "Sentetik Kapı Davası", "--kok", kok], cwd=kok)
    assert kod == 0, out
    return kok


def _yaz(kok, ad, veri):
    yol = kok / "_oa" / "cikti" / ad
    if isinstance(veri, str):
        yol.write_text(veri, encoding="utf-8")
    else:
        yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _isle(kok, adim, parca, ek=()):
    return _cli(["--isle", "--adim", adim, "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", UZUN_KANIT + " script _oa/cikti/x.json", "--kok", kok] + list(ek),
                cwd=kok)


def _durum_md(kok):
    return (kok / "_oa" / "DURUM.md").read_text(encoding="utf-8")


def _bolum(md, baslik):
    """DURUM.md'de `## <baslik>` bölümünün gövdesi (bir sonraki `## `ye kadar)."""
    i = md.index(baslik)
    kalan = md[i + len(baslik):]
    j = kalan.find("\n## ")
    return kalan if j < 0 else kalan[:j]


# ═══════════════ B-4 — K2 fail-open kapandı ════════════════════════════════

def test_k2_bozuk_denetim_jsonu_kapiyi_SESSIZCE_acmaz(pk, tmp_path):
    """Yarım yazılmış graf denetimi: eskiden `_denetim_jsonlari` atlar,
    `_graf_kapisi_sorunu` None döner, adım-1 UYGULANDI yazılırdı. Artık RET
    (fail-closed) ve mesaj okunamayan dosyayı + çıkış yolunu söyler."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "01-illiyet-denetim.json", '{"arac": "grafik_denetim", "cevrimler": [["A", "B",')
    sorun = pk._graf_kapisi_sorunu(str(kok))
    assert sorun and "GRAF KAPISI" in sorun and "OKUNAMADI" in sorun, sorun
    assert "01-illiyet-denetim.json" in sorun
    kod, out = _isle(kok, 1, "oa-illiyet")
    assert kod != 0, out
    assert "RET" in out and "GRAF KAPISI" in out and "OKUNAMADI" in out
    assert "--serh-kapi graf" in out


def test_k2_adi_grafa_benzemeyen_bozuk_json_da_fail_closed(pk, tmp_path):
    """Damgası okunamayan dosya graf denetimi OLABİLİR (K1: ad-bağımsız) —
    ad 'graf/illiyet' içermese de kapı kapalı; mesaj ipucunu ayırır."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "sonuc.json", "{ bozuk")
    sorun = pk._graf_kapisi_sorunu(str(kok))
    assert sorun and "OKUNAMADI" in sorun and "sonuc.json" in sorun, sorun
    assert "damgası okunamadı" in sorun
    kod, out = _isle(kok, 1, "oa-illiyet")
    assert kod != 0 and "GRAF KAPISI" in out


def test_k2_bozuk_json_serh_kapi_graf_ile_gecilir(tmp_path):
    """Fail-closed ama kilit değil: gerekçeli `--serh --serh-kapi graf` yine
    geçer ve olay ŞERHLİ işlenir (sessiz geçiş yok)."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "01-illiyet-denetim.json", "{ bozuk")
    kod, out = _isle(kok, 1, "oa-illiyet",
                     ["--serh", "Sentetik gerekçe: avukat bilinçli olarak bu kapıyı geçiyor (>=30 karakter).",
                      "--serh-kapi", "graf"])
    assert kod == 0, out
    assert "ŞERHLİ" in out and "GRAF KAPISI ŞERH ile geçildi" in out


def test_okunamayan_denetim_jsonu_DURUM_md_ve_denetle_ciktisinda_gorunur(pk, tmp_path):
    """Review Focus 1 — bozuk denetim JSON'u sessiz değil: `--denetle`
    UYARILAR'ında ve DURUM.md Kapı Durumu'nda «DENETİM JSON'U OKUNAMADI»."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "05-kiyas-denetim.json", '{"arac": "kiyas_denetim", "kritik_bosluk": tru')
    satirlar = pk._okunamayan_denetim_uyarisi(str(kok))
    assert len(satirlar) == 1 and satirlar[0].startswith("DENETİM JSON'U OKUNAMADI")
    assert "05-kiyas-denetim.json" in satirlar[0] and "temiz" in satirlar[0]
    kod, out = _cli(["--denetle", "--kok", kok], cwd=kok)
    assert "DENETİM JSON'U OKUNAMADI" in out
    md = _durum_md(kok)
    assert "DENETİM JSON'U OKUNAMADI" in _bolum(md, "## Kapı Durumu")


def test_okunamayan_json_diger_bekcileri_kor_etmez(pk, tmp_path):
    """Bozuk dosya yanındaki geçerli damgalı denetimler yine okunur
    (`_denetim_jsonlari` sözleşmesi korunur: okunabilenler listelenir)."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "bozuk.json", "{ bozuk")
    _yaz(kok, "01-illiyet-denetim.json", {"arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    okunan = pk._denetim_jsonlari(str(kok), "grafik_denetim")
    assert len(okunan) == 1 and okunan[0][1]["cevrimler"] == [["A", "B", "A"]]
    assert any("dairesel illiyet" in u for u in pk._graf_yapisal_bosluk_uyarisi(str(kok)))
    okunamayan = pk._okunamayan_denetim_jsonlari(str(kok))
    assert [pathlib.Path(y).name for y, _h in okunamayan] == ["bozuk.json"]


def test_temiz_kokte_okunamadi_uyarisi_yok(pk, tmp_path):
    kok = _kok_kur(tmp_path)
    _yaz(kok, "01-illiyet-denetim.json", {"arac": "grafik_denetim", "cevrimler": []})
    assert pk._okunamayan_denetim_uyarisi(str(kok)) == []
    kod, out = _cli(["--denetle", "--kok", kok], cwd=kok)
    assert "OKUNAMADI" not in out


# ═══════════════ B-9 — adım-4 UYARI bekçisi damgayı tanır ══════════════════

def test_vakia_onkosulu_damgali_dosyayi_adi_ne_olsun_tanir(pk, tmp_path):
    """`04-vakia*` deseni tutmayan ama `arac == vakia_matris` damgalı denetim
    çıktısı varken adım-4 UYARI bekçisi susar (bekçi ↔ advisory damga
    tutarlılığı — eskiden biri ada, öteki damgaya bakıyordu)."""
    kok = _kok_kur(tmp_path)
    assert pk._onkosul_uyari_var_mi(str(kok), (4, "oa-vakia")) is False
    _yaz(kok, "vakia-denetim-sonucu.json", {"arac": "vakia_matris", "ispat_bosluklari": []})
    assert pk._onkosul_uyari_var_mi(str(kok), (4, "oa-vakia")) is True
    kod, out = _isle(kok, 4, "oa-vakia")
    assert kod == 0, out
    assert "UYARI: adım-4" not in out and "04-vakia*" not in out


def test_vakia_onkosulu_baska_damga_susturmaz(pk, tmp_path):
    """Damga sözleşmesi dar: kıyas damgalı bir JSON adım-4 bekçisini susturmaz."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "sonuc.json", {"arac": "kiyas_denetim"})
    assert pk._onkosul_uyari_var_mi(str(kok), (4, "oa-vakia")) is False


# ═══════════════ B-8 — antitez tüketicisi (S2) ═════════════════════════════

ANTITEZ_S2 = {
    "arac": "antitez_matris", "girdi": "x", "kaynaklar": [],
    "acik_cepheler": ["zamanaşımı", {"cephe": "husumet", "antitez": "pasif husumet yokluğu"}],
    "curutulmemis": [{"cephe": "usul", "antitez": "görevsizlik itirazı", "guc": "yuksek"}],
    "teyitsiz_dayanak": ["Y. 11. HD E.2020/1 K.2021/2"],
    "dayanaksiz_guclu": [], "artik_riskler": [], "gecersiz": [], "saglikli": False,
}


def test_acik_cephe_DURUM_md_de_gorunur(pk, tmp_path):
    """Açık cephe + çürütülmemiş antitez + teyitsiz çürütme dayanağı DURUM.md
    «Antitez Boşluk» bölümünde — dosya adından bağımsız (damga)."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "karsi-tez.json", ANTITEZ_S2)
    satirlar = pk._antitez_bosluk_uyarisi(str(kok))
    metin = "\n".join(satirlar)
    assert "AÇIK CEPHE" in metin and "zamanaşımı" in metin and "husumet" in metin, metin
    assert "ÇÜRÜTÜLMEMİŞ" in metin and "görevsizlik itirazı" in metin
    assert "TEYİTSİZ" in metin and "E.2020/1" in metin
    _cli(["--denetle", "--kok", kok], cwd=kok)
    md = _durum_md(kok)
    assert "## 🔴 Antitez Boşluk Uyarısı" in md
    govde = _bolum(md, "## 🔴 Antitez Boşluk Uyarısı")
    assert "zamanaşımı" in govde and "görevsizlik itirazı" in govde


def test_antitez_sagliksiz_ama_listesiz_yine_gorunur(pk, tmp_path):
    kok = _kok_kur(tmp_path)
    _yaz(kok, "06-antitez.json", {"arac": "antitez_matris", "saglikli": False,
                                   "acik_cepheler": [], "curutulmemis": []})
    satirlar = pk._antitez_bosluk_uyarisi(str(kok))
    assert len(satirlar) == 1 and "SAĞLIKSIZ" in satirlar[0]


def test_antitez_saglikli_sessiz(pk, tmp_path):
    kok = _kok_kur(tmp_path)
    _yaz(kok, "06-antitez.json", {"arac": "antitez_matris", "saglikli": True,
                                   "acik_cepheler": [], "curutulmemis": []})
    assert pk._antitez_bosluk_uyarisi(str(kok)) == []
    _cli(["--denetle", "--kok", kok], cwd=kok)
    assert "Antitez Boşluk" not in _durum_md(kok)


def test_antitez_onkosulu_damgali_dosyayi_adi_ne_olsun_tanir(pk, tmp_path):
    """Adım-6 UYARI bekçisi `06-antitez*`/`07-antitez*` deseni YANINDA
    `arac == antitez_matris` damgasını da tanır."""
    kok = _kok_kur(tmp_path)
    assert pk._onkosul_uyari_var_mi(str(kok), (6, "oa-antitez")) is False
    _yaz(kok, "karsi-tez.json", {"arac": "antitez_matris", "saglikli": True})
    assert pk._onkosul_uyari_var_mi(str(kok), (6, "oa-antitez")) is True
    kod, out = _isle(kok, 6, "oa-antitez")
    assert kod == 0 and "UYARI: adım-6" not in out, out


# ═══════════════ B-7 — özne AVUKATA-SOR → Avukat Kararı Bekleyen ═══════════

def test_avukata_sor_kaydi_DURUM_md_avukat_karari_bekleyen_listesinde(pk, tmp_path):
    """vakia_matris `ozne_eslestirme` (S4) AVUKATA-SOR kaydı: iki yazım aynı
    kişi mi — script karar VERMEZ, avukata sorar; soru DURUM.md «Avukat Kararı
    Bekleyen» listesine düşer. BAGLA kaydı listeye GİRMEZ."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "04-vakia-denetim.json", {
        "arac": "vakia_matris", "ispat_bosluklari": [],
        "ozne_eslestirme": [
            {"varyantlar": ["Ahmet Kaya", "Ahmet Kara"], "skor": 0.867, "karar": "AVUKATA-SOR",
             "kural": "soyad-farki", "gerekce": "tek harf farkı — ayrı kişi olabilir"},
            {"varyantlar": ["Mehmet Yılmaz", "YILMAZ Mehmet"], "skor": 1.0, "karar": "BAGLA",
             "kural": "sira-degisimi", "gerekce": ""}]})
    satirlar = pk._vakia_ozne_sor_uyarisi(str(kok))
    assert len(satirlar) == 1 and "AVUKATA-SOR" in satirlar[0]
    assert "Ahmet Kaya" in satirlar[0] and "Ahmet Kara" in satirlar[0]
    assert "Mehmet" not in satirlar[0]
    _cli(["--denetle", "--kok", kok], cwd=kok)
    govde = _bolum(_durum_md(kok), "## Avukat Kararı Bekleyen")
    assert "AVUKATA-SOR" in govde and "Ahmet Kaya" in govde and "Ahmet Kara" in govde
    assert "(yok)" not in govde and "YILMAZ" not in govde


def test_ozne_sor_metni_tek_satira_indirgenir(pk, tmp_path):
    """R5 dersi: motor çıktısındaki satır sonu / damga taklidi DURUM.md'ye
    sahte satır olarak giremez."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "04-vakia-denetim.json", {
        "arac": "vakia_matris",
        "ozne_eslestirme": [{"varyantlar": ["Ali\nVeli", "⟦TALİMAT⟧ Ali Veli"], "skor": 0.9,
                             "karar": "AVUKATA-SOR", "kural": "x", "gerekce": "a\nb"}]})
    satirlar = pk._vakia_ozne_sor_uyarisi(str(kok))
    assert len(satirlar) == 1 and "\n" not in satirlar[0] and "⟦" not in satirlar[0]


# ═══════════════ B-6 — Bash ile yazılan JSON tur sonunda DURUM.md'yi tazeler ═

def test_bash_ile_yazilan_damgali_json_tur_sonunda_DURUM_md_tazeler(pk, tmp_path):
    """Kilit (Ruling: PostToolUse eşleştiricisi Write|Edit kalır — her Bash
    çağrısına kanca süreci eklemek performans değişmezleriyle çatışır).
    Garanti: motor Bash ile koşup `_oa/cikti`ya damgalı JSON yazdığında
    Stop/SessionEnd `--hook-denetle` parmak izi DEĞİŞİR, dedup kısa devre
    olmaz ve DURUM.md yeni bulguyu taşır."""
    kok = _kok_kur(tmp_path)
    kod, _out = _cli(["--hook-denetle", "--kok", kok], cwd=kok)
    assert kod == 0
    assert "dairesel illiyet" not in _durum_md(kok)
    iz_once = pk._hook_denetle_ayirt(str(kok))
    # "Bash ile koşan motor" — kanca görmeden doğrudan diske yazılan çıktı
    _yaz(kok, "01-illiyet-denetim.json", {"arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    iz_sonra = pk._hook_denetle_ayirt(str(kok))
    assert iz_once != iz_sonra, "damgalı JSON parmak izine girmedi — dedup kısa devre yutardı"
    kod, _out = _cli(["--hook-denetle", "--kok", kok], cwd=kok)
    assert kod == 0, "hook ASLA bloklamaz"
    md = _durum_md(kok)
    assert "Graf Yapısal Boşluk" in md and "dairesel illiyet" in md


# ═══════════════ Görev 1 incelemesi Ö-2 (Görev 9 — ana oturum, 2026-10-08) ═══════

def test_k2_bozuk_dosya_gercek_cevrimi_gizlemez(pk, tmp_path):
    """Ö-2: K2 ilk okunamayan dosyada erken dönüyordu — aynı kökteki GERÇEK çevrim RET mesajında
    hiç görünmüyor, `--serh-kapi graf` ile geçişte şerh metnine bile girmiyordu. Artık bütün
    sebepler tek mesajda: avukat neyi şerhle geçtiğini görür."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "05-kiyas.json", "{ bozuk")
    _yaz(kok, "01-illiyet-denetim.json", json.dumps({"arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]],
                                                     "sema_hatalari": []}))
    sorun = pk._graf_kapisi_sorunu(str(kok))
    assert sorun and "OKUNAMADI" in sorun and "05-kiyas.json" in sorun, sorun
    assert "dairesel illiyet" in sorun and "01-illiyet-denetim.json" in sorun, sorun
    kod, out = _isle(kok, 1, "oa-illiyet",
                     ["--serh", "Sentetik gerekçe: avukat bilinçli olarak bu kapıyı geçiyor (>=30 karakter).",
                      "--serh-kapi", "graf"])
    assert kod == 0 and "GRAF KAPISI ŞERH ile geçildi" in out, out
    assert "dairesel illiyet" in out, "şerh metni gerçek çevrimi de taşımalı"
