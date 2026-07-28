# -*- coding: utf-8 -*-
"""P1-11 DOKTRİN 4 KURAL (ek kurallar #2 ve #4) — advisory tarama kapıları:

[H] GÖRÜNMEZ İSKELET TARAMASI — İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri
paragrafın İÇ MANTIĞIDIR, yüzeye ETİKET olarak sızmaz; satır başında
'İddiamız:'/'Norm:'/'Somut örtüşme:' kalıp-açılışları bir akıcılık uyarısı
üretir — ASLA bloklamaz.

[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI — karşı tarafın kusuru TESPİT
edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik ara karar talebi KURULMAZ;
karşı-taraf-kusuru bağlamında 'süre verilsin/tamamlan-/gideril-' kalıpları
bir uyarı üretir — ASLA bloklamaz.

Her iki kapı da yalnız BİÇİM/BAĞLAM sinyalidir; exit koduna dokunmazlar.
"""
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _load():
    spec = importlib.util.spec_from_file_location("dilekce_denetim_h_i", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()


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
İlgili mevzuat hükümleri dayanak alınmıştır.

DELİLLER:
Tanık beyanları, bilirkişi incelemesi ve yazılı belgeler ispat vasıtasıdır.

NETİCE-İ TALEP:
Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini talep ederim.

Av. Ayşe Yılmaz
Vekil
İmza
"""


# ── [H] GÖRÜNMEZ İSKELET ────────────────────────────────────────────────────

def test_h_pozitif_iddia_norm_ortusme_kaliplari_yakalanir():
    metin = (
        "İddiamız: davalı temerrüde düşmüştür.\n"
        "Norm: TBK m.117 uyarınca temerrüt faizi işler.\n"
        "Somut örtüşme: dosyadaki ihtarname bu unsuru karşılamaktadır.\n"
    )
    uyarilar = dd._gorunmez_iskelet_uyarilari(metin)
    assert len(uyarilar) == 3
    metinler = " | ".join(uyarilar)
    assert "İddiamız:" in metinler and "Norm:" in metinler and "Somut örtüşme:" in metinler


def test_h_negatif_akici_metinde_uyari_yok():
    metin = (
        "Davalının temerrüde düştüğü, taraflar arasındaki ihtarname ile sabittir; "
        "TBK m.117 uyarınca temerrüt faizi bu tarihten itibaren işlemeye başlamıştır. "
        "Dosyadaki ihtarname bu unsuru açıkça karşılamaktadır."
    )
    assert dd._gorunmez_iskelet_uyarilari(metin) == []


def test_h_metin_icinde_gomulu_gecis_yakalanmaz():
    """Satır BAŞINDA olmayan, cümle içine gömülü 'norm:' gibi bir geçiş
    yanlış-pozitif üretmemeli (yalnız satır başı ETİKET biçimi sinyaldir)."""
    metin = "Bu olayda uygulanacak norm: TBK m.49'dur ve bu açık bir örtüşme değildir."
    assert dd._gorunmez_iskelet_uyarilari(metin) == []


def test_h_tekillestirir_ayni_etiket_tekrar_etse_bile():
    metin = "İddiamız: birinci\nİddiamız: ikinci\n"
    uyarilar = dd._gorunmez_iskelet_uyarilari(metin)
    assert len(uyarilar) == 1


def test_h_cli_uyari_basar_ama_exit_kodunu_degistirmez(tmp_path):
    taslak_temiz = tmp_path / "temiz.md"
    taslak_temiz.write_text(TEMIZ_TASLAK, encoding="utf-8")
    kod_temiz, cikti_temiz = _cli([str(taslak_temiz), "--tip", "dava"], cwd=tmp_path)

    taslak_iskelet = tmp_path / "iskelet.md"
    taslak_iskelet.write_text(
        TEMIZ_TASLAK + "\nİddiamız: davalı kusurludur.\nNorm: TBK m.49.\n"
        "Somut örtüşme: dosyadaki delillerle örtüşmektedir.\n", encoding="utf-8")
    kod_iskelet, cikti_iskelet = _cli([str(taslak_iskelet), "--tip", "dava"], cwd=tmp_path)

    assert "[H] GÖRÜNMEZ İSKELET TARAMASI" in cikti_temiz
    assert "[OK]" in cikti_temiz.split("[H] GÖRÜNMEZ İSKELET TARAMASI")[1].split("[I]")[0]

    h_bolum_iskelet = cikti_iskelet.split("[H] GÖRÜNMEZ İSKELET TARAMASI")[1].split("[I]")[0]
    assert "[UYARI]" in h_bolum_iskelet
    assert kod_temiz == kod_iskelet, "[H] advisory exit kodunu değiştirmemeli"


# ── [I] KUSUR→SONUÇ→TALEP ASİMETRİSİ ────────────────────────────────────────

def test_i_pozitif_karsi_taraf_kusuru_baglaminda_onarma_talebi_yakalanir():
    metin = "Davalının dava şartı eksikliği bulunmaktadır; bu eksikliğin tamamlanması gerekmektedir."
    uyarilar = dd._kusur_sonuc_talep_asimetri_uyarilari(metin)
    assert len(uyarilar) == 1
    assert "GİDERİLMESİNE" in uyarilar[0]


def test_i_pozitif_iki_farkli_kalip_ayri_ayri_uyarir():
    """'tamamlanması' VE 'süre verilsin' AYNI cümlede geçerse bunlar farklı
    onarma-talebi kalıpları sayılır — her biri ayrı bir uyarı üretir (aynı
    ihlalin tek bir tekrarı değil, iki bağımsız sinyaldir)."""
    metin = ("Davalının dava şartı eksikliği bulunmaktadır. Bu eksikliğin "
             "tamamlanması için süre verilsin.")
    uyarilar = dd._kusur_sonuc_talep_asimetri_uyarilari(metin)
    assert len(uyarilar) == 2


def test_i_negatif_baglamsiz_onarma_kalibinda_uyari_yok():
    """Aynı 'süre verilsin' kalıbı, karşı-taraf-kusuru bağlamı OLMADAN
    (ör. kendi tanığımız için usuli bir süre talebi) uyarı üretmemeli."""
    metin = "Tanığımızın dinlenebilmesi için mahkemece münasip bir süre verilsin."
    assert dd._kusur_sonuc_talep_asimetri_uyarilari(metin) == []


def test_i_negatif_kusur_tespiti_ret_talebiyle_sonuclaninca_uyari_yok():
    metin = ("Davalının dava şartı eksikliği tespit edilmiştir; bu nedenle "
             "davanın usulden reddine karar verilmesini talep ederiz.")
    assert dd._kusur_sonuc_talep_asimetri_uyarilari(metin) == []


def test_i_tekillestirir_ayni_ifade_tekrar_etse_bile():
    metin = ("Davalının kusuru nedeniyle eksikliğin tamamlanması gerekmektedir. "
             "Ayrıca davalının kusuru nedeniyle eksikliğin tamamlanması gerekmektedir.")
    uyarilar = dd._kusur_sonuc_talep_asimetri_uyarilari(metin)
    assert len(uyarilar) == 1


def test_i_cli_uyari_basar_ama_exit_kodunu_degistirmez(tmp_path):
    taslak_temiz = tmp_path / "temiz.md"
    taslak_temiz.write_text(TEMIZ_TASLAK, encoding="utf-8")
    kod_temiz, cikti_temiz = _cli([str(taslak_temiz), "--tip", "dava"], cwd=tmp_path)

    taslak_onarma = tmp_path / "onarma.md"
    taslak_onarma.write_text(
        TEMIZ_TASLAK + "\nDavalının dava şartı eksikliği bulunmaktadır; bu "
        "eksikliğin tamamlanması için süre verilsin.\n", encoding="utf-8")
    kod_onarma, cikti_onarma = _cli([str(taslak_onarma), "--tip", "dava"], cwd=tmp_path)

    assert "[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI" in cikti_temiz
    i_bolum_temiz = cikti_temiz.split("[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI")[1]
    assert "[OK]" in i_bolum_temiz.split("====")[0]

    i_bolum_onarma = cikti_onarma.split("[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI")[1]
    assert "[UYARI]" in i_bolum_onarma.split("====")[0]
    assert kod_temiz == kod_onarma, "[I] advisory exit kodunu değiştirmemeli"
