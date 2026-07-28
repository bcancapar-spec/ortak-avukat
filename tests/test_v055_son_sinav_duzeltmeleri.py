# -*- coding: utf-8 -*-
"""v0.5.5 SON SINAV düzeltmeleri — üç "sessizce açık kapı" bulgusunun kilidi.

Bu üç bulgu saldırı senaryosu DEĞİLDİR; iyi niyetli ama aceleci/eksik kurulumlu
normal kullanımda oluşan FAIL-OPEN hâlleridir (bkz. memory/amac-cizgisi.md):

  D1  kunye_ortak.py import edilemiyorsa (yarım kurulum / bozuk cache) cmd_teyit
      eskiden UYARI basıp DEVAM ediyordu → DAMGA çapraz kontrolü sessizce
      atlanıyordu. Kendi P1-12 doktrinimiz "çöken kapı = KAPALI kapı" der.
  D2  Aynı karara ait biri ALEYHE biri LEHE muhakeme kaydı varken denetim temiz
      olanı (LEHE) seçip [OK] veriyordu → salt-ALEYHE karar lehe kılığında
      dilekçeye girebiliyordu (anayasa m.6 ihlali).
  D3  Layer 0 sorgu taraması telefon / e-posta / plaka desenlerini kaçırıyordu →
      müvekkil kimlik verisi dış MCP'ye (Yargı Pro) çıkabiliyordu.
"""
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"


def _load(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hafiza = _load(HAFIZA, "oa_hafiza_v055")
imd = _load(DENETIM, "imd_v055")


# ── D1: kırık kardeş modül ⇒ kapı KAPANIR (fail-closed) ─────────────────────

def test_d1_kunye_ortak_import_edilemezse_damga_reddedilir(tmp_path, monkeypatch):
    """kunye_ortak yüklenemiyorken --damga'lı teyit RET etmeli (eskiden UYARI
    basıp devam ediyordu = DAMGA çapraz kontrolü sessizce atlanıyordu)."""
    (tmp_path / "_oa" / "teyit" / "dokum").mkdir(parents=True)
    dokum = tmp_path / "_oa" / "teyit" / "dokum" / "k.md"
    dokum.write_text("Yargıtay 9. HD E. 2021/4444 K. 2021/8888 tam metin: ilke şudur…",
                     encoding="utf-8")

    monkeypatch.setattr(hafiza, "_kunye_ortak_modulu", lambda: None)
    monkeypatch.setattr(sys, "argv", [
        "oa_hafiza.py", "teyit", "--kok", str(tmp_path),
        "--arac", "ictihat_getir",
        "--sorgu", "tasarrufun iptali ivazsız tasarruf",
        "--sonuc", "Yargıtay 9. HD E. 2021/4444 K. 2021/8888",
        "--damga", "LEHE",
        "--ilgili-kisim", "ilke şudur",
        "--bag", "Somut olayda tasarruf ivazsızdır; borç önce doğmuştur; süre içindedir.",
        "--dokum", str(dokum),
    ])
    try:
        hafiza.main()
        basarili = True
    except SystemExit as e:
        basarili = False
        mesaj = str(e.code or "")
    assert not basarili, "kunye_ortak yokken damga vurulabildi — fail-open!"
    assert "FAIL-CLOSED" in mesaj and "kunye_ortak" in mesaj, mesaj


# ── D2: çelişen damga sınıf-ötesiyse ⇒ BLOK ─────────────────────────────────

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678"
TASLAK = f"Somut olayda {KUNYE} sayılı karar uygulanmalıdır.\n"


def _kayit(yol, damga, ad):
    (yol / f"{ad}-ictihat-muhakeme.md").write_text(
        "\n".join([
            "# İçtihat Muhakeme Kaydı", "",
            f"**KUNYE:** {KUNYE}",
            "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
            f"**DAMGA:** {damga}", "",
            "## İLGİLİ-KISIM", "kararın taşıyıcı ilkesi burada…", "",
            "## DAVAYA-BAĞ", "somut olayla üç noktada örtüşür…", "",
            "## AYIRT-ETME", "", "",
        ]), encoding="utf-8")


def _iskelet(tmp_path):
    (tmp_path / "_oa" / "teyit" / "dokum").mkdir(parents=True)
    (tmp_path / "_oa" / "cikti").mkdir(parents=True)
    (tmp_path / "_oa" / "teyit" / "dokum" / "kaynak.md").write_text(
        f"{KUNYE} sayılı kararın tam metni…\n", encoding="utf-8")
    (tmp_path / "taslak.md").write_text(TASLAK, encoding="utf-8")


def _cli(tmp_path):
    cp = subprocess.run(
        [sys.executable, str(DENETIM), "taslak.md", "--kok", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(tmp_path))
    return cp.returncode, cp.stdout + cp.stderr


def test_d2_aleyhe_lehe_celiskisi_lehe_secilemez_blok(tmp_path):
    """ALEYHE + LEHE ikizi varken lehe olan sessizce seçilip [OK] verilemez."""
    _iskelet(tmp_path)
    _kayit(tmp_path / "_oa" / "cikti", "ALEYHE", "01")
    _kayit(tmp_path / "_oa" / "cikti", "LEHE", "02")
    kod, cikti = _cli(tmp_path)
    assert kod != 0, "ALEYHE ikizi gölgelendi, lehe kayıt sessizce geçti — m.6 kaçağı!"
    assert "ÇELİŞEN DAMGA" in cikti and "BLOK" in cikti, cikti


def test_d2_ayni_sinif_celiskisi_blok_degil_uyari(tmp_path):
    """LEHE ↔ ALEYHE-AYIRT (ikisi de girebilir sınıfı) engel DEĞİL, uyarıdır."""
    _iskelet(tmp_path)
    _kayit(tmp_path / "_oa" / "cikti", "LEHE", "01")
    yol = tmp_path / "_oa" / "cikti"
    (yol / "02-ictihat-muhakeme.md").write_text(
        "\n".join([
            "# İçtihat Muhakeme Kaydı", "",
            f"**KUNYE:** {KUNYE}",
            "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
            "**DAMGA:** ALEYHE-AYIRT", "",
            "## İLGİLİ-KISIM", "kararın taşıyıcı ilkesi…", "",
            "## DAVAYA-BAĞ", "somut olayla örtüşür…", "",
            "## AYIRT-ETME", "olayımızda ivaz yoktur, o kararda vardı — ayrılır.", "",
        ]), encoding="utf-8")
    kod, cikti = _cli(tmp_path)
    assert kod == 0, f"aynı sınıf içi çelişki bloklandı (aşırı sıkı): {cikti}"
    assert "ÇELİŞEN DAMGA" in cikti, "uyarı görünmüyor"


def test_d2_tek_kayit_lehe_hala_gecer(tmp_path):
    """Regresyon: çelişki yokken temiz LEHE zinciri geçmeye devam eder."""
    _iskelet(tmp_path)
    _kayit(tmp_path / "_oa" / "cikti", "LEHE", "01")
    kod, cikti = _cli(tmp_path)
    assert kod == 0, cikti


# ── D3: Layer 0 kaçış sınıfları ─────────────────────────────────────────────

def test_d3_telefon_eposta_plaka_yakalanir():
    for sorgu, beklenen in [
        ("müvekkil 0532 123 45 67 numaralı hat", "telefon"),
        ("+90 532 123 45 67 arayan kişi", "telefon"),
        ("bilgi@ornekhukuk.com adresine tebligat", "e-posta"),
        ("34 ABC 123 plakalı araç haczi", "plaka"),
    ]:
        sonuc = hafiza._layer0_sorgu_tara(sorgu)
        assert sonuc is not None, f"Layer 0 kaçırdı: {sorgu!r}"
        assert beklenen in sonuc, f"{sorgu!r} → {sonuc!r} (beklenen: {beklenen})"


def test_d3_mesru_hukuki_sorgular_yanlis_pozitif_uretmez():
    """Yanlış-pozitif kontrolü: meşru içtihat aramaları engellenmemeli."""
    for sorgu in [
        "tasarrufun iptali ivazsız tasarruf İİK 278",
        "Yargıtay Hukuk Genel Kurulu organik bağ birlikte istihdam",
        "HMK 119 dava dilekçesi zorunlu unsurlar",
        "İş Kanunu 25/II haklı fesih ispat yükü",
        "Bölge Adliye Mahkemesi istinaf incelemesi kapsamı",
    ]:
        assert hafiza._layer0_sorgu_tara(sorgu) is None, f"yanlış-pozitif: {sorgu!r}"
