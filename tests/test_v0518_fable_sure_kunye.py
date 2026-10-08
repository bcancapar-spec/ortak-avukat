# -*- coding: utf-8 -*-
"""v0.5.18 — FABLE BAĞIMSIZ DENETİMİ (2026-10-08): süre hesabı ve künye teyidi bulguları.

NEDEN VAR: davayı kazanma ölçütünde en ağır iki sınıf burada kilitlenir — GEÇ son gün (hak kaybı)
ve mahkemeye giden YANLIŞ künye. Her bulgu ana oturumca yeniden üretildi (künye bulgularının
dördü v0.5.17.1'de de vardı; bu dalın getirdiği değil, ama kapının kendi sözleşmesini — "teyitsiz
atıf → exit 1" — çiğniyordu):
  S3  Kural verilmeyen (`--sure/--birim`) usul hesabında yargı kolunun uzatması (HMK m.104 / İYUK
      m.8-3 / CMK m.331-4) TEYİTLİ sayılıyor, manşet GEÇ tarih oluyordu. Bu uzatmalar yalnız ilgili
      kanunun KENDİ tayin ettiği sürelere uygulanır; hâkimin verdiği kesin süre ya da başka
      kanundan (İİK, İş K., TBK, Av.K.) gelen süre UZAMAZ → 15 günlük süre 07.09 değil 17.08 olabilir.
  S1  Son gün hafta sonu kaymasıyla adli tatilin İLK gününe (20 Temmuz) düşünce uzatma okuması hiç
      gösterilmiyordu (sınır hâli sessizdi).
  S2  Son gün arifeye denk gelince (2429 s.K.: 13:00'ten itibaren tatil) uyarı yoktu.
  S4  "PARASAL KESİNLİK" uyarısı kanun yolu olmayan her sürede basılıyordu (alarm yorgunluğu).
  K1  İki ayrı kararın esas ve karar numaraları (aynı 260 karakterlik pencerede) yapışık künyeyi
      TEYİTLİ yapıyordu. K2  Esas ile karar yer değiştirmiş künye TEYİTLİ'ydi.
  K3  İzde aynı esas/karar FARKLI daireye aitken künye TEYİTLİ + exit 0'dı (E/K her dairede yılda
      sıfırdan başlar — farklı daire büyük olasılıkla yanlış künyedir).
  K4  AYM başvuru numarası herhangi bir Yargıtay esas numarasıyla eşleşip TEYİTLİ oluyordu.
Kontrol testleri iz kaybını (haksız TEYİTSİZ) da kilitler. Sentetik veri; ağ yok.
"""
import importlib.util
import pathlib
import subprocess
import sys
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"
HESAPLA = SK / "oa-sure" / "scripts" / "hesapla_sure.py"
KUNYE = SK / "oa-kontrol" / "scripts" / "kunye_teyit.py"


@pytest.fixture(scope="module")
def hs():
    spec = importlib.util.spec_from_file_location("_fable_sk_hesapla", HESAPLA)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_fable_sk_hesapla"] = mod
    spec.loader.exec_module(mod)
    return mod


def _hes(hs, kural=None, teblig="2026-08-01", miktar=None, birim=None, yargi="hukuk", tur="usul"):
    if kural:
        miktar, birim = hs.KURALLAR[kural][0], hs.KURALLAR[kural][1]
    bilgi = {}
    son, _rapor, uyarilar = hs.hesapla(date.fromisoformat(teblig), miktar, birim, yargi, tur=tur,
                                       kural=kural, _bilgi=bilgi)
    return son, uyarilar, bilgi


# ── S3 — kuralsız usul hesabı uzatmayı manşete koymaz ──────────────────────────────────

@pytest.mark.parametrize("yargi,teblig,miktar,manset,alt", [
    ("hukuk", "2026-08-01", 15, "2026-08-17", "2026-09-07"),   # 16.08 Pazar → 17.08
    ("idari", "2026-08-01", 30, "2026-08-31", "2026-09-07"),
])
def test_S3_kuralsiz_hesapta_manset_uzamasiz_erken_tarih(hs, yargi, teblig, miktar, manset, alt):
    son, uyarilar, bilgi = _hes(hs, teblig=teblig, miktar=miktar, birim="gun", yargi=yargi)
    assert son.isoformat() == manset, (son, uyarilar)
    assert bilgi["alt_son"] is not None and bilgi["alt_son"].isoformat() == alt, bilgi
    assert any("KURALSIZ" in u for u in uyarilar), uyarilar


def test_S3_ceza_kolu_bilerek_disarida_YCGK_ve_ihtiyat_plani_aynen(hs):
    """CMK m.331/4 "Adlî tatile rastlayan süreler işlemez" sınırsız yazılmıştır; tatil içi tebliğde
    YCGK'ya birebir bağlı Y-02 kararı manşeti, eski daire uygulaması ihtiyat planını (ERKEN tarih)
    zaten taşır — S3 ceza koluna uygulanmaz."""
    son, uyarilar, bilgi = _hes(hs, teblig="2026-08-10", miktar=7, birim="gun", yargi="ceza")
    assert son.isoformat() == "2026-09-07", (son, uyarilar)
    assert bilgi["ihtiyat_son"] is not None and bilgi["ihtiyat_son"].isoformat() == "2026-09-03", bilgi
    assert not any("KURALSIZ" in u for u in uyarilar), uyarilar


def test_S3_kurali_verilen_hesap_degismez(hs):
    son, _u, _b = _hes(hs, kural="hmk_istinaf", teblig="2026-07-25")
    assert son.isoformat() == "2026-09-07"


def test_S3_tatil_disinda_kuralsiz_hesap_gurultusuz(hs):
    son, uyarilar, bilgi = _hes(hs, teblig="2026-03-02", miktar=15, birim="gun")
    assert son.isoformat() == "2026-03-17" and bilgi["alt_son"] is None, (son, bilgi)
    assert not any("KURALSIZ" in u for u in uyarilar), uyarilar


@pytest.mark.parametrize("yargi,birim,tur", [("icra", "gun", "usul"), ("hukuk", "isgunu", "usul"),
                                              ("hukuk", "gun", "maddi")])
def test_S3_icra_isgunu_ve_maddi_sure_etkilenmez(hs, yargi, birim, tur):
    _son, uyarilar, _b = _hes(hs, teblig="2026-08-01", miktar=15, birim=birim, yargi=yargi, tur=tur)
    assert not any("KURALSIZ" in u for u in uyarilar), uyarilar


# ── S1 — hafta sonu kayması adli tatilin ilk gününe düşerse sınır hâli görünür ───────────

@pytest.mark.parametrize("kural,yargi,teblig,manset,alt", [
    ("hmk_istinaf", "hukuk", "2026-07-05", "2026-07-20", "2026-09-07"),
    ("iyuk_istinaf", "idari", "2026-06-19", "2026-07-20", "2026-09-07"),
    ("cmk_istinaf", "ceza", "2026-07-05", "2026-07-20", "2026-09-03"),
])
def test_S1_kayma_adli_tatilin_ilk_gunune_dusunce_sinir_hali(hs, kural, yargi, teblig, manset, alt):
    son, uyarilar, bilgi = _hes(hs, kural=kural, teblig=teblig, yargi=yargi)
    assert son.isoformat() == manset, (son, uyarilar)          # manşet ERKEN (güvenli) kalır
    assert bilgi["alt_son"] is not None and bilgi["alt_son"].isoformat() == alt, bilgi
    assert any("SINIR HÂLİ" in u and "20 Temmuz" in u for u in uyarilar), uyarilar


def test_S1_ham_bitis_tatil_icindeyse_bugunku_uzatma_aynen(hs):
    son, uyarilar, _b = _hes(hs, kural="hmk_istinaf", teblig="2026-07-06")
    assert son.isoformat() == "2026-09-07"
    assert not any("20 Temmuz" in u and "SINIR HÂLİ" in u for u in uyarilar)


def test_S1_kayma_yoksa_sinir_hali_yok(hs):
    son, uyarilar, bilgi = _hes(hs, kural="hmk_istinaf", teblig="2026-07-03")   # 17.07 Cuma
    assert son.isoformat() == "2026-07-17" and bilgi["alt_son"] is None, (son, bilgi)
    assert not any("SINIR HÂLİ" in u and "20 Temmuz" in u for u in uyarilar)


# ── S2 — arife ────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("teblig,son_gun", [("2026-03-12", "2026-03-19"),    # Ramazan arifesi
                                            ("2026-05-19", "2026-05-26")])   # Kurban arifesi
def test_S2_son_gun_arifeye_denk_gelirse_ogleden_once_uyarisi(hs, teblig, son_gun):
    son, uyarilar, _b = _hes(hs, kural="iik_sikayet", teblig=teblig, yargi="icra")
    assert son.isoformat() == son_gun, (son, uyarilar)
    assert any("ARİFE" in u and "13:00" in u for u in uyarilar), uyarilar


def test_S2_arife_olmayan_gunde_uyari_yok(hs):
    son, uyarilar, _b = _hes(hs, kural="iik_sikayet", teblig="2026-03-10", yargi="icra")
    assert son.isoformat() == "2026-03-17"
    assert not any("ARİFE" in u for u in uyarilar), uyarilar


# ── S4 — parasal kesinlik uyarısı yalnız kanun yolu kurallarında ─────────────────────────

def test_S4_parasal_kesinlik_kanun_yolunda_var(hs):
    _s, uyarilar, _b = _hes(hs, kural="hmk_istinaf", teblig="2026-03-02")
    assert any("PARASAL KESİNLİK" in u for u in uyarilar)


@pytest.mark.parametrize("kural,yargi", [("avk_istifa_vekalet_devam", "hukuk"),
                                         ("is_ise_iade_arabulucu", "hukuk"),
                                         ("iik_sikayet", "icra"), ("aihm_basvuru", "hukuk"),
                                         (None, "hukuk")])
def test_S4_kanun_yolu_olmayan_surede_parasal_kesinlik_gurultusu_yok(hs, kural, yargi):
    _s, uyarilar, _b = _hes(hs, kural=kural, teblig="2026-03-02", miktar=None if kural else 15,
                            birim=None if kural else "gun", yargi=yargi)
    assert not any("PARASAL KESİNLİK" in u for u in uyarilar), (kural, uyarilar)


# ── K1-K4 — yanlış künye TEYİTLİ sayılmaz; doğru künye iz kaybetmez ─────────────────────

KUTUK = ("| Zaman | Araç | Künye | Damga | Döküm |\n|---|---|---|---|---|\n"
         "| 2026-10-01 | ictihat_getir | Yargıtay 3. HD, E. 2019/1111, K. 2020/2222, T. 15.01.2020 "
         "| DAMGA=LEHE DOKUM-SINIFI=tam-metin | dokum/a.md |\n"
         "| 2026-10-01 | ictihat_getir | Yargıtay 11. HD, E. 2019/3333, K. 2020/4444, T. 20.02.2020 "
         "| DAMGA=LEHE DOKUM-SINIFI=tam-metin | dokum/b.md |\n")
DOKUM = ("ictihat_ara sonucu:\n1) Yargıtay 3. HD E. 2019/1111 K. 2020/2222 — kira alacağı\n"
         "2) Yargıtay 11. HD E. 2019/3333 K. 2020/4444 — marka\n")


def _kunye_kos(tmp_path, cumle, kutuk=KUTUK, dokumler=None):
    kok = tmp_path / "dava"
    (kok / "_oa" / "teyit" / "dokum").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir()
    (kok / "_oa" / "teyit" / "kunye-teyit.md").write_text(kutuk, encoding="utf-8")
    for ad, metin in (dokumler if dokumler is not None else {"arama.md": DOKUM}).items():
        (kok / "_oa" / "teyit" / "dokum" / ad).write_text(metin, encoding="utf-8")
    taslak = kok / "taslak.md"
    taslak.write_text("# DİLEKÇE\n\n" + cumle + "\n", encoding="utf-8")
    cp = subprocess.run([sys.executable, str(KUNYE), str(taslak), "--kok", str(kok)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, cp.stdout + cp.stderr


@pytest.mark.parametrize("ad,cumle", [
    ("K1 iki kararın parçası", "Yargıtay 3. HD'nin E. 2019/1111, K. 2020/4444 sayılı kararı uyarınca."),
    ("K2 esas-karar ters", "Yargıtay 3. HD'nin E. 2020/2222, K. 2019/1111 sayılı kararı uyarınca."),
    ("K3 farklı daire", "Yargıtay 9. HD'nin E. 2019/1111, K. 2020/2222 sayılı kararı uyarınca."),
    ("K4 AYM no = Yargıtay esası", "Anayasa Mahkemesi'nin B. No: 2019/1111 sayılı kararı emsaldir."),
])
def test_K_yanlis_kunye_teyitli_sayilmaz(tmp_path, ad, cumle):
    kod, out = _kunye_kos(tmp_path, cumle)
    assert kod == 1 and "[TEYİTSİZ]" in out and "[TEYİTLİ]" not in out, (ad, out[-1800:])


def test_K3_merci_celiskisi_acikca_soylenir(tmp_path):
    kod, out = _kunye_kos(tmp_path, "Yargıtay 9. HD'nin E. 2019/1111, K. 2020/2222 sayılı kararı.")
    assert kod == 1 and "MERCİ ÇELİŞKİSİ" in out, out[-1800:]


def test_K_dogru_kunye_teyitli_kalir(tmp_path):
    kod, out = _kunye_kos(tmp_path, "Yargıtay 3. HD'nin E. 2019/1111, K. 2020/2222 sayılı kararı.")
    assert kod == 0 and "[TEYİTLİ]" in out, out[-1800:]


def test_K_ayristirilamayan_dokum_bicimi_iz_kaybettirmez(tmp_path):
    """Kontrol: markdown kalın döküm başlığı ayrıştırıcının tanımadığı bir biçimdir — iz sayı
    varlığıyla korunur (haksız TEYİTSİZ yok)."""
    dokum = {"karar.md": "T.C. YARGITAY 3. Hukuk Dairesi\n**Esas No:** 2021/5555 **Karar No:** 2022/6666\n"}
    kod, out = _kunye_kos(tmp_path, "Yargıtay 3. HD'nin E. 2021/5555, K. 2022/6666 sayılı kararı.",
                          dokumler=dokum)
    assert kod == 0 and "[TEYİTLİ]" in out, out[-1800:]


@pytest.mark.parametrize("dokum", [
    "Anayasa Mahkemesi Genel Kurulu, Başvuru Numarası: 2018/1234, Karar Tarihi: 15.01.2020\n",
    "aym_ictihat_ara sonucu: BB 2018/1234 — mülkiyet hakkı\n",
])
def test_K4_dogru_aym_kunyesi_teyitli_kalir(tmp_path, dokum):
    kod, out = _kunye_kos(tmp_path, "Anayasa Mahkemesi'nin B. No: 2018/1234 sayılı kararı emsaldir.",
                          dokumler={"aym.md": dokum})
    assert kod == 0 and "[TEYİTLİ]" in out, out[-1800:]
