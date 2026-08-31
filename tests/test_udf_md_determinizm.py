# -*- coding: utf-8 -*-
"""v0.5.15 — UDF→MD ÇEVRİMİNDE DETERMİNİZM VE DENETLENEBİLİRLİK.

Avukatın talebi: *"Dönüşümlerde determinizm istiyoruz."* Bu iki ayrı şeydir ve
ikisi de burada kilitlenir:

  **Tekrarlanabilirlik** — aynı girdi + aynı sürüm → BAYT-ÖZDEŞ çıktı.
  **Denetlenebilirlik** — üçüncü bir taraf (ya da altı ay sonraki oturum)
  çıktının gerçekten o girdiden üretildiğini İSPATLAYABİLMELİ. Bunun için
  kayıt yetmez; yeniden koşu gerekir (`--denetle`).

Ölçülmüş kırılma eksenleri (Fable danışmanlığı, v0.5.15) ve buradaki karşılıkları:

  - satır sonu (Win/Linux)  → yazımda daima `\\n`; metin modu yasak
  - dosya sistemi sıralaması → çıktıya giden koleksiyon daima `sorted()`
  - `set` iterasyonu        → hash-seed testi (aşağıda)
  - duvar saati / mutlak yol → çekirdek çıktıya GİREMEZ; yalnız provenansta
  - `icerik_sha256`         → RENDERER'DAN BAĞIMSIZ; sürümler arası SABİT
    kalması gereken asıl delil parmak izi. Değişirse "kayıpsızlık tanımımız
    değişti" demektir ve ayrıca gerekçe ister.

Tamamen SENTETİK girdi — gerçek müvekkil dosyası CI'a asla girmez.
"""
import hashlib
import importlib.util as _iu
import io
import os
import re
import subprocess
import sys
import zipfile

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODUL_YOLU = os.path.join(REPO, "plugins", "ortak-avukat", "skills",
                          "oa-ingest", "scripts", "udf_md.py")

_spec = _iu.spec_from_file_location("udf_md_det", MODUL_YOLU)
udf_md = _iu.module_from_spec(_spec)
_spec.loader.exec_module(udf_md)


def _udf_yaz(yol, cdata, elemanlar=""):
    """Sentetik ama GERÇEKÇİ bir .udf üretir (ZIP + content.xml)."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<template format_id="1.8">'
        '<content><![CDATA[' + cdata + ']]></content>'
        '<elements resolver="hvl-default">' + elemanlar + '</elements>'
        '<styles><style name="default" family="Times New Roman" size="12"/></styles>'
        '</template>')
    with zipfile.ZipFile(yol, "w") as z:
        z.writestr("content.xml", xml.encode("utf-8"))
    return yol


def _basit(tmp_path, ad="a.udf"):
    metin = "BİRİNCİ PARAGRAF\nİKİNCİ PARAGRAF\nÜÇÜNCÜ SATIR\n"
    el = ('<paragraph Alignment="0"><content startOffset="0" length="16"/></paragraph>'
          '<paragraph Alignment="0"><content startOffset="17" length="16"/></paragraph>'
          '<paragraph Alignment="0"><content startOffset="34" length="12"/></paragraph>')
    return _udf_yaz(str(tmp_path / ad), metin, el)


def _md(yol):
    md, _k = udf_md.udf_markdown_cikar(yol)
    return md


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ─────────────────── TEKRARLANABİLİRLİK ───────────────────

def test_ayni_girdi_ayni_surecte_bayt_ozdes(tmp_path):
    y = _basit(tmp_path)
    assert _sha(_md(y)) == _sha(_md(y))


def test_ayni_girdi_ayri_surecte_ve_farkli_hash_seed_ozdes(tmp_path):
    """`set`/`dict` iterasyon sırası çıktıya sızarsa hash-seed bunu ortaya çıkarır."""
    y = _basit(tmp_path)
    betik = (
        "import importlib.util as u,sys,hashlib\n"
        "s=u.spec_from_file_location('m',%r)\n"
        "m=u.module_from_spec(s); s.loader.exec_module(m)\n"
        "md,_=m.udf_markdown_cikar(%r)\n"
        "sys.stdout.write(hashlib.sha256(md.encode('utf-8')).hexdigest())\n"
        % (MODUL_YOLU, y))
    sonuc = []
    for seed in ("0", "1", "424242"):
        ort = dict(os.environ, PYTHONHASHSEED=seed, PYTHONUTF8="1")
        cp = subprocess.run([sys.executable, "-c", betik], capture_output=True,
                            text=True, env=ort, timeout=120)
        assert cp.returncode == 0, cp.stderr[-400:]
        sonuc.append(cp.stdout.strip())
    assert len(set(sonuc)) == 1, "hash seed çıktıyı değiştirdi: %s" % sonuc


def test_dosya_yolu_ciktiyi_degistirmez(tmp_path):
    """Mutlak yol çekirdek çıktıya SIZAMAZ — makineler arası tekrarlanabilirlik."""
    a = _basit(tmp_path / "" if False else tmp_path, "aynidosya.udf")
    alt = tmp_path / "baska" / "derin"
    alt.mkdir(parents=True)
    b = _basit(alt, "aynidosya.udf")
    assert _sha(_md(a)) == _sha(_md(b))


def test_ciktida_zaman_damgasi_yok(tmp_path):
    """Duvar saati çıktıya girerse bayt-özdeşlik ölür."""
    md = _md(_basit(tmp_path))
    assert not re.search(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", md), md[:300]


def test_satir_sonu_daima_LF(tmp_path):
    """Windows'ta CRLF üretilirse aynı dosya iki platformda farklı sha alır."""
    md = _md(_basit(tmp_path))
    assert "\r" not in md


# ─────────────────── DENETLENEBİLİRLİK ───────────────────

def test_icerik_sha_uretiliyor_ve_kararli(tmp_path):
    y = _basit(tmp_path)
    _md1, k1 = udf_md.udf_markdown_cikar(y)
    _md2, k2 = udf_md.udf_markdown_cikar(y)
    assert k1.get("icerik_sha256")
    assert len(k1["icerik_sha256"]) == 64
    assert k1["icerik_sha256"] == k2["icerik_sha256"]


def test_icerik_sha_SUNUM_secimlerinden_bagimsiz(tmp_path):
    """Asıl delil parmak izi: renderer seçenekleri değişse de SABİT kalmalı.

    Bu, sürümler-arası sözleşmenin çekirdeğidir — `cikti_sha` sunum geliştikçe
    değişir, `icerik_sha` değişmez. Değiştiği gün bu test kırmızı yanar ve
    değişiklik bir KEŞİF değil bir KARAR olur.
    """
    y = _basit(tmp_path)
    _a, k1 = udf_md.udf_markdown_cikar(y, alanlar=True, veri=True, hiza_notu=True)
    _b, k2 = udf_md.udf_markdown_cikar(y, alanlar=False, veri=False, hiza_notu=False)
    assert k1["icerik_sha256"] == k2["icerik_sha256"]


def test_ayni_icerik_farkli_dosya_ayni_icerik_sha(tmp_path):
    a = _basit(tmp_path, "bir.udf")
    b = _basit(tmp_path, "iki.udf")
    _m1, k1 = udf_md.udf_markdown_cikar(a)
    _m2, k2 = udf_md.udf_markdown_cikar(b)
    assert k1["icerik_sha256"] == k2["icerik_sha256"]


def test_icerik_degisince_icerik_sha_degisir(tmp_path):
    a = _basit(tmp_path, "a.udf")
    b = _udf_yaz(str(tmp_path / "b.udf"), "BAŞKA METİN\n",
                 '<paragraph><content startOffset="0" length="11"/></paragraph>')
    _m1, k1 = udf_md.udf_markdown_cikar(a)
    _m2, k2 = udf_md.udf_markdown_cikar(b)
    assert k1["icerik_sha256"] != k2["icerik_sha256"]


def test_modul_surumu_kunyede(tmp_path):
    """Provenans: hangi sürümün ürettiği kayıtlı olmazsa bayatlık görülemez."""
    _md_, k = udf_md.udf_markdown_cikar(_basit(tmp_path))
    assert k.get("surum")


# ─────────────────── SALT OKUMA (K9) ───────────────────

def test_kaynak_arsive_asla_yazilmaz(tmp_path):
    """E-imzalı nüsha ham baytları üzerinden imzalanır; okuma onu bozamaz."""
    y = _basit(tmp_path)
    once = hashlib.sha256(open(y, "rb").read()).hexdigest()
    onceki_mtime = os.stat(y).st_mtime_ns
    udf_md.udf_markdown_cikar(y)
    assert hashlib.sha256(open(y, "rb").read()).hexdigest() == once
    assert os.stat(y).st_mtime_ns == onceki_mtime


# ─────────────────── SESSİZ KAYIP YASAĞI ───────────────────

def test_bozuk_dosyada_hata_alanı_dolu_ve_asla_firlatmaz(tmp_path):
    p = tmp_path / "bozuk.udf"
    p.write_bytes(b"bu bir zip degil")
    md, k = udf_md.udf_markdown_cikar(str(p))
    assert md == ""
    assert k.get("hata"), "sessiz boş çıktı YASAK — hata alanı dolmalı"


def test_bos_dosya_sessizce_gecmez(tmp_path):
    p = tmp_path / "bos.udf"
    p.write_bytes(b"")
    md, k = udf_md.udf_markdown_cikar(str(p))
    assert k.get("hata")
