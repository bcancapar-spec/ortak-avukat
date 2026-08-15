# -*- coding: utf-8 -*-
"""v0.5.8.4 HOOK KATMANI — 372 Torbalı saha ölçümlerinin devşirmesi.

SAHA KANITI (372 provası, A/B testiyle ölçülmüş):
- Elle kurulan content.xml'li UDF'ler UYAP editöründe AÇILMIYOR; html2udf
  ürünleri açılıyor. Suçlu re-zip değil, yerel motorun content.xml içeriği
  (styles bloğunda tanımsız `hvl-default` resolver'ı). → PreToolUse ELLE-UDF
  kapısı: elle zip+content.xml girişimi "ask" kararıyla görünür kılınır.
- Stop hook 23 kez MÜHÜRSÜZ uyardı, model 0 kez uyguladı. → uyarı işlemiyor;
  hook-denetle artık muhur_yaz.py'ı best-effort KENDİSİ koşturur.
- 372 defterinde hook tipli olay SIFIRDI — hook izleri yan dosyalarda
  kayboluyordu. → hook fiilen iş yaptığında deftere olay satırı düşer.

Tüm testler tmp_path + sentetik veri kullanır (repo kuralı m.7 —
sabit-yol-sızıntısı dersi: gerçek dava yolu/kişi adı ASLA yazılmaz).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
PK = PLUGIN / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
WRAP = PLUGIN / "hooks" / "run-hook.cmd"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"


@pytest.fixture(scope="module")
def pk():
    spec = importlib.util.spec_from_file_location("_test_v0584_pk", PK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_v0584_pk"] = mod
    spec.loader.exec_module(mod)
    return mod


def _kos(args, kok, stdin_metni=""):
    cp = subprocess.run([sys.executable, str(PK)] + args, capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        cwd=str(kok), input=stdin_metni, timeout=120)
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


def _dava_klasoru_kur(kok, defterli=False):
    """Sentetik dava klasörü: 3 adet NNN_ evrak → `_dosya_klasoru_mu` True."""
    for i in ("001", "002", "003"):
        (kok / f"{i}_Sentetik_Evrak.pdf").write_text("sentetik", encoding="utf-8")
    if defterli:
        (kok / "_oa" / "defter").mkdir(parents=True, exist_ok=True)


_ELLE_UDF_ICERIK = (
    "import zipfile\n"
    "with zipfile.ZipFile('taslak.udf', 'w') as z:\n"
    "    z.writestr('content.xml', '<template/>')\n")


# ── (1) PreToolUse ELLE-UDF KAPISI — ask kararı ─────────────────────────────

def test_pretool_dava_klasorunde_desenli_icerik_ask_basar(tmp_path):
    """372 dersi 10-D: dava klasöründe elle zipfile+content.xml girişimi
    'ask' kararıyla görünür olur — bloklamaz, avukata sorar."""
    _dava_klasoru_kur(tmp_path)
    payload = json.dumps({"cwd": str(tmp_path),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0, "PreToolUse hook'u ASLA bloklamaz (exit 0 şart)"
    veri = json.loads(out.strip())
    ozgu = veri["hookSpecificOutput"]
    assert ozgu["hookEventName"] == "PreToolUse"
    assert ozgu["permissionDecision"] == "ask"
    gerekce = ozgu["permissionDecisionReason"]
    assert "ELLE-UDF" in gerekce
    assert "udf_yaz.py" in gerekce and "html2udf" in gerekce
    assert "avukatın kararıdır" in gerekce


def test_pretool_zipfile_udf_deseni_komutta_da_yakalanir(tmp_path):
    """İkinci desen ailesi: `ZipFile(` + `.udf` — Bash/PowerShell komut satırı
    üstünden elle kurulum da aynı kapıya takılır."""
    _dava_klasoru_kur(tmp_path)
    payload = json.dumps({"cwd": str(tmp_path), "tool_input": {
        "command": "python -c \"from zipfile import ZipFile; ZipFile('cikti.udf','w')\""}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0
    veri = json.loads(out.strip())
    assert veri["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_pretool_desensiz_girdi_sessiz(tmp_path):
    """Dava klasöründe ama masum girdi — gürültü disiplini: ÇIKTI YOK."""
    _dava_klasoru_kur(tmp_path)
    payload = json.dumps({"cwd": str(tmp_path), "tool_input": {
        "content": "print('merhaba')", "command": "ls -la"}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0 and out.strip() == ""


def test_pretool_dava_disi_klasorde_sessiz(tmp_path):
    """Sıradan kod deposunda zipfile+content.xml MEŞRU iştir — kapı yalnız
    dava klasöründe nöbet tutar."""
    (tmp_path / "notlar.md").write_text("alışveriş", encoding="utf-8")
    payload = json.dumps({"cwd": str(tmp_path),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0 and out.strip() == ""


def test_pretool_bozuk_stdin_sessiz(tmp_path):
    """Bozuk payload → sessiz exit 0 (hook ASLA bloklamaz, ASLA çökmez)."""
    _dava_klasoru_kur(tmp_path)
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, "{{{bu json değil")
    assert kod == 0 and out.strip() == ""


def test_pretool_ask_hook_olayi_deftere_dusuyor(tmp_path):
    """HOOK OLAY İZİ (372 kanıtı: defterde hook tipli olay 0'dı): ask kararı
    verildiğinde ve defter VARSA pipeline-olaylar.jsonl'e iz düşer."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    payload = json.dumps({"cwd": str(tmp_path),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0 and "PreToolUse" in out
    jsonl = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    assert jsonl.is_file(), "hook olay izi deftere düşmedi"
    olaylar = [json.loads(s) for s in jsonl.read_text(encoding="utf-8").splitlines() if s.strip()]
    hook_olaylar = [o for o in olaylar if o.get("tip") == "hook"]
    assert hook_olaylar, "tip=hook olayı yok"
    assert hook_olaylar[-1]["olay"] == "pretool-ask"
    assert hook_olaylar[-1].get("zaman")


# ── (2) TESLİM DİSİPLİNİ DEFTER-VARKEN (hook-prompt) ───────────────────────

def test_hook_prompt_defter_ve_muhursuz_urun_teslim_disiplini_blogu(tmp_path):
    """Defter VAR + mühürsüz teslim-sınıfı ürün VAR → kısa TESLİM-DİSİPLİNİ
    bloğu enjekte edilir (tam devir bloğu DEĞİL — o defter yokken basılır)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "dilekce.udf").write_bytes(b"PK\x03\x04sentetik")
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    veri = json.loads(out.strip())
    metin = veri["hookSpecificOutput"]["additionalContext"]
    assert "TESLİM-DİSİPLİNİ" in metin
    assert "MÜHÜRSÜZ" in metin and "dilekce.udf" in metin
    assert "muhur_yaz.py" in metin
    assert "DEVİR YÜKÜMLÜLÜĞÜ" not in metin  # hat açık — devir metni tekrarlanmaz


def test_hook_prompt_defter_ve_temiz_durumda_sessiz(tmp_path):
    """Mevcut sözleşme KORUNUR: defter var + temiz durum → SESSİZ
    (test_devir_zorlayici.test_hat_ACIKSA_sessiz_kalir'ın simetriği)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0 and out.strip() == ""


# ── (3) AĞ-İMPORT SAHA TARAMASI (_oa/araclar) ──────────────────────────────

def test_ag_importlu_arac_kopyasi_uyari_uretir(tmp_path, pk):
    """`_oa/araclar/` kopyasında satır-başı ağ-import (Layer 0 ihlal adayı)
    → görünür uyarı; dosya adı + modül adı geçer."""
    _dava_klasoru_kur(tmp_path)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "kopya_arac.py").write_text(
        "import requests\n\ndef f():\n    return 1\n", encoding="utf-8")
    uyari = pk._arac_ag_import_uyarisi(str(tmp_path))
    assert uyari is not None
    assert "kopya_arac.py" in uyari and "requests" in uyari


def test_ag_import_temiz_kopyada_sessiz(tmp_path, pk):
    _dava_klasoru_kur(tmp_path)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "temiz_arac.py").write_text(
        "import os\nimport json\n", encoding="utf-8")
    assert pk._arac_ag_import_uyarisi(str(tmp_path)) is None


def test_ag_import_uyarisi_hook_prompt_enjeksiyonunda(tmp_path):
    """Uyarı yalnız fonksiyonda kalmaz — hook-prompt enjeksiyonuna taşınır
    (defter açıkken de görünür kalır; bayat-araç aşısıyla aynı kanal)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "kopya_arac.py").write_text("import httpx\n", encoding="utf-8")
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    metin = json.loads(out.strip())["hookSpecificOutput"]["additionalContext"]
    assert "AĞ-İMPORT" in metin and "kopya_arac.py" in metin


def test_ag_import_uyarisi_hook_denetle_ciktisinda(tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "kopya_arac.py").write_text(
        "import urllib.request\n", encoding="utf-8")
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, "hook-denetle ASLA bloklamaz"
    assert "AĞ-İMPORT" in out and "kopya_arac.py" in out


# ── (4) OTOMATİK MÜHÜR (23 uyarı / 0 uygulama dersi) ───────────────────────

def test_hook_denetle_muhursuz_urunu_otomatik_muhurler(tmp_path):
    """Uyarı işlemiyor (372: 23/0) → hook-denetle muhur_yaz.py'ı KENDİSİ
    koşturur; PROV dürüstlüğü: sonradan basılan mühür üretim yolunu İDDİA
    EDEMEZ (was_generated_by bunu açıkça söyler)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    urun = cikti / "dilekce.udf"
    urun.write_bytes(b"PK\x03\x04sentetik-udf")
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "OTOMATİK MÜHÜR: 1 ürün" in out
    prov = pathlib.Path(str(urun) + ".prov.json")
    assert prov.is_file(), "muhur_yaz fiilen koşmadı — .prov.json doğmadı"
    kayit = json.loads(prov.read_text(encoding="utf-8"))
    assert kayit["was_generated_by"] == (
        "hook-otomatik (post-hoc); üretim yolu beyan edilmedi")
    assert kayit["artifact_file"].endswith("dilekce.udf")
    # HOOK OLAY İZİ: denetle gövdesi fiilen iş yaptı + defter var → iz düşer.
    jsonl = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    assert jsonl.is_file()
    olaylar = [json.loads(s) for s in jsonl.read_text(encoding="utf-8").splitlines() if s.strip()]
    assert any(o.get("tip") == "hook" and o.get("olay") == "denetle" for o in olaylar)


def test_hook_denetle_ikinci_kosuda_muhur_tekrarlanmaz(tmp_path):
    """İdempotenlik: mühürlenen ürün ikinci koşuda artık mühürsüz listesinde
    değildir — OTOMATİK MÜHÜR satırı tekrar basılmaz."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "dilekce.udf").write_bytes(b"PK\x03\x04sentetik-udf")
    _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    _kod, out2, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert "OTOMATİK MÜHÜR" not in out2


# ── (5) run-hook.cmd — hook-pretool modu + stdin aktarımı (bash tarafı) ────

def _gercek_bash():
    """PATH'teki `bash` Windows'ta WSL stub'ına çözülebilir (447 tuzağı) —
    Git Bash'i açık yoldan ara; yoksa None (test atlanır)."""
    for aday in (r"C:\Program Files\Git\bin\bash.exe",
                 r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if pathlib.Path(aday).is_file():
            return aday
    import shutil
    b = shutil.which("bash")
    if b and "system32" not in b.lower():
        return b
    return None


def test_runhook_bash_stdin_aktarimi_pretool(tmp_path):
    """Sarmalayıcı stdin'i python'a AKTARMALI: payload sarmalayıcıdan geçip
    ask kararına dönüşür (aktarım kopuksa desen hiç görülmez → sessizlik)."""
    b = _gercek_bash()
    if b is None:
        pytest.skip("ortamda gerçek bash yok")
    _dava_klasoru_kur(tmp_path)
    payload = json.dumps({"cwd": str(tmp_path),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    cp = subprocess.run([b, str(WRAP), "hook-pretool"], cwd=str(tmp_path),
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", input=payload, timeout=120)
    assert cp.returncode == 0
    out = cp.stdout or ""
    assert "PreToolUse" in out and '"ask"' in out, (
        "stdin sarmalayıcıdan python'a AKMADI — desen görülmedi")


def test_hooks_json_pretool_girisi_kayitli():
    """hooks.json PreToolUse girdisi: matcher Write|Edit|Bash|PowerShell,
    komut = sarmalayıcı + hook-pretool (v0.5.8.2 sözleşmesi: || YASAK)."""
    veri = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
    assert "PreToolUse" in veri, "PreToolUse hook'u kayıtlı değil"
    girdiler = veri["PreToolUse"]
    assert any(all(t in (g.get("matcher") or "")
                   for t in ("Write", "Edit", "Bash", "PowerShell"))
               for g in girdiler), "matcher Write|Edit|Bash|PowerShell değil"
    komut = json.dumps(girdiler, ensure_ascii=False)
    assert "hook-pretool" in komut
    assert "run-hook.cmd" in komut
    assert "||" not in komut
