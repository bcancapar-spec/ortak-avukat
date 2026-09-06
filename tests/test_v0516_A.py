# -*- coding: utf-8 -*-
"""v0.5.16 / GRUP A-1 — oa-illiyet grafik_denetim.py: KAPI SERTLİĞİ +
DEDEKTÖR ONARIMLARI (bütünleşik denetim 2026-09-06: K2, G6, G1, G5, G7,
G8, G3, G4, G2; hamleler 2/5/6).

Kapatılan açıklar ve yeni sözleşme (BİLİNÇLİ karakterizasyon değişikliği —
eski "bulguda da exit 0" kilidi kaldırıldı; gerekçe: opsiyonel kapı =
ateşlemeyen kapı, avukat kararı #1 SERT kapı):

* K2+G6  exit sözleşmesi: 0 temiz · 1 kullanım hatası · 2 DENETİM ÇÖKTÜ
         (try/except sarmalı; --json'a denetim_coktu:true) · 3 çevrim VEYA
         şema hatası (blok_sinifi). DFS'ler özyinelemesiz; 5.000 düğümlük
         zincir çökmez.
* G1     çevrimler MİNİMAL ve mükerrersiz (Johnson benzeri basit çevrim
         sayımı ≤200 düğümde): A→B→C→B grafında ["B","C","B"].
* G5     mükerrer düğüm id → şema hatası (yukle sessizce yutuyordu); ilk
         kayıt korunur.
* G7     bağlanmamış delil AYRI SINIF (oa-vakia yetim delil semantiği):
         dayanak_delil referansı id veya ad-benzerliği (≥0.6) ile bağlar.
* G8     köprü düğüm: ayırdığı bileşenlerden en az ikisi ≥2 düğümlü;
         etiket tip-duyarlı ("perde" | "yapisal"); karar/mahkeme muaf.
* G3     illiyet kenarında dogrulama ZORUNLU (şema hatası); §3 desteksiz
         = dogrulama yok VEYA (iddia + delilsiz); norm eksik → advisory.
* G4     GUC_VARSAYILAN 0.4; guc_beyansiz_kenarlar ayrı sınıf.
* G2     köksüz illiyet grafı → "GÜVENİLMEZ" (sahte-yeşil kapanışı);
         çevrim varken §7 "çevrimde anlamsız" uyarısı.

Girdiler tempfile/tmp_path tabanlı izole dizinlerde üretilir; fikstürler
sentetiktir (anayasa m.7); repo dosyalarına dokunulmaz.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-illiyet"
          / "scripts" / "grafik_denetim.py")
SKILL_MD = SCRIPT.parents[1] / "SKILL.md"

spec = importlib.util.spec_from_file_location("grafik_denetim_v0516", SCRIPT)
gd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gd)


def _cli(*args, timeout=120):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout,
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


def _graf_yaz(kok, graf, ad="graf.json"):
    yol = kok / ad
    yol.write_text(json.dumps(graf, ensure_ascii=False), encoding="utf-8")
    return yol


def _kos_json(tmp_path, graf):
    yol = _graf_yaz(tmp_path, graf)
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    return kod, out, err, sonuc


def _ill(a, b, **ek):
    k = {"kaynak": a, "hedef": b, "kategori": "illiyet", "tur": "sebep_zarar",
         "illiyet_tipi": "uygun", "guc": "guclu", "dogrulama": "teyitli",
         "dayanak_delil": ["D1"], "norm": "çıpa"}
    k.update(ek)
    return k


def _ils(a, b, **ek):
    k = {"kaynak": a, "hedef": b, "kategori": "iliski", "tur": "ortaklik",
         "dogrulama": "teyitli", "dayanak_delil": ["D1"], "norm": "çıpa"}
    k.update(ek)
    return k


def _olay(*ids):
    return [{"id": i, "tip": "olay", "ad": f"Olay {i}"} for i in ids]


def _temiz_graf():
    return {
        "dugumler": _olay("A", "B", "C") + [
            {"id": "D1", "tip": "delil", "ad": "Bilirkisi Raporu"}],
        "kenarlar": [_ill("A", "B"), _ill("B", "C")],
    }


# ═══════════════════════════════════════════════════════════════════════════
# K2 + G6 — EXIT SÖZLEŞMESİ (SERT KAPI) + ÇÖKME SARMALI
# ═══════════════════════════════════════════════════════════════════════════

def test_temiz_graf_exit0_ve_json_cikis_kodu_0(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _temiz_graf())
    assert kod == 0, f"stdout:\n{out}\nstderr:\n{err}"
    assert sonuc["cikis_kodu"] == 0
    assert sonuc["denetim_coktu"] is False
    assert sonuc["blok_sinifi"] == []
    assert sonuc["arac"] == "grafik_denetim"


def test_sema_hatasi_exit3_blok_sinifi_sema(tmp_path):
    graf = _temiz_graf()
    graf["dugumler"].append({"id": "N", "ad": "Tipsiz"})  # tip eksik
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3, out
    assert sonuc["cikis_kodu"] == 3
    assert sonuc["blok_sinifi"] == ["sema"]
    assert sonuc["denetim_coktu"] is False
    assert "✗ Düğüm 'N': 'tip' eksik" in out


def test_cevrim_exit3_blok_sinifi_cevrim(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"].append(_ill("C", "A"))
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert sonuc["blok_sinifi"] == ["cevrim"]
    assert sonuc["cevrimler"] == [["A", "B", "C", "A"]]


def test_sema_ve_cevrim_birlikte_iki_sinif(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"].append(_ill("C", "A"))
    graf["dugumler"].append({"id": "N", "ad": "Tipsiz"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert sonuc["blok_sinifi"] == ["sema", "cevrim"]


def test_kullanim_hatasi_exit1_aynen():
    kod, out, err = _cli()
    assert kod == 1
    assert "Kullanım:" in out


def test_dosya_yok_denetim_coktu_exit2_json_yazilir(tmp_path):
    """K2: çökme artık traceback+exit 1 DEĞİL — görünür 'DENETİM ÇÖKTÜ'
    satırı + exit 2 + --json'a çökme kaydı (bekçi okuyabilsin)."""
    json_yol = tmp_path / "sonuc.json"
    yok = tmp_path / "yok.json"
    kod, out, err = _cli(yok, "--json", json_yol)
    assert kod == 2
    assert "DENETİM ÇÖKTÜ: FileNotFoundError" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["arac"] == "grafik_denetim"
    assert sonuc["denetim_coktu"] is True
    assert sonuc["cikis_kodu"] == 2
    assert "FileNotFoundError" in sonuc["hata"]
    assert sonuc["girdi"] == str(yok)


def test_bozuk_json_denetim_coktu_exit2(tmp_path):
    yol = tmp_path / "graf.json"
    yol.write_text("{ bozuk json", encoding="utf-8")
    kod, out, err = _cli(yol)
    assert kod == 2
    assert "DENETİM ÇÖKTÜ: JSONDecodeError" in out


def test_id_eksik_dugum_traceback_degil_sema_hatasi(tmp_path):
    """K2: `id` eksik düğüm eskiden yukle() içinde KeyError traceback'iydi."""
    graf = _temiz_graf()
    graf["dugumler"].append({"tip": "olay", "ad": "Kimliksiz"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert "Traceback" not in err
    assert any("'id' eksik" in h for h in sonuc["sema_hatalari"]), sonuc["sema_hatalari"]
    assert "✗ Düğüm #4: 'id' eksik" in out


def test_bes_bin_dugumlu_zincir_cokmez(tmp_path):
    """G6: DFS'ler özyinelemesiz — 5.000 düğümlük doğrusal illiyet zinciri
    RecursionError ile çökmez, exit 0 döner (çevrim yok, şema temiz)."""
    n = 5000
    ids = [f"N{i}" for i in range(n)]
    graf = {"dugumler": _olay(*ids),
            "kenarlar": [_ill(ids[i], ids[i + 1]) for i in range(n - 1)]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, f"stderr:\n{err[-2000:]}"
    assert "RecursionError" not in err
    assert sonuc["cevrimler"] == []
    assert sonuc["ozet"] == {"dugum": n, "kenar": n - 1}


def test_bes_bin_dugumlu_cevrimli_zincir_exit3_cokmez(tmp_path):
    """G6+G2: 5.000 düğümlük halka (çevrim) — özyinelemesiz çevrim tespiti
    çökmez, tek çevrim raporlar, köksüz zincir GÜVENİLMEZ damgası basar."""
    n = 5000
    ids = [f"N{i}" for i in range(n)]
    graf = {"dugumler": _olay(*ids),
            "kenarlar": [_ill(ids[i], ids[(i + 1) % n]) for i in range(n)]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3, f"stderr:\n{err[-2000:]}"
    assert len(sonuc["cevrimler"]) == 1
    assert len(sonuc["cevrimler"][0]) == n + 1
    assert "GÜVENİLMEZ" in out


# ═══════════════════════════════════════════════════════════════════════════
# G1 — ÇEVRİM: MİNİMAL + MÜKERRERSİZ
# ═══════════════════════════════════════════════════════════════════════════

def test_cevrim_minimal_cevrim_disi_dugum_icermez(tmp_path):
    """A→B→C→B: eski DFS [A,B,C,B] (A çevrim-dışı) raporluyordu;
    doğru çevrim tam olarak ["B","C","B"]."""
    graf = {"dugumler": _olay("A", "B", "C", "D"),
            "kenarlar": [_ill("A", "B"), _ill("B", "C"), _ill("C", "B"),
                         _ill("C", "D")]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert sonuc["cevrimler"] == [["B", "C", "B"]]
    assert "✗ Olay B → Olay C → Olay B" in out


def test_iki_ayri_cevrim_iki_kez_raporlanir_mukerrer_yok(tmp_path):
    graf = {"dugumler": _olay("A", "B", "C", "D", "E"),
            "kenarlar": [_ill("A", "B"), _ill("B", "A"),
                         _ill("C", "D"), _ill("D", "E"), _ill("E", "C"),
                         _ill("B", "C")]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert len(sonuc["cevrimler"]) == 2
    assert ["A", "B", "A"] in sonuc["cevrimler"]
    assert ["C", "D", "E", "C"] in sonuc["cevrimler"]
    # mükerrer yok: aynı çevrim iki rotasyonla iki kez YOK
    kanonik = {tuple(sorted(c[:-1])) for c in sonuc["cevrimler"]}
    assert len(kanonik) == 2


def test_cevrim_fonksiyonu_deterministik_ve_kucuk_kume():
    kenarlar = [_ill("A", "B"), _ill("B", "C"), _ill("C", "A"), _ill("C", "B")]
    c1 = gd.cevrim_var_mi(kenarlar)
    c2 = gd.cevrim_var_mi(kenarlar)
    assert c1 == c2
    assert sorted(len(c) for c in c1) == [3, 4]  # B-C-B ve A-B-C-A


# ═══════════════════════════════════════════════════════════════════════════
# G5 — MÜKERRER DÜĞÜM ID
# ═══════════════════════════════════════════════════════════════════════════

def test_mukerrer_id_sema_hatasi_ilk_kayit_korunur(tmp_path):
    graf = _temiz_graf()
    graf["dugumler"].append({"id": "A", "tip": "tuzel_kisi", "ad": "Ikinci A"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert "sema" in sonuc["blok_sinifi"]
    assert "mükerrer id 'A' (2 kez)" in out
    assert any("mükerrer id 'A' (2 kez)" in h for h in sonuc["sema_hatalari"])
    # ilk kayıt korunur, düşürülmez
    ilk = [d for d in sonuc["dugumler"] if d["id"] == "A"]
    assert len(ilk) == 1 and ilk[0]["ad"] == "Olay A" and ilk[0]["tip"] == "olay"
    assert sonuc["ozet"]["dugum"] == 4


# ═══════════════════════════════════════════════════════════════════════════
# G7 — BAĞLANMAMIŞ DELİL (ayrı sınıf)
# ═══════════════════════════════════════════════════════════════════════════

def test_alti_delilden_besi_dayanakla_anilir_yetim_cikmaz(tmp_path):
    """Avukat kararı #6: delil düğümü kenar ucu olmasa da dayanak_delil ile
    anılıyorsa BAĞLIDIR (yetim değil). Referans: id (D1..D3), tam ad (D4),
    benzer serbest metin ≥0.6 (D5). D6 hiçbir yerde anılmıyor → yetim DEĞİL,
    ayrı sınıf 'baglanmamis_deliller'."""
    deliller = [
        {"id": "D1", "tip": "delil", "ad": "Kaza Tutanagi"},
        {"id": "D2", "tip": "delil", "ad": "Bilirkisi Raporu"},
        {"id": "D3", "tip": "delil", "ad": "Tanik Beyani"},
        {"id": "D4", "tip": "delil", "ad": "Hastane Epikrizi"},
        {"id": "D5", "tip": "delil", "ad": "Trafik Sigorta Policesi"},
        {"id": "D6", "tip": "delil", "ad": "Banka Dekontu"},
    ]
    graf = {
        "dugumler": _olay("A", "B", "C") + deliller,
        "kenarlar": [
            _ill("A", "B", dayanak_delil=["D1", "D2"]),
            _ill("B", "C", dayanak_delil=["D3", "Hastane Epikrizi"]),
            _ils("A", "C", dayanak_delil=["trafik sigorta poliçesi"]),
        ],
    }
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, out
    assert sonuc["yetim_dugumler"] == []
    assert sonuc["baglanmamis_deliller"] == [{"id": "D6", "ad": "Banka Dekontu"}]
    assert "### 2b. BAĞLANMAMIŞ DELİL" in out
    assert "Banka Dekontu (D6)" in out


def test_delil_disi_yetim_mantigi_degismez(tmp_path):
    graf = _temiz_graf()
    graf["dugumler"].append({"id": "Y", "tip": "nesne", "ad": "Bagsiz Nesne"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["yetim_dugumler"] == [{"id": "Y", "ad": "Bagsiz Nesne"}]
    assert sonuc["baglanmamis_deliller"] == []


def test_baglanmamis_delil_temiz_grafta_bos_ve_exit0(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _temiz_graf())
    assert kod == 0
    assert sonuc["baglanmamis_deliller"] == []
    assert "✓ Her delil bir kenara bağlı." in out


def test_ad_benzerligi_tr_kucuk_harf_katlamali():
    assert gd._tr_kucuk("İSTİHKAK Iddia") == "istihkak ıddia"
    assert gd._delil_eslesir("bilirkişi raporu", "Bilirkişi Raporu")
    assert gd._delil_eslesir("bilirkisi rapor", "Bilirkişi Raporu")
    assert not gd._delil_eslesir("banka dekontu", "Bilirkişi Raporu")


# ═══════════════════════════════════════════════════════════════════════════
# G8 — KÖPRÜ DÜĞÜM: ≥2 düğümlü en az iki bileşen + tip-duyarlı etiket
# ═══════════════════════════════════════════════════════════════════════════

def _halter(orta_tip="gercek_kisi", kanat_tip="tuzel_kisi"):
    dugumler = [
        {"id": "S1", "tip": kanat_tip, "ad": "Sirket Bir"},
        {"id": "O1", "tip": "gercek_kisi", "ad": "Ortak Bir", "usul_rolu": "davali"},
        {"id": "M", "tip": orta_tip, "ad": "Mudur Kisi", "usul_rolu": "davali"},
        {"id": "S2", "tip": kanat_tip, "ad": "Sirket Iki"},
        {"id": "O2", "tip": "gercek_kisi", "ad": "Ortak Iki", "usul_rolu": "davali"},
    ]
    ciftler = [("S1", "O1"), ("S1", "M"), ("O1", "M"),
               ("M", "S2"), ("M", "O2"), ("S2", "O2")]
    return {"dugumler": dugumler,
            "kenarlar": [_ils(a, b) for a, b in ciftler]}


def test_halter_orta_mudur_perde_etiketi(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _halter())
    assert kod == 0, out
    assert sonuc["kopru_dugumler"] == [{"id": "M", "ad": "Mudur Kisi", "etiket": "perde"}]
    assert "perde/muvazaa sinyali" in out


def test_abc_zincirinde_b_isaretlenmez(tmp_path):
    """Doğrusal A-B-C: B articulation point AMA kalan bileşenler {A} ve {C}
    tek düğümlü → köprü DEĞİL (yaprak komşusu elenir)."""
    graf = {"dugumler": _olay("A", "B", "C"),
            "kenarlar": [_ils("A", "B"), _ils("B", "C")]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["kopru_dugumler"] == []
    assert "✓ Tek-nokta köprü yok." in out


def test_alacakli_gercek_kisi_iki_gercek_kisi_arasinda_yapisal(tmp_path):
    """Köprü gercek_kisi ama iki kanatta tuzel_kisi yok → nötr 'yapisal'
    (perde etiketi DEĞİL — sahte muvazaa sinyali üretilmez)."""
    graf = _halter(orta_tip="gercek_kisi", kanat_tip="gercek_kisi")
    for d in graf["dugumler"]:
        d.setdefault("usul_rolu", "alacakli")
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["kopru_dugumler"] == [{"id": "M", "ad": "Mudur Kisi", "etiket": "yapisal"}]
    assert "yapısal köprü (perde etiketi değil)" in out
    assert "perde/muvazaa sinyali" not in out


def test_tuzel_orta_dugum_yapisal(tmp_path):
    graf = _halter(orta_tip="tuzel_kisi")
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["kopru_dugumler"][0]["etiket"] == "yapisal"


def test_karar_ve_mahkeme_tipi_kopru_hesabindan_muaf(tmp_path):
    """A-2 grubu 'karar'/'mahkeme' tiplerini şemaya ekler; bugün KANONIK'te
    olmasa da kod tipe göre muaf tutar (mahkeme her tarafı bağlar — perde
    değil)."""
    graf = _halter(orta_tip="mahkeme")
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["kopru_dugumler"] == []
    graf = _halter(orta_tip="karar")
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["kopru_dugumler"] == []


def test_kopru_fonksiyonu_yildiz_grafta_merkez_isaretlenmez():
    """Yıldız: merkez çıkınca 4 tek-düğümlü bileşen → ≥2 düğümlü bileşen
    yok → köprü değil."""
    dugumler = {i: {"id": i, "tip": "olay"} for i in ("M", "A", "B", "C", "D")}
    kenarlar = [_ils("M", x) for x in ("A", "B", "C", "D")]
    assert gd.kopru_dugumler(dugumler, kenarlar) == []


# ═══════════════════════════════════════════════════════════════════════════
# G3 — dogrulama ZORUNLU (illiyet) + §3 desteksiz + norm advisory
# ═══════════════════════════════════════════════════════════════════════════

def test_illiyet_kenarinda_dogrulama_yoksa_sema_hatasi_exit3(tmp_path):
    graf = _temiz_graf()
    del graf["kenarlar"][0]["dogrulama"]
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert "✗ Kenar #0 (illiyet): 'dogrulama' eksik (zorunlu)" in out
    # §3 de yakalar: dogrulama yok
    assert any(k["index"] == 0 for k in sonuc["desteksiz_kenarlar"])


def test_iliski_kenarinda_dogrulama_yoksa_sema_hatasi_degil_ama_desteksiz(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"].append(_ils("A", "C"))
    del graf["kenarlar"][-1]["dogrulama"]
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, out
    assert sonuc["sema_hatalari"] == []
    assert [k["index"] for k in sonuc["desteksiz_kenarlar"]] == [2]
    assert "dogrulama beyan edilmemiş" in out


def test_iddia_ve_delilsiz_hala_desteksiz(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"][1].update({"dogrulama": "iddia", "dayanak_delil": []})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0
    assert [k["index"] for k in sonuc["desteksiz_kenarlar"]] == [1]


def test_norm_eksik_sema_uyarisi_advisory_exit0(tmp_path):
    graf = _temiz_graf()
    del graf["kenarlar"][0]["norm"]
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, "norm eksikliği advisory — saha grafları kırılmasın"
    assert sonuc["sema_hatalari"] == []
    assert "[ŞEMA UYARISI] Kenar #0: 'norm' eksik" in out


# ═══════════════════════════════════════════════════════════════════════════
# G4 — GÜÇ BEYANSIZ (ayrı sınıf) + varsayılan 0.4
# ═══════════════════════════════════════════════════════════════════════════

def test_guc_varsayilan_0_4():
    assert gd.GUC_VARSAYILAN == 0.4


def test_guc_beyansiz_kenarlar_ayri_sinif(tmp_path):
    graf = _temiz_graf()
    del graf["kenarlar"][1]["guc"]
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0
    assert [k["index"] for k in sonuc["guc_beyansiz_kenarlar"]] == [1]
    assert "GÜÇ BEYAN EDİLMEMİŞ (beyan-yok ≤ tartışmalı)" in out
    assert sonuc["zincirler"][0]["guven"] == round(0.9 * 0.4, 3)
    assert sonuc["zincirler"][0]["en_zayif"]["guc"] == "beyan-yok"
    assert sonuc["zincirler"][0]["en_zayif"]["agirlik"] == 0.4


def test_guc_beyansiz_yalniz_illiyet_kenarlarini_sayar(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"].append(_ils("A", "C"))  # iliski, guc yok — sayılmaz
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["guc_beyansiz_kenarlar"] == []


# ═══════════════════════════════════════════════════════════════════════════
# G2 — KÖKSÜZ İLLİYET GRAFI / ÇEVRİMDE YÜK TAŞIYAN KENAR
# ═══════════════════════════════════════════════════════════════════════════

def test_koksuz_illiyet_grafi_guvenilmez_damgasi(tmp_path):
    graf = {"dugumler": _olay("A", "B", "C"),
            "kenarlar": [_ill("A", "B"), _ill("B", "C"), _ill("C", "A")]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert "çevrim nedeniyle kök yok — zincir güven analizi GÜVENİLMEZ" in out
    assert "İlliyet zinciri bulunamadı" not in out
    assert sonuc["zincirler"] == []
    assert sonuc["zincir_uyarisi"]


def test_cevrim_varken_yuk_tasiyan_kenar_uyarisi(tmp_path):
    graf = {"dugumler": _olay("A", "B", "C", "D"),
            "kenarlar": [_ill("A", "B"), _ill("B", "C"), _ill("C", "B"),
                         _ill("C", "D")]}
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert "yük taşıyan kenar çevrimde anlamsız" in out


def test_cevrimsiz_grafta_g2_uyarilari_yok(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _temiz_graf())
    assert "GÜVENİLMEZ" not in out
    assert "çevrimde anlamsız" not in out
    assert sonuc["zincir_uyarisi"] is None


# ═══════════════════════════════════════════════════════════════════════════
# JSON SÖZLEŞMESİ (B grubu bekçisi) + BELGE
# ═══════════════════════════════════════════════════════════════════════════

JSON_ANAHTARLARI = {
    "arac", "ozet", "sema_hatalari", "yetim_dugumler", "desteksiz_kenarlar",
    "kopru_dugumler", "cevrimler", "kesme_adaylari", "yuk_tasiyan_kenarlar",
    "dugumler", "kenarlar", "girdi", "zincirler",
    # v0.5.16/A yeni alanlar
    "denetim_coktu", "cikis_kodu", "blok_sinifi", "baglanmamis_deliller",
    "guc_beyansiz_kenarlar", "zincir_uyarisi",
    # v0.5.16/A-2 (G9, G12): taraf/yön + kanun yolu zinciri
    "taraf", "yon", "kanun_yolu_zinciri",
}


def test_json_anahtar_seti_v0516(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _temiz_graf())
    assert set(sonuc) == JSON_ANAHTARLARI
    assert isinstance(sonuc["denetim_coktu"], bool)
    assert isinstance(sonuc["cikis_kodu"], int)
    for anahtar in ("baglanmamis_deliller", "guc_beyansiz_kenarlar",
                    "kopru_dugumler", "blok_sinifi"):
        assert isinstance(sonuc[anahtar], list)


def test_skill_md_json_zorunlu_ve_exit_tablosu():
    metin = SKILL_MD.read_text(encoding="utf-8")
    assert ("python scripts/grafik_denetim.py _oa/cikti/01-illiyet-graf.json "
            "--json _oa/cikti/01-illiyet-denetim.json") in metin
    assert "[--json" not in metin, "opsiyonel kapı = ateşlemeyen kapı"
    for parca in ("exit 2", "exit 3", "BAĞLANMAMIŞ DELİL", "guc_beyansiz_kenarlar",
                  "perde", "yapisal"):
        assert parca in metin, parca


def test_script_ag_importu_yok():
    kaynak = SCRIPT.read_text(encoding="utf-8")
    for yasak in ("import requests", "import urllib", "import socket", "import httpx"):
        assert yasak not in kaynak
    assert "__OA_UTF8_GUARD__" in kaynak


# ═══════════════════════════════════════════════════════════════════════════
# A-2 — ŞEMA GENİŞLETME + DAL + TARAF (G10, G9, G12, karar #11, doktrin kilidi)
# ═══════════════════════════════════════════════════════════════════════════

DOKTRIN_MD = SCRIPT.parents[1] / "references" / "illiyet-doktrini.md"
CIKTI_BLOGU_MD = SCRIPT.parents[1] / "references" / "cikti-blogu.md"

KESME_DAL_LISTESI = {
    "medeni:mucbir_sebep", "medeni:magdur_kusuru", "medeni:ucuncu_kisi_kusuru",
    "miras:paylastirma_kasti", "miras:ivaz",
    "ceza:izin_verilen_risk", "ceza:kendi_tehlikesine_girme",
    "ceza:hukuka_uygunluk", "ceza:magdur_kusuru",
}


# ── G10: kesme_flag dal-ayrımlı + göç ──────────────────────────────────────

def test_g10_kanonik_kesme_flag_dal_ayrimli():
    assert gd.KANONIK["kesme_flag"] == KESME_DAL_LISTESI


def test_g10_eski_ciplak_deger_sema_uyarisi_goc_onerisi_exit_degismez(tmp_path):
    """Eski çıplak 'magdur_kusuru' kanonik-dışı [ŞEMA UYARISI] + '--goc ile dal
    etiketle' önerisi; exit kodu DEĞİŞMEZ (geriye uyum — saha grafları kırılmaz)."""
    graf = _temiz_graf()
    graf["kenarlar"][0]["kesme_flag"] = "magdur_kusuru"
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, out
    assert "[ŞEMA UYARISI]" in out
    assert "kanonik-dışı kesme_flag: 'magdur_kusuru'" in out
    assert "--goc" in out and "dal etiketle" in out
    # kesme adayı yine raporlanır (eski değer yok sayılmaz)
    assert "KESME: magdur_kusuru" in out
    assert len(sonuc["kesme_adaylari"]) == 1


def test_g10_ceza_magdur_kusuru_sabit_not(tmp_path):
    """ceza:magdur_kusuru için §6'da SABİT doktrin hatırlatması: illiyeti
    KESMEZ, kusur derecesine/ceza miktarına etki eder. Bu hukuki HÜKÜM değil
    doktrin hatırlatmasıdır; künye kütükten (hafızadan yazılmaz)."""
    graf = _temiz_graf()
    graf["kenarlar"][0].update({"kesme_flag": "ceza:magdur_kusuru",
                                "illiyet_tipi": "objektif_isnadiyet"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, out
    assert "KESME: ceza:magdur_kusuru" in out
    assert "illiyeti KESMEZ" in out
    assert "kusur derecesine/ceza miktarına etki eder" in out
    assert "künye KÜTÜKTEN" in out
    aday = sonuc["kesme_adaylari"][0]
    assert aday["kesme_flag"] == "ceza:magdur_kusuru"
    assert aday["dal"] == "ceza"
    assert "illiyeti KESMEZ" in aday["not"]


def test_g10_miras_paylastirma_kasti_notu(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"][0]["kesme_flag"] = "miras:paylastirma_kasti"
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert "muris muvazaasında bozma gerekçesi" in out
    assert "ispat ölçütü" in out
    assert sonuc["kesme_adaylari"][0]["dal"] == "miras"


def test_g10_medeni_flag_notsuz_ve_uyarisiz(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"][0]["kesme_flag"] = "medeni:mucbir_sebep"
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0
    assert "kanonik-dışı kesme_flag" not in out
    assert sonuc["kesme_adaylari"][0]["not"] is None
    assert sonuc["kesme_adaylari"][0]["dal"] == "medeni"


def test_g10_goc_kaynaga_dokunmaz_degisen_sayisini_basar(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"][0]["kesme_flag"] = "magdur_kusuru"        # göç eder
    graf["kenarlar"][1]["kesme_flag"] = "ceza:hukuka_uygunluk"  # zaten dal önekli — dokunulmaz
    graf["kenarlar"].append(_ils("A", "C", kesme_flag="mucbir_sebep"))  # iliski kenarı da göçer
    eski = _graf_yaz(tmp_path, graf, "eski.json")
    eski_metin = eski.read_text(encoding="utf-8")
    yeni = tmp_path / "yeni.json"
    kod, out, err = _cli("--goc", eski, "--dal", "medeni", "--cikti", yeni)
    assert kod == 0, f"{out}\n{err}"
    assert eski.read_text(encoding="utf-8") == eski_metin, "kaynağa dokunulmaz"
    g2 = json.loads(yeni.read_text(encoding="utf-8"))
    assert g2["kenarlar"][0]["kesme_flag"] == "medeni:magdur_kusuru"
    assert g2["kenarlar"][1]["kesme_flag"] == "ceza:hukuka_uygunluk"
    assert g2["kenarlar"][2]["kesme_flag"] == "medeni:mucbir_sebep"
    assert "değişen kenar: 2" in out
    # göçmüş graf artık uyarısız
    kod2, out2, err2 = _cli(yeni)
    assert "kanonik-dışı kesme_flag" not in out2


def test_g10_goc_dal_disi_deger_gocmez_ve_gorunur(tmp_path):
    """'ivaz' ceza dalında yok → 'ceza:ivaz' kanonik olmaz; göç ETMEZ, uyarı basar
    (sahte kanoniklik üretilmez)."""
    graf = _temiz_graf()
    graf["kenarlar"][0]["kesme_flag"] = "ivaz"
    eski = _graf_yaz(tmp_path, graf, "eski.json")
    yeni = tmp_path / "yeni.json"
    kod, out, err = _cli("--goc", eski, "--dal", "ceza", "--cikti", yeni)
    assert kod == 0, out
    assert "değişen kenar: 0" in out
    assert "elle düzelt" in out and "'ivaz'" in out
    g2 = json.loads(yeni.read_text(encoding="utf-8"))
    assert g2["kenarlar"][0]["kesme_flag"] == "ivaz"


def test_g10_goc_eksik_arguman_exit1_ve_dosya_yok_exit2(tmp_path):
    kod, out, err = _cli("--goc", tmp_path / "x.json")     # --dal / --cikti yok
    assert kod == 1
    yeni = tmp_path / "yeni.json"
    kod, out, err = _cli("--goc", tmp_path / "yok.json", "--dal", "ceza", "--cikti", yeni)
    assert kod == 2
    assert "GÖÇ ÇÖKTÜ" in out
    assert not yeni.exists()


def test_g10_goc_fonksiyonu_python_api(tmp_path):
    graf = _temiz_graf()
    graf["kenarlar"][0]["kesme_flag"] = "paylastirma_kasti"
    eski = _graf_yaz(tmp_path, graf, "eski.json")
    yeni = tmp_path / "yeni.json"
    ozet = gd.goc(str(eski), "miras", str(yeni))
    assert ozet["degisen"] == 1 and ozet["atlanan"] == []
    assert json.loads(yeni.read_text(encoding="utf-8"))["kenarlar"][0]["kesme_flag"] \
        == "miras:paylastirma_kasti"


# ── G9: taraf → yön (kur | çürüt) ──────────────────────────────────────────

def _yuk_graf():
    """A→B→C→D: B→C yük taşıyan kenar; A→B kesme adayı."""
    graf = {"dugumler": _olay("A", "B", "C", "D") + [
                {"id": "D1", "tip": "delil", "ad": "Bilirkisi Raporu"}],
            "kenarlar": [_ill("A", "B", kesme_flag="medeni:ucuncu_kisi_kusuru"),
                         _ill("B", "C"), _ill("C", "D", guc="zayif")]}
    return graf


@pytest.mark.parametrize("taraf", ["sanik", "mudafii", "davali", "borclu"])
def test_g9_savunma_kanadi_yon_curut(tmp_path, taraf):
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--taraf", taraf)
    assert kod == 0, out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["taraf"] == taraf and sonuc["yon"] == "curut"
    assert "karşı tarafın bu bağını ÇÜRÜT" in out            # §7
    assert "kesme savunmasını KUR" in out                     # §6
    assert "bu bağı sağlamlaştır" not in out
    assert "önce burayı sağlamlaştır" not in out
    assert "taraf bilinmiyor" not in out


@pytest.mark.parametrize("taraf", ["katilan", "musteki", "davaci", "alacakli"])
def test_g9_iddia_kanadi_yon_kur(tmp_path, taraf):
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--taraf", taraf)
    assert kod == 0, out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["taraf"] == taraf and sonuc["yon"] == "kur"
    assert "stratejik öncelik: bu bağı sağlamlaştır" in out
    assert "oa-antitez ile çürüt veya kabul et" in out
    assert "ÇÜRÜT" not in out


def test_g9_taraf_yoksa_mevcut_metin_ve_not(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _yuk_graf())
    assert sonuc["taraf"] is None and sonuc["yon"] is None
    assert "taraf bilinmiyor — --taraf ver" in out
    assert "stratejik öncelik: bu bağı sağlamlaştır" in out


def _defter_yaz(kok, ceza_dali):
    defter = kok / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "pipeline-durum.json").write_text(
        json.dumps({"dosya": "E. 2099/1 sentetik", "ceza_dali": ceza_dali,
                    "adimlar": {}, "katmanlar": {}}), encoding="utf-8")
    return defter


def test_g9_kok_defterden_mudafii_sanik_tarafi(tmp_path):
    _defter_yaz(tmp_path, "mudafii")
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--kok", tmp_path)
    assert kod == 0, out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["taraf"] == "sanik" and sonuc["yon"] == "curut"
    assert "defter" in out.lower()


def test_g9_kok_defterden_musteki(tmp_path):
    _defter_yaz(tmp_path, "musteki")
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--kok", tmp_path)
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["taraf"] == "musteki" and sonuc["yon"] == "kur"


def test_g9_kok_defter_yok_veya_dal_bos_taraf_bilinmiyor(tmp_path):
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--kok", tmp_path)
    assert kod == 0, out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["taraf"] is None and sonuc["yon"] is None
    assert "taraf bilinmiyor — --taraf ver" in out
    _defter_yaz(tmp_path, None)                       # hukuk dosyası: ceza_dali null
    kod, out, err = _cli(yol, "--json", json_yol, "--kok", tmp_path)
    assert kod == 0
    assert json.loads(json_yol.read_text(encoding="utf-8"))["taraf"] is None
    assert "taraf bilinmiyor — --taraf ver" in out


def test_g9_bozuk_defter_cokertmez_fail_closed(tmp_path):
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "pipeline-durum.json").write_text("{ bozuk", encoding="utf-8")
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--kok", tmp_path)
    assert kod == 0, out
    assert "taraf bilinmiyor" in out and "okunamadı" in out


def test_g9_taraf_cli_defteri_ezer(tmp_path):
    _defter_yaz(tmp_path, "mudafii")
    yol = _graf_yaz(tmp_path, _yuk_graf())
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol, "--kok", tmp_path, "--taraf", "katilan")
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["taraf"] == "katilan" and sonuc["yon"] == "kur"


def test_g9_taraf_yonu_fonksiyonu():
    assert gd.taraf_yonu("sanik") == "curut"
    assert gd.taraf_yonu("alacakli") == "kur"
    assert gd.taraf_yonu(None) is None
    assert gd.taraf_yonu("bilinmeyen") is None


# ── G12: karar / mahkeme tipi + kanun_yolu kenarı + §9 ─────────────────────

def _kanun_yolu_graf():
    dugumler = _olay("A", "B") + [
        {"id": "D1", "tip": "delil", "ad": "Bilirkisi Raporu"},
        {"id": "K1", "tip": "karar", "ad": "Ilk Derece Karari"},
        {"id": "K2", "tip": "karar", "ad": "BAM Karari"},
        {"id": "K3", "tip": "karar", "ad": "Yargitay Karari"},
    ]
    kenarlar = [
        _ill("A", "B"),
        _ils("B", "K1", tur="islem_sonuc"),
        {"kaynak": "K1", "hedef": "K2", "kategori": "iliski", "tur": "kanun_yolu",
         "sonuc": "esastan_ret", "dogrulama": "teyitli", "dayanak_delil": ["D1"],
         "norm": "çıpa"},
        {"kaynak": "K2", "hedef": "K3", "kategori": "iliski", "tur": "kanun_yolu",
         "sonuc": "bozdu", "dogrulama": "teyitli", "dayanak_delil": ["D1"],
         "norm": "çıpa"},
    ]
    return {"dugumler": dugumler, "kenarlar": kenarlar}


def test_g12_kanonik_tip_ve_sonuc():
    assert {"karar", "mahkeme"} <= gd.KANONIK["tip"]
    assert gd.KANONIK["sonuc"] == {"onadi", "bozdu", "kaldirdi", "geri_cevirdi",
                                   "esastan_ret", "kesin"}
    assert "sonuc" in gd.KENAR_ALANLARI


def test_g12_karar_tipi_artik_sema_uyarisi_degil_ve_kopru_muaf(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _kanun_yolu_graf())
    assert kod == 0, out
    assert "kanonik-dışı tip" not in out
    assert "bilinmeyen alan: 'sonuc'" not in out
    # A-1 doğrulaması: karar/mahkeme köprüden muaf (kod tipe göre)
    graf = _halter(orta_tip="karar")
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["kopru_dugumler"] == [] and "kanonik-dışı tip: 'karar'" not in out


def test_g12_kanun_yolu_zinciri_bolum9_ve_json(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _kanun_yolu_graf())
    assert kod == 0, out
    assert "### 9. KANUN YOLU ZİNCİRİ" in out
    assert "Ilk Derece Karari → BAM Karari → Yargitay Karari" in out
    assert "esastan_ret" in out and "bozdu" in out
    assert sonuc["kanun_yolu_zinciri"] == [
        {"yol": ["K1", "K2", "K3"], "sonuclar": ["esastan_ret", "bozdu"]}]


def test_g12_kanun_yolu_illiyet_zincirine_cevrime_yuke_girmez(tmp_path):
    """kanun_yolu kenarları kategori 'illiyet' yazılsa bile çevrim/yük/zincir
    hesabına GİRMEZ (yargı kademesi neden-sonuç değildir)."""
    graf = _kanun_yolu_graf()
    for k in graf["kenarlar"]:
        if k["tur"] == "kanun_yolu":
            k["kategori"] = "illiyet"
    # K3 → K1 kanun_yolu geri kenarı: illiyet sayılsaydı çevrim olurdu
    graf["kenarlar"].append({"kaynak": "K3", "hedef": "K1", "kategori": "illiyet",
                             "tur": "kanun_yolu", "sonuc": "kesin",
                             "dogrulama": "teyitli", "dayanak_delil": ["D1"],
                             "norm": "çıpa"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert sonuc["cevrimler"] == []
    assert kod == 0, out
    assert all("K" not in z["yol"][0] for z in sonuc["zincirler"])
    assert all(k["tur"] != "kanun_yolu" for k in sonuc["yuk_tasiyan_kenarlar"])
    assert "[ŞEMA UYARISI]" in out and "kanun_yolu" in out  # illiyet kategorisi uyarılır


def test_g12_kanun_yolu_karar_disi_dugumde_sema_uyarisi(tmp_path):
    graf = _kanun_yolu_graf()
    graf["kenarlar"].append({"kaynak": "A", "hedef": "K1", "kategori": "iliski",
                             "tur": "kanun_yolu", "sonuc": "onadi",
                             "dogrulama": "teyitli", "dayanak_delil": ["D1"],
                             "norm": "çıpa"})
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0, "uç tipi uyarıdır, hata değil"
    assert "[ŞEMA UYARISI] Kenar #4" in out and "karar | mahkeme" in out


def test_g12_kanun_yolu_sonuc_zorunlu_exit3(tmp_path):
    graf = _kanun_yolu_graf()
    del graf["kenarlar"][2]["sonuc"]
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 3
    assert "✗ Kenar #2 (kanun_yolu): 'sonuc' eksik (zorunlu)" in out


def test_g12_kanonik_disi_sonuc_uyarilir(tmp_path):
    graf = _kanun_yolu_graf()
    graf["kenarlar"][2]["sonuc"] = "onandi"
    kod, out, err, sonuc = _kos_json(tmp_path, graf)
    assert kod == 0
    assert "kanonik-dışı sonuc: 'onandi'" in out and "'onadi'" in out


def test_g12_kanun_yolu_yoksa_bolum9_bos(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _temiz_graf())
    assert "### 9. KANUN YOLU ZİNCİRİ" in out
    assert sonuc["kanun_yolu_zinciri"] == []


def test_g12_kanun_yolu_cevrimi_cokertmez_uyarir():
    dugumler = {"K1": {"id": "K1", "tip": "karar"}, "K2": {"id": "K2", "tip": "karar"}}
    kenarlar = [{"kaynak": "K1", "hedef": "K2", "kategori": "iliski", "tur": "kanun_yolu",
                 "sonuc": "bozdu"},
                {"kaynak": "K2", "hedef": "K1", "kategori": "iliski", "tur": "kanun_yolu",
                 "sonuc": "kesin"}]
    zincir = gd.kanun_yolu_zinciri(dugumler, kenarlar)
    assert zincir and all(len(z["yol"]) <= 3 for z in zincir)


# ── Karar #11 + doktrin kilidi + belge ─────────────────────────────────────

def test_kanonik_her_deger_doktrinde_literal_gecer():
    """DOKTRİN ↔ KOD KİLİDİ: KANONIK sözlüğündeki HER string değer
    references/illiyet-doktrini.md'de literal geçmeli (G grubu aile_dogrula'ya
    aynı kilidi mekanik olarak ekliyor)."""
    metin = DOKTRIN_MD.read_text(encoding="utf-8")
    eksik = [f"{alan}:{deger}" for alan, kume in gd.KANONIK.items()
             for deger in sorted(kume) if deger not in metin]
    assert not eksik, eksik
    for alan in gd.KANONIK:
        assert f"`{alan}`" in metin, alan


def test_karar11_ticaret_modelleme_sablonu_belgelerde():
    for yol in (DOKTRIN_MD, CIKTI_BLOGU_MD):
        metin = yol.read_text(encoding="utf-8")
        assert "organik bağ" in metin and "perde" in metin, yol.name
        assert "AYRI" in metin and "hak" in metin, yol.name
        assert "alternatif değil, birlikte" in metin, yol.name
        assert "kütükten teyitli karar ile" in metin, yol.name


def test_skill_md_a2_belgesi():
    metin = SKILL_MD.read_text(encoding="utf-8")
    for parca in ("--taraf", "--goc", "--kok", "ceza:magdur_kusuru",
                  "miras:paylastirma_kasti", "kanun_yolu", "kanun_yolu_zinciri",
                  "karar", "mahkeme", "doktrin hatırlatması"):
        assert parca in metin, parca


def test_json_anahtar_seti_a2(tmp_path):
    kod, out, err, sonuc = _kos_json(tmp_path, _temiz_graf())
    assert {"taraf", "yon", "kanun_yolu_zinciri"} <= JSON_ANAHTARLARI
    assert set(sonuc) == JSON_ANAHTARLARI
    assert sonuc["taraf"] is None and sonuc["yon"] is None
    assert sonuc["kanun_yolu_zinciri"] == []
