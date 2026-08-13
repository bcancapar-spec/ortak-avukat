# -*- coding: utf-8 -*-
"""v0.5.8.1 tetik paketi testleri (447 provası dersleri):
[K] m.6 cephanelik bekçisi (dilekce_denetim) + mühürsüz-teslim nöbetçisi
(pipeline_kayit Stop hook'u). İkisi de ADVISORY — asla bloklamaz."""
import importlib.util
import pathlib
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"


def _yukle(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

dd = _yukle(SK / "oa-dilekce" / "scripts" / "dilekce_denetim.py", "dd")
pk = _yukle(SK / "oa-pipeline" / "scripts" / "pipeline_kayit.py", "pk")


# ── [K] m.6 cephanelik bekçisi ──────────────────────────────────────────

def test_muhtemel_savunma_analizi_yakalanir():
    metin = ("Davalı idare, tebligatın usulüne uygun olduğunu savunabilir; "
             "ancak bu savunma yerinde değildir çünkü...")
    u = dd.cephanelik_ifsa_uyarilari(metin)
    assert u and "m.6" in u[0] and "CEPHANELİĞE" in u[0]


def test_karsi_taraf_ileri_surebilir_kalibi():
    metin = ("Karşı taraf zamanaşımı def'ini ileri sürebilir ise de bu itiraz "
             "dinlenemez.")
    assert dd.cephanelik_ifsa_uyarilari(metin)


def test_normal_iddia_anlatimi_temiz():
    metin = ("Davalı idare 05/12/2024 tarihli ihbarnameyi tebliğ etmiştir. "
             "İşlem hukuka aykırıdır; iptali gerekir. Müvekkil gelir elde "
             "etmemiştir.")
    assert dd.cephanelik_ifsa_uyarilari(metin) == []


# ── mühürsüz-teslim nöbetçisi (Stop hook) ───────────────────────────────

def _kok(urunler, muhurlu=()):
    kok = pathlib.Path(tempfile.mkdtemp())
    d = kok / "_oa" / "cikti"
    d.mkdir(parents=True)
    for ad in urunler:
        (d / ad).write_bytes(b"x")
    for ad in muhurlu:
        (d / (ad + ".prov.json")).write_text("{}", encoding="utf-8")
    return str(kok)


def test_muhursuz_udf_uyari_uretir():
    kok = _kok(["dilekce.udf", "dilekce.pdf"])
    u = pk._muhursuz_teslim_uyarisi(kok)
    assert u and "MÜHÜRSÜZ" in u and "dilekce.udf" in u and "muhur_yaz" in u


def test_muhurlu_urun_sessiz():
    kok = _kok(["dilekce.udf"], muhurlu=["dilekce.udf"])
    assert pk._muhursuz_teslim_uyarisi(kok) is None


def test_test_onekli_ve_urunsuz_sessiz():
    assert pk._muhursuz_teslim_uyarisi(_kok(["TEST-deneme.udf", "_t.udf"])) is None
    assert pk._muhursuz_teslim_uyarisi(_kok([])) is None
