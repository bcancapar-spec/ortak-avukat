# -*- coding: utf-8 -*-
# __OA_UTF8_GUARD__
"""YENİ-1 (Paket D DÜZELTME) — M1 PAS PROTOKOLÜ `--pas-yolu` DİZİN SINIRI.

Çürütücü bulgu: `--pas-yolu` keyfi bir dosyayı (`../gizli/sirlar.txt`, mutlak
yol, sembolik bağ) işaret edebiliyordu; `pipeline_kayit.py --isle` bunu
deftere sessizce işliyor, `oa_hafiza.py ajan-brif` de dosyanın TAM içeriğini
(başka bir müvekkilin evrakı dahi olsa) alt-ajan brifine VERBATİM
enjekte ediyordu — dosya sınırı + gizlilik invaryantı ihlali.

Bu dosya İKİ savunma katmanını da test eder:
  (1) `pipeline_kayit.py --isle --pas-yolu <kapsam dışı>` → RET (exit != 0),
      olay deftere HİÇ YAZILMAZ.
  (2) `oa_hafiza.py ajan-brif` — defter DAHA ÖNCEden (bu düzeltmeden önce)
      kirlenmişse bile (doğrudan jsonl'e yazılan bir olay) gövdeyi OKUMAZ,
      görünür bir uyarı basar.
Ayrıca boyut tavanı (`PAS_AZAMI_BAYT`) regresyonu.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PIPELINE_KAYIT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
OA_HAFIZA = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"


def _load(script, ad):
    spec = importlib.util.spec_from_file_location(ad, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _load(PIPELINE_KAYIT, "pipeline_kayit_kapsam")


def _run(script, args, cwd):
    cp = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _p06_onkosul_fixture_kur(tmp_path):
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)


def _baslat(tmp_path):
    kod, cikti = _run(PIPELINE_KAYIT, ["--baslat", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, cikti
    _p06_onkosul_fixture_kur(tmp_path)


# ── (1) --isle --pas-yolu kapsam dışı → RET, defter kirlenmez ─────────────

@pytest.mark.parametrize("pas_yolu_uret", [
    lambda tmp_path: "../gizli-sirlar.txt",  # göreli `..` kaçışı
    lambda tmp_path: str(tmp_path.parent / "gizli-sirlar-mutlak.txt"),  # mutlak yol
    lambda tmp_path: str(tmp_path / "_oa" / "gizli-sirlar-yaninda.txt"),  # _oa altı ama cikti/ DIŞI
], ids=["goreli-kacis", "mutlak-yol-disi", "oa-alti-ama-cikti-disi"])
def test_pas_yolu_kapsam_disi_ret_edilir_defter_kirlenmez(tmp_path, pas_yolu_uret):
    _baslat(tmp_path)
    disardaki = pas_yolu_uret(tmp_path)
    # Kapsam dışı dosyanın GERÇEKTEN var olduğu senaryo (a) CANLI KANIT ile
    # birebir eşleşir — RET, dosyanın var/yok olmasından BAĞIMSIZ olmalı.
    disardaki_tam = disardaki if pathlib.Path(disardaki).is_absolute() else (tmp_path / disardaki)
    pathlib.Path(disardaki_tam).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(disardaki_tam).write_text(
        "TEZ: sahte\nGIZLI-SIR-ICERIK-12345 (dava kokunun DISINDA, baska muvekkilin evraki)",
        encoding="utf-8")

    kanit = "Skill fiilen çağrıldı; araştırma çıktısı üretildi (>=20 karakter)."
    kod, cikti = _run(
        PIPELINE_KAYIT,
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", kanit, "--pas-yolu", disardaki, "--kok", str(tmp_path)],
        tmp_path,
    )
    assert kod != 0, f"kapsam dışı --pas-yolu RET edilmeliydi:\n{cikti}"
    assert "RET" in cikti and "_oa/cikti" in cikti

    # Defter kirlenmedi: bu adım/parça için HİÇBİR olay yazılmamış olmalı.
    olaylar_yol = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    if olaylar_yol.is_file():
        for satir in olaylar_yol.read_text(encoding="utf-8").splitlines():
            olay = json.loads(satir)
            assert olay.get("pas_yolu") != disardaki, "kapsam dışı pas_yolu deftere YAZILMIŞ"


def test_pas_yolu_oa_cikti_icindeyse_kabul_edilir(tmp_path):
    """Kontrol grubu — YENİ-1 düzeltmesi meşru kullanımı BLOKLAMAMALI."""
    _baslat(tmp_path)
    (tmp_path / "_oa" / "cikti" / "03-arastirma.md").write_text(
        "TEZ: müvekkilin alacağı zamanaşımına uğramamıştır.\nGövde.", encoding="utf-8")
    kanit = "Skill fiilen çağrıldı; araştırma çıktısı üretildi (>=20 karakter)."
    kod, cikti = _run(
        PIPELINE_KAYIT,
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", kanit, "--pas-yolu", "_oa/cikti/03-arastirma.md", "--kok", str(tmp_path)],
        tmp_path,
    )
    assert kod == 0, cikti


# ── (2) savunma katmanı 2 — oa_hafiza.py ajan-brif, ÖNCEDEN kirlenmiş defter ─

def test_onceden_kirlenmis_defter_ajan_brife_govde_sizdirmaz(tmp_path):
    """Düzeltmeden ÖNCE yazılmış (veya CLI'yi atlayarak doğrudan jsonl'e
    eklenmiş) kapsam-dışı bir `pas_yolu` olayı varken, `ajan-brif` gövdeyi
    OKUMAMALI — ikinci savunma katmanı (`oa_hafiza._onceki_pas_govdesi`)."""
    _run(OA_HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    kod, _c = _run(PIPELINE_KAYIT, ["--baslat", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0

    gizli = tmp_path.parent / f"gizli-sirlar-{tmp_path.name}.txt"
    gizli.write_text(
        "GIZLI-SIR-ICERIK-12345 (dava kokunun DISINDA, baska muvekkilin evraki)",
        encoding="utf-8")
    try:
        olaylar_yol = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
        pk.olay_ekle(str(olaylar_yol), {
            "zaman": pk.simdi(), "tip": "adim", "adim": 3, "parca": "oa-ictihat",
            "durum": "UYGULANDI", "kanit": "kirli test olayı (>=20 karakter, CLI atlanarak)",
            "pas_yolu": str(gizli),
        })

        kod, cikti = _run(
            OA_HAFIZA,
            ["ajan-brif", "--parca", "oa-vakia", "--gorev", "kronoloji çıkar",
             "--kok", str(tmp_path)],
            tmp_path,
        )
        assert kod == 0, cikti
        assert "GIZLI-SIR-ICERIK-12345" not in cikti, (
            "kapsam dışı pas gövdesi ikinci savunma katmanına RAĞMEN brife sızdı")
        assert "DEVRALINMADI" in cikti or "GÜVENLİK" in cikti
    finally:
        gizli.unlink(missing_ok=True)


# ── (3) boyut tavanı — PAS_AZAMI_BAYT ───────────────────────────────────────

def test_pas_govdesi_azami_boyutu_asarsa_kirpilir(tmp_path):
    _run(OA_HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    kod, _c = _run(PIPELINE_KAYIT, ["--baslat", "Test Dosyası", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    _p06_onkosul_fixture_kur(tmp_path)

    azami = pk.PAS_AZAMI_BAYT
    dev_pas = tmp_path / "_oa" / "cikti" / "03-arastirma-dev.md"
    dev_pas.write_text("TEZ: dev pas testi.\n" + ("X" * (azami + 5000)), encoding="utf-8")

    kanit = "Skill fiilen çağrıldı; araştırma çıktısı üretildi (>=20 karakter)."
    kod, cikti = _run(
        PIPELINE_KAYIT,
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", kanit, "--pas-yolu", "_oa/cikti/03-arastirma-dev.md", "--kok", str(tmp_path)],
        tmp_path,
    )
    assert kod == 0, cikti

    kod, cikti = _run(
        OA_HAFIZA,
        ["ajan-brif", "--parca", "oa-vakia", "--gorev", "kronoloji çıkar",
         "--kok", str(tmp_path)],
        tmp_path,
    )
    assert kod == 0, cikti
    assert "kırpıldı" in cikti, "azami tavanı aşan pas gövdesi kırpılmadı"
    assert cikti.count("X") < (azami + 5000), "pas gövdesi TAM (kırpılmadan) enjekte edilmiş"
