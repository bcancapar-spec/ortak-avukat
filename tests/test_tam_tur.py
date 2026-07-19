# -*- coding: utf-8 -*-
"""oa-pipeline / tam_tur.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
cmd_* fonksiyonları sys.exit ÇAĞIRMAZ (yalnız main() çağırır) — bu yüzden
doğrudan import edilip int dönüş değeriyle test edilebilir (tmp_path izolasyonu).

Odak: (1) sha tabanlı delta tespiti — künye içeriği DEĞİŞTİĞİNDE (aynı dosya
adı, farklı sha) delta YENİ turda YAKALANMALI; (2) yutma denetimi — bekleyen
delta hiçbir GELİŞME kaydında anılmadan ikinci `--kaydet` ile snapshot'a
sessizce yutulamaz (--zorla olmadan RET).
"""
import hashlib
import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"


def _load():
    assert SCRIPT.is_file(), f"tam_tur.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("tam_tur", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tt = _load()


def _sha(icerik):
    return hashlib.sha256(icerik.encode("utf-8")).hexdigest()[:16]


def _kunye_yaz(kok, kayitlar):
    """_oa/metin/00-kunye.json yaz (tam_tur'un beklediği minimal şema).

    Ayrıca her `kaynak` için kökte BOŞ bir plasöy-holder dosya dokunur:
    tam_tur'un "KÜNYE BAYAT" denetimi (_bayat_kunye), künyede anılan kaynağın
    fiziken diskte VAR olup olmadığını ayrıca kontrol eder — asıl test
    konusu olan sha-tabanlı delta mantığına ulaşmadan önce bu ayrı denetim
    'silinmiş/taşınmış' diye erken exit 3 verir. Dosyanın GERÇEK içeriği
    ilgisizdir: delta motoru içerik imzasını YALNIZ künyedeki `sha` alanından
    okur (bkz. _evrak_imzalari), diskteki dosyayı yeniden hashlemez."""
    metin_dizin = kok / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    kunye = {"toplam_evrak": len(kayitlar), "kayitlar": kayitlar}
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps(kunye, ensure_ascii=False), encoding="utf-8")
    for k in kayitlar:
        kaynak = k.get("kaynak")
        if not kaynak:
            continue
        yol = kok / kaynak
        if not yol.exists():
            yol.parent.mkdir(parents=True, exist_ok=True)
            yol.write_text("plasöy-holder", encoding="utf-8")


def _cikti_birak(kok, ad="01-parca.md", icerik="çalışma evrakı"):
    cikti_dizin = kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / ad).write_text(icerik, encoding="utf-8")


# ── sha tabanlı delta: aynı ad, DEĞİŞEN içerik → 2. döngüde YAKALANIR ───────

def test_sha_delta_ikinci_dongude_yakalanir(tmp_path):
    ilk_icerik = "dilekçe metni v1"
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha(ilk_icerik)}])
    _cikti_birak(tmp_path)

    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    # Hemen ardından delta YOK olmalı (snapshot güncel).
    assert tt.cmd_delta(str(tmp_path)) == 0

    # İçerik DEĞİŞİYOR (aynı dosya adı, farklı sha) — bu, sha-tabanlı imzanın
    # yakalaması gereken TAM senaryo: karakter sayısı aynı kalsa bile içerik
    # hash'i değişmişse "değişen evrak" sayılmalı.
    yeni_icerik = "dilekçe metni v2"  # aynı uzunlukta, farklı içerik
    assert len(yeni_icerik) == len(ilk_icerik)
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha(yeni_icerik)}])

    kod = tt.cmd_delta(str(tmp_path))
    assert kod == 3, "sha değiştiği halde delta YOK dendi (2. döngü regresyonu)"

    yeni, degisen, silinen = tt._delta_hesapla(str(tmp_path), tt._durum_oku(str(tmp_path)))
    assert degisen == ["dilekce.pdf"], f"DEĞİŞEN evrak listesi yanlış: {degisen}"
    assert yeni == [] and silinen == []


def test_yeni_evrak_delta_yakalanir(tmp_path):
    _kunye_yaz(tmp_path, [{"kaynak": "ilk.pdf", "sha": _sha("a")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0
    assert tt.cmd_delta(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [
        {"kaynak": "ilk.pdf", "sha": _sha("a")},
        {"kaynak": "ikinci.pdf", "sha": _sha("b")},
    ])
    kod = tt.cmd_delta(str(tmp_path))
    assert kod == 3
    yeni, degisen, silinen = tt._delta_hesapla(str(tmp_path), tt._durum_oku(str(tmp_path)))
    assert yeni == ["ikinci.pdf"]
    assert degisen == [] and silinen == []


# ── Yutma denetimi (2. döngü): bekleyen delta GELİŞME'de anılmadan yutulamaz ─

def test_islenmemis_delta_gelisme_olmadan_kaydete_yutulamaz(tmp_path):
    """İKİNCİ tam tur döngüsü: bir önceki snapshot'tan sonra evrak değişti
    (bekleyen delta var) ama hiçbir `--ekle` ile işlenmedi. `--kaydet` bunu
    --zorla OLMADAN sessizce yutmamalı (exit 1, RET)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    # İçerik değişti ama hiç `--ekle` ile işlenmedi (yutma senaryosu).
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])

    kod = tt.cmd_kaydet(str(tmp_path))
    assert kod == 1, "işlenmemiş delta GELİŞME'de anılmadan --zorla olmadan yutulmamalı"


def test_islenmis_delta_gelisme_ile_kaydete_gecer(tmp_path):
    """Kontrast: bekleyen delta `--ekle` ile GELİŞME günlüğüne işlenmişse
    ikinci `--kaydet` sorunsuz geçmeli (exit 0)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])
    assert tt.cmd_ekle(str(tmp_path), "dilekce.pdf güncellendi, gözden geçirildi") == 0

    kod = tt.cmd_kaydet(str(tmp_path))
    assert kod == 0, "GELİŞME'de anılmış bekleyen delta ikinci kaydet'i engellememeli"


def test_zorla_ile_yutma_serh_dusulerek_gecer(tmp_path):
    """--zorla ile yutma engellenmez ama ŞERH düşülür (sessiz geçiş yok)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])
    kod = tt.cmd_kaydet(str(tmp_path), zorla=True)
    assert kod == 0
    analiz_md = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert "ŞERH" in analiz_md
    assert "dilekce.pdf" in analiz_md
