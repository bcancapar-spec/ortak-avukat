#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
md_udf_html.py — Markdown → UDF-uyumlu inline-CSS HTML (oa-dilekce yardımcısı)

Yargı Pro UDF rehberi (`udf_tiff_pdf_guide` MCP aracı / `yargi-udf-tiff-pdf-guide`
skill, sürüm 2026-06-22) şu kuralı koyar: "UDF her zaman `html2udf` ile yazılır,
`md2udf` ASLA kullanılmaz — Markdown yalnızca küçük bir alt küme destekler ve
gerisini sessizce düşürür." Bu script tam olarak rehberin öngördüğü ARA ADIMI
üretir: hukuki taslak markdown'ını, `npx udf-cli html2udf` girdisi olabilecek
inline-CSS HTML'e çevirir. `udf_yaz.py` bu modülü kardeş script olarak yükler
ve çıktısını hem `html2udf`'e hem de PDF üretimine (`udf_html2pdf.py`) besler.

Rehber kuralları (A.3/A.4 — bu script bunlara birebir uyar):
- tüm uzunluklar pt (bu script margin/boşluk üretmiyor; html2udf varsayılanı kullanır)
- paragraflar `<p>`, ARALARINDA `<br>` YOK — her paragraf ayrı `<p>` bloğu
- varsayılan yazı tipi Times New Roman 12pt → font-family/size YAZILMAZ (rehber A.3)
- `<tab/>` / `<page-break/>` escape edilmez (bu script hiçbirini üretmiyor)
- sayfa sonu YOK (açıkça istenmedikçe — bu script hiç üretmiyor)

Saha kökeni: bu dönüştürücü saha dosyası A dosyasında elle yazılan `md2udfhtml.py`
tohum aracının (`_oa/araclar/`) aile-standardına uyarlanmış hâlidir — o araç
canlı UYAP teslimini fiilen ÇÖZDÜ; algoritma korunmuştur.

Kullanım:
  python md_udf_html.py --girdi taslak.md --cikti taslak.udf.html
  Get-Content taslak.md -Raw | python md_udf_html.py --cikti taslak.udf.html
  python md_udf_html.py --girdi taslak.md --cikti X.html --ham   # md yorumlama yok

Yalnız standart kütüphane (re, argparse) — ek bağımlılık yoktur.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import re
import sys

# v0.5.7.2 — SAHA STANDARDI (e-imzalı gerçek nüshadan ölçüldü, bkz.
# references/udf-ic-yapi.md §6): gövde iki yana yaslı + İLK SATIR 24pt
# girintili + altında 6pt boşluk + 1,5 satır aralığı (v0.5.8.4: yorum
# koddan sapmıştı — sabit zaten 1.5 üretiyor, yorum da 1,5 der).
JUST = "text-align:justify; text-indent:24pt; line-height:1.5; margin-top:0pt; margin-bottom:6pt"
# v0.5.16.3 — KÜNYE BLOĞU: TAB ile hizalanmış başlık satırlarında ilk satır
# girintisi TAB sütununu kaydırır; gerçek UYAP dilekçelerinde bu bloklarda
# girinti YOKTUR (e-imzalı nüsha: <paragraph Alignment="3"> girintisiz).
JUST_KUNYE = "text-align:justify; line-height:1.5; margin-top:0pt; margin-bottom:6pt"
QUOTE = "text-align:justify; line-height:1.5; margin-left:36pt; margin-right:18pt; margin-top:6pt; margin-bottom:6pt"

# v0.5.16.2 — İÇ İZ AYIKLAMA (B-18/B-19 saha bulgusu: teslim evrakına araç izi
# sızması). _oa/cikti ürünleri KAYNAK-BLOĞU (<!-- kaynaklar: ... -->, v0.5.8
# konvansiyonu) ve kaynakça işaretleri (kunye_ortak KAYNAKCA_BLOK_BAS/SON) taşır;
# bunlar İÇ İZLEME verisidir. kacis() '<'/'>' karakterlerini escape ettiğinden
# yorumlar "normal paragraf" dalına düşüp html2udf'e ve PDF'e GÖRÜNÜR METİN
# olarak geçiyordu. Tek boğaz noktasında ayıklanır; kaynak .md'ye DOKUNULMAZ
# (tazelik_denetim ve kaynakça kapıları bloğu .md'den okumaya devam eder).
# MAKİNE BLOĞU (kaynakca_uret.py, `<!-- kaynakca:v1 --> … <!-- /kaynakca -->`)
# gövdesiyle birlikte çıkar: kunye_ortak'ın kendi tanımına göre "O blok
# avukatın GÖVDE METNİ DEĞİLDİR" ve önsözü aracın adını anar. B-20 avukat
# kararı (2026-10-06): kaynakça mahkemeye giden nüshaya GİRMEZ.
# v0.5.17.1: eski `<!--.*?-->` deseni yerine TEK GEÇİŞLİ tarama — kapanmayan
# çok sayıda '<!--' içeren taslakta desen her başlangıçtan metin sonuna dek
# tarıyordu (karesel).
# v0.5.17.1 / bağımsız inceleme (Fable 5.1, A1-A4): AYIKLAMA METİN YUTMAZ. Kapanmamış
# bir '<!--' (yarım kalmış not) ileride HERHANGİ bir '-->' ile — ör. dosya sonundaki
# kaynakça işaretiyle — "yorum" sanılırsa aradaki dilekçe metni UDF'den SESSİZCE
# silinirdi (veri kaybı). OA'nın kendi iç izleri tek satırlıktır (KAYNAK-BLOĞU,
# kaynakça işaretleri); bu yüzden kapanışından önce yeni '<!--' açılan, boş satır ya
# da Markdown başlığı içeren ya da _YORUM_AZAMI_KAR'ı aşan aday YORUM SAYILMAZ:
# metinde görünür kalır ve stderr'e uyarı basılır (fail-visible). Görünür sızıntı
# düzeltilebilir; sessiz kayıp düzeltilemez.
_KAYNAKCA_BAS_ICERIK = "kaynakca:v1"   # kunye_ortak.KAYNAKCA_BLOK_BAS içeriği
_KAYNAKCA_SON_ICERIK = "/kaynakca"     # kunye_ortak.KAYNAKCA_BLOK_SON içeriği
_YORUM_AZAMI_KAR = 2000
_METIN_YAPISI_RE = re.compile(r"\n[ \t]*\n|\n[ \t]*#")
_SATIR_AYRACI = " "   # paragraf içi satır sonu; satir_ici'de '.' ile eşleşir, '\n' eşleşmezdi


def _uyar(mesaj):
    print("UYARI (md_udf_html): " + mesaj, file=sys.stderr)


def _yorum_araliklari(md):
    """İç iz biçimindeki kapanmış HTML yorumlarının (başlangıç, bitiş, kırpılmış
    içerik) aralıkları, tek geçişte. HTML5 boş yorumları ('<!-->', '<!--->')
    kapanmış sayılır. Avukatın metnini yutabilecek aday (bkz. yukarı) aralığa
    GİRMEZ, metinde görünür kalır. Doğrusal: kapanış konumu önbellekte tutulur,
    her bölge en çok bir kez taranır."""
    out, i, k, supheli = [], 0, -1, 0
    while True:
        j = md.find("<!--", i)
        if j < 0:
            break
        bos = 5 if md.startswith("<!-->", j) else 6 if md.startswith("<!--->", j) else 0
        if bos:
            out.append((j, j + bos, ""))
            i = j + bos
            continue
        if k < j + 4:
            k = md.find("-->", j + 4)
            if k < 0:
                supheli += 1           # kapanışı hiç olmayan açılış: kalan metin aynen
                break
        n = md.find("<!--", j + 4, k)
        if n >= 0:                     # kapanıştan ÖNCE yeni açılış → bu açılış kapanmamış
            supheli += 1
            i = n
            continue
        icerik = md[j + 4:k]
        # tavan yalnız ÇOK SATIRLI adaya (2. tur inceleme): tek satırlık yorum paragraf sınırı
        # yutamaz; kaynak_blogu'nun çok girdili meşru satırı uzun olabilir.
        if ("\n" in icerik and len(icerik) > _YORUM_AZAMI_KAR) or _METIN_YAPISI_RE.search(icerik):
            supheli += 1               # metin yapısı taşıyan aday: yorum sayılmaz
            i = k + 3
            continue
        out.append((j, k + 3, icerik.strip()))
        i = k + 3
    if supheli:
        _uyar("%d HTML yorumu AYIKLANMADI (kapanmamış ya da dilekçe metni taşıyor) — "
              "metinde görünür kaldı; taslağı kontrol edin." % supheli)
    return out


def yorumlari_ayikla(md):
    """İç izleme artefaktlarını çıkarır: kapanışı olan MAKİNE BLOĞU (gövdesiyle
    birlikte) ve iç iz biçimindeki HTML yorumları. Makine bloğunun kapanışından
    önce ikinci bir açılış varsa (kapanışı silinmiş eski blok) sıçrama YAPILMAZ:
    yalnız o işaret çıkar, aradaki metin (EKLER, imza) kalır. Satır sonları önce LF'ye
    çevrilir (2. tur inceleme): CRLF'de boş satır koruması '\\n\\s*\\n' desenini kaçırıyordu."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")
    araliklar = _yorum_araliklari(md)
    # her aralıktan sonraki ilk kaynakça kapanışı ve SONRAKİ açılış — sondan tek geçiş
    sonraki_kapanis, sonraki_acilis, kap, ac = [None] * len(araliklar), [None] * len(araliklar), None, None
    for x in range(len(araliklar) - 1, -1, -1):
        sonraki_acilis[x] = ac
        if araliklar[x][2] == _KAYNAKCA_SON_ICERIK:
            kap = x
        elif araliklar[x][2] == _KAYNAKCA_BAS_ICERIK:
            ac = x
        sonraki_kapanis[x] = kap
    parcalar, i, x, yetim = [], 0, 0, 0
    while x < len(araliklar):
        bas, son, icerik = araliklar[x]
        if icerik == _KAYNAKCA_BAS_ICERIK:
            kp, ac = sonraki_kapanis[x], sonraki_acilis[x]
            if kp is not None and (ac is None or ac > kp):
                x = kp
                son = araliklar[x][1]
            else:
                yetim += 1
        parcalar.append(md[i:bas])
        i = son
        x += 1
    parcalar.append(md[i:])
    if yetim:
        _uyar("%d kaynakça açılış işaretinin kapanışı yok — blok gövdesi AYIKLANMADI, "
              "görünür kaldı; taslağı kontrol edin." % yetim)
    return "".join(parcalar)


def kacis(t):
    """HTML özel karakterlerini escape eder (&, <, >) — rehber A.3: escape ÖNCE, işaretleme SONRA."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def satir_ici(t):
    """Satır içi markdown → HTML. Önce escape, sonra işaretleme (kaçış çakışmasını önler)."""
    t = kacis(t)
    # v0.5.8.3 ŞEKİL STANDARDI (Can emri + Yönetmelik No. 2646 m.7: gövde 12pt,
    # gerekli hâlde küçültme serbest): karar/emsal bağlantıları PARANTEZ içinde
    # ve gövdeden 1 punto KÜÇÜK (11pt) yazılır — dilekçe akışını boğmadan
    # mahkemeye tek-tık erişim ([G4] zincirinin görsel ucu).
    # [metin](url) -> metin (url@11pt)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)",
               lambda m: m.group(1) +
               ' <span style="font-size:11pt">(' + m.group(2) + ')</span>', t)
    # düz yazılmış (https://...) parantezli bağlantılar da aynı stile çekilir.
    # v0.5.8.4: lookbehind, üstteki markdown-link dönüşümünün AZ ÖNCE ürettiği
    # span'i İKİNCİ kez sarmalamayı önler (iç içe çift span → çift stil).
    t = re.sub(r'(?<!font-size:11pt">)\((https?://[^\s\)]+)\)',
               r'<span style="font-size:11pt">(\1)</span>', t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
    # ALTI ÇİZİLİ (v0.5.16.3): ++metin++ → <u>metin</u>. UYAP dilekçe teamülünde
    # başlık bloğu etiketleri (DOSYA NO / DAVACI / VEKİLİ / KONU) ve bölüm
    # başlıkları altı çizilidir; markdown'da karşılığı yok. '__' SEÇİLMEDİ: tarih
    # boşluklarıyla (__.__.____) çakışıyor. html2udf <u>'yu underline="true" taşır.
    # v0.5.17.1 (inceleme C): yalnız sözcük sınırında — "C++ ve C++14" gibi metin bozulmasın.
    t = re.sub(r"(?<![\w+])\+\+(?=\S)(.+?)(?<=\S)\+\+(?![\w+])", r"<u>\1</u>", t)
    t = re.sub(r"`(.+?)`", r"\1", t)
    return t


def _ham_donustur(md):
    """--ham: markdown yorumlama YOK. Boş satırla ayrılmış paragraflar birebir
    (yalnız escape edilmiş) <p> bloklarına alınır — udf_yaz.py'nin eski --ham
    davranışıyla (satır/paragraf birebir) semantik olarak eşdeğerdir."""
    out = []
    for blok in re.split(r"\n\s*\n", md.strip("\n")):
        if not blok.strip():
            continue
        satirlar = [kacis(s) for s in blok.split("\n")]
        out.append('<p style="%s">%s</p>' % (JUST, "<br/>".join(satirlar)))
    return "\n".join(out) if out else '<p style="%s"></p>' % JUST


def donustur(md, ham=False):
    """Markdown metnini UDF-uyumlu inline-CSS HTML'e çevirir.

    Desteklenen bloklar: başlık (#..######), tablo, alıntı (>), numaralı/madde
    listesi, düz paragraf. Rehberin A.4 kurallarına uyar: sabit pt değerleri,
    `<p>` bazlı paragraflama, paragraflar arasında `<br>` KULLANILMAZ
    (paragraf İÇİ satır sonu `<br/>` yumuşak satırdır — v0.5.16.3).

    v0.5.16.2: İç iz (HTML yorumları, makine kaynakça bloğu) EN BAŞTA
    ayıklanır — --ham yolu da bu ayıklamadan geçer.
    """
    md = yorumlari_ayikla(md)
    if ham:
        return _ham_donustur(md)

    out = []
    lines = md.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i].rstrip()
        s = ln.strip()

        if not s or s in ("---", "***", "___"):
            i += 1
            continue

        # Tablo
        if s.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-\|]+\|$", lines[i + 1].strip()):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                r = lines[i].strip()
                if not re.match(r"^\|[\s:\-\|]+\|$", r):
                    rows.append([c.strip() for c in r.strip("|").split("|")])
                i += 1
            out.append("<table>")
            for ri, cells in enumerate(rows):
                out.append("<tr>")
                # v0.5.8.4 — 1,5 satır aralığı standardı tablo hücrelerinde de
                # geçerli: hücre İÇİ inline stil (html2udf hücre stilini
                # hücreden okur; dış <p> sarmalayıcı KULLANILMAZ).
                hucre_stil = ("background-color:#EEEEEE; line-height:1.5"
                              if ri == 0 else "line-height:1.5")
                for c in cells:
                    body = satir_ici(c) if c else "&nbsp;"
                    if ri == 0 and "<strong>" not in body:
                        body = "<strong>%s</strong>" % body
                    out.append('<td style="%s">%s</td>' % (hucre_stil, body))
                out.append("</tr>")
            out.append("</table>")
            continue

        # Başlıklar
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            txt = satir_ici(m.group(2))
            # v0.5.8.4 — başlıklar da 1,5 satır aralığı standardına dahil
            # (gövdeyle aynı; uzun başlıklar iki satıra kırıldığında sıkışmasın).
            if lvl == 1:
                out.append('<p style="text-align:center; line-height:1.5; margin-top:0pt; margin-bottom:12pt">'
                            '<span style="font-size:14pt"><strong>%s</strong></span></p>' % txt)
            elif lvl == 2:
                out.append('<p style="text-align:left; line-height:1.5; margin-top:14pt; margin-bottom:8pt">'
                            '<span style="font-size:13pt"><strong>%s</strong></span></p>' % txt)
            else:
                out.append('<p style="text-align:left; line-height:1.5; margin-top:12pt; margin-bottom:6pt">'
                            '<strong>%s</strong></p>' % txt)
            i += 1
            continue

        # Alıntı bloğu
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            para, chunks = [], []
            for b in buf:
                if b:
                    para.append(b)
                elif para:
                    chunks.append(" ".join(para)); para = []
            if para:
                chunks.append(" ".join(para))
            for c in chunks:
                out.append('<p style="%s">%s</p>' % (QUOTE, satir_ici(c)))
            continue

        # Numaralı liste
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            items = []
            while i < n:
                cur = lines[i].strip()
                mm = re.match(r"^(\d+)\.\s+(.*)$", cur)
                if mm:
                    items.append(mm.group(2)); i += 1
                elif cur.startswith(("a)", "b)", "c)")) or (cur and lines[i].startswith("    ")):
                    if items:
                        items[-1] += " " + cur
                    i += 1
                elif not cur:
                    break
                else:
                    break
            out.append("<ol>")
            for it in items:
                # v0.5.8.4 CANLI ÖLÇÜM (372): `<li><p style=...>` deseni
                # html2udf'te her maddeden sonra HAYALET boş Numbered paragraf
                # üretiyor — li içine blok <p> DEĞİL, doğrudan stillenmiş
                # span/metin verilir.
                out.append('<li><span style="line-height:1.5">%s</span></li>'
                           % satir_ici(it))
            out.append("</ol>")
            continue

        # Madde imli liste
        if re.match(r"^[-*+]\s+", s):
            items = []
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*+]\s+", "", lines[i].strip())); i += 1
            out.append("<ul>")
            for it in items:
                # bkz. <ol> notu — hayalet boş paragraf önlemi burada da geçerli.
                out.append('<li><span style="line-height:1.5">%s</span></li>'
                           % satir_ici(it))
            out.append("</ul>")
            continue

        # Normal paragraf
        buf = [s]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", ">", "|", "---"))
                    or re.match(r"^\d+\.\s", nxt) or re.match(r"^[-*+]\s", nxt)):
                break
            buf.append(nxt); i += 1
        # v0.5.16.3 — SATIR SONU ANLAMLIDIR: dilekçede yazarın koyduğu satır sonu
        # (künye bloğu, imza bloğu, adres ve taraf satırları) korunur. Markdown'ın
        # "tek satır sonu = aynı satır" kuralı hukuk metninde başlık bloğunu tek
        # paragrafa eziyordu (saha bulgusu: "MAHKEME: ... DOSYA NO: ..." yan yana).
        stil = JUST_KUNYE if any("\t" in x for x in buf) else JUST
        # v0.5.17.1 (inceleme B): satırlar U+2028 ile birleşip TEK seferde işlenir ki
        # satıra yayılan vurgu (`**…\n…**`) da <strong> olsun; ayraç sonra <br/> olur.
        out.append('<p style="%s">%s</p>' % (
            stil, satir_ici(_SATIR_AYRACI.join(buf)).replace(_SATIR_AYRACI, "<br/>")))

    return "\n".join(out)


def _kok_coz(yol, kok):
    """--kok verilmişse göreli yolu ona göre çözer; verilmemişse CWD'ye göre
    mutlaklaştırır. Güvenlik sınırı DEĞİL — yalnız yol kısayolu kolaylığıdır
    (bu araç ağdan gelen düşman girdi işlemez, doğrudan avukat/model çağırır)."""
    if yol is None:
        return None
    if os.path.isabs(yol) or not kok:
        return os.path.abspath(yol)
    return os.path.abspath(os.path.join(kok, yol))


def _atomik_yaz(yol, metin):
    """tmp + os.replace: yarım yazılmış dosya asla nihai adda görünmez."""
    tmp = yol + ".tmp-%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(metin)
    os.replace(tmp, yol)


def main():
    ap = argparse.ArgumentParser(
        description="Markdown → UDF-uyumlu inline-CSS HTML (udf-cli html2udf girdisi).")
    ap.add_argument("--girdi", "-g", metavar="YOL",
                     help="Girdi markdown dosyası. Verilmezse stdin okunur.")
    ap.add_argument("--cikti", "-c", metavar="YOL", required=True,
                     help="Çıktı .html dosyası (atomik yazılır).")
    ap.add_argument("--kok", metavar="KLASOR", default=None,
                     help="Göreli --girdi/--cikti yolları bu köke göre çözülür.")
    ap.add_argument("--ham", action="store_true",
                     help="Markdown yorumlama; paragrafları birebir <p> olarak al.")
    a = ap.parse_args()

    girdi = _kok_coz(a.girdi, a.kok)
    cikti = _kok_coz(a.cikti, a.kok)

    if girdi:
        with open(girdi, "r", encoding="utf-8", errors="replace") as f:
            md = f.read()
    else:
        if _sys.stdin is None:
            sys.exit("HATA: --girdi verilmedi ve stdin yok.")
        md = _sys.stdin.read()

    html = donustur(md, ham=a.ham)
    _atomik_yaz(cikti, html)
    blok_sayisi = html.count("<p ") + html.count("<table>")
    print("UDF-HTML yazıldı: %s (%d karakter, %d blok)" % (cikti, len(html), blok_sayisi))


if __name__ == "__main__":
    main()
