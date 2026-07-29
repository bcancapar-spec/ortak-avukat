# -*- coding: utf-8 -*-
"""oa-dilekce / udf_yaz.py — GÖREV B (P0-B, v0.5.5) ÜRETİM-ANI ÖN-DENETİM testleri.

Saha bulgusu (B3): bir .udf üretimi, İçtihat Muhakeme Zinciri + Atıf/Künye
Teyit kapılarından hiç geçmeden (model `dilekce_denetim.py`/`teslim_paketi.py`yi
çağırmadan doğrudan `udf_yaz.py`yi koşarsa) dökümde/denetimde HİÇBİR iz
bırakmadan TESLİM ADAYI üretebiliyordu. `on_denetim_kostur()` bu iki kapıyı
İN-PROCESS (subprocess YOK) çalıştırır; BLOK bulsa BİLE UDF üretimini
ENGELLEMEZ — yalnız görünürlük (rapor dosyası + DURUM.md notu) üretir.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
"""
import importlib.util
import pathlib
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py"


def _load():
    assert SCRIPT.is_file(), f"udf_yaz.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("udf_yaz_on_denetim", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


uy = _load()

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
TASLAK_METIN = (
    "Somut olayda Yargıtay 4. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı "
    "emsal teşkil etmektedir.\n"
)


def _zincirli_kur(tmp_path):
    """Tam zincirli (LEHE damgalı, kaynak-izli, teyit kütüklü) bir _oa
    iskeleti kurar — `on_denetim_kostur` bu kökte BLOK BULMAMALIDIR."""
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)

    kaynak_yol = dokum_dizin / "kaynak.md"
    kaynak_yol.write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni "
        "burada yer almaktadır...\n", encoding="utf-8")

    # kunye_teyit.py'nin `kutuk_var` denetimi yalnız dosyanın VARLIĞINA bakar
    # (içerik boş olabilir) — gerçek teyit izi zaten dokum dizininden gelir.
    kutuk_yol = tmp_path / "_oa" / "teyit" / "kunye-teyit.md"
    kutuk_yol.write_text("", encoding="utf-8")

    satirlar = [
        "# 01 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
        "**DAMGA:** LEHE", "",
        "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
        "## DAVAYA-BAĞ", "...davaya bağ açıklaması...", "",
        "## AYIRT-ETME", "", "",
    ]
    (cikti_dizin / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")


# ── on_denetim_kostur() — birim testleri ────────────────────────────────────

def test_zincirsiz_taslakta_blok_bulunur_ve_calisti_true(tmp_path):
    sonuc = uy.on_denetim_kostur(TASLAK_METIN, kok=str(tmp_path))
    assert sonuc["calisti"] is True
    assert sonuc["blok_sayisi"] > 0
    assert sonuc["rapor"]


def test_zincirli_kurulumda_blok_sifir(tmp_path):
    _zincirli_kur(tmp_path)
    sonuc = uy.on_denetim_kostur(TASLAK_METIN, kok=str(tmp_path))
    assert sonuc["calisti"] is True
    assert sonuc["blok_sayisi"] == 0, sonuc["rapor"]


def test_atifsiz_taslakta_blok_sifir(tmp_path):
    """İçtihat/mevzuat atfı hiç yoksa iki kapı da 'doğrulanacak atıf yok' der —
    BLOK 0 olmalı (yanlış-pozitif üretmez)."""
    sonuc = uy.on_denetim_kostur("Sayın Mahkeme, arz ve izah ederiz.\n", kok=str(tmp_path))
    assert sonuc["calisti"] is True
    assert sonuc["blok_sayisi"] == 0


def test_oa_kontrol_bulunamazsa_sessizce_atlanir(monkeypatch):
    monkeypatch.setattr(uy, "_ictihat_muhakeme_modulu", lambda: None)
    monkeypatch.setattr(uy, "_kunye_teyit_modulu", lambda: None)
    sonuc = uy.on_denetim_kostur(TASLAK_METIN, kok=".")
    assert sonuc["calisti"] is False
    assert sonuc["blok_sayisi"] == 0
    assert sonuc["not"]


# ── _durum_md_uyari_ekle() — birim testleri ─────────────────────────────────

def test_durum_md_yoksa_minimal_basanik_ile_olusturulur(tmp_path):
    uy._durum_md_uyari_ekle(str(tmp_path), "dilekce.udf: teslim adayı üretildi, denetim: BLOK 2")
    durum = tmp_path / "_oa" / "DURUM.md"
    assert durum.is_file()
    icerik = durum.read_text(encoding="utf-8")
    assert "teslim adayı üretildi, denetim: BLOK 2" in icerik


def test_durum_md_varsa_uzerine_yazilmaz_sonuna_eklenir(tmp_path):
    durum = tmp_path / "_oa"
    durum.mkdir(parents=True)
    durum_yol = durum / "DURUM.md"
    durum_yol.write_text("# DURUM — mevcut içerik korunmalı\n", encoding="utf-8")
    uy._durum_md_uyari_ekle(str(tmp_path), "x.udf: teslim adayı üretildi, denetim: BLOK 1")
    icerik = durum_yol.read_text(encoding="utf-8")
    assert "mevcut içerik korunmalı" in icerik
    assert "denetim: BLOK 1" in icerik


def test_durum_md_uyari_ekle_asla_istisna_firlatmaz(tmp_path, monkeypatch):
    """Best-effort — yazma başarısız olsa bile (ör. dizin yerine dosya
    çakışması) ana akışı etkilememeli, istisna fırlatmamalı."""
    # `_oa` yerine bir DOSYA koyarak os.makedirs'i imkansız kıl.
    (tmp_path / "_oa").write_text("engel", encoding="utf-8")
    uy._durum_md_uyari_ekle(str(tmp_path), "her hâlde çökmemeli")  # sessizce yutulmalı


# ── uçtan uca CLI (npx fake ile — ağ/oturum GEREKMEZ) ───────────────────────

def _dummy_udf_yaz(yol, metin):
    """`udf_dogrula`nın beklediği minimal GEÇERLİ bir .udf sahtesi üretir —
    gerçek `npx udf-cli html2udf`nin yerine geçer (bu test ağsız/deterministiktir)."""
    u16 = uy.utf16_uzunluk(metin)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<template format_id="1.8">'
        '<content><![CDATA[' + metin + ']]></content>'
        '<properties><pageFormat mediaSizeName="1" leftMargin="70.866" '
        'rightMargin="70.866" topMargin="70.866" bottomMargin="70.866" '
        'paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0"/></properties>'
        '<elements resolver="hvl-default">'
        '<paragraph Alignment="3"><content startOffset="0" length="%d"/></paragraph>'
        '</elements>'
        '<styles><style name="default" description="Govde" family="Times New Roman" '
        'size="12" bold="false" italic="false" foreground="-16777216"/></styles>'
        '</template>' % u16
    )
    with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml.encode("utf-8"))


def _fake_npx_ile_udf_uret(html_yolu, cikti_yolu, npx_yolu="npx", zaman_asimi=180):
    _dummy_udf_yaz(cikti_yolu, "Sahte teslim adayı metni.\n")
    return {"basarili": True, "exit_kod": 0, "stdout": "", "stderr": "", "hata": None}


def _cli_calistir(monkeypatch, argv):
    monkeypatch.setattr(uy, "npx_ile_udf_uret", _fake_npx_ile_udf_uret)
    monkeypatch.setattr(sys, "argv", argv)
    uy.main()  # başarı yolunda sys.exit ÇAĞIRMAZ


def test_cli_zincirsiz_kurulumda_denetim_dosyasi_ve_durum_md_notu_duser(tmp_path, monkeypatch):
    girdi = tmp_path / "taslak.md"
    girdi.write_text(TASLAK_METIN, encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"

    _cli_calistir(monkeypatch, [
        "udf_yaz.py", "--girdi", str(girdi), "--cikti", str(cikti), "--kok", str(tmp_path),
    ])

    denetim_yolu = pathlib.Path(str(cikti) + ".denetim.txt")
    assert denetim_yolu.is_file(), "BLOK varken ön-denetim raporu diskte olmalıydı"
    assert denetim_yolu.read_text(encoding="utf-8").strip()

    durum_yol = tmp_path / "_oa" / "DURUM.md"
    assert durum_yol.is_file(), "BLOK varken _oa/DURUM.md notu düşmeliydi"
    icerik = durum_yol.read_text(encoding="utf-8")
    assert "teslim adayı üretildi, denetim: BLOK" in icerik
    assert "dilekce.udf" in icerik


def test_cli_zincirli_kurulumda_uyari_yok(tmp_path, monkeypatch):
    _zincirli_kur(tmp_path)
    girdi = tmp_path / "taslak.md"
    girdi.write_text(TASLAK_METIN, encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"

    _cli_calistir(monkeypatch, [
        "udf_yaz.py", "--girdi", str(girdi), "--cikti", str(cikti), "--kok", str(tmp_path),
    ])

    assert not pathlib.Path(str(cikti) + ".denetim.txt").exists(), (
        "zincirli (damgalı) kurulumda ön-denetim raporu ÜRETİLMEMELİYDİ")
    durum_yol = tmp_path / "_oa" / "DURUM.md"
    assert not durum_yol.exists(), (
        "zincirli kurulumda udf_yaz.py DURUM.md'ye uyarı DÜŞÜRMEMELİYDİ")
