# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — HESAP + GÜNCEL ORAN: oa-strateji/scripts/maliyet_cetveli.py + tarife.json

Saha kanıtı: yetenek denetimi bulgusu Y-07 — "2026 harçları doğru (9/9); AAÜT ücret
tabloları boş; sulh/icra ve vergi yargısı harçları yok". Fikir kaynağı Yargı PRO
14-1 (hukuki hesaplama) ve 14-2 (güncel oran teyidi) — kod/metin alınmadı.

Resmî metin teyidi (Yargı PRO MCP, 2026-10-05):
  * RG 31.12.2025/33124 (5. mük.) Harçlar Kanunu Genel Tebliği (Seri No: 98) +
    mevzuat.gov.tr 492 s.K. tarifeleri 'Uygulanan Miktar' sütunu — iki kaynakta
    aynı tutar (sulh/icra tetkik başvurma, BAM/BİM/Yargıtay/Danıştay başvurma,
    AYM başvurma, (3) sayılı tarife vergi yargısı kalemleri).
  * 492 s.K. m.28/a (peşin dörtte bir; ölüm/cismani zarar tazminatında yirmide bir).
  * 3095 s.K. m.1 (Değişik: 7589/10), m.2; 7589 m.26/1-c (yayım RG 31.07.2026).
  * AAÜT (mevzuat.gov.tr 42687) m.13, m.21 — tablolar yalnız .doc eki → null.

Sözleşme: script hiçbir tarife rakamı ve hiçbir ORAN taşımaz; kaynaksız/tarihsiz
oranla yapılan faiz hesabı görünür uyarıyla ÇIPA (exit 2); oran verilmezse faiz
hesaplanmaz (exit 1). Fikstürler sentetiktir; testler tmp_path'te koşar.
"""
import datetime as dt
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


def _load():
    spec = importlib.util.spec_from_file_location("v0518_maliyet_cetveli", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()
GERCEK = json.loads(TARIFE.read_text(encoding="utf-8"))


def _cli(*args):
    cp = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(REPO))
    return cp.returncode, cp.stdout, cp.stderr


def _sentetik(**degisiklik):
    """Tam dolu SENTETİK tarife (gerçek değer DEĞİL — aritmetik sınavı için yuvarlak
    sayılar). harc_merci ve aaut merci maktuları da sentetik."""
    t = {
        "yil": 2026, "mcp_teyit_tarihi": "2026-10-05",
        "kaynak": "SENTETİK TEST TARİFESİ — gerçek değer değildir",
        "harc": {"basvuru_maktu": 100.0, "karar_ilam_nispi_binde": 50.0, "pesin_oran": 0.25,
                 "pesin_oran_olum_cismani": 0.05, "nispi_asgari": 200.0,
                 "istinaf_basvuru_maktu": 300.0, "temyiz_basvuru_maktu": 400.0, "kesif": 500.0},
        "harc_merci": {"rg": "SENTETİK RG", "yururluk": "2026-01-01", "teyit_tarihi": "2026-10-05",
                       "kalemler": {
                           "sulh_icra_tetkik_basvuru": {"tutar": 40.0, "satir": "sentetik A-I-1"},
                           "bim_istinaf": {"tutar": 310.0, "satir": "sentetik A-IV-d"},
                           "danistay_temyiz": {"tutar": 410.0, "satir": "sentetik A-IV-c"},
                           "vergi_basvuru_vm_bim": {"tutar": 90.0, "satir": "sentetik (3) I-a"},
                           "vergi_istinaf_bim": {"tutar": 320.0, "satir": "sentetik (3) I-d"},
                           "vergi_temyiz_danistay": {"tutar": 420.0, "satir": "sentetik (3) I-c"},
                           "vergi_nispi_vm_bim_binde": {"tutar": 5.0, "asgari": 150.0, "satir": "sentetik (3) II-a"}}},
        "aaut": {"maktu_asliye": 1000.0, "maktu_sulh": 600.0,
                 "nispi_dilimler": [{"ust": 50000, "yuzde": 10}, {"ust": None, "yuzde": 5}]},
        "oran_kurallari": GERCEK.get("oran_kurallari"),
    }
    for k, v in degisiklik.items():
        if isinstance(v, dict) and isinstance(t.get(k), dict):
            t[k].update(v)
        else:
            t[k] = v
    return t


def _yaz(tmp_path, veri, ad="tarife.json"):
    yol = tmp_path / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return str(yol)


# ═══════════════════════ tarife.json — Y-07 kalemleri ══════════════════════

def test_harc_merci_blogu_kaynakli_ve_yururluk_tarihli():
    b = GERCEK["harc_merci"]
    assert "Seri No: 98" in b["rg"] and "33124" in b["rg"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", b["yururluk"]) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", b["teyit_tarihi"])
    assert dt.date.fromisoformat(b["yururluk"]).year == GERCEK["yil"]
    assert "mevzuat.gov.tr" in b["_aciklama"] and "İKİ resmî kaynak" in b["_aciklama"]
    for ad, k in b["kalemler"].items():
        assert isinstance(k["tutar"], (int, float)) and k["tutar"] > 0, ad
        assert "tarife" in k["satir"], ad
    gecerli, neden = MOD.merci_blogu_gecerli(GERCEK)
    assert gecerli, neden


def test_2026_dogrulanmis_kalemler_kilitli():
    """Yalnız 2026 tarifesi iken: iki resmî kaynakta birebir okunan tutarlar.
    Yıl değişince dosya yeniden teyit edilir; bu test o yıl için atlanmaz,
    koşulu kendiliğinden düşer (yalnız yapı testleri kalır)."""
    if GERCEK["yil"] != 2026:
        return
    k = {ad: v["tutar"] for ad, v in GERCEK["harc_merci"]["kalemler"].items()}
    beklenen = {"sulh_icra_tetkik_basvuru": 335.2, "asliye_idare_basvuru": 732.0,
                "bam_bim_yargitay_danistay_basvuru": 1124.5, "aym_basvuru": 6024.1,
                "danistay_temyiz": 3608.5, "bim_istinaf": 2002.0, "icraya_basvurma": 732.0,
                "vergi_basvuru_vm_bim": 732.0, "vergi_basvuru_danistay": 1526.2,
                "vergi_temyiz_danistay": 3189.5, "vergi_istinaf_bim": 2121.7,
                "vergi_nispi_vm_bim_binde": 4.55, "vergi_nispi_danistay_binde": 9.1,
                "vergi_maktu_vm_bim": 732.0, "vergi_yd_karar": 1526.2}
    for ad, tutar in beklenen.items():
        assert k[ad] == tutar, (ad, k[ad], tutar)
    assert GERCEK["harc"]["pesin_oran_olum_cismani"] == 0.05
    assert "m.28/a" in GERCEK["harc"]["_pesin_oran_olum_cismani_kaynak"]


def test_aaut_tablolari_null_ve_TEYIT_BEKLIYOR():
    a = GERCEK["aaut"]
    assert a["maktu_asliye"] is None and a["nispi_dilimler"] == []
    assert "TEYİT BEKLİYOR" in a["_not"] and "42687" in a["_not"] and "m.21" in a["_not"]


def test_tarife_json_oran_tasimaz():
    """oran_kurallari yalnız kural metni ve tarih taşır; sayısal bir ORAN yok."""
    ok = GERCEK["oran_kurallari"]
    def _gez(x):
        if isinstance(x, dict):
            for v in x.values():
                yield from _gez(v)
        elif isinstance(x, list):
            for v in x:
                yield from _gez(v)
        else:
            yield x
    assert not any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in _gez(ok))
    assert any(r["tarih"] == "2026-07-31" and "7589" in r["kaynak"] for r in ok["rejim_sinirlari"])


# ═══════════════════════ merci kalemleri ══════════════════════════════════

def test_merci_sulh_basvuru_merci_blogundan_ve_maktu_merciye_gore():
    s = MOD.hesapla(100000, 0.6, _sentetik(), merci="sulh")
    assert s["harc"]["basvuru_maktu"] == 40.0
    assert s["harc"]["dava_acilis_toplam"] == 40.0 + 1250.0
    # sulh maktu 600 kullanıldı (asliye 1000 DEĞİL): ret 40.000 → nispi 4.000 > 600 → 4.000
    assert s["karsi_vekalet"]["aleyhe_ret_kismi"] == 4000.0
    s2 = MOD.hesapla(100000, 0.995, _sentetik(), merci="sulh")
    assert s2["karsi_vekalet"]["aleyhe_ret_kismi"] == 500.0   # taban 600 > ret 500 → tavan 500


def test_baska_merci_icin_asliye_maktuu_kullanilmaz():
    s = MOD.hesapla(100000, 0.6, _sentetik(), merci="icra_tetkik")
    assert "aaut.maktu_icra_tetkik" in s["eksik_alanlar"]
    assert s["karsi_vekalet"]["aleyhe_ret_kismi"] is None


def test_merci_blogu_yoksa_ya_da_yili_tutmazsa_kalem_teyitsiz(tmp_path):
    t = _sentetik()
    del t["harc_merci"]
    rc, out, _ = _cli("--deger", "100000", "--merci", "sulh", "--tarife", _yaz(tmp_path, t), "--yil", "2026")
    assert rc == 2 and "harc_merci.sulh_icra_tetkik_basvuru" in out and "TEYİTSİZ" in out
    t2 = _sentetik(harc_merci={"yururluk": "2025-01-01"})
    gecerli, neden = MOD.merci_blogu_gecerli(t2)
    assert not gecerli and "2025" in neden
    s = MOD.hesapla(100000, 1.0, t2, merci="sulh")
    assert s["harc"]["basvuru_maktu"] is None and "harc_merci.sulh_icra_tetkik_basvuru" in s["eksik_alanlar"]


def test_merci_vergi_ucuncu_tarife_pesin_hesaplanmaz_notlu(tmp_path):
    s = MOD.hesapla(100000, 1.0, _sentetik(), merci="vergi")
    h = s["harc"]
    assert h["basvuru_maktu"] == 90.0 and h["karar_ilam_dava_degeri"] == 500.0
    assert h["karar_ilam_pesin"] is None and h["dava_acilis_toplam"] == 90.0
    assert any("TEYİT BEKLİYOR" in n and "m.28" in n for n in s["notlar"])
    assert "harc.pesin_oran" not in s["eksik_alanlar"]
    rc, out, _ = _cli("--deger", "1000", "--merci", "vergi", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026")
    assert "(3) sayılı tarife" in out and "TEYİT BEKLİYOR — hesaplanmadı" in out
    assert "Karar ve ilam harcı — dava değeri üzerinden: 150,00 TL" in out   # asgari had
    assert "%" not in out


def test_idare_mercii_kanun_yolu_satirlari_merci_blogundan():
    s = MOD.hesapla(100000, 1.0, _sentetik(), merci="idare")
    assert "aaut.maktu_idare" in s["eksik_alanlar"]          # idare maktuu verilmedi → vekâlet yok
    # üst bant: başvuru 100 + karar 5000 + keşif 500 + BİM istinaf 310 + Danıştay temyiz 410
    assert s["gider_bandi"]["ust"] == 100 + 5000 + 500 + 310 + 410


def test_olum_cismani_pesin_yirmide_bir_ve_not():
    s = MOD.hesapla(100000, 1.0, _sentetik(), olum_cismani=True)
    assert s["harc"]["karar_ilam_pesin"] == 250.0       # 5000 × 1/20
    assert any("m.28/a" in n for n in s["notlar"])
    t = _sentetik()
    del t["harc"]["pesin_oran_olum_cismani"]
    s2 = MOD.hesapla(100000, 1.0, t, olum_cismani=True)
    assert "harc.pesin_oran_olum_cismani" in s2["eksik_alanlar"] and s2["harc"]["karar_ilam_pesin"] is None


def test_varsayilan_cagri_geriye_uyumlu_merci_satiri_basmaz(tmp_path):
    t = _sentetik()
    del t["harc_merci"]
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.6", "--tarife", _yaz(tmp_path, t), "--yil", "2026")
    assert rc == 0, out
    assert "Merci:" not in out and "DAVA AÇILIŞ TOPLAMI (başvuru + peşin)      : 1.350,00 TL" in out
    assert "ZAMAN NOTU" in out and "AAÜT m.21" in out


# ═══════════════════════ faiz + güncel oran teyidi ════════════════════════

def _oran_dosyasi(tmp_path, dilimler, ad="oranlar.json"):
    yol = tmp_path / ad
    yol.write_text(json.dumps({"oranlar": dilimler}, ensure_ascii=False), encoding="utf-8")
    return str(yol)


def _dilim(bas, bit, oran, tur="sozlesme", kaynak="SENTETİK KAYNAK — test", teyit="2026-10-05"):
    return {"tur": tur, "baslangic": bas, "bitis": bit, "yillik_yuzde": oran, "kaynak": kaynak,
            "teyit_tarihi": teyit}


def test_faiz_oran_verilmezse_hesaplanmaz_exit1(tmp_path):
    rc, out, err = _cli("--deger", "100000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026",
                        "--faiz-baslangic", "2026-01-01", "--faiz-bitis", "2026-03-01")
    assert rc == 1 and "oran ÜRETMEZ" in err and "FAİZ" not in out


def test_faiz_kaynakli_teyitli_dilim_tam_cetvel_exit0(tmp_path):
    oran = _oran_dosyasi(tmp_path, [_dilim("2026-08-01", "2026-12-31", 30)])
    rc, out, _ = _cli("--deger", "100000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026",
                      "--faiz-baslangic", "2026-08-01", "--faiz-bitis", "2026-10-01", "--oranlar", oran, "--json")
    assert rc == 0, out
    js = json.loads(out[out.index("{"):])
    assert js["faiz"]["teyitli"] is True and js["faiz"]["hesaplanan_gun"] == 61
    assert js["faiz"]["tutar"] == round(100000 * 30 / 100 * 61 / 365, 2)
    assert "FAİZ KALEMİ: TEYİTLİ" in out and "%" not in out


def test_faiz_kaynaksiz_tarihsiz_oran_gorunur_uyari_cipa_exit2(tmp_path):
    rc, out, _ = _cli("--deger", "100000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026",
                      "--faiz-baslangic", "2026-02-01", "--faiz-bitis", "2026-03-01", "--faiz-orani", "12",
                      "--faiz-turu", "sozlesme")
    assert rc == 2
    assert "KAYNAKSIZ/TARİHSİZ ORAN" in out and "ÇIPA" in out and "kaynak: YOK" in out


def test_faiz_kapsanmayan_gun_hesaplanmaz(tmp_path):
    oran = _oran_dosyasi(tmp_path, [_dilim("2026-01-01", "2026-01-31", 10), _dilim("2026-02-10", "2026-03-31", 10)])
    fz = MOD.faiz_hesapla(36500, dt.date(2026, 1, 1), dt.date(2026, 3, 1), MOD.oranlar_yukle(oran))
    assert fz["kapsanmayan"] == ["2026-02-01..2026-02-09"]
    assert fz["hesaplanan_gun"] == fz["gun"] - 9 and fz["teyitli"] is False
    assert fz["tutar"] == round(36500 * 0.10 / 365 * fz["hesaplanan_gun"], 2)


def test_faiz_cakisan_farkli_oranli_dilimler_hesaplanmaz():
    fz = MOD.faiz_hesapla(1000, dt.date(2026, 1, 1), dt.date(2026, 1, 11),
                          [_dilim("2026-01-01", "2026-01-10", 10), _dilim("2026-01-06", "2026-01-31", 20)])
    assert fz["cakisan"] == ["2026-01-06..2026-01-10"] and fz["hesaplanan_gun"] == 5 and not fz["teyitli"]


def test_faiz_teyit_sonrasi_projeksiyon_cipa():
    """Kuralı olmayan türde (diger) teyit gününden sonrası projeksiyondur."""
    fz = MOD.faiz_hesapla(1000, dt.date(2026, 10, 1), dt.date(2026, 12, 1),
                          [_dilim("2026-01-01", "2027-12-31", 10, tur="diger", teyit="2026-10-05")])
    assert fz["projeksiyon_gun"] == (dt.date(2026, 12, 1) - dt.date(2026, 10, 6)).days and not fz["teyitli"]


def test_faiz_projeksiyon_ture_gore_sozlesme_ve_yariyil():
    """Sözleşme faizinin oranı sözleşmeden gelir → projeksiyon yok. Yarıyıl
    kuralına tabi oran (7589 sonrası kanuni faiz) teyit edildiği yarıyılın
    sonuna kadar bilinir; sonraki yarıyıl projeksiyondur."""
    k = GERCEK["oran_kurallari"]
    soz = MOD.faiz_hesapla(1000, dt.date(2026, 10, 1), dt.date(2026, 12, 1),
                           [_dilim("2026-01-01", "2027-12-31", 10, tur="sozlesme", teyit="2026-10-05")], k)
    assert soz["projeksiyon_gun"] == 0 and soz["teyitli"]
    ayni = MOD.faiz_hesapla(1000, dt.date(2026, 10, 1), dt.date(2026, 12, 1),
                            [_dilim("2026-08-01", "2026-12-31", 10, tur="kanuni", teyit="2026-10-05")], k)
    assert ayni["projeksiyon_gun"] == 0 and ayni["teyitli"], ayni
    sonraki = MOD.faiz_hesapla(1000, dt.date(2027, 1, 1), dt.date(2027, 2, 1),
                               [_dilim("2027-01-01", "2027-06-30", 10, tur="kanuni", teyit="2026-10-05")], k)
    assert sonraki["projeksiyon_gun"] == 31 and not sonraki["teyitli"]


def test_faiz_turu_zorunlu_bilinmeyen_tur_reddedilir(tmp_path):
    rc, _, err = _cli("--deger", "1000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026",
                      "--faiz-baslangic", "2026-02-01", "--faiz-bitis", "2026-03-01", "--faiz-orani", "12",
                      "--faiz-kaynak", "SENTETİK", "--faiz-teyit", "2026-10-05")
    assert rc == 1 and "--faiz-turu zorunlu" in err
    for tur in ("garip", None):
        d = _dilim("2026-01-01", "2026-12-31", 9)
        d["tur"] = tur
        with pytest.raises(MOD.OranHatasi):
            MOD.faiz_hesapla(1000, dt.date(2026, 1, 1), dt.date(2026, 2, 1), [d])


def test_faiz_oran_kurallari_yoksa_kanuni_faiz_denetlenemedi():
    kanuni = MOD.faiz_hesapla(1000, dt.date(2026, 1, 1), dt.date(2026, 2, 1),
                              [_dilim("2026-01-01", "2026-03-31", 9, tur="kanuni", teyit="2026-03-31")], None)
    assert any("oran_kurallari" in h and "DENETLENEMEDİ" in h for h in kanuni["hatirlatmalar"])
    assert not kanuni["teyitli"]
    soz = MOD.faiz_hesapla(1000, dt.date(2026, 1, 1), dt.date(2026, 2, 1),
                           [_dilim("2026-01-01", "2026-03-31", 9, tur="sozlesme")], None)
    assert soz["hatirlatmalar"] == [] and soz["teyitli"]


def test_faiz_kesir_gibi_oran_gorunur_uyari_engellemez():
    fz = MOD.faiz_hesapla(1000, dt.date(2026, 1, 1), dt.date(2026, 2, 1),
                          [_dilim("2026-01-01", "2026-03-31", 0.24)])
    assert fz["uyarilar"] and "kesir" in fz["uyarilar"][0] and fz["teyitli"]
    assert not any("%" in satir for satir in MOD._faiz_raporu(fz))


def test_faiz_7589_rejim_siniri_hatirlatmasi():
    fz = MOD.faiz_hesapla(1000, dt.date(2026, 6, 1), dt.date(2026, 9, 1),
                          [_dilim("2026-06-01", "2026-09-01", 9, tur="kanuni")], GERCEK["oran_kurallari"])
    assert any("REJİM SINIRI 2026-07-31" in h and "7589" in h for h in fz["hatirlatmalar"])
    assert not fz["teyitli"]


def test_faiz_yariyil_hatirlatmasi_ture_ve_rejime_gore():
    k = GERCEK["oran_kurallari"]
    avans = MOD.faiz_hesapla(1000, dt.date(2025, 3, 1), dt.date(2025, 9, 1),
                             [_dilim("2025-03-01", "2025-09-01", 9, tur="avans")], k)
    assert any("2025-07-01" in h for h in avans["hatirlatmalar"])
    # 7589 öncesi kanuni faiz için yarıyıl kuralı YOK (gürültü üretilmez)
    eski = MOD.faiz_hesapla(1000, dt.date(2025, 3, 1), dt.date(2025, 9, 1),
                            [_dilim("2025-03-01", "2025-09-01", 9, tur="kanuni")], k)
    assert not eski["hatirlatmalar"]
    # 7589 sonrası kanuni faiz 1 Ocak 2027 sınırını keserse hatırlatma VAR
    yeni = MOD.faiz_hesapla(1000, dt.date(2026, 8, 1), dt.date(2027, 3, 1),
                            [_dilim("2026-08-01", "2027-03-01", 9, tur="kanuni", teyit="2027-03-01")], k)
    assert any("2027-01-01" in h for h in yeni["hatirlatmalar"])
    # sözleşmesel faizde hatırlatma yok
    soz = MOD.faiz_hesapla(1000, dt.date(2025, 3, 1), dt.date(2025, 9, 1),
                           [_dilim("2025-03-01", "2025-09-01", 9, tur="sozlesme")], k)
    assert not soz["hatirlatmalar"]


def test_faiz_donem_ve_dilim_ust_siniri_kilitlenmez():
    """Kaynak koruması: absürt dönem (veri hatası) hesaplanmaz; uzun ama makul
    dönem aralık taramasıyla (gün gün değil) hesaplanır — sonuç birebir."""
    with pytest.raises(MOD.OranHatasi):
        MOD.faiz_hesapla(1000, dt.date(1800, 1, 1), dt.date(2026, 1, 1), [_dilim("1800-01-01", "2026-12-31", 9)])
    with pytest.raises(MOD.OranHatasi):
        MOD.faiz_hesapla(1000, dt.date(2026, 1, 1), dt.date(2026, 2, 1),
                         [_dilim("2026-01-01", "2026-12-31", 9)] * (MOD.AZAMI_DILIM + 1))
    fz = MOD.faiz_hesapla(36500, dt.date(1950, 1, 1), dt.date(2040, 1, 1), [_dilim("1950-01-01", "2039-12-31", 10)])
    gun = (dt.date(2040, 1, 1) - dt.date(1950, 1, 1)).days
    assert fz["hesaplanan_gun"] == gun and fz["tutar"] == round(36500 * 0.10 / 365 * gun, 2)


def test_faiz_bicimsiz_oran_dosyasi_exit1(tmp_path):
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text('{"oranlar": [{"baslangic": "dün", "bitis": "2026-01-01", "yillik_yuzde": 9}]}', encoding="utf-8")
    rc, _, err = _cli("--deger", "1000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026",
                      "--faiz-baslangic", "2026-01-01", "--faiz-bitis", "2026-02-01", "--oranlar", str(bozuk))
    assert rc == 1 and "ISO tarih değil" in err
    with pytest.raises(MOD.OranHatasi):
        MOD.faiz_hesapla(1000, dt.date(2026, 2, 1), dt.date(2026, 1, 1), [_dilim("2026-01-01", "2026-12-31", 9)])


def test_script_tarife_ve_oran_sabiti_tasimaz():
    src = SCRIPT.read_text(encoding="utf-8")
    for yasak in ("335,20", "335.2", "1124", "6024", "3189", "2121", "1526", "4.55", "9.1"):
        assert yasak not in src, f"script gövdesinde tarife rakamı gömülü: {yasak}"
    assert "__OA_UTF8_GUARD__" in src
    assert not re.search(r"^\s*(?:from|import)\s+(requests|httpx|urllib|socket)", src, re.M)


# ═══════════════════════ SKILL.md protokolü ═══════════════════════════════

def test_skill_md_guncel_oran_teyidi_protokolu():
    txt = STRATEJI_MD.read_text(encoding="utf-8")
    assert "## GÜNCEL ORAN TEYİDİ" in txt
    blok = txt[txt.index("## GÜNCEL ORAN TEYİDİ"):txt.index("## Aktif çıkarım refleksi")]
    for k in ("oran\nÜRETMEZ", "3095 m.1", "7589", "31.07.2026", "--oranlar", "teyit_tarihi",
              "KAYNAKSIZ/TARİHSİZ", "PROJEKSİYON", "exit 2", "exit 1", "TEYİT BEKLİYOR"):
        assert k in blok or k.replace("\n", " ") in blok.replace("\n", " "), k
    merci = txt[txt.index("**Merci (v0.5.18"):txt.index("## GÜNCEL ORAN TEYİDİ")]
    for k in ("--merci", "harc_merci", "Seri No:98", "AAÜT m.13/1", "--olum-cismani", "m.28/a", "AAÜT m.21"):
        assert k in merci or k in merci.replace("\n  ", " "), k


# ═══════════════════════ tarife tazeliği ve tutarlılığı (Fable karşı-tezi) ═══

def test_tarife_teyit_tarihi_yildan_cok_eskiyse_BAYAT():
    with pytest.raises(MOD.TarifeHatasi):
        MOD.tarife_teyit_kontrol(_sentetik(mcp_teyit_tarihi="2024-12-31"), 2026)
    MOD.tarife_teyit_kontrol(_sentetik(mcp_teyit_tarihi="2025-12-31"), 2026)   # önceki yıl sonu kabul


def test_harc_merci_teyidi_yururlukten_cok_once_ise_teyitsiz():
    gecerli, neden = MOD.merci_blogu_gecerli(_sentetik(harc_merci={"teyit_tarihi": "2025-10-01"}))
    assert not gecerli and "çok önce" in neden
    assert MOD.merci_blogu_gecerli(_sentetik(harc_merci={"teyit_tarihi": "2025-12-31"}))[0]


def test_tarife_ici_basvuru_harci_tutarsizligi_kismi(tmp_path):
    t = _sentetik()
    t["harc_merci"]["kalemler"]["asliye_idare_basvuru"] = {"tutar": 120.0, "satir": "sentetik A-I-2"}
    s = MOD.hesapla(100000, 1.0, t)
    assert any("tarife tutarsız" in e for e in s["eksik_alanlar"])
    rc, out, _ = _cli("--deger", "100000", "--tarife", _yaz(tmp_path, t), "--yil", "2026")
    assert rc == 2 and "tarife tutarsız" in out
    t["harc_merci"]["kalemler"]["asliye_idare_basvuru"]["tutar"] = 100.0
    assert not any("tutarsız" in e for e in MOD.hesapla(100000, 1.0, t)["eksik_alanlar"])
    assert GERCEK["harc"]["basvuru_maktu"] == GERCEK["harc_merci"]["kalemler"]["asliye_idare_basvuru"]["tutar"]


def test_vergi_hukum_degeri_harci_TEYIT_BEKLIYOR(tmp_path):
    s = MOD.hesapla(100000, 0.5, _sentetik(), merci="vergi")
    assert s["harc"]["karar_ilam_hukum_degeri"] is None
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.5", "--merci", "vergi",
                      "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026")
    assert "Karar harcı — hüküm altına alınan değer    : TEYİT BEKLİYOR — hesaplanmadı" in out


def test_faiz_raporu_gun_esasi_ve_matrah_notu(tmp_path):
    oran = _oran_dosyasi(tmp_path, [_dilim("2026-08-01", "2026-12-31", 30)])
    rc, out, _ = _cli("--deger", "100000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026",
                      "--faiz-baslangic", "2026-08-01", "--faiz-bitis", "2026-10-01", "--oranlar", oran)
    assert rc == 0 and "artık yılda da 365" in out and "harç matrahına EKLENMEZ" in out


def test_faiz_artik_yil_gunu_gorunur_uyari():
    fz = MOD.faiz_hesapla(36500, dt.date(2028, 2, 1), dt.date(2028, 3, 1),
                          [_dilim("2028-01-01", "2028-12-31", 10)])
    assert any("2028-02-29" in u and "gün/365" in u for u in fz["uyarilar"])
    assert fz["hesaplanan_gun"] == 29 and fz["tutar"] == round(36500 * 0.10 / 365 * 29, 2)
    yok = MOD.faiz_hesapla(36500, dt.date(2026, 2, 1), dt.date(2026, 3, 1), [_dilim("2026-01-01", "2026-12-31", 10)])
    assert not any("artık yıl" in u for u in yok["uyarilar"])


def test_fail_closed_json_istenirse_hata_da_json(tmp_path):
    rc, out, _ = _cli("--deger", "1000", "--tarife", _yaz(tmp_path, _sentetik(yil=2025)), "--yil", "2026", "--json")
    assert rc == 2
    js = json.loads(out[out.index("{"):])
    assert js["durum"] == "FAIL-CLOSED" and js["cikis_kodu"] == 2 and " TL" not in out
    rc, out, _ = _cli("--deger", "1000", "--tarife", _yaz(tmp_path, _sentetik()), "--yil", "2026", "--json",
                      "--faiz-baslangic", "2026-01-01", "--faiz-bitis", "2026-02-01")
    assert rc == 1 and json.loads(out[out.index("{"):])["durum"] == "FAİZ HESAPLANMADI"
