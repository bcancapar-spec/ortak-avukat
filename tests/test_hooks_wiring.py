# -*- coding: utf-8 -*-
"""P0-7 (v0.5.5) sinav-turu KUCUK-düzeltme — hooks.json/plugin.json kablolaması
tek testsiz artefakttı: dosyalardan biri silinse/bozulsa 426 testin hiçbiri
kırılmazdı (P0-7 sessizce ölürdü). Bu dosya ucuz, statik doğrulamalar ekler.
"""
import importlib.util
import json
import pathlib
import shutil

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO / "plugins" / "ortak-avukat"
HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO / ".claude-plugin" / "marketplace.json"
PIPELINE_KAYIT = (PLUGIN_ROOT / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py")
TESLIM_PAKETI = (PLUGIN_ROOT / "skills" / "oa-kontrol" / "scripts" / "teslim_paketi.py")


def _pipeline_kayit_modulu():
    spec = importlib.util.spec_from_file_location("pk_hooks_wiring_test", PIPELINE_KAYIT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _teslim_paketi_modulu():
    spec = importlib.util.spec_from_file_location("tp_hooks_wiring_test", TESLIM_PAKETI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_hooks_json_var_ve_gecerli_json():
    assert HOOKS_JSON.is_file(), f"hooks.json bulunamadı: {HOOKS_JSON}"
    with open(HOOKS_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    assert isinstance(veri, dict) and "hooks" in veri


def test_hooks_json_stop_ve_sessionend_hook_denetle_cagirir():
    """v0.5.8.2 sözleşme (447 yapısal-arıza onarımı): komut artık
    `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" hook-denetle` — çift tire
    sarmalayıcının İÇİNDE eklenir; pipeline_kayit.py adı komutta GEÇMEZ."""
    with open(HOOKS_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    hooks = veri.get("hooks", {})
    for olay in ("Stop", "SessionEnd"):
        assert olay in hooks, f"hooks.json'da '{olay}' girdisi yok"
        komutlar = json.dumps(hooks[olay], ensure_ascii=False)
        assert "hook-denetle" in komutlar, f"'{olay}' hook'u hook-denetle çağırmıyor"
        assert "run-hook.cmd" in komutlar


def test_hooks_json_posttooluse_hook_postwrite_cagirir():
    """GÖREV B (P0-B, v0.5.5) — üretim-anı tetiğin ikinci ayağı: Write/Edit
    sonrası --hook-postwrite tetiklenmeli (yalnız Stop/SessionEnd'e kadar
    beklemek yerine)."""
    with open(HOOKS_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    hooks = veri.get("hooks", {})
    assert "PostToolUse" in hooks, "hooks.json'da 'PostToolUse' girdisi yok"
    girdiler = hooks["PostToolUse"]
    assert any("Write" in (g.get("matcher") or "") and "Edit" in (g.get("matcher") or "")
               for g in girdiler), "PostToolUse matcher'ı Write|Edit'i kapsamıyor"
    komutlar = json.dumps(girdiler, ensure_ascii=False)
    # v0.5.8.2 sözleşme: sarmalayıcı çağrısı (çift tire sarmalayıcının içinde).
    assert "hook-postwrite" in komutlar
    assert "run-hook.cmd" in komutlar


def test_hook_postwrite_bayragi_pipeline_kayit_scriptinde_tanimli():
    assert PIPELINE_KAYIT.is_file()
    metin = PIPELINE_KAYIT.read_text(encoding="utf-8")
    assert "--hook-postwrite" in metin
    assert "def hook_postwrite(" in metin


def test_plugin_json_var_ve_gecerli_json():
    assert PLUGIN_JSON.is_file(), f"plugin.json bulunamadı: {PLUGIN_JSON}"
    with open(PLUGIN_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    assert isinstance(veri, dict)
    assert veri.get("hooks") == "./hooks/hooks.json"


def test_plugin_json_hooks_alani_diskte_cozulebilir():
    """plugin.json'daki './hooks/hooks.json' göreli yolu FİİLEN diskte var mı?
    (Claude Code kuralı: plugin.json'daki göreli yollar `.claude-plugin/`ın
    BİR ÜST klasörüne — plugin paket köküne — göre çözülür, plugin.json'ın
    KENDİ bulunduğu `.claude-plugin/` klasörüne göre DEĞİL.)"""
    with open(PLUGIN_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    goreli = veri["hooks"]
    hedef = (PLUGIN_ROOT / goreli).resolve()
    assert hedef.is_file(), f"plugin.json'ın işaret ettiği hooks dosyası yok: {hedef}"
    assert hedef == HOOKS_JSON.resolve()


def test_hook_denetle_bayragi_pipeline_kayit_scriptinde_tanimli():
    assert PIPELINE_KAYIT.is_file()
    metin = PIPELINE_KAYIT.read_text(encoding="utf-8")
    assert "--hook-denetle" in metin
    assert "def hook_denetle(" in metin


def test_hooks_json_sarmalayici_sozlesmesi_v0582():
    """v0.5.8.2 SÖZLEŞME (447 yapısal-arıza onarımı — eski `||` zinciri
    testinin yerine): masaüstü uygulaması hook komutunu KABUKSUZ
    çalıştırabiliyor; `python X || py -3 X` zincirindeki `||` kabuk operatörü
    olarak değil python'a ARGÜMAN olarak gidiyordu → sessiz ölüm (üç sahada
    sıfır ateşleme). Fallback mantığı artık sarmalayıcının (run-hook.cmd)
    İÇİNDEDİR; hooks.json'daki HER komut tek tırnaklı TEK sarmalayıcı çağrısı
    olmalıdır: `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" <mod>` — `||`
    YASAK, çift tire pipeline_kayit'e sarmalayıcının İÇİNDE eklenir."""
    import sys as _sys
    with open(HOOKS_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    for olay, girdiler in veri["hooks"].items():
        for girdi in girdiler:
            for h in girdi.get("hooks", []):
                komut = h.get("command", "")
                assert "||" not in komut, (
                    f"'{olay}' komutunda || zinciri var — v0.5.8.2 yasağı: {komut}")
                parcalar = komut.split()
                assert len(parcalar) == 2, f"tek sarmalayıcı + tek mod olmalı: {komut}"
                assert parcalar[0].strip('"').endswith("hooks/run-hook.cmd"), komut
                assert parcalar[0].startswith('"'), (
                    "sarmalayıcı yolu tırnaklı olmalı (boşluklu kurulum yolları)")
                assert parcalar[1].startswith("hook-"), (
                    f"mod 'hook-*' biçiminde olmalı (çift tiresiz): {parcalar[1]}")
    # Sarmalayıcı diskte var VE bu makinede en az bir python launcher'ı
    # fiilen çalıştırılabilir (sarmalayıcının fallback zinciri boşa düşmesin).
    assert (PLUGIN_ROOT / "hooks" / "run-hook.cmd").is_file()
    launcherlar = ("python", "py", "python3")
    calisan_var = any(
        shutil.which(tok) or pathlib.Path(_sys.executable).stem.lower() == tok
        for tok in launcherlar)
    assert calisan_var, (
        f"sarmalayıcı zincirindeki HİÇBİR launcher ({launcherlar}) bu makinede "
        "çalıştırılabilir görünmüyor")


def test_plugin_json_surumu_pipeline_kayit_surumu_ile_ESZAMANLI():
    """Paket-B sinav-turu KUCUK-düzeltme: `plugin.json`'ın üst düzey `version`
    alanı ile `pipeline_kayit.OA_SURUM` (makbuz/defter geçiş supabının
    dayandığı damga) SESSİZCE AYRIŞABİLİYORDU — paket dışarıdan eski bir
    sürüm gösterirken içeride yeni sürüm davranışı zorunlu kılınabiliyordu.
    Bu invaryant iki damganın bir daha ayrışmasını testle kilitler."""
    with open(PLUGIN_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    pk = _pipeline_kayit_modulu()
    assert veri.get("version") == pk.OA_SURUM, (
        f"plugin.json version ({veri.get('version')!r}) != "
        f"pipeline_kayit.OA_SURUM ({pk.OA_SURUM!r}) — iki damga ayrıştı.")


def test_dort_surum_damgasi_TAMAMI_ESZAMANLI():
    """DÜZELTME (v0.5.5 şerh turu — Ş11 KUCUK): önceki invaryant YALNIZ
    plugin.json ↔ pipeline_kayit.OA_SURUM çiftini kilitliyordu.
    `teslim_paketi.OA_SURUM` (makbuza yazılan damga) ve
    `.claude-plugin/marketplace.json`'daki ortak-avukat girdisinin `version`
    alanı KİLİTSİZDİ — testin önlemek için yazıldığı sınıf (paket dışarıdan
    eski sürüm gösterirken içeride farklı sürüm davranışı) bu iki damga için
    aynen tekrarlanabilirdi. Dört damganın TÜMÜ tek assert'te eşitlenir."""
    with open(PLUGIN_JSON, encoding="utf-8") as f:
        plugin_veri = json.load(f)
    with open(MARKETPLACE_JSON, encoding="utf-8") as f:
        pazar_veri = json.load(f)
    pazar_girdisi = next(
        (p for p in pazar_veri.get("plugins", []) if p.get("name") == "ortak-avukat"), None)
    assert pazar_girdisi is not None, "marketplace.json'da 'ortak-avukat' girdisi yok"

    pk = _pipeline_kayit_modulu()
    tp = _teslim_paketi_modulu()

    damgalar = {
        "plugin.json version": plugin_veri.get("version"),
        "marketplace.json ortak-avukat.version": pazar_girdisi.get("version"),
        "pipeline_kayit.OA_SURUM": pk.OA_SURUM,
        "teslim_paketi.OA_SURUM": tp.OA_SURUM,
    }
    tekil = set(damgalar.values())
    assert len(tekil) == 1, f"Sürüm damgaları AYRIŞTI: {damgalar}"
