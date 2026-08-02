"""DIŞ SÜREÇ ÇIKTISI AÇIKÇA utf-8 ÇÖZÜLÜR — P0, saha platformu kusuru (v0.5.5.5).

BULGU: `subprocess.run(..., text=True)` çağrısına `encoding=` verilmezse Python
çıktıyı YEREL KOD SAYFASIYLA çözer. Türkçe Windows'ta bu **cp1254**'tür ve
`udf-cli` çıktısındaki ilk çok-baytlı karakterde şununla çöker:

    UnicodeDecodeError: 'charmap' codec can't decode byte 0x9e ...

Sonuç sessiz bir hata değil, TESLİM ENGELİDİR: UDF geçerlilik kapısının resmî
okuyucu bacağı çöker, GEÇERLİ bir dilekçe "GEÇERSİZ" ilan edilir ve teslim
bloklanır. Ölçüldü: avukatın kendi ortamında (PYTHONUTF8 ayarsız, cp1254)
teslim hattında **15 test kırmızı**; `encoding="utf-8", errors="replace"`
eklendikten sonra **36 yeşil**.

NEDEN GÖRÜLMEDİ: geliştirme koşularının tamamı `PYTHONUTF8=1` ile yapılmıştı —
o bayrak text modunu utf-8'e çevirdiği için kusuru MASKELİYORDU. Yani hata
kodda değil, ÖLÇÜM ORTAMINDAYDI: sistemin çalıştığı gerçek ortam hiç sınanmamış.

Bu test o maskeyi kaldırır: kaynağı statik tarar, ortamdan bağımsız çalışır.
`__OA_UTF8_GUARD__` (stdout/stderr reconfigure) bu kusuru KAPATMAZ — o yazma
yönünü korur, buradaki sorun OKUMA yönüdür.
"""
import ast
import os
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"

# text=True yerine geçen eş anlamlılar — ikisi de yerel kod sayfasını tetikler.
_METIN_MODU = ("text", "universal_newlines")


def _subprocess_cagrilari(yol):
    """Dosyadaki subprocess.run/Popen/check_output çağrılarını AST ile çıkarır.
    Regex DEĞİL AST: çok satırlı çağrılar ve yorum içindeki sahte eşleşmeler
    regex taramasını yanıltır (bu kusur ilk taramada tam olarak öyle kaçtı)."""
    agac = ast.parse(yol.read_text(encoding="utf-8"), filename=str(yol))
    for d in ast.walk(agac):
        if not isinstance(d, ast.Call):
            continue
        f = d.func
        ad = None
        if isinstance(f, ast.Attribute):
            ad = f.attr
            kok = f.value
            if not (isinstance(kok, ast.Name) and kok.id == "subprocess"):
                continue
        if ad not in ("run", "Popen", "check_output"):
            continue
        anahtarlar = {k.arg for k in d.keywords if k.arg}
        yield d.lineno, anahtarlar


def _uretim_dosyalari():
    return sorted(p for p in PLUGIN.rglob("*.py") if "__pycache__" not in str(p))


def test_metin_modlu_dis_surec_cagrisi_encoding_SIZ_olamaz():
    """ASIL KİLİT: üretim kodundaki hiçbir text-mod dış süreç çağrısı
    `encoding=` vermeden yazılamaz."""
    kusurlu = []
    for yol in _uretim_dosyalari():
        for satir, anahtarlar in _subprocess_cagrilari(yol):
            metin_modu = any(a in anahtarlar for a in _METIN_MODU)
            if metin_modu and "encoding" not in anahtarlar:
                kusurlu.append(f"{yol.relative_to(REPO)}:{satir}")

    assert not kusurlu, (
        "Bu çağrılar dış süreç çıktısını YEREL kod sayfasıyla çözer; Türkçe "
        "Windows'ta (cp1254) UnicodeDecodeError ile çöker ve GEÇERLİ dilekçe "
        "'GEÇERSİZ' ilan edilip teslim bloklanır. Çözüm: "
        'encoding="utf-8", errors="replace" ekleyin.\n  ' + "\n  ".join(kusurlu))


def test_encoding_verilen_yerde_errors_de_verilir():
    """`errors=` olmadan tek bir bozuk bayt yine çökertir — OCR'lı/bozuk
    çıktıda bu gerçek bir ihtimaldir. utf-8 + replace ikisi birlikte anlamlıdır."""
    kusurlu = []
    for yol in _uretim_dosyalari():
        for satir, anahtarlar in _subprocess_cagrilari(yol):
            if "encoding" in anahtarlar and "errors" not in anahtarlar:
                kusurlu.append(f"{yol.relative_to(REPO)}:{satir}")
    assert not kusurlu, (
        "encoding verilmiş ama errors verilmemiş — tek bozuk bayt yine "
        "çökertir:\n  " + "\n  ".join(kusurlu))


def test_udf_hattinin_dort_dis_cagrisi_da_kapsanir():
    """Kapsam kontrolü: taramanın UDF hattını gerçekten gördüğünü doğrular.
    Bu test olmadan, tarayıcı hiçbir çağrı bulamasa bile üstteki iki test
    'yeşil' görünürdü (boş kümede assert her zaman geçer — sahte yeşil)."""
    hat = [
        PLUGIN / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py",
        PLUGIN / "skills" / "oa-pipeline" / "scripts" / "udf_metin.py",
        PLUGIN / "skills" / "oa-kontrol" / "scripts" / "teslim_paketi.py",
    ]
    toplam = 0
    for yol in hat:
        assert yol.is_file(), f"beklenen script yok: {yol}"
        n = len(list(_subprocess_cagrilari(yol)))
        assert n > 0, f"{yol.name}: dış süreç çağrısı bulunamadı — tarayıcı kör"
        toplam += n
    assert toplam >= 5, f"UDF hattında beklenenden az çağrı görüldü: {toplam}"


@pytest.mark.parametrize("ad", ["udf_yaz.py", "udf_metin.py"])
def test_udf_scriptleri_gerekceyi_metinde_tasiyor(ad):
    """Kural yalnız testte değil KODUN YANINDA da yaşasın: bir sonraki
    geliştirici `encoding=` satırını 'gereksiz' sanıp silmesin."""
    yol = next(PLUGIN.rglob(ad))
    kaynak = yol.read_text(encoding="utf-8")
    assert "cp1254" in kaynak, (
        f"{ad}: encoding gerekçesi kodda anlatılmıyor — kuralın NEDENİ "
        "kaybolursa kural da kaybolur")
