# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP H: oa-ictihat KANUN YOLU ZİNCİRİ ÇIKARICI + İNİŞ RİTÜELİ +
İÇTİHAT HARİTASI regresyon ve kilit testleri.

Kapsanan denetim bulguları (2026-09-06 raporları):
  Hamle 8 / karar #10  — `kanun_yolu_zinciri.py` scripti oa-ictihat'a (üst karar
                          metninden alt künye çıkarımı; iniş kararı MEKANİK)
  D1                    — BAM kendi dosyasının alt künyelerini REDAKTE eder
                          («... Esas, ... Karar») → iniş kör; script bunu
                          `redakte:true` ile görünür kılar, "bulundu" demez
  D2                    — bulunamadı ≠ yok (indeks kapsaması) → SKILL bölümü
  D3                    — esas_no BAM'lar arası tekil değil; MCP'de BAM/daire
                          filtresi yok → istemci tarafı süzgeç (`--suzgec`)
  P2-5 / A-14           — İÇTİHAT HARİTASI adımı (triajdan ÖNCE yerleşik hat /
                          azınlık / ayrışma / HGK-İBK) + «üç lehe karar bulununca
                          DURULMAZ» cümlesi

ANONİMLİK (anayasa m.7): bütün fikstürler SENTETİKTİR — «E. 2099/N» sınıfı
numaralar, «Örnek ...» mahkeme adları; gerçek künye/kişi/dosya YOKTUR.

Norm teyitleri (Mevzuat MCP, 2026-09-06): HMK m.341 (istinaf), m.361 (temyiz);
CMK m.272 (istinaf), m.286 (temyiz); 2797 s. Yargıtay K. m.45 (İBK bağlayıcılığı).
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ictihat"
SCRIPT = SKILL / "scripts" / "kanun_yolu_zinciri.py"
SKILL_MD = SKILL / "SKILL.md"
README = SKILL / "README.md"


def _load():
    spec = importlib.util.spec_from_file_location("kanun_yolu_zinciri_v0516", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _cli(*args, cwd=None):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd or REPO),
    )
    return cp.returncode, cp.stdout, cp.stderr


# ═══════════════════ SENTETİK FİKSTÜRLER (m.7 — gerçek künye YOK) ═══════════

# (i) Yeni Yargıtay HUKUK başlık biçimi — BAM + ilk derece künyeleri TAM
YARGITAY_HUKUK_YENI = """T.C.
YARGITAY
11. Hukuk Dairesi

ESAS NO : 2099/5
KARAR NO : 2099/6
KARAR TARİHİ : 01.04.2099

MAHKEMESİ : Örnek Bölge Adliye Mahkemesi 3. Hukuk Dairesi
TARİHİ : 15.02.2099
SAYISI : 2099/11 E., 2099/22 K.

İLK DERECE MAHKEMESİ : Örnek 3. Asliye Hukuk Mahkemesi
TARİHİ : 12.03.2098
SAYISI : 2099/1 E., 2099/2 K.

Taraflar arasındaki alacak davasından dolayı yapılan yargılama sonunda
verilen karar davalı vekili tarafından temyiz edilmiştir.

KARAR: Dosyadaki yazılara göre kararın ONANMASINA karar verildi.
"""

# (ii) Eski biçim — gövde cümlesi «... Mahkemesince verilen dd.mm.yyyy tarih ve
# YYYY/N E., YYYY/N K. sayılı»
YARGITAY_ESKI = """T.C.
YARGITAY
4. Hukuk Dairesi
E. 2099/7
K. 2099/8
T. 05.05.2099

Taraflar arasındaki tazminat davasından dolayı yapılan yargılama sonunda
Örnek 2. Asliye Hukuk Mahkemesince verilen 10.01.2099 tarih ve 2099/3 E.,
2099/4 K. sayılı kararın Yargıtayca incelenmesi davacı vekili tarafından
istenilmekle, dosya incelendi, gereği görüşüldü.

Dosyadaki yazılara göre kararın BOZULMASINA karar verildi.
"""

# (iv) BAM metni — kendi dosyasının ilk derece künyesi REDAKTE («... Esas, ... Karar»)
BAM_REDAKTE = """T.C.
ÖRNEK BÖLGE ADLİYE MAHKEMESİ
3. HUKUK DAİRESİ

DOSYA NO : 2099/40 Esas
KARAR NO : 2099/41
KARAR TARİHİ : 20.06.2099

İNCELENEN KARARIN
MAHKEMESİ : Örnek 2. Asliye Hukuk Mahkemesi
TARİHİ : 11.11.2098
NUMARASI : ... Esas, ... Karar

Taraflar arasındaki davanın yapılan yargılaması sonunda ilamda yazılı
nedenlerle davanın reddine ilişkin karara karşı istinaf yoluna başvurulmuştur.

İstinaf başvurusunun HMK m.353/1-b-1 uyarınca ESASTAN REDDİNE karar verildi.
"""

# (iii) Ceza yeni biçim — BAM ceza dairesi TAM, ilk derece İLÇE ADI REDAKTE
YARGITAY_CEZA_ILCE_REDAKTE = """T.C.
YARGITAY
12. Ceza Dairesi

ESAS NO : 2099/50
KARAR NO : 2099/51
KARAR TARİHİ : 30.09.2099

MAHKEMESİ : Örnek Bölge Adliye Mahkemesi 2. Ceza Dairesi
TARİHİ : 01.07.2099
SAYISI : 2099/60 E., 2099/61 K.

İLK DERECE MAHKEMESİ : ... 1. Asliye Ceza Mahkemesi
TARİHİ : 02.02.2099
SAYISI : 2099/70 E., 2099/71 K.

Sanık hakkında kurulan hükme yönelik istinaf başvurusunun esastan reddine
ilişkin karar sanık müdafii tarafından temyiz edilmiştir.

Yapılan incelemede hükmün ONANMASINA karar verildi.
"""

# (v) Doğrudan temyiz (BAM katı yok — kanun yolu geçişi öncesi dosya): alt=ilk derece
YARGITAY_DOGRUDAN = """T.C.
YARGITAY
9. Hukuk Dairesi
ESAS NO : 2099/80
KARAR NO : 2099/81
KARAR TARİHİ : 03.03.2099

MAHKEMESİ : Örnek 5. İş Mahkemesi
TARİHİ : 04.04.2098
SAYISI : 2099/82 E., 2099/83 K.

Davacı, kıdem tazminatının ödetilmesine karar verilmesini istemiştir.
"""


# ═══════════════════ (1) Yeni Yargıtay hukuk → iniş EVET ════════════════════

def test_yeni_yargitay_hukuk_zincir_ve_inis_evet():
    r = MOD.zincir_cikar(YARGITAY_HUKUK_YENI, girdi="sentetik")
    assert r["arac"] == "kanun_yolu_zinciri"
    ust = r["ust"]
    assert ust["merci"] == "Yargıtay"
    assert ust["daire"] == "11. HD"
    assert ust["esas"] == "2099/5" and ust["karar"] == "2099/6"
    assert ust["tarih"] == "01.04.2099"
    alt = r["alt"]
    assert [a["seviye"] for a in alt] == ["BAM", "ilk_derece"]
    bam, ilk = alt
    assert bam["mahkeme"].startswith("Örnek Bölge Adliye Mahkemesi")
    assert bam["esas"] == "2099/11" and bam["karar"] == "2099/22"
    assert bam["tarih"] == "15.02.2099" and bam["redakte"] is False
    assert ilk["mahkeme"] == "Örnek 3. Asliye Hukuk Mahkemesi"
    assert ilk["esas"] == "2099/1" and ilk["karar"] == "2099/2"
    assert ilk["tarih"] == "12.03.2098" and ilk["redakte"] is False
    assert r["inis_mumkun"] is True
    assert r["inis_kati"] == "ilk_derece"
    assert "2099/1" in r["zincir_ozeti"] and "Yargıtay" in r["zincir_ozeti"]


# ═══════════════════ (2) Eski biçim (gövde cümlesi) → iniş EVET ═════════════

def test_eski_bicim_govde_cumlesi_inis_evet():
    r = MOD.zincir_cikar(YARGITAY_ESKI, girdi="sentetik")
    assert r["ust"]["merci"] == "Yargıtay" and r["ust"]["daire"] == "4. HD"
    assert r["ust"]["esas"] == "2099/7" and r["ust"]["karar"] == "2099/8"
    assert len(r["alt"]) == 1
    a = r["alt"][0]
    assert a["seviye"] == "ilk_derece"
    assert a["mahkeme"] == "Örnek 2. Asliye Hukuk Mahkemesi"
    assert a["esas"] == "2099/3" and a["karar"] == "2099/4"
    assert a["tarih"] == "10.01.2099" and a["redakte"] is False
    assert r["inis_mumkun"] is True and r["inis_kati"] == "ilk_derece"


# ═══════════════════ (3) BAM redakte → iniş HAYIR + redakte:true (D1) ═══════

def test_bam_redakte_inis_hayir_redakte_true():
    r = MOD.zincir_cikar(BAM_REDAKTE, girdi="sentetik")
    assert r["ust"]["merci"] == "BAM"
    assert r["ust"]["daire"] == "3. HD"
    assert r["ust"]["esas"] == "2099/40" and r["ust"]["karar"] == "2099/41"
    assert len(r["alt"]) == 1
    a = r["alt"][0]
    assert a["seviye"] == "ilk_derece"
    assert a["mahkeme"] == "Örnek 2. Asliye Hukuk Mahkemesi"
    assert a["redakte"] is True
    assert a["esas"] is None and a["karar"] is None
    assert r["inis_mumkun"] is False
    assert r["inis_kati"] is None
    assert "redakte" in r["gerekce"].lower() and "D1" in r["gerekce"]


def test_redakte_deseni_uc_nokta_ve_elips():
    # regex «\.{3}\s*Esas» / «…» — iki yazım da yakalanır; tam künye yakalanmaz
    assert MOD.redakte_mi("... Esas, ... Karar")
    assert MOD.redakte_mi("… Esas, … Karar")
    assert MOD.redakte_mi("…/… E., …/… K.")
    assert not MOD.redakte_mi("2099/11 E., 2099/22 K.")


# ═══════════════════ (4) Ceza ilçe redakte → BAM'a kadar ════════════════════

def test_ceza_ilce_redakte_inis_bam_a_kadar():
    r = MOD.zincir_cikar(YARGITAY_CEZA_ILCE_REDAKTE, girdi="sentetik")
    assert r["ust"]["merci"] == "Yargıtay" and r["ust"]["daire"] == "12. CD"
    alt = r["alt"]
    assert [a["seviye"] for a in alt] == ["BAM", "ilk_derece"]
    bam, ilk = alt
    assert bam["redakte"] is False and bam["esas"] == "2099/60"
    assert "Ceza Dairesi" in bam["mahkeme"]
    # ilk derece: künye numaraları var ama MAHKEME ADI (ilçe) redakte → iniş kör
    assert ilk["redakte"] is True
    assert ilk["esas"] == "2099/70" and ilk["karar"] == "2099/71"
    assert r["inis_mumkun"] is True
    assert r["inis_kati"] == "BAM"
    assert "ilçe" in r["gerekce"].lower()


def test_dogrudan_temyiz_bam_kati_yok():
    r = MOD.zincir_cikar(YARGITAY_DOGRUDAN, girdi="sentetik")
    assert [a["seviye"] for a in r["alt"]] == ["ilk_derece"]
    assert r["alt"][0]["mahkeme"] == "Örnek 5. İş Mahkemesi"
    assert r["inis_mumkun"] is True and r["inis_kati"] == "ilk_derece"


def test_alt_kunye_yoksa_fail_closed():
    metin = "T.C.\nYARGITAY\n3. Hukuk Dairesi\nESAS NO : 2099/90\nKARAR NO : 2099/91\n\nGereği düşünüldü.\n"
    r = MOD.zincir_cikar(metin, girdi="sentetik")
    assert r["alt"] == []
    assert r["inis_mumkun"] is False
    assert r["inis_kati"] is None
    assert r["gerekce"]


# ═══════════════════ CLI — --json, --kok (dosya + ÖNERİLEN komut, kütük YAZMAZ) ══

def test_cli_json_ve_kok_cikti_dosyasi_kutuk_yazmaz(tmp_path):
    girdi = tmp_path / "_oa" / "teyit" / "dokum" / "2099-ictihat_getir-ornek.md"
    girdi.parent.mkdir(parents=True)
    girdi.write_text(YARGITAY_HUKUK_YENI, encoding="utf-8")
    rc, out, err = _cli(str(girdi), "--json", "--kok", str(tmp_path))
    assert rc == 0, err
    veri = json.loads(out)
    assert veri["arac"] == "kanun_yolu_zinciri"
    assert veri["inis_mumkun"] is True
    assert veri["girdi"].endswith("2099-ictihat_getir-ornek.md")
    cikti = tmp_path / "_oa" / "cikti" / "03-kanun-yolu-zinciri.json"
    assert cikti.is_file()
    disk = json.loads(cikti.read_text(encoding="utf-8"))
    assert disk["ust"]["esas"] == "2099/5"
    # ÖNERİLEN teyit komutu STDERR'e (JSON stdout'u kirlenmez) — kat başına satır
    assert "oa_hafiza.py teyit" in err
    assert "SEVİYE=BAM" in err and "SEVİYE=ilk_derece" in err
    assert "KÜNYE=tam" in err
    # tek yazar oa_hafiza: script kütüğe KENDİSİ YAZMAZ
    assert not (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").exists()


def test_cli_redakte_kunye_onerisi_redakte_etiketi(tmp_path):
    girdi = tmp_path / "bam.md"
    girdi.write_text(BAM_REDAKTE, encoding="utf-8")
    rc, out, err = _cli(str(girdi), "--kok", str(tmp_path))
    assert rc == 0, err
    assert "KÜNYE=redakte" in err
    assert "iniş" in out.lower() or "İNİŞ" in out


def test_cli_dosya_yoksa_ret():
    rc, out, err = _cli(str(REPO / "tests" / "_yok_2099.md"))
    assert rc != 0
    assert "RET" in (out + err)


# ═══════════════════ --suzgec (D3: istemci tarafı BAM/daire/yıl süzgeci) ════

SONUCLAR = {
    "results": [
        {"birimAdi": "Örnek Bölge Adliye Mahkemesi 11. Hukuk Dairesi",
         "esasNo": "2099/100", "kararNo": "2099/101", "kararTarihi": "2099-05-01"},
        {"birimAdi": "Başka Bölge Adliye Mahkemesi 11. Hukuk Dairesi",
         "esasNo": "2099/100", "kararNo": "2099/200", "kararTarihi": "2099-06-01"},
        {"birimAdi": "Örnek Bölge Adliye Mahkemesi 3. Hukuk Dairesi",
         "esasNo": "2099/300", "kararNo": "2099/301", "kararTarihi": "2099-07-01"},
        {"birimAdi": "Örnek Bölge Adliye Mahkemesi 11. Hukuk Dairesi",
         "esasNo": "2090/400", "kararNo": "2090/401", "kararTarihi": "12.12.2090"},
        # tarih YOK, karar no YOK (yalnız esas) → yıl belirsiz → fail-closed elenir
        # (karar no varsa yılı ondan okumak MEKANİK olarak meşrudur — karar numarası
        # karar yılında verilir; esas yılı ise dava yılıdır, karar yılı DEĞİLDİR)
        {"birimAdi": "Örnek Bölge Adliye Mahkemesi 11. Hukuk Dairesi",
         "esasNo": "2099/500"},
    ]
}


def test_suzgec_bam_daire_yil(tmp_path):
    j = tmp_path / "arama.json"
    j.write_text(json.dumps(SONUCLAR, ensure_ascii=False), encoding="utf-8")
    rc, out, err = _cli("--suzgec", str(j), "--bam", "Örnek Bölge Adliye",
                        "--daire", "11. HD", "--yil-min", "2095", "--json")
    assert rc == 0, err
    v = json.loads(out)
    assert v["mod"] == "suzgec"
    assert v["sayilar"]["toplam"] == 5
    assert v["sayilar"]["suzulen"] == 1
    assert v["sayilar"]["elenen"] == 4
    assert v["suzulen"][0]["kararNo"] == "2099/101"
    nedenler = " ".join(e["neden"] for e in v["elenen"])
    # aynı esas_no farklı BAM → elenir (D3); farklı daire → elenir; eski yıl → elenir;
    # tarihsiz kayıt SESSİZCE geçmez — «yıl belirsiz» nedeniyle elenir (fail-closed)
    assert "BAM" in nedenler and "daire" in nedenler and "yıl" in nedenler
    assert "belirsiz" in nedenler
    # sessiz kırpma yok: sayılar STDERR özetinde de görünür
    assert "süzülen" in err.lower() and "elenen" in err.lower()


def test_suzgec_filtresiz_hepsi_gecer_ve_uyari(tmp_path):
    j = tmp_path / "arama.json"
    j.write_text(json.dumps(SONUCLAR["results"], ensure_ascii=False), encoding="utf-8")
    rc, out, err = _cli("--suzgec", str(j), "--json")
    assert rc == 0, err
    v = json.loads(out)
    assert v["sayilar"]["suzulen"] == 5
    assert "UYARI" in err  # filtre verilmedi — süzgeç anlamsız, görünür uyarı


def test_suzgec_daire_ayristirilamazsa_ret(tmp_path):
    j = tmp_path / "arama.json"
    j.write_text("[]", encoding="utf-8")
    rc, out, err = _cli("--suzgec", str(j), "--daire", "onbirinci daire")
    assert rc != 0
    assert "RET" in (out + err)


def test_suzgec_bozuk_json_ret(tmp_path):
    j = tmp_path / "arama.json"
    j.write_text("{bozuk", encoding="utf-8")
    rc, out, err = _cli("--suzgec", str(j), "--bam", "Örnek")
    assert rc != 0
    assert "RET" in (out + err)


# ═══════════════════ Mühendislik kilitleri ══════════════════════════════════

def test_script_utf8_guard_ve_ag_importu_yok():
    txt = SCRIPT.read_text(encoding="utf-8")
    assert "__OA_UTF8_GUARD__" in txt
    yasak = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib3|socket|"
                       r"http\.client|urllib\.request)\b", re.M)
    assert not yasak.search(txt)


def test_kunye_ortak_yuklenir_ve_yedek_fail_closed(monkeypatch):
    # Normal yol: oa-kontrol/scripts/kunye_ortak.py göreli yoldan yüklenir
    assert MOD.KO is not None and hasattr(MOD.KO, "esas_karar_atiflari")
    # Yedek yol: modül bulunamazsa yerel minimal regex + görünür uyarı
    ko, uyari = MOD.kunye_ortak_yukle(pathlib.Path("/_olmayan_2099_/kunye_ortak.py"))
    assert ko is None
    assert uyari and "kunye_ortak" in uyari
    r = MOD.zincir_cikar(YARGITAY_HUKUK_YENI, girdi="sentetik", ko=None)
    assert r["ust"]["esas"] == "2099/5"
    assert r["alt"][1]["esas"] == "2099/1"
    assert any("kunye_ortak" in u for u in r["uyarilar"])


# ═══════════════════ SKILL.md / README — İNİŞ RİTÜELİ + İÇTİHAT HARİTASI ════

def test_skill_inis_ritueli_bolumu():
    md = SKILL_MD.read_text(encoding="utf-8")
    assert "## İNİŞ RİTÜELİ" in md
    for parca in ("D1", "D2", "D3", "bulunamadı ≠ yok",
                  "SEVİYE=", "KÜNYE=", "METİN=",
                  "03-kanun-yolu-zinciri.json", "scripts/kanun_yolu_zinciri.py",
                  "Layer 0", "Mevzuat MCP teyit 2026-09-06"):
        assert parca in md, parca
    # UYAP'ta iniş avukata aittir
    assert "UYAP" in md and "avukat" in md.lower()
    # MCP-teyitli normlar anılır (madde numarası uydurulmaz)
    for norm in ("HMK m.341", "HMK m.361", "CMK m.272", "CMK m.286", "2797"):
        assert norm in md, norm


def test_skill_ictihat_haritasi_ve_uc_lehe_karar_cumlesi():
    md = SKILL_MD.read_text(encoding="utf-8")
    assert "## İÇTİHAT HARİTASI" in md
    assert "A-14" in md
    for parca in ("yerleşik hat", "azınlık", "ayrışma", "HGK", "İBK"):
        assert parca in md, parca
    # «Birincil kriter» bölümüne eklenen cümle
    bas = md.index("## Birincil kriter")
    son = md.index("## ", bas + 5)
    bolum = md[bas:son]
    assert "üç lehe karar bulununca DURULMAZ" in bolum
    assert "İBK > HGK > daire" in bolum


def test_readme_scripti_listeler():
    rd = README.read_text(encoding="utf-8")
    assert "scripts/kanun_yolu_zinciri.py" in rd
    assert "saf metin-disiplinidir" not in rd
