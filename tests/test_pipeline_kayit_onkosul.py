# -*- coding: utf-8 -*-
"""P0-6 (v0.5.5) — KADEMELİ ÖNKOŞUL-ARTEFAKT KAPISI testleri.

BLOKLEYİCİ küme: adım-5 (oa-kiyas: 05-kiyas* AND *ictihat-muhakeme*) + adım-9
(oa-kontrol: teslim-makbuz.json). UYARI kümesi: adım-3/4/6/7 (bloklamaz).
İNGEST-ÖNCE: adım 1+ UYGULANDI, 00-kunye.json diskte yoksa yazılamaz.
--serh: gerekçeli (>=30 kr) geçiş — olay 'serh:true' ile işlenir.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _baslat(tmp_path):
    kod, cikti = _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti


def _kunye_kur(tmp_path):
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


# ── İNGEST-ÖNCE ──────────────────────────────────────────────────────────

def test_ingest_once_00_kunye_yoksa_adim1_reddedilir(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "1", "--parca", "oa-interview", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "İNGEST-ÖNCE" in cikti


def test_ingest_once_00_kunye_varsa_adim1_gecer(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "1", "--parca", "oa-interview", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_ingest_once_adim0_muaf(tmp_path):
    """Adım 0 (MANİFEST) İNGEST-ÖNCE kapsamı DIŞINDA (adım 1+)."""
    _baslat(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_ingest_once_gereksiz_statusu_serbest(tmp_path):
    """GEREKSIZ statüsü İNGEST-ÖNCE kapısından muaf (yalnız UYGULANDI'da devrede)."""
    _baslat(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "1", "--parca", "oa-interview", "--durum", "GEREKSIZ",
         "--gerekce", "bu dosyada mülakat adımı gereksiz.", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


# ── BLOKLEYİCİ — adım-5 (oa-kiyas) ──────────────────────────────────────

def test_adim5_muhakeme_dosyasiz_reddedilir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "adım-5" in cikti or "05-kiyas" in cikti


def test_adim5_yalniz_muhakeme_dosyasi_varken_hala_reddedilir(tmp_path):
    """DÜZELTME: 05-kiyas* AND *ictihat-muhakeme* — biri TEK BAŞINA yetmez."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text(
        "Muhakeme gövdesi " * 10, encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, "yalnız muhakeme dosyası varken (05-kiyas* yokken) geçmemeliydi"


def test_adim5_her_iki_artefakt_varken_gecer(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "05-kiyas-test.md").write_text("Kıyas gövdesi " * 10, encoding="utf-8")
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text(
        "Muhakeme gövdesi " * 10, encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_adim5_bos_iskelet_dosya_yeterli_sayilmaz(tmp_path):
    """Min gövde eşiği: neredeyse boş bir dosya 'sağlam artefakt' sayılmaz."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "05-kiyas-bos.md").write_text("x", encoding="utf-8")
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text("y", encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, "boş/iskelet dosyalar sağlam artefakt sayılmamalıydı"


def test_adim5_gereksiz_gerekceli_serbest(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "GEREKSIZ",
         "--gerekce", "bu dosyada kıyas adımı gereksiz (tek taraflı beyan davası).",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


# ── ÇAPRAZ-ADIM — adım-8 (oa-dilekce) ∧ adım-5 (oa-kiyas) ───────────────

def test_adim8_yazim_adim5_bekliyorken_reddedilir(tmp_path):
    """adım-5 (KIYAS) hiç değerlendirilmeden (BEKLIYOR) adım-8 (YAZIM)
    UYGULANDI yazılamaz — saha bulgusu: kıyas atlanıp doğrudan yazıma geçiş."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "8", "--parca", "oa-dilekce", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "adım-5" in cikti or "adım-8" in cikti


def test_adim8_yazim_adim5_gereksizken_gecer(tmp_path):
    """adım-5 GEREKSİZ (gerekçeli) denmişse — bilinçli bir karar var demektir,
    adım-8 engellenmez."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod5, cikti5 = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "GEREKSIZ",
         "--gerekce", "bu dosyada kıyas adımı gereksiz (tek taraflı beyan davası).",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod5 == 0, cikti5
    kod8, cikti8 = _cli(
        ["--isle", "--adim", "8", "--parca", "oa-dilekce", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod8 == 0, cikti8


def test_adim8_yazim_adim5_uygulandiyken_gecer(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "05-kiyas-test.md").write_text("Kıyas gövdesi " * 10, encoding="utf-8")
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text(
        "Muhakeme gövdesi " * 10, encoding="utf-8")
    kod5, cikti5 = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod5 == 0, cikti5
    kod8, cikti8 = _cli(
        ["--isle", "--adim", "8", "--parca", "oa-dilekce", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod8 == 0, cikti8


def test_adim8_serh_ile_gecer(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    gerekce = "Adım-5 bu dosyada bilinçli olarak atlanıyor, avukat elle inceledi."
    kod, cikti = _cli(
        ["--isle", "--adim", "8", "--parca", "oa-dilekce", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--serh", gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "ŞERHLİ UYGULANDI" in cikti


# ── BLOKLEYİCİ — adım-9 (oa-kontrol) ────────────────────────────────────

def test_adim9_makbuzsuz_reddedilir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "teslim-makbuz.json" in cikti


def test_adim9_gecerli_makbuzla_gecer(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti


def test_adim9_red_makbuzla_reddedilir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 1}), encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0


# ── UYARI kümesi (bloklamaz) — adım-4 örneği ────────────────────────────

def test_adim4_vakia_yokken_yalniz_uyari_exit0(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, f"UYARI kümesi bloklamamalı:\n{cikti}"
    assert "UYARI" in cikti
    assert "04-vakia" in cikti


def test_adim3_arastirma_izsizken_yalniz_uyari_exit0(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0
    assert "UYARI" in cikti


def test_adim3_kutuk_varsa_uyari_basilmaz(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    teyit = tmp_path / "_oa" / "teyit"
    teyit.mkdir(parents=True, exist_ok=True)
    (teyit / "kunye-teyit.md").write_text("| Zaman | Araç | ... |\n", encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0
    assert "adım-3" not in cikti


# ── --serh gerekçeli geçiş ───────────────────────────────────────────────

def test_serh_kisa_gerekce_reddedilir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--serh", "kısa", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, "kısa --serh gerekçesi ile geçilmemeliydi"


def test_serh_gecerli_gerekceyle_gecer_ve_goster_serhli_isaretler(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    gerekce = "Bu dosyada kıyas adımı tek taraflı/basit alacak davası olduğu için atlanıyor."
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--serh", gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "ŞERHLİ UYGULANDI" in cikti

    kod_g, cikti_g = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod_g == 0
    assert "ŞERHLİ UYGULANDI" in cikti_g


def test_serh_denetle_de_de_gorunur(tmp_path):
    """Sinav-turu KUCUK-düzeltme: `--goster` ŞERHLİ UYGULANDI'yı zaten
    basıyordu ama `--denetle` (ve dolayısıyla teslim_paketi'nin (d) kapısı +
    _oa/DURUM.md) bunu görmüyordu — bir ŞERH ile atlanmış önkoşul en kritik
    tüketicide (--denetle) sessiz kalıyordu. Bu artık düzeltilmiştir."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    gerekce = "Bu dosyada kıyas adımı tek taraflı/basit alacak davası olduğu için atlanıyor."
    kod, _cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--serh", gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0

    # --denetle diğer BEKLIYOR adım/katmanlar yüzünden exit 1 dönebilir; burada
    # sadece ŞERHLİ satırının GÖRÜNÜR olup olmadığı denetleniyor.
    _kod_d, cikti_d = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "ŞERHLİ UYGULANDI" in cikti_d, f"--denetle şerhi göstermeliydi:\n{cikti_d}"

    durum_md = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "ŞERHLİ" in durum_md


def test_serh_olayi_jsonlde_serh_true_ile_iselnir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    gerekce = "Bu dosyada kıyas adımı tek taraflı/basit alacak davası olduğu için atlanıyor."
    _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--serh", gerekce, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    olaylar_yol = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    satirlar = [json.loads(s) for s in olaylar_yol.read_text(encoding="utf-8").splitlines() if s.strip()]
    adim5 = [o for o in satirlar if o.get("tip") == "adim" and o.get("adim") == 5]
    assert adim5 and adim5[-1].get("serh") is True


# ── Geriye uyum — eski (surum/serh alansız) jsonl satırları ─────────────

def test_eski_jsonl_surum_alansiz_satir_okunur(tmp_path):
    """Eski (P0-5 öncesi) jsonl satırları 'surum' alanı taşımaz — derle()
    bunu .get() ile okur, çökme/yanlış davranış üretmemeli."""
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    olaylar = defter / "pipeline-olaylar.jsonl"
    olaylar.write_text(
        json.dumps({"zaman": "2026-01-01T00:00:00", "tip": "baslat",
                    "dosya": "Eski Dosya", "ceza_dali": None}, ensure_ascii=False) + "\n"
        + json.dumps({"zaman": "2026-01-01T00:01:00", "tip": "adim", "adim": 0,
                      "parca": "manifest", "durum": "UYGULANDI",
                      "kanit": UZUN_KANIT}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "Eski Dosya" in cikti
