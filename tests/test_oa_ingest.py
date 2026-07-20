# -*- coding: utf-8 -*-
"""oa-ingest / oa_ingest.py için ALTIN VAKA (regresyon) testi.

Script'i CLI olarak subprocess ile çalıştırır — gerçek "iki koşu" delta
senaryosunu (önbellek dosyaya yazılıp ikinci sürecin onu okuması) yalnız
gerçek bir alt-süreç uçtan uca doğrulayabilir; içe aktarılmış modülü aynı
process'te iki kez main() ile çağırmak argparse/sys.argv durumunu paylaştırıp
senaryoyu gizler.

REGRESYON (Fable 5 bulgusu, HIGH, kod-hatası/veri-bütünlüğü):
`kullanilan` (md dosya-adı çakışma) kümesi eskiden yalnız döngü İLERLEDİKÇE
doluyordu; önbellekten doğrudan basılan kayıtların md adları döngü BAŞINDA
rezerve edilmiyordu. Delta iş akışında, ikinci koşuda sıralamada önbellekli
kayıttan ÖNCE gelen aynı taban-adlı YENİ bir evrak (a/001-x.txt), henüz sırası
gelmemiş b/001-x.txt önbellek kaydının "001-x.md" dosyasını SESSİZCE ÜZERİNE
YAZIYORDU: künyede iki kayıt aynı md'ye işaret ediyor, md içeriği yalnız
sonradan yazanınki oluyor, b'nin çıkarılmış metni okuma katmanından kayboluyor,
künyedeki karakter/sha ise b'nin eski içeriğini gösterip md ile ÇELİŞİYORDU —
hiçbir uyarı üretilmeden. Bu dosya tam o iki-koşulu senaryoyu (b önce işlenir
ve önbelleğe yazılır → a sonra eklenir ve sıralamada b'den ÖNCE gelir) kurup
künyede İKİ KAYDIN DA FARKLI md dosyasına sahip olduğunu ve her md dosyasının
YALNIZ kendi kaynağının metnini içerdiğini doğrular.
"""
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"


def _ingest(klasor):
    """oa_ingest.py'yi gerçek bir alt-süreçte (python <script> <klasor> --ocr kapali)
    çalıştırır. --ocr kapali: test yalnız düz-metin (.txt) evrak kullanır, Tesseract
    gerektirmez (ortamda kurulu olmayabilir) ve OCR dalına hiç girmez."""
    assert SCRIPT.is_file(), f"oa_ingest.py bulunamadı: {SCRIPT}"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(klasor), "--ocr", "kapali"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert cp.returncode == 0, f"oa_ingest.py hata ile bitti:\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    return cp


def _kunye_oku(klasor):
    yol = pathlib.Path(klasor) / "_oa" / "metin" / "00-kunye.json"
    return json.loads(yol.read_text(encoding="utf-8"))


def test_onbellekli_md_adi_cakismasi_ezmez(tmp_path):
    # 1. koşu: yalnız b/001-x.txt var → ingest (önbelleğe "001-x.md" olarak yazılır)
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "001-x.txt").write_text("B_ICERIGI_BIRINCI_KOSU", encoding="utf-8")
    _ingest(tmp_path)

    kunye1 = _kunye_oku(tmp_path)
    assert len(kunye1["kayitlar"]) == 1
    b_ilk = kunye1["kayitlar"][0]
    assert b_ilk["md"] == "001-x.md"
    metin_dizin = tmp_path / "_oa" / "metin"
    assert "B_ICERIGI_BIRINCI_KOSU" in (metin_dizin / "001-x.md").read_text(encoding="utf-8")

    # 2. koşu: sıralamada b'den ÖNCE gelen aynı taban-adlı a/001-x.txt eklendi.
    # b/001-x.txt DEĞİŞMEDİ → önbellekten (imza eşleşir) doğrudan basılacak.
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "001-x.txt").write_text("A_ICERIGI_IKINCI_KOSU", encoding="utf-8")
    _ingest(tmp_path)

    kunye2 = _kunye_oku(tmp_path)
    assert len(kunye2["kayitlar"]) == 2
    kayitlar = {k["kaynak"]: k for k in kunye2["kayitlar"]}
    a_kayit = kayitlar[str(pathlib.Path("a") / "001-x.txt")]
    b_kayit = kayitlar[str(pathlib.Path("b") / "001-x.txt")]

    # ESAS REGRESYON DENETİMİ: iki kayıt AYNI md dosyasına işaret etmemeli.
    assert a_kayit["md"] != b_kayit["md"], (
        "REGRESYON: a ve b AYNI md dosyasına işaret ediyor — önbellekli kaydın "
        "md adı döngü başında rezerve edilmemiş (Fable 5 bulgusu geri geldi)."
    )
    # b'nin önbellekten gelen kaydı DEĞİŞMEMİŞ olmalı (ilk koşudaki adıyla aynı).
    assert b_kayit["md"] == "001-x.md", "b'nin önbellekli md adı ikinci koşuda değişmemeli"

    a_md_metni = (metin_dizin / a_kayit["md"]).read_text(encoding="utf-8")
    b_md_metni = (metin_dizin / b_kayit["md"]).read_text(encoding="utf-8")

    # Her md dosyası YALNIZ kendi kaynağının metnini içermeli — biri diğerini EZMEMİŞ.
    assert "A_ICERIGI_IKINCI_KOSU" in a_md_metni
    assert "B_ICERIGI_BIRINCI_KOSU" not in a_md_metni
    assert "B_ICERIGI_BIRINCI_KOSU" in b_md_metni
    assert "A_ICERIGI_IKINCI_KOSU" not in b_md_metni

    # künyedeki karakter sayısı, md dosyasının GERÇEK içeriğiyle tutarlı olmalı
    # (bug'da b'nin künye kaydı eski karaktersayısını gösterirken md a'nın
    # içeriğini taşıyordu — karakter sayısı artık kendi md'sinin gövdesiyle uyuşmalı).
    assert b_kayit["karakter"] == len("B_ICERIGI_BIRINCI_KOSU")
    assert a_kayit["karakter"] == len("A_ICERIGI_IKINCI_KOSU")


def test_yeniden_bayragi_onbellegi_yok_sayar_ve_yine_cakismaz(tmp_path):
    """--yeniden ile önbellek tamamen yok sayılır (onbellek={}); bu durumda da
    aynı taban-adlı iki evrak md_yaz'ın KENDİ İÇİ çakışma denetimiyle (aynı
    koşu içinde kullanilan biriktirilerek) doğru şekilde ayrışmalı — regresyon
    fix'i --yeniden yolunu bozmamalı."""
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "001-x.txt").write_text("A_ICERIGI", encoding="utf-8")
    (tmp_path / "b" / "001-x.txt").write_text("B_ICERIGI", encoding="utf-8")
    _ingest(tmp_path)

    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--ocr", "kapali", "--yeniden"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert cp.returncode == 0

    kunye = _kunye_oku(tmp_path)
    kayitlar = {k["kaynak"]: k for k in kunye["kayitlar"]}
    a_kayit = kayitlar[str(pathlib.Path("a") / "001-x.txt")]
    b_kayit = kayitlar[str(pathlib.Path("b") / "001-x.txt")]
    assert a_kayit["md"] != b_kayit["md"]

    metin_dizin = tmp_path / "_oa" / "metin"
    assert "A_ICERIGI" in (metin_dizin / a_kayit["md"]).read_text(encoding="utf-8")
    assert "B_ICERIGI" in (metin_dizin / b_kayit["md"]).read_text(encoding="utf-8")


# ── EK-FİX v0.5.2 risk#1: ARIZA onbellek kaydı HIT sayılmamalı ─────────────

def test_ariza_onbellek_kaydi_hit_sayilmaz_yeniden_denenir(tmp_path):
    """REGRESYON: FAZ C (yazma) v1.5.1 (a)'dan beri {hata, atlandı} yöntemli
    sonuçları önbelleğe YAZMIYOR — ama eski/harici bir önbellek dosyasında böyle
    bir kayıt ZATEN varsa (imza aynı kaldığı sürece), FAZ A (okuma) eskiden bunu
    HIT sayıp doğrudan basıyordu: bayat 'YÜKLENEMEDİ' damgası SONSUZA dek servis
    ediliyordu (araç sonradan kurulsa/dosya normalde işlenebilir olsa bile hiç
    yeniden denenmiyordu). Bu test, imza eşleşen ama yöntemi 'hata' olan elle
    yazılmış bir önbellek kaydının MISS'e düşüp dosyanın GERÇEKTEN yeniden
    işlendiğini doğrular."""
    dosya = tmp_path / "dosya.txt"
    dosya.write_text("GERÇEK METİN İÇERİĞİ", encoding="utf-8")
    imza = f"{dosya.stat().st_mtime:.0f}-{dosya.stat().st_size}"

    metin_dizin = tmp_path / "_oa" / "metin"
    metin_dizin.mkdir(parents=True)
    onbellek = {
        "dosya.txt": {
            "imza": imza,
            "kayit": {
                "no": None, "ad": "dosya", "tarih": None, "kaynak": "dosya.txt",
                "yontem": "hata", "teyit_gerek": True, "karakter": 0,
                "sha": "0" * 16, "sayfa": None, "hata": "eski arıza (bayat)",
                "md": "000-dosya.md",
            },
        }
    }
    (metin_dizin / ".ingest-onbellek.json").write_text(
        json.dumps(onbellek, ensure_ascii=False), encoding="utf-8")

    _ingest(tmp_path)

    kunye = _kunye_oku(tmp_path)
    assert len(kunye["kayitlar"]) == 1
    kayit = kunye["kayitlar"][0]
    assert kayit["yontem"] != "hata", (
        "REGRESYON: eski ARIZA önbellek kaydı HIT sayılıp bayat sonuç basıldı — "
        "dosya yeniden işlenmedi."
    )
    assert kayit["yontem"] == "duz-metin"
    # karakter = anlamlı (boşluksuz) karakter sayısı — oa_ingest.anlamli() ile aynı ölçüm.
    assert kayit["karakter"] == len(re.sub(r"\s+", "", "GERÇEK METİN İÇERİĞİ"))
    md_metni = (metin_dizin / kayit["md"]).read_text(encoding="utf-8")
    assert "GERÇEK METİN İÇERİĞİ" in md_metni

    # Bu koşudan sonra önbellek GERÇEK (arıza-olmayan) sonuçla güncellenmiş olmalı.
    yeni_onbellek = json.loads((metin_dizin / ".ingest-onbellek.json").read_text(encoding="utf-8"))
    assert yeni_onbellek["dosya.txt"]["kayit"]["yontem"] == "duz-metin"
