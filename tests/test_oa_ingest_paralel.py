# -*- coding: utf-8 -*-
"""oa-ingest v1.5 / PARALEL ÇIKARIM — VERİ KAYBI KANITI testi (Fable K reçetesi #2).

v1.5 çıkarımı çok-çekirdeğe taşıdı. Tek kabul ölçütü: paralellik ÇIKTIYI DEĞİŞTİRMEZ.
Bu dosya bunu deterministik olarak kanıtlar — hiçbiri Tesseract gerektirmez (--ocr kapali,
yalnız düz-metin/arşiv), CI-güvenli ve İÇERİK-AGNOSTİK (belirli bir dava korpusuna bağlı
DEĞİL; genel/sınırsız evrak deseni: ad çakışması, çok-evraklı arşiv, boş/bozuk arşiv,
0-bayt dosya, bilinmeyen uzantı).

İSPATLANAN İNVARYANTLAR:
  1. seri (--isci 1) == paralel (--isci N)  →  künye YAPISAL özdeş (kaynak=göreli yol,
     abspath'siz) + her md dosyasının sha256'sı AYNI + md ad kümesi AYNI.
  2. Aynı dizinde çift --yeniden koşu  →  00-kunye.json BYTE-AYNI (literal determinizm).
  3. İdempotens: soğuk koşu (önbellek üretir) == sıcak koşu (hepsi önbellekten) künye.
  4. SESSİZ-ATLAMA YASAĞI: bozuk arşiv / boş arşiv / bilinmeyen uzantı / 0-bayt dosya —
     hiçbiri DÜŞMEZ; her biri künyeye (hata/elle kontrol damgasıyla) GİRER.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"


# ---------------- yardımcılar ----------------
def _korpus_kur(kok):
    """İçerik-agnostik ama TUZAKLI sentetik külliyat kur (genel evrak desenleri)."""
    kok = pathlib.Path(kok)
    (kok / "a").mkdir(parents=True, exist_ok=True)
    (kok / "b").mkdir(parents=True, exist_ok=True)
    # (i) aynı taban-adlı iki evrak, farklı klasör → md ad çakışması dalı
    (kok / "a" / "001-dilekce.txt").write_text("DAVACI beyani — birinci koldan", encoding="utf-8")
    (kok / "b" / "001-dilekce.txt").write_text("DAVALI cevabi — ikinci koldan", encoding="utf-8")
    # (ii) kök düzeyinde düz metin
    (kok / "002-mutalaa.txt").write_text("hukuki mutalaa govdesi " * 3, encoding="utf-8")
    # (iii) çok-evraklı arşiv → a/b ek-harflemesi dalı
    z = kok / "005-paket.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("apple.txt", "arsiv ici birinci evrak")
        zf.writestr("banana.txt", "arsiv ici ikinci evrak")
    # (iv) boş arşiv (yalnız desteklenmeyen iç tür) → 'arşiv-boş' damgası
    zb = kok / "006-bos.zip"
    with zipfile.ZipFile(zb, "w") as zf:
        zf.writestr("veri.dat", b"\x00\x01\x02desteklenmeyen ic tur")
    # (v) bozuk arşiv (geçerli zip değil) → 'hata' damgası
    (kok / "007-bozuk.eyp").write_bytes(b"BUNLAR RASTGELE BAYTLAR, ZIP DEGIL " * 4)
    # (vi) 0-bayt düz metin → duz-metin, karakter 0
    (kok / "008-sifir.txt").write_bytes(b"")
    # (vii) bilinmeyen uzantı → 'bilinmeyen' damgası (sessiz atlama YASAK)
    (kok / "009-resim.xyz").write_bytes(b"desteklenmeyen uzanti icerigi")


def _kos(klasor, isci, yeniden=False):
    args = [sys.executable, str(SCRIPT), str(klasor), "--ocr", "kapali", "--isci", str(isci)]
    if yeniden:
        args.append("--yeniden")
    cp = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, f"oa_ingest.py hata:\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    return cp


def _kos_ham(klasor, isci, yeniden=False):
    """returncode'u ASSERT ETMEDEN çalıştır (mekanik kapının ATEŞLENDİĞİNİ test etmek için)."""
    args = [sys.executable, str(SCRIPT), str(klasor), "--ocr", "kapali", "--isci", str(isci)]
    if yeniden:
        args.append("--yeniden")
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _metin_dizin(klasor):
    return pathlib.Path(klasor) / "_oa" / "metin"


def _kunye_ham(klasor):
    return (_metin_dizin(klasor) / "00-kunye.json").read_text(encoding="utf-8")


def _kunye(klasor):
    return json.loads(_kunye_ham(klasor))


def _md_sha_haritasi(klasor):
    """künyede anılan her (boş olmayan) md dosyasının sha256'sı → {md_adi: sha}."""
    md = _metin_dizin(klasor)
    harita = {}
    for k in _kunye(klasor)["kayitlar"]:
        ad = k.get("md")
        if ad:
            harita[ad] = hashlib.sha256((md / ad).read_bytes()).hexdigest()
    return harita


def _yapisal(klasor):
    """künye'yi dizin-bağımsız kıl: abspath taşıyan 'klasor' alanını çıkar."""
    d = _kunye(klasor)
    d.pop("klasor", None)
    return d


# ---------------- 1) seri == paralel (bağımsız iki dizin, yapısal + md sha) ----------------
def test_seri_paralel_yapisal_ozdes(tmp_path):
    d1, d4 = tmp_path / "seri", tmp_path / "paralel"
    _korpus_kur(d1)
    _korpus_kur(d4)
    _kos(d1, isci=1)     # seri
    _kos(d4, isci=4)     # paralel

    assert _yapisal(d1) == _yapisal(d4), "seri ile paralel künye YAPISAL farklı — determinizm bozuk"
    assert _md_sha_haritasi(d1) == _md_sha_haritasi(d4), "md dosyalarının sha256'ları farklı — içerik kayması"


# ---------------- 2) aynı dizin, çift --yeniden → künye BYTE-AYNI ----------------
def test_seri_paralel_byte_ayni_ayni_dizin(tmp_path):
    _korpus_kur(tmp_path)
    _kos(tmp_path, isci=1, yeniden=True)
    seri_bytes = _kunye_ham(tmp_path)
    seri_md = _md_sha_haritasi(tmp_path)

    _kos(tmp_path, isci=6, yeniden=True)   # aynı dizin, paralel, önbellek yok say
    paralel_bytes = _kunye_ham(tmp_path)
    paralel_md = _md_sha_haritasi(tmp_path)

    assert seri_bytes == paralel_bytes, "00-kunye.json BYTE düzeyinde farklı (çekirdek sayısına bağımlı çıktı!)"
    assert seri_md == paralel_md


# ---------------- 3) idempotens: soğuk (önbellek üretir) == sıcak (önbellekten) ----------------
def test_idempotens_sicak_esittir_soguk(tmp_path):
    _korpus_kur(tmp_path)
    _kos(tmp_path, isci=4)               # soğuk → önbellek üretilir
    soguk = _yapisal(tmp_path)
    soguk_md = _md_sha_haritasi(tmp_path)

    _kos(tmp_path, isci=4)               # sıcak → hepsi önbellekten basılmalı
    cp = _kos(tmp_path, isci=4)
    assert "önbellekten:" in cp.stdout
    sicak = _yapisal(tmp_path)
    assert soguk == sicak, "sıcak (önbellekli) koşu künyesi soğuk koşudan farklı — önbellek yolu bozuk"
    assert soguk_md == _md_sha_haritasi(tmp_path)


# ---------------- 4) SESSİZ-ATLAMA YASAĞI: her arıza künyeye DAMGALANIR ----------------
def test_arizalar_sessizce_dusmez_kunyeye_girer(tmp_path):
    _korpus_kur(tmp_path)
    _kos(tmp_path, isci=4)
    kayitlar = {k["kaynak"]: k for k in _kunye(tmp_path)["kayitlar"]}

    # bilinmeyen uzantı → yöntem 'bilinmeyen', md yok, hata damgalı
    bil = kayitlar[str(pathlib.Path("009-resim.xyz"))]
    assert bil["yontem"] == "bilinmeyen" and bil["md"] == "" and "elle kontrol" in (bil["hata"] or "")

    # bozuk arşiv → yöntem 'hata'
    boz = kayitlar[str(pathlib.Path("007-bozuk.eyp"))]
    assert boz["yontem"] == "hata"

    # boş arşiv → 'arşiv-boş'
    bos = kayitlar[str(pathlib.Path("006-bos.zip"))]
    assert bos["yontem"] == "arşiv-boş"

    # çok-evraklı arşiv → İKİ iç kayıt (a/b ek-harfli), kaynak "arşiv::iç" biçimli
    ic = [k for k in _kunye(tmp_path)["kayitlar"] if str(pathlib.Path("005-paket.zip")) + "::" in k["kaynak"]]
    assert len(ic) == 2, "çok-evraklı arşivin iç evrakları eksik — sessiz kayıp"
    assert {k["no"][-1] for k in ic} == {"a", "b"}

    # 0-bayt dosya → duz-metin, karakter 0 (düşmez)
    sfr = kayitlar[str(pathlib.Path("008-sifir.txt"))]
    assert sfr["yontem"] == "duz-metin" and sfr["karakter"] == 0

    # aynı-ad iki dilekçe → FARKLI md (çakışma ezmedi)
    a1 = kayitlar[str(pathlib.Path("a") / "001-dilekce.txt")]
    b1 = kayitlar[str(pathlib.Path("b") / "001-dilekce.txt")]
    assert a1["md"] != b1["md"]


# ---------------- 5) mekanik kapı sağlam: hiçbir kayıt kaybolmaz (toplam sayım) ----------------
def test_mekanik_kapi_tam_sayim(tmp_path):
    _korpus_kur(tmp_path)
    _kos(tmp_path, isci=8)
    kunye = _kunye(tmp_path)
    # 7 kaynak dosya: a/001, b/001, 002, 005-paket(→2 iç), 006-bos, 007-bozuk, 008-sifir, 009-resim
    # kayıt sayısı = 2(dilekçe)+1(mutalaa)+2(paket içi)+1(bos)+1(bozuk)+1(sifir)+1(resim) = 9
    assert kunye["toplam_evrak"] == len(kunye["kayitlar"]) == 9


# ---------------- 6) MEKANİK KAPI GERÇEKTEN ateşlenir (Fable K: eski kapı totolojiydi) ----------------
def test_mekanik_kapi_bos_onbellek_yakalar(tmp_path):
    """Eski kapı 'append başına say' totolojisiydi → HİÇ ateşlenemezdi. Arşiv-hit dalına
    bozuk önbellekle 'kayitlar': [] enjekte edilince o kaynak SIFIR kayıt üretir; gerçek
    invaryant (her kaynak ≥1 kayıtla temsil) bunu YAKALAMALI: returncode != 0 ve künye
    ÜZERİNE YAZILMAMALI (eski sağlam künye korunur)."""
    _korpus_kur(tmp_path)
    _kos(tmp_path, isci=1)                        # soğuk → önbellek + künye üretir
    kunye_once = _kunye_ham(tmp_path)
    onb_yol = _metin_dizin(tmp_path) / ".ingest-onbellek.json"
    onb = json.loads(onb_yol.read_text(encoding="utf-8"))
    ark = str(pathlib.Path("005-paket.zip"))
    assert ark in onb and onb[ark].get("kayitlar"), "önkoşul: arşiv önbellekte çoklu kayıtla olmalı"
    onb[ark]["kayitlar"] = []                     # imza AYNI kalır → 2. koşuda HIT ama 0 kayıt
    onb_yol.write_text(json.dumps(onb, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    cp = _kos_ham(tmp_path, isci=1)              # sıcak → arşiv 0 kayıt → kapı ATEŞLENMELİ
    assert cp.returncode != 0, "mekanik kapı ateşlenmedi — sessiz kayıp geçti (totoloji geri geldi)"
    assert "mekanik kapı" in (cp.stdout + cp.stderr)
    assert _kunye_ham(tmp_path) == kunye_once, "kapı ateşlenince künye ÜZERİNE YAZILMAMALIYDI"


# ---------------- 7) arşiv-içi aynı taban-ad farklı klasör → benzersiz kaynak + determinizm ----------------
def test_arsiv_ic_ayni_taban_ad_ayrisir(tmp_path):
    """Fable K: iç kimlik yalnız taban-ada bağlıysa EYP içinde farklı alt klasörde aynı
    adlı iki evrak (UYAP'ta gerçekçi) hem platform-bağımlı sıra alır hem 'kaynak'ı BİREBİR
    AYNI olur. Kimlik artık ARŞİV-GÖRELİ YOL → benzersiz + deterministik (klasorA<klasorB → a/b)."""
    z = tmp_path / "010-cok.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("klasorA/content.txt", "A KLASORUNDAKI icerik")
        zf.writestr("klasorB/content.txt", "B KLASORUNDAKI icerik")
    _kos(tmp_path, isci=4)

    ic = [k for k in _kunye(tmp_path)["kayitlar"] if "010-cok.zip::" in k["kaynak"]]
    assert len(ic) == 2, "iki iç evrak da künyede olmalı (biri diğerini yutmamalı)"
    kaynaklar = sorted(k["kaynak"] for k in ic)
    assert kaynaklar == ["010-cok.zip::klasorA/content.txt", "010-cok.zip::klasorB/content.txt"], kaynaklar

    mds = {k["kaynak"]: k["md"] for k in ic}
    assert len(set(mds.values())) == 2, "aynı-ad iki iç evrak FARKLI md almalı"
    md = _metin_dizin(tmp_path)
    a_txt = (md / mds["010-cok.zip::klasorA/content.txt"]).read_text(encoding="utf-8")
    b_txt = (md / mds["010-cok.zip::klasorB/content.txt"]).read_text(encoding="utf-8")
    assert "A KLASORUNDAKI" in a_txt and "B KLASORUNDAKI" not in a_txt
    assert "B KLASORUNDAKI" in b_txt and "A KLASORUNDAKI" not in b_txt

    no_map = {k["kaynak"]: k["no"] for k in ic}    # göreli-yol sırasına göre deterministik a/b
    assert no_map["010-cok.zip::klasorA/content.txt"].endswith("a")
    assert no_map["010-cok.zip::klasorB/content.txt"].endswith("b")
