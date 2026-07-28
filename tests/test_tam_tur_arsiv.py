# -*- coding: utf-8 -*-
"""P1-10 (v0.5.5) DÜZELTME — dosya-analiz.md'nin ÜZERİNE yazmadan ÖNCE eski
içeriğin `_oa/arsiv-yerel/dosya-analiz-<ts>.md` olarak nüshalanması
(`cmd_senkron`/`cmd_kaydet` ATOMİK YENİDEN TÜRETİM'inin kayıpsızlık supabı).
"""
import hashlib
import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"


def _load():
    spec = importlib.util.spec_from_file_location("tam_tur_arsiv", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tt = _load()


def _sha(icerik):
    return hashlib.sha256(icerik.encode("utf-8")).hexdigest()[:16]


def _kunye_yaz(kok, kayitlar):
    metin_dizin = pathlib.Path(kok) / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": len(kayitlar), "kayitlar": kayitlar}, ensure_ascii=False),
        encoding="utf-8")
    for k in kayitlar:
        (pathlib.Path(kok) / k["kaynak"]).write_text("x", encoding="utf-8")


def _cikti_birak(kok, ad="01-parca.md", icerik="çalışma evrakı"):
    d = pathlib.Path(kok) / "_oa" / "cikti"
    d.mkdir(parents=True, exist_ok=True)
    (d / ad).write_text(icerik, encoding="utf-8")


def test_senkron_eski_mdyi_arsivler(tmp_path):
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")

    md_yol = pathlib.Path(tt._analiz_md(str(tmp_path)))
    assert md_yol.is_file()  # --baslat doğum-anı iskeleti yazdı
    eski_icerik = md_yol.read_text(encoding="utf-8")

    tt.cmd_senkron(str(tmp_path))

    arsiv_dizin = tmp_path / "_oa" / "arsiv-yerel"
    nushalar = list(arsiv_dizin.glob("dosya-analiz-*.md"))
    assert nushalar, "senkron öncesi md nüshalanmadı"
    assert any(n.read_text(encoding="utf-8") == eski_icerik for n in nushalar)


def test_arsivsiz_ilk_yazimda_hata_vermez(tmp_path):
    # dosya-analiz.md HİÇ yokken ilk --baslat çağrısı arşivleme adımını
    # sorunsuz atlamalı (eski dosya yok → nüshalanacak bir şey yok).
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    kod = tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert kod == 0
    arsiv_dizin = tmp_path / "_oa" / "arsiv-yerel"
    assert not arsiv_dizin.exists() or not list(arsiv_dizin.glob("dosya-analiz-*.md"))
