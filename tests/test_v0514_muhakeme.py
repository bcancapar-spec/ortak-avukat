# -*- coding: utf-8 -*-
"""v0.5.14 — MUHAKEME MOTORLARI paketi (vakia · kiyas · antitez).

Kapatılan bulgular (bkz. DENETIM-CELISKI-KIRIK.md + PLAN-SEMA-PAKETI.md):

  B-10 / T5A  `vakia_matris` "belgeli" hesabı NEGATİF listeye dayanıyordu
              (`ispat_durumu != "ispatsiz"`); geçersiz bir etiket (`"video"`)
              dolu belgeyle iddiayı "belgeli" sayıyor, `ispat_bosluklari`
              boş çıkıyordu. POZİTİF BEYAZ LİSTEye çevrildi ve ISPAT kümesi
              üçe bölündü (ISPAT_TAM / ISPAT_KISMI={"beyan"} / "ispatsiz").
  B-11        `kiyas_denetim` norm unsurlara HİÇ ayrılmamışken subsumtion
              denetimi yapılmadığı hâlde "SONUÇ: Yapı bütün." +
              `kritik_bosluk=False` basıyordu (sessiz yanlış-yeşil).
              Ayrıca `karsilar` TANIMSIZ bir unsura işaret eden vakıa ne
              eşleşiyor ne yetim sayılıyordu — tamamen görünmezdi.
  T7/T8       `ispat_yuku` carve-out'u: yükü karşı tarafta olan unsur artık
              kritik boşluk sayılmaz — AMA yalnız ÜÇ ŞART birlikte varsa
              (`ispat_yuku == "karsi_taraf"` + dolu `ispat_yuku_kaynak` +
              boş olmayan `curutme_hazirligi`). Tek token ile yeşil satın
              alınamaz (fail-CLOSED).
  B-12        Boş girdi "TAMAM" sayılıyordu — `vakia_matris` için ayrı
              "DENETLENEMEDİ" sonuç sınıfı. (Exit kodu sözleşmesi bilinçli
              olarak DEĞİŞTİRİLMEDİ — kiyas'ın exit 0 kararı yazılı bir
              avukat kararıdır.)
  B-23        JSON kökü sözlük değilse (null / [] / "str") motorlar ham
              traceback ile çöküyordu; artık temiz mesaj + exit 1.
  B-26        `--iskelet` çıktısı geçerli JSON değildi (insan raporu +
              son satır düz metin). SKILL.md'nin kendi öğrettiği
              `--iskelet > _oa/cikti/04-vakia.json` kullanımı sessizce
              kullanılamaz dosya üretiyordu. Artık JSON stdout'a, banner
              ve açıklamalar stderr'e gider.

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
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
VAKIA = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
KIYAS = SKILLS / "oa-kiyas" / "scripts" / "kiyas_denetim.py"
ANTITEZ = SKILLS / "oa-antitez" / "scripts" / "antitez_matris.py"


def _kos(script, *args):
    cp = subprocess.run(
        [sys.executable, str(script), *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


@pytest.fixture
def izole_dizin():
    return pathlib.Path(tempfile.mkdtemp())


def _yaz(dizin, ad, veri):
    yol = dizin / ad
    if isinstance(veri, str):
        yol.write_text(veri, encoding="utf-8")
    else:
        yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


# ═══════════════════════════════════════════════════════════════════════════
# oa-vakia — B-10 / T5A / B-12 / B-23 / B-26
# ═══════════════════════════════════════════════════════════════════════════

def _vakia_saglikli():
    return {
        "iddialar": [{"id": "I1", "metin": "Sozlesme kuruldu"}],
        "olaylar": [
            {"tarih": "2025-01-10", "olgu": "Sozlesme imzalandi",
             "belge": "yazili sozlesme", "destekler": ["I1"],
             "ispat_durumu": "belgeli"},
        ],
    }


# ── B-26: --iskelet saf JSON ────────────────────────────────────────────────

def test_vakia_iskelet_stdout_gecerli_json():
    """B-26: `vakia_matris.py --iskelet > 04-vakia.json` SKILL.md'nin kendi
    öğrettiği kullanımdır; stdout tek başına ayrıştırılabilir JSON olmalı."""
    kod, out, err = _kos(VAKIA, "--iskelet")
    assert kod == 0
    sablon = json.loads(out)          # ← ham metin karışırsa JSONDecodeError
    assert set(sablon) == {"taraflar", "iddialar", "olaylar"}
    assert sablon["olaylar"][0]["destekler"] == ["I1"]


def test_vakia_iskelet_banner_stderre_gider_ve_beyan_listede():
    """B-26 + T5A-A10: insan-okur banner/açıklama stderr'e taşındı; ISPAT
    kümesi artık `beyan`ı da içerir (ISPAT_TAM | ISPAT_KISMI | ispatsiz)."""
    kod, out, err = _kos(VAKIA, "--iskelet")
    assert kod == 0
    assert "VAKIA/DELİL MATRİSİ" in err
    assert "VAKIA/DELİL MATRİSİ" not in out
    assert ("ispat_durumu değerleri: belgeli, beyan, bilirkisi, ikrar, "
            "ispatsiz, karine, tanik, yemin") in err
    assert "beyan" in json.loads(out)["olaylar"][0]["ispat_durumu"]


# ── B-10 / T5A: pozitif beyaz liste ─────────────────────────────────────────

def test_vakia_gecersiz_etiket_dolu_belgeyle_belgeli_SAYILMAZ(izole_dizin):
    """B-10 (fail-open kapanışı): `ispat_durumu: "video"` kapalı kümede
    yoktur; dolu bir `belge` alanı olsa bile iddiayı BELGELİ yapmamalı ve
    iddia `ispat_bosluklari`na düşmelidir. (Bugüne kadar 'belgeli destekli:
    1 | ispat boşluğu: 0' basılıyordu.)"""
    veri = {
        "iddialar": [{"id": "I1", "metin": "Gecersiz etiketli destek"}],
        "olaylar": [{"tarih": "2025-02-01", "olgu": "Video kayitli olay",
                     "belge": "usb", "destekler": ["I1"],
                     "ispat_durumu": "video"}],
    }
    yol = _yaz(izole_dizin, "vakia.json", veri)
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _kos(VAKIA, "--dogrula", yol, "--json", hedef)
    assert kod == 0
    assert "İddia: 1 | belgeli destekli: 0 | ispat boşluğu: 1" in out
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))
    assert sonuc["ispat_bosluklari"] == ["I1"]
    assert sonuc["iddia_delil_matrisi"][0]["belgeli"] is False


def test_vakia_beyan_kismi_destek_iddiayi_belgeli_yapmaz(izole_dizin):
    """T5A: `beyan` ISPAT_KISMI sınıfıdır — tek başına iddiayı belgeli
    yapmaz, `kismi_destek: True` ile işaretlenir ve boşluğa düşer."""
    veri = {
        "iddialar": [{"id": "I1", "metin": "Yalniz beyanla desteklenen iddia"}],
        "olaylar": [{"tarih": "2025-02-01", "olgu": "Muvekkil beyani",
                     "belge": "ifade tutanagi", "destekler": ["I1"],
                     "ispat_durumu": "beyan"}],
    }
    yol = _yaz(izole_dizin, "vakia.json", veri)
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _kos(VAKIA, "--dogrula", yol, "--json", hedef)
    assert kod == 0
    assert "GEÇERSİZ ispat_durumu" not in out       # beyan GEÇERLİ bir etikettir
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is False
    assert satir["kismi_destek"] is True
    assert sonuc["ispat_bosluklari"] == ["I1"]


def test_vakia_kismi_destek_alt_satiri_yalniz_belgeli_yokken_basilir(izole_dizin):
    """T5A-A5b (R2 daraltması): `↳ yalnız KISMİ destek` satırı, iddianın
    hiç belgeli desteği yokken basılır."""
    veri = {
        "iddialar": [{"id": "I1", "metin": "Beyanla destekli"}],
        "olaylar": [{"tarih": "2025-02-01", "olgu": "Beyan", "belge": "tutanak",
                     "destekler": ["I1"], "ispat_durumu": "beyan"}],
    }
    yol = _yaz(izole_dizin, "vakia.json", veri)
    kod, out, err = _kos(VAKIA, "--dogrula", yol)
    assert kod == 0
    assert "⚠ İSPAT BOŞLUĞU: bu iddiayı destekleyen belgeli/somut delil yok" in out
    assert "↳ yalnız KISMİ destek (beyan) — tek başına belgeli sayılmaz" in out


def test_vakia_beyan_ve_belgeli_birlikte_ise_alt_satir_basilmaz(izole_dizin):
    """T5A-A5b: sağlıklı iddiada yetim `↳` satırı DOĞMAZ."""
    veri = {
        "iddialar": [{"id": "I1", "metin": "Hem belge hem beyan"}],
        "olaylar": [
            {"tarih": "2025-02-01", "olgu": "Sozlesme", "belge": "sozlesme",
             "destekler": ["I1"], "ispat_durumu": "belgeli"},
            {"tarih": "2025-02-02", "olgu": "Beyan", "belge": "tutanak",
             "destekler": ["I1"], "ispat_durumu": "beyan"},
        ],
    }
    yol = _yaz(izole_dizin, "vakia.json", veri)
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _kos(VAKIA, "--dogrula", yol, "--json", hedef)
    assert kod == 0
    assert "↳ yalnız KISMİ destek" not in out
    assert ">>> Dosya olgu/delil bütünlüğü TAMAM <<<" in out
    satir = json.loads(hedef.read_text(encoding="utf-8"))["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is True and satir["kismi_destek"] is True


def test_vakia_ust_duzey_json_semasi_DEGISMEDI(izole_dizin):
    """T5A YAPILMAYACAK kilidi: matris SATIRINA `kismi_destek` eklenir ama
    ÜST-DÜZEY JSON anahtar kümesi değişmez (yeni anahtar YOK)."""
    yol = _yaz(izole_dizin, "vakia.json", _vakia_saglikli())
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _kos(VAKIA, "--dogrula", yol, "--json", hedef)
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))
    assert set(sonuc.keys()) == {
        "arac", "girdi", "kronoloji", "tarihsiz", "iddia_delil_matrisi",
        "ispat_bosluklari", "yetim_deliller", "gecersiz_referans",
        "gecersiz_ispat_durumu", "ozne_eslestirme", "ozet", "saglikli",
    }
    assert set(sonuc["iddia_delil_matrisi"][0].keys()) == {
        "iddia_id", "metin", "destekler", "belgeli", "kismi_destek"}


def test_vakia_kronoloji_satir_semasi_degismedi_regresyon(izole_dizin):
    """Regresyon çıpası: kronoloji satır biçimi ve JSON alanları T5A'dan
    etkilenmez."""
    yol = _yaz(izole_dizin, "vakia.json", _vakia_saglikli())
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _kos(VAKIA, "--dogrula", yol, "--json", hedef)
    assert "2025-01-10 | Sozlesme imzalandi  [delil: yazili sozlesme; belgeli]" in out
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))
    assert sonuc["kronoloji"][0] == {
        "tarih": "2025-01-10", "olgu": "Sozlesme imzalandi",
        "belge": "yazili sozlesme", "ispat_durumu": "belgeli"}


# ── B-12: boş girdi ayrı sonuç sınıfı ───────────────────────────────────────

def test_vakia_bos_girdi_TAMAM_sayilmaz(izole_dizin):
    """B-12: `{}` girdisi bugüne kadar '>>> Dosya olgu/delil bütünlüğü
    TAMAM <<<' basıyordu — '0 iddia = kusursuz dosya'. Artık ayrı
    DENETLENEMEDİ sınıfı. Exit kodu sözleşmesi DEĞİŞMEZ (0)."""
    yol = _yaz(izole_dizin, "vakia.json", {})
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _kos(VAKIA, "--dogrula", yol, "--json", hedef)
    assert kod == 0, "exit kodu sözleşmesi bilinçli olarak değişmedi"
    assert "TAMAM <<<" not in out
    assert "DENETLENEMEDİ" in out
    assert json.loads(hedef.read_text(encoding="utf-8"))["saglikli"] is False


# ── B-23: kök tipi sağlamlaştırması ─────────────────────────────────────────

def test_vakia_json_koku_liste_ise_temiz_mesaj_exit1(izole_dizin):
    """B-23: kök sözlük değilse ham AttributeError traceback'i yerine temiz
    mesaj + exit 1 (aile standardı)."""
    yol = _yaz(izole_dizin, "vakia.json", "[]")
    kod, out, err = _kos(VAKIA, "--dogrula", yol)
    assert kod == 1
    assert "Traceback" not in err
    assert "JSON kökü sözlük" in out


# ═══════════════════════════════════════════════════════════════════════════
# oa-kiyas — B-11 / T7-T8 / B-23
# ═══════════════════════════════════════════════════════════════════════════

def _kiyas_tek_unsur(unsur):
    """Tek unsurlu, vakıası olmayan kıyas — carve-out dallarını izole eder."""
    return {
        "buyuk_onerme": {
            "norm": "TBK m.49",
            "ictihat": [{"kunye": "Y.4.HD 2020/1 E.", "dogrulama": "teyitli"}],
            "unsurlar": [unsur],
        },
        "kucuk_onerme": {"vakialar": [{"metin": "Baska bir olgu",
                                       "karsilar": ["baska"],
                                       "dayanak_delil": ["x"]}]},
        "sonuc": "Taslak",
    }


# ── karakterizasyon (kod değişmeden de YEŞİL) ───────────────────────────────

def test_kiyas_ispat_yuku_alani_hic_yoksa_karsilanmamis_ve_kritik(izole_dizin):
    """Eski saha artefaktı çıpası: `ispat_yuku` alanı hiç yoksa varsayılan
    'bilinmiyor'dur ve eski davranış (KARŞILANMAMIŞ + kritik) aynen kalır."""
    yol = _yaz(izole_dizin, "kiyas.json",
               _kiyas_tek_unsur({"id": "kusur", "ad": "Kusur"}))
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    assert kod == 0
    assert "✗ [Kusur] ← KARŞILANMAMIŞ unsur" in out
    assert "KRİTİK BOŞLUK var" in out
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["kritik_bosluk"] is True
    assert veri["unsur_vakia_eslesme"][0]["durum"] == "karsilanmamis"


def test_kiyas_duz_string_unsurda_cokmez(izole_dizin):
    """`_unsur_alan` düz-string unsurda varsayılana düşer (R8: `vars`
    gölgelemesi yok, isinstance denetimi var)."""
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur("kusur"))
    kod, out, err = _kos(KIYAS, yol)
    assert kod == 0 and "Traceback" not in err
    assert "✗ [kusur] ← KARŞILANMAMIŞ unsur" in out


# ── T7/T8 carve-out (fail-CLOSED) ───────────────────────────────────────────

@pytest.mark.parametrize("unsur,neden", [
    ({"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf"},
     "kaynak da hazırlık da yok"),
    ({"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
      "ispat_yuku_kaynak": "TBK m.112 kusur karinesi"},
     "çürütme hazırlığı yok"),
    ({"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
      "curutme_hazirligi": ["bilirkişi raporu talebi"]},
     "kaynak gösterilmemiş"),
    ({"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
      "ispat_yuku_kaynak": "  ", "curutme_hazirligi": ["   "]},
     "ikisi de fiilen boş"),
])
def test_kiyas_kaynaksiz_veya_curutmesiz_yuk_karsida_carve_out_VERILMEZ(
        izole_dizin, unsur, neden):
    """PAKETİN EN KRİTİK KİLİDİ (Ö1). Model tek token (`ispat_yuku:
    karsi_taraf`) yazarak hem 'Yapı bütün' yeşilini hem DURUM.md
    kırmızısının yokluğunu SATIN ALAMAZ. Carve-out ÜÇ ŞART birliktedir."""
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    assert "KRİTİK BOŞLUK var" in out, neden
    assert "carve-out VERİLMEDİ" in out, neden
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["kritik_bosluk"] is True, neden
    assert veri["unsur_vakia_eslesme"][0]["durum"] == "karsilanmamis", neden


def test_kiyas_yuk_karsida_uc_sart_tamken_kritik_sayilmaz(izole_dizin):
    """Üç şart tamken unsur kritik boşluk SAYILMAZ; `durum` dördüncü
    değeri alır ve rapor DAHİLİ filigranlı §5 bölümünü basar."""
    unsur = {"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
             "ispat_yuku_kaynak": "TBK m.112 — kusur karinesi",
             "curutme_hazirligi": ["bilirkişi incelemesi talebi",
                                   "bakım kayıtları celbi"]}
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    assert kod == 0
    assert "⇄ [Kusur] ← vakıa yok — İSPAT YÜKÜ KARŞI TARAFTA" in out
    assert "KRİTİK BOŞLUK" not in out
    assert "SONUÇ: Yapı bütün." in out
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["kritik_bosluk"] is False
    assert veri["unsur_vakia_eslesme"][0]["durum"] == "ispat_yuku_karsida"


def test_kiyas_ispat_yuku_raporu_DAHILI_filigranli(izole_dizin):
    """R2: §5 İSPAT YÜKÜ bölümü dahili çürütme hazırlığını listeler; 40-UYAP
    sızıntısına karşı filigran ZORUNLUDUR."""
    unsur = {"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
             "ispat_yuku_kaynak": "TBK m.112",
             "curutme_hazirligi": ["bilirkişi talebi"]}
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    kod, out, _ = _kos(KIYAS, yol)
    assert "### 5. İSPAT YÜKÜ" in out
    assert "⚠ DAHİLİ — DOSYAYA EKLENMEZ / UYAP'A YÜKLENMEZ" in out
    assert "bilirkişi talebi" in out


def test_kiyas_yuk_bizdeyken_eski_davranis_aynen(izole_dizin):
    unsur = {"id": "k", "ad": "Kusur", "ispat_yuku": "bizde",
             "ispat_yuku_kaynak": "HMK m.190",
             "curutme_hazirligi": ["x"]}
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    kod, out, _ = _kos(KIYAS, yol)
    assert "✗ [Kusur] ← KARŞILANMAMIŞ unsur" in out
    assert "KRİTİK BOŞLUK var" in out
    assert "### 5. İSPAT YÜKÜ" not in out


def test_kiyas_enum_disi_deger_nitelendirilmez_bilinmiyor_sayilir(izole_dizin):
    """M1: script hukuki NİTELENDİRME yapmaz — kapalı enum dışı bir değeri
    yorumlamaz, görünür uyarı basıp 'bilinmiyor' sayar ve fail-closed kalır."""
    unsur = {"id": "k", "ad": "Kusur", "ispat_yuku": "belki karsida",
             "ispat_yuku_kaynak": "X", "curutme_hazirligi": ["y"]}
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    assert "ispat_yuku değeri kapalı enum dışında ('belki karsida')" in out
    assert "script nitelendirme yapmaz" in out
    assert "KRİTİK BOŞLUK var" in out
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["unsur_vakia_eslesme"][0]["durum"] == "karsilanmamis"


def test_kiyas_vakia_varsa_yuk_karsida_olsa_bile_durum_degismez(izole_dizin):
    """Carve-out YALNIZ karşılanmamış unsur dalındadır; vakıa varsa eski üç
    durumdan biri döner."""
    k = _kiyas_tek_unsur({"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
                          "ispat_yuku_kaynak": "TBK m.112",
                          "curutme_hazirligi": ["z"]})
    k["kucuk_onerme"]["vakialar"] = [{"metin": "Kusurlu davranis",
                                      "karsilar": ["k"],
                                      "dayanak_delil": ["tutanak"]}]
    yol = _yaz(izole_dizin, "kiyas.json", k)
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["unsur_vakia_eslesme"][0]["durum"] == "karsilanan_delilli"


def test_kiyas_yeni_ust_duzey_anahtar_URETMEZ(izole_dizin):
    """K1 ileri koruması: T7/T8 ve B-11 hiçbir yeni ÜST-DÜZEY JSON anahtarı
    üretmez (tüketici `pipeline_kayit.py` tam-küme okur)."""
    unsur = {"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
             "ispat_yuku_kaynak": "TBK m.112", "curutme_hazirligi": ["z"]}
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    hedef = izole_dizin / "sonuc.json"
    _kos(KIYAS, yol, "--json", hedef)
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert set(veri.keys()) == {
        "arac", "buyuk_onerme", "kucuk_onerme", "sonuc", "teyitsiz_ictihat",
        "unsur_vakia_eslesme", "yetim_vakialar", "kritik_bosluk", "girdi"}


def test_kiyas_eslesme_kaydi_yalniz_uc_anahtar_tasir(izole_dizin):
    """K4 ileri koruması: eşleşme kaydına yeni anahtar EKLENMEZ; carve-out
    bilgisi yalnız `durum` değerinde taşınır."""
    unsur = {"id": "k", "ad": "Kusur", "ispat_yuku": "karsi_taraf",
             "ispat_yuku_kaynak": "TBK m.112", "curutme_hazirligi": ["z"]}
    yol = _yaz(izole_dizin, "kiyas.json", _kiyas_tek_unsur(unsur))
    hedef = izole_dizin / "sonuc.json"
    _kos(KIYAS, yol, "--json", hedef)
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert set(veri["unsur_vakia_eslesme"][0].keys()) == {
        "unsur_id", "unsur_ad", "durum"}


def test_kiyas_durum_dort_degerli_kapali_kume(izole_dizin):
    """Dört durumun tamamı tek dosyada üretilir ve kapalı küme kilitlenir."""
    k = {
        "buyuk_onerme": {
            "norm": "TBK m.49",
            "ictihat": [{"kunye": "X", "dogrulama": "teyitli"}],
            "unsurlar": [
                {"id": "a", "ad": "Delilli"},
                {"id": "b", "ad": "Delilsiz"},
                {"id": "c", "ad": "Karsilanmamis"},
                {"id": "d", "ad": "Yuk karsida", "ispat_yuku": "karsi_taraf",
                 "ispat_yuku_kaynak": "TBK m.112", "curutme_hazirligi": ["q"]},
            ],
        },
        "kucuk_onerme": {"vakialar": [
            {"metin": "v1", "karsilar": ["a"], "dayanak_delil": ["d1"]},
            {"metin": "v2", "karsilar": ["b"], "dayanak_delil": []},
        ]},
        "sonuc": "Taslak",
    }
    yol = _yaz(izole_dizin, "kiyas.json", k)
    hedef = izole_dizin / "sonuc.json"
    _kos(KIYAS, yol, "--json", hedef)
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert [u["durum"] for u in veri["unsur_vakia_eslesme"]] == [
        "karsilanan_delilli", "karsilanan_delilsiz", "karsilanmamis",
        "ispat_yuku_karsida"]


# ── B-11: sessiz yanlış-yeşil ───────────────────────────────────────────────

def test_kiyas_unsursuz_norm_artik_kritik_bosluk(izole_dizin):
    """B-11: norm unsurlara HİÇ ayrılmamışsa subsumtion denetimi HİÇ
    yapılmamıştır; 'denetim yapılamadı' ile 'denetim geçti' aynı hükmü
    üretemez. Artık kritik boşluktur (fail-closed)."""
    k = _kiyas_tek_unsur({"id": "x", "ad": "X"})
    k["buyuk_onerme"]["unsurlar"] = []
    yol = _yaz(izole_dizin, "kiyas.json", k)
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    assert kod == 0, "exit kodu sözleşmesi (yazılı avukat kararı) değişmez"
    assert "SONUÇ: Yapı bütün." not in out
    assert "KRİTİK BOŞLUK var" in out
    assert "subsumtion denetimi YAPILAMADI" in out
    assert json.loads(hedef.read_text(encoding="utf-8"))["kritik_bosluk"] is True


def test_kiyas_tanimsiz_unsura_isaret_eden_vakia_yetim_sayilir(izole_dizin):
    """B-11 ikinci ayak: `karsilar` TANIMSIZ bir unsura işaret eden vakıa
    bugüne kadar ne eşleşiyor ne yetim sayılıyordu — tamamen görünmezdi."""
    k = {
        "buyuk_onerme": {"norm": "TBK m.49", "ictihat": [],
                         "unsurlar": [{"id": "fiil", "ad": "Fiil"}]},
        "kucuk_onerme": {"vakialar": [
            {"metin": "Gercek olgu", "karsilar": ["fiil"],
             "dayanak_delil": ["tutanak"]},
            {"metin": "Hayali unsura atif", "karsilar": ["U99"],
             "dayanak_delil": ["x"]},
        ]},
        "sonuc": "Taslak",
    }
    yol = _yaz(izole_dizin, "kiyas.json", k)
    hedef = izole_dizin / "sonuc.json"
    kod, out, _ = _kos(KIYAS, yol, "--json", hedef)
    assert "TANIMSIZ unsur" in out
    assert "✓ Her vakıa bir unsura bağlı." not in out
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["yetim_vakialar"] == ["Hayali unsura atif"]


# ── B-23: kök tipi / girdi hatası ───────────────────────────────────────────

def test_kiyas_json_koku_liste_ise_temiz_mesaj_exit1(izole_dizin):
    yol = _yaz(izole_dizin, "kiyas.json", "[]")
    kod, out, err = _kos(KIYAS, yol)
    assert kod == 1
    assert "Traceback" not in err
    assert "JSON kökü sözlük" in out


def test_kiyas_olmayan_dosya_ve_bozuk_json_temiz_mesaj_exit1(izole_dizin):
    kod, out, err = _kos(KIYAS, izole_dizin / "yok.json")
    assert kod == 1 and "Traceback" not in err
    assert "❌ JSON okunamadı" in out

    yol = _yaz(izole_dizin, "kiyas.json", "{ bozuk")
    kod, out, err = _kos(KIYAS, yol)
    assert kod == 1 and "Traceback" not in err
    assert "❌ JSON okunamadı" in out


# ═══════════════════════════════════════════════════════════════════════════
# oa-antitez — B-26 / B-23
# ═══════════════════════════════════════════════════════════════════════════

def test_antitez_iskelet_stdout_gecerli_json():
    """B-26: `antitez_matris.py --iskelet > antitez.json` doğrudan
    `dilekce_denetim` [G] kapısının okuduğu dosyayı üretebilmeli."""
    kod, out, err = _kos(ANTITEZ, "--iskelet")
    assert kod == 0
    sablon = json.loads(out)
    assert set(sablon) == {"tez", "cepheler"}
    assert len(sablon["cepheler"]) == 8
    assert sablon["cepheler"][0]["duyulmus"] is False


def test_antitez_iskelet_cephe_listesi_stderre_gider():
    kod, out, err = _kos(ANTITEZ, "--iskelet")
    assert "ANTİTEZ CEPHELERİ" in err
    assert "ANTİTEZ CEPHELERİ" not in out
    assert "[usul]" in err and "[muvekkil_zaaf]" in err


def test_antitez_json_koku_liste_ise_temiz_mesaj_exit1(izole_dizin):
    yol = _yaz(izole_dizin, "antitez.json", "[]")
    kod, out, err = _kos(ANTITEZ, "--dogrula", yol)
    assert kod == 1
    assert "Traceback" not in err
    assert "JSON kökü sözlük" in out


def test_antitez_bozuk_cephe_elemani_cokmez(izole_dizin):
    """B-23: `cepheler` içinde sözlük olmayan eleman (model çıktısı hatası)
    ham traceback üretmemeli; şema hatası olarak raporlanmalı."""
    veri = {"tez": "T", "cepheler": ["usul", {"cephe": "usul", "guc": "yok"}]}
    yol = _yaz(izole_dizin, "antitez.json", veri)
    kod, out, err = _kos(ANTITEZ, "--dogrula", yol)
    assert "Traceback" not in err
    assert "ŞEMA HATASI" in out
