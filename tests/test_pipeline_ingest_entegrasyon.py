# -*- coding: utf-8 -*-
"""oa-pipeline ↔ oa-ingest v1.5 (paralel) ENTEGRASYON testi (Aşama 4).

Amaç: `oa_ingest.py`'nin v1.5 `--isci` paralelliği pipeline'ın 0. MANİFEST
hattına (manifest_olustur.py sayım/mutabakat + tam_tur.py TAM TUR/DELTA
yaşam döngüsü) BAĞLANDIĞINDA akışın kırılmadığını ve determinizmin
korunduğunu kanıtlar. `oa_ingest.py`'nin kendi paralellik/determinizm
kanıtı `test_oa_ingest_paralel.py`'dedir; bu dosya onu TEKRARLAMAZ —
yalnız pipeline'ın gerçekten dokümante ettiği ZİNCİRİ (manifest → paralel
ingest → mutabakat → tam_tur snapshot/delta) uçtan uca test eder.

Üç script de dosya-yolundan çağrılır (subprocess) — skill dizinleri paket
değildir; gerçek CLI çağrısı, gerçek dosya sistemi.
"""
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "manifest_olustur.py"
INGEST = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"
TAM_TUR = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"

for _s in (MANIFEST, INGEST, TAM_TUR):
    assert _s.is_file(), f"betik bulunamadı: {_s}"


# ---------------- yardımcılar ----------------
def _korpus_kur(kok):
    """Küçük, içerik-agnostik sentetik dava klasörü (gerçek müvekkil verisi YOK)."""
    kok = pathlib.Path(kok)
    (kok / "dilekceler").mkdir(parents=True, exist_ok=True)
    (kok / "kararlar").mkdir(parents=True, exist_ok=True)
    (kok / "dilekceler" / "001-dava-dilekcesi.txt").write_text(
        "DAVACI vekili beyan eder ki " * 5, encoding="utf-8")
    (kok / "dilekceler" / "002-cevap-dilekcesi.txt").write_text(
        "DAVALI vekili cevaben beyan eder ki " * 5, encoding="utf-8")
    (kok / "kararlar" / "003-karar.txt").write_text(
        "MAHKEME karar verir ki " * 5, encoding="utf-8")
    (kok / "004-mutalaa.txt").write_text("hukuki mütalaa gövdesi " * 5, encoding="utf-8")


def _run(args, cwd=None):
    cp = subprocess.run(
        [sys.executable] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd,
    )
    return cp


def _manifest_json(kok, dosya="manifest.json"):
    # JSON çıktısı KORPUS KÖKÜNÜN DIŞINA yazılır — köke yazılsaydı manifest.json'un
    # kendisi bir sonraki taramada "ham evrak" sayılıp evrak adedini şişirirdi.
    out = pathlib.Path(kok).parent / f"{pathlib.Path(kok).name}-{dosya}"
    cp = _run([MANIFEST, kok, "--json", out])
    assert cp.returncode == 0, cp.stdout + cp.stderr
    return json.loads(out.read_text(encoding="utf-8")), cp


def _ingest(kok, isci=None, yeniden=False):
    args = [INGEST, kok, "--ocr", "kapali"]
    if isci is not None:
        args += ["--isci", str(isci)]
    if yeniden:
        args.append("--yeniden")
    cp = _run(args)
    assert cp.returncode == 0, f"oa_ingest.py hata:\n{cp.stdout}\n{cp.stderr}"
    return cp


def _kunye_yolu(kok):
    return pathlib.Path(kok) / "_oa" / "metin" / "00-kunye.json"


def _kunye(kok):
    return json.loads(_kunye_yolu(kok).read_text(encoding="utf-8"))


def _mutabakat(kok):
    return _run([MANIFEST, kok, "--mutabakat", _kunye_yolu(kok)])


def _tam_tur(args, kok):
    return _run([TAM_TUR, "--kok", str(kok)] + list(args))


# ---------------- 1) 0. MANİFEST: sayım → PARALEL ingest → mutabakat kırılmaz ----------------
def test_manifest_paralel_ingest_mutabakat_tutar(tmp_path):
    _korpus_kur(tmp_path)
    manifest, _cp = _manifest_json(tmp_path)
    assert manifest["toplam"] == 4, "sentetik korpus 4 ham dosya olmalı"

    # pipeline dokümanının anlattığı gibi: 0. adımda oa_ingest.py PARALEL koşar
    _ingest(tmp_path, isci=4)

    mut = _mutabakat(tmp_path)
    assert mut.returncode == 0, f"paralel ingest sonrası mutabakat TUTMADI:\n{mut.stdout}\n{mut.stderr}"
    assert "TUTUYOR" in mut.stdout


# ---------------- 2) --isci VERİLMEZSE otomatik paralellik de akışı bozmaz ----------------
def test_isci_verilmezse_otomatik_da_mutabakat_tutar(tmp_path):
    _korpus_kur(tmp_path)
    _manifest_json(tmp_path)
    _ingest(tmp_path, isci=None)   # --isci hiç verilmedi → script içi varsayılan (oto) devrede

    kunye = _kunye(tmp_path)
    assert kunye["toplam_evrak"] == 4
    mut = _mutabakat(tmp_path)
    assert mut.returncode == 0
    assert "TUTUYOR" in mut.stdout


# ---------------- 3) seri (--isci 1) ↔ paralel (--isci N): pipeline zinciri özdeş sonuç ----------------
def test_seri_paralel_pipeline_zincirinde_ozdes(tmp_path):
    d_seri, d_paralel = tmp_path / "seri", tmp_path / "paralel"
    _korpus_kur(d_seri)
    _korpus_kur(d_paralel)
    _manifest_json(d_seri)
    _manifest_json(d_paralel)

    _ingest(d_seri, isci=1)
    _ingest(d_paralel, isci=8)

    for d in (d_seri, d_paralel):
        mut = _mutabakat(d)
        assert mut.returncode == 0 and "TUTUYOR" in mut.stdout, f"{d}: mutabakat tutmadı"

    k_seri, k_paralel = _kunye(d_seri), _kunye(d_paralel)
    k_seri.pop("klasor", None)
    k_paralel.pop("klasor", None)
    assert k_seri == k_paralel, "0. MANİFEST zincirinde seri≠paralel künye — pipeline determinizmi bozuk"


# ---------------- 4) TAM TUR yaşam döngüsü: paralel ingest sonrası baslat→kaydet→durum kırılmaz ----------------
def test_tam_tur_yasam_dongusu_paralel_ingest_sonrasi(tmp_path):
    _korpus_kur(tmp_path)
    _manifest_json(tmp_path)
    _ingest(tmp_path, isci=4)

    # tam tur hiç yapılmamış → --durum exit 3
    cp = _tam_tur(["--durum"], tmp_path)
    assert cp.returncode == 3

    # FİZİKSEL İŞLETİM PROTOKOLÜ: adım çalışma evrakı bırakmadan --kaydet TAMAM diyemez
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "00-manifest-ingest-kanit.md").write_text(
        "0. MANİFEST: oa_ingest.py --isci 4 ile koştu, mutabakat TUTUYOR.", encoding="utf-8")

    cp = _tam_tur(["--baslat", "--dosya", "Entegrasyon Testi"], tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr

    cp = _tam_tur(["--kaydet"], tmp_path)
    assert cp.returncode == 0, f"paralel ingest sonrası --kaydet başarısız:\n{cp.stdout}\n{cp.stderr}"

    cp = _tam_tur(["--durum"], tmp_path)
    assert cp.returncode == 0
    assert "yok" in cp.stdout.lower() or "güncel" in cp.stdout.lower()

    # ---- yeni evrak ekle, tekrar PARALEL ingest, DELTA yakalanmalı (tam tur tekrar YOK) ----
    (tmp_path / "005-yeni-belge.txt").write_text("sonradan eklenen evrak " * 5, encoding="utf-8")
    _ingest(tmp_path, isci=4)   # künyeyi güncel evrakla tazele (paralel)

    cp = _tam_tur(["--delta"], tmp_path)
    assert cp.returncode == 3, "yeni evrak eklendi ama delta YAKALANMADI (paralel ingest sonrası körlük)"
    assert "005-yeni-belge.txt" in cp.stdout
    assert "ARTIMLI MOD" in cp.stdout
    assert "tam tur" in cp.stdout.lower() and "TEKRAR YAPILMAZ" in cp.stdout

    cp = _tam_tur(["--ekle", "005-yeni-belge.txt paralel ingest ile işlendi"], tmp_path)
    assert cp.returncode == 0

    cp = _tam_tur(["--kaydet"], tmp_path)
    assert cp.returncode == 0, f"delta sonrası --kaydet başarısız:\n{cp.stdout}\n{cp.stderr}"

    cp = _tam_tur(["--durum"], tmp_path)
    assert cp.returncode == 0
    assert "bekliyor" not in cp.stdout.lower()
