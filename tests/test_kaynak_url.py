"""KAYNAK-URL — dilekçede künye yanına parantez içinde yazılacak resmî bağlantı.

Avukat talimatı (v0.5.5.3): "dilekçeye işlenen içtihatların linkleri de parantez
içinde verilsin". Bunun ön şartı mekaniktir: bağlantı YAZIM anında değil, kararın
fiilen çekildiği TEYİT anında yakalanmalıdır. Yazım aşamasında model bir URL
hatırlayamaz, ancak uydurabilir — ve uydurma bağlantı çıplak künyeden DAHA
KÖTÜDÜR: çıplak künye "teyit edilmedi" der, sahte bağlantı "teyit edildi" der.

Bu testler üç şeyi kilitler: (1) URL teyit anında muhakeme kaydına GEÇER,
(2) biçimi bozuk URL fail-closed REDDEDİLİR, (3) URL verilmezse satır HİÇ
yazılmaz (yokluk sessiz boş-değere dönüşmez — dilekçe yazarı "kayıt yok" ile
"kayıt boş" arasında ayrım yapabilmelidir).
"""
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
BETIK = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
         / "scripts" / "oa_hafiza.py")

ALINTI = ("Borclunun mal kacirma kastiyla hareket ettigi ve tasarrufun ivazsiz "
          "oldugu dosya kapsamiyla sabittir.")
BAG = ("Somut olayda da tasarruf ivazsiz olup borclunun kastini gosterir; "
       "muvekkil lehine dogrudan uygulanabilir niteliktedir.")


def _kos(args, kok):
    cp = subprocess.run([sys.executable, str(BETIK)] + args,
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(kok))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def kok(tmp_path):
    kod, cikti = _kos(["init", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, cikti
    (tmp_path / "dokum.txt").write_text(
        "Yargitay 17. Hukuk Dairesi 2019/1234 E. 2021/5678 K.\n" + ALINTI + "\n",
        encoding="utf-8")
    return tmp_path


def _teyit_args(kok, ek=None):
    return ["teyit", "--kok", str(kok), "--arac", "ictihat_getir",
            "--sorgu", "tasarrufun iptali ivazsiz",
            "--sonuc", "Yargitay 17. HD 2019/1234 E. 2021/5678 K.",
            "--dokum-icerik", "@" + str(kok / "dokum.txt"),
            "--damga", "LEHE", "--ilgili-kisim", ALINTI, "--bag", BAG] + (ek or [])


def _muhakeme(kok):
    yol = kok / "_oa" / "cikti" / "03-ictihat-muhakeme.md"
    return yol.read_text(encoding="utf-8") if yol.is_file() else ""


def test_kaynak_url_muhakeme_kaydina_gecer(kok):
    url = "https://karararama.yargitay.gov.tr/karar/12345"
    kod, cikti = _kos(_teyit_args(kok, ["--kaynak-url", url]), kok)
    assert kod == 0, cikti

    icerik = _muhakeme(kok)
    assert f"**KAYNAK-URL:** {url}" in icerik, icerik


def test_url_verilmezse_satir_HIC_yazilmaz(kok):
    """Yokluk, boş değere DÖNÜŞMEZ: dilekçe yazarı 'kayıt yok' ile 'kayıt boş'
    arasını ayırt edebilmeli — boş bir `**KAYNAK-URL:**` satırı, parantezin
    açılıp boş bırakılmasına davetiye olurdu."""
    kod, cikti = _kos(_teyit_args(kok), kok)
    assert kod == 0, cikti

    icerik = _muhakeme(kok)
    assert "KAYNAK-URL" not in icerik, icerik
    assert "**DAMGA:** LEHE" in icerik, "diğer alanlar normal yazılmalı"


@pytest.mark.parametrize("bozuk", [
    "yargitay.gov.tr/karar/1",                 # şema yok
    "javascript:alert(1)",                     # http(s) değil
    "https://ornek.gov.tr/a b",                # boşluk
    "https://ornek.gov.tr/a\nikinci-satir",    # satır sonu (kayıt enjeksiyonu)
    "ftp://ornek.gov.tr/karar",                # yanlış şema
])
def test_bozuk_url_FAIL_CLOSED_reddedilir(kok, bozuk):
    """Biçimi bozuk bir değeri sessizce kabul etmek 'teyitli link' görüntüsü
    üretirdi; satır sonu ise muhakeme kaydına sahte alan enjekte edebilirdi."""
    kod, cikti = _kos(_teyit_args(kok, ["--kaynak-url", bozuk]), kok)

    assert kod != 0, f"bozuk URL kabul edildi: {bozuk!r}\n{cikti}"
    assert "--kaynak-url" in cikti
    assert "KAYNAK-URL" not in _muhakeme(kok), "RET'te muhakeme kaydı yazılmamalı"


def test_url_damgasiz_cagrida_da_dogrulanir(kok):
    """Biçim denetimi --damga'dan BAĞIMSIZDIR: URL verilen HER çağrıda geçerli
    olmalı, yoksa ARAMA satırlarında bozuk URL sessizce kütüğe girerdi."""
    kod, cikti = _kos(["teyit", "--kok", str(kok), "--arac", "ictihat_ara",
                       "--sorgu", "tasarrufun iptali", "--sonuc", "12 sonuç",
                       "--kaynak-url", "bozuk-adres"], kok)
    assert kod != 0, cikti
    assert "--kaynak-url" in cikti


def test_skill_kurali_parantez_ve_uydurma_yasagini_soyluyor():
    """Kural metinde de bağlayıcı olmalı — script tek başına 'parantez aç/açma'
    davranışını üretmez, onu yazım disiplini üretir."""
    dilekce = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
               / "SKILL.md").read_text(encoding="utf-8")
    ictihat = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ictihat"
               / "SKILL.md").read_text(encoding="utf-8")

    assert "KAYNAK-URL" in dilekce and "parantez" in dilekce
    assert "--kaynak-url" in ictihat
    for metin in (dilekce, ictihat):
        assert "uydurma" in metin.lower() or "uydurulmaz" in metin.lower()
