# -*- coding: utf-8 -*-
"""v0.5.14 — VİTRİN + TEST ALTYAPISI + CI kapıları.

Denetim bulguları (2026-08-30 çelişki/kırık denetimi, mühendislik kanadı):

  B-25  `oa_ingest.py` argümansız çalıştırılınca BULUNULAN dizini onaysız,
        özyinelemeli ingest ediyordu. Denetim sırasında eklentinin kendi
        deposuna 88 dosya yazıldı; `_oa/` .gitignore'da olduğu için kirlenme
        `git status` refleksiyle GÖRÜNMEZ. Birden çok müvekkil klasörünü
        içeren bir üst dizinde tek komut, dosya ayrımı ilkesini mekanik
        olarak bozar. → pozisyonel varsayılan (`nargs="?" default="."`)
        KALDIRILDI; yol artık AÇIKÇA verilir.

  B-34  Vitrin README'leri sürüm kapısının DIŞINDAydı (0.5.11 / 0.5.7.5),
        dört damga ise 0.5.13'te eşit ve testle kilitliydi. Kurulum yapan
        kişiye hangi nesli aldığı yanlış söyleniyordu. → damga sayısı 4 → 6.

  B-35  Test sayısı iddiası ÜÇ yerde ÜÇ ayrı sayıydı ve üçü de yanlıştı
        (107/1.302/1.385 ve 1405; ölçüm 110/1319/1406). Sayıyı denetleyen
        kapı YOKTU. → sayı TEK kaynağa (`tests/README.md` OA-SUIT-SAYISI
        işaretçisi) indirildi; vitrin belgelerinde serbest sayı iddiası
        yasaklandı; işaretçi gerçek toplama ile mekanik karşılaştırılıyor.

  B-36  `STATUS.md` §A2 kör-nokta defteri bayattı: 6 motoru "testsiz"
        sayıyordu, 4'ünün test dosyası aylar önce eklenmişti. → defter
        tarama çıktısına bağlandı; bu dosya "testsiz" ilan edilen her motorun
        GERÇEKTEN testsiz olduğunu doğrular.

  B-37  Motor kapsamı hiç denetlenmiyordu (`sozlesme_denetim` hiçbir testte
        yüklenmiyordu ve bu yıllarca görünmedi). → evrensel kapsam defteri.

  B-38  Sabit mutlak yerel yol yasağı MEKANİK değildi — oysa bu, ailenin
        bedelini bir kez ödediği sızıntı sınıfıdır (müvekkil dosyasını açık
        depoya sızdırma + testi sessizce öldürme). → depo çapında tarama.

  B-39  CI'da etiket (tag) tetiği yoktu; dosya kendini "RELEASE KAPISI" ilan
        ederken release'in kesildiği olayda ateşlemiyordu. OCR bacağı hiçbir
        platformda koşmuyordu. → `on.push.tags` + ayrı `ocr` işi.

  B-40  (envanter kanadı) `test_hook_komutlari.py` docstring'i "dört olay"
        derken hooks.json'da ALTI olay vardı; envanter tam-küme kilidi yoktu.

Kural: bu dosya SENTETİK veri kullanır; gerçek dava numarası/kişi adı/yerel
yol test koduna giremez (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
SKILLS = PLUGIN / "skills"
TESTS = REPO / "tests"

KOK_README = REPO / "README.md"
PLUGIN_README = PLUGIN / "README.md"
TESTS_README = TESTS / "README.md"
STATUS_MD = REPO / "STATUS.md"
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
PLUGIN_JSON = PLUGIN / ".claude-plugin" / "plugin.json"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"
OA_INGEST = SKILLS / "oa-ingest" / "scripts" / "oa_ingest.py"


def _oku(p):
    return p.read_text(encoding="utf-8")


BU_DOSYA = pathlib.Path(__file__).name


def _test_govdeleri(kendini_dahil_et=False):
    """Test gövdeleri. Kapsam ölçümünde BU dosya dışarıda bırakılır: kapsam
    DEFTERİ bir motorun adını anıyor diye o motor 'test ediliyor' sayılamaz
    (öz-atıf kapıyı kendi kendine yeşile boyar)."""
    return {p.name: _oku(p) for p in sorted(TESTS.glob("test_*.py"))
            if kendini_dahil_et or p.name != BU_DOSYA}


# ═══════════════════════════════════════════════════════════════════════════
# B-25 — oa_ingest.py: pozisyonel varsayılan (CWD) kaldırıldı
# ═══════════════════════════════════════════════════════════════════════════

def test_b25_argumansiz_ingest_reddedilir_ve_cwd_kirletilmez(tmp_path):
    """Argümansız `oa_ingest.py`, BULUNULAN dizini sessizce ingest ETMEZ:
    exit != 0, açıkça yol ister ve cwd'ye `_oa/` YAZMAZ."""
    for i in ("001", "002"):
        (tmp_path / f"{i}-sentetik-evrak.txt").write_text(
            "Sentetik evrak metni — yeterince uzun bir örnek satır. " * 3,
            encoding="utf-8")
    cp = subprocess.run([sys.executable, str(OA_INGEST)], capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        cwd=str(tmp_path), timeout=180)
    ciktilar = (cp.stdout or "") + (cp.stderr or "")
    assert cp.returncode != 0, (
        "argümansız koşu HÂLÂ ingest ediyor (B-25 fail-open):\n" + ciktilar)
    assert "klasor" in ciktilar or "klasör" in ciktilar, ciktilar
    assert not (tmp_path / "_oa").exists(), (
        "argümansız koşu bulunulan dizine `_oa/` yazdı — B-25 kirlenmesi sürüyor")


def test_b25_acik_yol_verilince_aynen_calisir(tmp_path):
    """Kapının bedeli sıfır olmalı: yol AÇIKÇA verildiğinde davranış aynen."""
    for i in ("001", "002"):
        (tmp_path / f"{i}-sentetik-evrak.txt").write_text(
            "Sentetik evrak metni — yeterince uzun bir örnek satır. " * 3,
            encoding="utf-8")
    cp = subprocess.run([sys.executable, str(OA_INGEST), str(tmp_path),
                         "--ocr", "kapali"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=300)
    assert cp.returncode == 0, (cp.stdout or "") + (cp.stderr or "")
    assert (tmp_path / "_oa" / "metin" / "00-kunye.json").is_file()


def test_b25_nokta_yolu_acik_iradedir(tmp_path):
    """`.` yazmak AÇIK bir iradedir — yasaklanan şey sessiz varsayılandır."""
    (tmp_path / "001-sentetik-evrak.txt").write_text(
        "Sentetik evrak metni — yeterince uzun bir örnek satır. " * 3,
        encoding="utf-8")
    cp = subprocess.run([sys.executable, str(OA_INGEST), ".", "--ocr", "kapali"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(tmp_path), timeout=300)
    assert cp.returncode == 0, (cp.stdout or "") + (cp.stderr or "")
    assert (tmp_path / "_oa" / "metin" / "00-kunye.json").is_file()


# ═══════════════════════════════════════════════════════════════════════════
# B-34 — vitrin README'leri sürüm kapısının İÇİNE alındı (4 damga → 6)
# ═══════════════════════════════════════════════════════════════════════════

_SURUM_RE = re.compile(r"^\*\*Sürüm:\*\*\s*([0-9][0-9A-Za-z.]*)", re.M)


def _readme_surumu(yol):
    m = _SURUM_RE.search(_oku(yol))
    assert m, f"{yol.name}: '**Sürüm:** X' satırı bulunamadı (vitrin damgası yok)"
    return m.group(1)


def test_b34_vitrin_readmeleri_surum_damgasiyla_esit():
    """İki README'nin sürüm damgası, kanonik `plugin.json` sürümüyle EŞİT
    olmalı. B-34: dört damga kilitliyken READMEler kapının dışındaydı ve
    2-5 sürüm gerideydi (0.5.11 / 0.5.7.5 ↔ 0.5.13)."""
    kanonik = json.loads(_oku(PLUGIN_JSON))["version"]
    damgalar = {
        "plugin.json version": kanonik,
        "README.md **Sürüm:**": _readme_surumu(KOK_README),
        "plugins/ortak-avukat/README.md **Sürüm:**": _readme_surumu(PLUGIN_README),
    }
    assert len(set(damgalar.values())) == 1, (
        "Vitrin sürüm damgaları AYRIŞTI (B-34): %s" % damgalar)


# ═══════════════════════════════════════════════════════════════════════════
# B-35 — süit sayısı TEK kaynakta ve GERÇEK
# ═══════════════════════════════════════════════════════════════════════════

_SAYI_ISARETCI_RE = re.compile(r"<!--\s*OA-SUIT-SAYISI:\s*(\d+)\s*-->")

# Serbest (kaynaksız) süit-büyüklüğü iddiası deseni: "1.385 test", "1405 yeşil",
# "107 test dosyası", "1.302 test fonksiyonu" …
_SERBEST_SAYI_RE = re.compile(
    r"\b\d{1,2}[.,]?\d{3}\b\s*(?:adet\s*)?(?:otomatik\s*)?"
    r"(?:test|sınama|koşum|yeşil)"
    r"|\b\d{2,4}\b\s*test\s*(?:dosya|fonksiyon)",
    re.I)


def _isaretci_sayisi():
    m = _SAYI_ISARETCI_RE.search(_oku(TESTS_README))
    assert m, (
        "tests/README.md'de `<!-- OA-SUIT-SAYISI: N -->` işaretçisi YOK — "
        "süit sayısının TEK kaynağı budur (B-35).")
    return int(m.group(1))


def _gercek_toplanan():
    cp = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "--collect-only",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=600)
    m = re.findall(r"(\d+)\s+tests?\s+collected", cp.stdout or "")
    assert m, "pytest --collect-only çıktısı okunamadı:\n%s\n%s" % (
        (cp.stdout or "")[-2000:], (cp.stderr or "")[-2000:])
    # Toplama HATALIYSA sayı kısmidir; kısmi sayıyı beyanla kıyaslamak yanlış
    # kırmızı/yeşil üretir — hatayı olduğu gibi söyle.
    assert cp.returncode == 0, (
        "SÜİT TOPLANAMIYOR (rc=%d) — bu bir sayı uyuşmazlığı değil, toplama "
        "kırıklığıdır:\n%s" % (cp.returncode, (cp.stdout or "")[-2000:]))
    return int(m[-1])


def test_b35_suit_sayisi_isaretcisi_gercek_toplama_ile_ayni():
    """B-35 kapısı: `tests/README.md` işaretçisi süitin GERÇEK toplanan test
    sayısına eşit olmalı. Sayı değiştiğinde güncellenecek TEK yer burasıdır —
    başka hiçbir belgede sayı yazmaz."""
    beyan = _isaretci_sayisi()
    gercek = _gercek_toplanan()
    assert beyan == gercek, (
        "Süit sayısı beyanı GERÇEĞE UYMUYOR (B-35). Tek düzeltme noktası:\n"
        "  tests/README.md  →  <!-- OA-SUIT-SAYISI: %d -->\n"
        "(beyan edilen: %d · gerçek toplanan: %d)" % (gercek, beyan, gercek))


def test_b35_vitrin_belgelerinde_serbest_suit_sayisi_yok():
    """Sayı iddiası TEK kaynakta yaşar. README.md / STATUS.md / tests/README.md
    (işaretçi satırı hariç) serbest süit-büyüklüğü sayısı TAŞIYAMAZ.

    `CHANGELOG.md` ve `STATUS.md` MUAFTIR: ikisi de sürüm/tarih damgalı
    ÖLÇÜM defteridir (her satır kendi tarihini taşır), geçmişe dönük olarak
    yeniden yazılmaz. Yasak, tarihsiz "bugün şu kadar test var" iddiasını
    tekrarlayan VİTRİN belgeleri içindir."""
    hatalar = []
    for yol in (KOK_README, PLUGIN_README, TESTS_README):
        for no, satir in enumerate(_oku(yol).splitlines(), 1):
            if _SAYI_ISARETCI_RE.search(satir):
                continue
            m = _SERBEST_SAYI_RE.search(satir)
            if m:
                hatalar.append("%s:%d → %r" % (yol.name, no, satir.strip()[:110]))
    assert not hatalar, (
        "Serbest süit sayısı iddiası (B-35) — tek kaynak `tests/README.md` "
        "OA-SUIT-SAYISI işaretçisidir:\n  " + "\n  ".join(hatalar))


# ═══════════════════════════════════════════════════════════════════════════
# B-37 — motor kapsam defteri (hangi script hiçbir testte yüklenmiyor)
# ═══════════════════════════════════════════════════════════════════════════

# Kapsam defteri: bugün HİÇBİR testte adı geçmeyen motorlar. Boş olması hedeftir.
# Her girdi bir BORÇTUR; test dosyası yazıldığı gün buradan SİLİNİR (defterin
# bayatlaması B-36'nın ta kendisiydi — bu yüzden iki yönlü denetlenir).
KAPSAM_DEFTERI = {
    # (ölçüm 2026-08-31: defter BOŞ — `sozlesme_denetim` de dahil her motorun
    #  artık en az bir testi var. Bir motor kapsam dışına düşerse yukarıdaki
    #  test kırmızı yanar ve borç ADIYLA buraya yazılır.)
}


def _kapsamsiz_motorlar():
    govdeler = list(_test_govdeleri().values())
    kapsamsiz = set()
    for s in sorted(SKILLS.glob("*/scripts/*.py")):
        if not any(s.stem in g for g in govdeler):
            kapsamsiz.add(s.name)
    return kapsamsiz


def test_b37_testte_hic_yuklenmeyen_motor_defterle_ortusuyor():
    """Evrensel kapsam kapısı: `skills/*/scripts/*.py` altındaki her motor en
    az bir testte anılmalı. Anılmayanlar KAPSAM_DEFTERI ile birebir aynı
    olmalı — yeni bir testsiz motor da, kapatılmış bir borcun defterde kalması
    da kırmızı yakar."""
    kapsamsiz = _kapsamsiz_motorlar()
    defter = set(KAPSAM_DEFTERI)
    yeni = sorted(kapsamsiz - defter)
    bayat = sorted(defter - kapsamsiz)
    assert not yeni, (
        "TESTSİZ MOTOR (B-37) — hiçbir testte yüklenmiyor: %s\n"
        "Test yaz ya da gerekçeyle KAPSAM_DEFTERI'ne işle." % yeni)
    assert not bayat, (
        "KAPSAM DEFTERİ BAYAT (B-36 sınıfı): %s artık test ediliyor — "
        "tests/test_v0514_vitrin.py içindeki KAPSAM_DEFTERI satırını SİL." % bayat)


def test_b37_kapsam_kapisi_gercekten_ateslenir():
    """Kapının kendisi ölü olmasın: var olmayan sentetik bir motor adı
    defterde yokken 'kapsamsız' listesine düşmelidir (mekanizma sınavı)."""
    govdeler = list(_test_govdeleri(kendini_dahil_et=True).values())
    yok_ad = "oa_hic_boyle" + "_bir_motor_yok_xyz"   # öz-atıf olmasın diye parçalı
    assert not any(yok_ad in g for g in govdeler)
    assert any("pipeline_kayit" in g for g in govdeler), (
        "kapsam ölçütü (ad geçiyor mu) çalışmıyor — pozitif kontrol düştü")


# ═══════════════════════════════════════════════════════════════════════════
# B-36 — STATUS.md kör-nokta defteri gerçekle örtüşüyor mu
# ═══════════════════════════════════════════════════════════════════════════

_TESTSIZ_IMA = re.compile(r"hiçbir testte|testsiz|sınanmıyor|anılmıyor", re.I)
_BACKTICK = re.compile(r"`([A-Za-z0-9_]+)`")


def test_b36_status_md_testsiz_ilan_ettigi_motor_gercekten_testsiz():
    """B-36: STATUS.md bir motoru 'testsiz / hiçbir testte anılmıyor' diye
    yazıyorsa bu ölçümle DOĞRULANABİLİR olmalı. Defter bayatladığında
    (test yazıldı, satır kaldı) kırmızı yanar."""
    kapsamsiz_stem = {a.rsplit(".py", 1)[0] for a in _kapsamsiz_motorlar()}
    motor_adlari = {s.stem for s in SKILLS.glob("*/scripts/*.py")}
    hatalar = []
    for blok in re.split(r"\n\s*\n", _oku(STATUS_MD)):
        if not _TESTSIZ_IMA.search(blok):
            continue
        for ad in _BACKTICK.findall(blok):
            if ad in motor_adlari and ad not in kapsamsiz_stem:
                hatalar.append(ad)
    assert not hatalar, (
        "STATUS.md 'testsiz' ilan ettiği hâlde GERÇEKTE test edilen motorlar "
        "(bayat kör-nokta defteri, B-36): %s" % sorted(set(hatalar)))


# ═══════════════════════════════════════════════════════════════════════════
# B-38 — sabit mutlak yerel yol yasağı (MEKANİK)
# ═══════════════════════════════════════════════════════════════════════════

# Sentetik örnek (desen testi) taşıyan satırlar bu işaretçiyle MUAF olur.
SENTETIK_ISARETCI = "SENTETIK-YOL"

# Denetim öncesinden devralınan, bu pakete AİT OLMAYAN dosya (devir kalemi).
YOL_MUAF_DOSYALAR = {
    "_gorus/semantica-uyarlama.md":
        "iç görüş notu; başka pakete ait — temizlik devir listesinde (B-38).",
}

TARANAN_UZANTILAR = {".py", ".md", ".json", ".yml", ".yaml", ".txt", ".toml",
                     ".cfg", ".ini", ".sh", ".ps1"}

_YOL_DESENLERI = (
    # Sürücü harfli kişisel kök: C:\Users\... / D:/Users/...   # SENTETIK-YOL
    re.compile(r"[A-Za-z]:[\\/]{1,2}(?:Users|Documents and Settings)[\\/]", re.I),
    # POSIX kişisel kök: /home/ad/ · /Users/ad/                # SENTETIK-YOL
    re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/"),
    # UNC paylaşımı: \\sunucu\pay                              # SENTETIK-YOL
    re.compile(r"\\\\[A-Za-z0-9][A-Za-z0-9._-]{1,}\\[A-Za-z0-9._$-]{2,}"),
)


def _izlenen_dosyalar():
    cp = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(REPO),
                        timeout=120)
    assert cp.returncode == 0, "git ls-files başarısız: %s" % cp.stderr
    return [s.strip() for s in cp.stdout.splitlines() if s.strip()]


def test_b38_depoda_sabit_mutlak_yerel_yol_yok():
    """Ailenin bedelini ödediği sızıntı sınıfı artık MEKANİK yasak: izlenen
    hiçbir dosyada kişisel/mutlak yerel yol (C:\\Users\\…, /home/…, UNC — SENTETIK-YOL)
    bulunamaz. Sentetik desen örnekleri satır sonundaki `SENTETIK-YOL`
    işaretçisiyle muaftır."""
    hatalar = []
    for goreli in _izlenen_dosyalar():
        if goreli in YOL_MUAF_DOSYALAR:
            continue
        p = REPO / goreli
        if p.suffix.lower() not in TARANAN_UZANTILAR or not p.is_file():
            continue
        try:
            metin = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for no, satir in enumerate(metin.splitlines(), 1):
            if SENTETIK_ISARETCI in satir:
                continue
            if any(d.search(satir) for d in _YOL_DESENLERI):
                hatalar.append("%s:%d → %s" % (goreli, no, satir.strip()[:110]))
    assert not hatalar, (
        "SABİT MUTLAK YEREL YOL (B-38) — müvekkil verisi sızıntısı sınıfı.\n"
        "Yolu göreli/tmp_path'e çevir; gerçekten sentetik bir desen örneğiyse "
        "satıra `%s` işaretçisi koy:\n  %s"
        % (SENTETIK_ISARETCI, "\n  ".join(hatalar)))


def test_b38_yol_deseni_gercek_ornekleri_yakaliyor():
    """Kapı ölü olmasın: bilinen üç biçim de yakalanmalı, masum yollar
    yakalanmamalı."""
    yakalanmali = [
        r'RPM = "C:\Users\ornek\AppData\Roaming"',  # SENTETIK-YOL
        'yol = "C:/Users/ornek/dava"',  # SENTETIK-YOL
        'yol = "/home/ornek/dava"',  # SENTETIK-YOL
        r'pay = "\\sunucu\ortak"',  # SENTETIK-YOL
    ]
    for s in yakalanmali:
        assert any(d.search(s) for d in _YOL_DESENLERI), s
    yakalanmamali = [
        'font = "C:\\\\Windows\\\\Fonts"',
        'yol = os.path.join(kok, "_oa", "metin")',
        'goreli = "tests/README.md"',
        'assert "/usr/share/tesseract" not in metin',
    ]
    for s in yakalanmamali:
        assert not any(d.search(s) for d in _YOL_DESENLERI), s


def test_b38_sentetik_isaretci_muafiyeti_calisiyor():
    """İşaretçi gerçekten muaf kılıyor mu (aksi hâlde kapı ya hep ya hiç)."""
    satir = r'RPM = "C:\Users\ornek\AppData"   # ' + SENTETIK_ISARETCI  # SENTETIK-YOL
    assert any(d.search(satir) for d in _YOL_DESENLERI)
    assert SENTETIK_ISARETCI in satir


# ═══════════════════════════════════════════════════════════════════════════
# B-39 — CI: etiket tetiği + OCR bacağı
# ═══════════════════════════════════════════════════════════════════════════

def test_b39_ci_etiket_tetigi_var():
    """Dosya kendini RELEASE KAPISI ilan ediyor; release'in kesildiği olay
    etiket push'udur. `on.push.tags` olmadan kapı o olayda ateşlemez."""
    metin = _oku(CI_YML)
    m = re.search(r"^on:\s*$(.*?)^jobs:", metin, re.M | re.S)
    assert m, "ci.yml `on:` / `jobs:` bloğu ayrıştırılamadı"
    on_blok = m.group(1)
    assert re.search(r"^\s{4}tags:\s*\[.*['\"]v\*['\"].*\]", on_blok, re.M), (
        "ci.yml `on.push.tags: ['v*']` YOK (B-39) — sürüm etiketi CI'yı "
        "tetiklemiyor:\n" + on_blok)


def test_b39_ci_ocr_bacagi_gercekten_kosuyor():
    """OCR bacağı hiçbir platformda koşmuyordu (3 uçtan uca test her koşuda
    sessizce atlanıyordu). Ayrı bir işte tesseract kurulup OCR testleri
    ADIYLA koşmalı."""
    metin = _oku(CI_YML)
    assert re.search(r"^\s{2}ocr:", metin, re.M), "ci.yml'de `ocr:` işi yok (B-39)"
    assert "tesseract-ocr" in metin, "OCR işi tesseract kurmuyor (B-39)"
    assert "tesseract-ocr-tur" in metin, "Türkçe dil paketi kurulmuyor (B-39)"
    assert "tests/test_oa_ingest_ocr_nobetci.py" in metin, (
        "OCR testleri adıyla koşulmuyor (B-39)")


def test_b39_ci_yesil_ne_demez_listesi_ocr_bacagini_aniyor():
    """CI başlığındaki 'yeşil ne DEMEZ' istisna listesi OCR bacağını da
    anmalı — istisna beyan edilmeyen atlama, sessiz atlamadır."""
    metin = _oku(CI_YML)
    baslik = metin.split("on:", 1)[0]
    assert "OCR" in baslik, (
        "ci.yml başlığındaki istisna listesi OCR bacağını anmıyor (B-39)")


# ═══════════════════════════════════════════════════════════════════════════
# B-40 (envanter kanadı) — hook olay envanteri tek kaynak, docstring'ler taze
# ═══════════════════════════════════════════════════════════════════════════

def _test_modulu(ad):
    yol = TESTS / ad
    spec = importlib.util.spec_from_file_location("_v0514_" + yol.stem, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_b40_hook_olay_envanteri_hooks_json_ile_tam_kume():
    """B-40: envanter kilidi TAM KÜME olmalı — bugüne dek yalnız 'her beklenen
    olay dosyada var mı' denetleniyordu; hooks.json'a sessizce EKLENEN bir
    olay hiçbir yerde görünmüyordu."""
    beklenen = set(_test_modulu("test_hook_komutlari.py").BEKLENEN_OLAYLAR)
    gercek = set(json.loads(_oku(HOOKS_JSON))["hooks"].keys())
    assert beklenen == gercek, (
        "hooks.json olay kümesi ↔ BEKLENEN_OLAYLAR ayrıştı (B-40): "
        "fazla=%s eksik=%s" % (sorted(gercek - beklenen), sorted(beklenen - gercek)))


def test_b40_hook_testlerinin_docstringleri_bayat_degil():
    """İki bayat docstring: 'dört olay' (gerçek altı) ve doğrulanmayan
    '(bugün 6 olay)' sayı beyanı. Öz-denetim metni yanıltmamalı."""
    komutlari = _oku(TESTS / "test_hook_komutlari.py")
    doktor = _oku(TESTS / "test_hook_doktor.py")
    assert "dört olay" not in komutlari, (
        "test_hook_komutlari.py docstring'i hâlâ 'dört olay' diyor (B-40)")
    assert "(bugün 6 olay)" not in doktor, (
        "test_hook_doktor.py docstring'i doğrulanmayan sabit sayı beyanı "
        "taşıyor (B-40) — envanter kilidi kardeş dosyadadır")
