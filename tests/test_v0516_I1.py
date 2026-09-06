# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP I1: oa-strateji + oa-interview.

Kapsanan denetim bulguları:
  P1-1 / A-19   KORUMA TEDBİRİ 0. adımı (İİK m.257 vd., HMK m.389 vd.; tamamlayıcı
                süreler İİK m.264 / HMK m.397 → oa-sure/hesapla_sure yönlendirmesi;
                sure_kurallari.json'a kural EKLENMEZ — yalnız çıpa)
  P1-2 / A-16 / A-17 / A-6   ZAMAN EKSENİ (nitel bant + kat sayısı; SAYI/YIL yok;
                "bugün X vs N kat sonra Y" şablonu) + risk toleransı / masraf gücü
                girdisi olmadan yol kararı yok («Müvekkil Kararı Bekleyen»)
  A-5           oa-interview: muhatap AVUKATTIR; her cevap belgeli|beyan statüsü;
                müvekkil anlatısı belge gelene kadar İDDİA
  P2-3 / A-8 / A-9   USUL ZAMANLAMA: tamamlanabilir vs tamamlanamaz kusur; usul
                kazanımının gecikme maliyeti AYRI satır; "1. satır" ilanı korunur
  P1-11 / A-18  DETERMİNİSTİK MALİYET CETVELİ: scripts/maliyet_cetveli.py +
                scripts/tarife.json; teyitsiz/bayat tarifede FAIL-CLOSED exit 2;
                sentetik tarifeyle aritmetik; olasılık üretmez

Norm metinleri Mevzuat MCP'den okundu (2026-09-06): İİK m.257, 258, 259, 264;
HMK m.20, 115, 119, 323, 326, 389, 392, 397; 492 s.K. m.15, 16, 28, 30 ve
(1) sayılı tarife 2026 tutarları (Harçlar K. Genel Tebliği Seri No:98, RG
31.12.2025/33124 5. mükerrer); AAÜT RG 04.11.2025/33067 genel hükümler.

Tüm fikstürler sentetiktir; testler tmp_path'te koşar, depo dosyasına yazmaz.
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
STRATEJI = SKILLS / "oa-strateji"
INTERVIEW = SKILLS / "oa-interview"
SCRIPT = STRATEJI / "scripts" / "maliyet_cetveli.py"
TARIFE = STRATEJI / "scripts" / "tarife.json"
STRATEJI_MD = STRATEJI / "SKILL.md"
STRATEJI_README = STRATEJI / "README.md"
INTERVIEW_MD = INTERVIEW / "SKILL.md"
SORU_BANKASI = INTERVIEW / "references" / "soru-bankasi.md"
SURE_KURALLARI = SKILLS / "oa-sure" / "scripts" / "sure_kurallari.json"


def _oku(yol):
    return yol.read_text(encoding="utf-8")


def _load():
    spec = importlib.util.spec_from_file_location("maliyet_cetveli_v0516", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )
    return cp.returncode, cp.stdout, cp.stderr


def _sentetik_tarife(**degisiklik):
    """Tam dolu SENTETİK tarife (gerçek tarife DEĞİL — aritmetik sınavı için
    yuvarlak sayılar). Anahtarlar şemayla birebir."""
    t = {
        "yil": 2026,
        "mcp_teyit_tarihi": "2026-09-06",
        "kaynak": "SENTETİK TEST TARİFESİ — gerçek değer değildir",
        "harc": {"basvuru_maktu": 100.0, "karar_ilam_nispi_binde": 50.0,
                 "pesin_oran": 0.25, "nispi_asgari": 200.0,
                 "istinaf_basvuru_maktu": 300.0, "temyiz_basvuru_maktu": 400.0,
                 "kesif": 500.0},
        "aaut": {"maktu_asliye": 1000.0,
                 "nispi_dilimler": [{"ust": 50000, "yuzde": 10},
                                    {"ust": None, "yuzde": 5}]},
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


# ═══════════════════════════════════════════════════════════════════════════
# P1-11 / A-18 — tarife.json şeması ve SAYI UYDURMA YASAĞI
# ═══════════════════════════════════════════════════════════════════════════

def test_P1_11_tarife_json_var_ve_sema_yil_damgali():
    veri = json.loads(_oku(TARIFE))
    for k in ("yil", "mcp_teyit_tarihi", "kaynak", "harc", "aaut"):
        assert k in veri, f"tarife.json şema dışı: '{k}' yok"
    assert isinstance(veri["yil"], int)
    for k in ("basvuru_maktu", "karar_ilam_nispi_binde", "pesin_oran"):
        assert k in veri["harc"], f"harc.{k} anahtarı yok (null olabilir ama anahtar şart)"
    for k in ("maktu_asliye", "nispi_dilimler"):
        assert k in veri["aaut"]
    assert isinstance(veri["aaut"]["nispi_dilimler"], list)


def test_P1_11_tarife_json_teyitsiz_alan_null_teyitli_alan_kaynakli():
    """SAYI UYDURMA YASAK: teyit tarihi doluysa 'kaynak' resmî kaynağı adıyla
    anmalı; sayısal alan ya sayı ya null (dizge/yorum sayı olamaz)."""
    veri = json.loads(_oku(TARIFE))
    if veri["mcp_teyit_tarihi"]:
        assert re.match(r"\d{4}-\d{2}-\d{2}$", veri["mcp_teyit_tarihi"])
        assert "492" in veri["kaynak"] and ("Resmî Gazete" in veri["kaynak"]
                                            or "RG" in veri["kaynak"])
    for blok in ("harc", "aaut"):
        for k, v in veri[blok].items():
            if k.startswith("_") or k in ("nispi_dilimler", "rg"):
                continue
            assert v is None or isinstance(v, (int, float)), f"{blok}.{k}: sayı ya da null olmalı"


def test_P1_11_script_ici_parasal_sabit_yok():
    """Script HİÇBİR tarife rakamını gövdesinde taşımaz (tek kaynak tarife.json).
    Bilinen 2026 değerleri ve 'binde 68' kalıbı kaynakta geçemez."""
    src = _oku(SCRIPT)
    for yasak in ("732", "68.31", "68,31", "1206", "2002", "3608"):
        assert yasak not in src, f"script gövdesinde tarife rakamı gömülü: {yasak}"


# ═══════════════════════════════════════════════════════════════════════════
# FAIL-CLOSED — bayat / teyitsiz tarife → exit 2, rakam yok
# ═══════════════════════════════════════════════════════════════════════════

def test_A18_bayat_tarife_yil_uyusmazligi_exit_2(tmp_path):
    yol = _yaz(tmp_path, _sentetik_tarife(yil=2025))
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.6", "--tarife", yol, "--yil", "2026")
    assert rc == 2, out
    assert "TARİFE TEYİTSİZ/BAYAT — hesap yapılmadı" in out
    assert "Başvurma harcı" not in out and " TL" not in out, "bayat tarifeyle rakam basıldı"


def test_A18_bos_teyit_tarihi_exit_2(tmp_path):
    yol = _yaz(tmp_path, _sentetik_tarife(mcp_teyit_tarihi=""))
    rc, out, _ = _cli("--deger", "100000", "--tarife", yol, "--yil", "2026")
    assert rc == 2
    assert "TARİFE TEYİTSİZ/BAYAT" in out and " TL" not in out


def test_A18_bozuk_teyit_tarihi_exit_2(tmp_path):
    yol = _yaz(tmp_path, _sentetik_tarife(mcp_teyit_tarihi="dün"))
    rc, out, _ = _cli("--deger", "100000", "--tarife", yol, "--yil", "2026")
    assert rc == 2 and "TARİFE TEYİTSİZ/BAYAT" in out


def test_A18_tarife_dosyasi_yok_veya_bozuk_json_exit_2(tmp_path):
    rc, out, _ = _cli("--deger", "100000", "--tarife", str(tmp_path / "yok.json"), "--yil", "2026")
    assert rc == 2 and "FAIL-CLOSED" in out
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text("{yil: 2026", encoding="utf-8")
    rc, out, _ = _cli("--deger", "100000", "--tarife", str(bozuk), "--yil", "2026")
    assert rc == 2 and "FAIL-CLOSED" in out


def test_A18_sema_disi_tarife_exit_2(tmp_path):
    veri = _sentetik_tarife()
    del veri["aaut"]
    yol = _yaz(tmp_path, veri)
    rc, out, _ = _cli("--deger", "100000", "--tarife", yol, "--yil", "2026")
    assert rc == 2 and "şema dışı" in out


def test_A18_eksik_kalem_kismi_cetvel_exit_2(tmp_path):
    """aaut.maktu_asliye null → karşı vekâlet 'hesaplanmadı', harç satırları
    basılır, exit 2 (kısmi cetvel; sessiz atlama yok)."""
    yol = _yaz(tmp_path, _sentetik_tarife(aaut={"maktu_asliye": None}))
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.6", "--tarife", yol, "--yil", "2026")
    assert rc == 2
    assert "TEYİTSİZ (tarife alanı null) — hesaplanmadı" in out
    assert "aaut.maktu_asliye" in out
    assert "Başvurma harcı (maktu)                    : 100,00 TL" in out


# ═══════════════════════════════════════════════════════════════════════════
# ARİTMETİK — sentetik tarifeyle deterministik sonuç
# ═══════════════════════════════════════════════════════════════════════════

def test_P1_11_aritmetik_kismi_kabul_0_6():
    """deger 100.000; binde 50 → karar harcı 5.000; peşin 1/4 → 1.250; başvuru 100;
    açılış 1.350. kabul 60.000 / ret 40.000. Dilim: ilk 50.000 %10, üstü %5 →
    lehe nispi 5.000+500=5.500; aleyhe nispi(40.000)=4.000 (maktu 1.000 tabanı
    üstünde, ret 40.000 ve lehe 5.500 tavanı altında) → 4.000."""
    s = MOD.hesapla(100000, 0.6, _sentetik_tarife())
    h, kv = s["harc"], s["karsi_vekalet"]
    assert h["basvuru_maktu"] == 100.0
    assert h["karar_ilam_dava_degeri"] == 5000.0
    assert h["karar_ilam_pesin"] == 1250.0
    assert h["karar_ilam_hukum_degeri"] == 3000.0
    assert h["dava_acilis_toplam"] == 1350.0
    assert kv["lehe_kabul_kismi"] == 5500.0
    assert kv["aleyhe_ret_kismi"] == 4000.0
    assert s["eksik_alanlar"] == []
    # gider bandı: alt = açılış; üst = başvuru + tam karar + keşif + istinaf + temyiz + aleyhe
    assert s["gider_bandi"]["alt"] == 1350.0
    assert s["gider_bandi"]["ust"] == 100 + 5000 + 500 + 300 + 400 + 4000


def test_P1_11_tam_kabul_aleyhe_sifir_tam_ret_maktu():
    tam = MOD.hesapla(100000, 1.0, _sentetik_tarife())
    assert tam["karsi_vekalet"]["aleyhe_ret_kismi"] == 0.0
    assert tam["karsi_vekalet"]["lehe_kabul_kismi"] == 7500.0   # 50.000×%10 + 50.000×%5
    ret = MOD.hesapla(100000, 0.0, _sentetik_tarife())
    assert ret["karsi_vekalet"]["aleyhe_ret_kismi"] == 1000.0, "tam ret → maktu (AAÜT m.13/4)"
    assert ret["karsi_vekalet"]["lehe_kabul_kismi"] == 0.0


def test_P1_11_maktu_taban_ve_ret_tavani():
    """Küçük ret: nispi 5.000×%10=500 < maktu 1.000 → 1.000 (m.13/1); ama ret
    miktarı 5.000'i geçemez (m.13/2) → 1.000. Çok küçük ret 500: taban 1.000 >
    ret 500 → tavan 500."""
    s = MOD.hesapla(100000, 0.95, _sentetik_tarife())
    assert s["karsi_vekalet"]["aleyhe_ret_kismi"] == 1000.0
    s2 = MOD.hesapla(100000, 0.995, _sentetik_tarife())
    assert s2["karsi_vekalet"]["aleyhe_ret_kismi"] == 500.0


def test_P1_11_nispi_asgari_had_uygulanir():
    """deger 1.000 → binde 50 = 50 < asgari 200 → 200."""
    s = MOD.hesapla(1000, 1.0, _sentetik_tarife())
    assert s["harc"]["karar_ilam_dava_degeri"] == 200.0
    assert s["harc"]["karar_ilam_pesin"] == 50.0


def test_P1_11_nispi_ucret_dilim_fonksiyonu():
    d = [{"ust": 50000, "yuzde": 10}, {"ust": 100000, "yuzde": 8}, {"ust": None, "yuzde": 5}]
    assert MOD.nispi_ucret(30000, d) == 3000.0
    assert MOD.nispi_ucret(50000, d) == 5000.0
    assert MOD.nispi_ucret(120000, d) == 5000.0 + 4000.0 + 1000.0
    assert MOD.nispi_ucret(120000, []) is None


def test_P1_11_cli_tam_hesap_exit_0_ve_json(tmp_path):
    yol = _yaz(tmp_path, _sentetik_tarife())
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.6", "--tarife", yol,
                      "--yil", "2026", "--bilirkisi", "1000", "--json")
    assert rc == 0, out
    assert "DAVA AÇILIŞ TOPLAMI (başvuru + peşin)      : 1.350,00 TL" in out
    assert "ALEYHE (reddedilen kısım — müvekkil öder)  : 4.000,00 TL" in out
    js = json.loads(out[out.index("{"):])
    assert js["gider_bandi"]["alt"] == 2350.0
    assert js["girdi"]["bilirkisi"] == 1000.0


def test_P1_11_olasilik_uretmez(tmp_path):
    """Çıktıda yüzde işareti ve 'kazanma şansı' rakamı YOK; 'olasılık' yalnız
    'ÜRETMEZ' cümlesinde geçer."""
    yol = _yaz(tmp_path, _sentetik_tarife())
    rc, out, _ = _cli("--deger", "100000", "--kismi-kabul", "0.6", "--tarife", yol, "--yil", "2026")
    assert rc == 0
    assert "%" not in out
    assert "ÜRETMEZ" in out
    for satir in out.splitlines():
        if "olasılık" in satir.lower():
            assert "ÜRETMEZ" in satir, satir


def test_P1_11_gecersiz_girdi_exit_1(tmp_path):
    yol = _yaz(tmp_path, _sentetik_tarife())
    assert _cli("--deger", "-5", "--tarife", yol, "--yil", "2026")[0] == 1
    assert _cli("--deger", "100", "--kismi-kabul", "1.5", "--tarife", yol, "--yil", "2026")[0] == 1


def test_P1_11_help_exit_0_ve_utf8_guard():
    rc, out, _ = _cli("--help")
    assert rc == 0 and "--kismi-kabul" in out
    src = _oku(SCRIPT)
    assert "__OA_UTF8_GUARD__" in src
    assert not re.search(r"^\s*(?:from|import)\s+(requests|httpx|urllib|socket)", src, re.M)


def test_P1_11_depo_tarifesi_bugunku_yilla_dogru_davranir():
    """Depodaki gerçek tarife.json: teyit tarihi doluysa ve yıl uyuyorsa —
    aaut null ise kısmi cetvel (exit 2, harç satırları var), aaut doluysa exit 0.
    Teyit boşsa exit 2 ve rakam yok. Hangi dal olursa olsun SESSİZ başarı yok."""
    veri = json.loads(_oku(TARIFE))
    rc, out, _ = _cli("--deger", "250000", "--kismi-kabul", "0.6", "--yil", str(veri["yil"]))
    if not veri["mcp_teyit_tarihi"]:
        assert rc == 2 and "TARİFE TEYİTSİZ/BAYAT" in out
        return
    eksik = [k for k in ("basvuru_maktu", "karar_ilam_nispi_binde", "pesin_oran")
             if veri["harc"].get(k) is None]
    if eksik:
        assert rc == 2 and "hesaplanmadı" in out
        return
    assert "Başvurma harcı (maktu)" in out and "hesap yapılmadı" not in out
    if veri["aaut"]["maktu_asliye"] is None or not veri["aaut"]["nispi_dilimler"]:
        assert rc == 2 and "aaut." in out and "hesaplanmadı" in out
    else:
        assert rc == 0, out


def test_P1_11_depo_tarifesi_gelecek_yil_bayat_sayilir():
    veri = json.loads(_oku(TARIFE))
    rc, out, _ = _cli("--deger", "1000", "--yil", str(veri["yil"] + 1))
    assert rc == 2 and "TARİFE TEYİTSİZ/BAYAT" in out and " TL" not in out


# ═══════════════════════════════════════════════════════════════════════════
# P1-1 / A-19 — oa-strateji: KORUMA TEDBİRİ 0. ADIM (çıpa; kural EKLENMEZ)
# ═══════════════════════════════════════════════════════════════════════════

def test_P1_1_koruma_tedbiri_sifirinci_adim_var():
    txt = _oku(STRATEJI_MD)
    assert "0. **KORUMA TEDBİRİ gerekli mi?" in txt
    assert txt.index("0. **KORUMA TEDBİRİ") < txt.index("1. **Müvekkilin gerçek hedefi")
    for norm in ("İİK m.257", "İİK m.264", "HMK m.389", "HMK m.397", "m.259", "m.392"):
        assert norm in txt, f"{norm} çıpası yok"
    assert "Mevzuat MCP teyit 2026-09-06" in txt
    assert "yedi gün" in txt and "iki hafta" in txt
    assert "hesapla_sure.py" in txt
    assert "Haklı olmak ≠ tahsil etmek" in txt


def test_P1_1_sure_kurallari_jsona_kural_eklenmedi():
    """oa-sure alanı (I5) — bu grup sure_kurallari.json'a DOKUNMAZ; SKILL bunu
    açıkça 'yalnız çıpa' diye yazar. Dosya HEAD ile aynı olmalı."""
    txt = _oku(STRATEJI_MD)
    assert "sure_kurallari.json" in txt and "eklenmez" in txt.lower()
    cp = subprocess.run(["git", "-C", str(REPO), "diff", "--quiet", "HEAD", "--",
                         str(SURE_KURALLARI.relative_to(REPO)).replace("\\", "/")],
                        capture_output=True)
    assert cp.returncode == 0, "sure_kurallari.json değişmiş — I1 grubunun alanı değil"


# ═══════════════════════════════════════════════════════════════════════════
# P1-2 / A-16 / A-17 / A-6 — ZAMAN EKSENİ + risk toleransı + masraf gücü kapısı
# ═══════════════════════════════════════════════════════════════════════════

def test_P1_2_zaman_ekseni_bolumu_nitel_bant_ve_kat_sayisi():
    txt = _oku(STRATEJI_MD)
    assert "## ZAMAN EKSENİ" in txt
    blok = txt[txt.index("## ZAMAN EKSENİ"):txt.index("## USUL ZAMANLAMA")]
    assert "SAYI/YIL ÜRETİLMEZ" in blok
    for b in ("kısa", "orta", "uzun", "1 kat", "2 kat", "3 kat"):
        assert b in blok
    assert "Bugün X" in blok and "N kat sonra Y" in blok and "faiz" in blok and "erime" in blok
    # sayısal süre iddiası yok (ör. "2 yıl", "18 ay")
    assert not re.search(r"\b\d+\s*(?:yıl|ay)\b", blok), "ZAMAN EKSENİ bloğunda sayısal süre iddiası var"


def test_A6_A17_risk_toleransi_ve_masraf_gucu_girdisiz_yol_karari_yok():
    txt = _oku(STRATEJI_MD)
    assert "Risk toleransı" in txt and "kaçınan | nötr | alan" in txt
    assert "Masraf gücü" in txt and "karşı vekâlet" in txt.lower() and "teminat" in txt.lower()
    assert "yol\n     kararı verilmez" in txt or "yol kararı verilmez" in txt.replace("\n     ", " ")
    assert "Müvekkil Kararı Bekleyen" in txt


# ═══════════════════════════════════════════════════════════════════════════
# P2-3 / A-8 / A-9 — USUL ZAMANLAMA (strateji tarafı)
# ═══════════════════════════════════════════════════════════════════════════

def test_P2_3_usul_zamanlama_tamamlanabilir_vs_tamamlanamaz_ve_gecikme_satiri():
    txt = _oku(STRATEJI_MD)
    assert "## USUL ZAMANLAMA" in txt
    blok = txt[txt.index("## USUL ZAMANLAMA"):txt.index("## DETERMİNİSTİK MALİYET CETVELİ")]
    assert "TAMAMLANABİLİR" in blok and "TAMAMLANAMAZ" in blok
    for norm in ("492 s.K. m.30", "HMK m.119/2", "HMK m.115", "HMK m.20"):
        assert norm in blok, f"{norm} çıpası yok"
    # Vekâletname eksiği m.119/2'nin değil m.77/1'in konusudur (2026-09-07 yeniden
    # teyitte düzeltildi): m.119/2 dilekçe İÇERİK eksiğidir; m.77 vekâletname ibrazı.
    duz = blok.replace("\n  ", " ")
    assert "m.77/1" in duz, "vekâletname eksiği için HMK m.77/1 çıpası yok"
    assert "vekâletname/dilekçe eksiği (HMK m.119/2" not in duz, \
        "vekâletname eksiği yanlış maddeye (m.119/2) bağlanmış"
    assert "görevsizlik" in blok.lower() and "yetkisizlik" in blok.lower()
    assert "sıfırdan" in blok
    assert "1. satır" in blok
    assert "hız\n  hedefli" in blok or "hız hedefli" in blok.replace("\n  ", " ")
    assert "avukat kararıdır" in blok
    assert "oa-usul" in blok
    # tabloda AYRI satır ilanı
    assert "AYRI" in blok


def test_P2_3_maliyet_fayda_tablosunda_usul_zamanlama_satiri_ve_bir_satir_ilani_korundu():
    txt = _oku(STRATEJI_MD)
    assert "Usul zamanlama satırı (P2-3)" in txt
    assert "maliyet-fayda tablosunun İLK satırıdır" in txt, "anayasal 1. satır ilanı silinmiş"
    # KUSUR→SONUÇ→TALEP asimetrisi korunur (test_skill_doktrin ile uyum)
    assert "GİDERİLMESİNE" in txt and "KURULMAZ" in txt


# ═══════════════════════════════════════════════════════════════════════════
# P1-11 — SKILL/README script bağlantısı
# ═══════════════════════════════════════════════════════════════════════════

def test_P1_11_skill_ve_readme_scripti_anar():
    txt = _oku(STRATEJI_MD)
    assert "scripts/maliyet_cetveli.py" in txt and "scripts/tarife.json" in txt
    assert "TARİFE TEYİTSİZ/BAYAT" in txt and "exit 2" in txt
    assert "olasılık üretmez" in txt.lower()
    readme = _oku(STRATEJI_README)
    assert "maliyet_cetveli.py" in readme and "tarife.json" in readme
    assert "deterministik script içermez" not in readme


# ═══════════════════════════════════════════════════════════════════════════
# A-5 — oa-interview: muhatap AVUKAT; belgeli|beyan statüsü; İDDİA
# ═══════════════════════════════════════════════════════════════════════════

def test_A5_interview_muhatap_avukat_ve_cevap_statusu():
    txt = _oku(INTERVIEW_MD)
    assert "Muhatap AVUKATTIR" in txt
    assert "`belgeli`" in txt and "`beyan`" in txt
    assert "belgeli|beyan" in txt
    assert "İDDİA" in txt
    assert "oa-vakia" in txt and "kismi_destek" in txt
    assert "fail-closed" in txt.lower()


def test_A5_muvekkile_yansit_ifadeleri_duzeltildi():
    """BİLİNÇLİ karakterizasyon değişikliği (A-5): eski metin mülakatın
    muhatabını müvekkil sayıyordu ('müvekkile yansıt', 'Müvekkilin zaten verdiği
    bilgiyi tekrar sorma', 'müvekkil hemen düzeltsin', 'Müvekkil onayından').
    Muhatap avukattır; müvekkil anlatısı belge gelene kadar İDDİA'dır."""
    txt = _oku(INTERVIEW_MD)
    for eski in ("müvekkile yansıt", "Müvekkilin **zaten verdiği** bilgiyi tekrar sorma",
                 "müvekkil hemen düzeltsin", "Müvekkil onayından",
                 "müvekkilin cevabına göre", "müvekkille gidip gelen",
                 "müvekkile erkenden aktif değer"):
        assert eski not in txt, f"eski müvekkil-muhatap ifadesi duruyor: {eski!r}"
    assert "Avukatın **zaten verdiği** bilgiyi tekrar sorma" in txt
    assert "avukat hemen düzeltsin" in txt
    assert "Avukat onayından" in txt
    bank = _oku(SORU_BANKASI)
    assert "müvekkilin zaten verdiğini tekrar sorma" not in bank
    assert "avukatın zaten verdiğini tekrar sorma" in bank


def test_A6_A17_soru_bankasi_ortak_cekirdege_iki_soru():
    bank = _oku(SORU_BANKASI)
    blok = bank[bank.index("## Her alanda ortak çekirdek"):bank.index("## İş hukuku")]
    assert "7. **Masraf gücü" in blok and "8. **Risk toleransı" in blok
    for k in ("harç", "bilirkişi", "teminat", "karşı vekâlet", "kaçınan | nötr | alan",
              "müvekkil kararı bekleyen", "maliyet_cetveli.py"):
        assert k in blok.lower(), f"ortak çekirdekte '{k}' yok"
    assert "belgeli|beyan" in bank
    skill = _oku(INTERVIEW_MD)
    assert "MASRAF GÜCÜ" in skill and "RİSK TOLERANSI" in skill


# ═══════════════════════════════════════════════════════════════════════════
# Aile yapı denetimi — yeni script/atıflar aileyi kırmadı
# ═══════════════════════════════════════════════════════════════════════════

def test_aile_dogrula_temiz_I1():
    cp = subprocess.run(
        [sys.executable, str(SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"), str(SKILLS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0 and "AİLE YAPI DENETİMİ TEMİZ" in cp.stdout + cp.stderr, cp.stdout + cp.stderr
