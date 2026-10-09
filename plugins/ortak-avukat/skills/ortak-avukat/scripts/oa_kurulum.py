# -*- coding: utf-8 -*-
"""Ortak Avukat — kurulum denetimi ve tamamlayıcısı (tek prompt'luk zincirin proje içindeki motoru).

NEDEN VAR: avukat talimatı (Av. Bayram Can ÇAPAR, 2026-10-07) — "projenin içerisinde mutlaka
zincirleme şekilde, Yargı Pro hariç kalan tüm gereksinimleri tek prompt'ta indirecek kısmı
oluştur". README'deki tek yapıştırmalık prompt kurulumu Claude'a yürütür; bu motor zincirin
KANIT halkasıdır: gereksinimleri deterministik olarak denetler, eksik olanın resmî kurulum
komutunu basar, yalnız güvenli iki işi kendisi yapar (koşan yorumlayıcıya pip paketleri ve
compileall). Sistem yazılımını (Python, Tesseract, Node) KURMAZ — komutunu basar; kurulumu
avukatın onayıyla Claude yürütür. Yargı Pro KAPSAM DIŞIDIR (ücretli üyelik; /mcp ile avukat
yetkilendirir) — motor onu ne yapılandırır ne ağdan yoklar.

Zincir: prompt → eklenti kurulur → bu motor (denetim) → EKSİK satırının komutu (onayla) →
motor yeniden → Yargı Pro hariç hepsi TAMAM.

Kullanım (kancaların kullandığı yorumlayıcıyla: Windows `python`, macOS/Linux `python3`):
  python oa_kurulum.py                 # denetle — salt okur, ağsız
  python oa_kurulum.py --uygula        # pip paketleri + compileall, sonra yeniden denetle
  python oa_kurulum.py --json <yol>    # deterministik rapor da yaz
Çıkış: 0 = zorunlular TAMAM · 1 = eksik var · 2 = kullanım hatası (argparse).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import importlib.metadata
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

BETIK = pathlib.Path(__file__).resolve()
EKLENTI_KOKU = BETIK.parents[3]          # <kök>/skills/ortak-avukat/scripts/oa_kurulum.py
BEKLENEN_PARCA = 20
ASGARI_PYTHON = (3, 12)
ONERILEN_PYTHON = (3, 14)
WINDOWS_TESSERACT = pathlib.Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
# `markitdown[all]` ekinin Office dönüştürücüleri (markitdown 0.1.8 bağımlılık bildirimiyle doğrulandı):
# .docx → mammoth, .xlsx → openpyxl, .pptx → python-pptx (README "Office evrakı" satırı).
MARKITDOWN_OFIS_EKLERI = ("mammoth", "openpyxl", "python-pptx")

TAMAM, EKSIK, ELIMDE, BILGI = "TAMAM", "EKSİK", "ELİMDE", "BİLGİ"
_SURUM_KLASORU = re.compile(r"^\d+(\.\d+)+$")


# ── sistem sondaları (testlerde sahtelenir; ağ yok) ─────────────────────────────────

def _platform():
    return sys.platform


def _python_surumu():
    return tuple(sys.version_info[:3])


def _paket_surumu(ad):
    try:
        return importlib.metadata.version(ad)
    except importlib.metadata.PackageNotFoundError:
        return None


def _guvenli_which(ad):
    """Programı PATH'ten çözer; ÇALIŞMA DİZİNİNDEKİ bir dosyayı asla seçmez.

    NEDEN VAR (v0.5.18 Fable denetimi): Windows'ta `shutil.which`, NoDefaultCurrentDirectoryInExePath
    tanımlı değilse aramaya çalışma dizinini öne koyar. Araçlar dava kökünde koşar; karşı tarafın
    evrakıyla gelen bir `npx.cmd` / `tesseract.bat` / `node.bat` çalıştırılabilirdi. Değişken bu süreç
    ve çocukları için tanımlanır; PATH'e '.' konmuş olsa bile çalışma dizinindeki sonuç reddedilir.
    Açık yol verilmişse (dizin bileşeni var) kullanıcının seçimine dokunulmaz. Dört betikte
    (udf_yaz, udf_metin, oa_ingest, oa_kurulum) özdeştir — testle kilitli."""
    os.environ.setdefault("NoDefaultCurrentDirectoryInExePath", "1")
    yol = shutil.which(ad)
    if yol and not os.path.dirname(ad) and os.path.exists(yol):
        if (os.path.normcase(os.path.dirname(os.path.abspath(yol)))
                == os.path.normcase(os.path.abspath(os.getcwd()))):
            return None
    return yol


def _komut_bul(ad):
    return _guvenli_which(ad)


def _dosya_var(yol):
    return pathlib.Path(yol).is_file()


def _calistir(argv, zaman_asimi=60):
    """Yerel bir komutu koşturur: (çıkış kodu, stdout+stderr). Bulunamazsa 127."""
    try:
        p = subprocess.run([str(x) for x in argv], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=zaman_asimi)
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, "zaman aşımı (%d sn)" % zaman_asimi
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _pyc_taze(kaynak):
    """Python'un import sırasında yaptığı başlık doğrulamasının aynısı: sihirli sayı, bayrak,
    kaynak mtime ve boyutu. Bayat ya da yok → False (kanca her ateşlemede yeniden derler)."""
    kaynak = pathlib.Path(kaynak)
    pyc = pathlib.Path(importlib.util.cache_from_source(str(kaynak)))
    try:
        baslik = pyc.read_bytes()[:16]
        st = kaynak.stat()
    except OSError:
        return False
    if len(baslik) < 16 or baslik[:4] != importlib.util.MAGIC_NUMBER:
        return False
    bayrak = int.from_bytes(baslik[4:8], "little")
    if bayrak & 0b1:                 # karma tabanlı (SOURCE_DATE_EPOCH ile compileall üretir)
        if not bayrak & 0b10:        # denetimsiz karma: Python da kaynağa bakmaz
            return True
        try:
            return baslik[8:16] == importlib.util.source_hash(kaynak.read_bytes())
        except OSError:
            return False
    return (int.from_bytes(baslik[8:12], "little") == (int(st.st_mtime) & 0xFFFFFFFF)
            and int.from_bytes(baslik[12:16], "little") == (st.st_size & 0xFFFFFFFF))


# ── tek kaynaktan okunan sabitler (kopyalanmaz) ─────────────────────────────────────

def _sabit_oku(yol, desen):
    try:
        m = re.search(desen, pathlib.Path(yol).read_text(encoding="utf-8"), re.M)
    except OSError:
        return None
    return m.groups() if m else None


def _pymupdf_asgari(kok):
    g = _sabit_oku(kok / "skills" / "oa-ingest" / "scripts" / "belge_guvenlik.py",
                   r"^PYMUPDF_ASGARI\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")
    return ".".join(g) if g else None


def _udf_cli_surumu(kok):
    g = _sabit_oku(kok / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py",
                   r'^UDF_CLI_SURUM\s*=\s*"([^"]+)"')
    return g[0] if g else None


def _surum_demeti(metin):
    return tuple(int(x) for x in re.findall(r"\d+", str(metin))[:3])


def _py():
    return '"%s"' % sys.executable


# ── adımlar ──────────────────────────────────────────────────────────────────────────

def _adim(anahtar, ad, durum, ayrinti, komut=""):
    return {"anahtar": anahtar, "ad": ad, "durum": durum, "ayrinti": ayrinti, "komut": komut}


def _python_adimi():
    s = _python_surumu()
    yazim = ".".join(str(x) for x in s)
    if s[:2] < ASGARI_PYTHON:
        komut = ("winget install --id Python.Python.3.14 -e --source winget --accept-source-agreements"
                 if _platform() == "win32" else "https://www.python.org/downloads/ (ya da dağıtımın paket yöneticisi)")
        return _adim("python", "Python", EKSIK, "%s — en az 3.12 gerekir, 3.14 önerilir" % yazim, komut)
    not_ = "önerilen sürüm" if s[:2] >= ONERILEN_PYTHON else "yeterli; önerilen 3.14"
    return _adim("python", "Python", TAMAM, "%s (%s)" % (yazim, not_))


def _pip_adimi(kok):
    asgari = _pymupdf_asgari(kok)
    if asgari is None:
        return _adim("pip_paketleri", "Python paketleri", EKSIK,
                     "PyMuPDF alt sınırı tek kaynaktan (belge_guvenlik.py) okunamadı — eklenti eksik/bozuk")
    istenen = (("pymupdf", '"pymupdf>=%s"' % asgari, _surum_demeti(asgari)),
               ("pillow", "pillow", None),
               ("markitdown", '"markitdown[all]"', None))
    eksik, durumlar = [], []
    for ad, belirtec, alt in istenen:
        surum = _paket_surumu(ad)
        if surum is None:
            eksik.append(belirtec)
            durumlar.append("%s yok" % ad)
        elif alt is not None and _surum_demeti(surum) < alt:
            eksik.append(belirtec)
            durumlar.append("%s %s < %s" % (ad, surum, asgari))
        else:
            durumlar.append("%s %s" % (ad, surum))
    # Fable denetimi P3 (2026-10-08): README Office evrakı için `markitdown[all]` ister; düz
    # `markitdown` .docx/.xlsx/.pptx dönüştürücülerini getirmez. Paket varken ekler yoksa aynı
    # pip komutu (idempotent) eksikleri tamamlar.
    if _paket_surumu("markitdown") is not None:
        eksik_ek = [ek for ek in MARKITDOWN_OFIS_EKLERI if _paket_surumu(ek) is None]
        if eksik_ek:
            eksik.append('"markitdown[all]"')
            durumlar.append("markitdown[all] ekleri yok (%s)" % ", ".join(eksik_ek))
    if eksik:
        return _adim("pip_paketleri", "Python paketleri", EKSIK, "; ".join(durumlar),
                     "%s -m pip install %s   (ya da: oa_kurulum.py --uygula)" % (_py(), " ".join(eksik)))
    return _adim("pip_paketleri", "Python paketleri", TAMAM, "; ".join(durumlar))


def _tesseract_adimi():
    plat = _platform()
    yol, ayrinti_ek = _komut_bul("tesseract"), ""
    if yol is None and plat == "win32" and _dosya_var(WINDOWS_TESSERACT):
        yol, ayrinti_ek = str(WINDOWS_TESSERACT), " — PATH'te değil, standart yolda bulundu (PATH'e kullanıcı kapsamında eklenmeli)"
    if yol is None:
        komut = {"win32": "winget install --id UB-Mannheim.TesseractOCR -e --source winget --accept-source-agreements"
                          " (ya da resmî UB-Mannheim kurucusu: https://github.com/UB-Mannheim/tesseract/wiki —"
                          " kurulumda Turkish dil verisini seçin)",
                 "darwin": "brew install tesseract tesseract-lang"}.get(
                     plat, "sudo apt-get install tesseract-ocr tesseract-ocr-tur")
        return _adim("tesseract", "Tesseract OCR + Türkçe (yerel; bulut OCR yok)", EKSIK, "tesseract bulunamadı", komut)
    kod, cikti = _calistir([yol, "--list-langs"])
    diller = {s.strip() for s in cikti.splitlines()}
    if kod != 0 or "tur" not in diller:
        komut = {"win32": "resmî tessdata deposundan tur.traineddata → C:\\Program Files\\Tesseract-OCR\\tessdata"
                          " (https://github.com/tesseract-ocr/tessdata/raw/main/tur.traineddata; yönetici onayı)",
                 "darwin": "brew install tesseract-lang"}.get(plat, "sudo apt-get install tesseract-ocr-tur")
        return _adim("tesseract", "Tesseract OCR + Türkçe (yerel; bulut OCR yok)", EKSIK,
                     "tur dil verisi yok (Türkçe evrak doğru okunmaz)" + ayrinti_ek, komut)
    return _adim("tesseract", "Tesseract OCR + Türkçe (yerel; bulut OCR yok)", TAMAM, "tur var" + ayrinti_ek)


def _node_adimi():
    node, npx = _komut_bul("node"), _komut_bul("npx")
    if node is None or npx is None:
        komut = {"win32": "winget install --id OpenJS.NodeJS.LTS -e --source winget --accept-source-agreements",
                 "darwin": "brew install node"}.get(_platform(), "https://nodejs.org (LTS) ya da dağıtımın paket yöneticisi")
        return _adim("node", "Node.js + npx (UDF üretimi)", EKSIK,
                     "%s bulunamadı" % ("node" if node is None else "npx"), komut)
    kod, cikti = _calistir([node, "--version"])
    return _adim("node", "Node.js + npx (UDF üretimi)", TAMAM, cikti.strip() or "node var")


def _udf_cli_adimi(kok):
    surum = _udf_cli_surumu(kok)
    if surum is None:
        return _adim("udf_cli", "udf-cli girişi", EKSIK,
                     "udf-cli sürümü tek kaynaktan (udf_yaz.py) okunamadı — eklenti eksik/bozuk")
    paket = "udf-cli@" + surum
    return _adim("udf_cli", "udf-cli girişi", ELIMDE,
                 "ağ ve oturum ister; motor ağa çıkmaz — siz doğrulayın (sürüm sabit: %s)" % surum,
                 "npx -y %s whoami   (giriş yoksa: npx -y %s login — tarayıcıda siz onaylarsınız)" % (paket, paket))


def _eklenti_adimi(kok):
    pj = kok / ".claude-plugin" / "plugin.json"
    try:
        surum = json.loads(pj.read_text(encoding="utf-8")).get("version")
    except (OSError, ValueError):
        return _adim("eklenti", "Eklenti bütünlüğü", EKSIK, "plugin.json okunamadı: %s" % pj)
    if (kok / ".orphaned_at").exists():
        return _adim("eklenti", "Eklenti bütünlüğü", EKSIK,
                     "bu klasör yetim (.orphaned_at) eski sürüm %s — etkin sürüm klasöründen koşun "
                     "(`claude plugin list` → Version)" % surum)
    if _SURUM_KLASORU.match(kok.name) and kok.name != surum:
        return _adim("eklenti", "Eklenti bütünlüğü", EKSIK,
                     "sürüm klasörü %s ama plugin.json %s — kurulum yarım/karışık" % (kok.name, surum))
    parcalar = sorted(p.name for p in (kok / "skills").iterdir()
                      if (p / "SKILL.md").is_file()) if (kok / "skills").is_dir() else []
    try:
        olaylar = json.loads((kok / "hooks" / "hooks.json").read_text(encoding="utf-8")).get("hooks") or {}
    except (OSError, ValueError):
        olaylar = {}
    if len(parcalar) != BEKLENEN_PARCA or not olaylar:
        return _adim("eklenti", "Eklenti bütünlüğü", EKSIK,
                     "%d parça (beklenen %d); hooks/hooks.json %s" % (
                         len(parcalar), BEKLENEN_PARCA, "%d olay" % len(olaylar) if olaylar else "yok ya da boş"))
    yer = "sürüm klasörü" if _SURUM_KLASORU.match(kok.name) else "depo kopyası"
    return _adim("eklenti", "Eklenti bütünlüğü", TAMAM,
                 "sürüm %s (%s) · %d parça · %d kanca olayı" % (surum, yer, len(parcalar), len(olaylar)))


def _derleme_adimi(kok):
    kaynaklar = sorted(kok.glob("skills/*/scripts/*.py")) + sorted(kok.glob("hooks/*.py"))
    bayat = [k for k in kaynaklar if not _pyc_taze(k)]
    if not kaynaklar:
        return _adim("derleme", "İlk çağrı derlemesi (.pyc)", EKSIK, "derlenecek betik bulunamadı")
    if bayat:
        return _adim("derleme", "İlk çağrı derlemesi (.pyc)", EKSIK,
                     "%d/%d betiğin .pyc'si yok ya da bayat — kancalar her ateşlemede yeniden derler. "
                     "PYTHONDONTWRITEBYTECODE ortamda olsa bile derleyin; değişkene dokunmayın "
                     "(Claude uygulaması verir; compileall yine yazar)" % (len(bayat), len(kaynaklar)),
                     '%s -m compileall -q "%s"   (ya da: oa_kurulum.py --uygula)' % (_py(), kok))
    return _adim("derleme", "İlk çağrı derlemesi (.pyc)", TAMAM, "%d betik derli ve taze" % len(kaynaklar))


def _aile_adimi(kok):
    betik = kok / "skills" / "oa-usta" / "scripts" / "aile_dogrula.py"
    kod, cikti = _calistir([sys.executable, betik, kok / "skills"], zaman_asimi=120)
    if kod == 0 and "AİLE YAPI DENETİMİ TEMİZ" in cikti:
        return _adim("aile", "Aile yapı denetimi", TAMAM, "AİLE YAPI DENETİMİ TEMİZ")
    ilk = next((s.strip() for s in cikti.splitlines() if s.strip()), "çıktı yok")
    return _adim("aile", "Aile yapı denetimi", EKSIK, "çıkış %s — %s" % (kod, ilk[:200]),
                 '%s "%s" "%s"' % (_py(), betik, kok / "skills"))


def _yargi_pro_adimi():
    return _adim("yargi_pro", "Yargı Pro (içtihat/mevzuat teyidi)", BILGI,
                 "KAPSAM DIŞI — ücretli üyelik gerektirir; motor kurmaz, yetkilendirmez, ağdan yoklamaz. "
                 "Üyelik yoksa sistem çalışır, içtihat 'teyit YAPILAMADI' damgasıyla işlenir",
                 "/mcp → plugin:ortak-avukat:yargi-pro → Authenticate (tarayıcıda siz onaylarsınız)")


def denetle(kok=None):
    kok = pathlib.Path(kok) if kok is not None else EKLENTI_KOKU
    adimlar = [_python_adimi(), _pip_adimi(kok), _tesseract_adimi(), _node_adimi(),
               _udf_cli_adimi(kok), _eklenti_adimi(kok), _derleme_adimi(kok),
               _aile_adimi(kok), _yargi_pro_adimi()]
    for i, a in enumerate(adimlar, 1):
        a["no"] = i
    return adimlar


def cikis_kodu(adimlar):
    return 1 if any(a["durum"] == EKSIK for a in adimlar) else 0


def rapor_bas(adimlar):
    for a in adimlar:
        satir = "%d) %s — %s (%s)" % (a["no"], a["ad"], a["durum"], a["ayrinti"])
        if a["komut"]:
            satir += " → " + a["komut"]
        print(satir)
    if cikis_kodu(adimlar):
        print("SONUÇ: EKSİK VAR — her EKSİK satırının komutunu avukatın onayıyla koşun, sonra bu motoru yeniden koşun.")
    else:
        print("SONUÇ: zorunlu gereksinimlerin tümü TAMAM (ELİMDE/BİLGİ satırları avukatındır).")


# ── --uygula: yalnız pip (koşan yorumlayıcı) ve compileall ──────────────────────────

_YONETILEN_ORTAM = "externally-managed-environment"


def uygula(kok=None):
    kok = pathlib.Path(kok) if kok is not None else EKLENTI_KOKU
    pip = next(a for a in denetle(kok) if a["anahtar"] == "pip_paketleri")
    if pip["durum"] == EKSIK and pip["komut"]:
        paketler = re.findall(r'"[^"]+"|\S+', pip["komut"].split(" -m pip install ", 1)[1].split("   (", 1)[0])
        kod, cikti = _calistir([sys.executable, "-m", "pip", "install"] + [p.strip('"') for p in paketler],
                               zaman_asimi=900)
        if kod != 0:
            if _YONETILEN_ORTAM in cikti:
                print("DURDU: pip '%s' dedi — bu yorumlayıcıya paket kurulamaz. İki yol var, karar "
                      "avukatın: (1) dağıtımın paket yöneticisiyle kurmak, (2) kancaların bulacağı bir "
                      "sanal ortam (venv). Sistem paketlerini zorlayan bayrak KULLANILMAZ." % _YONETILEN_ORTAM)
            else:
                print("DURDU: pip başarısız (çıkış %s): %s" % (kod, cikti.strip()[-400:]))
            return 1
    kod, cikti = _calistir([sys.executable, "-m", "compileall", "-q", kok], zaman_asimi=600)
    if kod != 0:
        print("DURDU: compileall başarısız (çıkış %s): %s" % (kod, cikti.strip()[-400:]))
        return 1
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ortak Avukat kurulum denetimi (Yargı Pro hariç gereksinimler)")
    ap.add_argument("--uygula", action="store_true",
                    help="eksik pip paketlerini koşan yorumlayıcıya kur ve eklentiyi derle, sonra yeniden denetle")
    ap.add_argument("--json", metavar="YOL", help="deterministik raporu bu dosyaya da yaz")
    a = ap.parse_args(argv)
    if a.uygula:
        sonuc = uygula()
        if sonuc is not None:
            return sonuc
    adimlar = denetle()
    rapor_bas(adimlar)
    kod = cikis_kodu(adimlar)
    if a.json:
        veri = {"adimlar": adimlar, "cikis": kod}
        pathlib.Path(a.json).write_text(json.dumps(veri, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    return kod


if __name__ == "__main__":
    sys.exit(main())
