"""[J] SAYI/TARİH HARİTASI — BAĞIMSIZ İÇERİK HAKEMİ'nin mekanik gözü (v0.5.5.2).

2026/307 saha vakası: mekanik kapıların TÜMÜ yeşilken, dilekçenin nakden tazmin
savunması KENDİ başka bölümüyle aritmetik olarak çelişiyordu — karşı tarafın 836
rakamı zaten `1100 − 264` idi (264 hesabın DIŞINDA), taslak ise "264, 836'nın
içinde" diyordu. Böyle bir çelişkiyi bir script "yanlış" diye ADLANDIRAMAZ
(sahte kesinlik yasağı); ama GÖRÜNÜR kılabilir: aynı sayının geçtiği yerleri yan
yana koyar, hükmü hakeme/avukata bırakır.

Bu testler kapının üç niteliğini kilitler: (1) çapraz-hesaba giren sayıları
gerçekten yan yana getiriyor, (2) künye/mevzuat gürültüsünü haritaya sokmuyor,
(3) ASLA bloklamıyor ve kırptığında bunu SÖYLÜYOR.
"""
import importlib.util
import os
import subprocess
import sys

import pytest

BETIK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "ortak-avukat", "skills", "oa-dilekce", "scripts", "dilekce_denetim.py")


@pytest.fixture(scope="module")
def dd():
    spec = importlib.util.spec_from_file_location("_test_j_dilekce_denetim", BETIK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_j_dilekce_denetim"] = mod
    spec.loader.exec_module(mod)
    return mod


SAHA_METNI = (
    "Davacı, dava dışı kişilere devredildiğini iddia ettiği 836 payın bedelini istemektedir.\n"
    "Müvekkilin devrettiği toplam pay 770'tir; bunun 264'ü davalı Hayati Kural'a devredilmiştir.\n"
    "Davacının 836 rakamı, devraldığı 1100 paydan yalnızca Kural'a giden 264'ün "
    "düşülmesiyle elde edilmiştir.\n"
)


def test_capraz_hesaba_giren_sayilari_yan_yana_getirir(dd):
    """ASIL KAZANIM: 836 · 770 · 264 · 1100 aynı raporda görünür — hakem
    ilişkiyi tek bakışta kurar."""
    kalemler, _atlanan = dd._sayi_haritasi(SAHA_METNI)
    degerler = {d for d, _y in kalemler}

    assert {"836", "264"} <= degerler, f"çapraz-hesap sayıları haritada yok: {degerler}"
    # 264 birden çok yerde geçiyor; her geçiş satır no + bağlamıyla gelmeli
    yerler = dict(kalemler)["264"]
    assert len(yerler) >= 2
    for satir, bag in yerler:
        assert isinstance(satir, int) and satir >= 1
        assert "264" in bag


def test_tek_gecen_sayi_haritaya_girmez(dd):
    """Harita çapraz-hesap içindir: bir kez geçen sayı çelişki adayı değildir,
    rapora sokmak gürültüdür."""
    kalemler, _ = dd._sayi_haritasi("Toplam 4321 adet belge sunulmuştur.\n")
    assert kalemler == []


def test_kunye_ve_mevzuat_gurultusu_haritaya_girmez(dd):
    """Esas/karar numaraları ve madde numaraları çapraz-HESAP değildir; haritaya
    girerlerse gerçek rakamları boğar (kapı işe yaramaz hâle gelir)."""
    metin = (
        "Yargıtay 17. HD E. 2014/18684 K. 2016/11524 sayılı karar uyarınca;\n"
        "İİK m.278 ve İİK m.278/2-a hükümleri ile HMK m.115 uygulanır.\n"
        "Yargıtay 17. HD E. 2014/18684 K. 2016/11524 kararı tekrar anılmıştır.\n"
        "İİK m.278 yeniden zikredilmiştir.\n"
    )
    kalemler, _ = dd._sayi_haritasi(metin)
    degerler = {d for d, _y in kalemler}

    assert "278" not in degerler, "madde numarası çapraz-hesap sayısı değildir"
    assert "115" not in degerler
    assert not any(d.startswith("2014") or d.startswith("2016") for d in degerler), degerler


def test_binlik_ayraci_ile_yazilan_ayni_sayi_TEK_gruba_duser(dd):
    """'1.100' ve '1100' aynı rakamdır — ayrı gruplara düşerlerse çelişki
    görünmez kalır (kapının bütün amacı kaybolur)."""
    metin = ("Müvekkile devredilen 1.100 payın tamamı kayıtlıdır.\n"
             "Devralınan 1100 pay bakımından iddia yersizdir.\n")
    kalemler, _ = dd._sayi_haritasi(metin)
    degerler = dict(kalemler)

    assert "1100" in degerler, degerler
    assert len(degerler["1100"]) == 2


def test_kirpma_SESSIZ_olmaz(dd):
    """Sessiz kırpma yasağı: rapor sınırı aşılırsa KAÇ kalem dışarıda kaldığı
    sayıyla döner (kapsandı sanılmasın)."""
    parcalar = []
    for i in range(dd._SAYI_AZAMI_KALEM + 5):
        deger = 1000 + i
        parcalar.append(f"Kalem {deger} birinci geçiş.\nKalem {deger} ikinci geçiş.\n")
    kalemler, atlanan = dd._sayi_haritasi("".join(parcalar))

    assert len(kalemler) == dd._SAYI_AZAMI_KALEM
    assert atlanan == 5


def test_deterministik_ayni_metin_ayni_rapor(dd):
    """Aynı metin → bit-özdeş rapor (sıralama geçiş sayısı, sonra sayısal değer)."""
    a, _ = dd._sayi_haritasi(SAHA_METNI)
    b, _ = dd._sayi_haritasi(SAHA_METNI)
    assert a == b
    gecisler = [len(y) for _d, y in a]
    assert gecisler == sorted(gecisler, reverse=True)


def test_J_kapisi_ASLA_bloklamaz_ve_ciktida_gorunur(tmp_path):
    """Advisory sözleşmesi: [J] rapora çıkar ama çıkış kodunu DEĞİŞTİRMEZ."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(SAHA_METNI, encoding="utf-8")

    def _kos(args):
        cp = subprocess.run([sys.executable, BETIK] + args, capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
        return cp.returncode, (cp.stdout or "") + (cp.stderr or "")

    kod, cikti = _kos([str(taslak), "--tip", "cevap", "--taraf", "davali",
                       "--ictihat-muhakeme-yok"])
    assert "[J] SAYI/TARİH HARİTASI" in cikti
    assert "836" in cikti and "264" in cikti

    # Sayıları taşımayan bir metinde [J] hiçbir şey bulmaz — çıkış kodu AYNI kalmalı.
    bos = tmp_path / "bos.md"
    bos.write_text(SAHA_METNI.replace("836", "sekiz yüz otuz altı")
                   .replace("770", "yedi yüz yetmiş").replace("264", "iki yüz altmış dört")
                   .replace("1100", "bin yüz"), encoding="utf-8")
    kod2, cikti2 = _kos([str(bos), "--tip", "cevap", "--taraf", "davali",
                         "--ictihat-muhakeme-yok"])
    assert "[J] SAYI/TARİH HARİTASI" in cikti2
    assert kod == kod2, "[J] çıkış kodunu etkilememeli (advisory)"
