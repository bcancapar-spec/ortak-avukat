# -*- coding: utf-8 -*-
"""oa-kontrol / teslim_paketi.py için testler.

Bu script Fable-tespitli TESTSİZ release-kapısı scriptlerinden biridir: tek
komut teslim zincirini (dilekçe denetimi → atıf/künye → gizlilik →
pipeline defteri → tam tur → UDF üretimi) hiçbir test doğrulamıyordu.

Uçtan uca subprocess ile çağrılır (gerçek "ilk engelde dur" garantisi
main()'in sys.exit çağrısında yaşar). --kok her testte tempfile.mkdtemp()
ile açılan izole bir _oa iskeletine verilir; gerçek repo hiç dokunulmaz.

İki altın vaka:
  (1) eksik-unsurlu taslak → (a) dilekçe denetimi kapısı KAPANIR, zincir
      İLK ENGELDE durur, UDF üretilmez, exit != 0.
  (2) tam/temiz (atıfsız) taslak → tüm engelleyici kapılar açılır (kütük
      olmasa bile taslakta hiç atıf yok → (b) kapısı da açık sayılır),
      UDF üretilir, exit 0.
"""
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
          / "scripts" / "teslim_paketi.py")

# Zorunlu unsurları (mahkeme başlığı, taraf/kimlik, konu, vakıa, hukuki
# sebep, delil, netice-i talep, tarih, imza/vekil) TAŞIYAN ve hiçbir hukuki
# atıf (içtihat esas/karar no, kanun+madde) İÇERMEYEN taslak — bu yüzden
# (b) atıf/künye kapısı, kütük dosyası hiç olmasa bile "atıf yok → kapı
# açık" kuralıyla geçer.
TAM_TEMIZ_TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: 12345678901)
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

# Hiçbir zorunlu unsuru içermeyen, (a) kapısını kapatması garanti taslak.
EKSIK_TASLAK = "Bu kısa bir taslaktır ve zorunlu unsurları içermez.\n"


def _cli(taslak, kok, extra=()):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(taslak), "--tip", "genel", "--kok", str(kok), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole_kok():
    """tempfile tabanlı boş _oa iskeleti — gerçek repo kirletilmez."""
    tmp = tempfile.mkdtemp()
    return pathlib.Path(tmp)


def test_script_mevcut():
    assert SCRIPT.is_file(), f"teslim_paketi.py bulunamadı: {SCRIPT}"


# ── (1) eksik-unsurlu taslak → ilk kapı kapanır ─────────────────────────────

def test_eksik_unsurlu_taslak_ilk_kapida_durur_udf_uretilmez(izole_kok):
    taslak = izole_kok / "eksik.md"
    taslak.write_text(EKSIK_TASLAK, encoding="utf-8")

    kod, cikti = _cli(taslak, izole_kok)

    assert kod != 0, f"eksik unsurlu taslak zinciri geçmemeliydi; çıktı:\n{cikti}"
    assert "DİLEKÇE DENETİMİ" in cikti
    assert "TESLİM DURDURULDU" in cikti
    assert "İLK KAPANAN KAPI" in cikti
    assert "UDF ÜRETİLMEDİ" in cikti
    udf_yolu = taslak.with_suffix(taslak.suffix + ".udf")
    assert not udf_yolu.exists(), "eksik unsurlu taslak için UDF üretilmemeliydi"


def test_eksik_unsurlu_taslakta_sonraki_kapilar_calistirilmaz(izole_kok):
    """İlk engelde dur ilkesi: (a) kapandıktan sonra (b)/(c)/(d)/(e) hiç
    işletilmemeli (rapor bunu açıkça söylemeli — sessiz atlama değil)."""
    taslak = izole_kok / "eksik.md"
    taslak.write_text(EKSIK_TASLAK, encoding="utf-8")

    _kod, cikti = _cli(taslak, izole_kok)
    assert "SONRAKİ KAPILAR ÇALIŞTIRILMADI" in cikti
    assert "ATIF/KÜNYE DOĞRULAMA" not in cikti.split("İLK KAPANAN KAPI")[-1]


# ── (2) tam/temiz (atıfsız) taslak → zincir geçer ───────────────────────────

def test_tam_temiz_taslak_zincir_gecer_udf_uretilir(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    kod, cikti = _cli(taslak, izole_kok)

    assert kod == 0, f"tam/temiz taslak zinciri geçmeliydi; çıktı:\n{cikti}"
    assert "TESLİME HAZIR" in cikti
    udf_yolu = taslak.with_suffix(taslak.suffix + ".udf")
    assert udf_yolu.exists(), "temiz taslak için UDF üretilmeliydi"
    assert udf_yolu.stat().st_size > 0


def test_tam_temiz_taslakta_dilekce_ve_kunye_kapilari_acik(izole_kok):
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")

    _kod, cikti = _cli(taslak, izole_kok)
    assert "[OK] kapı açık (exit 0)." in cikti
    assert "BULUNAMADI" in cikti  # kunye_teyit: taslakta atıf yok → "BULUNAMADI"
    assert "TEYİTSİZ" not in cikti  # atıfsız taslakta hiç TEYİTSİZ atıf olamaz


# ── (3) İçtihatli taslak — (b2) İÇTİHAT MUHAKEME ZİNCİRİ kapısı (M2-3) ─────
# Uçtan uca: sentetik dilekçe + muhakeme kaydı + ham döküm → gate doğru
# geçer/engeller. Taslak zorunlu unsurları taşır (a) açık olsun; içtihat
# atfının aynı esas/karar no'su hem (b) kunye_teyit hem (b2) ictihat_
# muhakeme_denetim'in KAYNAK-İZİ denetimi için AYNI döküm dosyasında yer
# alır — böylece (b) her iki senaryoda da açık kalır, yalnız (b2) DAMGA/
# muhakeme-kaydı durumuna göre değişir.

KUNYE_ICTIHAT = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
TASLAK_ICTIHATLI = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: 12345678901)
Adres: Örnek Mahallesi No:1 İstanbul

DAVALI: Mehmet Kaya

KONU: Alacağın tahsili talebimizden ibarettir.

AÇIKLAMALAR (VAKIALAR):
1. Taraflar arasındaki ticari ilişkiden doğan alacak vakıası aşağıda özetlenmiştir.
2. Somut olayda Yargıtay 4. HD'nin E. 2023/1234, K. 2023/5678 sayılı kararı emsal
   teşkil etmektedir.

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


def _b2_kur(izole_kok, muhakeme_kaydi=True, damga="LEHE", ayirt_etme=""):
    """Ortak döküm (kunye_teyit + ictihat_muhakeme_denetim'in KAYNAK-İZİ
    denetimi AYNI dosyayı paylaşır) + isteğe bağlı muhakeme kaydı kurar;
    taslak dosya yolunu döndürür."""
    dokum_dizin = izole_kok / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True, exist_ok=True)
    (dokum_dizin / "kaynak.md").write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni "
        "burada yer almaktadır...\n",
        encoding="utf-8",
    )
    # kunye_teyit.py (b) yalnızca döküm dizinini değil, KÜTÜK DOSYASININ
    # DE var olduğunu şart koşar (kütük yoksa yapısal blok — dosya boş
    # olsa bile "var" sayılır, eşleşme yine dökümden gelir).
    (izole_kok / "_oa" / "teyit" / "kunye-teyit.md").write_text(
        "# Künye Teyit Kütüğü (test iskeleti — içerik dökümde)\n", encoding="utf-8")
    if muhakeme_kaydi:
        cikti_dizin = izole_kok / "_oa" / "cikti"
        cikti_dizin.mkdir(parents=True, exist_ok=True)
        satirlar = [
            "# 01 — İçtihat Muhakeme Kaydı", "",
            f"**KUNYE:** {KUNYE_ICTIHAT}",
            "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
            f"**DAMGA:** {damga}", "",
            "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
            "## İLLİYET", "...illiyet açıklaması...", "",
            "## AYIRT-ETME", ayirt_etme, "",
        ]
        (cikti_dizin / "01-ictihat-muhakeme.md").write_text(
            "\n".join(satirlar), encoding="utf-8")

    taslak = izole_kok / "ictihatli.md"
    taslak.write_text(TASLAK_ICTIHATLI, encoding="utf-8")
    return taslak


def test_ictihatli_taslak_muhakeme_kaydi_yoksa_b2_kapisi_engeller(izole_kok):
    """(b) döküm izli olduğu için açılır ama (b2) muhakeme kaydı YOK — çıplak
    atıf, zincir (b2)'de durmalı; UDF üretilmemeli."""
    taslak = _b2_kur(izole_kok, muhakeme_kaydi=False)

    kod, cikti = _cli(taslak, izole_kok)

    assert kod != 0, f"muhakeme kaydı olmayan içtihatlı taslak geçmemeliydi; çıktı:\n{cikti}"
    assert "[b2] İÇTİHAT MUHAKEME ZİNCİRİ" in cikti
    assert "İLK KAPANAN KAPI: (b2)" in cikti
    assert "[OK] kapı açık (exit 0)." in cikti.split("[b2]")[0], (
        "(b2)'den önceki (a)/(b) kapıları açık olmalıydı")
    udf_yolu = taslak.with_suffix(taslak.suffix + ".udf")
    assert not udf_yolu.exists()


def test_ictihatli_taslak_aleyhe_damgali_kayitla_b2_kapisi_engeller(izole_kok):
    """Muhakeme kaydı VAR ama DAMGA=ALEYHE — anayasa m.6, (b2) yine engel
    (bu kez 'çıplak atıf' değil, DAMGA gerekçesiyle)."""
    taslak = _b2_kur(izole_kok, muhakeme_kaydi=True, damga="ALEYHE")

    kod, cikti = _cli(taslak, izole_kok)

    assert kod != 0
    assert "İLK KAPANAN KAPI: (b2)" in cikti
    assert "ALEYHE" in cikti


def test_ictihatli_taslak_lehe_muhakeme_kaydiyla_tum_kapilar_gecer_udf_uretilir(izole_kok):
    """Muhakeme kaydı VAR, DAMGA=LEHE, KAYNAK-İZİ dosyası döküm dizininde
    gerçekten var ve künye orada dize olarak geçiyor → (b) VE (b2) açık,
    zincirin tamamı geçer, UDF üretilir."""
    taslak = _b2_kur(izole_kok, muhakeme_kaydi=True, damga="LEHE")

    kod, cikti = _cli(taslak, izole_kok)

    assert kod == 0, f"LEHE damgalı, tam alanlı muhakeme kaydıyla zincir geçmeliydi; çıktı:\n{cikti}"
    assert "TESLİME HAZIR" in cikti
    assert "(b2) içtihat muhakeme zinciri" in cikti
    udf_yolu = taslak.with_suffix(taslak.suffix + ".udf")
    assert udf_yolu.exists()
    assert udf_yolu.stat().st_size > 0


def test_izole_kok_gercek_repoyu_kirletmez(izole_kok):
    """Testler bittiğinde gerçek repo kökünde _oa/ klasörü OLUŞMAMALI —
    izolasyonun kanıtı: --kok her zaman tempfile dizinine verilir."""
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    _cli(taslak, izole_kok)
    assert not (REPO / "_oa").exists(), "gerçek repo kökünde _oa/ oluşmamalı"
