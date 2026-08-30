# -*- coding: utf-8 -*-
"""v0.5.14 — PIPELINE + HOOK + KİT GÜVENLİĞİ paketi (B-1, B-4, B-5, B-27, B-28).

Denetim raporu (DENETIM-CELISKI-KIRIK.md) bulguları:

- **B-1 (P0)** SERVİS EDİLEN NESİL ≠ DENETLENEN NESİL. Bu makinede ölçüldü:
  depo `plugin.json` = 0.5.13, kurulu önbellek = 0.5.9.1, rpm anlık görüntüsü
  (`…/local-agent-mode-sessions/…/rpm/plugin_01SKxz…`) = **0.5.0**; buna
  rağmen `hook_doktor --kurulu` "TÜM MEKANİK KONTROLLER GEÇTİ ✓" + exit 0
  basıyordu. Kodda depo↔servis sürüm karşılaştırması YOKTU.
- **B-4 (P0)** SUNUM KİLİDİ kök keşfi yalnız `tool_input.file_path` okuyordu;
  `SendUserFile` payload'ı ise `tool_input.files` listesi taşır → oturum dava
  klasörünün DIŞINDAYSA kapı sessizce ölüydü (EXIT=0, çıktı yok).
- **B-5 (P0)** Bayat-araç nöbetçisi NEGATİF parmak izine dayanıyordu: parmak
  izi tam ama nesli eski bir kit "kanaldan YENİ … bayat DEĞİLDİR, tazeleme
  gerekmez" ilan ediliyor, üstüne salt-okunur çivileniyordu.
- **B-27** `aile_dogrula.py --help` exit 1 döndürüyordu (32 scriptten tek).
- **B-28** Kıyas artefaktı için iki ad sözleşmesi (`05-kiyas*` önkoşulda,
  `*kiyas*.json` tüketicide) ve önkoşul İÇERİĞE değil BOYUTA bakıyordu.
"""
import importlib.util
import json
import os
import pathlib
import stat
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
DOKTOR = REPO / "tools" / "hook_doktor.py"
AILE_DOGRULA = SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"
PLUGIN_JSON = REPO / "plugins" / "ortak-avukat" / ".claude-plugin" / "plugin.json"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _yukle("pipeline_kayit_v0514", PIPELINE)
hd = _yukle("hook_doktor_v0514", DOKTOR)

DEPO_SURUM = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]


def _sahte_plugin_koku(kok, surum, adi="ortak-avukat"):
    """Sentetik bir 'servis edilen' eklenti ağacı üretir."""
    kok = pathlib.Path(kok)
    (kok / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (kok / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": adi, "version": surum}), encoding="utf-8")
    return kok


# ═══════════════ B-1 — SERVİS EDİLEN NESİL DENETİMİ (hook_doktor) ═══════════

def test_b1_plugin_surumu_okunur():
    """`plugin_surumu()` bir eklenti kökünün plugin.json sürümünü döndürür."""
    assert hd.plugin_surumu(REPO / "plugins" / "ortak-avukat") == DEPO_SURUM


def test_b1_plugin_surumu_okunamayan_kokte_none(tmp_path):
    assert hd.plugin_surumu(tmp_path) is None


def test_b1_oa_surum_damgalari_depo_agacinda_depo_surumune_esit():
    """Makine-okur `OA_SURUM` damgaları depo plugin.json sürümüyle aynı
    olmalı — 'denetlenen nesil' iddiasının tek kaynağı budur."""
    damgalar = hd.oa_surum_damgalari(REPO / "plugins" / "ortak-avukat")
    assert damgalar, "hiçbir OA_SURUM damgası bulunamadı"
    assert set(damgalar.values()) == {DEPO_SURUM}, damgalar


def test_b1_farkli_surumlu_servis_koku_YESIL_BASTIRMAZ(tmp_path):
    """B-1'in ta kendisi: servis edilen nesil depodan FARKLIYSA rapor
    hata döndürmeli (fail-closed) — 'kurulu 0.5.9.1 + TÜM KONTROLLER
    GEÇTİ' bir daha basılamaz."""
    kok = _sahte_plugin_koku(tmp_path / "kurulu", "0.5.9.1")
    satirlar, hata = hd.servis_mutabakati_raporu(
        DEPO_SURUM, [("kurulu", kok, "0.5.9.1", None)])
    assert hata is True
    assert any("0.5.9.1" in s for s in satirlar)


def test_b1_ayni_surumlu_servis_koku_temiz(tmp_path):
    kok = _sahte_plugin_koku(tmp_path / "kurulu", DEPO_SURUM)
    _satirlar, hata = hd.servis_mutabakati_raporu(
        DEPO_SURUM, [("kurulu", kok, DEPO_SURUM, None)])
    assert hata is False


def test_b1_okunamayan_servis_koku_FAIL_CLOSED(tmp_path):
    """'Denetleyemiyorsa YEŞİL BASMAMALI': servis kökü VAR ama sürümü
    okunamıyorsa bu bir bilinmezliktir, temiz değildir."""
    kok = tmp_path / "bozuk"
    (kok / ".claude-plugin").mkdir(parents=True)
    (kok / ".claude-plugin" / "plugin.json").write_text("{bozuk", encoding="utf-8")
    _satirlar, hata = hd.servis_mutabakati_raporu(
        DEPO_SURUM, [("kurulu", kok, None, "plugin.json okunamadı")])
    assert hata is True


def test_b1_hic_servis_koku_yoksa_temiz_ama_ACIKCA_soylenir():
    """Kurulum HİÇ yoksa (temiz klon / CI) bu belirli bir cevaptır: bayat
    nesil servis edilmiyor. Yeşil kalır ama sessiz kalmaz."""
    satirlar, hata = hd.servis_mutabakati_raporu(DEPO_SURUM, [])
    assert hata is False
    assert any("bulunamadı" in s.lower() for s in satirlar)


def test_b1_servis_kokleri_liste_dondurur():
    """`servis_kokleri()` ASLA fırlatmaz; (etiket, yol, surum, hata)
    dörtlülerinden oluşan bir liste döndürür."""
    kokler = hd.servis_kokleri()
    assert isinstance(kokler, list)
    for k in kokler:
        assert len(k) == 4


def test_b1_rpm_anlik_goruntusu_kesfedilir(tmp_path, monkeypatch):
    """Skill gövdelerinin geldiği ağaç: masaüstü uygulamasının rpm anlık
    görüntüsü. Denetimde orada 0.5.0 bulundu; keşif onu görmezse B-1'in
    en pahalı bacağı kapanmamış olur."""
    oturum = (tmp_path / "Claude" / "local-agent-mode-sessions"
              / "oturum" / "alt" / "rpm" / "plugin_01SKxz")
    _sahte_plugin_koku(oturum, "0.5.0")
    yabanci = (tmp_path / "Claude" / "local-agent-mode-sessions"
               / "oturum" / "alt" / "rpm" / "plugin_01ABCD")
    _sahte_plugin_koku(yabanci, "1.3.0", adi="legal")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    kokler = hd.servis_kokleri()
    surumler = {s for _e, _y, s, _h in kokler}
    assert "0.5.0" in surumler, kokler
    assert "1.3.0" not in surumler, "yabancı eklenti (legal) süzülmedi"


def test_b1_cli_servis_atla_bayragi_var():
    """Depo katmanını tek başına denetlemek isteyen (CI/temiz klon) için
    açık bayrak — sessiz varsayılan YOK."""
    cp = subprocess.run([sys.executable, str(DOKTOR), "--help"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(REPO))
    assert cp.returncode == 0
    assert "--servis-atla" in (cp.stdout or "")


# ═══════════════ B-4 — SUNUM KİLİDİ KÖK KEŞFİ (files[]) ════════════════════

def _dava_koku(tmp_path, ad="dava"):
    dava = tmp_path / ad
    (dava / "_oa" / "defter").mkdir(parents=True)
    (dava / "_oa" / "cikti").mkdir(parents=True, exist_ok=True)
    return dava


def test_b4_kok_kesfi_files_listesini_okur(tmp_path):
    """B-4: SendUserFile payload'ı `tool_input.files` taşır. Onarım öncesi
    kök adayları [] idi (yalnız `file_path` okunuyordu)."""
    dava = _dava_koku(tmp_path)
    urun = dava / "_oa" / "cikti" / "08-dilekce.udf"
    urun.write_bytes(b"x")
    payload = {"tool_name": "SendUserFile",
               "tool_input": {"files": [str(urun)]}}
    adaylar = pk._hook_kok_adaylarini_bul(None, payload=payload)
    assert str(dava.resolve()) in adaylar


def test_b4_kok_kesfi_files_tek_string_de_calisir(tmp_path):
    dava = _dava_koku(tmp_path)
    urun = dava / "_oa" / "cikti" / "08-dilekce.udf"
    urun.write_bytes(b"x")
    payload = {"tool_name": "SendUserFile",
               "tool_input": {"files": str(urun)}}
    adaylar = pk._hook_kok_adaylarini_bul(None, payload=payload)
    assert str(dava.resolve()) in adaylar


def test_b4_kok_kesfi_defter_yokken_de_dava_klasorunu_bulur(tmp_path):
    """Yukarı-arama ölçütü `_oa/defter` ile sınırlı kalmamalı: defter henüz
    doğmamış bir dava klasörü de (`_oa` var) aday olmalı."""
    dava = tmp_path / "dava2"
    (dava / "_oa").mkdir(parents=True)
    urun = dava / "dilekce.pdf"
    urun.write_bytes(b"x")
    payload = {"tool_name": "SendUserFile",
               "tool_input": {"files": [str(urun)]}}
    adaylar = pk._hook_kok_adaylarini_bul(None, payload=payload)
    assert str(dava.resolve()) in adaylar


def test_b4_dava_disi_gonderimde_gorunur_uyari(tmp_path):
    """Kök hiç bulunamadığında SESSİZ geçilmez: teslim-sınıfı adlı bir ürün
    gönderiliyorsa görünür bir 'ask' basılır (karar devri, engel değil)."""
    disari = tmp_path / "disari"
    disari.mkdir()
    urun = disari / "istinaf-dilekcesi.udf"
    urun.write_bytes(b"x")
    payload = {"tool_name": "SendUserFile",
               "tool_input": {"files": [str(urun)]}}
    cp = subprocess.run([sys.executable, str(PIPELINE), "--hook-pretool"],
                        input=json.dumps(payload), capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        cwd=str(disari))
    assert cp.returncode == 0, "hook ASLA bloklamaz"
    assert "permissionDecision" in (cp.stdout or ""), cp.stdout
    assert "DOĞRULANAMADI" in (cp.stdout or "")


def test_b4_dava_disi_sira_disi_dosyada_sessiz(tmp_path):
    """Yanlış-pozitif disiplini: teslim-sınıfı OLMAYAN dosya gönderiminde
    dava kökü yokken de çıktı basılmaz."""
    disari = tmp_path / "disari2"
    disari.mkdir()
    dosya = disari / "notlar.txt"
    dosya.write_text("x", encoding="utf-8")
    payload = {"tool_name": "SendUserFile",
               "tool_input": {"files": [str(dosya)]}}
    cp = subprocess.run([sys.executable, str(PIPELINE), "--hook-pretool"],
                        input=json.dumps(payload), capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        cwd=str(disari))
    assert cp.returncode == 0
    assert (cp.stdout or "").strip() == ""


# ═══════════════ B-5 — BAYAT KİT: POZİTİF SÜRÜM DOĞRULAMASI ════════════════

def _kit_yaz(dava, ad, icerik):
    araclar = dava / "_oa" / "araclar"
    araclar.mkdir(parents=True, exist_ok=True)
    yol = araclar / ad
    yol.write_text(icerik, encoding="utf-8")
    return yol


_PARMAK_IZI_TAM = ('OLAYLAR_ADI = "x"\n'
                   'def _hook_nabiz_damgala():\n    pass\n')


def test_b5_surum_damgasi_okunur():
    """Pozitif doğrulamanın çıpası: makine-okur `OA_SURUM` damgası."""
    assert pk._arac_surum_damgasi('OA_SURUM = "0.5.13"\n') == "0.5.13"
    assert pk._arac_surum_damgasi("damga yok") is None


def test_b5_surumsuz_kit_TAZE_ILAN_EDILMEZ(tmp_path):
    """B-5'in ta kendisi: parmak izi TAM ama sürüm damgası YOK olan kopya
    'kanaldan YENİ … tazeleme gerekmez' diye ilan EDİLEMEZ."""
    dava = _dava_koku(tmp_path, "kit1")
    _kit_yaz(dava, "pipeline_kayit.py", _PARMAK_IZI_TAM)
    metin = pk._bayat_arac_uyarisi(str(dava)) or ""
    assert "tazeleme gerekmez" not in metin
    assert "doğrulanamadı" in metin


def test_b5_eski_surumlu_kit_BAYAT_sayilir(tmp_path):
    """Sürüm damgası VAR ama eklentininkinden ESKİ → bayat; 'yeni' dalına
    düşemez."""
    dava = _dava_koku(tmp_path, "kit2")
    _kit_yaz(dava, "pipeline_kayit.py",
             'OA_SURUM = "0.5.9.1"\n' + _PARMAK_IZI_TAM)
    metin = pk._bayat_arac_uyarisi(str(dava)) or ""
    assert "tazeleme gerekmez" not in metin
    assert "0.5.9.1" in metin


def test_b5_yeni_surumlu_kit_kanit_ile_yeni_ilan_edilir(tmp_path):
    """Pozitif kanıt varsa (damga ≥ eklenti sürümü) 'kanaldan YENİ' hükmü
    meşrudur — yön ayrımı korunur, ama artık KANITA dayanır."""
    dava = _dava_koku(tmp_path, "kit3")
    _kit_yaz(dava, "pipeline_kayit.py",
             'OA_SURUM = "%s"\n' % pk.OA_SURUM + _PARMAK_IZI_TAM)
    metin = pk._bayat_arac_uyarisi(str(dava)) or ""
    assert "kanaldan YENİ" in metin
    assert pk.OA_SURUM in metin


def test_b5_cekirdek_kilitle_surum_kanitsiz_kilitlemez(tmp_path):
    """B-5 ikinci yarısı: bayat çekirdeği salt-okunur çivilemek tazelemeyi
    de imkânsız kılıyordu. Sürüm kanıtı yoksa KİLİTLENMEZ."""
    dava = _dava_koku(tmp_path, "kit4")
    yol = _kit_yaz(dava, "pipeline_kayit.py", _PARMAK_IZI_TAM)
    kilitlenen = pk._cekirdek_kilitle(str(dava))
    assert kilitlenen == 0
    assert os.stat(yol).st_mode & stat.S_IWRITE, "sürüm kanıtsız kit çivilendi"


def test_b5_cekirdek_kilitle_surum_kanitliysa_kilitler(tmp_path):
    dava = _dava_koku(tmp_path, "kit5")
    yol = _kit_yaz(dava, "pipeline_kayit.py",
                   'OA_SURUM = "%s"\n' % pk.OA_SURUM + _PARMAK_IZI_TAM)
    try:
        kilitlenen = pk._cekirdek_kilitle(str(dava))
        assert kilitlenen == 1
        assert not (os.stat(yol).st_mode & stat.S_IWRITE)
    finally:
        os.chmod(yol, stat.S_IWRITE | stat.S_IREAD)


def test_b5_version_json_beyani_artefakt_ile_dogrulanir(tmp_path):
    """Ailenin kendi doktrini: 'makbuz artefakta bağlanır, beyana değil'.
    VERSION.json güncel sürümü BEYAN ederken çantadaki çekirdek o sürümü
    taşımıyorsa uyarı susmaz."""
    dava = _dava_koku(tmp_path, "kit6")
    _kit_yaz(dava, "pipeline_kayit.py",
             'OA_SURUM = "0.5.9.1"\n' + _PARMAK_IZI_TAM)
    (dava / "_oa" / "araclar" / "VERSION.json").write_text(
        json.dumps({"surum": pk.OA_SURUM}), encoding="utf-8")
    metin = pk._arac_version_uyarisi(str(dava)) or ""
    assert metin, "yalan beyan sessizce kabul edildi"
    assert "0.5.9.1" in metin


def test_b5_version_json_beyani_dogruysa_susar(tmp_path):
    dava = _dava_koku(tmp_path, "kit7")
    _kit_yaz(dava, "pipeline_kayit.py",
             'OA_SURUM = "%s"\n' % pk.OA_SURUM + _PARMAK_IZI_TAM)
    (dava / "_oa" / "araclar" / "VERSION.json").write_text(
        json.dumps({"surum": pk.OA_SURUM}), encoding="utf-8")
    assert pk._arac_version_uyarisi(str(dava)) is None


# ═══════════════ B-28 — KIYAS ARTEFAKTI: TEK SÖZLEŞME + İÇERİK ═════════════

_KIYAS_GECERLI = {"arac": "kiyas_denetim", "kritik_bosluk": False,
                  "unsur_vakia_eslesme": [{"unsur_id": "U1", "durum": "karsilanan_delilli"}],
                  "teyitsiz_ictihat": []}


def _muhakeme_yaz(dava):
    (dava / "_oa" / "cikti" / "06-ictihat-muhakeme.md").write_text(
        "İçtihat muhakemesi gövdesi " * 20, encoding="utf-8")


def test_b28_01_kiyas_json_da_onkosulu_karsilar(tmp_path):
    """B-28: tüketici `*kiyas*.json` okurken önkoşul yalnız `05-kiyas*`
    arıyordu — `01-kiyas.json` üreten model haksız yere bloklanıyordu."""
    dava = _dava_koku(tmp_path, "k1")
    (dava / "_oa" / "cikti" / "01-kiyas.json").write_text(
        json.dumps(_KIYAS_GECERLI), encoding="utf-8")
    _muhakeme_yaz(dava)
    tamam, eksik = pk._kiyas_onkosul_saglam_mi(str(dava))
    assert tamam is True, eksik


def test_b28_govdesi_dolu_ama_gecersiz_json_reddedilir(tmp_path):
    """Ters yön (daha kötü): 400 harflik 'A' dolgusu boyut kapısını geçiyor
    ve önkoşul (True, None) diyordu."""
    dava = _dava_koku(tmp_path, "k2")
    (dava / "_oa" / "cikti" / "05-kiyas.json").write_text(
        "A" * 400, encoding="utf-8")
    _muhakeme_yaz(dava)
    tamam, eksik = pk._kiyas_onkosul_saglam_mi(str(dava))
    assert tamam is False
    assert "kiyas" in (eksik or "")


def test_b28_yanlis_arac_json_reddedilir(tmp_path):
    """Geçerli JSON ama `arac != kiyas_denetim` → kıyas artefaktı değildir."""
    dava = _dava_koku(tmp_path, "k3")
    (dava / "_oa" / "cikti" / "05-kiyas.json").write_text(
        json.dumps({"arac": "vakia_matris", "x": "y" * 400}), encoding="utf-8")
    _muhakeme_yaz(dava)
    tamam, _eksik = pk._kiyas_onkosul_saglam_mi(str(dava))
    assert tamam is False


def test_b28_markdown_calisma_evraki_kabul_edilmeye_devam_eder(tmp_path):
    """Geriye uyum: kıyas çalışma evrakı .md olarak yazıldığında (mevcut
    saha deseni) önkoşul AYNEN geçer — içerik kapısı yalnız .json'a."""
    dava = _dava_koku(tmp_path, "k4")
    (dava / "_oa" / "cikti" / "05-kiyas-test.md").write_text(
        "Kıyas gövdesi " * 20, encoding="utf-8")
    _muhakeme_yaz(dava)
    tamam, eksik = pk._kiyas_onkosul_saglam_mi(str(dava))
    assert tamam is True, eksik


# ═══════════════ B-27 — aile_dogrula --help exit 0 ═════════════════════════

def test_b27_aile_dogrula_help_exit0():
    """32 scriptten tek istisna: `--help` exit 1 döndürüyordu; otomatik
    keşif yapan üst katman aracı 'bozuk/yok' sayabilir."""
    for bayrak in ("-h", "--help"):
        cp = subprocess.run([sys.executable, str(AILE_DOGRULA), bayrak],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=str(REPO))
        assert cp.returncode == 0, f"{bayrak} → exit {cp.returncode}"
        assert "Kullanım" in (cp.stdout or "")


def test_b27_argumansiz_cagri_hala_kullanim_hatasi():
    """Geriye uyum: argümansız çağrı hâlâ kullanım hatasıdır (exit != 0)."""
    cp = subprocess.run([sys.executable, str(AILE_DOGRULA)],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(REPO))
    assert cp.returncode != 0
