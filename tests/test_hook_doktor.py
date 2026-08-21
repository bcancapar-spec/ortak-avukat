# -*- coding: utf-8 -*-
"""tools/hook_doktor.py testleri (v0.5.9 — T1 sahte-arıza onarımı + T2 dinamik envanter).

KANIT (onarım öncesi, bu ağaçta koşulup görüldü): hook_doktor sarmalayıcı
yolunu düşürüyordu — `argv = [sys.executable] + parcalar[1:]` fiilen
`python hook-prompt` koşuyor, python "hook-prompt" diye dosya arıyor,
exit 2 → 4 olayda "bloklamama sözleşmesi İHLAL" + SONUÇ: ARIZA VAR.
Oysa katman SAĞLAM (test_hook_sarmalayici yeşil). Bu SAHTE ARIZADIR:
teşhis aracının kendisi hasta.

Bu testler kilitler:
- [T2] Sabit OLAYLAR listesi yok; olaylar hooks.json'dan DİNAMİK okunur
  (yarın 7. olay eklense kod değişmez).
- [T1] run-hook.cmd sarmalayıcısı DÜŞÜRÜLMEZ: komut bash ile TAM olarak
  koşulur (git-bash açık yoldan — WSL stub tuzağına düşülmez), stdin'e
  boş JSON verilir.
- Uçtan uca: GERÇEK repo hooks.json'ıyla tüm olaylar exit 0 → SONUÇ yeşil.
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
DOKTOR = REPO / "tools" / "hook_doktor.py"
HOOKS_JSON = REPO / "plugins" / "ortak-avukat" / "hooks" / "hooks.json"
PLUGIN_KOK = REPO / "plugins" / "ortak-avukat"


def _modul():
    spec = importlib.util.spec_from_file_location("hook_doktor_test", DOKTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gercek_bash():
    """test_hook_sarmalayici._gercek_bash deseni: PATH'teki bash Windows'ta
    WSL stub'ına (System32) çözülüp patlayabilir; Git Bash'i açık yoldan ara."""
    for aday in (r"C:\Program Files\Git\bin\bash.exe",
                 r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if pathlib.Path(aday).is_file():
            return aday
    b = shutil.which("bash")
    if b and "system32" not in b.lower():
        return b
    return None


def _dava_klasoru():
    t = pathlib.Path(tempfile.mkdtemp(prefix="oa-hd-test-"))
    for i in ("001", "002", "003"):
        (t / f"{i}_sentetik_evrak.pdf").write_bytes(b"x")
    return t


# ── T2: DİNAMİK ENVANTER ────────────────────────────────────────────────────

def test_sabit_olay_listesi_silindi():
    """Sabit `OLAYLAR = [...]` listesi kaynak koddan SİLİNMİŞ olmalı —
    envanter hooks.json'dan okunur, kod sabitinden değil."""
    kaynak = DOKTOR.read_text(encoding="utf-8")
    assert "OLAYLAR = [" not in kaynak, (
        "hook_doktor.py hâlâ sabit OLAYLAR listesi taşıyor — dinamik envanter (T2) yok")


def test_hooks_olaylari_gercek_hooks_json_ile_esit():
    """hook_doktor.hooks_olaylari() GERÇEK repo hooks.json'ındaki olay
    kümesiyle birebir eşit olmalı (bugün 6 olay)."""
    mod = _modul()
    beklenen = set(json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"].keys())
    assert set(mod.hooks_olaylari(HOOKS_JSON)) == beklenen
    # varsayılan çağrı da repo hooks.json'ını bulmalı
    assert set(mod.hooks_olaylari()) == beklenen


def test_hooks_olaylari_yeni_olay_kod_degisikliksiz_gorunur():
    """Yarın 7. olay eklense kod değişmez: sentetik hooks.json'a bilinmeyen
    bir olay eklenince hooks_olaylari() onu da döndürmeli."""
    mod = _modul()
    veri = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    veri["hooks"]["YepyeniOlay"] = [{"hooks": [{"type": "command", "command": "echo x"}]}]
    t = pathlib.Path(tempfile.mkdtemp(prefix="oa-hd-syn-")) / "hooks.json"
    t.write_text(json.dumps(veri), encoding="utf-8")
    olaylar = mod.hooks_olaylari(t)
    assert "YepyeniOlay" in olaylar and len(olaylar) == 7


# ── T1: SARMALAYICI YOLU DÜŞÜRÜLMEZ ─────────────────────────────────────────

def test_sarmalayici_komutu_dusurulmeden_kosulur():
    """_komut_calistir, run-hook.cmd sarmalayıcılı komutu TAM olarak (bash ile)
    koşmalı: hook-prompt sentetik dava klasöründe exit 0 + DEVİR enjeksiyonu.
    Onarım öncesi bu çağrı exit 2 basıyordu (python 'hook-prompt' dosyası arıyordu)."""
    if _gercek_bash() is None:
        pytest.skip("ortamda gerçek bash yok")
    mod = _modul()
    komut = "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" hook-prompt"
    kod, out = mod._komut_calistir(komut, PLUGIN_KOK, _dava_klasoru())
    assert kod == 0, f"sarmalayıcı komut exit {kod} — yol hâlâ düşürülüyor olabilir"
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in out


def test_sarmalayici_stdin_bos_json_alir():
    """hook-pretool payload'ı stdin'den okur; doktor stdin'e boş JSON {}
    vermeli ki gövde asılı kalmadan / çökmeden exit 0 dönsün."""
    if _gercek_bash() is None:
        pytest.skip("ortamda gerçek bash yok")
    mod = _modul()
    komut = "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" hook-pretool"
    kod, _out = mod._komut_calistir(komut, PLUGIN_KOK, _dava_klasoru())
    assert kod == 0


# ── UÇTAN UCA: GERÇEK repo hooks.json ile tüm olaylar YEŞİL ─────────────────

def test_uctan_uca_tum_olaylar_yesil():
    """Onarım sonrası hook_doktor GERÇEK repo üzerinde koşunca: her olay
    için sarmalayıcı komut + exit satırı basılır ve SONUÇ yeşildir.
    (Sentetik değil — repo hooks.json'ındaki 6 olayın tamamı fiilen koşulur.)"""
    if _gercek_bash() is None:
        pytest.skip("ortamda gerçek bash yok")
    cp = subprocess.run([sys.executable, str(DOKTOR)], cwd=str(REPO),
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=600)
    out = cp.stdout or ""
    assert cp.returncode == 0, f"hook_doktor ARIZA basıyor:\n{out}\n{cp.stderr}"
    assert "TÜM MEKANİK KONTROLLER GEÇTİ" in out
    olaylar = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"].keys()
    for olay in olaylar:
        assert olay in out, f"olay satırı yok: {olay}"
    # her olay satırında sarmalayıcı komut görünür (T2: komut + exit + sonuç)
    assert out.count("run-hook.cmd") >= len(olaylar)
