# -*- coding: utf-8 -*-
"""P1-9 KUCUK-DÜZELTME (sinav bulgusu, düzeltme turu Paket C) — kısmi
(--onbakis) ingest gerçeği, İNGEST-ÖNCE kapısı --serh ile geçildiğinde
MODELİN kendi şerh metnine bağlı kalmadan üç mekanik yüzeyde DETERMİNİSTİK
olarak görünür kalmalı:
  (a) pipeline_kayit.py olayının serh_metni'ne "KISMI INGEST: N/M" ön eki,
  (b) teslim_paketi.py'nin teslim-makbuz(.RED).json'ında kismi_ingest:{n,m},
  (c) tam_tur.py'nin dosya-analiz.md başlığında "ÖN-BAKIŞ — DOSYA TAM
      OKUNMADI (N/M)" satırı.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OA_INGEST = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"
PK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
TAM_TUR = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"

UZUN_SERH = "Bilinçli olarak elden devam ediliyor, gerekçe >=30 karakter burada."


def _run(script, args, cwd):
    cp = subprocess.run([sys.executable, str(script)] + args, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, cp.stdout + cp.stderr


def _kismi_kok_kur(tmp_path, n=2, toplam=5):
    for i in range(1, toplam + 1):
        (tmp_path / f"{i:03d}-evrak.txt").write_text(
            f"Evrak {i} içeriği — yeterince uzun metin örneği burada tekrar eder. " * 2,
            encoding="utf-8")
    kod, cikti = _run(OA_INGEST, ["--ocr", "kapali", "--onbakis", str(n)], tmp_path)
    assert kod == 4, cikti
    assert (tmp_path / "_oa" / "metin-onbakis" / "00-kunye.onbakis.json").is_file()


def test_serh_metnine_kismi_ingest_onegi_eklenir(tmp_path):
    _kismi_kok_kur(tmp_path, n=2, toplam=5)
    kod, _ = _run(PK, ["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0
    kod, cikti = _run(PK, ["--isle", "--adim", "1", "--parca", "oa-interview",
                           "--durum", "UYGULANDI", "--kanit", "script çağrısı yapıldı >=20",
                           "--serh", UZUN_SERH, "--kok", "."], tmp_path)
    assert kod == 0, cikti
    assert "KISMI INGEST: 2/5" in cikti, cikti

    # --denetle "⚠ ŞERHLİ UYGULANDI" satırında serh_metni'nin TAMAMINI basar
    # (--goster yalnız kısa bir işaretçi basar, tam metni değil).
    _kod, cikti = _run(PK, ["--denetle", "--kok", "."], tmp_path)
    assert "KISMI INGEST: 2/5" in cikti


def test_kismi_ingest_yokken_onek_eklenmez(tmp_path):
    kod, _ = _run(PK, ["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0
    kod, cikti = _run(PK, ["--isle", "--adim", "1", "--parca", "oa-interview",
                           "--durum", "UYGULANDI", "--kanit", "script çağrısı yapıldı >=20",
                           "--serh", UZUN_SERH, "--kok", "."], tmp_path)
    assert kod == 0, cikti
    assert "KISMI INGEST" not in cikti


def test_teslim_makbuzunda_kismi_ingest_alani(tmp_path):
    _kismi_kok_kur(tmp_path, n=1, toplam=3)
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Basit bir taslak metni.", encoding="utf-8")

    teslim = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
              / "teslim_paketi.py")
    kod, cikti = _run(teslim, [str(taslak), "--kok", "."], tmp_path)
    # dilekce_denetim vb. kapılar kapanacaktır (taslak eksik) — asıl ilgimiz makbuzun
    # KENDİSİ RED de olsa kismi_ingest alanını taşıması.
    assert kod != 0 or kod == 0  # yalnız makbuz üretilmiş olsun, exit kodu bu testin konusu değil
    defter = tmp_path / "_oa" / "defter"
    aday = list(defter.glob("teslim-makbuz*.json"))
    assert aday, "hiçbir teslim makbuzu üretilmedi (RED dahi olsa üretilmeliydi)"
    makbuz = json.loads(aday[0].read_text(encoding="utf-8"))
    assert "kismi_ingest" in makbuz
    assert makbuz["kismi_ingest"] == {"n": 1, "m": 3}


def test_dosya_analiz_md_basliginda_onbakis_damgasi(tmp_path):
    _kismi_kok_kur(tmp_path, n=2, toplam=4)
    kod, cikti = _run(TAM_TUR, ["--baslat", "--dosya", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0, cikti
    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    assert analiz_md.is_file()
    icerik = analiz_md.read_text(encoding="utf-8")
    assert "ÖN-BAKIŞ — DOSYA TAM OKUNMADI (2/4)" in icerik


def test_dosya_analiz_md_tam_ingest_sonrasi_damgasiz(tmp_path):
    for i in range(1, 3):
        (tmp_path / f"{i:03d}-evrak.txt").write_text("İçerik " * 5, encoding="utf-8")
    kod, cikti = _run(OA_INGEST, ["--ocr", "kapali", "--isci", "1"], tmp_path)
    assert kod == 0, cikti
    kod, cikti = _run(TAM_TUR, ["--baslat", "--dosya", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert "ÖN-BAKIŞ" not in icerik
