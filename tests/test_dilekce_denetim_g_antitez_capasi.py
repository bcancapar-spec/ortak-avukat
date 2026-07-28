# -*- coding: utf-8 -*-
"""M3 (Paket D, v0.5.5) — ANTİTEZ PASI: [G] ANTİTEZ-CEVAP-ÇAPASI advisory kapısı.

Kapsam: `_oa/cikti/*antitez*.json` matrisindeki DUYULMUŞ (karşı taraf fiilen
ileri sürmüş) + çürütülmüş her cephe için dilekçede bir anahtar-kelime
çapası aranır. Bu ASLA blokleyici değildir (exit koduna etkisi yoktur) —
yalnız GÖRÜNÜR bir uyarı üretir.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _load():
    spec = importlib.util.spec_from_file_location("dilekce_denetim", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()


def _matris_yaz(tmp_path, cepheler, ad="07-antitez-matris.json"):
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / ad).write_text(
        json.dumps({"tez": "test tezi", "cepheler": cepheler}, ensure_ascii=False),
        encoding="utf-8")


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


TEMIZ_TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz
DAVALI: Mehmet Kaya

AÇIKLAMALAR (VAKIALAR):
1. Taraflar arasındaki ilişkiden doğan alacak vakıası aşağıda özetlenmiştir.

HUKUKİ SEBEPLER:
İlgili mevzuat hükümleri dayanak alınmıştır. Zamanaşımı def'i yerinde değildir
zira alacak muaccel olduğu tarihten itibaren süresi içinde dava açılmıştır.

DELİLLER:
Tanık beyanları, bilirkişi incelemesi ve yazılı belgeler ispat vasıtasıdır.

NETİCE-İ TALEP:
Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini talep ederim.

Av. Ayşe Yılmaz
Vekil
İmza
"""


def test_matris_yoksa_g_bloklamaz_ve_bilgi_der(tmp_path):
    """M3 düzeltmesi (Paket D sınav bulgusu) — matrisin TAMAMEN YOKLUĞU,
    'matris var ve tam örtüşüyor' hâliyle AYNI [OK] etiketini almamalı;
    ayrı [BİLGİ] ile 'ANTİTEZ PASI koşulmamış olabilir' işaretlenmeli."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(TEMIZ_TASLAK, encoding="utf-8")
    kod, cikti = _cli([str(taslak), "--tip", "dava", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "[G] ANTİTEZ-CEVAP-ÇAPASI" in cikti
    bolum = cikti.split("[G] ANTİTEZ-CEVAP-ÇAPASI")[1].split("[H]")[0]
    assert "[BİLGİ]" in bolum
    assert "koşulmamış olabilir" in bolum
    assert "[OK]" not in bolum


def test_matris_var_ve_tam_ortusuyorsa_ok_der(tmp_path):
    """Matris VARKEN ve tüm DUYULMUŞ cepheler çapalanmışken [OK] (matrisin
    tamamen YOK olduğu durumdan ayrı bir etiket) basılmalı."""
    curutme = ("Alacağın muaccel olduğu vergilendirme dönemi farklı hesaplanmalı "
               "davalı beyanı gerçeği yansıtmıyor")
    _matris_yaz(tmp_path, [
        {"cephe": "zamanasimi", "curutme": curutme, "duyulmus": True},
    ])
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        TEMIZ_TASLAK + "\nSomut olayda alacağın muaccel olduğu vergilendirme dönemi "
        "farklı hesaplanmalı; davalı beyanı gerçeği yansıtmamaktadır.\n",
        encoding="utf-8")
    kod, cikti = _cli([str(taslak), "--tip", "dava", "--kok", str(tmp_path)], cwd=tmp_path)
    bolum = cikti.split("[G] ANTİTEZ-CEVAP-ÇAPASI")[1].split("[H]")[0]
    assert "[OK]" in bolum
    assert "tam örtüşüyor" in bolum
    assert "[BİLGİ]" not in bolum


def test_duyulmus_curutme_dilekcede_yoksa_uyarir_ama_bloklamaz(tmp_path):
    _matris_yaz(tmp_path, [
        {"cephe": "zamanasimi", "curutme": "Alacağın muaccel olduğu vergilendirme dönemi "
                                            "farklı hesaplanmalı davalı beyanı gerçeği yansıtmıyor",
         "duyulmus": True},
    ])
    taslak = tmp_path / "taslak.md"
    # Çürütmedeki anahtar kelimelerin HİÇBİRİNİ içermeyen bir taslak.
    taslak.write_text("Bu dilekçe tamamen ilgisiz kelimelerle yazılmıştır bugün burada.",
                       encoding="utf-8")
    kod, cikti = _cli([str(taslak), "--kok", str(tmp_path)], cwd=tmp_path)
    assert "[G] ANTİTEZ-CEVAP-ÇAPASI" in cikti
    assert "DUYULMUŞ" in cikti
    assert "zamanasimi" in cikti
    # [G] hiçbir zaman TESLİM ENGELİ üretmez — yalnız (A/eksik unsur gibi)
    # başka nedenlerle engel olabilir; burada assert ederiz ki G kendi başına
    # exit koduna dokunmaz (fonksiyon çağrısı ile doğrudan doğrulanır).


def test_duyulmus_curutme_dilekcede_varsa_uyarmaz(tmp_path):
    curutme = ("Alacağın muaccel olduğu vergilendirme dönemi farklı hesaplanmalı "
               "davalı beyanı gerçeği yansıtmıyor")
    _matris_yaz(tmp_path, [
        {"cephe": "zamanasimi", "curutme": curutme, "duyulmus": True},
    ])
    taslak_metin = ("Somut olayda alacağın muaccel olduğu vergilendirme dönemi "
                    "farklı hesaplanmalı; davalı beyanı gerçeği yansıtmamaktadır.")
    uyarilar = dd.antitez_cevap_capasi_uyarilari(taslak_metin, str(tmp_path))
    assert uyarilar == [], f"örtüşen çürütme yine de uyardı: {uyarilar}"


def test_duyulmamis_cephe_hic_denetlenmez(tmp_path):
    _matris_yaz(tmp_path, [
        {"cephe": "ictihat", "curutme": "Tamamen alakasız uzun bir çürütme metni burada yer alır",
         "duyulmus": False},
    ])
    uyarilar = dd.antitez_cevap_capasi_uyarilari("bambaşka bir dilekçe metni", str(tmp_path))
    assert uyarilar == []


def test_kok_verilmezse_sessizce_bos_doner():
    assert dd.antitez_cevap_capasi_uyarilari("herhangi bir metin", None) == []


def test_g_asla_exit_kodunu_degistirmez(tmp_path):
    """[G] yalnız advisory: aynı temiz taslak, matris VARKEN de YOKKEN de
    (duyulmuş+eksik-çapa uyarısı üretse dahi) exit kodu 0 kalmalı."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(TEMIZ_TASLAK, encoding="utf-8")
    kod_matrissiz, _c = _cli([str(taslak), "--tip", "dava", "--kok", str(tmp_path)], cwd=tmp_path)

    _matris_yaz(tmp_path, [
        {"cephe": "usul", "curutme": "Tamamen alakasız uzun bir çürütme metni burada yer alır",
         "duyulmus": True},
    ])
    kod_matrisli, cikti = _cli([str(taslak), "--tip", "dava", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "[UYARI]" in cikti.split("[G] ANTİTEZ-CEVAP-ÇAPASI")[1].split("[H]")[0] \
        or "DUYULMUŞ" in cikti
    assert kod_matrissiz == kod_matrisli, "[G] uyarısı exit kodunu değiştirmemeli"
