# -*- coding: utf-8 -*-
"""v0.5.18 — tam zincir fikstür taslakları Layer 0'dan TEMİZ geçmeli.

NEDEN VAR: UDF teslimde Layer 0 (gizlilik_tara, strict) artık ZORUNLU ve KATI ENGEL (avukat
kararı 2026-10-05). `udf_arglari` / `gercek_udf_yazici_gerekli` testleri, udf-cli oturumu AÇIK
bir makinede (avukatın kendi makinesi) teslim zincirini `--udf-yok` OLMADAN sonuna kadar koşar.
Taslakta 11 haneli kimlik benzeri bir sayı olduğunda (checksum tutmasa bile) tarama ASK verir →
(c) kapısı BLOK → bu testler yalnız o makinede kırmızıya döner (CI'da ve OA_TEST_UDF_YAZICI=0
ile görünmez). Kimlik unsuru dilekçe denetiminde ETİKETTEN ("T.C. Kimlik No") tanındığı için
fikstürde rakam gerekmez. Bu test, fikstürlerin o makinede de zinciri geçebileceğini kilitler.
"""
import ast
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
GIZLILIK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-gizlilik" / "scripts" / "gizlilik_tara.py"
DOSYALAR = ("test_teslim_makbuz.py", "test_teslim_paketi.py")


@pytest.fixture(scope="module")
def gt():
    spec = importlib.util.spec_from_file_location("v0518_fikstur_gt", GIZLILIK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _taslaklar():
    for ad in DOSYALAR:
        agac = ast.parse((REPO / "tests" / ad).read_text(encoding="utf-8"))
        for d in ast.walk(agac):
            if (isinstance(d, ast.Assign) and isinstance(d.value, ast.Constant)
                    and isinstance(d.value.value, str) and "TASLAK" in getattr(d.targets[0], "id", "")
                    and len(d.value.value) > 200):
                yield "%s:%s" % (ad, d.targets[0].id), d.value.value


def test_tam_zincir_taslaklari_layer0_strict_temiz(gt):
    taslaklar = list(_taslaklar())
    assert len(taslaklar) >= 3, taslaklar   # test boş geçmesin
    kirli = []
    for ad, metin in taslaklar:
        deny, ask = gt.tara(metin, "strict", [])
        if deny or ask:
            kirli.append((ad, [a for _, a in deny + ask]))
    assert kirli == [], kirli
