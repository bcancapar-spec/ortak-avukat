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

JUST = "text-align:justify; line-height:1.4; margin-top:0pt; margin-bottom:6pt"
QUOTE = "text-align:justify; line-height:1.3; margin-left:36pt; margin-right:18pt; margin-top:6pt; margin-bottom:6pt"


def kacis(t):
    """HTML özel karakterlerini escape eder (&, <, >) — rehber A.3: escape ÖNCE, işaretleme SONRA."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def satir_ici(t):
    """Satır içi markdown → HTML. Önce escape, sonra işaretleme (kaçış çakışmasını önler)."""
    t = kacis(t)
    # [metin](url) -> okunabilir düz metin (UDF'de tıklanabilir bağlantı beklenmez)
    t = re.sub(r"\[([^\]]+)\]\(https?://([^\)]+)\)", lambda m: m.group(1) + " - " + m.group(2), t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
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
    `<p>` bazlı paragraflama, `<br>` KULLANILMAZ.
    """
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
                bg = ' style="background-color:#EEEEEE"' if ri == 0 else ""
                for c in cells:
                    body = satir_ici(c) if c else "&nbsp;"
                    if ri == 0 and "<strong>" not in body:
                        body = "<strong>%s</strong>" % body
                    out.append("<td%s>%s</td>" % (bg, body))
                out.append("</tr>")
            out.append("</table>")
            continue

        # Başlıklar
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            txt = satir_ici(m.group(2))
            if lvl == 1:
                out.append('<p style="text-align:center; margin-top:0pt; margin-bottom:12pt">'
                            '<span style="font-size:14pt"><strong>%s</strong></span></p>' % txt)
            elif lvl == 2:
                out.append('<p style="text-align:left; margin-top:14pt; margin-bottom:8pt">'
                            '<span style="font-size:13pt"><strong>%s</strong></span></p>' % txt)
            else:
                out.append('<p style="text-align:left; margin-top:12pt; margin-bottom:6pt">'
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
                out.append("<li><p style=\"%s\">%s</p></li>" % (JUST, satir_ici(it)))
            out.append("</ol>")
            continue

        # Madde imli liste
        if re.match(r"^[-*+]\s+", s):
            items = []
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*+]\s+", "", lines[i].strip())); i += 1
            out.append("<ul>")
            for it in items:
                out.append("<li><p style=\"%s\">%s</p></li>" % (JUST, satir_ici(it)))
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
        out.append('<p style="%s">%s</p>' % (JUST, satir_ici(" ".join(buf))))

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
