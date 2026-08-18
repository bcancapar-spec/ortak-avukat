# -*- coding: utf-8 -*-
"""v0.5.9 HIZLI KİP — dilekce_denetim.hizli_denetim() iç API testleri.

Sözleşme (dört ilke izdüşümü):
  * YALNIZ metin-tabanlı hızlı denetimler koşar: [Y] havada-kalan alıntı,
    [M] madde sürekliliği/mükerrerlik, [N] çıplak kısaltma, [K] cephanelik-
    ifşa, [T] teslime-hazır/yeşil-makbuz beyanı (YALNIZ kok verilmişse),
    [L] kaynak-bloğu ilk-satır yokluğu.
  * .udf/zip/npx/resmî-okuyucu bacaklarına ASLA girmez (hız şartı).
  * list[str] döner; her bulgu "[X] ..." biçiminde, en kritik (BLOK) önce.
  * Hiçbir koşulda exception sızdırmaz — bozuk girdide tek uyarı bulgusu.
  * CLI davranışı DEĞİŞMEZ (fonksiyon iç API'dir).

Script dosya-yolundan yüklenir (skill dizinleri paket değildir). Sentetik
metinler tamamen uydurmadır — gerçek dava adı/yolu YASAKTIR.
"""
import importlib.util
import json
import pathlib
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
          / "scripts" / "dilekce_denetim.py")


def _load():
    assert SCRIPT.is_file(), f"dilekce_denetim.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "dilekce_denetim_hizli_kip", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()

# Kaynak bloklu, alıntısız, kısaltmasız, tek-maddeli TEMİZ sentetik taslak —
# negatif vakaların ortak tabanı ([L] dahil hiçbir sınıf ateşlememeli).
TEMIZ = (
    "<!-- kaynaklar: taslak.md@12ab34cd · analiz.md@abcd1234 -->\n"
    "# SENTETİK MAHKEME BAŞKANLIĞINA\n"
    "1. Olay şu şekilde gelişmiştir.\n"
    "2. Talebimiz aşağıda açıklanmıştır.\n"
)


def test_fonksiyon_var_ve_liste_doner():
    assert hasattr(dd, "hizli_denetim"), "hizli_denetim iç API'si tanımlı değil"
    sonuc = dd.hizli_denetim(TEMIZ)
    assert isinstance(sonuc, list)
    assert all(isinstance(b, str) for b in sonuc)


def test_temiz_metin_bulgu_uretmez():
    assert dd.hizli_denetim(TEMIZ) == []


def test_her_bulgu_koseli_etiketle_baslar():
    kirli = TEMIZ + '\nMahkeme "gerekçe şudur ..." KISALT metnini yazdı.\n'
    for bulgu in dd.hizli_denetim(kirli):
        assert bulgu.startswith("["), f"etiketsiz bulgu: {bulgu!r}"


# ── [Y] havada-kalan alıntı ────────────────────────────────────────────────

def test_y_havada_kalan_alinti_pozitif():
    metin = TEMIZ + '\nKararda "sözleşme feshedilmiştir ..."\n'
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[Y]") for b in bulgular), bulgular


def test_y_akis_bagli_alinti_negatif():
    metin = TEMIZ + '\nKararda "sözleşme feshedilmiştir ..." şeklinde denilmiştir.\n'
    bulgular = dd.hizli_denetim(metin)
    assert not any(b.startswith("[Y]") for b in bulgular), bulgular


# ── [M] madde sürekliliği / mükerrerlik ────────────────────────────────────

def test_m_mukerrer_madde_pozitif():
    metin = TEMIZ + "\n3. Üçüncü madde.\n3. Üçüncü madde tekrar doğmuş.\n"
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[M]") and "mükerrer" in b for b in bulgular), bulgular


def test_m_atlama_pozitif():
    metin = TEMIZ + "\n5. Beşinci madde.\n9. Dokuzuncu madde.\n"
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[M]") and "atlama" in b for b in bulgular), bulgular


def test_m_bolum_basi_yeniden_baslama_negatif():
    metin = TEMIZ + "\n## YENİ BÖLÜM\n1. Yeniden birden başlamak meşrudur.\n"
    bulgular = dd.hizli_denetim(metin)
    assert not any(b.startswith("[M]") for b in bulgular), bulgular


# ── [N] çıplak kısaltma ────────────────────────────────────────────────────

def test_n_ciplak_kisaltma_pozitif():
    metin = TEMIZ + "\nBu işlemde GKT belgesi esas alınmıştır.\n"
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[N]") and "GKT" in b for b in bulgular), bulgular


def test_n_acilimli_kisaltma_negatif():
    metin = TEMIZ + "\nGenel Kontrol Tutanağı (GKT) esas alınmıştır. GKT geçerlidir.\n"
    bulgular = dd.hizli_denetim(metin)
    assert not any(b.startswith("[N]") for b in bulgular), bulgular


def test_n_beyaz_liste_negatif():
    metin = TEMIZ + "\nHMK ve TBK hükümleri uygulanır.\n"
    bulgular = dd.hizli_denetim(metin)
    assert not any(b.startswith("[N]") for b in bulgular), bulgular


# ── [K] cephanelik-ifşa ────────────────────────────────────────────────────

def test_k_cephanelik_ifsa_pozitif():
    metin = TEMIZ + "\nDavalı taraf zamanaşımı def'ini ileri sürebilir.\n"
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[K]") for b in bulgular), bulgular


def test_k_cephanelik_negatif():
    metin = TEMIZ + "\nDavalı taraf borcu ödememiştir.\n"
    bulgular = dd.hizli_denetim(metin)
    assert not any(b.startswith("[K]") for b in bulgular), bulgular


# ── [T] teslime-hazır / yeşil-makbuz beyanı (yalnız kok verilmişse) ────────

def test_t_kok_verilmisse_makbuzsuz_beyan_pozitif(tmp_path):
    metin = TEMIZ + "\nTaslak TESLİME HAZIR durumdadır.\n"
    bulgular = dd.hizli_denetim(metin, kok=str(tmp_path))
    assert any(b.startswith("[T]") for b in bulgular), bulgular


def test_t_gecerli_makbuz_varsa_negatif(tmp_path):
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    metin = TEMIZ + "\nTaslak TESLİME HAZIR durumdadır.\n"
    bulgular = dd.hizli_denetim(metin, kok=str(tmp_path))
    assert not any(b.startswith("[T]") for b in bulgular), bulgular


def test_t_kok_verilmemisse_kosulmaz():
    """kok yokken [T] CWD'ye DÜŞMEZ — hızlı kip dosya sistemine tırmanmaz."""
    metin = TEMIZ + "\nTaslak TESLİME HAZIR durumdadır.\n"
    bulgular = dd.hizli_denetim(metin)
    assert not any(b.startswith("[T]") for b in bulgular), bulgular


def test_t_yesil_makbuz_iddiasi_pozitif(tmp_path):
    metin = TEMIZ + "\nYEŞİL MAKBUZ alınmıştır.\n"
    bulgular = dd.hizli_denetim(metin, kok=str(tmp_path))
    assert any(b.startswith("[T]") for b in bulgular), bulgular


# ── [L] kaynak-bloğu ilk-satır yokluğu ─────────────────────────────────────

def test_l_kaynak_blogu_yoklugu_pozitif():
    metin = "# SENTETİK MAHKEME BAŞKANLIĞINA\n1. Olay anlatımı.\n"
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[L]") for b in bulgular), bulgular


def test_l_hashsiz_oge_pozitif():
    metin = "<!-- kaynaklar: taslak.md -->\n# BAŞLIK\n1. Olay.\n"
    bulgular = dd.hizli_denetim(metin)
    assert any(b.startswith("[L]") for b in bulgular), bulgular


def test_l_kaynak_blogu_varsa_negatif():
    bulgular = dd.hizli_denetim(TEMIZ)
    assert not any(b.startswith("[L]") for b in bulgular), bulgular


# ── sıralama: en kritik (BLOK sınıfı) önce ─────────────────────────────────

def test_blok_sinifi_uyarilardan_once_gelir(tmp_path):
    metin = (
        "# BAŞLIK (kaynak bloğu bilerek yok)\n"          # [L] uyarı
        'Kararda "borç ödenmemiştir ..."\n\n'            # [Y] BLOK
        "Taslak TESLİME HAZIR durumdadır.\n"             # [T] BLOK
        "Bu işlemde GKT belgesi esas alınmıştır.\n"      # [N] uyarı
    )
    bulgular = dd.hizli_denetim(metin, kok=str(tmp_path))
    etiketler = [b.split()[0] for b in bulgular]
    assert "[T]" in etiketler and "[Y]" in etiketler, bulgular
    son_blok = max(i for i, e in enumerate(etiketler) if e in ("[T]", "[Y]"))
    uyari_ilk = min(i for i, e in enumerate(etiketler) if e in ("[N]", "[L]"))
    assert son_blok < uyari_ilk, (
        f"BLOK sınıfı bulgular uyarılardan ÖNCE gelmeli: {etiketler}")


# ── exception sızdırmaz ────────────────────────────────────────────────────

@pytest.mark.parametrize("bozuk", [None, b"bytes girdi", 12345, ["liste"]])
def test_bozuk_girdide_exception_sizdirmaz_tek_uyari(bozuk):
    sonuc = dd.hizli_denetim(bozuk)
    assert isinstance(sonuc, list)
    assert len(sonuc) == 1, sonuc
    assert sonuc[0].startswith("["), sonuc


# ── ağır bacaklara girmez (.udf/zip/npx/resmî-okuyucu) ─────────────────────

def test_agir_bacaklara_girmez(monkeypatch):
    """subprocess/zipfile ayağı çağrılırsa test patlar — hızlı kip yalnız
    metin işler (deterministik ilke: ağır halka inline zincire taşınmaz)."""
    def _yasak(*a, **k):
        raise AssertionError("hızlı kip ağır bacağa girdi (subprocess/zip)")
    monkeypatch.setattr(dd.subprocess, "run", _yasak)
    monkeypatch.setattr(dd.zipfile, "ZipFile", _yasak)
    kirli = TEMIZ + '\nKararda "gerekçe ..." GKT ibaresi geçmektedir.\n'
    sonuc = dd.hizli_denetim(kirli)
    assert isinstance(sonuc, list)


# ── hız: 50KB sentetik taslakta < 1 sn ─────────────────────────────────────

def test_hiz_50kb_sentetik_1sn_altinda():
    paragraf = (
        "12. Sentetik vakıa anlatımı: taraflar arasındaki sözleşme uyarınca "
        "1.000 TL bedel kararlaştırılmış, GKT tutanağı düzenlenmiş ve "
        '"ifa gerçekleşmemiştir ..." şeklinde tespit yapılmıştır. '
        "Davalı taraf buna itiraz edebilir.\n\n"
    )
    metin = TEMIZ + paragraf * (50 * 1024 // len(paragraf.encode("utf-8")) + 1)
    assert len(metin.encode("utf-8")) >= 50 * 1024
    dd.hizli_denetim(TEMIZ)          # ısınma (kardeş modül import'u ölçüme girmesin)
    t0 = time.perf_counter()
    sonuc = dd.hizli_denetim(metin)
    sure = time.perf_counter() - t0
    assert isinstance(sonuc, list)
    assert sure < 1.0, f"hızlı kip {sure:.3f} sn sürdü (şart: 50KB'de < 1 sn)"
