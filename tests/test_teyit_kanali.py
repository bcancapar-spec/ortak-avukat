# -*- coding: utf-8 -*-
"""2026-10-15 avukat kararı — HİBRİT TEYİT KANALI: resmî kaynak beyaz listesi + kapılar.

NEDEN VAR: içtihat ve mevzuat teyidi v0.6.0'a kadar tek bir üçüncü taraf MCP
sunucusuna bağlıydı; avukat kararıyla (2026-10-15) o ilan ve tüm anmaları
kaldırıldı. Anayasa m.5 "resmî kaynaktan teyit edilmeyen içtihat yoktur" der;
kanal değişince kanıt da değişir: teyidin kanıtı artık RESMÎ PORTALIN ADRESİ
(beyaz liste) + diske inmiş tam metindir. Kapılar fail-closed'dur: adres yoksa
ya da listede değilse teyit yoktur.

Kilitler:
  (a) beyaz liste tek kaynaktır: `kunye_ortak.RESMI_KAYNAKLAR` + `resmi_kaynak_mi()`;
      avukatın okuyacağı `ortak-avukat/references/resmi-kaynaklar.md` her alan adını
      listeler (kod ↔ belge ayrışmaz);
  (b) `oa_hafiza.py teyit`: GETİR sınıfı (ictihat_getir, kurum_karari_getir, WebFetch)
      ve mevzuat_getir / resmi_gazete_getir için `--kaynak-url` ZORUNLU ve beyaz
      listeli; ARAMA sınıfında isteğe bağlı, verilirse beyaz listeli;
  (c) araç sözlüğü üçüncü taraf MCP araç adlarını taşımaz; genel web araçları
      sınıflıdır (WebFetch → GETİR: damga ister; WebSearch → ARAMA);
  (d) `ictihat_muhakeme_denetim.py` [G7]: dilekçeye dayanak olan muhakeme kaydının
      KAYNAK-URL'i yoksa ya da beyaz liste dışıysa TESLİM ENGELİ; dayanak olmayan
      kayıtta görünür UYARI;
  (e) eklenti hiçbir MCP sunucusu ilan etmez (`plugin.json`, `marketplace.json`,
      `.mcp.json` yok).
Sentetik veri; ağsız (adresler yalnız dize olarak denetlenir, hiçbir adrese gidilmez).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
EKLENTI = REPO / "plugins" / "ortak-avukat"
SKILLS = EKLENTI / "skills"
OA_HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
KUNYE_ORTAK = SKILLS / "oa-kontrol" / "scripts" / "kunye_ortak.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"
RESMI_KAYNAKLAR_MD = SKILLS / "ortak-avukat" / "references" / "resmi-kaynaklar.md"

RESMI_URL = "https://mevzuat.adalet.gov.tr/ictihat/sentetik-karar-1"
MEVZUAT_URL = "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6100&MevzuatTur=1&MevzuatTertip=5"
YABANCI_URL = "https://ornek-ucuncu-taraf.example.com/mcp/karar/1"

ALINTI = ("Borclunun mal kacirma kastiyla hareket ettigi ve tasarrufun ivazsiz "
          "oldugu dosya kapsamiyla sabittir.")
BAG = ("Somut olayda da tasarruf ivazsiz olup borclunun kastini gosterir; "
       "muvekkil lehine dogrudan uygulanabilir niteliktedir.")


def _yukle(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ko():
    return _yukle(KUNYE_ORTAK, "_kunye_ortak_teyit_kanali")


@pytest.fixture(scope="module")
def oh():
    return _yukle(OA_HAFIZA, "_oa_hafiza_teyit_kanali")


# ── (a) beyaz liste ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6100&MevzuatTur=1&MevzuatTertip=5",
    "https://mevzuat.gov.tr/MevzuatMetin/1.5.6100.pdf",
    "https://www.resmigazete.gov.tr/eskiler/2026/01/20260101.htm",
    "https://mevzuat.adalet.gov.tr/ictihat/sentetik-1",
    "https://karararama.yargitay.gov.tr/karar/1",
    "https://www.yargitay.gov.tr/kategori/1/icerik/1",
    "https://emsal.uyap.gov.tr/BilgiBankasiIstemciWeb/",
    "https://karararama.danistay.gov.tr/karar/1",
    "https://kararlarbilgibankasi.anayasa.gov.tr/BB/2019/1",
    "https://normkararlarbilgibankasi.anayasa.gov.tr/ND/2022/79",
    "https://www.uyusmazlik.gov.tr/karar/1",
    "https://hudoc.echr.coe.int/eng?i=001-000001",
    "https://www.barobirlik.org.tr/Haberler/aaut-tarifesi",
    "https://www.kvkk.gov.tr/Icerik/1/karar",
])
def test_resmi_kaynak_mi_beyaz_listedeki_adresi_kabul_eder(ko, url):
    assert ko.resmi_kaynak_mi(url) is True, url


@pytest.mark.parametrize("url", [
    YABANCI_URL,
    "https://mevzuat.gov.tr.evil.example/x",          # sahte alt alan adı
    "https://example.com/gov.tr/karar",                # yol içinde gov.tr
    "https://karararama.yargitay.gov.tr.sahte.net/1",  # sondan ekleme
    "http://kararara.example.net/karar/1",             # özel içtihat sitesi
    "javascript:alert(1)",
    "",
    None,
])
def test_resmi_kaynak_mi_liste_disini_reddeder(ko, url):
    assert ko.resmi_kaynak_mi(url) is False, url


def test_beyaz_liste_avukat_belgesiyle_ozdes(ko):
    """Kod ↔ belge tek kaynak: avukatın okuduğu referans her alan adını taşır."""
    assert RESMI_KAYNAKLAR_MD.is_file(), "ortak-avukat/references/resmi-kaynaklar.md yok"
    metin = RESMI_KAYNAKLAR_MD.read_text(encoding="utf-8")
    assert len(ko.RESMI_KAYNAKLAR) >= 12
    for k in ko.RESMI_KAYNAKLAR:
        assert k["alan"] in metin, "belgede eksik alan adı: %s" % k["alan"]
        assert k["ad"] in metin, "belgede eksik kaynak adı: %s" % k["ad"]
    assert ".gov.tr" in metin, "genel .gov.tr kuralı belgede yazılı olmalı"


# ── (c) araç sözlüğü ─────────────────────────────────────────────────────────

def test_arac_sozlugu_ucuncu_taraf_mcp_adlari_tasimaz(oh):
    yasak_onekler = ("search_bedesten", "get_bedesten", "get_anayasa", "search_anayasa",
                     "agentic_legal", "legal_research_guide", "reklam_bulten",
                     "sigorta_dergi", "spk_icinde")
    kirli = sorted(a for a in oh.BILINEN_ARACLAR if a.startswith(yasak_onekler))
    assert kirli == [], "üçüncü taraf araç adı sözlükte: %s" % kirli


def test_web_araclari_siniflidir(oh):
    assert "WebFetch" in oh.GETIR_ARACLARI
    assert "WebSearch" in oh.ARAMA_ARACLARI
    assert oh._arac_normalize_ve_dogrula("web_fetch")[0] == "WebFetch"
    assert oh._arac_normalize_ve_dogrula("websearch")[0] == "WebSearch"
    assert {"ictihat_getir", "kurum_karari_getir", "WebFetch", "mevzuat_getir",
            "resmi_gazete_getir"} <= set(oh.URL_ZORUNLU_ARACLAR)


# ── (b) teyit komutu ─────────────────────────────────────────────────────────

def _kos(args, kok):
    cp = subprocess.run([sys.executable, str(OA_HAFIZA)] + args, capture_output=True,
                        text=True, encoding="utf-8", errors="replace", cwd=str(kok))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def kok(tmp_path):
    kod, cikti = _kos(["init", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, cikti
    (tmp_path / "dokum.txt").write_text(
        "Yargitay 17. Hukuk Dairesi 2019/1234 E. 2021/5678 K.\n" + ALINTI + "\n",
        encoding="utf-8")
    return tmp_path


def _getir_args(kok, arac="ictihat_getir", ek=None):
    return ["teyit", "--kok", str(kok), "--arac", arac,
            "--sorgu", "tasarrufun iptali ivazsiz",
            "--sonuc", "Yargitay 17. HD 2019/1234 E. 2021/5678 K.",
            "--dokum-icerik", "@" + str(kok / "dokum.txt"),
            "--damga", "LEHE", "--ilgili-kisim", ALINTI, "--bag", BAG] + (ek or [])


def _muhakeme(kok):
    yol = kok / "_oa" / "cikti" / "03-ictihat-muhakeme.md"
    return yol.read_text(encoding="utf-8") if yol.is_file() else ""


def test_getir_sinifinda_kaynak_url_zorunlu(kok):
    """Adres yoksa teyit yoktur: fail-closed, muhakeme kaydı doğmaz."""
    kod, cikti = _kos(_getir_args(kok), kok)
    assert kod != 0, cikti
    assert "--kaynak-url" in cikti and "resm" in cikti.lower(), cikti
    assert _muhakeme(kok) == "", "RET'te muhakeme kaydı yazılmamalı"


def test_getir_beyaz_liste_disi_adres_reddedilir(kok):
    kod, cikti = _kos(_getir_args(kok, ek=["--kaynak-url", YABANCI_URL]), kok)
    assert kod != 0, cikti
    assert "beyaz liste" in cikti.lower(), cikti
    assert _muhakeme(kok) == ""


def test_getir_beyaz_liste_adresiyle_kabul(kok):
    kod, cikti = _kos(_getir_args(kok, ek=["--kaynak-url", RESMI_URL]), kok)
    assert kod == 0, cikti
    assert "**KAYNAK-URL:** %s" % RESMI_URL in _muhakeme(kok)


def test_webfetch_getir_sinifidir_damga_ister(kok):
    """Genel web aracıyla çekilen tam metin de aynı disipline tabidir: damgasız olmaz."""
    kod, cikti = _kos(["teyit", "--kok", str(kok), "--arac", "WebFetch",
                       "--sorgu", "tasarrufun iptali ivazsiz",
                       "--sonuc", "Yargitay 17. HD 2019/1234 E. 2021/5678 K.",
                       "--kaynak-url", RESMI_URL], kok)
    assert kod != 0, cikti
    assert "--damga" in cikti, cikti


def test_mevzuat_getir_kaynak_url_zorunlu_ve_beyaz_listeli(kok):
    temel = ["teyit", "--kok", str(kok), "--arac", "mevzuat_getir",
             "--sorgu", "HMK m.107", "--sonuc", "HMK m.107 metni okundu"]
    kod, cikti = _kos(temel, kok)
    assert kod != 0 and "--kaynak-url" in cikti, cikti
    kod, cikti = _kos(temel + ["--kaynak-url", YABANCI_URL], kok)
    assert kod != 0 and "beyaz liste" in cikti.lower(), cikti
    kod, cikti = _kos(temel + ["--kaynak-url", MEVZUAT_URL], kok)
    assert kod == 0, cikti


def test_arama_sinifinda_url_istege_bagli_ama_beyaz_listeli(kok):
    temel = ["teyit", "--kok", str(kok), "--arac", "ictihat_ara",
             "--sorgu", "tasarrufun iptali", "--sonuc", "12 sonuç"]
    kod, cikti = _kos(temel, kok)
    assert kod == 0, cikti
    kod, cikti = _kos(temel + ["--kaynak-url", YABANCI_URL], kok)
    assert kod != 0 and "beyaz liste" in cikti.lower(), cikti


# ── (d) [G7] muhakeme kaydının adresi ───────────────────────────────────────

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"


def _denetim_koku(kaynak_url):
    kok = pathlib.Path(tempfile.mkdtemp())
    dokum = kok / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True)
    (dokum / "kaynak.md").write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 tam metni...\n", encoding="utf-8")
    (kok / "_oa" / "teyit" / "kunye-teyit.md").write_text(
        "# Künye Teyit Kütüğü\n| 2026-10-15T10:00:00 | ictihat_getir | sorgu | "
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 DAMGA=LEHE DOKUM-SINIFI=tam-metin | "
        "[döküm](_oa/teyit/dokum/kaynak.md) |\n", encoding="utf-8")
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    satirlar = ["# 01 — İçtihat Muhakeme Kaydı", "", "**KUNYE:** %s" % KUNYE,
                "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md", "**DAMGA:** LEHE", ""]
    if kaynak_url:
        satirlar.insert(4, "**KAYNAK-URL:** %s" % kaynak_url)
    satirlar += ["## İLGİLİ-KISIM", "...ilgili kısım...", "",
                 "## DAVAYA-BAĞ", "...davaya bağ açıklaması (kırk karakteri aşan "
                 "gerçekçi bir bağ cümlesi)...", "", "## AYIRT-ETME", "", ""]
    (cikti / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")
    return kok


def _denetim(kok, govde):
    taslak = kok / "taslak.md"
    taslak.write_text(govde, encoding="utf-8")
    cp = subprocess.run([sys.executable, str(DENETIM), str(taslak), "--kok", str(kok)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


ATIF = ("Somut olayda Yargıtay 4. HD'nin E. 2023/1234, K. 2023/5678 sayılı kararı "
        "(%s) emsaldir.\n")


def test_g7_dayanak_kaydinin_adresi_yoksa_teslim_engeli():
    kok = _denetim_koku(kaynak_url=None)
    kod, cikti = _denetim(kok, "Somut olayda Yargıtay 4. HD'nin E. 2023/1234, "
                               "K. 2023/5678 sayılı kararı emsaldir.\n")
    assert kod != 0, cikti
    assert "[G7]" in cikti and "TESLİM ENGELİ" in cikti, cikti


def test_g7_beyaz_liste_disi_adres_teslim_engeli():
    kok = _denetim_koku(kaynak_url=YABANCI_URL)
    kod, cikti = _denetim(kok, ATIF % YABANCI_URL)
    assert kod != 0, cikti
    assert "[G7]" in cikti, cikti


def test_g7_beyaz_liste_adresi_temiz():
    kok = _denetim_koku(kaynak_url="https://karararama.yargitay.gov.tr/karar/12345")
    kod, cikti = _denetim(kok, ATIF % "https://karararama.yargitay.gov.tr/karar/12345")
    assert kod == 0, cikti
    assert "TESLİM ENGELİ" not in cikti


# ── (e) eklenti MCP ilan etmez ───────────────────────────────────────────────

def test_eklenti_hicbir_mcp_sunucusu_ilan_etmez():
    pj = json.loads((EKLENTI / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert not pj.get("mcpServers"), "plugin.json MCP sunucusu ilan ediyor: %s" % pj.get("mcpServers")
    mp = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    for p in mp.get("plugins", []):
        assert "mcpServers" not in p
    assert not (EKLENTI / ".mcp.json").exists() and not (REPO / ".mcp.json").exists()
    for yol in (EKLENTI / ".claude-plugin" / "plugin.json", REPO / ".claude-plugin" / "marketplace.json"):
        assert "betaspacestudio" not in yol.read_text(encoding="utf-8")


# ── (f) heyet 2026-10-17 üçüncü koşum GÜVENLİK U-2 — adres de Layer 0'dan geçer ─────────────────────

TCKN_SENTETIK = "10000000146"        # sağlama geçen sentetik numara (tests/test_gizlilik.py ile aynı)
KIMLIK_SENTETIK = "12345678901"      # 11 hane ama sağlama GEÇMEZ: karar kimliği gibi meşru bir dizi


def _oa_metinlerinde_gecer_mi(kok, parca):
    for p in (kok / "_oa").rglob("*"):
        if p.is_file() and p.suffix in (".md", ".json", ".jsonl", ".txt"):
            if parca in p.read_text(encoding="utf-8", errors="replace"):
                return True
    return False


def test_kaynak_url_sorgu_dizesinde_tckn_layer0_ret(kok):
    """NEDEN VAR (heyet 2026-10-17 GÜVENLİK U-2): Layer 0 yalnız `--sorgu`'yu tarıyordu; yeni kanalda zorunlu olan
    `--kaynak-url` resmî portala giden sorgu dizesi taşır ve dış araca gider — adresin yolu/sorgusu/parçası da
    müvekkil-tanımlayıcı veri taşıyamaz (anayasa m.10). Sağlama geçen TCKN adreste → RET; kütüğe/muhakemeye yazılmaz."""
    url = "https://mevzuat.adalet.gov.tr/ictihat/ara?q=" + TCKN_SENTETIK
    kod, cikti = _kos(_getir_args(kok, ek=["--kaynak-url", url]), kok)
    assert kod != 0, cikti
    assert "Layer 0" in cikti and "--kaynak-url" in cikti, cikti
    assert _muhakeme(kok) == "", "RET'te muhakeme kaydı yazılmamalı"
    assert not _oa_metinlerinde_gecer_mi(kok, TCKN_SENTETIK), "adresteki numara hiçbir kayda sızmamalı"


def test_kaynak_url_sorgu_onayli_ile_gecer(kok):
    url = "https://mevzuat.adalet.gov.tr/ictihat/ara?q=" + TCKN_SENTETIK
    kod, cikti = _kos(_getir_args(kok, ek=["--kaynak-url", url, "--sorgu-onayli"]), kok)
    assert kod == 0, cikti


def test_kaynak_url_saglama_gecmeyen_11_hane_karar_kimligi_engellenmez(kok):
    """Resmî portal karar kimlikleri de 11 haneli olabilir: sağlama geçmeyen dizi TCKN sayılmaz (yanlış engel yok)."""
    url = "https://mevzuat.adalet.gov.tr/ictihat/" + KIMLIK_SENTETIK
    kod, cikti = _kos(_getir_args(kok, ek=["--kaynak-url", url]), kok)
    assert kod == 0, cikti
    assert "**KAYNAK-URL:** %s" % url in _muhakeme(kok)
