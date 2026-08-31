# -*- coding: utf-8 -*-
"""udf_md.py için pytest süiti — TAMAMEN SENTETİK girdi.

GİZLİLİK KURALI: bu süitte hiçbir gerçek müvekkil dosyası kullanılmaz ve
hiçbir belge içeriği geçmez. Bütün `.udf` girdileri aşağıdaki `Kurgu`
sınıfıyla, testin kendi uydurma metniyle üretilir — süit CI'da koşar.

Süit K1–K10'un HER BİRİNİ ayrı ayrı kilitler; her testin adı hangi kuralı
bağladığını söyler.
"""
import hashlib
import io
import json
import os
import struct
import sys
import zipfile

import pytest

# Modül eklentinin içinde yaşar; ailenin yerleşik deseniyle YOLDAN yüklenir
# (tests/ altına kopya BIRAKILMAZ — ikiz dosya yasağı).
import importlib.util as _iu
_MODUL_YOLU = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "plugins", "ortak-avukat", "skills", "oa-ingest", "scripts", "udf_md.py")
_spec = _iu.spec_from_file_location("udf_md", os.path.normpath(_MODUL_YOLU))
udf_md = _iu.module_from_spec(_spec)
_spec.loader.exec_module(udf_md)
sys.modules["udf_md"] = udf_md
from udf_md import (BIRLESIK_IM, Metin, main, udf_markdown_cikar,
                           _CF_RE, _gercek_tur, _gorunur_temizle, _olcum_metni)

ZWS = "​"


# ===========================================================================
# SENTETİK UDF KURUCUSU
# ===========================================================================

def _oz(attr):
    return "".join(' %s="%s"' % (k, v) for k, v in attr.items())


class Kurgu:
    """CDATA'yı ve offsetleri TUTARLI üreten sentetik UDF kurucusu.

    Çağrı sırası = belge sırasıdır: her `p()` çağrısı metni CDATA'nın sonuna
    ekler ve o metne işaret eden span'leri döndürür. Paragraf sonundaki tek
    `\\n`, K2'nin tarif ettiği "aradaki bir karakter" boşluğudur.
    """

    def __init__(self, format_id="1.8"):
        self.format_id = format_id
        self._cd = []
        self.off = 0

    # -- düşük düzey ------------------------------------------------------
    def span(self, metin, etiket="content", **attr):
        bas = self.off
        self._cd.append(metin)
        self.off += len(metin)
        return '<%s startOffset="%d" length="%d"%s/>' % (
            etiket, bas, len(metin), _oz(attr))

    def ham_cdata(self, metin):
        """Hiçbir span'in işaret etmediği metin ekle (K2 boşluk kurgusu)."""
        self._cd.append(metin)
        self.off += len(metin)

    def satir_sonu(self):
        self.ham_cdata("\n")

    # -- blok düzeyi ------------------------------------------------------
    def p(self, parcalar, **pattr):
        """parcalar: str | (metin, {öznitelik}) | (etiket, metin, {öznitelik})"""
        ic = ""
        for pr in parcalar:
            if isinstance(pr, str):
                ic += self.span(pr)
            elif len(pr) == 2:
                ic += self.span(pr[0], **pr[1])
            else:
                ic += self.span(pr[1], etiket=pr[0], **pr[2])
        self.satir_sonu()
        return "<paragraph%s>%s</paragraph>" % (_oz(pattr), ic)

    def bos_p(self, **pattr):
        """K3 — boş paragraf: CDATA'ya ZWS + `\\n`, length=2 yer tutucu."""
        ic = self.span(ZWS + "\n")
        return "<paragraph%s>%s</paragraph>" % (_oz(pattr), ic)

    def sayfa_sonu(self):
        """K5 — içinde tek boş paragraf taşıyan sarmalayıcı."""
        return "<page-break>%s</page-break>" % self.bos_p()

    # -- birleştirme ------------------------------------------------------
    def belge(self, elements_xml, ek_kok=""):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<template format_id="%s">'
            '<content><![CDATA[%s]]></content>'
            '<properties><pageFormat mediaSizeName="A4"/></properties>'
            '<elements resolver="hvl-default">%s</elements>'
            '<styles><style name="hvl-default" family="Times New Roman" '
            'size="12" description="Gövde"/></styles>'
            '%s</template>' % (self.format_id, "".join(self._cd),
                               elements_xml, ek_kok)
        ) .encode("utf-8")


def hucre(ic, **attr):
    return "<cell%s>%s</cell>" % (_oz(attr), ic)


def satir(*hucreler, **attr):
    return "<row%s>%s</row>" % (_oz(attr), "".join(hucreler))


def tablo(*satirlar, **attr):
    return "<table%s>%s</table>" % (_oz(attr), "".join(satirlar))


def yaz_udf(tmp_path, xml_baytlari, ad="sentetik.udf", imzali=False,
            zipli=True):
    yol = tmp_path / ad
    if not zipli:
        yol.write_bytes(xml_baytlari)
        return str(yol)
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml_baytlari)
        if imzali:
            z.writestr("imza.sgn", b"SENTETIK-IMZA-BLOGU")
    yol.write_bytes(tampon.getvalue())
    return str(yol)


def crc_boz(ham):
    """Merkezî dizindeki CRC alanını boz (zipfile 'Bad CRC' ile reddetsin).

    Merkezî başlık: sig(4) sürüm(2) gerek(2) bayrak(2) yöntem(2) saat(2)
    tarih(2) CRC(4) -> CRC ofseti 16.
    """
    i = ham.find(b"PK\x01\x02")
    assert i > 0, "merkezî dizin bulunamadı"
    return ham[:i + 16] + b"\xde\xad\xbe\xef" + ham[i + 20:]


def basit_belge(metinler=("Birinci satır", "İkinci satır"), format_id="1.8"):
    k = Kurgu(format_id)
    bloklar = "".join(k.p([m]) for m in metinler)
    return k.belge(bloklar)


# ===========================================================================
# K1 — OFFSET BİRİMİ (UTF-16 mi codepoint mi)
# ===========================================================================

def test_k1_bmp_ici_metinde_ayrisma_uyarisi_yok(tmp_path):
    """Türkçe hukuk metni tamamen BMP içindedir: iki sayım ÖZDEŞTİR."""
    yol = yaz_udf(tmp_path, basit_belge(("Şüpheli müdafii İĞÜÇÖŞ", "ikinci")))
    md, k = udf_markdown_cikar(yol)
    assert k["hata"] == ""
    assert k["bmp_disi_karakter"] == 0
    assert not any("K1/" in u for u in k["uyarilar"])
    assert "Şüpheli müdafii İĞÜÇÖŞ" in md


def test_k1_bmp_disi_karakter_uyari_uretir(tmp_path):
    """BMP dışı karakterde iki sayım AYRIŞIR; şart, uyarı basılmasıdır."""
    # CDATA: "AB😀CD\n" -> UTF-16 birimleri: A0 B1 😀(2,3) C4 D5 \n6
    cdata = "AB\U0001F600CD\n"
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<template format_id="1.8">'
           '<content><![CDATA[%s]]></content>'
           '<elements><paragraph>'
           '<content startOffset="0" length="6"/>'
           '</paragraph></elements>'
           '<styles><style name="hvl-default"/></styles>'
           '</template>' % cdata).encode("utf-8")
    yol = yaz_udf(tmp_path, xml)
    md, k = udf_markdown_cikar(yol)
    assert k["hata"] == ""
    assert k["bmp_disi_karakter"] == 1
    assert any("K1/BMP-dışı" in u for u in k["uyarilar"])
    assert any("K1/ayrışma" in u for u in k["uyarilar"]), \
        "UTF-16 ve codepoint dilimleri farklı olmalıydı"
    # UTF-16 sayımı seçildiği için "\n" değil "AB😀CD" alınır.
    assert "AB\U0001F600CD" in md


def test_k1_metin_sinifi_utf16_haritasini_dogru_kurar():
    T = Metin("AB\U0001F600CD")
    assert T.birim == 6           # UTF-16 kod birimi sayısı
    assert T.dilim(0, 6) == "AB\U0001F600CD"
    assert T.dilim(4, 2) == "CD"
    assert T.bmp_disi == 1


# ===========================================================================
# K2 — BOŞLUKSUZ (GAP-FREE) DÖŞEME
# ===========================================================================

def test_k2_gapfree_dosyada_bosluk_uyarisi_yok(tmp_path):
    yol = yaz_udf(tmp_path, basit_belge())
    md, k = udf_markdown_cikar(yol)
    assert k["bosluk_gorunur"] == 0
    assert k["cakisma_karakter"] == 0
    assert not any("K2/" in u for u in k["uyarilar"])
    # Satır sonları span dışıdır; bu NORMALDİR ve uyarı üretmez.
    assert k["bosluk_satir_sonu"] >= 2


def test_k2_gorunur_bosluk_sessiz_gecilmez(tmp_path):
    """Hiçbir yapıya bağlanmamış GÖRÜNÜR metin varsa uyarı ZORUNLUDUR."""
    k0 = Kurgu()
    b1 = k0.p(["bağlı metin"])
    k0.ham_cdata("KAYIP-METIN\n")        # hiçbir span işaret etmiyor
    b2 = k0.p(["yine bağlı"])
    yol = yaz_udf(tmp_path, k0.belge(b1 + b2))
    md, k = udf_markdown_cikar(yol)
    assert k["bosluk_gorunur"] == len("KAYIP-METIN")
    assert any("K2/boşluk" in u for u in k["uyarilar"])


def test_k2_cakisma_sessiz_gecilmez(tmp_path):
    """Aynı CDATA aralığı iki span tarafından gösterilirse ÇAKIŞMA uyarısı."""
    cdata = "ABCDEF\n"
    xml = ('<template format_id="1.8">'
           '<content><![CDATA[%s]]></content>'
           '<elements>'
           '<paragraph><content startOffset="0" length="4"/></paragraph>'
           '<paragraph><content startOffset="2" length="4"/></paragraph>'
           '</elements><styles/></template>' % cdata).encode("utf-8")
    yol = yaz_udf(tmp_path, xml)
    md, k = udf_markdown_cikar(yol)
    assert k["cakisma_karakter"] == 2
    assert any("K2/çakışma" in u for u in k["uyarilar"])


# ===========================================================================
# K3 — ZWS / GÖRÜNMEZ KARAKTER AYIKLAMA
# ===========================================================================

def test_k3_zws_ciktiya_sizmaz(tmp_path):
    k0 = Kurgu()
    b = k0.p(["metin" + ZWS + "içi"]) + k0.bos_p() + k0.p(["ikinci"])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert ZWS not in md, "ZWS çıktıya sızdı (K3 ihlali)"
    assert "metiniçi" in md


def test_cf_regexi_unicodedata_ile_birebir():
    """HIZ YOLU DENETİMİ — regex ile `unicodedata` AYNI kümeyi vermeli.

    Modül, görünmez karakteri hızlı taramak için bir aralık regexi kullanır;
    ÖLÇÜT ise `unicodedata.category(ch) == 'Cf'`. Python'un Unicode sürümü
    değişip yeni bir Cf karakteri eklenirse bu test kırılır ve regex güncellenir
    — sessizce ayrışmaz.
    """
    import unicodedata
    ayrisan = [cp for cp in range(0x110000)
               if (unicodedata.category(chr(cp)) == "Cf")
               != bool(_CF_RE.fullmatch(chr(cp)))]
    assert not ayrisan, "regex ile unicodedata %d kod noktasında ayrıştı" % len(ayrisan)


def test_gorunur_temizle_ascii_yolu_dogru():
    assert _gorunur_temizle("duz ascii") == "duz ascii"
    assert _gorunur_temizle("a" + ZWS + "b") == "ab"
    assert _gorunur_temizle("a﻿b­c") == "abc"
    assert _gorunur_temizle("İĞÜÇÖŞ") == "İĞÜÇÖŞ"     # Cf değil, korunur


def test_k3_bos_paragraf_sahte_satir_uretmez(tmp_path):
    k0 = Kurgu()
    b = k0.p(["ilk"]) + k0.bos_p() + k0.bos_p() + k0.bos_p() + k0.p(["son"])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert md == "ilk\n\nson", repr(md)


# ===========================================================================
# K4 — SATIR SONU KIRPMA
# ===========================================================================

def test_k4_ardisik_bos_satir_birikmez(tmp_path):
    k0 = Kurgu()
    b = "".join(k0.p([m]) + k0.bos_p() for m in ("bir", "iki", "üç"))
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert "\n\n\n" not in md, "3+ ardışık satır sonu birikti (K4 ihlali)"
    assert " \n" not in md and "\t\n" not in md, "satır sonu öncesi boşluk kaldı"
    assert not md.endswith("\n")


# ===========================================================================
# K5 — SAYFA SONU
# ===========================================================================

def test_k5_sayfa_sonu_gorunur_icerik_uretmez(tmp_path):
    k0 = Kurgu()
    b = k0.p(["birinci sayfa"]) + k0.sayfa_sonu() + k0.p(["ikinci sayfa"])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert ZWS not in md, "sayfa sonu ZWS'si çıktıya sızdı"
    assert k["sayfa_sonu"] == 1
    assert "<!--sayfa-sonu-->" in md
    # Görünür metin yalnız iki paragraftır.
    assert _olcum_metni(md.replace("<!--sayfa-sonu-->", "")) == \
        "birincisayfaikincisayfa"


def test_k5_sayfa_sonu_hucre_icinde_de_yutulur(tmp_path):
    """Şartname sayfa sonunun HÜCRE İÇİNDE de görülebileceğini söyler."""
    k0 = Kurgu()
    h1 = hucre(k0.p(["A1"]) + k0.sayfa_sonu())
    h2 = hucre(k0.p(["B1"]))
    t = tablo(satir(h1, h2), columnCount="2")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert ZWS not in md
    assert k["sayfa_sonu"] == 1
    assert "| A1 | B1 |" in md


# ===========================================================================
# K6 — SEKME DURAĞI AYRACI
# ===========================================================================

def test_k6_noktali_virgullu_tabset_uyari_uretir(tmp_path):
    k0 = Kurgu()
    b = k0.p([("metin", {"TabSet": "40;80;120"})])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert any("K6/sekme" in u for u in k["uyarilar"])


def test_k6_virgullu_tabset_uyari_uretmez(tmp_path):
    k0 = Kurgu()
    b = k0.p([("metin", {"TabSet": "40,80,120"})])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert not any("K6/" in u for u in k["uyarilar"])


# ===========================================================================
# K7 — TABLO (bu işin kalbi)
# ===========================================================================

def _boru_say(s):
    """KAÇIŞLANMAMIŞ boru işaretlerini say — `\\|` hücre içeriğidir, ayraç değil."""
    n, i = 0, 0
    while i < len(s):
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "|":
            n += 1
        i += 1
    return n


def _md_tablo_bicimleri(md):
    """MD çıktısındaki tabloların (satır, sütun) biçimi — bağımsız ölçüm."""
    out = []
    L = md.split("\n")
    i = 0
    while i < len(L):
        if L[i].startswith("|") and i + 1 < len(L) and \
                set(L[i + 1].replace("|", "").replace(" ", "")) <= set(":-") \
                and L[i + 1].startswith("|"):
            genislik = _boru_say(L[i]) - 1
            j, satir_sayisi = i + 2, 1
            while j < len(L) and L[j].startswith("|"):
                satir_sayisi += 1
                j += 1
            out.append((satir_sayisi, genislik))
            i = j
        else:
            i += 1
    return out


def test_k7_tablo_satir_sutun_dogru_kurulur(tmp_path):
    k0 = Kurgu()
    satirlar = []
    for r in range(2):
        satirlar.append(satir(*[hucre(k0.p(["h%d%d" % (r, c)]))
                                for c in range(3)]))
    t = tablo(*satirlar, columnCount="3")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert _md_tablo_bicimleri(md) == [(2, 3)]
    assert k["tablo"] == 1 and k["satir"] == 2 and k["hucre"] == 6
    assert k["tablo_bicimi"] == [(2, 3)]
    assert "| h00 | h01 | h02 |" in md


def test_k7_birlesik_hucre_sessizce_duzlestirilmez(tmp_path):
    """K7'nin AÇIK yasağı: korunamayan birleşme SESSİZ geçilemez."""
    k0 = Kurgu()
    r1 = satir(*[hucre(k0.p(["h0%d" % c])) for c in range(3)])
    r2 = satir(hucre(k0.p(["birleşik"])), hucre(k0.p(["son"])))  # 3 yerine 2
    t = tablo(r1, r2, columnCount="3")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert k["birlesik_hucre_satiri"] == 1
    assert any("K7/birleşik-hücre" in u for u in k["uyarilar"])
    assert BIRLESIK_IM in md, "eksik hücre AÇIK damga olmadan dolduruldu"
    assert "tablo-uyari" in md, "tablonun üstünde uyarı satırı yok"
    assert _md_tablo_bicimleri(md) == [(2, 3)]


def test_k7_columncount_genisligi_belirler(tmp_path):
    """Bildirilen sütun sayısı, görülen hücreden ÇOKSA sütun düşürülmez."""
    k0 = Kurgu()
    r1 = satir(hucre(k0.p(["a"])), hucre(k0.p(["b"])))
    t = tablo(r1, columnCount="4")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert _md_tablo_bicimleri(md) == [(1, 4)], "columnCount yok sayıldı"
    assert k["birlesik_hucre_satiri"] == 1


def _ic_ice_belge(k0):
    """Dış tablo + hücresinde iç tablo; CDATA BELGE SIRASINDA kurulur."""
    p_dis_a = k0.p(["dis-a"])
    p_ic_a, p_ic_b = k0.p(["ic-a"]), k0.p(["ic-b"])
    p_dis_b = k0.p(["dis-b"])
    ic = tablo(satir(hucre(p_ic_a), hucre(p_ic_b)), columnCount="2")
    return tablo(satir(hucre(p_dis_a + ic), hucre(p_dis_b)), columnCount="2")


def test_k7_ic_ice_tablo_varsayilan_kipte_sirayi_korur(tmp_path):
    """VARSAYILAN kip: iç tablo satır içinde, GEOMETRİSİ BİLDİRİLEREK.

    Şartnamenin başarı ölçütü (madde 1 ve 5) SIRALI kayıpsızlıktır; bu yüzden
    varsayılan kip metni yerinden oynatmaz. Prototipten farkı: satır/sütun
    sayısı açıkça yazılır (prototipte geometri kayıptı).
    """
    k0 = Kurgu()
    yol = yaz_udf(tmp_path, k0.belge(_ic_ice_belge(k0)))
    md, k = udf_markdown_cikar(yol)
    assert k["ic_ice_tablo"] == 1
    assert k["kayip_karakter"] == 0 and k["eksik_karakter"] == 0
    assert "{tablo 1x2: [ic-a / ic-b]}" in md, "iç tablo geometrisi bildirilmedi"
    assert k["ic_ice_bicimi"] == [(1, 2)]
    assert _md_tablo_bicimleri(md) == [(1, 2)]      # yalnız DIŞ tablo GFM
    yerler = [md.index("dis-a"), md.index("ic-a"), md.index("dis-b")]
    assert yerler == sorted(yerler), "okuma sırası bozuldu"


def test_k7_ayri_kip_yapiyi_korur_ama_sira_kaymasini_damgalar(tmp_path):
    """`ic_ice='ayri'`: yapı tam korunur, bedeli SIRA kaymasıdır — damgalanır."""
    k0 = Kurgu()
    yol = yaz_udf(tmp_path, k0.belge(_ic_ice_belge(k0)))
    md, k = udf_markdown_cikar(yol, ic_ice="ayri")
    assert "[iç-tablo-1]" in md, "hücrede iç tabloya atıf yok"
    assert "| ic-a | ic-b |" in md, "iç tablo ayrı MD tablosu olarak kurulmadı"
    assert len(_md_tablo_bicimleri(md)) == 2
    # Metin YERİNDEN OYNADI ama hiçbiri YOK OLMADI — ikisi ayrı ölçülür.
    assert k["kayip_karakter"] > 0
    assert k["eksik_karakter"] == 0
    assert any("kayıpsızlık/SIRA" in u for u in k["uyarilar"])


def test_k7_derin_ic_ice_tablo_ayri_kipte_belge_sirasinda_basilir(tmp_path):
    """Ölçüm: sahada 4 derinliğe kadar iç içe tablo var; blok sırası bozulmamalı."""
    k0 = Kurgu()
    p1, p2, p3 = k0.p(["derin1"]), k0.p(["derin2"]), k0.p(["derin3"])
    d3 = tablo(satir(hucre(p3)), columnCount="1")
    d2 = tablo(satir(hucre(p2 + d3)), columnCount="1")
    d1 = tablo(satir(hucre(p1 + d2)), columnCount="1")
    yol = yaz_udf(tmp_path, k0.belge(d1))
    md, k = udf_markdown_cikar(yol, ic_ice="ayri")
    assert k["ic_ice_tablo"] == 2
    yerler = [md.index("derin1"), md.index("derin2"), md.index("derin3")]
    assert yerler == sorted(yerler), "iç içe tablolar belge sırasında değil"
    assert len(_md_tablo_bicimleri(md)) == 3
    assert k["tablo_bicimi"] == [(1, 1), (1, 1), (1, 1)]


def test_k7_derin_ic_ice_varsayilan_kipte_kayipsiz(tmp_path):
    k0 = Kurgu()
    p1, p2, p3 = k0.p(["derin1"]), k0.p(["derin2"]), k0.p(["derin3"])
    d3 = tablo(satir(hucre(p3)), columnCount="1")
    d2 = tablo(satir(hucre(p2 + d3)), columnCount="1")
    d1 = tablo(satir(hucre(p1 + d2)), columnCount="1")
    yol = yaz_udf(tmp_path, k0.belge(d1))
    md, k = udf_markdown_cikar(yol)
    assert k["kayip_karakter"] == 0 and k["eksik_karakter"] == 0
    assert k["ic_ice_bicimi"] == [(1, 1), (1, 1)]
    assert md.index("derin1") < md.index("derin2") < md.index("derin3")


def test_k7_rowspans_yorumlanamadigi_soylenir(tmp_path):
    k0 = Kurgu()
    t = tablo(satir(hucre(k0.p(["a"])), hucre(k0.p(["b"]))),
              columnCount="2", rowSpans="457")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert any("K7/rowSpans" in u for u in k["uyarilar"])


def test_k7_tek_satirli_tablo_baslik_degil_diye_isaretlenir(tmp_path):
    k0 = Kurgu()
    t = tablo(satir(hucre(k0.p(["veri1"])), hucre(k0.p(["veri2"]))),
              columnCount="2")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert "tablo:tek-satir" in md


def test_k7_hucre_icindeki_boru_isareti_kacislanir(tmp_path):
    k0 = Kurgu()
    t = tablo(satir(hucre(k0.p(["a|b"])), hucre(k0.p(["c"]))), columnCount="2")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    assert "a\\|b" in md
    assert _md_tablo_bicimleri(md) == [(1, 2)]


# ===========================================================================
# K8 — UZANTI YALANI
# ===========================================================================

def test_k8_pdf_uzantili_udf_markdown_uretmez(tmp_path):
    yol = tmp_path / "aslinda-pdf.udf"
    yol.write_bytes(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< >>\nendobj\n")
    md, k = udf_markdown_cikar(str(yol))
    assert md == ""
    assert k["gercek_tur"] == "pdf"
    assert k["yonlendir"] == "pdf_isle"
    assert k["hata"], "sessiz atlama YASAK — hata alanı dolu olmalı"


def test_k8_docx_uzantili_udf_yonlendirilir(tmp_path):
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<w:document/>")
    yol = tmp_path / "aslinda-docx.udf"
    yol.write_bytes(tampon.getvalue())
    md, k = udf_markdown_cikar(str(yol))
    assert md == ""
    assert k["gercek_tur"] == "docx"
    assert k["yonlendir"] == "docx_isle"
    assert k["hata"]


def test_k8_ole2_eski_doc_taninir(tmp_path):
    yol = tmp_path / "aslinda-doc.udf"
    yol.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512)
    md, k = udf_markdown_cikar(str(yol))
    assert md == ""
    assert k["gercek_tur"] == "ole2"
    assert k["hata"]


def test_k8_ciplak_xml_udf_okunabilir(tmp_path):
    """Ölçüm: sahada ZIP olmayan dosyaların çoğu ÇIPLAK XML'dir; kurtarılır."""
    yol = yaz_udf(tmp_path, basit_belge(), zipli=False)
    md, k = udf_markdown_cikar(yol)
    assert k["hata"] == ""
    assert k["kabuk"] == "ciplak_xml"
    assert "Birinci satır" in md


def test_k8_bozuk_crc_arsiv_kurtarilir_ve_damgalanir(tmp_path):
    yol = tmp_path / "bozuk.udf"
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", basit_belge())
    yol.write_bytes(crc_boz(tampon.getvalue()))
    md, k = udf_markdown_cikar(str(yol))
    assert k["hata"] == "", "kurtarılabilir arşiv külliyat dışında kaldı"
    assert k["kabuk"] == "zip(crc-atlandi)"
    assert any("CRC DOĞRULANMADI" in u for u in k["uyarilar"])
    assert "Birinci satır" in md


def test_k8_gercek_tur_tespiti_bayta_bakar():
    assert _gercek_tur(b"%PDF-1.4")[0] == "pdf"
    assert _gercek_tur(b"{\\rtf1")[0] == "rtf"
    assert _gercek_tur(b"")[0] == "bos"
    assert _gercek_tur(b"\x00\x01\x02\x03")[0] == "bilinmeyen"


# ===========================================================================
# K9 — E-İMZALI NÜSHA DOKUNULMAZ
# ===========================================================================

def test_k9_imzali_dosya_okuma_sirasinda_degismez(tmp_path):
    yol = yaz_udf(tmp_path, basit_belge(), imzali=True)
    once = hashlib.sha256(open(yol, "rb").read()).hexdigest()
    once_mtime = os.stat(yol).st_mtime_ns
    md, k = udf_markdown_cikar(yol)
    sonra = hashlib.sha256(open(yol, "rb").read()).hexdigest()
    assert k["imzali"] is True
    assert once == sonra, "imzalı arşiv DEĞİŞTİ (K9 ihlali)"
    assert once_mtime == os.stat(yol).st_mtime_ns
    assert "Birinci satır" in md


def test_k9_gorsel_dizini_verilse_bile_arsive_yazilmaz(tmp_path):
    png = (b"\x89PNG\r\n\x1a\n" + b"\x00" * 40)
    import base64 as _b64
    k0 = Kurgu()
    b = k0.p([("image", "¸", {"imageData": _b64.b64encode(png).decode(),
                                   "width": "10", "height": "10"})])
    yol = yaz_udf(tmp_path, k0.belge(b), imzali=True)
    once = hashlib.sha256(open(yol, "rb").read()).hexdigest()
    hedef = tmp_path / "gorseller"
    md, k = udf_markdown_cikar(yol, gorsel_dizin=str(hedef))
    assert hashlib.sha256(open(yol, "rb").read()).hexdigest() == once
    assert k["gorsel"] == 1 and k["gorsel_yazildi"] == 1
    assert (hedef / "gorsel-001.png").exists()
    assert "gorsel-001.png" in md


def test_gorsel_dizin_verilmezse_yalniz_yer_tutucu(tmp_path):
    k0 = Kurgu()
    b = k0.p([("image", "¸", {"width": "20", "height": "30"})])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert k["gorsel"] == 1 and k["gorsel_yazildi"] == 0
    assert "![gorsel-1 20x30]" in md
    assert k["kayip_karakter"] == 0, "yer tutucu karakteri kaybedildi"


# ===========================================================================
# K10 — BİÇİM İŞARETLERİ
# ===========================================================================

def test_k10_kalin_italik_alti_cizili(tmp_path):
    k0 = Kurgu()
    b = k0.p([("kalın", {"bold": "true"}),
              (" düz ", {}),
              ("italik", {"italic": "true"}),
              (" ", {}),
              ("altçizgi", {"underline": "true"})])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert "**kalın**" in md
    assert "*italik*" in md
    assert "<u>altçizgi</u>" in md, "altı çizili atıldı (K10 ihlali)"


def test_k10_ayni_bicimli_bitisik_spanlar_birlestirilir(tmp_path):
    k0 = Kurgu()
    b = k0.p([("Ka", {"bold": "true"}), ("lın", {"bold": "true"})])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert "**Kalın**" in md, "her span ayrı ** ile sarıldı"


def test_k10_tablo_sutun_hizasi_korunur(tmp_path):
    k0 = Kurgu()
    r = satir(hucre(k0.p(["sol"])),
              hucre(k0.p(["orta"]), align="center"),
              hucre(k0.p(["sağ"]), align="right"))
    t = tablo(r, columnCount="3")
    yol = yaz_udf(tmp_path, k0.belge(t))
    md, k = udf_markdown_cikar(yol)
    ayrac = [s for s in md.split("\n") if s.startswith("|") and "-" in s][0]
    assert ":---:" in ayrac, "orta hiza kayboldu"
    assert "---:" in ayrac, "sağ hiza kayboldu"


def test_liste_imleri_geri_kurulur(tmp_path):
    k0 = Kurgu()
    b = (k0.p(["Talepler:"])
         + k0.p(["birinci talep"], Numbered="true", ListLevel="0", ListId="1")
         + k0.p(["ikinci talep"], Numbered="true", ListLevel="0", ListId="1")
         + k0.p(["madde"], Bulleted="true", ListLevel="1"))
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert "1. birinci talep" in md
    assert "2. ikinci talep" in md
    assert "  - madde" in md
    assert k["liste_ogesi"] == 3


# ===========================================================================
# BİÇİM SÜRÜMLERİ / KÜNYE SÖZLEŞMESİ
# ===========================================================================

@pytest.mark.parametrize("fmt", ["1.7", "1.8"])
def test_format_1_7_ve_1_8_desteklenir(tmp_path, fmt):
    yol = yaz_udf(tmp_path, basit_belge(format_id=fmt), ad="f%s.udf" % fmt)
    md, k = udf_markdown_cikar(yol)
    assert k["hata"] == ""
    assert k["format_id"] == fmt
    assert "Birinci satır" in md


def test_kunye_sozlesmesi_tam(tmp_path):
    """İngest sözleşmesi: künye SU alanları HER koşumda taşımalı."""
    zorunlu = ("format_id", "imzali", "paragraf", "tablo", "satir", "hucre",
               "cdata_uzunluk", "kayip_karakter", "uyarilar", "sure_ms",
               "gercek_tur", "hata")
    yol = yaz_udf(tmp_path, basit_belge())
    _, k = udf_markdown_cikar(yol)
    for alan in zorunlu:
        assert alan in k, "künyede eksik alan: %s" % alan
    assert isinstance(k["uyarilar"], list)
    assert isinstance(k["imzali"], bool)
    assert isinstance(k["sure_ms"], float) and k["sure_ms"] >= 0
    # Hatalı koşumda da aynı alanlar bulunmalı.
    _, k2 = udf_markdown_cikar(str(tmp_path / "yok-boyle-dosya.udf"))
    for alan in zorunlu:
        assert alan in k2
    assert json.dumps(k, ensure_ascii=False)   # künye JSON'lanabilir olmalı


# ===========================================================================
# KAYIPSIZLIK
# ===========================================================================

def test_kayipsizlik_paragraf_tablo_bicim_karisik(tmp_path):
    k0 = Kurgu()
    b = k0.p(["Giriş paragrafı"])
    b += k0.p([("vurgulu", {"bold": "true"}), " devam"])
    r1 = satir(hucre(k0.p(["Kalem"])), hucre(k0.p(["Tutar"])))
    r2 = satir(hucre(k0.p(["Vekâlet ücreti"])), hucre(k0.p(["1.234,56 TL"])))
    b += tablo(r1, r2, columnCount="2")
    b += k0.p(["Sonuç paragrafı"])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert k["kayip_karakter"] == 0, k["uyarilar"]
    assert k["gorunur_karakter"] > 0
    for parca in ("Giriş", "vurgulu", "Vekâlet ücreti", "1.234,56 TL",
                  "Sonuç"):
        assert parca in md


def test_ustbilgi_altbilgi_metni_korunur(tmp_path):
    k0 = Kurgu()
    b = ("<header>%s</header>" % k0.p(["üst bilgi metni"])
         + k0.p(["gövde"])
         + "<footer>%s</footer>" % k0.p(["alt bilgi metni"]))
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert k["ustbilgi_altbilgi"] == 2
    assert "ÜSTBİLGİ" in md and "üst bilgi metni" in md
    assert "ALTBİLGİ" in md and "alt bilgi metni" in md
    assert k["kayip_karakter"] == 0


def test_cdata_disi_uyap_verisi_kurtarilir(tmp_path):
    """Ham okumada %100 kaybolan alan verisi ek blokta görünmeli."""
    k0 = Kurgu()
    b = k0.p(["gövde"])
    ek = "<data><mahkemeAdi>Sentetik Mahkeme</mahkemeAdi></data>"
    yol = yaz_udf(tmp_path, k0.belge(b, ek_kok=ek))
    md, k = udf_markdown_cikar(yol)
    assert k["veri_dugumu"] >= 1
    assert "Sentetik Mahkeme" in md
    md2, k2 = udf_markdown_cikar(yol, veri=False)
    assert "Sentetik Mahkeme" not in md2


def test_fieldname_alan_eki(tmp_path):
    k0 = Kurgu()
    b = k0.p([("field", "12345", {"fieldName": "dosyaNo", "fieldType": "1",
                                  "isList": "false"})])
    yol = yaz_udf(tmp_path, k0.belge(b))
    md, k = udf_markdown_cikar(yol)
    assert k["alan"] == 1
    assert "**dosyaNo**: 12345" in md


# ===========================================================================
# DAYANIKLILIK — "ASLA FIRLATMAZ"
# ===========================================================================

def test_bozuk_xml_ama_saglam_metin_duz_metne_dusurulur(tmp_path):
    """Ölçüm: külliyatta 1 dosyanın XML'i gerçekten bozuk, metni sağlam.

    Mevcut ham ingest hattı bu dosyadan METİN ÇIKARIYOR; yeni hat yapı
    kuramadı diye dosyayı tümden reddederse bu bir GERİLEME olur. Doğru
    davranış: düz metne düş, bozulmayı AÇIKÇA damgala.
    """
    yol = yaz_udf(tmp_path, "<template format_id='1.8'><content>"
                            "<![CDATA[birinci satır\nikinci satır]]></content>"
                            "<elements><paragraph <<< bozuk".encode("utf-8"))
    md, k = udf_markdown_cikar(yol)
    assert k["hata"] == "", "kurtarılabilir metin reddedildi"
    assert k["yapi_kuruldu"] is False
    assert any("XML/bozuk" in u for u in k["uyarilar"])
    assert "UYARI" in md and "birinci satır" in md and "ikinci satır" in md
    assert k["kayip_karakter"] == 0 and k["eksik_karakter"] == 0
    assert k["tablo"] == 0


def test_bozuk_xml_ve_metin_yoksa_hata(tmp_path):
    yol = yaz_udf(tmp_path, b"<template format_id='1.8'><elements>")
    md, k = udf_markdown_cikar(yol)
    assert md == ""
    assert k["hata"].startswith("xml_bozuk")


def test_saglam_dosyada_yapi_kuruldu_dogru(tmp_path):
    yol = yaz_udf(tmp_path, basit_belge())
    _, k = udf_markdown_cikar(yol)
    assert k["yapi_kuruldu"] is True


def test_bos_cdata_firlatmaz(tmp_path):
    yol = yaz_udf(tmp_path, b'<template format_id="1.8">'
                            b"<content><![CDATA[]]></content>"
                            b"<elements/><styles/></template>")
    md, k = udf_markdown_cikar(yol)
    assert md == ""
    assert k["hata"].startswith("cdata_yok")


def test_bos_dosya_firlatmaz(tmp_path):
    yol = tmp_path / "bos.udf"
    yol.write_bytes(b"")
    md, k = udf_markdown_cikar(str(yol))
    assert md == "" and k["hata"] == "bos_dosya"


def test_olmayan_dosya_firlatmaz(tmp_path):
    md, k = udf_markdown_cikar(str(tmp_path / "hic-yok.udf"))
    assert md == "" and k["hata"].startswith("okunamadi")


def test_content_xml_olmayan_zip_firlatmaz(tmp_path):
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("baska.txt", "merhaba")
    yol = tmp_path / "bos-zip.udf"
    yol.write_bytes(tampon.getvalue())
    md, k = udf_markdown_cikar(str(yol))
    assert md == ""
    assert k["hata"]


@pytest.mark.parametrize("veri", [
    b"\x00" * 64,
    b"PK\x03\x04" + b"\xff" * 60,
    b"<?xml version='1.0'?><template>",
    b"\x89PNG\r\n\x1a\n" + b"\x11" * 32,
])
def test_rastgele_baytlar_asla_firlatmaz(tmp_path, veri):
    yol = tmp_path / "fuzz.udf"
    yol.write_bytes(veri)
    md, k = udf_markdown_cikar(str(yol))      # istisna fırlatırsa test kırılır
    assert isinstance(md, str) and isinstance(k, dict)
    assert md == "" or k["hata"] == ""


def test_offset_tasmasi_sessiz_kirpilmaz(tmp_path):
    xml = ('<template format_id="1.8">'
           '<content><![CDATA[ABC\n]]></content>'
           '<elements><paragraph>'
           '<content startOffset="0" length="999"/>'
           '</paragraph></elements><styles/></template>').encode("utf-8")
    yol = yaz_udf(tmp_path, xml)
    md, k = udf_markdown_cikar(yol)
    assert k["offset_tasma"] == 1
    assert any("offset/taşma" in u for u in k["uyarilar"])
    assert "ABC" in md


def test_bozuk_offset_degeri_yutulur(tmp_path):
    xml = ('<template format_id="1.8">'
           '<content><![CDATA[ABC\n]]></content>'
           '<elements><paragraph>'
           '<content startOffset="abc" length="x"/>'
           '<content startOffset="0" length="3"/>'
           '</paragraph></elements><styles/></template>').encode("utf-8")
    yol = yaz_udf(tmp_path, xml)
    md, k = udf_markdown_cikar(yol)
    assert k["hata"] == ""
    assert "ABC" in md


# ===========================================================================
# CLI
# ===========================================================================

def test_cli_help_cikis_kodu_sifir():
    with pytest.raises(SystemExit) as e:
        main(["--help"])
    assert e.value.code == 0


def test_cli_cikti_dosyasina_yazar(tmp_path):
    girdi = yaz_udf(tmp_path, basit_belge())
    cikti = tmp_path / "cikti.md"
    kod = main([girdi, "-o", str(cikti)])
    assert kod == 0
    assert "Birinci satır" in cikti.read_text(encoding="utf-8")


def test_cli_uzanti_yalaninda_sifirdan_farkli_doner(tmp_path):
    yol = tmp_path / "pdf.udf"
    yol.write_bytes(b"%PDF-1.4\n")
    assert main([str(yol)]) == 1


def test_cli_kunye_bayragi_json_basar(tmp_path, capsys):
    girdi = yaz_udf(tmp_path, basit_belge())
    cikti = tmp_path / "c.md"
    assert main([girdi, "-o", str(cikti), "--kunye"]) == 0
    hata_akisi = capsys.readouterr().err
    assert json.loads(hata_akisi.strip())["format_id"] == "1.8"
