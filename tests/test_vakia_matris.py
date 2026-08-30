# -*- coding: utf-8 -*-
"""Fable-tespitli TESTSİZ release-kapısı scriptlerinden biri olan
oa-vakia/vakia_matris.py için KARAKTERİZASYON testleri.

Bu dosya MEVCUT davranışı olduğu gibi KİLİTLER, değiştirmez. Script'in
deterministik vakıa/delil motoru davranışları koddan çıkarılıp aynen test
edilir; "tuhaf" görünen davranışlar da (aşağıda tek tek işaretli) mevcut
tasarım olarak belgelenir ve kilitlenir:

  * dogrula() sonunda sys.exit YOKTUR — dosya SAĞLIKSIZ (saglikli=false)
    olsa bile exit kodu 0'dır (karakterizasyon — mevcut tasarım).
  * YETİM delil (hiçbir iddiaya bağlanmamış olgu) raporlanır ama saglikli
    hesabına GİRMEZ; yalnız yetim varken dosya yine "TAMAM" sayılır
    (karakterizasyon — mevcut tasarım).
  * --iskelet ile verilen --json bayrağı sessizce yoksayılır, dosya
    yazılmaz (karakterizasyon — mevcut tasarım).
  * ispat_durumu alanı hiç yoksa geçersiz sayılır ve mesajda Python'un
    None temsili ("'None'") basılır (karakterizasyon — mevcut tasarım).

v0.5.14'te BİLİNÇLİ olarak güncellenen üç kilit + bir docstring (gerekçeler
ilgili testlerin kendi docstring'lerinde): --iskelet stdout'unun saf JSON
olması (B-26) · boş girdinin 'TAMAM' yerine 'DENETLENEMEDİ' sayılması
(B-12) · kök tipi hatasında traceback yerine temiz mesaj (B-23) · matris
satırına `kismi_destek` eklenmesi ve "belgeli" tanımının pozitif beyaz
listeye çevrilmesi (T5A/B-10).

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
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-vakia"
          / "scripts" / "vakia_matris.py")


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, cp.stdout or "", cp.stderr or ""


@pytest.fixture
def izole_dizin():
    return pathlib.Path(tempfile.mkdtemp())


def _vakia_yaz(dizin, veri):
    yol = dizin / "vakia.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _saglikli_vakia():
    """İki iddia, ikisi de belgeli destekli; olaylar KASITLI olarak tarih
    sırasının TERSİNE dizilmiş (kronoloji sıralaması test edilecek)."""
    return {
        "iddialar": [
            {"id": "I1", "metin": "Sozlesme kuruldu"},
            {"id": "I2", "metin": "Bedel odenmedi"},
        ],
        "olaylar": [
            {"tarih": "2025-03-15", "olgu": "Ihtarname gonderildi",
             "belge": "ihtarname", "destekler": ["I2"], "ispat_durumu": "belgeli"},
            {"tarih": "2025-01-10", "olgu": "Sozlesme imzalandi",
             "belge": "yazili sozlesme", "destekler": ["I1"], "ispat_durumu": "belgeli"},
        ],
    }


def test_script_mevcut():
    assert SCRIPT.is_file(), f"vakia_matris.py bulunamadı: {SCRIPT}"


# ── argüman düzeni ──────────────────────────────────────────────────────────

def test_argumansiz_cagri_argparse_hatasi_exit2():
    kod, out, err = _cli()
    assert kod == 2, f"--iskelet/--dogrula zorunlu grubu eksikken argparse exit 2 verir; stderr:\n{err}"
    assert "usage" in err.lower()


# ── --iskelet: şablon + ISPAT kümesi ────────────────────────────────────────

def test_iskelet_sablon_ve_ispat_kumesi_exit0():
    """v0.5.14'te BİLİNÇLİ olarak güncellendi (iki gerekçe):
    (1) B-26 — `--iskelet` stdout'u artık SAF JSON'dur; banner/açıklama
        STDERR'e taşındı (SKILL.md'nin öğrettiği `--iskelet > 04-vakia.json`
        kullanımı bugüne dek ayrıştırılamaz dosya üretiyordu).
    (2) T5A — ISPAT kümesine `beyan` (ISPAT_KISMI) eklendi; alfabetik satır
        bu yüzden değişti."""
    kod, out, err = _cli("--iskelet")
    assert kod == 0
    assert "VAKIA/DELİL MATRİSİ" in err
    # ISPAT kümesi alfabetik sıralı tek satırda (stderr'de) basılır
    assert ("ispat_durumu değerleri: belgeli, beyan, bilirkisi, ikrar, "
            "ispatsiz, karine, tanik, yemin") in err
    # STDOUT tek başına geçerli JSON olmalı
    sablon = json.loads(out)
    assert set(sablon) == {"taraflar", "iddialar", "olaylar"}
    assert sablon["iddialar"][0]["id"] == "I1"
    assert sablon["olaylar"][0]["tarih"] == "YYYY-MM-DD"
    assert "--- Doldurulacak şablon (JSON — STDOUT) ---" in err
    assert "Doldurduktan sonra: python vakia_matris.py --dogrula vakia.json" in err


def test_iskelet_ile_json_bayragi_sessizce_yoksayilir(izole_dizin):
    """Karakterizasyon — mevcut tasarım: --json yalnız --dogrula yolunda
    kullanılır; --iskelet ile verilirse hata YOK, dosya da YAZILMAZ."""
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _cli("--iskelet", "--json", str(hedef))
    assert kod == 0
    assert not hedef.exists()
    assert "[JSON]" not in out


# ── mutlu yol: sağlıklı dosya ───────────────────────────────────────────────

def test_saglikli_dosya_tamam_ve_exit0(izole_dizin):
    yol = _vakia_yaz(izole_dizin, _saglikli_vakia())
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "VAKIA/DELİL DENETİMİ" in out
    assert ">>> Dosya olgu/delil bütünlüğü TAMAM <<<" in out
    # hiçbir tespit bloğu basılmamalı
    assert "İSPAT BOŞLUKLARI" not in out
    assert "YETİM DELİLLER" not in out
    assert "GEÇERSİZ İDDİA REFERANSI" not in out
    assert "GEÇERSİZ ispat_durumu" not in out
    assert "tarihsiz" in out  # özet satırında sayaç olarak yine geçer
    assert "İddia: 2 | belgeli destekli: 2 | ispat boşluğu: 0" in out
    assert "Olay: 2 | tarihsiz: 0 | yetim: 0" in out


def test_kronoloji_tarihli_olaylar_tarih_sirasinda_basilir(izole_dizin):
    """Girdide 2025-03-15 önce verilir; çıktı kronolojisi 2025-01-10'u
    öne almalı. Satır biçimi: 'TARİH | olgu  [delil: belge; durum]'."""
    yol = _vakia_yaz(izole_dizin, _saglikli_vakia())
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "--- KRONOLOJİ ---" in out
    assert "2025-01-10 | Sozlesme imzalandi  [delil: yazili sozlesme; belgeli]" in out
    assert "2025-03-15 | Ihtarname gonderildi  [delil: ihtarname; belgeli]" in out
    assert out.index("2025-01-10") < out.index("2025-03-15")
    # tarihsiz blok başlığı hiç basılmamalı
    assert "(tarihsiz — sıralanamadı:)" not in out


# ── tespit sınıfları (her biri ayrı) ────────────────────────────────────────

def test_tarihsiz_olay_ayri_blokta_ve_sagligi_bozar(izole_dizin):
    """Geçersiz/boş tarihli olay kronolojiye giremez; '(tarihsiz —
    sıralanamadı:)' bloğunda '?' işaretiyle listelenir ve saglikli=false
    yapar. Exit yine 0 (karakterizasyon — mevcut tasarım)."""
    veri = _saglikli_vakia()
    veri["olaylar"].append({"tarih": "bozuk-tarih", "olgu": "Tarihsiz gorusme",
                            "belge": "not", "destekler": ["I1"],
                            "ispat_durumu": "tanik"})
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "(tarihsiz — sıralanamadı:)" in out
    assert "? Tarihsiz gorusme" in out
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out
    assert "Olay: 3 | tarihsiz: 1 | yetim: 0" in out


def test_ispat_boslugu_belgeli_destegi_olmayan_iddia(izole_dizin):
    """Desteği olmayan iddia İSPAT BOŞLUĞU sayılır: hem matris satırının
    altında uyarı hem ayrı blok basılır; saglikli=false, exit yine 0."""
    veri = _saglikli_vakia()
    veri["iddialar"].append({"id": "I3", "metin": "Temerrut faizi isler"})
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "⚠ İSPAT BOŞLUĞU: bu iddiayı destekleyen belgeli/somut delil yok" in out
    assert "İSPAT BOŞLUKLARI (delilsiz iddialar — ispat yükü riski)" in out
    assert "✗ I3" in out
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out
    assert "İddia: 3 | belgeli destekli: 2 | ispat boşluğu: 1" in out


def test_ispatsiz_durumlu_veya_belgesiz_destek_bosluk_sayilir(izole_dizin):
    """'Belgeli' sayılmak için İKİ koşul birden gerekir: ispat_durumu
    ISPAT_TAM beyaz listesinde VE belge alanı dolu. Biri eksikse destek var
    görünse de iddia yine boşluktadır.

    v0.5.14 (T5A/B-10): bu docstring GÜNCELLENDİ — eski metin koşulu
    "ispat_durumu != 'ispatsiz'" diye yazıyordu (NEGATİF liste). Kod pozitif
    beyaz listeye çevrildiğinde bu sözleşme KIRILMADAN yalan olacaktı;
    denetim izinin tek koruması docstring'in aynı turda düzeltilmesidir."""
    veri = {
        "iddialar": [
            {"id": "I1", "metin": "Belge var ama ispatsiz"},
            {"id": "I2", "metin": "Durum gecerli ama belge bos"},
        ],
        "olaylar": [
            {"tarih": "2025-02-01", "olgu": "Ispatsiz olay", "belge": "kagit",
             "destekler": ["I1"], "ispat_durumu": "ispatsiz"},
            {"tarih": "2025-02-02", "olgu": "Belgesiz tanik olayi", "belge": "",
             "destekler": ["I2"], "ispat_durumu": "tanik"},
        ],
    }
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "✗ I1" in out
    assert "✗ I2" in out
    assert "İddia: 2 | belgeli destekli: 0 | ispat boşluğu: 2" in out
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out


def test_yetim_delil_raporlanir_ama_sagligi_bozmaz(izole_dizin):
    """Karakterizasyon — mevcut tasarım: destekler'i boş olay YETİM
    DELİLLER bloğunda raporlanır, ancak saglikli hesabına GİRMEZ —
    yalnız yetim varken dosya yine 'TAMAM' basar."""
    veri = _saglikli_vakia()
    veri["olaylar"].append({"tarih": "2025-04-01", "olgu": "Kimseye bagli olmayan tutanak",
                            "belge": "tutanak", "destekler": [],
                            "ispat_durumu": "belgeli"})
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "YETİM DELİLLER (hiçbir iddiaya bağlanmamış olgu)" in out
    assert "! Kimseye bagli olmayan tutanak" in out
    assert ">>> Dosya olgu/delil bütünlüğü TAMAM <<<" in out
    assert "Olay: 3 | tarihsiz: 0 | yetim: 1" in out


def test_gecersiz_iddia_referansi_yakalanir(izole_dizin):
    veri = _saglikli_vakia()
    veri["olaylar"].append({"tarih": "2025-05-01", "olgu": "Hayali iddiaya atif",
                            "belge": "e-posta", "destekler": ["I9"],
                            "ispat_durumu": "belgeli"})
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "GEÇERSİZ İDDİA REFERANSI" in out
    assert "Hayali iddiaya atif → bilinmeyen iddia 'I9'" in out
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out


def test_gecersiz_ispat_durumu_yakalanir(izole_dizin):
    veri = _saglikli_vakia()
    veri["olaylar"].append({"tarih": "2025-05-02", "olgu": "Video kayitli olay",
                            "belge": "usb", "destekler": ["I1"],
                            "ispat_durumu": "video"})
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "GEÇERSİZ ispat_durumu" in out
    assert "Video kayitli olay: 'video'" in out
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out


def test_ispat_durumu_alani_yoksa_none_ile_gecersiz_sayilir(izole_dizin):
    """Karakterizasyon — mevcut tasarım: ispat_durumu alanı hiç yoksa
    o.get(...) None döner, küme üyeliği tutmaz ve mesajda 'None' basılır."""
    veri = _saglikli_vakia()
    veri["olaylar"].append({"tarih": "2025-05-03", "olgu": "Durumsuz olay",
                            "belge": "x", "destekler": ["I1"]})
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert "GEÇERSİZ ispat_durumu" in out
    assert "Durumsuz olay: 'None'" in out


def test_bos_sozluk_girdisi_denetlenemedi_exit0(izole_dizin):
    """v0.5.14'te BİLİNÇLİ olarak değiştirildi (B-12): eski karakterizasyon
    boş dosyanın 'TAMAM' sayılmasını kilitliyordu — yani "0 iddia = kusursuz
    dosya". Denetlenecek içeriğin yokluğu denetimin GEÇTİĞİ anlamına gelmez;
    artık ayrı DENETLENEMEDİ sonuç sınıfı basılır. Exit kodu sözleşmesi
    (sys.exit yokluğu) DEĞİŞMEDİ."""
    yol = _vakia_yaz(izole_dizin, {})
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 0
    assert ">>> Dosya olgu/delil bütünlüğü TAMAM <<<" not in out
    assert "DENETLENEMEDİ" in out
    assert "İddia: 0 | belgeli destekli: 0 | ispat boşluğu: 0" in out
    assert "Olay: 0 | tarihsiz: 0 | yetim: 0" in out


# ── EKSİK halde de exit 0 (dogrula sonunda sys.exit yok) ────────────────────

def test_eksik_dosyada_da_exit_kodu_sifir(izole_dizin):
    """Karakterizasyon — mevcut tasarım: dogrula() sonunda sys.exit
    çağrısı YOK; saglikli=false olsa bile süreç 0 ile döner. Çağıran
    taraf sağlık sinyalini exit kodundan DEĞİL çıktıdan/JSON'dan okumalı."""
    veri = {"iddialar": [{"id": "I1", "metin": "Delilsiz iddia"}], "olaylar": []}
    yol = _vakia_yaz(izole_dizin, veri)
    kod, out, err = _cli("--dogrula", str(yol))
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out
    assert kod == 0, "mevcut tasarım: EKSİK halde de exit 0"


# ── --json makine-okur çıktı şeması ─────────────────────────────────────────

# v0.5.8.4: "ozne_eslestirme" anahtarı eklendi (ÖZNE TETİĞİ — taraf/özne
# yazım varyantları ozne_eslestirici eşikleriyle damgalanır; varyant yoksa
# boş liste, sessiz — bkz. test_v0584_desenler.py).
BEKLENEN_ANAHTARLAR = {
    "arac", "girdi", "kronoloji", "tarihsiz", "iddia_delil_matrisi",
    "ispat_bosluklari", "yetim_deliller", "gecersiz_referans",
    "gecersiz_ispat_durumu", "ozne_eslestirme", "ozet", "saglikli",
}


def test_json_cikti_semasi_saglikli_dosya(izole_dizin):
    yol = _vakia_yaz(izole_dizin, _saglikli_vakia())
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _cli("--dogrula", str(yol), "--json", str(hedef))
    assert kod == 0
    assert f"[JSON] Makine-okur sonuc yazildi: {hedef}" in out
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))

    assert set(sonuc.keys()) == BEKLENEN_ANAHTARLAR
    assert sonuc["arac"] == "vakia_matris"
    assert sonuc["girdi"] == str(yol)
    assert sonuc["saglikli"] is True

    # kronoloji tarih sıralı ve alanları tam
    assert [k["tarih"] for k in sonuc["kronoloji"]] == ["2025-01-10", "2025-03-15"]
    assert sonuc["kronoloji"][0] == {"tarih": "2025-01-10", "olgu": "Sozlesme imzalandi",
                                     "belge": "yazili sozlesme", "ispat_durumu": "belgeli"}
    # matris satırı şeması
    # v0.5.14 (T5A): matris SATIRINA `kismi_destek` eklendi — `belgeli`
    # alanının anlamı/tipi değişmedi, ÜST-DÜZEY şema da değişmedi.
    m1 = [s for s in sonuc["iddia_delil_matrisi"] if s["iddia_id"] == "I1"][0]
    assert set(m1.keys()) == {"iddia_id", "metin", "destekler", "belgeli",
                              "kismi_destek"}
    assert m1["belgeli"] is True and m1["destekler"] == ["Sozlesme imzalandi"]
    assert m1["kismi_destek"] is False

    assert sonuc["tarihsiz"] == []
    assert sonuc["ispat_bosluklari"] == []
    assert sonuc["yetim_deliller"] == []
    assert sonuc["gecersiz_referans"] == []
    assert sonuc["gecersiz_ispat_durumu"] == []
    assert sonuc["ozne_eslestirme"] == []  # taraf/ozne alanı yok → sessiz boş liste
    assert sonuc["ozet"] == {"iddia": 2, "belgeli_destekli": 2, "ispat_boslugu": 0,
                             "olay": 2, "tarihsiz": 0, "yetim": 0}


def test_json_cikti_semasi_eksik_dosya_tum_tespit_listeleri(izole_dizin):
    """Tüm tespit sınıflarını tek dosyada üretip JSON alanlarını ve
    saglikli=false + exit 0 ikilisini birlikte kilitler."""
    veri = {
        "iddialar": [
            {"id": "I1", "metin": "Desteksiz iddia"},
            {"id": "I2", "metin": "Belgeli iddia"},
        ],
        "olaylar": [
            {"tarih": "2025-05-01", "olgu": "Belgeli destek", "belge": "makbuz",
             "destekler": ["I2"], "ispat_durumu": "belgeli"},
            {"olgu": "Tarihsiz yetim olay", "belge": "", "destekler": [],
             "ispat_durumu": "tanik"},
            {"tarih": "2025-06-01", "olgu": "Sorunlu olay", "belge": "x",
             "destekler": ["I9"], "ispat_durumu": "video"},
        ],
    }
    yol = _vakia_yaz(izole_dizin, veri)
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _cli("--dogrula", str(yol), "--json", str(hedef))
    assert kod == 0, "mevcut tasarım: saglikli=false iken de exit 0"
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))

    assert set(sonuc.keys()) == BEKLENEN_ANAHTARLAR
    assert sonuc["saglikli"] is False
    assert sonuc["ispat_bosluklari"] == ["I1"]
    assert sonuc["tarihsiz"] == ["Tarihsiz yetim olay"]
    assert sonuc["yetim_deliller"] == ["Tarihsiz yetim olay"]
    assert sonuc["gecersiz_referans"] == ["Sorunlu olay → bilinmeyen iddia 'I9'"]
    assert sonuc["gecersiz_ispat_durumu"] == ["Sorunlu olay: 'video'"]
    assert sonuc["ozet"] == {"iddia": 2, "belgeli_destekli": 1, "ispat_boslugu": 1,
                             "olay": 3, "tarihsiz": 1, "yetim": 1}


# ── bozuk/eksik girdi ───────────────────────────────────────────────────────

def test_bozuk_json_girdisi_okunamadi_exit1(izole_dizin):
    yol = izole_dizin / "vakia.json"
    yol.write_text("{ gecersiz json", encoding="utf-8")
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 1
    assert "❌ JSON okunamadı" in out


def test_olmayan_dosya_okunamadi_exit1(izole_dizin):
    kod, out, err = _cli("--dogrula", str(izole_dizin / "yok.json"))
    assert kod == 1
    assert "❌ JSON okunamadı" in out


def test_json_koku_liste_ise_temiz_mesaj_exit1(izole_dizin):
    """v0.5.14'te BİLİNÇLİ olarak değiştirildi (B-23): eski karakterizasyon
    ham AttributeError traceback'ini kilitliyordu. Girdiyi MODEL üretir;
    traceback 'araç bozuldu' izlenimi verip asıl mesajı kaybediyordu.
    Aile standardı (temiz mesaj + exit 1) buraya da uygulandı."""
    yol = izole_dizin / "vakia.json"
    yol.write_text("[]", encoding="utf-8")
    kod, out, err = _cli("--dogrula", str(yol))
    assert kod == 1
    assert "Traceback" not in err
    assert "JSON kökü sözlük değil (list)" in out
