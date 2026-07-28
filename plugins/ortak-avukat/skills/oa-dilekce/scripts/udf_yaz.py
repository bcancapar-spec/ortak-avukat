#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
udf_yaz.py — markdown → UYAP UDF TESLİM HATTI (oa-dilekce yardımcısı)

P0-10 (Yargı Pro UDF rehberi uyumu, v0.5.5): Denizli 307 dosyasında bu
script'in eski (yalnız yerel) motoru UYAP-geçerli bir `.udf` ÜRETEMEDİ.
Rehber (`udf_tiff_pdf_guide` MCP aracı / `yargi-udf-tiff-pdf-guide` skill,
sürüm 2026-06-22) açıkça şunu söyler: **"UDF opak bir UYAP biçimidir — yalnız
`udf-cli` üretebilir/okuyabilir; ASLA elle yazma/düzenleme; her zaman
`html2udf`, ASLA `md2udf`."** Bu yüzden VARSAYILAN hat artık rehbere birebir
uyar:

    md taslak → UDF-HTML (md_udf_html.py, inline-CSS) → `npx udf-cli
    html2udf` (GERÇEK UYAP yazıcısı) → [+opsiyonel] UDF-HTML → PDF
    (udf_html2pdf.py, PyMuPDF Story)

`--yerel-motor` verilirse eski (2026 öncesi) hand-rolled ZIP/XML motoru
kullanılır — bu YEDEKTİR, ağ/oturum olmadığında (ör. teslim_paketi.py'nin
otomatik ön-kapı zincirinde) hızlı yapısal denetim için tutulur; **UYAP
uyumu rehber gereği GARANTİ DEĞİLDİR** ve script bunu her koşuda açıkça basar.
`--dogrula` HER İKİ motorun çıktısını da aynı mekanik kapıdan geçirir (zip
açılır mı / content.xml var mı / XML iyi biçimli mi / CDATA+offset tutarlı
mı) — bu denetim gerçek `udf-cli` çıktısında da doğrulanmıştır (bkz.
`references/degisiklik-gunlugu.md`).

Yerel motorun `content.xml` şeması (yalnız `--yerel-motor` ile üretilir,
UYAP editör / Swing tabanlı okuyucunun BEKLEDİĞİ asgari alt küme):
  - kök  : <template format_id="...">
  - metin: <content><![CDATA[...]]></content>   (ATTRIBUTESİZ — okuyucu bunu arar)
  - düzen: <properties><pageFormat .../></properties>
  - blok : <elements resolver="hvl-default"> altında her paragraf için
           <paragraph Alignment="N"><content startOffset="S" length="L"/></paragraph>
           startOffset/length CDATA metniyle BİREBİR tutar; paragraflar metni
           boşluksuz böler (her paragraf sonundaki '\n' dahildir).
  - stil : <styles><style name="default" .../></styles>
`udf_metin.py` (oa-pipeline, ingest okuyucusu) bu CDATA yapısını arar; hem
yerel motorun hem gerçek `udf-cli`'nin çıktısı bu okuyucuyla round-trip eder.

DETERMİNİST MOTOR: bu script hukuki değerlendirme YAPMAZ; yalnız biçim üretir.

Kullanım (Windows/PowerShell — 'python', 'python3' DEĞİL):
  python udf_yaz.py --girdi taslak.md --cikti dilekce.udf              # varsayılan: npx udf-cli html2udf
  python udf_yaz.py --girdi taslak.md --cikti dilekce.udf --pdf dilekce.pdf
  python udf_yaz.py --girdi taslak.md --cikti dilekce.udf --yerel-motor  # ağsız yedek motor
  Get-Content taslak.md -Raw | python udf_yaz.py --cikti dilekce.udf
  python udf_yaz.py --girdi taslak.txt --cikti dilekce.udf --ham       # md yorumlama yok
  python udf_yaz.py --dogrula dilekce.udf                              # yazmadan mekanik denetim

Varsayılan motor `npx` (Node.js) + `udf-cli` (login-gated, ağ gerektirir —
rehberin Kimlik Doğrulama bölümü) çağırır; `--yerel-motor` yalnız standart
kütüphane (zipfile, xml, argparse) kullanır, ek bağımlılık yoktur.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
import xml.etree.ElementTree as ET

# UYAP editörünün yazdığı güncel şablon sürümü. Uyum sorununda düşürülebilir
# (bilinen değerler: 1.6 / 1.7 / 1.8). Gerçek cihaz testinde ilk denenecek yer burası.
FORMAT_ID = "1.8"

# UYAP Alignment (java Swing StyleConstants): 0=SOL 1=ORTA 2=SAG 3=İKİ_YANA_YASLI
HIZA_SOL, HIZA_ORTA, HIZA_SAG, HIZA_YASLI = 0, 1, 2, 3


def utf16_uzunluk(s):
    """UYAP editörü (Java/Swing) offset'leri UTF-16 CODE UNIT sayar; Python str ise
    code-point sayar. BMP-dışı karakter (emoji, U+10000+) Python'da tek code-point
    ama UTF-16'da İKİ code unit'tir (surrogate çifti). Offset'leri Swing ile aynı
    birime çekmek için UTF-16 code unit sayısını döndür; aksi halde tek bir emoji
    o paragraftan sonraki TÜM offset'leri 1 kaydırır ve UYAP'ta biçim/aralık bozulur.
    """
    return len(s.encode("utf-16-le")) // 2


# ───────────────────────────── markdown → düz metin ─────────────────────────
def md_satir_duzlestir(satir):
    """Bir markdown satırını düz metne indir. (metin, baslik_mi) döndürür.

    UDF zengin metindir; ama önce DOĞRU düz-metin + paragraf yapısı garanti
    edilir. İşaretler (##, **, *, `, [..](..)) makul biçimde temizlenir.
    """
    s = satir.rstrip("\r")
    baslik = False

    # ATX başlık:  '# ...' / '###   ...'  → baslik; sondaki süs '#'leri at
    m = re.match(r"^(#{1,6})\s*(.*?)\s*#*\s*$", s)
    if m:
        baslik = True
        s = m.group(2)

    # liste imi:  '- ' / '* ' / '+ '  → '• ' (girinti korunur)
    m = re.match(r"^(\s*)[-*+]\s+(.*)$", s)
    if m:
        s = m.group(1) + "• " + m.group(2)

    # kalın **..** / __..__  → içerik
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"__(.+?)__", r"\1", s)
    # italik *..* / _.._  → içerik (tek yıldız/alt çizgi)
    s = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)", r"\1", s)
    s = re.sub(r"(?<!_)_(?!_)([^_]+?)_(?!_)", r"\1", s)
    # satır içi kod `..`  → içerik
    s = re.sub(r"`([^`]+)`", r"\1", s)
    # bağlantı [metin](url)  → 'metin (url)'
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)

    return s, baslik


def cdata_guvenli(metin):
    """CDATA içinde yasak olan `]]>` dizisini böler (tek yer bu olabilir)."""
    return metin.replace("]]>", "]]]]><![CDATA[>")


# ───────────────────────────── UDF üretimi ─────────────────────────────────
def udf_uret(ham_metin, ham_mod=False, format_id=FORMAT_ID):
    """Metinden content.xml (str), tam-metin (str) ve paragraf listesi üretir.

    paragraflar: [(startOffset, length, baslik_mi), ...]
    length her paragrafın SONUNDAKİ '\n' karakterini de içerir; böylece
    offset'ler CDATA metnini boşluksuz ve birebir böler.

    startOffset/length UTF-16 CODE UNIT olarak hesaplanır (UYAP/Swing birimi);
    BMP-dışı karakterde Python code-point sayımı Swing'le kayardı — bkz. utf16_uzunluk.
    """
    ham = ham_metin.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    satirlar = ham.split("\n") if ham != "" else [""]

    parcalar, paragraflar, imlec = [], [], 0
    for satir in satirlar:
        if ham_mod:
            duz, baslik = satir, False
        else:
            duz, baslik = md_satir_duzlestir(satir)
        parca = duz + "\n"                      # paragraf + ayraç newline
        u16 = utf16_uzunluk(parca)              # UYAP/Swing offset birimi
        paragraflar.append((imlec, u16, baslik))
        parcalar.append(parca)
        imlec += u16                            # UTF-16 code unit offset
    tam = "".join(parcalar)

    x = []
    x.append('<?xml version="1.0" encoding="UTF-8"?>')
    x.append('<template format_id="%s">' % format_id)
    x.append('<content><![CDATA[' + cdata_guvenli(tam) + ']]></content>')
    x.append('<properties>')
    x.append('<pageFormat mediaSizeName="1" leftMargin="70.866" '
             'rightMargin="70.866" topMargin="70.866" bottomMargin="70.866" '
             'paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0"/>')
    x.append('</properties>')
    x.append('<elements resolver="hvl-default">')
    for start, length, baslik in paragraflar:
        hiza = HIZA_ORTA if baslik else HIZA_YASLI
        x.append('<paragraph Alignment="%d">' % hiza)
        if baslik:
            x.append('<content startOffset="%d" length="%d" bold="true"/>'
                     % (start, length))
        else:
            x.append('<content startOffset="%d" length="%d"/>' % (start, length))
        x.append('</paragraph>')
    x.append('</elements>')
    x.append('<styles>')
    x.append('<style name="default" description="Govde" '
             'family="Times New Roman" size="12" bold="false" italic="false" '
             'foreground="-16777216"/>')
    x.append('</styles>')
    x.append('</template>')
    xml_str = "\n".join(x) + "\n"

    # üretilen XML gerçekten iyi biçimli mi? (okuyucunun ET fallback'i için de şart)
    try:
        ET.fromstring(xml_str)
    except ET.ParseError as e:
        sys.exit("HATA: üretilen content.xml iyi biçimli değil: %s" % e)

    return xml_str, tam, paragraflar


def udf_yaz(cikti_yolu, xml_str):
    """content.xml'i UDF (ZIP) arşivine ATOMİK yazar (tmp + os.replace) —
    yarım yazılmış/kesintiye uğramış bir .udf asla nihai adda görünmez."""
    tmp = cikti_yolu + ".tmp-%d" % os.getpid()
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml_str.encode("utf-8"))
    _atomik_tasi(tmp, cikti_yolu)


# ─────────────────── round-trip doğrulama (udf_metin.py mantığı) ────────────
def udf_metni_geri_oku(cikti_yolu):
    """udf_metin.py / udf_isle() ile AYNI regex mantığıyla metni geri okur."""
    zf = zipfile.ZipFile(cikti_yolu)
    hedef = next((a for a in zf.namelist()
                  if a.lower().endswith("content.xml")), None)
    if hedef is None:
        return None
    ham = zf.read(hedef).decode("utf-8", errors="replace")
    m = re.search(r"<content>\s*<!\[CDATA\[(.*?)\]\]>\s*</content>", ham, re.S)
    return m.group(1) if m else None


# ───────────────── UDF GEÇERLİLİK KAPISI (mekanik denetim, hüküm YOK) ───────
def udf_dogrula(yol):
    """Var olan bir `.udf` dosyasının UYAP okuyucusunun (udf_metin.py) beklediği
    yapıya uyup uymadığını MEKANİK olarak denetler.

    Bu fonksiyon hukuki/biçimsel KALİTE hakkında hüküm VERMEZ ("iyi dilekçe"
    demez); yalnız dört somut denetimi "var/yok" ve "tutarlı/tutarsız" olarak
    raporlar — model kurar/script denetler ayrımı burada da geçerlidir:
      1) zip açılır mı (bozuk/ZIP-olmayan dosya → GEÇERSİZ)
      2) content.xml arşivde var mı
      3) content.xml iyi biçimli XML mi (ET.fromstring parse eder mi)
      4) <content><![CDATA[...]]></content> bulunuyor mu (metin round-trip'in
         kaynağı) ve paragraph/content startOffset+length değerleri UTF-16
         code-unit biriminde ARDIŞIK mı, toplamları CDATA metninin UTF-16
         uzunluğuyla birebir tutuyor mu (offset kayması → UYAP'ta biçim/aralık
         bozulur; bu denetim onu yazımdan SONRA da yakalayabilir, ör. dosya
         elle düzenlenmiş/bozulmuşsa).

    Döner: dict —
      gecerli (bool), hatalar (list[str] — boşsa geçerli),
      content_xml_var (bool), xml_iyi_bicimli (bool), cdata_bulundu (bool),
      karakter_sayisi (int|None), paragraf_sayisi (int|None),
      offsetler_tutarli (bool|None).
    """
    sonuc = {
        "gecerli": False, "hatalar": [],
        "content_xml_var": False, "xml_iyi_bicimli": False,
        "cdata_bulundu": False, "karakter_sayisi": None,
        "paragraf_sayisi": None, "offsetler_tutarli": None,
    }

    # 1) zip açılır mı
    try:
        zf = zipfile.ZipFile(yol)
    except (zipfile.BadZipFile, FileNotFoundError, OSError) as e:
        sonuc["hatalar"].append("ZIP açılamadı: %s" % e)
        return sonuc

    # 2) content.xml var mı
    hedef = next((a for a in zf.namelist()
                  if a.lower().endswith("content.xml")), None)
    if hedef is None:
        sonuc["hatalar"].append("content.xml arşivde bulunamadı")
        return sonuc
    sonuc["content_xml_var"] = True
    ham = zf.read(hedef).decode("utf-8", errors="replace")

    # 3) XML iyi biçimli mi
    try:
        kok = ET.fromstring(ham)
        sonuc["xml_iyi_bicimli"] = True
    except ET.ParseError as e:
        sonuc["hatalar"].append("content.xml iyi biçimli değil: %s" % e)
        return sonuc

    # 4) CDATA + offset/uzunluk tutarlılığı (round-trip'in temeli)
    m = re.search(r"<content>\s*<!\[CDATA\[(.*?)\]\]>\s*</content>", ham, re.S)
    if not m:
        sonuc["hatalar"].append("<content><![CDATA[...]]></content> bulunamadı")
        return sonuc
    sonuc["cdata_bulundu"] = True
    tam = m.group(1)
    sonuc["karakter_sayisi"] = len(tam)
    toplam_u16 = utf16_uzunluk(tam)

    # NOT (P0-10 düzeltme): gerçek `udf-cli` çıktısında tablo hücreleri
    # (<table><row><cell><paragraph><content .../></paragraph></cell>...)
    # üst-seviye <paragraph>'lardan AYRI, iç içe bir dalda yaşar — yalnız
    # DİREKT paragraph/content arayan bir XPath bu hücreleri KAÇIRIR ve
    # tablolu her belgeyi (tamamen GEÇERLİ olsa bile) yanlışlıkla
    # "GEÇERSİZ" işaretler. ".//elements//content" `<elements>` altındaki
    # HER derinlikte content'i (üst paragraf + liste maddesi + tablo hücresi)
    # belge sırasıyla (ElementTree'nin doğal DFS'i) döndürür.
    paragraflar = kok.findall(".//elements//content")
    if not paragraflar:
        # esnek arama: <elements> sarmalayıcısı yok/adı farklıysa, startOffset
        # taşıyan HER content elemanı (CDATA'nın kendi <content>'i attribute'süz
        # olduğundan otomatik elenir).
        paragraflar = [el for el in kok.iter("content") if "startOffset" in el.attrib]
    sonuc["paragraf_sayisi"] = len(paragraflar)
    if not paragraflar:
        sonuc["hatalar"].append(
            "paragraph/content elemanı bulunamadı (offset/uzunluk denetlenemedi)")
        return sonuc

    imlec, tutarli = 0, True
    for el in paragraflar:
        try:
            start = int(el.attrib["startOffset"])
            length = int(el.attrib["length"])
        except (KeyError, ValueError):
            tutarli = False
            sonuc["hatalar"].append(
                "paragraph/content içinde startOffset/length okunamadı")
            break
        if start != imlec:
            tutarli = False
            sonuc["hatalar"].append(
                "offset süreksiz: beklenen %d, bulunan %d" % (imlec, start))
            break
        imlec += length
    if tutarli and imlec != toplam_u16:
        tutarli = False
        sonuc["hatalar"].append(
            "paragraf uzunlukları toplamı (%d) CDATA UTF-16 uzunluğuyla (%d) uyuşmuyor"
            % (imlec, toplam_u16))
    sonuc["offsetler_tutarli"] = tutarli

    if not sonuc["hatalar"]:
        sonuc["gecerli"] = True
    return sonuc


# ─────────────── ortak yardımcılar: yol çözme + atomik taşıma ──────────────
def _kok_coz(yol, kok):
    """--kok verilmişse göreli yolu ona göre çözer; verilmemişse CWD'ye göre
    mutlaklaştırır. Bu bir GÜVENLİK SINIRI DEĞİLDİR — yalnız yol kısayolu
    kolaylığıdır (bu araç ağdan gelen düşman girdi işlemez, doğrudan
    avukat/model çağırır; bkz. oa_hafiza.py'deki --arac sınıfı ile karıştırma)."""
    if yol is None:
        return None
    if os.path.isabs(yol) or not kok:
        return os.path.abspath(yol)
    return os.path.abspath(os.path.join(kok, yol))


def _atomik_tasi(gecici_yol, hedef_yol):
    """os.replace ile atomik taşıma; Windows'ta antivirüs/handle gecikmesi
    kaynaklı geçici PermissionError'a karşı kısa yeniden deneme (veri kaybı
    riski YOK — yalnız gecikme; bkz. udf_html2pdf.py'deki aynı desen)."""
    son_hata = None
    for _deneme in range(10):
        try:
            os.replace(gecici_yol, hedef_yol)
            return
        except PermissionError as e:
            son_hata = e
            time.sleep(0.15)
    raise son_hata


# ───────────── kardeş script yükleme (md_udf_html.py / udf_html2pdf.py) ────
def _sibling_yukle(dosya_adi, modul_adi):
    """Aynı dizindeki kardeş script'i dosya-yolundan yükler (paket değildir —
    dilekce_denetim.py'nin `_udf_yaz_yukle` desenindeki AYNI yaklaşım)."""
    yol = pathlib.Path(__file__).resolve().parent / dosya_adi
    if not yol.is_file():
        return None
    spec = importlib.util.spec_from_file_location(modul_adi, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def md_html_uret(metin, ham=False):
    """md_udf_html.py'yi yükleyip markdown → UDF-uyumlu inline-CSS HTML çevirir.
    Rehberin ZORUNLU kıldığı ara adım (html2udf girdisi)."""
    mod = _sibling_yukle("md_udf_html.py", "_oa_udf_yaz_md_udf_html")
    if mod is None:
        sys.exit("HATA: md_udf_html.py (kardeş script) bulunamadı — "
                  "UDF-HTML üretilemedi (beklenen konum: aynı klasör).")
    return mod.donustur(metin, ham=ham)


# ───────────────── gerçek yazıcı: `npx udf-cli html2udf` ────────────────────
def npx_kullanilabilir_mi(npx_yolu="npx", zaman_asimi=20):
    """npx + udf-cli oturum durumunu hızlıca sınar (ağ + login gerektirir).
    Yalnız TANI/TEST amaçlı — üretim akışı bunu önden çağırmaz, doğrudan
    `npx_ile_udf_uret` dener ve kendi hatasını raporlar. Döner: (uygun mu,
    açıklama)."""
    yol = shutil.which(npx_yolu)
    if yol is None:
        return False, "npx bulunamadı (Node.js kurulu olmayabilir)"
    try:
        # ÖNEMLİ (Windows): npx.CMD gibi PATHEXT uzantısı yalnız shutil.which
        # ile çözülür — CreateProcess çıplak "npx" adını PATHEXT'e göre
        # KENDİLİĞİNDEN bulmaz (WinError 2). Her zaman ÇÖZÜLMÜŞ yolu çağır.
        p = subprocess.run([yol, "-y", "udf-cli@latest", "whoami"],
                            capture_output=True, text=True, timeout=zaman_asimi)
    except Exception as e:
        return False, "udf-cli whoami çalıştırılamadı: %s" % e
    if p.returncode != 0:
        return False, "udf-cli oturumu yok — 'npx -y udf-cli@latest login' gerekir"
    return True, (p.stdout or "").strip()


def npx_ile_udf_uret(html_yolu, cikti_yolu, npx_yolu="npx", zaman_asimi=180):
    """Rehberin ZORUNLU kıldığı gerçek yazıcıyı çağırır: `npx -y udf-cli@latest
    html2udf <html> <udf>`. UDF içeriğini ASLA elle kurmaz (rehber A.2/D.1) —
    yalnız dış süreci çağırır, sonucu ATOMİK taşır.

    Döner: dict — basarili(bool), exit_kod(int|None), stdout(str), stderr(str),
    hata(str|None — yalnız basarisiz ise)."""
    yol = shutil.which(npx_yolu)
    if yol is None:
        return {"basarili": False, "exit_kod": None, "stdout": "", "stderr": "",
                "hata": ("npx bulunamadı (Node.js kurulu olmayabilir). Kurulum: "
                         "https://nodejs.org — ardından "
                         "'npx -y udf-cli@latest login' ile giriş yapın.")}

    tmp_udf = cikti_yolu + ".tmp-%d" % os.getpid()
    try:
        # bkz. npx_kullanilabilir_mi — çıplak "npx" değil, ÇÖZÜLMÜŞ yol çağrılır.
        p = subprocess.run(
            [yol, "-y", "udf-cli@latest", "html2udf", html_yolu, tmp_udf],
            capture_output=True, text=True, timeout=zaman_asimi)
    except subprocess.TimeoutExpired:
        return {"basarili": False, "exit_kod": None, "stdout": "", "stderr": "",
                "hata": "udf-cli html2udf zaman aşımına uğradı (%ds)" % zaman_asimi}
    except Exception as e:
        return {"basarili": False, "exit_kod": None, "stdout": "", "stderr": "",
                "hata": "udf-cli html2udf çalıştırılamadı: %s" % e}

    if p.returncode != 0 or not os.path.isfile(tmp_udf):
        return {"basarili": False, "exit_kod": p.returncode,
                "stdout": p.stdout or "", "stderr": p.stderr or "",
                "hata": ("udf-cli html2udf başarısız (exit %s). Oturum "
                          "gerekebilir: 'npx -y udf-cli@latest login'."
                          % p.returncode)}

    try:
        _atomik_tasi(tmp_udf, cikti_yolu)
    except Exception as e:
        return {"basarili": False, "exit_kod": p.returncode,
                "stdout": p.stdout or "", "stderr": p.stderr or "",
                "hata": "atomik taşıma başarısız: %s" % e}

    return {"basarili": True, "exit_kod": 0, "stdout": p.stdout or "",
            "stderr": p.stderr or "", "hata": None}


# ───────────────────────────────── main ────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Markdown → UYAP UDF teslim hattı (md → UDF-HTML → .udf [+ opsiyonel PDF]).")
    ap.add_argument("--girdi", "-g", metavar="YOL",
                    help="Girdi dosyası (.md veya .txt). Verilmezse stdin okunur.")
    ap.add_argument("--cikti", "-c", metavar="YOL",
                    help="Çıktı .udf dosyası (yazma modunda zorunlu).")
    ap.add_argument("--dogrula", metavar="YOL",
                    help="YAZMADAN — var olan bir .udf dosyasını GEÇERLİLİK "
                         "KAPISI ile denetler (zip/content.xml/XML/offset "
                         "round-trip). Diğer seçenekler yok sayılır.")
    ap.add_argument("--ham", action="store_true",
                    help="Markdown yorumlama; paragrafları birebir al.")
    ap.add_argument("--kok", metavar="KLASOR", default=None,
                    help="Göreli --girdi/--cikti/--html/--pdf yolları bu köke göre çözülür.")
    ap.add_argument("--html", metavar="YOL", default=None,
                    help="Ara UDF-HTML dosyasının yolu (verilmezse --cikti ile "
                         "aynı ad, '.udf.html' uzantılı; her koşuda üretilir/kalır — "
                         "hem html2udf girdisi hem PDF kaynağıdır).")
    ap.add_argument("--pdf", metavar="YOL", default=None,
                    help="Verilirse aynı UDF-HTML'den A4 PDF de üretilir (udf_html2pdf.py, PyMuPDF).")
    ap.add_argument("--baslik", default="Dilekçe", help="PDF meta başlığı (yalnız --pdf ile).")
    ap.add_argument("--font-dizini", default=None,
                    help="PDF için Times New Roman TTF dizini (yalnız --pdf ile).")
    ap.add_argument("--yerel-motor", action="store_true",
                    help="RESMİ REHBERE UYUMLU DEĞİL — ağsız yedek: eski hand-rolled "
                         "ZIP/XML motoru (yalnız hızlı yapısal denetim / npx yokken).")
    ap.add_argument("--npx", default="npx", metavar="KOMUT",
                    help="npx çalıştırılabilir yolu/adı (varsayılan: %(default)s).")
    ap.add_argument("--format-id", default=FORMAT_ID,
                    help="template format_id — yalnız --yerel-motor (varsayılan: %(default)s).")
    a = ap.parse_args()

    if a.dogrula:
        sonuc = udf_dogrula(a.dogrula)
        print("UDF GEÇERLİLİK KAPISI: %s" % a.dogrula)
        print("  content.xml var  : %s" % ("EVET" if sonuc["content_xml_var"] else "HAYIR"))
        print("  XML iyi biçimli  : %s" % ("EVET" if sonuc["xml_iyi_bicimli"] else "HAYIR"))
        print("  CDATA bulundu    : %s" % ("EVET" if sonuc["cdata_bulundu"] else "HAYIR"))
        if sonuc["karakter_sayisi"] is not None:
            print("  karakter (CDATA) : %d" % sonuc["karakter_sayisi"])
        if sonuc["paragraf_sayisi"] is not None:
            print("  paragraf sayısı  : %d" % sonuc["paragraf_sayisi"])
        print("  offset/uzunluk   : %s" % (
            "TUTARLI" if sonuc["offsetler_tutarli"]
            else ("TUTARSIZ" if sonuc["offsetler_tutarli"] is False else "—")))
        for h in sonuc["hatalar"]:
            print("  [HATA] %s" % h, file=sys.stderr)
        print("SONUÇ: %s" % ("GEÇERLİ ✓" if sonuc["gecerli"] else "GEÇERSİZ ✗"))
        sys.exit(0 if sonuc["gecerli"] else 1)

    if not a.cikti:
        sys.exit("HATA: --cikti gerekli (yazma modu) ya da --dogrula (denetim modu) verin.")

    girdi = _kok_coz(a.girdi, a.kok)
    cikti = _kok_coz(a.cikti, a.kok)
    pdf_yolu = _kok_coz(a.pdf, a.kok) if a.pdf else None

    # NOT (P0-10 regresyon düzeltmesi): --html AÇIKÇA verilmediyse ara HTML
    # SİSTEM TEMP dizinine yazılır, --cikti'nin yanına DEĞİL. `_oa/cikti`
    # içine (dilekçeyle AYNI klasöre) bırakılan bir kopya, pipeline_kayit.py
    # `_dilekce_sekilli_makbuzsuz_uyarisi` taramasını YANLIŞLIKLA tetikler
    # (dosya İÇERİĞİ "Sayın Mahkeme"/"netice-i talep" gibi dilekçe-şekilli
    # desenleri taşıdığından, üst dizindeki taslaktan DAHA YENİ görünen bir
    # "makbuzsuz aday" gibi okunur). Ara dosya işini bitirince (finally)
    # SİLİNİR — kullanıcı --html ile AÇIKÇA bir yol verdiyse bu onun bilinçli
    # tercihidir, dokunulmaz/silinmez.
    html_gecici = a.html is None
    if html_gecici:
        _fd, html_yolu = tempfile.mkstemp(prefix="oa-udf-ara-", suffix=".html")
        os.close(_fd)
    else:
        html_yolu = _kok_coz(a.html, a.kok)

    try:
        if girdi:
            with open(girdi, "r", encoding="utf-8", errors="replace") as f:
                metin = f.read()
        else:
            if _sys.stdin is None:
                sys.exit("HATA: --girdi verilmedi ve stdin yok.")
            metin = _sys.stdin.read()

        # BMP-dışı karakter (emoji vb.) tespiti — her iki motorda da geçerli bir uyarı.
        bmp_disi = sum(1 for ch in metin if ord(ch) > 0xFFFF)
        if bmp_disi:
            print("UYARI: metinde %d adet BMP-dışı karakter (emoji vb.) var; bu "
                  "karakterleri dilekçede kullanmak genellikle istenmez."
                  % bmp_disi, file=sys.stderr)

        # UDF-HTML HER ZAMAN üretilir/yazılır — hem `npx html2udf` girdisi hem
        # PDF kaynağıdır (--yerel-motor seçilse BİLE PDF bacağı bundan üretilir;
        # PDF, UDF motorundan BAĞIMSIZDIR).
        html = md_html_uret(metin, ham=a.ham)
        with open(html_yolu, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("UDF-HTML yazıldı: %s%s (%d karakter)"
              % (html_yolu, " (geçici)" if html_gecici else "", len(html)))

        if a.yerel_motor:
            # ── YEDEK MOTOR: ağsız, hand-rolled — rehber uyumu GARANTİ DEĞİL ──
            print("UYARI: --yerel-motor kullanılıyor — bu motorun ürettiği .udf, "
                  "Yargı Pro UDF rehberinin ('UDF yalnız udf-cli ile yazılır') "
                  "gerçek UYAP editör uyumunu GARANTİ ETMEZ; yalnız hızlı yapısal "
                  "ön-denetim / ağsız ortam için tutulur. Gerçek teslim için "
                  "--yerel-motor OLMADAN (varsayılan npx motoru) yeniden üretin.",
                  file=sys.stderr)
            if "]]>" in metin:
                print("UYARI: metinde ']]>' dizisi var; CDATA'da bölünerek yazılıyor. "
                      "udf_metin.py tek-CDATA okuyucusu bu noktada metni kısaltabilir.",
                      file=sys.stderr)

            xml_str, tam, paragraflar = udf_uret(metin, ham_mod=a.ham, format_id=a.format_id)
            udf_yaz(cikti, xml_str)

            geri = udf_metni_geri_oku(cikti)
            if geri is None:
                sys.exit("HATA: round-trip — geri okumada content.xml/CDATA bulunamadı.")
            korundu = (geri == tam)

            print("UDF yazıldı (yerel motor): %s" % cikti)
            print("  paragraf : %d" % len(paragraflar))
            print("  karakter : %d (CDATA)" % len(tam))
            print("  format_id: %s" % a.format_id)
            print("  round-trip (udf_metin.py mantığı): %s"
                  % ("KORUNDU ✓" if korundu else "FARK VAR ✗"))
            if not korundu:
                i = next((k for k in range(min(len(geri), len(tam)))
                          if geri[k] != tam[k]), min(len(geri), len(tam)))
                print("  ! ilk sapma indeksi: %d  (yazılan=%d, okunan=%d karakter)"
                      % (i, len(tam), len(geri)), file=sys.stderr)
                sys.exit(2)
        else:
            # ── VARSAYILAN: rehbere birebir — UDF-HTML (yukarıda üretildi) → npx udf-cli html2udf ──
            sonuc = npx_ile_udf_uret(html_yolu, cikti, npx_yolu=a.npx)
            if not sonuc["basarili"]:
                print("HATA: %s" % sonuc["hata"], file=sys.stderr)
                if sonuc["stderr"]:
                    print("  --- npx stderr ---\n%s" % sonuc["stderr"], file=sys.stderr)
                sys.exit(sonuc["exit_kod"] or 1)

            dogrulama = udf_dogrula(cikti)
            print("UDF yazıldı (npx udf-cli html2udf): %s" % cikti)
            if dogrulama["paragraf_sayisi"] is not None:
                print("  paragraf sayısı  : %d" % dogrulama["paragraf_sayisi"])
            if dogrulama["karakter_sayisi"] is not None:
                print("  karakter (CDATA) : %d" % dogrulama["karakter_sayisi"])
            print("  GEÇERLİLİK KAPISI: %s" % ("GEÇERLİ ✓" if dogrulama["gecerli"] else "GEÇERSİZ ✗"))
            if not dogrulama["gecerli"]:
                for h in dogrulama["hatalar"]:
                    print("  [HATA] %s" % h, file=sys.stderr)
                sys.exit(1)

        if pdf_yolu:
            mod = _sibling_yukle("udf_html2pdf.py", "_oa_udf_yaz_html2pdf")
            if mod is None:
                sys.exit("HATA: udf_html2pdf.py (kardeş script) bulunamadı — PDF üretilemedi.")
            sayfa, font_gomuldu = mod.pdf_uret(html_yolu, pdf_yolu, baslik=a.baslik,
                                                font_dizini=a.font_dizini)
            print("PDF yazıldı: %s (%d sayfa, font gömüldü: %s)"
                  % (pdf_yolu, sayfa, "EVET" if font_gomuldu else "HAYIR"))
    finally:
        # Geçici ara HTML'i temizle (--html AÇIKÇA verilmediyse) — kalıcı
        # çıktı klasörlerini (_oa/cikti dâhil) kirletmemek için EN İYİ ÇABA
        # (silinemezse sessizce geç; bu bir güvenlik/veri-kaybı sınırı değil).
        if html_gecici:
            try:
                os.remove(html_yolu)
            except OSError:
                pass


if __name__ == "__main__":
    main()
