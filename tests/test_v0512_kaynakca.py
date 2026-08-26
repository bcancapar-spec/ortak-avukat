# -*- coding: utf-8 -*-
"""v0.5.12 — İÇTİHAT KAYNAKÇASI (link zinciri tamamlayıcısı).

Avukat kuralı (2026-08-27): "dilekçeye veya herhangi bir çalışmaya giren
TÜM yargı kararlarının linkleri TÜM çıktılarda olsun."

Mevcut zemin: muhakeme kaydı her künye için **KAYNAK-URL:** satırı taşır
(v0.5.5.3'ten beri; URL uydurulamaz, yalnız teyitten gelir). Eksik olan:
bu linklerin ÜRÜNE (taslak → UDF → PDF → 40-UYAP kopyaları) taşınması.

v0.5.12 sözleşmesi:
  1. `kaynakca_uret.py` taslaktaki karar künyelerini (esas/karar çifti
     üzerinden) muhakeme kaydıyla eşler ve taslağın sonuna işaretli
     '## İÇTİHAT KAYNAKÇASI' bloğunu İDEMPOTENT işler.
  2. URL'si olan künye linkli satır alır; URL'siz künye GİZLENMEZ —
     "erişim linki kütüğe işlenmedi" notuyla listelenir (uydurma link,
     çıplak künyeden kötüdür; yokluk görünür kalır).
  3. Taslakta geçmeyen muhakeme künyesi kaynakçaya GİRMEZ.
  4. teslim_paketi zinciri kaynakçayı UDF üretiminden ÖNCE işler; makbuza
     `ictihat_kaynakca` alanı (linkli/linksiz sayıları) düşer.

Tamamen ağsız/deterministik; tüm veriler sentetiktir.
"""
import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"


def _yukle(gorece, ad):
    yol = SK / gorece
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ka():
    return _yukle("oa-kontrol/scripts/kaynakca_uret.py", "v0512_kaynakca")


MUHAKEME = """# İÇTİHAT MUHAKEME ZİNCİRİ — test

---

**KUNYE:** Yargıtay 4. Hukuk Dairesi E. 2021/19277 K. 2022/10757 T. 21.09.2022
**KAYNAK-URL:** https://ornek.adalet.gov.tr/ictihat/111
**DAMGA:** LEHE

## İLGİLİ-KISIM
"..."

---

**KUNYE:** Yargıtay 17. Hukuk Dairesi E. 2012/12754 K. 2013/273 T. 21.01.2013
**DAMGA:** LEHE

## İLGİLİ-KISIM
"..."

---

**KUNYE:** Yargıtay 12. Hukuk Dairesi E. 2020/1111 K. 2021/2222 T. 01.02.2021
**KAYNAK-URL:** https://ornek.adalet.gov.tr/ictihat/333
**DAMGA:** LEHE
"""

TASLAK = """# CEVAP DİLEKÇESİ (sentetik)

Yargıtay 4. Hukuk Dairesi E. 2021/19277 K. 2022/10757 sayılı kararında ...
Ayrıca Yargıtay 17. Hukuk Dairesi E. 2012/12754 K. 2013/273 sayılı kararı da ...

NETİCE-İ TALEP: ...
"""


def _kok_kur(tmp_path):
    kok = tmp_path
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "11-ictihat-muhakeme.md").write_text(MUHAKEME, encoding="utf-8")
    taslak = cikti / "08-taslak.md"
    taslak.write_text(TASLAK, encoding="utf-8")
    return kok, taslak


def test_harita_muhakemeden_cikar(ka, tmp_path):
    kok, _ = _kok_kur(tmp_path)
    harita = ka.muhakeme_haritasi(str(kok))
    assert len(harita) == 3
    urller = {k: v.get("url") for k, v in harita.items()}
    assert "https://ornek.adalet.gov.tr/ictihat/111" in urller.values()
    assert None in urller.values()          # URL'siz kayıt da haritada


def test_taslaga_islenir_ve_idempotent(ka, tmp_path):
    kok, taslak = _kok_kur(tmp_path)
    r1 = ka.taslaga_isle(str(taslak), str(kok))
    m1 = taslak.read_text(encoding="utf-8")
    assert "İÇTİHAT KAYNAKÇASI" in m1
    assert "https://ornek.adalet.gov.tr/ictihat/111" in m1
    assert r1["linkli"] == 1 and r1["linksiz"] == 1
    # taslakta geçmeyen 12. HD kararı bloğa GİRMEZ (linkli sayısı 1 kaldı)
    assert "2021/2222" not in m1
    # idempotenz: ikinci koşu ikinci blok üretmez
    r2 = ka.taslaga_isle(str(taslak), str(kok))
    m2 = taslak.read_text(encoding="utf-8")
    assert m2.count("İÇTİHAT KAYNAKÇASI") == 1
    assert r2["linkli"] == 1


def test_linksiz_kunye_gizlenmez(ka, tmp_path):
    kok, taslak = _kok_kur(tmp_path)
    ka.taslaga_isle(str(taslak), str(kok))
    m = taslak.read_text(encoding="utf-8")
    assert "2012/12754" in m                 # linksiz künye bloğa girdi
    assert "işlenmedi" in m.lower() or "LİNKSİZ" in m


def test_muhakeme_yoksa_zarif(ka, tmp_path):
    kok = tmp_path
    (kok / "_oa" / "cikti").mkdir(parents=True)
    taslak = kok / "_oa" / "cikti" / "08-t.md"
    taslak.write_text("Yargıtay 4. HD E. 2021/1 K. 2022/2 ...", encoding="utf-8")
    r = ka.taslaga_isle(str(taslak), str(kok))
    assert r["linkli"] == 0
    # taslakta künye VAR ama muhakeme kaydı yok → linksiz olarak görünür
    assert r["linksiz"] >= 1
    assert "KAYNAKÇASI" in taslak.read_text(encoding="utf-8")


def test_teslim_makbuzuna_alan_girer(ka, tmp_path):
    """Entegrasyon sözleşmesi: teslim_paketi._kaynakca_isle makbuz alanını
    döndürür ve taslağı işler."""
    teslim = _yukle("oa-kontrol/scripts/teslim_paketi.py", "v0512_teslim")
    kok, taslak = _kok_kur(tmp_path)
    alan = teslim._kaynakca_isle(str(taslak), str(kok))
    assert alan["linkli"] == 1 and alan["linksiz"] == 1
    assert "İÇTİHAT KAYNAKÇASI" in taslak.read_text(encoding="utf-8")
