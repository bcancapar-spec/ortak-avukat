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


# ═══════════════════════════════════════════════════════════════════════════
# B6 — İŞ MAHKEMELERİ EKSENİ (2026-09-10 saha testi)
#
# Genel medeni usul kalıpları (kabul/ikrar/feragat/vazgeçme) iş davasında
# YETMEZ: müvekkili bitiren ikrar orada BAŞKA bir dille gelir. Onarım öncesi
# ölçüm: işçi yanında 0/7, işveren yanında 0/5 — hiçbiri yakalanmıyordu.
# ═══════════════════════════════════════════════════════════════════════════

def _ocr_bozulmus(metin):
    """Türkçe karakterleri düşmüş metin — OCR'dan geçmiş evrakın gerçek hâli."""
    for a, b in (("ş", "s"), ("ı", "i"), ("ğ", "g"), ("ü", "u"),
                 ("ö", "o"), ("ç", "c"), ("İ", "I"), ("Ş", "S")):
        metin = metin.replace(a, b)
    return metin


# Her biri, işçi (davacı) müvekkilin davasını TEK BAŞINA bitirebilecek ikrardır.
IS_ISCI_YANI = [
    ("Müvekkil 12.03.2024 tarihinde istifa etmiştir.",
     "istifa → fesih işçiye ait olur, kıdem+ihbar düşer (4857 m.17, m.120)"),
    ("İş sözleşmesi müvekkilin kendi isteğiyle ayrılması ile sona ermiştir.",
     "kendi isteğiyle ayrılma → işveren feshi yok, tazminat yok"),
    ("Müvekkil işten ayrılırken ibranameyi imzalamıştır.",
     "ibraname → alacakların ibrası (TBK m.420)"),
    ("Taraflar arasında ikale sözleşmesi imzalanarak iş akdi sona ermiştir.",
     "ikale → işe iade hakkı ve tazminatlar ortadan kalkar"),
    ("Müvekkilin tüm yasal alacakları ödenmiş, bakiye alacağı kalmamıştır.",
     "alacak kalmadı ikrarı → dava konusuz kalır"),
    ("Müvekkil işyerinde devamsızlık yapmıştır.",
     "devamsızlık → işverenin haklı fesih sebebi (4857 m.25/II-g)"),
    ("Feshin haklı sebebe dayandığı görülmektedir.",
     "haklı fesih ikrarı → işe iade + tazminat talepleri çöker"),
]

# Her biri, işveren (davalı) müvekkil için yıkıcıdır.
IS_ISVEREN_YANI = [
    ("Fesih haksız olarak gerçekleştirilmiştir.", "haksız fesih ikrarı"),
    ("Davacı işçinin kıdem tazminatına hak kazandığı açıktır.", "kıdem hakkı ikrarı"),
    ("İşçi fazla mesai yapmıştır ancak ücretleri ödenmemiştir.", "ödenmemiş fazla mesai"),
    ("Davacı sigortasız çalıştırılmıştır.", "sigortasız çalıştırma (SGK + ceza riski)"),
    ("İhbar öneline uyulmamıştır.", "ihbar tazminatı ikrarı"),
]


@pytest.mark.parametrize("metin,neden", IS_ISCI_YANI)
@pytest.mark.parametrize("bozulma", [lambda x: x, _ocr_bozulmus], ids=["turkce", "ocr"])
def test_b6_isci_yani_ikrar_yakalanir(metin, neden, bozulma):
    _e, _d, _o, aleyhe, _n = dd.denetle(bozulma(metin), "dava", "davaci")
    assert aleyhe, "İŞ HUKUKU KÖRLÜĞÜ (B6): %r yakalanmadı — %s" % (metin, neden)


@pytest.mark.parametrize("metin,neden", IS_ISVEREN_YANI)
@pytest.mark.parametrize("bozulma", [lambda x: x, _ocr_bozulmus], ids=["turkce", "ocr"])
def test_b6_isveren_yani_ikrar_yakalanir(metin, neden, bozulma):
    _e, _d, _o, aleyhe, _n = dd.denetle(bozulma(metin), "cevap", "davali")
    assert aleyhe, "İŞ HUKUKU KÖRLÜĞÜ (B6): %r yakalanmadı — %s" % (metin, neden)


@pytest.mark.parametrize("metin,taraf,neden", [
    ("Davacı işçi kendi isteğiyle ayrılmış, istifa etmiştir.", "davali",
     "işveren vekili için istifa LEHE bir olgudur — alarm üretmemeli"),
    ("İşveren müvekkilimi haksız olarak işten çıkarmıştır.", "davaci",
     "işçi vekili için haksız fesih LEHE bir olgudur — alarm üretmemeli"),
    ("Müşteki şikayetinden vazgeçmemiştir.", "musteki",
     "ceza tarafı iş hukuku kalıplarından etkilenmemeli"),
    ("Sanık isnat edilen suçu kabul etmemektedir.", "sanik",
     "ceza tarafı iş hukuku kalıplarından etkilenmemeli"),
])
def test_b6_taraf_asimetrisi_ters_tarafta_alarm_uretmez(metin, taraf, neden):
    """İş hukuku ekseni TARAF ASİMETRİKTİR ve öyle kalmalıdır.

    Aynı olgu bir tarafta yıkıcı, öbür tarafta müvekkil lehinedir; kalıpları
    her iki sete birden koymak kapıyı gürültüye boğar ve güveni aşındırır
    (yanlış alarm da bir kusurdur)."""
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, "genel", taraf)
    assert not aleyhe, "YANLIŞ ALARM (B6): %r → %r — %s" % (metin, aleyhe, neden)


def test_b6_turkce_morfoloji_capasi():
    """Türkçe çekim, kalıbı sessizce ıskalatır — bu ailenin tekrar eden tuzağı.

    B3'te `-me` eki (olumsuzluk mü, mastar mı) aynı sınıftandı. Burada iki
    ayrı olay var: ÜNLÜ DÜŞMESİ (`fesih` → `feshin`) ve ÜNSÜZ YUMUŞAMASI
    (`sebep` → `sebebe`). İlk yazımda ikisi de kalıbı kaçırıyordu."""
    for metin, taraf in (("Feshin haklı sebebe dayandığı görülmektedir.", "davaci"),
                         ("Fesih haksız olarak gerçekleştirilmiştir.", "davali")):
        for donusum in (lambda x: x, _ocr_bozulmus):
            _e, _d, _o, aleyhe, _n = dd.denetle(donusum(metin), "genel", taraf)
            assert aleyhe, "Türkçe morfoloji kaçağı: %r" % donusum(metin)
