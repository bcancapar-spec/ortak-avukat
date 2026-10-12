# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİR ÜRETİCİLERİ · S2 ANTİTEZ DENETİM JSON'U + DAMGA (B-8).

NEDEN VAR: Fable tutarlılık raporu (2026-10-07) B-8 — antitez K1 sözleşmesinin
DIŞINDAYDI: `--iskelet` şablonu `arac` damgası taşımıyor, `--dogrula` makine-
okur `--json` yazmıyordu; `dilekce_denetim.py` [G] kapısı ve `pipeline_kayit`
antitez dosyasını yalnız DOSYA ADIYLA (`*antitez*.json`) tanıyordu — diğer
üç motor için v0.5.16'da kapatılan "ad sözleşmesi kopuşu" (SKILL örneği
başka ad verirse bekçi hiç okumaz → sahte yeşil) antitezde açıktı. Ayrıca
cephe kaydının zincirin hangi halkasına (vakıa / illiyet / kıyas kimliği)
saldırdığı makine-okur değildi.

Sözleşme (S2 — Görev 2 üretir, Görev 1 `_antitez_bosluk_uyarisi` tüketir):
`antitez_matris.py --dogrula <girdi> --json <yol>` →
  {"arac": "antitez_matris", "girdi": <argüman aynen>, "kaynaklar": S1,
   "acik_cepheler", "curutulmemis", "teyitsiz_dayanak", "dayanaksiz_guclu",
   "artik_riskler", "gecersiz": list, "saglikli": bool}, sort_keys=True.
Görev 1 en az `arac`, `saglikli`, `acik_cepheler`, `curutulmemis` okur.
Ek (Ruling, bu dosyada): `uyarilar` (list[str]) — advisory kanal; `hedef`
biçim uyarıları buraya düşer, `saglikli`ye GİRMEZ (brief: "bilinmeyen biçim
UYARI olur", şema hatası değil). `--iskelet` şablonu `arac` TAŞIMAZ (Ruling 16 / Ö-1:
damga YALNIZ `--dogrula … --json` denetim çıktısında); cephe kaydında opsiyonel
`hedef: {"halka": "vakia|illiyet|kiyas", "id": str}`.
`dilekce_denetim._antitez_matris_dosyalari` dosya adına EK olarak
`arac == "antitez_matris"` damgalı `.json`ları da — `cepheler` listesi taşıyorsa — tanır
(K-1: denetim çıktısı ve bozuk/yabancı dosya matris sayılmaz).
Bütün veriler kurgudur (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
ANTITEZ = SKILLS / "oa-antitez" / "scripts" / "antitez_matris.py"
DILEKCE = SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py"

S2_ANAHTARLAR = {"arac", "girdi", "kaynaklar", "acik_cepheler", "curutulmemis",
                 "teyitsiz_dayanak", "dayanaksiz_guclu", "artik_riskler", "gecersiz", "saglikli"}


def _modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _kos(argumanlar, cwd):
    cp = subprocess.run([sys.executable, str(ANTITEZ), *argumanlar], cwd=str(cwd),
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    return cp.returncode, cp.stdout or "", cp.stderr or ""


def _yaz(yol, nesne):
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(nesne, ensure_ascii=False, indent=2), encoding="utf-8")
    return yol


CEPHELER = list(_modul(ANTITEZ, "v0518_uretici_antitez_json_sabit").STANDART_CEPHELER)


def _cephe(ad, **ek):
    k = {"cephe": ad, "antitez": "değerlendirildi: saldırı yok", "guc": "yok", "curutme": "",
         "curutme_dayanak": "", "dayanak_durum": "yok", "artik_risk": "", "duyulmus": False}
    k.update(ek)
    return k


def _tam_matris():
    # Ö-1 (ana oturum kararı, düzeltme turu 1): girdi matrisi `arac` damgası TAŞIMAZ — şablonla aynı.
    return {"tez": "Kurgu tez", "cepheler": [_cephe(c) for c in CEPHELER]}


# ═══════════════════════════ B-8: iskelet damgası + --json ══════════════════

def test_iskelet_arac_damgali_ve_dogrula_json_yazar(tmp_path):
    """Ö-1 (ana oturum kararı, düzeltme turu 1): `--iskelet` şablonu damga
    TAŞIMAZ; `arac: "antitez_matris"` YALNIZ `--dogrula … --json` denetim
    çıktısındadır (K1 damga sözleşmesi = motor ÇIKTISI damgası — vakia/graf/
    kıyas ile aynı anlam). Girdi matrisi de damga taşısa, damgaya bakan her
    tüketici (`_denetim_jsonlari`, [G], adım-6 bekçisi) girdiyi denetim sanıp
    DURUM.md'ye sahte "sağlıksız" satırı yazabilirdi; kaynağında kesildi.
    Denetim çıktısı S2 anahtarlarını sort_keys ile yazar; `girdi` komut
    satırının yankısıdır; `kaynaklar` S1 biçimindedir. K-12: stderr `--json`u
    "ZORUNLU (pipeline)" diye anar (modelin ilk gördüğü metin stderr'dir)."""
    kod, out, err = _kos(["--iskelet"], cwd=tmp_path)
    assert kod == 0 and "Traceback" not in err
    sablon = json.loads(out)
    assert "arac" not in sablon, "Ö-1: şablon damga taşımaz"
    assert set(sablon) == {"tez", "cepheler"}
    assert [c["cephe"] for c in sablon["cepheler"]] == CEPHELER
    assert "--json ZORUNLU (pipeline)" in err

    _yaz(tmp_path / "m.json", _tam_matris())
    kod, out, err = _kos(["--dogrula", "m.json", "--json", "denetim.json"], cwd=tmp_path)
    assert kod == 0 and "Traceback" not in err, err[-1500:]
    assert "[JSON] Makine-okur sonuc yazildi: denetim.json" in out
    d = json.loads((tmp_path / "denetim.json").read_text(encoding="utf-8"))

    assert S2_ANAHTARLAR <= set(d), sorted(S2_ANAHTARLAR - set(d))
    assert d["arac"] == "antitez_matris" and d["girdi"] == "m.json"
    assert d["saglikli"] is True
    for alan in ("acik_cepheler", "curutulmemis", "teyitsiz_dayanak",
                 "dayanaksiz_guclu", "artik_riskler", "gecersiz"):
        assert d[alan] == [], (alan, d[alan])
    assert d["kaynaklar"] == [] and "kaynaklar_notu" in d      # _oa dışı girdi (S1)
    assert list(d) == sorted(d), "sort_keys=True"
    assert "Matris bütünlüğü TAMAM" in out


def test_dogrula_json_bulgulari_rapor_ile_ortusur(tmp_path):
    """Makine-okur listeler insan raporundaki bloklarla AYNI içeriği taşır —
    tüketici (DURUM.md hattı) raporu değil JSON'u okur; ikisi ayrışamaz."""
    m = {"arac": "antitez_matris", "tez": "Kurgu tez", "cepheler": [
        _cephe("usul", guc="dusuk", curutme="Yetki şartı var (kurgu)",
               curutme_dayanak="HMK m.17", dayanak_durum="teyitsiz"),            # teyitsiz dayanak
        _cephe("maddi_vakia", guc="yuksek", curutme="İrsaliye (kurgu)",
               artik_risk="İmzaya itiraz gelebilir"),                             # dayanaksız güçlü + artık risk
        _cephe("ispat_delil", guc="orta"),                                       # çürütülmemiş
        _cephe("ictihat", guc="cok"),                                            # şema hatası
        _cephe("zamanasimi"), _cephe("defi_karsi_talep"),
        # hukuki_niteleme · muvekkil_zaaf · bilirkisi_teknik → AÇIK CEPHE
    ]}
    _yaz(tmp_path / "m.json", m)
    kod, out, err = _kos(["--dogrula", "m.json", "--json", "denetim.json"], cwd=tmp_path)
    assert kod == 0 and "Traceback" not in err
    d = json.loads((tmp_path / "denetim.json").read_text(encoding="utf-8"))

    assert d["acik_cepheler"] == ["hukuki_niteleme", "muvekkil_zaaf", "bilirkisi_teknik"]
    assert d["curutulmemis"] == ["ispat_delil"]
    assert d["teyitsiz_dayanak"] == ["usul: 'HMK m.17'"]
    assert d["dayanaksiz_guclu"] == ["maddi_vakia"]
    assert d["artik_riskler"] == ["maddi_vakia: İmzaya itiraz gelebilir"]
    assert d["gecersiz"] == ["ictihat: geçersiz 'guc' = cok"]
    assert d["saglikli"] is False
    assert "AÇIK CEPHELER" in out and "Matris bütünlüğü EKSİK" in out


def test_json_bayragi_verilmezse_dosya_yazilmaz(tmp_path):
    """Diğer üç motorla aynı sözleşme: `--json` yoksa dosya yok, `[JSON]` satırı yok."""
    _yaz(tmp_path / "m.json", _tam_matris())
    kod, out, err = _kos(["--dogrula", "m.json"], cwd=tmp_path)
    assert kod == 0
    assert "[JSON]" not in out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["m.json"]


# ═══════════════════════════ B-8: hedef alanı ═══════════════════════════════

def test_hedef_alani_bicimsizse_uyari(tmp_path):
    """Opsiyonel `hedef` (cephe → zincir halkası bağı) tanınır; bilinmeyen
    biçim UYARIDIR — şema hatası DEĞİL: `gecersiz` boş kalır, `saglikli`
    değişmez; uyarı hem raporda hem JSON `uyarilar`da görünür."""
    m = _tam_matris()
    m["cepheler"][0]["hedef"] = "I3"                                   # dize — sözlük bekleniyor
    m["cepheler"][1]["hedef"] = {"halka": "delil", "id": "D1"}         # halka kapalı küme dışı
    m["cepheler"][2]["hedef"] = {"halka": "vakia"}                     # id yok
    m["cepheler"][3]["hedef"] = {"halka": "kiyas", "id": ""}           # id boş
    _yaz(tmp_path / "m.json", m)
    kod, out, err = _kos(["--dogrula", "m.json", "--json", "denetim.json"], cwd=tmp_path)
    assert kod == 0 and "Traceback" not in err
    d = json.loads((tmp_path / "denetim.json").read_text(encoding="utf-8"))

    assert len(d["uyarilar"]) == 4
    for cephe, u in zip(CEPHELER[:4], d["uyarilar"]):
        assert u.startswith(f"{cephe}: 'hedef' biçimsiz"), u
        assert "vakia|illiyet|kiyas" in u
    assert d["gecersiz"] == [] and d["saglikli"] is True
    assert "HEDEF UYARISI" in out and "Matris bütünlüğü TAMAM" in out


def test_hedef_alani_bicimli_ise_uyari_yok(tmp_path):
    """Üç halka için biçimli `hedef` sessizce kabul edilir (uyarı yok)."""
    m = _tam_matris()
    m["cepheler"][0]["hedef"] = {"halka": "vakia", "id": "I3"}
    m["cepheler"][1]["hedef"] = {"halka": "illiyet", "id": "FIIL->ZARAR"}
    m["cepheler"][2]["hedef"] = {"halka": "kiyas", "id": "unsur:kusur"}
    _yaz(tmp_path / "m.json", m)
    kod, out, err = _kos(["--dogrula", "m.json", "--json", "denetim.json"], cwd=tmp_path)
    assert kod == 0 and "Traceback" not in err
    d = json.loads((tmp_path / "denetim.json").read_text(encoding="utf-8"))
    assert d["uyarilar"] == [] and d["saglikli"] is True
    assert "HEDEF UYARISI" not in out


# ═══════════════════════════ B-8: dilekce_denetim damgayla tanır ════════════

def test_dilekce_denetim_antitez_dosyasini_damgayla_da_tanir(tmp_path):
    """[G] kapısının aday listesi: dosya adı sözleşmesi (`*antitez*.json`) KORUNUR,
    ona EK olarak adında 'antitez' geçmeyen ama `arac == "antitez_matris"`
    damgalı .json da adaydır (Ö-1'den sonra şablon damga yazmaz — bu yol elle
    damgalanmış/eski dosyalar için kalır); K-1: her aday `cepheler` LİSTESİ
    taşımalı; yabancı damga ve bozuk JSON dışarıda, liste sıralı."""
    kok = tmp_path
    cikti = kok / "_oa" / "cikti"
    _yaz(cikti / "07-antitez-matris.json", {"tez": "T", "cepheler": [_cephe("usul")]})      # ad sözleşmesi, damgasız (eski)
    _yaz(cikti / "06-cephanelik.json", {"arac": "antitez_matris", "tez": "T", "cepheler": [   # damga, adda 'antitez' yok
        _cephe("zamanasimi", guc="orta", duyulmus=True,
               curutme="Zamanaşımı ihtarname tebliğiyle kesilmiştir dolayısıyla süre yeniden işlemektedir")]})
    _yaz(cikti / "05-kiyas-denetim.json", {"arac": "kiyas_denetim", "kritik_bosluk": False})  # yabancı damga
    (cikti / "99-bozuk.json").write_text("{bozuk", encoding="utf-8")                            # bozuk → sessiz dışarıda

    dd = _modul(DILEKCE, "v0518_uretici_antitez_json_dd")
    assert dd._antitez_matris_dosyalari(str(kok)) == [
        str(cikti / "06-cephanelik.json"), str(cikti / "07-antitez-matris.json")]

    uyarilar = dd.antitez_cevap_capasi_uyarilari("Davacı alacağın tahsilini talep eder.", str(kok))
    assert len(uyarilar) == 1 and "zamanasimi" in uyarilar[0] and "06-cephanelik.json" in uyarilar[0]


def test_dilekce_denetim_damga_taramasi_cikti_dizini_yoksa_bos(tmp_path):
    """Kök var, `_oa/cikti` yok → [] (eski davranış korunur; çökme yok)."""
    dd = _modul(DILEKCE, "v0518_uretici_antitez_json_dd_bos")
    assert dd._antitez_matris_dosyalari(str(tmp_path)) == []


def test_dilekce_denetim_yalniz_denetim_ciktisi_varsa_matris_adayi_yok(tmp_path):
    """K-1: SKILL.md'nin önerdiği `06-antitez-denetim.json` (gerçek S2 çıktısı:
    `arac` VAR, `cepheler` YOK) adıyla `*antitez*.json` globuna, damgasıyla
    damga süzgecine yakalanır; matris silinmiş/adı değişmişken yalnız o kalırsa
    [G] «[OK] … matris tam örtüşüyor» sahte yeşilini basardı. Aday kabulü
    `isinstance(m.get("cepheler"), list)` ile sınırlıdır (glob ve damga adayları
    için): denetim çıktısı, `cepheler`i liste olmayan dosya ve bozuk JSON aday
    DEĞİL → liste boş, uyarı yok ([BİLGİ] «bulunamadı» dalı). Gerçek matris
    gelince aday yalnız odur."""
    kok = tmp_path
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)                       # motor dizin yaratmaz (pipeline yaratır)
    _yaz(kok / "m.json", _tam_matris())
    kod, out, err = _kos(["--dogrula", "m.json", "--json", "_oa/cikti/06-antitez-denetim.json"], cwd=kok)
    assert kod == 0 and "Traceback" not in err
    d = json.loads((cikti / "06-antitez-denetim.json").read_text(encoding="utf-8"))
    assert d["arac"] == "antitez_matris" and "cepheler" not in d        # gerçek S2 çıktısı
    _yaz(cikti / "07-antitez-bozuk.json", {"tez": "T", "cepheler": "bozuk"})
    (cikti / "08-antitez-yarim.json").write_text("{yarım", encoding="utf-8")

    dd = _modul(DILEKCE, "v0518_uretici_antitez_json_dd_k1")
    assert dd._antitez_matris_dosyalari(str(kok)) == []
    assert dd.antitez_cevap_capasi_uyarilari("Davacı alacağın tahsilini talep eder.", str(kok)) == []

    _yaz(cikti / "06-antitez-matris.json", _tam_matris())
    assert dd._antitez_matris_dosyalari(str(kok)) == [str(cikti / "06-antitez-matris.json")]
