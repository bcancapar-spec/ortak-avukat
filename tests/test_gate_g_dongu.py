# -*- coding: utf-8 -*-
"""P0-4 (v0.5.5) — Gate G dairesel bağımlılık kırıcı.

Eski mimaride `tam_tur.cmd_kaydet` → subprocess `pipeline_kayit.py --denetle`
→ subprocess `tam_tur.py --durum` zinciri, TAMAM işaretini YAZACAK OLAN
`--kaydet` çağrısının kendi kendine bu işareti ÖNCEDEN istemesine (fiziksel
olarak imkânsız) yol açıyordu — defter açık + tam_tur kullanılan HER kökte
İLK `--kaydet` `--zorla` gerektiriyordu (bootstrap çıkmazı). P0-4 kökten
çözümü: `pipeline_kayit.py` `tam_tur.py`'yi İN-PROCESS import eder (subprocess
VE env sınıfı TAMAMEN kalkar); tam_tur.cmd_kaydet kendi Gate G kalıcılık
denetimini yalnız kendisine karşı ATLAR (`gate_g_atla=True`, CLI'de YOK),
bağımsız `pipeline_kayit.py --denetle` çağrılarında Gate G TAM GÜÇTE kalır.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PK_SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
TT_SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"


def _load(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _load(PK_SCRIPT, "pipeline_kayit_gdongu")


def _pk_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(PK_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _tt_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(TT_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _p06_onkosul_fixture_kur(tmp_path):
    """P0-6 (v0.5.5) — İNGEST-ÖNCE (00-kunye.json) + adım-5 (05-kiyas* AND
    *ictihat-muhakeme*) + adım-9 (teslim-makbuz.json) blokleyici kümesini bu
    dosyanın 'tüm adım/katman UYGULANDI' senaryosunda ÖNCEDEN karşılar —
    testlerin AMACI (Gate G dairesel bağımlılık davranışı) DEĞİŞMEZ."""
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "05-kiyas-test.md").write_text(
        "# Kıyas\n" + ("Somut olayla emsal karar arasında kıyas gövdesi. " * 6),
        encoding="utf-8")
    (cikti / "ornek-ictihat-muhakeme.md").write_text(
        "# İçtihat Muhakeme Kaydı\n" + ("Muhakeme gövdesi test amaçlı doldurulmuştur. " * 6),
        encoding="utf-8")
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0, "taslak_yol": None, "taslak_sha256": None}),
        encoding="utf-8")


def _tum_adim_katmanlari_isle(tmp_path):
    _p06_onkosul_fixture_kur(tmp_path)
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    for no, (_ad, parcalar) in pk.ADIMLAR.items():
        for parca in parcalar:
            kod, cikti = _pk_cli(
                ["--isle", "--adim", str(no), "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", uzun_kanit + " script", "--kok", str(tmp_path)],
                cwd=tmp_path,
            )
            assert kod == 0, f"adım {no}/{parca} işlenemedi: {cikti}"
    for katman in pk.KATMANLAR:
        kod, cikti = _pk_cli(
            ["--katman", katman, "--durum", "UYGULANDI", "--kanit", uzun_kanit + " script",
             "--kok", str(tmp_path)],
            cwd=tmp_path,
        )
        assert kod == 0, f"katman {katman} işlenemedi: {cikti}"


def _kunye_ve_cikti_kur(tmp_path):
    metin_dizin = tmp_path / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 1,
                    "kayitlar": [{"kaynak": "dilekce.pdf", "sha": "a" * 16}]}),
        encoding="utf-8")
    (tmp_path / "dilekce.pdf").write_text("plasöy-holder", encoding="utf-8")
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "01-parca.md").write_text("çalışma evrakı", encoding="utf-8")


# ── (1) regresyon kilidi: subprocess/env sınıfı TAMAMEN kalktı ─────────────

def test_subprocess_importu_pipeline_kayit_ve_tam_turdan_kalkti():
    pk_kaynak = PK_SCRIPT.read_text(encoding="utf-8")
    tt_kaynak = TT_SCRIPT.read_text(encoding="utf-8")
    assert "import subprocess" not in pk_kaynak
    assert "import subprocess" not in tt_kaynak
    assert "OA_GATE_ZINCIR" not in pk_kaynak
    assert "OA_GATE_ZINCIR" not in tt_kaynak
    assert "importlib.util" in pk_kaynak
    assert "importlib.util" in tt_kaynak


# ── (2) KRİTİK — taze defterli + tam_tur kullanan kökte İLK --kaydet
#        --zorla'SIZ tamamlanır (bootstrap çıkmazı ÇÖZÜLDÜ) ────────────────

def test_defterli_kokte_ilk_kaydet_zorlasiz_tamamlanir(tmp_path):
    kod, cikti = _pk_cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    _tum_adim_katmanlari_isle(tmp_path)
    _kunye_ve_cikti_kur(tmp_path)

    kod, cikti = _tt_cli(["--baslat", "--dosya", "Test Dosyası", "--kok", str(tmp_path)],
                          cwd=tmp_path)
    assert kod == 0, cikti

    kod, cikti = _tt_cli(["--kaydet", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, (
        "P0-4 REGRESYONU — defter açık + tam_tur kullanan kökte İLK --kaydet "
        f"--zorla gerektirmemeli (bootstrap döngüsü):\n{cikti}"
    )
    assert "--zorla" not in cikti

    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    assert analiz_md.is_file()
    icerik = analiz_md.read_text(encoding="utf-8")
    assert "oa:tam-tur:TAMAM" in icerik


# ── (3) bağımsız dış --denetle Gate G'yi AYNEN (tam güçte) koşar ───────────

def test_bagimsiz_denetle_gate_g_tam_guctedir(tmp_path):
    """`pipeline_kayit.py --denetle` DIŞARIDAN (tam_tur.cmd_kaydet dışından)
    çağrıldığında `gate_g_atla`ya HİÇBİR yoldan erişemez — dosya-analiz.md
    fiziksel TAMAM değilken (yalnız --baslat/--senkron ile İSKELET varken)
    Gate G kalıcılık kapısı GERÇEKTEN engel üretmelidir (fail-closed)."""
    kod, cikti = _pk_cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    _tum_adim_katmanlari_isle(tmp_path)
    _kunye_ve_cikti_kur(tmp_path)

    kod, cikti = _tt_cli(["--baslat", "--dosya", "Test Dosyası", "--kok", str(tmp_path)],
                          cwd=tmp_path)
    assert kod == 0, cikti
    assert (tmp_path / "_oa" / "analiz" / "dosya-analiz.json").exists()
    assert not tt_tamam_var_mi(tmp_path)  # yardımcı aşağıda

    kod, cikti = _pk_cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, f"--baslat sonrası (TAMAM YOK) Gate G bağımsız --denetle'de ENGEL vermeliydi:\n{cikti}"
    assert "Gate G" in cikti
    assert "ATLANDI" not in cikti  # bu çağrı gate_g_atla=True KULLANMAMALI


def tt_tamam_var_mi(tmp_path):
    yol = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    if not yol.is_file():
        return False
    return "oa:tam-tur:TAMAM" in yol.read_text(encoding="utf-8")


# ── P0-4 DÜZELTME — import çökerse istisna metni GÖRÜNÜR kalmalı ──────────
# Eski subprocess yolu istisnayı `({e})` ile raporluyordu; in-process
# sarmalayıcı bunu `except Exception: return None` ile YUTUYOR ve çağıran
# yalnız 'import edilemedi — kapı atlandı' basıyordu (tanı gücü azaldı). Bu
# test doğrudan `_tam_tur_modulu()`'nun import HATASINI kaybetmediğini,
# çıktıya bastığını doğrular.

def test_tam_tur_modulu_import_hatasi_metni_kaybetmez(monkeypatch, capsys):
    class _SahteHata(RuntimeError):
        pass

    def _patlayan_exec_module(mod):
        raise _SahteHata("kasıtlı-test-çöküşü")

    class _SahteLoader:
        create_module = staticmethod(lambda spec: None)
        exec_module = staticmethod(_patlayan_exec_module)

    gercek_spec_from_file = pk.importlib.util.spec_from_file_location

    def _sahte_spec(*a, **kw):
        spec = gercek_spec_from_file(*a, **kw)
        spec.loader = _SahteLoader()
        return spec

    monkeypatch.setattr(pk, "_TAM_TUR_MOD", None)
    monkeypatch.setattr(pk.importlib.util, "spec_from_file_location", _sahte_spec)

    sonuc = pk._tam_tur_modulu()
    assert sonuc is None

    cikti = capsys.readouterr().out
    assert "kasıtlı-test-çöküşü" in cikti, (
        "P0-4 REGRESYONU — import istisnasının metni ÇAĞIRANA taşınmıyor "
        f"(sessizce yutuluyor):\n{cikti}"
    )


# ── P0-4 DÜZELTME — tam_tur HİÇ kullanılmamış kökte 'ATLANDI' gürültüsü YOK ─
# `atla=True` kontrolü artık `dosya-analiz.json` varlık kontrolünün ARDINA
# alındı: tam_tur.py hiç kullanılmamış (dosya-analiz.json yok) bir kökte her
# `--kaydet` çağrısında gereksiz 'ATLANDI' notu basılmamalı — gerçek atlama
# yalnız tam_tur KULLANAN bir kökte (dosya-analiz.json varken) anlamlıdır.

def test_atla_true_ama_tam_tur_hic_kullanilmamis_kokte_sessiz(tmp_path):
    sorun, uyari = pk._gate_g_kalicilik_denetle(str(tmp_path), atla=True)
    assert sorun is None
    assert uyari is None, (
        "P0-4 REGRESYONU — dosya-analiz.json hiç yokken (tam_tur kullanılmamış "
        f"kök) atla=True yine de bir 'ATLANDI' notu üretti: {uyari}"
    )


def test_atla_true_tam_tur_kullanilan_kokte_atlandi_notu_verir(tmp_path):
    analiz_dizin = tmp_path / "_oa" / "analiz"
    analiz_dizin.mkdir(parents=True)
    (analiz_dizin / "dosya-analiz.json").write_text("{}", encoding="utf-8")
    sorun, uyari = pk._gate_g_kalicilik_denetle(str(tmp_path), atla=True)
    assert sorun is None
    assert uyari is not None and "ATLANDI" in uyari


# ── (4) atlama GÖRÜNÜR: ilk --kaydet çıktısında Gate G ATLANDI notu görünür ─

def test_ilk_kaydette_gate_g_atlandi_notu_gorunur(tmp_path):
    kod, cikti = _pk_cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    _tum_adim_katmanlari_isle(tmp_path)
    _kunye_ve_cikti_kur(tmp_path)
    _tt_cli(["--baslat", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)

    kod, cikti = _tt_cli(["--kaydet", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "Gate G" in cikti
    assert "ATLANDI" in cikti
