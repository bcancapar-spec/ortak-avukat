# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP G: oa-usta / aile_dogrula.py YAPISAL KİLİTLER (Hamle 10)
+ SÜRÜM İŞARETÇİSİ (P2-10 / B-3) + HATA TETİKLİ DAMITMA belgesi (P2-8 / A-27 / A-28).

Denetim raporları (2026-09-06) bulguları:

- **K1** oa-illiyet SKILL.md örneği denetim çıktısını `01-illiyet-denetim.json`
  adıyla yazdırıyor; oa-pipeline bekçisi `_graf_yapisal_bosluk_uyarisi` ise
  `*graf*.json` okuyordu → üretilen JSON bekçiye hiç girmedi, DURUM.md "boşluk
  yok" gösterdi (sahte yeşil). Hamle 10 (a): bekçi deseni ↔ SKILL örneği aynı
  kapıda fnmatch ile karşılaştırılır.
- **Hamle 10 (b)** grafik_denetim.KANONIK enum ↔ illiyet-doktrini.md literal
  uyumu (A grubu doktrini yeni enumlarla güncelliyor; enum eklenip doktrin
  güncellenmezse kapı kırmızı).
- **P2-10 / B-3** STATUS.md ve YOL-HARITASI.md sürüm işaretçileri plugin.json
  «version» ile eşit olmalı (main'de 0.5.11 / 0.5.8.4 ↔ 0.5.15).
- **P2-8 / A-27 / A-28** damıtma yalnız tekrar sayacıyla değil avukat revize
  diff'iyle tetiklenir (`_oa/defter/avukat-hukmu.jsonl`); eşik/oran yok,
  sayım görünür; SICRAMA-NOTU §5 şartı.

Tüm fikstürler SENTETİKTİR (tempfile; depo dosyasına yazılmaz). Gerçek depo
yalnız salt-okunur ölçülür.
"""
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
AILE_DOGRULA = SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"
USTA_SKILL = SKILLS / "oa-usta" / "SKILL.md"
PLUGIN_JSON = REPO / "plugins" / "ortak-avukat" / ".claude-plugin" / "plugin.json"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ad = _yukle("aile_dogrula_v0516_G", AILE_DOGRULA)


@pytest.fixture
def tmp():
    d = pathlib.Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ═══════════════ KİLİT-A — bekçi↔skill sözleşmesi (K1) ═════════════════════

_BEKCI_SABLON = textwrap.dedent('''\
    import glob, json, os

    def _graf_yapisal_bosluk_uyarisi(kok):
        cdiz = os.path.join(kok, "_oa", "cikti")
        uyarilar = []
        for yol in sorted(glob.glob(os.path.join(cdiz, "{graf}"))):
            uyarilar.append(yol)
        return uyarilar


    def _kiyas_bosluk_uyarisi(kok):
        cdiz = os.path.join(kok, "_oa", "cikti")
        for yol in sorted(glob.glob(os.path.join(cdiz, "{kiyas}"))):
            pass
        return []


    def _usul_bosluk_uyarisi(kok):
        cdiz = os.path.join(kok, "_oa", "cikti")
        for yol in sorted(glob.glob(os.path.join(cdiz, "{usul}"))):
            pass
        return []
''')


def _sentetik_kok(tmp, graf="*graf*.json", kiyas="*kiyas*.json", usul="*usul*.json",
                  illiyet_ornek="01-illiyet-denetim.json", bekci_var=True):
    """Sentetik aile kökü: oa-pipeline/scripts/pipeline_kayit.py (bekçiler) +
    oa-illiyet/SKILL.md (örnek komut). Gerçek depoya dokunmaz."""
    kok = tmp / "skills"
    (kok / "oa-pipeline" / "scripts").mkdir(parents=True)
    pk = kok / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
    if bekci_var:
        pk.write_text(_BEKCI_SABLON.format(graf=graf, kiyas=kiyas, usul=usul),
                      encoding="utf-8")
    else:
        pk.write_text("import os\n\ndef baska_fonksiyon():\n    return 1\n",
                      encoding="utf-8")
    (kok / "oa-illiyet").mkdir()
    (kok / "oa-illiyet" / "SKILL.md").write_text(
        "# oa-illiyet\n\n```bash\npython scripts/grafik_denetim.py "
        f"_oa/cikti/01-illiyet-graf.json [--json _oa/cikti/{illiyet_ornek}]\n```\n",
        encoding="utf-8")
    (kok / "oa-kiyas").mkdir()
    (kok / "oa-kiyas" / "SKILL.md").write_text(
        "# oa-kiyas\n\n```bash\npython scripts/kiyas_denetim.py _oa/cikti/05-kiyas.json"
        " --json _oa/cikti/05-kiyas-denetim.json\n```\n", encoding="utf-8")
    (kok / "oa-usul").mkdir()
    (kok / "oa-usul" / "SKILL.md").write_text(
        "# oa-usul\n\n```bash\npython scripts/usul_matris.py --girdi "
        "_oa/cikti/usul-matris.json\n```\n", encoding="utf-8")
    return kok


def test_kilit_a_eski_desen_hata(tmp):
    """K1 yönü: bekçi `*graf*.json`, SKILL örneği `01-illiyet-denetim.json` →
    HATA; mesaj parçayı, örnek adı ve bekçi desenini adıyla söyler."""
    kok = _sentetik_kok(tmp)
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(kok))
    assert uyarilar == []
    assert len(hatalar) == 1, hatalar
    h = hatalar[0]
    assert "K1" in h and "oa-illiyet" in h
    assert "01-illiyet-denetim.json" in h and "*graf*.json" in h
    # oa-kiyas örneği `05-kiyas-denetim.json` ↔ `*kiyas*.json` eşleşir (hata yok)


def test_kilit_a_yildiz_json_temiz(tmp):
    """Karşı yön: B grubunun hedef deseni `*.json` (+ damga süzgeci) SKILL
    örneğiyle eşleşir → temiz. Entegrasyonda gerçek depoyu yeşile çeviren durum."""
    kok = _sentetik_kok(tmp, graf="*.json", kiyas="*.json", usul="*.json")
    assert ad.bekci_skill_sozlesmesi(str(kok)) == ([], [])


def test_kilit_a_kiyas_kopusu_da_yakalanir(tmp):
    """Sözleşme yalnız illiyet için değil: kıyas bekçisi `05-kiyas*` gibi bir
    desene dönerse SKILL örneği `05-kiyas-denetim.json` yine eşleşir; ama
    `*subsumtion*.json` gibi bir desen eşleşmez → HATA (B-28 sınıfı)."""
    kok = _sentetik_kok(tmp, kiyas="*subsumtion*.json")
    hatalar, _ = ad.bekci_skill_sozlesmesi(str(kok))
    assert any("oa-kiyas" in h and "05-kiyas-denetim.json" in h for h in hatalar), hatalar


def test_kilit_a_depo_disi_sessiz(tmp):
    """VENDOR deseni: pipeline_kayit.py yoksa (depo-dışı kopya) sessiz atlanır —
    ne hata ne uyarı."""
    kok = tmp / "skills"
    (kok / "oa-illiyet").mkdir(parents=True)
    (kok / "oa-illiyet" / "SKILL.md").write_text(
        "--json _oa/cikti/01-illiyet-denetim.json\n", encoding="utf-8")
    assert ad.bekci_skill_sozlesmesi(str(kok)) == ([], [])


def test_kilit_a_bekci_yoksa_uyari_cokmez(tmp):
    """Geriye uyum / sessiz-atlama yasağı: pipeline_kayit.py var ama bekçi
    fonksiyonları yoksa (eski nesil ya da yeniden adlandırılmış) kilit kör
    kalır — bu ÇÖKME değil, GÖRÜNÜR UYARI olmalı; hata üretilmez."""
    kok = _sentetik_kok(tmp, bekci_var=False)
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(kok))
    assert hatalar == []
    assert len(uyarilar) == 3
    assert all("kilidi kör" in u for u in uyarilar)


def test_kilit_a_desen_cikarilamazsa_uyari(tmp):
    """Bekçi var ama gövdesinde tanınan glob deseni yok → 'kör' uyarısı
    (kilit sessizce yeşil sanılmasın)."""
    kok = _sentetik_kok(tmp)
    pk = kok / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
    pk.write_text(pk.read_text(encoding="utf-8").replace(
        'glob.glob(os.path.join(cdiz, "*graf*.json"))', "GRAF_DOSYALARI(cdiz)"),
        encoding="utf-8")
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(kok))
    assert hatalar == []
    assert any("_graf_yapisal_bosluk_uyarisi" in u and "kör" in u for u in uyarilar)


def test_kilit_a_gercek_depo_kilit_kor_degil():
    """Gerçek depoda kilit KÖR OLMAMALI: üç bekçi de bulunmalı ve her birinden
    bir glob deseni çıkarılmalı. (Kopuş var mı yok mu — o B grubunun bekçi
    değişikliğiyle entegrasyonda kapanır; burada yalnız kilidin GÖRDÜĞÜ
    doğrulanır. B bekçiyi yeniden yapılandırırsa bu test onu söyler.)"""
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(SKILLS))
    assert not any("kör" in u for u in uyarilar), uyarilar
    for h in hatalar:  # varsa yalnız K1 sınıfı olabilir
        assert "K1" in h, h


# ═══════════════ KİLİT-B — KANONİK↔doktrin ═════════════════════════════════

def _illiyet_koku(tmp, kanonik_kod, doktrin_metin):
    kok = tmp / "skills"
    (kok / "oa-illiyet" / "scripts").mkdir(parents=True)
    (kok / "oa-illiyet" / "references").mkdir()
    (kok / "oa-illiyet" / "scripts" / "grafik_denetim.py").write_text(
        kanonik_kod, encoding="utf-8")
    if doktrin_metin is not None:
        (kok / "oa-illiyet" / "references" / "illiyet-doktrini.md").write_text(
            doktrin_metin, encoding="utf-8")
    return kok


_KANONIK_KOD = textwrap.dedent('''\
    KANONIK = {
        "kesme_flag": {"mucbir_sebep", "magdur_kusuru", "ceza:izin_verilen_risk"},
        "guc": {"guclu", "zayif"},
    }
''')


def test_kilit_b_eksik_deger_hata(tmp):
    """Enum'da olup doktrinde LİTERAL geçmeyen değer → HATA (alan + değer adıyla)."""
    kok = _illiyet_koku(tmp, _KANONIK_KOD,
                        "## 6. Şema\nkesme_flag: mucbir_sebep | magdur_kusuru\n"
                        "guc: guclu | zayif\n")
    hatalar, uyarilar = ad.kanonik_doktrin_uyum(str(kok))
    assert uyarilar == []
    assert hatalar == ["enum↔doktrin ayrışması: kesme_flag 'ceza:izin_verilen_risk' "
                       "doktrinde yok (illiyet-doktrini.md)"]


def test_kilit_b_tam_uyum_temiz(tmp):
    kok = _illiyet_koku(tmp, _KANONIK_KOD,
                        "kesme_flag: mucbir_sebep | magdur_kusuru | "
                        "ceza:izin_verilen_risk\nguc: guclu | zayif\n")
    assert ad.kanonik_doktrin_uyum(str(kok)) == ([], [])


def test_kilit_b_doktrin_yoksa_hata(tmp):
    kok = _illiyet_koku(tmp, _KANONIK_KOD, None)
    hatalar, _ = ad.kanonik_doktrin_uyum(str(kok))
    assert len(hatalar) == 1 and "illiyet-doktrini.md yok" in hatalar[0]


def test_kilit_b_yuklenemezse_uyari(tmp):
    """grafik_denetim.py import edilemiyorsa (sözdizimi hatası / KANONIK yok)
    ÇÖKME değil UYARI — sessiz atlama yasağı, ama paketleme de kilitlenmez."""
    kok = _illiyet_koku(tmp, "def bozuk(:\n", "x")
    hatalar, uyarilar = ad.kanonik_doktrin_uyum(str(kok))
    assert hatalar == []
    assert len(uyarilar) == 1 and "yüklenemedi" in uyarilar[0]
    kok2 = _illiyet_koku(tmp / "b", "BASKA = 1\n", "x")
    hatalar, uyarilar = ad.kanonik_doktrin_uyum(str(kok2))
    assert hatalar == [] and len(uyarilar) == 1


def test_kilit_b_script_yoksa_sessiz(tmp):
    kok = tmp / "skills"
    kok.mkdir()
    assert ad.kanonik_doktrin_uyum(str(kok)) == ([], [])


def test_kilit_b_gercek_depo_olcum():
    """ÖLÇÜM (main 80ac847, 2026-09-06): grafik_denetim.KANONIK'in 23 değerinin
    23'ü illiyet-doktrini.md'de literal geçiyor → 0 ayrışma. A grubu doktrine
    yeni enum eklerse (ör. ceza kesme bayrakları) ve doktrini güncellemezse bu
    test + aile_dogrula kırmızıya düşer — istenen davranış."""
    hatalar, uyarilar = ad.kanonik_doktrin_uyum(str(SKILLS))
    assert uyarilar == [], uyarilar
    assert hatalar == [], "\n".join(hatalar)


# ═══════════════ P2-10 / B-3 — SÜRÜM İŞARETÇİLERİ ══════════════════════════

def test_surum_isaretcileri():
    """P2-10 / B-3: STATUS.md «**Sürüm:** X» ve YOL-HARITASI.md «## DURUM — son
    (… · vX)» sürümü plugin.json «version» ile EŞİT olmalı.

    BİLİNÇLİ KIRMIZI (main 80ac847): STATUS.md = 0.5.11, YOL-HARITASI.md =
    0.5.8.4, plugin.json = 0.5.15. Bu dosyalar G grubunun sahipliği DIŞINDADIR
    (DOKUNMA listesi); entegratör v0.5.16 bump'ında iki işaretçiyi de
    plugin.json'a hizaladığında test yeşile döner. xfail KULLANILMADI: kırmızı
    görünür kalmalı (sessiz atlama yasağı)."""
    pv = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    status = (REPO / "STATUS.md").read_text(encoding="utf-8", errors="replace")
    yol = (REPO / "YOL-HARITASI.md").read_text(encoding="utf-8", errors="replace")
    ms = ad._STATUS_SURUM_RE.search(status)
    my = ad._YOL_DURUM_SURUM_RE.search(yol)
    assert ms, "STATUS.md'de «**Sürüm:** X» satırı yok"
    assert my, "YOL-HARITASI.md'de «## DURUM — son (… · vX)» satırı yok"
    assert ms.group(1) == pv, f"STATUS.md Sürüm={ms.group(1)} ↔ plugin.json={pv}"
    assert my.group(1) == pv, f"YOL-HARITASI.md DURUM v{my.group(1)} ↔ plugin.json={pv}"


def _depo_iskeleti(tmp, plugin_surum, status_surum, yol_surum):
    depo = tmp / "depo"
    kok = depo / "plugins" / "ortak-avukat" / "skills"
    kok.mkdir(parents=True)
    (depo / "plugins" / "ortak-avukat" / ".claude-plugin").mkdir()
    (depo / "plugins" / "ortak-avukat" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "ortak-avukat", "version": plugin_surum}), encoding="utf-8")
    (depo / "STATUS.md").write_text(
        f"# DURUM\n\n**Tarih:** 2099-01-01 · **Sürüm:** {status_surum} · **Commit:** `abc`\n",
        encoding="utf-8")
    (depo / "YOL-HARITASI.md").write_text(
        f"# Yol\n\n## DURUM — son (2099-01-01 · v{yol_surum})\n- x\n", encoding="utf-8")
    return kok


def test_surum_isaretcileri_aile_dogrula_uyari(tmp):
    """aile_dogrula'daki aynı denetim UYARI sınıfındadır (hata değil):
    bayat işaretçi paketlemeyi durdurmaz ama görünür kalır."""
    kok = _depo_iskeleti(tmp, "0.5.16", "0.5.11", "0.5.8.4")
    u = ad.surum_isaretcileri(str(kok))
    assert len(u) == 2, u
    assert any("STATUS.md" in x and "0.5.11" in x and "0.5.16" in x for x in u)
    assert any("YOL-HARITASI.md" in x and "0.5.8.4" in x for x in u)


def test_surum_isaretcileri_hizali_temiz(tmp):
    kok = _depo_iskeleti(tmp, "0.5.16", "0.5.16", "0.5.16")
    assert ad.surum_isaretcileri(str(kok)) == []


def test_surum_isaretcileri_depo_disi_sessiz(tmp):
    """Depo-dışı kopyada (plugin.json / STATUS.md yok) sessiz."""
    kok = tmp / "skills"
    kok.mkdir()
    assert ad.surum_isaretcileri(str(kok)) == []


# ═══════════════ CLI — gerçek ağacın kopyası: K1 tek kırmızı mı? ═══════════

def test_cli_kopya_bekci_yildiz_json_ile_temiz(tmp):
    """Gerçek skills ağacının tempfile KOPYASINDA üç bekçi desenini `*.json`
    yapınca aile_dogrula exit 0 vermeli. Bu, (1) bugünkü tek kırmızının K1
    olduğunu ve (2) B grubunun `*.json`+damga bekçisiyle entegrasyonda kapının
    yeşile döneceğini kanıtlar. Gerçek depo değişmez. (Kopyada plugin.json /
    STATUS.md yok → manifest ve sürüm işaretçisi denetimleri sessiz atlanır.)"""
    hedef = tmp / "skills"
    shutil.copytree(SKILLS, hedef)
    pk = hedef / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
    metin = pk.read_text(encoding="utf-8")
    yeni = re.sub(r'glob\.glob\(os\.path\.join\(cdiz, "\*(?:graf|kiyas|usul)\*\.json"\)\)',
                  'glob.glob(os.path.join(cdiz, "*.json"))', metin)
    pk.write_text(yeni, encoding="utf-8")
    cp = subprocess.run([sys.executable, str(AILE_DOGRULA), str(hedef)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    cikti = (cp.stdout or "") + (cp.stderr or "")
    assert cp.returncode == 0, cikti
    assert "AİLE YAPI DENETİMİ TEMİZ" in cikti


def test_cli_kopya_kanonik_enum_eklenince_kirmizi(tmp):
    """Uçtan uca: kopyada KANONIK'e doktrinde olmayan bir değer eklenirse CLI
    exit 1 ve mesaj değeri adıyla söyler."""
    hedef = tmp / "skills"
    shutil.copytree(SKILLS, hedef)
    gd = hedef / "oa-illiyet" / "scripts" / "grafik_denetim.py"
    metin = gd.read_text(encoding="utf-8")
    assert '"kesme_flag": {"mucbir_sebep", "magdur_kusuru", "ucuncu_kisi_kusuru"}' in metin
    gd.write_text(metin.replace(
        '"kesme_flag": {"mucbir_sebep", "magdur_kusuru", "ucuncu_kisi_kusuru"}',
        '"kesme_flag": {"mucbir_sebep", "magdur_kusuru", "ucuncu_kisi_kusuru", '
        '"sentetik:olmayan_bayrak"}'), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(AILE_DOGRULA), str(hedef)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    cikti = (cp.stdout or "") + (cp.stderr or "")
    assert cp.returncode == 1
    assert "enum↔doktrin ayrışması: kesme_flag 'sentetik:olmayan_bayrak'" in cikti


# ═══════════════ P2-8 / A-27 / A-28 — HATA TETİKLİ DAMITMA belgesi ═════════

def test_skill_md_hata_tetikli_damitma():
    """oa-usta SKILL.md'de bölüm var; tetik (revize diff + avukat hükmü defteri),
    eşik/oran yokluğu + görünür sayım ve SICRAMA-NOTU §5 şartı yazılı."""
    m = USTA_SKILL.read_text(encoding="utf-8")
    assert "## HATA TETİKLİ DAMITMA" in m
    assert "_oa/defter/avukat-hukmu.jsonl" in m
    assert "--avukat-hukmu" in m and "REVIZYONLA" in m and "RET" in m
    assert "revize" in m.lower() and "diff" in m
    assert "eşik/oran YOK" in m and "sayım GÖRÜNÜR" in m
    assert "§5" in m and "silinmeyi hak eder" in m
    # damıtma tetiği artık yalnız tekrar sayacı değil
    assert "tek bir avukat revizesi" in m


def test_skill_md_aile_denetimi_yeni_kilitleri_anar():
    m = USTA_SKILL.read_text(encoding="utf-8")
    assert "bekçi↔skill sözleşmesi (K1)" in m
    assert "KANONİK↔doktrin" in m
    assert "sürüm işaretçisi (P2-10/B-3)" in m


def test_aile_dogrula_docstring_ve_utf8_guard():
    src = AILE_DOGRULA.read_text(encoding="utf-8")
    assert "__OA_UTF8_GUARD__" in src
    assert "KİLİT-A" in src and "KİLİT-B" in src
    # ağ import'u yok (aile_dogrula'nın kendi kuralı kendine de uygulanır)
    assert not re.search(r"^\s*(?:from|import)\s+(requests|httpx|socket|urllib\.request)\b",
                         src, re.M)
