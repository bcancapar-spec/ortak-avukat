# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİRLEME TEPKİ (B-2 / B-3): çapraz denetim kapıya bağlanır,
ortak kimlik uzayı kimlik-önce çalışır.

Fable tutarlılık raporu (2026-10-07):
- B-2: `capraz_denetim.py` "ateşlemeyen kapı" idi — pipeline_kayit, teslim
  ve kancaların hiçbiri onu çağırmıyordu (yalnız SKILL talimatı). Artık
  `_capraz_bosluk_uyarisi(kok)` capraz_denetim'i İN-PROCESS yükler (CLAUDE.md
  #5), model girdilerini S1 `kaynaklar[rol=girdi]` üzerinden bulur (yoksa
  dizin taraması), kopukluğu DURUM.md'ye taşır; (5, oa-kiyas) önkoşulunda
  kopukluk UYARI'dır (bloklamaz — karar avukatın).
- B-3: `_eslesir` ≥4 karakter ALT-DİZE kapsamasıyla eşliyordu ('delil-1' ⊂
  'delil-12' → sahte eşleşme). Artık önce KİMLİK (S5: vakia `olaylar[].id`,
  kıyas `vakialar[].vakia_id`), yoksa KELİME SINIRLI ad eşleşmesi; tam olmayan
  eşleşme kopuk SAYILMAZ ama «ad-eşleşmesi (belirsiz)» etiketiyle GÖRÜNÜR.
  `_dosya_bul` damgalı denetim çıktısını model girdisi sanmaz.

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
CAPRAZ = SKILLS / "oa-pipeline" / "scripts" / "capraz_denetim.py"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cd():
    return _yukle("capraz_denetim_v0518_zincir", CAPRAZ)


@pytest.fixture(scope="module")
def pk():
    return _yukle("pipeline_kayit_v0518_zincir_capraz", PIPELINE)


def _cli(script, args, cwd=None):
    cp = subprocess.run([sys.executable, str(script)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(cwd) if cwd else None)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# Tutarlı üçlü (test_capraz_denetim.py ile aynı) ve kasıtlı kopuk üçlü.
GRAF_TEMIZ = {
    "dugumler": [{"id": "delil-1", "tip": "delil", "ad": "Sözleşme örneği"}],
    "kenarlar": [{"dayanak_delil": ["delil-1"]}],
}
VAKIA_TEMIZ = {
    "iddialar": [{"id": "iddia-1", "metin": "Taraflar sözleşme imzaladı"}],
    "olaylar": [{"olgu": "Taraflar sözleşme imzaladı", "belge": "Sözleşme örneği",
                 "ispat_durumu": "belgeli"}],
}
KIYAS_TEMIZ = {
    "buyuk_onerme": {"unsurlar": [{"id": "unsur-1"}]},
    "kucuk_onerme": {"vakialar": [{"metin": "Taraflar sözleşme imzaladı",
                                    "karsilar": ["unsur-1"],
                                    "dayanak_delil": ["delil-1"]}]},
}
GRAF_BOZUK = GRAF_TEMIZ
VAKIA_BOZUK = {
    "iddialar": [{"id": "iddia-1", "metin": "Ödeme yapılmadı"}],
    "olaylar": [{"olgu": "Ödeme yapılmadı", "belge": "Fatura no 123",
                 "ispat_durumu": "belgeli"}],
}
KIYAS_BOZUK = {
    "buyuk_onerme": {"unsurlar": [{"id": "unsur-1"}]},
    "kucuk_onerme": {"vakialar": [{"metin": "Taraflar hiç görüşmedi",
                                    "karsilar": ["unsur-99"],
                                    "dayanak_delil": ["delil-XYZ"]}]},
}


def _kok_kur(tmp_path):
    kok = tmp_path / "dava"
    (kok / "_oa" / "metin").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    (kok / "_oa" / "metin" / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    return kok


def _yaz(kok, ad, veri):
    yol = kok / "_oa" / "cikti" / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _baslat(kok):
    kod, out = _cli(PIPELINE, ["--baslat", "Sentetik Çapraz Davası", "--kok", kok], cwd=kok)
    assert kod == 0, out


def _durum_md(kok):
    return (kok / "_oa" / "DURUM.md").read_text(encoding="utf-8")


def _tipler(kopuk):
    return {k["tip"] for k in kopuk}


# ═══════════════ B-3 — kimlik önce, ad eşleşmesi kelime sınırlı ═════════════

def test_altdize_eslesmesi_yanlis_pozitif_uretmez(cd):
    """'delil-1' artık 'delil-12'nin içinde diye EŞLEŞMEZ; kelime sınırında
    geçen 'delil-1 banka dekontu' ise eşleşir."""
    assert cd._eslesir(cd._norm("delil-1"), {cd._norm("delil-12")}) is False
    assert cd._eslesir(cd._norm("delil-1"), {cd._norm("delil-1 banka dekontu")}) is True
    assert cd._eslesir(cd._norm("fatura"), {cd._norm("faturalar")}) is False
    assert cd._eslesir(cd._norm("Fatura no 12"), {cd._norm("Fatura no 123")}) is False
    # uçtan uca: vakıanın delili 'Fatura no 12', grafta yalnız 'Fatura no 123'
    graf = {"dugumler": [{"id": "d-123", "tip": "delil", "ad": "Fatura no 123"}],
            "kenarlar": [{"dayanak_delil": ["d-123"]}]}
    vakia = {"iddialar": [], "olaylar": [{"olgu": "Ödeme", "belge": "Fatura no 12",
                                          "ispat_durumu": "belgeli"}]}
    kopuk = cd.caprazla(graf, vakia, None)
    assert "DELIL_GRAFTA_YOK" in _tipler(kopuk), kopuk


def test_kimlik_esitligi_once_gelir(cd):
    """S5: kıyas vakıası `vakia_id` taşıyorsa ad hiç uymasa da kimlik eşitliği
    yeter; kimlik verilmiş ama vakıada YOKSA ad uysa bile KOPUK."""
    vakia = {"iddialar": [],
             "olaylar": [{"id": "o-1", "olgu": "Taraflar 12.03.2024'te sözleşme imzaladı",
                          "belge": "Sözleşme örneği", "ispat_durumu": "belgeli"}]}
    kiyas_id_ile = {"buyuk_onerme": {"unsurlar": [{"id": "u-1"}]},
                    "kucuk_onerme": {"vakialar": [{"vakia_id": "o-1", "metin": "akit kuruldu",
                                                    "karsilar": ["u-1"], "dayanak_delil": []}]}}
    assert "KIYAS_VAKIA_VAKIADA_YOK" not in _tipler(cd.caprazla(None, vakia, kiyas_id_ile))
    kiyas_yanlis_id = {"buyuk_onerme": {"unsurlar": [{"id": "u-1"}]},
                       "kucuk_onerme": {"vakialar": [{"vakia_id": "o-99",
                                                       "metin": "Taraflar 12.03.2024'te sözleşme imzaladı",
                                                       "karsilar": ["u-1"], "dayanak_delil": []}]}}
    kopuk = cd.caprazla(None, vakia, kiyas_yanlis_id)
    assert "KIYAS_VAKIA_VAKIADA_YOK" in _tipler(kopuk)
    assert any("o-99" in k["mesaj"] for k in kopuk), kopuk


def test_ad_eslesmesi_belirsiz_etiketiyle_gorunur(cd, tmp_path):
    """Kimlik yokken tam olmayan (kelime sınırlı kapsama) ad eşleşmesi kopuk
    SAYILMAZ ama sessiz de kalmaz: «ad-eşleşmesi (belirsiz)» etiketi hem
    `caprazla_ayrintili`de hem CLI/JSON çıktısında görünür."""
    vakia = {"iddialar": [],
             "olaylar": [{"olgu": "Ödeme yapılmadı ve ihtar çekildi", "belge": "İhtarname",
                          "ispat_durumu": "belgeli"}]}
    kiyas = {"buyuk_onerme": {"unsurlar": [{"id": "u-1"}]},
             "kucuk_onerme": {"vakialar": [{"metin": "Ödeme yapılmadı",
                                             "karsilar": ["u-1"], "dayanak_delil": []}]}}
    kopuk, belirsiz = cd.caprazla_ayrintili(None, vakia, kiyas)
    assert "KIYAS_VAKIA_VAKIADA_YOK" not in _tipler(kopuk)
    assert len(belirsiz) == 1 and "ad-eşleşmesi (belirsiz)" in belirsiz[0]["mesaj"]
    assert cd.caprazla(None, vakia, kiyas) == kopuk      # eski sözleşme korunur

    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "04-vakia.json").write_text(json.dumps(vakia, ensure_ascii=False), encoding="utf-8")
    (cikti / "05-kiyas.json").write_text(json.dumps(kiyas, ensure_ascii=False), encoding="utf-8")
    json_yol = tmp_path / "capraz.json"
    kod, out = _cli(CAPRAZ, ["--cikti-dizin", cikti, "--json", json_yol])
    assert kod == 0, out                                  # belirsizlik kopukluk değil
    assert "ad-eşleşmesi (belirsiz)" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["kopuk_sayisi"] == 0 and sonuc["belirsiz_sayisi"] == 1
    assert "ad-eşleşmesi (belirsiz)" in sonuc["belirsiz_eslesmeler"][0]["mesaj"]


def test_tam_ad_eslesmesi_belirsiz_sayilmaz(cd):
    """Birebir (normalize) eşleşme kesindir — etiket gürültüsü üretmez."""
    kopuk, belirsiz = cd.caprazla_ayrintili(GRAF_TEMIZ, VAKIA_TEMIZ, KIYAS_TEMIZ)
    assert kopuk == [] and belirsiz == []


def test_denetim_ciktisi_girdi_sanilmaz(cd, tmp_path):
    """`04-vakia-denetim.json` (arac damgalı, sıralamada önce gelir) model
    girdisi DEĞİLDİR; `_dosya_bul` damgasız `04-vakia.json`u seçer."""
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "04-vakia-denetim.json").write_text(
        json.dumps({"arac": "vakia_matris", "ispat_bosluklari": []}), encoding="utf-8")
    (cikti / "04-vakia.json").write_text(json.dumps(VAKIA_TEMIZ, ensure_ascii=False),
                                         encoding="utf-8")
    secilen = cd._dosya_bul(str(cikti), None, cd.ANAHTAR["vakia"])
    assert pathlib.Path(secilen).name == "04-vakia.json"
    # yalnız damgalı dosya varsa: girdi YOK (denetim çıktısı girdi sayılmaz)
    (cikti / "04-vakia.json").unlink()
    assert cd._dosya_bul(str(cikti), None, cd.ANAHTAR["vakia"]) is None


def test_bozuk_json_dosya_bul_tarafindan_hala_aday(cd, tmp_path):
    """Damga süzgeci yalnız ÇÖZÜLEN JSON'a bakar: bozuk dosya aday kalır ki
    `main` onu 'okunamadı' diye GÖRÜNÜR raporlasın (sessiz eleme yok)."""
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "04-vakia.json").write_text("{ bozuk", encoding="utf-8")
    secilen = cd._dosya_bul(str(cikti), None, cd.ANAHTAR["vakia"])
    assert pathlib.Path(secilen).name == "04-vakia.json"


# ═══════════════ B-2 — pipeline_kayit kapıya bağlar ═════════════════════════

def test_kopuk_uclu_DURUM_md_de_gorunur(pk, tmp_path):
    """Kasıtlı kopuk üçlü dizinde dururken `--denetle` → DURUM.md «Çapraz
    Denetim» bölümü kopukluk tiplerini söyler (bloklamaz: advisory)."""
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _yaz(kok, "01-illiyet-graf.json", GRAF_BOZUK)
    _yaz(kok, "04-vakia.json", VAKIA_BOZUK)
    _yaz(kok, "05-kiyas.json", KIYAS_BOZUK)

    satirlar = pk._capraz_bosluk_uyarisi(str(kok))
    assert satirlar and all(s.startswith("ÇAPRAZ") for s in satirlar), satirlar
    metin = "\n".join(satirlar)
    for tip in ("DELIL_GRAFTA_YOK", "KIYAS_VAKIA_VAKIADA_YOK",
                "KIYAS_DELIL_BILINMIYOR", "KIYAS_UNSUR_YOK"):
        assert tip in metin, metin

    _cli(PIPELINE, ["--denetle", "--kok", kok], cwd=kok)
    md = _durum_md(kok)
    assert "## 🔴 Çapraz Denetim Uyarısı" in md
    assert "DELIL_GRAFTA_YOK" in md and "KIYAS_UNSUR_YOK" in md


def test_temiz_uclude_capraz_bolumu_yok(pk, tmp_path):
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _yaz(kok, "01-illiyet-graf.json", GRAF_TEMIZ)
    _yaz(kok, "04-vakia.json", VAKIA_TEMIZ)
    _yaz(kok, "05-kiyas.json", KIYAS_TEMIZ)
    assert pk._capraz_bosluk_uyarisi(str(kok)) == []
    _cli(PIPELINE, ["--denetle", "--kok", kok], cwd=kok)
    assert "Çapraz Denetim" not in _durum_md(kok)


def test_capraz_girdileri_S1_kaynaklar_uzerinden_bulunur(pk, tmp_path):
    """Model girdileri standart ad taşımıyor (`g.json`/`v.json`/`k.json` —
    dizin taraması bulamaz); damgalı denetim JSON'larının S1 `kaynaklar
    [rol=girdi]` beyanı onları gösterir → kopukluk yine görünür."""
    kok = _kok_kur(tmp_path)
    _yaz(kok, "g.json", GRAF_BOZUK)
    _yaz(kok, "v.json", VAKIA_BOZUK)
    _yaz(kok, "k.json", KIYAS_BOZUK)
    assert pk._capraz_bosluk_uyarisi(str(kok)) == []        # beyan yok, ad yok → bulunamaz
    for arac, girdi in (("grafik_denetim", "cikti/g.json"), ("vakia_matris", "cikti/v.json"),
                        ("kiyas_denetim", "cikti/k.json")):
        _yaz(kok, f"denetim-{arac}.json", {
            "arac": arac,
            "kaynaklar": [{"rol": "girdi", "yol": girdi, "sha8": "00000000"}]})
    metin = "\n".join(pk._capraz_bosluk_uyarisi(str(kok)))
    assert "DELIL_GRAFTA_YOK" in metin and "KIYAS_UNSUR_YOK" in metin, metin


def test_capraz_S1_yolu_oa_disina_kacamaz(pk, tmp_path):
    """Beyan edilen girdi yolu `_oa` dışına çıkıyorsa OKUNMAZ (yol-kaçış
    koruması tazelik `_guvenli_yol` ile aynı sınır)."""
    kok = _kok_kur(tmp_path)
    disari = tmp_path / "disari-vakia.json"
    disari.write_text(json.dumps(VAKIA_BOZUK, ensure_ascii=False), encoding="utf-8")
    _yaz(kok, "01-illiyet-graf.json", GRAF_BOZUK)
    _yaz(kok, "denetim-vakia.json", {
        "arac": "vakia_matris",
        "kaynaklar": [{"rol": "girdi", "yol": "../../disari-vakia.json", "sha8": "00000000"}]})
    # yalnız graf yüklenebilir (vakıa dışarıda) → en az iki dosya yok → sessiz
    assert pk._capraz_bosluk_uyarisi(str(kok)) == []


def test_capraz_modulu_paylasimli_anahtarla_yukler(pk):
    mod = pk._capraz_denetim_modulu()
    assert mod is not None and callable(getattr(mod, "caprazla", None))
    assert sys.modules.get(pk._OA_PAYLASIMLI_CAPRAZ) is mod
    assert pk._capraz_denetim_modulu() is mod


def _kiyas_onkosulu_kur(kok, graf, vakia, kiyas):
    """(5, oa-kiyas) BLOKLEYİCİ önkoşulu karşılayan artefaktlar + üçlü."""
    _yaz(kok, "01-illiyet-graf.json", graf)
    _yaz(kok, "04-vakia.json", vakia)
    _yaz(kok, "05-kiyas.json", kiyas)
    _yaz(kok, "05-kiyas-denetim.json", {"arac": "kiyas_denetim", "kritik_bosluk": False,
                                         "unsur_vakia_eslesme": [], "teyitsiz_ictihat": [],
                                         "dolgu": "x" * 200})
    (kok / "_oa" / "cikti" / "ornek-ictihat-muhakeme.md").write_text(
        "Muhakeme gövdesi " * 10, encoding="utf-8")


def test_kiyas_onkosulu_kopuk_referansta_UYARI(tmp_path):
    """(5, oa-kiyas) UYGULANDI yazılırken üçlü kopuksa RET DEĞİL, görünür
    UYARI (avukat kararı: karar avukatın). Kıyasın kendi artefaktı
    (`05-kiyas*` + muhakeme) yerinde — kapı o yüzden açık."""
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _kiyas_onkosulu_kur(kok, GRAF_BOZUK, VAKIA_BOZUK, KIYAS_BOZUK)
    kod, out = _cli(PIPELINE, ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum",
                               "UYGULANDI", "--kanit",
                               UZUN_KANIT + " script _oa/cikti/05-kiyas-denetim.json",
                               "--kok", kok], cwd=kok)
    assert kod == 0, out
    assert "UYARI" in out and "ÇAPRAZ DENETİM" in out and "kopuk" in out.lower(), out


def test_kiyas_onkosulu_temiz_uclude_capraz_uyarisi_yok(tmp_path):
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _kiyas_onkosulu_kur(kok, GRAF_TEMIZ, VAKIA_TEMIZ, KIYAS_TEMIZ)
    kod, out = _cli(PIPELINE, ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum",
                               "UYGULANDI", "--kanit",
                               UZUN_KANIT + " script _oa/cikti/05-kiyas-denetim.json",
                               "--kok", kok], cwd=kok)
    assert kod == 0, out
    assert "ÇAPRAZ DENETİM" not in out
