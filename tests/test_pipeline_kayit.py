# -*- coding: utf-8 -*-
"""oa-pipeline / pipeline_kayit.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
CLI çağrıları subprocess ile yapılır (main() argparse + sys.exit kullanıyor);
her test kendi tmp_path kökünü kullanarak izole çalışır.

Odak: append-only jsonl olay defteri + --denetle'nin BEKLİYOR/kanıtsız adımda
TESLİM ENGELİ (exit 1) vermesi — fiziksel işletim protokolünün garantörü.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
TAM_TUR_SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"


def _load():
    assert SCRIPT.is_file(), f"pipeline_kayit.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("pipeline_kayit", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ── --baslat sonra --denetle: hiç işlenmemiş adımlar BEKLİYOR → exit 1 ─────

def test_baslat_sonra_denetle_bekliyor_exit1(tmp_path):
    kod, _cikti = _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, "hiçbir adım işlenmemişken denetle TESLİM ENGELİ vermeli"
    assert "TESLİM ENGELİ" in cikti
    assert "statü YOK" in cikti or "BEKLIYOR" in cikti.upper() or "BEKLİYOR" in cikti


def test_defter_hic_acilmadan_denetle_hata(tmp_path):
    """--baslat hiç yapılmamışsa --denetle 'defter bulunamadı' ile durmalı."""
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0
    assert "defter bulunamadı" in cikti


def test_kanitsiz_uygulandi_reddedilir(tmp_path):
    """UYGULANDI statüsü kanıt olmadan (veya kısa kanıtla) yazılamaz — RET."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", "kısa", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "kanıtsız" in cikti.lower() or "RET" in cikti


def test_jsonl_append_only_iki_olay_ikisi_de_kalir(tmp_path):
    """Append-only garanti: iki ayrı --isle çağrısı defterde İKİ AYRI satır
    olarak kalmalı (eski satır silinmez/üzerine yazılmaz)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kanit_1 = "Skill çağrısı yapıldı; ictihat_ara 'istihkak muvazaa' 12.HD → 3 künye teyitli"
    kanit_2 = "oa-vakia scripti koşuldu; kronoloji + delil matrisi üretildi (12 kalem)"
    kod1, _c1 = _cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", kanit_1, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    kod2, _c2 = _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "UYGULANDI",
         "--kanit", kanit_2, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0 and kod2 == 0

    olaylar_yol = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    assert olaylar_yol.is_file()
    satirlar = [json.loads(s) for s in olaylar_yol.read_text(encoding="utf-8").splitlines() if s.strip()]
    # baslat + 2 x isle = en az 3 olay; İKİSİ de (adım 3 ve adım 4) korunmuş olmalı
    adimlar = [o.get("adim") for o in satirlar if o.get("tip") == "adim"]
    assert 3 in adimlar and 4 in adimlar, f"append-only olay defteri satır kaybetti: {satirlar}"


def test_tum_zorunlu_adimlar_uygulandi_ve_katmanlar_denetle_gecer(tmp_path):
    """Tüm adım/parça + tüm katmanlar UYGULANDI/GEREKSIZ statüsündeyse
    --denetle TEMİZ geçmeli (exit 0) — pozitif kontrast vaka."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    for no, (_ad, parcalar) in pk.ADIMLAR.items():
        for parca in parcalar:
            kod, cikti = _cli(
                ["--isle", "--adim", str(no), "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", uzun_kanit + " script", "--kok", str(tmp_path)],
                cwd=tmp_path,
            )
            assert kod == 0, f"adım {no}/{parca} işlenemedi: {cikti}"
    for katman in pk.KATMANLAR:
        kod, cikti = _cli(
            ["--katman", katman, "--durum", "UYGULANDI", "--kanit", uzun_kanit + " script",
             "--kok", str(tmp_path)],
            cwd=tmp_path,
        )
        assert kod == 0, f"katman {katman} işlenemedi: {cikti}"
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"tüm adım/katman işlenmişken denetle TEMİZ geçmeli:\n{cikti}"
    assert "DENETİM TEMİZ" in cikti


# ── D5 — SESSİZ-ARAÇ HATASI KAPISI: --arac-hata ────────────────────────────

def test_arac_hata_defter_acilmadan_reddedilir(tmp_path):
    """--baslat hiç yapılmamışsa --arac-hata da 'defter bulunamadı' ile durmalı
    (diğer --isle/--katman komutlarıyla AYNI ön-koşul — sessiz-atlama yasağı)."""
    kod, cikti = _cli(
        ["--arac-hata", "--arac", "ictihat_getir", "--hata", "MCP zaman aşımı",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "defter bulunamadı" in cikti


def test_arac_hata_hata_metni_zorunlu(tmp_path):
    """--hata verilmeden --arac-hata reddedilmeli."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--arac-hata", "--arac", "ictihat_getir", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0
    assert "--hata" in cikti


def test_arac_hata_kaydedilir_ve_goster_de_gorunur(tmp_path):
    """Bir araç çöküşü kaydedilince jsonl'e 'arac-hatasi' tipiyle İŞLENMELİ ve
    --goster çıktısında HER ZAMAN görünür olmalı — sessizce geçilmez (D5)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--arac-hata", "--arac", "ictihat_getir", "--sorgu", "12.HD 2023/1234",
         "--hata", "MCP zaman aşımı / araç erişilemedi", "--adim", "3",
         "--parca", "oa-ictihat", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, f"--arac-hata başarıyla kaydedilmeli:\n{cikti}"
    assert "ARAÇ ÇÖKTÜ" in cikti

    olaylar_yol = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    satirlar = [json.loads(s) for s in olaylar_yol.read_text(encoding="utf-8").splitlines() if s.strip()]
    arac_olaylari = [o for o in satirlar if o.get("tip") == "arac-hatasi"]
    assert len(arac_olaylari) == 1
    assert arac_olaylari[0]["arac"] == "ictihat_getir"
    assert arac_olaylari[0]["hata"] == "MCP zaman aşımı / araç erişilemedi"

    kod_g, cikti_g = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod_g == 0
    assert "ARAÇ ÇÖKTÜ" in cikti_g
    assert "ictihat_getir" in cikti_g


# ── Gate G — KALICILIK KAPISI: --denetle, tam_tur'un mekanik --durum'unu sorar ──

def _tum_adim_katmanlari_isle(tmp_path):
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    for no, (_ad, parcalar) in pk.ADIMLAR.items():
        for parca in parcalar:
            kod, cikti = _cli(
                ["--isle", "--adim", str(no), "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", uzun_kanit + " script", "--kok", str(tmp_path)],
                cwd=tmp_path,
            )
            assert kod == 0, f"adım {no}/{parca} işlenemedi: {cikti}"
    for katman in pk.KATMANLAR:
        kod, cikti = _cli(
            ["--katman", katman, "--durum", "UYGULANDI", "--kanit", uzun_kanit + " script",
             "--kok", str(tmp_path)],
            cwd=tmp_path,
        )
        assert kod == 0, f"katman {katman} işlenemedi: {cikti}"


def test_gate_g_tam_tur_kullanilmamissa_denetle_atlar(tmp_path):
    """tam_tur.py bu kökte HİÇ kullanılmamışsa (_oa/analiz/dosya-analiz.json yok)
    Gate G sessizce atlanmalı — mevcut tam_tur'suz akış bloklanmamalı (kontrast)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _tum_adim_katmanlari_isle(tmp_path)
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"tam_tur kullanılmayan akışta Gate G bloklamamalı:\n{cikti}"
    assert "Gate G" not in cikti
    assert "DENETİM TEMİZ" in cikti


def test_gate_g_analiz_md_eksikken_denetle_teslim_engeli(tmp_path):
    """tam_tur.py KULLANILMIŞ (dosya-analiz.json var) ama dosya-analiz.md fiziken
    YOKSA/eksikse — tüm defter adımları/katmanları temiz olsa bile --denetle
    Gate G nedeniyle TESLİM ENGELİ (exit 1) vermeli (model 'tamamlandı' diyemez)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _tum_adim_katmanlari_isle(tmp_path)

    # tam_tur'un "kullanılmış" olduğunu simüle et: durum.json TAMAM diyor ama
    # dosya-analiz.md fiziken hiç yazılmamış (Gate G'nin yakalaması gereken tam senaryo).
    analiz_dizin = tmp_path / "_oa" / "analiz"
    analiz_dizin.mkdir(parents=True, exist_ok=True)
    (analiz_dizin / "dosya-analiz.json").write_text(json.dumps({
        "dosya": "Test Dosyası", "tam_tur_durumu": "TAMAM",
        "tam_tur_tarihi": "2026-01-01 00:00",
        "kunye_snapshot": {"toplam_evrak": 0, "alindi": "2026-01-01 00:00",
                           "imzalar": {}, "gelisme_sayisi": 0},
        "gelismeler": [], "adim_ciktilari": [],
    }, ensure_ascii=False), encoding="utf-8")
    metin_dizin = tmp_path / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")

    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, f"dosya-analiz.md fiziken yokken Gate G TESLİM ENGELİ vermeliydi:\n{cikti}"
    assert "Gate G" in cikti
    assert "TESLİM ENGELİ" in cikti


def test_gate_g_tam_tur_tamamlandiginda_denetle_temiz_gecer(tmp_path):
    """tam_tur.py GERÇEKTEN --kaydet ile tamamlanmışsa (dosya-analiz.md fiziksel
    kanıtı taze) Gate G engellemez — pozitif kontrast vaka."""
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

    # tam_tur.py --baslat/--kaydet doğrudan tam_tur.py üzerinden çağrılır.
    r1 = subprocess.run([sys.executable, str(TAM_TUR_SCRIPT), "--baslat",
                         "--dosya", "Test Dosyası", "--kok", str(tmp_path)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r1.returncode == 0, r1.stdout + r1.stderr
    r2 = subprocess.run([sys.executable, str(TAM_TUR_SCRIPT), "--kaydet", "--kok", str(tmp_path)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r2.returncode == 0, r2.stdout + r2.stderr
    assert (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").exists()

    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _tum_adim_katmanlari_isle(tmp_path)
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"tam_tur GERÇEKTEN tamamlanmışken Gate G engellememeli:\n{cikti}"
    assert "DENETİM TEMİZ" in cikti


def test_arac_hata_denetle_uyari_verir_ama_tek_basina_bloklamaz(tmp_path):
    """Bir araç hatası --denetle çıktısında GÖRÜNÜR bir UYARI olarak basılmalı;
    ama diğer tüm adım/katmanlar temizse tek başına TESLİM ENGELİ (exit 1)
    üretmemeli — iş alternatif kaynak/yöntemle fiilen tamamlanmış olabilir."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    mod = pk
    for no, (_ad, parcalar) in mod.ADIMLAR.items():
        for parca in parcalar:
            _cli(
                ["--isle", "--adim", str(no), "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", uzun_kanit + " script", "--kok", str(tmp_path)],
                cwd=tmp_path,
            )
    for katman in mod.KATMANLAR:
        _cli(
            ["--katman", katman, "--durum", "UYGULANDI", "--kanit", uzun_kanit + " script",
             "--kok", str(tmp_path)],
            cwd=tmp_path,
        )
    kod_h, _c = _cli(
        ["--arac-hata", "--arac", "mevzuat_ara", "--hata", "araç erişilemedi",
         "--adim", "2", "--parca", "oa-alan", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod_h == 0

    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"araç hatası TEK BAŞINA teslim engeli üretmemeli:\n{cikti}"
    assert "ARAÇ ÇÖKTÜ" in cikti
    assert "mevzuat_ara" in cikti
