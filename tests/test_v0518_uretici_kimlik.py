# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİR ÜRETİCİLERİ · S5 OPSİYONEL KİMLİKLER (B-3, üretici ayağı).

NEDEN VAR: Fable tutarlılık raporu (2026-10-07) B-3 — ortak kimlik uzayı yok:
`capraz_denetim` vakıa ↔ kıyas eşleşmesini ≥4 karakterlik alt-dize
benzerliğiyle yapıyor (yanlış eşleşme / yanlış kopukluk). P2 çözümü: vakia
`olaylar[]` öğesinde opsiyonel `"id"` (str), kıyas `kucuk_onerme.vakialar[]`
öğesinde opsiyonel `"vakia_id"` (str); tüketici (Görev 1, capraz_denetim)
önce kimlik eşitliğine bakar, yoksa ad eşleşmesini "ad-eşleşmesi (belirsiz)"
etiketiyle gösterir.

Bu dosyanın kilitlediği üretici sözleşmesi (S5): bu iki alan ŞEMA HATASI
SAYILMAZ — `saglikli` / `kritik_bosluk` değişmez, BİÇİMSİZ/GEÇERSİZ bloğuna
düşmez; kıyas çıktısı `vakia_id`yi aşağı akışa AYNEN taşır. Benzersizlik
denetimi UYARIDIR (aynı kimlik iki kayıtta → görünür not; karar avukatın) —
mükerrer kimlik kimlik-eşlemesini belirsiz kılar, ama olgunun kendisini
geçersiz kılmaz.

Karakterizasyon notu (dürüst): "şema hatası değil" ayağı tabanda da
sağlanıyordu (iki motor bilinmeyen alanı yok sayar); kilit, gelecekte bir
"bilinmeyen alan = hata" sıkılaştırmasının bu iki alanı yutmasını önler.
Mükerrerlik uyarısı ise yeni davranıştır (RED görüldü).
Bütün veriler kurgudur (anayasa m.7).
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
VAKIA_MATRIS = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
KIYAS = SKILLS / "oa-kiyas" / "scripts" / "kiyas_denetim.py"


def _kos(script, argumanlar, cwd):
    cp = subprocess.run([sys.executable, str(script), *argumanlar], cwd=str(cwd),
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    assert "Traceback" not in (cp.stderr or ""), cp.stderr[-1500:]
    return cp.returncode, cp.stdout or ""


def _yaz(yol, nesne):
    yol.write_text(json.dumps(nesne, ensure_ascii=False, indent=2), encoding="utf-8")


def _vakia(olaylar):
    return {"iddialar": [{"id": "I1", "metin": "Mal kurgu tarihte teslim edildi", "tur": "vakia"}],
            "olaylar": olaylar}


def _olay(kimlik, olgu, tarih="2025-03-12"):
    o = {"tarih": tarih, "olgu": olgu, "belge": f"{olgu} belgesi (kurgu)",
         "destekler": ["I1"], "ispat_durumu": "belgeli"}
    if kimlik is not None:
        o["id"] = kimlik
    return o


def _kiyas(vakialar):
    return {"buyuk_onerme": {"norm": "TBK m.49 (kurgu çıpa)",
                             "ictihat": [{"kunye": "Yargıtay 4. HD 2099/1 E. (kurgu)", "dogrulama": "teyitli"}],
                             "unsurlar": [{"id": "fiil", "ad": "Fiil"}]},
            "kucuk_onerme": {"vakialar": vakialar},
            "sonuc": "Sorumluluk doğar (kurgu)."}


def _vakia_kaydi(kimlik, metin):
    v = {"metin": metin, "karsilar": ["fiil"], "dayanak_delil": ["tutanak (kurgu)"]}
    if kimlik is not None:
        v["vakia_id"] = kimlik
    return v


def test_opsiyonel_kimlik_alanlari_sema_hatasi_degil(tmp_path):
    """vakia `olaylar[].id` ve kıyas `kucuk_onerme.vakialar[].vakia_id`
    yazılmış dosya tamamen temiz kalır; kıyas çıktısı kimliği aynen taşır."""
    _yaz(tmp_path / "vakia.json", _vakia([_olay("O1", "Teslim"), _olay("O2", "Fatura", "2025-03-13")]))
    kod, out = _kos(VAKIA_MATRIS, ["--dogrula", "vakia.json", "--json", "v.json"], cwd=tmp_path)
    v = json.loads((tmp_path / "v.json").read_text(encoding="utf-8"))
    assert kod == 0 and v["saglikli"] is True
    assert "BİÇİMSİZ" not in out and "GEÇERSİZ" not in out and "mükerrer" not in out
    assert ">>> Dosya olgu/delil bütünlüğü TAMAM <<<" in out

    _yaz(tmp_path / "kiyas.json", _kiyas([_vakia_kaydi("O1", "Davalı fiili işledi (kurgu)"),
                                           _vakia_kaydi("O2", "Fatura kesildi (kurgu)")]))
    kod, out = _kos(KIYAS, ["kiyas.json", "--json", "k.json"], cwd=tmp_path)
    k = json.loads((tmp_path / "k.json").read_text(encoding="utf-8"))
    assert kod == 0 and k["kritik_bosluk"] is False
    assert "⚠" not in out and "✗" not in out, out
    assert [x["vakia_id"] for x in k["kucuk_onerme"]["vakialar"]] == ["O1", "O2"], \
        "kimlik aşağı akışa (capraz_denetim) AYNEN taşınmalı"


def test_mukerrer_kimlik_uyari_verir_saglikli_degismez(tmp_path):
    """Aynı kimlik iki kayıtta: görünür UYARI (hangi kimlik, kaç kez) — ama
    ne `saglikli` ne `kritik_bosluk` değişir (şema hatası değil, eşleme
    belirsizliği); kimliksiz kayıtlar denetime girmez."""
    _yaz(tmp_path / "vakia.json", _vakia([
        _olay("O1", "Teslim"), _olay("O1", "Fatura", "2025-03-13"),
        _olay(None, "Kimliksiz olay", "2025-03-14"), _olay(None, "Kimliksiz olay 2", "2025-03-15")]))
    kod, out = _kos(VAKIA_MATRIS, ["--dogrula", "vakia.json", "--json", "v.json"], cwd=tmp_path)
    v = json.loads((tmp_path / "v.json").read_text(encoding="utf-8"))
    assert kod == 0 and v["saglikli"] is True
    assert "[BİLGİ]" in out
    assert "olaylar: 'id' mükerrer: O1 (2 kez)" in out, out
    assert "BİÇİMSİZ" not in out

    _yaz(tmp_path / "kiyas.json", _kiyas([
        _vakia_kaydi("V1", "Davalı fiili işledi (kurgu)"), _vakia_kaydi("V1", "Fatura kesildi (kurgu)"),
        _vakia_kaydi(None, "Kimliksiz vakıa (kurgu)")]))
    kod, out = _kos(KIYAS, ["kiyas.json", "--json", "k.json"], cwd=tmp_path)
    k = json.loads((tmp_path / "k.json").read_text(encoding="utf-8"))
    assert kod == 0 and k["kritik_bosluk"] is False
    assert "⚠ kucuk_onerme.vakialar: 'vakia_id' mükerrer: V1 (2 kez)" in out, out
    assert "KRİTİK BOŞLUK" not in out
