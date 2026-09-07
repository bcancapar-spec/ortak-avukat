# -*- coding: utf-8 -*-
"""v0.5.16 / GRUP D — `oa_hafiza.py` AKIBET ÜRETİCİSİ (K5, Hamle 4) +
SENKRON KLASÖR UYARISI (P1-8 / A-11 / B-5) + oa-gizlilik belge bağı.

Saha kanıtı (2026-09-06 denetim raporları):
- K5: `ictihat_muhakeme_denetim.py` [G5] kapısı aşılmışlığı okur ama kararın
  AKIBETİNİ (kesinleşti / bozuldu / kaldırıldı …) yazan ÜRETİCİ adım yoktu —
  bozulmuş bir karar LEHE damgalanıp dilekçeye girebiliyordu. Karar #4:
  araç birincil, avukat beyanı GÖRÜNÜR (sınıf etiketi kütükte ve kayıtta).
- P1-8/A-11/B-5: meslek sırrının en sık sızma yolu dış çağrı değil, `_oa/`
  kökünün bulut senkron klasöründe (OneDrive/Google Drive/Dropbox …) yaşaması
  — Layer 0 dış çağrıyı korur, cihazı korumaz. `init` görünür uyarır +
  `_oa/defter/senkron-uyari.json` bırakır (DURUM.md türetimi pipeline_kayit'te).

Testler tmp_path altında izole koşar; kimlikler sentetiktir (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"
DENETIM = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
           / "ictihat_muhakeme_denetim.py")
GIZLILIK_SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-gizlilik" / "SKILL.md"
GIZLILIK_DESEN = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-gizlilik" / "references"
                  / "gizlilik-desenleri.md")


def _load():
    spec = importlib.util.spec_from_file_location("v0516_d_oa_hafiza", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


oh = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _denetim_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(DENETIM)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _init(kok):
    kod, cikti = _cli(["init", "--dosya", "Test Dosyası", "--kok", str(kok)], cwd=kok)
    assert kod == 0, cikti
    return cikti


KUNYE = "Yargıtay 4. HD, E. 2099/1234, K. 2099/5678, T. 12.09.2099"
DOKUM_METIN = (
    "Yargıtay 4. HD, E. 2099/1234, K. 2099/5678 sayılı kararın tam metni: "
    "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır; "
    "TBK m.49 uyarınca tazminat sorumluluğu doğar.\n"
)
ILGILI_KISIM = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"
BAG_METNI = ("Bu karar, dosyamızdaki trafik kazası olgusuyla aynı unsur setini "
             "içeriyor; TBK m.49'un büyük önermesini somutlaştıran doğrudan emsaldir.")


def _getir_args(kok, sonuc=KUNYE, damga="LEHE", ek=()):
    return (["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
             "--sonuc", sonuc, "--damga", damga, "--bag", BAG_METNI,
             "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
             "--dokum-sinifi", "tam-metin", "--kok", str(kok)] + list(ek))


def _kutuk(kok):
    return (kok / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")


def _muhakeme(kok):
    return (kok / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# K5 — AKIBET ÜRETİCİSİ
# ═══════════════════════════════════════════════════════════════════════════

def test_k5_akibet_arac_kaynagi_kayit_ve_kutuge_yazilir(tmp_path):
    """--akibet + arac:<ad> kaynağı: muhakeme kaydında **AKIBET:** ve
    **AKIBET-KAYNAK:** satırları (KUNYE/DAMGA ile AYNI blokta, tek satır),
    kütük hücresinde AKIBET=<enum> tokenı + GÖRÜNÜR 'araç' sınıf etiketi."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "kesinlesti", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    metin = _muhakeme(tmp_path)
    assert "**AKIBET:** kesinlesti\n" in metin
    assert "**AKIBET-KAYNAK:** araç: arac:ictihat_getir\n" in metin
    # Aynı blokta: KUNYE ile İLGİLİ-KISIM başlığı arasında.
    blok = metin.split("**KUNYE:**", 1)[1].split("## İLGİLİ-KISIM", 1)[0]
    assert "**AKIBET:**" in blok and "**DAMGA:** LEHE" in blok
    kutuk = _kutuk(tmp_path)
    assert "DAMGA=LEHE" in kutuk
    assert "AKIBET=kesinlesti" in kutuk
    assert "AKIBET-KAYNAK=araç" in kutuk


def test_k5_akibet_avukat_beyani_sinifi_gorunur(tmp_path):
    """Kaynak 'arac:' ile başlamıyorsa sınıf 'avukat beyanı'dır ve bu etiket
    hem kayıtta hem kütükte GÖRÜNÜR (Karar #4: araç birincil, beyan görünür)."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "kesinlesmedi",
        "--akibet-kaynak", "UYAP dosya kapağı — temyiz incelemesi sürüyor"]), cwd=tmp_path)
    assert kod == 0, cikti
    metin = _muhakeme(tmp_path)
    assert "**AKIBET:** kesinlesmedi\n" in metin
    assert "**AKIBET-KAYNAK:** avukat beyanı: UYAP dosya kapağı — temyiz incelemesi sürüyor\n" in metin
    kutuk = _kutuk(tmp_path)
    assert "AKIBET=kesinlesmedi" in kutuk
    assert "AKIBET-KAYNAK=avukat beyanı" in kutuk


def test_k5_akibet_kaynaksiz_ret(tmp_path):
    """--akibet verildiğinde --akibet-kaynak ZORUNLU (RET, yan etkisiz)."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=["--akibet", "bozuldu"]), cwd=tmp_path)
    assert kod != 0, cikti
    assert "--akibet-kaynak" in cikti
    assert not (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").exists()
    assert "AKIBET=" not in _kutuk(tmp_path)


def test_k5_akibet_kaynak_akibetsiz_ret(tmp_path):
    """--akibet-kaynak tek başına (akıbet yokken) sessizce düşmez — RET."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod != 0, cikti
    assert "--akibet" in cikti


def test_k5_akibet_aramada_ret(tmp_path):
    """ARAMA sınıfında --akibet RET (sessiz düşme yok): arama tam metin
    döndürmez, akıbet beyanı GETİR + --damga ritüeline aittir."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "trafik kazası illiyet TBK 49",
         "--sonuc", "birkaç aday künye bulundu", "--akibet", "kesinlesti",
         "--akibet-kaynak", "arac:ictihat_ara", "--kok", str(tmp_path)],
        cwd=tmp_path)
    assert kod != 0, cikti
    assert "akıbet" in cikti.lower() or "akibet" in cikti.lower()
    assert "AKIBET=" not in _kutuk(tmp_path)


def test_k5_akibet_mevzuat_kaydinda_ret(tmp_path):
    """mevzuat_getir kaydında --akibet RET — sessiz düşme yok (E3 damga
    düşürmesinden farklı: akıbet, damgasız kayıtta anlamsız; fail-closed)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "mevzuat_getir", "--sorgu", "TBK m.49",
         "--sonuc", "TBK m.49 — haksız fiil", "--akibet", "kesinlesti",
         "--akibet-kaynak", "arac:mevzuat_getir", "--kok", str(tmp_path)],
        cwd=tmp_path)
    assert kod != 0, cikti
    assert "AKIBET=" not in _kutuk(tmp_path)


def test_k5_akibet_gecersiz_enum_ret(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "onandi", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod != 0, cikti


@pytest.mark.parametrize("sonuc,beklenen", [
    (KUNYE + " — KESİNLEŞTİ", "kesinlesti"),
    (KUNYE + " (kesinleşti)", "kesinlesti"),
    (KUNYE + " — KESİNLEŞMEDİ, temyizde", "kesinlesmedi"),
    (KUNYE + " kesinleşmedi", "kesinlesmedi"),
    (KUNYE + " — KESINLESMEDI", "kesinlesmedi"),
])
def test_k5_otomatik_akis_sonuc_metninden(tmp_path, sonuc, beklenen):
    """--akibet verilmemişse --sonuc'taki KESİNLEŞTİ/KESİNLEŞMEDİ (büyük/küçük
    harf duyarsız, İ/I katlamalı) otomatik akıbet + kaynak arac:<arac> üretir
    ve [BİLGİ] satırıyla GÖRÜNÜR kılınır (sessiz değil)."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, sonuc=sonuc), cwd=tmp_path)
    assert kod == 0, cikti
    assert "[BİLGİ] akıbet arama sonucundan otomatik alındı" in cikti
    metin = _muhakeme(tmp_path)
    assert f"**AKIBET:** {beklenen}\n" in metin
    assert "**AKIBET-KAYNAK:** araç: arac:ictihat_getir\n" in metin
    assert f"AKIBET={beklenen}" in _kutuk(tmp_path)


def test_k5_otomatik_akis_acik_akibete_dokunmaz(tmp_path):
    """Açık --akibet varsa metin sezgisi devreye GİRMEZ (açık beyan üstün)."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, sonuc=KUNYE + " — kesinleşti", ek=[
        "--akibet", "bozuldu", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    assert "otomatik alındı" not in cikti
    assert "**AKIBET:** bozuldu\n" in _muhakeme(tmp_path)


def test_k5_akibet_ifadesi_olmayan_sonucta_akibet_yazilmaz(tmp_path):
    """Sezgi yoksa satır/hücre ÜRETİLMEZ — eski çıktı biçimi birebir korunur."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path), cwd=tmp_path)
    assert kod == 0, cikti
    assert "AKIBET" not in _muhakeme(tmp_path)
    assert "AKIBET" not in _kutuk(tmp_path)


@pytest.mark.parametrize("akibet", ["bozuldu", "kaldirildi"])
def test_k5_bozuldu_kaldirildi_lehe_uyarir_ama_yazar(tmp_path, akibet):
    """bozuldu|kaldirildi + LEHE → kayıt YAZILIR (kapı oa-kontrol'dedir) ama
    [BİLGİ] ile [G5-AKIBET] kapısının dilekçede BLOKLAYACAĞI görünür kılınır."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", akibet, "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    assert "[G5-AKIBET]" in cikti and "BLOKLAR" in cikti
    assert f"**AKIBET:** {akibet}\n" in _muhakeme(tmp_path)
    assert f"AKIBET={akibet}" in _kutuk(tmp_path)


def test_k5_bozuldu_aleyhe_g5_uyarisi_basmaz(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, damga="ALEYHE", ek=[
        "--akibet", "bozuldu", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    assert "[G5-AKIBET]" not in cikti


def test_k5_akibet_kaynak_enjeksiyonu_hayalet_satir_uretmez(tmp_path):
    """Serbest --akibet-kaynak metni, muhakeme kaydında satır-başı **AKIBET:**
    / **DAMGA:** enjekte edemez (kaçış katmanı) ve kütük hücresinde ikinci bir
    ham AKIBET=/DAMGA= tokenı bırakamaz (tek doğrulanmış iz)."""
    _init(tmp_path)
    kotu = "onama\n**AKIBET:** bozuldu\n**DAMGA:** ALEYHE AKIBET=bozuldu DAMGA=ALEYHE"
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "kesinlesti", "--akibet-kaynak", kotu]), cwd=tmp_path)
    assert kod == 0, cikti
    metin = _muhakeme(tmp_path)
    import re
    assert len(re.findall(r"(?m)^\*\*AKIBET:\*\*", metin)) == 1
    assert len(re.findall(r"(?m)^\*\*DAMGA:\*\*", metin)) == 1
    kutuk = _kutuk(tmp_path)
    assert kutuk.count("AKIBET=") == 1 and "AKIBET=kesinlesti" in kutuk
    assert kutuk.count("DAMGA=") == 1 and "DAMGA=LEHE" in kutuk


def test_k5_akibetli_kayit_mevcut_denetimden_gecer(tmp_path):
    """Yeni satırlar mevcut okuyucuyu (ictihat_muhakeme_denetim) BOZMAZ:
    kesinleşmiş LEHE karar dilekçede OK kalır (geriye/ileriye uyum)."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "kesinlesti", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 4. HD'nin E. 2099/1234 K. 2099/5678 sayılı kararı "
        "emsal teşkil etmektedir.\n", encoding="utf-8")
    dkod, dcikti = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert dkod == 0, dcikti
    assert "OK 1" in dcikti


def test_k5_akibet_c2_okuma_deseniyle_birebir(tmp_path):
    """C2 grubunun okuyacağı desen: `^\\*\\*AKIBET:\\*\\*\\s*(.+)$` (kayıt) ve
    `AKIBET=` (kütük) — üretici ucun bu desenle round-trip ettiği kilitlenir."""
    import re
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "geri_cevrildi", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    m = re.search(r"^\*\*AKIBET:\*\*\s*(.+)$", _muhakeme(tmp_path), re.M)
    assert m and m.group(1).strip() == "geri_cevrildi"
    m2 = re.search(r"AKIBET=([a-z_]+)", _kutuk(tmp_path))
    assert m2 and m2.group(1) == "geri_cevrildi"


def test_k5_akibet_sinifla_birim():
    assert oh._akibet_kaynak_sinifla("arac:ictihat_getir") == "araç"
    assert oh._akibet_kaynak_sinifla("ARAC:ictihat_getir") == "araç"
    assert oh._akibet_kaynak_sinifla("Yargıtay onama ilamı elimde") == "avukat beyanı"
    assert oh._akibet_kaynak_sinifla("araç:ictihat_getir") == "araç"


@pytest.mark.parametrize("metin,beklenen", [
    ("… KESİNLEŞTİ", "kesinlesti"),
    ("… Kesinleşti.", "kesinlesti"),
    ("… kesinleşmedi", "kesinlesmedi"),
    ("… KESİNLEŞMEDİ", "kesinlesmedi"),
    ("… KESINLESTI", "kesinlesti"),
    ("… onandı", None),
    ("", None),
])
def test_k5_sonuc_akibet_sezgisi_birim(metin, beklenen):
    assert oh._sonuc_akibet_sezgisi(metin) == beklenen


# ═══════════════════════════════════════════════════════════════════════════
# P1-8 / A-11 / B-5 — SENKRON KLASÖR UYARISI (init)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("parca", [
    "OneDrive", "onedrive", "OneDrive - Sirket AS", "Google Drive", "GoogleDrive",
    "My Drive", "Dropbox", "Dropbox (Personal)", "iCloudDrive", "iCloud Drive",
    "Box Sync", "Nextcloud", "Syncthing",
])
def test_p18_senkron_desen_bul_yakalar(tmp_path, parca):
    yol = str(tmp_path / parca / "dava-klasoru")
    assert oh._senkron_desen_bul(yol) is not None


@pytest.mark.parametrize("parca", ["dava", "Belgeler", "onedrivelike", "dropboxes", "Drive"])
def test_p18_senkron_desen_bul_normal_kok_yakalamaz(tmp_path, parca):
    yol = str(tmp_path / parca / "dosya")
    assert oh._senkron_desen_bul(yol) is None


def test_p18_init_onedrive_kokunde_uyarir_ve_json_yazar(tmp_path):
    kok = tmp_path / "OneDrive" / "dava"
    kok.mkdir(parents=True)
    cikti = _init(kok)
    assert "UYARI" in cikti and "SENKRON" in cikti.upper()
    assert "m.36" in cikti  # Av.K. m.36 meslek sırrı
    j = kok / "_oa" / "defter" / "senkron-uyari.json"
    assert j.is_file()
    d = json.loads(j.read_text(encoding="utf-8"))
    assert set(d) >= {"yol", "desen", "zaman"}
    assert "onedrive" in d["desen"].lower()
    assert d["yol"].replace("\\", "/").endswith("OneDrive/dava")


def test_p18_init_normal_kokte_uyarmaz_ve_json_yok(tmp_path):
    kok = tmp_path / "dava"
    kok.mkdir()
    cikti = _init(kok)
    assert "SENKRON" not in cikti.upper()
    assert not (kok / "_oa" / "defter" / "senkron-uyari.json").exists()


def test_p18_init_bayat_senkron_uyarisini_gorunur_kaldirir(tmp_path):
    """Kök artık senkron deseninde değilse önceki init'ten kalan bayat JSON
    sessizce kalmaz: [BİLGİ] ile kaldırılır (bayat uyarı = yanlış defter)."""
    kok = tmp_path / "dava"
    kok.mkdir()
    (kok / "_oa" / "defter").mkdir(parents=True)
    (kok / "_oa" / "defter" / "senkron-uyari.json").write_text(
        json.dumps({"yol": "eski", "desen": "OneDrive", "zaman": "x"}), encoding="utf-8")
    cikti = _init(kok)
    assert "[BİLGİ]" in cikti and "senkron-uyari.json" in cikti
    assert not (kok / "_oa" / "defter" / "senkron-uyari.json").exists()


# ═══════════════════════════════════════════════════════════════════════════
# oa-gizlilik belge bağı
# ═══════════════════════════════════════════════════════════════════════════

def test_gizlilik_skill_senkron_klasor_riski_bolumu():
    metin = GIZLILIK_SKILL.read_text(encoding="utf-8")
    assert "## Senkron klasör riski" in metin
    for anahtar in ("OneDrive", "VeraCrypt", "BitLocker", "senkron-uyari.json",
                    "Layer 0", "m.36", "KVKK m.6", "Mevzuat MCP teyit 2026-09-06"):
        assert anahtar in metin, anahtar


def test_gizlilik_desenleri_senkron_listesi_ve_init_isaretcisi():
    metin = GIZLILIK_DESEN.read_text(encoding="utf-8")
    assert "Senkron" in metin
    for desen in ("OneDrive", "Google Drive", "Dropbox", "iCloud", "Box Sync",
                  "Nextcloud", "Syncthing"):
        assert desen in metin, desen
    assert "oa_hafiza.py init" in metin
    assert "senkron-uyari.json" in metin


# ═══════════════════════════════════════════════════════════════════════════
# Tamamlama turu (2026-09-07) — sessiz-düşme ve C2 sözleşme kilitleri
# ═══════════════════════════════════════════════════════════════════════════

def test_k5_aramada_akibet_ifadesi_sessiz_gecilmez(tmp_path):
    """ARAMA kaydında --sonuc «KESİNLEŞTİ» taşıyorsa akıbet İŞLENMEZ ama
    SESSİZCE de geçilmez: [BİLGİ] ile GETİR + --damga ritüeline yönlendirir;
    kütüğe AKIBET= hücresi YAZILMAZ (sessiz atlama yasağı, K5)."""
    _init(tmp_path)
    kod, cikti = _cli(["teyit", "--arac", "ictihat_ara", "--sorgu", "TBK m.49 illiyet",
                       "--sonuc", KUNYE + " — KESİNLEŞTİ", "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    assert "[BİLGİ]" in cikti and "İŞLENMEZ" in cikti and "GETİR" in cikti
    assert "AKIBET=" not in _kutuk(tmp_path)


def test_k5_akibet_damgasiz_getirde_ret_yan_etkisiz(tmp_path):
    """GETİR + --akibet ama --damga yok → RET; kütük/muhakeme yazılmaz."""
    _init(tmp_path)
    args = _getir_args(tmp_path, ek=["--akibet", "kesinlesti",
                                     "--akibet-kaynak", "arac:ictihat_getir"])
    i = args.index("--damga")
    del args[i:i + 2]
    kod, cikti = _cli(args, cwd=tmp_path)
    assert kod != 0 and "RET" in cikti
    assert "AKIBET" not in _kutuk(tmp_path)
    assert not (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").exists()


def test_k5_kutuk_hucresi_damga_ile_ayni_duzende(tmp_path):
    """Kütük satırında AKIBET= hücresi DAMGA= ile AYNI sütunda (5-sütun /
    7-hücre satır; sonuç hücresi = 4. indeks) ve DAMGA=…'dan SONRA gelir —
    C2 `kunye_ortak._kutukten_son_token` bu hücreyi `AKIBET=` ile tarar."""
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "kaldirildi", "--akibet-kaynak", "arac:ictihat_getir"]), cwd=tmp_path)
    assert kod == 0, cikti
    satirlar = [s for s in _kutuk(tmp_path).splitlines()
                if s.startswith("|") and "AKIBET=" in s]
    assert len(satirlar) == 1
    hucreler = satirlar[0].split("|")
    assert len(hucreler) == 7, satirlar[0]
    sonuc_hucresi = hucreler[4]
    assert "DAMGA=LEHE" in sonuc_hucresi and "AKIBET=kaldirildi" in sonuc_hucresi
    assert sonuc_hucresi.index("DAMGA=") < sonuc_hucresi.index("AKIBET=")
    # Kaynak etiketi tek doğrulanmış tokenın ARDINDAN gelir, ikinci AKIBET= üretmez.
    assert sonuc_hucresi.count("AKIBET=") == 1


def _c2_okuyucu():
    """Depo içi C2 okuyucusunu (ictihat_muhakeme_denetim + kunye_ortak) yükler;
    AKIBET tüketicisi henüz birleşmemişse (main tabanı) None döner → skip."""
    kdir = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
    if not (kdir / "ictihat_muhakeme_denetim.py").is_file():
        return None
    eski = list(sys.path)
    sys.path.insert(0, str(kdir))
    try:
        spec = importlib.util.spec_from_file_location(
            "v0516_d_c2_imd", kdir / "ictihat_muhakeme_denetim.py")
        imd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(imd)
        spec2 = importlib.util.spec_from_file_location(
            "v0516_d_c2_ko", kdir / "kunye_ortak.py")
        ko = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(ko)
    finally:
        sys.path[:] = eski
    if not hasattr(imd, "AKIBET_LINE_RE") or not hasattr(ko, "kutukten_son_akibet"):
        return None
    return imd, ko


def test_k5_c2_tuketicisi_uretici_ciktisini_okur(tmp_path):
    """Sözleşme kilidi (D üretici ↔ C2 tüketici): C2'nin `MuhakemeKaydi`
    ayrıştırıcısı **AKIBET:** satırından enum'u, `kutukten_son_akibet` kütük
    hücresinden aynı enum'u okumalı. C2 henüz birleşmemişse gerekçeli atlanır
    (entegrasyonda yeşil olmalı)."""
    okuyucu = _c2_okuyucu()
    if okuyucu is None:
        pytest.skip("C2 AKIBET tüketicisi bu ağaçta yok (main tabanı) — entegrasyonda koşar")
    imd, ko = okuyucu
    _init(tmp_path)
    kod, cikti = _cli(_getir_args(tmp_path, ek=[
        "--akibet", "bozuldu", "--akibet-kaynak", "UYAP dosya kapağı — bozma ilamı"]),
        cwd=tmp_path)
    assert kod == 0, cikti
    kayit_yolu = tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md"
    metin = kayit_yolu.read_text(encoding="utf-8")
    m = imd.AKIBET_LINE_RE.search(metin)
    assert m and imd._akibet_normalize(m.group(1)) == "bozuldu"
    m2 = imd.AKIBET_KAYNAK_LINE_RE.search(metin)
    assert m2 and m2.group(1).strip().startswith("avukat beyanı:")
    kutuk = tmp_path / "_oa" / "teyit" / "kunye-teyit.md"
    assert ko.kutukten_son_akibet(str(kutuk), "2099/1234", "2099/5678") == "bozuldu"


def test_p18_senkron_json_zaman_ve_yol_alanlari(tmp_path):
    """senkron-uyari.json alan sözleşmesi: yol = init'in gördüğü mutlak kök,
    desen = eşleşen yol parçası (orijinal yazım), zaman = ISO-8601 damgası."""
    import re
    kok = tmp_path / "Dropbox (Personal)" / "dava"
    kok.mkdir(parents=True)
    _init(kok)
    d = json.loads((kok / "_oa" / "defter" / "senkron-uyari.json").read_text(encoding="utf-8"))
    assert d["desen"] == "Dropbox (Personal)"
    assert pathlib.Path(d["yol"]).resolve() == kok.resolve()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", d["zaman"]), d["zaman"]
