# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİRLEME TEPKİ (B-1b / B-1c): tazelik denetimi JSON ürünlerini
de görür; pipeline_kayit bayat halkayı DURUM.md'ye taşır.

Fable tutarlılık raporu (2026-10-07) B-1: ingest yeniden koşup `00-kunye.json`
değişince dört motorun denetim JSON'u (vakıa/graf/kıyas/antitez) AYNEN duruyor,
`tazelik_denetim.py` yalnız `.md/.txt` ürünlerinin `<!-- kaynaklar: -->`
bloğuna bakıyordu → DURUM.md ve teslim YEŞİL kalıyordu. Sözleşme S1: motorlar
denetim JSON'una `"kaynaklar": [{"rol","yol","sha8"}]` yazar (Görev 2); bu
dosya o beyanı TÜKETEN tarafı kilitler (fikstür verisiyle — üretici kod bu
worktree'de yok).

Kademeli benimseme (Review Focus 3): eski sürümün `kaynaklar`sız JSON'u BAYAT
sayılmaz, "beyansız" görünür. `_oa` dışı girdi (Review Focus 2): kaynak
beyanı boş + not → "temiz" DENMEZ, "denetim dışı" denir. Okunamayan JSON
(Review Focus 1) "temiz" sayılmaz, görünür.

Gerçek müvekkil verisi yok — her fikstür sentetiktir (anayasa m.7).
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
TAZELIK = SKILLS / "oa-kontrol" / "scripts" / "tazelik_denetim.py"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tz():
    return _yukle("tazelik_denetim_v0518_zincir", TAZELIK)


@pytest.fixture(scope="module")
def pk():
    return _yukle("pipeline_kayit_v0518_zincir_tazelik", PIPELINE)


def _sha8(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:8]


def _kok_kur(tmp_path):
    kok = tmp_path / "dava"
    (kok / "_oa" / "metin").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    (kok / "_oa" / "metin" / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 10, "kayitlar": []}), encoding="utf-8")
    return kok


def _girdi_yaz(kok, ad, veri):
    yol = kok / "_oa" / "cikti" / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _kaynaklar(kok, girdi_goreli):
    """S1 sözleşmesi: (rol, yol) sırasıyla; yol `_oa`ya göre POSIX göreli."""
    oa = kok / "_oa"
    kayitlar = [{"rol": "girdi", "yol": girdi_goreli, "sha8": _sha8(oa / girdi_goreli)}]
    kunye = oa / "metin" / "00-kunye.json"
    if kunye.is_file():
        kayitlar.append({"rol": "kunye", "yol": "metin/00-kunye.json", "sha8": _sha8(kunye)})
    return sorted(kayitlar, key=lambda k: (k["rol"], k["yol"]))


def _denetim_yaz(kok, ad, arac, girdi_goreli, **ek):
    """Damgalı denetim JSON'u (Görev 2'nin üreteceği biçimin fikstürü)."""
    veri = {"arac": arac, "girdi": str(kok / "_oa" / girdi_goreli),
            "kaynaklar": _kaynaklar(kok, girdi_goreli)}
    veri.update(ek)
    yol = kok / "_oa" / "cikti" / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return yol


def _kunye_degistir(kok):
    (kok / "_oa" / "metin" / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 11, "kayitlar": [{"ad": "yeni mazbata"}]}),
        encoding="utf-8")


def _tazelik_cli(kok, *ek):
    cp = subprocess.run([sys.executable, str(TAZELIK), "--kok", str(kok), *ek],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _pk_cli(args, cwd):
    cp = subprocess.run([sys.executable, str(PIPELINE)] + args, capture_output=True,
                        text=True, encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _durum_md(kok):
    return (kok / "_oa" / "DURUM.md").read_text(encoding="utf-8")


# ═══════════════ B-1(b) — tazelik_denetim.py JSON ürünlerini denetler ═══════

def test_json_urun_kunye_degisince_BAYAT(tz, tmp_path):
    """Damgalı vakıa denetimi künyeyi kaynak beyan etmiş; künye değişti →
    ürün BAYAT (urun_denetle sözleşmesi .json için de geçerli)."""
    kok = _kok_kur(tmp_path)
    _girdi_yaz(kok, "04-vakia.json", {"iddialar": [], "olaylar": []})
    yol = _denetim_yaz(kok, "04-vakia-denetim.json", "vakia_matris", "cikti/04-vakia.json",
                       ispat_bosluklari=[])
    _kunye_degistir(kok)
    bayatlar, eksikler = tz.urun_denetle(str(kok), str(yol))
    assert bayatlar is not None and eksikler == []
    assert [b[0] for b in bayatlar] == ["metin/00-kunye.json"]
    beyan, simdiki = bayatlar[0][1], bayatlar[0][2]
    assert beyan != simdiki and simdiki == _sha8(kok / "_oa" / "metin" / "00-kunye.json")


def test_json_urun_taze_ise_bayat_yok(tz, tmp_path):
    kok = _kok_kur(tmp_path)
    _girdi_yaz(kok, "01-illiyet-graf.json", {"dugumler": [], "kenarlar": []})
    yol = _denetim_yaz(kok, "01-illiyet-denetim.json", "grafik_denetim",
                       "cikti/01-illiyet-graf.json", cevrimler=[])
    assert tz.urun_denetle(str(kok), str(yol)) == ([], [])


def test_json_girdi_degisince_de_BAYAT(tz, tmp_path):
    """Yalnız künye değil: denetlenen model girdisi (ör. graf) sonradan
    değişirse denetim JSON'u o girdi için BAYAT."""
    kok = _kok_kur(tmp_path)
    girdi = _girdi_yaz(kok, "01-illiyet-graf.json", {"dugumler": [], "kenarlar": []})
    yol = _denetim_yaz(kok, "01-illiyet-denetim.json", "grafik_denetim",
                       "cikti/01-illiyet-graf.json")
    girdi.write_text(json.dumps({"dugumler": [{"id": "A", "tip": "olay"}], "kenarlar": []}),
                     encoding="utf-8")
    bayatlar, eksikler = tz.urun_denetle(str(kok), str(yol))
    assert [b[0] for b in bayatlar] == ["cikti/01-illiyet-graf.json"] and eksikler == []


def test_kaynaklarsiz_eski_json_bayat_DEGIL_beyansiz(tz, tmp_path):
    """Review Focus 3 — kademeli benimseme: eski sürümün `kaynaklar`sız damgalı
    JSON'u bayat SAYILMAZ (yanlış alarm yok), raporda 'beyansız' görünür."""
    kok = _kok_kur(tmp_path)
    yol = _girdi_yaz(kok, "05-kiyas-denetim.json",
                     {"arac": "kiyas_denetim", "kritik_bosluk": False, "teyitsiz_ictihat": []})
    _kunye_degistir(kok)
    assert tz.urun_denetle(str(kok), str(yol)) == (None, None)
    kod, out = _tazelik_cli(kok, "--json")
    assert kod == 0
    r = json.loads(next(s for s in out.splitlines() if s.strip().startswith("{")))
    assert r["bayat"] == [] and r["eksik"] == []
    assert "05-kiyas-denetim.json" in r["beyansiz_json"]
    kod, out = _tazelik_cli(kok)
    assert kod == 0 and "beyansız" in out and "BAYAT" not in out


def test_kok_disi_kaynak_yolu_EKSIK(tz, tmp_path):
    """`_guvenli_yol` korunur: `_oa` dışına kaçan beyan EKSİK sayılır
    (bayat değil, ama temiz de değil — görünür)."""
    kok = _kok_kur(tmp_path)
    disari = tmp_path / "disari.json"
    disari.write_text("{}", encoding="utf-8")
    yol = kok / "_oa" / "cikti" / "04-vakia-denetim.json"
    yol.write_text(json.dumps({
        "arac": "vakia_matris",
        "kaynaklar": [{"rol": "girdi", "yol": "../../disari.json", "sha8": _sha8(disari)}],
    }), encoding="utf-8")
    bayatlar, eksikler = tz.urun_denetle(str(kok), str(yol))
    assert bayatlar == [] and eksikler == ["../../disari.json"]
    kod, out = _tazelik_cli(kok, "--json")
    r = json.loads(next(s for s in out.splitlines() if s.strip().startswith("{")))
    assert r["eksik"] == [{"urun": "04-vakia-denetim.json", "kaynak": "../../disari.json"}]


def test_oa_disi_girdi_denetim_disi_temiz_DEMEZ(tz, tmp_path):
    """Review Focus 2 — avukatın masaüstündeki taslak üzerinde koşan motor:
    `kaynaklar: []` + not. Tazelik 'TAZE/temiz' demez, 'denetim dışı' der."""
    kok = _kok_kur(tmp_path)
    yol = _girdi_yaz(kok, "kiyas-taslak-denetim.json", {
        "arac": "kiyas_denetim", "kaynaklar": [],
        "kaynaklar_notu": "_oa dışı girdi — tazelik denetimi dışı"})
    assert tz.urun_denetle(str(kok), str(yol)) == (None, None)
    kod, out = _tazelik_cli(kok, "--json")
    r = json.loads(next(s for s in out.splitlines() if s.strip().startswith("{")))
    assert r["denetim_disi"] == [{"urun": "kiyas-taslak-denetim.json",
                                 "not": "_oa dışı girdi — tazelik denetimi dışı"}]
    kod, out = _tazelik_cli(kok)
    assert kod == 0
    assert "denetim DIŞI" in out and "TAZE" not in out


def test_bozuk_json_OKUNAMADI_gorunur_temiz_sayilmaz(tz, tmp_path):
    """Review Focus 1 — yarım yazılmış/bozuk denetim JSON'u: sessizce atlanmaz,
    'OKUNAMADI' görünür; o kökte 'tüm ürünler TAZE' denmez."""
    kok = _kok_kur(tmp_path)
    (kok / "_oa" / "cikti" / "01-illiyet-denetim.json").write_text(
        '{"arac": "grafik_denetim", "kaynaklar": [', encoding="utf-8")
    kod, out = _tazelik_cli(kok, "--json")
    assert kod == 0  # advisory sözleşmesi korunur
    r = json.loads(next(s for s in out.splitlines() if s.strip().startswith("{")))
    assert len(r["okunamayan"]) == 1 and r["okunamayan"][0]["urun"] == "01-illiyet-denetim.json"
    kod, out = _tazelik_cli(kok)
    assert "OKUNAMADI" in out and "01-illiyet-denetim.json" in out
    assert "TAZE" not in out


def test_damgasiz_json_model_girdisi_urun_sayilmaz(tz, tmp_path):
    """`04-vakia.json` gibi damgasız model girdileri KAYNAKTIR, türetilmiş ürün
    değil — ne bloksuz ne okunamayan sayılır (gürültü yok)."""
    kok = _kok_kur(tmp_path)
    _girdi_yaz(kok, "04-vakia.json", {"iddialar": [], "olaylar": []})
    kod, out = _tazelik_cli(kok, "--json")
    r = json.loads(next(s for s in out.splitlines() if s.strip().startswith("{")))
    assert r["bloksuz"] == 0 and r["beyansiz_json"] == [] and r["okunamayan"] == []


def test_md_urun_sozlesmesi_degismedi(tz, tmp_path):
    """Geriye uyum: `.md` ürünlerinin `<!-- kaynaklar: -->` bloğu aynen çalışır."""
    kok = _kok_kur(tmp_path)
    kunye = kok / "_oa" / "metin" / "00-kunye.json"
    (kok / "_oa" / "cikti" / "07-strateji.md").write_text(
        f"<!-- kaynaklar: metin/00-kunye.json@{_sha8(kunye)} -->\n# Strateji\n", encoding="utf-8")
    assert tz.urun_denetle(str(kok), str(kok / "_oa" / "cikti" / "07-strateji.md")) == ([], [])
    _kunye_degistir(kok)
    bayatlar, _ = tz.urun_denetle(str(kok), str(kok / "_oa" / "cikti" / "07-strateji.md"))
    assert [b[0] for b in bayatlar] == ["metin/00-kunye.json"]


# ═══════════════ B-1(c) — pipeline_kayit: DURUM.md bayat zincir hattı ═══════

def _zincir_kur(kok):
    """Üç halkanın model girdisi + üç damgalı denetim JSON'u (künye kaynaklı)."""
    _girdi_yaz(kok, "04-vakia.json", {"iddialar": [], "olaylar": []})
    _girdi_yaz(kok, "01-illiyet-graf.json", {"dugumler": [], "kenarlar": []})
    _girdi_yaz(kok, "05-kiyas.json", {"buyuk_onerme": {"unsurlar": []},
                                      "kucuk_onerme": {"vakialar": []}})
    _denetim_yaz(kok, "04-vakia-denetim.json", "vakia_matris", "cikti/04-vakia.json",
                 ispat_bosluklari=[])
    _denetim_yaz(kok, "01-illiyet-denetim.json", "grafik_denetim",
                 "cikti/01-illiyet-graf.json", cevrimler=[], sema_hatalari=[])
    _denetim_yaz(kok, "05-kiyas-denetim.json", "kiyas_denetim", "cikti/05-kiyas.json",
                 kritik_bosluk=False, teyitsiz_ictihat=[])


def _baslat(kok):
    kod, out = _pk_cli(["--baslat", "Sentetik Zincir Davası", "--kok", str(kok)], cwd=kok)
    assert kod == 0, out


def test_kunye_degisince_vakia_graf_kiyas_BAYAT_isaretlenir(pk, tmp_path):
    """B-1'in ta kendisi: yeni evrak → künye değişir → vakıa/graf/kıyas
    denetimleri BAYAT; DURUM.md advisory hattı üçünü de adıyla söyler ve
    'ilgili motoru yeniden koşun' der. Teslimi DURDURMAZ (avukat kararı)."""
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _zincir_kur(kok)
    _kunye_degistir(kok)

    satirlar = pk._bayat_zincir_uyarisi(str(kok))
    assert len(satirlar) == 3, satirlar
    for urun in ("04-vakia-denetim.json", "01-illiyet-denetim.json", "05-kiyas-denetim.json"):
        s = next(x for x in satirlar if urun in x)
        assert s.startswith("BAYAT — ")
        assert "metin/00-kunye.json" in s and "üretiminden sonra değişti" in s
        assert "ilgili motoru yeniden koşun" in s

    kod, out = _pk_cli(["--denetle", "--kok", str(kok)], cwd=kok)
    md = _durum_md(kok)
    assert "## 🔴 Bayat Zincir Uyarısı" in md
    for urun in ("04-vakia-denetim.json", "01-illiyet-denetim.json", "05-kiyas-denetim.json"):
        assert f"BAYAT — _oa/cikti/{urun}" in md.replace("\\", "/"), md


def test_taze_zincirde_bayat_bolumu_yok(pk, tmp_path):
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _zincir_kur(kok)
    assert pk._bayat_zincir_uyarisi(str(kok)) == []
    _pk_cli(["--denetle", "--kok", str(kok)], cwd=kok)
    assert "Bayat Zincir" not in _durum_md(kok)


def test_beyansiz_eski_json_bayat_alarmi_vermez(pk, tmp_path):
    """Kademeli benimseme DURUM.md tarafında da: `kaynaklar`sız eski denetim
    JSON'u künye değişse bile bayat satırı üretmez."""
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _girdi_yaz(kok, "01-illiyet-denetim.json", {"arac": "grafik_denetim", "cevrimler": []})
    _kunye_degistir(kok)
    assert pk._bayat_zincir_uyarisi(str(kok)) == []


def test_oa_disi_girdi_DURUM_md_de_denetim_disi_notu(pk, tmp_path):
    """Review Focus 2 — kaynak beyanı boş + not: DURUM.md 'temiz' demez,
    'DENETİM DIŞI' satırı düşer."""
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _girdi_yaz(kok, "kiyas-taslak-denetim.json", {
        "arac": "kiyas_denetim", "kaynaklar": [],
        "kaynaklar_notu": "_oa dışı girdi — tazelik denetimi dışı"})
    satirlar = pk._bayat_zincir_uyarisi(str(kok))
    assert len(satirlar) == 1 and satirlar[0].startswith("DENETİM DIŞI — ")
    assert "kiyas-taslak-denetim.json" in satirlar[0] and "temiz SAYILMAZ" in satirlar[0]


def test_bayat_zincir_tazelik_modulunu_paylasimli_anahtarla_yukler(pk):
    """CLAUDE.md #5 — kardeş modül in-process, süreç çapında TEK örnek
    (`sys.modules` paylaşımlı anahtar); subprocess YOK."""
    mod = pk._tazelik_denetim_modulu()
    assert mod is not None and callable(getattr(mod, "kok_denetle", None))
    assert sys.modules.get(pk._OA_PAYLASIMLI_TAZELIK) is mod
    assert pk._tazelik_denetim_modulu() is mod


# ═══════════════ Görev 1 incelemesi Ö-1 / Ö-3 (Görev 9 — ana oturum, 2026-10-08) ═══════

def _kismi_beyanli_denetim(kok, yol_ek="", not_ek=""):
    """Görev 2'nin `kaynak_beyani` kısmi hâli: okunamayan `girdi` rolü listeden düşer, sebebi
    `kaynaklar_notu`na yazılır; liste yalnız künyeyi taşır."""
    _girdi_yaz(kok, "04-vakia.json", {"iddialar": [], "olaylar": []})
    kunye = kok / "_oa" / "metin" / "00-kunye.json"
    veri = {"arac": "vakia_matris", "girdi": str(kok / "_oa" / "cikti" / "04-vakia.json"),
            "kaynaklar": [{"rol": "kunye", "yol": "metin/00-kunye.json" + yol_ek, "sha8": _sha8(kunye)}],
            "kaynaklar_notu": "girdi kaynak beyanına alınamadı (PermissionError)" + not_ek,
            "ispat_bosluklari": []}
    yol = kok / "_oa" / "cikti" / "04-vakia-denetim.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return yol


def test_kismi_beyan_notu_gorunur_girdi_eksigi_TAZE_demez(tz, tmp_path):
    """Ö-1: liste doluyken `kaynaklar_notu` okunmuyor, `girdi` rolünün yokluğu fark edilmiyordu —
    beyansız girdi sonradan değişse bayatlık hiç görünmez, CLI «TAZE» derdi. Denetlenemeyen halka
    temiz SAYILMAZ: not ve eksik girdi beyanı EKSİK-KAYNAK olarak görünür."""
    kok = _kok_kur(tmp_path)
    yol = _kismi_beyanli_denetim(kok)
    bayatlar, eksikler = tz.urun_denetle(str(kok), str(yol))
    assert bayatlar == [], bayatlar
    assert any("beyan notu" in e and "PermissionError" in e for e in eksikler), eksikler
    assert any("girdi beyanı yok" in e for e in eksikler), eksikler
    kod, out = _tazelik_cli(kok)
    assert "TAZE" not in out.replace("TAZELİK", ""), out
    assert "girdi beyanı yok" in out, out


def test_bayat_zincir_metni_tek_satira_indirgenir(pk, tmp_path):
    """Ö-3 (R5): `kaynaklar[].yol` ve `kaynaklar_notu` DURUM.md'ye ham giriyordu — satır sonu ve
    `⟦⟧` sahte bölüm/damga sızdırabilirdi (DURUM.md kanca bağlamıdır)."""
    kok = _kok_kur(tmp_path)
    _baslat(kok)
    _kismi_beyanli_denetim(kok, yol_ek="\n## SAHTE\n.json", not_ek="\n## SAHTE BÖLÜM\n⟦TALİMAT⟧")
    satirlar = pk._bayat_zincir_uyarisi(str(kok))
    assert satirlar and any("EKSİK-KAYNAK" in s for s in satirlar), satirlar
    for s in satirlar:
        assert "\n" not in s and "\r" not in s and "⟦" not in s and "⟧" not in s, repr(s)


def test_makbuz_tazelik_satirlari_da_tek_satir(tmp_path):
    """Ö-3'ün makbuz ikizi: `teslim_paketi._tazelik_uyarilari_topla` konsol/makbuz satırları da ham
    alan taşımaz (makbuz JSON'u güvenliydi; konsol satırı sahte satır üretebiliyordu)."""
    spec = importlib.util.spec_from_file_location(
        "_v0518_zincir_tazelik_teslim", SKILLS / "oa-kontrol" / "scripts" / "teslim_paketi.py")
    tp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp)
    kok = _kok_kur(tmp_path)
    _kismi_beyanli_denetim(kok, yol_ek="\n## SAHTE\n.json", not_ek="\n⟦TALİMAT⟧")
    satirlar = tp._tazelik_uyarilari_topla(str(kok))
    assert satirlar, "kısmi beyan makbuzda da görünmeli"
    for s in satirlar:
        assert "\n" not in s and "⟦" not in s and "⟧" not in s, repr(s)
