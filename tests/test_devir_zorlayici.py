"""DEVİR ZORLAYICI + ATLANMIŞ HAT NÖBETÇİSİ (v0.5.6.1 — P0, saha kanıtlı).

SAHA VAKASI: Avukat çekirdek skill'i çağırdı; model iki dilekçe + UDF + PDF
üretti ama `oa-pipeline`'a HİÇ devretmedi — parçaların yalnız description'larını
okuyup disiplini kendi muhakemesiyle yürüttü. Çıktı iyiydi; ama süre hesabı,
antitez matrisi ve teslim kapıları hiç koşmadı. Avukat "plugin'i kullandın mı?"
diye sormasa fark edilmeyecekti.

İKİ AYRI KUSUR BİRLEŞMİŞTİ:

1) `plugin.json`'dan `"hooks"` kaydı düşmüştü (v0.5.6). `hooks.json` diskte
   duruyordu ama manifest onu kaydetmediği için Claude Code HİÇ yüklemiyordu —
   yani üç tetiğin (PostToolUse/Stop/SessionEnd) üçü de ölüydü. Mevcut
   `test_hooks_wiring.py` bunu YAKALAYAMADI: dosyanın VARLIĞINI sınıyordu,
   manifeste KAYITLI olduğunu değil.

2) Hooks çalışsa bile sessiz kalırdı: hem `_hook_postwrite_tetikle_mi` hem
   `_hook_govde_calistir` işe "`_oa/defter` var mı" diye başlıyordu. Hat hiç
   açılmadıysa defter de yoktur → nöbetçi, tam da nöbet tutması gereken vakada
   uyuyordu.

DÜRÜST SINIR (test bunu da kilitler): hiçbir hook modeli bir skill'i çağırmaya
ZORLAYAMAZ. `UserPromptSubmit` elimizdeki en güçlü şeydir — çıktısı modelin
BAĞLAMINA, model prompt'u işlemeden önce girer; SKILL.md ise ancak çağrılırsa
yüklenir. Yani metin bağlama taşınır. Garanti değildir; bu yüzden ikinci ayak
(Stop hook tespiti) ayrıca vardır.
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
PLUGIN_JSON = PLUGIN / ".claude-plugin" / "plugin.json"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"
PK = PLUGIN / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


@pytest.fixture(scope="module")
def pk():
    spec = importlib.util.spec_from_file_location("_test_devir_pk", PK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_devir_pk"] = mod
    spec.loader.exec_module(mod)
    return mod


def _kos(args, kok):
    cp = subprocess.run([sys.executable, str(PK)] + args, capture_output=True,
                        text=True, encoding="utf-8", errors="replace", cwd=str(kok))
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


# ── (1) MANİFEST KABLOSU — kaydı düşen hook, olmayan hooktur ────────────────

def test_plugin_json_hooks_KAYDINI_tasimak_ZORUNDA():
    """ASIL REGRESYON: v0.5.6'da bu satır silindi ve üç tetiğin üçü birden
    öldü. `hooks.json`'un diskte durması YETMEZ — manifest onu kaydetmelidir."""
    veri = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))

    assert "hooks" in veri, (
        "plugin.json'da `hooks` kaydı YOK. hooks.json diskte dursa bile "
        "Claude Code onu YÜKLEMEZ; PostToolUse/Stop/SessionEnd/UserPromptSubmit "
        "tetiklerinin HEPSİ ölür ve model bir adımı atladığında hiçbir şey "
        "uyarmaz (v0.5.6 saha vakası).")
    assert veri["hooks"] == "./hooks/hooks.json", veri["hooks"]

    # Kayıt, gerçekten var olan bir dosyayı göstermeli (kırık yol da ölü hooktur).
    hedef = (PLUGIN_JSON.parent.parent / veri["hooks"].lstrip("./")).resolve()
    assert hedef.is_file(), f"manifest kaydı var olmayan dosyayı gösteriyor: {hedef}"


def test_dort_hook_olayi_da_kayitli():
    """Devir zorlayıcısı (UserPromptSubmit) ve üç tespit ayağı birlikte olmalı."""
    veri = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
    for olay in ("UserPromptSubmit", "PostToolUse", "Stop", "SessionEnd"):
        assert olay in veri, f"{olay} hook'u kayıtlı değil"
    komut = json.dumps(veri["UserPromptSubmit"], ensure_ascii=False)
    assert "--hook-prompt" in komut


# ── (2) DEVİR ZORLAYICISI — bağlama enjeksiyon ─────────────────────────────

def _dava_klasoru_kur(kok, defterli=False, urun=False):
    for i in range(3):
        (kok / f"00{i + 1}_Evrak.pdf").write_text("x", encoding="utf-8")
    if defterli:
        (kok / "_oa" / "defter").mkdir(parents=True, exist_ok=True)
    if urun:
        (kok / "cikti").mkdir(parents=True, exist_ok=True)
        (kok / "cikti" / "dilekce.md").write_text(
            "MAHKEMESİ'NE\nDAVALI : X\nNETİCE-İ TALEP : reddine karar verilmesini talep ederiz.",
            encoding="utf-8")


def test_hat_acilmamis_dava_klasorunde_devir_baglama_ENJEKTE_edilir(tmp_path):
    """SKILL.md ancak model onu çağırırsa yüklenir — atlama vakasında hiç
    okunmaz. Bu hook çağrıdan bağımsız her turda koşar; yükümlülük böylece
    metinden BAĞLAMA taşınır."""
    _dava_klasoru_kur(tmp_path)
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)

    assert kod == 0, "hook ASLA bloklamaz"
    veri = json.loads(out.strip())
    ek = veri["hookSpecificOutput"]
    assert ek["hookEventName"] == "UserPromptSubmit"
    metin = ek["additionalContext"]
    assert "oa-pipeline" in metin
    assert "ÇAĞRIYLA" in metin, "devir sözle değil çağrıyla olur kuralı geçmeli"
    for parca in ("oa-sure", "oa-vakia", "oa-antitez", "oa-kontrol", "oa-gizlilik"):
        assert parca in metin, f"atlanınca koşmayacak parça sayılmamış: {parca}"
    assert "ENGEL DEĞİLDİR" in metin, "amaç çizgisi: bloklamaz, görünür kılar"


def test_hat_ACIKSA_sessiz_kalir(tmp_path):
    """Gürültü disiplini: her turda tekrar eden uyarı, okunmayan uyarıya
    dönüşür (uyum maliyeti = uyum). Defter varsa hiçbir şey basılmaz."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert out.strip() == "", f"hat açıkken konuşmamalıydı: {out!r}"


def test_dava_klasoru_degilse_sessiz_kalir(tmp_path):
    """Sıradan bir dizinde (kod deposu, masaüstü) hukuk uyarısı basmak
    gürültüdür — ve kullanıcının güvenini aşındırır."""
    (tmp_path / "notlar.md").write_text("alışveriş listesi", encoding="utf-8")
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0 and out.strip() == ""


# ── (3) ATLANMIŞ HAT NÖBETÇİSİ — tespit ayağı ──────────────────────────────

def test_urun_VAR_defter_YOK_ise_gorunur_uyari(tmp_path, pk):
    """SAHA VAKASININ BİREBİR TAKLİDİ: model çıktıyı kök altındaki `cikti/`ye
    yazdı, hattı hiç açmadı. Nöbetçi sözleşmeli dizine (`_oa/cikti`) bakarak
    arasaydı yine kör kalırdı — bu yüzden kökün ilk iki katmanı taranır."""
    _dava_klasoru_kur(tmp_path, urun=True)

    uyari = pk._hat_atlandi_uyarisi(str(tmp_path))

    assert uyari is not None, "ürün var, defter yok — bu hâl GÖRÜNMELİ"
    assert "HAT ATLANDI" in uyari
    assert "dilekce.md" in uyari, "hangi ürün bulundu, adıyla söylenmeli"
    assert "ENGEL DEĞİLDİR" in uyari


def test_defter_VARSA_notbetci_susar(tmp_path, pk):
    """Hat açılmışsa bu nöbetçinin işi yok — diğer kapılar devralır."""
    _dava_klasoru_kur(tmp_path, defterli=True, urun=True)
    assert pk._hat_atlandi_uyarisi(str(tmp_path)) is None


def test_urun_YOKSA_notbetci_susar(tmp_path, pk):
    """Boş/yeni klasörde uyarı basmak yanlış-pozitiftir."""
    _dava_klasoru_kur(tmp_path)
    assert pk._hat_atlandi_uyarisi(str(tmp_path)) is None


def test_notbetci_stop_hookunda_gorunur_ve_BLOKLAMAZ(tmp_path):
    """Uyarı yalnız fonksiyonda kalmaz — Stop hook çıktısına da düşer; ve
    çıkış kodunu DEĞİŞTİRMEZ."""
    _dava_klasoru_kur(tmp_path, urun=True)
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, "Stop hook ASLA bloklamaz"
    assert "HAT ATLANDI" in out


def test_notbetci_agir_dizinlere_dalmaz(tmp_path, pk):
    """Maliyet sınırı: nöbetçi her turda koşar; derin ağaçlara dalarsa
    oturumu yavaşlatır. Derinlik 2 ile sınırlı olmalı."""
    derin = tmp_path / "a" / "b" / "c" / "d"
    derin.mkdir(parents=True)
    (derin / "dilekce.md").write_text("NETİCE-İ TALEP : ...", encoding="utf-8")
    _dava_klasoru_kur(tmp_path)

    assert pk._hat_atlandi_uyarisi(str(tmp_path)) is None, (
        "derin ağaçtaki dosya taranmamalı — maliyet sınırı")
