# -*- coding: utf-8 -*-
"""[G5] AŞILMIŞ-İÇTİHAT (v0.5.8) — ictihat_muhakeme_denetim.py.

Semantica superseded deseninin devşirmesi (anayasa m.0 devşirme protokolü,
Can kararı 2026-08-12): İBK / kanun değişikliği / daire kaymasıyla AŞILMIŞ
bir içtihat LEHE dayanak olarak dilekçede kalamaz:
  (a) DAMGA=LEHE + aşılmışlık alanı dolu + künye dilekçede atıf → BLOK;
  (b) DAMGA=LEHE + aşılmış ama dilekçede kullanılmamış → UYARI (kütük hijyeni);
  (c) DAMGA=ALEYHE + aşılmış → UYARI (cephanelik bilgisi — bloklamaz);
  (d) aşılmışlık alanları boş → kapı hiç ateşlemez (geriye dönük uyum).
"""
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
          / "scripts" / "ictihat_muhakeme_denetim.py")

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
ASAN = "Yargıtay İBK, E. 2025/2, K. 2026/1, T. 15.03.2026"


def _kok_kur(damga="LEHE", asan_kaynak=None, asilma_tarihi=None):
    kok = pathlib.Path(tempfile.mkdtemp())
    dokum = kok / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True)
    (dokum / "kaynak.md").write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 tam metni...\n", encoding="utf-8")
    (kok / "_oa" / "teyit" / "kunye-teyit.md").write_text(
        "# Künye Teyit Kütüğü\n| 2026-08-07 | ictihat_getir | sorgu | "
        f"E. 2023/1234 K. 2023/5678 | {damga} | dokum |\n", encoding="utf-8")
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    satirlar = [
        "# 01 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
        f"**DAMGA:** {damga}", ""]
    if asan_kaynak:
        satirlar.append(f"**AŞAN-KAYNAK:** {asan_kaynak}")
    if asilma_tarihi:
        satirlar.append(f"**AŞILMA-TARİHİ:** {asilma_tarihi}")
    satirlar += ["", "## İLGİLİ-KISIM", "...ilgili kısım...", "",
                 "## DAVAYA-BAĞ", "...davaya bağ açıklaması (kırk karakteri aşan "
                 "gerçekçi bir bağ cümlesi)...", "",
                 "## AYIRT-ETME", "", ""]
    if damga == "ALEYHE":
        # ALEYHE kayıt dilekçe atfı olarak DEĞİL, kütük bilgisi olarak sınanır.
        pass
    (cikti / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")
    return kok


def _cli(kok, taslak_metin):
    t = kok / "taslak.md"
    t.write_text(taslak_metin, encoding="utf-8")
    p = subprocess.run(
        [sys.executable, str(SCRIPT), str(t), "--kok", str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")

ATIFLI = ("İstinaf sebeplerimiz Yargıtay 4. HD E. 2023/1234 K. 2023/5678 "
          "sayılı kararına dayanmaktadır.\n")
ATIFSIZ = "Bu dilekçede içtihat atfı bulunmamaktadır.\n"


def test_lehe_asilmis_atifta_blok():
    kok = _kok_kur(damga="LEHE", asan_kaynak=ASAN, asilma_tarihi="15.03.2026")
    kod, out = _cli(kok, ATIFLI)
    assert kod == 1
    assert "[G5]" in out and "KALAMAZ" in out


def test_lehe_alanlar_bos_kapi_atesleMEZ():
    kok = _kok_kur(damga="LEHE")
    kod, out = _cli(kok, ATIFLI)
    assert "[G5]" not in out


def test_aleyhe_asilmis_yalniz_uyari():
    kok = _kok_kur(damga="ALEYHE", asan_kaynak=ASAN)
    kod, out = _cli(kok, ATIFSIZ)
    assert "[G5]" in out and "cephanelik" in out
    # ALEYHE+aşılmış G5'ten BLOK üretmez (başka kapılar taslağa göre değişebilir;
    # G5'e özgü engel metni bulunmamalı).
    assert "aşılmış karar lehte" not in out.lower() or "TESLİM ENGELİ — İBK" not in out


def test_lehe_asilmis_atifsiz_uyari_bloklamaz():
    kok = _kok_kur(damga="LEHE", asan_kaynak=ASAN)
    kod, out = _cli(kok, ATIFSIZ)
    assert "[G5]" in out and "gözden" in out
    assert "SONUÇ-EK: TESLİM ENGELİ — İBK" not in out
