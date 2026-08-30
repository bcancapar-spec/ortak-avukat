# -*- coding: utf-8 -*-
"""P1-9(b) (v0.5.5) — sözleşme-dışı dizin bekçisi: _oa altında DIZIN_BEYAZ_LISTE
dışı bir birinci-seviye klasör görüldüğünde `pipeline_kayit.py --denetle`/
`--goster` (ve dolayısıyla DURUM.md/KAPANIŞ Gate) GÖRÜNÜR bir uyarı basar —
gölge hat (ör. `_oa/hizli/`) bir daha SESSİZ kalamaz. Advisory: exit kodunu
DEĞİŞTİRMEZ.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
OA_INGEST = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"


def _cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )


def _baslat(tmp_path):
    cp = _cli(["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr


def test_gozle_disi_dizin_denetle_uyarisinda_gorunur(tmp_path):
    _baslat(tmp_path)
    golge = tmp_path / "_oa" / "hizli"
    golge.mkdir()
    (golge / "kacamak.txt").write_text("x", encoding="utf-8")

    cp = _cli(["--denetle", "--kok", "."], tmp_path)
    assert "SÖZLEŞME-DIŞI DİZİN" in cp.stdout
    assert "_oa/hizli" in cp.stdout


def test_gozle_disi_dizin_goster_uyarisinda_gorunur(tmp_path):
    _baslat(tmp_path)
    (tmp_path / "_oa" / "hizli").mkdir()

    cp = _cli(["--goster", "--kok", "."], tmp_path)
    assert "SÖZLEŞME-DIŞI DİZİN" in cp.stdout
    assert "_oa/hizli" in cp.stdout


def test_onbakis_sonrasi_sozlesme_disi_uyarisi_YOK(tmp_path):
    """P1-9 DÜZELTME (ONEMLI, sinav bulgusu) — meşru bir `oa_ingest.py --onbakis`
    koşusunun ürettiği `_oa/metin-onbakis/` bekçi tarafından GÖLGE HAT
    sayılmamalı: sayılırsa (a) meşru bir --onbakis koşusundan sonra 'gölge-dizin
    uyarısı 0' kabul ölçütü ASLA sağlanamaz, (b) P2-14 görünmez-kaçış sayacı
    kalıcı yanlış-pozitif alır."""
    _baslat(tmp_path)
    (tmp_path / "001-evrak.txt").write_text(
        "Test evrakı — yeterince uzun metin örneği burada tekrar eder. " * 2,
        encoding="utf-8")
    # v0.5.14/B-25: klasör AÇIKÇA verilir (argümansız koşu artık reddedilir).
    cp = subprocess.run([sys.executable, str(OA_INGEST), ".", "--ocr", "kapali", "--onbakis", "1"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         cwd=str(tmp_path))
    assert cp.returncode == 4, cp.stdout + cp.stderr
    assert (tmp_path / "_oa" / "metin-onbakis").is_dir()

    cp2 = _cli(["--denetle", "--kok", "."], tmp_path)
    assert "SÖZLEŞME-DIŞI DİZİN" not in cp2.stdout, (
        "meşru --onbakis artefaktı gölge-hat sayıldı (P1-9 REGRESYONU):\n" + cp2.stdout)


def test_sozlesme_dizinleri_uyari_uretmez(tmp_path):
    _baslat(tmp_path)
    # cmd_init tarafından zaten yaratılan sözleşme dizinleri (defter/cikti/...)
    # + üretici modüllerin dizinleri (metin/analiz) uyarı üretmemeli.
    for ad in ("defter", "devir", "cikti", "teyit", "oturum", "arsiv-yerel",
               "metin", "analiz"):
        (tmp_path / "_oa" / ad).mkdir(parents=True, exist_ok=True)

    cp = _cli(["--denetle", "--kok", "."], tmp_path)
    assert "SÖZLEŞME-DIŞI DİZİN" not in cp.stdout


def test_uyari_exit_kodunu_degistirmez(tmp_path):
    _baslat(tmp_path)
    (tmp_path / "_oa" / "hizli").mkdir()
    # boşluklu tur (--denetle exit != 0 ZATEN üretir) — gölge-dizin uyarısı bu
    # kararı DEĞİŞTİRMEMELİ (advisory kalır, blokleyiciye yükselmez).
    cp_bos = _cli(["--denetle", "--kok", "."], tmp_path)
    kod_bos = cp_bos.returncode
    assert kod_bos != 0  # hiç adım işlenmemiş boşluklu tur zaten TESLİM ENGELİ

    # gölge dizin OLMADAN aynı boşluklu turun exit kodu ile KIYASLA — aynı olmalı.
    import shutil
    shutil.rmtree(tmp_path / "_oa" / "hizli")
    cp_temiz = _cli(["--denetle", "--kok", "."], tmp_path)
    assert cp_temiz.returncode == kod_bos


def test_beyaz_liste_tek_kaynaktan_gelir():
    """P1-9 DÜZELTME (sinav bulgusu) — yalnız ÜYELİK değil, TEK-KAYNAKLILIĞIN
    KENDİSİ sınanır: DIZIN_BEYAZ_LISTE, oa_hafiza.DIZINLER'i canlı olarak
    değiştirip yeniden hesaplandığında bu değişikliği YANSITMALIDIR (elle
    kopyalanmış sabit bir küme olsaydı bu test KIRILIRDI)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("pk_golge_dizin_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert "metin" in mod.DIZIN_BEYAZ_LISTE
    assert "metin-onbakis" in mod.DIZIN_BEYAZ_LISTE
    assert "analiz" in mod.DIZIN_BEYAZ_LISTE
    for ad in ("defter", "devir", "cikti", "teyit", "oturum", "arsiv-yerel"):
        assert ad in mod.DIZIN_BEYAZ_LISTE

    # Tek-kaynaklılığın kendisi: oa_hafiza.DIZINLER'e yeni bir dizin ekleyip
    # yeniden hesapla — sonuç bu ekten HABERDAR olmalı (ikiz-liste OLSAYDI
    # olmazdı).
    hafiza = mod._oa_hafiza_modulu_beyaz_liste()
    assert hafiza is not None, "oa_hafiza.py İN-PROCESS import edilemedi"
    orijinal = list(hafiza.DIZINLER)
    try:
        hafiza.DIZINLER.append("yeni-test-dizini")
        yeniden = mod._dizin_beyaz_liste_hesapla()
        assert "yeni-test-dizini" in yeniden, (
            "DIZIN_BEYAZ_LISTE oa_hafiza.DIZINLER'den TÜRETİLMİYOR — ikiz-liste "
            "sızıntısı (P1-9 REGRESYONU)")
    finally:
        hafiza.DIZINLER[:] = orijinal

    # oa_ingest.ONBAKIS_DIZIN de aynı şekilde tek kaynaktan gelir.
    ingest = mod._oa_ingest_modulu_beyaz_liste()
    assert ingest is not None, "oa_ingest.py İN-PROCESS import edilemedi"
    assert ingest.ONBAKIS_DIZIN == "metin-onbakis"
