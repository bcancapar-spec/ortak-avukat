# -*- coding: utf-8 -*-
"""KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 3) — `_hook_kok_adaylarini_
bul`'un GERÇEK dağıtım senaryosunda kör kalmasının giderimi.

Saha bulgusu: hooks.json --kok VERMEZ (argparse varsayılanı '.'); dava
klasörü oturum CWD'sinin DIŞINDAYSA (gerçek dağıtım — CWD=eklenti deposu,
dosya=başka bir sürücü/klasördeki dava kökü) ne stdin `cwd` alanı ne
`CLAUDE_PROJECT_DIR` ne de süreç CWD'si dava köküne değer; hook sessizce
hiçbir şey yapmadan exit 0 döner ve `_oa/DURUM.md` hiç doğmaz.

Düzeltme: PostToolUse payload'ındaki `tool_input.file_path` (YENİ YAZILAN
dosyanın kendi yolu) üzerinden yukarı yürüyerek `_oa/defter` içeren ilk ata
dizin bulunur ve aday listesine eklenir.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _load():
    spec = importlib.util.spec_from_file_location("pipeline_kayit_kok_kesif", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _load()


def _cli(args, cwd, stdin_payload=None):
    girdi = json.dumps(stdin_payload) if stdin_payload is not None else None
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd), input=girdi,
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ── _defter_koku_yukari_ara() — birim testleri ─────────────────────────────

def test_ata_dizinde_defter_varsa_bulunur(tmp_path):
    dava = tmp_path / "dava"
    (dava / "_oa" / "defter").mkdir(parents=True)
    nested_dosya = dava / "_oa" / "cikti" / "08-taslak.md"
    nested_dosya.parent.mkdir(parents=True, exist_ok=True)
    nested_dosya.write_text("x", encoding="utf-8")
    bulunan = pk._defter_koku_yukari_ara(str(nested_dosya))
    assert bulunan == str(dava.resolve())


def test_hicbir_atada_defter_yoksa_none(tmp_path):
    dosya = tmp_path / "a" / "b" / "c.md"
    dosya.parent.mkdir(parents=True, exist_ok=True)
    dosya.write_text("x", encoding="utf-8")
    assert pk._defter_koku_yukari_ara(str(dosya)) is None


def test_henuz_var_olmayan_dosya_yolu_da_calisir(tmp_path):
    """`tool_input.file_path` PostToolUse payload'ında bazen henüz flush
    edilmemiş bir yol olabilir — fonksiyon dosyanın VAR OLMASINI şart
    koşmamalı, yalnız üst dizinleri yürür."""
    dava = tmp_path / "dava"
    (dava / "_oa" / "defter").mkdir(parents=True)
    henuz_yok = dava / "_oa" / "cikti" / "yeni-dosya.md"
    bulunan = pk._defter_koku_yukari_ara(str(henuz_yok))
    assert bulunan == str(dava.resolve())


def test_asla_istisna_firlatmaz():
    assert pk._defter_koku_yukari_ara("") is None or isinstance(
        pk._defter_koku_yukari_ara(""), str)
    assert pk._defter_koku_yukari_ara(None) is None


# ── Uçtan uca — gerçek saha senaryosunun birebir simülasyonu ───────────────

def test_hook_postwrite_tool_input_file_path_ile_dava_kokunu_kesfeder(tmp_path):
    """Süreç CWD'si ('baska-yer') dava kökünün DIŞINDA; stdin `cwd` alanı da
    'baska-yer'i gösteriyor (gerçek dağıtımda olduğu gibi); `--kok` hiç
    VERİLMİYOR (argparse varsayılanı '.'). Yalnız stdin payload'ındaki
    `tool_input.file_path` (dava kökündeki YENİ dosyanın yolu) dava kökünü
    keşfetmeye yeter."""
    dava = tmp_path / "dava"
    baska_yer = tmp_path / "baska-yer"
    baska_yer.mkdir(parents=True, exist_ok=True)

    kod0, cikti0 = _cli(["--baslat", "Test Dosyası", "--kok", str(dava)], cwd=tmp_path)
    assert kod0 == 0, cikti0
    assert (dava / "_oa" / "defter").is_dir()

    dilekce_yolu = dava / "_oa" / "cikti" / "08-dilekce-taslak.md"
    dilekce_yolu.parent.mkdir(parents=True, exist_ok=True)
    dilekce_yolu.write_text(
        "DAVACI: Ali Veli\nDAVALI: XYZ A.Ş.\nSONUÇ VE İSTEM: ...\n", encoding="utf-8")

    durum_md = dava / "_oa" / "DURUM.md"
    onceki = durum_md.read_text(encoding="utf-8") if durum_md.is_file() else ""

    payload = {"cwd": str(baska_yer), "tool_input": {"file_path": str(dilekce_yolu)}}
    kod, cikti = _cli(["--hook-postwrite"], cwd=baska_yer, stdin_payload=payload)

    assert kod == 0, f"hook ASLA bloklamamalı:\n{cikti}"
    assert "OTOMATİK DENETİM" in cikti, (
        f"tool_input.file_path üzerinden dava kökü keşfedilmeliydi:\n{cikti}")
    assert "makbuzsuz dilekçe adayı" in cikti
    assert str(dava.resolve()) in cikti or "kök:" in cikti

    guncel = durum_md.read_text(encoding="utf-8")
    assert guncel != onceki, "dava kökündeki DURUM.md tazelenmeliydi"


def test_eski_payload_bicimi_tool_input_olmadan_davranis_ayni_kalir(tmp_path):
    """Kontrast/regresyon: `tool_input` alanı hiç YOKSA (eski payload biçimi)
    davranış AYNEN eskisi gibi kalır — yeni aday sessizce hiçbir şey
    eklemez."""
    dava = tmp_path / "dava"
    kod0, _c = _cli(["--baslat", "Test Dosyası", "--kok", str(dava)], cwd=tmp_path)
    assert kod0 == 0

    payload = {"cwd": str(dava)}
    kod, cikti = _cli(["--hook-denetle"], cwd=dava, stdin_payload=payload)
    assert kod == 0
    assert "OTOMATİK DENETİM" in cikti
