# -*- coding: utf-8 -*-
"""grafik_denetim.py zincir analizi (v0.5.8 P3 — semantica confidence_decay +
weakest_link deseni) testleri.

SÖZLEŞME DEĞİŞİKLİĞİ (v0.5.8.4, bilinçli): zincir analizi artık VARSAYILAN
çalışır — 372 Torbalı sahasında grafik_denetim 2 kez koştu ama --zincir
bayrağı 0 kez verildi, analiz HİÇ üretilmedi (opsiyonel kapı = ateşlemeyen
kapı). Yeni sözleşme: bayraksız ÜRETİLİR; --zincirsiz kapatır; --zincir
geriye uyum için kabul edilen NO-OP'tur. Advisory niteliği değişmedi."""
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


def test_cli_zincir_varsayilan_zincirsiz_kapatir_zincir_noop():
    """v0.5.8.4 yeni sözleşme (bilinçli değişiklik — 372'de 0 ateşleme kanıtı):
    (a) bayraksız → bölüm 8 VAR + json'a 'zincirler' düşer (varsayılan);
    (b) --zincirsiz → bölüm 8 YOK + json'da 'zincirler' anahtarı YOK;
    (c) --zincir → geriye-uyum NO-OP (varsayılanla aynı çıktı)."""
    d = {"dugumler": [{"id": "a", "tip": "olay", "ad": "A"},
                      {"id": "b", "tip": "olay", "ad": "B"}],
         "kenarlar": [{"kaynak": "a", "hedef": "b", "kategori": "illiyet",
                       "tur": "fiil_netice", "guc": "guclu",
                       "dayanak_delil": [], "dogrulama": "iddia"}]}
    tmp = pathlib.Path(tempfile.mkdtemp())
    graf = tmp / "graf.json"
    graf.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    # (a) bayraksız: VARSAYILAN üretim
    out1 = tmp / "out1.json"
    p1 = subprocess.run([sys.executable, str(SCRIPT), str(graf),
                         "--json", str(out1)],
                        capture_output=True, text=True, encoding="utf-8")
    assert "ZİNCİR GÜVEN" in (p1.stdout or "")
    r1 = json.loads(out1.read_text(encoding="utf-8"))
    assert r1["zincirler"] and r1["zincirler"][0]["guven"] == 0.9

    # (b) --zincirsiz: bilinçli kapatma
    out2 = tmp / "out2.json"
    p2 = subprocess.run([sys.executable, str(SCRIPT), str(graf), "--zincirsiz",
                         "--json", str(out2)],
                        capture_output=True, text=True, encoding="utf-8")
    assert "ZİNCİR GÜVEN" not in (p2.stdout or "")
    r2 = json.loads(out2.read_text(encoding="utf-8"))
    assert "zincirler" not in r2

    # (c) --zincir: geriye-uyum no-op — varsayılanla aynı
    out3 = tmp / "out3.json"
    p3 = subprocess.run([sys.executable, str(SCRIPT), str(graf), "--zincir",
                         "--json", str(out3)],
                        capture_output=True, text=True, encoding="utf-8")
    assert "ZİNCİR GÜVEN" in (p3.stdout or "")
    r3 = json.loads(out3.read_text(encoding="utf-8"))
    assert r3["zincirler"] == r1["zincirler"]
