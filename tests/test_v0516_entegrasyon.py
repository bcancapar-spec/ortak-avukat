# -*- coding: utf-8 -*-
"""v0.5.16 — ENTEGRASYON (15 dalın birleşimi sonrası hizalama bulguları H1/H4/H5).

DEVAM-PLANI «Hizalama bulguları» (2026-09-07):
- **H1** I5 `sure_nobetci.py` `tur: asama` kayıtlarını okuyor ama KANONİK yazıcı
  `oa_hafiza.py sure-flag` (--tarih/--aciklama/--kural) aşama kaydı YAZAMIYORDU
  → `--asama <ad> --pipeline-adimi N` (tarihsiz kayıt; --tarih ile birlikte RET).
- **H4** D (yazar: `oa_hafiza.py teyit --akibet`) ↔ C2 (okur: `ictihat_muhakeme_denetim.py`
  [G5-AKIBET]) sözleşmesi ancak birleşim sonrası uçtan uca sınanabilir:
  LEHE + bozuldu + dilekçede atıf → BLOK (exit 1).
- **H5** main'de kalan `*vakia*.json` DOSYA-ADI bekçisi (K1 ile aynı sınıf) →
  `*.json` + `arac == vakia_matris` damgası; aile_dogrula KİLİT-A bu bekçiyi de
  denetler (damga sözleşmesi: bekçi damgasını üretici script yazmıyorsa HATA).

Tüm fikstürler tmp_path altında sentetiktir (anayasa m.7: kişi/dosya adı yok).
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
NOBETCI = SKILLS / "oa-sure" / "scripts" / "sure_nobetci.py"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"
AILE_DOGRULA = SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(script, args, cwd):
    cp = subprocess.run([sys.executable, str(script)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _init(kok):
    kod, out = _run(HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", kok], kok)
    assert kod == 0, out


def _defter(kok):
    return json.loads((kok / "_oa" / "sureler.json").read_text(encoding="utf-8"))


# ═══════════════ H1 — sure-flag --asama / --pipeline-adimi ═════════════════

def test_h1_asama_kaydi_tarihsiz_ve_i5_semasiyla(tmp_path):
    """Kayıt I5 şemasıyla birebir: tur=asama, asama, pipeline_adimi, aciklama,
    kural, kayit — son_gun/tarih alanı YOK (boş tarih değil, alan yok)."""
    _init(tmp_path)
    kod, out = _run(HAFIZA, ["sure-flag", "--asama", "cevap dilekçesi (dilekçeler aşaması)",
                             "--pipeline-adimi", "8", "--aciklama", "ilk itirazlar cevapla",
                             "--kural", "hmk_ilk_itiraz", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "[≡]" in out and "adım-8" in out
    fl = _defter(tmp_path)["flagler"]
    assert len(fl) == 1
    k = fl[0]
    assert k["tur"] == "asama" and k["pipeline_adimi"] == 8
    assert k["asama"] == "cevap dilekçesi (dilekçeler aşaması)"
    assert k["kural"] == "hmk_ilk_itiraz" and k["aciklama"] == "ilk itirazlar cevapla"
    assert "son_gun" not in k and "tarih" not in k
    assert k["kayit"]


def test_h1_sure_nobetci_asama_kaydini_ayri_blokta_okur(tmp_path):
    """Uçtan uca: oa_hafiza yazar → sure_nobetci [≡] bloğunda gösterir, tarih
    sayımına katmaz, bozuk saymaz (exit 0)."""
    _init(tmp_path)
    kod, out = _run(HAFIZA, ["sure-flag", "--asama", "tahkikat (sona erene kadar)",
                             "--pipeline-adimi", "8", "--aciklama", "ıslah tahkikat bitene kadar",
                             "--kural", "hmk_islah", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    kod, out = _run(NOBETCI, ["--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "[≡]" in out and "1 aşama tetikli" in out
    assert "BOZUK" not in out.upper().replace("BOZUK KAYIT: 0", "")


def test_h1_asama_ile_tarih_birlikte_ret(tmp_path):
    """Tarihli aşama kaydı sessizce yazılmaz (nöbetçi tarihi yutar) → RET, yan etkisiz."""
    _init(tmp_path)
    kod, out = _run(HAFIZA, ["sure-flag", "--asama", "x", "--pipeline-adimi", "6",
                             "--aciklama", "a", "--tarih", "2026-10-01", "--kok", tmp_path], tmp_path)
    assert kod != 0
    assert "--tarih" in out and "RET" in out
    assert _defter(tmp_path).get("flagler", []) == []


@pytest.mark.parametrize("ek", [
    ["--asama", "x", "--aciklama", "a"],                                  # adım yok
    ["--asama", "x", "--pipeline-adimi", "11", "--aciklama", "a"],        # adım aralık dışı
    ["--asama", "x", "--pipeline-adimi", "6"],                            # açıklama yok
    ["--asama", "x", "--pipeline-adimi", "6", "--aciklama", "a", "--tur", "usul"],  # tur çelişkisi
    ["--pipeline-adimi", "6", "--tarih", "2026-10-01", "--aciklama", "a"],  # adım asama'sız
])
def test_h1_eksik_veya_celiskili_asama_ret(tmp_path, ek):
    _init(tmp_path)
    kod, out = _run(HAFIZA, ["sure-flag", "--kok", tmp_path] + ek, tmp_path)
    assert kod != 0, out
    assert "RET" in out
    assert _defter(tmp_path).get("flagler", []) == []


def test_h1_takvim_kaydi_geriye_uyumlu(tmp_path):
    """Eski çağrı biçimi (--tarih/--aciklama) aynen çalışır; aşama ve takvim
    kaydı aynı defterde yan yana durur, aynı çift tekrar eklenmez."""
    _init(tmp_path)
    kod, out = _run(HAFIZA, ["sure-flag", "--tarih", "2099-01-15", "--aciklama", "istinaf",
                             "--kural", "hmk_istinaf", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    for _ in range(2):
        kod, out = _run(HAFIZA, ["sure-flag", "--asama", "ön inceleme", "--pipeline-adimi", "8",
                                 "--aciklama", "belge sunma", "--kok", tmp_path], tmp_path)
        assert kod == 0, out
    fl = _defter(tmp_path)["flagler"]
    assert len(fl) == 2
    assert sorted(k.get("tur") or "takvim" for k in fl) == ["asama", "takvim"]
    assert "ZATEN VAR" in out


# ═══════════════ H4 — AKIBET uçtan uca (D yazar → C2 okur) ══════════════════

KUNYE = "Yargıtay 4. HD, E. 2099/1234, K. 2099/5678, T. 12.09.2099"
DOKUM = ("Yargıtay 4. HD, E. 2099/1234, K. 2099/5678 sayılı kararın tam metni: "
         "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır.\n")
ILGILI = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"
BAG = ("Bu karar, dosyamızdaki olguyla aynı unsur setini içeriyor; TBK m.49'un "
       "büyük önermesini somutlaştıran doğrudan emsaldir.")
ATIFLI = ("İstinaf sebeplerimiz Yargıtay 4. HD E. 2099/1234 K. 2099/5678 "
          "sayılı kararına dayanmaktadır.\n")


def _teyit(kok, damga, akibet=None, kaynak="arac:ictihat_getir"):
    args = ["teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
            "--sonuc", KUNYE, "--damga", damga, "--bag", BAG, "--ilgili-kisim", ILGILI,
            "--dokum-icerik", DOKUM, "--dokum-sinifi", "tam-metin", "--kok", kok]
    if akibet:
        args += ["--akibet", akibet, "--akibet-kaynak", kaynak]
    kod, out = _run(HAFIZA, args, kok)
    assert kod == 0, out
    return out


def _denetim(kok):
    t = kok / "taslak.md"
    t.write_text(ATIFLI, encoding="utf-8")
    return _run(DENETIM, [t, "--kok", kok], kok)


def test_h4_lehe_bozuldu_teyit_sonrasi_muhakeme_denetim_blok(tmp_path):
    """oa_hafiza teyit --akibet bozuldu (LEHE) → ictihat_muhakeme_denetim
    dilekçedeki atfı [G5-AKIBET] ile BLOKLAR (exit 1). Yazar–okur sözleşmesi
    (**AKIBET:** satırı + kütük AKIBET= tokenı) gerçek script çıktısıyla sınanır."""
    _init(tmp_path)
    _teyit(tmp_path, "LEHE", akibet="bozuldu")
    kutuk = (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")
    assert "AKIBET=bozuldu" in kutuk
    kod, out = _denetim(tmp_path)
    assert kod == 1, out
    assert "[G5-AKIBET]" in out and "LEHE dayanak olamaz" in out


def test_h4_lehe_kesinlesti_teyit_sonrasi_gecer(tmp_path):
    """Karşı yön: kesinleşmiş LEHE karar atfı kapıyı ateşlemez (exit 0)."""
    _init(tmp_path)
    _teyit(tmp_path, "LEHE", akibet="kesinlesti")
    kod, out = _denetim(tmp_path)
    assert kod == 0, out
    assert "LEHE dayanak olamaz" not in out


def test_h4_lehe_kesinlesmedi_uyari_bloklamaz(tmp_path):
    _init(tmp_path)
    _teyit(tmp_path, "LEHE", akibet="kesinlesmedi",
           kaynak="UYAP dosya kapağı — temyiz incelemesi sürüyor")
    kod, out = _denetim(tmp_path)
    assert kod == 0, out
    assert "[G5-AKIBET]" in out


def test_h4_akibetsiz_eski_kayit_kapiyi_ateslemez(tmp_path):
    """Geriye uyum: AKIBET satırı olmayan kayıt (v0.5.15 biçimi) [G5-AKIBET] üretmez."""
    _init(tmp_path)
    _teyit(tmp_path, "LEHE")
    kod, out = _denetim(tmp_path)
    assert "[G5-AKIBET]" not in out


# ═══════════════ H5 — vakia bekçisi damga sözleşmesi ═══════════════════════

pk = _yukle("pipeline_kayit_v0516_entegrasyon", PIPELINE)
ad = _yukle("aile_dogrula_v0516_entegrasyon", AILE_DOGRULA)


def _cikti(kok, ad_, veri):
    c = kok / "_oa" / "cikti"
    c.mkdir(parents=True, exist_ok=True)
    (c / ad_).write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")


def test_h5_vakia_bekcisi_ad_bagimsiz_damga_ile_okur(tmp_path):
    """SKILL örneğinin verdiği HERHANGİ bir ad (`04-olgu-delil-denetim.json`)
    `arac == vakia_matris` damgasıyla bekçiye ulaşır; damgasız `04-vakia.json`
    (yabancı şema) okunmaz — K1 sınıfı sahte yeşil kapatıldı."""
    _cikti(tmp_path, "04-olgu-delil-denetim.json",
           {"arac": "vakia_matris", "ispat_bosluklari": ["U2"]})
    _cikti(tmp_path, "04-vakia.json", {"ispat_bosluklari": ["U9"]})
    uyarilar = pk._vakia_delilsiz_unsur_uyarisi(str(tmp_path))
    assert any("U2" in u and "DESTEKLEYİCİ DELİL YOK" in u for u in uyarilar), uyarilar
    assert not any("U9" in u for u in uyarilar), uyarilar


def test_h5_vakia_matris_gercek_ciktisi_bekciye_ulasir(tmp_path):
    """Gerçek üretici: vakia_matris.py --json çıktısı damgayı taşır ve bekçi okur."""
    vm = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
    girdi = tmp_path / "girdi.json"
    girdi.write_text(json.dumps({
        "iddialar": [{"id": "I1", "metin": "Bedel elden ödendi"}],
        "olaylar": []}, ensure_ascii=False), encoding="utf-8")
    c = tmp_path / "_oa" / "cikti"
    c.mkdir(parents=True)
    kod, out = _run(vm, ["--dogrula", girdi, "--json", c / "04-olgu-denetim.json"], tmp_path)
    veri = json.loads((c / "04-olgu-denetim.json").read_text(encoding="utf-8"))
    assert veri.get("arac") == "vakia_matris", (kod, out)
    assert veri.get("ispat_bosluklari") == ["I1"], veri
    uyarilar = pk._vakia_delilsiz_unsur_uyarisi(str(tmp_path))
    assert any("I1" in u for u in uyarilar), "damgalı çıktı (serbest ad) bekçiye ulaşmadı"


def test_h5_kilit_a_gercek_depoda_vakia_bekcisi_kapsamda_ve_temiz():
    assert ad.BEKCI_PARCA.get("_vakia_delilsiz_unsur_uyarisi") == "oa-vakia"
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(SKILLS))
    assert hatalar == [], hatalar
    assert not any("kör" in u for u in uyarilar), uyarilar


_DAMGA_SABLON = textwrap.dedent('''\
    import glob, json, os

    def _denetim_jsonlari(kok, arac):
        cdiz = os.path.join(kok or ".", "_oa", "cikti")
        sonuc = []
        for yol in sorted(glob.glob(os.path.join(cdiz, "*.json"))):
            sonuc.append((yol, {{}}))
        return sonuc


    def _graf_yapisal_bosluk_uyarisi(kok):
        return [y for y, m in _denetim_jsonlari(kok, "grafik_denetim")]


    def _kiyas_bosluk_uyarisi(kok):
        return [y for y, m in _denetim_jsonlari(kok, "kiyas_denetim")]


    def _usul_bosluk_uyarisi(kok):
        return [y for y, m in _denetim_jsonlari(kok, "usul_matris")]


    def _vakia_delilsiz_unsur_uyarisi(kok):
        return [y for y, m in _denetim_jsonlari(kok, "{vakia_arac}")]
''')


def _damga_koku(tmp, vakia_arac="vakia_matris", script_damga="vakia_matris"):
    kok = tmp / "skills"
    (kok / "oa-pipeline" / "scripts").mkdir(parents=True)
    (kok / "oa-pipeline" / "scripts" / "pipeline_kayit.py").write_text(
        _DAMGA_SABLON.format(vakia_arac=vakia_arac), encoding="utf-8")
    for parca, arac in (("oa-illiyet", "grafik_denetim"), ("oa-kiyas", "kiyas_denetim"),
                        ("oa-usul", "usul_matris"), ("oa-vakia", script_damga)):
        (kok / parca / "scripts").mkdir(parents=True)
        (kok / parca / "scripts" / "arac.py").write_text(
            f'sonuc = {{"arac": "{arac}"}}\n', encoding="utf-8")
        (kok / parca / "SKILL.md").write_text(
            f"# {parca}\n\n```bash\npython scripts/arac.py --json _oa/cikti/01-serbest-ad.json\n```\n",
            encoding="utf-8")
    return kok


def test_h5_kilit_a_damga_bicimi_temiz(tmp_path):
    """B biçimi (`_denetim_jsonlari(kok, "<arac>")`): desen `*.json` ortak
    süzgeçten çıkarılır, SKILL örneği serbest adla eşleşir, damga script'te var → temiz."""
    kok = _damga_koku(tmp_path)
    assert ad.bekci_skill_sozlesmesi(str(kok)) == ([], [])


def test_h5_kilit_a_damga_kopusu_hata(tmp_path):
    """Bekçi `arac == vakia_matris` okur ama üretici script `vakia_denetim` yazar
    → bekçi o çıktıyı HİÇ okumaz → HATA (sahte yeşil), uyarı değil."""
    kok = _damga_koku(tmp_path, script_damga="vakia_denetim")
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(kok))
    assert uyarilar == []
    assert len(hatalar) == 1, hatalar
    assert "damga kopuşu" in hatalar[0] and "vakia_matris" in hatalar[0]
    assert "oa-vakia" in hatalar[0]


def test_h5_kilit_a_damga_scripts_yoksa_uyari(tmp_path):
    kok = _damga_koku(tmp_path)
    shutil.rmtree(kok / "oa-vakia" / "scripts")
    hatalar, uyarilar = ad.bekci_skill_sozlesmesi(str(kok))
    assert hatalar == []
    assert any("oa-vakia/scripts yok" in u for u in uyarilar), uyarilar


def test_h5_kilit_a_cli_gercek_depo_kor_degil_ve_temiz():
    """CLI: gerçek depoda «kilidi kör» uyarısı yok ve denetim TEMİZ (sürüm
    işaretçisi uyarıları damga sözleşmesinden bağımsızdır)."""
    kod, out = _run(AILE_DOGRULA, [SKILLS], REPO)
    assert kod == 0, out
    assert "kilidi kör" not in out
    assert "AİLE YAPI DENETİMİ TEMİZ" in out
