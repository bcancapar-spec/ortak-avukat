# -*- coding: utf-8 -*-
"""[G4] KAYNAK-URL TUTARLILIĞI (v0.5.7) — ictihat_muhakeme_denetim.py.

Kullanıcı kuralı (Denizli 754 sonrası): dilekçede bir karardan bahsedilince
bağlantısı da yazılmalı. Zincirin v0.5.5.3'ten beri duran ilk yarısı (teyit
anında `--kaynak-url` → muhakeme kaydına `**KAYNAK-URL:**`) bu kapıyla
dilekçe ucuna bağlanır:
  (a) künye yanında kütükte izi OLMAYAN bağlantı → BLOK (uydurma-bağlantı
      çıplak künyeden DAHA KÖTÜDÜR — 'teyit edildi' der);
  (b) kayıtlı bağlantı dilekçeye işlenmemiş → UYARI (bloklamaz — araç URL
      döndürmemişse künye bağlantısız yazılır, uydurulmaz).
"""
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
          / "scripts" / "ictihat_muhakeme_denetim.py")

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
URL = "https://ornek-resmi-kaynak.adalet.gov.tr/karar/12345"


def _kok_kur(kaynak_url=None):
    kok = pathlib.Path(tempfile.mkdtemp())
    dokum = kok / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True)
    (dokum / "kaynak.md").write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 tam metni...\n", encoding="utf-8")
    (kok / "_oa" / "teyit" / "kunye-teyit.md").write_text(
        "# Künye Teyit Kütüğü\n| 2026-08-07 | ictihat_getir | sorgu | "
        "E. 2023/1234 K. 2023/5678 | LEHE | dokum |\n", encoding="utf-8")
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    satirlar = [
        "# 01 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
        "**DAMGA:** LEHE", ""]
    if kaynak_url:
        satirlar.insert(4, f"**KAYNAK-URL:** {kaynak_url}")
    satirlar += ["## İLGİLİ-KISIM", "...ilgili kısım...", "",
                 "## DAVAYA-BAĞ", "...davaya bağ açıklaması (kırk karakteri aşan "
                 "gerçekçi bir bağ cümlesi)...", "",
                 "## AYIRT-ETME", "", ""]
    (cikti / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")
    return kok


def _taslak_yaz(kok, gövde):
    t = kok / "taslak.md"
    t.write_text(gövde, encoding="utf-8")
    return t


def _cli(taslak, kok):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(taslak), "--kok", str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def test_kayitli_url_dilekcede_varsa_temiz():
    kok = _kok_kur(kaynak_url=URL)
    taslak = _taslak_yaz(kok, f"Somut olayda Yargıtay 4. HD'nin E. 2023/1234, "
                              f"K. 2023/5678 sayılı kararı ({URL}) emsaldir.\n")
    kod, cikti = _cli(taslak, kok)
    assert kod == 0, cikti
    assert "UYDURMA" not in cikti
    assert "İŞLENMEMİŞ" not in cikti


def test_kayitli_url_dilekceye_islenmemisse_uyari_ama_bloklamaz():
    kok = _kok_kur(kaynak_url=URL)
    taslak = _taslak_yaz(kok, "Somut olayda Yargıtay 4. HD'nin E. 2023/1234, "
                              "K. 2023/5678 sayılı kararı emsaldir.\n")
    kod, cikti = _cli(taslak, kok)
    assert kod == 0, "kayıtlı-link-kullanılmamış YALNIZ uyarıdır — bloklamaz"
    assert "[G4]" in cikti and "İŞLENMEMİŞ" in cikti


def test_kutukte_izi_olmayan_link_kunye_yaninda_blok():
    kok = _kok_kur(kaynak_url=None)   # kayıtta hiç URL yok
    taslak = _taslak_yaz(kok, "Somut olayda Yargıtay 4. HD'nin E. 2023/1234, "
                              "K. 2023/5678 sayılı kararı "
                              "(https://uydurma-site.example.com/k/99) emsaldir.\n")
    kod, cikti = _cli(taslak, kok)
    assert kod == 1, f"uydurma bağlantı TESLİM ENGELİ olmalıydı:\n{cikti}"
    assert "UYDURMA" in cikti and "TESLİM ENGELİ" in cikti


def test_kunyeden_uzak_link_dokunulmaz():
    """Künye penceresi dışındaki bir bağlantı (ör. UYAP portal yönergesi)
    [G4]'ün konusu değildir — yanlış-BLOK üretilmez (amaç çizgisi)."""
    kok = _kok_kur(kaynak_url=URL)
    taslak = _taslak_yaz(kok,
        f"Somut olayda Yargıtay 4. HD'nin E. 2023/1234, K. 2023/5678 sayılı "
        f"kararı ({URL}) emsaldir.\n\n\n\n\n"
        "Başvuru https://www.turkiye.gov.tr uzerinden de izlenebilir.\n")
    kod, cikti = _cli(taslak, kok)
    assert kod == 0, cikti
    assert "UYDURMA" not in cikti
