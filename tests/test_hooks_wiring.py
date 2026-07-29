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
    with open(HOOKS_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    hooks = veri.get("hooks", {})
    for olay in ("Stop", "SessionEnd"):
        assert olay in hooks, f"hooks.json'da '{olay}' girdisi yok"
        komutlar = json.dumps(hooks[olay], ensure_ascii=False)
        assert "--hook-denetle" in komutlar, f"'{olay}' hook'u --hook-denetle çağırmıyor"
        assert "pipeline_kayit.py" in komutlar


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
    assert "--hook-postwrite" in komutlar
    assert "pipeline_kayit.py" in komutlar


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


def test_hooks_json_python_fallback_zinciri_calistirabilir_bir_yorumlayiciya_sahip():
    """DÜZELTME (v0.5.5 şerh turu — Ş12 KUCUK): `hooks.json` çıplak `python`
    çağırıyordu — Windows'ta `python` PATH'te olmayabilir (yalnız `py`
    launcher'ı, ya da Microsoft Store alias'ı Store'u açar) ve P0-7 fail-open
    tasarımı gereği bu durum HİÇBİR sinyal üretmeden hook'u kalıcı no-op
    yapardı. Komut artık `python || py -3 || python3` ZİNCİRİDİR; bu ucuz
    statik test zincirdeki launcher token'larından EN AZ BİRİNİN bu makinede
    fiilen ÇALIŞTIRILABİLİR olduğunu doğrular (shutil.which VEYA mevcut
    yorumlayıcının kendisi — `sys.executable`)."""
    import sys as _sys
    with open(HOOKS_JSON, encoding="utf-8") as f:
        veri = json.load(f)
    komut = veri["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert "||" in komut, "hooks.json'da fallback zinciri ('||') yok"
    segmentler = [s.strip() for s in komut.split("||")]
    launcherlar = [s.split()[0] for s in segmentler if s.split()]
    assert len(launcherlar) >= 2, launcherlar
    calisan_var = any(
        shutil.which(tok) or pathlib.Path(_sys.executable).stem.lower() == tok.lower()
        for tok in launcherlar
    )
    assert calisan_var, (
        f"fallback zincirindeki HİÇBİR launcher ({launcherlar}) bu makinede "
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
