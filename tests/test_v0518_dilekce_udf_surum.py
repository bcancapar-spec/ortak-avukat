# -*- coding: utf-8 -*-
"""v0.5.18 — DIŞ ARAÇ SÜRÜM SABİTLERİ (kullanıcı kararı 2026-10-05: "Layer 0'a
dahil + sürüm sabitle").

NEDEN VAR: `udf_yaz.py` her teslimde sabitlenmemiş en son udf-cli (ve hazır
.docx/.pdf için docx2udf) sürümünü ağ + oturumla çalıştırıyordu; yeni bir
upstream yayını denetimsiz biçimde teslim zincirine giriyordu. Sürümler artık
tek kaynaktaki sabitlerdedir (`UDF_CLI_SURUM`, `DOCX2UDF_SURUM`); belgede
yalnız önerilen dış araçlar (uyap-tiff-cli, uyap-pdf-cli) da sabitlenmiş
sürümle yazılır.

Kilitlenen sözleşmeler:
  1. `UDF_CLI_SURUM = "x.y.z"` ve `DOCX2UDF_SURUM = "x.y.z"` tek satır, sütun
     0, düz string literalidir (başka scriptler SATIR olarak okur);
     `*_PAKET == "<paket>@" + *_SURUM`.
  2. oa-dilekce scriptlerinde, belgelerinde ve SKILL.md'de HİÇBİR
     `<paket>@latest` (sabitlenmemiş sürüm) ifadesi YOK.
  3. Belgelerdeki her `udf-cli@<sürüm>` / `docx2udf@<sürüm>` örneği koddaki
     sabitle AYNIDIR; belgede yalnız önerilen araçların her biri tek bir
     sabit sürümle yazılır — yükseltmede belge güncellemesi unutulamaz.
  4. whoami / html2udf / udf2md / docx2udf çağrıları sabitlenmiş paketi
     kullanır; giriş talimatı sabitlenmiş sürümü gösterir; üretim makbuzu
     üretici paketi kaydeder.
  5. Yükseltme yöntemi (avukat onayı + yayım notları + testler) belgelidir.

Deterministik: gerçek npx ÇAĞRILMAZ (shutil.which ve subprocess.run sahte),
ağ yok, indirme yok, rastgelelik ve süre ölçümü yok.
"""
import importlib.util
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
UDF_YAZ = SKILL / "scripts" / "udf_yaz.py"
# Sabitlenmemiş sürüm: '<paket>@latest'. Desen parçalı kurulur ki bu test
# dosyasının kendisi de bir tarayıcıya takılmasın.
SABITSIZ_RE = re.compile(r"[A-Za-z0-9][\w.\-]*@" + "latest" + r"\b")
SURUM_RE = r"([0-9][0-9A-Za-z.\-]*[0-9A-Za-z])"


@pytest.fixture(scope="module")
def uy():
    spec = importlib.util.spec_from_file_location("udf_yaz_v0518_surum", UDF_YAZ)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _skill_dosyalari():
    yollar = (sorted(SKILL.glob("scripts/*.py")) + sorted(SKILL.glob("references/*.md"))
              + [SKILL / "SKILL.md"])
    assert len(yollar) > 5, yollar
    return yollar


def _surum_ornekleri(paket):
    """oa-dilekce dosyalarındaki `<paket>@<sürüm>` örnekleri: [(dosya, sürüm)]."""
    desen = re.compile(r"(?<![\w.\-])" + re.escape(paket) + "@" + SURUM_RE)
    return [(p.name, m.group(1)) for p in _skill_dosyalari()
            for m in desen.finditer(p.read_text(encoding="utf-8"))]


# ── 1. Tek kaynak sabitler ───────────────────────────────────────────────────

@pytest.mark.parametrize("ad,paket_ad,paket", [
    ("UDF_CLI_SURUM", "UDF_CLI_PAKET", "udf-cli"),
    ("DOCX2UDF_SURUM", "DOCX2UDF_PAKET", "docx2udf"),
])
def test_surum_sabiti_tek_satir_duz_string_literali(uy, ad, paket_ad, paket):
    metin = UDF_YAZ.read_text(encoding="utf-8")
    eslesmeler = re.findall(r'^' + ad + r' = "([^"\n]+)"[ \t]*$', metin, re.M)
    assert eslesmeler == [getattr(uy, ad)], eslesmeler
    assert re.fullmatch(r"\d+\.\d+\.\d+", getattr(uy, ad)), getattr(uy, ad)
    assert getattr(uy, paket_ad) == paket + "@" + getattr(uy, ad)


def test_sabitlenmis_surumler_avukat_onayli_degerler(uy):
    """Yükseltme bilinçli iştir: bu beklentiler YALNIZ avukat onaylı
    yükseltmede, yayım notları okunduktan sonra değiştirilir."""
    assert uy.UDF_CLI_SURUM == "0.5.6"
    assert uy.DOCX2UDF_SURUM == "1.0.6"


# ── 2-3. Belgeler ve scriptler ───────────────────────────────────────────────

def test_oa_dilekce_dosyalarinda_sabitlenmemis_surum_yok():
    bulunan = [(str(p.relative_to(REPO)), m.group(0)) for p in _skill_dosyalari()
               for m in SABITSIZ_RE.finditer(p.read_text(encoding="utf-8"))]
    assert bulunan == [], bulunan


@pytest.mark.parametrize("paket,sabit", [("udf-cli", "UDF_CLI_SURUM"),
                                         ("docx2udf", "DOCX2UDF_SURUM")])
def test_belgelerdeki_surum_ornekleri_koddaki_sabitle_ayni(uy, paket, sabit):
    ornekler = _surum_ornekleri(paket)
    farkli = [o for o in ornekler if o[1] != getattr(uy, sabit)]
    assert farkli == [], farkli
    assert len(ornekler) >= 3, f"{paket}: belgelerde sabitlenmiş örnek beklenirdi ({ornekler})"


@pytest.mark.parametrize("paket", ["uyap-tiff-cli", "uyap-pdf-cli"])
def test_yalniz_belgede_onerilen_araclar_tek_sabit_surumle(paket):
    ornekler = _surum_ornekleri(paket)
    assert ornekler, f"{paket}: sabitlenmiş örnek bulunamadı"
    assert len({s for _d, s in ornekler}) == 1, ornekler


def test_dis_arac_layer0_notu_ve_yerel_hat_tercihi_belgeli():
    metin = (SKILL / "references" / "uyap-belge-formatlari.md").read_text(encoding="utf-8")
    assert "Layer 0" in metin and "oa-ingest" in metin and "çevrimdışı" in metin
    assert "lisans" in metin.lower() and "UNLICENSED" in metin


def test_yukseltme_yontemi_belgeli():
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    gunluk = (SKILL / "references" / "degisiklik-gunlugu.md").read_text(encoding="utf-8")
    plan = (SKILL / "references" / "udf-hatti-kesinti-plani.md").read_text(encoding="utf-8")
    for metin in (skill, gunluk, plan):
        assert "UDF_CLI_SURUM" in metin and "DOCX2UDF_SURUM" in metin
        assert "ükseltme yöntemi" in metin
        assert "yayım notları" in metin


# ── 4. Çağrılar sahte npx ile — gerçek npx ÇAĞRILMAZ ─────────────────────────

class _Sonuc:
    def __init__(self, kod=0, cikti="", hata=""):
        self.returncode, self.stdout, self.stderr = kod, cikti, hata


@pytest.fixture
def sahte_npx(uy, monkeypatch):
    cagrilar = []

    def _run(args, **_k):
        cagrilar.append(list(args))
        return _Sonuc(0, "sahte cikti", "")

    monkeypatch.setattr(uy.shutil, "which", lambda _ad: "npx-sahte")
    monkeypatch.setattr(uy.subprocess, "run", _run)
    return cagrilar


def test_udf_cli_cagrilari_sabitlenmis_paketi_kullanir(uy, sahte_npx, tmp_path):
    uy.npx_kullanilabilir_mi()
    html = tmp_path / "taslak.html"
    html.write_text("<p>Sentetik metin.</p>", encoding="utf-8")
    uy.npx_ile_udf_uret(str(html), str(tmp_path / "taslak.udf"))
    uy.npx_ile_udf_oku(str(tmp_path / "taslak.udf"))
    assert len(sahte_npx) == 3, sahte_npx
    alt_komutlar = []
    for args in sahte_npx:
        assert args[:3] == ["npx-sahte", "-y", "udf-cli@0.5.6"], args
        assert args[2] == uy.UDF_CLI_PAKET
        assert not any("latest" in str(a) for a in args), args
        alt_komutlar.append(args[3])
    assert alt_komutlar == ["whoami", "html2udf", "udf2md"]


def test_docx2udf_cagrisi_sabitlenmis_paketi_kullanir(uy, sahte_npx, tmp_path):
    girdi = tmp_path / "taslak.docx"
    girdi.write_bytes(b"sentetik")
    uy.docx2udf_ile_uret(str(girdi), str(tmp_path / "taslak.udf"))
    assert len(sahte_npx) == 1, sahte_npx
    args = sahte_npx[0]
    assert args[:3] == ["npx-sahte", "-y", "docx2udf@1.0.6"], args
    assert args[2] == uy.DOCX2UDF_PAKET
    assert not any("latest" in str(a) for a in args), args


def test_giris_talimati_sabitlenmis_surumu_gosterir(uy):
    assert uy._GIRIS_TALIMATI.count("npx -y " + uy.UDF_CLI_PAKET + " login") == 2
    assert "latest" not in uy._GIRIS_TALIMATI


@pytest.mark.parametrize("motor,beklenen_ad", [
    ("html2udf", "UDF_CLI_PAKET"), ("docx2udf", "DOCX2UDF_PAKET"), ("yerel-riskli", None)])
def test_uretim_makbuzu_uretici_paketi_kaydeder(uy, tmp_path, motor, beklenen_ad):
    (tmp_path / "_oa").mkdir()
    cikti = tmp_path / "dilekce.udf"
    cikti.write_bytes(b"sentetik")
    yol = uy._uretim_makbuzu_yaz(str(tmp_path), "taslak.md", str(cikti), motor,
                                {"gecerli": True, "resmi_okuyucu": "OK"})
    kayit = json.loads(pathlib.Path(yol).read_text(encoding="utf-8").splitlines()[-1])
    beklenen = getattr(uy, beklenen_ad) if beklenen_ad else None
    assert kayit["uretici_paket"] == beklenen
