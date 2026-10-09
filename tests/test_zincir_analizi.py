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
    """v0.5.16/A G4 (avukat kararı #5, bilinçli değişiklik): beyan-yok
    ağırlığı 0.8 → 0.4 (≤ tartışmalı). Gerekçe: 0.8, `guc` beyan ETMEYEN
    kenarı `zayif` beyan edenden (0.6) güçlü sayıyordu — dürüstlük ödülü
    tersine dönmüştü (beyan etmemek kazandırıyordu)."""
    d, k = _graf([
        {"kaynak": "fiil", "hedef": "zarar", "kategori": "illiyet",
         "tur": "fiil_netice"},                          # guc yok → 0.4
        {"kaynak": "yan", "hedef": "zarar", "kategori": "iliski",
         "tur": "ortaklik", "guc": "guclu"},             # illiyet DEĞİL — hariç
    ])
    z = gd.zincir_analizi(d, k)
    assert len(z) == 1 and abs(z[0]["guven"] - 0.4) < 1e-9
    assert z[0]["en_zayif"]["guc"] == "beyan-yok"
    assert z[0]["en_zayif"]["agirlik"] == gd.GUC_VARSAYILAN == 0.4


def test_cli_zincir_varsayilan_zincirsiz_kapatir_zincir_noop():
    """v0.5.8.4 yeni sözleşme (bilinçli değişiklik — 372'de 0 ateşleme kanıtı):
    (a) bayraksız → bölüm 8 VAR + json'a 'zincirler' düşer (varsayılan);
    (b) --zincirsiz → bölüm 8 YOK + json'da 'zincirler' anahtarı YOK;
    (c) --zincir → geriye-uyum NO-OP (varsayılanla aynı çıktı)."""
    d = {"dugumler": [{"id": "a", "tip": "olay", "ad": "A"},
                      {"id": "b", "tip": "olay", "ad": "B"}],
         # v0.5.16/A: illiyet_tipi eklendi — eksikliği artık exit 3 şema
         # hatasıdır; bu test zincir sözleşmesini sınar, kapıyı değil.
         "kenarlar": [{"kaynak": "a", "hedef": "b", "kategori": "illiyet",
                       "tur": "fiil_netice", "illiyet_tipi": "dogal",
                       "guc": "guclu", "dayanak_delil": [], "dogrulama": "iddia"}]}
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


# ── v0.5.18 B-10 — zincir TAVANI sessiz kalmaz ─────────────────────────────
# Fable tutarlılık raporu (2026-10-07) B-10: `zincir_analizi` maksimal yol
# sayımını `en_cok*5` tavanında keser, sonra "en kırılgan 10"u bu KISMİ
# kümeden seçer. Tavan aşıldıysa en zayıf halka listesi tam DEĞİLDİR; eskiden
# bunu söyleyen tek satır yoktu (belirsizlik gizleniyordu — anayasa: okunamayan/
# denetlenemeyen "temiz" sayılmaz). Sözleşme: `zincir_uyarisi` =
# "zincir tavanı aşıldı — en zayıf halka listesi tam değil"; başka uyarıyla
# (çevrim) birleşirse " · " ile eklenir. Advisory: exit kodu DEĞİŞMEZ.

TAVAN_UYARISI = "zincir tavanı aşıldı — en zayıf halka listesi tam değil"


def _katmanli_dag(dallanma, derinlik):
    """Kök → dallanma^1 → … → dallanma^derinlik yaprak: her kök→yaprak yolu
    maksimal bir illiyet zinciridir (yol sayısı = dallanma**derinlik); çevrim yok."""
    dugumler = [{"id": "KOK", "tip": "olay", "ad": "Kök olay (kurgu)"},
                {"id": "D1", "tip": "delil", "ad": "Delil (kurgu)"}]
    kenarlar, onceki = [], ["KOK"]
    for _ in range(derinlik):
        yeni = []
        for p in onceki:
            for i in range(dallanma):
                c = f"{p}_{i}"
                dugumler.append({"id": c, "tip": "olay", "ad": f"{c} (kurgu)"})
                kenarlar.append({"kaynak": p, "hedef": c, "kategori": "illiyet",
                                 "tur": "fiil_netice", "illiyet_tipi": "uygun", "guc": "guclu",
                                 "dogrulama": "teyitli", "dayanak_delil": ["D1"],
                                 "norm": "çıpa (kurgu)"})
                yeni.append(c)
        onceki = yeni
    return {"dugumler": dugumler, "kenarlar": kenarlar}


def _cli_json(tmp, graf):
    yol = tmp / "graf.json"
    yol.write_text(json.dumps(graf, ensure_ascii=False), encoding="utf-8")
    out = tmp / "out.json"
    p = subprocess.run([sys.executable, str(SCRIPT), str(yol), "--json", str(out)],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout or "", json.loads(out.read_text(encoding="utf-8"))


def test_tavan_asildiginda_uyari_basilir(tmp_path):
    """4^3 = 64 maksimal yol > tavan (10×5 = 50): rapor §8 ve JSON
    `zincir_uyarisi` tavan uyarısını taşır; liste yine ≤10 öğe; exit 0
    (advisory — çevrim/şema yok). In-process API: `zincir_analizi` listeyi
    döndürmeye devam eder (geriye uyum), `zincir_analizi_tam` bayrağı verir."""
    graf = _katmanli_dag(4, 3)
    kod, out, r = _cli_json(tmp_path, graf)
    assert kod == 0
    assert TAVAN_UYARISI in out
    assert r["zincir_uyarisi"] == TAVAN_UYARISI
    assert len(r["zincirler"]) == 10

    d = {x["id"]: x for x in graf["dugumler"]}
    zincirler, tavan_asildi = gd.zincir_analizi_tam(d, graf["kenarlar"])
    assert tavan_asildi is True and len(zincirler) == 10
    assert gd.zincir_analizi(d, graf["kenarlar"]) == zincirler


def test_tavan_asilmayan_grafta_uyari_yok(tmp_path):
    """4^2 = 16 yol < 50: uyarı yok (`zincir_uyarisi` null) — yanlış alarm yasağı."""
    graf = _katmanli_dag(4, 2)
    kod, out, r = _cli_json(tmp_path, graf)
    assert kod == 0
    assert TAVAN_UYARISI not in out and r["zincir_uyarisi"] is None
    d = {x["id"]: x for x in graf["dugumler"]}
    assert gd.zincir_analizi_tam(d, graf["kenarlar"])[1] is False


def test_cevrim_ve_tavan_birlikte_iki_uyari_birlesir(tmp_path):
    """Ayrı bileşende çevrim + tavanı aşan DAG: iki uyarı da görünür (" · " ile
    birleşik); çevrim exit 3'ü korur, tavan uyarısı onu DEĞİŞTİRMEZ."""
    graf = _katmanli_dag(4, 3)
    graf["dugumler"] += [{"id": "X", "tip": "olay", "ad": "X (kurgu)"},
                         {"id": "Y", "tip": "olay", "ad": "Y (kurgu)"}]
    for a, b in (("X", "Y"), ("Y", "X")):
        graf["kenarlar"].append({"kaynak": a, "hedef": b, "kategori": "illiyet",
                                 "tur": "fiil_netice", "illiyet_tipi": "uygun", "guc": "guclu",
                                 "dogrulama": "teyitli", "dayanak_delil": ["D1"], "norm": "çıpa (kurgu)"})
    kod, out, r = _cli_json(tmp_path, graf)
    assert kod == 3 and r["blok_sinifi"] == ["cevrim"]
    assert "çevrim var" in r["zincir_uyarisi"] and TAVAN_UYARISI in r["zincir_uyarisi"]
    assert " · " in r["zincir_uyarisi"]
    assert TAVAN_UYARISI in out
