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


def test_izole_kok_gercek_repoyu_kirletmez(izole_kok):
    """Testler bittiğinde gerçek repo kökünde _oa/ klasörü OLUŞMAMALI —
    izolasyonun kanıtı: --kok her zaman tempfile dizinine verilir."""
    taslak = izole_kok / "temiz.md"
    taslak.write_text(TAM_TEMIZ_TASLAK, encoding="utf-8")
    _cli(taslak, izole_kok)
    assert not (REPO / "_oa").exists(), "gerçek repo kökünde _oa/ oluşmamalı"
