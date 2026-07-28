# -*- coding: utf-8 -*-
"""P1-10 (v0.5.5) — CANLI-SENKRON KAPISI: bayat working-memory (dosya-analiz.md)
üstüne yeni bir adım UYGULANDI yazılamaz.

Kapsam:
1. _oa/cikti'ya yeni dosya + eski md → UYGULANDI exit != 0, mesajda
   'tam_tur.py --senkron' komutu.
2. md'nin mtime'ı tazelenince (senkron sonrası) aynı yazım geçer.
3. dosya-analiz.json yoksa (tam_tur akışı hiç kullanılmamış) kontrol
   TAMAMEN atlanır.
4. aynı-saniye/2sn tolerans içindeki fark yanlış pozitif üretmez.
5. --serh (>=30 kr) ile geçilir; olay 'serh:true' ile işlenir.
6. *ictihat-muhakeme*/teyit dosyaları bayatlık hesabından HARİÇ — yalnız bu
   tür bir dosya yeni olsa dahi md 'bayat' sayılmaz.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _baslat(tmp_path):
    kod, cikti = _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti


def _kunye_kur(tmp_path):
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def _analiz_kur(tmp_path, eski_mtime_offset=-100):
    """dosya-analiz.md + .json'u kurar; md mtime'ı şimdiden `eski_mtime_offset`
    saniye ÖNCEYE ayarlanır (varsayılan: 100sn ESKİ — açıkça bayat)."""
    analiz = tmp_path / "_oa" / "analiz"
    analiz.mkdir(parents=True, exist_ok=True)
    (analiz / "dosya-analiz.json").write_text(json.dumps({"durum": "test"}), encoding="utf-8")
    md = analiz / "dosya-analiz.md"
    md.write_text("# Dosya Analizi (iskelet)\n", encoding="utf-8")
    hedef = time.time() + eski_mtime_offset
    os.utime(md, (hedef, hedef))
    return md


def _cikti_dosya_yaz(tmp_path, ad, icerik="çalışma evrakı"):
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    dosya = cikti / ad
    dosya.write_text(icerik, encoding="utf-8")
    return dosya


def _isle(tmp_path, adim="4", parca="oa-vakia", ek_args=None):
    args = ["--isle", "--adim", adim, "--parca", parca, "--durum", "UYGULANDI",
            "--kanit", UZUN_KANIT, "--kok", str(tmp_path)]
    if ek_args:
        args += ek_args
    return _cli(args, cwd=tmp_path)


def test_bayat_md_uygulandi_reddedilir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _analiz_kur(tmp_path)
    _cikti_dosya_yaz(tmp_path, "04-vakia.md")

    kod, cikti = _isle(tmp_path)
    assert kod != 0, cikti
    assert "CANLI-SENKRON" in cikti
    assert "--senkron" in cikti


def test_senkron_sonrasi_gecer(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    md = _analiz_kur(tmp_path)
    _cikti_dosya_yaz(tmp_path, "04-vakia.md")

    kod, _ = _isle(tmp_path)
    assert kod != 0

    # "--senkron koştu" simülasyonu: md'nin mtime'ını şimdiye tazele.
    simdi = time.time() + 10
    os.utime(md, (simdi, simdi))

    kod2, cikti2 = _isle(tmp_path)
    assert kod2 == 0, cikti2


def test_dosya_analiz_json_yoksa_atlanir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    # dosya-analiz.json YOK (tam_tur hiç kullanılmamış) — yalnız eski bir
    # cikti dosyası var, md de yok; kontrol tamamen atlanmalı.
    _cikti_dosya_yaz(tmp_path, "04-vakia.md")

    kod, cikti = _isle(tmp_path)
    assert kod == 0, cikti
    assert "CANLI-SENKRON" not in cikti


def test_tolerans_ici_fark_yanlis_pozitif_uretmez(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    md = _analiz_kur(tmp_path, eski_mtime_offset=0)
    # cikti dosyasını md'den yalnız 1sn SONRA yaz (2sn tolerans içinde).
    dosya = _cikti_dosya_yaz(tmp_path, "04-vakia.md")
    hedef = os.path.getmtime(md) + 1
    os.utime(dosya, (hedef, hedef))

    kod, cikti = _isle(tmp_path)
    assert kod == 0, cikti
    assert "CANLI-SENKRON" not in cikti


def test_serh_ile_gecilir_ve_olayda_gorunur(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _analiz_kur(tmp_path)
    _cikti_dosya_yaz(tmp_path, "04-vakia.md")

    serh = "Avukat bilinçli olarak elden devam ediyor, senkron sonra koşulacak"
    kod, cikti = _isle(tmp_path, ek_args=["--serh", serh])
    assert kod == 0, cikti
    assert "ŞERHLİ UYGULANDI" in cikti
    assert "CANLI-SENKRON ŞERH ile geçildi" in cikti


def test_ictihat_muhakeme_ve_teyit_dosyalari_bayatlik_haricinde(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    md = _analiz_kur(tmp_path, eski_mtime_offset=0)
    # yalnız *ictihat-muhakeme* ve *teyit* desenli dosyalar YENİ — bunlar
    # hariç tutulduğundan md hâlâ 'taze' sayılmalı.
    ileri = time.time() + 500
    d1 = _cikti_dosya_yaz(tmp_path, "03-ictihat-muhakeme.md")
    os.utime(d1, (ileri, ileri))
    d2 = _cikti_dosya_yaz(tmp_path, "teyit-ozet.md")
    os.utime(d2, (ileri, ileri))

    kod, cikti = _isle(tmp_path)
    assert kod == 0, cikti
    assert "CANLI-SENKRON" not in cikti
