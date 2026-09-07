"""v0.5.16.1 — SAHA YAN-BULGULARI (gerçek dava kopyalarında v0.5.16 saha ölçümü).

İki kusur, iki kilit:

(1) KÜTÜK AYRIŞTIRICISI SÜTUN KATILIĞI — `kunye_ortak.kutukten_son_damga` (ve
    ortak gövdeyi paylaşan `kutukten_son_akibet` / `kutukte_esas_karar_satiri_
    var_mi` / `kutuk_gercek_veri_var_mi` / `kutukte_damgali_dayanak_satiri_var_mi`,
    ayrıca `ictihat_muhakeme_denetim._kutuk_kunye_bilgisi` / `farkindalik_
    denetimi` ve `kunye_teyit.kutuk_ham_baglari`) satırı `split("|")` ile
    böler, `len != 7` ise «BOZUK, fail-CLOSED atlandı» diyordu. Saha
    kütüklerinde satırlar 17 hücreli (genişletilmiş düzen) → 26/33 taslakta
    her künye «damgasız» göründü; [F] hafif kip ve kütük teyidi kör kaldı.
    ÖLÇÜM (bu turda, `oa_hafiza.py teyit` ile): mevcut yazıcı 5 sütun = 7
    hücre yazar; saha dosyalarındaki 17 hücre yazıcı dışı/genişletilmiş
    düzendir → okuyucu SÜTUN SAYISINA BAĞLI KALMAMALI: esas+karar eşleşmesi
    ve `DAMGA=`/`AKIBET=` tokenları hücre konumundan bağımsız (satırın
    tamamında) aranır; yalnız `|` ile başlamayan/başlık/ayraç satırları
    atlanır; BOZUK yalnız gerçekten ayrıştırılamayan satır için; birden çok
    `DAMGA=` varsa SONUNCUSU geçerli (mevcut «son damga» semantiği).
    Satır-geneli aramanın açtığı yeni kapı (kullanıcı-kontrolündeki `--sorgu`
    hücresinden `DAMGA=` / künye izi enjekte etme) yazıcı tarafında kapanır:
    `oa_hafiza.py teyit` sorgu hücresini de aynı kaçış katmanından geçirir.

(2) ŞERH ZİNCİRİ KAPI ATLATMA — `pipeline_kayit._onkosul_kontrol`: `_oa/metin/
    00-kunye.json` YOKKEN `--serh --serh-kapi ingest-once` verilirse İNGEST-
    ÖNCE şerhi ERKEN DÖNÜŞ yapıyor, sonraki kapılar (özellikle K2 GRAF KAPISI)
    hiç değerlendirilmiyordu → çevrimli/şema hatalı graf şerhsiz geçiyordu.
    Artık şerhli geçiş erken dönmez: şerh mesajı biriktirilir, KALAN kapılar da
    değerlendirilir; kalan kapılardan biri bloklu ve şerh onu kapsamıyorsa RET
    (mesajda hangi kapı); `tumu` tüm kapıları kapsar; dönüş sözleşmesi (izin,
    sorun, uyarı, serh_mesaj) korunur, `serh_mesaj` birden çok kapıyı listeler.

Fikstürler sentetiktir (E. 2099/1 sınıfı); müvekkil verisi yoktur.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
KUNYE_ORTAK = SKILLS / "oa-kontrol" / "scripts" / "kunye_ortak.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"
KUNYE_TEYIT = SKILLS / "oa-kontrol" / "scripts" / "kunye_teyit.py"
DILEKCE = SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _modul(yol, ad):
    assert yol.is_file(), f"bulunamadı: {yol}"
    spec = importlib.util.spec_from_file_location(ad, str(yol))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ko():
    return _modul(KUNYE_ORTAK, "kunye_ortak_yan_bulgular")


@pytest.fixture(scope="module")
def imd():
    return _modul(DENETIM, "ictihat_muhakeme_denetim_yan_bulgular")


@pytest.fixture(scope="module")
def kt():
    return _modul(KUNYE_TEYIT, "kunye_teyit_yan_bulgular")


@pytest.fixture(scope="module")
def dd():
    return _modul(DILEKCE, "dilekce_denetim_yan_bulgular")


@pytest.fixture(scope="module")
def pk():
    return _modul(PIPELINE, "pipeline_kayit_yan_bulgular")


def _cli(script, args, cwd):
    cp = subprocess.run(
        [sys.executable, str(script)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ═══════════════════════ (1) KÜTÜK AYRIŞTIRICISI — sütun toleransı ═══════════

KUNYE = "Yargıtay 9. HD, E. 2099/1, K. 2099/2"
ESAS, KARAR = "2099/1", "2099/2"
DOKUM_IZI = "_oa/teyit/dokum/d0.md"

BASLIK_5 = ("| Zaman | Araç | Sorgu | Sonuç (künye/madde + lehe/aleyhe) | Döküm |\n"
            "|---|---|---|---|---|\n")

# Saha düzeni: 15 sütun → `split("|")` 17 hücre. Künye parçaları AYRI
# sütunlara dağılmış, tam künye + tokenlar «Sonuç» sütununda, damga/akıbet
# ayrıca kendi sütununda da yazılı (elle genişletilmiş kütük).
BASLIK_15 = ("| Zaman | Araç | Sorgu | Merci | Daire | Esas | Karar | Tarih | "
             "Sonuç (künye/madde + lehe/aleyhe) | Damga | Döküm-Sınıfı | Akıbet | "
             "Bağ | Kaynak-URL | Döküm |\n"
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")


def _satir17(sonuc, damga="ALEYHE", akibet="kesinlesti", daire="9. HD",
             dokum=DOKUM_IZI, zaman="2099-01-01T10:00:00"):
    return (f"| {zaman} | ictihat_getir | sentetik sorgu | Yargıtay | {daire} | "
            f"E. {ESAS} | K. {KARAR} | 01.01.2099 | {sonuc} | {damga} | tam-metin | "
            f"{akibet} | sentetik bağ metni | https://ornek.invalid/karar | "
            f"[döküm]({dokum}) |\n")


def _satir7(sonuc, dokum=DOKUM_IZI, zaman="2099-01-01T10:00:00"):
    return (f"| {zaman} | ictihat_getir | sentetik sorgu | {sonuc} | "
            f"[döküm]({dokum}) |\n")


def _kutuk_yaz(kok, icerik):
    teyit = kok / "_oa" / "teyit"
    teyit.mkdir(parents=True, exist_ok=True)
    yol = teyit / "kunye-teyit.md"
    yol.write_text("# Künye Teyit Kütüğü (sentetik)\n\n" + icerik, encoding="utf-8")
    return str(yol)


def _hafiza_init(kok):
    kod, cikti = _cli(HAFIZA, ["init", "--dosya", "Sentetik Dosya E. 2099/1",
                               "--kok", str(kok)], cwd=kok)
    assert kod == 0, cikti


def _hucre_sayisi(kutuk_yolu):
    """Kütükteki veri satırlarının `split("|")` hücre sayıları (ölçüm)."""
    sayilar = []
    for s in pathlib.Path(kutuk_yolu).read_text(encoding="utf-8").splitlines():
        if s.startswith("|") and not s.startswith("| Zaman") and not s.startswith("|---"):
            sayilar.append(len(s.split("|")))
    return sayilar


def test_a_gercek_teyit_satiri_damga_ve_akibet_okunur(tmp_path, ko):
    """(a) `oa_hafiza.py teyit` ile GERÇEK biçimde üretilmiş satır — ALEYHE,
    AKIBET, sonra `--damga-degistir` ile LEHE — `kutukten_son_damga` /
    `kutukten_son_akibet` ile okunur. Hücre sayısı ÖLÇÜLÜR (yazıcı 5 sütun =
    7 hücre); okuyucu bu sayıya bağlı olmadığı için ölçüm yalnız bilgidir."""
    _hafiza_init(tmp_path)
    dokum = tmp_path / "ham.md"
    dokum.write_text(
        f"{KUNYE} — sentetik fikstür. Somut olayda fazla mesai alacağı "
        "ispatlanamamıştır; tanık beyanları soyut kalmıştır.\n" * 3, encoding="utf-8")
    ortak = ["--arac", "ictihat_getir", "--sorgu", "fazla mesai ispat tanık",
             "--sonuc", KUNYE, "--dokum-sinifi", "tam-metin",
             "--bag", "sentetik fikstür — fazla mesai ispat yükü davacı işçide, tanık "
                      "beyanı soyut kaldı (≥40 karakter)",
             "--ilgili-kisim", "tanık beyanları soyut kalmıştır",
             "--dokum-icerik", "@" + str(dokum), "--sorgu-onayli", "--kok", str(tmp_path)]
    kod, cikti = _cli(HAFIZA, ["teyit", "--damga", "ALEYHE", "--akibet", "bozuldu",
                               "--akibet-kaynak", "arac:ictihat_getir"] + ortak, cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = str(tmp_path / "_oa" / "teyit" / "kunye-teyit.md")
    sayilar = _hucre_sayisi(kutuk)
    assert sayilar and all(n >= 7 for n in sayilar), sayilar  # ölçüm: yazıcı ≥ 5 sütun
    daire = ko.daire_key(KUNYE)
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR, daire) == "ALEYHE"
    assert ko.kutukten_son_akibet(kutuk, ESAS, KARAR, daire) == "bozuldu"
    assert ko.kutukte_esas_karar_satiri_var_mi(kutuk, ESAS, KARAR, daire)
    assert ko.kutuk_gercek_veri_var_mi(kutuk)

    kod, cikti = _cli(HAFIZA, ["teyit", "--damga", "LEHE", "--damga-degistir",
                               "sentetik gerekçe: karar yeniden okundu, bağ lehe yönde "
                               "kuruldu (≥40 karakter)"] + ortak, cwd=tmp_path)
    assert kod == 0, cikti
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR, daire) == "LEHE"  # SON damga


def test_b_17_hucreli_satir_okunur_bozuk_uyarisi_yok(tmp_path, ko, capfd):
    """(b) 17 hücreli (15 sütun) elle yazılmış saha düzeni: son damga, akıbet,
    satır-var, gerçek-veri ve damgalı-dayanak okuyucularının HEPSİ görür;
    stderr'e «BOZUK» uyarısı DÜŞMEZ (satır ayrıştırılabilir)."""
    kutuk = _kutuk_yaz(tmp_path, BASLIK_15 + _satir17(
        f"{KUNYE} DAMGA=ALEYHE DOKUM-SINIFI=tam-metin AKIBET=kesinlesti"))
    assert _hucre_sayisi(kutuk) == [17]
    daire = ko.daire_key(KUNYE)
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR, daire) == "ALEYHE"
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR) == "ALEYHE"
    assert ko.kutukten_son_akibet(kutuk, ESAS, KARAR, daire) == "kesinlesti"
    assert ko.kutukte_esas_karar_satiri_var_mi(kutuk, ESAS, KARAR, daire)
    assert ko.kutuk_gercek_veri_var_mi(kutuk)
    assert ko.kutukte_damgali_dayanak_satiri_var_mi(kutuk, ESAS, KARAR, "ALEYHE",
                                                    kaynak_izi=DOKUM_IZI, daire=daire)
    assert not ko.kutukte_damgali_dayanak_satiri_var_mi(kutuk, ESAS, KARAR, "LEHE",
                                                        kaynak_izi=DOKUM_IZI, daire=daire)
    err = capfd.readouterr().err
    assert "BOZUK" not in err, err


def test_b2_17_hucreli_satirda_daire_farki_eslesmez(tmp_path, ko):
    """Daire-kör olmama korunur: aynı esas/karar no'lu ama FARKLI dairenin
    17 hücreli satırı, daire verilince eşleşmez; daire verilmezse okunur."""
    kutuk = _kutuk_yaz(tmp_path, BASLIK_15 + _satir17(
        f"Yargıtay 22. HD, E. {ESAS}, K. {KARAR} DAMGA=LEHE", damga="LEHE", daire="22. HD"))
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR, ko.daire_key(KUNYE)) is None
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR) == "LEHE"


def test_c_7_hucreli_eski_satir_hala_okunur(tmp_path, ko, capfd):
    """(c) Eski 5-sütun/7-hücre satır DEĞİŞMEDEN okunur (geriye uyum)."""
    kutuk = _kutuk_yaz(tmp_path, BASLIK_5 + _satir7(
        f"{KUNYE} DAMGA=ALEYHE DOKUM-SINIFI=tam-metin AKIBET=kesinlesmedi"))
    assert _hucre_sayisi(kutuk) == [7]
    daire = ko.daire_key(KUNYE)
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR, daire) == "ALEYHE"
    assert ko.kutukten_son_akibet(kutuk, ESAS, KARAR, daire) == "kesinlesmedi"
    assert ko.kutukte_esas_karar_satiri_var_mi(kutuk, ESAS, KARAR, daire)
    assert ko.kutukte_damgali_dayanak_satiri_var_mi(kutuk, ESAS, KARAR, "ALEYHE",
                                                    kaynak_izi=DOKUM_IZI, daire=daire)
    assert "BOZUK" not in capfd.readouterr().err


def test_son_damga_semantigi_satir_ici_ve_satirlar_arasi(tmp_path, ko):
    """Birden çok `DAMGA=` → SONUNCUSU geçerli: aynı satırda (damga-degistir
    gerekçesi gibi) ve ardışık satırlarda (append-only kütük)."""
    kutuk = _kutuk_yaz(tmp_path, BASLIK_5
                       + _satir7(f"{KUNYE} DAMGA=LEHE (DEĞİŞTİRİLDİ — önceki: LEHE) DAMGA=ALEYHE"))
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR) == "ALEYHE"
    kutuk = _kutuk_yaz(tmp_path, BASLIK_15
                       + _satir17(f"{KUNYE} DAMGA=ALEYHE", damga="ALEYHE")
                       + _satir17(f"{KUNYE} DAMGA=LEHE", damga="LEHE",
                                  zaman="2099-01-02T10:00:00"))
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR) == "LEHE"


def test_bozuk_uyarisi_yalniz_gercekten_ayristirilamayan_satira(tmp_path, ko, capfd):
    """Başlık, ayraç, `|` içermeyen ya da `|` ile başlamayan düz metin satırları
    SESSİZ atlanır; `|` ile başlayıp tek hücre bile kuramayan satır BOZUK
    (görünür, fail-closed). Aynı kütükteki sağlam satır yine okunur."""
    icerik = (BASLIK_5
              + "Kural: bir künye bu kütükte YOKSA | çıktıya giremez (düz metin).\n"
              + "| yarım satır — kapanmamış\n"
              + _satir7(f"{KUNYE} DAMGA=ALEYHE")
              + "\n")
    kutuk = _kutuk_yaz(tmp_path, icerik)
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR) == "ALEYHE"
    err = capfd.readouterr().err
    assert err.count("BOZUK") == 1, err
    assert "yarım satır" in err
    assert "Zaman" not in err and "---" not in err and "düz metin" not in err


def test_d_hizli_denetim_f_hafif_kip_17_hucreli_kutukle_aleyhe_kunye(tmp_path, dd):
    """(d) `dilekce_denetim.hizli_denetim` [F] HAFİF KİP (in-process) — 17
    hücreli kütükle «ALEYHE künye» satırı ÜRETİR (saha: «damgasız» sanılıp
    kör kalıyordu)."""
    _kutuk_yaz(tmp_path, BASLIK_15 + _satir17(f"{KUNYE} DAMGA=ALEYHE DOKUM-SINIFI=tam-metin"))
    taslak = ("# SENTETİK MAHKEME BAŞKANLIĞINA\n1. Olay şu şekilde gelişmiştir.\n"
              f"\nEmsal: {KUNYE} kararı bu yöndedir.\n")
    bulgular = dd.hizli_denetim(taslak, kok=str(tmp_path))
    f = [b for b in bulgular if b.startswith("[F]")]
    assert len(f) == 1, bulgular
    assert "ALEYHE künye" in f[0] and "2099/1" in f[0] and "m.6" in f[0], f
    assert "izi yok" not in f[0] and "damgasız" not in f[0]


def test_imd_kutuk_kunye_bilgisi_ve_farkindalik_17_hucre(tmp_path, imd, ko):
    """`ictihat_muhakeme_denetim` kendi kütük okuyucuları da aynı toleransı
    alır: [G6] tam-metin/duyulmuş bilgisi ve FARKINDALIK (ALEYHE → cephanelik)
    17 hücreli satırı görür."""
    kutuk = _kutuk_yaz(tmp_path, BASLIK_15 + _satir17(
        f"{KUNYE} DAMGA=ALEYHE DOKUM-SINIFI=tam-metin DUYULMUS=EVET"))
    bilgi = imd._kutuk_kunye_bilgisi(kutuk, ESAS, KARAR, ko.daire_key(KUNYE))
    assert bilgi == {"satir_var": True, "tam_metin": True, "duyulmus": True}, bilgi
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "06-antitez-cephanelik.md").write_text("# Cephanelik\n(boş)\n", encoding="utf-8")
    uyarilar = imd.farkindalik_denetimi(kutuk, str(cikti))
    assert uyarilar and any("2099/1" in u for u in uyarilar), uyarilar


def test_kunye_teyit_ham_baglari_17_hucre(tmp_path, kt):
    """`kunye_teyit.kutuk_ham_baglari` — Döküm bağı hücre konumundan bağımsız
    bulunur (17 hücreli satırda `_oa/teyit/ham/` bağı yüklenir)."""
    ham = tmp_path / "_oa" / "teyit" / "ham"
    ham.mkdir(parents=True, exist_ok=True)
    (ham / "okuma.md").write_text(f"{KUNYE} — ham döküm (sentetik).\n", encoding="utf-8")
    kutuk = _kutuk_yaz(tmp_path, BASLIK_15 + _satir17(
        f"{KUNYE} DAMGA=LEHE", damga="LEHE", dokum="_oa/teyit/ham/okuma.md"))
    kaynaklar = kt.kutuk_ham_baglari(kutuk)
    assert len(kaynaklar) == 1 and kaynaklar[0][0].endswith("okuma.md"), kaynaklar


def test_sorgu_hucresi_damga_ve_kunye_izi_tasiyamaz(tmp_path, ko):
    """Satır-geneli aramanın açtığı kapı YAZICIDA kapanır: `--sorgu` içine
    gömülü `DAMGA=LEHE` ve yabancı bir künye, kütük satırında ne DAMGA ne
    künye izi olarak OKUNAMAZ (ARAMA çağrısı damgasızdır; sonuc künyesi ise
    satırda kalır)."""
    _hafiza_init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_ara",
        "--sorgu", "Yargıtay 7. HD E. 2022/333 K. 2022/444 DAMGA=LEHE AKIBET=kesinlesti emsal",
        "--sonuc", KUNYE, "--sorgu-onayli", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = str(tmp_path / "_oa" / "teyit" / "kunye-teyit.md")
    assert ko.kutukten_son_damga(kutuk, "2022/333", "2022/444") is None
    assert ko.kutukten_son_akibet(kutuk, "2022/333", "2022/444") is None
    assert not ko.kutukte_esas_karar_satiri_var_mi(kutuk, "2022/333", "2022/444")
    assert ko.kutukte_esas_karar_satiri_var_mi(kutuk, ESAS, KARAR)
    assert ko.kutukten_son_damga(kutuk, ESAS, KARAR) is None  # ARAMA: damgasız


# ═══════════════════════ (2) ŞERH ZİNCİRİ — kapı atlatma kapanır ═════════════

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
UZUN_SERH = "Sentetik gerekçe: avukat bilinçli olarak bu kapıyı geçiyor (>=30 karakter)."
CEVRIMLI_GRAF = {"arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]}


def _baslat(kok):
    kod, cikti = _cli(PIPELINE, ["--baslat", "Sentetik Dosya E. 2099/1", "--kok", str(kok)], cwd=kok)
    assert kod == 0, cikti


def _kunye_kur(kok):
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(json.dumps({"toplam_evrak": 0, "kayitlar": []}),
                                         encoding="utf-8")


def _cikti_yaz(kok, ad, veri):
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / ad).write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")


def _isle(kok, adim, parca, ek=()):
    return _cli(PIPELINE, ["--isle", "--adim", str(adim), "--parca", parca, "--durum",
                           "UYGULANDI", "--kanit", UZUN_KANIT, "--kok", str(kok)] + list(ek),
                cwd=kok)


def _son_olay(kok):
    satirlar = (kok / "_oa" / "defter" / "pipeline-olaylar.jsonl").read_text(
        encoding="utf-8").splitlines()
    return json.loads([s for s in satirlar if s.strip()][-1])


def test_serh_ingest_once_graf_kapisini_atlatamaz(tmp_path):
    """(a) 00-kunye.json YOK + çevrimli graf + `--serh-kapi ingest-once` → RET;
    mesaj GRAF KAPISI'nı ve gereken kapı adını söyler. Olay YAZILMAZ."""
    _baslat(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", CEVRIMLI_GRAF)
    kod, cikti = _isle(tmp_path, 1, "oa-illiyet", ["--serh", UZUN_SERH, "--serh-kapi", "ingest-once"])
    assert kod != 0, cikti
    assert "GRAF KAPISI" in cikti and "--serh-kapi graf" in cikti, cikti
    assert "tumu" in cikti  # iki kapı birden bloklu → tek çare görünür
    son = _son_olay(tmp_path)
    assert not (son.get("adim") == 1 and son.get("parca") == "oa-illiyet"
                and son.get("durum") == "UYGULANDI"), son


def test_serh_tumu_iki_kapiyi_gecer_ve_ikisini_listeler(tmp_path):
    """(b) `--serh-kapi tumu` → geçer; şerh mesajı İKİ kapıyı da listeler
    (İNGEST-ÖNCE + GRAF KAPISI) ve olaya `serh_metni` olarak işlenir."""
    _baslat(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", CEVRIMLI_GRAF)
    kod, cikti = _isle(tmp_path, 1, "oa-illiyet", ["--serh", UZUN_SERH, "--serh-kapi", "tumu"])
    assert kod == 0, cikti
    assert "İNGEST-ÖNCE ŞERH ile geçildi" in cikti and "GRAF KAPISI ŞERH ile geçildi" in cikti, cikti
    son = _son_olay(tmp_path)
    assert son.get("serh") is True and son.get("serh_kapi") == "tumu"
    metni = son.get("serh_metni") or ""
    assert "İNGEST-ÖNCE" in metni and "GRAF KAPISI" in metni, metni


def test_kunye_var_cevrimli_graf_serh_graf_gecer(tmp_path):
    """(c) 00-kunye.json VAR + çevrimli graf + `--serh-kapi graf` → geçer;
    şerh mesajı yalnız GRAF KAPISI'nı anar (İNGEST-ÖNCE bloklu değildi)."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", CEVRIMLI_GRAF)
    kod, cikti = _isle(tmp_path, 1, "oa-illiyet", ["--serh", UZUN_SERH, "--serh-kapi", "graf"])
    assert kod == 0, cikti
    metni = _son_olay(tmp_path).get("serh_metni") or ""
    assert "GRAF KAPISI" in metni and "İNGEST-ÖNCE" not in metni, metni


def test_onkosul_kontrol_in_process_donus_sozlesmesi(tmp_path, pk):
    """Dönüş sözleşmesi (izin, sorun, uyarı, serh_mesaj) korunur; şerh birden
    çok kapıyı tek dizede listeler; kapsamayan şerh → izin False + sorun."""
    _baslat(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", CEVRIMLI_GRAF)
    izin, sorun, uyari, serh = pk._onkosul_kontrol(
        str(tmp_path), 1, "oa-illiyet", UZUN_SERH, serh_kapi="ingest-once")
    assert (izin, uyari, serh) == (False, None, False)
    assert "GRAF KAPISI" in sorun and "graf" in sorun, sorun

    izin, sorun, uyari, serh = pk._onkosul_kontrol(
        str(tmp_path), 1, "oa-illiyet", UZUN_SERH, serh_kapi="tumu")
    assert (izin, sorun, uyari) == (True, None, None)
    assert isinstance(serh, str) and "İNGEST-ÖNCE" in serh and "GRAF KAPISI" in serh, serh
    assert "[kapı: tumu]" in serh

    _kunye_kur(tmp_path)
    izin, sorun, uyari, serh = pk._onkosul_kontrol(
        str(tmp_path), 1, "oa-illiyet", UZUN_SERH, serh_kapi="graf")
    assert (izin, sorun, uyari) == (True, None, None)
    assert "GRAF KAPISI" in serh and "İNGEST-ÖNCE" not in serh, serh

    # temiz graf + künye var + şerh → hiçbir kapı bloklu değil: şerh mesajı YOK
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {"arac": "grafik_denetim", "cevrimler": []})
    assert pk._onkosul_kontrol(str(tmp_path), 1, "oa-illiyet", UZUN_SERH,
                               serh_kapi="tumu") == (True, None, None, False)


def test_serh_ingest_once_kiyas_kapisini_atlatamaz(tmp_path):
    """Aynı sınıf erken dönüş KIYAS kapısında da kapanır: 00-kunye.json yok +
    adım-5 artefaktsız + `--serh-kapi ingest-once` → RET (adım-5/kiyas);
    `tumu` → geçer, iki kapı listelenir."""
    _baslat(tmp_path)
    kod, cikti = _isle(tmp_path, 5, "oa-kiyas", ["--serh", UZUN_SERH, "--serh-kapi", "ingest-once"])
    assert kod != 0, cikti
    assert "adım-5" in cikti and "--serh-kapi kiyas" in cikti, cikti
    kod, cikti = _isle(tmp_path, 5, "oa-kiyas", ["--serh", UZUN_SERH, "--serh-kapi", "tumu"])
    assert kod == 0, cikti
    metni = _son_olay(tmp_path).get("serh_metni") or ""
    assert "İNGEST-ÖNCE" in metni and "adım-5" in metni, metni


def test_serh_ingest_once_kontrol_kapisini_atlatamaz(tmp_path):
    """KONTROL kapısı (adım-9, teslim makbuzu): ingest-once şerhi onu geçemez."""
    _baslat(tmp_path)
    kod, cikti = _isle(tmp_path, 9, "oa-kontrol", ["--serh", UZUN_SERH, "--serh-kapi", "ingest-once"])
    assert kod != 0, cikti
    assert "adım-9" in cikti and "--serh-kapi kontrol" in cikti, cikti


def test_serh_ingest_once_capraz_adim_kapisini_atlatamaz(tmp_path):
    """ÇAPRAZ-ADIM (adım-8 yazım, adım-5 BEKLIYOR) yalnız `tumu`/çıplak şerhle
    geçilir; `ingest-once` şerhi onu atlatamaz."""
    _baslat(tmp_path)
    kod, cikti = _isle(tmp_path, 8, "oa-dilekce", ["--serh", UZUN_SERH, "--serh-kapi", "ingest-once"])
    assert kod != 0, cikti
    assert "adım-8" in cikti and "adım-5" in cikti and "tumu" in cikti, cikti
