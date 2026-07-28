# -*- coding: utf-8 -*-
"""M1 (Paket D, v0.5.5) — PAS PROTOKOLÜ regresyon testleri.

Kapsam: `oa_hafiza.py ajan-brif` (1) `tam_tur.py --tez` ile kaydedilmiş güncel
DAVA TEZİni brifin EN BAŞINDA gösterir; (2) `pipeline_kayit.py --isle ...
--pas-yolu <dosya>` ile deftere işlenmiş EN SON pasın TAM içeriğini (kayıpsız)
1. sırada enjekte eder; (3) KURALLAR bloğunda pasın kendi çıktısının TEZ
satırıyla başlaması gerektiğini hatırlatır.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OA_HAFIZA = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"
TAM_TUR = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"
PIPELINE_KAYIT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _run(script, args, cwd):
    cp = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _brif(tmp_path):
    _run(OA_HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    kod, cikti = _run(
        OA_HAFIZA,
        ["ajan-brif", "--parca", "oa-vakia", "--gorev", "kronoloji çıkar", "--kok", str(tmp_path)],
        tmp_path,
    )
    assert kod == 0, cikti
    return cikti


def test_tez_belirlenmemisken_brif_bunu_soyler(tmp_path):
    cikti = _brif(tmp_path)
    assert "TEZ" in cikti
    assert "henüz belirlenmedi" in cikti


def test_tez_belirlenmisse_brif_ilk_satirlarda_gosterir(tmp_path):
    kod, _c = _run(TAM_TUR, ["--baslat", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    kod, _c = _run(TAM_TUR, ["--tez", "Davalı temerrüde düşürülmüştür.", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0

    cikti = _brif(tmp_path)
    assert "Davalı temerrüde düşürülmüştür." in cikti
    # TEZ satırı brifin ÇOK erken bir yerinde (ilk 500 karakter) yer alır.
    assert "Davalı temerrüde düşürülmüştür." in cikti[:600]


def test_onceki_pas_tam_icerikle_enjekte_edilir(tmp_path):
    _run(OA_HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    kod, _c = _run(PIPELINE_KAYIT, ["--baslat", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0

    # P0-6 önkoşulu (İNGEST-ÖNCE): 00-kunye.json diskte olmalı.
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                          encoding="utf-8")

    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    pas_icerik = "TEZ: Davalı temerrüde düşürülmüştür.\n\nAraştırma bulgusu: " + ("X" * 500)
    (cikti_dizin / "03-arastirma-oa-ictihat.md").write_text(pas_icerik, encoding="utf-8")

    kanit = "Skill fiilen çağrıldı; araştırma tam metni üretildi (>=20 karakter)."
    kod, _c = _run(
        PIPELINE_KAYIT,
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", kanit, "--pas-yolu", "_oa/cikti/03-arastirma-oa-ictihat.md",
         "--kok", str(tmp_path)],
        tmp_path,
    )
    assert kod == 0, _c

    cikti = _brif(tmp_path)
    assert "ÖNCEKİ PAS" in cikti
    assert "03-arastirma-oa-ictihat.md" in cikti
    assert pas_icerik in cikti, "önceki pas TAM (kayıpsız) gömülmedi"


def test_kurallar_blogu_pas_protokolunu_hatirlatir(tmp_path):
    cikti = _brif(tmp_path)
    assert "PAS PROTOKOLÜ" in cikti
    assert "--pas-yolu" in cikti
