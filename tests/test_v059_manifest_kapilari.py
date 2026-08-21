# -*- coding: utf-8 -*-
"""aile_dogrula.py v0.5.9 İKİ YENİ KAPI testleri (T7).

KAPI-A (MANİFEST SAYI): marketplace.json/plugin.json description metnindeki
"N skill" iddiası skills/ altındaki GERÇEK parça sayısıyla eşleşmiyorsa HATA.
(Saha gerçeği: vitrin "22 skill (+2 işlem rehberi)" diyordu, repoda 20 vardı —
vitrin bayatlığı mekanik yakalanmalı, göz taramasıyla değil.)

KAPI-B (HOOK KAPSAM): hooks.json'daki her run-hook.cmd modu pipeline_kayit.py
içinde --<mod> bayrağı olarak tanımlı olmalı; ayrıca hook_doktor'un dinamik
envanteri (hooks_olaylari) hooks.json olay kümesiyle eşit olmalı.

VENDOR deseni: aile depo DIŞINA kopyalanmışsa (manifest/hooks.json/tools yok)
her iki kapı SESSİZCE atlanır — kural depoyu bağlar, kopyayı değil.

Tüm senaryolar SENTETİK ağaçta koşar; gerçek repo asla değiştirilmez.
Sentetik yollarda gerçek dava adı/yolu YOKTUR.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-usta" / "scripts" / "aile_dogrula.py"
SKILLS_KOKU = REPO / "plugins" / "ortak-avukat" / "skills"
HOOKS_JSON = REPO / "plugins" / "ortak-avukat" / "hooks" / "hooks.json"
DOKTOR = REPO / "tools" / "hook_doktor.py"


def _cli(kok):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _gercek_parca_sayisi():
    return sum(1 for d in SKILLS_KOKU.iterdir()
               if d.is_dir() and (d / "SKILL.md").is_file())


def _sentetik_repo(skill_iddia=None, ekstra_hook_mod=None):
    """Gerçek skills ağacının kopyası + sentetik manifest/hooks/tools iskeleti.
    skill_iddia: marketplace description'a yazılacak 'N skill' metni (None = gerçek sayı).
    ekstra_hook_mod: hooks.json'a eklenecek, pipeline_kayit.py'de karşılığı
    OLMAYAN sentetik mod adı."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="oa-v059-kapi-"))
    eklenti = tmp / "plugins" / "ortak-avukat"
    shutil.copytree(SKILLS_KOKU, eklenti / "skills")
    (eklenti / ".claude-plugin").mkdir(parents=True)
    (tmp / ".claude-plugin").mkdir(parents=True)
    (tmp / "tools").mkdir()
    shutil.copy(DOKTOR, tmp / "tools" / "hook_doktor.py")

    if skill_iddia is None:
        skill_iddia = "%d skill" % _gercek_parca_sayisi()
    (eklenti / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": "ortak-avukat", "version": "0.5.9",
        "description": "Sentetik test eklentisi.",
    }), encoding="utf-8")
    (tmp / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "ortak-avukat",
        "description": "Sentetik vitrin.",
        "plugins": [{
            "name": "ortak-avukat", "source": "./plugins/ortak-avukat",
            "description": "Sentetik: %s iceren vitrin metni." % skill_iddia,
            "version": "0.5.9",
        }],
    }), encoding="utf-8")

    hveri = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    if ekstra_hook_mod:
        hveri["hooks"]["SentetikOlay"] = [{"hooks": [{
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" " + ekstra_hook_mod,
            "shell": "bash", "async": False,
        }]}]
    (eklenti / "hooks").mkdir()
    (eklenti / "hooks" / "hooks.json").write_text(
        json.dumps(hveri), encoding="utf-8")
    return eklenti / "skills"


# ── KAPI-A: MANİFEST SAYI ───────────────────────────────────────────────────

def test_kapi_a_yanlis_sayi_iddiasi_hata():
    """Vitrin '22 skill' derken gerçekte 20 parça varsa → HATA + exit 1."""
    kok = _sentetik_repo(skill_iddia="22 skill")
    kod, cikti = _cli(kok)
    assert kod == 1, f"yanlış sayı iddiası exit 1 üretmeliydi; çıktı:\n{cikti}"
    assert "22 skill" in cikti and "manifest" in cikti.lower()


def test_kapi_a_dogru_sayi_temiz():
    """İddia gerçek sayıyla eşleşiyorsa kapı sessiz → exit 0."""
    kok = _sentetik_repo()  # gerçek sayı yazılır
    kod, cikti = _cli(kok)
    assert kod == 0, f"doğru sayı iddiasında temiz geçmeliydi; çıktı:\n{cikti}"
    assert "AİLE YAPI DENETİMİ TEMİZ" in cikti


# ── KAPI-B: HOOK KAPSAM ─────────────────────────────────────────────────────

def test_kapi_b_tanimsiz_mod_hata():
    """hooks.json pipeline_kayit.py'de --bayrağı OLMAYAN bir mod çağırıyorsa → HATA."""
    kok = _sentetik_repo(ekstra_hook_mod="hook-hayalet")
    kod, cikti = _cli(kok)
    assert kod == 1, f"tanımsız hook modu exit 1 üretmeliydi; çıktı:\n{cikti}"
    assert "hook-hayalet" in cikti


def test_kapi_b_gercek_repo_kapsami_tam():
    """GERÇEK repo: hooks.json'daki tüm modlar pipeline_kayit.py'de tanımlı,
    hook_doktor dinamik envanteri hooks.json ile eşit → denetim temiz."""
    kod, cikti = _cli(SKILLS_KOKU)
    assert kod == 0, f"gerçek repo hook kapsamı temiz olmalıydı; çıktı:\n{cikti}"


# ── VENDOR: depo-dışı kopyada sessiz atlama ─────────────────────────────────

def test_depo_disi_kopyada_kapilar_sessiz_atlanir():
    """Yalnız skills/ ağacı kopyalanmışsa (manifest/hooks/tools YOK) yeni
    kapılar hata üretmez — kural depoyu bağlar, kopyayı değil."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="oa-v059-vendor-"))
    hedef = tmp / "skills"
    shutil.copytree(SKILLS_KOKU, hedef)
    kod, cikti = _cli(hedef)
    assert kod == 0, f"depo-dışı kopyada sessiz atlama bekleniyordu; çıktı:\n{cikti}"
