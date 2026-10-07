# -*- coding: utf-8 -*-
"""v0.5.18 — Vitrin V1: tak-çalıştır MASTER PROMPT (Görev 5, 2026-10-07).

AVUKAT TALİMATI (bağlayıcı): "vitrine bakan ajan bu plug in için tek bir master
prompt versin; kolay kurulumu Claude Code için kopyala-yapıştır yapan biri direkt
plug and play yapsın; Yargı Pro haricindeki kısımda — onda ücretli üyelik gerekiyor."

NEDEN VAR: Kurulum anlatımı iki README'de dağınıktı ve kök README'deki eski
prompt dört yerden yanlıştı: (1) Yargı Pro'yu KURMAYA çalışıyordu — ücretli
üyelik kişiye bırakılmalı; (2) paket alt sınırını taşımıyordu
(`pymupdf>=1.24.2`, tek kaynak `belge_guvenlik.PYMUPDF_ASGARI`); (3) ilk çağrı
derlemesini (`compileall`) ve eski `yargi-mcp-yedek` kalıntısını bilmiyordu;
(4) README aynı MCP sunucusunu `claude mcp add … yargipro` ile bir de elle
eklemeyi öneriyordu — eklentinin zaten ilan ettiği uç noktanın İKİNCİ kaydı.

DÜZELTME TURU 1 (bağımsız inceleme, 2026-10-07) dört önemli metin düzeltmesi
getirdi ve bu dosya onları da kilitler: (Ö-1) `PYTHONDONTWRITEBYTECODE` Claude
uygulamasının alt süreçlerine kendisinin verdiği bir değişkendir (User/Machine
kapsamında yok); import .pyc yazmaz, `compileall` YAZAR, var olan .pyc OKUNUR →
derleme KOŞULSUZ, değişkene dokunulmaz, kaldırma önerilmez; (Ö-2) Windows'ta
PATH yalnız kullanıcı kapsamı oku-ekle, `setx PATH` yasak (birleşik PATH'i
kopyalar, 1024 karakterde kırpar), doğrulama tam yolla; Tesseract'ta birincil yol
resmî kurucu (Turkish seçimi), winget ikincil; (Ö-3) macOS/Linux'ta `python3`,
PEP 668 "externally-managed-environment" → `--break-system-packages` yasak;
(Ö-4) güncellemede önce raf tazeleme, sonra eklenti güncelleme.

Bu dosya master prompt'un VARLIĞINI ve TEKLİĞİNİ (tek kaynak: kök README;
plugin README yalnız işaret eder), adım SIRASINI, tek-kaynak sabitlerle
eşitliğini (`PYMUPDF_ASGARI`, `UDF_CLI_SURUM`) ve kurallar bloğunu kilitler;
emek etiketini harfi harfine korur. B-34/B-35 vitrin kapılarının kardeşidir.

Kural: ağsız, deterministik; README'ler METİN olarak okunur, hiçbir kurulum
komutu koşulmaz. Sentetik veri yok — belgenin kendisi denetlenir.
"""
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
KOK_README = REPO / "README.md"
PLUGIN_README = PLUGIN / "README.md"
REQUIREMENTS = REPO / "requirements.txt"
BELGE_GUVENLIK = PLUGIN / "skills" / "oa-ingest" / "scripts" / "belge_guvenlik.py"
UDF_YAZ = PLUGIN / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py"

# Master prompt'un ilk cümlesi — bloğu BULMAK ve TEKLİĞİNİ saymak için ayırt edici.
ILK_SATIR = 'Bu bilgisayara "Ortak Avukat" sistemini uçtan uca kur'
BASLIK_0 = "### 0. Tek yapıştırmayla kurulum"

# Emek etiketi — HARFİ HARFİNE korunur (avukat talimatı). Satır sonu bağımsız.
EMEK_ETIKETI = (
    "> 🙏 **Emek etiketi:** Türk hukuku içtihat/mevzuat erişimini modele açan\n"
    "> **Yargı Pro MCP** — ve daha önce açık kaynak olarak yayımlanan **yargi-mcp** —\n"
    "> [Said Sürücü](https://github.com/saidsurucu)'nün eseridir. Bu sistemin\n"
    "> \"resmî kaynaktan tam metin\" disiplini, onun kurduğu gişeler üzerinde çalışır."
)
GELISTIRICI_PARCASI = "geliştirici: [@saidsurucu](https://github.com/saidsurucu)"


def _oku(p):
    # Metin kipi evrensel satır sonu uygular: CRLF dosya da "\n" ile okunur.
    return p.read_text(encoding="utf-8")


def _master_prompt_blogu(metin=None):
    """`### 0.` başlığından sonraki İLK ```text bloğunun içi."""
    metin = _oku(KOK_README) if metin is None else metin
    bas = metin.find(BASLIK_0)
    assert bas >= 0, "kök README'de '%s' başlığı yok" % BASLIK_0
    fence = metin.find("```text\n", bas)
    assert fence >= 0, "başlıktan sonra ```text bloğu yok"
    ic_bas = fence + len("```text\n")
    son = metin.find("\n```", ic_bas)
    assert son >= 0, "```text bloğu kapanmıyor"
    return metin[ic_bas:son]


def _bolum(metin, bas_isareti, son_isareti):
    bas = metin.find(bas_isareti)
    assert bas >= 0, "bölüm başlığı yok: %r" % bas_isareti
    son = metin.find(son_isareti, bas + len(bas_isareti))
    assert son >= 0, "bölüm sonu yok: %r" % son_isareti
    return metin[bas:son]


def _sirali(metin, parcalar):
    """Her parça metinde VAR ve ilk geçişleri verilen sırada; aksi hâlde assert."""
    konumlar = []
    for parca in parcalar:
        k = metin.find(parca)
        assert k >= 0, "metinde yok: %r" % parca
        konumlar.append(k)
    assert konumlar == sorted(konumlar), "sıra bozuk: %s" % list(zip(parcalar, konumlar))


def _pymupdf_asgari():
    m = re.search(r"^PYMUPDF_ASGARI\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
                  _oku(BELGE_GUVENLIK), re.M)
    assert m, "belge_guvenlik.PYMUPDF_ASGARI okunamadı"
    return ".".join(m.groups())


def _udf_cli_surum():
    m = re.search(r'^UDF_CLI_SURUM\s*=\s*"([^"]+)"', _oku(UDF_YAZ), re.M)
    assert m, "udf_yaz.UDF_CLI_SURUM okunamadı"
    return m.group(1)


# ═══════════════════════════════════════════════════════════════════════════
# Varlık ve TEKLİK — tek kaynak kök README
# ═══════════════════════════════════════════════════════════════════════════

def test_master_prompt_blogu_var_tek_ve_tek_kod_blogu():
    """Kök README'de master prompt: `### 0.` başlığı altında TEK bir ```text
    bloğu; blok içinde iç içe fence yok (kopyala-yapıştır bütünlüğü)."""
    metin = _oku(KOK_README)
    blok = _master_prompt_blogu(metin)
    assert ILK_SATIR in blok, "blok ilk cümleyle başlamıyor"
    assert "```" not in blok, "blok içinde iç içe kod fence'i var — yapıştırma bozulur"
    assert metin.count(ILK_SATIR) == 1, (
        "master prompt kök README'de %d kez geçiyor — TEK olmalı" % metin.count(ILK_SATIR))


def test_plugin_readme_master_prompta_isaret_eder_kopya_tasimaz():
    """plugin README ikinci bir prompt KOPYASI taşımaz (iki yerde iki sürüm
    yaşamasın); kök README'nin kurulum bölümüne bağlantı verir."""
    metin = _oku(PLUGIN_README)
    assert ILK_SATIR not in metin, "plugin README master prompt'un kopyasını taşıyor"
    kurulum = _bolum(metin, "## Kurulum", "## Parça dizini")
    assert "README.md#kurulum" in kurulum, (
        "plugin README kurulum bölümü kök README'nin kurulum bölümüne bağlantı vermiyor")
    assert "master prompt" in kurulum.lower()


# ═══════════════════════════════════════════════════════════════════════════
# Yargı Pro: KURMAZ, YETKİLENDİRMEZ — yalnız durum + talimat
# ═══════════════════════════════════════════════════════════════════════════

def test_master_prompt_yargi_proyu_kurmaz_yetkilendirmez_yalniz_bildirir():
    blok = _master_prompt_blogu()
    assert "ücretli" in blok, "Yargı Pro'nun ücretli üyelik istediği yazılı değil"
    assert "/mcp" in blok, "yetkilendirme yolu (/mcp) kişiye söylenmiyor"
    assert "plugin:ortak-avukat:yargi-pro" in blok, (
        "eklentinin ilan ettiği sunucu adı yazılı değil — kişi /mcp'de neyi arayacağını bilemez")
    assert "teyit YAPILAMADI" in blok, "Pro yoksa içtihadın nasıl işleneceği yazılı değil"
    assert re.search(r"mcp\s+add", blok) is None, "prompt Yargı Pro'yu KURMAYA çalışıyor (mcp add)"
    assert "mcp login" not in blok, "prompt Yargı Pro'yu YETKİLENDİRMEYE çalışıyor (mcp login)"
    assert "--transport" not in blok, "prompt elle MCP kaydı açıyor (--transport)"


def test_master_prompt_yargi_pro_durumu_mcp_panelinden_okunur():
    """K-3: `claude mcp list` eklenti sunucularını göstermeyebilir ve her sunucuya
    ağ sağlık denetimi yapar; durum doğrudan `/mcp` panelinden okunur."""
    blok = _master_prompt_blogu()
    assert "`/mcp` yazdır" in blok, "durum /mcp panelinden okutulmuyor"
    assert re.search(r"claude mcp list[^\n]*koşturma", blok), (
        "`claude mcp list` koşturma yasağı yok (K-3)")


def test_readme_claude_mcp_add_yargipro_onerisi_kalmadi():
    """Eklenti `yargi-pro`'yu plugin.json'da zaten ilan eder; `claude mcp add …
    yargipro` aynı uç noktanın İKİNCİ kaydıdır. İki README'de de kalmamalı."""
    hatalar = []
    for yol in (KOK_README, PLUGIN_README):
        for no, satir in enumerate(_oku(yol).splitlines(), 1):
            if re.search(r"claude\s+mcp\s+add", satir) or "--transport http yargipro" in satir:
                hatalar.append("%s:%d → %s" % (yol.name, no, satir.strip()[:100]))
    assert not hatalar, "elle ikinci MCP kaydı önerisi sürüyor:\n  " + "\n  ".join(hatalar)


def test_readme_yargi_pro_adimi_ucretli_mcp_ile_yetkilendirir_ve_ikinci_kaydi_gerekcelendirir():
    kok = _bolum(_oku(KOK_README), "### 5.", "### 6.")
    for parca in ("ücretli", "/mcp", "plugin:ortak-avukat:yargi-pro", "ikinci"):
        assert parca in kok, "kök README 5. adımda eksik: %r" % parca
    plugin = _bolum(_oku(PLUGIN_README), "## Kurulum", "## Parça dizini")
    for parca in ("ücretli", "/mcp", "plugin:ortak-avukat:yargi-pro"):
        assert parca in plugin, "plugin README kurulum bölümünde eksik: %r" % parca


# ═══════════════════════════════════════════════════════════════════════════
# Tek-kaynak sabitleri: PyMuPDF alt sınırı, udf-cli sürümü
# ═══════════════════════════════════════════════════════════════════════════

def test_master_prompt_pymupdf_alt_siniri_belge_guvenlik_ile_ayni():
    ver = _pymupdf_asgari()
    blok = _master_prompt_blogu()
    assert "pymupdf>=%s" % ver in blok, (
        "master prompt PyMuPDF alt sınırını (%s) taşımıyor" % ver)
    bulunan = set()
    for yol in (KOK_README, PLUGIN_README, REQUIREMENTS):
        bulunan |= set(re.findall(r"pymupdf\s*>=\s*([0-9][0-9.]*[0-9])", _oku(yol), re.I))
    assert bulunan == {ver}, (
        "PyMuPDF alt sınırı AYRIŞTI: belgelerde %s, belge_guvenlik.PYMUPDF_ASGARI %s"
        % (sorted(bulunan), ver))


def test_master_prompt_udf_cli_surumu_sabit_ve_latest_yok():
    ver = _udf_cli_surum()
    blok = _master_prompt_blogu()
    assert "udf-cli@%s" % ver in blok, "master prompt udf-cli sürümünü sabitlemiyor"
    assert "@latest" not in blok
    for yol in (KOK_README, PLUGIN_README):
        metin = _oku(yol)
        surumler = set(re.findall(r"udf-cli@([0-9A-Za-z.\-]+)", metin))
        assert surumler == {ver}, "%s: udf-cli sürümleri %s ≠ %s" % (yol.name, sorted(surumler), ver)
        assert "udf-cli@latest" not in metin


# ═══════════════════════════════════════════════════════════════════════════
# İçerik: sıra, eklenti komutları, derleme, doğrulama, platformlar
# ═══════════════════════════════════════════════════════════════════════════

def test_master_prompt_adim_sirasi_brief_ile_ayni():
    """Önkoşul → eklenti → Python → Tesseract → Node/udf-cli → compileall →
    doğrulama → Yargı Pro DURUMU → eski yedek → özet → TAM kapat."""
    _sirali(_master_prompt_blogu(), [
        "claude --version",
        "claude plugin marketplace add bcancapar-spec/ortak-avukat",
        "pymupdf>=%s" % _pymupdf_asgari(),
        "tesseract --list-langs",
        "udf-cli@%s" % _udf_cli_surum(),
        "compileall",
        "aile_dogrula.py",
        "YARGI PRO DURUMU",
        "yargi-mcp-yedek",
        "ÖZET",
        "TAM KAPATIP",
    ])


def test_master_prompt_eklenti_komutlari_cli_ve_sohbet_yedegi():
    blok = _master_prompt_blogu()
    for parca in ("claude plugin list",
                  "claude plugin marketplace add bcancapar-spec/ortak-avukat",
                  "claude plugin install ortak-avukat@ortak-avukat",
                  "/plugin marketplace add bcancapar-spec/ortak-avukat",
                  "/plugin install ortak-avukat@ortak-avukat"):
        assert parca in blok, "eklenti komutu eksik: %r" % parca


def test_master_prompt_guncelleme_kolu_once_raf_tazeler_sonra_gunceller():
    """Ö-4: üçüncü taraf raflarda otomatik tazeleme KAPALI; `plugin update` tek
    başına "zaten güncel" deyip eski sürümde kalabilir. Prompt ve README
    Güncelleme bölümü: önce `marketplace update`, sonra `plugin update`; sohbet
    yedeği `/plugin marketplace update`."""
    blok = _master_prompt_blogu()
    _sirali(blok, ["claude plugin marketplace update ortak-avukat",
                   "claude plugin update ortak-avukat@ortak-avukat"])
    assert "/plugin marketplace update ortak-avukat" in blok
    guncelleme = _bolum(_oku(KOK_README), "### Güncelleme", "### Sorun giderme")
    _sirali(guncelleme, ["claude plugin marketplace update ortak-avukat",
                         "claude plugin update ortak-avukat@ortak-avukat"])
    assert "/plugin marketplace update ortak-avukat" in guncelleme


def test_master_prompt_ilk_cagri_derlemesi_kosulsuz_ve_degiskene_dokunmaz():
    """Ö-1 (deneyle doğrulandı, 3.12 ve 3.14): `PYTHONDONTWRITEBYTECODE=1`'i Claude
    uygulaması alt süreçlerine KENDİSİ verir (User/Machine kapsamında yok); import
    .pyc yazmaz, `python -m compileall` YAZAR, var olan .pyc OKUNUR. Kancalar kendi
    .pyc'sini yazamadığı için hızlanmanın TEK yolu bu derlemedir ve her güncellemeden
    sonra yinelenir. Prompt: koşulsuz derle; değişkene dokunma; kaldırmayı önerme."""
    blok = _master_prompt_blogu()
    assert "compileall" in blok
    assert "PYTHONDONTWRITEBYTECODE" in blok
    assert "değişkene dokunma" in blok, "prompt değişkene dokunmama kuralını taşımıyor (Ö-1)"
    assert "kaldırmamı öner" not in blok, "prompt değişkenin kaldırılmasını öneriyor — yanlış (Ö-1)"
    assert "boşa gider" not in blok, "prompt derlemenin boşa gittiğini söylüyor — yanlış (Ö-1)"
    adim8 = _bolum(_oku(KOK_README), "### 8.", "### Güncelleme")
    assert "compileall" in adim8
    assert "değişkeni kaldırın" not in adim8, "README 8. adım değişkeni kaldırmayı öneriyor (Ö-1)"
    assert "Değişkene dokunmayın" in adim8


def test_master_prompt_unix_python3_ve_pep668_kirma_yasak():
    """Ö-3: kanca sarmalayıcısının bash kolu `python3`'ü önce arar (run-hook.cmd);
    pip 'externally-managed-environment' derse `--break-system-packages` KULLANILMAZ."""
    blok = _master_prompt_blogu()
    assert "python3" in blok, "macOS/Linux için python3 yok (Ö-3)"
    assert "externally-managed-environment" in blok, "PEP 668 durumu ele alınmıyor (Ö-3)"
    assert re.search(r"--break-system-packages[^\n]*KULLANMA", blok), (
        "--break-system-packages yasağı yok (Ö-3)")


def test_master_prompt_windows_path_yontemi_kullanici_kapsami_setx_yasak():
    """Ö-2: `setx PATH` birleşik PATH'i kullanıcı PATH'ine kopyalar ve 1024
    karakterde sessizce kırpar → yasak. Yöntem: yalnız User kapsamını oku-ekle;
    yeni PATH çalışan oturuma yansımaz → doğrulama tam yolla."""
    blok = _master_prompt_blogu()
    assert "[Environment]::GetEnvironmentVariable('Path','User')" in blok, (
        "kullanıcı kapsamı PATH okuma yöntemi yok (Ö-2)")
    assert "SetEnvironmentVariable(" in blok, "kullanıcı kapsamı PATH yazma yöntemi yok (Ö-2)"
    assert "`setx PATH` KULLANMA" in blok, "setx yasağı yok (Ö-2)"
    assert re.search(r'setx\s+PATH\s+"', blok) is None, "prompt fiilen setx komutu veriyor (Ö-2)"
    assert 'Tesseract-OCR\\tesseract.exe" --list-langs' in blok, (
        "tam yolla doğrulama yok (Ö-2)")


def test_master_prompt_windows_tesseract_birincil_kurucu_ikincil_winget():
    """K-8 ruling (ana oturum): Windows'ta BİRİNCİL yol resmî UB-Mannheim kurucusu
    (kişi Turkish'i seçer; yükseltilmiş çalışır — tessdata kopyası ve yönetici adımı
    gerekmez); winget ikincil (o zaman tur.traineddata resmî tessdata'dan + yönetici)."""
    blok = _master_prompt_blogu()
    _sirali(blok, ["UB-Mannheim/tesseract/wiki",
                   "winget install --id UB-Mannheim.TesseractOCR",
                   "tur.traineddata"])
    assert "Turkish" in blok, "kurucuda Turkish seçimi söylenmiyor"
    assert "BİRİNCİL" in blok and "İKİNCİL" in blok


def test_master_prompt_dosya_kanitiyla_dogrular():
    blok = _master_prompt_blogu()
    for parca in ("20", "skills/", "hooks.json", "plugin.json", "aile_dogrula.py",
                  "claude plugin list"):
        assert parca in blok, "dosya kanıtı ögesi eksik: %r" % parca


def test_master_prompt_tam_kapat_ve_tek_satir_rapor():
    blok = _master_prompt_blogu()
    assert re.search(r"TAM\s+KAPAT", blok, re.I), "'TAM kapatıp açın' hatırlatması yok"
    assert "tek satır" in blok, "her adımın tek satır raporlanması istenmiyor"


@pytest.mark.parametrize("parca", [
    "UB-Mannheim/tesseract/wiki",
    "winget install --id UB-Mannheim.TesseractOCR",
    "brew install tesseract tesseract-lang",
    "tesseract-ocr-tur",
    "tur.traineddata",
])
def test_master_prompt_tesseract_uc_platform_ve_turkce_paket(parca):
    assert parca in _master_prompt_blogu(), "Tesseract/Türkçe paket ögesi eksik: %r" % parca


@pytest.mark.parametrize("parca", [
    "pip show pymupdf",             # K-1: sürüm pip'ten; `import pymupdf` 1.24.3'te geldi
    "import fitz",                  # K-1: her sürümde var olan modül adıyla yoklama
    ".orphaned_at",                 # K-2: eski sürüm klasörü işaretliyse normal (14 gün)
    "--accept-source-agreements",   # K-4: winget kaynak sözleşmesi istemi TTY'siz takılmasın
    "UAC",                          # K-4: kurucuların yönetici penceresi kişinin elinde
    "py -3.14 -m pip",              # K-5: yeni kurulan Python bu oturumda PATH'te değil
    "Python.Python.3.14",           # avukat kararı: yeni kurulumda önerilen sürüm 3.14 (asgari 3.12)
])
def test_master_prompt_duzeltme_turu_1_kucukler(parca):
    assert parca in _master_prompt_blogu(), "düzeltme turu 1 ögesi eksik: %r" % parca


@pytest.mark.parametrize("parca", [
    "şifre, PIN, kart ya da kimlik bilgisi isteme",
    "sudo/yönetici şifresini ben girerim",
    "E-imza ve UYAP",
    "kurulumun parçası DEĞİLDİR",
    "benden onay al",
    "Bulut OCR yok",
    "Müvekkil evrakına dokunma",
    "Yargı Pro'yu kurma",
])
def test_master_prompt_kurallar_blogu(parca):
    """Şifre/PIN/kart istenmez; e-imza ve UYAP girişi kurulumun parçası değil;
    her kurulumdan önce onay; bulut OCR yok; müvekkil evrakına dokunulmaz;
    Yargı Pro kurulmaz. (K-7: kısa alt dizgi yerine ayırt edici cümle parçaları,
    büyük-küçük harf duyarlı — "pin"/"kart" başka sözcüklerde de geçebilirdi.)"""
    assert parca in _master_prompt_blogu(), "kural eksik: %r" % parca


# ═══════════════════════════════════════════════════════════════════════════
# Emek etiketi — harfi harfine
# ═══════════════════════════════════════════════════════════════════════════

def test_emek_etiketi_ve_gelistirici_parcasi_harfi_harfine_korunur():
    metin = _oku(KOK_README)
    assert EMEK_ETIKETI in metin, "emek etiketi dört satırı harfi harfine korunmadı"
    assert metin.count("**Emek etiketi:**") == 1
    assert GELISTIRICI_PARCASI in metin, "gereksinim tablosundaki geliştirici parçası değişti"
