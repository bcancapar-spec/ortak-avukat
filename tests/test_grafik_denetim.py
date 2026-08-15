# -*- coding: utf-8 -*-
"""Fable-tespitli TESTSİZ release-kapısı scriptlerinden biri olan
oa-illiyet / grafik_denetim.py için KARAKTERİZASYON testleri.

Bu testler scriptin MEVCUT davranışını olduğu gibi KİLİTLER; davranışı
değiştirmez, "doğru" davranışı dayatmaz. Koddan çıkarılan ve burada
kilitlenen dikkat çekici mevcut-tasarım kararları:

* `rapor()` hiçbir koşulda `sys.exit` çağırmaz → şema hatası, yetim düğüm,
  çevrim vb. BULGULAR OLSA DA exit kodu 0'dır (karakterizasyon — mevcut
  tasarım). Exit 1 yalnızca iki yoldan gelir: argümansız çağrı (usage
  mesajı + sys.exit(1)) veya yakalanmayan istisna (dosya yok / bozuk JSON
  → traceback).
* Çevrim denetimi yalnızca kategori="illiyet" kenarlarına bakar; "iliski"
  kenarlarının oluşturduğu yönlü çevrim raporlanmaz.
* Kesme adayı denetimi de yalnızca kategori="illiyet" kenarlarındaki
  kesme_flag'i görür; "iliski" kenarındaki kesme_flag sessizce yok sayılır.
* Yük taşıyan kenar (bridge) tespitinde bileşen sayısı, KALAN kenar
  kümesinden türetilen düğümler üzerinden sayılır: zincirin UÇ kenarı
  çıkarılınca sarkaç düğüm de kümeden düştüğü için bileşen sayısı artmaz →
  doğrusal zincirde yalnız İÇ kenarlar bridge sayılır; 2 kenarlı zincirde
  HİÇBİR kenar bridge çıkmaz (karakterizasyon — mevcut tasarım).
* --json çıktısındaki kenar referansı (_kenar_ref) kesme_flag ve
  illiyet_tipi alanlarını TAŞIMAZ; kesme_flag değeri yalnız stdout'ta
  görünür (karakterizasyon — mevcut tasarım).

Girdiler tempfile tabanlı izole dizinlerde üretilir; repo dosyalarına
dokunulmaz.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-illiyet"
          / "scripts" / "grafik_denetim.py")

# v0.5.8.4: zincir analizi VARSAYILAN çalıştığından "zincirler" anahtarı da
# bayraksız --json çıktısının parçasıdır (bilinçli sözleşme değişikliği —
# 372 sahasında --zincir 0 kez verildi, analiz hiç üretilmedi; --zincirsiz
# verilirse anahtar düşer, bkz. test_zincir_analizi.py).
JSON_ANAHTARLARI = {
    "arac", "ozet", "sema_hatalari", "yetim_dugumler", "desteksiz_kenarlar",
    "kopru_dugumler", "cevrimler", "kesme_adaylari", "yuk_tasiyan_kenarlar",
    "dugumler", "kenarlar", "girdi", "zincirler",
}
KENAR_REF_ANAHTARLARI = {
    "index", "kaynak", "hedef", "kategori", "tur", "dayanak_delil", "dogrulama",
}


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


@pytest.fixture
def izole_kok():
    return pathlib.Path(tempfile.mkdtemp())


def _graf_yaz(kok, graf, ad="graf.json"):
    yol = kok / ad
    yol.write_text(json.dumps(graf, ensure_ascii=False), encoding="utf-8")
    return yol


def _temiz_graf():
    """Yedi denetimin hiçbirine takılmayan örnek graf (üçgen → köprü yok)."""
    return {
        "dugumler": [
            {"id": "DAVALI", "tip": "gercek_kisi", "ad": "Davali Kisi",
             "usul_rolu": "davali"},
            {"id": "FIIL", "tip": "olay", "ad": "Trafik Kazasi"},
            {"id": "ZARAR", "tip": "olay", "ad": "Bedensel Zarar"},
        ],
        "kenarlar": [
            {"kaynak": "DAVALI", "hedef": "FIIL", "kategori": "iliski",
             "tur": "faili", "dogrulama": "delil",
             "dayanak_delil": ["kaza tutanagi"]},
            {"kaynak": "FIIL", "hedef": "ZARAR", "kategori": "illiyet",
             "tur": "sebep", "illiyet_tipi": "dogal", "dogrulama": "delil",
             "dayanak_delil": ["bilirkisi raporu"]},
            {"kaynak": "DAVALI", "hedef": "ZARAR", "kategori": "iliski",
             "tur": "sorumlu", "dogrulama": "delil",
             "dayanak_delil": ["kusur raporu"]},
        ],
    }


def test_script_mevcut():
    assert SCRIPT.is_file(), f"grafik_denetim.py bulunamadı: {SCRIPT}"


# ── mutlu yol: temiz graf → yedi denetim de temiz, exit 0 ───────────────────

def test_temiz_graf_yedi_denetim_de_temiz_exit0(izole_kok):
    yol = _graf_yaz(izole_kok, _temiz_graf())
    kod, out, err = _cli(yol)

    assert kod == 0, f"stderr:\n{err}"
    assert "OA-ILLIYET — DETERMİNİSTİK GRAF DENETİM RAPORU" in out
    assert "Düğüm: 3  |  Kenar: 3" in out
    assert "✓ Şema bütün." in out
    assert "✓ Yetim düğüm yok." in out
    assert "✓ Her kenar delil-teyitli veya karine." in out
    assert "✓ Tek-nokta köprü yok." in out
    assert "✓ İlliyet zinciri dairesel değil." in out
    assert "Kesme adayı işaretlenmemiş" in out
    assert "Belirgin tek yük taşıyan kenar yok" in out
    assert "nihai karar avukata aittir" in out


# ── 1. şema denetimi: dört tespit sınıfı + bulgulara rağmen exit 0 ──────────

def test_sema_hatalari_tek_tek_raporlanir_ama_exit_yine_sifir(izole_kok):
    """rapor() sys.exit çağırmadığı için şema hatalarında da exit 0
    (karakterizasyon — mevcut tasarım)."""
    graf = {
        "dugumler": [
            {"id": "N1", "ad": "Tipsiz Dugum"},                       # tip eksik
            {"id": "N2", "tip": "gercek_kisi", "ad": "Rolsuz Kisi"},  # usul_rolu eksik
        ],
        "kenarlar": [
            {"kaynak": "N1", "hedef": "HAYALET", "kategori": "iliski",
             "tur": "bag"},                                            # tanımsız hedef
            {"kaynak": "N1", "hedef": "N2", "kategori": "illiyet",
             "tur": "sebep"},                                          # illiyet_tipi eksik
            {"kaynak": "N1", "hedef": "N2", "kategori": "iliski"},     # tur eksik
        ],
    }
    yol = _graf_yaz(izole_kok, graf)
    kod, out, err = _cli(yol)

    assert kod == 0, f"bulgu olsa da mevcut tasarımda exit 0 beklenir; stderr:\n{err}"
    assert "✗ Düğüm 'N1': 'tip' eksik" in out
    assert "✗ Düğüm 'N2' (gerçek kişi): 'usul_rolu' eksik (zorunlu)" in out
    assert "✗ Kenar #0: hedef 'HAYALET' tanımsız düğüm" in out
    assert "✗ Kenar #1 (illiyet): 'illiyet_tipi' eksik" in out
    assert "✗ Kenar #2: 'tur' eksik" in out
    assert "Şema hataları var — diğer denetimler eksik çalışabilir." in out


# ── 2. yetim düğüm ──────────────────────────────────────────────────────────

def test_yetim_dugum_ad_ve_id_ile_raporlanir_exit0(izole_kok):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
            {"id": "YETIM", "tip": "belge", "ad": "Bagsiz Belge"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "iliski", "tur": "bag",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
        ],
    }
    yol = _graf_yaz(izole_kok, graf)
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "⚠ Bagsiz Belge (YETIM) — dosyada neden var? bağ kur veya çıkar" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["yetim_dugumler"] == [{"id": "YETIM", "ad": "Bagsiz Belge"}]


# ── 3. desteksiz kenar (dogrulama=iddia + dayanak_delil boş) ────────────────

def test_desteksiz_kenar_yalniz_iddia_ve_delilsiz_olani_yakalar(izole_kok):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
            {"id": "C", "tip": "olay", "ad": "Olay C"},
        ],
        "kenarlar": [
            # tespit: iddia + boş dayanak_delil
            {"kaynak": "A", "hedef": "B", "kategori": "iliski",
             "tur": "iddia bagi", "dogrulama": "iddia", "dayanak_delil": []},
            # tespit DEĞİL: iddia ama delilli
            {"kaynak": "B", "hedef": "C", "kategori": "iliski",
             "tur": "delilli bag", "dogrulama": "iddia",
             "dayanak_delil": ["senet"]},
            # tespit DEĞİL: dogrulama=karine, delilsiz
            {"kaynak": "A", "hedef": "C", "kategori": "iliski",
             "tur": "karine bagi", "dogrulama": "karine"},
        ],
    }
    yol = _graf_yaz(izole_kok, graf)
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "oa-vakia ile delil tespiti" in out
    assert "⚠ Olay A —[iddia bagi]→ Olay B" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert len(sonuc["desteksiz_kenarlar"]) == 1
    tek = sonuc["desteksiz_kenarlar"][0]
    assert tek["index"] == 0
    assert tek["dayanak_delil"] == []
    assert tek["dogrulama"] == "iddia"


# ── 4. köprü düğüm (halter şekli: iki üçgeni bağlayan tek orta düğüm) ───────

def test_kopru_dugum_halter_grafinda_yalniz_orta_dugum(izole_kok):
    """5 düğümlü halter: {A,B,C} üçgeni + {C,D,E} üçgeni, C ortak.
    C çıkınca iki küme kopar → yalnız C articulation point."""
    dugumler = [{"id": i, "tip": "olay", "ad": f"Dugum {i}"}
                for i in ("A", "B", "C", "D", "E")]
    ciftler = [("A", "B"), ("A", "C"), ("B", "C"),
               ("C", "D"), ("C", "E"), ("D", "E")]
    kenarlar = [{"kaynak": a, "hedef": b, "kategori": "iliski", "tur": "bag",
                 "dogrulama": "delil", "dayanak_delil": ["x"]}
                for a, b in ciftler]
    yol = _graf_yaz(izole_kok, {"dugumler": dugumler, "kenarlar": kenarlar})
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "⚑ Dugum C (C) iki kümeyi bağlıyor" in out
    assert "muvazaa / perdeyi kaldırma incele" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["kopru_dugumler"] == [{"id": "C", "ad": "Dugum C"}]


# ── 5. yönlü çevrim (dairesel illiyet) ──────────────────────────────────────

def test_yonlu_illiyet_cevrimi_a_b_c_a_raporlanir(izole_kok):
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
            {"id": "C", "tip": "olay", "ad": "Olay C"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "illiyet", "tur": "sebep",
             "illiyet_tipi": "dogal", "dogrulama": "delil", "dayanak_delil": ["x"]},
            {"kaynak": "B", "hedef": "C", "kategori": "illiyet", "tur": "sebep",
             "illiyet_tipi": "dogal", "dogrulama": "delil", "dayanak_delil": ["x"]},
            {"kaynak": "C", "hedef": "A", "kategori": "illiyet", "tur": "sebep",
             "illiyet_tipi": "dogal", "dogrulama": "delil", "dayanak_delil": ["x"]},
        ],
    }
    yol = _graf_yaz(izole_kok, graf)
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0, "çevrim bulgusu da exit kodunu değiştirmez (mevcut tasarım)"
    assert "✗ Olay A → Olay B → Olay C → Olay A" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["cevrimler"] == [["A", "B", "C", "A"]]


def test_iliski_kenarlarinin_cevrimi_denetime_girmez(izole_kok):
    """Çevrim denetimi yalnız kategori=illiyet kenarlarına bakar; iliski
    kenarlarından oluşan yönlü çevrim raporlanmaz (karakterizasyon —
    mevcut tasarım)."""
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "iliski", "tur": "bag",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
            {"kaynak": "B", "hedef": "A", "kategori": "iliski", "tur": "bag",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
        ],
    }
    yol = _graf_yaz(izole_kok, graf)
    kod, out, err = _cli(yol)

    assert kod == 0
    assert "✓ İlliyet zinciri dairesel değil." in out


# ── 6. kesme adayı (kesme_flag) ─────────────────────────────────────────────

def test_kesme_flagli_illiyet_kenari_aday_iliski_kenari_yok_sayilir(izole_kok):
    """kesme_flag yalnız kategori=illiyet kenarında görülür; iliski
    kenarındaki kesme_flag sessizce yok sayılır. JSON kenar referansı
    kesme_flag alanını TAŞIMAZ (karakterizasyon — mevcut tasarım)."""
    graf = {
        "dugumler": [
            {"id": "A", "tip": "olay", "ad": "Olay A"},
            {"id": "B", "tip": "olay", "ad": "Olay B"},
            {"id": "C", "tip": "olay", "ad": "Olay C"},
        ],
        "kenarlar": [
            {"kaynak": "A", "hedef": "B", "kategori": "illiyet", "tur": "sebep",
             "illiyet_tipi": "dogal", "kesme_flag": "mucbir sebep",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
            {"kaynak": "B", "hedef": "C", "kategori": "iliski", "tur": "bag",
             "kesme_flag": "ucuncu kisi kusuru",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
            {"kaynak": "A", "hedef": "C", "kategori": "iliski", "tur": "bag",
             "dogrulama": "delil", "dayanak_delil": ["x"]},
        ],
    }
    yol = _graf_yaz(izole_kok, graf)
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "KESME: mucbir sebep" in out
    assert "oa-antitez ile çürüt veya kabul et" in out
    assert "KESME: ucuncu kisi kusuru" not in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert len(sonuc["kesme_adaylari"]) == 1
    tek = sonuc["kesme_adaylari"][0]
    assert tek["index"] == 0
    # _kenar_ref kesme_flag/illiyet_tipi taşımaz — anahtar seti sabit:
    assert set(tek) == KENAR_REF_ANAHTARLARI


# ── 7. yük taşıyan kenar (illiyet alt-grafında bridge) ──────────────────────

def test_dort_dugumlu_zincirde_yalniz_ic_kenar_yuk_tasir(izole_kok):
    """A→B→C→D illiyet zincirinde koddan doğrulanan davranış: bileşen
    sayımı KALAN kenarlardan türetilen düğümler üzerinde yapıldığından uç
    kenarlar (A→B, C→D) bridge sayılMAZ; yalnız iç kenar B→C bridge çıkar
    (karakterizasyon — mevcut tasarım)."""
    dugumler = [{"id": i, "tip": "olay", "ad": f"Olay {i}"}
                for i in ("A", "B", "C", "D")]
    ciftler = [("A", "B"), ("B", "C"), ("C", "D")]
    kenarlar = [{"kaynak": a, "hedef": b, "kategori": "illiyet", "tur": "sebep",
                 "illiyet_tipi": "dogal", "dogrulama": "delil",
                 "dayanak_delil": ["x"]}
                for a, b in ciftler]
    yol = _graf_yaz(izole_kok, {"dugumler": dugumler, "kenarlar": kenarlar})
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "★ Olay B —[sebep]→ Olay C" in out
    assert "stratejik öncelik: bu bağı sağlamlaştır" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert len(sonuc["yuk_tasiyan_kenarlar"]) == 1
    tek = sonuc["yuk_tasiyan_kenarlar"][0]
    assert (tek["index"], tek["kaynak"], tek["hedef"]) == (1, "B", "C")


def test_uc_dugumlu_zincirde_hicbir_kenar_yuk_tasiyan_sayilmaz(izole_kok):
    """A→B→C zincirinde her iki kenar da uç kenardır: hangisi çıkarılsa
    sarkaç düğüm kenar kümesinden düşer ve bileşen sayısı artmaz → hiçbir
    kenar bridge raporlanmaz (karakterizasyon — mevcut tasarım)."""
    dugumler = [{"id": i, "tip": "olay", "ad": f"Olay {i}"}
                for i in ("A", "B", "C")]
    ciftler = [("A", "B"), ("B", "C")]
    kenarlar = [{"kaynak": a, "hedef": b, "kategori": "illiyet", "tur": "sebep",
                 "illiyet_tipi": "dogal", "dogrulama": "delil",
                 "dayanak_delil": ["x"]}
                for a, b in ciftler]
    yol = _graf_yaz(izole_kok, {"dugumler": dugumler, "kenarlar": kenarlar})
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "Belirgin tek yük taşıyan kenar yok" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["yuk_tasiyan_kenarlar"] == []


# ── --json çıktısı: anahtar seti + içerik ───────────────────────────────────

def test_json_cikti_anahtar_seti_ve_arac_degeri(izole_kok):
    yol = _graf_yaz(izole_kok, _temiz_graf())
    json_yol = izole_kok / "sonuc.json"
    kod, out, err = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "[JSON] Makine-okur sonuc yazildi:" in out
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))

    assert set(sonuc) == JSON_ANAHTARLARI
    assert sonuc["arac"] == "grafik_denetim"
    assert sonuc["ozet"] == {"dugum": 3, "kenar": 3}
    assert sonuc["girdi"] == str(yol)

    # temiz grafta tüm bulgu listeleri boş
    for anahtar in ("sema_hatalari", "yetim_dugumler", "desteksiz_kenarlar",
                    "kopru_dugumler", "cevrimler", "kesme_adaylari",
                    "yuk_tasiyan_kenarlar"):
        assert sonuc[anahtar] == [], f"{anahtar} temiz grafta boş olmalı"

    # düğüm ve kenar dökümlerinin alan setleri
    assert len(sonuc["dugumler"]) == 3
    for d in sonuc["dugumler"]:
        assert set(d) == {"id", "tip", "ad", "usul_rolu"}
    assert len(sonuc["kenarlar"]) == 3
    for k in sonuc["kenarlar"]:
        assert set(k) == KENAR_REF_ANAHTARLARI
    # gercek_kisi olmayan düğümlerde usul_rolu null olarak dökülür
    roller = {d["id"]: d["usul_rolu"] for d in sonuc["dugumler"]}
    assert roller == {"DAVALI": "davali", "FIIL": None, "ZARAR": None}


# ── bozuk/eksik girdi ve exit kodları ───────────────────────────────────────

def test_arguman_yok_kullanim_mesaji_exit1(izole_kok):
    kod, out, err = _cli()
    assert kod == 1
    assert "Kullanım: python grafik_denetim.py graf.json" in out


def test_var_olmayan_dosya_cokus_traceback_exit1(izole_kok):
    """yukle() dosya-yok durumunu yakalamaz — script traceback ile çöker
    (karakterizasyon — mevcut tasarım; düzeltme yapılmaz)."""
    kod, out, err = _cli(izole_kok / "yok.json")
    assert kod != 0
    assert kod == 1
    assert "Traceback" in err
    assert "FileNotFoundError" in err


def test_bozuk_json_cokus_traceback_exit1(izole_kok):
    """Bozuk JSON da yakalanmaz — json.JSONDecodeError traceback'i ile
    çöker (karakterizasyon — mevcut tasarım)."""
    yol = izole_kok / "graf.json"
    yol.write_text("{ bozuk json", encoding="utf-8")
    kod, out, err = _cli(yol)
    assert kod != 0
    assert kod == 1
    assert "Traceback" in err
    assert "JSONDecodeError" in err


def test_bos_graf_nesnesi_cokmez_exit0(izole_kok):
    """{} girdisi: 0 düğüm / 0 kenar ile rapor üretir, çökmez."""
    yol = _graf_yaz(izole_kok, {})
    kod, out, err = _cli(yol)
    assert kod == 0, f"stderr:\n{err}"
    assert "Düğüm: 0  |  Kenar: 0" in out
    assert "✓ Şema bütün." in out
