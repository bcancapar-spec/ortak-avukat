# -*- coding: utf-8 -*-
"""T12 + T13 (v0.5.9) — çift-kanal hook dedup + oran ölçüm aracı testleri.

T12 — ÇİFT-KANAL DEDUP: plugin `hooks/hooks.json` VE kullanıcı
`settings.json` AYNI olayı iki kez kaydettirmiş olabilir; aynı olay AYNI
SANİYE içinde ikinci kez çağrıldığında hook gövdesi YAN-ETKİSİZ kısa devre
yapar (çıktı yok, defter olayı yok). Farklı saniye ve farklı olay
ETKİLENMEZ. Damga `.hook-son-iz.json` içinde `"_dedup": {olay: epoch_ms}`
alanında yaşar — mevcut nabız şeması (olay-başına ISO damga + hash)
KORUNUR.

T13 — ORAN BEKÇİSİ: `tools/oran_olc.py` deterministik ölçüm — pay
(mekanizma satırları: plugins/**/scripts/*.py + tools/*.py + hooks/*,
TEST HARİÇ) / payda (plugins/**/*.md). Kapı YOK (anayasa kararı) —
yalnız ölçüm + `--kaydet` ile append-only defter.

Testlerde gerçek dava adı/yolu YOKTUR — her şey sentetik tmp ağaçlarında.
"""
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PIPELINE_KAYIT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
                  / "scripts" / "pipeline_kayit.py")
ORAN_OLC = REPO / "tools" / "oran_olc.py"


def _modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pk():
    return _modul(PIPELINE_KAYIT, "pk_v059_dedup_test")


@pytest.fixture(scope="module")
def oran():
    return _modul(ORAN_OLC, "oran_olc_v059_test")


@pytest.fixture()
def dava_kok(tmp_path):
    """Sentetik dava klasörü: `_oa/defter` var → hat açık, nabız/dedup
    damgaları yazılabilir."""
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    return str(tmp_path)


def _iz_oku(dava_kok):
    yol = pathlib.Path(dava_kok) / "_oa" / "defter" / ".hook-son-iz.json"
    if not yol.is_file():
        return {}
    return json.loads(yol.read_text(encoding="utf-8"))


def _olay_sayisi(dava_kok):
    yol = pathlib.Path(dava_kok) / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    if not yol.is_file():
        return 0
    return len([s for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()])


# ═══ T12 — ÇİFT-KANAL DEDUP ════════════════════════════════════════════════

def test_dedup_ayni_saniye_ikinci_cagri_kisa_devre(pk, dava_kok, monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is False  # ilk çağrı geçer
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is True   # aynı saniye → kısa devre
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is True   # üçüncü de kısa devre


def test_dedup_farkli_saniye_normal(pk, dava_kok, monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.900)
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is False
    monkeypatch.setattr("time.time", lambda: 1_700_000_002.100)
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is False  # meşru ardışık tur


def test_dedup_farkli_olay_etkilenmez(pk, dava_kok, monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is False
    assert pk._hook_dedup_kisa_devre(dava_kok, "denetle") is False  # farklı olay geçer
    assert pk._hook_dedup_kisa_devre(dava_kok, "acilis") is False


def test_dedup_ayirt_edici_farkli_payload_gecer(pk, dava_kok, monkeypatch):
    """pretool/postwrite güvenlik istisnası: AYNI saniyede FARKLI payload'lı
    iki meşru araç çağrısı (paralel Write/Bash) birbirini SUSTURMAZ — ayırt
    edici (payload parmak izi) anahtarın parçasıdır. Aynı payload (çift
    kanal kopyası) yine kısa devre."""
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk._hook_dedup_kisa_devre(dava_kok, "pretool", ayirt="aaaa1111") is False
    assert pk._hook_dedup_kisa_devre(dava_kok, "pretool", ayirt="bbbb2222") is False
    assert pk._hook_dedup_kisa_devre(dava_kok, "pretool", ayirt="aaaa1111") is True


def test_dedup_defter_yoksa_hep_gecer(pk, tmp_path, monkeypatch):
    """Defter yoksa damga yazılamaz (dosya defterde yaşar) — dedup devre
    dışıdır, gövde normal akar (mevcut nabız sözleşmesiyle simetrik)."""
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    kok = str(tmp_path)  # _oa/defter YOK
    assert pk._hook_dedup_kisa_devre(kok, "prompt") is False
    assert pk._hook_dedup_kisa_devre(kok, "prompt") is False


def test_dedup_nabiz_semasi_korunur(pk, dava_kok, monkeypatch):
    """`.hook-son-iz.json` MERGE edilir: mevcut hash + olay-başına ISO nabız
    damgaları silinmez; `_dedup` yalnız EK alandır."""
    iz_yolu = pathlib.Path(dava_kok) / "_oa" / "defter" / ".hook-son-iz.json"
    iz_yolu.write_text(json.dumps({"hash": "abc123", "prompt": "2026-01-01T00:00:00"}),
                       encoding="utf-8")
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is False
    veri = _iz_oku(dava_kok)
    assert veri.get("hash") == "abc123"
    assert veri.get("prompt") == "2026-01-01T00:00:00"
    assert isinstance(veri.get("_dedup"), dict)
    assert veri["_dedup"].get("prompt") == 1_700_000_000_200


def test_dedup_bozuk_iz_dosyasi_hata_yutulur(pk, dava_kok, monkeypatch):
    iz_yolu = pathlib.Path(dava_kok) / "_oa" / "defter" / ".hook-son-iz.json"
    iz_yolu.write_text("{BOZUK json", encoding="utf-8")
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk._hook_dedup_kisa_devre(dava_kok, "prompt") is False  # fırlatmaz


def test_hook_acilis_ayni_saniye_ikinci_cagri_sessiz(pk, dava_kok, capsys, monkeypatch):
    """Uçtan uca: çift kanal SessionStart'ı aynı saniyede iki kez koşturursa
    ikinci koşu SESSİZ (stdout boş) ve defter olay sayısı ARTMAZ."""
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk.hook_acilis(dava_kok) == 0
    ilk = capsys.readouterr().out
    assert "AÇILIŞ ENVANTERİ" in ilk
    sayi_ilk = _olay_sayisi(dava_kok)
    assert sayi_ilk >= 1
    assert pk.hook_acilis(dava_kok) == 0                 # aynı saniye — çift kanal
    ikinci = capsys.readouterr().out
    assert ikinci == ""                                   # çıktı basılmadı
    assert _olay_sayisi(dava_kok) == sayi_ilk             # defter olayı yazılmadı


def test_hook_acilis_farkli_saniye_normal_kosar(pk, dava_kok, capsys, monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1_700_000_000.200)
    assert pk.hook_acilis(dava_kok) == 0
    capsys.readouterr()
    monkeypatch.setattr("time.time", lambda: 1_700_000_005.000)
    assert pk.hook_acilis(dava_kok) == 0
    assert "AÇILIŞ ENVANTERİ" in capsys.readouterr().out


def test_denetle_ayirt_durum_degisince_farkli_iz(pk, dava_kok):
    """`denetle` dedup'u durum-körü DEĞİLDİR: parmak izi `_oa/cikti`ya yeni
    dosya yazılınca DA defterdeki gerçek değişiklikte DE (--isle olayı)
    değişir — aynı saniyede bile denetim koşar (Paket-B atlatma-tespiti
    yaşar). Hiçbir şey değişmeyince sabittir; denetle'nin KENDİ yazdığı
    `.hook-son-iz.json` bağışıktır (dahil olsa dedup ölü kod olurdu)."""
    iz1 = pk._hook_denetle_ayirt(dava_kok)
    assert iz1 == pk._hook_denetle_ayirt(dava_kok)        # değişiklik yok → sabit
    # kendi-yazımı bağışıklığı: .hook-son-iz.json izi DEĞİŞTİRMEZ
    (pathlib.Path(dava_kok) / "_oa" / "defter" / ".hook-son-iz.json").write_text(
        json.dumps({"prompt": "2026-01-01T00:00:00"}), encoding="utf-8")
    assert pk._hook_denetle_ayirt(dava_kok) == iz1
    # defterdeki GERÇEK değişiklik (olay defteri) → iz DEĞİŞİR
    (pathlib.Path(dava_kok) / "_oa" / "defter" / "pipeline-olaylar.jsonl").write_text(
        '{"tip": "olay"}\n', encoding="utf-8")
    iz2 = pk._hook_denetle_ayirt(dava_kok)
    assert iz2 != iz1
    # cikti'ya dilekçe-şekilli dosya → iz yine DEĞİŞİR
    cikti = pathlib.Path(dava_kok) / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "08-taslak.md").write_text("SONUÇ VE İSTEM\n", encoding="utf-8")
    assert pk._hook_denetle_ayirt(dava_kok) != iz2


# ═══ T13 — ORAN ÖLÇÜM ARACI ════════════════════════════════════════════════

def _yaz(yol, satir_sayisi):
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text("".join(f"satir {i}\n" for i in range(satir_sayisi)),
                   encoding="utf-8")


@pytest.fixture()
def sentetik_kok(tmp_path):
    """Mini ağaç — beklenen sayım:
    PAY (mekanizma): scripts/a.py(3) + tools/b.py(2) + plugins hooks(2)
                     + kök hooks(1) = 8   [scripts/test_z.py(10) TEST → HARİÇ]
    PAYDA (öğreti):  SKILL.md(4) + references/r.md(2) = 6
    TEST:            tests/test_c.py(5) + scripts/test_z.py(10) = 15
    """
    k = tmp_path
    _yaz(k / "plugins" / "px" / "skills" / "sy" / "scripts" / "a.py", 3)
    _yaz(k / "plugins" / "px" / "skills" / "sy" / "scripts" / "test_z.py", 10)
    _yaz(k / "tools" / "b.py", 2)
    _yaz(k / "plugins" / "px" / "hooks" / "hooks.json", 2)
    _yaz(k / "hooks" / "run-hook.cmd", 1)
    _yaz(k / "plugins" / "px" / "skills" / "sy" / "SKILL.md", 4)
    _yaz(k / "plugins" / "px" / "skills" / "sy" / "references" / "r.md", 2)
    _yaz(k / "tests" / "test_c.py", 5)
    return str(k)


def test_oran_olc_dogru_sayim(oran, sentetik_kok):
    o = oran.olc(sentetik_kok)
    assert o["pay"] == 8
    assert o["payda"] == 6
    assert o["oran"] == round(8 / 6, 4)
    assert o["test_satir"] == 15
    assert o["test_mekanizma_orani"] == round(15 / 8, 4)
    assert "tarih" in o and "commit" in o


def test_oran_olc_test_haric_kaniti(oran, sentetik_kok):
    """scripts altına düşen test dosyası PAY'a girmez: 10 satırlık
    test_z.py silinince pay DEĞİŞMEZ, test_satir düşer."""
    once = oran.olc(sentetik_kok)
    (pathlib.Path(sentetik_kok) / "plugins" / "px" / "skills" / "sy"
     / "scripts" / "test_z.py").unlink()
    sonra = oran.olc(sentetik_kok)
    assert sonra["pay"] == once["pay"] == 8
    assert sonra["test_satir"] == 5


def test_oran_kaydet_append_only(oran, sentetik_kok):
    o1 = oran.olc(sentetik_kok)
    defter_yolu = oran.kaydet(sentetik_kok, o1)
    kayitlar = json.loads(pathlib.Path(defter_yolu).read_text(encoding="utf-8"))
    assert isinstance(kayitlar, list) and len(kayitlar) == 1
    o2 = oran.olc(sentetik_kok)
    oran.kaydet(sentetik_kok, o2)
    kayitlar2 = json.loads(pathlib.Path(defter_yolu).read_text(encoding="utf-8"))
    assert len(kayitlar2) == 2
    assert kayitlar2[0] == kayitlar[0]        # append-only: ilk kayıt bit-bit korunur


def test_oran_defteri_gercek_agacta_taban_kaydi_var():
    """İlk kayıt = mevcut ağacın ölçümü (taban) — depo içinde durur."""
    defter = (REPO / "plugins" / "ortak-avukat" / "skills" / "ortak-avukat"
              / "references" / "oran-defteri.json")
    assert defter.is_file(), f"taban kaydı yok: {defter}"
    kayitlar = json.loads(defter.read_text(encoding="utf-8"))
    assert isinstance(kayitlar, list) and len(kayitlar) >= 1
    for alan in ("pay", "payda", "oran", "tarih", "commit"):
        assert alan in kayitlar[0]
    assert kayitlar[0]["pay"] > 0 and kayitlar[0]["payda"] > 0
