# -*- coding: utf-8 -*-
"""v0.5.16 / GRUP I5 — oa-sure AŞAMA TETİKLİ SÜRE SINIFI (P1-3 / A-10).

Saha gerekçesi: bazı usul "süreleri" takvimle değil, yargılamanın bir AŞAMASIYLA
kapanır — ilk itiraz cevap dilekçesiyle birlikte (HMK m.117/1), delil bildirimi
dilekçeler aşamasında (m.119/1-f, m.129/1-e; sonradan gösterme yasağı m.145),
ıslah tahkikat sona erene kadar (m.177/1), ön inceleme belge sunma ihtarı
(m.139/1-ç → m.140/5). Bunlar için "tebliğ + N gün" aritmetiği yoktur; tarih
üretmek YANLIŞ TARİH üretmektir. Ceza kolundaki katılma anı deseni (v0.5.13,
CMK m.237 — "olay tetikli kırmızı bayrak") hukuk koluna genellendi.

Tüm hukuki iddialar Mevzuat MCP'den teyitlidir (2026-09-06): HMK m.116, m.117,
m.119, m.129, m.139, m.140, m.145, m.177 · CMK m.237.

Kilitlenen mühendislik şartları:
  · aşama kuralı ile çağrılan hesapla_sure.py TARİH ARİTMETİĞİ YAPMAZ (exit 0,
    ">>> HESAPLANAN SON GÜN" satırı YOK; --teblig verilse bile).
  · `--json` → {"tur": "asama", ...}; son_gun alanı null.
  · `--pencereler` aşama kaydını GÖRÜNÜR atlar (sessiz değil), pencereye katmaz.
  · sure_nobetci.py aşama kayıtlarını AYRI blokta gösterir, tarih sayımına ve
    acil sınıfına KATMAZ; exit sözleşmesi (0/3/1) korunur.
  · JSON `asama_kurallari` ↔ gömülü `_GOMULU_ASAMA_KURALLAR` BİREBİR (ikiz
    tablo kilidi, B-21 deseni); tarih kuralları tablosu (21 kural) DEĞİŞMEDİ.
Testler tempfile ile izole dizinde koşar; depo dosyalarına yazmaz; ağ yok.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure"
HESAPLA = SKILL / "scripts" / "hesapla_sure.py"
NOBETCI = SKILL / "scripts" / "sure_nobetci.py"
KURAL_JSON = SKILL / "scripts" / "sure_kurallari.json"
SKILL_MD = SKILL / "SKILL.md"
CIZELGE = SKILL / "references" / "sure-cizelgesi.md"

ASAMA_KURALLARI = ("hmk_ilk_itiraz", "hmk_delil_bildirimi", "hmk_islah",
                   "hmk_on_inceleme_belge", "cmk_katilma")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("v0516_hesapla", HESAPLA)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _hesapla(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(HESAPLA)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or ""), cp.stdout or ""


def _nobetci(kok):
    cp = subprocess.run(
        [sys.executable, str(NOBETCI), "--kok", str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole_kok():
    return pathlib.Path(tempfile.mkdtemp())


def _defter_yaz(kok, kayitlar):
    oa = kok / "_oa"
    oa.mkdir(parents=True, exist_ok=True)
    (oa / "sureler.json").write_text(json.dumps(kayitlar, ensure_ascii=False),
                                     encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════
# 1) Kural tablosu — aşama kuralları (JSON + gömülü, ikiz kilit)
# ══════════════════════════════════════════════════════════════════════════

def test_asama_kurallari_json_ve_gomulu_BIREBIR(mod):
    """B-21 deseni: `asama_kurallari` JSON bölümü ↔ `_GOMULU_ASAMA_KURALLAR`
    anahtar, aşama, pipeline_adimi, kaynak ve teyit tarihi bakımından aynı."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["asama_kurallari"]
    g = mod._GOMULU_ASAMA_KURALLAR
    assert set(g) == set(j), (sorted(set(g) ^ set(j)))
    ayrisan = []
    for k in sorted(g):
        for alan in ("asama", "pipeline_adimi", "kaynak", "mcp_teyit_tarihi", "aciklama"):
            if g[k].get(alan) != j[k].get(alan):
                ayrisan.append(f"{k}.{alan}")
    assert not ayrisan, "İKİZ AŞAMA TABLOSU AYRIŞMASI: " + ", ".join(ayrisan)


def test_asama_kurallari_beklenen_kume_ve_alanlar(mod):
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["asama_kurallari"]
    assert set(j) == set(ASAMA_KURALLARI)
    for k, v in j.items():
        assert v.get("tur") == "asama", k
        assert "miktar" not in v and "birim" not in v, f"{k}: aşama kuralında miktar/birim OLMAZ"
        assert isinstance(v.get("pipeline_adimi"), int) and 0 <= v["pipeline_adimi"] <= 10, k
        assert v.get("asama", "").strip(), k
        assert "m." in v.get("kaynak", ""), f"{k}: kaynak madde çıpası taşımalı"
        assert v.get("mcp_teyit_tarihi"), f"{k}: MCP teyit tarihi BOŞ — teyitsiz kural eklenemez"


def test_tarih_kurallari_tablosu_degismedi_21_kural(mod):
    """Aşama sınıfı AYRI bölümde yaşar; 21 gün/hafta kuralı ve B-21 kilidi aynen."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    assert len(j) == 21 and len(mod._GOMULU_KURALLAR) == 21
    assert not (set(j) & set(ASAMA_KURALLARI))
    for k, v in j.items():
        assert v["birim"] in ("gun", "hafta"), k


def test_asama_kurallari_kural_seceneginde(mod):
    for k in ASAMA_KURALLARI:
        assert k in mod.ASAMA_KURALLAR
        assert k not in mod.KURALLAR


# ══════════════════════════════════════════════════════════════════════════
# 2) hesapla_sure.py — aşama kuralı TARİH ARİTMETİĞİ YAPMAZ
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("kural", ASAMA_KURALLARI)
def test_asama_kurali_tarih_uretmez_exit0(kural, tmp_path):
    kod, metin, _ = _hesapla(["--kural", kural, "--flagsiz"], tmp_path)
    assert kod == 0, metin
    assert "AŞAMA TETİKLİ" in metin, metin
    assert "tarih yok" in metin.lower(), metin
    assert "pipeline adım" in metin.lower(), metin
    assert "HESAPLANAN SON GÜN" not in metin, "aşama kuralı tarih üretti:\n" + metin


def test_asama_kurali_teblig_verilse_bile_tarih_uretmez(tmp_path):
    """Yanlış tarih üretme yasağı: --teblig girilse de aritmetik yapılmaz, girdi
    görünür şekilde 'kullanılmadı' diye raporlanır."""
    kod, metin, _ = _hesapla(["--kural", "hmk_islah", "--teblig", "2026-05-20", "--flagsiz"],
                             tmp_path)
    assert kod == 0, metin
    assert "HESAPLANAN SON GÜN" not in metin
    assert "2026-06-03" not in metin and "2026-05-21" not in metin
    assert "kullanılmadı" in metin.lower() or "kullanılmaz" in metin.lower(), metin


def test_asama_kurali_json_ciktisi(tmp_path):
    kod, metin, stdout = _hesapla(["--kural", "hmk_ilk_itiraz", "--flagsiz", "--json"], tmp_path)
    assert kod == 0, metin
    veri = json.loads(stdout)
    assert veri["tur"] == "asama"
    assert veri["kural"] == "hmk_ilk_itiraz"
    assert veri["son_gun"] is None
    assert isinstance(veri["pipeline_adimi"], int)
    assert "m.117" in veri["kaynak"]
    assert veri["mcp_teyit_tarihi"]


def test_asama_kurali_yargi_kolu_uyusmazligi_bloklamaz(tmp_path):
    """A-1 kol uyuşmazlığı ADLİ TATİL rejimi içindir; aşama kuralında tatil
    aritmetiği olmadığından cmk_katilma --yargi hukuk ile de DURMAZ (uyarır)."""
    kod, metin, _ = _hesapla(["--kural", "cmk_katilma", "--flagsiz"], tmp_path)
    assert kod == 0, metin
    assert "AŞAMA TETİKLİ" in metin


def test_tarih_kurali_json_ciktisi_geriye_uyum(tmp_path):
    """--json tarih kuralında da çalışır (son blok); insan-okur rapor korunur."""
    kod, metin, stdout = _hesapla(["--teblig", "2026-05-20", "--kural", "hmk_istinaf",
                                   "--flagsiz", "--json"], tmp_path)
    assert kod == 0, metin
    assert "HESAPLANAN SON GÜN" in metin
    satir = [s for s in stdout.splitlines() if s.startswith("[JSON] ")]
    assert satir, "tarih kuralında --json satırı yok"
    veri = json.loads(satir[-1][len("[JSON] "):])
    assert veri["tur"] == "usul" and veri["son_gun"] == "2026-06-03"


def test_asama_kurali_deftere_son_gunsuz_kayit_yazar(tmp_path):
    """E4a süre bağı aşama için: `_oa` varsa {"tur":"asama","asama","pipeline_adimi",
    "aciklama","kural"} kaydı yazılır — son_gun/tarih alanı YOK. İkinci koşu çoğaltmaz."""
    (tmp_path / "_oa").mkdir()
    for _ in range(2):
        kod, metin, _ = _hesapla(["--kural", "hmk_delil_bildirimi", "--kok", str(tmp_path)],
                                 tmp_path)
        assert kod == 0, metin
    d = json.loads((tmp_path / "_oa" / "sureler.json").read_text(encoding="utf-8"))
    kayitlar = [f for f in d["flagler"] if f.get("tur") == "asama"]
    assert len(kayitlar) == 1, kayitlar
    k = kayitlar[0]
    assert "son_gun" not in k and "tarih" not in k
    assert k["kural"] == "hmk_delil_bildirimi" and k["asama"] and k["aciklama"]
    assert isinstance(k["pipeline_adimi"], int)


def test_asama_kurali_oa_yoksa_defter_icat_etmez(tmp_path):
    kod, metin, _ = _hesapla(["--kural", "hmk_islah", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, metin
    assert not (tmp_path / "_oa").exists()


# ══════════════════════════════════════════════════════════════════════════
# 3) --pencereler — aşama kaydı GÖRÜNÜR atlanır, pencereye katılmaz
# ══════════════════════════════════════════════════════════════════════════

def test_pencereler_asama_kaydini_gorunur_atlar(tmp_path):
    yol = tmp_path / "p.json"
    yol.write_text(json.dumps([
        {"ad": "İstinaf", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
        {"ad": "Cevap", "teblig": "2026-05-25", "kural": "hmk_cevap"},
        {"ad": "İlk itiraz", "kural": "hmk_ilk_itiraz"},
    ], ensure_ascii=False), encoding="utf-8")
    cikti = tmp_path / "p_out.json"
    kod, metin, _ = _hesapla(["--pencereler", str(yol), "--pencereler-json", str(cikti)], tmp_path)
    assert kod == 0, metin
    assert "İlk itiraz" in metin and "AŞAMA TETİKLİ" in metin, metin
    veri = json.loads(cikti.read_text(encoding="utf-8"))
    assert [p["ad"] for p in veri["pencereler"]] == ["İstinaf", "Cevap"]
    assert veri["asama"] and veri["asama"][0]["ad"] == "İlk itiraz"
    assert veri["denetlenen_kayit"] == 2


def test_pencereler_yalniz_asama_ise_denetlenemedi(tmp_path):
    yol = tmp_path / "p.json"
    yol.write_text(json.dumps([{"ad": "Islah", "kural": "hmk_islah"}]), encoding="utf-8")
    kod, metin, _ = _hesapla(["--pencereler", str(yol)], tmp_path)
    assert kod == 1, metin
    assert "DENETLENEMEDİ" in metin and "aşama" in metin.lower()


# ══════════════════════════════════════════════════════════════════════════
# 4) sure_nobetci.py — ayrı blok, sayılmaz, exit sözleşmesi korunur
# ══════════════════════════════════════════════════════════════════════════

def _asama_kaydi():
    return {"tur": "asama", "asama": "cevap dilekçesi", "pipeline_adimi": 8,
            "aciklama": "İlk itirazlar cevap dilekçesiyle birlikte (HMK m.117/1)",
            "kural": "hmk_ilk_itiraz"}


def test_nobetci_asama_ayri_blok_ve_exit0(izole_kok):
    ileri = (date.today() + timedelta(days=120)).isoformat()
    _defter_yaz(izole_kok, {"flagler": [
        {"son_gun": ileri, "aciklama": "Ileri sure - istinaf", "tur": "usul"},
        _asama_kaydi(),
    ]})
    kod, cikti = _nobetci(izole_kok)
    assert kod == 0, cikti
    assert "[≡]" in cikti and "AŞAMA TETİKLİ" in cikti, cikti
    assert "adım 8 tamamlanmadan" in cikti, cikti
    assert "0 GEÇMİŞ" in cikti and "1 İLERİ" in cikti
    assert "BOZUK" not in cikti, "aşama kaydı bozuk sayıldı:\n" + cikti
    assert "aşama tetikli" in cikti.lower()


def test_nobetci_asama_acil_sinifina_katilmaz_ama_gecmis_exit3_korunur(izole_kok):
    gecmis = (date.today() - timedelta(days=2)).isoformat()
    _defter_yaz(izole_kok, [
        {"son_gun": gecmis, "aciklama": "Gecmis sure - temyiz", "tur": "usul"},
        _asama_kaydi(),
    ])
    kod, cikti = _nobetci(izole_kok)
    assert kod == 3, cikti
    assert "1 GEÇMİŞ" in cikti
    assert "DİKKAT: 1 geçmiş" in cikti, cikti   # aşama sayıya girmedi


def test_nobetci_yalniz_asama_kaydi_exit0(izole_kok):
    _defter_yaz(izole_kok, [_asama_kaydi()])
    kod, cikti = _nobetci(izole_kok)
    assert kod == 0, cikti
    assert "AŞAMA TETİKLİ" in cikti


def test_nobetci_asama_iptal_edilebilir(izole_kok):
    """Append-only iptal rejimi aşama kaydına da uygulanır; kapatılan aşama
    nöbet dışına düşer."""
    k = _asama_kaydi(); k["id"] = "asm1"
    _defter_yaz(izole_kok, [k, {"iptal_eder": "asm1", "gerekce": "cevap verildi"}])
    kod, cikti = _nobetci(izole_kok)
    assert kod == 0, cikti
    assert "[≡]" not in cikti
    assert "İPTAL/DÜZELTİLDİ" in cikti


def test_nobetci_tarihsiz_ama_asamasiz_kayit_hala_bozuk(izole_kok):
    """Geriye uyum: tur alanı olmayan tarihsiz kayıt yine BOZUK sınıfındadır
    (aşama sınıfı ancak açık `tur: asama` ile tanınır — fail-closed)."""
    _defter_yaz(izole_kok, [{"aciklama": "tarihsiz eski kayıt"}])
    kod, cikti = _nobetci(izole_kok)
    assert kod == 3
    assert "BOZUK" in cikti


# ══════════════════════════════════════════════════════════════════════════
# 5) Talimat katmanı — SKILL.md / çizelge
# ══════════════════════════════════════════════════════════════════════════

def test_skill_md_asama_bolumu():
    md = SKILL_MD.read_text(encoding="utf-8")
    assert "AŞAMA TETİKLİ SÜRELER" in md
    for k in ASAMA_KURALLARI:
        assert k in md, f"{k} SKILL.md tablosunda yok"
    for alan in ("pipeline_adimi", "asama", "aciklama", "\"tur\"", "son_gun"):
        assert alan in md, alan
    assert "m.237" in md and "katılma" in md.lower()   # ceza deseniyle ilişki
    assert "sure-flag" in md


def test_cizelge_asama_capalari():
    md = CIZELGE.read_text(encoding="utf-8")
    for capa in ("m.117", "m.145", "m.177", "m.139"):
        assert capa in md, capa
