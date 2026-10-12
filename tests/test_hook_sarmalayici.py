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


def _calisir_yaz(yol, metin):
    """Sahte yorumlayıcı: Linux'ta çalıştırma izni olmadan `exec` "Permission denied"
    verir (CI matrisi ubuntu'yu da koşar); Windows'ta chmod zararsızdır."""
    import os
    yol.write_text(metin, encoding="utf-8")
    os.chmod(yol, 0o755)


def test_bash_yolu_python3u_onceki_dizindeki_pythondan_once_secer(tmp_path):
    """Bağımsız inceleme (2026-10-12): dizin başına arama, PATH'te önce gelen bir
    dizindeki `python`'u (eski dağıtımlarda Python 2) sonraki dizindeki `python3`'ten önce
    seçiyordu; eski sarmalayıcı python3'ü PATH genelinde önce arıyordu."""
    b = _gercek_bash()
    if b is None:
        return
    import os
    eski, yeni = tmp_path / "eskipy", tmp_path / "yenipy"
    eski.mkdir()
    yeni.mkdir()
    _calisir_yaz(eski / "python", "#!/bin/sh\necho 'eski python' >&2\nexit 3\n")
    _calisir_yaz(yeni / "python3", '#!/bin/sh\nexec "%s" "$@"\n' % pathlib.Path(sys.executable).as_posix())
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(eski), str(yeni), env.get("PATH", "")])
    p = subprocess.run([b, str(WRAP), "hook-prompt"], cwd=str(_dava_klasoru()), env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert p.returncode == 0, (p.returncode, p.stderr)
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in (p.stdout or ""), (p.stdout, p.stderr)


def _store_kisayollu_path(tmp):
    """v0.5.18 (2026-10-11, bu makinede ölçüldü): PATH'te Microsoft Store'un sahte
    `python`/`python3` kısayolu (WindowsApps; "Python was not found…", çıkış 49) gerçek
    yorumlayıcıdan ÖNCE geliyordu; sarmalayıcı onu koşturdu ve kanca katmanının altı
    olayı da sessizce öldü. Bu düzenek aynı sırayı kurar: önce sahte WindowsApps, sonra
    gerçek Python'a yönlenen kısayol."""
    import os
    stub = tmp / "WindowsApps"
    gercek = tmp / "gercekpy"
    stub.mkdir()
    gercek.mkdir()
    py = pathlib.Path(sys.executable)
    for ad in ("python3", "python"):
        _calisir_yaz(stub / ad, "#!/bin/sh\necho 'Python was not found; run without arguments "
                                "to install from the Microsoft Store' >&2\nexit 49\n")
        _calisir_yaz(gercek / ad, '#!/bin/sh\nexec "%s" "$@"\n' % py.as_posix())
    (stub / "python.cmd").write_text("@echo Python was not found 1>&2\r\n@exit /b 49\r\n", encoding="utf-8")
    (gercek / "python.cmd").write_text('@"%s" %%*\r\n' % py, encoding="utf-8")
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(stub), str(gercek), env.get("PATH", "")])
    return env


def test_bash_yolu_store_kisayolunu_atlar_gercek_pythonu_kosturur(tmp_path):
    b = _gercek_bash()
    if b is None:
        return
    env = _store_kisayollu_path(tmp_path)
    p = subprocess.run([b, str(WRAP), "hook-prompt"], cwd=str(_dava_klasoru()), env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert p.returncode == 0, (p.returncode, p.stderr)
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in (p.stdout or ""), (p.stdout, p.stderr)


def test_cmd_yolu_store_kisayolunu_atlar_gercek_pythonu_kosturur(tmp_path):
    if sys.platform != "win32":
        return
    env = _store_kisayollu_path(tmp_path)
    p = subprocess.run(["cmd", "/c", str(WRAP), "hook-prompt"], cwd=str(_dava_klasoru()), env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert p.returncode == 0 and "DEVİR YÜKÜMLÜLÜĞÜ" in (p.stdout or ""), (p.stdout, p.stderr)


def test_sarmalayici_saf_ascii_kalir():
    """v0.5.18 (2026-10-12, bu makinede ölçüldü): konsol kod sayfası UTF-8 (65001) iken
    cmd, LF satır sonlu batch dosyasındaki çok baytlı karakterin (REM satırındaki uzun
    tire) ofsetini yanlış sayıyor, satırın ortasından okumaya başlıyor ve REM yorumunun
    PARÇALARINI komut diye çalıştırıyordu. Depo dosyayı LF saklar (bash kolu CRLF'yi
    kaldıramaz); sistem genelinde UTF-8 kullanan Windows'ta kanca sessizce ölür. Saf
    ASCII dosyada ofset kayması olmaz."""
    veri = WRAP.read_bytes()
    disi = sorted({b for b in veri if b > 127})
    assert not disi, "run-hook.cmd ASCII dışı bayt taşıyor: %r" % disi


def test_cmd_yolu_utf8_kod_sayfasinda_da_calisir():
    if sys.platform != "win32":
        return
    # Kod sayfası konsola aittir ve paylaşılır: chcp kendi gizli konsolunda koşar
    # (CREATE_NO_WINDOW), paralel işçilerin konsolunu değiştirmez.
    p = subprocess.run(["cmd", "/c", "chcp 65001 >nul & " + str(WRAP) + " hook-prompt"],
                       cwd=str(_dava_klasoru()), capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode == 0 and "DEVİR YÜKÜMLÜLÜĞÜ" in (p.stdout or ""), (p.stdout, p.stderr)


def test_hooks_json_tek_komut_zincirsiz():
    """Regresyon kilidi: hooks.json'a bir daha || zinciri girmesin."""
    t = (REPO / "plugins" / "ortak-avukat" / "hooks" / "hooks.json").read_text(encoding="utf-8")
    assert "||" not in t
    # v0.5.8.4: PreToolUse (hook-pretool, elle-UDF kapısı) eklendi → 5 komut.
    # v0.5.8.5: SessionStart (hook-acilis, C4 açılış envanteri) eklendi → 6 komut.
    assert "run-hook.cmd" in t and t.count("${CLAUDE_PLUGIN_ROOT}") == 6
