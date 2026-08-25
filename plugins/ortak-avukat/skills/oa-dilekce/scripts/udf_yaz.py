#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
udf_yaz.py — markdown → UYAP UDF TESLİM HATTI (oa-dilekce yardımcısı)

GÜNCEL SÖZLEŞME (v0.5.8.4 — 372 sahası A/B hükmü, ders 10-D): elle kurulan
`content.xml`'li UDF'ler **UYAP editöründe AÇILMADI** (7 dosya karantina);
A/B testi python re-zip'ini ve pageFormat kenar yamasını AKLADI — suçlu,
yerel motorun `content.xml` içeriğidir (styles bloğunda `name="hvl-default"`
STİL TANIMI yok; `udf_dogrula` bu imzayı artık GEÇERSİZ sayar). Yargı Pro
rehberi (`udf_tiff_pdf_guide` MCP aracı / `yargi-udf-tiff-pdf-guide` skill,
sürüm 2026-06-22) zaten açıkça söyler: **"UDF opak bir UYAP biçimidir — yalnız
`udf-cli` üretebilir/okuyabilir; ASLA elle yazma/düzenleme; her zaman
`html2udf`, ASLA `md2udf`."**

BİRİNCİL (ve varsayılan) yazma hattı:

    md taslak → UDF-HTML (md_udf_html.py, inline-CSS, rehber şemasına birebir)
             → `npx -y udf-cli@latest html2udf` (GERÇEK UYAP yazıcısı)
             → [+opsiyonel] aynı UDF-HTML'den PDF önizleme (udf_html2pdf.py)

`npx`/`udf-cli` bulunamazsa VEYA oturum (login) gerekiyorsa: script FAIL-CLOSED
davranır — çıkış kodu != 0, stderr'e NET talimat (`npx -y udf-cli@latest
login` İNSAN varsa; başsız/otomasyon ortamda `issue_cli_login_code` MCP aracı
çağrılıp dönen tek-kullanımlık kodla `udf-cli login --token <kod>`), ve HİÇBİR
`.udf` dosyası YAZILMAZ. Yerel motora SESSİZCE düşmek YASAKTIR — bozuk ama
"üretildi" görünen bir UDF, hiç üretilmemiş bir UDF'den DAHA KÖTÜDÜR
(sessiz-yanlış > açık-eksik).

İSTİSNA — BİLİNÇLİ RİSK BAYRAĞI: `--yerel-motor` EMEKLİDİR (artık HATA verir
ve yönlendirir); çevrimdışı yerel üretim yalnız `--yerel-motor-riskli` ile
koşar. Bu yol resmî okuyucu (`udf2md`) doğrulamasını dener; OK gelmezse
çıktının YANINA `<ad>.DOGRULANMADI` işaret dosyası bırakır — üretim kırılmaz
ama doğrulanmamışlık diskte görünür kalır (işaretli dosya UYAP'a yüklenmez;
işareti görsel teyit sonrası avukat siler).

ÜRETİM MAKBUZU (v0.5.8.4; B7 garantisi): her `.udf` üretimi, dava klasöründe
`_oa` dizini varsa `_oa/defter/udf-uretim-makbuz.jsonl`'e tek satır iz düşer
(defter alt dizini yoksa makedirs ile KURULUR; `_oa` da yoksa sessiz atlanır)
— makbuz kayıt aracıdır, kapı değildir; yazılamaması üretimi asla kırmaz.

`--dogrula` var olan HERHANGİ bir `.udf` dosyasını (gerçek `udf-cli` çıktısı
dâhil) mekanik GEÇERLİLİK KAPISI'ndan geçirir (zip açılır mı / content.xml var
mı / XML iyi biçimli mi / `hvl-default` STİL TANIMI var mı / CDATA+offset
tutarlı mı) — bu bir hukuki/biçimsel
KALİTE hükmü DEĞİLDİR, yalnız yapısal "var/yok" ve "tutarlı/tutarsız" denetimi.

DETERMİNİST MOTOR: bu script hukuki değerlendirme YAPMAZ; yalnız biçim üretir.

Kullanım (Windows/PowerShell — 'python', 'python3' DEĞİL):
  python udf_yaz.py --girdi taslak.md --cikti dilekce.udf              # npx udf-cli html2udf
  python udf_yaz.py --girdi taslak.md --cikti dilekce.udf --pdf dilekce.pdf
  Get-Content taslak.md -Raw | python udf_yaz.py --cikti dilekce.udf
  python udf_yaz.py --girdi taslak.txt --cikti dilekce.udf --ham       # md yorumlama yok
  python udf_yaz.py --dogrula dilekce.udf                              # yazmadan mekanik denetim

Bu script yalnızca standart kütüphane (argparse, subprocess, zipfile, xml)
kullanır; gerçek yazıcı `npx` (Node.js) + `udf-cli` çağrılarak dış süreç
olarak çalıştırılır (login-gated, ağ gerektirir — rehberin Kimlik Doğrulama
bölümü).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import contextlib
import datetime
import hashlib
import importlib.util
import io
import json
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


def utf16_uzunluk(s):
    """UYAP editörü (Java/Swing) offset'leri UTF-16 CODE UNIT sayar; Python str ise
    code-point sayar. BMP-dışı karakter (emoji, U+10000+) Python'da tek code-point
    ama UTF-16'da İKİ code unit'tir (surrogate çifti). Offset'leri Swing ile aynı
    birime çekmek için UTF-16 code unit sayısını döndür; aksi halde tek bir emoji
    o paragraftan sonraki TÜM offset'leri 1 kaydırır ve UYAP'ta biçim/aralık bozulur.
    Yalnız `udf_dogrula`'nın (mekanik geçerlilik kapısı) offset tutarlılık
    denetiminde kullanılır — bu script artık kendi offset'ini ÜRETMEZ
    (gerçek yazıcı `udf-cli`'dir)."""
    return len(s.encode("utf-16-le")) // 2


# ───────────────── UDF GEÇERLİLİK KAPISI (mekanik denetim, hüküm YOK) ───────
def udf_dogrula(yol, resmi_okuyucu=True, okuyucu_fn=None):
    """Var olan bir `.udf` dosyasının UYAP okuyucusunun (udf_metin.py / oa_ingest
    udf_isle) beklediği yapıya uyup uymadığını MEKANİK olarak denetler. Bu
    denetim gerçek `udf-cli html2udf` çıktısı ÜZERİNDE çalışır — script artık
    kendi content.xml'ini üretmediğinden bu, "üretilen dosya bozuk mu" sorusuna
    yazımdan SONRA bağımsız bir ikinci kanıt sağlar (dosya sonradan tahrif
    edilmişse de yakalar).

    `resmi_okuyucu=True` (varsayılan) 5. denetimi ekler: dosyayı ÜRETEN aracın
    kendi okuyucusuyla (`udf-cli udf2md`) geri okuma — 2026/307 saha reçetesinin
    3. adımı. İlk dört denetim BİZİM varsayımımızı sınar; sahada bizi yakan
    hata sınıfı ise tam olarak "bizim round-trip'imizi geçen ama UYAP'ın
    açmadığı dosya"ydı, yani kendi kendini doğrulamanın kör noktasıydı. Ağ/
    oturum yoksa bu bacak GÖRÜNÜR biçimde "YAPILAMADI" der, "doğrulandı"
    SAYILMAZ ve bloklamaz (ortam koşulu, dosyanın kusuru değil).
    `okuyucu_fn` yalnız TEST enjeksiyonu içindir (ağsız koşu).

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
         bozulur).

    İMZALI-NÜSHA PROFİLİ (B6, v0.5.8.5): arşivde `sign.sgn` (ya da `.p7s`)
    girdisi varsa sonuçta `imzali_nusha=True` döner ve YALNIZ bu profilde
    editör-kaynaklı sapmalar GEÇERSİZLİK sebebi SAYILMAZ:
      (a) float kenar değerleri (14.170000000000032 gibi — kenar zaten
          mekanik kapının denetim konusu değildir, burada belgelenir),
      (b) prolog öncesi fazla boşluk/satır (katı parser'ı kıran sınıf),
      (c) zip data-descriptor bayrağı (zipfile merkez dizinden okur; ek
          denetim kurulmaz — editörün akış yazıcısının olağan izidir),
      (d) offset döşemesinde 1-boşluk sınıfı sapma (TEK küçük boşluk
          toleransı — kaplanmayan kuyruk metinse ya da 1 birimden büyükse
          imzalıda BİLE red).
    GEREKÇE (v0.5.5.2 dersinin devamı — resmî gerçeklik > bizim varsayım):
    gerçek e-imzalı, MAHKEMECE KABUL EDİLMİŞ bir dosyada 1 boşluk sapması
    ölçüldü; katı kural o gerçek-geçerli dosyayı yanlış-BLOK'lardı. İMZASIZ
    dosyada tolerans YOKTUR — katı invaryant aynen sürer (imzasız dosya bizim
    üretim hattımızın taze ürünüdür, sapması üretim hatasıdır; imzalı nüsha
    ise editörden/eimzadan geçmiş resmî gerçekliktir). Uygulanan her tolerans
    `imzali_tolerans` listesinde GÖRÜNÜR bırakılır (sessiz gevşeme yok).

    Döner: dict —
      gecerli (bool), hatalar (list[str] — boşsa geçerli),
      content_xml_var (bool), xml_iyi_bicimli (bool), cdata_bulundu (bool),
      karakter_sayisi (int|None), paragraf_sayisi (int|None),
      offsetler_tutarli (bool|None),
      imzali_nusha (bool), imzali_tolerans (list[str] — uygulanan toleranslar),
      resmi_okuyucu ("OK"|"RET"|"YAPILAMADI"|None — None = hiç denenmedi),
      resmi_okuyucu_not (str|None), resmi_okuyucu_karakter (int|None).
    """
    sonuc = {
        "gecerli": False, "hatalar": [],
        "content_xml_var": False, "xml_iyi_bicimli": False,
        "cdata_bulundu": False, "karakter_sayisi": None,
        "paragraf_sayisi": None, "offsetler_tutarli": None,
        "hvl_stil_tanimi": None,
        "imzali_nusha": False, "imzali_tolerans": [],
        "resmi_okuyucu": None, "resmi_okuyucu_not": None,
        "resmi_okuyucu_karakter": None,
        "notlar": [], "kapsanmayan_bosluk": None, "imza_dosyasi": None,
    }

    # 1) zip açılır mı
    try:
        zf = zipfile.ZipFile(yol)
    except (zipfile.BadZipFile, FileNotFoundError, OSError) as e:
        sonuc["hatalar"].append("ZIP açılamadı: %s" % e)
        return sonuc

    # E-İMZA TESPİTİ: UYAP editöründe imzalanmış UDF arşivinde `sign.sgn`
    # (PKCS#7/CMS) bulunur. Bu bilgi teslim öncesi KRİTİKTİR: imzalı dosyanın
    # içeriği sonradan değiştirilirse imza geçersiz kalır; bu yüzden imzalı
    # dosya "düzenlenip yeniden kaydedilecek" bir taslak DEĞİL, teslim edilecek
    # nüshadır. Script imzanın GEÇERLİLİĞİNİ doğrulamaz (kripto doğrulama UYAP/
    # e-imza altyapısının işidir) — yalnız VARLIĞINI bildirir; sahte kesinlik yok.
    # (B6: tespit content.xml denetiminden ÖNCE yapılır ki imzalı-nüsha profili
    # sonraki tüm bacaklarda bilinsin.)
    adlar = zf.namelist()
    sonuc["imza_dosyasi"] = next(
        (a for a in adlar if a.lower().endswith((".sgn", ".p7s"))), None)
    sonuc["imzali_nusha"] = sonuc["imza_dosyasi"] is not None
    # NOT (B6-c): imzalı nüshalarda zip girdileri data-descriptor bayrağı
    # (genel-amaç bit 3, editörün akış yazıcısı) taşıyabilir. zipfile merkez
    # dizinden okuduğu için bu okuma başarısını etkilemez; ayrıca (a) float
    # kenar değerleri mekanik kapının denetim konusu DEĞİLDİR — ikisi de
    # geçersizlik sebebi sayılmaz (imzalı ya da imzasız; burada belgelenir).

    # 2) content.xml var mı
    hedef = next((a for a in adlar
                  if a.lower().endswith("content.xml")), None)
    if hedef is None:
        sonuc["hatalar"].append("content.xml arşivde bulunamadı")
        return sonuc
    sonuc["content_xml_var"] = True
    ham = zf.read(hedef).decode("utf-8", errors="replace")

    # 3) XML iyi biçimli mi
    # B6-b (İMZALI-NÜSHA PROFİLİ): editörün kaydettiği content.xml'de prolog
    # ÖNCESİ fazla boşluk/satır görülebilir; katı parser bunu "XML declaration
    # not at start of entity" ile keser. Gerçek e-imzalı, mahkemece kabul
    # edilmiş dosyayı yanlış-BLOK'lamamak için YALNIZ imzalı nüshada baştaki
    # boşluk kırpılarak parse edilir — imzasız dosyada tolerans YOK (katı
    # invaryant sürer; sapma bizim üretim hattımızın hatası olurdu).
    parse_metni = ham
    if sonuc["imzali_nusha"]:
        kirpik = ham.lstrip("\ufeff\r\n\t ")
        if kirpik != ham:
            sonuc["imzali_tolerans"].append(
                "prolog öncesi fazla boşluk/satır (editör-kaynaklı) tolere edildi")
            parse_metni = kirpik
    try:
        kok = ET.fromstring(parse_metni)
        sonuc["xml_iyi_bicimli"] = True
    except ET.ParseError as e:
        sonuc["hatalar"].append("content.xml iyi biçimli değil: %s" % e)
        return sonuc

    # 3.5) hvl-default STİL TANIMI (v0.5.8.4 — 372 A/B saha hükmü): UYAP'ta
    # AÇILMAYAN elle üretimlerin ayırt edici imzası, `<elements
    # resolver="hvl-default" ...>` yazıp `<styles>` bloğunda `name="hvl-default"`
    # STİL TANIMI vermemekti (açılan gerçek üretici çıktılarında tanım VAR).
    # DİKKAT: `<elements ... name="hvl-default">` bu denetimi SAĞLAMAZ —
    # ölçüt tam olarak `<style>` etiketidir; ayırt edici fark budur.
    sonuc["hvl_stil_tanimi"] = bool(
        re.search(r'<style\b[^>]*name="hvl-default"', ham))
    if not sonuc["hvl_stil_tanimi"]:
        sonuc["hatalar"].append(
            "hvl-default stil tanımı yok (elle-üretim imzası)")

    # 4) CDATA + offset/uzunluk tutarlılığı (round-trip'in temeli)
    m = re.search(r"<content>\s*<!\[CDATA\[(.*?)\]\]>\s*</content>", ham, re.S)
    if not m:
        sonuc["hatalar"].append("<content><![CDATA[...]]></content> bulunamadı")
        return sonuc
    sonuc["cdata_bulundu"] = True
    tam = m.group(1)
    sonuc["karakter_sayisi"] = len(tam)
    toplam_u16 = utf16_uzunluk(tam)

    # NOT: gerçek `udf-cli` çıktısında tablo hücreleri
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

    # DÜZELTME (v0.5.5.2 — YANLIŞ-BLOK, saha kanıtlı): süreklilik denetimi
    # YALNIZ <content> elemanlarına bakıyordu. Gerçek `udf-cli html2udf`
    # çıktısında CDATA gövdesindeki bazı karakterler <content> DIŞINDA, kendi
    # etiketiyle temsil edilir — ölçülen dosyada `<tab startOffset=".." length="1"/>`
    # (8 adet). Her biri imleci bir karakter kaydırdığından, avukatın UYAP'ta
    # AÇILDIĞINI TEYİT ETTİĞİ 46.336 karakterlik gerçek dilekçe "offset süreksiz:
    # beklenen 61, bulunan 62" diyerek GEÇERSİZ işaretleniyordu — yani kapı, tam
    # da korumaya çalıştığı teslimi kesiyordu. Denetlenen invaryant "yalnız
    # paragraflar ardışık" DEĞİL, "offset taşıyan TÜM elemanlar CDATA'yı
    # boşluksuz ve örtüşmesiz döşer"dir. Etiket adı beyaz-listelenmez (yarın
    # <space/> gelirse yine yanlış-BLOK olurdu): ölçüt attribute'un VARLIĞIdır.
    ofsetli = []
    hatali_attr = False
    for el in kok.iter():
        if "startOffset" not in el.attrib:
            continue
        try:
            ofsetli.append((int(el.attrib["startOffset"]),
                            int(el.attrib.get("length", 0)), el.tag))
        except (TypeError, ValueError):
            hatali_attr = True
            break

    imlec, tutarli = 0, True
    if hatali_attr:
        tutarli = False
        sonuc["hatalar"].append("startOffset/length sayıya çevrilemedi")
    else:
        # Belge sırası değil OFFSET sırası esas alınır — denetlenen şey sıralama
        # değil, döşemenin örtüşmesiz ve METİN KAYBI'sız olmasıdır.
        #
        # DÜZELTME (v0.5.5.2, ikinci saha vakası — UYAP EDİTÖRÜNDE KAYDEDİLMİŞ
        # dosya): editörün ürettiği `content.xml`'de BOŞ PARAGRAF'ın ayraç
        # `\n`'i hiçbir offset'li elemanla kaplanmaz. Avukatın imzalayıp UYAP'a
        # yükleyeceği 51.243 karakterlik gerçek dilekçe bu yüzden "boşluk"
        # sayılıp GEÇERSİZ işaretlendi — resmî okuyucu ise dosyayı sorunsuz
        # okuyordu. Yani "kaplanmayan her karakter kayıptır" varsayımı YANLIŞ.
        # Doğru ölçüt İÇERİKtir: kaplanmayan aralık YALNIZ boşluk karakteri
        # (paragraf ayracı) ise yapısaldır — görünür NOT düşülür, teslim
        # kesilmez; içinde METİN varsa gerçek kayıptır ve BLOKLAR.
        bosluk_notlari = []
        for start, length, etiket in sorted(ofsetli):
            if start < imlec:
                tutarli = False
                sonuc["hatalar"].append(
                    "offset örtüşmesi: beklenen %d, bulunan %d (<%s>)"
                    % (imlec, start, etiket))
                break
            if start > imlec:
                kapsanmayan = tam[imlec:start]
                if kapsanmayan.strip():
                    tutarli = False
                    sonuc["hatalar"].append(
                        "offset boşluğu METİN İÇERİYOR (%d-%d, <%s> öncesi): %r — "
                        "bu karakterler CDATA'da var ama hiçbir elemanla "
                        "kaplanmıyor (metin kaybı)."
                        % (imlec, start, etiket, kapsanmayan[:60]))
                    break
                bosluk_notlari.append((imlec, start))
            imlec = start + length
        if bosluk_notlari:
            sonuc["kapsanmayan_bosluk"] = bosluk_notlari
            sonuc["notlar"] = sonuc.get("notlar") or []
            sonuc["notlar"].append(
                "%d yerde offset'siz boşluk karakteri var (boş paragraf ayracı — "
                "UYAP editöründe kaydedilmiş dosyalarda olağandır, metin kaybı DEĞİL)."
                % len(bosluk_notlari))
    if tutarli and imlec != toplam_u16:
        # B6-d (İMZALI-NÜSHA PROFİLİ — TEK küçük boşluk toleransı): gerçek
        # e-imzalı, mahkemece KABUL EDİLMİŞ bir dosyada offset döşemesinin
        # CDATA'yı 1 boşluk EKSİK kapladığı ÖLÇÜLDÜ; katı kural o gerçek-
        # geçerli dosyayı yanlış-BLOK'lardı (v0.5.5.2 dersinin devamı: resmî
        # gerçeklik > bizim varsayım). Tolerans BİLİNÇLİ olarak dardır:
        #   - yalnız İMZALI nüshada (imzasızda katı invaryant aynen sürer —
        #     imzasız dosya bizim hattımızın taze ürünüdür, sapması hatadır),
        #   - yalnız 1 UTF-16 birimlik EKSİK kaplama,
        #   - yalnız kaplanmayan kuyruk BOŞLUK SINIFI ise (metinse kayıptır
        #     ve imzalı nüshada BİLE bloklar).
        fark = toplam_u16 - imlec
        # kuyruk dilimi UTF-16 biriminde alınır (BMP-dışı karakterlerde
        # code-point indeksi kayar); fark=1 kuyruk tek BMP karakteridir.
        kalan = (tam.encode("utf-16-le")[2 * imlec:]
                 .decode("utf-16-le", "replace") if fark > 0 else "")
        if sonuc["imzali_nusha"] and fark == 1 and kalan.isspace():
            sonuc["imzali_tolerans"].append(
                "offset döşemesi CDATA'yı 1 boşluk eksik kapladı (%d/%d) — "
                "imzalı nüshada tolere edildi (imzasızda tolerans YOK)"
                % (imlec, toplam_u16))
        else:
            tutarli = False
            sonuc["hatalar"].append(
                "paragraf uzunlukları toplamı (%d) CDATA UTF-16 uzunluğuyla (%d) uyuşmuyor"
                % (imlec, toplam_u16))
    sonuc["offsetler_tutarli"] = tutarli
    if sonuc["imzali_tolerans"]:
        # sessiz gevşeme yok: uygulanan toleranslar hem ayrı listede hem
        # notlarda görünür kalır (istisna defterine yazım çağıran taraftadır —
        # bkz. _istisna_kaydi_yaz; bu fonksiyon dava kökünü bilmez).
        sonuc["notlar"].append(
            "imzalı-nüsha profili: %d editör-kaynaklı sapma tolere edildi "
            "(imzasız dosyada bu toleranslar YOKTUR)."
            % len(sonuc["imzali_tolerans"]))

    # 5) RESMİ OKUYUCU TANIĞI (dışarıdan kanıt) — bkz. `npx_ile_udf_oku` notu.
    if resmi_okuyucu:
        r = (okuyucu_fn or npx_ile_udf_oku)(yol)
        if not r.get("calisti"):
            sonuc["resmi_okuyucu"] = "YAPILAMADI"
            sonuc["resmi_okuyucu_not"] = r.get("hata") or "sebep bildirilmedi"
        elif not r.get("basarili"):
            sonuc["resmi_okuyucu"] = "RET"
            sonuc["resmi_okuyucu_not"] = r.get("hata") or "resmî okuyucu reddetti"
            sonuc["hatalar"].append(
                "RESMİ OKUYUCU REDDETTİ — %s. (Bizim ayrıştırıcımız dosyayı "
                "okuyabiliyor olsa BİLE bu dosya UYAP tarafında açılmayabilir; "
                "sahada bizi yakan hata sınıfı tam olarak budur.)" % sonuc["resmi_okuyucu_not"])
        else:
            resmi_metin = r.get("metin") or ""
            sonuc["resmi_okuyucu_karakter"] = len(resmi_metin)
            # "Açılıyor ama boş/kırpık" hâlini yakala: resmî okuyucunun döndürdüğü
            # metin, CDATA gövdesinin yarısından kısaysa içerik kaybı vardır.
            # (Uzun olması NORMALDİR — udf2md markdown imleri ekler.)
            if len(resmi_metin.strip()) < _RESMI_OKUYUCU_ASGARI_ORAN * len(tam.strip()):
                sonuc["resmi_okuyucu"] = "RET"
                sonuc["resmi_okuyucu_not"] = (
                    "resmî okuyucu %d karakter döndürdü, CDATA gövdesi %d karakter"
                    % (len(resmi_metin.strip()), len(tam.strip())))
                sonuc["hatalar"].append(
                    "RESMİ OKUYUCU İÇERİK KAYBI — %s (dosya açılıyor ama gövdenin "
                    "önemli kısmı okunamıyor)." % sonuc["resmi_okuyucu_not"])
            else:
                sonuc["resmi_okuyucu"] = "OK"

    if not sonuc["hatalar"]:
        sonuc["gecerli"] = True
    return sonuc


def _resmi_okuyucu_bas(sonuc, akis=None):
    """Resmî okuyucu bacağının durumunu GÖRÜNÜR biçimde basar. "YAPILAMADI"
    hâli özellikle susturulmaz: doğrulanmamış bir dosyayı doğrulanmış sanmak,
    hiç doğrulamamaktan daha tehlikelidir."""
    durum = sonuc.get("resmi_okuyucu")
    if durum is None:
        return
    akis = akis or sys.stdout
    if durum == "OK":
        print("  resmî okuyucu    : OK (udf2md geri okudu, %d karakter)"
              % (sonuc.get("resmi_okuyucu_karakter") or 0), file=akis)
    elif durum == "YAPILAMADI":
        print("  resmî okuyucu    : YAPILAMADI — %s  ⚠ bu dosya UYAP tarafında "
              "AÇILDIĞI DOĞRULANMADI (yalnız kendi ayrıştırıcımız onayladı)"
              % (sonuc.get("resmi_okuyucu_not") or "sebep bildirilmedi"), file=akis)
    else:
        print("  resmî okuyucu    : RET — %s"
              % (sonuc.get("resmi_okuyucu_not") or ""), file=akis)


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


_KENAR_PT = "42.52"  # 1,5 cm — Resmî Yazışma Yönetmeliği No. 2646 m.8


def _sayfa_kenari_yonetmelik(udf_yolu):
    """v0.5.8.3 — üretilmiş UDF'in pageFormat kenarlarını dört yönden 42.52 pt
    (1,5 cm; Yönetmelik No. 2646 m.8) yapar. İçeriğe DOKUNMAZ; yalnız
    pageFormat özniteliklerini yeniden yazar. Döner: kısa not metni
    (başarı/atlama) — ASLA fırlatmaz, üretimi asla kırmaz."""
    import zipfile as _zf
    import re as _re
    try:
        with _zf.ZipFile(udf_yolu) as z:
            adlar = z.namelist()
            icerikler = {ad: z.read(ad) for ad in adlar}
        x = icerikler.get("content.xml")
        if x is None:
            return "kenar: content.xml yok — atlandı"
        metin = x.decode("utf-8")

        def _oznitelik(m):
            etiket = m.group(0)
            for ad in ("leftMargin", "rightMargin", "topMargin", "bottomMargin"):
                if ad + '="' in etiket:
                    etiket = _re.sub(ad + r'="[0-9.]+"',
                                     '%s="%s"' % (ad, _KENAR_PT), etiket)
                else:
                    etiket = etiket.replace(
                        "<pageFormat",
                        '<pageFormat %s="%s"' % (ad, _KENAR_PT), 1)
            return etiket

        yeni, n = _re.subn(r"<pageFormat[^>]*/?>", _oznitelik, metin, count=1)
        if not n:
            return "kenar: pageFormat bulunamadı — atlandı"
        icerikler["content.xml"] = yeni.encode("utf-8")
        tmp = udf_yolu + ".kenar"
        with _zf.ZipFile(tmp, "w", _zf.ZIP_DEFLATED) as z:
            for ad in adlar:
                z.writestr(ad, icerikler[ad])
        os.replace(tmp, udf_yolu)
        return "kenar: 4x%s pt (Yönetmelik 2646 m.8) uygulandı" % _KENAR_PT
    except Exception as e:
        return "kenar: uygulanamadı (%s) — varsayılan kenarlarla sürüldü" % e


# ───────────────── gerçek yazıcı: `npx udf-cli html2udf` ────────────────────
_GIRIS_TALIMATI = (
    "Giriş gerekli: İNSAN varsa 'npx -y udf-cli@latest login' (tarayıcıda "
    "onaylayana kadar bekler). Başsız/otomasyon ortamda `issue_cli_login_code` "
    "MCP aracını çağırıp dönen tek-kullanımlık kodla "
    "'npx -y udf-cli@latest login --token <kod>' çalıştırın."
)


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
                            capture_output=True, text=True, timeout=zaman_asimi,
                            encoding="utf-8", errors="replace")
    except Exception as e:
        return False, "udf-cli whoami çalıştırılamadı: %s" % e
    if p.returncode != 0:
        return False, "udf-cli oturumu yok — %s" % _GIRIS_TALIMATI
    return True, (p.stdout or "").strip()


def npx_ile_udf_uret(html_yolu, cikti_yolu, npx_yolu="npx", zaman_asimi=180):
    """Rehberin ZORUNLU kıldığı TEK yazıcıyı çağırır: `npx -y udf-cli@latest
    html2udf <html> <udf>`. UDF içeriğini ASLA elle kurmaz (rehber A.2/D.1) —
    yalnız dış süreci çağırır, sonucu ATOMİK taşır. FAIL-CLOSED: başarısızlık
    durumunda hiçbir dosya `cikti_yolu`'na yazılmaz (geçici dosya, üretilmişse
    bile, nihai konuma taşınmaz) — eski elle-zip yoluna SESSİZCE düşülmez.

    Döner: dict — basarili(bool), exit_kod(int|None), stdout(str), stderr(str),
    hata(str|None — yalnız basarisiz ise)."""
    yol = shutil.which(npx_yolu)
    if yol is None:
        return {"basarili": False, "exit_kod": None, "stdout": "", "stderr": "",
                "hata": ("FAIL-CLOSED: npx bulunamadı (Node.js kurulu olmayabilir). "
                         "Kurulum: https://nodejs.org — ardından " + _GIRIS_TALIMATI)}

    tmp_udf = cikti_yolu + ".tmp-%d" % os.getpid()
    try:
        # bkz. npx_kullanilabilir_mi — çıplak "npx" değil, ÇÖZÜLMÜŞ yol çağrılır.
        p = subprocess.run(
            [yol, "-y", "udf-cli@latest", "html2udf", html_yolu, tmp_udf],
            capture_output=True, text=True, timeout=zaman_asimi,
            encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"basarili": False, "exit_kod": None, "stdout": "", "stderr": "",
                "hata": "FAIL-CLOSED: udf-cli html2udf zaman aşımına uğradı (%ds)" % zaman_asimi}
    except Exception as e:
        return {"basarili": False, "exit_kod": None, "stdout": "", "stderr": "",
                "hata": "FAIL-CLOSED: udf-cli html2udf çalıştırılamadı: %s" % e}

    if p.returncode != 0 or not os.path.isfile(tmp_udf):
        # yarım/bozuk geçici dosya kalmışsa temizle — nihai konuma ASLA taşınmaz.
        try:
            if os.path.isfile(tmp_udf):
                os.remove(tmp_udf)
        except OSError:
            pass
        return {"basarili": False, "exit_kod": p.returncode,
                "stdout": p.stdout or "", "stderr": p.stderr or "",
                "hata": ("FAIL-CLOSED: udf-cli html2udf başarısız (exit %s) — "
                          "HİÇBİR .udf yazılmadı (eski elle-zip yoluna düşülmedi). %s"
                          % (p.returncode, _GIRIS_TALIMATI))}

    # v0.5.8.3 ŞEKİL STANDARDI v2 — html2udf importer'ının varsayılan sayfa
    # kenarları dar (sahada "metin kenara çok yakın" bulgusu). Yönetmelik
    # No. 2646 m.8 (yazı alanı kenarlardan 1,5 cm) uyarınca pageFormat dört
    # kenarı 42.52 pt'ye çekilir. Bu içerik DEĞİL biçim yamasıdır; ardından
    # dosya yine udf_dogrula + resmî okuyucu kapılarından geçer. Başarısızlık
    # ÜRETİMİ KIRMAZ (kenar kozmetiktir) — sonuçta görünür not düşülür.
    kenar_notu = _sayfa_kenari_yonetmelik(tmp_udf)

    try:
        _atomik_tasi(tmp_udf, cikti_yolu)
    except Exception as e:
        return {"basarili": False, "exit_kod": p.returncode,
                "stdout": p.stdout or "", "stderr": p.stderr or "",
                "hata": "FAIL-CLOSED: atomik taşıma başarısız: %s" % e}

    return {"basarili": True, "exit_kod": 0, "stdout": p.stdout or "",
            "stderr": p.stderr or "", "hata": None, "kenar_notu": kenar_notu}


# ── RESMİ OKUYUCU ile geri okuma (udf2md) — 2026/307 saha reçetesi, adım 3 ──
# NEDEN AYRI BİR BACAK: `udf_dogrula` dosyayı BİZİM okuyucumuzun (udf_metin.py /
# oa_ingest udf_isle) beklentisine göre denetler. Sahada bizi yakan hata sınıfı
# TAM OLARAK buydu — eski hand-rolled zip çıktısı BİZİM round-trip'imizi
# GEÇİYOR ama UYAP Doküman Editörü onu AÇMIYORDU. Kendi varsayımımızla kendimizi
# doğrulamak kanıt değildir; bu yüzden geçerlilik kapısına DIŞARIDAN bir tanık
# eklenir: dosyayı üreten aracın kendi okuyucusu (`udf-cli udf2md`).
#
# ÜÇ DURUM AYRI TUTULUR (sessiz atlama yasağı):
#   çalıştı+okudu   → dosya hakkında OLUMLU dış kanıt
#   çalıştı+REDDETTİ→ dosya hakkında OLUMSUZ dış kanıt (GEÇERSİZ — blokleyici)
#   çalışamadı      → dosya hakkında HİÇBİR kanıt (ağ/oturum/Node yok) —
#                     "doğrulandı" SAYILMAZ, görünür biçimde "YAPILAMADI" der.
# Çalışamama blokleyici DEĞİLDİR: ortam koşuludur, dosyanın kusuru değil; aksi
# hâlde çevrimdışı çalışma imkânsızlaşırdı. Ama makbuza/rapora bu hâliyle geçer.
_RESMI_OKUYUCU_ASGARI_ORAN = 0.5   # resmî metin, CDATA metninin bu oranından kısaysa içerik kaybı


def npx_ile_udf_oku(udf_yolu, npx_yolu="npx", zaman_asimi=120):
    """`npx -y udf-cli@latest udf2md <udf>` — dosyayı ÜRETEN aracın kendi
    okuyucusuyla geri okur. Döner: dict —
      calisti (bool): dış süreç fiilen koştu ve bir hüküm verdi mi
      basarili (bool): koştuysa dosyayı okuyabildi mi
      metin (str): okunan markdown
      hata (str|None): calisti=False ise SEBEP (ortam), True+basarisiz ise RET gerekçesi
    """
    yol = shutil.which(npx_yolu)
    if yol is None:
        return {"calisti": False, "basarili": False, "metin": "",
                "hata": "npx bulunamadı (Node.js kurulu olmayabilir)"}
    try:
        # bkz. npx_kullanilabilir_mi — Windows PATHEXT için ÇÖZÜLMÜŞ yol.
        p = subprocess.run([yol, "-y", "udf-cli@latest", "udf2md", udf_yolu],
                           capture_output=True, text=True, timeout=zaman_asimi,
            encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"calisti": False, "basarili": False, "metin": "",
                "hata": "udf-cli udf2md zaman aşımına uğradı (%ds)" % zaman_asimi}
    except Exception as e:
        return {"calisti": False, "basarili": False, "metin": "",
                "hata": "udf-cli udf2md çalıştırılamadı: %s" % e}

    if p.returncode != 0:
        # Oturum/ağ hatası bir ORTAM koşuludur (dosya hakkında hüküm DEĞİL);
        # dosyanın gerçekten reddedilmesinden ayırt edilir — aksi hâlde
        # login'i unutmuş bir avukatın geçerli dilekçesi "bozuk" ilan edilirdi.
        birlesik = ((p.stderr or "") + (p.stdout or "")).lower()
        ortamsal = any(im in birlesik for im in
                       ("login", "giriş", "giris", "oturum", "unauthor", "quota",
                        "kota", "network", "ağ", "econn", "etimedout", "fetch failed"))
        if ortamsal:
            return {"calisti": False, "basarili": False, "metin": "",
                    "hata": "udf-cli udf2md ortam hatası (exit %s) — %s"
                            % (p.returncode, _GIRIS_TALIMATI)}
        return {"calisti": True, "basarili": False, "metin": "",
                "hata": "resmî okuyucu dosyayı OKUYAMADI (udf2md exit %s): %s"
                        % (p.returncode, ((p.stderr or "").strip()[:300] or "(çıktı yok)"))}

    return {"calisti": True, "basarili": True, "metin": p.stdout or "", "hata": None}


# ─────── BONUS YOL: elde hazır .docx/.pdf → UDF (`docx2udf`, rehber §5) ─────
# Bu, md → UDF-HTML → html2udf akışının dışındadır: avukatın Word'de HAZIR
# yazdığı bir taslak varsa (ör. `dilekce.docx`) doğrudan `.udf`'e çevirir.
# `docx2udf` `udf-cli`'den AYRI bir npm paketidir; login-gated (aynı paylaşılan
# ~/.config/yargi/token.json), ağ gerektirir, FAIL-CLOSED (sunucuya
# ulaşılamazsa/hesap yasaklıysa dosya YAZILMAZ).
DOCX2UDF_CIKIS_KODU = {
    0: "Başarı",
    1: "Dönüştürme/girdi hatası (desteklenmeyen biçim, dosya eksik, beklenmedik sunucu yanıtı)",
    2: "Giriş gerekli",
    3: "Hesap yasaklı",
    4: "Sunucuya erişilemiyor (ağ/5xx — geçici, sonra tekrar dene)",
    5: "Aylık kota bitti",
}


def docx2udf_ile_uret(girdi_yolu, cikti_yolu=None, npx_yolu="npx", zaman_asimi=180):
    """`npx -y docx2udf@latest -input <girdi> [-output <cikti>]` çağırır.
    Başarı ölçütü REHBERE GÖRE: çıkış kodu + `-output` (veya türetilen) dosyanın
    VARLIĞI — stdout/stderr metni ayrıştırılmaz (rehber §5 kuralı). `-y` her
    zaman geçilir (npx'in etkileşimli sorusu bloklamasın).

    Döner: dict — basarili(bool), exit_kod(int|None), aciklama(str — çıkış
    kodu tablosundan), cikti_yolu(str|None — başarılıysa gerçek dosya yolu),
    stdout(str), stderr(str)."""
    yol = shutil.which(npx_yolu)
    if yol is None:
        return {"basarili": False, "exit_kod": None,
                "aciklama": "npx bulunamadı (Node.js kurulu olmayabilir).",
                "cikti_yolu": None, "stdout": "", "stderr": ""}

    args = [yol, "-y", "docx2udf@latest", "-input", girdi_yolu]
    if cikti_yolu:
        args += ["-output", cikti_yolu]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=zaman_asimi,
                           encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"basarili": False, "exit_kod": None,
                "aciklama": "docx2udf zaman aşımına uğradı (%ds)" % zaman_asimi,
                "cikti_yolu": None, "stdout": "", "stderr": ""}
    except Exception as e:
        return {"basarili": False, "exit_kod": None,
                "aciklama": "docx2udf çalıştırılamadı: %s" % e,
                "cikti_yolu": None, "stdout": "", "stderr": ""}

    aciklama = DOCX2UDF_CIKIS_KODU.get(p.returncode, "bilinmeyen çıkış kodu")
    beklenen_cikti = cikti_yolu or (os.path.splitext(girdi_yolu)[0] + ".udf")
    basarili = (p.returncode == 0 and os.path.isfile(beklenen_cikti))
    if p.returncode == 2:
        aciklama += " — " + _GIRIS_TALIMATI
    return {"basarili": basarili, "exit_kod": p.returncode, "aciklama": aciklama,
            "cikti_yolu": beklenen_cikti if basarili else None,
            "stdout": p.stdout or "", "stderr": p.stderr or ""}


# ═════════════ GÖREV B (P0-B, v0.5.5) — ÜRETİM-ANI ÖN-DENETİM ═══════════════
# Saha bulgusu (B3): teslim kapısı (İçtihat Muhakeme Zinciri + Atıf/Künye
# Teyit) yalnız `dilekce_denetim.py`/`teslim_paketi.py` MODEL TARAFINDAN
# çağrılırsa çalışıyordu — bir .udf üretimi bu zincire hiç uğramadan (model
# doğrudan `udf_yaz.py`yi çağırıp) TESLİM ADAYI üretebiliyordu, dökümde/
# denetimde HİÇBİR iz bırakmadan. Kullanıcı ilkesi (amaç-çizgisi KABUL
# KURALI): kapı İŞİ değil FORMU denetler; burada da AYNI ilke — bu bir
# TESLİM ENGELİ DEĞİLDİR (avukat egemen, UDF yine üretilir), yalnız BLOK
# varsa GÖRÜNÜRLÜK garanti edilir (rapor dosyası + stdout uyarısı + DURUM.md
# notu) — model bir sonraki adımı (`pipeline_kayit.py --isle`/`--denetle`)
# hiç çağırmasa BİLE.
def _capraz_skill_yukle(dosya_adi, modul_adi):
    """Kardeş skill oa-kontrol'ün scriptini (…/oa-dilekce/scripts/ →
    …/oa-kontrol/scripts/) İN-PROCESS import eder — `dilekce_denetim.py`'nin
    `_ictihat_muhakeme_yolu`/`_kunye_ortak_modulu` ile AYNI desen. Bulunamaz/
    çökerse None (fail-safe; bu bir güvenlik sınırı DEĞİL — kardeş skill
    kurulu değilse veya beklenmedik bir hata varsa ön-denetim SESSİZCE
    atlanır, UDF üretimini ASLA engellemez)."""
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-kontrol" / "scripts" / dosya_adi)
    if not yol.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location(modul_adi, str(yol))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


# ═══════════ v0.5.10 — ATOMİK MÜHÜR + ÇİFT-UZANTI (307 karnesi K1) ═══════════
# 307 saha kanıtı: teslim UDF'i yeşil makbuzdan ~68 dk sonra yeniden üretildi,
# mühür (.prov.json) TAZELENMEDİ → mühürdeki sha ile dosyanın gerçek sha'sı
# uyuşmaz kaldı ve o pencerede hiçbir katman ateşlemedi. Kök neden: üretim ile
# mühür AYRIK yaşıyordu (üretici udf_yaz, mühürcü hook/oa-kontrol). v0.5.10
# sözleşmesi: ÜRETİM VE MÜHÜR TEK ATOMİK İŞLEMDİR — udf_yaz her başarılı
# üretimde mührü KOŞULSUZ kendisi basar/tazeler; hook'a/başka zincire güven
# YOK. Tek istisna e-imza halkası: imzalı nüshanın (sign.sgn / entity_type=
# e-imzali-nusha) mührü ASLA ezilmez (B5b, v0.5.8.5 — imza baytları değiştirir,
# o zincir teslim_paketi'nin işidir).

_BILINEN_ARA_UZANTILAR = {".md", ".markdown", ".txt", ".html", ".htm", ".docx"}


def _cikti_adi_normalize(yol):
    """307 kozmetik kusuru: '…TESLIM.md.udf' sınıfı çift-uzantılı çıktı adı.
    Taban adın sonunda bilinen bir BELGE ara-uzantısı + '.udf' bitişikse ara
    uzantıyı soyar. Döner: (normalize_yol, not|None) — not, düzeltme yapıldıysa
    çağıranın GÖRÜNÜR basacağı tek satırdır (sessiz ad değişikliği yok)."""
    taban, uzanti = os.path.splitext(yol)
    if uzanti.lower() != ".udf":
        return yol, None
    kok2, ara = os.path.splitext(taban)
    if ara.lower() in _BILINEN_ARA_UZANTILAR and kok2:
        yeni = kok2 + ".udf"
        return yeni, ("çıktı adı normalize edildi: %s → %s (çift-uzantı; "
                      "v0.5.10)" % (os.path.basename(yol),
                                    os.path.basename(yeni)))
    return yol, None


def _udf_zipte_imza_var_mi(yol):
    """zip'te sign.sgn girdisi var mı — e-imzalı nüsha tespiti (asla fırlatmaz)."""
    try:
        with zipfile.ZipFile(yol) as z:
            return any(ad.lower().endswith("sign.sgn") for ad in z.namelist())
    except Exception:
        return False


def _prov_muhur_yaz(cikti_yolu, kok=None, motor="html2udf", girdi_yolu=None):
    """ATOMİK MÜHÜR: üretilen .udf için .prov.json'u KOŞULSUZ yaz/tazele.
    Öncelik: kardeş oa-kontrol/muhur_yaz.py (tek şema kaynağı); yoksa aynı
    oa-muhur/1.0 şemasıyla yerleşik yazım (udf_yaz tek başına da atomiktir).
    E-imza guard'ı: dosya imzalıysa VEYA mevcut mühür e-imzali-nusha ise
    DOKUNULMAZ. Asla fırlatmaz → (prov_yolu|None, hata_notu|None)."""
    try:
        if _udf_zipte_imza_var_mi(cikti_yolu):
            return None, "e-imzalı nüsha — mühre dokunulmadı (e-imza halkası)"
        prov_yolu = cikti_yolu + ".prov.json"
        if os.path.isfile(prov_yolu):
            try:
                with open(prov_yolu, encoding="utf-8") as f:
                    if json.load(f).get("entity_type") == "e-imzali-nusha":
                        return None, ("mevcut mühür e-imzali-nusha — "
                                      "dokunulmadı (e-imza halkası)")
            except Exception:
                pass  # bozuk mühür TAZELENİR (kırık mühür bırakmak K1'dir)
        kok_gercek = kok or os.path.dirname(os.path.abspath(cikti_yolu))
        arac = "udf_yaz.py v0.5.10 (%s)" % motor
        girdiler = [girdi_yolu] if (girdi_yolu and os.path.isfile(girdi_yolu)) else []
        # muhur_yaz modülü köke `_oa/provenance.jsonl` de yazar — `_oa` YOKSA
        # o yol KULLANILMAZ (udf_yaz "_oa yoksa dizin kurmaz" sözleşmesi;
        # üretim makbuzu kuralıyla simetrik). Çıplak klasörde yalnız ürün
        # yanına .prov.json basılır (yerleşik yol).
        mod = None
        if os.path.isdir(os.path.join(kok_gercek, "_oa")):
            mod = _capraz_skill_yukle("muhur_yaz.py", "_oa_udf_yaz_muhur_inproc")
        if mod is not None:
            kayit = mod.muhur_uret(kok_gercek, cikti_yolu, "dilekce",
                                   "urun:%s" % os.path.basename(cikti_yolu),
                                   girdiler, arac=arac)
            return mod.muhur_yaz(kok_gercek, cikti_yolu, kayit)
        # Yerleşik yedek — muhur_yaz.py yoksa AYNI şema, aynı atomiklik.
        with open(cikti_yolu, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        kayit = {
            "prov_schema": "oa-muhur/1.0",
            "entity_id": "urun:%s" % os.path.basename(cikti_yolu),
            "entity_type": "dilekce",
            "artifact_file": os.path.basename(cikti_yolu),
            "artifact_sha256": sha,
            "generated_at_time": datetime.datetime.now(
                datetime.timezone.utc).isoformat(timespec="seconds"),
            "was_generated_by": arac,
            "used": [],
            "was_derived_from": None,
            "llm_kullanimi": None,
        }
        for g in girdiler:
            with open(g, "rb") as f:
                kayit["used"].append({
                    "file": os.path.basename(g),
                    "sha256": hashlib.sha256(f.read()).hexdigest()})
        tmp = "%s.tmp.%s" % (prov_yolu, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(kayit, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, prov_yolu)
        return prov_yolu, None
    except Exception as e:
        return None, "mühür yazılamadı: %r" % e


_ICTIHAT_MUHAKEME_MOD = None
_KUNYE_TEYIT_MOD = None


def _ictihat_muhakeme_modulu():
    global _ICTIHAT_MUHAKEME_MOD
    if _ICTIHAT_MUHAKEME_MOD is None:
        _ICTIHAT_MUHAKEME_MOD = _capraz_skill_yukle(
            "ictihat_muhakeme_denetim.py", "_oa_udf_yaz_ictihat_muhakeme_inproc")
    return _ICTIHAT_MUHAKEME_MOD


def _kunye_teyit_modulu():
    global _KUNYE_TEYIT_MOD
    if _KUNYE_TEYIT_MOD is None:
        _KUNYE_TEYIT_MOD = _capraz_skill_yukle(
            "kunye_teyit.py", "_oa_udf_yaz_kunye_teyit_inproc")
    return _KUNYE_TEYIT_MOD


def on_denetim_kostur(metin, kok=None):
    """UDF ÜRETİLMEDEN ÖNCE hafif bir ön-denetim: kardeş skill oa-kontrol'ün
    iki mekanik kapısını — İçtihat Muhakeme Zinciri (`ictihat_muhakeme_denetim.py`)
    ve Atıf/Künye Teyit (`kunye_teyit.py`) — İN-PROCESS (subprocess YOK,
    fonksiyonlar doğrudan çağrılır) çalıştırır. TESLİM ENGELİ ÜRETMEZ (bu
    fonksiyonun dönüşü UDF üretimini ASLA durdurmaz — çağıran taraf `main()`
    yalnız BLOK sayısı > 0 ise görünür rapor/uyarı üretir).

    Döner: dict — calisti(bool), blok_sayisi(int), rapor(str), not(str|None).
    Kardeş skill (oa-kontrol) kurulu değilse veya her iki modül de
    yüklenemezse `calisti=False` ile SESSİZCE atlanır."""
    sonuc = {"calisti": False, "blok_sayisi": 0, "rapor": "", "not": None}
    imd = _ictihat_muhakeme_modulu()
    kt = _kunye_teyit_modulu()
    if imd is None and kt is None:
        sonuc["not"] = ("oa-kontrol ön-denetim modülleri (ictihat_muhakeme_denetim.py / "
                         "kunye_teyit.py) bulunamadı/yüklenemedi — ön-denetim atlandı.")
        return sonuc

    taban = kok or "."
    rapor_parcalar = []
    blok_toplam = 0

    if imd is not None:
        try:
            muhakeme_dizin = os.path.join(taban, "_oa", "cikti")
            dokum_dizin = os.path.join(taban, "_oa", "teyit", "dokum")
            kutuk_yolu = os.path.join(taban, "_oa", "teyit", "kunye-teyit.md")
            atiflar = imd.taslaktaki_atiflari_bul(metin)
            kayitlar, gecersiz_sayisi = imd.muhakeme_kayitlarini_yukle(muhakeme_dizin)
            sonuclar = [imd._atif_denetle(a, kayitlar, taban, dokum_dizin, kutuk_yolu)
                        for a in atiflar]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                imd.rapor_yaz(
                    "<UDF taslağı>", atiflar, sonuclar, muhakeme_dizin, dokum_dizin,
                    kutuk_bos_mu=(not kayitlar and not gecersiz_sayisi), tip=None,
                    gecersiz_sayisi=gecersiz_sayisi,
                    kutuk_kullanimda_mi=imd.ko.kutuk_gercek_veri_var_mi(kutuk_yolu))
            blok_f = sum(1 for (d, *_r) in sonuclar if d == "BLOK")
            blok_toplam += blok_f
            rapor_parcalar.append("── [F] İÇTİHAT MUHAKEME ZİNCİRİ ──\n" + buf.getvalue())
        except Exception as e:
            rapor_parcalar.append(f"── [F] İÇTİHAT MUHAKEME ZİNCİRİ — ön-denetim çöktü: {e}")

    if kt is not None:
        try:
            kutuk = os.path.join(taban, "_oa", "teyit", "kunye-teyit.md")
            dokum_dizin = os.path.join(taban, "_oa", "teyit", "dokum")
            cikti_dizin = os.path.join(taban, "_oa", "cikti")
            atiflar_kt = kt.atiflari_cikar(metin)
            teyit_kaynaklar, bilgi_kaynaklar, kutuk_var = kt.kaynaklari_yukle(
                kutuk, dokum_dizin, cikti_dizin)
            if kutuk_var:
                for a in atiflar_kt:
                    kt.teyit_et(a, teyit_kaynaklar, bilgi_kaynaklar)
            buf2 = io.StringIO()
            with contextlib.redirect_stdout(buf2):
                kt.rapor_yaz(atiflar_kt, kutuk_var, kutuk)
            teyitsiz = sum(1 for a in atiflar_kt if a.durum == "TEYİTSİZ")
            if not atiflar_kt:
                blok_g = 0
            elif not kutuk_var:
                blok_g = len(atiflar_kt)
            else:
                blok_g = teyitsiz
            blok_toplam += blok_g
            rapor_parcalar.append("── [KÜNYE TEYİT] ATIF/KÜNYE DOĞRULAMA ──\n" + buf2.getvalue())
        except Exception as e:
            rapor_parcalar.append(f"── [KÜNYE TEYİT] ön-denetim çöktü: {e}")

    sonuc["calisti"] = True
    sonuc["blok_sayisi"] = blok_toplam
    sonuc["rapor"] = "\n\n".join(rapor_parcalar)
    return sonuc


def _durum_md_uyari_ekle(kok, satir):
    """B3 (v0.5.5 GÖREV B) — ön-denetim BLOK bulduğunda `_oa/DURUM.md`'ye EN
    İYİ ÇABA ile GÖRÜNÜR bir uyarı satırı ekler; teslim kapısının görünürlüğü
    modelin `pipeline_kayit.py`yi ÇAĞIRMASINA bağlı KALMASIN diye burada
    BAĞIMSIZ ve UCUZ (yalnız dosyaya ekleme) çalışır — `pipeline_kayit.py`yi
    İN-PROCESS ÇAĞIRMAZ (o modülün kademeli import zinciri ağırdır; bu
    ön-denetim HAFİF kalmalıdır — amaç-çizgisi: 'araç yolunu ucuzlat').
    `_oa/DURUM.md` normalde `pipeline_kayit.py._durum_md_yaz` tarafından
    TAMAMEN türetilir/üzerine yazılır (bkz. o dosyanın başlığı); bu fonksiyon
    onu ASLA üzerine yazmaz, yalnız SONUNA ekler — dosya hiç yoksa (defter
    hiç açılmamış/pipeline_kayit hiç çalışmamış) minimal bir başlıkla
    oluşturulur ki bu uyarı pipeline kullanılıp kullanılmadığından BAĞIMSIZ
    görünür kalsın. ASLA istisna fırlatmaz (best-effort; ana UDF üretim
    akışını etkilemez)."""
    try:
        hedef = os.path.join(kok or ".", "_oa", "DURUM.md")
        ust = os.path.dirname(hedef)
        if ust:
            os.makedirs(ust, exist_ok=True)
        yeni = not os.path.isfile(hedef)
        with open(hedef, "a", encoding="utf-8") as f:
            if yeni:
                f.write("<!-- pipeline_kayit.py çalıştığında bu dosya TAMAMEN "
                         "türetilir/üzerine yazılır — bu satır ondan ÖNCE, "
                         "udf_yaz.py ön-denetiminden düşmüştür. -->\n")
            zaman = datetime.datetime.now().isoformat(timespec="seconds")
            f.write(f"\n⚠ [{zaman}] {satir}\n")
    except Exception:
        pass


# ───────────────────────────────── main ────────────────────────────────────
# ═════════════════════════════════════════════════════════════════════════
# YEREL MOTOR v2 (v0.5.7 — BİLİNÇLİ GERİ DÖNÜŞ, sıkı kapılı)
#
# TARİHÇE: v0.5.5.1'de eski yerel motor B5 saha bulgusuyla (ürettiği .udf
# UYAP'ta açılmıyordu ama zincir "TESLİME HAZIR" basıyordu — sessiz-yanlış)
# TAMAMEN kaldırılmıştı. Denizli 754 koşusunda ise 307 sahasında TAMİR
# GÖRMÜŞ nesil (CDATA + template 1.8 + resolver/pageFormat + UTF-16 offset)
# gerçek mekanik kapıdan SIFIR sorunla ve resmî okuyucu (npx udf2md)
# round-trip'inden 13/13 çapayla geçti. Kullanıcı talebi: md→UDF çevrimi
# barındırılan hesaba (npx udf-cli oturumu) MAHKÛM olmasın.
#
# GÜNCEL SÖZLEŞME (v0.5.8.4 — 372 sahası A/B hükmüyle SIKILAŞTI):
#   0. 372 sahasında bu hattın ürünleri UYAP'ta AÇILMADI (7 dosya karantina);
#      A/B testi re-zip'i ve kenar yamasını AKLADI — suçlu content.xml'in
#      kendisi (styles bloğunda hvl-default STİL TANIMI yok). Bu yüzden
#      `--yerel-motor` EMEKLİDİR: artık HATA verir ve yönlendirir.
#   1. Hat yalnız YENİ AÇIK BAYRAKLA (--yerel-motor-riskli) koşar —
#      varsayılan hat DEĞİŞMEDİ (md → UDF-HTML → npx html2udf, fail-closed).
#      Sessiz düşüş YOKTUR.
#   2. Ürettiği dosya udf_dogrula(resmi_okuyucu=True) kapısından geçirilir;
#      okuyucu OK vermezse çıktının yanına `<ad>.DOGRULANMADI` işaret dosyası
#      düşer (üretim tamamlanır, fırlatmaz — doğrulanmamışlık diskte görünür).
#   3. Her koşuda GÖRÜNÜR uyarı: resmî yazıcı değildir; e-imza öncesi UYAP
#      Doküman Editörü'nde görsel teyit ZORUNLUDUR.
# Eski motorun fonksiyon adları (udf_uret/udf_yaz/udf_metni_geri_oku) BİLEREK
# geri getirilmedi — o adları yasaklayan regresyon kilidi anlamını korur.
# ═════════════════════════════════════════════════════════════════════════

_YM_FORMAT_ID = "1.8"   # UYAP editör şablonu (bilinen değerler: 1.6/1.7/1.8)
_YM_HIZA_ORTA, _YM_HIZA_YASLI = 1, 3   # Swing StyleConstants hizaları


def _ym_utf16_uzunluk(s):
    """UYAP editörü (Java/Swing) offset'leri UTF-16 CODE UNIT sayar; Python
    code-point sayar. BMP-dışı karakterde (emoji) tek code-point iki code
    unit'tir — offset'i Swing birimine çekmezsek sonraki TÜM hizalar kayar."""
    return len(s.encode("utf-16-le")) // 2


def _ym_md_satir_duzlestir(satir):
    """Bir markdown satırını düz metne indir; (metin, baslik_mi) döndür."""
    s = satir.rstrip("\r")
    baslik = False
    m = re.match(r"^(#{1,6})\s*(.*?)\s*#*\s*$", s)
    if m:
        baslik = True
        s = m.group(2)
    m = re.match(r"^(\s*)[-*+]\s+(.*)$", s)
    if m:
        s = m.group(1) + "• " + m.group(2)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"__(.+?)__", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)", r"\1", s)
    s = re.sub(r"(?<!_)_(?!_)([^_]+?)_(?!_)", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    return s, baslik


def _ym_cdata_guvenli(metin):
    """CDATA içinde yasak `]]>` dizisini böler."""
    return metin.replace("]]>", "]]]]><![CDATA[>")


def _ym_icerik_xml(ham_metin, ham_mod=False, format_id=_YM_FORMAT_ID):
    """Metinden content.xml üretir (307-tamirli saha nesli, alan-kanıtlı yapı):
    <template format_id> · <content><![CDATA[..]]></content> ·
    <properties><pageFormat/></properties> · <elements resolver="hvl-default"
    name="hvl-default"> paragraf offset'leri (UTF-16 code unit, bitişik) ·
    <styles>. Döner: (xml_str, tam_metin, paragraf_sayisi)."""
    ham = ham_metin.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    satirlar = ham.split("\n") if ham != "" else [""]
    parcalar, paragraflar, imlec = [], [], 0
    for satir in satirlar:
        duz, baslik = (satir, False) if ham_mod else _ym_md_satir_duzlestir(satir)
        parca = duz + "\n"
        u16 = _ym_utf16_uzunluk(parca)
        paragraflar.append((imlec, u16, baslik))
        parcalar.append(parca)
        imlec += u16
    tam = "".join(parcalar)

    # v0.5.7.2 — SAHA STANDARDI: kenar boşlukları ve paragraf metrikleri,
    # avukatın e-imzalayıp fiilen sunduğu gerçek bir nüshadan ÖLÇÜLDÜ
    # ŞEKİL STANDARDI v2 (v0.5.8.3 — Can emri + Resmî Yazışma Yönetmeliği
    # No. 2646 m.8: yazı alanı kenarlardan 1,5 cm): DÖRT kenar 42.52 pt;
    # gövde = yaslı + FirstLineIndent 24 + SpaceBelow 6 + LineSpacing 0.5
    # (~1,5 satır aralığı; eski ölçüm 0.3 tek-aralığa yakındı); her span'da
    # açık Times New Roman 12. (bkz. references/udf-ic-yapi.md §6-v2)
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<template format_id="%s">' % format_id,
         '<content><![CDATA[' + _ym_cdata_guvenli(tam) + ']]></content>',
         '<properties>',
         '<pageFormat mediaSizeName="1" leftMargin="42.52" '
         'rightMargin="42.52" topMargin="42.52" bottomMargin="42.52" '
         'paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0"/>',
         '</properties>',
         '<elements resolver="hvl-default" name="hvl-default">']
    for start, length, baslik in paragraflar:
        if baslik:
            x.append('<paragraph Alignment="%d" SpaceBelow="6.0">' % _YM_HIZA_ORTA)
            x.append('<content startOffset="%d" length="%d" bold="true" '
                     'family="Times New Roman" size="12"/>' % (start, length))
        else:
            x.append('<paragraph Alignment="%d" FirstLineIndent="24.0" '
                     'SpaceBelow="6.0" LineSpacing="0.5">' % _YM_HIZA_YASLI)
            x.append('<content startOffset="%d" length="%d" '
                     'family="Times New Roman" size="12"/>' % (start, length))
        x.append('</paragraph>')
    x += ['</elements>', '<styles>',
          '<style name="default" description="Govde" '
          'family="Times New Roman" size="12" bold="false" italic="false" '
          'foreground="-16777216"/>',
          '</styles>', '</template>']
    xml_str = "\n".join(x) + "\n"
    ET.fromstring(xml_str)          # iyi biçimlilik — bozuksa burada patlar
    return xml_str, tam, len(paragraflar)


def yerel_motor_ile_uret(metin, cikti_yolu, ham_mod=False, npx_yolu="npx"):
    """--yerel-motor-riskli gövdesi (v0.5.8.4): üret → ATOMİK yaz →
    udf_dogrula RESMÎ OKUYUCU DAHİL (resmi_okuyucu=True — 372 dersi: kendi
    round-trip'imiz kanıt değildir). Okuyucu OK vermezse çıktının YANINA
    `<ad>.DOGRULANMADI` işaret dosyası bırakılır — üretim yine TAMAMLANIR
    (fırlatmaz), ama doğrulanmamışlık diskte GÖRÜNÜR kalır; çağıran taraf
    (main) ayrıca stderr'e blok uyarı basar. 372 A/B hükmü gereği bu hattın
    ürünleri mekanik kapıda da 'elle-üretim imzası' ile işaretlenir; sonuç
    dict'in `dogrulama` alanı her iki bacağı olduğu gibi taşır (sahte
    kesinlik yok)."""
    xml_str, tam, paragraf = _ym_icerik_xml(metin, ham_mod=ham_mod)
    tmp = cikti_yolu + ".tmp-%d" % os.getpid()
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("content.xml", xml_str.encode("utf-8"))
        _atomik_tasi(tmp, cikti_yolu)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

    dogrulama = udf_dogrula(
        cikti_yolu, resmi_okuyucu=True,
        okuyucu_fn=lambda yol: npx_ile_udf_oku(yol, npx_yolu=npx_yolu))

    isaret = None
    if dogrulama.get("resmi_okuyucu") != "OK":
        # üretim KIRILMAZ; ama dosyanın UYAP tarafında açıldığı DOĞRULANMADI —
        # işaret dosyası, teslim anında gözden kaçmasın diye çıktının yanında.
        isaret = cikti_yolu + ".DOGRULANMADI"
        try:
            with open(isaret, "w", encoding="utf-8") as f:
                f.write(
                    "Bu .udf dosyasının UYAP tarafında AÇILDIĞI DOĞRULANMADI.\n"
                    "Üretici: yerel motor (--yerel-motor-riskli, bilinçli risk).\n"
                    "372 sahası: bu hattın ürünleri UYAP'ta açılmadı (7 dosya "
                    "karantina).\n"
                    "resmî okuyucu: %s — %s\n"
                    "Teslimden ÖNCE UYAP Doküman Editörü'nde açıp görsel teyit "
                    "ZORUNLUDUR; teyit sonrası bu işaret dosyasını avukat siler.\n"
                    % (dogrulama.get("resmi_okuyucu"),
                       dogrulama.get("resmi_okuyucu_not") or
                       "; ".join(dogrulama.get("hatalar", [])) or "ayrıntı yok"))
        except OSError:
            isaret = None  # yazılamadıysa görünürlük stderr uyarısına kalır

    return {"basarili": True, "paragraf": paragraf, "karakter": len(tam),
            "hatalar": dogrulama.get("hatalar", []),
            "dogrulama": dogrulama, "isaret_dosyasi": isaret}


# ═══════════ ÜRETİM MAKBUZU (v0.5.8.4 — best-effort, _oa/defter) ════════════
# 372 saha ölçümü: makbuz HİÇ üretilmedi çünkü tek üretici
# `teslim_paketi._makbuz_yaz` idi ve model o zinciri atladı (Stop hook 23 kez
# uyardı, 0 kez uygulandı). Çözüm zorlamak değil ÜRETİM NOKTASINA taşımak:
# .udf'i FİİLEN yazan bu script, dava klasörü `_oa` tutuyorsa kendi üretim
# makbuzunu düşer — B7 (v0.5.8.5) garantisi: `_oa/defter` alt dizini henüz
# yoksa makedirs ile KURULUR (372'nin devamı: "defter yoksa sessiz atla"
# kuralı makbuzu _oa'lı ama defteri açılmamış klasörlerde kaybettiriyordu).
# `_oa` da yoksa sessiz atlanır (defter/_oa açmak pipeline'ın işidir, bu
# script dayatmaz); HİÇBİR hata üretimi kırmaz (makbuz kayıt aracıdır,
# kapı değildir).
def _uretim_makbuzu_yaz(kok, girdi_yolu, cikti_yolu, motor, dogrulama,
                        kenar_notu=None):
    """`_oa/defter/udf-uretim-makbuz.jsonl` dosyasına TEK satır JSON APPEND
    eder. Döner: yazılan dosyanın yolu ya da None (defter yok / yazılamadı).
    ASLA istisna fırlatmaz — üretim akışını hiçbir koşulda etkilemez."""
    try:
        oa_dizin = os.path.join(kok or ".", "_oa")
        defter = os.path.join(oa_dizin, "defter")
        if not os.path.isdir(defter):
            # B7 (v0.5.8.5 — MAKBUZ GARANTİSİ): dava klasörü `_oa` tutuyorsa
            # defter alt dizini makbuz için KURULUR ve yazılır — "defter yoksa
            # sessiz atla" kuralı makbuzu, defteri henüz açılmamış ama _oa'lı
            # klasörlerde kaybettiriyordu. `_oa` da yoksa sessiz atlama sürer
            # (defter/_oa açmak pipeline'ın işidir, bu script dayatmaz).
            if not os.path.isdir(oa_dizin):
                return None
            os.makedirs(defter, exist_ok=True)
        with open(cikti_yolu, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        d = dogrulama or {}
        kayit = {
            "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
            "girdi": girdi_yolu,
            "cikti": cikti_yolu,
            "sha256": sha,
            "motor": motor,                      # "html2udf" | "yerel-riskli"
            "dogrulama": bool(d.get("gecerli")),
            "resmi_okuyucu": d.get("resmi_okuyucu"),
            "kenar_notu": kenar_notu,
        }
        yol = os.path.join(defter, "udf-uretim-makbuz.jsonl")
        with open(yol, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
        return yol
    except Exception:
        return None


# ─────────── İSTİSNA DEFTERİ (ortak şema, append-only, best-effort) ─────────
def _istisna_kaydi_yaz(kok, tur, ilgili, gerekce, onay="otomatik-kural"):
    """`_oa/defter/istisna-kayitlari.jsonl`e TEK satır JSON APPEND eder —
    birden çok aracın yazdığı ORTAK istisna defteri şeması:
    {zaman, tur, ilgili, gerekce, onay, imza}. Bu yardımcı bilerek yereldir
    (ortak modül bağımlılığı YARATILMAZ — her araç kendi küçük yazıcısını
    taşır). Dizin kuralı makbuzla AYNIDIR: `_oa` varsa `defter` kurulur;
    `_oa` da yoksa sessiz atlanır. ASLA istisna fırlatmaz (kayıt aracıdır,
    kapı değildir — üretim/denetim akışını hiçbir koşulda etkilemez).
    Döner: yazılan dosyanın yolu ya da None."""
    try:
        oa_dizin = os.path.join(kok or ".", "_oa")
        defter = os.path.join(oa_dizin, "defter")
        if not os.path.isdir(defter):
            if not os.path.isdir(oa_dizin):
                return None
            os.makedirs(defter, exist_ok=True)
        kayit = {
            "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
            "tur": tur,
            "ilgili": ilgili,
            "gerekce": gerekce,
            "onay": onay,
            "imza": "udf_yaz.py",
        }
        yol = os.path.join(defter, "istisna-kayitlari.jsonl")
        with open(yol, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
        return yol
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(
        description="Markdown → UYAP UDF teslim hattı (md → UDF-HTML → npx udf-cli html2udf [+ opsiyonel PDF]).")
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
                    help="Verilirse aynı UDF-HTML'den A4 PDF de üretilir (udf_html2pdf.py, "
                         "PyMuPDF) — PDF üretimi UDF motorundan BAĞIMSIZDIR, npx/ağ "
                         "gerektirmez ve UDF üretimi başarısız olsa BİLE denenir.")
    ap.add_argument("--baslik", default="Dilekçe", help="PDF meta başlığı (yalnız --pdf ile).")
    ap.add_argument("--font-dizini", default=None,
                    help="PDF için Times New Roman TTF dizini (yalnız --pdf ile).")
    ap.add_argument("--npx", default="npx", metavar="KOMUT",
                    help="npx çalıştırılabilir yolu/adı (varsayılan: %(default)s).")
    ap.add_argument("--yerel-motor", action="store_true",
                    help="EMEKLİ (v0.5.8.4): bu bayrak artık HATA verir — 372 "
                         "sahasında yerel motor ürünleri UYAP'ta açılmadı "
                         "(7 dosya karantina). Varsayılan html2udf hattını "
                         "kullanın; bilinçli risk için --yerel-motor-riskli.")
    ap.add_argument("--yerel-motor-riskli", action="store_true",
                    help="BİLİNÇLİ RİSK (çevrimdışı yedek yol): UDF'i npx/oturum "
                         "OLMADAN yerel motorla üretir. UYAP uyumu GARANTİ "
                         "DEĞİLDİR (372: bu hattın ürünleri UYAP'ta AÇILMADI); "
                         "çıktı resmî okuyucu (udf2md) ile doğrulanamazsa yanına "
                         "'<ad>.DOGRULANMADI' işareti bırakılır. E-imza öncesi "
                         "UYAP Doküman Editörü'nde görsel teyit ZORUNLUDUR. "
                         "Varsayılan hattı DEĞİŞTİRMEZ; sessiz düşüş yolu YOKTUR.")
    ap.add_argument("--kaynak-docx", metavar="YOL", default=None,
                    help="BONUS YOL (rehber §5): md/HTML akışını ATLAYIP hazır bir "
                         ".docx/.pdf dosyasını doğrudan `docx2udf` ile --cikti'ye "
                         "çevirir (login-gated, ayrı npm paketi; --girdi/--ham/--html "
                         "yok sayılır). Çıkış kodu tablosu (0 Başarı, 1 Dönüştürme/"
                         "girdi hatası, 2 Giriş gerekli, 3 Hesap yasaklı, 4 Sunucuya "
                         "erişilemiyor, 5 Kota bitti) stderr'e basılır.")
    a = ap.parse_args()

    # v0.5.8.4 — YEREL MOTOR EMEKLİYE: 372 saha ölçümü (A/B) elle kurulan
    # content.xml'li UDF'lerin UYAP'ta AÇILMADIĞINI kanıtladı (7 dosya
    # karantina). Eski bayrak sessizce üretmeye devam etmesin: HATA + yönlendirme.
    if a.yerel_motor:
        sys.exit(
            "HATA: --yerel-motor EMEKLİYE AYRILDI — yerel motor ürünleri "
            "UYAP'ta açılmıyor (372 sahası: 7 dosya karantina). html2udf "
            "hattını kullanın (bayraksız varsayılan yol); bilinçli risk "
            "almak için --yerel-motor-riskli.")

    if a.kaynak_docx:
        kaynak = _kok_coz(a.kaynak_docx, a.kok)
        cikti_docx = _kok_coz(a.cikti, a.kok) if a.cikti else None
        sonuc = docx2udf_ile_uret(kaynak, cikti_docx, npx_yolu=a.npx)
        print("docx2udf: %s (exit %s)" % (sonuc["aciklama"], sonuc["exit_kod"]))
        if sonuc["stderr"]:
            print("  --- docx2udf stderr ---\n%s" % sonuc["stderr"], file=sys.stderr)
        if not sonuc["basarili"]:
            sys.exit(sonuc["exit_kod"] if sonuc["exit_kod"] else 1)
        print("UDF yazıldı (docx2udf): %s" % sonuc["cikti_yolu"])
        # NOT: rehber §5 başarı ölçütü AÇIKÇA "çıkış kodu + -output dosyasının
        # varlığı"dır — stdout/stderr AYRIŞTIRILMAZ. `udf_dogrula()`nın offset-
        # bitişiklik varsayımı (paragraf uzunluğu = CDATA'nın TAMAMINI TİLER)
        # `html2udf` çıktısına göre reverse-engineer edilmiştir; gerçek
        # `docx2udf` çıktısı paragraflar ARASI ayraçları (newline) HİÇBİR
        # elemente saymaz (offsetler arasında BOŞLUK bırakır) — bu YAPISAL
        # bir FARKTIR, bozukluk değildir. Bu yüzden burada o kapı ÇAĞRILMAZ;
        # docx2udf'in KENDİ resmî ölçütü (yukarıdaki exit+dosya kontrolü)
        # yeterlidir — yanlış-BLOK (false negative) üretmek amaç-çizgisi
        # ihlalidir (kapı FORMU değil İŞİ denetler).
        _uretim_makbuzu_yaz(a.kok, kaynak, sonuc["cikti_yolu"], "docx2udf",
                            {"gecerli": True})
        # v0.5.10 ATOMİK MÜHÜR (K1) — bu yol da mühürsüz ürün bırakamaz.
        p_yol, p_hata = _prov_muhur_yaz(sonuc["cikti_yolu"], kok=a.kok,
                                        motor="docx2udf", girdi_yolu=kaynak)
        print("  mühür (.prov)    : %s" % (p_yol or ("BASILAMADI: %s" % p_hata)))
        sys.exit(0)

    if a.dogrula:
        sonuc = udf_dogrula(a.dogrula)
        print("UDF GEÇERLİLİK KAPISI: %s" % a.dogrula)
        print("  content.xml var  : %s" % ("EVET" if sonuc["content_xml_var"] else "HAYIR"))
        print("  XML iyi biçimli  : %s" % ("EVET" if sonuc["xml_iyi_bicimli"] else "HAYIR"))
        print("  CDATA bulundu    : %s" % ("EVET" if sonuc["cdata_bulundu"] else "HAYIR"))
        if sonuc.get("imzali_nusha"):
            print("  imzalı nüsha     : EVET (%s) — editör-kaynaklı sapma "
                  "toleransı profili etkin" % sonuc.get("imza_dosyasi"))
        if sonuc["karakter_sayisi"] is not None:
            print("  karakter (CDATA) : %d" % sonuc["karakter_sayisi"])
        if sonuc["paragraf_sayisi"] is not None:
            print("  paragraf sayısı  : %d" % sonuc["paragraf_sayisi"])
        print("  offset/uzunluk   : %s" % (
            "TUTARLI" if sonuc["offsetler_tutarli"]
            else ("TUTARSIZ" if sonuc["offsetler_tutarli"] is False else "—")))
        _resmi_okuyucu_bas(sonuc)
        for n in sonuc.get("notlar") or []:
            print("  [NOT] %s" % n)
        for h in sonuc["hatalar"]:
            print("  [HATA] %s" % h, file=sys.stderr)
        # B6: imzalı-nüsha toleransı uygulandıysa ortak istisna defterine
        # (varsa) iz düşülür — tolerans SESSİZ kalmaz, denetlenebilir olur.
        if sonuc.get("imzali_tolerans"):
            istisna_yolu = _istisna_kaydi_yaz(
                a.kok, "dogrulama-toleransi", a.dogrula,
                "; ".join(sonuc["imzali_tolerans"]))
            if istisna_yolu:
                print("  istisna kaydı    : %s" % istisna_yolu)
        print("SONUÇ: %s" % ("GEÇERLİ ✓" if sonuc["gecerli"] else "GEÇERSİZ ✗"))
        sys.exit(0 if sonuc["gecerli"] else 1)

    if not a.cikti:
        sys.exit("HATA: --cikti gerekli (yazma modu) ya da --dogrula (denetim modu) verin.")

    girdi = _kok_coz(a.girdi, a.kok)
    cikti = _kok_coz(a.cikti, a.kok)
    # v0.5.10 — çift-uzantı ('x.md.udf'): udf_yaz VERİLEN ada yazar (çağıran
    # sözleşmesi kırılmaz — ad değiştirmek çağıranın beklediği yolu boşa
    # düşürür); kusur KAYNAĞINDA düzeltildi (teslim_paketi ad türetimi +
    # 40-UYAP kopya adı). Burada yalnız GÖRÜNÜR not basılır.
    _oneri, _ad_notu = _cikti_adi_normalize(cikti)
    if _ad_notu:
        print("NOT: çıktı adı çift-uzantılı (%s) — önerilen ad: %s"
              % (os.path.basename(cikti), os.path.basename(_oneri)),
              file=sys.stderr)
    pdf_yolu = _kok_coz(a.pdf, a.kok) if a.pdf else None

    if a.yerel_motor_riskli:
        # BİLİNÇLİ RİSK YOLU (v0.5.8.4) — yalnız açık bayrakla. Ağ/npx/oturum
        # GEREKMEZ (resmî okuyucu bacağı denenir, olmazsa GÖRÜNÜR "YAPILAMADI").
        if girdi:
            with open(girdi, "r", encoding="utf-8", errors="replace") as f:
                metin = f.read()
        else:
            if _sys.stdin is None:
                sys.exit("HATA: --girdi verilmedi ve stdin yok.")
            metin = _sys.stdin.read()
        print("⚠ YEREL MOTOR — RİSKLİ (bilinçli istekle):", file=sys.stderr)
        print("  Bu çıktı RESMÎ yazıcıdan (npx udf-cli html2udf) ÇIKMADI.", file=sys.stderr)
        print("  UYAP uyumu GARANTİ DEĞİLDİR — 372 sahasında bu hattın ürünleri", file=sys.stderr)
        print("  UYAP'ta AÇILMADI (7 dosya karantina). E-imza öncesi UYAP", file=sys.stderr)
        print("  Doküman Editörü'nde açıp görsel teyit ZORUNLUDUR.", file=sys.stderr)
        sonuc = yerel_motor_ile_uret(metin, cikti, ham_mod=a.ham, npx_yolu=a.npx)
        d = sonuc["dogrulama"]
        print("UDF yazıldı (YEREL MOTOR — RİSKLİ): %s" % cikti)
        print("  paragraf         : %d" % sonuc["paragraf"])
        print("  karakter (CDATA) : %d" % sonuc["karakter"])
        print("  mekanik kapı     : %s" % (
            "GEÇERLİ ✓" if d.get("gecerli") else "GEÇERSİZ ✗"))
        for h in d.get("hatalar", []):
            print("  [HATA] %s" % h, file=sys.stderr)
        _resmi_okuyucu_bas(d)
        if sonuc["isaret_dosyasi"] or d.get("resmi_okuyucu") != "OK":
            print("", file=sys.stderr)
            print("!" * 66, file=sys.stderr)
            print("UYARI: bu dosyanın UYAP tarafında açıldığı DOĞRULANMADI — "
                  "üretim tamamlandı ama bu dosya doğrulanmadan YÜKLENMEZ.",
                  file=sys.stderr)
            if sonuc["isaret_dosyasi"]:
                print("  İşaret dosyası: %s" % sonuc["isaret_dosyasi"],
                      file=sys.stderr)
            print("!" * 66, file=sys.stderr)
        _uretim_makbuzu_yaz(a.kok, girdi or "<stdin>", cikti,
                            "yerel-riskli", d)
        # v0.5.10 ATOMİK MÜHÜR (K1) — riskli yol da mühürsüz ürün bırakamaz
        # (was_generated_by "yerel" içerir → teslim kapısı YEREL-DAMGA'yı
        # zaten RED'ler; mühür burada dürüst kimlik beyanıdır, aklama değil).
        p_yol, p_hata = _prov_muhur_yaz(cikti, kok=a.kok,
                                        motor="yerel-riskli", girdi_yolu=girdi)
        print("  mühür (.prov)    : %s" % (p_yol or ("BASILAMADI: %s" % p_hata)))
        sys.exit(0)

    # NOT: --html AÇIKÇA verilmediyse ara HTML SİSTEM TEMP dizinine yazılır,
    # --cikti'nin yanına DEĞİL. `_oa/cikti` içine (dilekçeyle AYNI klasöre)
    # bırakılan bir kopya, pipeline_kayit.py `_dilekce_sekilli_makbuzsuz_
    # uyarisi` taramasını YANLIŞLIKLA tetikler (dosya İÇERİĞİ "Sayın
    # Mahkeme"/"netice-i talep" gibi dilekçe-şekilli desenleri taşıdığından,
    # üst dizindeki taslaktan DAHA YENİ görünen bir "makbuzsuz aday" gibi
    # okunur). Ara dosya işini bitirince (finally) SİLİNİR — kullanıcı --html
    # ile AÇIKÇA bir yol verdiyse bu onun bilinçli tercihidir, dokunulmaz/silinmez.
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

        # BMP-dışı karakter (emoji vb.) tespiti — genel bir uyarı.
        bmp_disi = sum(1 for ch in metin if ord(ch) > 0xFFFF)
        if bmp_disi:
            print("UYARI: metinde %d adet BMP-dışı karakter (emoji vb.) var; bu "
                  "karakterleri dilekçede kullanmak genellikle istenmez."
                  % bmp_disi, file=sys.stderr)

        # UDF-HTML HER ZAMAN üretilir/yazılır — hem `npx html2udf` girdisi hem
        # PDF kaynağıdır.
        html = md_html_uret(metin, ham=a.ham)
        with open(html_yolu, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("UDF-HTML yazıldı: %s%s (%d karakter)"
              % (html_yolu, " (geçici)" if html_gecici else "", len(html)))

        # ── TEK GEÇERLİ MOTOR: npx udf-cli html2udf (rehbere birebir) ────────
        sonuc = npx_ile_udf_uret(html_yolu, cikti, npx_yolu=a.npx)

        # PDF önizlemesi UDF motorundan BAĞIMSIZDIR (aynı UDF-HTML'den,
        # ağsız/PyMuPDF ile üretilir) — UDF üretimi başarısız olsa BİLE
        # (ör. ağ/oturum yoksa) avukatın en azından biçim önizlemesi elinde
        # olsun diye YİNE denenir.
        if pdf_yolu:
            mod = _sibling_yukle("udf_html2pdf.py", "_oa_udf_yaz_html2pdf")
            if mod is None:
                print("UYARI: udf_html2pdf.py (kardeş script) bulunamadı — PDF üretilemedi.",
                      file=sys.stderr)
            else:
                sayfa, font_gomuldu = mod.pdf_uret(html_yolu, pdf_yolu, baslik=a.baslik,
                                                    font_dizini=a.font_dizini)
                print("PDF yazıldı: %s (%d sayfa, font gömüldü: %s)"
                      % (pdf_yolu, sayfa, "EVET" if font_gomuldu else "HAYIR"))

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
        _resmi_okuyucu_bas(dogrulama)
        print("  GEÇERLİLİK KAPISI: %s" % ("GEÇERLİ ✓" if dogrulama["gecerli"] else "GEÇERSİZ ✗"))
        # v0.5.8.4 ÜRETİM MAKBUZU (best-effort): .udf fiilen üretildi —
        # defter varsa iz düşülür (dogrulama alanı sonucu OLDUĞU GİBİ taşır;
        # geçersiz çıksa bile üretim kaydı dürüstçe deftere geçer).
        makbuz_yolu = _uretim_makbuzu_yaz(
            a.kok, girdi or "<stdin>", cikti, "html2udf", dogrulama,
            kenar_notu=sonuc.get("kenar_notu"))
        if makbuz_yolu:
            print("  üretim makbuzu   : %s" % makbuz_yolu)
        # v0.5.10 ATOMİK MÜHÜR (K1): üretim ile mühür ayrılamaz — mühür
        # burada, üretimin parçası olarak KOŞULSUZ basılır/tazelenir.
        prov_yolu, prov_hata = _prov_muhur_yaz(cikti, kok=a.kok,
                                               motor="html2udf",
                                               girdi_yolu=girdi)
        if prov_yolu:
            print("  mühür (.prov)    : %s" % prov_yolu)
        else:
            print("  [UYARI] mühür basılamadı: %s — mühürsüz ürün teslim "
                  "kapısında (FİLO-TAZELİK) RED yer." % prov_hata,
                  file=sys.stderr)
        if not dogrulama["gecerli"]:
            for h in dogrulama["hatalar"]:
                print("  [HATA] %s" % h, file=sys.stderr)
            sys.exit(1)

        # GÖREV B (P0-B, v0.5.5) — ÜRETİM-ANI ÖN-DENETİM: UDF fiilen üretildi
        # (avukat egemen, ENGEL YOK — bu bir teslim kapısı DEĞİLDİR). BLOK
        # varsa GÖRÜNÜRLÜK garanti edilir; model bir sonraki adımı hiç
        # çağırmasa bile rapor + stdout uyarısı + DURUM.md notu diskte kalır.
        on_denetim = on_denetim_kostur(metin, kok=a.kok)
        if on_denetim["calisti"] and on_denetim["blok_sayisi"] > 0:
            denetim_yolu = cikti + ".denetim.txt"
            try:
                with open(denetim_yolu, "w", encoding="utf-8") as f:
                    f.write(on_denetim["rapor"])
            except OSError as e:
                denetim_yolu = None
                print("UYARI: ön-denetim raporu yazılamadı: %s" % e, file=sys.stderr)
            print("")
            print("!" * 66)
            print("UYARI: UDF ÖN-DENETİM %d BLOK buldu (İçtihat Muhakeme Zinciri "
                  "+ Atıf/Künye Teyit) — bu bir TESLİM ENGELİ DEĞİLDİR, UDF "
                  "üretildi; ama teslimden ÖNCE avukat gözü ŞARTTIR."
                  % on_denetim["blok_sayisi"])
            if denetim_yolu:
                print("  Ön-denetim raporu: %s" % denetim_yolu)
            print("!" * 66)
            not_satiri = ("%s: teslim adayı üretildi, denetim: BLOK %d"
                          % (os.path.basename(cikti), on_denetim["blok_sayisi"]))
            if denetim_yolu:
                not_satiri += " (bkz. %s)" % os.path.basename(denetim_yolu)
            _durum_md_uyari_ekle(a.kok, not_satiri)
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
