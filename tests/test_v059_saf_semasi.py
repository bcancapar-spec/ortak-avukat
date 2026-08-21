# -*- coding: utf-8 -*-
"""v0.5.9 T23/P1 — SAHTE-YEŞİL kapanışı: grafik_denetim.py sözlük denetimi.

Kapatılan açık: bilinçli-yanlış alanlı graf (kenar alanı `delil` vs beklenen
`dayanak_delil`; kategori `fiil-netice` vs kanonik `illiyet`) bugüne dek
"Şema bütün ✓" + 8 katman yeşil + analizler SESSİZCE BOŞ üretiyordu
(unknown-field tolerance + enum non-enforcement + silent no-op).

Yeni sözleşme (ADVISORY — bloklamaz):
* Bilinmeyen alan adı / kanonik-dışı enum değeri → çıktı başında görünür
  [ŞEMA UYARISI] satırları (yakın-eşleşme önerili).
* Bir analiz katmanını boş bırakacak yapısal boşluk (0 kenar; kenar var ama
  0 illiyet kenarı) → açıklanabilir-boşluk uyarısı; sessiz kalmak YASAK.
* Exit kodu DEĞİŞMEZ; mevcut stdout/JSON çıktıları birebir korunur
  (yalnız ek uyarı satırları); JSON anahtar seti SABİT kalır.
* Gürültü disiplini: kanonik-temiz graf SIFIR yeni satır üretir.

Yerli not: bu ağacın fikstürlerinde `dogrulama: "delil"` yerleşiktir
(karakterizasyon kilidi) → kabul kümesindedir, uyarı ÜRETMEZ.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-illiyet"
          / "scripts" / "grafik_denetim.py")

UYARI = "[ŞEMA UYARISI]"


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


def _graf_yaz(kok, graf):
    yol = kok / "graf.json"
    yol.write_text(json.dumps(graf, ensure_ascii=False), encoding="utf-8")
    return yol


def _kanonik_temiz_graf():
    """Sözlüğe birebir uyan graf — sıfır uyarı beklenir."""
    return {
        "dugumler": [
            {"id": "SORUMLU", "tip": "gercek_kisi", "ad": "Sorumlu Kisi",
             "usul_rolu": "davali"},
            {"id": "FIIL", "tip": "olay", "ad": "Zarar Verici Fiil"},
            {"id": "ZARAR", "tip": "olay", "ad": "Netice Zarari"},
        ],
        "kenarlar": [
            {"kaynak": "SORUMLU", "hedef": "FIIL", "kategori": "iliski",
             "tur": "faili", "dogrulama": "delil",
             "dayanak_delil": ["tutanak"]},
            {"kaynak": "FIIL", "hedef": "ZARAR", "kategori": "illiyet",
             "tur": "fiil_netice", "illiyet_tipi": "dogal", "guc": "guclu",
             "dogrulama": "teyitli", "dayanak_delil": ["bilirkisi raporu"]},
            {"kaynak": "SORUMLU", "hedef": "ZARAR", "kategori": "iliski",
             "tur": "sorumlu", "dogrulama": "karine", "dayanak_delil": []},
        ],
    }


# ── NEGATİF 1: denetim raporundaki birebir senaryo — yanlış alan adı +
#    kanonik-dışı kategori → uyarı + açıklanabilir boşluk + sahte-yeşil teşhiri ──

def test_yanlis_alan_ve_kanonik_disi_kategori_uyarilir_exit0(tmp_path):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
        ],
        "kenarlar": [
            # `delil` (bilinmeyen alan) vs beklenen `dayanak_delil`;
            # kategori `fiil-netice` vs kanonik `illiyet`
            {"kaynak": "A", "hedef": "B", "kategori": "fiil-netice",
             "tur": "sebep", "delil": ["tutanak"]},
        ],
    }
    kod, out, err = _cli(_graf_yaz(tmp_path, graf))

    assert kod == 0, f"advisory bloklamaz — exit 0 beklenir; stderr:\n{err}"
    # bilinmeyen alan + yakın-eşleşme önerisi
    assert "bilinmeyen alan: 'delil'" in out
    assert "dayanak_delil" in out
    # kanonik-dışı enum değeri + kanonik küme
    assert "kanonik-dışı kategori: 'fiil-netice'" in out
    assert "iliski | illiyet" in out
    # açıklanabilir boşluk: 0 illiyet kenarı sessiz geçilmez
    assert "0 'illiyet' kategorili kenar" in out
    # uyarılar görünür damgayla ve rapor başında (bölüm 1'den önce) gelir
    assert UYARI in out
    assert out.index(UYARI) < out.index("### 1. ŞEMA DENETİMİ")


# ── NEGATİF 2: kanonik-dışı enum değerleri (guc / illiyet_tipi / kesme_flag) ──

def test_kanonik_disi_enum_degerleri_tek_tek_uyarilir(tmp_path):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "kurum", "ad": "Tip Bozuk"},  # kanonik-dışı tip
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "illiyet",
             "tur": "sebep", "illiyet_tipi": "fiili",        # kanonik-dışı
             "guc": "cok guclu",                              # kanonik-dışı
             "kesme_flag": "mucbir sebep",                    # kanonik-dışı (alt çizgisiz)
             "dogrulama": "delil", "dayanak_delil": ["x"]},
        ],
    }
    kod, out, err = _cli(_graf_yaz(tmp_path, graf))

    assert kod == 0
    assert "kanonik-dışı tip: 'kurum'" in out
    assert "kanonik-dışı illiyet_tipi: 'fiili'" in out
    assert "kanonik-dışı guc: 'cok guclu'" in out
    assert "kanonik-dışı kesme_flag: 'mucbir sebep'" in out
    assert "'mucbir_sebep'" in out  # yakın-eşleşme önerisi


# ── NEGATİF 3: düğümde bilinmeyen alan adı ──────────────────────────────────

def test_dugumde_bilinmeyen_alan_uyarilir(tmp_path):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A",
             "usul_rol": "davaci"},                           # beklenen: usul_rolu
            {"id": "B", "tip": "olay", "ad": "Olay B"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "illiyet",
             "tur": "fiil_netice", "illiyet_tipi": "dogal",
             "dogrulama": "teyitli", "dayanak_delil": ["x"]},
        ],
    }
    kod, out, err = _cli(_graf_yaz(tmp_path, graf))

    assert kod == 0
    assert "bilinmeyen alan: 'usul_rol'" in out
    assert "usul_rolu" in out  # yakın-eşleşme önerisi


# ── NEGATİF 4: boş graf → açıklanabilir boşluk (sessizlik yasak) ────────────

def test_bos_graf_aciklanabilir_bosluk_uyarisi(tmp_path):
    kod, out, err = _cli(_graf_yaz(tmp_path, {}))
    assert kod == 0
    assert UYARI in out
    assert "0 düğüm" in out and "0 kenar" in out
    # mevcut karakterizasyon çıktısı korunur
    assert "✓ Şema bütün." in out


# ── NEGATİF 5: yalnız iliski kenarlı graf → 0-illiyet boşluğu açıklanır ─────

def test_yalniz_iliski_kenarli_graf_illiyet_boslugu_aciklanir(tmp_path):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "iliski", "tur": "bag",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
        ],
    }
    kod, out, err = _cli(_graf_yaz(tmp_path, graf))
    assert kod == 0
    assert "0 'illiyet' kategorili kenar" in out
    assert "iliski | illiyet" in out


# ── GÜRÜLTÜ DİSİPLİNİ: kanonik-temiz graf SIFIR yeni satır ──────────────────

def test_dogru_graf_sifir_uyari_satiri(tmp_path):
    kod, out, err = _cli(_graf_yaz(tmp_path, _kanonik_temiz_graf()))
    assert kod == 0, f"stderr:\n{err}"
    assert UYARI not in out
    assert "bilinmeyen alan" not in out
    assert "kanonik-dışı" not in out


def test_yerlesik_dogrulama_delil_degeri_uyari_uretmez(tmp_path):
    """Bu ağacın fikstür gerçeği: dogrulama='delil' yerleşiktir; sözlük
    denetimi onu kabul kümesinde tutar (gürültü disiplini)."""
    graf = _kanonik_temiz_graf()
    for k in graf["kenarlar"]:
        k["dogrulama"] = "delil"
    kod, out, err = _cli(_graf_yaz(tmp_path, graf))
    assert kod == 0
    assert UYARI not in out


# ── SÖZLEŞME KORUMASI: JSON anahtar seti ve exit yolu değişmez ──────────────

def test_uyarili_grafta_json_anahtar_seti_sabit_kalir(tmp_path):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "fiil-netice",
             "tur": "sebep", "delil": ["x"]},
        ],
    }
    json_yol = tmp_path / "sonuc.json"
    kod, out, err = _cli(_graf_yaz(tmp_path, graf), "--json", json_yol)

    assert kod == 0
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    # test_grafik_denetim.py ile aynı kilit: uyarılar JSON'a anahtar EKLEMEZ
    assert set(sonuc) == {
        "arac", "ozet", "sema_hatalari", "yetim_dugumler", "desteksiz_kenarlar",
        "kopru_dugumler", "cevrimler", "kesme_adaylari", "yuk_tasiyan_kenarlar",
        "dugumler", "kenarlar", "girdi", "zincirler",
    }
