# -*- coding: utf-8 -*-
"""grafik_denetim.py --zincir (v0.5.8 P3 — semantica confidence_decay +
weakest_link deseni) testleri. Advisory: --zincir bayrağı olmadan çıktı
DEĞİŞMEZ (78 karakterizasyon testi korunur)."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-illiyet"
          / "scripts" / "grafik_denetim.py")

spec = importlib.util.spec_from_file_location("grafik_denetim", SCRIPT)
gd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gd)


def _graf(kenarlar_ek):
    dugumler = {x: {"id": x, "tip": "olay", "ad": x.upper()}
                for x in ("fiil", "ara", "zarar", "yan")}
    return dugumler, kenarlar_ek


def test_tek_zincir_guven_carpimi_ve_zayif_halka():
    d, k = _graf([
        {"kaynak": "fiil", "hedef": "ara", "kategori": "illiyet",
         "tur": "fiil_netice", "guc": "guclu"},          # 0.9
        {"kaynak": "ara", "hedef": "zarar", "kategori": "illiyet",
         "tur": "sebep_zarar", "guc": "tartismali"},     # 0.4
    ])
    z = gd.zincir_analizi(d, k)
    assert len(z) == 1
    assert z[0]["yol"] == ["fiil", "ara", "zarar"]
    assert abs(z[0]["guven"] - 0.36) < 1e-9              # 0.9 * 0.4
    assert z[0]["en_zayif"]["guc"] == "tartismali"


def test_catalli_graf_en_kirilgan_once():
    d, k = _graf([
        {"kaynak": "fiil", "hedef": "zarar", "kategori": "illiyet",
         "tur": "fiil_netice", "guc": "dispozitif"},     # güven 1.0
        {"kaynak": "yan", "hedef": "ara", "kategori": "illiyet",
         "tur": "fiil_netice", "guc": "zayif"},          # güven 0.6
    ])
    z = gd.zincir_analizi(d, k)
    assert len(z) == 2 and z[0]["guven"] <= z[1]["guven"]  # kırılgan önce


def test_guc_beyan_edilmemis_varsayilan_ve_iliski_kenari_haric():
    d, k = _graf([
        {"kaynak": "fiil", "hedef": "zarar", "kategori": "illiyet",
         "tur": "fiil_netice"},                          # guc yok → 0.8
        {"kaynak": "yan", "hedef": "zarar", "kategori": "iliski",
         "tur": "ortaklik", "guc": "guclu"},             # illiyet DEĞİL — hariç
    ])
    z = gd.zincir_analizi(d, k)
    assert len(z) == 1 and abs(z[0]["guven"] - 0.8) < 1e-9
    assert z[0]["en_zayif"]["guc"] == "beyan-yok"


def test_cli_bayraksiz_cikti_degismez_bayrakli_json_alani():
    d = {"dugumler": [{"id": "a", "tip": "olay", "ad": "A"},
                      {"id": "b", "tip": "olay", "ad": "B"}],
         "kenarlar": [{"kaynak": "a", "hedef": "b", "kategori": "illiyet",
                       "tur": "fiil_netice", "guc": "guclu",
                       "dayanak_delil": [], "dogrulama": "iddia"}]}
    tmp = pathlib.Path(tempfile.mkdtemp())
    graf = tmp / "graf.json"
    graf.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    out_json = tmp / "out.json"
    # bayraksız: bölüm 8 YOK (karakterizasyon korunur)
    p1 = subprocess.run([sys.executable, str(SCRIPT), str(graf)],
                        capture_output=True, text=True, encoding="utf-8")
    assert "ZİNCİR GÜVEN" not in (p1.stdout or "")
    # bayraklı: bölüm 8 VAR + json'a zincirler alanı düşer
    p2 = subprocess.run([sys.executable, str(SCRIPT), str(graf), "--zincir",
                         "--json", str(out_json)],
                        capture_output=True, text=True, encoding="utf-8")
    assert "ZİNCİR GÜVEN" in (p2.stdout or "")
    r = json.loads(out_json.read_text(encoding="utf-8"))
    assert r["zincirler"] and r["zincirler"][0]["guven"] == 0.9
