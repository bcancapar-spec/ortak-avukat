# -*- coding: utf-8 -*-
"""2026-10-15 denetimi — KAYNAK HİJYENİ KAPISI (docs/DENETIM-2026-10-15.md B-2, B-3, B-4, B-5).

NEDEN VAR: süit 3.756 yeşilken kaynak kodda iki tanımsız ad (hiç koşmayan bir
dalda), ham çift-yönlü/görünmez Unicode karakterleri ve 35 kullanılmayan import
duruyordu; hiçbir kapı bunları görmüyordu. Ham çift-yönlü karakter, kaynağı
gözle okunandan farklı gösterebilir (Trojan Source sınıfı) — belge güvenlik
kapısının evrakta yakaladığı şeyin, eklentinin kendi kaynağında kapısı yoktu.
README "eklenti metinlerinde ham görünmez karakter yasağı" der; o kural .md
içindi, .py için bu dosya kapıdır.

Üç kilit:
  (a) `ruff.toml` var ve YALNIZ hata sınıfı kuralları seçer — biçim/stil
      kuralı seçilmez: gürültü kapıyı öldürür (447 dersi: sürekli kırmızı
      kapı, olmayan kapıdır).
  (b) CI'da ayrı `lint` işi `ruff check` koşar; ruff sürümü SABİTTİR
      (udf-cli ile aynı gerekçe — kural seti sürümle kaymasın) ve iş
      `test` işine bağlı DEĞİLDİR (bir kapı başka kapının arkasına saklanmaz).
  (c) `plugins/`, `tools/`, `tests/` altındaki `.py` kaynaklarında ham
      Cf-sınıfı (görünmez / çift-yönlü biçim) karakter yok — ruff'tan
      BAĞIMSIZ doğrudan tarama: denetçi de denetlenir, kapı ölü olmasın.
ruff `requirements.txt`'e GİRMEZ: son kullanıcıya geliştirme aracı yüklenmez
(pytest-xdist ile aynı karar). Ağsız; yalnız depo metnini okur. Sentetik veri.
"""
import pathlib
import re
import unicodedata

REPO = pathlib.Path(__file__).resolve().parents[1]
RUFF_TOML = REPO / "ruff.toml"
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
REQUIREMENTS = REPO / "requirements.txt"
KAYNAK_DIZINLER = ("plugins", "tools", "tests")

# Hata sınıfı: sözdizimi, karşılaştırma/format kusurları, tanımsız ad,
# yeniden tanım, kullanılmayan import, yinelenen küme öğesi, pylint hataları
# (ham görünmez/çift-yönlü karakter dahil).
ZORUNLU_KURALLAR = {"E9", "F63", "F7", "F82", "F811", "F401", "B033", "PLE"}
# Biçim/stil aileleri: seçilirse kapı gürültüye boğulur.
YASAK_KURALLAR = {"E", "W", "I", "D", "N", "UP", "E5", "E7", "C90", "ANN", "Q"}


def _oku(p):
    return p.read_text(encoding="utf-8")


def _is_blogu(ci_metni, ad):
    """`jobs:` altındaki 2-boşluk girintili `ad:` işinin gövdesi (sonraki işe kadar)."""
    m = re.search(r"^  %s:\n(.*?)(?=^  \w+:|\Z)" % re.escape(ad), ci_metni, re.M | re.S)
    assert m, "ci.yml'de `%s:` işi yok" % ad
    return m.group(1)


# ── (a) yapılandırma ────────────────────────────────────────────────────────

def test_ruff_yapilandirmasi_var_ve_yalniz_hata_sinifi_secer():
    assert RUFF_TOML.is_file(), "ruff.toml yok — kaynak hijyeni kapısı yapılandırmasız"
    metin = _oku(RUFF_TOML)
    m = re.search(r"^select\s*=\s*\[([^\]]*)\]", metin, re.M)
    assert m, "ruff.toml `select = [...]` satırı yok"
    secilen = set(re.findall(r'"([A-Z]+[0-9]*)"', m.group(1)))
    assert ZORUNLU_KURALLAR <= secilen, "eksik kural: %s" % sorted(ZORUNLU_KURALLAR - secilen)
    assert not (secilen & YASAK_KURALLAR), "biçim kuralı seçilmiş: %s" % sorted(secilen & YASAK_KURALLAR)
    assert 'target-version = "py312"' in metin, "hedef sürüm pyproject ile aynı (3.12) olmalı"
    # Müvekkil evrakı ve ajan worktree'leri taranmaz.
    assert "_oa" in metin and ".claude" in metin, "exclude listesi _oa/ ve .claude/ taşımalı"


# ── (b) CI işi ───────────────────────────────────────────────────────────────

def test_ci_lint_isi_var_surumu_sabit_ve_bagimsiz():
    metin = _oku(CI_YML)
    lint = _is_blogu(metin, "lint")
    assert re.search(r"pip install[^\n]*\bruff==\d+\.\d+\.\d+", lint), (
        "ruff sürümü sabit değil (kural seti sürümle kayar)")
    assert "ruff check" in lint, "lint işi `ruff check` koşmuyor"
    assert "needs:" not in lint, "lint işi başka işe bağlı — kapı kapının arkasına saklanmaz"
    assert "ruff" not in _oku(REQUIREMENTS).lower(), (
        "ruff requirements.txt'e girmiş — son kullanıcıya geliştirme aracı yüklenmez")


def test_ci_basligi_lint_isini_de_anar():
    """`yeşil ne demek` başlığı yeni kapıyı da saymalı — anılmayan kapı görünmezdir."""
    baslik = _oku(CI_YML).split("on:", 1)[0]
    assert "lint" in baslik.lower() or "ruff" in baslik.lower(), (
        "ci.yml başlığı lint işini anmıyor")


# ── (c) ham görünmez / çift-yönlü karakter ─────────────────────────────────

def _ham_cf_satirlari(metin):
    """Satır no + kod noktası: metinde ham Cf (format) karakteri taşıyan satırlar.
    Kaçışlı yazım (`\\u200b`) ham karakter DEĞİLDİR ve yakalanmaz."""
    bulunan = []
    for no, satir in enumerate(metin.splitlines(), 1):
        for ch in satir:
            if unicodedata.category(ch) == "Cf":
                bulunan.append((no, "U+%04X" % ord(ch)))
                break
    return bulunan


def _py_dosyalari():
    for d in KAYNAK_DIZINLER:
        for p in sorted((REPO / d).rglob("*.py")):
            if "__pycache__" not in p.parts:
                yield p


def test_tarama_ham_karakteri_yakalar_kacisli_olani_yakalamaz():
    """Kapı ölü olmasın: ham U+200B ve ham çift-yönlü U+202E yakalanır; aynı
    karakterin kaçışlı yazımı ve düz Türkçe metin yakalanmaz."""
    assert _ham_cf_satirlari("a\u200bb") == [(1, "U+200B")]
    assert _ham_cf_satirlari("x = 'abc'  # \u202e gizli") == [(1, "U+202E")]
    assert _ham_cf_satirlari("RE = re.compile('[\\\\u200b-\\\\u200f]')") == []
    assert _ham_cf_satirlari("hâkim — resmî kaynak; müvekkil") == []


def test_py_kaynaklarinda_ham_gorunmez_veya_cift_yonlu_karakter_yok():
    bulunan = []
    for p in _py_dosyalari():
        for no, kod in _ham_cf_satirlari(p.read_bytes().decode("utf-8", "replace")):
            bulunan.append("%s:%d %s" % (p.relative_to(REPO).as_posix(), no, kod))
    assert bulunan == [], (
        "HAM GÖRÜNMEZ/ÇİFT-YÖNLÜ KARAKTER (B-3) — kaynak gözle okunandan farklı "
        "görünebilir; karakteri `\\uXXXX` kaçışıyla yazın:\n  " + "\n  ".join(bulunan))
