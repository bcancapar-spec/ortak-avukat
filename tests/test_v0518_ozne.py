# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — ÖZNE EŞLEŞTİRİCİ KURAL SETİ (oa-vakia/scripts/ozne_eslestirici.py).

Kullanıcı kararı (2026-10-05): YANLIŞ BİRLEŞTİRME, FAZLADAN SORUDAN DAHA KÖTÜDÜR.
Tanım ve ölçüm: özne eşleştirici ölçüm raporu §3.2 (21 kurgu çift; eski motor 8 ayrı
kişiyi BAGLA'dı, aynı kişinin 2 yazımını sessiz geçti). Kabul ölçütü: raporun
tüm kurgu çiftleri testte; farklı kişide yanlış BAGLA = 0; aynı kişide sessiz
kaçak = 0; bilinen bedel (OCR varyantı BAGLA→SOR) testte belgeli.

Bu uygulama raporun kural setini daha da sıkılaştırır — her inceltme yalnız
BAGLA'yı azaltır ya da sessizi SOR'a çevirir, hiç yeni BAGLA kaynağı açmaz:
(a) BAGLA yalnız YAZIM eşdeğerliğinde (sayısal yakınlık ve OCR jokeri tek
    başına yetmez — kardeş adları "Serkan"/"Serhan" 0,922 alıyor);
(b) Türkçe harf katlaması yalnız ASCII yazımı tanır ("Gülşen"/"Gülsen" SOR);
(c) sıra farkı yalnız soyad tutarlıysa BAGLA ("Şahin Yıldız"/"Yıldız Şahin" SOR);
(d) baş harf, çift soyad, kurum eki, OCR karışıklığı kısa adda sessiz kalmaz;
(e) tür koruması BAGLA zinciri ve SOR komşuluğu üzerinden de delinemez.
(a)-(e)'nin bir kısmı Fable 5.1 salt okunur karşı-tez turlarında önerildi;
hepsi aşağıda kurgu örneklerle kilitli.

Bütün adlar kurgudur. Testler ağsız, tarihsiz, rastgelesiz ve
deterministiktir (süre ölçmez).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
VAKIA_DIZIN = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-vakia"
SCRIPT = VAKIA_DIZIN / "scripts" / "ozne_eslestirici.py"
VAKIA = VAKIA_DIZIN / "scripts" / "vakia_matris.py"
SKILL_MD = VAKIA_DIZIN / "SKILL.md"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = _yukle("ozne_eslestirici_v0518", SCRIPT)


def _k(a, b, t1=None, t2=None):
    return m.ozne_karari(a, b, t1, t2)


# ── 1) Raporun kurgu tablosu (§3.2) — karar ve skor ─────────────────────────
# (ad1, ad2, gerçekte, beklenen karar, beklenen skor)
TABLO = [
    ("Ahmet Kaya", "Ahmet Kara", "farkli", "AVUKATA-SOR", 0.867),
    # Raporda 0,919 "önek-uzantı tavanı" ile kırpılmış değerdir; bu uygulama
    # gerçek parça skorunu gösterir (0,943) — karar aynı: SOR.
    ("Ali Demir", "Ali Demirci", "farkli", "AVUKATA-SOR", 0.943),
    ("Hasan Çelik", "Hasan Çetin", "farkli", None, 0.787),
    ("Fatma Aksoy", "Fatma Aksu", "farkli", "AVUKATA-SOR", 0.848),
    ("Ayşe Kaya", "Ayşe Kayaalp", "farkli", "AVUKATA-SOR", 0.914),
    ("Mustafa Şahin", "Mustafa Şahan", "farkli", "AVUKATA-SOR", 0.907),
    ("Kemal Öz", "Kemal Özer", "farkli", "AVUKATA-SOR", 0.867),
    ("Selin Er", "Selin Ek", "farkli", None, 0.700),
    ("Ahmet Yılmaz", "Ahmet Yılmaz İnşaat Ltd. Şti.", "kisi-sirket", "AVUKATA-SOR", 0.889),
    ("Mehmet Yılmaz", "YILMAZ Mehmet", "ayni", "BAGLA", 1.0),
    ("İsmail Güneş", "ISMAIL GUNES", "ayni", "BAGLA", 1.0),
    ("Hüseyin Öztürk", "Huseyin Ozturk", "ayni", "BAGLA", 1.0),
    ("Ömer Faruk Şen", "Omer Faruk Sen", "ayni", "BAGLA", 1.0),
    ("Ayşegül Kaya", "Ayşe Gül Kaya", "ayni", "BAGLA", 1.0),
    # Raporun önerisinde BAGLA 0,950; bu uygulamada OCR jokeri tek başına BAGLA
    # ettirmez (joker birden çok ada uyabilir) → SOR. Kullanıcının seçtiği bedel.
    ("Mehmet Yılmaz", "Mehmet Y.lmaz", "ayni", "AVUKATA-SOR", 0.950),
    ("Mehmet Yılmaz", "Mehmet Yılrnaz", "ayni", "AVUKATA-SOR", 0.894),
    ("Mehmet Ali Yılmaz", "Mehmet Yılmaz", "muhtemelen-ayni", "AVUKATA-SOR", 0.914),
]
# Raporun "+4 diakritik çifti" için kurgu karşılıkları (ASCII yazım → BAGLA).
DIAKRITIK = [("Çiğdem Işık", "CIGDEM ISIK"), ("Gülşen Çağlar", "GULSEN CAGLAR"),
             ("Şükrü Öğüt", "Sukru Ogut"), ("Ünal Ağca", "UNAL AGCA")]
# Kardeş/akraba adı kalıpları ve diğer "ayrı kişi olabilir" çiftleri.
KARDES = [("Serkan Yıldız", "Serhan Yıldız"), ("Gökhan Aydın", "Gökcan Aydın"),
          ("Sevda Kaya", "Seda Kaya"), ("Selin Kurt", "Selim Kurt"),
          ("Aysel Polat", "Aysen Polat"), ("Gülsen Tekin", "Gülen Tekin"),
          ("Seda Kaya", "Sedat Kaya"), ("Nur Yılmaz", "Nuri Yılmaz"),
          ("Emin Koç", "Emine Koç"), ("Barış Öztürk", "Haldun Öztürk")]
AYRI_OLABILIR = [("Gülşen Kaya", "Gülsen Kaya"), ("Mehmet Can Kaya", "Mehmet Çankaya"),
                 ("Şahin Yıldız", "Yıldız Şahin"), ("Ali Mehmet Yılmaz", "Mehmet Ali Yılmaz"),
                 ("Ha.an Kaya", "Hasan Kaya"), ("Yılmaz İnşaat A.Ş.", "Yılmaz İnşaat Ltd. Şti."),
                 ("MEHMET YILMAZ", "YILMAZ MEHMET")]


@pytest.mark.parametrize("a,b,gercek,karar,skor", TABLO)
def test_rapor_tablosu_kurgu_ciftleri(a, b, gercek, karar, skor):
    k = _k(a, b)
    assert k["karar"] == karar, (a, b, k)
    assert round(k["skor"], 3) == skor, (a, b, k)


def test_farkli_kiside_yanlis_bagla_sifir():
    farkli = [(a, b) for a, b, g, _, _ in TABLO if g in ("farkli", "kisi-sirket")] + KARDES + AYRI_OLABILIR
    bagla = [(a, b) for a, b in farkli if _k(a, b)["karar"] == "BAGLA"]
    assert bagla == []
    # "ayrı olabilir" çiftleri sessiz de kalmaz: belirsizlik avukata SORU olarak çıkar
    assert all(_k(a, b)["karar"] == "AVUKATA-SOR" for a, b in AYRI_OLABILIR)


def test_ayni_kiside_sessiz_kacak_sifir():
    ayni = [(a, b) for a, b, g, _, _ in TABLO if g.startswith(("ayni", "muhtemelen"))] + DIAKRITIK
    ayni += [("Osman Balcı", "Osrnan Balcı"), ("Emine Arslan", "Ernine Arslan"),
             ("M. Yılmaz", "Mehmet Yılmaz"), ("M.Yılmaz", "Mehmet Yılmaz"),
             ("M.A. Yılmaz", "Mehmet Ali Yılmaz"), ("Y.LMAZ Mehmet", "Mehmet Yılmaz"),
             ("Ayşe Kaya-Demir", "Ayşe Demir"), ("lsa Kaya", "İsa Kaya"),
             ("Ahmet Yılmaz İnş. Ltd. Şti.", "Ahmet Yılmaz İnşaat Limited Şirketi")]
    sessiz = [(a, b) for a, b in ayni if _k(a, b)["karar"] is None]
    assert sessiz == []
    for a, b in DIAKRITIK:
        assert _k(a, b)["karar"] == "BAGLA", (a, b)


def test_bilinen_bedel_ocr_varyanti_soru_olur():
    """BEDEL (kabul edildi): OCR varyantı eski motorda BAGLA idi ("Yılrnaz"
    0,956; "Y.lmaz" 0,985); artık AVUKATA-SOR. Yanlış birleştirme riskine
    karşı fazladan bir soru."""
    k = _k("Mehmet Yılmaz", "Mehmet Yılrnaz")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "ocr-karisikligi"
    assert m._dize_skoru(["mehmet", "yilmaz"], ["mehmet", "yilrnaz"]) >= 0.92   # eski yol BAGLA'ydı
    k = _k("Mehmet Yılmaz", "Mehmet Y.lmaz")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "ocr-joker"


# ── 2) Güvenlik inceltmeleri ─────────────────────────────────────────────────

def test_kardes_adlari_sayisal_yakinlikla_bagla_olmaz():
    """Rapor kuralının harfi harfine uygulanması (parça min ≥0,92 → BAGLA)
    bu çiftleri birleştirirdi; yazım eşdeğerliği yoksa karar SOR'dur."""
    yuksek = 0
    for a, b in KARDES[:-1]:
        k = _k(a, b)
        assert k["karar"] == "AVUKATA-SOR", (a, b, k)
        if k["skor"] >= m.BAGLA_ESIK:
            yuksek += 1
            assert "yuksek_benzerlik_ama_yapisal_kanit_yok" in k["nedenler"]
    assert yuksek >= 7  # ölçüm: dokuz kardeş çiftinden en az yedisi ≥0,92


def test_onek_uzantisi_gerekcede():
    assert "onek_uzantisi=demir/demirci" in _k("Ali Demir", "Ali Demirci")["nedenler"]
    assert "onek_uzantisi=seda/sedat" in _k("Seda Kaya", "Sedat Kaya")["nedenler"]


def test_turkce_katlama_yalniz_ascii_yazimi_tanir():
    """Katlama İ/I ve ASCII yazımını kapatır; iki yazım da Türkçe harfli ve
    harfleri farklıysa ("Gülşen"/"Gülsen") bunlar ayrı adlardır → SOR."""
    k = _k("Gülşen Kaya", "Gülsen Kaya")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "diakritik-farki"
    assert "diakritik=gülşen~gülsen" in k["nedenler"]
    assert _k("Gülşen Kaya", "GULSEN KAYA")["karar"] == "BAGLA"      # ASCII yazım
    assert _k("Mehmet Demir", "Mehmet Demır")["karar"] == "BAGLA"    # OCR ı/i, bir taraf ASCII


def test_birlesik_bicim_harfi_harfine_olmali():
    assert _k("Ayşegül Kaya", "Ayşe Gül Kaya")["kural"] == "birlesik-esit"
    k = _k("Mehmet Can Kaya", "Mehmet Çankaya")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "birlesik-katlama"
    assert _k("Mehmet Yıl-maz", "Mehmet Yılmaz")["karar"] == "BAGLA"   # OCR hecelemesi


def test_sira_farki_yalniz_soyad_tutarliysa_bagla():
    for a, b in (("Mehmet Yılmaz", "YILMAZ Mehmet"), ("YILDIZ Şahin", "Şahin Yıldız"),
                 ("Yıldız, Şahin", "Şahin Yıldız"), ("Mehmet Ali Yılmaz", "YILMAZ Mehmet Ali")):
        k = _k(a, b)
        assert k["karar"] == "BAGLA" and "sira=soyad-tutarli" in k["nedenler"], (a, b, k)
    for a, b in (("Şahin Yıldız", "Yıldız Şahin"), ("MEHMET YILMAZ", "YILMAZ MEHMET"),
                 ("Ali Mehmet Yılmaz", "Mehmet Ali Yılmaz")):
        k = _k(a, b)
        assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "sira-farki", (a, b, k)


def test_ayni_ilk_ad_farkli_soyad_gurultu_ve_birlesme_yok():
    """Eski tüm-dize skoru ortak ilk adı ödüllendiriyordu: "Mehmet Demir" ~
    "Mehmet Dere" 0,948 ile BAGLA'ydı. Parça bazında 0,707 → ayrı özne."""
    assert m._dize_skoru(["mehmet", "demir"], ["mehmet", "dere"]) >= 0.92
    assert _k("Mehmet Demir", "Mehmet Dere")["karar"] is None
    assert _k("Mehmet Kaya", "Mehmet Demir")["karar"] is None


def test_eski_sor_ornegi_artik_ayri_ozne():
    """DAVRANIŞ DEĞİŞİKLİĞİ (test_v0584 örneğinin neden değiştiği): aynı soyadlı
    farklı ön adlar ("Osman Balcı ~ Orhan Balcı") eskiden SOR idi; farklı ad
    parçası 0,76 → artık ayrı özne (sessiz) — yazım varyantı değildir."""
    k = _k("Osman Balcı", "Orhan Balcı")
    assert k["karar"] is None and round(k["skor"], 2) == 0.76
    assert round(m._dize_skoru(["osman", "balci"], ["orhan", "balci"]), 3) == 0.891
    yeni = _k("Osman Balcı", "Osman Balcıoğlu")
    assert yeni["karar"] == "AVUKATA-SOR" and 0.80 <= yeni["skor"] < 0.92


def test_bas_harf_cift_soyad_ve_ocr_karisikligi_sessiz_kalmaz():
    for a, b in (("M. Yılmaz", "Mehmet Yılmaz"), ("M.Yılmaz", "Mehmet Yılmaz"),
                 ("M.A. Yılmaz", "Mehmet Ali Yılmaz")):
        k = _k(a, b)
        assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "bas-harf", (a, b, k)
    assert _k("M. Kaya", "Mehmet Yılmaz")["karar"] is None
    k = _k("Ayşe Kaya-Demir", "Ayşe Demir")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "alt-kume"
    # Parça-min tek başına bu çiftleri SESSİZ bırakırdı (0,791 / 0,765 / 0,778)
    for a, b in (("Osman Balcı", "Osrnan Balcı"), ("Emine Arslan", "Ernine Arslan"), ("lsa Kaya", "İsa Kaya")):
        k = _k(a, b)
        assert k["skor"] < m.SOR_ESIK and k["karar"] == "AVUKATA-SOR" and k["kural"] == "ocr-karisikligi", (a, b)


def test_ocr_jokeri_her_zaman_soru():
    """Joker birden çok ada uyabilir ("Ha.an" → Hasan/Hakan; "Se.a" → Seda/Sema);
    listede tek aday olsa bile BAGLA verilmez."""
    for a, b in (("Se.a Kaya", "Seda Kaya"), ("Ha.an Kaya", "Hasan Kaya"), ("Y.LMAZ Mehmet", "Mehmet Yılmaz"),
                 ("A.i Kaya", "Ali Kaya")):
        k = _k(a, b)
        assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "ocr-joker", (a, b, k)
    sonuc = {(e["a"]["ad"], e["b"]["ad"]): (e["karar"], e["kural"])
             for e in m.eslestir(["Ahmet Tekçin", "AHMET TEKÇİN", "Ahmet Tek.in"])}
    assert sonuc[("Ahmet Tekçin", "AHMET TEKÇİN")] == ("BAGLA", "katlanmis-esit")
    assert sonuc[("Ahmet Tekçin", "Ahmet Tek.in")] == ("AVUKATA-SOR", "ocr-joker")


def test_kurum_eki_esdegerligi_ve_hukuki_bicim_farki():
    k = _k("Ahmet Yılmaz İnş. Ltd. Şti.", "Ahmet Yılmaz İnşaat Limited Şirketi")
    assert k["karar"] == "BAGLA" and k["kural"] == "katlanmis-esit"
    assert _k("Yılmaz İnşaat A.Ş.", "YILMAZ İNŞAAT ANONİM ŞİRKETİ")["karar"] == "BAGLA"
    k = _k("Yılmaz İnşaat A.Ş.", "Yılmaz İnşaat Ltd. Şti.")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "kurum-turu-farki"
    # şirket işareti yoksa "San" bir soyaddır — kurum eki açılımı yapılmaz
    assert _k("Ahmet San", "Ahmet Sanayi")["karar"] != "BAGLA"


def test_parca_sayisi_farkli_en_fazla_soru():
    k = _k("Ahmet", "Ahmet Kaya")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "alt-kume"
    assert _k("Tek.in", "Ahmet Tekçin")["karar"] == "AVUKATA-SOR"
    for a, b in (("Mehmet Ali Yılmaz", "Mehmet Yılmaz"),
                 ("Ahmet Yılmaz", "Ahmet Yılmaz İnşaat Ltd. Şti.")):
        assert _k(a, b)["karar"] == "AVUKATA-SOR"


def test_tur_farkli_bagla_asla_alan_yoksa_degisiklik_yok():
    k = _k("Ahmet Yılmaz", "AHMET YILMAZ", "gercek_kisi", "tuzel_kisi")
    assert k["karar"] == "AVUKATA-SOR" and k["kural"] == "katlanmis-esit+tur-farkli"
    assert "tur_farkli=gercek_kisi/tuzel_kisi" in k["nedenler"]
    assert "BAGLA YASAK" in k["gerekce"]
    # Tek tarafta alan → davranış değişmez (fail-open, yeni gürültü yok)
    assert _k("Ahmet Yılmaz", "AHMET YILMAZ", "gercek_kisi", None)["karar"] == "BAGLA"
    # Eş anlamlılar
    assert _k("Kaya", "KAYA", "Gerçek Kişi", "tüzel")["karar"] == "AVUKATA-SOR"
    assert _k("Kaya", "KAYA", "kamu kurumu", "Belediye")["karar"] == "BAGLA"
    assert [m.tur_normalize(x)[0] for x in ("şahıs", "anonim şirket", "davacı")] == \
        ["gercek_kisi", "tuzel_kisi", None]
    # Tanınmayan değer yok sayılır, görünür not düşer
    k = _k("Kaya", "KAYA", "garip", "tuzel_kisi")
    assert k["karar"] == "BAGLA" and "tur_taninmadi=garip" in k["nedenler"]
    # Kişi ~ şirket: parça sayısı farklı → en fazla SOR; tür farkı da yazılır
    k = _k("Ahmet Yılmaz", "Ahmet Yılmaz İnşaat Ltd. Şti.", "gercek_kisi", "tuzel_kisi")
    assert k["karar"] == "AVUKATA-SOR" and "tür de farklı" in k["gerekce"]


def test_tur_korumasi_gecisli_kopruyle_delinemez():
    """BAGLA geçişlidir: türsüz "YILMAZ Ahmet" hem kişiye hem aynı adlı
    şirkete BAGLA'nırsa model ikisini dolaylı birleştirir. Zincirde farklı tür
    varsa türsüz uçlu BAGLA'lar SOR'a iner; aynı türden iki kayıt BAGLA kalır."""
    sonuc = {(e["a"]["ad"], e["b"]["ad"]): (e["karar"], e["kural"]) for e in m.eslestir([
        {"ad": "Ahmet Yılmaz", "tur": "gercek_kisi"}, {"ad": "AHMET YILMAZ", "tur": "gercek_kisi"},
        "YILMAZ Ahmet", {"ad": "Ahmet YILMAZ", "tur": "tuzel_kisi"}])}
    assert sonuc[("Ahmet Yılmaz", "AHMET YILMAZ")] == ("BAGLA", "katlanmis-esit")
    assert sonuc[("Ahmet Yılmaz", "YILMAZ Ahmet")] == ("AVUKATA-SOR", "katlanmis-esit+tur-belirsiz")
    assert sonuc[("YILMAZ Ahmet", "Ahmet YILMAZ")] == ("AVUKATA-SOR", "katlanmis-esit+tur-belirsiz")
    assert sonuc[("Ahmet Yılmaz", "Ahmet YILMAZ")] == ("AVUKATA-SOR", "katlanmis-esit+tur-farkli")
    # Şirket yoksa türsüz yazım kişiye BAGLA'nır (alan yokmuş gibi — davranış değişmez)
    yalniz = m.eslestir([{"ad": "Ahmet Yılmaz", "tur": "gercek_kisi"}, "YILMAZ Ahmet"])
    assert [e["karar"] for e in yalniz] == ["BAGLA"]


def test_tur_korumasi_sor_komsulugu_uzerinden_de_isler():
    """Türsüz "AHMET YILMAZ" kişiye BAGLA, şirkete SOR ile bağlıysa kişi mi
    şirket mi olduğu belirsizdir → kişi BAGLA'sı da SOR (Fable karşı-tezi)."""
    sonuc = {(e["a"]["ad"], e["b"]["ad"]): (e["karar"], e["kural"]) for e in m.eslestir([
        {"ad": "Ahmet Yılmaz", "tur": "gercek_kisi"}, "AHMET YILMAZ",
        {"ad": "Ahmet Yılmaz İnşaat Ltd. Şti.", "tur": "tuzel_kisi"}])}
    assert sonuc[("Ahmet Yılmaz", "AHMET YILMAZ")] == ("AVUKATA-SOR", "katlanmis-esit+tur-belirsiz")
    assert {k for k, _ in sonuc.values()} == {"AVUKATA-SOR"}


def test_normalizasyon_nfc_sapka_yabanci_harf_ve_eski_sozlesme():
    assert m.tr_normalize("TEKÇİN") == "tekçin" and m.tr_normalize("Tek.in") == "tekin"
    assert m.tr_normalize("Kâmil NÂZIM") == "kamil nazım"
    assert m.tr_normalize("José Müller") == "jose müller"
    assert m.tr_normalize("Łukasz") == "lukasz"
    assert m.tr_katla("ışık çağlar ömür") == "isik caglar omur"
    assert _k("Kâmil Şahin", "Kamil Sahin")["karar"] == "BAGLA"
    assert _k("Gu\u0308nes\u0327 Kılıç", "Güneş Kılıç")["karar"] == "BAGLA"  # ayrışık (NFD) yazım


# ── 3) Arayüz, determinizm, sınırlar ─────────────────────────────────────────

def test_eslestir_arayuzu_geriye_uyumlu_ve_deterministik():
    girdi = ["Mehmet Yılmaz", {"id": "T2", "ad": "YILMAZ Mehmet", "tur": "gercek_kisi"},
             "Ahmet Kaya", "Ahmet Kara", "Zeynep Ak"]
    a, b = m.eslestir(girdi), m.eslestir(list(girdi))
    assert a == b
    assert [(e["a"]["id"], e["b"]["id"]) for e in a] == [("V1", "T2"), ("V3", "V4")]
    e = a[0]
    assert set(e) == {"a", "b", "skor", "karar", "kural", "nedenler", "gerekce"}
    assert "tur" not in e["a"] and e["b"]["tur"] == "gercek_kisi"
    assert m.ozne_skoru("Mehmet Yılmaz", "YILMAZ Mehmet")[0] == 1.0  # v0.5.8 arayüzü
    assert m.eslestir([]) == [] and m.eslestir(None) == []


def test_bicimsiz_girdi_uydurma_eslesme_uretmez():
    with pytest.raises(ValueError):
        m.eslestir([None, "None"])          # str(None) "None"~"None" BAGLA'sı olmasın
    with pytest.raises(ValueError):
        m.eslestir([{"ad": 5}, "5"])


def test_sinirlar_kilitlenme_yok(monkeypatch, tmp_path):
    with pytest.raises(ValueError):
        m.eslestir(["Ad %d" % i for i in range(m.AZAMI_OZNE + 1)])
    uzun1, uzun2 = "Ahmet " * 40, "Ahmet " * 39 + "Mehmet"
    assert m.eslestir([uzun1, uzun2]) == []          # yalnız yazım eşdeğerliği
    assert m.eslestir([uzun1, uzun1.upper()])[0]["karar"] == "BAGLA"
    assert len(m.asiri_uzun_adlar([uzun1, "Ali Kaya"])) == 1
    assert m._dize_skoru(["a" * (m.AZAMI_DIZE + 6)], ["b" * (m.AZAMI_DIZE + 6)]) is None  # karesel tam-dize sınırı
    assert m._dize_skoru(["a" * 40], ["b" * 40]) == 0.0                              # sınır altı hesaplanır
    monkeypatch.setattr(m, "AZAMI_BAYT", 10)
    p = tmp_path / "buyuk.json"
    p.write_text(json.dumps(["Ali Kaya", "Ali Kara"]), encoding="utf-8")
    with pytest.raises(ValueError):
        m._girdi_oku(str(p))


def test_is_butcesi_asilinca_gorunur_uyari_ve_yazim_esdegerligi_surer(monkeypatch):
    monkeypatch.setattr(m, "IS_BUTCESI", 100)
    uyarilar = []
    sonuc = m.eslestir(["Ahmet Kaya", "Ahmet Kara", "Mehmet Yılmaz", "YILMAZ Mehmet"], uyarilar)
    kararlar = {(e["a"]["ad"], e["b"]["ad"]): e["karar"] for e in sonuc}
    assert kararlar[("Mehmet Yılmaz", "YILMAZ Mehmet")] == "BAGLA"
    assert uyarilar and "iş bütçesi aşıldı" in uyarilar[0]


def _cli(*args, cwd=None):
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def test_cli_json_ve_girdi_hatalari(tmp_path):
    kod, out, _ = _cli("Mehmet Yılmaz", "YILMAZ Mehmet", "Ahmet Kaya", "Ahmet Kara", "--json")
    assert kod == 0
    r = json.loads(out)
    assert r["esik_bagla"] == 0.92 and r["esik_sor"] == 0.80 and r["kural_seti"] == "v0.5.18"
    assert [e["karar"] for e in r["eslesmeler"]] == ["BAGLA", "AVUKATA-SOR"] and r["uyarilar"] == []
    g = tmp_path / "ozneler.json"
    g.write_text(json.dumps([{"ad": "Ali Kaya", "tur": "gercek_kisi"},
                             {"ad": "ALİ KAYA", "tur": "tuzel_kisi"}], ensure_ascii=False),
                 encoding="utf-8")
    kod, out, _ = _cli("--girdi", str(g))
    assert kod == 0 and "AVUKATA-SOR" in out and "BAGLA YASAK" in out
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text("{bozuk", encoding="utf-8")
    kod, _, err = _cli("--girdi", str(bozuk))
    assert kod == 2 and "GİRDİ HATASI" in err
    kod, _, err = _cli("--girdi", str(tmp_path / "yok.json"))
    assert kod == 2
    tipsiz = tmp_path / "tipsiz.json"
    tipsiz.write_text("[null, 3]", encoding="utf-8")
    kod, _, err = _cli("--girdi", str(tipsiz))
    assert kod == 2 and "GİRDİ HATASI" in err


def _vakia_dogrula(tmp_path, veri):
    yol = tmp_path / "vakia.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    hedef = tmp_path / "sonuc.json"
    p = subprocess.run([sys.executable, str(VAKIA), "--dogrula", str(yol), "--json", str(hedef)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout, json.loads(hedef.read_text(encoding="utf-8"))


def _vakia_veri(taraflar, ozne=None):
    olay = {"tarih": "2025-01-10", "olgu": "Sozlesme imzalandi", "belge": "yazili sozlesme",
            "destekler": ["I1"], "ispat_durumu": "belgeli"}
    if ozne:
        olay["ozne"] = ozne
    return {"taraflar": taraflar, "iddialar": [{"id": "I1", "metin": "Sozlesme kuruldu"}],
            "olaylar": [olay]}


def test_vakia_matris_tur_alani_eslestiriciye_tasinir(tmp_path):
    cikti, sonuc = _vakia_dogrula(tmp_path, _vakia_veri(
        [{"ad": "Ahmet Yılmaz", "tur": "gercek_kisi"}, {"ad": "AHMET YILMAZ", "tur": "tuzel_kisi"}],
        ozne="YILMAZ Ahmet"))
    bul = {tuple(b["varyantlar"]): b for b in sonuc["ozne_eslestirme"]}
    tur_cifti = bul[("Ahmet Yılmaz", "AHMET YILMAZ")]
    assert tur_cifti["karar"] == "AVUKATA-SOR" and tur_cifti["kural"].endswith("+tur-farkli")
    # Türsüz olay öznesi hem kişiye hem şirkete eşit → hangisi olduğu SORULUR
    assert bul[("Ahmet Yılmaz", "YILMAZ Ahmet")]["kural"].endswith("+tur-belirsiz")
    assert {b["karar"] for b in sonuc["ozne_eslestirme"]} == {"AVUKATA-SOR"}
    assert all(set(b) == {"varyantlar", "skor", "karar", "kural", "gerekce"}
               for b in sonuc["ozne_eslestirme"])
    assert "BAGLA YASAK" in cikti and "ÖZNE EŞLEŞTİRME" in cikti


def test_vakia_matris_taninmayan_tur_ve_tur_celiskisi_gorunur(tmp_path):
    cikti, _ = _vakia_dogrula(tmp_path, _vakia_veri(
        [{"ad": "Ali Kaya", "tur": "davacı"}, {"ad": "Veli Kaya", "tur": "gercek_kisi"},
         {"ad": "Veli Kaya", "tur": "tuzel_kisi"}]))
    assert "tur «davacı» tanınmadı ve YOK SAYILDI" in cikti
    assert "«Veli Kaya» iki ayrı türle yazılmış" in cikti


def test_vakia_matris_eski_girdi_ve_dize_taraflar_degismez(tmp_path):
    _, sonuc = _vakia_dogrula(tmp_path, _vakia_veri(["Mehmet Yılmaz", "Zeynep Kaya"]))
    assert sonuc["ozne_eslestirme"] == []
    _, sonuc = _vakia_dogrula(tmp_path, _vakia_veri(["Mehmet Demir"], ozne="Mehmet Demır"))
    assert [b["karar"] for b in sonuc["ozne_eslestirme"]] == ["BAGLA"]


def test_vakia_matris_eslestirici_cokerse_gorunur_uyari(monkeypatch):
    vm = _yukle("vakia_matris_v0518_ozne", VAKIA)

    class _Bozuk:
        @staticmethod
        def eslestir(*_a, **_k):
            raise RuntimeError("deneme")

    monkeypatch.setattr(vm, "_ozne_eslestirici_modulu", lambda: _Bozuk)
    bulgular, uyari = vm.ozne_eslestirme_kur(_vakia_veri(["Ali Kaya", "Ali Kara"]))
    assert bulgular == [] and "YAPILAMADI" in uyari and "RuntimeError" in uyari
    adlar = vm._ozne_adlarini_topla(_vakia_veri([{"ad": "Ali Kaya", "tur": "kamu"}, "Ali Kaya"],
                                                ozne="Veli Ak"))
    assert adlar == [{"ad": "Ali Kaya", "tur": "kamu"}, {"ad": "Veli Ak"}]


# ── 4) Başlık etiketi ve belge ──────────────────────────────────────────────

def test_baslik_vendor_etiketi_duzeltildi_kaynak_atfi_korundu():
    bas = "\n".join(SCRIPT.read_text(encoding="utf-8").splitlines()[:14])
    assert "# VENDOR:" not in bas            # aile_dogrula'nın vendor dondurma denetimi tetiklenmez
    for k in ("kavramsal devşirme", "github.com/semantica-agi/semantica@v0.6.5",
              "similarity_calculator.py:529-615", "MIT", "Copyright (c) 2026 Hawksight AI",
              "#1149", "5846 sayılı FSEK"):
        assert k in bas, k


def test_skill_md_yeni_kural_seti_anlatiliyor():
    txt = SKILL_MD.read_text(encoding="utf-8")
    bolum = txt[txt.index("## ÖZNE EŞLEŞTİRME"):txt.index("## DELİL TEDARİK PLANI")]
    duz = " ".join(bolum.split())
    for k in ("v0.5.18", "YAZIM eşdeğerliğinde", "BAGLA asla", "`tur`", "scripts/ozne_eslestirici.py",
              "tek başına BAGLA ettirmez", "Gülşen/Gülsen", "Bilinen bedel", "Davranış değişikliği",
              "Osman Balcı / Orhan Balcı", "model KENDİ KARAR VERMEZ"):
        assert k in duz, k
    assert "skor ≥0.92 → BAGLA" not in duz   # eski eşik anlatımı kalmadı
