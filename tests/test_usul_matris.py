# -*- coding: utf-8 -*-
"""Fable-tespitli TESTSİZ release-kapısı scriptlerinden biri olan
oa-usul/scripts/usul_matris.py için KARAKTERİZASYON testleri.

Bu dosya KARAKTERİZASYON testidir: scriptin MEVCUT davranışını olduğu gibi
KİLİTLER, değiştirmez. Davranış "tuhaf" görünse bile mevcut hali test edilir
ve ilgili testin docstring'inde "karakterizasyon — mevcut tasarım" diye
belgelenir.

Kilitlenen dikkat çekici mevcut davranışlar:
  * `--ornek` şablonu KENDİ denetiminden TEMİZ geçer (exit 0, "✓ Boşluk yok").
  * [G1] boşluğu `continue` ile işlemin KALAN denetimlerini de atlar — aynı
    işlemde belgesiz kesin_dil olsa bile [G4] üretilmez.
  * Karşı tarafın fiili_tarih'i hiç yoksa yalnız BULGU üretilir ("işlem HİÇ
    yapılmamış görünüyor"), boşluk değil → muhtemel kaçırmaya rağmen exit 0.
  * Boş "islemler" listesi (hatta boş girdi sözlüğü) temiz sayılır → exit 0.
  * Girdi dosyası yoksa veya JSON bozuksa script yakalanmamış istisna ile
    ÇÖKER (returncode 1 + traceback) — mevcut tasarım.
  * Girdisiz çağrı argparse error → exit 2.
  * Yakın zamanda eklenen opsiyonel --json bayrağı, bayraksız ESKİ yüzeyi
    değiştirmemiştir: buradaki tüm --girdi senaryoları bayraksız koşar ve
    eski çıktı/exit sözleşmesini doğrular (--json'ın kendisi ayrı dosyada
    test edilir).

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; repo dosyalarına
dokunulmaz.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-usul"
          / "scripts" / "usul_matris.py")


def _cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def _girdi_yaz(veri):
    """Veriyi izole bir temp dizine dosya_usul.json olarak yazar, yolu döner."""
    kok = pathlib.Path(tempfile.mkdtemp())
    yol = kok / "dosya_usul.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _denetle(islemler):
    yol = _girdi_yaz({"dosya": "Test 2026/999", "islemler": islemler})
    cp = _cli("--girdi", str(yol))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _karsi_kacirma(**ek):
    """Karşı tarafın süreyi +5 gün kaçırdığı taban işlem (G2 zemini)."""
    i = {"id": "I1", "taraf": "karsi", "islem": "istinaf",
         "sure_kurali": "hmk_istinaf",
         "teblig": "2026-04-01", "teblig_belgeli": True,
         "son_gun": "2026-04-15", "fiili_tarih": "2026-04-20"}
    i.update(ek)
    return i


def _biz_kacirma(**ek):
    """Müvekkilin süreyi +4 gün kaçırdığı taban işlem (G3/G5 zemini)."""
    i = {"id": "I2", "taraf": "biz", "islem": "cevap",
         "teblig": "2026-03-02", "teblig_belgeli": True,
         "son_gun": "2026-03-16", "fiili_tarih": "2026-03-20"}
    i.update(ek)
    return i


def test_script_mevcut():
    assert SCRIPT.is_file(), f"usul_matris.py bulunamadı: {SCRIPT}"


# ── --ornek: şablon çıktısı ─────────────────────────────────────────────────

def test_ornek_sablon_json_parse_edilebilir_ve_islemler_listesi_icerir():
    cp = _cli("--ornek")
    assert cp.returncode == 0
    v = json.loads(cp.stdout)
    assert v["dosya"] == "Örnek 2026/000"
    assert v["yargi_kolu"] == "hukuk"
    assert isinstance(v["islemler"], list) and len(v["islemler"]) == 3
    assert [i["id"] for i in v["islemler"]] == ["I1", "I2", "K1"]
    assert [i["taraf"] for i in v["islemler"]] == ["karsi", "biz", "kamu"]


def test_ornek_sablon_kendi_denetiminden_temiz_gecer_exit0():
    """Karakterizasyon — mevcut tasarım: ÖRNEK şablon boşluksuzdur.

    Ölçüldü ve kilitlendi: --ornek çıktısı --girdi olarak geri verildiğinde
    exit 0 + '✓ Boşluk yok' üretir; iki kaçırma bulgusu, AY m.40/2 adayı ve
    kural-uyumlu kasıt kaydı bulgular arasında raporlanır. Bu koşu aynı
    zamanda yeni --json bayrağının bayraksız eski yüzeyi bozmadığının
    temiz-senaryo doğrulamasıdır.
    """
    ornek = _cli("--ornek")
    yol = _girdi_yaz(json.loads(ornek.stdout))
    cp = _cli("--girdi", str(yol))
    cikti = (cp.stdout or "") + (cp.stderr or "")
    assert cp.returncode == 0, f"örnek şablon temiz geçmeli; çıktı:\n{cikti}"
    assert "✓ Boşluk yok" in cikti
    assert "TESLİM EDİLEMEZ" not in cikti
    assert "oa-usul EKSİKSİZLİK DENETİMİ — Örnek 2026/000" in cikti
    assert "KAÇIRILMIŞ (+5 gün)" in cikti   # I1 karşı istinaf
    assert "KAÇIRILMIŞ (+4 gün)" in cikti   # I2 bizim cevap
    assert "AY m.40/2 İHLALİ adayı" in cikti
    assert "kural uyumlu" in cikti
    assert "kapatılan kapılar" in cikti


# ── G1: tebliğ var, son_gun yok ─────────────────────────────────────────────

def test_g1_teblig_var_son_gun_yok_bosluk_exit1_ve_kalan_denetimler_atlanir():
    """Karakterizasyon — mevcut tasarım: [G1] boşluğu `continue` ile aynı
    işlemin KALAN denetimlerini de atlar; belgesiz kesin_dil=true olmasına
    rağmen [G4] üretilMEZ."""
    kod, cikti = _denetle([{
        "id": "I1", "taraf": "karsi", "islem": "istinaf",
        "teblig": "2026-04-01", "teblig_belgeli": False,
        "kesin_dil": True,
    }])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert "[G1] I1" in cikti and "son_gun yok" in cikti
    assert "oa-sure ile hesapla" in cikti
    assert "[G4]" not in cikti  # continue nedeniyle atlanır — mevcut tasarım


# ── G2a: karşı kaçırma sonuca bağlanmamış / içtihat teyitsiz ────────────────

def test_g2a_karsi_kacirma_sonuc_norm_ve_ictihat_teyit_yok_iki_bosluk_exit1():
    kod, cikti = _denetle([_karsi_kacirma(
        kapi_kapatma=[{"kapi": "K-1 eski hâle getirme", "kapatma": "mazeret yok"}],
    )])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert "[G2a] I1: karşı kaçırma usuli SONUCA bağlanmamış" in cikti
    assert "[G2a] I1: sonucun içtihat teyidi yok" in cikti
    assert "[G2b]" not in cikti  # kapı kapatma verildi, izole G2a
    assert "kapatılan kapılar → K-1 eski hâle getirme" in cikti


def test_g2a_sonuc_norm_var_ama_ictihat_teyit_yok_tek_bosluk_exit1():
    kod, cikti = _denetle([_karsi_kacirma(
        sonuc_norm="HMK m.346 — süreden ret",
        kapi_kapatma=[{"kapi": "K-1", "kapatma": "x"}],
    )])
    assert kod == 1
    assert "SONUCA bağlanmamış" not in cikti
    assert "[G2a] I1: sonucun içtihat teyidi yok" in cikti


# ── G2b: karşı kaçırmada kapı kapatma boş ───────────────────────────────────

def test_g2b_karsi_kacirma_kapi_kapatma_bos_bosluk_exit1():
    kod, cikti = _denetle([_karsi_kacirma(
        sonuc_norm="HMK m.346 — süreden ret", sonuc_ictihat_teyit=True,
    )])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert "[G2b] I1: karşı tarafın kurtuluş KAPILARI KAPATILMAMIŞ" in cikti
    assert "[G2a]" not in cikti


# ── G3: müvekkil hatasında üç kanal + kapı kayıtları ────────────────────────

def test_g3_muvekkil_hatasi_kapi_arastirmasi_hic_yok_dort_bosluk_exit1():
    """kapi_arastirmasi tamamen eksik → üç kanal boşluğu + 'hiç kapı kaydı
    yok' boşluğu birlikte üretilir."""
    kod, cikti = _denetle([_biz_kacirma()])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    for kanal in ("ictihat", "doktrin", "web"):
        assert f"[G3] I2: müvekkil hatasında '{kanal}' kanalı araştırılmamış" in cikti
    assert "[G3] I2: hiç kapı kaydı yok" in cikti
    assert "sahte umut da, sessizlik de yasak" in cikti


def test_g3_g5_kapi_var_ama_norm_teyit_sure_uygulanabilirlik_eksik_exit1():
    kod, cikti = _denetle([_biz_kacirma(
        kapi_arastirmasi={"ictihat": True, "doktrin": True, "web": True,
                          "kapilar": [{"kapi": "K-2 usulsüz tebliğ"}]},
    )])
    assert kod == 1
    assert "[G3] I2/K-2 usulsüz tebliğ: norm Mevzuat MCP teyidi yok" in cikti
    assert "[G5] I2/K-2 usulsüz tebliğ: kapının KENDİ süresi hesaplanmamış" in cikti
    assert "[G3] I2/K-2 usulsüz tebliğ: dürüst uygulanabilirlik değerlendirmesi yok" in cikti
    assert "kanalı araştırılmamış" not in cikti  # üç kanal tam, izole G3/G5


def test_g5_yalniz_kapi_suresi_eksik_tek_bosluk_exit1():
    kod, cikti = _denetle([_biz_kacirma(
        kapi_arastirmasi={"ictihat": True, "doktrin": True, "web": True,
                          "kapilar": [{"kapi": "K-2", "norm_teyit": True,
                                       "uygulanabilirlik": "güçlü"}]},
    )])
    assert kod == 1
    assert "[G5] I2/K-2: kapının KENDİ süresi hesaplanmamış (oa-sure)." in cikti
    assert "[G3]" not in cikti


# ── G4: tebliğ belgesiz + kesin dil ─────────────────────────────────────────

def test_g4_teblig_belgesiz_kesin_dil_bosluk_exit1():
    """G4 kilidi kaçırmadan bağımsızdır: süresinde yapılmış işlemde bile
    belgesiz tebliğ + kesin_dil=true boşluk üretir."""
    kod, cikti = _denetle([{
        "id": "I3", "taraf": "biz", "islem": "cevap",
        "teblig": "2026-03-02", "teblig_belgeli": False,
        "son_gun": "2026-03-16", "fiili_tarih": "2026-03-16",  # SÜRESİNDE
        "kesin_dil": True,
    }])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert "[G4] I3: tebliğ BELGESİZ iken kesin_dil=true" in cikti
    assert "'teyidi kaydıyla' formülüne dön" in cikti
    assert "SÜRESİNDE" in cikti


# ── G6: kamu işlemi unsur denetimi ──────────────────────────────────────────

def test_g6_kamu_unsur_denetimi_hic_yok_bosluk_exit1():
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
    }])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert "[G6] K1 (kamu/idare): unsur denetimi HİÇ yapılmamış" in cikti
    assert "yetki + şekil + AY m.40/2 başvuru-yolu üçlüsü zorunlu" in cikti


def test_g6_kamu_unsur_denetimi_eksik_alanlar_alan_basina_bosluk_exit1():
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
        "unsur_denetimi": {"yetki": True},  # şekil + ay40 soruları eksik
    }])
    assert kod == 1
    assert "[G6] K1: 'şekil' sorusu sorulmamış (unsur_denetimi.sekil eksik)." in cikti
    assert ("[G6] K1: 'AY m.40/2 başvuru yolu' sorusu sorulmamış "
            "(unsur_denetimi.ay40_basvuru_yolu_gosterildi eksik).") in cikti
    assert "'yetki' sorusu sorulmamış" not in cikti


def test_g6_ay40_false_bulgusu_uretilir_aykirilik_tam_ise_temiz_exit0():
    """ay40_basvuru_yolu_gosterildi=false bir BOŞLUK değil BULGU üretir
    (İHLAL adayı + K-12 kapısı); aykırılık kaydı tam ise denetim temiz."""
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
        "unsur_denetimi": {"yetki": True, "sekil": True,
                           "ay40_basvuru_yolu_gosterildi": False},
        "aykiriliklar": [{"aykirilik": "başvuru yolu gösterilmemiş",
                          "niteleme": "AY m.40/2 — süre işlemez",
                          "ictihat_teyit": True, "kapiya_donusturuldu": "K-12"}],
    }])
    assert kod == 0, f"tam aykırılık kaydıyla temiz beklenir; çıktı:\n{cikti}"
    assert "AY m.40/2 İHLALİ adayı" in cikti
    assert "süre-işlemez kapısı (K-12)" in cikti
    assert "✓ Boşluk yok" in cikti


# ── G7: aykırılık niteleme/teyit/kapı zinciri ───────────────────────────────

def test_g7_unsur_aykiriligi_var_ama_aykirilik_kaydi_yok_bosluk_exit1():
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
        "unsur_denetimi": {"yetki": True, "sekil": False,
                           "ay40_basvuru_yolu_gosterildi": True},
    }])
    assert kod == 1
    assert ("[G7] K1: unsur denetimi aykırılık gösteriyor ama 'aykiriliklar' "
            "kaydı yok.") in cikti


def test_g7_aykirilik_niteleme_teyit_kapi_eksik_uc_bosluk_exit1():
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
        "unsur_denetimi": {"yetki": True, "sekil": True,
                           "ay40_basvuru_yolu_gosterildi": True},
        "aykiriliklar": [{"aykirilik": "gerekçe yok"}],
    }])
    assert kod == 1
    assert "[G7] K1/'gerekçe yok': NİTELEME yok" in cikti
    assert "[G7] K1/'gerekçe yok': içtihat teyidi yok (oa-ictihat)." in cikti
    assert "[G7] K1/'gerekçe yok': bir KAPIYA dönüştürülmemiş" in cikti


# ── G8: belgesiz kasıt dili ihtiyat kilidi ──────────────────────────────────

def test_g8_belgesiz_kasit_dili_bosluk_exit1():
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
        "unsur_denetimi": {"yetki": True, "sekil": True,
                           "ay40_basvuru_yolu_gosterildi": True},
        "kasit_deseni": {"var": True, "belgeli": False, "metinde_kasit_dili": True},
    }])
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert ("[G8] K1: kasıt deseni BELGESİZ iken metinde kasıt dili "
            "kullanılmış — yasak") in cikti
    assert "deseni dahili raporda tut" in cikti


def test_g8_kasit_belgesiz_ama_metin_objektif_ise_kural_uyumlu_bulgu_exit0():
    kod, cikti = _denetle([{
        "id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası",
        "unsur_denetimi": {"yetki": True, "sekil": True,
                           "ay40_basvuru_yolu_gosterildi": True},
        "kasit_deseni": {"var": True, "belgeli": False, "metinde_kasit_dili": False},
    }])
    assert kod == 0
    assert "belgeli=False" in cikti
    assert "metin dili=objektif aykırılık (kural uyumlu)" in cikti
    assert "✓ Boşluk yok" in cikti


# ── kaçırma dışı yollar: süresinde / fiili yok / boş girdi ──────────────────

def test_suresinde_islemde_g2_g3_denetimi_yapilmaz_exit0():
    kod, cikti = _denetle([_karsi_kacirma(fiili_tarih="2026-04-10")])  # fark<=0
    assert kod == 0
    assert "SÜRESİNDE" in cikti
    assert "[G2a]" not in cikti and "[G2b]" not in cikti
    assert "✓ Boşluk yok" in cikti


def test_karsi_fiili_tarih_yoksa_yalniz_bulgu_bosluk_degil_exit0():
    """Karakterizasyon — mevcut tasarım: karşı tarafın işlemi HİÇ yapılmamış
    görünse (fiili_tarih yok) yalnız bulgu üretilir, boşluk üretilmez;
    muhtemel kaçırmaya rağmen exit 0."""
    kod, cikti = _denetle([{
        "id": "I1", "taraf": "karsi", "islem": "istinaf",
        "teblig": "2026-04-01", "teblig_belgeli": True,
        "son_gun": "2026-04-15",
    }])
    assert kod == 0
    assert "işlem HİÇ yapılmamış görünüyor" in cikti
    assert "dolduysa kaçırma; teyit et" in cikti
    assert "✓ Boşluk yok" in cikti


def test_bos_islemler_listesi_temiz_sayilir_exit0():
    """Karakterizasyon — mevcut tasarım: hiç işlem kaydı olmayan girdi de
    'boşluksuz' sayılır ve exit 0 verir."""
    kod, cikti = _denetle([])
    assert kod == 0
    assert "✓ Boşluk yok" in cikti
    assert "oa-usul EKSİKSİZLİK DENETİMİ — Test 2026/999" in cikti


# ── bozuk/eksik girdi: çöküş karakterizasyonu ───────────────────────────────

def test_girdisiz_cagri_argparse_error_exit2():
    cp = _cli()
    assert cp.returncode == 2
    assert "usage" in cp.stderr
    assert "--girdi dosya.json" in cp.stderr


def test_olmayan_girdi_dosyasi_traceback_ile_coker_exit1():
    """Karakterizasyon — mevcut tasarım: var olmayan girdi dosyasında script
    dostane hata vermez, FileNotFoundError traceback'i ile çöker."""
    yok = pathlib.Path(tempfile.mkdtemp()) / "yok.json"
    cp = _cli("--girdi", str(yok))
    assert cp.returncode == 1
    assert "Traceback" in cp.stderr
    assert "FileNotFoundError" in cp.stderr


def test_bozuk_json_girdi_traceback_ile_coker_exit1():
    """Karakterizasyon — mevcut tasarım: bozuk JSON'da yakalanmamış
    JSONDecodeError traceback'i ile çöküş."""
    kok = pathlib.Path(tempfile.mkdtemp())
    yol = kok / "bozuk.json"
    yol.write_text("{ gecersiz json", encoding="utf-8")
    cp = _cli("--girdi", str(yol))
    assert cp.returncode == 1
    assert "Traceback" in cp.stderr
    assert "JSONDecodeError" in cp.stderr
