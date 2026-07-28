# -*- coding: utf-8 -*-
"""v0.5.5 ŞERH TURU — `oa_hafiza.py teyit --arac` GÜVENLİK REGRESYONLARI.

Bu dosya, açık şerh listesindeki (Ş1/Ş2/Ş3/Ş4) KÖK ÇÖZÜMÜN ("--arac artık
BİLİNEN ARAÇ SÖZLÜĞÜ'ne casefold+strip ile eşlenir; sözlük dışı bir değer
GÜVENLİ TOKEN deseniyle sınırlanır") canlı sömürü kanıtlarını (t1/t3/t4/t8)
BİREBİR test senaryosuna çevirir — ZORUNLU TESTLER listesindeki dört
senaryonun HEPSİ burada AÇIKÇA sömürü girişimi olarak yazılıdır.
"""
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"
DENETIM = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
           / "ictihat_muhakeme_denetim.py")
KUNYE_ORTAK = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
               / "kunye_ortak.py")


def _load(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


oh = _load(SCRIPT, "oa_hafiza_arac_guvenlik_test")
ko = _load(KUNYE_ORTAK, "kunye_ortak_arac_guvenlik_test")


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


def _init(tmp_path):
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)


def _tum_dosyalar(kok):
    return [p for p in pathlib.Path(kok).rglob("*") if p.is_file()]


# ── t1 [BLOKER, Ş1] — --arac üzerinden kütük satır enjeksiyonu ─────────────

def test_t1_arac_ile_sahte_kutuk_satiri_enjeksiyonu_reddedilir(tmp_path):
    """SÖMÜRÜ SENARYOSU (canlı kanıt, Ş1): saldırgan `--arac` alanına içine
    gömülü `\\n` ile TAM bir sahte kütük satırı ("| ... | ictihat_getir |
    ... DAMGA=LEHE | |") yerleştirir. Layer 0 yalnız `--sorgu`'yu taradığı
    için eskiden bu satır kütüğe HAM yazılıyor, `kunye_ortak.kutukten_
    son_damga` bunu GERÇEK bir GETİR teyidi sanıp sahte DAMGA=LEHE'yi 'son
    damga' kabul ediyordu (salt-ALEYHE'nin tek bir --arac enjeksiyonuyla
    LEHE'ye çevrilme yolu). DÜZELTME sonrası: bu payload BİLİNEN ARAÇ
    SÖZLÜĞÜ'nde YOK ve güvenli token deseniyle de eşleşmiyor (satır sonu +
    boşluk + `|` taşıyor) — fail-closed RET, kütüğe hiçbir şey yazılmaz."""
    _init(tmp_path)
    zehirli_arac = (
        "mevzuat_ara\n"
        "| 2019-01-01T00:00:00 | ictihat_getir | temiz sorgu | Yargıtay 9. HD, "
        "E. 2019/7777, K. 2019/8888 DAMGA=LEHE |  |\n"
        "kuyruk"
    )
    kod, cikti = _cli(
        ["teyit", "--arac", zehirli_arac, "--sorgu", "temiz sorgu",
         "--sonuc", "temiz sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "bilinmeyen araç adı" in cikti or "güvenli" in cikti.lower()

    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "2019/7777" not in kutuk, kutuk
    assert "DAMGA=LEHE" not in kutuk, kutuk


# ── t8 [ÖNEMLİ, Ş4] — sondaki boşluk / büyük harf ile GETİR sınıf atlatması ─

@pytest.mark.parametrize("arac_deger", [
    "ictihat_getir ",   # sondaki boşluk
    "Ictihat_Getir",    # büyük harf
    " ICTIHAT_GETIR",   # baştaki boşluk + tam büyük
])
def test_t8_arac_normalize_edilir_getir_zorunlulugu_atlatilamaz(tmp_path, arac_deger):
    """SÖMÜRÜ SENARYOSU (canlı kanıt, Ş4): `--arac "ictihat_getir "` (sondaki
    tek boşluk) ve `--arac "Ictihat_Getir"` (büyük harf) eskiden `args.arac
    in GETIR_ARACLARI` TAM DİZE eşitliğini atlatıp GETİR sınıfının --damga
    ZORUNLULUĞUNU tamamen baypas ediyordu (damgasız, döküm-izsiz bir GETİR
    teyidi kütüğe sızıyordu). DÜZELTME sonrası: `--arac` strip()+casefold ile
    KANONİK ada normalize edilir — bu üç varyasyonun HEPSİ 'ictihat_getir'e
    eşlenir ve --damga eksikse RET alır."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", arac_deger, "--sorgu", "temiz sorgu",
         "--sonuc", "Yargıtay 9. HD, E. 2023/1111, K. 2023/2222", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "ZORUNLU" in cikti.upper()
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "DAMGA=" not in kutuk, kutuk


# ── t4 [BLOKER, Ş3] — --arac üzerinden döküm dosya adında path traversal ───

def test_t4_arac_path_traversal_reddedilir_dosya_disari_yazilmaz(tmp_path):
    """SÖMÜRÜ SENARYOSU (canlı kanıt, Ş3): `--arac "x/../../../../KACAK"` ile
    `--dokum-icerik` verildiğinde eskiden döküm dosyası `_oa/teyit/dokum/`
    dışına, hatta `_oa` kökünün dışına (`--kok` dizinine) yazılıyordu (kaynak
    evrak SALT-OKUNURDUR + 'her üretim _oa altına gider' invaryantlarının
    ikisi de kırıktı). DÜZELTME sonrası: bu payload bilinen araç sözlüğünde
    yok ve `/` karakteri güvenli token desenine UYMADIĞI için en baştan
    fail-closed RET alır — hiçbir dosya (ne `_oa` içine ne dışına) yazılmaz."""
    _init(tmp_path)
    mevcut_dosyalar = set(_tum_dosyalar(tmp_path))

    kod, cikti = _cli(
        ["teyit", "--arac", "x/../../../../KACAK", "--sorgu", "temiz sorgu",
         "--sonuc", "temiz sonuç", "--dokum-icerik", "ZARARLI ICERIK",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert not (tmp_path / "KACAK").exists()
    assert not list(tmp_path.glob("KACAK*"))

    yeni_dosyalar = set(_tum_dosyalar(tmp_path)) - mevcut_dosyalar
    assert yeni_dosyalar == set(), yeni_dosyalar
    # Kalıcı olarak: init'in ürettiği HER dosya `_oa` altındadır — bu RET
    # sonrası da hiçbir dosya bu sınırın DIŞINA taşmamıştır.
    for p in _tum_dosyalar(tmp_path):
        assert "_oa" in p.relative_to(tmp_path).parts, p


# ── t3 [BLOKER, Ş2 — EN KRİTİK] — HAYALET MUHAKEME: kütük dayanağı yok ─────

KUNYE_GERCEK = "Yargıtay 9. HD, E. 2023/1111, K. 2023/2222, T. 01.01.2023"
KUNYE_HAYALET = "4. HD, E. 2019/7777, K. 2019/8888, T. 01.01.2019"


def _kutuk_satiri_yaz(kutuk_yolu, kunye, damga, dokum_ad="a.md"):
    with open(kutuk_yolu, "a", encoding="utf-8") as f:
        f.write(f"| 2026-01-01T00:00:00 | ictihat_getir | sorgu | {kunye} "
                f"DAMGA={damga} | [döküm](_oa/teyit/dokum/{dokum_ad}) |\n")


def test_t3_hayalet_muhakeme_kutuk_dayanagi_olmadan_bloklanir(tmp_path):
    """SÖMÜRÜ SENARYOSU (canlı kanıt, Ş2 — EN KRİTİK): önce GERÇEK bir
    `teyit --damga` çağrısı yapılmış gibi kütükte bir satır VAR (bu kökte
    kütük FİİLEN kullanılıyor). Ayrıca `_oa/teyit/dokum/` içinde HİÇ bir
    `teyit` çağrısına dayanmayan (elden yerleştirilmiş) bir döküm dosyası
    VAR — içinde 'hayalet' bir künyenin (4. HD, E. 2019/7777, K. 2019/8888)
    sayıları geçiyor. Bu dökümü KAYNAK-IZI göstererek elle yazılmış bir
    muhakeme bölümü (`03-ictihat-muhakeme.md`) DAMGA=LEHE ile üretiliyor —
    hiçbir MCP çağrısı, hiçbir kütük satırı bu künyeye karşılık GELMİYOR.
    DÜZELTME ÖNCESİ: `ictihat_muhakeme_denetim.py` bu kaydı yalnızca (a)
    KAYNAK-IZI dosyası var mı (b) künye numaraları dökümde geçiyor mu (c)
    alanlar dolu mu (d) DAMGA geçerli mi denetliyordu — hiçbiri kütükte bir
    İZ arayan bir denetim İÇERMİYORDU; bu yüzden [OK] veriyordu (HAYALET
    MUHAKEME kütük dayanağı olmadan G2/G3'ten geçiyordu). DÜZELTME SONRASI:
    kütük bu kökte fiilen kullanıldığından (`kutuk_gercek_veri_var_mi`),
    hayalet künyenin kütükte HİÇBİR satırı olmadığı tespit edilir → BLOK."""
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    teyit_dizin = tmp_path / "_oa" / "teyit"

    # (1) Kütük FİİLEN kullanılıyor — GERÇEK künye için gerçek bir satır var.
    kutuk_yolu = teyit_dizin / "kunye-teyit.md"
    kutuk_yolu.write_text("| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
                          "|---|---|---|---|---|\n", encoding="utf-8")
    (dokum_dizin / "a.md").write_text(
        f"{KUNYE_GERCEK} sayılı kararın tam metni burada yer almaktadır...\n",
        encoding="utf-8")
    _kutuk_satiri_yaz(kutuk_yolu, KUNYE_GERCEK, "LEHE", dokum_ad="a.md")

    # (2) HAYALET döküm — hiçbir `teyit` çağrısına dayanmadan diskte duruyor
    # (attacker'ın elle yerleştirdiği/başka bir bağlamdan kalan bir dosya).
    (dokum_dizin / "hayalet.md").write_text(
        f"{KUNYE_HAYALET} sayılı kararın tam metni burada yer almaktadır...\n",
        encoding="utf-8")

    # (3) Hayalet muhakeme bölümü — kütükte KARŞILIĞI YOK.
    satirlar = [
        "# 02 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE_HAYALET}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/hayalet.md",
        "**DAMGA:** LEHE", "",
        "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
        "## DAVAYA-BAĞ", "...davaya bağ açıklaması...", "",
        "## AYIRT-ETME", "", "",
    ]
    (cikti_dizin / "02-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")

    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        f"Somut olayda {KUNYE_HAYALET} sayılı karar emsal teşkil etmektedir.\n",
        encoding="utf-8")

    kod, cikti = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, (
        f"HAYALET MUHAKEME (kütük dayanağı olmayan kayıt) BLOK vermeliydi:\n{cikti}")
    assert "TESLİM ENGELİ" in cikti
    assert "geçmiyor" in cikti.lower()
    assert "HAYALET MUHAKEME" in cikti


def test_t3_negatif_gercek_teyitli_kunye_kutuk_dayanagiyla_gecer(tmp_path):
    """Simetrik pozitif kontrol: kütük FİİLEN kullanılıyorken, bir muhakeme
    kaydının künyesi kütükte GERÇEKTEN bir satırla karşılanıyorsa (normal,
    dürüst akış) `kutuk_dayanagi_denetle` YANLIŞLIKLA BLOK üretmemeli."""
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    teyit_dizin = tmp_path / "_oa" / "teyit"

    kutuk_yolu = teyit_dizin / "kunye-teyit.md"
    kutuk_yolu.write_text("| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
                          "|---|---|---|---|---|\n", encoding="utf-8")
    (dokum_dizin / "a.md").write_text(
        f"{KUNYE_GERCEK} sayılı kararın tam metni burada yer almaktadır...\n",
        encoding="utf-8")
    _kutuk_satiri_yaz(kutuk_yolu, KUNYE_GERCEK, "LEHE", dokum_ad="a.md")

    satirlar = [
        "# 01 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE_GERCEK}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/a.md",
        "**DAMGA:** LEHE", "",
        "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
        "## DAVAYA-BAĞ", "...davaya bağ açıklaması...", "",
        "## AYIRT-ETME", "", "",
    ]
    (cikti_dizin / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")

    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        f"Somut olayda {KUNYE_GERCEK} sayılı karar emsal teşkil etmektedir.\n",
        encoding="utf-8")

    kod, cikti = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "OK 1" in cikti


# ── Bilinen sınır: kurulum-bağımlı FARKLI adlı bir araç REDDEDİLMEMELİ ─────

def test_bilinmeyen_ama_guvenli_token_arac_adi_kabul_edilir(tmp_path):
    """`oa-ictihat/SKILL.md` AÇIKÇA belirtir: araç adları kurulumdan
    kuruluma değişebilir (Türkçe/İngilizce eşdeğerleri). Bu yüzden BİLİNEN
    sözlük dışındaki bir ad TAMAMEN reddedilmez — yalnız güvenli TOKEN
    deseniyle ([A-Za-z0-9_.-]{1,64}) sınırlanır; böyle bir ad ARAMA/GETIR
    sınıfına GİRMEZ (mevcut 'diğer araçlar serbest kalır' davranışı).

    DÜZELTME (v0.5.5 şerh turu 2 — YENİ-2, KÜÇÜK): sözlük dışı ama güvenli
    bir token kabul edildiğinde artık GÖRÜNÜR bir UYARI basılır — aksi hâlde
    ARAMA/GETİR sınıf kurallarının (--damga zorunluluğu/yasağı) o çağrı için
    HİÇ uygulanmadığı sessizce gözden kaçıyordu (bir yazım hatası kadar ucuz
    bir 'damgasız GETİR teyidi' senaryosu, t8'in aynı sınıfı)."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "get_bedesten_document_markdown", "--sorgu", "temiz sorgu",
         "--sonuc", "temiz sonuç", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "get_bedesten_document_markdown" in kutuk
    assert "UYARI" in cikti and "sözlüğünde yok" in cikti, cikti
    assert "get_bedesten_document_markdown" in cikti


# ── YENİ-2 [KÜÇÜK] — sözlük dışı token GETİR/ARAMA sınıf kurallarını sessizce
#    atlamamalı; damgasız bir "GETİR-benzeri" ad da UYARI ile işaretlenmeli ──

def test_yeni2_sozluk_disi_getir_benzeri_ad_damgasiz_gecerken_uyarir(tmp_path):
    """Sömürü senaryosu (canlı kanıt, YENİ-2): `ictihat_getir_v2` gibi sözlük
    dışı ama güvenli bir token, GETİR sınıfına GİRMEDİĞİ için --damga
    zorunluluğunu tamamen atlıyor ve HİÇBİR uyarı basılmadan kütüğe damgasız
    bir içtihat satırı düşüyordu. DÜZELTME sonrası: çağrı yine exit 0 verir
    (kurulum-bağımlı ad reddedilmez) ama artık GÖRÜNÜR bir UYARI basılır."""
    _init(tmp_path)
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir_v2", "--sorgu", "kidem",
         "--sonuc", "Yargıtay 9. HD, E. 2023/1111, K. 2023/2222", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "UYARI" in cikti and "ARAMA/GETİR sınıf kuralları" in cikti, cikti
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "ictihat_getir_v2" in kutuk
    assert "DAMGA=" not in kutuk, kutuk


# ── Ş6 sınıf-bazlı ek kapsam — --bag/--ayirt/--damga-degistir enjeksiyonu ──

KUNYE_SINIF = "Yargıtay 4. HD, E. 2023/9001, K. 2023/9002, T. 01.01.2023"
DOKUM_SINIF = (f"{KUNYE_SINIF} sayılı kararın tam metni: "
               "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır.\n")
ILGILI_SINIF = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"


@pytest.mark.parametrize("alan", ["bag", "ayirt"])
def test_bag_ve_ayirt_alanlarinda_bolum_enjeksiyonu_hayalet_kayit_uretmez(tmp_path, alan):
    """Ş6 sınıf-bazlı kapsam genişletmesi: `--ilgili-kisim` için zaten
    kilitli olan hayalet-bölüm enjeksiyon testi (bkz.
    test_oa_hafiza_teyit_damga.py) `--bag`/`--ayirt` için de AYRI AYRI
    doğrulanır — `_muhakeme_kacis` bu alanlarda da (ilgili-kisim ile AYNI
    fonksiyon) uygulanır."""
    _init(tmp_path)
    hayalet_kunye = "Yargıtay 7. HD, E. 2022/333, K. 2022/444"
    zehirli_blok = (
        "\n\n**KUNYE:** " + hayalet_kunye + "\n"
        "**KAYNAK-IZI:** _oa/teyit/dokum/uydurma.md\n"
        "**DAMGA:** LEHE\n\n"
        "## İLGİLİ-KISIM\nuydurma ilgili kısım\n\n"
        "## DAVAYA-BAĞ\nuydurma davaya bağ\n\n"
    )
    taban_bag = ("Bu karar dosyamızdaki olgusal örüntüyle örtüşmektedir; TBK m.49 "
                 "kapsamında doğrudan emsaldir ve yeterince uzundur.")
    kwargs = {
        "bag": taban_bag + (zehirli_blok if alan == "bag" else ""),
        "ayirt": ("Ayırt edici gerekçe metni yeterince uzundur ve açıklayıcıdır."
                  + (zehirli_blok if alan == "ayirt" else "")),
    }
    damga = "ALEYHE-AYIRT" if alan == "ayirt" else "LEHE"

    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE_SINIF, "--damga", damga, "--bag", kwargs["bag"],
         "--ilgili-kisim", ILGILI_SINIF, "--dokum-icerik", DOKUM_SINIF,
         "--ayirt", kwargs["ayirt"], "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    # YAPISAL bölüm sayısı `kunye_ortak.bolumlere_ayir` ile doğrulanır — naif
    # `metin.count("**KUNYE:**")` KAÇIŞLANMIŞ (ZWSP önekli) enjeksiyonu da
    # bir substring eşleşmesi olarak SAYAR (yanlış-pozitif); YAPISAL ayraç
    # (satır-başı, kaçışsız `**KUNYE:**`) tek gerçek bölümü doğru sayar.
    bolumler = ko.bolumlere_ayir(metin)
    assert len(bolumler) == 1, metin  # hayalet bölüm YOK — tek gerçek kayıt
    assert hayalet_kunye in metin  # görünür metin kayıpsız kalır (kaçışlanmış)


def test_damga_degistir_gerekcesinde_bolum_enjeksiyonu_hayalet_kayit_uretmez(tmp_path):
    """Ş6 sınıf-bazlı kapsam: `--damga-degistir` gerekçesi de (GEÇERSİZ-
    KILINDI satırına eklenen serbest metin) `_muhakeme_kacis`'ten geçer."""
    _init(tmp_path)
    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE_SINIF, "--damga", "ALEYHE",
         "--bag", "Bu karar dosyamızdaki olgusal örüntüyle örtüşmektedir yeterince uzun.",
         "--ilgili-kisim", ILGILI_SINIF, "--dokum-icerik", DOKUM_SINIF,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    hayalet_kunye = "Yargıtay 8. HD, E. 2021/111, K. 2021/222"
    zehirli_gerekce = (
        "Yeniden inceleme sonucu kararın aslında LEHE olduğu anlaşıldı (düzeltme)."
        "\n\n**KUNYE:** " + hayalet_kunye + "\n**KAYNAK-IZI:** _oa/teyit/dokum/x.md\n"
        "**DAMGA:** LEHE\n\n## İLGİLİ-KISIM\nx\n\n## DAVAYA-BAĞ\nx\n\n"
    )
    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet düzeltme",
         "--sonuc", KUNYE_SINIF, "--damga", "LEHE",
         "--bag", "Bu karar dosyamızdaki olgusal örüntüyle örtüşmektedir yeterince uzun.",
         "--ilgili-kisim", ILGILI_SINIF, "--dokum-icerik", DOKUM_SINIF,
         "--damga-degistir", zehirli_gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 == 0, cikti2
    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    # YAPISAL bölüm sayısı (bkz. yukarıdaki test'in gerekçesi) — bu çağrı
    # doğal biçimde İKİ bölüm üretir (eski ALEYHE bölüm GEÇERSİZ-KILINDI
    # işaretiyle KORUNUR + yeni LEHE bölüm eklenir); hayalet künye yalnız
    # GEÇERSİZ-KILINDI gerekçe METNİNİN İÇİNDE (kaçışlanmış) görünür kalır.
    bolumler = ko.bolumlere_ayir(metin)
    assert len(bolumler) == 2, metin
    assert hayalet_kunye in metin


# ── t3-B [BLOKER, Ş2 İKİNCİ KATMAN] — damgasız ARAMA satırı dayanak SAYILMAZ ─

def test_t3b_arama_satiri_hayalet_muhakemeyi_mesrulastirmaz(tmp_path):
    """SÖMÜRÜ SENARYOSU (canlı kanıt, t3-B — düzeltme turu): DÜZELTME
    ÖNCESİ `kutuk_dayanagi_denetle` yalnız 'esas/karar kütükte HERHANGİ bir
    satırda geçiyor mu' (`kutukte_esas_karar_satiri_var_mi`) diye soruyordu
    — DAMGA tokenı ARANMIYORDU. Damgasız/tam-metinsiz UCUZ bir ARAMA teyidi
    (`teyit --arac ictihat_ara --sonuc "<uydurma künye>"`, döküm-icerik'siz,
    --damga'sız, kod=0) bu denetimi bedavaya geçiyordu (sb6 kanıtı). Burada
    kütükte hayalet künye için TAM DA böyle damgasız bir ARAMA satırı VAR
    (gerçek bir `teyit --arac ictihat_ara` çağrısının bırakacağı izin
    birebir aynısı) — ama hiçbir DAMGA'lı/GETİR teyidi YOK. DÜZELTME
    SONRASI: `kutukte_damgali_dayanak_satiri_var_mi` damgasız bir ARAMA
    satırını dayanak olarak KABUL ETMEZ → BLOK (HAYALET MUHAKEME)."""
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    teyit_dizin = tmp_path / "_oa" / "teyit"

    kutuk_yolu = teyit_dizin / "kunye-teyit.md"
    kutuk_yolu.write_text("| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
                          "|---|---|---|---|---|\n", encoding="utf-8")
    (dokum_dizin / "a.md").write_text(
        f"{KUNYE_GERCEK} sayılı kararın tam metni burada yer almaktadır...\n",
        encoding="utf-8")
    _kutuk_satiri_yaz(kutuk_yolu, KUNYE_GERCEK, "LEHE", dokum_ad="a.md")

    (dokum_dizin / "hayalet.md").write_text(
        f"{KUNYE_HAYALET} sayılı kararın tam metni burada yer almaktadır...\n",
        encoding="utf-8")
    # UCUZ ARAMA satırı — DAMGA=YOK, yalnız "[ARAMA — tam metin çekilmedi]"
    # etiketi (gerçek bir `teyit --arac ictihat_ara` çağrısının kütükteki
    # izi ile BİREBİR aynı biçim).
    with open(kutuk_yolu, "a", encoding="utf-8") as f:
        f.write(f"| 2026-01-02T00:00:00 | ictihat_ara | sorgu | {KUNYE_HAYALET} "
                "[ARAMA — tam metin çekilmedi] |  |\n")

    satirlar = [
        "# 02 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE_HAYALET}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/hayalet.md",
        "**DAMGA:** LEHE", "",
        "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
        "## DAVAYA-BAĞ", "...davaya bağ açıklaması...", "",
        "## AYIRT-ETME", "", "",
    ]
    (cikti_dizin / "02-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")

    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        f"Somut olayda {KUNYE_HAYALET} sayılı karar emsal teşkil etmektedir.\n",
        encoding="utf-8")

    kod, cikti = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, (
        f"Damgasız ARAMA satırı hayalet muhakemeyi MEŞRULAŞTIRMAMALIYDI:\n{cikti}")
    assert "TESLİM ENGELİ" in cikti
    assert "HAYALET MUHAKEME" in cikti


# ── t9 [BLOKER, Ş2 — CR SATIR-SONU KAÇIŞ ATLATMASI] — sb6 birleşik zinciri ──

def test_bolum_enjeksiyonu_CR_ile_de_engellenir(tmp_path):
    """SÖMÜRÜ SENARYOSU (canlı kanıt, sb6 — t3-B + t9 BİRLEŞİK ZİNCİRİ): SIFIR
    elle dosya düzenlemesi, yalnız 3 CLI çağrısı. (1) init. (2) UCUZ bir
    ARAMA teyidi (--arac ictihat_ara, damgasız, döküm-icerikli) 'hayalet'
    bir künye (22. HD, E. 2021/9999, K. 2021/8888) için kütükte damgasız bir
    satır + dökümde bir dosya doğurur — hiçbir --damga/--bag/--ilgili-kisim
    denetiminden geçmez. (3) meşru bir GETİR teyidinin (--damga ALEYHE)
    --bag alanına, satır-başı kaçışını `\\n` yerine LONE `\\r` ile atlatmayı
    deneyen TAM bir hayalet **KUNYE:**/**DAMGA:** LEHE bloğu gömülür — bu
    blok (2)'de üretilen dökümü KAYNAK-IZI göstererek kaynak-izi denetimini
    de geçmeyi hedefler. DÜZELTME ÖNCESİ (t9): CR kaçış katmanını hiç
    tetiklemeden dosyada TAM GEÇERLİ ikinci bir bölüm doğuruyordu VE
    (t3-B) o bölümün kütük dayanağı yalnız damgasız ARAMA satırına dayanarak
    G2/G3'ten [OK] ile geçiyordu. DÜZELTME SONRASI: `_muhakeme_kacis` artık
    CR'yi de kaçışlar (tek bölüm doğar) VE `kutuk_dayanagi_denetle` damgasız
    bir ARAMA satırını dayanak olarak KABUL ETMEZ — ikisi birden bu zinciri
    KAPATIR (hayalet künyenin HİÇ muhakeme kaydı kalmaz → çıplak atıf BLOK)."""
    _init(tmp_path)

    hayalet_kunye = "Yargıtay 22. HD, E. 2021/9999, K. 2021/8888"
    hayalet_tam_metin = (hayalet_kunye + " sayılı kararın tam metni burada yer "
                         "almaktadır — uydurma karar.")
    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "22 HD arama sorgusu",
         "--sonuc", hayalet_kunye, "--dokum-icerik", hayalet_tam_metin,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    hayalet_dokum_dosyalari = list(dokum_dizin.glob("*ictihat_ara*.md"))
    assert len(hayalet_dokum_dosyalari) == 1, list(dokum_dizin.iterdir())
    hayalet_kaynak_izi = "_oa/teyit/dokum/" + hayalet_dokum_dosyalari[0].name

    zehirli_bag = (
        "Bu karar dosyamızdaki olgusal örüntüyle örtüşmektedir; TBK m.49 "
        "kapsamında doğrudan emsaldir ve yeterince uzundur."
        "\r\r**KUNYE:** " + hayalet_kunye + "\r"
        "**KAYNAK-IZI:** " + hayalet_kaynak_izi + "\r"
        "**DAMGA:** LEHE\r\r"
        "## İLGİLİ-KISIM\ruydurma ilgili kısım\r\r"
        "## DAVAYA-BAĞ\ruydurma davaya bağ\r\r"
    )
    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", KUNYE_SINIF, "--damga", "ALEYHE", "--bag", zehirli_bag,
         "--ilgili-kisim", ILGILI_SINIF, "--dokum-icerik", DOKUM_SINIF,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 == 0, cikti2

    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(encoding="utf-8")
    bolumler = ko.bolumlere_ayir(metin)
    assert len(bolumler) == 1, metin  # hayalet bölüm YOK — CR de kaçışlandı
    assert hayalet_kunye in metin  # görünür metin kayıpsız kalır (kaçışlanmış)

    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        f"Somut olayda {hayalet_kunye} sayılı karar emsal teşkil etmektedir.\n",
        encoding="utf-8")
    kod3, cikti3 = _denetim_cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod3 == 1, cikti3


# ── Birim testleri — `_satir_sonu_normalize` / `_muhakeme_kacis` (t9) ───────

@pytest.mark.parametrize("nl", ["\n", "\r\n", "\r"])
def test_muhakeme_kacis_her_satir_sonu_bicimini_kacislar(nl):
    """`_muhakeme_kacis` üç satır-sonu biçiminin (LF/CRLF/lone-CR) HEPSİNDE
    aynı sonucu üretmeli — DÜZELTME ÖNCESİ yalnız `\\n` kaçışlanıyordu, `\\r`
    (CRLF içindeki dahil değil, LONE `\\r`) kaçmıyordu (t9 BLOKER)."""
    zehirli = "taban metin" + nl + "**KUNYE:** hayalet" + nl + nl + "## İLGİLİ-KISIM"
    kacan = oh._muhakeme_kacis(zehirli)
    # görünür metin (ZWSP hariç) kayıpsız — yalnız satır-başı biçimi normalize
    assert "**KUNYE:** hayalet" in kacan
    assert "## İLGİLİ-KISIM" in kacan
    # ama artık satır-BAŞI (kaçışsız) bir `**KUNYE:**`/`##` YOK — hepsi ZWSP
    # önekli; `kunye_ortak.bolum_araliklari` ile ayrıştırıldığında TEK bölüm.
    assert ko.bolumlere_ayir("**KUNYE:** gerçek\n" + kacan) == \
        ko.bolumlere_ayir("**KUNYE:** gerçek\n" + kacan)  # sabitlik (tek bölüm)
    tek_bolum_test_metni = "**KUNYE:** gerçek\n" + kacan
    assert len(ko.bolumlere_ayir(tek_bolum_test_metni)) == 1, tek_bolum_test_metni


def test_satir_sonu_normalize_lone_cr_yi_lf_yapar():
    assert oh._satir_sonu_normalize("a\rb\r\nc\r") == "a\nb\nc\n"
    assert oh._satir_sonu_normalize("") == ""
    assert oh._satir_sonu_normalize(None) == ""  # falsy girdi — çağıran taraf zaten önceden korur


# ── Birim testleri — `kunye_ortak.kutukte_damgali_dayanak_satiri_var_mi` ────

def test_kutukte_damgali_dayanak_arama_satirini_kabul_etmez(tmp_path):
    """Damgasız bir ARAMA satırı ('[ARAMA — tam metin çekilmedi]', DAMGA=
    tokenı YOK) hiçbir zaman damgalı bir dayanak olarak KABUL EDİLMEMELİ."""
    kutuk = tmp_path / "kunye-teyit.md"
    kutuk.write_text(
        "| Zaman | Araç | Sorgu | Sonuç | Döküm |\n|---|---|---|---|---|\n"
        "| 2026-01-01T00:00:00 | ictihat_ara | sorgu | Yargıtay 4. HD, "
        "E. 2020/1, K. 2020/2 [ARAMA — tam metin çekilmedi] |  |\n",
        encoding="utf-8")
    assert ko.kutukte_damgali_dayanak_satiri_var_mi(
        str(kutuk), "2020/1", "2020/2", "LEHE") is False


def test_kutukte_damgali_dayanak_dogru_damga_ve_kaynak_ile_gecer(tmp_path):
    """Dürüst akış: aynı DAMGA + aynı döküm dosyasını gösteren gerçek bir
    GETİR satırı VARSA dayanak KABUL edilmeli (yanlış-pozitif BLOK yok)."""
    kutuk = tmp_path / "kunye-teyit.md"
    kutuk.write_text(
        "| Zaman | Araç | Sorgu | Sonuç | Döküm |\n|---|---|---|---|---|\n"
        "| 2026-01-01T00:00:00 | ictihat_getir | sorgu | Yargıtay 4. HD, "
        "E. 2020/1, K. 2020/2 DAMGA=LEHE | [döküm](_oa/teyit/dokum/a.md) |\n",
        encoding="utf-8")
    assert ko.kutukte_damgali_dayanak_satiri_var_mi(
        str(kutuk), "2020/1", "2020/2", "LEHE",
        kaynak_izi="_oa/teyit/dokum/a.md") is True


def test_kutukte_damgali_dayanak_farkli_damga_reddedilir(tmp_path):
    """Kütükteki satırın DAMGA'sı bölümdekinden FARKLIYSA dayanak sayılmaz —
    yalnız aynı esas/karar+DAMGA kombinasyonu geçerli bir iz sayılır."""
    kutuk = tmp_path / "kunye-teyit.md"
    kutuk.write_text(
        "| Zaman | Araç | Sorgu | Sonuç | Döküm |\n|---|---|---|---|---|\n"
        "| 2026-01-01T00:00:00 | ictihat_getir | sorgu | Yargıtay 4. HD, "
        "E. 2020/1, K. 2020/2 DAMGA=ALEYHE | [döküm](_oa/teyit/dokum/a.md) |\n",
        encoding="utf-8")
    assert ko.kutukte_damgali_dayanak_satiri_var_mi(
        str(kutuk), "2020/1", "2020/2", "LEHE",
        kaynak_izi="_oa/teyit/dokum/a.md") is False


# ── YENİ-1 [ÖNEMLİ, şerh turu 2] — KAYNAK-IZI üzerinden hayalet bölüm ───────
# enjeksiyonu: komşu BEŞ serbest-metin alanının hepsi `_muhakeme_kacis`'ten
# geçerken KAYNAK-IZI tek KAÇIŞSIZ alandı; `--dokum` yolu satır sonu (`\n`/
# `\r`) taşıyabilen platformlarda (Linux/macOS/WSL — ci.yml `ubuntu-latest`)
# satır başında tam geçerli bir hayalet **KUNYE:**/**DAMGA:** bölümü
# doğurabiliyordu. DÜZELTME: `_kaynak_izi_yolu` girişte satır-sonu taşıyan
# bir yolu fail-closed RET eder (+ yazım noktası ayrıca `_muhakeme_kacis`'ten
# geçirilir, savunma katmanı).

def test_yeni1_dokum_yolu_satir_sonu_iceremez_hayalet_bolum_uretilmez(tmp_path):
    """Sömürü senaryosu (canlı kanıt, YENİ-1): `--dokum` değerine gömülü
    `\\n` ile satır-başında tam geçerli bir hayalet `**KUNYE:**`/`**DAMGA:**
    LEHE` bloğu taşıyan bir 'yol' verilir (ARAMA sınıfı, --damga YOK — kod
    yoluna --damga denetimlerinden ETKİLENMEDEN ulaşmak için). DÜZELTME
    ÖNCESİ bu değer hiçbir kaçıştan geçirilmeden kütük hücresine/olası bir
    muhakeme yazımına sızabilirdi. DÜZELTME SONRASI: `_kaynak_izi_yolu` bu
    değeri girişte fail-closed RET eder — kütüğe HİÇBİR satır yazılmaz."""
    _init(tmp_path)
    hayalet_kunye = "Yargıtay 4. HD, E. 2019/7777, K. 2019/8888"
    zehirli_dokum_yolu = (
        "gercek-dokum.md\n"
        "**KUNYE:** " + hayalet_kunye + "\n"
        "**DAMGA:** LEHE\n\n"
        "## İLGİLİ-KISIM\nuydurma\n\n## DAVAYA-BAĞ\nuydurma\n\n"
        "kuyruk.md"
    )
    kod, cikti = _cli(
        ["teyit", "--arac", "ictihat_ara", "--sorgu", "temiz sorgu",
         "--sonuc", "temiz sonuç", "--dokum", zehirli_dokum_yolu, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, cikti
    assert "satır sonu" in cikti or "RET" in cikti, cikti

    kutuk_yolu = tmp_path / "_oa" / "teyit" / "kunye-teyit.md"
    if kutuk_yolu.exists():
        kutuk = kutuk_yolu.read_text(encoding="utf-8")
        assert "KUNYE" not in kutuk, kutuk
        assert "7777" not in kutuk, kutuk
    muhakeme_yolu = tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md"
    assert not muhakeme_yolu.exists(), "hayalet muhakeme dosyası oluşmamalıydı"


def test_yeni1_kaynak_izi_yolu_birim_testi_satir_sonunu_reddeder():
    """Birim düzeyinde (platform bağımsız — dosya sistemi oluşturmaya
    gerek YOK): `_kaynak_izi_yolu` `\\n`/`\\r` taşıyan HERHANGİ bir --dokum
    değerini fail-closed RET eder (SystemExit); temiz bir yol ETKİLENMEZ."""
    with pytest.raises(SystemExit):
        oh._kaynak_izi_yolu("a\nb.md", ".")
    with pytest.raises(SystemExit):
        oh._kaynak_izi_yolu("a\rb.md", ".")
    # dürüst/temiz bir yol hâlâ normal biçimde çözülür (yanlış-pozitif YOK).
    assert oh._kaynak_izi_yolu(None, ".") is None
    assert oh._kaynak_izi_yolu("", ".") == ""


# ── YENİ-3 [KÜÇÜK, şerh turu 2] — --damga-degistir gerekçesi kütük hücresine
#    İKİNCİ bir ham DAMGA= tokenı bırakmamalı ─────────────────────────────

def test_yeni3_damga_degistir_gerekcesi_kutuk_hucresinde_ikinci_damga_tokeni_birakmaz(tmp_path):
    """Sömürü senaryosu (canlı kanıt, YENİ-3): `--damga-degistir` gerekçesine
    literal `DAMGA=LEHE` gömülür. DÜZELTME ÖNCESİ bu ham metin script'in
    KENDİ doğrulanmış `DAMGA=NOTR` son ekinden SONRA hücreye eklenip
    hücrede İKİ `DAMGA=` tokenı bırakıyordu (güvenlik yalnız okuyucuların
    ilk-eşleşme sırasına dayanıyordu — dokümante edilmemiş varsayım).
    DÜZELTME SONRASI: gerekçe de `_sonuc_damga_ize_karismasin`'den geçirilir
    — kütük satırında TAM OLARAK BİR `DAMGA=` tokenı kalır ve o token her
    zaman script'in doğrulanmış --damga değeridir."""
    _init(tmp_path)
    kunye = "Yargıtay 4. HD, E. 2023/9001, K. 2023/9002, T. 01.01.2023"
    dokum_icerik = (kunye + " sayılı kararın tam metni: davalının kusuru ile "
                     "davacının zararı arasında illiyet bağı bulunmaktadır.\n")
    ilgili = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"
    bag = ("Bu karar dosyamızdaki olgusal örüntüyle örtüşmektedir; TBK m.49 "
           "kapsamında doğrudan emsaldir ve yeterince uzundur.")

    kod1, cikti1 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", kunye, "--damga", "ALEYHE", "--bag", bag,
         "--ilgili-kisim", ilgili, "--dokum-icerik", dokum_icerik,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0, cikti1

    zehirli_gerekce = ("Yeniden degerlendirme sonucu damga notr olarak "
                        "guncellenmistir DAMGA=LEHE ek aciklama")
    kod2, cikti2 = _cli(
        ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
         "--sonuc", kunye, "--damga", "NOTR", "--bag", bag,
         "--ilgili-kisim", ilgili, "--dokum-icerik", dokum_icerik,
         "--damga-degistir", zehirli_gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod2 == 0, cikti2

    kutuk_satirlari = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(
        encoding="utf-8").splitlines()
    son_satir = [s for s in kutuk_satirlari if "ictihat_getir" in s][-1]
    assert son_satir.count("DAMGA=") == 1, son_satir
    assert "DAMGA=NOTR" in son_satir
    assert "DAMGA=LEHE" not in son_satir
    assert "DAMGA∶LEHE" in son_satir  # kullanıcı metnindeki token görünür kalır (kaçışlanmış)

    # kunye_ortak.kutukten_son_damga hâlâ doğru sonucu verir (ilk-eşleşmeye
    # değil artık TEK gerçek tokene dayanan sağlam bir garanti).
    assert ko.kutukten_son_damga(
        str(tmp_path / "_oa" / "teyit" / "kunye-teyit.md"), "2023/9001", "2023/9002",
        None) == "NOTR"
