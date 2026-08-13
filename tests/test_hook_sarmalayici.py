# -*- coding: utf-8 -*-
"""run-hook.cmd sarmalayıcısı (v0.5.8.2 — 447 yapısal-arıza dersi) testleri.

KÖK NEDEN: masaüstü uygulaması hook komutunu KABUKSUZ çalıştırınca
`python X || py -3 X` zincirindeki `||` python'a argüman gitti → üç sahada
sıfır ateşleme. Çözüm: fallback sarmalayıcı İÇİNDE; hooks.json tek komut.
Bu testler sarmalayıcının her iki yürütücüde (bash + cmd) enjeksiyonu
gerçekten bastığını kilitler.
"""
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
WRAP = (REPO / "plugins" / "ortak-avukat" / "hooks" / "run-hook.cmd")


def _dava_klasoru():
    t = pathlib.Path(tempfile.mkdtemp())
    for i in ("001", "002", "003"):
        (t / f"{i}_evrak.pdf").write_bytes(b"x")
    return t


def _bash(kok, mod="hook-prompt"):
    p = subprocess.run(["bash", str(WRAP), mod], cwd=str(kok),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, p.stdout or ""


def test_bash_yolu_enjeksiyon_basar():
    kod, out = _bash(_dava_klasoru())
    assert kod == 0
    assert "hookSpecificOutput" in out and "DEVİR YÜKÜMLÜLÜĞÜ" in out
    assert "TESLİM DİSİPLİNİ" in out          # v0.5.8.1 beşlisi taşınıyor


def test_dava_disi_klasorde_sessiz():
    bos = pathlib.Path(tempfile.mkdtemp())
    kod, out = _bash(bos)
    assert kod == 0 and out.strip() == ""      # sessiz — asla gürültü/blok yok


def test_cmd_yolu_windows():
    if sys.platform != "win32":
        return                                  # cmd yalnız Windows'ta
    kok = _dava_klasoru()
    p = subprocess.run(["cmd", "/c", str(WRAP), "hook-prompt"], cwd=str(kok),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert p.returncode == 0 and "DEVİR YÜKÜMLÜLÜĞÜ" in (p.stdout or "")


def test_hooks_json_tek_komut_zincirsiz():
    """Regresyon kilidi: hooks.json'a bir daha || zinciri girmesin."""
    t = (REPO / "plugins" / "ortak-avukat" / "hooks" / "hooks.json").read_text(encoding="utf-8")
    assert "||" not in t
    assert "run-hook.cmd" in t and t.count("${CLAUDE_PLUGIN_ROOT}") == 4
