# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — DELİL / TANIK / ZABIT kapıları:
oa-vakia/scripts/delil_plani.py, oa-vakia/scripts/tanik_plani.py,
oa-antitez/scripts/zapt_denetim.py

Fikir kaynağı Yargı PRO 16-4 (delil toplama planı), 16-3 (tanık soruları),
16-2 (duruşma zaptı denetimi) — kod/metin ALINMADI. Saha gerekçesi: ispat
boşluğu analizde "eksik" yazılıp dilekçede "sair deliller"e dönüşüyor; tanık
cevabı yazdırmak TCK m.272/m.277 riskidir; zapta geçmeyen talep ispat
edilemez (HMK m.156).

Resmî metin teyidi (Yargı PRO MCP mevzuat_getir, 2026-10-05): HMK m.145, 152,
154, 156, 190, 240, 243, 255, 259, 261, 324, 400; CMK m.201; TCK m.272, 277.
Tutanak düzeltme süresi HMK m.154-158'de yok → TEYİT BEKLİYOR (test kilitler).

Tüm veriler kurgu; matris girdisi gerçek vakia_matris.py ile tmp_path'te
üretilir (entegrasyon). Ağsız, deterministik; bugünün tarihine bağlı değil.
"""
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
VAKIA = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
DELIL = SKILLS / "oa-vakia" / "scripts" / "delil_plani.py"
TANIK = SKILLS / "oa-vakia" / "scripts" / "tanik_plani.py"
ZAPT = SKILLS / "oa-antitez" / "scripts" / "zapt_denetim.py"


def _kos(script, *args, cwd=None):
    cp = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(cwd or REPO))
    return cp.returncode, cp.stdout


def _yaz(yol, veri):
    yol.write_text(json.dumps(veri, ensure_ascii=False) if not isinstance(veri, str) else veri, encoding="utf-8")
    return str(yol)


VAKIA_GIRDI = {
    "iddialar": [{"id": "I1", "metin": "Mal kurgu tarihte teslim edildi", "tur": "vakia"},
                 {"id": "I2", "metin": "Davalı ayıbı süresinde bildirmedi", "tur": "vakia"},
                 {"id": "I3", "metin": "Sözleşme eser sözleşmesidir", "tur": "hukuki"}],
    "olaylar": [{"tarih": "2025-03-12", "olgu": "Teslim", "belge": "İrsaliye (kurgu)", "destekler": ["I1"],
                 "ispat_durumu": "belgeli"},
                {"tarih": "2025-04-01", "olgu": "Tanık gördü", "belge": "Tanık T1 beyanı (kurgu)",
                 "destekler": ["I2"], "ispat_durumu": "tanik"}],
}


@pytest.fixture
def matris(tmp_path):
    giris = _yaz(tmp_path / "04-vakia.json", VAKIA_GIRDI)
    cikis = tmp_path / "04-vakia-denetim.json"
    rc, _ = _kos(VAKIA, "--dogrula", giris, "--json", str(cikis))
    assert rc == 0 and cikis.is_file()
    m = json.loads(cikis.read_text(encoding="utf-8"))
    assert m["ispat_bosluklari"] == ["I2"], "fikstür sözleşmesi: tanık caizliği belirsiz → I2 boşluk"
    return str(cikis)


def _satir(**k):
    s = {"iddia_id": "I2", "hedef_delil": "Site güvenlik kamera kaydı", "kaynak": "Site yönetimi",
         "yontem": "Yazılı saklama talebi ve delil tespiti değerlendirmesi", "kim": "AVUKAT",
         "aciliyet": "KAYBOLUYOR", "son_gun": "2026-11-02", "dayanak": "HMK m.400", "durum": "PLANLANDI"}
    s.update(k)
    return s


# ═══════════════════════════ delil tedarik planı (16-4) ═══════════════════

def test_iskelet_her_bosluga_satir_ve_doldurulmadan_gecmez(tmp_path, matris):
    rc, out = _kos(DELIL, "--matris", matris, "--iskelet")
    assert rc == 0
    isk = json.loads(out)
    assert [s["iddia_id"] for s in isk["satirlar"]] == ["I2"]
    plan = _yaz(tmp_path / "plan.json", out)
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 1 and "MUĞLAK hedef_delil «DOLDUR»" in out and "GEÇERSİZ kim" in out


def test_tam_plan_exit0_kaybolan_ve_kanun_hatirlatmalari(tmp_path, matris):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [
        _satir(), _satir(hedef_delil="Tanık T1 (kurgu)", kaynak="Müvekkil", yontem="Tanık listesine yazılması",
                         kim="MUVEKKIL", aciliyet="SURELI", dayanak="HMK m.240")]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 0 and ">>> PLAN TAM <<<" in out
    assert "🔴 satır 1 [I2]" in out and "HMK m.400/2" in out
    assert "HMK m.324" in out and "HMK m.240/2" in out
    assert "tanık caizliği BELİRSİZ" in out, "matristeki caizlik bilgisi plana taşınmalı"


def test_tedariksiz_bosluk_exit1(tmp_path, matris):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [_satir(iddia_id="I1")]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 1 and "TEDARİKSİZ BOŞLUK [I2]" in out


@pytest.mark.parametrize("muglak", ["Sair deliller", "Her türlü yasal delil", "İlgili yerlerden temin edilecektir",
                                    "Bilahare bildirilecektir"])
def test_sair_deliller_sinifi_muglak_exit1(tmp_path, matris, muglak):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [_satir(hedef_delil=muglak)]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 1 and "MUĞLAK hedef_delil" in out


def test_kosul_ifadesi_muglak_sayilmaz(tmp_path, matris):
    """'gerekirse keşif' meşru bir plan ifadesidir — sahte EKSİK alarmı yok."""
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [_satir(yontem="Müzekkere; gerekirse keşif talebi")]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 0, out


def test_karsi_taraf_ispat_yuku_tedarik_planlanmaz_uyarisi(tmp_path, matris):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [
        _satir(kim="KARSI_TARAF", kaynak="", yontem="", aciliyet="NORMAL", dayanak="HMK m.190")]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 0 and "ispat yükü KARŞI TARAFTA" in out and "HMK m.190/1" in out


def test_bilinmeyen_iddia_gecersiz_enum_ve_tarih_exit1(tmp_path, matris):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [
        _satir(), _satir(iddia_id="I9", aciliyet="ACİL", son_gun="yarın")]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 1
    assert "BİLİNMEYEN İDDİA" in out and "GEÇERSİZ aciliyet='ACİL'" in out and "GEÇERSİZ son_gun='yarın'" in out


def test_belirlenemedi_ve_gelmedi_uyarilari(tmp_path, matris):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [_satir(son_gun="BELIRLENEMEDI", durum="GELMEDI")]})
    rc, out = _kos(DELIL, "--matris", matris, "--plan", plan)
    assert rc == 0 and "oa-sure" in out and "HMK m.145" in out


def test_matris_sema_disi_exit2(tmp_path):
    sahte = _yaz(tmp_path / "sahte.json", {"satirlar": []})
    rc, out = _kos(DELIL, "--matris", sahte, "--iskelet")
    assert rc == 2 and "GİRDİ HATASI" in out


# ═══════════════════════════ tanık soru planı (16-3) ══════════════════════

def _tanik_plan(**ek):
    p = {"rejim": "hmk", "taniklar": [
        {"tanik": "T1 (komşu — kurgu)", "yan": "biz", "listede": "evet", "dinleme": "istinabe",
         "sorular": [{"soru": "Teslim günü olay yerinde miydiniz?", "vakia_id": "I1", "ispat_yonu": "ispat",
                      "risk": "dusuk"},
                     {"soru": "Davalı size ayıptan şöyle söylemiş miydi?", "vakia_id": "I2", "ispat_yonu": "ispat",
                      "risk": "orta"}]},
        {"tanik": "T2 (karşı tanık — kurgu)", "yan": "karsi", "listede": "hayir",
         "sorular": [{"soru": "Teslim günü işyerinde miydiniz?", "vakia_id": "I1", "ispat_yonu": "curutme",
                      "risk": "yuksek"}]}]}
    p.update(ek)
    return p


def test_gecerli_plan_exit0_ve_mesru_gecmis_zaman_sorusu(tmp_path, matris):
    rc, out = _kos(TANIK, "--matris", matris, "--plan", _yaz(tmp_path / "s.json", _tanik_plan()))
    assert rc == 0 and ">>> SORU PLANI GEÇERLİ <<<" in out
    assert "HMK m.240/2" in out and "HMK m.243/1" in out          # listede olmayan karşı tanık
    assert "HMK m.259/4" in out and "HMK m.255" in out and "HMK m.152" in out
    assert "tanık caizliği BELİRSİZ" in out and "HMK m.261/2" in out and "TCK m.277" in out


def test_tanik_cevabi_alani_ve_dikte_kalibi_exit1(tmp_path, matris):
    p = _tanik_plan()
    p["taniklar"][0]["sorular"][0]["beklenen_cevap"] = "Evet, gördüm"
    p["taniklar"][0]["sorular"][1]["soru"] = "Mahkemede teslimi gördüğünüzü söyleyin."
    p["taniklar"][1]["ifade_taslagi"] = "kurgu metin"
    rc, out = _kos(TANIK, "--matris", matris, "--plan", _yaz(tmp_path / "s.json", p))
    assert rc == 1
    assert out.count("TANIK CEVABI ÜRETİLEMEZ") == 2 and "TANIĞA CEVAP DİKTE EDEN İFADE" in out
    assert "TCK m.272" in out


@pytest.mark.parametrize("vid", ["", "I9"])
def test_vakiasiz_soru_exit1(tmp_path, matris, vid):
    p = _tanik_plan()
    p["taniklar"][0]["sorular"][0]["vakia_id"] = vid
    rc, out = _kos(TANIK, "--matris", matris, "--plan", _yaz(tmp_path / "s.json", p))
    assert rc == 1 and "VAKIASIZ SORU" in out


def test_hukuki_iddiaya_soru_uyari_cmk_rejiminde_liste_kilidi_yok(tmp_path, matris):
    p = _tanik_plan(rejim="cmk")
    p["taniklar"][0]["sorular"][0]["vakia_id"] = "I3"
    rc, out = _kos(TANIK, "--matris", matris, "--plan", _yaz(tmp_path / "s.json", p))
    assert rc == 0 and "hukuki iddia" in out and "CMK m.201" in out
    assert "HMK m.240/2" not in out, "HMK tek liste kilidi ceza rejimine taşınmaz"


def test_gecersiz_rejim_ve_enum_exit1(tmp_path, matris):
    p = _tanik_plan(rejim="idari")
    p["taniklar"][0]["sorular"][0]["ispat_yonu"] = "genel"
    rc, out = _kos(TANIK, "--matris", matris, "--plan", _yaz(tmp_path / "s.json", p))
    assert rc == 1 and "GEÇERSİZ rejim" in out and "GEÇERSİZ ispat_yonu='genel'" in out


# ═══════════════════════════ zabıt karşılaştırması (16-2) ═════════════════

KART = """⚠ DAHİLİ — DOSYAYA EKLENMEZ / UYAP'A YÜKLENMEZ

# Celse kartı (kurgu)

## (a) Hedefler
- Keşif kararı

## (c) Tutanağa geçirilmesi şart olan beyanlar
- Tanık T1'in dinlenmesi talebimiz
- Bilirkişi raporuna itirazımız
- Banka kayıtlarının celbi talebimiz

## (d) Ara karar talepleri
- Keşif
"""

ZABIT = """# 051 · durusma-zapti.pdf

- Kaynak evrak: `kurgu/zapt.pdf`
- Çıkarım yöntemi: **metin**

---

ÖRNEK ASLİYE HUKUK MAHKEMESİ DURUŞMA TUTANAĞI Tarih: 05.10.2026

HAKİM: Kurgu Hâkim KATİP: Kurgu Kâtip

Açık yargılamaya devam olundu. Davacı vekili tanık T1'in dinlenmesini talep etti. Davacı vekili bilirkişi raporuna itiraz etti.

GEREĞİ DÜŞÜNÜLDÜ: 1- Davacı vekilinin tanık dinletme talebinin reddine, 2- Bilirkişi raporuna karşı beyan için davacı vekiline iki haftalık kesin süre verilmesine, 3- Duruşmanın ertelenmesine karar verildi.
"""


def _zapt(tmp_path, kart=KART, zabit=ZABIT, *ek):
    k = _yaz(tmp_path / ("kart.json" if kart.lstrip().startswith("{") else "kart.md"), kart)
    z = _yaz(tmp_path / "zapt.md", zabit)
    rc, out = _kos(ZAPT, "--kart", k, "--zapt", z, "--json", *ek)
    return rc, (json.loads(out) if rc == 0 else out)


def test_kalem_eslesme_ara_karar_sure_ve_gerekcesiz_ret(tmp_path):
    rc, r = _zapt(tmp_path)
    assert rc == 0
    durum = {k["id"]: k["durum"] for k in r["kalemler"]}
    assert durum == {"K1": "GEÇMİŞ GÖRÜNÜYOR", "K2": "GEÇMİŞ GÖRÜNÜYOR", "K3": "GEÇMEMİŞ GÖRÜNÜYOR"}
    ak = {a["no"]: a for a in r["ara_kararlar"]}
    assert ak["1"]["ret"] and ak["1"]["ret_konusu_delil_talep"] and ak["1"]["gerekce_ibaresi"] is False
    assert ak["2"]["sure_dogurabilir"] and not ak["2"]["ret"]
    assert r["ozet"]["gerekce_ibaresiz_ret"] == 1 and r["ozet"]["sure_dogurabilir_ara_karar"] == 1
    assert "(d)" not in json.dumps(r, ensure_ascii=False), "yalnız 'TUTANAĞA' bölümü okunur"


def test_insan_raporu_aday_ve_teyit_bekliyor_notu(tmp_path):
    k = _yaz(tmp_path / "kart.md", KART)
    z = _yaz(tmp_path / "zapt.md", ZABIT)
    rc, out = _kos(ZAPT, "--kart", k, "--zapt", z)
    assert rc == 0 and "ADAYDIR" in out and "TEYİT BEKLİYOR" in out and "oa-sure" in out
    assert "HMK m.154/3-ğ" in out and "HMK m.156" in out


def test_unsuz_yumusamasi_yalniz_kok_sonunda():
    spec = __import__("importlib.util").util.spec_from_file_location("v0518_zapt", ZAPT)
    mod = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod._kok_eslesir("TALEP", "TALEB") and mod._kok_eslesir("TALEBİNİN", "TALEB")
    assert mod._kok_eslesir("AĞACI", "AĞAÇ") is True
    assert not mod._kok_eslesir("TAVAN", "DAVA"), "yumuşama yalnız kök SONUNDA denk sayılır"
    assert not mod._kok_eslesir("TAL", "TALEB")


def test_gerekceli_ret_isaretlenir(tmp_path):
    z = ZABIT.replace("talebinin reddine,", "talebinin, vakıanın tanıkla ispatı mümkün olmadığından reddine,")
    rc, r = _zapt(tmp_path, KART, z)
    assert rc == 0 and r["ara_kararlar"][0]["gerekce_ibaresi"] is True and r["ozet"]["gerekce_ibaresiz_ret"] == 0


def test_json_kart_ve_acik_anahtar(tmp_path):
    kart = json.dumps({"kalemler": [{"id": "T9", "tur": "talep", "metin": "Banka kayıtları",
                                     "anahtar": ["banka", "kayıt"]}]}, ensure_ascii=False)
    z = ZABIT.replace("itiraz etti.", "itiraz etti. Banka kayıtlarının celbi talep edildi.")
    rc, r = _zapt(tmp_path, kart, z)
    assert rc == 0 and r["kalemler"][0]["durum"] == "GEÇMİŞ GÖRÜNÜYOR" and r["kalemler"][0]["tur"] == "talep"


def test_unsur_ipucu_bilgi_duzeyi(tmp_path):
    rc, r = _zapt(tmp_path, KART, "Davacı vekili tanık dinletme talebinde bulundu.\n")
    assert rc == 0
    eksik = " ".join(r["unsur_ipucu_bulunamadi"])
    assert "mahkemenin adı" in eksik and "ara kararlar" in eksik


def test_zapt_girdi_hatalari_exit2(tmp_path):
    rc, out = _zapt(tmp_path, "# Kart\n- tutanak bölümü yok\n")
    assert rc == 2 and "TUTANAĞA" in out
    rc, out = _zapt(tmp_path, KART, "\n\n")
    assert rc == 2 and "boş" in out
    ikili = tmp_path / "zapt.pdf"
    ikili.write_bytes(b"%PDF-1.4 kurgu")
    rc, out = _kos(ZAPT, "--kart", _yaz(tmp_path / "k.md", KART), "--zapt", str(ikili))
    assert rc == 2 and "oa-ingest" in out


# ═══════════════════════════ ortak sözleşme ═══════════════════════════════

def test_uc_kapi_hicbir_dosya_yazmaz(tmp_path, matris):
    plan = _yaz(tmp_path / "plan.json", {"satirlar": [_satir()]})
    soru = _yaz(tmp_path / "soru.json", _tanik_plan())
    kart, zapt = _yaz(tmp_path / "kart.md", KART), _yaz(tmp_path / "zapt.md", ZABIT)
    once = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    _kos(DELIL, "--matris", matris, "--plan", plan, "--json", cwd=tmp_path)
    _kos(DELIL, "--matris", matris, "--iskelet", cwd=tmp_path)
    _kos(TANIK, "--matris", matris, "--plan", soru, "--json", cwd=tmp_path)
    _kos(ZAPT, "--kart", kart, "--zapt", zapt, "--json", cwd=tmp_path)
    assert once == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


@pytest.mark.parametrize("script", [DELIL, TANIK, ZAPT])
def test_guvenlik_ve_bicim_sozlesmesi(script):
    src = script.read_text(encoding="utf-8")
    assert "__OA_UTF8_GUARD__" in src and "5846 sayılı FSEK" in src and "NEDEN VAR" in src
    assert not re.search(r"^\s*(?:from|import)\s+(requests|httpx|urllib|socket|subprocess|pickle)", src, re.M)
    assert "eval(" not in src and "exec(" not in src and "shell=True" not in src
    assert not re.search(r"open\([^)]*['\"][wa]b?['\"]", src), "kapı yazma kipinde dosya açıyor"


def test_skill_md_baglantilari():
    vakia = (SKILLS / "oa-vakia" / "SKILL.md").read_text(encoding="utf-8")
    for k in ("scripts/delil_plani.py", "scripts/tanik_plani.py", "VAKIASIZ SORU YOKTUR", "TANIĞIN CEVABI YAZILMAZ",
              "HMK m.400/2", "HMK m.324", "TCK m.272", "DAHİLİ", "UNSUR ŞABLONLARI", "ispat_bosluklari"):
        assert k in vakia, k
    antitez = (SKILLS / "oa-antitez" / "SKILL.md").read_text(encoding="utf-8")
    blok = re.sub(r"\s+", " ", antitez[antitez.index("**Zabıt karşılaştırma yardımcısı"):])
    for k in ("scripts/zapt_denetim.py", "TUTANAĞA", "ADAY", "HMK m.154/3-g", "(m.156)", "**TEYİT BEKLİYOR**",
              "oa-sure", "avukatındır"):
        assert k in blok, k
