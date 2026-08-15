# -*- coding: utf-8 -*-
"""v0.5.8.4 — KAYNAK-BLOĞU üretici + dilekce_denetim görünürlük katmanları.

372 Torbalı saha bulgusu: KAYNAK-BLOĞU deseni yarım kaldı — bloklar var ama
@sha8'siz, tazelik_denetim.py'nin KAYNAK_OGE_RE'si hash'siz öğeyi yakalamıyor,
denetim fiilen işlevsiz. Modelden elle sha yazması beklenemez → üretici script.

Denetlenen sözleşmeler:
  (1) kaynak_blogu.py çıktısı tazelik_denetim.py'nin KAYNAK_BLOK_RE +
      KAYNAK_OGE_RE regexleriyle BİREBİR parse edilir (import ederek round-trip);
  (2) sha8 = dosya ham baytlarının sha256 ilk 8 hex'i;
  (3) dosya yoksa öğe 'yol@BULUNAMADI' + stderr uyarı, exit 0;
  (4) [K] cephanelik denetimi 0 bulguda da İZ SATIRI basar (karne ölçülebilir);
  (5) girdi md'de kaynaklar bloğu yok/hashsiz → İSTİŞARİ uyarı, exit SABİT;
  (6) [Ş] şekil bölümü (.udf girdide content.xml'den): kenar 42.52 /
      LineSpacing 0.50 / '(https://' 11pt — istişari, exit SABİT.

Tümü sentetik veri + tmp_path (repo m.7: gerçek dava yolu/kişi adı YAZILMAZ).
"""
import hashlib
import importlib.util
import pathlib
import subprocess
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
KAYNAK_BLOGU = SKILLS / "oa-kontrol" / "scripts" / "kaynak_blogu.py"
TAZELIK = SKILLS / "oa-kontrol" / "scripts" / "tazelik_denetim.py"
DILEKCE = SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kb = _yukle("kaynak_blogu_v0584", KAYNAK_BLOGU)
tz = _yukle("tazelik_denetim_v0584", TAZELIK)
dd = _yukle("dilekce_denetim_v0584", DILEKCE)


def _kb_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(KAYNAK_BLOGU)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


def _dd_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(DILEKCE)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# Tüm zorunlu unsur + tertip-düzen kalemlerini karşılayan, aleyhe/OCR sinyalsiz
# SENTETİK taslak — exit 0 taban çizgisi (advisory katmanların exit'e
# dokunmadığı bununla POZİTİF olarak kanıtlanır, yalnız 'iki koşu eşit' değil).
TAM_TEMIZ = """# İstanbul 4. Asliye Hukuk Mahkemesi Sayın Hakimliği'ne

Davacı : Ayşe Yılmaz (TC kimlik no 11111111110, adres: Sentetik Mah. No: 1)
Davalı : Mehmet Kaya
Vekil  : Av. Elif Sentetik

Konu: Alacak istemi hakkında dava dilekçesidir.

Açıklamalar (vakıalar):
1. Taraflar arasında sözleşme ilişkisi kurulmuştur.
2. Davalı taraf edimini ifa etmemiştir.

Hukuki sebepler: TBK, HMK ve ilgili mevzuat dayanak alınmıştır.

Deliller: Tanık beyanı, bilirkişi incelemesi ve yazılı belgeler.

Netice-i talep: Davanın kabulüne karar verilmesini saygıyla talep ederiz.

15.08.2026
Av. Elif Sentetik — vekil — imza
"""


# ── (1) round-trip: üretici çıktısı ↔ tazelik_denetim regexleri ────────────

def test_cikti_tek_satir_ve_tazelik_regexleriyle_birebir_parse_edilir(tmp_path):
    (tmp_path / "a.md").write_text("sentetik iddia metni\n", encoding="utf-8")
    (tmp_path / "b.json").write_text('{"k": 1}\n', encoding="utf-8")
    rc, out, err = _kb_cli(
        ["--girdiler", "a.md", "b.json",
         "--besledigi", "08-dilekce", "--uretim", "2026-08-15T10:00Z"],
        cwd=tmp_path)
    assert rc == 0, err
    satir = out.strip()
    assert satir and "\n" not in satir, "stdout TEK satır olmalı"
    m = tz.KAYNAK_BLOK_RE.search(satir)
    assert m, "çıktı tazelik_denetim.KAYNAK_BLOK_RE ile eşleşmeli"
    ogeler = tz.KAYNAK_OGE_RE.findall(m.group(1))
    beklenen = [("a.md", tz.sha8(str(tmp_path / "a.md"))),
                ("b.json", tz.sha8(str(tmp_path / "b.json")))]
    assert ogeler == beklenen, "öğeler tazelik_denetim.KAYNAK_OGE_RE ile birebir çıkmalı"
    assert "besledigi: 08-dilekce" in satir
    assert "uretim: 2026-08-15T10:00Z" in satir


def test_besledigi_ve_uretim_opsiyoneldir(tmp_path):
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    rc, out, err = _kb_cli(["--girdiler", "a.md"], cwd=tmp_path)
    assert rc == 0, err
    satir = out.strip()
    assert tz.KAYNAK_BLOK_RE.search(satir)
    assert "besledigi" not in satir and "uretim" not in satir


def test_round_trip_urun_denetle_taze_ve_bayat(tmp_path):
    """En güçlü kanıt: üretilen blok, tazelik_denetim.urun_denetle'nin
    UÇTAN UCA hattından geçer — taze ürün temiz, kaynak değişince BAYAT."""
    oa = tmp_path / "_oa"
    (oa / "metin").mkdir(parents=True)
    (oa / "cikti").mkdir()
    kaynak = oa / "metin" / "kaynak.md"
    kaynak.write_text("sentetik olgu\n", encoding="utf-8")
    rc, out, err = _kb_cli(
        ["--girdiler", "metin/kaynak.md", "--besledigi", "urun"], cwd=oa)
    assert rc == 0, err
    urun = oa / "cikti" / "urun.md"
    urun.write_text(out.strip() + "\n\n# Sentetik ürün\n", encoding="utf-8")

    bayatlar, eksikler = tz.urun_denetle(str(tmp_path), str(urun))
    assert bayatlar == [] and eksikler == [], "taze üründe bulgu olmamalı"

    kaynak.write_text("sentetik olgu DEĞİŞTİ\n", encoding="utf-8")
    bayatlar, eksikler = tz.urun_denetle(str(tmp_path), str(urun))
    assert len(bayatlar) == 1 and eksikler == [], "kaynak değişince BAYAT çıkmalı"


# ── (2) sha8 doğruluğu ─────────────────────────────────────────────────────

def test_sha8_ham_baytlarin_sha256_ilk_8_hexi(tmp_path):
    icerik = b"ortak avukat sentetik veri\n"
    yol = tmp_path / "v.bin"
    yol.write_bytes(icerik)
    beklenen = hashlib.sha256(icerik).hexdigest()[:8]
    assert kb.sha8(str(yol)) == beklenen
    satir, uyarilar = kb.blok_uret([str(yol)])
    assert ("@" + beklenen) in satir
    assert uyarilar == []


# ── (3) BULUNAMADI yolu ────────────────────────────────────────────────────

def test_bulunamayan_dosya_oge_bulunamadi_stderr_uyari_exit_0(tmp_path):
    rc, out, err = _kb_cli(["--girdiler", "yok.md"], cwd=tmp_path)
    assert rc == 0, "dosya yokken de exit 0 (üretici bloklamaz)"
    assert "yok.md@BULUNAMADI" in out
    assert "BULUNAMADI" in err or "bulunamadı" in err, "stderr'e uyarı düşmeli"


# ── (4) [K] cephanelik İZ SATIRI ───────────────────────────────────────────

def test_k_iz_satiri_sifir_bulguda_da_basilir(tmp_path):
    taslak = tmp_path / "temiz.md"
    taslak.write_text(TAM_TEMIZ, encoding="utf-8")
    rc, out = _dd_cli([str(taslak), "--tip", "dava"], cwd=tmp_path)
    assert "[K] cephanelik: 0 bulgu" in out, "sessiz yeşil ölçülebilir olmalı (372 karnesi dersi)"


def test_k_iz_satiri_bulgu_sayisini_yazar(tmp_path):
    taslak = tmp_path / "ifsali.md"
    taslak.write_text(
        TAM_TEMIZ + "\nDavalı taraf zamanaşımı definî ileri sürebilir.\n",
        encoding="utf-8")
    rc, out = _dd_cli([str(taslak), "--tip", "dava"], cwd=tmp_path)
    assert "[K] cephanelik: 1 bulgu" in out


# ── (5) KAYNAK-BLOĞU istişari uyarısı — exit SABİT ─────────────────────────

def test_kaynak_blogu_yoksa_istisari_uyari_exit_sifir_kalir(tmp_path):
    taslak = tmp_path / "bloksuz.md"
    taslak.write_text(TAM_TEMIZ, encoding="utf-8")
    rc, out = _dd_cli([str(taslak), "--tip", "dava"], cwd=tmp_path)
    assert "KAYNAK-BLOĞU EKSİK/HASHSİZ — kaynak_blogu.py kullan" in out
    assert rc == 0, "istişari uyarı exit kodunu DEĞİŞTİRMEMELİ (taban çizgisi 0)"


def test_kaynak_blogu_hashsiz_ogede_uyari_exit_sifir_kalir(tmp_path):
    taslak = tmp_path / "hashsiz.md"
    taslak.write_text(
        "<!-- kaynaklar: metin/a.md · cikti/b.json -->\n" + TAM_TEMIZ,
        encoding="utf-8")
    rc, out = _dd_cli([str(taslak), "--tip", "dava"], cwd=tmp_path)
    assert "KAYNAK-BLOĞU EKSİK/HASHSİZ — kaynak_blogu.py kullan" in out
    assert rc == 0


def test_kaynak_blogu_hashli_blokta_uyari_yok(tmp_path):
    taslak = tmp_path / "hashli.md"
    taslak.write_text(
        "<!-- kaynaklar: metin/a.md@a1b2c3d4 · cikti/b.json@e5f6a7b8 | "
        "besledigi: 08-dilekce | uretim: 2026-08-15T10:00Z -->\n" + TAM_TEMIZ,
        encoding="utf-8")
    rc, out = _dd_cli([str(taslak), "--tip", "dava"], cwd=tmp_path)
    assert "KAYNAK-BLOĞU EKSİK/HASHSİZ" not in out
    assert rc == 0


def test_kaynak_blogu_yalniz_ilk_uc_satirda_aranir():
    gec = "satır 1\nsatır 2\nsatır 3\n<!-- kaynaklar: x@11223344 -->\n"
    uyarilar = dd.kaynak_blogu_uyarilari(gec)
    assert uyarilar and "KAYNAK-BLOĞU EKSİK/HASHSİZ" in uyarilar[0]
    bas = "<!-- kaynaklar: x@11223344 -->\nsatır 2\n"
    assert dd.kaynak_blogu_uyarilari(bas) == []


# ── (6) [Ş] şekil bölümü — sentetik mini UDF ───────────────────────────────

def _u16(s):
    return len(s.encode("utf-16-le")) // 2


METIN_ON = "Sentetik dilekçe gövdesi "
LINK = "(https://ornek.example/karar)"
METIN_SON = " uyarınca sunulmuştur.\n"
CDATA = METIN_ON + LINK + METIN_SON


def _standart_elements(link_size="11", linespacing="0.50", ls_var=True):
    a, b, c = _u16(METIN_ON), _u16(LINK), _u16(METIN_SON)
    ls = ' LineSpacing="%s"' % linespacing if ls_var else ""
    return (
        '<paragraph Alignment="3" FirstLineIndent="24.0" SpaceBelow="6.0"%s>'
        '<content startOffset="0" length="%d" family="Times New Roman" size="12"/>'
        '<content startOffset="%d" length="%d" family="Times New Roman" size="%s"/>'
        '<content startOffset="%d" length="%d" family="Times New Roman" size="12"/>'
        '</paragraph>' % (ls, a, a, b, link_size, a + b, c))


def _mini_udf_yaz(yol, cdata=CDATA, elements_xml=None, kenar_attrs=None):
    kenarlar = {"leftMargin": "42.52", "rightMargin": "42.52",
                "topMargin": "42.52", "bottomMargin": "42.52"}
    if kenar_attrs:
        kenarlar.update(kenar_attrs)
    pf = " ".join('%s="%s"' % (k, v) for k, v in kenarlar.items())
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<template format_id="1.8">\n'
        '<content><![CDATA[' + cdata + ']]></content>\n'
        '<properties>\n'
        '<pageFormat mediaSizeName="1" ' + pf + ' paperOrientation="1"/>\n'
        '</properties>\n'
        '<elements resolver="hvl-default" name="hvl-default">\n'
        + (elements_xml if elements_xml is not None else _standart_elements()) +
        '\n</elements>\n<styles>\n'
        '<style name="default" description="Govde" family="Times New Roman" size="12"/>\n'
        '</styles>\n</template>\n')
    with zipfile.ZipFile(str(yol), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml.encode("utf-8"))
    return yol


def test_s_uyumlu_udfde_uyari_yok(tmp_path):
    udf = _mini_udf_yaz(tmp_path / "uyumlu.udf")
    assert dd.sekil_uyarilari(str(udf)) == []


def test_s_linespacing_0_5_yazimi_da_kabul(tmp_path):
    """Yerel motor '0.5', saha standardı '0.50' yazar — ikisi de aynı değerdir."""
    udf = _mini_udf_yaz(tmp_path / "nokta5.udf",
                        elements_xml=_standart_elements(linespacing="0.5"))
    assert dd.sekil_uyarilari(str(udf)) == []


def test_s_kenar_42_52_degilse_uyari(tmp_path):
    udf = _mini_udf_yaz(tmp_path / "kenar.udf",
                        kenar_attrs={"topMargin": "70.87"})
    uyarilar = dd.sekil_uyarilari(str(udf))
    assert any("42.52" in u and "topMargin" in u for u in uyarilar)


def test_s_linespacing_yaygin_degilse_uyari(tmp_path):
    udf = _mini_udf_yaz(tmp_path / "aralik.udf",
                        elements_xml=_standart_elements(ls_var=False))
    uyarilar = dd.sekil_uyarilari(str(udf))
    assert any("LineSpacing" in u for u in uyarilar)


def test_s_link_11pt_kapsaminda_degilse_uyari(tmp_path):
    udf = _mini_udf_yaz(tmp_path / "link12.udf",
                        elements_xml=_standart_elements(link_size="12"))
    uyarilar = dd.sekil_uyarilari(str(udf))
    assert any("11pt" in u for u in uyarilar)


def test_s_cli_udf_girdide_gorunur_ve_exit_sabit(tmp_path):
    """Taslak .udf ise [Ş] content.xml'den çalışır; şekil sapması exit'i
    DEĞİŞTİRMEZ (sert kapı teslim_paketi'nde — burada yalnız görünürlük)."""
    uyumlu = _mini_udf_yaz(tmp_path / "uyumlu.udf")
    bozuk = _mini_udf_yaz(tmp_path / "bozuk.udf",
                          kenar_attrs={"leftMargin": "70.87"})
    rc_u, out_u = _dd_cli([str(uyumlu), "--tip", "genel"], cwd=tmp_path)
    rc_b, out_b = _dd_cli([str(bozuk), "--tip", "genel"], cwd=tmp_path)
    assert "[Ş] ŞEKİL" in out_u and "[Ş] ŞEKİL" in out_b
    s_bolum_u = out_u.split("[Ş] ŞEKİL")[1].split("====")[0]
    s_bolum_b = out_b.split("[Ş] ŞEKİL")[1].split("====")[0]
    assert "[OK]" in s_bolum_u
    assert "[UYARI]" in s_bolum_b and "42.52" in s_bolum_b
    assert rc_u == rc_b, "[Ş] advisory exit kodunu değiştirmemeli"
