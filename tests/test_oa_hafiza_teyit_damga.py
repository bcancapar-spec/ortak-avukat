# -*- coding: utf-8 -*-
"""P0-2 (v0.5.5) — tek-komut içtihat muhakeme ritüeli: `oa_hafiza.py teyit`
--damga/--bag/--ayirt/--dokum-icerik/--ilgili-kisim genişlemesi.

Kapsam:
- İKİ ARAÇ SINIFI: ARAMA (tam metin yok) damgasız SERBEST + 'ARAMA — tam metin
  çekilmedi' tokenı; GETİR (tam metin var) --damga ZORUNLU.
- --bag ≥40 karakter, --ayirt (ALEYHE-AYIRT'ta) ≥20 karakter.
- --dokum-icerik → dökum/ dosyası doğar (provenans notlu), .son-dokum güncellenir,
  kütük satırı linklenir.
- --ilgili-kisim VERBATİM döküm içinde geçmeli (özet ikamesi reddedilir).
- --damga LEHE → 03-ictihat-muhakeme.md'de şablon-uyumlu bölüm doğar ve
  ictihat_muhakeme_denetim.py bu bölümü OK sayar (uçtan uca entegrasyon).
- mevzuat_getir damgasız → v0.5.1 davranışı birebir (geriye uyum).
- Layer-0: TCKN/IBAN içeren --sorgu ile içtihat araçları RET eder.
"""
import importlib.util
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"
DENETIM = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
           / "ictihat_muhakeme_denetim.py")
KUNYE_TEYIT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
               / "kunye_teyit.py")
KUNYE_ORTAK = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
               / "kunye_ortak.py")


def _load(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ko = _load(KUNYE_ORTAK, "kunye_ortak_teyit_damga_duzeltme_test")


def _cli(args, cwd, env=None):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
        env=env,
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _denetim_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(DENETIM)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _kunye_teyit_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(KUNYE_TEYIT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _init(tmp_path):
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)


KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
DOKUM_METIN = (
    "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni: "
    "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır; "
    "TBK m.49 uyarınca tazminat sorumluluğu doğar.\n"
)
ILGILI_KISIM = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"
BAG_METNI = ("Bu karar, dosyamızdaki trafik kazası olgusuyla aynı unsur setini "
             "içeriyor; TBK m.49'un büyük önermesini somutlaştıran doğrudan emsaldir.")


# ── GETİR sınıfı: damgasız RET ──────────────────────────────────────────────

def test_getir_damgasiz_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ZORUNLU" in cikti


def test_bag_39_karakter_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", "x" * 39,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "40" in cikti


def test_aleyhe_ayirt_ayirt_yok_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "ALEYHE-AYIRT", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "AYIRT-ETME" in cikti


# ── --dokum-icerik: dosya doğar, kütük linklenir, .son-dokum günceller ─────

def test_dokum_icerik_dosya_dogar_ve_son_dokum_guncellenir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dosyalar = list(dokum_dizin.glob("*.md"))
    assert len(dosyalar) == 1, dosyalar
    icerik = dosyalar[0].read_text(encoding="utf-8")
    assert DOKUM_METIN.strip() in icerik
    assert "VERİLEN metin" in icerik  # provenans notu
    son_dokum = (tmp_path / "_oa" / "teyit" / ".son-dokum").read_text(encoding="utf-8")
    assert dosyalar[0].name in son_dokum
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "[döküm]" in kutuk
    assert dosyalar[0].name in kutuk


# ── --damga LEHE → şablon-uyumlu bölüm + denetim entegrasyonu ──────────────

def test_damga_lehe_muhakeme_bolumu_denetimden_gecer(tmp_path):
    _init(tmp_path)
    # v0.5.8.5 [G6] sözleşmesi: kütük fiilen kullanılan kökte denetimden
    # geçmek için döküm sınıfı TAM-METİN beyan edilmiş olmalı (A1 tam-okuma).
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--dokum-sinifi", "tam-metin", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    muhakeme = tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md"
    assert muhakeme.is_file()
    metin = muhakeme.read_text(encoding="utf-8")
    assert "**KUNYE:**" in metin
    assert "**KAYNAK-IZI:**" in metin
    assert "**DAMGA:** LEHE" in metin
    assert "## İLGİLİ-KISIM" in metin
    assert "## DAVAYA-BAĞ" in metin

    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 4. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı "
        "emsal teşkil etmektedir.\n", encoding="utf-8",
    )
    dkod, dcikti = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert dkod == 0, dcikti
    assert "OK 1" in dcikti


def test_damga_aleyhe_uyari_basar(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "ALEYHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "GİREMEZ" in cikti


# ── İLGİLİ-KISIM verbatim doğrulaması ───────────────────────────────────────

def test_ilgili_kisim_dokumde_gecmiyorsa_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", "bu cümle döküm içinde YOK — uydurma alıntı",
         "--dokum-icerik", DOKUM_METIN, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "VERBATİM" in cikti


def test_sonuc_kunye_no_dokumde_gecmiyorsa_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", "Yargıtay 4. HD, E. 2099/9999, K. 2099/9999",
         "--damga", "LEHE", "--bag", BAG_METNI, "--ilgili-kisim", ILGILI_KISIM,
         "--dokum-icerik", DOKUM_METIN, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "tutarsız" in cikti.lower()


# ── ARAMA sınıfı: damgasız serbest + token ──────────────────────────────────

def test_arama_damgasiz_serbest_ve_token_eklenir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "trafik kazası illiyet TBK 49",
         "--sonuc", "birkaç aday künye bulundu", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "ARAMA — tam metin çekilmedi" in kutuk


def test_arama_damga_verilirse_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "trafik kazası illiyet TBK 49",
         "--sonuc", "birkaç aday künye bulundu", "--damga", "LEHE",
         "--bag", BAG_METNI, "--ilgili-kisim", ILGILI_KISIM, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "TAM METİN" in cikti.upper()


# ── mevzuat_getir damgasız → geçer (v0.5.1 davranışı birebir) ──────────────

def test_mevzuat_getir_damgasiz_gecer(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "mevzuat_getir", "--sorgu", "TBK m.49",
         "--sonuc", "TBK m.49 — haksız fiil sorumluluğu", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "TBK m.49" in kutuk
    assert "DAMGA=" not in kutuk


# ── Layer 0 — TCKN/IBAN içtihat sorgusuna sızamaz ──────────────────────────

def test_layer0_tckn_sorguda_exit1(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "müvekkil TC 12345678901 trafik kazası",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti


def test_layer0_sorgu_onayli_ile_gecer(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "müvekkil TC 12345678901 trafik kazası",
         "--sonuc", "sonuç", "--sorgu-onayli", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_layer0_normal_sorgu_etkilenmez(tmp_path):
    """Normal bir esas/karar no'lu içtihat araması (meşru kullanım) Layer-0
    tarafından YANLIŞLIKLA engellenmemeli (TCKN/IBAN deseni yok)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "Yargıtay 4. HD E. 2023/1234 illiyet",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


# ── stdin yolu (--dokum-icerik -) UTF-8 okur ────────────────────────────────

def test_dokum_icerik_stdin_utf8_okur(tmp_path):
    import os
    _init(tmp_path)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1254"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "teyit", "--arac", "ictihat_getir",
         "--sorgu", "TBK m.49 illiyet", "--sonuc", KUNYE, "--damga", "LEHE",
         "--bag", BAG_METNI, "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", "-",
         "--kok", str(tmp_path)],
        cwd=str(tmp_path), input=DOKUM_METIN, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=env,
    )
    assert cp.returncode == 0, cp.stdout + cp.stderr
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dosyalar = list(dokum_dizin.glob("*.md"))
    assert len(dosyalar) == 1
    icerik = dosyalar[0].read_text(encoding="utf-8")
    assert "illiyet bağı" in icerik


# ── P0-2 DÜZELTME (--dokum-icerik damgadan bağımsız) ───────────────────────

def test_arama_dokum_icerik_damgasiz_da_dosya_dogurur(tmp_path):
    """ARAMA sınıfının normal kullanımı (arama çıktısını iz olarak saklamak)
    damgasızdır — eskiden bu içerik --damga verilmedikçe SESSİZCE atılıyordu
    (kayıpsızlık invaryantı ihlali); artık --damga'dan BAĞIMSIZ dosyaya yazılır."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "trafik kazası illiyet TBK 49",
         "--sonuc", "birkaç aday künye bulundu", "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dosyalar = list(dokum_dizin.glob("*.md"))
    assert len(dosyalar) == 1, dosyalar
    assert DOKUM_METIN.strip() in dosyalar[0].read_text(encoding="utf-8")
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "[döküm]" in kutuk
    assert "DAMGA=" not in kutuk


# ── P0-2 DÜZELTME (kunye dogrulamasi) ──────────────────────────────────────

def test_damga_ile_ayristirilamayan_sonuc_exit1(tmp_path):
    """--sonuc'tan (E./K. YYYY/NNNN) ayrıştırılabilir bir künye çıkmıyorsa
    üretilecek muhakeme kaydı hiçbir dilekçe atfıyla eşleşemez — erkenden RET."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", "Yargıtay 4. HD kararı (esas/karar no yok)", "--damga", "LEHE",
         "--bag", BAG_METNI, "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ayrıştırılabilir bir künye" in cikti


# ── P0-2 DÜZELTME (KAYNAK-IZI yolu — köke-göreli + posix) ──────────────────

def test_kaynak_izi_koke_goreli_posix_yazilir(tmp_path):
    """--kok MUTLAK verilse bile KAYNAK-IZI'ye makine yolu GÖMÜLMEZ — köke
    göreli, ileri-bölülü (posix) `_oa/teyit/dokum/<ad>` biçiminde yazılır."""
    _init(tmp_path)
    assert tmp_path.is_absolute()
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--dokum-sinifi", "tam-metin", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    import re as _re
    m = _re.search(r"^\*\*KAYNAK-IZI:\*\*\s*(.+)$", metin, _re.M)
    assert m, metin
    kaynak_izi = m.group(1).strip()
    assert kaynak_izi.startswith("_oa/teyit/dokum/"), kaynak_izi
    assert "\\" not in kaynak_izi
    assert str(tmp_path) not in kaynak_izi

    # farklı bir cwd'den koşulan denetim de aynı --kok ile yolu bulabilmeli
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 4. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı "
        "emsal teşkil etmektedir.\n", encoding="utf-8",
    )
    dkod, dcikti = _denetim_cli([str(taslak), "--kok", str(tmp_path)], cwd=tmp_path.parent)
    assert dkod == 0, dcikti
    assert "OK 1" in dcikti


# ── P0-2 DÜZELTME (d) — DAMGA sessizce değiştirilemez (yazma-öncesi kapı) ──

def test_damga_ikinci_teyitte_sessizce_farkli_verilemez(tmp_path):
    """Aynı künye için ALEYHE teyit edildikten sonra --damga-degistir OLMADAN
    ikinci bir `teyit --damga LEHE` çağrısı RET edilmeli — salt-ALEYHE'nin
    dosya elle düzenlenmeden, yalnız ikinci bir CLI çağrısıyla temizlenmesi
    yolu kapalı kalmalı (P0-2 DÜZELTME d, yazma-zamanı çapraz kontrol)."""
    _init(tmp_path)
    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "ALEYHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet ikinci tur",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 != 0, cikti2
    assert "SON DAMGA farklı" in cikti2
    assert "--damga-degistir" in cikti2


def test_damga_degistir_ile_gecerli_gerekceyle_gecer_ve_eskiyi_isaretler(tmp_path):
    """--damga-degistir (≥40 karakter gerekçe) ile bilinçli DAMGA değişimi
    KABUL edilir; eski (ALEYHE) muhakeme bölümü SİLİNMEZ, GEÇERSİZ-KILINDI
    satırıyla işaretlenir (kayıpsızlık invaryantı — içerik korunur)."""
    _init(tmp_path)
    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "ALEYHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    gerekce = "Yeniden inceleme sonucu kararın aslında LEHE olduğu anlaşıldı (düzeltme)."
    assert len(gerekce) >= 40
    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet düzeltme",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--damga-degistir", gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 == 0, cikti2

    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    assert metin.count("**KUNYE:**") == 2, metin  # her iki bölüm de KORUNDU
    assert "**GEÇERSİZ-KILINDI:**" in metin
    assert "**DAMGA:** ALEYHE" in metin  # eski bölüm SİLİNMEDİ
    assert "**DAMGA:** LEHE" in metin
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "DEĞİŞTİRİLDİ" in kutuk


# ── P0-2 DÜZELTME (e) — Layer-0: arac sınıfından bağımsız + yeni kalıplar ──

def test_layer0_kurum_karari_ara_tckn_ile_de_engellenir(tmp_path):
    """Layer-0 taraması artık ARAMA/GETİR sınıfıyla SINIRLI değil — HER --arac
    (kurum_karari_ara dahil) dış MCP'ye giden bir sorgu taşır."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "kurum_karari_ara", "--sorgu", "musteri 12345678901 sikayet",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti


def test_layer0_mevzuat_ara_tckn_ile_de_engellenir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "mevzuat_ara", "--sorgu", "12345678901 numaralı müvekkil",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti


def test_layer0_ad_soyad_kalibi_engellenir(tmp_path):
    """Kurumsal olmayan iki ardışık büyük-harfli sözcük (olası ad-soyad) —
    anayasa §10'un dört deseninden biri (TCKN/ad-soyad/dosya-esas no/IBAN).
    Sorguda mahkeme adı/esas no BİLİNÇLİ OLARAK yok — yalnız ad-soyad
    kalıbının kendi başına yakalandığını doğrular (ayrık regresyon kilidi)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara",
         "--sorgu", "Ahmet Yılmaz için kıdem tazminatı hesaplaması",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti
    assert "ad-soyad" in cikti


def test_layer0_ilk_derece_mahkeme_esas_ile_engellenir(tmp_path):
    """Şehir + ilk derece mahkeme adı + esas no eş-geçmesi somut bir dosyayı
    işaret eder (Yargıtay/BAM gibi genel emsal-arama mercilerinden AYRI)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "kurum_karari_ara",
         "--sorgu", "Örnek 1. İş Mahkemesi E. 2099/1 dosyası",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti
    assert "mahkeme" in cikti.lower()


def test_layer0_ad_soyad_onayli_ile_gecer(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "Ahmet Yılmaz kıdem tazminatı",
         "--sonuc", "sonuç", "--sorgu-onayli", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_layer0_yargitay_daire_genel_arama_hala_serbest(tmp_path):
    """Genel Yargıtay/BAM daire referansları (şehir/ilk-derece adı OLMADAN)
    yanlışlıkla engellenmemeli — meşru içtihat aramasıdır (regresyon kilidi)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara",
         "--sorgu", "Yargıtay Hukuk Genel Kurulu E. 2023/1234 kıdem tazminatı",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


# ── DÜZELTME (v0.5.5 düzeltme turu, ÖNEMLİ) — Layer 0 ad-soyad isabeti ─────
# UYAP evrakının standart biçimi TAM BÜYÜK HARFLİ soyaddır (saha dizin adı
# örüntüsü: "<yıl>_<esas>_<Şehir>_<N>._<Tür>_Mahkemesi") — eski desen bunu
# hiç yakalamıyordu (yanlış-negatif, gerçek PII biçiminde en büyük körlük).

@pytest.mark.parametrize("sorgu", [
    "AHMET YILMAZ için kıdem tazminatı hesaplaması",
    "Ahmet YILMAZ için kıdem tazminatı hesaplaması",
    "MEHMET DEMİR aleyhine açılan dava",
])
def test_layer0_tam_buyuk_harfli_ad_soyad_artik_yakalanir(tmp_path, sorgu):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", sorgu,
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti
    assert "ad-soyad" in cikti


# ── DÜZELTME (v0.5.5 düzeltme turu, ÖNEMLİ) — Layer 0 yanlış-pozitif giderimi ──
# Ölçülen 7 yanlış-pozitiften (tamamen anonim, gündelik hukuk sorguları)
# örnekler — artık kurumsal kelime kümesinde bilinen terimlerle RET ALMAMALI.

@pytest.mark.parametrize("sorgu", [
    "Avrupa İnsan Hakları Mahkemesi kararları TBK 49",
    "Sosyal Güvenlik Kurumu prim borcu",
    "Kamu İhale Kurumu itiraz süresi",
    "Yüksek Seçim Kurulu kararı",
    "Bilirkişi Raporu itiraz dilekçesi",
    "Maddi Manevi Tazminat hesaplaması",
    "Fikri Sınai Haklar mahkemesi görevi",
])
def test_layer0_kurumsal_terimler_artik_yanlis_pozitif_uretmez(tmp_path, sorgu):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", sorgu,
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


# ── DÜZELTME (v0.5.5 şerh turu, Ş5a BLOKER/ÖNEMLİ) — ilk derece mahkeme ────
# deseni GENELLEŞTİRİLDİ: eski sabit tür listesi (İş/Asliye Hukuk/.../Vergi)
# 8/11 gerçekçi "şehir + N. mahkeme + esas no" sorgusunu HİÇ yakalamıyordu.

@pytest.mark.parametrize("sorgu", [
    "Denizli 2. Asliye Ticaret Mahkemesi 2024/88 esas",
    "İzmir 3. Tüketici Mahkemesi 2024/12 esas",
    "Bursa 1. İcra Hukuk Mahkemesi 2024/45 esas",
    "Konya 2. İcra Ceza Mahkemesi 2024/9 esas",
    "İstanbul 4. Fikri ve Sınai Haklar Hukuk Mahkemesi 2024/321 esas",
    "Antalya 1. Çocuk Mahkemesi 2024/17 esas",
    "Samsun 2. Kadastro Mahkemesi 2024/3 esas",
    "Eskişehir 3. IS Mahkemesi 2024/77 esas",  # ASCII harf-çevrimli "İş"
])
def test_layer0_genellenmis_ilk_derece_mahkeme_deseni_artik_yakalar(tmp_path, sorgu):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "kurum_karari_ara", "--sorgu", sorgu,
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti
    assert "mahkeme" in cikti.lower()


def test_layer0_bam_bim_numarali_referans_hala_serbest(tmp_path):
    """BAM/BİM (Bölge Adliye/İdare Mahkemesi) numaralı referansı — 'N. Bölge
    Adliye Mahkemesi' biçimi genelleştirilmiş regex'e YAPISAL olarak uysa
    bile — genel bir emsal-arama mercii İŞARETİDİR, somut bir İLK DERECE
    dosya kimliği DEĞİLDİR; AÇIKÇA muaf tutulur (regresyon kilidi)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "kurum_karari_ara",
         "--sorgu", "İzmir 2. Bölge Adliye Mahkemesi 2024/100 esas kararı",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


# ── DÜZELTME (v0.5.5 şerh turu, Ş5b ÖNEMLİ) — Title-Case hukuki BAŞLIKLARDA ─
# ad-soyad yanlış-pozitifi giderildi (7/13 ölçülen FP). Kişi-bağlam sözcüğü
# YOK ve sorgu tümüyle Title-Case bir BAŞLIK biçiminde OLDUĞUNDAN artık
# serbest geçer.

@pytest.mark.parametrize("sorgu", [
    "Bilirkişi Raporuna İtiraz Dilekçesi",
    "Mobbing İddiası Manevi Tazminat",
    "Fazla Mesai Ücreti Takdiri İndirim",
    "İşe İade Davası Boşta Geçen Süre",
    "Anayasa Mahkemesi Bireysel Başvuru",
    "Kısmi Dava Fazlaya İlişkin Hakların Saklı Tutulması",
    "Ulusal Yargı Ağı Bilişim Sistemi",
])
def test_layer0_title_case_hukuki_basliklar_artik_yanlis_pozitif_uretmez(tmp_path, sorgu):
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", sorgu,
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_layer0_cift_kelimelik_ciplak_ad_soyad_title_case_bastirmaya_ragmen_yakalanir(tmp_path):
    """YENİ İHLAL ÖNLEME: Title-Case başlık bastırması (Ş5b) yalnız sorgu
    2'DEN FAZLA sözcük içerdiğinde uygulanır — bariz, SALT iki sözcükten
    ibaret bir ad-soyad araması (ör. "Ahmet Yılmaz") tümüyle Title-Case
    olsa bile YAKALANMAYA devam etmelidir (aksi hâlde bastırma bariz PII
    aramasını da susturabilirdi)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "Ahmet Yılmaz",
         "--sonuc", "sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ANONİM" in cikti
    assert "ad-soyad" in cikti


# ── P0-2 DÜZELTME (dokum ad üretimi) — ÇAKIŞMADA ÜZERİNE YAZMA YOK ─────────
# ts() saniye çözünürlüklü olduğundan CLI/subprocess ile aynı-saniye çakışması
# güvenilir biçimde ZORLANAMAZ; bu yüzden modül İN-PROCESS import edilip
# `ts()` sabitlenerek (monkeypatch) iki ardışık çağrı AYNI ad üretecek şekilde
# kurulur — O_CREAT|O_EXCL'in gerçekten devreye girip sonek eklediği doğrulanır.

import argparse
import importlib.util as _ilu

_OH_SPEC = _ilu.spec_from_file_location("oa_hafiza_dokum_cakisma_test", SCRIPT)
_oh = _ilu.module_from_spec(_OH_SPEC)
_OH_SPEC.loader.exec_module(_oh)


def _teyit_args(**over):
    taban = dict(arac="ictihat_getir", sorgu="TBK m.49 illiyet", sonuc=KUNYE,
                 damga="LEHE", bag=BAG_METNI, ayirt=None, ilgili_kisim=ILGILI_KISIM,
                 dokum=None, dokum_icerik=DOKUM_METIN, sorgu_onayli=False,
                 damga_degistir=None, kok=None)
    taban.update(over)
    return argparse.Namespace(**taban)


def test_dokum_ad_cakismasi_var_olan_dosyanin_uzerine_yazmaz(tmp_path, monkeypatch):
    """`len(mevcut)+1` sayacı, dizin listelemesi ile fiilî diskteki dosyalar
    ARASINDA bir TUTARSIZLIK varsa (dizinden bir dosya silinip sayaç geri
    sarınca, ya da iki çağrının aynı bayat listelemeyi görmesi — TOCTOU) AYNI
    adı ikinci kez üretebilir. Burada `os.listdir` GERÇEK diskten FARKLI
    (bayat/boş) bir liste dönecek şekilde sabitlenip bu tutarsızlık BİLE BİLE
    zorlanıyor — `open(..., 'w')` ile sessizce ezilmemeli, `O_CREAT|O_EXCL`
    çakışmayı yakalayıp sonek ekleyerek yeniden denemelidir (kayıpsızlık
    invaryantı, P0-2 DÜZELTME)."""
    _oh._kok_ayarla(str(tmp_path))
    _oh.cmd_init(argparse.Namespace(dosya="Test Dosyası"))
    monkeypatch.setattr(_oh, "ts", lambda: "2026-01-01T00-00-00")

    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    # kodun (sayaç=0 sanarak) üreteceği ada AYNEN sahip, YABANCI bir dosya
    # fiilen diskte VAR — ama `os.listdir` bunu GÖRMÜYORMUŞ gibi sabitlendi.
    onceden_var_olan = dokum_dizin / "001-ictihat_getir-2026-01-01T00-00-00.md"
    onceden_var_olan.write_text("BAŞKA bir teyidin ham dökümü — bu içerik KORUNMALI.",
                                 encoding="utf-8")
    gercek_listdir = os.listdir
    monkeypatch.setattr(
        _oh.os, "listdir",
        lambda d: [] if os.path.normpath(str(d)) == os.path.normpath(str(dokum_dizin))
        else gercek_listdir(d))

    _oh.cmd_teyit(_teyit_args(kok=str(tmp_path)))

    # yabancı dosya SESSİZCE EZİLMEMİŞ olmalı
    assert onceden_var_olan.read_text(encoding="utf-8") == \
        "BAŞKA bir teyidin ham dökümü — bu içerik KORUNMALI."

    dosyalar = sorted(p.name for p in dokum_dizin.glob("*.md"))
    assert len(dosyalar) == 2, dosyalar  # eski + YENİ (soneki eklenmiş) dosya
    yeni_dosyalar = [d for d in dosyalar if d != onceden_var_olan.name]
    assert len(yeni_dosyalar) == 1, yeni_dosyalar
    yeni_icerik = (dokum_dizin / yeni_dosyalar[0]).read_text(encoding="utf-8")
    assert DOKUM_METIN.strip() in yeni_icerik
    # .son-dokum YENİ yazılan dosyayı göstermeli (eskiyi değil)
    son_dokum = (tmp_path / "_oa" / "teyit" / ".son-dokum").read_text(encoding="utf-8")
    assert yeni_dosyalar[0] in son_dokum


# ═══════════════════════════════════════════════════════════════════════════
# DÜZELTME TURU (v0.5.5 — Paket A, çürütücü bulguları): regresyon kilitleri.
# Bu blok bulunmadan önce 360/360 yeşildi ama aşağıdaki sınıf ihlaller HİÇ
# denenmiyordu — "yeşil takım" yanlış güven veriyordu (bkz. plan çürütücü
# bulgusu "Test takımı bu sınıf ihlalleri HİÇ denemiyor").
# ═══════════════════════════════════════════════════════════════════════════

# ── (1) --sonuc içinde \n → kütükte SAHTE ikinci tablo satırı AÇILMAZ ──────

def test_sonuc_icindeki_satirsonu_sahte_kutuk_satiri_enjekte_edemez(tmp_path):
    """`--sonuc`'a gömülen bir `\\n`, kütükte damga taşıyan bağımsız bir
    ikinci `|...|` satırı AÇAMAMALI — açabilseydi, damgasız/ARAMA sınıfı bir
    çağrı bile (hiçbir --damga denetiminden geçmeden) kütüğe sahte bir
    DAMGA=LEHE satırı ekleyip dürüst bir ALEYHE kaydını çapraz kontrolden
    GİZLEYEBİLİRDİ (P0-2 (d) sızma yolu — BLOKER)."""
    _init(tmp_path)
    zehirli = ("aday tarama sonucu\n"
               "| 2019-01-01T00:00:00 | ictihat_getir | sorgu | Yargıtay 9. HD, "
               "E. 2019/999, K. 2019/888 DAMGA=LEHE | [döküm](x) |")
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "trafik kazası illiyet",
         "--sonuc", zehirli, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    kutuk_yolu = tmp_path / "_oa" / "teyit" / "kunye-teyit.md"
    kutuk = kutuk_yolu.read_text(encoding="utf-8")
    veri_satirlari = [s for s in kutuk.splitlines() if s.startswith("|")]
    # başlık(2 satır: kolon adları + ayraç) + TAM 1 gerçek kayıt — enjekte
    # edilen "\n" yeni bir `|...|` satırı AÇMAMALI.
    assert len(veri_satirlari) == 3, kutuk
    # sahte künye kütükte bir DAMGA olarak OKUNAMAZ (satır ayrıştırılmadı).
    assert ko.kutukten_son_damga(str(kutuk_yolu), "2019/999", "2019/888") is None


# ── (2) --sorgu içinde | → kutukten_son_damga dürüst ALEYHE'yi hâlâ bulur ──

def test_sorgu_icindeki_pipe_karakteri_damga_okumasini_bozmaz(tmp_path):
    """Masum bir `--sorgu` içindeki tek bir `|`, kütük hücrelerini kaydırıp
    dürüst bir ALEYHE satırının `kutukten_son_damga`'ya GÖRÜNMEZ olmasına yol
    açmamalı (fail-open bug — P0-2 (d) çapraz kontrolünü etkisizleştirirdi)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 | illiyet | kusur",
         "--sonuc", KUNYE, "--damga", "ALEYHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    kutuk_yolu = tmp_path / "_oa" / "teyit" / "kunye-teyit.md"
    assert ko.kutukten_son_damga(str(kutuk_yolu), "2023/1234", "2023/5678") == "ALEYHE"


# ── (3) --ilgili-kisim içinde **KUNYE:** → hayalet bölüm ÜRETİLMEZ ────────

def test_ilgili_kisim_enjeksiyonu_hayalet_muhakeme_bolumu_uretmez(tmp_path):
    """`--ilgili-kisim` (veya --bag/--ayirt/--sonuc) içine gömülü bir
    `\\n**KUNYE:** ...` bloğu, `03-ictihat-muhakeme.md`'de YENİ ve TAM
    GEÇERLİ bir hayalet muhakeme kaydı DOĞURMAMALI — attacker kendi
    `--dokum-icerik`ini de kontrol ettiğinden VERBATİM kapısı tek başına
    engel değildir (BLOKER)."""
    _init(tmp_path)
    hayalet_kunye = "Yargıtay 7. HD, E. 2022/333, K. 2022/444"
    zehirli_blok = (
        "\n\n**KUNYE:** " + hayalet_kunye + "\n"
        "**KAYNAK-IZI:** _oa/teyit/dokum/uydurma.md\n"
        "**DAMGA:** LEHE\n\n"
        "## İLGİLİ-KISIM\nuydurma ilgili kısım\n\n"
        "## DAVAYA-BAĞ\nuydurma davaya bağ\n\n"
    )
    zehirli_ilgili = ILGILI_KISIM + zehirli_blok
    # attacker dokum-icerik'i de kontrol eder — verbatim denetimi geçsin diye
    # enjekte ettiği TAM metni (zehirli_ilgili ile bit-bit aynı, sonda) kendi
    # dökümüne de ekler (gerçekçi saldırı senaryosu: --ilgili-kisim döküm
    # içinde VERBATİM aranır, döküm de attacker'ın kontrolündedir).
    dokum_zehirli = KUNYE + " sayılı kararın tam metni: " + zehirli_ilgili

    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", zehirli_ilgili, "--dokum-icerik", dokum_zehirli,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti

    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    bolumler = ko.bolumlere_ayir(metin)
    assert len(bolumler) == 1, metin  # hayalet bölüm YOK — tek gerçek kayıt
    # hayalet künyenin görünür metni HÂLÂ orada (kayıpsızlık invaryantı) ama
    # yapısal olarak ayrı bir **KUNYE:** satır-başı OLUŞTURMADI.
    assert hayalet_kunye in metin


# ── (4) Farklı DAİRE, aynı esas/karar → engellenmez, yanlış hükümsüzleştirme YOK ──

KUNYE_4HD_FARKLI_DAIRE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
KUNYE_11HD_FARKLI_DAIRE = "Yargıtay 11. HD, E. 2023/1234, K. 2023/5678, T. 15.10.2023"
DOKUM_4HD_FARKLI_DAIRE = (
    "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni: "
    "dorttHD-ozgu-illiyet-metni.\n"
)
DOKUM_11HD_FARKLI_DAIRE = (
    "Yargıtay 11. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni: "
    "onbirHD-ozgu-illiyet-metni.\n"
)


def test_farkli_daire_ayni_esas_karar_no_yanlislikla_engellenmez(tmp_path):
    """Esas/karar no'ları HER dairede yılda sıfırdan başlar — GERÇEKTEN
    FARKLI bir dairenin aynı numaralı kararı, önceki daireninkiyle 'aynı
    künye' SAYILMAMALI: ikinci `--damga` çağrısı RET ALMAMALI ve
    `--damga-degistir` gerekmeden ilk (4. HD) kaydı YANLIŞ yere hükümsüz
    kılınmamalı (daire-kör bug)."""
    _init(tmp_path)
    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet 4hd",
         "--sonuc", KUNYE_4HD_FARKLI_DAIRE, "--damga", "ALEYHE", "--bag", BAG_METNI,
         "--ilgili-kisim", "dorttHD-ozgu-illiyet-metni",
         "--dokum-icerik", DOKUM_4HD_FARKLI_DAIRE, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet 11hd",
         "--sonuc", KUNYE_11HD_FARKLI_DAIRE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", "onbirHD-ozgu-illiyet-metni",
         "--dokum-icerik", DOKUM_11HD_FARKLI_DAIRE, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 == 0, cikti2  # eskiden 'kütükteki SON DAMGA farklı' diye RET ederdi

    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    assert "**GEÇERSİZ-KILINDI:**" not in metin  # 4. HD kaydı YANLIŞ hükümsüz kılınmadı
    assert metin.count("**DAMGA:** ALEYHE") == 1
    assert metin.count("**DAMGA:** LEHE") == 1


# ── (5) Verbatim RET sonrası döküm dizini BOŞ kalır, künye TEYİTSİZ kalır ──

def test_verbatim_ret_sonrasi_dokum_yetim_kalmaz_ve_teyitsiz_kalir(tmp_path):
    """`--ilgili-kisim` VERBATİM denetiminden geçemeyip RET alan bir çağrı,
    `_oa/teyit/dokum/`'da YETİM bir dosya BIRAKMAMALI — aksi hâlde
    `kunye_teyit.py` bu yetim dosyayı teyit kaynağı sayıp reddedilmiş
    çağrının künyesini TEYİTLİ gösterebilirdi (BLOKER — kozmetik RET)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", "bu cümle döküm içinde YOK — uydurma alıntı",
         "--dokum-icerik", DOKUM_METIN, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti

    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    assert list(dokum_dizin.glob("*.md")) == [], list(dokum_dizin.glob("*.md"))
    assert not (tmp_path / "_oa" / "teyit" / ".son-dokum").exists()
    kutuk_metin = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "DAMGA=" not in kutuk_metin

    taslak = tmp_path / "taslak.md"
    taslak.write_text(f"{KUNYE} sayılı karar emsal teşkil etmektedir.\n", encoding="utf-8")
    tkod, tcikti = _kunye_teyit_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert tkod != 0, tcikti
    assert "TEYİTSİZ" in tcikti


# ── (4b) --damga-degistir sonrası GEÇERSİZ-KILINDI kayıt aday havuzundan
#         düşer — sahte ÇELİŞEN DAMGA uyarısı üretmez (bkz. ictihat_muhakeme_denetim) ──

def test_damga_degistir_sonrasi_gecersiz_kayit_denetimde_celisen_damga_uretmez(tmp_path):
    _init(tmp_path)
    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE, "--damga", "ALEYHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    gerekce = "Yeniden inceleme sonucu kararın aslında LEHE olduğu anlaşıldı (düzeltme)."
    # v0.5.8.5 [G6]: denetimden geçmek için düzeltilmiş LEHE teyidinin döküm
    # sınıfı TAM-METİN beyanlı olmalı (A1 tam-okuma şartı).
    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet düzeltme",
         "--sonuc", KUNYE, "--damga", "LEHE", "--bag", BAG_METNI,
         "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
         "--dokum-sinifi", "tam-metin", "--damga-degistir", gerekce,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 == 0, cikti2

    taslak = tmp_path / "taslak.md"
    taslak.write_text(f"{KUNYE} sayılı karar emsal teşkil etmektedir.\n", encoding="utf-8")
    dkod, dcikti = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert dkod == 0, dcikti
    assert "OK 1" in dcikti
    assert "ÇELİŞEN DAMGA" not in dcikti  # GEÇERSİZ-KILINDI kayıt aday havuzundan düştü
    assert "hükümsüz kılınmış" in dcikti
