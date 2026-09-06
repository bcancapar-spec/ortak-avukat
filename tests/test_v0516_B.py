# -*- coding: utf-8 -*-
"""v0.5.16 / GRUP B-1 — oa-pipeline / pipeline_kayit.py: BEKÇİ + GRAF KAPISI +
ŞERH-KAPI + H1 SAYAÇ (bütünleşik analiz K1/K2/P1/H1, karar #1 SERT, karar #2 N=3).

Bulgular (2026-09-06 denetim raporları):
- K1 [Hamle 2]: üç advisory bekçi (`_graf_yapisal_bosluk_uyarisi`,
  `_kiyas_bosluk_uyarisi`, `_usul_bosluk_uyarisi`) dosya-adı sözleşmesine
  (`*graf*.json` / `*kiyas*.json` / `*usul*.json`) bağlıydı — SKILL.md'nin kendi
  örneği `01-illiyet-denetim.json` bekçiden GEÇMİYORDU (bugün 0 uyarı). Artık
  `*.json` + `arac` damgası. Graf bekçisi A grubunun yeni alanlarını taşır
  (`denetim_coktu`, `baglanmamis_deliller`, `guc_beyansiz_kenarlar`); köprü
  düğüm 'perde' etiketi yine ALINMAZ (karar-malzemesi).
- K2 [karar #1 SERT]: adım-1/oa-illiyet UYGULANDI yazılırken graf denetimi
  `cevrimler`/`sema_hatalari`/`denetim_coktu` taşıyorsa BLOKLEYİCİ RET (GRAF
  KAPISI). Denetim JSON'u hiç yoksa RET DEĞİL (mevcut uyarı mantığı).
- P1 [Hamle 9]: `--serh-kapi ingest-once|graf|kiyas|kontrol|tumu` — şerh
  yalnız adlandırılan kapıyı geçer; çıplak `--serh` geriye uyumlu (tüm kapılar)
  ama görünür UYARI basar. C5 ELDEN düşürmesi şerhten BAĞIMSIZ: ELDEN + ŞERHLİ
  birlikte yazılabilir.
- H1 [Hamle 11 + karar #2 N=3]: `_hook_inline_dilekce_denetim` — (dosya, bulgu
  sınıfı) çifti `_oa/defter/inline-sayac.json`'da sayılır; 3 ARDIŞIK turda aynı
  sınıf kapanmıyorsa DURUM.md 'Avukat Kararı Bekleyen'e M7 satırı + stdout'ta
  TEK satır; bulgu kaybolunca sayaç sıfırlanır. Sınıf önceliği [F] > [Y] > [P] >
  diğer (ilk 5 satır).

Testler tempfile/tmp_path ile izole koşar; depo dosyalarına yazmaz; tüm
fikstürler sentetiktir (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
          / "scripts" / "pipeline_kayit.py")
SKILL_MD = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "SKILL.md"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
UZUN_SERH = "Sentetik gerekçe: avukat bilinçli olarak bu kapıyı geçiyor (>=30 karakter)."


def _load():
    spec = importlib.util.spec_from_file_location("pipeline_kayit_v0516_B", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pk():
    return _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _baslat(kok):
    kod, cikti = _cli(["--baslat", "Sentetik Dosya E. 2099/1", "--kok", str(kok)], cwd=kok)
    assert kod == 0, cikti


def _kunye_kur(kok):
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def _cikti_yaz(kok, ad, veri):
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    yol = cikti / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _durum_md(kok):
    return (kok / "_oa" / "DURUM.md").read_text(encoding="utf-8")


def _isle_illiyet(kok, ek=()):
    return _cli(["--isle", "--adim", "1", "--parca", "oa-illiyet", "--durum", "UYGULANDI",
                 "--kanit", UZUN_KANIT + " _oa/cikti/01-illiyet-denetim.json",
                 "--kok", str(kok)] + list(ek), cwd=kok)


# ═══════════════════ K1 — bekçiler ad sözleşmesinden kurtulur ═══════════════

def test_k1_graf_bekcisi_skill_ornegi_dosya_adiyla_cevrimi_gorur(pk, tmp_path):
    """SKILL.md'nin kendi örneği `01-illiyet-denetim.json` (adında 'graf' YOK)
    — K1 kanıtı: bugün 0 uyarı, artık 1."""
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    uyarilar = pk._graf_yapisal_bosluk_uyarisi(str(tmp_path))
    assert len(uyarilar) == 1
    assert "dairesel illiyet — A → B → A" in uyarilar[0]


def test_k1_graf_bekcisi_yeni_alanlari_tasir_perdeyi_almaz(pk, tmp_path):
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim",
        "denetim_coktu": "KeyError: 'kenarlar'",
        "baglanmamis_deliller": [{"id": "D1", "ad": "Sentetik banka dekontu"}, "D2"],
        "guc_beyansiz_kenarlar": [{"kaynak": "A", "hedef": "B", "tur": "odeme"}],
        "kopru_dugumler": [{"id": "S1", "ad": "Sentetik A.Ş.", "etiket": "perde"}],
    })
    uyarilar = pk._graf_yapisal_bosluk_uyarisi(str(tmp_path))
    metin = "\n".join(uyarilar)
    assert "graf denetimi ÇÖKTÜ (KeyError: 'kenarlar') — çöken kapı = atlanan kapı" in metin
    assert "bağlanmamış delil: Sentetik banka dekontu" in metin
    assert "bağlanmamış delil: D2" in metin
    assert "güç beyansız kenar A→B" in metin
    assert "perde" not in metin and "Sentetik A.Ş." not in metin  # karar-malzemesi


def test_k1_graf_bekcisi_denetim_coktu_bool_ve_hata_alani(pk, tmp_path):
    _cikti_yaz(tmp_path, "x.json", {"arac": "grafik_denetim", "denetim_coktu": True,
                                    "hata": "sentetik istisna"})
    uyarilar = pk._graf_yapisal_bosluk_uyarisi(str(tmp_path))
    assert len(uyarilar) == 1 and "ÇÖKTÜ (sentetik istisna)" in uyarilar[0]


def test_k1_kiyas_ve_usul_bekcileri_ad_bagimsiz(pk, tmp_path):
    _cikti_yaz(tmp_path, "05-silojizm.json", {
        "arac": "kiyas_denetim", "kritik_bosluk": True,
        "teyitsiz_ictihat": [], "unsur_vakia_eslesme": []})
    _cikti_yaz(tmp_path, "02-matris.json", {
        "arac": "usul_matris", "bosluklar": ["[G1] I1: sentetik boşluk"]})
    assert len(pk._kiyas_bosluk_uyarisi(str(tmp_path))) == 1
    assert len(pk._usul_bosluk_uyarisi(str(tmp_path))) == 1


def test_k1_damgasiz_json_hicbir_bekciye_girmez(pk, tmp_path):
    _cikti_yaz(tmp_path, "01-illiyet-graf.json", {"cevrimler": [["A", "B", "A"]]})
    _cikti_yaz(tmp_path, "05-kiyas.json", {"kritik_bosluk": True})
    _cikti_yaz(tmp_path, "02-usul.json", {"bosluklar": ["[G1] x"]})
    assert pk._graf_yapisal_bosluk_uyarisi(str(tmp_path)) == []
    assert pk._kiyas_bosluk_uyarisi(str(tmp_path)) == []
    assert pk._usul_bosluk_uyarisi(str(tmp_path)) == []


def test_k1_cevrim_bulgusu_durum_md_ye_ulasir(tmp_path):
    """Uçtan uca: SKILL örneği adıyla yazılan çevrim DURUM.md'de görünür."""
    _baslat(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    kod, _ = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    md = _durum_md(tmp_path)
    assert "Graf Yapısal Boşluk" in md
    assert "dairesel illiyet — A → B → A" in md


# ═══════════════════ K2 — GRAF KAPISI (karar #1: SERT) ══════════════════════

def test_k2_cevrimli_graf_adim1_illiyet_uygulandi_reddedilir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    kod, cikti = _isle_illiyet(tmp_path)
    assert kod != 0
    assert "GRAF KAPISI" in cikti and "01-illiyet-denetim.json" in cikti
    assert "dairesel illiyet" in cikti
    assert "--serh-kapi graf" in cikti


@pytest.mark.parametrize("veri, beklenen", [
    ({"arac": "grafik_denetim", "sema_hatalari": ["Düğüm 'X': 'tip' eksik"]}, "şema hatası"),
    ({"arac": "grafik_denetim", "denetim_coktu": "sentetik çökme"}, "denetim çöktü"),
])
def test_k2_sema_hatasi_ve_cokme_de_kapiyi_kapatir(tmp_path, veri, beklenen):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _cikti_yaz(tmp_path, "graf.json", veri)
    kod, cikti = _isle_illiyet(tmp_path)
    assert kod != 0 and "GRAF KAPISI" in cikti and beklenen in cikti


def test_k2_denetim_jsonu_yoksa_ret_degil(tmp_path):
    """Graf denetimi hiç koşmamışsa kapı KAPANMAZ (mevcut uyarı mantığı —
    ateşlemeyen kapı eklenmez; ELDEN/uyarı katmanı zaten görünür kılar)."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-illiyet", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    assert "GRAF KAPISI" not in cikti


def test_k2_temiz_graf_gecer_ve_baska_parcayi_etkilemez(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [], "sema_hatalari": [],
        "desteksiz_kenarlar": [{"kaynak": "A", "hedef": "B", "tur": "t"}]})
    kod, cikti = _isle_illiyet(tmp_path)
    assert kod == 0, cikti
    # çevrimli graf, adım-1'in DİĞER parçalarını (oa-interview) kapatmaz
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-interview", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti


def test_k2_serh_kapi_graf_ile_gerekceli_gecis(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    kod, cikti = _isle_illiyet(tmp_path, ["--serh", UZUN_SERH, "--serh-kapi", "graf"])
    assert kod == 0, cikti
    assert "ŞERHLİ" in cikti and "GRAF KAPISI ŞERH ile geçildi" in cikti
    assert "--serh-kapi verilmedi" not in cikti
    md = _durum_md(tmp_path)
    assert "ŞERHLİ" in md and "Avukat Kararı Bekleyen" in md


def test_k2_serh_kapi_yanlis_kapiyi_adlandirirsa_ret(tmp_path):
    """Şerh yalnız ADLANDIRILAN kapıyı geçer — 'kiyas' adlandırılmışken graf
    kapısı kapalı kalır."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    kod, cikti = _isle_illiyet(tmp_path, ["--serh", UZUN_SERH, "--serh-kapi", "kiyas"])
    assert kod != 0 and "GRAF KAPISI" in cikti
    assert "graf" in cikti  # hangi kapının adlandırılması gerektiği görünür


def test_k2_kod_tablosu_ve_skill_tablosu_satiri(pk):
    assert (1, "oa-illiyet") in pk.ONKOSUL_GRAF_KAPISI
    txt = SKILL_MD.read_text(encoding="utf-8")
    assert "GRAF KAPISI" in txt
    assert "--serh-kapi" in txt
    assert "| adım-1 | oa-illiyet |" in txt


# ═══════════════════ P1 — --serh-kapi + ELDEN/şerh bağımsızlığı ═════════════

def test_p1_ciplak_serh_geriye_uyum_ama_gorunur_uyari(tmp_path):
    _baslat(tmp_path)  # 00-kunye.json YOK → İNGEST-ÖNCE bloklu
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-interview", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--serh", UZUN_SERH,
                       "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "ŞERHLİ UYGULANDI" in cikti
    assert "--serh-kapi verilmedi" in cikti and "TÜM kapılara" in cikti


def test_p1_serh_kapi_ingest_once_adlandirilinca_uyari_yok(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-interview", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--serh", UZUN_SERH,
                       "--serh-kapi", "ingest-once", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "İNGEST-ÖNCE ŞERH ile geçildi" in cikti
    assert "--serh-kapi verilmedi" not in cikti


def test_p1_serh_kapi_graf_ingest_kapisini_gecmez(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-interview", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--serh", UZUN_SERH,
                       "--serh-kapi", "graf", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0
    assert "İNGEST-ÖNCE" in cikti and "ingest-once" in cikti


def test_p1_serh_kapi_tumu_her_kapiyi_gecer(tmp_path):
    _baslat(tmp_path)
    _cikti_yaz(tmp_path, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [["A", "B", "A"]]})
    kod, cikti = _isle_illiyet(tmp_path, ["--serh", UZUN_SERH, "--serh-kapi", "tumu"])
    assert kod == 0, cikti
    assert "İNGEST-ÖNCE ŞERH ile geçildi" in cikti  # ilk kapı ingest — o geçildi
    assert "--serh-kapi verilmedi" not in cikti


def test_p1_serh_kapi_serhsiz_verilirse_hata(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-interview", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--serh-kapi", "graf",
                       "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0 and "--serh-kapi" in cikti and "--serh" in cikti


def test_p1_elden_dusurme_serhten_bagimsiz(tmp_path):
    """İNGEST-ÖNCE şerhli + kanıtta _oa/ artefakt yolu YOK → statü ELDEN + şerh
    notu (eskiden şerh ELDEN düşürmesini bastırıyor, UYGULANDI kalıyordu).
    BİLİNÇLİ karakterizasyon değişikliği: P1 [Hamle 9] — şerh görünür
    istisnadır ama script artefaktının YOKLUĞUNU gizleyemez; ikisi de ayrı
    ayrı görünür kalır."""
    _baslat(tmp_path)
    kod, cikti = _cli(["--isle", "--adim", "1", "--parca", "oa-illiyet", "--durum",
                       "UYGULANDI", "--kanit", UZUN_KANIT, "--serh", UZUN_SERH,
                       "--serh-kapi", "ingest-once", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "→ ELDEN" in cikti
    assert "ELDEN DÜŞÜRME (C5)" in cikti
    assert "ŞERHLİ ELDEN" in cikti and "İNGEST-ÖNCE ŞERH ile geçildi" in cikti
    md = _durum_md(tmp_path)
    satir = next(s for s in md.splitlines() if "adım 1 (ALIM) / oa-illiyet" in s)
    assert "ELDEN" in satir and "⚠ŞERHLİ" in satir
    assert "ŞERHLİ ELDEN" in md  # Avukat Kararı Bekleyen'de de görünür
    olaylar = [json.loads(s) for s in (tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl")
               .read_text(encoding="utf-8").splitlines() if s.strip()]
    son = olaylar[-1]
    assert son["durum"] == "ELDEN" and son.get("serh") is True and son.get("serh_kapi") == "ingest-once"


# ═══════════════════ H1 — inline sayaç (karar #2: N=3) ═════════════════════

def _dava_kur(kok):
    _baslat(kok)
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    taslak = cikti / "01-dilekce-taslak.md"
    taslak.write_text("sentetik taslak metni — inline sayaç provası", encoding="utf-8")
    return taslak


def _payload(taslak):
    return {"tool_input": {"file_path": str(taslak)}}


def _sayac(kok):
    return json.loads((kok / "_oa" / "defter" / "inline-sayac.json").read_text(encoding="utf-8"))


def _tur(pk, kok, taslak, bulgular, monkeypatch, capsys):
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD",
                        types.SimpleNamespace(hizli_denetim=lambda m, k: list(bulgular)))
    pk._hook_inline_dilekce_denetim(str(kok), _payload(taslak))
    return capsys.readouterr().out


def test_h1_ayni_sinif_uc_turda_m7_satiri_ve_durum_md(pk, tmp_path, monkeypatch, capsys):
    taslak = _dava_kur(tmp_path)
    bulgu = ["[F] sentetik: netice-i talep faiz başlangıcı belirsiz"]
    out1 = _tur(pk, tmp_path, taslak, bulgu, monkeypatch, capsys)
    out2 = _tur(pk, tmp_path, taslak, bulgu, monkeypatch, capsys)
    assert "turdur kapanmıyor" not in out1 + out2
    assert _sayac(tmp_path)["_oa/cikti/01-dilekce-taslak.md"]["tur"] == 2
    out3 = _tur(pk, tmp_path, taslak, bulgu, monkeypatch, capsys)
    m7 = [s for s in out3.splitlines() if "turdur kapanmıyor" in s]
    assert len(m7) == 1, out3
    assert "inline bulgu 3 turdur kapanmıyor: [F]" in m7[0]
    assert "avukat kararı: kabul/düzelt" in m7[0]
    md = _durum_md(tmp_path)
    akb = md.split("## Avukat Kararı Bekleyen")[1].split("## ")[0]
    assert "inline bulgu 3 turdur kapanmıyor: [F]" in akb
    assert "01-dilekce-taslak.md" in akb


def test_h1_bulgu_kaybolunca_sayac_sifirlanir(pk, tmp_path, monkeypatch, capsys):
    taslak = _dava_kur(tmp_path)
    bulgu = ["[Y] sentetik: havada kalan alıntı"]
    for _ in range(3):
        _tur(pk, tmp_path, taslak, bulgu, monkeypatch, capsys)
    assert _sayac(tmp_path)["_oa/cikti/01-dilekce-taslak.md"]["tur"] == 3
    out = _tur(pk, tmp_path, taslak, [], monkeypatch, capsys)
    assert out.strip() == "inline denetim: temiz"
    assert "_oa/cikti/01-dilekce-taslak.md" not in _sayac(tmp_path)
    md = _durum_md(tmp_path)
    assert "turdur kapanmıyor" not in md
    # yeniden başlarsa 1'den sayar
    _tur(pk, tmp_path, taslak, bulgu, monkeypatch, capsys)
    assert _sayac(tmp_path)["_oa/cikti/01-dilekce-taslak.md"]["tur"] == 1


def test_h1_sinif_degisirse_ardisiklik_bozulur(pk, tmp_path, monkeypatch, capsys):
    taslak = _dava_kur(tmp_path)
    _tur(pk, tmp_path, taslak, ["[F] sentetik a"], monkeypatch, capsys)
    _tur(pk, tmp_path, taslak, ["[F] sentetik a"], monkeypatch, capsys)
    _tur(pk, tmp_path, taslak, ["[M] sentetik b"], monkeypatch, capsys)  # sınıf değişti
    kayit = _sayac(tmp_path)["_oa/cikti/01-dilekce-taslak.md"]
    assert kayit["sinif"] == "[M]" and kayit["tur"] == 1
    out = _tur(pk, tmp_path, taslak, ["[F] sentetik a"], monkeypatch, capsys)
    assert "turdur kapanmıyor" not in out


@pytest.mark.parametrize("bulgular, beklenen", [
    (["[M] m", "[P] p", "[Y] y", "[F] f"], "[F]"),
    (["[M] m", "[P] p", "[Y] y"], "[Y]"),
    (["[N] n", "[P] p", "[M] m"], "[P]"),
    (["[N] n", "[M] m"], "[N]"),                        # diğer: ilk satır
    (["[K] k1", "[K] k2", "[K] k3", "[K] k4", "[K] k5", "[F] f6"], "[K]"),  # yalnız ilk 5
    (["etiketsiz bulgu satırı"], None),
])
def test_h1_sinif_onceligi(pk, bulgular, beklenen):
    assert pk._inline_bulgu_sinifi(bulgular) == beklenen


def test_h1_bozuk_sayac_dosyasi_cokmez_sifirlanir_gorunur(pk, tmp_path, monkeypatch, capsys):
    taslak = _dava_kur(tmp_path)
    (tmp_path / "_oa" / "defter" / "inline-sayac.json").write_text("{bozuk", encoding="utf-8")
    out = _tur(pk, tmp_path, taslak, ["[F] sentetik"], monkeypatch, capsys)
    assert "İNLİNE DENETİM" in out
    assert "inline-sayac.json" in out and "sıfırlandı" in out
    assert _sayac(tmp_path)["_oa/cikti/01-dilekce-taslak.md"]["tur"] == 1


def test_h1_tespit_throttle_edilmez_defter_olayi_sinifi_tasir(pk, tmp_path, monkeypatch, capsys):
    """Sayaç TESPİTİ her turda işler (throttle yalnız basıma); eşikten sonra
    her turda ayrı bir `inline-sayac` defter olayı sınıf+tur bilgisini taşır
    (mevcut `inline-denetim` olayının 'N bulgu' notu DEĞİŞMEZ — v0.5.9
    karakterizasyonu korunur)."""
    taslak = _dava_kur(tmp_path)
    for _ in range(4):
        _tur(pk, tmp_path, taslak, ["[F] sentetik"], monkeypatch, capsys)
    assert _sayac(tmp_path)["_oa/cikti/01-dilekce-taslak.md"]["tur"] == 4
    olaylar = [json.loads(s) for s in (tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl")
               .read_text(encoding="utf-8").splitlines() if s.strip()]
    assert [o for o in olaylar if o.get("olay") == "inline-denetim"][-1]["not"] == "1 bulgu"
    sayac_olaylari = [o for o in olaylar if o.get("olay") == "inline-sayac"]
    assert len(sayac_olaylari) == 2  # tur 3 ve tur 4
    assert "[F]" in sayac_olaylari[-1]["not"] and "tur 4" in sayac_olaylari[-1]["not"]


def test_h1_skill_md_anlatimi_var():
    txt = SKILL_MD.read_text(encoding="utf-8")
    assert "inline-sayac.json" in txt
    assert "3 turdur kapanmıyor" in txt or "3 ARDIŞIK" in txt


# ═══════════════════════════════════════════════════════════════════════════
# GRUP B-2 — HAT SIRASI (P0-3 / A-2) + MÜVEKKİL KARARI (P1-9 / A-3) + AVUKAT
# HÜKMÜ SENSÖRÜ (A-28 / P2-8, SICRAMA-NOTU §3(A)+§5).
#
# - P0-3: ADIMLAR 6↔7 yer değişir — 6 = ANTİTEZ (oa-antitez), 7 = STRATEJİ
#   (oa-strateji). Gerekçe: karşı tarafın en güçlü tezi görülmeden dava/sulh
#   kararı verilmez (oa-strateji §2 antitezi girdi sayar). Eski defterlerdeki
#   (6, oa-strateji)/(7, oa-antitez) olayları «derle»'de hata değil — yeni
#   sıraya EŞLENİR ve DURUM.md'de «(eski hat sırası ≤v0.5.15 — adım eşlendi)»
#   notu düşer; YENİ yazımda eski çift RET.
# - P1-9: `--muvekkil-karari "<konu>" --secenekler "a|b|c"` (≥2 seçenek) açar,
#   `--muvekkil-karari-kapat "<konu>" --karar "<seçim>" --gerekce "<…>"`
#   kapatır (gerekçesiz RET — M7 disiplini). Kapanmamış müvekkil kararı varken
#   adım-10 KAPANIŞ UYGULANDI → görünür UYARI (bloklamaz).
# - A-28: `--avukat-hukmu KABUL|REVIZYONLA|RET --sebep <kapalı liste> --urun
#   <yol> [--not "…"]` → defter olayı + `_oa/defter/avukat-hukmu.jsonl`
#   (append-only) + DURUM.md «## Avukat Hükümleri» sayaç satırı. YALNIZ
#   ÖLÇER — hiçbir kapıyı/brifi değiştirmez ("enjeksiyon yapmaz").
# ═══════════════════════════════════════════════════════════════════════════

REFS = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "references"
SABLON_MD = REFS / "pipeline-durum-sablonu.md"
MUVEKKIL_SABLON_MD = REFS / "muvekkil-bilgilendirme-sablonu.md"


def _olaylar(kok):
    yol = kok / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def _isle(kok, adim, parca, ek=()):
    return _cli(["--isle", "--adim", str(adim), "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", UZUN_KANIT + " script koştu", "--kok", str(kok)] + list(ek), cwd=kok)


# ─────────────────────────── P0-3 — hat sırası ────────────────────────────

def test_p03_adimlar_6_antitez_7_strateji(pk):
    assert pk.ADIMLAR[6] == ("ANTİTEZ", ["oa-antitez"])
    assert pk.ADIMLAR[7] == ("STRATEJİ", ["oa-strateji"])
    assert (6, "oa-antitez") in pk.ONKOSUL_UYARI and (7, "oa-strateji") in pk.ONKOSUL_UYARI
    assert (6, "oa-strateji") not in pk.ONKOSUL_UYARI and (7, "oa-antitez") not in pk.ONKOSUL_UYARI
    assert "adım-6 (ANTİTEZ)" in pk.ONKOSUL_UYARI[(6, "oa-antitez")]
    assert "adım-7 (STRATEJİ)" in pk.ONKOSUL_UYARI[(7, "oa-strateji")]


def test_p03_eski_ciftle_yeni_isle_ret(tmp_path):
    """Yeni yazımda eski (≤v0.5.15) çift RET — sessiz eşleme YOK: yazan
    taraf yeni sırayı bilmek zorunda (geriye uyum yalnız OKUMA tarafındadır)."""
    _baslat(tmp_path); _kunye_kur(tmp_path)
    kod, cikti = _isle(tmp_path, 6, "oa-strateji")
    assert kod != 0 and "RET" in cikti and "v0.5.16" in cikti and "STRATEJİ adım 7" in cikti
    kod, cikti = _isle(tmp_path, 7, "oa-antitez")
    assert kod != 0 and "RET" in cikti and "ANTİTEZ adım 6" in cikti
    assert all(o.get("tip") != "adim" for o in _olaylar(tmp_path))  # hiçbiri deftere girmedi


def test_p03_yeni_sira_isle_gecer_ve_artefakt_bekcisi_iki_adi_kabul_eder(tmp_path):
    """06-antitez* (yeni ad) VE 07-antitez* (≤v0.5.15 adı) ikisi de adım-6
    UYARI bekçisini susturur — komşu parçaların (oa-antitez SKILL/dilekce_
    denetim) dosya adı sözleşmesi bu sürümde değişmek zorunda değil."""
    _baslat(tmp_path); _kunye_kur(tmp_path)
    yol = _cikti_yaz(tmp_path, "06-antitez-matris.json", {"arac": "antitez_matris", "x": "y" * 100})
    kod, cikti = _isle(tmp_path, 6, "oa-antitez",
                       ["--kanit", UZUN_KANIT + " script _oa/cikti/06-antitez-matris.json"])
    assert kod == 0, cikti
    assert "adım 6 / oa-antitez → UYGULANDI" in cikti and "UYARI: adım-6" not in cikti
    assert "adım 6 (ANTİTEZ) / oa-antitez: UYGULANDI" in _durum_md(tmp_path)
    yol.unlink()
    _cikti_yaz(tmp_path, "07-antitez-matris.json", {"arac": "antitez_matris", "x": "y" * 100})
    kod, cikti = _isle(tmp_path, 6, "oa-antitez",
                       ["--kanit", UZUN_KANIT + " script _oa/cikti/07-antitez-matris.json"])
    assert kod == 0 and "UYARI: adım-6" not in cikti
    # Strateji: artefakt yok → UYARI (bloklamaz), yeni numarayla.
    kod, cikti = _isle(tmp_path, 7, "oa-strateji")
    assert kod == 0 and "adım-7 (STRATEJİ)" in cikti and "07-strateji*" in cikti
    assert "adım 7 (STRATEJİ) / oa-strateji: UYGULANDI" in _durum_md(tmp_path)


def test_p03_eski_defter_yeni_siraya_eslenir(pk, tmp_path):
    """Geriye uyum: ≤v0.5.15 defterindeki (6, oa-strateji) / (7, oa-antitez)
    olayları derle'de HATA değil — yeni (7, oa-strateji) / (6, oa-antitez)
    hücrelerine eşlenir; DURUM.md eşlemeyi görünür not düşer; hayalet
    'oa-strateji' hücresi adım-6'da, 'oa-antitez' hücresi adım-7'de DOĞMAZ."""
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    satirlar = [
        {"zaman": "2026-08-01T10:00:00", "tip": "baslat", "dosya": "Eski Sentetik E. 2099/2"},
        {"zaman": "2026-08-01T10:01:00", "tip": "adim", "adim": 6, "parca": "oa-strateji",
         "durum": "UYGULANDI", "kanit": UZUN_KANIT, "surum": "0.5.15"},
        {"zaman": "2026-08-01T10:02:00", "tip": "adim", "adim": 7, "parca": "oa-antitez",
         "durum": "GEREKSIZ", "kanit": "GEREKÇE: sentetik", "surum": "0.5.15"},
        {"zaman": "2026-08-01T10:03:00", "tip": "avukat-karari", "adim": 6, "parca": "oa-strateji",
         "karar": "sulh", "gerekce": "sentetik gerekçe ≥15 kr"},
    ]
    (defter / "pipeline-olaylar.jsonl").write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in satirlar) + "\n", encoding="utf-8")
    d = pk.derle(str(defter / "pipeline-olaylar.jsonl"))
    assert d["adimlar"]["7"]["parcalar"]["oa-strateji"]["durum"] == "UYGULANDI"
    assert d["adimlar"]["7"]["parcalar"]["oa-strateji"].get("eski_hat_eslendi") is True
    assert d["adimlar"]["6"]["parcalar"]["oa-antitez"]["durum"] == "GEREKSIZ"
    assert "oa-strateji" not in d["adimlar"]["6"]["parcalar"]
    assert "oa-antitez" not in d["adimlar"]["7"]["parcalar"]
    assert str(d["avukat_kararlari"][0]["adim"]) == "7"   # karar da eşlenir → çatal çözülmüş sayılır
    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    md = _durum_md(tmp_path)
    assert "adım 7 (STRATEJİ) / oa-strateji: UYGULANDI" in md
    assert "(eski hat sırası ≤v0.5.15 — adım eşlendi)" in md
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "adım 6 (ANTİTEZ) / oa-strateji" not in cikti  # hayalet hücre yok


def test_p03_skill_md_sablon_ve_zincir_metni():
    txt = SKILL_MD.read_text(encoding="utf-8")
    assert "6. ANTİTEZ" in txt and "7. STRATEJİ" in txt
    assert "6. STRATEJİ" not in txt and "7. ANTİTEZ" not in txt
    assert "KIYAS → ANTİTEZ → STRATEJİ → YAZIM" in txt
    assert "KIYAS → STRATEJİ → ANTİTEZ" not in txt
    assert "| adım-6 | oa-antitez |" in txt and "| adım-7 | oa-strateji |" in txt
    sablon = SABLON_MD.read_text(encoding="utf-8")
    assert "| 6 | ANTİTEZ | oa-antitez" in sablon and "| 7 | STRATEJİ | oa-strateji" in sablon


# ─────────────────────── P1-9 — müvekkil kararı ───────────────────────────

def _mk_ac(kok, konu="Sulh teklifi", secenekler="kabul|ret|karşı teklif", ek=()):
    return _cli(["--muvekkil-karari", konu, "--secenekler", secenekler, "--kok", str(kok)]
                + list(ek), cwd=kok)


def _mk_kapat(kok, konu="Sulh teklifi", karar="ret",
              gerekce="müvekkil alacağın tamamında ısrarlı — sentetik"):
    args = ["--muvekkil-karari-kapat", konu, "--karar", karar, "--kok", str(kok)]
    if gerekce is not None:
        args += ["--gerekce", gerekce]
    return _cli(args, cwd=kok)


def test_p19_muvekkil_karari_acilir_durum_md_bolumu(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _mk_ac(tmp_path, ek=["--adim", "7", "--parca", "oa-strateji"])
    assert kod == 0, cikti
    assert "MÜVEKKİL KARARI" in cikti and "Sulh teklifi" in cikti
    md = _durum_md(tmp_path)
    assert "## Müvekkil Kararı Bekleyen" in md
    assert "Sulh teklifi" in md and "kabul | ret | karşı teklif" in md and "adım 7 / oa-strateji" in md
    olay = [o for o in _olaylar(tmp_path) if o.get("tip") == "muvekkil_karari"]
    assert len(olay) == 1 and olay[0]["secenekler"] == ["kabul", "ret", "karşı teklif"]
    assert olay[0].get("imza")  # araç-imzalı


def test_p19_tek_secenek_ret_ve_defter_yoksa_hata(tmp_path):
    kod, cikti = _mk_ac(tmp_path)
    assert kod != 0 and "defter" in cikti.lower()
    _baslat(tmp_path)
    kod, cikti = _mk_ac(tmp_path, secenekler="kabul")
    assert kod != 0 and "RET" in cikti and "2" in cikti
    kod, cikti = _mk_ac(tmp_path, secenekler="kabul|  |kabul")
    assert kod != 0 and "RET" in cikti


def test_p19_kapat_gerekcesiz_ret_gerekceli_gecer(tmp_path):
    _baslat(tmp_path); _mk_ac(tmp_path)
    kod, cikti = _mk_kapat(tmp_path, gerekce=None)
    assert kod != 0 and "RET" in cikti and "gerekçe" in cikti.lower()
    kod, cikti = _mk_kapat(tmp_path, gerekce="kısa")
    assert kod != 0 and "RET" in cikti
    kod, cikti = _mk_kapat(tmp_path)
    assert kod == 0, cikti
    md = _durum_md(tmp_path)
    bekleyen = md.split("## Müvekkil Kararı Bekleyen")[1].split("##")[0]
    assert "(yok)" in bekleyen
    assert "## Müvekkil Kararları (Kayıtlı" in md and "Sulh teklifi" in md and "**ret**" in md
    # append-only: açılış olayı silinmedi
    tipler = [o.get("tip") for o in _olaylar(tmp_path)]
    assert tipler.count("muvekkil_karari") == 1 and tipler.count("muvekkil_karari_kapat") == 1


def test_p19_kapat_acik_olmayan_konu_uyari_ama_bloklamaz(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _mk_kapat(tmp_path, konu="Hiç açılmamış konu")
    assert kod == 0 and "UYARI" in cikti and "AÇIK" in cikti


def test_p19_kapanmamis_kararla_adim10_kapanis_uyari_bloklamaz(tmp_path):
    _baslat(tmp_path); _kunye_kur(tmp_path)
    _mk_ac(tmp_path, konu="Tedbir teminatı", secenekler="yatır|yatırma")
    kod, cikti = _isle(tmp_path, 10, "oa-usta")
    assert kod == 0, cikti
    assert "UYARI" in cikti and "MÜVEKKİL KARARI" in cikti and "Tedbir teminatı" in cikti
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "Tedbir teminatı" in cikti and "kapanmamış müvekkil kararı" in cikti
    assert "Tedbir teminatı" in _durum_md(tmp_path).split("## Kapı Durumu")[1].split("##")[0]
    _mk_kapat(tmp_path, konu="Tedbir teminatı", karar="yatır")
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "kapanmamış müvekkil kararı" not in cikti


def test_p19_adim10_disinda_uyari_yok(tmp_path):
    _baslat(tmp_path); _kunye_kur(tmp_path)
    _mk_ac(tmp_path)
    kod, cikti = _isle(tmp_path, 2, "oa-alan")
    assert kod == 0 and "MÜVEKKİL KARARI" not in cikti


def test_p19_sablon_ve_skill_md():
    assert MUVEKKIL_SABLON_MD.is_file()
    s = MUVEKKIL_SABLON_MD.read_text(encoding="utf-8")
    assert "m.34" in s and "Mevzuat MCP teyit 2026-09-06" in s
    assert "m.6" in s and "Layer 0" in s and "aleyhe" in s
    txt = SKILL_MD.read_text(encoding="utf-8")
    assert "--muvekkil-karari" in txt and "--muvekkil-karari-kapat" in txt
    for konu in ("sulh teklifi", "dava değeri", "risk kabulü", "tedbir teminatı"):
        assert konu in txt.lower()
    assert "muvekkil-bilgilendirme-sablonu.md" in txt


# ─────────────────────── A-28 — avukat hükmü sensörü ──────────────────────

def _hukum(kok, hukum, urun="_oa/cikti/08-dilekce-taslak-v1.md", ek=()):
    return _cli(["--avukat-hukmu", hukum, "--urun", urun, "--kok", str(kok)] + list(ek), cwd=kok)


def _hukum_defteri(kok):
    yol = kok / "_oa" / "defter" / "avukat-hukmu.jsonl"
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def test_a28_kabul_kaydi_iki_deftere_ve_durum_md_sayaca(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _hukum(tmp_path, "KABUL")
    assert kod == 0, cikti
    assert "AVUKAT HÜKMÜ" in cikti and "KABUL" in cikti
    olay = [o for o in _olaylar(tmp_path) if o.get("tip") == "avukat_hukmu"]
    assert len(olay) == 1 and olay[0]["hukum"] == "KABUL"
    assert olay[0]["urun"].endswith("08-dilekce-taslak-v1.md")
    assert olay[0].get("imza")
    h = _hukum_defteri(tmp_path)
    assert len(h) == 1 and h[0]["hukum"] == "KABUL" and h[0]["urun"] and h[0]["zaman"]
    md = _durum_md(tmp_path)
    assert "## Avukat Hükümleri" in md
    assert "KABUL 1 / REVİZYONLA 0 / RET 0" in md


def test_a28_ret_revizyon_sebep_zorunlu_kapali_liste(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _hukum(tmp_path, "RET")
    assert kod != 0 and "RET" in cikti and "--sebep" in cikti
    kod, cikti = _hukum(tmp_path, "REVIZYONLA")
    assert kod != 0 and "--sebep" in cikti
    kod, cikti = _hukum(tmp_path, "RET", ek=["--sebep", "keyfi"])
    assert kod != 0
    kod, cikti = _hukum(tmp_path, "KABULX")
    assert kod != 0
    kod, cikti = _cli(["--avukat-hukmu", "RET", "--sebep", "usul", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0 and "--urun" in cikti
    assert not (tmp_path / "_oa" / "defter" / "avukat-hukmu.jsonl").exists()


def test_a28_sayac_ve_sebep_dagilimi_append_only(tmp_path):
    _baslat(tmp_path)
    assert _hukum(tmp_path, "KABUL")[0] == 0
    assert _hukum(tmp_path, "REVIZYONLA", ek=["--sebep", "usul", "--not", "tebliğ tarihi eksik"])[0] == 0
    assert _hukum(tmp_path, "RET", ek=["--sebep", "olgu"])[0] == 0
    assert _hukum(tmp_path, "RET", urun="_oa/cikti/08-dilekce-taslak-v2.md", ek=["--sebep", "olgu"])[0] == 0
    h = _hukum_defteri(tmp_path)
    assert [x["hukum"] for x in h] == ["KABUL", "REVIZYONLA", "RET", "RET"]
    assert h[1]["not"] == "tebliğ tarihi eksik" and h[1]["sebep"] == "usul"
    md = _durum_md(tmp_path)
    assert "KABUL 1 / REVİZYONLA 1 / RET 2" in md
    assert "olgu: 2" in md and "usul: 1" in md


def test_a28_yalniz_olcer_kapi_ve_denetle_degismez(tmp_path):
    """SICRAMA-NOTU §5 şartı: sensör ölçer, ENJEKSİYON yapmaz — RET hükmü
    --denetle exit kodunu/sorun listesini değiştirmez, hiçbir adımı bloklamaz."""
    _baslat(tmp_path); _kunye_kur(tmp_path)
    kod0, cikti0 = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    sorun0 = [s for s in cikti0.splitlines() if s.strip().startswith("✗")]
    assert _hukum(tmp_path, "RET", ek=["--sebep", "hukuk"])[0] == 0
    kod1, cikti1 = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    sorun1 = [s for s in cikti1.splitlines() if s.strip().startswith("✗")]
    assert kod1 == kod0 and sorun1 == sorun0
    assert "hük" not in cikti1.lower()          # denetle çıktısına hüküm satırı sızmaz
    kod, cikti = _isle(tmp_path, 2, "oa-alan")
    assert kod == 0 and "hük" not in cikti.lower()


def test_a28_defter_yoksa_hata_bozuk_hukum_defteri_cokertmez(tmp_path):
    kod, cikti = _hukum(tmp_path, "KABUL")
    assert kod != 0 and "defter" in cikti.lower()
    _baslat(tmp_path)
    (tmp_path / "_oa" / "defter" / "avukat-hukmu.jsonl").write_text("{bozuk\n", encoding="utf-8")
    assert _hukum(tmp_path, "KABUL")[0] == 0
    md = _durum_md(tmp_path)
    assert "KABUL 1 / REVİZYONLA 0 / RET 0" in md and "bozuk" in md.lower()


def test_a28_skill_md_sensor_anlatimi():
    txt = SKILL_MD.read_text(encoding="utf-8")
    assert "--avukat-hukmu" in txt and "avukat-hukmu.jsonl" in txt
    assert "kapanışta avukat hükmü kaydı önerilir" in txt
    assert "enjeksiyon yapmaz" in txt
    assert "Avukat Hükümleri" in txt
