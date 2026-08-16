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


def _gercek_bash():
    """PATH'teki `bash` Windows'ta WSL stub'ına (System32) çözülebilir ve WSL
    kurulu değilse patlar — 447 sonrası bu testin ilk sürümünün düştüğü tuzak.
    Git Bash'i açık yoldan ara; yoksa None (test o yürütücüyü atlar)."""
    for aday in (r"C:\Program Files\Git\bin\bash.exe",
                 r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if pathlib.Path(aday).is_file():
            return aday
    import shutil
    b = shutil.which("bash")
    if b and "system32" not in b.lower():
        return b
    return None


def _dava_klasoru():
    t = pathlib.Path(tempfile.mkdtemp())
    for i in ("001", "002", "003"):
        (t / f"{i}_evrak.pdf").write_bytes(b"x")
    return t


def _bash(kok, mod="hook-prompt"):
    b = _gercek_bash()
    if b is None:
        return None, None                      # bash yok — çağıran atlar
    p = subprocess.run([b, str(WRAP), mod], cwd=str(kok),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, p.stdout or ""


def test_bash_yolu_enjeksiyon_basar():
    kod, out = _bash(_dava_klasoru())
    if kod is None:
        return                                  # ortamda gerçek bash yok
    assert kod == 0
    assert "hookSpecificOutput" in out and "DEVİR YÜKÜMLÜLÜĞÜ" in out
    assert "TESLİM DİSİPLİNİ" in out          # v0.5.8.1 beşlisi taşınıyor


def test_dava_disi_klasorde_sessiz():
    kod, out = _bash(pathlib.Path(tempfile.mkdtemp()))
    if kod is None:
        return
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
    # v0.5.8.4: PreToolUse (hook-pretool, elle-UDF kapısı) eklendi → 5 komut.
    # v0.5.8.5: SessionStart (hook-acilis, C4 açılış envanteri) eklendi → 6 komut.
    assert "run-hook.cmd" in t and t.count("${CLAUDE_PLUGIN_ROOT}") == 6
