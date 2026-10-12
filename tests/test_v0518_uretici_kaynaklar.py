# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİR ÜRETİCİLERİ · S1 KAYNAK BEYANI (B-1(a), B-11).

NEDEN VAR: Fable tutarlılık raporu (2026-10-07) B-1 — "zincirleme tepki yok":
ingest yeniden koşup `00-kunye.json` değişince vakıa matrisi, illiyet grafı,
kıyas ve antitez denetim JSON'ları ESKİ girdiye göre üretilmiş hâlleriyle
yerinde duruyor, DURUM.md ve teslim yeşil kalıyordu. Çünkü dört motorun
JSON'u hangi girdiden üretildiğini BEYAN ETMİYORDU; tazelik denetimi yalnız
`<!-- kaynaklar: -->` bloğu taşıyan .md/.txt ürünleri okuyabiliyordu.

Sözleşme (S1 — Görev 2 üretir, Görev 1 `tazelik_denetim` tüketir): denetim
JSON'unun üst düzeyinde
    "kaynaklar": [{"rol": str, "yol": str, "sha8": str}, …]   (rol, yol) sıralı
    yol  = dosyayı içeren `_oa` dizinine göre POSIX göreli yol
    sha8 = hashlib.sha256(bayt).hexdigest()[:8]   (tazelik_denetim.sha8 ile aynı)
    rol  = "girdi" (denetlenen model girdisi) · "kunye" (`<_oa>/metin/00-kunye.json` VARSA)
Girdi bir `_oa` ağacında değilse "kaynaklar": [] + "kaynaklar_notu":
"_oa dışı girdi — tazelik denetimi dışı" (denetim dışı ≠ temiz). Not alanı
HER ZAMAN vardır (not yoksa null) — üst-düzey anahtar kümesi girdinin yerine
göre değişmez (K1 ileri koruması kilitleri kararlı kalır).
B-11 (Ruling): mevcut `girdi` alanı GERİYE UYUM için AYNEN kalır (komut
satırındaki yolun yankısı); köke göreli kimlik `kaynaklar[].yol` ile sağlanır.

Determinizm: `yol` göreli/POSIX, `sha8` yalnız bayta bağlı — dava klasörü
taşınsa da, cwd değişse de aynı. Mutlak yol, zaman damgası YOK.
Bütün veriler kurgudur (anayasa m.7); ağ yok, gerçek dava verisi yok.
"""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
VAKIA_MATRIS = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
GRAFIK = SKILLS / "oa-illiyet" / "scripts" / "grafik_denetim.py"
KIYAS = SKILLS / "oa-kiyas" / "scripts" / "kiyas_denetim.py"
ANTITEZ = SKILLS / "oa-antitez" / "scripts" / "antitez_matris.py"

OA_DISI_NOTU = "_oa dışı girdi — tazelik denetimi dışı"


def _modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha8(bayt):
    return hashlib.sha256(bayt).hexdigest()[:8]


def _kos(script, argumanlar, cwd):
    cp = subprocess.run([sys.executable, str(script), *argumanlar], cwd=str(cwd),
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    return cp.returncode, cp.stdout or "", cp.stderr or ""


# ── kurgu girdiler (dört motor, hepsi "temiz" sonuç verir) ──────────────────

VAKIA_GIRDI = {
    "iddialar": [{"id": "I1", "metin": "Mal kurgu tarihte teslim edildi", "tur": "vakia"}],
    "olaylar": [{"tarih": "2025-03-12", "olgu": "Teslim", "belge": "İrsaliye (kurgu)",
                 "destekler": ["I1"], "ispat_durumu": "belgeli"}],
}

GRAF_GIRDI = {
    "dugumler": [{"id": "FIIL", "tip": "olay", "ad": "Fiil (kurgu)"},
                 {"id": "ZARAR", "tip": "olay", "ad": "Zarar (kurgu)"},
                 {"id": "D1", "tip": "delil", "ad": "Bilirkişi raporu (kurgu)"}],
    "kenarlar": [{"kaynak": "FIIL", "hedef": "ZARAR", "kategori": "illiyet",
                  "tur": "sebep_zarar", "illiyet_tipi": "uygun", "guc": "guclu",
                  "dogrulama": "teyitli", "dayanak_delil": ["D1"], "norm": "TBK m.49 (kurgu çıpa)"}],
}

KIYAS_GIRDI = {
    "buyuk_onerme": {"norm": "TBK m.49 (kurgu çıpa)",
                     "ictihat": [{"kunye": "Yargıtay 4. HD 2099/1 E. (kurgu)", "dogrulama": "teyitli"}],
                     "unsurlar": [{"id": "fiil", "ad": "Fiil"}]},
    "kucuk_onerme": {"vakialar": [{"metin": "Davalı fiili işledi (kurgu)", "karsilar": ["fiil"],
                                   "dayanak_delil": ["tutanak (kurgu)"]}]},
    "sonuc": "Sorumluluk doğar (kurgu).",
}


def _antitez_girdi():
    cepheler = _modul(ANTITEZ, "v0518_uretici_kaynaklar_antitez").STANDART_CEPHELER
    return {"tez": "Kurgu tez", "cepheler": [
        {"cephe": k, "antitez": "değerlendirildi: saldırı yok", "guc": "yok", "curutme": "",
         "curutme_dayanak": "", "dayanak_durum": "yok", "artik_risk": "", "duyulmus": False}
        for k in cepheler]}


def _vakia_argv(g, j):
    return ["--dogrula", g, "--json", j]


# (etiket, script, girdi dosya adı, argüman kurucu, girdi, beklenen arac)
MOTORLAR = [
    pytest.param("vakia", VAKIA_MATRIS, "04-vakia.json",
                 _vakia_argv, VAKIA_GIRDI, "vakia_matris", id="vakia"),
    pytest.param("illiyet", GRAFIK, "01-illiyet-graf.json",
                 lambda g, j: [g, "--json", j], GRAF_GIRDI, "grafik_denetim", id="illiyet"),
    pytest.param("kiyas", KIYAS, "05-kiyas.json",
                 lambda g, j: [g, "--json", j], KIYAS_GIRDI, "kiyas_denetim", id="kiyas"),
    pytest.param("antitez", ANTITEZ, "06-antitez-matris.json",
                 lambda g, j: ["--dogrula", g, "--json", j], _antitez_girdi, "antitez_matris", id="antitez"),
]

KUNYE = {"dosya": "E. 2099/1 (kurgu)", "evrak": [{"no": "001", "ad": "sentetik-evrak.txt"}]}


def _bayt(nesne):
    nesne = nesne() if callable(nesne) else nesne
    return json.dumps(nesne, ensure_ascii=False, indent=2).encode("utf-8")


def _dava_koku(tmp_path, kunye=True):
    kok = tmp_path / "dava"
    (kok / "_oa" / "cikti").mkdir(parents=True)
    kunye_bayt = None
    if kunye:
        (kok / "_oa" / "metin").mkdir()
        kunye_bayt = _bayt(KUNYE)
        (kok / "_oa" / "metin" / "00-kunye.json").write_bytes(kunye_bayt)
    return kok, kunye_bayt


def _denetim(script, argv, kok, ad, girdi):
    """Girdiyi `<kok>/_oa/cikti/<ad>` olarak yazar, motoru kök içinden göreli
    yolla koşturur, denetim JSON'unu döner."""
    girdi_bayt = _bayt(girdi)
    (kok / "_oa" / "cikti" / ad).write_bytes(girdi_bayt)
    goreli_girdi = f"_oa/cikti/{ad}"
    goreli_json = f"_oa/cikti/{ad[:-5]}-denetim.json"
    kod, out, err = _kos(script, argv(goreli_girdi, goreli_json), cwd=kok)
    assert "Traceback" not in err, err[-1500:]
    assert kod == 0, out[-1500:]
    return girdi_bayt, goreli_girdi, json.loads((kok / goreli_json).read_text(encoding="utf-8"))


# ═══════════════════════════════ S1 ═════════════════════════════════════════

@pytest.mark.parametrize("etiket, script, ad, argv, girdi, arac", MOTORLAR)
def test_kaynaklar_girdi_ve_kunye_sha8_ile_yazilir(tmp_path, etiket, script, ad, argv, girdi, arac):
    """`_oa` ağacındaki girdi + mevcut künye → iki kayıt, (rol, yol) sıralı,
    yol `_oa`ya göre POSIX göreli, sha8 = sha256[:8]. `girdi` alanı komut
    satırındaki yolun AYNISI (B-11 geriye uyum). JSON sort_keys ile yazılır."""
    kok, kunye_bayt = _dava_koku(tmp_path)
    girdi_bayt, goreli_girdi, d = _denetim(script, argv, kok, ad, girdi)

    assert d["arac"] == arac
    assert d["kaynaklar"] == [
        {"rol": "girdi", "yol": f"cikti/{ad}", "sha8": _sha8(girdi_bayt)},
        {"rol": "kunye", "yol": "metin/00-kunye.json", "sha8": _sha8(kunye_bayt)},
    ]
    assert d["kaynaklar_notu"] is None
    assert d["girdi"] == goreli_girdi, "B-11: `girdi` alanı komut satırının yankısı kalır"
    assert list(d) == sorted(d), "denetim JSON'u sort_keys=True ile yazılmalı"
    for k in d["kaynaklar"]:
        assert "\\" not in k["yol"] and not k["yol"].startswith("/"), k
        assert len(k["sha8"]) == 8 and int(k["sha8"], 16) >= 0


@pytest.mark.parametrize("etiket, script, ad, argv, girdi, arac", MOTORLAR)
def test_oa_disi_girdide_kaynaklar_bos_ve_not_var(tmp_path, etiket, script, ad, argv, girdi, arac):
    """Avukatın masaüstündeki taslak (`_oa` ağacı dışı): kaynak beyanı BOŞ +
    görünür not. Tazelik denetimi bunu "temiz" DEĞİL "denetim dışı" okur."""
    taslak = tmp_path / "taslak"
    taslak.mkdir()
    (taslak / ad).write_bytes(_bayt(girdi))
    kod, out, err = _kos(script, argv(ad, "denetim.json"), cwd=taslak)
    assert "Traceback" not in err, err[-1500:]
    assert kod == 0, out[-1500:]
    d = json.loads((taslak / "denetim.json").read_text(encoding="utf-8"))

    assert d["kaynaklar"] == []
    assert d["kaynaklar_notu"] == OA_DISI_NOTU
    assert d["girdi"] == ad


@pytest.mark.parametrize("etiket, script, ad, argv, girdi, arac", MOTORLAR)
def test_kunye_yoksa_yalniz_girdi_beyan_edilir(tmp_path, etiket, script, ad, argv, girdi, arac):
    """Künye henüz üretilmemişse (ingest koşmamış) beyan yalnız girdiyi taşır;
    yokluk not üretmez — "kunye" rolü VARSA yazılır (S1)."""
    kok, _ = _dava_koku(tmp_path, kunye=False)
    girdi_bayt, _, d = _denetim(script, argv, kok, ad, girdi)

    assert d["kaynaklar"] == [{"rol": "girdi", "yol": f"cikti/{ad}", "sha8": _sha8(girdi_bayt)}]
    assert d["kaynaklar_notu"] is None


def test_mutlak_yolla_cagrilsa_da_kaynak_yolu_goreli_posix(tmp_path):
    """Farklı cwd + MUTLAK girdi yolu: `kaynaklar[].yol` yine `_oa`ya göre
    göreli POSIX (determinizm: dava klasörü taşınsa da aynı bayt); `girdi`
    alanı ise verilen mutlak yolun yankısıdır (B-11)."""
    kok, kunye_bayt = _dava_koku(tmp_path)
    cikti = kok / "_oa" / "cikti"
    girdi_bayt = _bayt(VAKIA_GIRDI)
    (cikti / "04-vakia.json").write_bytes(girdi_bayt)
    baska_cwd = tmp_path / "baska"
    baska_cwd.mkdir()
    mutlak = str(cikti / "04-vakia.json")
    hedef = str(cikti / "04-vakia-denetim.json")
    kod, out, err = _kos(VAKIA_MATRIS, ["--dogrula", mutlak, "--json", hedef], cwd=baska_cwd)
    assert kod == 0 and "Traceback" not in err
    d = json.loads(pathlib.Path(hedef).read_text(encoding="utf-8"))

    assert [k["yol"] for k in d["kaynaklar"]] == ["cikti/04-vakia.json", "metin/00-kunye.json"]
    assert d["girdi"] == mutlak


def test_girdi_degisince_sha8_degisir_zincirleme_tepki_sinyali(tmp_path):
    """Zincirleme tepkinin tohumu: aynı girdi dosyası değişince `girdi`
    kaydının sha8'i değişir, künye kaydı aynı kalır — tazelik denetimi
    "bayat halka"yı bu farktan okur."""
    kok, kunye_bayt = _dava_koku(tmp_path)
    _, _, once = _denetim(VAKIA_MATRIS, _vakia_argv, kok, "04-vakia.json", VAKIA_GIRDI)
    degisik = json.loads(json.dumps(VAKIA_GIRDI))
    degisik["olaylar"][0]["belge"] = "İrsaliye + teslim tutanağı (kurgu)"
    _, _, sonra = _denetim(VAKIA_MATRIS, _vakia_argv, kok, "04-vakia.json", degisik)

    girdi = {k["rol"]: k["sha8"] for k in once["kaynaklar"]}
    girdi2 = {k["rol"]: k["sha8"] for k in sonra["kaynaklar"]}
    assert girdi["girdi"] != girdi2["girdi"]
    assert girdi["kunye"] == girdi2["kunye"] == _sha8(kunye_bayt)


@pytest.mark.parametrize("etiket, script, ad, argv, girdi, arac", MOTORLAR)
def test_iki_ayri_oa_kokunde_goreli_cagri_bayt_ozdes(tmp_path, etiket, script, ad, argv, girdi, arac):
    """K-6 (inceleme): determinizm süiti S1'in `_oa` dalını hiç çalıştırmaz
    (girdileri tmp kökünde → her koşuda `kaynaklar == []`). Bu test `_oa`
    DALINI kilitler: iki ayrı `_oa` kökünde (farklı derinlik → farklı mutlak
    yol) aynı girdi + aynı künye, göreli çağrı → denetim JSON'u ve stdout BAYT
    BAYT aynı; `kaynaklar` dolu (fikstür sözleşmesi: dal gerçekten koştu).
    `tests/test_v0518_determinizm_dort_parca.py` DEĞİŞTİRİLMEDİ."""
    sonuclar = []
    for kok in (tmp_path / "a" / "dava", tmp_path / "b" / "ic" / "ic" / "dava"):
        (kok / "_oa" / "cikti").mkdir(parents=True)
        (kok / "_oa" / "metin").mkdir()
        (kok / "_oa" / "metin" / "00-kunye.json").write_bytes(_bayt(KUNYE))
        (kok / "_oa" / "cikti" / ad).write_bytes(_bayt(girdi))
        goreli_json = f"_oa/cikti/{ad[:-5]}-denetim.json"
        kod, out, err = _kos(script, argv(f"_oa/cikti/{ad}", goreli_json), cwd=kok)
        assert kod == 0 and "Traceback" not in err, err[-1500:]
        sonuclar.append((out, (kok / goreli_json).read_bytes()))
    (out1, json1), (out2, json2) = sonuclar
    assert json1 == json2, "iki `_oa` kökünde denetim JSON'u bayt-özdeş değil"
    assert out1 == out2, "iki `_oa` kökünde stdout bayt-özdeş değil"
    d = json.loads(json1)
    assert [k["rol"] for k in d["kaynaklar"]] == ["girdi", "kunye"] and d["kaynaklar_notu"] is None


def test_grafik_denetim_coktu_kaydi_da_kaynak_beyani_tasir(tmp_path):
    """K2'nin okuduğu çökme kaydı (`denetim_coktu: true`, exit 2) hangi
    girdi baytlarına ait olduğunu söyler — bozuk girdinin sha8'i + künye.
    Okunamayan girdi "temiz" sayılmaz; kaydın kimliği yine de belli olur."""
    kok, kunye_bayt = _dava_koku(tmp_path)
    bozuk = b"{bozuk json"
    (kok / "_oa" / "cikti" / "01-illiyet-graf.json").write_bytes(bozuk)
    kod, out, err = _kos(GRAFIK, ["_oa/cikti/01-illiyet-graf.json",
                                  "--json", "_oa/cikti/01-illiyet-denetim.json"], cwd=kok)
    assert kod == 2 and "DENETİM ÇÖKTÜ" in out
    d = json.loads((kok / "_oa" / "cikti" / "01-illiyet-denetim.json").read_text(encoding="utf-8"))

    assert d["denetim_coktu"] is True and d["arac"] == "grafik_denetim"
    assert d["kaynaklar"] == [
        {"rol": "girdi", "yol": "cikti/01-illiyet-graf.json", "sha8": _sha8(bozuk)},
        {"rol": "kunye", "yol": "metin/00-kunye.json", "sha8": _sha8(kunye_bayt)},
    ]
    assert d["kaynaklar_notu"] is None
