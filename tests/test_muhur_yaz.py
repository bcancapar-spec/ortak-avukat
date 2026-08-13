# -*- coding: utf-8 -*-
"""muhur_yaz.py (v0.5.8 P1 — PROV-O hizalı provenance mührü) testleri."""
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
          / "scripts" / "muhur_yaz.py")


def _kok_kur():
    kok = pathlib.Path(tempfile.mkdtemp())
    (kok / "_oa" / "teslim").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    urun = kok / "_oa" / "teslim" / "dilekce.udf"
    urun.write_bytes(b"PK\x03\x04 sahte-udf-icerik")
    girdi = kok / "_oa" / "cikti" / "08-dilekce.md"
    girdi.write_text("# taslak", encoding="utf-8")
    return kok, urun, girdi


def _cli(*arglar):
    p = subprocess.run([sys.executable, str(SCRIPT), *arglar],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def test_muhur_semasi_tam_ve_defter_append():
    kok, urun, girdi = _kok_kur()
    kod, out = _cli("--kok", str(kok), "--urun", str(urun),
                    "--tip", "dilekce_udf", "--kimlik", "dilekce:test:v1",
                    "--girdi", str(girdi), "--llm", "YOK — test")
    assert kod == 0 and "✓ mühür" in out
    kayit = json.loads((urun.parent / "dilekce.udf.prov.json").read_text(encoding="utf-8"))
    for alan in ("prov_schema", "entity_id", "entity_type", "artifact_file",
                 "artifact_sha256", "generated_at_time", "was_generated_by",
                 "used", "was_derived_from", "llm_kullanimi"):
        assert alan in kayit, alan
    assert kayit["prov_schema"] == "oa-muhur/1.0"
    assert len(kayit["artifact_sha256"]) == 64
    assert kayit["used"][0]["file"].endswith("08-dilekce.md")
    # defter append-only satır
    defter = (kok / "_oa" / "provenance.jsonl").read_text(encoding="utf-8")
    assert json.loads(defter.strip().splitlines()[-1])["entity_id"] == "dilekce:test:v1"


def test_dogrula_uyumlu_ve_bozulma_yakalanir():
    kok, urun, girdi = _kok_kur()
    _cli("--kok", str(kok), "--urun", str(urun), "--girdi", str(girdi))
    kod, out = _cli("--kok", str(kok), "--dogrula", str(urun))
    assert kod == 0 and "uyumlu" in out
    urun.write_bytes(b"PK\x03\x04 SONRADAN-DEGISTI")  # mühürden sonra oynama
    kod, out = _cli("--kok", str(kok), "--dogrula", str(urun))
    assert kod == 1 and "UYUŞMAZLIĞI" in out and "YÜKLEME" in out


def test_muhursuz_dogrulama_exit1():
    kok, urun, _ = _kok_kur()
    kod, out = _cli("--kok", str(kok), "--dogrula", str(urun))
    assert kod == 1 and "mühür yok" in out
