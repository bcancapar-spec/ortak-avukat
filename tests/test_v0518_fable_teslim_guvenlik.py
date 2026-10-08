# -*- coding: utf-8 -*-
"""v0.5.18 — FABLE BAĞIMSIZ DENETİMİ (2026-10-08): teslim/UDF ve güvenlik bulguları.

NEDEN VAR: yedi salt okunur Fable denetçisinin bu alandaki DOĞRULANMIŞ bulguları burada
kilitlenir (her biri ana oturumca yeniden üretildi):
  T1  `npm warn cleanup` UYARI satırı, resmî okuyucunun GERÇEK reddini "YAPILAMADI"ya
      çeviriyordu — bu dalın CI düzeltmesi 2'nin gerilemesi; geçersiz UDF "TESLİME HAZIR"
      olabiliyordu. O imin kapsadığı CI vakası zaten "çıkış kodu > 255" kuralıyla yakalanır.
  T3  Ortam imleri stdout'ta da aranıyordu (düşmanca bir evrakın kısmi çıktısı "oturum"/"ağ"
      sözcüğüyle gerçek reddi örtebilirdi) ve "ağ" sözcük sınırsızdı ("aşağıdaki" ⊃ "ağ").
  T2  Resmî okuyucu doğrulayamayınca html2udf yolu `.DOGRULANMADI` işareti bırakmıyor, teslim
      zinciri de işarete hiç bakmıyordu: belirsizlik yalnız iç içe bir satırda kalıyordu.
  T4  Tazelik denetimi hiç koşamayınca teslim çıktısı sessizdi ("temiz" ile ayırt edilemez).
  P1  Windows'ta `shutil.which`, NoDefaultCurrentDirectoryInExePath yoksa aramaya ÇALIŞMA
      DİZİNİNİ öne koyar; araçlar dava kökünde koşar → karşı tarafın evrakıyla gelen
      `npx.cmd` / `tesseract.bat` / `node.bat` çalıştırılabilirdi (denetçi kanıtladı).
Sentetik veri; ağ yok; npx çağrılmaz.
"""
import ast
import importlib.util
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"
UDF_YAZ = SK / "oa-dilekce" / "scripts" / "udf_yaz.py"
UDF_METIN = SK / "oa-pipeline" / "scripts" / "udf_metin.py"
INGEST = SK / "oa-ingest" / "scripts" / "oa_ingest.py"
KURULUM = SK / "ortak-avukat" / "scripts" / "oa_kurulum.py"
TESLIM = SK / "oa-kontrol" / "scripts" / "teslim_paketi.py"
GUVENLI_COZUMLEYENLER = (UDF_YAZ, UDF_METIN, INGEST, KURULUM)


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def uy():
    return _yukle("_fable_tg_udf_yaz", UDF_YAZ)


@pytest.fixture(scope="module")
def tp():
    return _yukle("_fable_tg_teslim", TESLIM)


def _fn_kaynagi(yol, ad):
    kaynak = yol.read_text(encoding="utf-8")
    for dugum in ast.parse(kaynak).body:
        if isinstance(dugum, ast.FunctionDef) and dugum.name == ad:
            return ast.get_source_segment(kaynak, dugum)
    return None


def _sahte_surec(donus, stderr, stdout=""):
    class _P:
        returncode = donus
    _P.stdout, _P.stderr = stdout, stderr
    return _P()


# ── P1 — çalışma dizinindeki program çalıştırılmaz ─────────────────────────────────────

def test_P1_guvenli_cozumleyici_dort_betikte_ozdes_ve_ciplak_which_kalmadi():
    kaynaklar = {p.name: _fn_kaynagi(p, "_guvenli_which") for p in GUVENLI_COZUMLEYENLER}
    assert all(kaynaklar.values()), "eksik kopya: %s" % [a for a, k in kaynaklar.items() if not k]
    assert len(set(kaynaklar.values())) == 1, "dört kopya ayrıştı — tek kural olmalı"
    for p in GUVENLI_COZUMLEYENLER:
        govde = p.read_text(encoding="utf-8").replace(kaynaklar[p.name], "")
        assert "shutil.which(" not in govde, "%s: program yalnız _guvenli_which ile çözülür" % p.name


def test_P1_calisma_dizinindeki_sahte_npx_calistirilmaz(uy, tmp_path, monkeypatch):
    monkeypatch.delenv("NoDefaultCurrentDirectoryInExePath", raising=False)
    sahte = tmp_path / ("npx.cmd" if os.name == "nt" else "npx")
    sahte.write_text("@echo SAHTE\r\n" if os.name == "nt" else "#!/bin/sh\necho SAHTE\n", encoding="utf-8")
    if os.name != "nt":
        sahte.chmod(0o755)
    monkeypatch.chdir(tmp_path)
    cagrilan = []
    monkeypatch.setattr(uy.subprocess, "run",
                        lambda argv, **k: (cagrilan.append(argv[0]), _sahte_surec(0, "", "metin"))[1])
    uy.npx_ile_udf_oku(str(tmp_path / "x.udf"))
    dizin = os.path.normcase(os.path.abspath(str(tmp_path)))
    assert not any(os.path.normcase(os.path.dirname(os.path.abspath(c))) == dizin for c in cagrilan), \
        "dava kökündeki sahte npx seçildi: %s" % cagrilan


# ── T1 / T3 — resmî okuyucunun reddi ortam hâli sanılmaz ──────────────────────────────────

def test_T1_npm_warn_cleanup_gercek_reddi_ortmez(uy, tmp_path, monkeypatch):
    stderr = ("npm warn cleanup Failed to remove some directories [\nnpm warn cleanup   [Error: EPERM: "
              "operation not permitted, rmdir 'C:\\npm\\cache\\_npx\\x\\node_modules\\zod']\n"
              "Error: content.xml not found in .udf")
    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _sahte_surec(1, stderr))
    r = uy.npx_ile_udf_oku(str(tmp_path / "x.udf"))
    assert r["calisti"] is True and r["basarili"] is False, r
    assert "OKUYAMADI" in r["hata"], r["hata"]


@pytest.mark.parametrize("stdout,stderr", [
    # ortam sözcükleri YALNIZ stdout'ta (belge içeriği) — hüküm stderr'de
    ("# Dilekçe\nOturum açıldı; ağ bağlantısı ve login kaydı...", "Error: invalid UDF structure"),
    # başlatıcı imi YALNIZ stdout'ta
    ("program ya da toplu iş dosyası olarak tanınmıyor", "Error: invalid UDF structure"),
    # 'ağ' sözcük sınırsız eşleşmemeli
    ("", "Hata: dosya bozuk, aşağıdaki girdi okunamadı"),
    ("", "Hata: bağlantı kaydı sağlanamadı — content.xml yok"),
])
def test_T3_imler_yalniz_stderrde_ve_sozcuk_sinirli(uy, tmp_path, monkeypatch, stdout, stderr):
    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _sahte_surec(1, stderr, stdout))
    r = uy.npx_ile_udf_oku(str(tmp_path / "x.udf"))
    assert r["calisti"] is True and r["basarili"] is False, (stderr, r)


@pytest.mark.parametrize("stderr", ["ağ hatası: sunucuya ulaşılamadı", "Hata: ağa bağlanılamadı"])
def test_T3_gercek_ag_hatasi_hala_ortam_hali(uy, tmp_path, monkeypatch, stderr):
    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _sahte_surec(1, stderr))
    r = uy.npx_ile_udf_oku(str(tmp_path / "x.udf"))
    assert r["calisti"] is False, (stderr, r)


# ── T2 — doğrulanamayan UDF görünür kalır ───────────────────────────────────────────────

def test_T2_dogrulanamayan_udf_isaret_birakir_ok_olunca_bayat_isaret_kalkar(uy, tmp_path):
    cikti = tmp_path / "dilekce.udf"
    cikti.write_bytes(b"PK")
    isaret = uy._dogrulanmadi_isareti_guncelle(
        str(cikti), {"resmi_okuyucu": "YAPILAMADI", "resmi_okuyucu_not": "npx başlatılamadı",
                     "hatalar": []}, "html2udf")
    assert isaret == str(cikti) + ".DOGRULANMADI" and os.path.isfile(isaret), isaret
    metin = pathlib.Path(isaret).read_text(encoding="utf-8")
    assert "html2udf" in metin and "npx başlatılamadı" in metin and "UYAP" in metin, metin
    assert uy._dogrulanmadi_isareti_guncelle(str(cikti), {"resmi_okuyucu": "OK"}, "html2udf") is None
    assert not os.path.exists(str(cikti) + ".DOGRULANMADI"), "OK gelince bayat işaret kalmamalı"


def test_T2_yerel_motor_isareti_372_notunu_korur(uy, tmp_path):
    cikti = tmp_path / "d.udf"
    cikti.write_bytes(b"PK")
    isaret = uy._dogrulanmadi_isareti_guncelle(
        str(cikti), {"resmi_okuyucu": "RET", "resmi_okuyucu_not": "x", "hatalar": []}, "yerel")
    metin = pathlib.Path(isaret).read_text(encoding="utf-8")
    assert "yerel motor" in metin and "372" in metin, metin


def test_T2_teslim_isareti_gorur_ve_sonuc_satirini_niteler(tp, tmp_path):
    udf = tmp_path / "d.udf"
    udf.write_bytes(b"PK")
    assert tp._udf_dogrulanmadi_isareti(str(udf)) is None
    assert tp._teslime_hazir_satiri(None) == "SONUÇ: TESLİME HAZIR"
    (tmp_path / "d.udf.DOGRULANMADI").write_text("x", encoding="utf-8")
    isaret = tp._udf_dogrulanmadi_isareti(str(udf))
    assert isaret and isaret.endswith(".DOGRULANMADI"), isaret
    satir = tp._teslime_hazir_satiri(isaret)
    assert satir.startswith("SONUÇ: TESLİME HAZIR") and "DOĞRULANAMADI" in satir, satir


def test_T2_teslim_akisi_isareti_makbuza_ve_sonuca_baglar():
    kaynak = TESLIM.read_text(encoding="utf-8")
    assert "_teslime_hazir_satiri(" in kaynak.split("def _teslime_hazir_satiri", 1)[1], \
        "teslim akışı sonuç satırını yardımcıdan basmalı"
    assert '"udf_dogrulanmadi_isareti"' in kaynak, "makbuz işareti taşımalı"


# ── T4 — tazelik denetimi koşamazsa görünür ─────────────────────────────────────────────

def test_T4_tazelik_denetimi_kosamayinca_gorunur_temizse_sessiz(tp, capsys):
    tp._tazelik_bolumu_yazdir(None)
    assert "DENETLENEMEDİ" in capsys.readouterr().out
    tp._tazelik_bolumu_yazdir([])
    assert capsys.readouterr().out == ""
    tp._tazelik_bolumu_yazdir(["BAYAT: x — kaynağı değişti"])
    assert "BAYAT: x" in capsys.readouterr().out
