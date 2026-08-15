# -*- coding: utf-8 -*-
"""v0.5.8.4 — GATE A DİRİLTME (büyük-evrak okuma ekonomisi) testleri.

SAHA KANITI (iki ayrı saha koşusu): binlerce md'ye karşı 0 adet .harita.json;
00-kunye.json'da `buyuk_esik`/`buyuk_evrak` alanları ŞEMADA BİLE YOK; kayıtlarda
`buyuk`/`harita` anahtarı yok (v1.5 dönemi şeması). KÖK NEDEN: harita üretimi
yalnız çıkarım (önbellek-MISS) yolundaki md_yaz'a bağlıydı; önbellek-HIT kayıtları
künyeye OLDUĞU GİBİ basılıyordu → v1.6 öncesi bir motorla ingest edilmiş korpusta
kaynak dosyaların imzası (mtime+size) hiç değişmediği için Gate A SONSUZA DEK ölü
kalıyordu. Bu dosya üç şeyi kanıtlar:

  1) Taze koşuda 45k'lık sentetik evrak → .harita.json + künyede buyuk_esik==40000,
     buyuk_evrak>=1, kayıtta buyuk:true + harita dolu (varsayılan eşikle, bayraksız).
  2) 2k'lık evrak → harita YOK, buyuk_evrak==0 ama alanlar HER koşuda MEVCUT.
  3) DİRİLTME: v1.5-şemalı eski korpus (künye+önbellekte buyuk/harita anahtarı yok,
     harita dosyası yok) önbellek-HIT'li bir sonraki koşuda KENDİNİ İYİLEŞTİRİR —
     harita md'den BYTE-ÖZDEŞ geri üretilir, künye alanları dolar, önbellek de
     onarılır (sonraki koşular yeniden stat-only kalır).

Testler tmp_path + sentetik veri kullanır — gerçek dava yolu/kişi verisi YASAK (m.7).
"""
import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"

BUYUK_ESIK_VARSAYILAN = 40000


def _kos(klasor, ekstra=None):
    args = [sys.executable, str(SCRIPT), str(klasor), "--ocr", "kapali", "--isci", "1"]
    if ekstra:
        args += ekstra
    cp = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, f"oa_ingest.py hata:\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    return cp


def _metin_dizin(klasor):
    return pathlib.Path(klasor) / "_oa" / "metin"


def _kunye(klasor):
    return json.loads((_metin_dizin(klasor) / "00-kunye.json").read_text(encoding="utf-8"))


def _buyuk_evrak_yaz(klasor, ad="001-buyuk-bilirkisi-raporu.txt"):
    """~45k ANLAMLI (boşluk-dışı) karakterlik sentetik evrak — varsayılan 40000
    eşiğini bayraksız koşuda aşar. Satır gövdesi 45 boşluk-dışı karakter × 1000."""
    satir = "SentetikHukukiMetinSatiriABCDEFGH0123456789XY \n"   # 45 anlamlı karakter
    (pathlib.Path(klasor) / ad).write_text("BÜYÜK EVRAK BAŞLIĞI\n" + satir * 1000,
                                           encoding="utf-8")
    return ad


# ==================== 1) taze koşu — büyük evrak (varsayılan eşik) ====================

def test_taze_kosu_45k_evrak_harita_ve_kunye_alanlari(tmp_path):
    _buyuk_evrak_yaz(tmp_path)
    _kos(tmp_path)   # bayraksız: varsayılan eşik 40000 devrede olmalı

    kunye = _kunye(tmp_path)
    # üst seviye alanlar HER koşuda yazılır
    assert kunye["buyuk_esik"] == BUYUK_ESIK_VARSAYILAN
    assert kunye["buyuk_evrak"] >= 1
    # kayıt düzeyi: buyuk:true + harita dolu
    kayit = kunye["kayitlar"][0]
    assert kayit["buyuk"] is True
    assert kayit["harita"], "büyük evrak için künyede harita adı dolu olmalı"
    harita_yol = _metin_dizin(tmp_path) / kayit["harita"]
    assert harita_yol.exists(), "eşiği aşan evrak için .harita.json üretilmeli"
    harita = json.loads(harita_yol.read_text(encoding="utf-8"))
    # asgari şema: sonraki parçaların seçici okuması için bölümler + offset + karakter
    assert harita["kaynak_md"] == kayit["md"]
    assert harita["adet"] >= 1
    for bolum in harita["bolumler"]:
        assert "offset" in bolum and "baslik" in bolum and "karakter" in bolum


# ==================== 2) küçük evrak — harita yok ama alanlar MEVCUT ====================

def test_kucuk_evrak_harita_yok_ama_alanlar_mevcut(tmp_path):
    (tmp_path / "001-kucuk-dilekce.txt").write_text("kısa dilekçe metni " * 100,
                                                    encoding="utf-8")   # ~2k karakter
    _kos(tmp_path)

    kunye = _kunye(tmp_path)
    # alanlar ŞEMADA — büyük evrak hiç yokken bile
    assert kunye["buyuk_esik"] == BUYUK_ESIK_VARSAYILAN
    assert kunye["buyuk_evrak"] == 0
    kayit = kunye["kayitlar"][0]
    assert kayit["buyuk"] is False
    assert kayit["harita"] == ""
    assert not list(_metin_dizin(tmp_path).glob("*.harita.json"))


# ==================== 3) DİRİLTME — v1.5-şemalı eski korpus önbellek-HIT'te iyileşir ====================

def _v15_semasina_indir(kayit):
    """Kaydı saha künyesindeki v1.5 şemasına indirger (Gate A/C ve P0-9 alanları YOK)."""
    return {k: v for k, v in kayit.items()
            if k in ("no", "ad", "tarih", "kaynak", "yontem", "teyit_gerek",
                     "karakter", "sha", "sayfa", "hata", "md")}


def test_eski_korpus_onbellek_hit_gate_a_dirilir(tmp_path):
    """Saha senaryosu: korpus v1.6 ÖNCESİ bir motorla ingest edilmiş (künye +
    önbellek kayıtlarında buyuk/harita anahtarı YOK, .harita.json YOK), kaynaklar
    hiç değişmediği için sonraki her koşu %100 önbellek-HIT. Yeni koşu Gate A'yı
    DİRİLTMELİ: harita md'den BYTE-ÖZDEŞ geri üretilir, künye alanları dolar."""
    _buyuk_evrak_yaz(tmp_path)
    (tmp_path / "002-kucuk-tebligat.txt").write_text("kısa tebligat metni",
                                                     encoding="utf-8")
    _kos(tmp_path)
    metin_dizin = _metin_dizin(tmp_path)

    # taze harita'nın imzasını al, sonra ESKİ MOTOR ÇIKTISINI taklit et:
    haritalar = list(metin_dizin.glob("*.harita.json"))
    assert len(haritalar) == 1
    taze_harita_sha = hashlib.sha256(haritalar[0].read_bytes()).hexdigest()
    haritalar[0].unlink()                                   # 0 adet .harita.json

    kunye_yol = metin_dizin / "00-kunye.json"
    kunye = json.loads(kunye_yol.read_text(encoding="utf-8"))
    for alan in ("buyuk_esik", "buyuk_evrak"):              # üst seviye şemadan sil
        kunye.pop(alan, None)
    kunye["kayitlar"] = [_v15_semasina_indir(k) for k in kunye["kayitlar"]]
    kunye_yol.write_text(json.dumps(kunye, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    onbellek_yol = metin_dizin / ".ingest-onbellek.json"
    onbellek = json.loads(onbellek_yol.read_text(encoding="utf-8"))
    for onb in onbellek.values():                           # önbellek kayıtları da v1.5
        if onb.get("kayit"):
            onb["kayit"] = _v15_semasina_indir(onb["kayit"])
        if onb.get("kayitlar"):
            onb["kayitlar"] = [_v15_semasina_indir(k) for k in onb["kayitlar"]]
    onbellek_yol.write_text(json.dumps(onbellek, ensure_ascii=False, sort_keys=True),
                            encoding="utf-8")

    # ---- yeni koşu: kaynaklar DEĞİŞMEDİ → %100 önbellek-HIT (yeniden çıkarım YOK) ----
    cp = _kos(tmp_path)
    assert "önbellekten: 2" in cp.stdout, f"beklenen tam HIT koşusu değil:\n{cp.stdout}"

    kunye = _kunye(tmp_path)
    assert kunye["buyuk_esik"] == BUYUK_ESIK_VARSAYILAN
    assert kunye["buyuk_evrak"] == 1
    kayitlar = {k["kaynak"]: k for k in kunye["kayitlar"]}
    buyuk = kayitlar["001-buyuk-bilirkisi-raporu.txt"]
    kucuk = kayitlar["002-kucuk-tebligat.txt"]
    assert buyuk["buyuk"] is True
    assert buyuk["harita"], "önbellek-HIT büyük kayıtta harita adı dolmalı (diriltme)"
    assert kucuk["buyuk"] is False and kucuk["harita"] == ""

    harita_yol = metin_dizin / buyuk["harita"]
    assert harita_yol.exists(), "eksik .harita.json md'den GERİ üretilmeli (onarım)"
    # DETERMİNİZM: geri-üretilen harita taze koşununkiyle BYTE-ÖZDEŞ (uydurma yok)
    assert hashlib.sha256(harita_yol.read_bytes()).hexdigest() == taze_harita_sha

    # önbellek de iyileşti → bir SONRAKİ koşu yeniden stat-only, alanlar kalıcı
    onbellek = json.loads(onbellek_yol.read_text(encoding="utf-8"))
    onarilan = onbellek["001-buyuk-bilirkisi-raporu.txt"]["kayit"]
    assert onarilan.get("buyuk") is True and onarilan.get("harita")


def test_dirilen_korpus_sonraki_kosuda_idempotent(tmp_path):
    """Diriltme TEK SEFERLİKTİR: normalizasyon koşudan koşuya OYNAMAZ.
    NOT: soğuk→sıcak BYTE eşitliği bu kapının işi değil — önbellek `sort_keys`
    ile yazıldığı için kayıt anahtar SIRASI ilk sıcak koşuda alfabetikleşir
    (v1.5'ten beri böyle, İÇERİK aynı). Buradaki iddia: soğuk==sıcak SEMANTİK
    özdeş + sıcak→sıcak BYTE özdeş (normalizasyon kalıcı durum üretmez)."""
    _buyuk_evrak_yaz(tmp_path)
    _kos(tmp_path)
    kunye_yol = _metin_dizin(tmp_path) / "00-kunye.json"
    soguk = json.loads(kunye_yol.read_text(encoding="utf-8"))
    _kos(tmp_path)   # tam HIT koşusu 1
    sicak1 = kunye_yol.read_bytes()
    assert json.loads(sicak1.decode("utf-8")) == soguk, "soğuk≠sıcak (semantik) — normalizasyon içerik değiştirdi"
    _kos(tmp_path)   # tam HIT koşusu 2
    assert kunye_yol.read_bytes() == sicak1, "sıcak→sıcak byte-özdeş değil (idempotens bozuk)"
