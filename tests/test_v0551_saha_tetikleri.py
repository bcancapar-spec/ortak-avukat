"""v0.5.5.1 — İsmail Gümüş saha koşusundan çıkan ÜÇ TETİK düzeltmesi.

Saha bulgusunun özü: E1 (Gate A), E2 (muhakeme kaydı yazımı), E3 (dava tezi) ve
E5 (kayıpsız senkron) için ŞÜPHELENİLEN kod kusurları sentetik yeniden üretimle
sınandı ve DÖRDÜ DE SAĞLAM çıktı — harita üretiliyor, `teyit --damga` muhakeme
dosyasını koşulsuz yazıyor, TEZ bölümü iskelette var, `--senkron` çıktıyı
kayıpsız gömüyor (40.541 B cikti → 42.775 B md). Yani kusur MEKANİZMADA değil,
mekanizmanın ÇAĞRILMAMASINDAYDI: saha oturumunda ritüeller hiç koşmadı, kütük ve
working memory ELLE yazıldı.

Bu yüzden buradaki üç test kod yollarını değil TETİKLERİ kilitler:
  * `_analiz_md_kendini_onar` — elle yazılmış dosya-analiz.md hook'ta onarılır
  * `_defter_muhakeme_dengesi_uyarisi` — elle yazılmış kütük satırı görünür olur
  * `_sozlesme_disi_kok_dosyalari` — bekçinin kök-dosya kör noktası kapanır
"""
import importlib.util
import os
import subprocess
import sys

import pytest

BETIK_DIZIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "ortak-avukat", "skills", "oa-pipeline", "scripts")


def _defter_kur(kok):
    """Gerçek CLI ile defter aç — `_denetle_hesapla` defter YOKSA erken döner
    (uyarı listesi hiç kurulmaz), bu yüzden uyarı testleri gerçek deftere
    ihtiyaç duyar."""
    cp = subprocess.run(
        [sys.executable, os.path.join(BETIK_DIZIN, "pipeline_kayit.py"),
         "--baslat", "Test Dosyası", "--kok", kok],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=kok)
    assert cp.returncode == 0, (cp.stdout or "") + (cp.stderr or "")


def _denetim_uyarilari(pk, kok):
    """Defter yollarını `_yollar`dan TÜRETİR (dosya adlarını testte
    sabitlemek ikiz-liste yaratırdı)."""
    olaylar_yol, durum_yol = pk._yollar(type("A", (), {"kok": kok, "yol": None})())
    d, sorunlar, uyarilar = pk._denetle_hesapla(kok, olaylar_yol, durum_yol)
    assert d is not None, "defter okunamadı — test kurulumu bozuk"
    return sorunlar, uyarilar


def _modul(ad, dosya):
    spec = importlib.util.spec_from_file_location(ad, os.path.join(BETIK_DIZIN, dosya))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pk():
    return _modul("_test_v0551_pipeline_kayit", "pipeline_kayit.py")


@pytest.fixture(scope="module")
def tt():
    return _modul("_test_v0551_tam_tur", "tam_tur.py")


# ── E5 — WORKING MEMORY TETİĞİ ──────────────────────────────────────────────

def test_elle_yazilmis_analiz_md_onarilir_ve_cikti_kayipsiz_gomulur(tmp_path, pk, tt):
    """Saha kalıbının birebir yeniden üretimi: 3 çalışma evrakı üretilmiş, ama
    dosya-analiz.md model tarafından ELLE yazılmış (kısa, bizim biçimimizde
    değil). Onarım sonrası md, cikti gövdesini KAYIPSIZ taşımalı."""
    kok = str(tmp_path)
    cikti = os.path.join(kok, "_oa", "cikti")
    os.makedirs(cikti)
    adlar = ["01-vakia.md", "03-ictihat-muhakeme.md", "08-dilekce-taslak.md"]
    for i, ad in enumerate(adlar):
        govde = "".join(f"{ad} satir {j} — ozgun icerik golgesi.\n" for j in range(300 + i * 50))
        with open(os.path.join(cikti, ad), "w", encoding="utf-8") as f:
            f.write(f"# {ad}\n\n{govde}")
    cikti_toplam = sum(os.path.getsize(os.path.join(cikti, a)) for a in adlar)

    tt.cmd_baslat(kok, "Test Dosyası")
    md_yol = tt._analiz_md(kok)
    # Modelin elle yazdığı hâli taklit et (saha: 1.247 B, birkaç başlık).
    with open(md_yol, "w", encoding="utf-8") as f:
        f.write("# dosya-analiz\n\n## Adım çıktıları\n\n- tamamlandı\n\n## GELİŞMELER\n")
    assert not tt._iskelet_saglam_mi(open(md_yol, encoding="utf-8").read())

    uyari = pk._analiz_md_kendini_onar(kok)

    assert uyari is not None, "elle yazılmış md sessizce kabul edilemez"
    assert "WORKING MEMORY ONARILDI" in uyari
    icerik = open(md_yol, encoding="utf-8").read()
    assert tt._iskelet_saglam_mi(icerik), "onarım sonrası iskelet sağlam olmalı"
    # KAYIPSIZLIK: her çalışma evrakının ADI ve GÖVDESİ md'de olmalı.
    for ad in adlar:
        assert ad in icerik
    assert "01-vakia.md satir 250" in icerik
    assert len(icerik.encode("utf-8")) >= cikti_toplam, (
        "senkron gövdeyi gömdüyse md, cikti toplamından küçük olamaz")
    # Onarım TAMAM ÜRETMEZ — Gate G+ fail-closed kalır.
    assert not tt._tamam_isaretci_var_mi(icerik)


def test_saglam_analiz_md_ye_dokunulmaz(tmp_path, pk, tt):
    """Biçimi sağlam md yeniden yazılmaz (gereksiz senkron değirmeni yok)."""
    kok = str(tmp_path)
    os.makedirs(os.path.join(kok, "_oa", "cikti"))
    tt.cmd_baslat(kok, "Test Dosyası")
    tt.cmd_senkron(kok)
    md_yol = tt._analiz_md(kok)
    onceki = open(md_yol, encoding="utf-8").read()

    assert pk._analiz_md_kendini_onar(kok) is None
    assert open(md_yol, encoding="utf-8").read() == onceki


def test_tam_tur_kullanilmamis_kokte_onarim_sessizce_atlanir(tmp_path, pk):
    """dosya-analiz.json yoksa (tam_tur akışı hiç kullanılmamış) kapı
    SESSİZCE atlanır — defter kapısıyla simetrik davranış."""
    kok = str(tmp_path)
    os.makedirs(os.path.join(kok, "_oa", "cikti"))
    assert pk._analiz_md_kendini_onar(kok) is None
    assert not os.path.exists(os.path.join(kok, "_oa", "analiz", "dosya-analiz.md"))


# ── E2 — DEFTER-MUHAKEME SAYIM DENGESİ ──────────────────────────────────────

def _kutuk_yaz(kok, satir_sayisi, damgali=True):
    teyit = os.path.join(kok, "_oa", "teyit")
    os.makedirs(teyit, exist_ok=True)
    satirlar = ["# Künye Teyit Kütüğü\n",
                "| Zaman | Araç | Sorgu | Sonuç | Döküm |\n", "|---|---|---|---|---|\n"]
    for i in range(satir_sayisi):
        son = f"Yargitay 17. HD 2019/{i} E. 2021/{i} K." + (" DAMGA=LEHE" if damgali else "")
        satirlar.append(f"| 2026-07-29T0{i}:00:00 | ictihat_getir | sorgu | {son} | — |\n")
    with open(os.path.join(teyit, "kunye-teyit.md"), "w", encoding="utf-8") as f:
        f.writelines(satirlar)


def _muhakeme_yaz(kok, bolum_sayisi):
    cikti = os.path.join(kok, "_oa", "cikti")
    os.makedirs(cikti, exist_ok=True)
    p = ["# İçtihat Muhakeme Kaydı\n\n"]
    for i in range(bolum_sayisi):
        p.append(f"**KUNYE:** Yargitay 17. HD 2019/{i} E. 2021/{i} K.\n")
        p.append("**DAMGA:** LEHE\n\n## DAVAYA-BAĞ\nSomut olayla ortusur.\n\n")
    with open(os.path.join(cikti, "03-ictihat-muhakeme.md"), "w", encoding="utf-8") as f:
        f.writelines(p)


def test_kutukte_damga_var_muhakeme_yoksa_uyarir(tmp_path, pk):
    """SAHA KALIBI: kütükte 3 DAMGA'lı satır, muhakeme kaydı HİÇ yok →
    satırlar elle eklenmiş demektir, görünür uyarı üretilir."""
    kok = str(tmp_path)
    _kutuk_yaz(kok, 3)

    uyari = pk._defter_muhakeme_dengesi_uyarisi(kok)

    assert uyari is not None
    assert "DEFTER-MUHAKEME DENGESİZLİĞİ" in uyari
    assert "3 satır" in uyari and "0 bölüm" in uyari


def test_sayilar_esitse_uyari_yok(tmp_path, pk):
    """`teyit --damga` ikisini birlikte yazdığında sayılar eşittir — sessiz."""
    kok = str(tmp_path)
    _kutuk_yaz(kok, 3)
    _muhakeme_yaz(kok, 3)
    assert pk._defter_muhakeme_dengesi_uyarisi(kok) is None


def test_damgasiz_kutuk_uyari_uretmez(tmp_path, pk):
    """ARAMA araçlarında damga YASAK — damgasız kütük tek başına kusur değil."""
    kok = str(tmp_path)
    _kutuk_yaz(kok, 4, damgali=False)
    assert pk._defter_muhakeme_dengesi_uyarisi(kok) is None


def test_denge_uyarisi_denetim_ciktisinda_gorunur(tmp_path, pk):
    """Uyarı yalnız fonksiyonda kalmaz — --denetle STDOUT'una da çıkar."""
    kok = str(tmp_path)
    _defter_kur(kok)
    _kutuk_yaz(kok, 2)
    sorunlar, uyarilar = _denetim_uyarilari(pk, kok)
    assert any("DEFTER-MUHAKEME DENGESİZLİĞİ" in u for u in uyarilar)
    # Advisory — teslim kapısı ictihat_muhakeme_denetim.py'dedir, burası değil.
    assert not any("DEFTER-MUHAKEME DENGESİZLİĞİ" in s for s in sorunlar)


# ── E4 — KÖK DOSYA BEKÇİSİ ──────────────────────────────────────────────────

def test_kok_dosya_beyaz_liste_disi_uyarir(tmp_path, pk):
    kok = str(tmp_path)
    oa = os.path.join(kok, "_oa")
    os.makedirs(oa)
    for ad in ("dosya.md", "sureler.json", "gecici-notlar.md", "taslak.txt"):
        with open(os.path.join(oa, ad), "w", encoding="utf-8") as f:
            f.write("x")

    disi = pk._sozlesme_disi_kok_dosyalari(kok)

    assert disi == ["gecici-notlar.md", "taslak.txt"], "beyaz listedekiler sayılmamalı"


def test_kok_dosya_bekcisi_dizinleri_saymaz(tmp_path, pk):
    """Dizinler P1-9(b)'nin işi — kök dosya bekçisi onlara karışmaz (çift
    basım olmasın)."""
    kok = str(tmp_path)
    os.makedirs(os.path.join(kok, "_oa", "cikti"))
    os.makedirs(os.path.join(kok, "_oa", "golge-dizin"))
    assert pk._sozlesme_disi_kok_dosyalari(kok) == []


def test_kok_dosya_bekcisi_bloklamaz(tmp_path, pk):
    """Amaç çizgisi: görünürlük evet, muhakemeyi durduran kapı HAYIR."""
    kok = str(tmp_path)
    _defter_kur(kok)
    with open(os.path.join(kok, "_oa", "beklenmeyen.md"), "w", encoding="utf-8") as f:
        f.write("x")
    sorunlar, uyarilar = _denetim_uyarilari(pk, kok)
    assert any("SÖZLEŞME-DIŞI KÖK DOSYA" in u for u in uyarilar)
    assert not any("SÖZLEŞME-DIŞI KÖK DOSYA" in s for s in sorunlar)
