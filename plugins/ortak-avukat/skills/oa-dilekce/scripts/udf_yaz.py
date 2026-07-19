#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
udf_yaz.py — düz metin / markdown → UYAP UDF YAZICI (oa-dilekce yardımcısı)

Bir dilekçe metnini UYAP'a yüklenebilir `.udf` dosyasına çevirir. UDF bir ZIP
arşividir; içine `content.xml` yazılır. Metin, `udf_metin.py` okuyucusunun
beklediği BİREBİR yapıda taşınır:

    <content><![CDATA[ TÜM METİN ]]></content>

Bu okuyucuyla tam uyumludur (round-trip): yazılan `.udf`, `udf_metin.py`
mantığıyla geri okunduğunda metin korunur.

UDF `content.xml` şeması (UYAP editör / Swing tabanlı):
  - kök  : <template format_id="...">
  - metin: <content><![CDATA[...]]></content>   (ATTRIBUTESİZ — okuyucu bunu arar)
  - düzen: <properties><pageFormat .../></properties>
  - blok : <elements resolver="hvl-default"> altında her paragraf için
           <paragraph Alignment="N"><content startOffset="S" length="L"/></paragraph>
           startOffset/length CDATA metniyle BİREBİR tutar; paragraflar metni
           boşluksuz böler (her paragraf sonundaki '\n' dahildir).
  - stil : <styles><style name="default" .../></styles>

DETERMİNİST MOTOR: bu script hukuki değerlendirme YAPMAZ; yalnız biçim üretir.

Kullanım (Windows/PowerShell — 'python', 'python3' DEĞİL):
  python udf_yaz.py --girdi taslak.md --cikti dilekce.udf
  Get-Content taslak.md -Raw | python udf_yaz.py --cikti dilekce.udf
  python udf_yaz.py --girdi taslak.txt --cikti dilekce.udf --ham   # md yorumlama yok

Yalnız standart kütüphane (zipfile, xml, argparse) — ek bağımlılık yoktur.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import re
import sys
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
    """content.xml'i UDF (ZIP) arşivine yazar."""
    with zipfile.ZipFile(cikti_yolu, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml_str.encode("utf-8"))


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


# ───────────────────────────────── main ────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Düz metin / markdown → UYAP UDF yazıcı (deterministik biçim motoru).")
    ap.add_argument("--girdi", "-g", metavar="YOL",
                    help="Girdi dosyası (.md veya .txt). Verilmezse stdin okunur.")
    ap.add_argument("--cikti", "-c", metavar="YOL", required=True,
                    help="Çıktı .udf dosyası.")
    ap.add_argument("--ham", action="store_true",
                    help="Markdown yorumlama; metni birebir satır-paragraf al.")
    ap.add_argument("--format-id", default=FORMAT_ID,
                    help="template format_id (varsayılan: %(default)s).")
    a = ap.parse_args()

    if a.girdi:
        with open(a.girdi, "r", encoding="utf-8", errors="replace") as f:
            metin = f.read()
    else:
        if _sys.stdin is None:
            sys.exit("HATA: --girdi verilmedi ve stdin yok.")
        metin = _sys.stdin.read()

    if "]]>" in metin:
        print("UYARI: metinde ']]>' dizisi var; CDATA'da bölünerek yazılıyor. "
              "udf_metin.py tek-CDATA okuyucusu bu noktada metni kısaltabilir.",
              file=sys.stderr)

    # BMP-dışı karakter (emoji vb.) tespiti: offset'ler UTF-16 code unit olarak
    # hesaplandığı için UYAP hizalaması korunur; yine de avukat bilinçli olsun diye işaretle.
    bmp_disi = sum(1 for ch in metin if ord(ch) > 0xFFFF)
    if bmp_disi:
        print("UYARI: metinde %d adet BMP-dışı karakter (emoji vb.) var; offset/length "
              "UTF-16 code unit olarak hesaplanıyor (UYAP/Swing hizası korunur). "
              "Yine de bu karakterleri dilekçede kullanmak genellikle istenmez."
              % bmp_disi, file=sys.stderr)

    xml_str, tam, paragraflar = udf_uret(metin, ham_mod=a.ham,
                                         format_id=a.format_id)
    udf_yaz(a.cikti, xml_str)

    # round-trip: udf_metin.py mantığıyla geri oku ve birebir karşılaştır
    geri = udf_metni_geri_oku(a.cikti)
    if geri is None:
        sys.exit("HATA: round-trip — geri okumada content.xml/CDATA bulunamadı.")
    korundu = (geri == tam)

    print("UDF yazıldı: %s" % a.cikti)
    print("  paragraf : %d" % len(paragraflar))
    print("  karakter : %d (CDATA)" % len(tam))
    print("  format_id: %s" % a.format_id)
    print("  round-trip (udf_metin.py mantığı): %s"
          % ("KORUNDU ✓" if korundu else "FARK VAR ✗"))
    if not korundu:
        # ilk sapma noktasını göster (teşhis için)
        i = next((k for k in range(min(len(geri), len(tam)))
                  if geri[k] != tam[k]), min(len(geri), len(tam)))
        print("  ! ilk sapma indeksi: %d  (yazılan=%d, okunan=%d karakter)"
              % (i, len(tam), len(geri)), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
