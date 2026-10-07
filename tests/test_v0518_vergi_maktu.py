# -*- coding: utf-8 -*-
"""v0.5.18 — K2 (GİZLİ KUSUR): vergi/harç/6183 davasında karşı vekâlet NİSPİ dilimle
hesaplanıyordu; Av.K. m.168/2 MAKTU şart koşar (oa-strateji/maliyet_cetveli.py).

Kusur (Aşama 4 / T5-4, ana oturum teyidi 2026-10-07): `hesapla()` karşı vekâlet
kolunda `merci=vergi` için ayrı dal yoktu; `aaut.maktu_vergi` + `aaut.nispi_dilimler`
dolduğu anda üçüncü kısım nispi dilimi uygulanırdı. Bugün tarife.json'da aaut
tabloları null olduğundan rakam ÜRETMİYORDU — avukat tabloyu elle doldurduğu anda
yanlış karşı vekâlet üretirdi (gizli kusur).

Resmî metin teyidi (Yargı PRO MCP `mevzuat_getir`, 2026-10-07):
  * Av.K. (1136) m.168/2 (Ek cümle: 16/6/2009-5904/35): "hazırlanan tarifede; genel
    bütçeye, il özel idareleri, belediye ve köylere ait vergi, resim, harç ve benzeri
    mali yükümlülükler ve bunların zam ve cezaları ile tarifelere ilişkin davalar ve
    6183 sayılı Amme Alacaklarının Tahsil Usulü Hakkında Kanunun uygulanmasından
    doğan her türlü davalar için avukatlık ücreti tutarı maktu olarak belirlenir."
  * AAÜT (RG 04.11.2025/33067; mevzuat.gov.tr 42687) genel hükümler: m.3/1 (tarifede
    yazılı miktardan az ve üç katından çok olamaz), m.13/1-4 (konusu para olan işte
    ÜÇÜNCÜ KISIM — nispi; m.13/2 kabul/ret tavanı; m.13/4 tam rette maktu), m.15/1
    (Danıştay/BİM/idare/VERGİ mahkemelerinde birinci savunma dilekçesi süresinin
    bitimine kadar feragat/kabul/konusuz kalma/bu nedenlerle ret → ücretin YARISI,
    diğer durumlarda TAMAMI), m.21 (hüküm tarihindeki tarife esas).
  Kısmi kabul/ret hâlinde MAKTU ücretin taraflar arasında nasıl dağıtılacağı genel
  hükümlerde YOKTUR (m.13 nispi rejime aittir); m.13/2 tavanının maktu vergi ücretine
  uygulanıp uygulanmayacağı da okunamadı → script bu hâllerde RAKAM ÜRETMEZ, görünür
  not basar (brief: "okunamayan dağılımda rakam üretilmez").

Fikstürler sentetiktir (gerçek tutar değil); testler ağsız, tmp_path'te koşar.
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
STRATEJI = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-strateji"
SCRIPT = STRATEJI / "scripts" / "maliyet_cetveli.py"
TARIFE = STRATEJI / "scripts" / "tarife.json"
STRATEJI_MD = STRATEJI / "SKILL.md"
STRATEJI_GUNLUK = STRATEJI / "references" / "degisiklik-gunlugu.md"


def _load():
    spec = importlib.util.spec_from_file_location("v0518_vergi_maktu_cetvel", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()
GERCEK = json.loads(TARIFE.read_text(encoding="utf-8"))


def _cli(*args):
    cp = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(REPO))
    return cp.returncode, cp.stdout, cp.stderr


def _sentetik(maktu_vergi=700.0, dilimler=None):
    """Tam dolu SENTETİK tarife — yuvarlak sayılar, gerçek değer DEĞİL. Nispi dilim
    BİLEREK doludur: vergi davasında UYGULANMAMASI gerektiği sınanır."""
    aaut = {"maktu_asliye": 1000.0, "maktu_sulh": 600.0,
            "nispi_dilimler": [{"ust": 50000, "yuzde": 10}, {"ust": None, "yuzde": 5}]
            if dilimler is None else dilimler}
    if maktu_vergi is not None:
        aaut["maktu_vergi"] = maktu_vergi
    return {
        "yil": 2026, "mcp_teyit_tarihi": "2026-10-05",
        "kaynak": "SENTETİK TEST TARİFESİ — gerçek değer değildir",
        "harc": {"basvuru_maktu": 100.0, "karar_ilam_nispi_binde": 50.0, "pesin_oran": 0.25,
                 "pesin_oran_olum_cismani": 0.05, "nispi_asgari": 200.0,
                 "istinaf_basvuru_maktu": 300.0, "temyiz_basvuru_maktu": 400.0, "kesif": 500.0},
        "harc_merci": {"rg": "SENTETİK RG", "yururluk": "2026-01-01", "teyit_tarihi": "2026-10-05",
                       "kalemler": {
                           "sulh_icra_tetkik_basvuru": {"tutar": 40.0, "satir": "sentetik A-I-1"},
                           "vergi_basvuru_vm_bim": {"tutar": 90.0, "satir": "sentetik (3) I-a"},
                           "vergi_istinaf_bim": {"tutar": 320.0, "satir": "sentetik (3) I-d"},
                           "vergi_temyiz_danistay": {"tutar": 420.0, "satir": "sentetik (3) I-c"},
                           "vergi_nispi_vm_bim_binde": {"tutar": 5.0, "asgari": 150.0,
                                                        "satir": "sentetik (3) II-a"}}},
        "aaut": aaut,
        "oran_kurallari": GERCEK.get("oran_kurallari"),
    }


def _yaz(tmp_path, veri):
    yol = tmp_path / "tarife.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return str(yol)


# ═══════════════════════ Av.K. m.168/2 — nispi dilim UYGULANMAZ ═══════════════════

def test_vergi_merciinde_nispi_dilim_uygulanmaz():
    """Nispi dilim dolu (50.000'e kadar %10, üstü %5); asliyede 100.000 × 0,6 → lehe
    5.500 / aleyhe 4.000 çıkardı. Vergide (Av.K. m.168/2 maktu) bu rakamlar ÜRETİLMEZ:
    tam kabul/ret → maktu_vergi (AAÜT m.15/1 'tamamına'); kısmi kabul/ret → dağılım
    genel hükümlerde okunamadı → None + görünür not; hiçbir hâlde 5.500/4.000/7.500 yok."""
    t = _sentetik()
    kismi = MOD.hesapla(100000, 0.6, t, merci="vergi")
    kv = kismi["karsi_vekalet"]
    assert kv["lehe_kabul_kismi"] is None and kv["aleyhe_ret_kismi"] is None, kv
    assert 5500.0 not in kv.values() and 4000.0 not in kv.values()
    assert "aaut.nispi_dilimler" not in kismi["eksik_alanlar"], kismi["eksik_alanlar"]
    # KÜÇÜK-8 (inceleme): m.168/2 notu HARÇ bölümünün listesinde DEĞİL, karşı vekâlet notlarında
    assert any("m.168/2" in n for n in kismi["vekalet_notlari"]), kismi["vekalet_notlari"]
    assert not any("m.168/2" in n for n in kismi["notlar"]), kismi["notlar"]
    assert kismi["hesaplanamayan"] and any("m.168/2" in h for h in kismi["hesaplanamayan"])
    tam = MOD.hesapla(100000, 1.0, t, merci="vergi")
    assert tam["karsi_vekalet"] == {"lehe_kabul_kismi": 700.0, "aleyhe_ret_kismi": 0.0}, tam["karsi_vekalet"]
    assert tam["hesaplanamayan"] == []
    ret = MOD.hesapla(100000, 0.0, t, merci="vergi")
    assert ret["karsi_vekalet"] == {"lehe_kabul_kismi": 0.0, "aleyhe_ret_kismi": 700.0}, ret["karsi_vekalet"]
    # kontrol: asliye kolu DEĞİŞMEDİ (nispi dilim orada hâlâ uygulanır)
    asliye = MOD.hesapla(100000, 0.6, t, merci="asliye")
    assert asliye["karsi_vekalet"] == {"lehe_kabul_kismi": 5500.0, "aleyhe_ret_kismi": 4000.0}
    assert asliye["hesaplanamayan"] == []


def test_vergi_maktu_alani_bossa_eksik_listesinde():
    """`aaut.maktu_vergi` null/yok → 'aaut.maktu_vergi' eksik listesinde, karşı vekâlet
    None; `aaut.nispi_dilimler` vergi için İLGİSİZDİR — boş olsa da eksik SAYILMAZ,
    dolu olsa da kullanılmaz."""
    bos = MOD.hesapla(100000, 1.0, _sentetik(maktu_vergi=None), merci="vergi")
    assert "aaut.maktu_vergi" in bos["eksik_alanlar"], bos["eksik_alanlar"]
    assert "aaut.nispi_dilimler" not in bos["eksik_alanlar"]
    assert bos["karsi_vekalet"] == {"lehe_kabul_kismi": None, "aleyhe_ret_kismi": None}
    # maktu var, nispi dilim BOŞ → vergide eksik DEĞİL (asliyede eksik olurdu)
    dilimsiz = MOD.hesapla(100000, 1.0, _sentetik(dilimler=[]), merci="vergi")
    assert "aaut.nispi_dilimler" not in dilimsiz["eksik_alanlar"], dilimsiz["eksik_alanlar"]
    assert dilimsiz["karsi_vekalet"]["lehe_kabul_kismi"] == 700.0
    asliye_dilimsiz = MOD.hesapla(100000, 1.0, _sentetik(dilimler=[]), merci="asliye")
    assert "aaut.nispi_dilimler" in asliye_dilimsiz["eksik_alanlar"]


def test_vergi_notu_dayanaklari_ve_okunamayan_dagilimi_soyler():
    """Not: Av.K. m.168/2 (maktu), AAÜT m.15/1 (yarısı/tamamı — aşama bilinmez),
    m.3/1 (üç katına kadar takdir — çıpa), m.13/2 tavanının maktu vergi ücretine
    uygulanması OKUNAMADI (tavan uygulanmadı) — hiçbiri sessiz değil."""
    s = MOD.hesapla(100000, 0.5, _sentetik(), merci="vergi")
    not_metni = " ".join(s["vekalet_notlari"])
    for k in ("m.168/2", "5904", "6183", "maktu", "m.15/1", "yarısı", "m.3/1", "üç katı", "m.13/2"):
        assert k in not_metni, (k, not_metni)
    h = " ".join(s["hesaplanamayan"])
    assert "kısmi" in h.lower() and "okunamadı" in h.lower() and "rakam" in h.lower(), h


def test_vergi_kismi_ust_bandi_bilinen_maktuyu_UST_SINIR_olarak_icerir():
    """ÖNEMLİ-1 (inceleme): kısmi kabul/rette karşı vekâlet HESAPLANAMADI iken ÜST gider bandı
    onu sessizce dışlıyor, etiketi 'aleyhe vekâlet dahil' diyordu → müvekkilin azami maruziyeti
    maktu kadar DÜŞÜK görünüyordu (1.830 yerine 2.530). Bilinen maktu ÜST SINIR olarak eklenir
    (müvekkil için güvenli yön); maktu bilinmiyorsa band 'haric' diye işaretlenir — mevcut
    null-maktu kilidi (test_v0518_hesap.py 191-195) bozulmaz."""
    t = _sentetik()
    taban = 90 + 500 + 500 + 320 + 420      # başvuru + karar (dava değeri) + keşif + istinaf + temyiz
    kismi = MOD.hesapla(100000, 0.6, t, merci="vergi")
    assert kismi["gider_bandi"]["ust"] == taban + 700, kismi["gider_bandi"]
    assert kismi["gider_bandi"]["ust_vekalet"] == "maktu_ust_sinir"
    tam_ret = MOD.hesapla(100000, 0.0, t, merci="vergi")
    assert tam_ret["gider_bandi"]["ust"] == taban + 700 and tam_ret["gider_bandi"]["ust_vekalet"] == "dahil"
    tam_kabul = MOD.hesapla(100000, 1.0, t, merci="vergi")
    assert tam_kabul["gider_bandi"]["ust"] == taban and tam_kabul["gider_bandi"]["ust_vekalet"] == "dahil"
    bos = MOD.hesapla(100000, 0.6, _sentetik(maktu_vergi=None), merci="vergi")
    assert bos["gider_bandi"]["ust"] == taban and bos["gider_bandi"]["ust_vekalet"] == "haric"
    idare = MOD.hesapla(100000, 0.6, t, merci="idare")     # maktu_idare yok → dışarıda, ETİKETLİ
    assert idare["gider_bandi"]["ust"] == 100 + 5000 + 500 and idare["gider_bandi"]["ust_vekalet"] == "haric"


def test_idare_merciinde_m168_2_gorunur_uyari_kapsam_genislemeden(tmp_path):
    """KÜÇÜK-9 (inceleme): idare mahkemesindeki 6183/harç kaynaklı dava (ecrimisil, idari para
    cezası ödeme emri) Av.K. m.168/2 'her türlü dava' kapsamında maktu iken `--merci idare`
    nispi kolda kalır — kapsam GENİŞLETİLMEDİ (merci eklenmedi); yalnız görünür uyarı."""
    s = MOD.hesapla(100000, 0.6, _sentetik(), merci="idare")
    uyari = [n for n in s["vekalet_notlari"] if "m.168/2" in n]
    assert uyari and "6183" in uyari[0] and "nispi" in uyari[0].lower() and "avukat" in uyari[0].lower(), s["vekalet_notlari"]
    assert MOD.hesapla(100000, 0.6, _sentetik(), merci="asliye")["vekalet_notlari"] == []
    assert "idare" not in MOD.AVK168_MAKTU_MERCILER
    rc, out, _ = _cli("--deger", "100000", "--merci", "idare", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026")
    blok = out[out.index("KARŞI VEKÂLET"):out.index("YARGILAMA GİDERİ BANDI")]
    assert "m.168/2" in blok and "6183" in blok, out


def test_avk168_maktu_mercileri_sabiti_vergiyi_kapsar():
    """Aynı rejimdeki (vergi/resim/harç/6183) mercilerin genişleme noktası tek
    sabittir; bugün yalnız 'vergi' (6183 ödeme emri davası vergi mahkemesinde)."""
    assert "vergi" in MOD.AVK168_MAKTU_MERCILER
    assert set(MOD.AVK168_MAKTU_MERCILER) <= set(MOD.MERCILER)
    assert "asliye" not in MOD.AVK168_MAKTU_MERCILER


# ═══════════════════════ CLI — görünür not, exit 2, JSON ═══════════════════════════

def test_cli_vergi_kismi_kabul_rakam_yerine_gorunur_not_exit2(tmp_path):
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.6", "--merci", "vergi",
                      "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026", "--json")
    assert rc == 2, out
    assert "m.168/2" in out and "MAKTU" in out, out
    assert "HESAPLANAMAYAN" in out and "rakam" in out.lower(), out
    assert "5.500,00 TL" not in out and "4.000,00 TL" not in out, "nispi dilim rakamı sızdı"
    # Tarife DOLU; okunamayan şey KURAL — satır 'tarife alanı null' diyemez (yanlış teşhis
    # avukatı tarife.json doldurmaya yönlendirir, oysa bunu kapatmaz).
    assert "tarife alanı null" not in out, out
    assert "HESAPLANAMADI" in out, out
    # KÜÇÜK-6: '%' denetimi ilgili bölüme daraltılır; JSON bloğu ayırt ediciyle ayrılır
    vekalet_blok = out[out.index("KARŞI VEKÂLET"):out.index("YARGILAMA GİDERİ BANDI")]
    assert "%" not in vekalet_blok, vekalet_blok
    # ÖNEMLİ-1: ÜST bandı bilinen maktuyu ÜST SINIR olarak içerir ve bunu satırda söyler
    ust_satiri = next(s for s in out.splitlines() if s.strip().startswith("ÜST ("))
    assert "2.530,00 TL" in ust_satiri and "ÜST SINIR" in ust_satiri, ust_satiri
    js = json.loads(out[out.index("\n{\n") + 1:])      # json.dumps(indent=2): '{' tek başına satırda
    assert js["hesaplanamayan"] and js["karsi_vekalet"]["lehe_kabul_kismi"] is None
    assert js["gider_bandi"]["ust_vekalet"] == "maktu_ust_sinir"


def test_cli_vergi_tam_kabul_maktu_exit0(tmp_path):
    """Tüm kalemler teyitli tarifeden hesaplandı (tam kabul → maktu; harç kalemleri
    sentetik tarifede dolu) → exit 0; karşı vekâlet satırında maktu tutar."""
    rc, out, _ = _cli("--deger", "100000", "--merci", "vergi",
                      "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026")
    assert rc == 0, out
    assert "Lehe (kabul edilen kısım)                  : 700,00 TL" in out, out
    assert "ALEYHE (reddedilen kısım — müvekkil öder)  : 0,00 TL" in out, out
    assert "Av.K. m.168/2" in out and "nispi dilim" in out.lower(), out
    # KÜÇÜK-8: m.168/2 notu KARŞI VEKÂLET başlığından ÖNCE (HARÇ bölümünde) basılmaz
    assert "m.168/2" not in out[:out.index("KARŞI VEKÂLET")], out


def test_cli_vergi_maktu_bos_exit2_ve_nispi_dilim_istenmez(tmp_path):
    rc, out, _ = _cli("--deger", "100000", "--merci", "vergi",
                      "--tarife", _yaz(tmp_path, _sentetik(maktu_vergi=None)), "--yil", "2026")
    assert rc == 2 and "aaut.maktu_vergi" in out, out
    assert "aaut.nispi_dilimler" not in out
    # ÖNEMLİ-1: maktu da bilinmiyorsa ÜST bandı aleyhe vekâleti içermez ve bunu SÖYLER
    ust_satiri = next(s for s in out.splitlines() if s.strip().startswith("ÜST ("))
    assert "DAHİL DEĞİL" in ust_satiri, ust_satiri


def test_gercek_tarife_vergide_de_rakam_uretmez_ve_sabit_tasimaz():
    """Gerçek tarife.json (KÜÇÜK-5: veri durumu kilitlenmez): `aaut.maktu_vergi` NULL ise
    vergide karşı vekâlet None ve eksik listesinde; avukat tabloyu doldurduğu gün ise tam
    kabulde o sayı yazılır, kısmi dağılım yine üretilmez. Nispi dilim hiçbir hâlde istenmez;
    script hiçbir tarife rakamı taşımaz (yalnız anahtar adı)."""
    maktu = GERCEK["aaut"].get("maktu_vergi")
    kismi = MOD.hesapla(100000, 0.6, GERCEK, merci="vergi")
    assert kismi["karsi_vekalet"] == {"lehe_kabul_kismi": None, "aleyhe_ret_kismi": None}
    assert "aaut.nispi_dilimler" not in kismi["eksik_alanlar"]
    if maktu is None:
        assert "aaut.maktu_vergi" in kismi["eksik_alanlar"] and kismi["hesaplanamayan"] == []
    else:
        assert "aaut.maktu_vergi" not in kismi["eksik_alanlar"] and kismi["hesaplanamayan"]
        tam = MOD.hesapla(100000, 1.0, GERCEK, merci="vergi")
        assert tam["karsi_vekalet"]["lehe_kabul_kismi"] == float(maktu)
    kaynak = SCRIPT.read_text(encoding="utf-8")
    assert "AVK168_MAKTU_MERCILER" in kaynak
    assert not re.search(r"maktu_vergi\W+\d", kaynak), "script'e maktu tutar gömülmüş"


# ═══════════════════════ Talimat katmanı ═══════════════════════════════════════════

def test_strateji_skill_md_ve_gunluk_m168_2_maktuyu_anlatir():
    md = STRATEJI_MD.read_text(encoding="utf-8")
    assert "m.168/2" in md and "maktu_vergi" in md, "SKILL.md vergi davasında karşı vekâletin MAKTU olduğunu söylemeli"
    # KÜÇÜK-7: kanonik "Çıkış kodları" satırı hesaplanamayan (kuralı okunamayan kalem) sebebini sayar
    i = md.index("**Çıkış kodları:**")
    assert "hesaplanamayan" in md[i:i + 500], md[i:i + 500]
    # KÜÇÜK-9: idare merciindeki 6183/harç kaynaklı dava için görünür not (kapsam genişlemeden)
    assert "--merci idare" in md and "ecrimisil" in md, "SKILL.md idare merciindeki m.168/2 boşluğunu söylemeli"
    g = STRATEJI_GUNLUK.read_text(encoding="utf-8")
    assert "m.168/2" in g
