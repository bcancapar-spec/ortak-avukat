"""RESMİ OKUYUCU TANIĞI — geçerlilik kapısının kör noktasını kapatan 5. denetim.

2026/307 saha oturumunun bildirdiği reçetenin 3. adımı. Gerekçe: `udf_dogrula`nın
ilk dört denetimi dosyayı BİZİM okuyucumuzun (udf_metin.py) beklentisine göre
sınar. Sahada bizi yakan hata sınıfı tam olarak buydu — eski hand-rolled zip
çıktısı BİZİM round-trip'imizi GEÇİYOR ama UYAP Doküman Editörü onu AÇMIYORDU.
Kendi varsayımıyla kendini doğrulamak kanıt değildir; bu yüzden dosyayı ÜRETEN
aracın kendi okuyucusu (`udf-cli udf2md`) dışarıdan tanık olarak çağrılır.

Testler AĞSIZ koşar: dış süreç `okuyucu_fn` ile enjekte edilir.
"""
import importlib.util
import io
import os
import sys
import zipfile

import pytest

BETIK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "ortak-avukat", "skills", "oa-dilekce", "scripts", "udf_yaz.py")


@pytest.fixture(scope="module")
def uy():
    spec = importlib.util.spec_from_file_location("_test_resmi_udf_yaz", BETIK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_resmi_udf_yaz"] = mod
    spec.loader.exec_module(mod)
    return mod


GOVDE = ("T.C. DENİZLİ 8. ASLİYE HUKUK MAHKEMESİ'NE\n"
         "CEVAP DİLEKÇESİ\n"
         "Müvekkil aleyhine açılan davanın reddi gerekmektedir.\n"
         "Yargıtay 17. Hukuk Dairesi 2019/1234 E. 2021/5678 K. sayılı kararı uyarınca.\n"
         "NETİCE-İ TALEP: Davanın reddine karar verilmesini talep ederiz.\n")


def _gecerli_udf_yaz(yol, govde=GOVDE):
    """İlk DÖRT denetimden geçen (bizim ayrıştırıcımızın kabul ettiği) bir UDF
    üretir — resmî okuyucu bacağını yalıtarak sınayabilmek için."""
    paragraflar = [s + "\n" for s in govde.split("\n") if s] or [govde]
    tam = "".join(paragraflar)
    parcalar, imlec = [], 0
    for p in paragraflar:
        u = len(p.encode("utf-16-le")) // 2
        parcalar.append('<paragraph><content startOffset="%d" length="%d"/></paragraph>'
                        % (imlec, u))
        imlec += u
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<template format_id="1.8">'
           '<content><![CDATA[%s]]></content>'
           '<elements resolver="hvl-default">%s</elements>'
           '</template>' % (tam, "".join(parcalar)))
    with zipfile.ZipFile(yol, "w") as zf:
        zf.writestr("content.xml", xml)
    return tam


def _sahte_okuyucu(calisti=True, basarili=True, metin=None, hata=None):
    def _fn(_yol, **_kw):
        return {"calisti": calisti, "basarili": basarili,
                "metin": metin if metin is not None else GOVDE, "hata": hata}
    return _fn


# ── (1) Üç durum ayrı tutulur ────────────────────────────────────────────────

def test_resmi_okuyucu_okuduysa_OK_ve_gecerli(tmp_path, uy):
    yol = str(tmp_path / "a.udf")
    _gecerli_udf_yaz(yol)
    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu())
    assert s["resmi_okuyucu"] == "OK"
    assert s["gecerli"] is True
    assert s["resmi_okuyucu_karakter"] == len(GOVDE)


def test_resmi_okuyucu_REDDEDERSE_gecersiz(tmp_path, uy):
    """ASIL KAZANIM: bizim dört denetimimiz GEÇSE BİLE, dosyayı üreten aracın
    okuyucusu reddediyorsa dosya GEÇERSİZDİR — sahadaki hata sınıfı budur."""
    yol = str(tmp_path / "b.udf")
    _gecerli_udf_yaz(yol)
    kontrol = uy.udf_dogrula(yol, resmi_okuyucu=False)
    assert kontrol["gecerli"] is True, "ön koşul: ilk dört denetim geçmeli"

    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(
        calisti=True, basarili=False, hata="udf2md exit 1: bozuk belge"))

    assert s["resmi_okuyucu"] == "RET"
    assert s["gecerli"] is False
    assert any("RESMİ OKUYUCU REDDETTİ" in h for h in s["hatalar"])


def test_arac_yoksa_YAPILAMADI_ve_BLOKLAMAZ(tmp_path, uy):
    """Ağ/oturum/Node yokluğu ORTAM koşuludur, dosyanın kusuru değil — çevrimdışı
    çalışma imkânsızlaşmasın diye bloklamaz. Ama 'doğrulandı' da SAYILMAZ."""
    yol = str(tmp_path / "c.udf")
    _gecerli_udf_yaz(yol)
    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(
        calisti=False, basarili=False, hata="npx bulunamadı"))

    assert s["resmi_okuyucu"] == "YAPILAMADI"
    assert s["gecerli"] is True, "ortam eksikliği dosyayı geçersiz kılmaz"
    assert "npx bulunamadı" in s["resmi_okuyucu_not"]
    assert not any("RESMİ OKUYUCU" in h for h in s["hatalar"])


def test_YAPILAMADI_hali_STDOUT_ta_GORUNUR(tmp_path, uy):
    """Sessiz atlama yasağının simetriği: doğrulanmamış bir dosyayı doğrulanmış
    sanmak, hiç doğrulamamaktan tehlikelidir — bu hâl susturulamaz."""
    tampon = io.StringIO()
    uy._resmi_okuyucu_bas(
        {"resmi_okuyucu": "YAPILAMADI", "resmi_okuyucu_not": "oturum yok"}, akis=tampon)
    cikti = tampon.getvalue()
    assert "YAPILAMADI" in cikti
    assert "AÇILDIĞI DOĞRULANMADI" in cikti


# ── (2) "Açılıyor ama boş/kırpık" — içerik kaybı ─────────────────────────────

def test_resmi_okuyucu_icerik_kaybini_yakalar(tmp_path, uy):
    """Dosya açılıyor ama gövdenin önemli kısmı okunamıyorsa GEÇERSİZ — 'açıldı'
    tek başına yeterli kanıt değildir."""
    yol = str(tmp_path / "d.udf")
    tam = _gecerli_udf_yaz(yol)
    kirpik = tam[:int(len(tam) * 0.2)]

    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(metin=kirpik))

    assert s["resmi_okuyucu"] == "RET"
    assert s["gecerli"] is False
    assert any("İÇERİK KAYBI" in h for h in s["hatalar"])


def test_markdown_imleri_yuzunden_UZUN_metin_kusur_sayilmaz(tmp_path, uy):
    """udf2md markdown imleri ekler (## , **, | ) — çıktının UZUN olması
    NORMALDİR; yalnız KISALIK içerik kaybı işaretidir."""
    yol = str(tmp_path / "e.udf")
    tam = _gecerli_udf_yaz(yol)
    zengin = "## " + tam.replace("\n", "\n\n**") + "\n\n| a | b |\n"

    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(metin=zengin))

    assert s["resmi_okuyucu"] == "OK"
    assert s["gecerli"] is True


# ── (3) Ortam hatası ile GERÇEK RET birbirine karışmaz ──────────────────────

@pytest.mark.parametrize("stderr_metni", [
    "Error: login required", "Oturum bulunamadı", "quota exceeded",
    "fetch failed", "ETIMEDOUT",
])
def test_oturum_ag_hatasi_RET_degil_YAPILAMADI(tmp_path, uy, monkeypatch, stderr_metni):
    """Login'i unutmuş bir avukatın GEÇERLİ dilekçesi 'bozuk' ilan edilemez —
    ortam hatası dosya hakkında hüküm DEĞİLDİR."""
    class _P:
        returncode = 1
        stdout = ""
        stderr = stderr_metni

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is False, f"{stderr_metni!r} ortamsal sayılmalıydı"
    assert r["basarili"] is False


def test_gercek_bozukluk_RET_olarak_isaretlenir(tmp_path, uy, monkeypatch):
    class _P:
        returncode = 1
        stdout = ""
        stderr = "Error: invalid UDF structure — unexpected element"

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is True, "yapısal hata bir HÜKÜMDÜR, ortam koşulu değil"
    assert r["basarili"] is False
    assert "OKUYAMADI" in r["hata"]


def test_npx_yoksa_calisti_False(tmp_path, uy, monkeypatch):
    monkeypatch.setattr(uy.shutil, "which", lambda _a: None)
    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))
    assert r["calisti"] is False and "npx bulunamadı" in r["hata"]


def test_zaman_asimi_ortam_sayilir(tmp_path, uy, monkeypatch):
    def _patla(*_a, **_k):
        raise uy.subprocess.TimeoutExpired(cmd="udf2md", timeout=1)
    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", _patla)

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is False and "zaman aşımı" in r["hata"]


# ── (4) Hat bütünlüğü: md2udf'e dönüş yok ───────────────────────────────────

def test_okuyucu_udf2md_cagirir_md2udf_DEGIL(tmp_path, uy, monkeypatch):
    cagrilar = []

    class _P:
        returncode = 0
        stdout = GOVDE
        stderr = ""

    def _yakala(args, **_k):
        cagrilar.append(args)
        return _P()

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", _yakala)
    uy.npx_ile_udf_oku(str(tmp_path / "x.udf"))

    assert cagrilar, "dış süreç çağrılmalıydı"
    komut = cagrilar[0]
    assert "udf2md" in komut
    assert "md2udf" not in komut
    assert "udf-cli@latest" in komut
