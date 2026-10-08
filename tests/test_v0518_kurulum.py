# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — KURULUM MOTORU `oa_kurulum.py` (avukat talimatı, 2026-10-07: "projenin
içerisinde mutlaka zincirleme şekilde, Yargı Pro hariç kalan tüm gereksinimleri tek prompt'ta
indirecek kısmı oluştur — vitrinde bu zaten konseptimiz").

NEDEN VAR: README'deki tek yapıştırmalık prompt kurulumu Claude'a yürütür; zincirin KANIT
halkası bu motordur — beyan değil, script çıktısı. Bu dosya kilitler:
  - her gereksinim tek satırda TAMAM / EKSİK (→ resmî komut) / ELİMDE / BİLGİ,
  - çıkış kodu sözleşmesi (0 zorunlular tamam · 1 eksik var · 2 kullanım hatası),
  - sürüm sabitlerinin TEK kaynaktan okunması (PYMUPDF_ASGARI, UDF_CLI_SURUM — kopya yok),
  - Tesseract PATH'te yokken Windows standart yolunda bulunması,
  - `.pyc` tazeliğinin Python'un kendi başlık doğrulamasıyla ölçülmesi,
  - `--uygula`nın pip "externally-managed-environment" ortamında DURMASI,
  - Yargı Pro'nun KAPSAM DIŞI kalması ve yasak komutların kaynakta bulunmaması,
  - JSON raporunun deterministik olması.
Gerçek kurulum ve ağ YOK: sistem sondaları sahtelenir (monkeypatch).
"""
import importlib.util
import json
import os
import pathlib
import py_compile
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
EKLENTI = REPO / "plugins" / "ortak-avukat"
MOTOR = EKLENTI / "skills" / "ortak-avukat" / "scripts" / "oa_kurulum.py"
BELGE_GUVENLIK = EKLENTI / "skills" / "oa-ingest" / "scripts" / "belge_guvenlik.py"
UDF_YAZ = EKLENTI / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py"


def _yukle(ad="_v0518_oa_kurulum_test"):
    spec = importlib.util.spec_from_file_location(ad, MOTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pymupdf_asgari():
    m = re.search(r"^PYMUPDF_ASGARI\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
                  BELGE_GUVENLIK.read_text(encoding="utf-8"), re.M)
    return ".".join(m.groups())


def _udf_surum():
    return re.search(r'^UDF_CLI_SURUM\s*=\s*"([^"]+)"', UDF_YAZ.read_text(encoding="utf-8"), re.M).group(1)


@pytest.fixture
def mod(monkeypatch):
    """Her şeyin TAMAM olduğu sahte bir Windows makinesi; testler tek sondayı bozar."""
    m = _yukle()
    surumler = {"pymupdf": _pymupdf_asgari(), "pillow": "11.0.0", "markitdown": "0.1.2"}
    komutlar = {"tesseract": r"C:\Tesseract\tesseract.exe", "node": r"C:\node\node.exe",
                "npx": r"C:\node\npx.cmd", "npm": r"C:\node\npm.cmd"}

    def _calistir(argv, zaman_asimi=60):
        ad = os.path.basename(str(argv[0])).lower()
        if "tesseract" in ad:
            return 0, "List of available languages (3):\neng\nosd\ntur\n"
        if ad.startswith("node"):
            return 0, "v22.11.0\n"
        if "aile_dogrula" in " ".join(map(str, argv)):
            return 0, "AİLE YAPI DENETİMİ TEMİZ.\n"
        return 0, ""

    monkeypatch.setattr(m, "_paket_surumu", lambda ad: surumler.get(ad))
    monkeypatch.setattr(m, "_komut_bul", lambda ad: komutlar.get(ad))
    monkeypatch.setattr(m, "_calistir", _calistir)
    monkeypatch.setattr(m, "_platform", lambda: "win32")
    monkeypatch.setattr(m, "_python_surumu", lambda: (3, 14, 8))
    monkeypatch.setattr(m, "_pyc_taze", lambda kaynak: True)
    m._sahte = {"surumler": surumler, "komutlar": komutlar}
    return m


def _adim(adimlar, anahtar):
    bulunan = [a for a in adimlar if a["anahtar"] == anahtar]
    assert len(bulunan) == 1, (anahtar, [a["anahtar"] for a in adimlar])
    return bulunan[0]


# ── çıkış sözleşmesi ve satır biçimi ─────────────────────────────────────────────────

def test_her_sey_tamamken_cikis_0_ve_her_adim_tek_satir(mod, capsys):
    kod = mod.main([])
    out = capsys.readouterr().out
    assert kod == 0, out
    satirlar = [s for s in out.splitlines() if re.match(r"^\d+\) ", s)]
    assert len(satirlar) >= 9, out
    for s in satirlar:
        assert re.search(r" — (TAMAM|EKSİK|ELİMDE|BİLGİ)\b", s), s
    assert "EKSİK" not in out


def test_eski_pymupdf_eksik_ve_alt_sinir_tek_kaynaktan(mod):
    mod._sahte["surumler"]["pymupdf"] = "1.23.0"
    a = _adim(mod.denetle(), "pip_paketleri")
    assert a["durum"] == "EKSİK", a
    assert '"pymupdf>=%s"' % _pymupdf_asgari() in a["komut"], a["komut"]
    assert sys.executable in a["komut"] or "python" in a["komut"].lower()
    kaynak = MOTOR.read_text(encoding="utf-8")
    assert _pymupdf_asgari() not in kaynak, "alt sınır motora KOPYALANMIŞ (tek kaynak: belge_guvenlik.py)"


def test_eksik_paketler_tek_pip_komutunda(mod):
    mod._sahte["surumler"].pop("markitdown")
    mod._sahte["surumler"].pop("pillow")
    a = _adim(mod.denetle(), "pip_paketleri")
    assert a["durum"] == "EKSİK" and "pillow" in a["komut"] and '"markitdown[all]"' in a["komut"]
    assert "pymupdf" not in a["komut"], "kurulu ve yeterli paket yeniden kurulmaz"
    assert "--break-system-packages" not in a["komut"]


def test_tesseract_pathte_yok_ama_windows_standart_yolunda_bulunur(mod, monkeypatch):
    mod._sahte["komutlar"].pop("tesseract")
    monkeypatch.setattr(mod, "_dosya_var", lambda yol: str(yol) == str(mod.WINDOWS_TESSERACT))
    a = _adim(mod.denetle(), "tesseract")
    assert a["durum"] == "TAMAM", a
    assert "PATH" in a["ayrinti"], "PATH'te olmadığı görünür not olmalı"


def test_tur_dil_verisi_yoksa_eksik_ve_platform_komutu(mod, monkeypatch):
    def _calistir(argv, zaman_asimi=60):
        if "tesseract" in os.path.basename(str(argv[0])).lower():
            return 0, "List of available languages (2):\neng\nosd\n"
        if "aile_dogrula" in " ".join(map(str, argv)):
            return 0, "AİLE YAPI DENETİMİ TEMİZ.\n"
        return 0, "v22.11.0\n"
    monkeypatch.setattr(mod, "_calistir", _calistir)
    a = _adim(mod.denetle(), "tesseract")
    assert a["durum"] == "EKSİK" and "tur" in a["ayrinti"], a
    assert "tur.traineddata" in a["komut"]
    monkeypatch.setattr(mod, "_platform", lambda: "linux")
    assert "tesseract-ocr-tur" in _adim(mod.denetle(), "tesseract")["komut"]
    monkeypatch.setattr(mod, "_platform", lambda: "darwin")
    assert "brew install tesseract-lang" in _adim(mod.denetle(), "tesseract")["komut"]


def test_node_yoksa_eksik_ve_resmi_kimlikli_komut(mod):
    mod._sahte["komutlar"].pop("node")
    a = _adim(mod.denetle(), "node")
    assert a["durum"] == "EKSİK" and "OpenJS.NodeJS.LTS" in a["komut"], a


def test_udf_cli_girisi_elimde_ve_surum_tek_kaynaktan(mod):
    a = _adim(mod.denetle(), "udf_cli")
    assert a["durum"] == "ELİMDE", a
    assert "udf-cli@%s whoami" % _udf_surum() in a["komut"] and "login" in a["komut"]
    assert '"%s"' % _udf_surum() not in MOTOR.read_text(encoding="utf-8"), \
        "udf-cli sürümü motora KOPYALANMIŞ (tek kaynak: udf_yaz.py)"


def test_python_eskiyse_eksik_314_onerilir(mod, monkeypatch):
    monkeypatch.setattr(mod, "_python_surumu", lambda: (3, 11, 9))
    a = _adim(mod.denetle(), "python")
    assert a["durum"] == "EKSİK" and "Python.Python.3.14" in a["komut"], a
    monkeypatch.setattr(mod, "_python_surumu", lambda: (3, 12, 15))
    a = _adim(mod.denetle(), "python")
    assert a["durum"] == "TAMAM" and "3.14" in a["ayrinti"], "3.12 yeterli ama 3.14 önerisi görünmeli"


# ── eklenti bütünlüğü, derleme, aile denetimi ───────────────────────────────────────

def test_eklenti_butunlugu_depoda_tamam(mod):
    a = _adim(mod.denetle(), "eklenti")
    assert a["durum"] == "TAMAM", a
    assert "20 parça" in a["ayrinti"] and "kanca olayı" in a["ayrinti"]


def test_yetim_surum_klasorunden_kosulursa_eksik(mod, tmp_path):
    kok = tmp_path / "0.5.17"
    (kok / ".claude-plugin").mkdir(parents=True)
    (kok / ".claude-plugin" / "plugin.json").write_text('{"version": "0.5.17"}', encoding="utf-8")
    (kok / ".orphaned_at").write_text("1", encoding="utf-8")
    a = _adim(mod.denetle(kok=kok), "eklenti")
    assert a["durum"] == "EKSİK" and "orphaned" in a["ayrinti"], a


def test_surum_klasoru_ile_plugin_json_ayrisirsa_eksik(mod, tmp_path):
    kok = tmp_path / "0.5.18"
    (kok / ".claude-plugin").mkdir(parents=True)
    (kok / ".claude-plugin" / "plugin.json").write_text('{"version": "0.5.17"}', encoding="utf-8")
    a = _adim(mod.denetle(kok=kok), "eklenti")
    assert a["durum"] == "EKSİK" and "0.5.17" in a["ayrinti"], a


def test_bayat_pyc_eksik_ve_compileall_komutu(mod, monkeypatch):
    monkeypatch.setattr(mod, "_pyc_taze", lambda kaynak: False)
    a = _adim(mod.denetle(), "derleme")
    assert a["durum"] == "EKSİK" and "compileall" in a["komut"], a
    assert "PYTHONDONTWRITEBYTECODE" in a["ayrinti"]


def test_pyc_tazeligi_pythonun_kendi_baslik_dogrulamasiyla(tmp_path):
    m = _yukle("_v0518_oa_kurulum_pyc")
    kaynak = tmp_path / "ornek.py"
    kaynak.write_text("X = 1\n", encoding="utf-8")
    assert m._pyc_taze(kaynak) is False, "derlenmemiş kaynak taze sayılmaz"
    zaman = py_compile.PycInvalidationMode.TIMESTAMP
    py_compile.compile(str(kaynak), doraise=True, invalidation_mode=zaman)
    assert m._pyc_taze(kaynak) is True
    kaynak.write_text("X = 22\n", encoding="utf-8")   # boyut değişti → pyc bayat
    assert m._pyc_taze(kaynak) is False
    # SOURCE_DATE_EPOCH tanımlıysa compileall karma tabanlı pyc yazar — kaynak karması denetlenir
    karma = py_compile.PycInvalidationMode.CHECKED_HASH
    py_compile.compile(str(kaynak), doraise=True, invalidation_mode=karma)
    assert m._pyc_taze(kaynak) is True
    kaynak.write_text("X = 333\n", encoding="utf-8")
    assert m._pyc_taze(kaynak) is False, "karma tabanlı pyc kaynak değişince bayat sayılmalı"


def test_aile_denetimi_temiz_degilse_eksik(mod, monkeypatch):
    def _calistir(argv, zaman_asimi=60):
        if "aile_dogrula" in " ".join(map(str, argv)):
            return 1, "HATA: oa-x: SKILL.md eksik\n"
        if "tesseract" in os.path.basename(str(argv[0])).lower():
            return 0, "tur\n"
        return 0, "v22.11.0\n"
    monkeypatch.setattr(mod, "_calistir", _calistir)
    assert _adim(mod.denetle(), "aile")["durum"] == "EKSİK"


# ── Yargı Pro kapsam dışı, yasaklar ─────────────────────────────────────────────────

def test_yargi_pro_kapsam_disi_bilgi_ve_cikisi_etkilemez(mod, capsys):
    a = _adim(mod.denetle(), "yargi_pro")
    assert a["durum"] == "BİLGİ" and "KAPSAM DIŞI" in a["ayrinti"] and "ücretli" in a["ayrinti"]
    assert "/mcp" in a["komut"]
    assert mod.main([]) == 0


@pytest.mark.parametrize("yasak", [
    "setx", "--break-system-packages", "Invoke-Expression", "iex ", "| sh", "| bash",
    "claude mcp add", "curl ", "wget ", "import requests", "import urllib",
])
def test_kaynakta_yasak_desen_yok(yasak):
    kaynak = MOTOR.read_text(encoding="utf-8")
    govde = kaynak.split('"""', 2)[2]   # modül docstring'i dışı: kod ve yorumlar
    assert yasak not in govde, "yasak desen kaynakta: %r" % yasak


# ── --uygula ─────────────────────────────────────────────────────────────────────────

def test_uygula_externally_managed_ortamda_durur(mod, monkeypatch, capsys):
    mod._sahte["surumler"].pop("pillow")
    cagrilar = []

    def _calistir(argv, zaman_asimi=60):
        cagrilar.append([str(x) for x in argv])
        if "pip" in argv:
            return 1, "error: externally-managed-environment\n× This environment is externally managed\n"
        return 0, "tur\n"
    monkeypatch.setattr(mod, "_calistir", _calistir)
    kod = mod.main(["--uygula"])
    out = capsys.readouterr().out
    assert kod == 1, out
    assert "externally-managed" in out and "venv" in out
    assert not any("compileall" in c for c in cagrilar), "pip durunca zincir ilerlememeli"
    assert not any("--break-system-packages" in c for c in cagrilar)


def test_uygula_pip_ve_compileall_kosturur_sonra_yeniden_denetler(mod, monkeypatch, capsys):
    mod._sahte["surumler"].pop("pillow")
    cagrilar = []

    def _calistir(argv, zaman_asimi=60):
        cagrilar.append([str(x) for x in argv])
        if "pip" in argv:
            mod._sahte["surumler"]["pillow"] = "11.0.0"     # kurulum "başarılı"
            return 0, "Successfully installed pillow\n"
        if "tesseract" in os.path.basename(str(argv[0])).lower():
            return 0, "tur\n"
        if "aile_dogrula" in " ".join(map(str, argv)):
            return 0, "AİLE YAPI DENETİMİ TEMİZ.\n"
        return 0, "v22.11.0\n"
    monkeypatch.setattr(mod, "_calistir", _calistir)
    kod = mod.main(["--uygula"])
    assert kod == 0, capsys.readouterr().out
    pip = [c for c in cagrilar if "pip" in c]
    assert pip and pip[0][:4] == [sys.executable, "-m", "pip", "install"] and "pillow" in pip[0]
    derleme = [c for c in cagrilar if "compileall" in c]
    assert derleme and derleme[0][:4] == [sys.executable, "-m", "compileall", "-q"]


# ── JSON determinizmi ────────────────────────────────────────────────────────────────

def test_json_raporu_deterministik(mod, tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    assert mod.main(["--json", str(a)]) == 0 and mod.main(["--json", str(b)]) == 0
    assert a.read_bytes() == b.read_bytes()
    veri = json.loads(a.read_text(encoding="utf-8"))
    assert veri["cikis"] == 0 and veri["adimlar"] and all("durum" in x for x in veri["adimlar"])


def test_kullanim_hatasi_cikis_2(mod):
    with pytest.raises(SystemExit) as e:
        mod.main(["--olmayan-bayrak"])
    assert e.value.code == 2
