# -*- coding: utf-8 -*-
"""HOOK KATMANI — YEREL DETERMİNİSTİK DOĞRULAMA (v0.5.7).

Denizli 754 bulgusu: 50 dakikalık saha oturumunda dört hook olayından SIFIR
iz vardı. Kök neden kod değildi (taze süreçte `UserPromptSubmit` enjeksiyonu
birebir çalıştı) — masaüstü uygulamasının BAYAT süreciydi (eklenti
güncellemesinden önce açılmış; hook kaydını eski süreçten miras aldı).

Bu dosya, hook katmanının "çalışır durumda" iddiasını BEYAN olmaktan çıkarır:
hooks.json'daki HER komut, harness'in yapacağı gibi (${CLAUDE_PLUGIN_ROOT}
ikamesiyle) fiilen çalıştırılır ve sözleşmesi doğrulanır — ağsız, API'siz,
her makinede. (Canlı oturumda ateşlemenin son doğrulaması yine insanındır:
uygulamayı TAM kapat-aç, dava klasöründe ilk mesajda enjeksiyonu gör —
`tools/hook_doktor.py` bu tarifi basar.)
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN_KOK = REPO / "plugins" / "ortak-avukat"
HOOKS_JSON = PLUGIN_KOK / "hooks" / "hooks.json"

BEKLENEN_OLAYLAR = ["UserPromptSubmit", "PostToolUse", "Stop", "SessionEnd"]


def _hooks_veri():
    with open(HOOKS_JSON, encoding="utf-8") as f:
        return json.load(f)


def _ilk_python_alternatifi(komut):
    """v0.5.8.2 SÖZLEŞME (447 yapısal-arıza onarımı): hooks.json artık `||`
    zinciri DEĞİL, tek tırnaklı sarmalayıcı çağırır —
    `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" <mod>`. Kabuksuz yürütmede
    `||` python'a argüman gidip sessizce ölüyordu (üç sahada sıfır ateşleme);
    fallback mantığı sarmalayıcının İÇİNE taşındı. Bu yardımcı, sarmalayıcı
    semantiğini deterministik doğrulama için doğrudan python çağrısına çevirir:
    run-hook.cmd <mod>  ≡  python pipeline_kayit.py --<mod>."""
    assert "||" not in komut, "|| zinciri yasak (v0.5.8.2 yapısal onarım)"
    ilk = komut.replace("${CLAUDE_PLUGIN_ROOT}", str(PLUGIN_KOK).replace("\\", "/"))
    parcalar = ilk.split()
    assert parcalar[0].strip('"').endswith("hooks/run-hook.cmd"), ilk
    assert len(parcalar) == 2, ilk
    mod = parcalar[1]
    assert mod in ("hook-prompt", "hook-postwrite", "hook-denetle"), mod
    script = PLUGIN_KOK / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
    return [sys.executable, str(script), "--" + mod]


def _kos(argv, cwd):
    cp = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(cwd), timeout=120)
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


@pytest.fixture
def dava_klasoru():
    """Sentetik dava klasörü: 3 adet NNN_ evrak → `_dosya_klasoru_mu` True."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in ("001", "002", "003"):
        (tmp / f"{i}_Test_Evraki.pdf").write_text("sentetik", encoding="utf-8")
    return tmp


# ── (1) ŞEMA — belgeyle birebir (docs: hooks.md) ────────────────────────────

def test_hooks_json_semasi_belgeye_uygun():
    """Üst seviye `hooks` sarmalayıcısı + dört olay + her girdide `hooks`
    listesi + `type: command`. (Belge teyidi 2026-08-07: bu üçlü yuvalama
    TEK belgelenmiş şemadır.)"""
    v = _hooks_veri()
    assert set(v.keys()) == {"hooks"}, "üst seviye YALNIZ 'hooks' olmalı"
    ic = v["hooks"]
    for olay in BEKLENEN_OLAYLAR:
        assert olay in ic, f"'{olay}' olayı hooks.json'da yok"
        for girdi in ic[olay]:
            assert isinstance(girdi.get("hooks"), list) and girdi["hooks"]
            for h in girdi["hooks"]:
                assert h.get("type") == "command"
                assert "${CLAUDE_PLUGIN_ROOT}" in h.get("command", ""), (
                    "hook komutu eklenti köküne mutlak bağlanmalı (belge kuralı)")


def test_posttooluse_eslestiricisi_write_edit():
    v = _hooks_veri()["hooks"]["PostToolUse"]
    assert any(re.search(r"Write\|Edit|Edit\|Write", g.get("matcher", "")) for g in v)


# ── (2) KOMUT SÖZLEŞMELERİ — fiilen koştur ──────────────────────────────────

def test_userpromptsubmit_dava_klasorunde_devir_enjeksiyonu_basar(dava_klasoru):
    komut = _hooks_veri()["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    kod, out, _err = _kos(_ilk_python_alternatifi(komut), dava_klasoru)
    assert kod == 0, "UserPromptSubmit ASLA bloklamaz (exit 0 şart)"
    veri = json.loads(out)
    ozgu = veri["hookSpecificOutput"]
    assert ozgu["hookEventName"] == "UserPromptSubmit"
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in ozgu["additionalContext"]
    assert "oa-pipeline" in ozgu["additionalContext"]


def test_userpromptsubmit_dava_disi_klasorde_sessiz(tmp_path):
    komut = _hooks_veri()["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    kod, out, _err = _kos(_ilk_python_alternatifi(komut), tmp_path)
    assert kod == 0
    assert out.strip() == "", "dava-dışı klasörde enjeksiyon OLMAMALI (gürültü disiplini)"


def test_stop_ve_sessionend_komutlari_calisir_ve_bloklamaz(dava_klasoru):
    ic = _hooks_veri()["hooks"]
    for olay in ("Stop", "SessionEnd"):
        komut = ic[olay][0]["hooks"][0]["command"]
        kod, _out, _err = _kos(_ilk_python_alternatifi(komut), dava_klasoru)
        assert kod == 0, f"{olay} hook'u ASLA bloklamaz (exit 0 şart)"


def test_posttooluse_komutu_calisir_ve_bloklamaz(dava_klasoru):
    komut = _hooks_veri()["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    kod, _out, _err = _kos(_ilk_python_alternatifi(komut), dava_klasoru)
    assert kod == 0


# ── (3) BAYAT-TOHUM AŞISI (v0.5.7) ─────────────────────────────────────────

def _pk():
    import importlib.util
    yol = PLUGIN_KOK / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
    spec = importlib.util.spec_from_file_location("pk_hook_test", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bayat_arac_uyarisi_eski_kopyayi_yakalar(dava_klasoru):
    """`_oa/araclar/`daki kopya eklentidekiyle bayt-farklıysa uyarı ÜRETİLİR
    ve bayat dosyanın adı geçer (Denizli 754: komşudan miras v1.1 kopyalar)."""
    pk = _pk()
    araclar = dava_klasoru / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "oa_ingest.py").write_text("# ESKI NESIL KOPYA\n", encoding="utf-8")
    uyari = pk._bayat_arac_uyarisi(str(dava_klasoru))
    assert uyari is not None and "BAYAT" in uyari and "oa_ingest.py" in uyari
    assert "komşu" in uyari  # kaynağı da öğretir


def test_bayat_arac_uyarisi_taze_kopyada_sessiz(dava_klasoru):
    pk = _pk()
    araclar = dava_klasoru / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    gercek = PLUGIN_KOK / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"
    (araclar / "oa_ingest.py").write_bytes(gercek.read_bytes())
    assert pk._bayat_arac_uyarisi(str(dava_klasoru)) is None


def test_bayat_arac_uyarisi_araclar_yoksa_sessiz(dava_klasoru):
    pk = _pk()
    assert pk._bayat_arac_uyarisi(str(dava_klasoru)) is None


def test_hook_prompt_hat_acikken_bayat_araci_enjekte_eder(dava_klasoru):
    """Hat açık (defter var) → devir hatırlatması YOK ama bayat araç VARSA
    o enjekte EDİLİR — kapı kaybı her turda görünür kalır."""
    pk = _pk()
    (dava_klasoru / "_oa" / "defter").mkdir(parents=True)
    araclar = dava_klasoru / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "udf_yaz.py").write_text("# eski\n", encoding="utf-8")
    komut = _hooks_veri()["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    kod, out, _err = _kos(_ilk_python_alternatifi(komut), dava_klasoru)
    assert kod == 0
    veri = json.loads(out)
    metin = veri["hookSpecificOutput"]["additionalContext"]
    assert "BAYAT" in metin and "udf_yaz.py" in metin
    assert "DEVİR YÜKÜMLÜLÜĞÜ" not in metin  # hat açık — devir metni tekrarlanmaz
