# -*- coding: utf-8 -*-
"""oa-dilekce / dilekce_denetim.py — v0.5.8.5 saha kuralları (346 dersleri).

Dört yeni kural + istisna defteri yazıcısı:
  [Y] HAVADA-KALAN ALINTI — dört sınıf: (a) akış-bağlı alıntı DOKUNULMAZ,
      (b) '...' ile kesilip kapanış kalıbı taşımadan biten alıntı BLOK,
      (c) paragraf sonunda kapanmayan tırnak BLOK, (d) alıntı-dışı serbest
      '...' yalnız UYARI. Saha dersi: sınıflandırma önce gelir — akış-içi
      alıntıya kapanış eklemek metni bozar; (a) sınıfının temiz kaldığının
      kanıtı bu dosyadadır.
  [M] MADDE NUMARASI SÜREKLİLİĞİ — atlama + MÜKERRERLİK (uyarı sınıfı;
      bölüm başına 1'den yeniden başlama meşrudur, uyarı üretmez).
  [N] ÇIPLAK KISALTMA — açılımsız 2+ büyük harfli kısaltma uyarısı; birebir
      alıntı (tırnak içi) MUAF; yaygın hukuki kısaltmalar beyaz listede.
  [T] TESLİME-HAZIR MAKBUZ KAPISI — 'TESLİME HAZIR' ibaresi var ama
      _oa/defter/teslim-makbuz.json yok/geçersiz → makbuzsuz hazır-beyanı
      (BLOK sınıfı görünür ihlal).
  İstisna defteri — _oa/defter/istisna-kayitlari.jsonl append-only ortak şema.

GİZLİLİK (m.7): tüm senaryolar tmp_path + sentetik desenler ('2024/123 Esas'
gibi uydurma); gerçek dava no / kişi adı / gerçek yol YOKTUR.
"""
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
          / "scripts" / "dilekce_denetim.py")


def _load():
    assert SCRIPT.is_file(), f"dilekce_denetim.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("dilekce_denetim_v0585", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()


# Sekiz zorunlu unsuru taşıyan, [A]/[B]/[D] kapılarından temiz geçen sentetik
# taban taslak — yeni kuralların exit-koduna etkisi bunun üstüne kurulur.
TEMIZ_TASLAK = (
    "# Örnek 1. İş Mahkemesi Başkanlığına\n\n"
    "## Taraflar\n"
    "Davacı: Ahmet Yılmaz, Adres: Örnek Mah.\n"
    "Davalı: Örnek A.Ş., Adres: Örnek Cad.\n"
    "Vekil: Av. Test Vekil\n\n"
    "## Konu\nİşçilik alacaklarına ilişkindir (2024/123 Esas).\n\n"
    "## Açıklamalar\n1. Davacının işe giriş vakıası.\n2. İkinci vakıa.\n\n"
    "## Hukuki Sebepler\n4857 sayılı Kanun ve ilgili hukuki dayanaklar.\n\n"
    "## Deliller\nTanık, bilirkişi incelemesi, bordro.\n\n"
    "## Netice-i Talep\n"
    "Davanın kabulüne karar verilmesini saygıyla talep ederiz.\n\n"
    "01.01.2026\nAv. Test Vekil\nimza\n"
)


def _main_kos(argv):
    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py"] + argv
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek
    return exc.value.code


# ── [Y] HAVADA-KALAN ALINTI — sınıf (a): akış-bağlı alıntı DOKUNULMAZ ───────

def test_y_akis_bagli_seklinde_temiz():
    """(a) '... şeklinde' ile gramerce devam eden alıntı TEMİZ kalmalı —
    saha dersi: bu sınıfa kapanış eklemek metni bozar, kural körlemesine
    uygulanamaz."""
    metin = ('Mahkeme, "fesih son çare olmalıdır..." şeklinde '
             "değerlendirme yapmıştır.")
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [], f"akış-bağlı alıntı BLOK üretmemeli: {bloklar}"
    assert uyarilar == [], f"akış-bağlı alıntı uyarı da üretmemeli: {uyarilar}"


def test_y_akis_bagli_ifadesiyle_temiz():
    metin = ('İlk derece kararında "...son çare ilkesi gözetilmelidir..." '
             "ifadesiyle bu husus vurgulanmıştır.")
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [] and uyarilar == []


def test_y_akis_bagli_denilmis_devaminda_temiz():
    metin = ('Kararda "fesih son çaredir..." denilmiş; devamında somut '
             "olay incelenmiştir.")
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [] and uyarilar == []


def test_y_akis_bagli_sonucuna_varilmistir_temiz():
    metin = ('Bilirkişi raporunda "ispat yükü karşılanmamıştır..." '
             "sonucuna varılmıştır.")
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [] and uyarilar == []


def test_y_kapanis_kalibi_denilmistir_temiz():
    metin = ('Emsal kararda "eşit davranma borcu esastır..." denilmiştir.')
    bloklar, _uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == []


def test_y_ellipsissiz_kisa_alinti_temiz():
    """'...' ile kesilmemiş kısa tırnak alıntısı (terim aktarımı) hiçbir
    sınıfa girmez — sahte pozitif üretilmemeli."""
    metin = 'Sözleşmedeki "haklı neden" kavramı somut olayda gerçekleşmemiştir.'
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [] and uyarilar == []


# ── [Y] sınıf (b): havada-kalan alıntı BLOK ────────────────────────────────

def test_y_havada_kalan_paragraf_sonu_blok():
    """(b) tırnak '...' ile kesilmiş, kapanış kalıbı yok, paragraf bitmiş."""
    metin = 'Emsal kararda "eşit davranma borcu işverenin temel yükümüdür..."'
    bloklar, _uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar, "havada-kalan alıntı BLOK sınıfı bulgu üretmeli"
    assert any("havada" in b.lower() for b in bloklar), bloklar


def test_y_havada_kalan_kapanissiz_devam_cumlesi_blok():
    """(b) alıntıdan sonra cümle var ama kapanış/akış kalıbı DEĞİL —
    alıntı yine havada kalmıştır."""
    metin = ('Emsal kararda "işveren eşit davranmakla yükümlüdür..." '
             "Bu nedenle davanın kabulü gerekir.")
    bloklar, _uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar, "kapanış kalıbı taşımayan kesik alıntı BLOK olmalı"


def test_y_kivrik_tirnak_da_taninir_blok():
    metin = "Kararda “fesih son çaredir...”"
    bloklar, _uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar, "kıvrık tırnaklı havada-kalan alıntı da yakalanmalı"


# ── [Y] sınıf (c): kapanmayan tırnak BLOK ──────────────────────────────────

def test_y_kapanmayan_tirnak_blok():
    metin = 'Kararda "eşit davranma borcu esastır denilmektedir.'
    bloklar, _uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar, "paragraf sonunda kapanmayan tırnak BLOK olmalı"
    assert any("kapan" in b.lower() for b in bloklar), bloklar


# ── [Y] sınıf (d): alıntı-dışı serbest '...' yalnız UYARI ──────────────────

def test_y_serbest_uc_nokta_uyari_ama_blok_degil():
    metin = "Bu husus tartışmalıdır... ancak sonucu değiştirmez."
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [], f"serbest '...' BLOK üretmemeli: {bloklar}"
    assert uyarilar, "alıntı-dışı serbest '...' uyarı üretmeli"


def test_y_markdown_blok_alinti_satiri_taranmaz():
    """'>' satırları birebir alıntı gövdesidir ([B4]'ün alanı) — içindeki
    '...' [Y]'nin serbest-üç-nokta uyarısına GİRMEZ."""
    metin = "> Karardan birebir alıntı ... devamı kısaltıldı.\n\nAçıklama paragrafı.\n"
    bloklar, uyarilar = dd.havada_kalan_alinti_denetle(metin)
    assert bloklar == [] and uyarilar == []


# ── [Y] CLI ucu: BLOK sınıfı exit 1, akış-bağlı temiz exit 0 ───────────────

def test_main_y_havada_kalan_teslimi_durdurur(tmp_path, capsys):
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        TEMIZ_TASLAK + '\nEmsal kararda "eşit davranma borcu esastır..."\n',
        encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path)])
    cikti = capsys.readouterr().out
    assert "[Y]" in cikti
    assert kod == 1, cikti


def test_main_y_akis_bagli_alinti_teslimi_durdurmaz(tmp_path, capsys):
    """(a) sınıfının uçtan-uca kanıtı: aynı alıntı '... şeklinde' akışına
    bağlıyken exit 0 — kurala DOKUNULMAZLIK."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        TEMIZ_TASLAK + '\nEmsal kararda "eşit davranma borcu esastır..." '
        "şeklinde vurgu yapılmıştır.\n",
        encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path)])
    cikti = capsys.readouterr().out
    assert kod == 0, cikti


# ── [M] MADDE NUMARASI SÜREKLİLİĞİ ─────────────────────────────────────────

def test_m_atlama_uyari_uretir():
    metin = "## Açıklamalar\n1. Birinci vakıa.\n2. İkinci vakıa.\n4. Dördüncü vakıa.\n"
    uyarilar = dd.madde_numara_uyarilari(metin)
    assert any("atla" in u.lower() for u in uyarilar), uyarilar


def test_m_mukerrer_uyari_uretir():
    metin = "## Açıklamalar\n1. Birinci.\n2. İkinci.\n2. Yine ikinci.\n3. Üçüncü.\n"
    uyarilar = dd.madde_numara_uyarilari(metin)
    assert any("mükerrer" in u.lower() for u in uyarilar), uyarilar


def test_m_saha_vakasi_eklenen_blok_mukerrerligi_gorunur():
    """346 sahası: ekleme sırasında 1-5 bloğu ikinci kez doğmuştu — aynı
    bölümde tekrar eden numaralar GÖRÜNÜR bulgu olmalı."""
    satirlar = [f"{i}. Vakıa {i}." for i in range(1, 6)]
    metin = "## Açıklamalar\n" + "\n".join(satirlar + satirlar) + "\n"
    uyarilar = dd.madde_numara_uyarilari(metin)
    assert any("mükerrer" in u.lower() for u in uyarilar), uyarilar


def test_m_bolum_basina_yeniden_baslama_mesru():
    """Bölüm başlığından sonra 1'den yeniden başlamak meşru yazım tarzıdır —
    uyarı ÜRETİLMEMELİ (sıra bozukluğu BLOK olmadığı gibi sahte alarm da yok)."""
    metin = ("## Açıklamalar\n1. Birinci.\n2. İkinci.\n\n"
             "## Netice-i Talep\n1. Kabulüne,\n2. Giderlerin yükletilmesine.\n")
    assert dd.madde_numara_uyarilari(metin) == []


def test_m_tarih_satiri_madde_numarasi_sayilmaz():
    metin = "## Açıklamalar\n1. Vakıa.\n2. Vakıa.\n\n01.01.2026\nimza\n"
    assert dd.madde_numara_uyarilari(metin) == []


def test_m_uyari_sinifi_exit_koduna_dokunmaz(tmp_path, capsys):
    """[M] uyarı sınıfıdır — atlama olsa da teslim BLOKLANMAZ (exit 0)."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        TEMIZ_TASLAK.replace("2. İkinci vakıa.", "4. Dördüncü vakıa."),
        encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path)])
    cikti = capsys.readouterr().out
    assert "[M]" in cikti
    assert "atla" in cikti.lower()
    assert kod == 0, cikti


# ── [N] ÇIPLAK KISALTMA ────────────────────────────────────────────────────

def test_n_acilimsiz_kisaltma_uyari():
    metin = "Müvekkil hakkında TKY raporu düzenlenmiş ve dosyaya sunulmuştur."
    uyarilar = dd.ciplak_kisaltma_uyarilari(metin)
    assert any("TKY" in u for u in uyarilar), uyarilar


def test_n_acilim_verilmisse_temiz():
    metin = ("Toplam Kalite Yönetimi (TKY) raporu düzenlenmiştir. "
             "TKY bulguları esas alınmıştır.")
    assert dd.ciplak_kisaltma_uyarilari(metin) == []


def test_n_beyaz_liste_uyari_uretmez():
    metin = ("HMK m.119, TBK m.112 ve TMK hükümleri uyarınca; AYM ve BAM "
             "içtihatları ile CMK, TTK, İYUK atıfları saklıdır.")
    assert dd.ciplak_kisaltma_uyarilari(metin) == []


def test_n_tirnak_icindeki_kisaltma_muaf():
    """Birebir alıntı içindeki kısaltma MUAF — alıntı metnine müdahale
    edilemez, açılım eklenmesi beklenemez."""
    metin = 'Kararda "TKY raporu tek başına esas alınamaz" denilmiştir.'
    assert dd.ciplak_kisaltma_uyarilari(metin) == []


def test_n_tamami_buyuk_baslik_satiri_kisaltma_sayilmaz():
    metin = "SONUÇ VE İSTEM\nDavanın kabulünü talep ederiz.\n"
    assert dd.ciplak_kisaltma_uyarilari(metin) == []


def test_n_uyari_sinifi_exit_koduna_dokunmaz(tmp_path, capsys):
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        TEMIZ_TASLAK + "\nAyrıca TKY raporu dosyaya sunulmuştur.\n",
        encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path)])
    cikti = capsys.readouterr().out
    assert "[N]" in cikti
    assert "TKY" in cikti
    assert kod == 0, cikti


# ── [T] TESLİME-HAZIR MAKBUZ KAPISI ────────────────────────────────────────

def _makbuz_yaz(kok, veri):
    defter = kok / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps(veri, ensure_ascii=False), encoding="utf-8")


def test_t_makbuzsuz_hazir_beyani_ihlal(tmp_path):
    metin = TEMIZ_TASLAK + "\nDurum: TESLİME HAZIR.\n"
    ihlaller = dd.teslime_hazir_ihlalleri(metin, str(tmp_path))
    assert ihlaller, "makbuzsuz 'TESLİME HAZIR' beyanı görünür ihlal olmalı"
    assert any("makbuzsuz hazır-beyanı" in u for u in ihlaller), ihlaller


def test_t_makbuz_varsa_temiz(tmp_path):
    _makbuz_yaz(tmp_path, {"exit_kodu": 0, "zaman": "2026-01-01T00:00:00"})
    metin = TEMIZ_TASLAK + "\nDurum: TESLİME HAZIR.\n"
    assert dd.teslime_hazir_ihlalleri(metin, str(tmp_path)) == []


def test_t_bozuk_makbuz_gecerli_sayilmaz(tmp_path):
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "teslim-makbuz.json").write_text("{bozuk json", encoding="utf-8")
    metin = "Taslak gövdesi.\n\nTESLİME HAZIR\n"
    assert dd.teslime_hazir_ihlalleri(metin, str(tmp_path)), \
        "bozuk makbuz JSON'u geçerli makbuz sayılmamalı"


def test_t_exit_kodu_sifir_olmayan_makbuz_gecerli_sayilmaz(tmp_path):
    _makbuz_yaz(tmp_path, {"exit_kodu": 1})
    metin = "TESLİME HAZIR\n"
    assert dd.teslime_hazir_ihlalleri(metin, str(tmp_path))


def test_t_oa_belgesindeki_ibare_de_yakalanir(tmp_path):
    """İbare taslakta değil klasörün _oa belgesinde olsa da yakalanmalı."""
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "09-durum.md").write_text(
        "Paket denetlendi, dosya TESLİME HAZIR.\n", encoding="utf-8")
    ihlaller = dd.teslime_hazir_ihlalleri("İbaresiz taslak gövdesi.\n", str(tmp_path))
    assert ihlaller, "_oa belgesindeki makbuzsuz hazır-beyanı da ihlaldir"


def test_t_olumsuzlanmis_gecis_beyan_sayilmaz(tmp_path):
    """pipeline_kayit'ın DURUM.md uyarı metni 'hiç TESLİME HAZIR olmamış'
    hazır-BEYANI değildir — sahte pozitif üretmemeli."""
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "DURUM.md").write_text(
        "adım-9 UYGULANDI ama teslim_paketi.py hiç TESLİME HAZIR olmamış.\n",
        encoding="utf-8")
    assert dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path)) == []


def test_t_ibare_hic_yoksa_temiz(tmp_path):
    assert dd.teslime_hazir_ihlalleri(TEMIZ_TASLAK, str(tmp_path)) == []


def test_main_t_makbuzsuz_hazir_beyani_teslimi_durdurur(tmp_path, capsys):
    taslak = tmp_path / "taslak.md"
    taslak.write_text(TEMIZ_TASLAK + "\nDurum: TESLİME HAZIR.\n", encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path)])
    cikti = capsys.readouterr().out
    assert "[T]" in cikti
    assert "makbuzsuz hazır-beyanı" in cikti
    assert kod == 1, cikti


# ── İSTİSNA DEFTERİ (ortak şema, append-only) ──────────────────────────────

def test_istisna_kaydi_append_only_ortak_sema(tmp_path):
    dd.istisna_kaydi_yaz(str(tmp_path), "yanlis-pozitif-ilani",
                         "taslak.md#Y", "akış-içi alıntı, avukat teyit etti")
    dd.istisna_kaydi_yaz(str(tmp_path), "yanlis-pozitif-ilani",
                         "taslak.md#T", "makbuz ayrı kökte üretildi")
    yol = tmp_path / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    satirlar = yol.read_text(encoding="utf-8").strip().splitlines()
    assert len(satirlar) == 2, "append-only: iki çağrı iki satır"
    for satir in satirlar:
        kayit = json.loads(satir)
        assert set(kayit) == {"zaman", "tur", "ilgili", "gerekce", "onay", "imza"}
        assert kayit["tur"] == "yanlis-pozitif-ilani"
        assert kayit["onay"] == "avukat"
        assert "dilekce_denetim" in kayit["imza"]


def test_main_istisna_gerekce_blok_dusurur_ve_deftere_yazar(tmp_path, capsys):
    """Avukat onaylı istisna: [Y]/[T] BLOK bulguları --istisna-gerekce ile
    görünür uyarıya düşer (exit 0) ve gerekçe istisna defterine append-only
    yazılır — kapı muhakemeyi ENGELLEMEZ, kaydını tutarak yol verir."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        TEMIZ_TASLAK + '\nEmsal kararda "eşit davranma borcu esastır..."\n',
        encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path),
                     "--istisna-gerekce", "alıntı bilinçli kısaltıldı, avukat inceledi"])
    cikti = capsys.readouterr().out
    assert kod == 0, cikti
    assert "istisna" in cikti.lower()
    yol = tmp_path / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    assert yol.is_file(), "istisna defteri satırı yazılmalı"
    kayit = json.loads(yol.read_text(encoding="utf-8").strip().splitlines()[0])
    assert kayit["tur"] == "yanlis-pozitif-ilani"
    assert kayit["gerekce"] == "alıntı bilinçli kısaltıldı, avukat inceledi"


def test_main_istisna_gerekce_bulgu_yokken_defter_yazilmaz(tmp_path, capsys):
    """Bulgu yokken istisna gerekçesi verilmesi defteri KİRLETMEZ —
    kayıt yalnız fiilen düşürülen bir BLOK varken atılır."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(TEMIZ_TASLAK, encoding="utf-8")
    kod = _main_kos([str(taslak), "--tip", "dava", "--taraf", "davaci",
                     "--kok", str(tmp_path),
                     "--istisna-gerekce", "gereksiz gerekçe"])
    assert kod == 0
    yol = tmp_path / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    assert not yol.exists(), "bulgu yokken istisna kaydı atılmamalı"


# ── [T] TARİHÇE MUAFİYETİ (346 prova bulgusu) ──────────────────────────────

def test_t_tarihce_dizinleri_taranmaz_yasayan_belgeler_taranir(tmp_path):
    """oturum/devir/dersler/arsiv-yerel GEÇMİŞ kayıttır — [T] taramaz (eski
    koşunun hatası kökü kalıcı bloğa çeviremez); yaşayan belge (00-TESLIM.md)
    taranmaya devam eder."""
    import importlib.util, sys
    yol = os.path.join(SCRIPTS, "dilekce_denetim.py") if "SCRIPTS" in dir() else None
    if yol is None:
        import pathlib
        yol = str(pathlib.Path(__file__).resolve().parents[1] / "plugins" /
                  "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" /
                  "dilekce_denetim.py")
    spec = importlib.util.spec_from_file_location("_dd_t_tarihce", yol)
    dd = importlib.util.module_from_spec(spec)
    sys.modules["_dd_t_tarihce"] = dd
    spec.loader.exec_module(dd)

    (tmp_path / "_oa" / "oturum").mkdir(parents=True)
    (tmp_path / "_oa" / "oturum" / "2024-01-01.md").write_text(
        "KAPANIŞ: TESLİME HAZIR denmişti (tarihçe)", encoding="utf-8")
    # yalnız tarihçede ibare → ihlal YOK
    assert dd.teslime_hazir_ihlalleri("temiz taslak", str(tmp_path)) == []
    # yaşayan belgede ibare → ihlal VAR
    (tmp_path / "_oa" / "00-TESLIM.md").write_text(
        "Durum: TESLİME HAZIR", encoding="utf-8")
    ihlaller = dd.teslime_hazir_ihlalleri("temiz taslak", str(tmp_path))
    assert len(ihlaller) == 1 and "00-TESLIM.md" in ihlaller[0]
