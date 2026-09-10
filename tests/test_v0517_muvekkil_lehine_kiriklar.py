# -*- coding: utf-8 -*-
"""v0.5.17 — MÜVEKKİL LEHİNE SONUCU BOZAN SİSTEMSEL KIRIKLARIN KİLİDİ.

2026-09-10 backend taramasının bulduğu dört kusur burada kilitlenir. Ortak
paydaları şudur: hiçbiri "script çöktü" diye görünmez; hepsi **sessizce**
müvekkilin aleyhine çalışır — bir kapı ya hiç doğmaz, ya baktığını sanıp
bakmaz, ya da baktığı şeyi yanlış okur.

  B1  tam_tur.py Python <3.12'de İMPORT EDİLEMEZ (f-string içi ters bölü)
      → Gate G'nin dayandığı dosya-analiz.json hiç doğmaz → kapı "yok" sayılır.
  B2  --taraf verilmeden koşulan müvekkil-aleyhi taraması KÖR, ama çıktı
      "[OK] ... bulunamadı" diyor → YANLIŞ GÜVENCE.
  B3  NEG deseni Türkçe `-me` OLUMSUZLUK ekiyle MASTAR/çekim `-me`sini
      ayırmıyor → "kabul etmektedir" (ikrar) olumsuzlanmış sayılıp susuyor.
  B4  `mudahil` CLI'de kabul ediliyor ama ALEYHE sözlüğünde yok → avukat taraf
      sıfatını DOĞRU verse bile tarama kör kalıyor.
"""
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
DD = SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py"

sys.path.insert(0, str(DD.parent))
import dilekce_denetim as dd  # noqa: E402


# ── B1 — HER SCRIPT DERLENEBİLİR OLMAK ZORUNDA ────────────────────────────

def test_b1_tum_scriptler_calisan_python_ile_derlenebilir():
    """Bir script'in İMPORT EDİLEMEMESİ, o script'in koruduğu kapının
    kapanması değil YOK SAYILMASIdır.

    `tam_tur.py` iki satırında f-string ifadesi İÇİNDE ters bölü taşıyordu;
    bu, Python 3.12'den ÖNCE (PEP 701) SyntaxError'dur. Depo `pyproject.toml`
    ile >=3.12 istiyor ve CI yalnız 3.12/3.13 koşuyor — ama `README.md`
    avukata "Python 3.10+" diyor. README'ye uyan bir kurulumda `tam_tur.py`
    HİÇ çalışmaz; `_oa/analiz/dosya-analiz.json` hiç doğmaz; ve
    `pipeline_kayit._gate_g_kalicilik_denetle` ilk satırında o dosyayı
    bulamayınca kapıyı SESSİZCE atlar (fail-closed dalına hiç varamaz).

    Bu test, sözdizimi düzeyindeki uyum kırığını süitin koştuğu HER Python
    sürümünde yakalar — kapının koruduğu araç, kapıdan önce ayakta olmalıdır.
    """
    kirik = []
    for yol in sorted(REPO.glob("plugins/**/*.py")) + sorted(REPO.glob("tools/*.py")):
        cp = subprocess.run([sys.executable, "-m", "py_compile", str(yol)],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace")
        if cp.returncode != 0:
            kirik.append("%s\n%s" % (yol.relative_to(REPO), (cp.stderr or "").strip()))
    assert not kirik, (
        "Şu script(ler) bu Python sürümünde DERLENMİYOR — import edilemeyen bir "
        "script, koruduğu kapıyı kapatmaz, YOK ETTİRİR:\n\n" + "\n\n".join(kirik))


# ── B2 — "BAKMADIM" İLE "BULAMADIM" AYNI ŞEY DEĞİLDİR ─────────────────────

IKRARLI_TASLAK = (
    "ADANA 2. ASLİYE HUKUK MAHKEMESİ'NE\n\n"
    "DOSYA NO : 2025/100 E.\nDAVALI : Müvekkil\nKONU : Cevap dilekçemizdir.\n\n"
    "AÇIKLAMALAR\n"
    "1. Müvekkil borcu kabul etmektedir ve davayı kabul ediyoruz.\n"
    "2. Müvekkilin kusurlu olduğunu beyan ederiz; iddia doğrudur.\n\n"
    "HUKUKİ SEBEPLER : HMK\nDELİLLER : Dosya kapsamı\n"
    "SONUÇ VE İSTEM : 1- Gereğini arz ederiz.\n"
)


def _kos(taslak_yolu, *ek):
    cp = subprocess.run(
        [sys.executable, str(DD), str(taslak_yolu), "--tip", "cevap",
         "--ictihat-muhakeme-yok", *ek],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=300)
    return cp.stdout or ""


@pytest.fixture()
def ikrarli(tmp_path):
    y = tmp_path / "taslak.md"
    y.write_text(IKRARLI_TASLAK, encoding="utf-8")
    return y


def test_b2_taraf_verilmeden_kosulan_tarama_TEMIZ_BEYANI_URETEMEZ(ikrarli):
    """--taraf yokken yalnız iki desenli 'genel' seti taranır. Eski çıktı buna
    rağmen `[OK] belirgin müvekkil-aleyhi ifade sinyali bulunamadı` basıyordu:
    dört ayrı ikrar cümlesi taşıyan bir dilekçeye TEMİZLİK BEYANI. HMK m.188 —
    ikrar kesin delildir; geri alınamaz."""
    cikti = _kos(ikrarli)
    assert "TARAMA KISMİ" in cikti, (
        "taraf sıfatı verilmeden koşulan tarama KISMİ olduğunu SÖYLEMEK "
        "ZORUNDADIR (sessiz atlama yasağı):\n" + cikti)
    assert "belirgin müvekkil-aleyhi ifade sinyali bulunamadı" not in cikti, (
        "YANLIŞ GÜVENCE REGRESYONU: kör tarama 'bulunamadı' diye raporlanamaz "
        "— 'bakmadım' ile 'bakıp bulamadım' aynı şey değildir:\n" + cikti)


def test_b2_taraf_verilince_kapsam_GORUNUR_ve_ikrar_yakalanir(ikrarli):
    cikti = _kos(ikrarli, "--taraf", "davali")
    assert "[KAPSAM]" in cikti and "davali" in cikti
    assert "TARAMA KISMİ" not in cikti
    assert "müvekkil-aleyhi ifade" in cikti


# ── B3 — TÜRKÇE `-me`: OLUMSUZLUK EKİ mi, MASTAR mı? ──────────────────────

@pytest.mark.parametrize("metin", [
    "Müvekkil borcu kabul etmektedir ve davayı kabul ediyoruz.",
    "Borcun tamamını kabul etmekteyiz; davayı kabul ediyoruz.",
    "Müvekkilin borcu kabul etmesi sebebiyle davayı kabul ediyoruz.",
])
def test_b3_olumlu_cekim_olumsuzlama_SAYILAMAZ(metin):
    """`kabul etmektedir / etmekteyiz / etmesi` OLUMLU İKRARDIR.

    Eski NEG deseni `\\bkabul\\s*etme` (kelime sınırı YOK) bu çekimleri
    olumsuzlama sanıyordu; ±70 karakterlik pencereye düşen her aleyhe kalıbı
    BLOK'tan BİLGİ'ye iniyor ve avukat UYARILMIYORDU."""
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, "cevap", "davali")
    assert aleyhe, (
        "REGRESYON (B3): olumlu çekim olumsuzlama sayıldı, gerçek ikrar "
        "susturuldu — %r" % metin)


@pytest.mark.parametrize("metin", [
    "İşbu beyanlarımız davanın kabulü anlamına gelmemek kaydıyla sunulmuştur. "
    "Davayı kabul etmiyoruz.",
    "Doğrudur, ancak davayı kabul etmiyoruz.",
])
def test_b3_gercek_olumsuzlama_HALA_susturur(metin):
    """Daraltma, gerçek olumsuzlama korumasını BOZMAMALIDIR (sahte alarm
    üretmek de bir kusurdur — kapıya güveni aşındırır)."""
    _e, _d, _o, aleyhe, notu = dd.denetle(metin, "cevap", "davali")
    assert not aleyhe, "gerçek olumsuzlama hâlâ sinyali düşürmeli: %r" % metin
    assert notu, "olumsuzlanmış kalıp [BİLGİ] notuna düşmeli (sessizce yutulmamalı)"


# ── B4 — CLI'NİN KABUL ETTİĞİ HER TARAF SIFATI TARANMALIDIR ───────────────

def test_b4_cli_taraf_secenekleri_ile_kalip_kapsami_AYRISAMAZ():
    """`--taraf` choices ile taranabilir sıfat kümesi ayrışırsa, avukat taraf
    sıfatını DOĞRU verdiği hâlde kör bir tarama alır — B2'den daha sinsidir,
    çünkü kullanıcı 'verdim, tarandı' sanır."""
    kaynak = DD.read_text(encoding="utf-8")
    m = re.search(r'add_argument\(\s*"--taraf".*?choices=\[(.*?)\]', kaynak, re.S)
    assert m, "--taraf choices listesi bulunamadı (test çıpası kaydı)"
    secenekler = {x.strip().strip('"\'') for x in m.group(1).split(",")}
    secenekler.discard("")
    kapsanmayan = sorted(
        t for t in secenekler if aleyhe_kapsami_kismi(t))
    assert not kapsanmayan, (
        "CLI şu taraf sıfat(lar)ını kabul ediyor ama kalıp kapsamı YOK — "
        "tarama sessizce körleşir: %s" % kapsanmayan)


def aleyhe_kapsami_kismi(taraf):
    _setler, kismi, _sebep = dd.aleyhe_kapsami(taraf)
    return kismi


def test_b4_mudahil_her_iki_ekseni_de_tarar():
    """Fer'î müdahil yanında katıldığı tarafın yardımcısıdır (HMK m.66-69);
    script hangi tarafta olduğunu BİLEMEZ → fail-closed: iki eksen de taranır.
    Yanlış-pozitifi avukat gözü eler; yanlış-negatif müvekkili batırır."""
    setler, kismi, _ = dd.aleyhe_kapsami("mudahil")
    assert not kismi
    assert {"davaci", "davali", "genel"} <= set(setler)

    _e, _d, _o, aleyhe, _n = dd.denetle(
        "Müdahil olarak davayı kabul ediyoruz.", "cevap", "mudahil")
    assert aleyhe, "müdahil tarafında kabul/ikrar ekseni yakalanmalı"
