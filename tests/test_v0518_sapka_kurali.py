# -*- coding: utf-8 -*-
"""v0.5.18 — ŞAPKA KURALI: dilekçede â ve î yok (avukat lafzı, 2026-10-09).

NEDEN VAR: Avukat talimatı (2026-10-09): bundan sonra dilekçelerde şapkalı a ve
şapkalı i kullanılmaz; teyitli yazım â → a, î → i (büyük harfte Â → A, Î → İ).
oa-dilekce'nin "Yazar sistemi ve lafzı" kuralı Çapar'ın lafzına uymayı ESAS
sayar. Kuralın mekanik gözü dilekce_denetim [Ş]'dir (uyarı sınıfı, ASLA
bloklamaz): avukatın kendi metninde kalan şapkalı harfi ve önerilen yazımı
gösterir, düzeltmeyi yazar yapar.

Birebir alıntı MUAFTIR (tırnak içi ve '>' blok-alıntı, [N] ile aynı tespit):
karar, mevzuat ya da evrak metnine dokunmak alıntıyı tahrif etmektir.
û (mahkûm) talimatın kapsamında değildir. Bütün metinler kurgudur.
"""
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DD = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _dd():
    spec = importlib.util.spec_from_file_location("_v0518_sapka_dd", DD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_v0518_sapka_dd"] = mod
    spec.loader.exec_module(mod)
    return mod


dd = _dd()

TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: kurgu-maskeli)
Adres: Örnek Mahallesi No:1 İstanbul

DAVALI: Mehmet Kaya

KONU: Alacağın tahsili talebimizden ibarettir.

AÇIKLAMALAR (VAKIALAR):
1. Taraflar arasındaki ticari ilişkiden doğan alacak vakıası aşağıda özetlenmiştir.
2. Davalı, sözleşme kapsamındaki edimini yerine getirmemiştir.

HUKUKİ SEBEPLER:
İlgili mevzuat hükümleri ve genel hukuk kuralları dayanak alınmıştır.

DELİLLER:
Tanık beyanları, bilirkişi incelemesi ve yazılı belgeler ispat vasıtasıdır.

NETİCE-İ TALEP:
Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini saygılarımla talep ederim.

Tarih: 01.07.2026

Av. Ayşe Yılmaz
Vekil
İmza
"""


def test_avukat_metninde_sapkali_harf_gorunur_ve_dogru_yazim_onerilir():
    metin = ("SAYIN HÂKİMLİĞE\nResmî Gazete'de yayımlanan kararla manevî zarar doğmuştur.\n"
             "MİLLÎ ÂMİRLİK yazısı hukukî dayanaktır; kâtip tutanağı da vardır.\n")
    uyarilar = "\n".join(dd.sapkali_harf_uyarilari(metin))
    for yanlis, dogru in (("HÂKİMLİĞE", "HAKİMLİĞE"), ("Resmî", "Resmi"), ("manevî", "manevi"),
                          ("MİLLÎ", "MİLLİ"), ("ÂMİRLİK", "AMİRLİK"), ("hukukî", "hukuki"),
                          ("kâtip", "katip")):
        assert "'%s' → '%s'" % (yanlis, dogru) in uyarilar, (yanlis, uyarilar)


def test_birebir_alinti_ici_muaf():
    metin = ("> Yargıtay: hâkimin takdir yetkisi resmî belgeyle sınırlıdır.\n"
             "Kararda “hâkim resmî kayda bağlıdır” denilmiştir.\n"
             'Bilirkişi "manevî zarar" ifadesini kullanmıştır.\n')
    assert dd.sapkali_harf_uyarilari(metin) == []


def test_sapkasiz_metin_sessiz():
    assert dd.sapkali_harf_uyarilari(TASLAK) == []


def test_u_sapkasi_talimat_kapsaminda_degil():
    assert dd.sapkali_harf_uyarilari("Sanık mahkûm edilmiştir; sükûnet bozulmamıştır.") == []


def test_ayni_sozcuk_tek_satirda_sayilir():
    uyarilar = dd.sapkali_harf_uyarilari("hâkim hâkim hâkim")
    assert len(uyarilar) == 1 and "3 kez" in uyarilar[0], uyarilar


def test_uyari_listesi_tavanli_ve_kesinti_gorunur():
    metin = " ".join("kelimeâ%d" % i for i in range(20))
    uyarilar = dd.sapkali_harf_uyarilari(metin)
    assert len(uyarilar) == dd._S_AZAMI_UYARI + 1, uyarilar
    assert uyarilar[-1].startswith("(+"), uyarilar[-1]


def test_hizli_denetim_sapka_bulgusunu_tasir():
    bulgular = dd.hizli_denetim("Sayın hâkim, dava süresindedir.")
    assert any(b.startswith("[Ş] ") and "'hâkim' → 'hakim'" in b for b in bulgular), bulgular


def test_cli_sapka_bolumunu_basar_ve_bloklamaz(tmp_path):
    temiz = tmp_path / "temiz.md"
    temiz.write_text(TASLAK, encoding="utf-8")
    sapkali = tmp_path / "sapkali.md"
    sapkali.write_text(TASLAK.replace("talep ederim", "talep ederim. Hâkim takdiri resmî kayda bağlıdır"),
                       encoding="utf-8")

    def _kos(yol):
        cp = subprocess.run([sys.executable, str(DD), str(yol), "--tip", "genel", "--kok", str(tmp_path)],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        return cp.returncode, cp.stdout + cp.stderr

    kod_t, out_t = _kos(temiz)
    kod_s, out_s = _kos(sapkali)
    assert kod_s == kod_t, (kod_t, kod_s, out_s)
    assert "[Ş] ŞAPKALI HARF" in out_s and "'Hâkim' → 'Hakim'" in out_s, out_s
    assert "[Ş] ŞAPKALI HARF" in out_t and "şapkalı harf (â/î) yok" in out_t, out_t
