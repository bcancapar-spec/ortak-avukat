# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP I4: oa-usul (Hamle 12 + P2-3/A-8) · oa-alan (P2-2/A-7) ·
oa-kiyas (P1-4/A-15 yarışan norm).

Bulgu → kalem eşlemesi:
  Hamle 12   oa-usul SKILL.md «GÖREV DÖNGÜSÜ — MERCİ TAYİNİ» notu (HMK m.21-23;
             HSK 07/07/2021-608; BAM tutumu "gönderme kararı istinaf edilemez").
  P2-3/A-8   oa-usul A-cephesi: tamamlanabilir vs tamamlanamaz kusur; zamanlama
             AVUKAT KARARI. usul_matris.py'ye opsiyonel `tamamlanabilir` +
             `zamanlama` alanları (advisory — exit sözleşmesi KORUNUR).
  P2-2/A-7   oa-alan SKILL.md «FORUM SEÇİMİ» adımı (HMK m.6 genel yetki, m.7,
             m.9-16 özel/seçimlik yetki) — nitel ölçütler, soru listesi, «forum»
             satırı.
  P1-4/A-15  kiyas_denetim.py: `buyuk_onermeler` listesi (yarışan normlar);
             birden çok varsa `secim_gerekcesi` zorunlu; raporda «YARIŞAN
             NORMLAR» tablosu; exit 0 sözleşmesi KORUNUR (2026-08-12 Can kararı).

Normlar Mevzuat MCP'den teyitli (2026-09-06): HMK m.6, m.7, m.9-16, m.21-23,
m.77, m.115, m.119; TBK m.60. İçtihat: Antalya BAM 4. HD E.2023/126 K.2023/67
(24.01.2023) tam metin Yargı Pro'dan okundu.

Fikstürler SENTETİKTİR (anayasa m.7); tempfile ile izole dizinde koşar, depo
dosyalarına yazmaz.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
USUL = SKILLS / "oa-usul" / "scripts" / "usul_matris.py"
KIYAS = SKILLS / "oa-kiyas" / "scripts" / "kiyas_denetim.py"
USUL_SKILL = SKILLS / "oa-usul" / "SKILL.md"
USUL_CETVEL = SKILLS / "oa-usul" / "references" / "usul-cetveli.md"
ALAN_SKILL = SKILLS / "oa-alan" / "SKILL.md"
KIYAS_SKILL = SKILLS / "oa-kiyas" / "SKILL.md"
KIYAS_REHBER = SKILLS / "oa-kiyas" / "references" / "kiyas-rehberi.md"


def _oku(p):
    return p.read_text(encoding="utf-8")


def _cli(script, *args):
    cp = subprocess.run(
        [sys.executable, str(script), *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole():
    return pathlib.Path(tempfile.mkdtemp())


# ════════════════════════════════════════════════════════════════════════════
#  Hamle 12 — oa-usul SKILL.md: GÖREV DÖNGÜSÜ — MERCİ TAYİNİ
# ════════════════════════════════════════════════════════════════════════════

def test_hamle12_usul_skill_merci_tayini_notu_var():
    m = _oku(USUL_SKILL)
    assert "MERCİ TAYİNİ" in m
    assert "GÖREV DÖNGÜSÜ" in m
    # norm çıpası (Mevzuat MCP teyitli)
    assert "HMK m.21" in m and "m.22" in m and "m.23" in m
    # HSK kararı — kamu bilgisi
    assert "608" in m and "07/07/2021" in m and "01/09/2021" in m
    # BAM tutumu
    assert "gönderme kararı" in m and "istinaf" in m
    assert "Mevzuat MCP teyit 2026-09-06" in m


def test_hamle12_bam_kunyesi_kamu_bilgisi_ve_orneklem_ilkesi():
    m = _oku(USUL_SKILL)
    # Yargı Pro'dan tam metin teyitli künye (kamu bilgisi — kişi/dosya değil)
    assert "Antalya BAM 4. HD" in m
    assert "E. 2023/126" in m and "K. 2023/67" in m and "24.01.2023" in m
    # örneklem ilkesi: tüm görev/yetki döngülerine kıyasen, dış hakem = döngü kırıcı
    assert "döngü kırıcı" in m
    assert "kıyasen" in m


# ════════════════════════════════════════════════════════════════════════════
#  P2-3 / A-8 — oa-usul: tamamlanabilir kusur × zamanlama (metin + motor)
# ════════════════════════════════════════════════════════════════════════════

def test_p23_usul_skill_tamamlanabilir_ayrimi_ve_avukat_karari():
    m = _oku(USUL_SKILL)
    assert "TAMAMLANABİLİR" in m and "TAMAMLANAMAZ" in m
    assert "HMK m.119/2" in m and "m.115/2" in m
    assert "AVUKAT KARARI" in m
    # "derhâl" kuralının tamamlanamaz kusura özgü olduğu ve m.2 ile çelişmediği
    assert "derhâl" in m and "m.2" in m
    assert "tamamlanabilir" in m and "zamanlama" in m


def test_p23_cetvel_sema_belgesi_alanlari_tanimlar():
    m = _oku(USUL_CETVEL)
    assert "tamamlanabilir" in m and "zamanlama" in m
    for deger in ("simdi", "sonra", "avukat_karari"):
        assert deger in m
    assert "tamamlanabilir kusurda zamanlama kararı yok" in m


def _karsi_kacirma(**ek):
    """Karşı taraf +5 gün kaçırmış; G2/G4/G9 boşlukları doğmasın diye tam
    kayıt. Testte YALNIZ zamanlama denetimi izole edilir."""
    i = {"id": "I1", "taraf": "karsi", "islem": "cevap",
         "sure_kurali": "hmk_cevap", "yargi_kolu": "hukuk",
         "teblig": "2026-04-01", "teblig_belgeli": True,
         "son_gun": "2026-04-15", "fiili_tarih": "2026-04-20",
         "sonuc_norm": "HMK m.128 — inkâr sayılma", "sonuc_ictihat_teyit": True,
         "kapi_kapatma": [{"kapi": "K-1", "kapatma": "mazeret yok"}],
         "kesin_dil": True}
    i.update(ek)
    return i


def _usul(izole, islemler, **ust):
    yol = izole / "usul.json"
    veri = {"dosya": "Örnek 2099/1", "yargi_kolu": "hukuk", "islemler": islemler}
    veri.update(ust)
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return _cli(USUL, "--girdi", yol)


def test_usul_tamamlanabilir_true_zamanlama_yok_advisory_satir_exit0(izole):
    """Tamamlanabilir kusurda zamanlama kararı verilmemişse GÖRÜNÜR advisory
    satır basılır; boşluk DEĞİLDİR (exit sözleşmesi korunur: exit 0)."""
    kod, out = _usul(izole, [_karsi_kacirma(tamamlanabilir=True)])
    assert kod == 0, out
    assert "tamamlanabilir kusurda zamanlama kararı yok" in out
    assert "BOŞLUKLAR" not in out


@pytest.mark.parametrize("z", ["simdi", "sonra", "avukat_karari"])
def test_usul_tamamlanabilir_true_zamanlama_enum_kayitli_exit0(izole, z):
    kod, out = _usul(izole, [_karsi_kacirma(tamamlanabilir=True, zamanlama=z)])
    assert kod == 0, out
    assert "tamamlanabilir kusurda zamanlama kararı yok" not in out
    assert f"zamanlama={z}" in out


def test_usul_zamanlama_enum_disi_deger_nitelendirilmez_bilinmiyor(izole):
    """Kapalı enum dışı değer YORUMLANMAZ: görünür uyarı + 'bilinmiyor' + advisory
    satır; boşluk üretmez (model kurar, script denetler)."""
    kod, out = _usul(izole, [_karsi_kacirma(tamamlanabilir=True, zamanlama="hemen")])
    assert kod == 0, out
    assert "kapalı enum dışı" in out and "bilinmiyor" in out
    assert "tamamlanabilir kusurda zamanlama kararı yok" in out


def test_usul_tamamlanamaz_kusurda_derhal_notu_zamanlama_sorulmaz(izole):
    """Tamamlanamaz kusurda (süre) 'derhâl' kuralı işler; zamanlama satırı
    basılmaz (o soru yalnız tamamlanabilir kusur içindir)."""
    kod, out = _usul(izole, [_karsi_kacirma(tamamlanabilir=False)])
    assert kod == 0, out
    assert "derhâl" in out
    assert "tamamlanabilir kusurda zamanlama kararı yok" not in out


def test_usul_eski_dosya_alansiz_hic_satir_basmaz(izole):
    """Geriye uyum: alan hiç yoksa hiçbir tamamlanabilir/zamanlama satırı yok."""
    kod, out = _usul(izole, [_karsi_kacirma()])
    assert kod == 0, out
    assert "tamamlanabilir" not in out.lower()
    assert "zamanlama" not in out.lower()


def test_usul_tamamlanabilir_alani_biz_tarafinda_yok_sayilir_gorunur(izole):
    """Alan yalnız KARŞI taraf kusurunda anlamlıdır (A-cephesi); 'biz' kaydında
    verilirse sessizce yutulmaz — görünür bilgi satırı basılır, boşluk yok."""
    i = {"id": "I2", "taraf": "biz", "islem": "cevap", "sure_kurali": "hmk_cevap",
         "teblig": "2026-03-02", "teblig_belgeli": True,
         "son_gun": "2026-03-16", "fiili_tarih": "2026-03-10",
         "kesin_dil": False, "tamamlanabilir": True, "zamanlama": "simdi"}
    kod, out = _usul(izole, [i])
    assert kod == 0, out
    assert "yalnız karşı taraf" in out


def test_usul_tamamlanabilir_string_true_kabul_bool_disi_uyari(izole):
    """`tamamlanabilir` bool dışı bir tipte gelirse (eski/elle yazılmış JSON)
    çökmez: görünür uyarı + yok sayılır."""
    kod, out = _usul(izole, [_karsi_kacirma(tamamlanabilir="evet")])
    assert kod == 0, out
    assert "bool değil" in out


def test_usul_ornek_sablon_zamanlama_alanlarini_tasir_ve_temiz_gecer(izole):
    kod, out = _cli(USUL, "--ornek")
    assert kod == 0
    v = json.loads(out)
    karsi = [i for i in v["islemler"] if i.get("taraf") == "karsi"]
    assert any("tamamlanabilir" in i and "zamanlama" in i for i in karsi)
    yol = izole / "ornek.json"
    yol.write_text(out, encoding="utf-8")
    kod2, out2 = _cli(USUL, "--girdi", yol)
    assert kod2 == 0, out2


def test_usul_json_ciktisi_zamanlama_satirini_bulgulara_tasir(izole):
    yol = izole / "usul.json"
    yol.write_text(json.dumps({"dosya": "Örnek 2099/1", "yargi_kolu": "hukuk",
                               "islemler": [_karsi_kacirma(tamamlanabilir=True)]},
                              ensure_ascii=False), encoding="utf-8")
    jyol = izole / "sonuc.json"
    kod, out = _cli(USUL, "--girdi", yol, "--json", jyol)
    assert kod == 0, out
    veri = json.loads(jyol.read_text(encoding="utf-8"))
    assert veri["saglikli"] is True
    assert any("zamanlama kararı yok" in b for b in veri["bulgular"])


# ════════════════════════════════════════════════════════════════════════════
#  P2-2 / A-7 — oa-alan SKILL.md: FORUM SEÇİMİ
# ════════════════════════════════════════════════════════════════════════════

def test_p22_alan_skill_forum_secimi_adimi():
    m = _oku(ALAN_SKILL)
    assert "FORUM SEÇİMİ" in m
    # norm çıpaları — Mevzuat MCP teyitli
    assert "HMK m.6" in m and "m.7" in m and "m.9-16" in m
    assert "Mevzuat MCP teyit 2026-09-06" in m
    # nitel ölçütler
    for olcut in ("mesafe", "iş yükü", "bilirkişi havuzu", "BAM/daire eğilimi"):
        assert olcut in m, olcut
    # soru listesi + konumlama çıktısına «forum» satırı
    assert "Soru listesi" in m or "SORU LİSTESİ" in m
    assert "«forum»" in m or "`forum`" in m


def test_p22_alan_forum_bolumu_sayi_uydurmaz_ve_kesin_yetkiyi_ayirir():
    m = _oku(ALAN_SKILL)
    b = m.split("FORUM SEÇİMİ", 1)[1].split("\n## ", 1)[0]
    # nitel: yüzde/olasılık sayısı yok
    assert "%" not in b
    # kesin yetki hâlinde seçim yoktur (m.11/12/14-2/15-2 örneklem)
    assert "kesin yetki" in b
    assert "seçim yoktur" in b or "seçim YOKTUR" in b


# ════════════════════════════════════════════════════════════════════════════
#  P1-4 / A-15 — oa-kiyas: YARIŞAN NORMLAR (buyuk_onermeler listesi)
# ════════════════════════════════════════════════════════════════════════════

def _onerme(norm, **ek):
    d = {"norm": norm,
         "unsurlar": [{"id": "fiil", "ad": "Fiil"}, {"id": "zarar", "ad": "Zarar"}],
         "ictihat": [{"kunye": "Y. .. HD E. 2099/1 K. 2099/1 (sentetik)",
                      "dogrulama": "teyitli"}],
         "zamanasimi": "—", "kusur_sarti": "—", "ispat_kolayligi": "—", "faiz": "—"}
    d.update(ek)
    return d


def _kucuk():
    return {"vakialar": [
        {"metin": "Sentetik olay A", "karsilar": ["fiil"], "dayanak_delil": ["d1"]},
        {"metin": "Sentetik olay B", "karsilar": ["zarar"], "dayanak_delil": ["d2"]},
    ]}


def _kiyas(izole, veri, *args):
    yol = izole / "kiyas.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return (yol,) + _cli(KIYAS, yol, *args)


def test_kiyas_yarisan_normlar_gerekceli_tablo_ve_exit0(izole):
    veri = {"buyuk_onermeler": [
        _onerme("TBK m.112 (sözleşmeye aykırılık) — MCP teyit", secili=True,
                zamanasimi="TBK m.146 — 10 yıl (çıpa)", kusur_sarti="karine (m.112)",
                ispat_kolayligi="borç ilişkisi belgeli", faiz="temerrütten",
                secim_gerekcesi="daha uzun zamanaşımı + kusur karinesi; TBK m.60 en iyi giderim"),
        _onerme("TBK m.49 (haksız fiil) — MCP teyit",
                zamanasimi="TBK m.72 — 2/10 yıl (çıpa)", kusur_sarti="davacı ispatlar",
                ispat_kolayligi="kusur ispatı bizde", faiz="olay tarihinden"),
    ], "kucuk_onerme": _kucuk(), "sonuc": "Sözleşme sorumluluğu esas alındı."}
    yol, kod, out = _kiyas(izole, veri)
    assert kod == 0, out
    assert "YARIŞAN NORMLAR" in out
    assert "TBK m.112" in out and "TBK m.49" in out
    assert "zamanaşımı" in out and "kusur" in out and "ispat" in out and "faiz" in out
    assert "yarışan norm seçimi gerekçesiz" not in out
    assert "SONUÇ: Yapı bütün." in out


def test_kiyas_yarisan_normlar_gerekcesiz_bosluk_satiri_exit0_korunur(izole):
    """Birden çok büyük önerme var ama `secim_gerekcesi` boş → «yarışan norm
    seçimi gerekçesiz» boşluk satırı + kritik boşluk; exit 0 sözleşmesi
    KORUNUR (2026-08-12 Can kararı — kapı değil karar-malzemesi)."""
    veri = {"buyuk_onermeler": [_onerme("TBK m.112"), _onerme("TBK m.49")],
            "kucuk_onerme": _kucuk(), "sonuc": "x"}
    yol, kod, out = _kiyas(izole, veri, "--json", izole / "s.json")
    assert kod == 0, out
    assert "yarışan norm seçimi gerekçesiz" in out
    assert "KRİTİK BOŞLUK var" in out
    v = json.loads((izole / "s.json").read_text(encoding="utf-8"))
    assert v["kritik_bosluk"] is True
    assert len(v["buyuk_onerme"]["yarisan_normlar"]) == 2


def test_kiyas_gerekce_yalniz_bosluk_karakteri_ise_gerekcesiz_sayilir(izole):
    veri = {"buyuk_onermeler": [_onerme("TBK m.112", secim_gerekcesi="   "),
                                _onerme("TBK m.49")],
            "kucuk_onerme": _kucuk(), "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri)
    assert kod == 0
    assert "yarışan norm seçimi gerekçesiz" in out


def test_kiyas_secili_onerme_unsur_denetimine_esas_alinir(izole):
    """`secili: true` işaretli önerme subsumtion denetimine esas alınır; işaret
    yoksa listenin ilki. Seçilen normun adı §3 başlığında görünür."""
    a = _onerme("NORM-A", unsurlar=[{"id": "fiil", "ad": "Fiil"}])
    b = _onerme("NORM-B", secili=True, secim_gerekcesi="B daha elverişli",
                unsurlar=[{"id": "ozel_unsur", "ad": "Özel unsur"}])
    veri = {"buyuk_onermeler": [a, b], "kucuk_onerme": _kucuk(), "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri, "--json", izole / "s.json")
    assert kod == 0
    v = json.loads((izole / "s.json").read_text(encoding="utf-8"))
    assert v["buyuk_onerme"]["norm"] == "NORM-B"
    assert [u["unsur_id"] for u in v["unsur_vakia_eslesme"]] == ["ozel_unsur"]
    assert any(y["secili"] for y in v["buyuk_onerme"]["yarisan_normlar"] if y["norm"] == "NORM-B")


def test_kiyas_tek_ogeli_liste_yarisma_yok_gerekce_aranmaz(izole):
    veri = {"buyuk_onermeler": [_onerme("TBK m.49")], "kucuk_onerme": _kucuk(),
            "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri, "--json", izole / "s.json")
    assert kod == 0
    assert "YARIŞAN NORMLAR" not in out
    assert "yarışan norm seçimi gerekçesiz" not in out
    assert "SONUÇ: Yapı bütün." in out
    v = json.loads((izole / "s.json").read_text(encoding="utf-8"))
    assert v["buyuk_onerme"]["yarisan_normlar"] == []


def test_kiyas_eski_tekil_buyuk_onerme_aynen_calisir_yarisan_bos(izole):
    """Geriye uyum: mevcut tekil `buyuk_onerme` şeması değişmeden çalışır;
    JSON'da `buyuk_onerme.yarisan_normlar` boş liste. Üst-düzey anahtar
    kümesi DEĞİŞMEZ (K1 ileri koruması — test_v0514_muhakeme)."""
    veri = {"buyuk_onerme": _onerme("TBK m.49"), "kucuk_onerme": _kucuk(),
            "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri, "--json", izole / "s.json")
    assert kod == 0
    assert "SONUÇ: Yapı bütün." in out
    v = json.loads((izole / "s.json").read_text(encoding="utf-8"))
    assert v["buyuk_onerme"]["yarisan_normlar"] == []
    assert "YARIŞAN NORMLAR" not in out


def test_kiyas_her_iki_alan_varsa_liste_esas_gorunur_uyari(izole):
    veri = {"buyuk_onerme": _onerme("ESKİ"),
            "buyuk_onermeler": [_onerme("YENİ-1", secili=True, secim_gerekcesi="g"),
                                _onerme("YENİ-2")],
            "kucuk_onerme": _kucuk(), "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri, "--json", izole / "s.json")
    assert kod == 0
    assert "buyuk_onermeler esas alındı" in out
    v = json.loads((izole / "s.json").read_text(encoding="utf-8"))
    assert v["buyuk_onerme"]["norm"] == "YENİ-1"


def test_kiyas_bozuk_liste_ogesi_cokmez_gorunur_uyari(izole):
    veri = {"buyuk_onermeler": ["düz string", _onerme("TBK m.49", secim_gerekcesi="g")],
            "kucuk_onerme": _kucuk(), "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri)
    assert kod == 0, out
    assert "sözlük değil" in out


def test_kiyas_karsilastirma_alani_eksik_gorunur_uyari_kritik_degil(izole):
    """Karşılaştırma alanı (zamanasimi/kusur_sarti/ispat_kolayligi/faiz) boşsa
    tabloda '—' + görünür uyarı; kritik DEĞİL (yorum avukatındır)."""
    a = _onerme("TBK m.112", secili=True, secim_gerekcesi="g")
    b = _onerme("TBK m.49")
    for alan in ("zamanasimi", "kusur_sarti", "ispat_kolayligi", "faiz"):
        b.pop(alan)
    veri = {"buyuk_onermeler": [a, b], "kucuk_onerme": _kucuk(), "sonuc": "x"}
    _, kod, out = _kiyas(izole, veri)
    assert kod == 0
    assert "karşılaştırma alanı boş" in out
    assert "SONUÇ: Yapı bütün." in out


def test_kiyas_yarisan_json_kaydi_alanlari():
    veri = {"buyuk_onermeler": [
        _onerme("N1", secili=True, secim_gerekcesi="g", zamanasimi="z1",
                kusur_sarti="k1", ispat_kolayligi="i1", faiz="f1"),
        _onerme("N2")], "kucuk_onerme": _kucuk(), "sonuc": "x"}
    izole = pathlib.Path(tempfile.mkdtemp())
    _, kod, out = _kiyas(izole, veri, "--json", izole / "s.json")
    v = json.loads((izole / "s.json").read_text(encoding="utf-8"))
    n1 = [y for y in v["buyuk_onerme"]["yarisan_normlar"] if y["norm"] == "N1"][0]
    assert set(n1.keys()) == {"norm", "zamanasimi", "kusur_sarti",
                              "ispat_kolayligi", "faiz", "secim_gerekcesi", "secili"}
    assert n1["zamanasimi"] == "z1" and n1["secili"] is True


def test_p14_kiyas_skill_ve_rehber_yarisan_normlar_belgesi():
    s = _oku(KIYAS_SKILL)
    assert "YARIŞAN NORMLAR" in s
    assert "TBK m.60" in s and "Mevzuat MCP teyit 2026-09-06" in s
    for k in ("sözleşme", "haksız fiil", "özel", "genel", "zamanaşımı", "kusur",
              "ispat", "faiz", "secim_gerekcesi"):
        assert k in s, k
    r = _oku(KIYAS_REHBER)
    assert "buyuk_onermeler" in r and "secim_gerekcesi" in r
    for alan in ("zamanasimi", "kusur_sarti", "ispat_kolayligi", "faiz", "secili"):
        assert alan in r, alan
    assert "yarisan_normlar" in r
