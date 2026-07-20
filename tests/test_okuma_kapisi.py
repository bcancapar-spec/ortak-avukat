# -*- coding: utf-8 -*-
"""oa-pipeline / okuma_kapisi.py için ALTIN VAKA testleri (GATE B — OKUMA KAPISI).

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
CLI çağrıları subprocess ile yapılır (main() argparse + sys.exit kullanıyor);
her test kendi tmp_path kökünü kullanarak izole çalışır.

Odak: (1) 00-kunye.json'dan SADECE MEKANİK öncelikli evrak listesi + büyük-evrak
uyarısı, (2) tam-yükleme dedup defterinin mükerrer tam yüklemede UYARMASI ama
ASLA BLOKLAMAMASI (advisory, derinlik kısılmaz).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "okuma_kapisi.py"


def _load():
    assert SCRIPT.is_file(), f"okuma_kapisi.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("okuma_kapisi", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ok = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _kunye_yaz(tmp_path, kayitlar, buyuk_esik=40000):
    metin_dizin = tmp_path / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    kunye = {
        "klasor": str(tmp_path), "toplam_evrak": len(kayitlar),
        "ocr_teyit_gerek": sum(1 for k in kayitlar if k.get("teyit_gerek")),
        "bilinmeyen": 0, "buyuk_evrak": sum(1 for k in kayitlar if k.get("buyuk")),
        "buyuk_esik": buyuk_esik,
        "toplam_karakter": sum(k.get("karakter", 0) for k in kayitlar),
        "tahmini_token": 0, "kayitlar": kayitlar,
    }
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps(kunye, ensure_ascii=False, indent=2), encoding="utf-8")
    return kunye


# ── künye yoksa: dur, açık hata ─────────────────────────────────────────────

def test_kunye_yoksa_hata_ile_durur(tmp_path):
    kod, cikti = _cli(["--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1
    assert "künye bulunamadı" in cikti.lower() or "kunye bulunamadi" in cikti.lower()


# ── öncelik sırası: tebligat/karar önce, tahmin edilemeyen sona ────────────

def test_oncelik_sirasi_tebligat_once_bilinmeyen_sonra(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "bilanço 2024", "kaynak": "a.pdf", "tur_tahmini": "bilanco",
         "karakter": 500, "teyit_gerek": False, "buyuk": False, "md": "001-a.md"},
        {"no": "002", "ad": "tebligat 12.01", "kaynak": "b.pdf", "tur_tahmini": "tebligat",
         "karakter": 300, "teyit_gerek": False, "buyuk": False, "md": "002-b.md"},
        {"no": "003", "ad": "rastgele evrak", "kaynak": "c.pdf", "tur_tahmini": None,
         "karakter": 200, "teyit_gerek": False, "buyuk": False, "md": "003-c.md"},
        {"no": "004", "ad": "karar 2023/55", "kaynak": "d.pdf", "tur_tahmini": "karar",
         "karakter": 400, "teyit_gerek": False, "buyuk": False, "md": "004-d.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    kod, cikti = _cli(["--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    # tebligat ilk sırada, sonra karar, sonra bilanço, en sonda tahminsiz olmalı
    poz_tebligat = cikti.index("002-b.md")
    poz_karar = cikti.index("004-d.md")
    poz_bilanco = cikti.index("001-a.md")
    poz_bilinmeyen = cikti.index("003-c.md")
    assert poz_tebligat < poz_karar < poz_bilanco < poz_bilinmeyen, cikti


# ── büyük evrak uyarısı ──────────────────────────────────────────────────

def test_buyuk_evrak_uyarisi_haritayla_gorunur(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "bilirkişi raporu", "kaynak": "buyuk.pdf",
         "tur_tahmini": "bilirkisi", "karakter": 55000, "teyit_gerek": False,
         "buyuk": True, "harita": "001-buyuk.harita.json", "md": "001-buyuk.md"},
        {"no": "002", "ad": "kısa dilekçe", "kaynak": "kucuk.pdf", "tur_tahmini": "dilekce",
         "karakter": 800, "teyit_gerek": False, "buyuk": False, "md": "002-kucuk.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    kod, cikti = _cli(["--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "BÜYÜK EVRAK UYARISI" in cikti
    assert "buyuk.pdf" in cikti
    assert "001-buyuk.harita.json" in cikti
    # küçük evrak büyük-evrak uyarı bloğunda GEÇMEMELİ
    uyari_blogu = cikti.split("BÜYÜK EVRAK UYARISI", 1)[1]
    assert "kucuk.pdf" not in uyari_blogu


def test_json_ciktisi_yazilir(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "tebligat", "kaynak": "t.pdf", "tur_tahmini": "tebligat",
         "karakter": 300, "teyit_gerek": False, "buyuk": False, "md": "001-t.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    hedef = tmp_path / "oncelik.json"
    kod, cikti = _cli(["--kok", str(tmp_path), "--json", str(hedef)], cwd=tmp_path)
    assert kod == 0, cikti
    assert hedef.is_file()
    veri = json.loads(hedef.read_text(encoding="utf-8"))
    assert veri["liste"][0]["kaynak"] == "t.pdf"


# ── tam-yükleme dedup defteri: UYARIR ama BLOKLAMAZ ────────────────────────

def test_tam_yukle_kaydet_ilk_seferde_uyarmaz(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "büyük bilirkişi", "kaynak": "buyuk.pdf",
         "tur_tahmini": "bilirkisi", "karakter": 55000, "teyit_gerek": False,
         "buyuk": True, "harita": "001-buyuk.harita.json", "md": "001-buyuk.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    kod, cikti = _cli(
        ["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf", "--ajan", "oa-vakia"],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "TAM YÜKLEME KAYDEDİLDİ" in cikti
    assert "UYARI" not in cikti
    defter = tmp_path / "_oa" / "defter" / "tam-yukleme.jsonl"
    assert defter.is_file()
    satirlar = [json.loads(s) for s in defter.read_text(encoding="utf-8").splitlines() if s.strip()]
    assert len(satirlar) == 1
    assert satirlar[0]["kaynak"] == "buyuk.pdf"
    assert satirlar[0]["ajan"] == "oa-vakia"
    assert satirlar[0]["buyuk_kunyede"] is True


def test_tam_yukle_kaydet_ikinci_seferde_uyarir_ama_kod_0(tmp_path):
    """AYNI büyük evrak İKİNCİ kez tam yüklenince script UYARIR — ama exit 0
    (BLOKLAMAZ, advisory — derinlik kısılmaz doktrini)."""
    kayitlar = [
        {"no": "001", "ad": "büyük bilirkişi", "kaynak": "buyuk.pdf",
         "tur_tahmini": "bilirkisi", "karakter": 55000, "teyit_gerek": False,
         "buyuk": True, "harita": "001-buyuk.harita.json", "md": "001-buyuk.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    kod1, _c1 = _cli(["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf"], cwd=tmp_path)
    assert kod1 == 0
    kod2, cikti2 = _cli(["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf"], cwd=tmp_path)
    assert kod2 == 0, "mükerrer tam yükleme BLOKLANMAMALI — yalnız uyarılmalı"
    assert "UYARI" in cikti2
    assert "2. kez" in cikti2 or "(2. kez)" in cikti2

    defter = tmp_path / "_oa" / "defter" / "tam-yukleme.jsonl"
    satirlar = [json.loads(s) for s in defter.read_text(encoding="utf-8").splitlines() if s.strip()]
    assert len(satirlar) == 2, "append-only: iki kayıt da defterde kalmalı"


def test_liste_komutu_mukerrer_tam_yuklemeyi_gosterir(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "büyük bilirkişi", "kaynak": "buyuk.pdf",
         "tur_tahmini": "bilirkisi", "karakter": 55000, "teyit_gerek": False,
         "buyuk": True, "harita": "001-buyuk.harita.json", "md": "001-buyuk.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    _cli(["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf"], cwd=tmp_path)
    _cli(["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf"], cwd=tmp_path)
    kod, cikti = _cli(["--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "DAHA ÖNCE 2 kez TAM yüklenmiş" in cikti


def test_tam_yukle_defter_bos_ve_dolu(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "büyük bilirkişi", "kaynak": "buyuk.pdf",
         "tur_tahmini": "bilirkisi", "karakter": 55000, "teyit_gerek": False,
         "buyuk": True, "harita": "001-buyuk.harita.json", "md": "001-buyuk.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    kod0, cikti0 = _cli(["--kok", str(tmp_path), "--tam-yukle-defter"], cwd=tmp_path)
    assert kod0 == 0
    assert "boş" in cikti0.lower()

    _cli(["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf", "--ajan", "oa-vakia"],
         cwd=tmp_path)
    _cli(["--kok", str(tmp_path), "--tam-yukle-kaydet", "buyuk.pdf", "--ajan", "oa-antitez"],
         cwd=tmp_path)
    kod1, cikti1 = _cli(["--kok", str(tmp_path), "--tam-yukle-defter"], cwd=tmp_path)
    assert kod1 == 0
    assert "buyuk.pdf: 2 kez" in cikti1
    assert "mükerrer" in cikti1


def test_tam_yukle_kaydet_kunyede_olmayan_kaynak_da_kabul_edilir(tmp_path):
    """Künyede bulunmayan bir kaynak elle girilirse BLOKLANMAZ; yalnız
    bilgilendirici not verilir (sessiz-atlama yasağı ile tutarlı, ama katı değil)."""
    kayitlar = [
        {"no": "001", "ad": "x", "kaynak": "x.pdf", "tur_tahmini": None,
         "karakter": 100, "teyit_gerek": False, "buyuk": False, "md": "001-x.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    kod, cikti = _cli(
        ["--kok", str(tmp_path), "--tam-yukle-kaydet", "elle-girilmis.pdf"], cwd=tmp_path)
    assert kod == 0
    assert "künye ile eşleşmedi" in cikti or "eşleşmedi" in cikti


# ── --kok cwd-bağımsızlık: farklı cwd'den mutlak --kok ile çalışır ─────────

def test_kok_ile_cwd_bagimsiz_calisir(tmp_path):
    kayitlar = [
        {"no": "001", "ad": "tebligat", "kaynak": "t.pdf", "tur_tahmini": "tebligat",
         "karakter": 300, "teyit_gerek": False, "buyuk": False, "md": "001-t.md"},
    ]
    _kunye_yaz(tmp_path, kayitlar)
    baska_cwd = tmp_path.parent
    kod, cikti = _cli(["--kok", str(tmp_path)], cwd=baska_cwd)
    assert kod == 0, cikti
    assert "001-t.md" in cikti
