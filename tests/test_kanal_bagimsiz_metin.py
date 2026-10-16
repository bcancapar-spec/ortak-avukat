# -*- coding: utf-8 -*-
"""2026-10-15 avukat kararı — CANLI METİNLERDE ÜÇÜNCÜ TARAF TEYİT SUNUCUSU ANMASI YOK.

NEDEN VAR: içtihat/mevzuat teyidi tek bir ticari MCP sunucusuna bağlıydı ve adı
138 dosyada geçiyordu. Karar: ilan kaldırıldı, teyit kanalı resmî portal beyaz
listesi oldu (tests/test_teyit_kanali.py) ve canlı metinler kanal-bağımsız
yazıldı — "resmî kaynaktan teyit", "resmî portal", "web aracı". Bu kapı, o adın
(ve eski açık kaynak yedek projesinin) canlı metne geri sızmasını önler.

TARİHLİ KAYITLAR MUAFTIR (avukat talimatı: "tarihli kayıtlara dokunma"):
CHANGELOG.md, docs/arsiv/**, _gorus/**, her parçanın references/degisiklik-gunlugu.md
dosyası, tarihli belgeler (docs/YARGI-PRO-UYARLAMA-PLANI.md, docs/SURUM-0.6.0-YETENEKLER.md,
docs/DENETIM-2026-10-15.md, docs/YARGI-PRO-BOSLUK-ANALIZI-2026-10-15.md), docs/heyet/**
(2026-10-16 tarihli heyet koşumu raporları — o günkü açık işi adıyla anar). STATUS.md ve
YOL-HARITASI.md tarihli bölümler taşıdığı için mekanik taramadan muaftır; güncel
"DURUM — son" bölümleri elle temiz tutulur. Kilit testleri (bu dosya, test_teyit_kanali,
test_v0518_mcp_ilan) yasaklanan adı/adresi yasak-dize OLARAK taşır; muaftır. Tarihli iki
belgenin dosya ADI (`YARGI-PRO-UYARLAMA-PLANI`, `YARGI-PRO-BOSLUK-ANALIZI`) canlı metinde
bağlantı hedefi olarak geçebilir — desen o iki adı dışlar (bağlantı kapısı hedefi ister).
Ağsız; yalnız izlenen dosyaları okur.
"""
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
UZANTILAR = {".md", ".py", ".json", ".yml", ".yaml", ".toml", ".txt", ".cmd", ".ps1"}
MUAF_DOSYALAR = {
    "CHANGELOG.md", "STATUS.md", "YOL-HARITASI.md",
    "docs/YARGI-PRO-UYARLAMA-PLANI.md", "docs/SURUM-0.6.0-YETENEKLER.md",
    "docs/DENETIM-2026-10-15.md", "docs/YARGI-PRO-BOSLUK-ANALIZI-2026-10-15.md",
    "tests/test_kanal_bagimsiz_metin.py", "tests/test_teyit_kanali.py",
    "tests/test_v0518_mcp_ilan.py",
}
MUAF_ONEKLER = ("docs/arsiv/", "_gorus/", "docs/heyet/")
# Ticari sunucu adı (yazım türevleri), uç nokta alan adı ve eski açık kaynak yedek proje adı.
DESEN = re.compile(r"yarg[ıi]\s*pro\b|yargipro|yargi-pro(?!-uyarlama-plani|-bosluk-analizi)|betaspacestudio|yargi-mcp", re.I)


def _izlenen():
    cp = subprocess.run(["git", "ls-files"], capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(REPO), timeout=120)
    assert cp.returncode == 0, cp.stderr
    return [s.strip() for s in cp.stdout.splitlines() if s.strip()]


def _taranir(goreli):
    if goreli in MUAF_DOSYALAR or goreli.startswith(MUAF_ONEKLER):
        return False
    if goreli.endswith("/degisiklik-gunlugu.md"):
        return False
    return pathlib.PurePosixPath(goreli).suffix.lower() in UZANTILAR


def test_desen_gercek_anmayi_yakalar_masum_metni_yakalamaz():
    """Kapı ölü olmasın: yazım türevleri yakalanır; 'yargı' ve 'profesyonel' tek başına
    yakalanmaz, Yargıtay / UYAP / Bedesten gibi resmî kaynak adları hiç yakalanmaz."""
    for s in ("Yargı Pro", "yargi pro", "YargıPRO", "plugin:ortak-avukat:yargi-pro",
              "https://yargi.betaspacestudio.com/mcp", "yargi-mcp-yedek"):
        assert DESEN.search(s), s
    for s in ("Yargıtay 4. HD kararı", "profesyonel", "yargı kolu", "UYAP Emsal",
              "Bedesten", "resmî kaynak beyaz listesi", "yargılama",
              "[plan](docs/YARGI-PRO-UYARLAMA-PLANI.md)",   # tarihli belgenin adı
              "docs/YARGI-PRO-BOSLUK-ANALIZI-2026-10-15.md"):
        assert not DESEN.search(s), s


def test_canli_metinlerde_ucuncu_taraf_sunucu_anmasi_yok():
    bulunan = []
    for goreli in _izlenen():
        if not _taranir(goreli):
            continue
        p = REPO / goreli
        if not p.is_file():
            continue
        try:
            metin = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for no, satir in enumerate(metin.splitlines(), 1):
            if DESEN.search(satir):
                bulunan.append("%s:%d → %s" % (goreli, no, satir.strip()[:100]))
    assert bulunan == [], (
        "Canlı metinde üçüncü taraf teyit sunucusu anması (2026-10-15 kararı) — "
        "kanal-bağımsız yazın ('resmî kaynaktan teyit', 'resmî portal'); tarihli kayıt "
        "ise MUAF listesine gerekçesiyle ekleyin:\n  " + "\n  ".join(bulunan[:80])
        + ("\n  … (+%d)" % (len(bulunan) - 80) if len(bulunan) > 80 else ""))
