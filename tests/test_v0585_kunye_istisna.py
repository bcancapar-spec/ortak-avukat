# -*- coding: utf-8 -*-
"""v0.5.8.5 — B1 KENDİ-DOSYA-NO İSTİSNASI (`kunye_teyit.py`).

Saha bulgusu: taslağın BAŞLIK/KÜNYE bloğundaki kendi dosya numarası satırı
("DOSYA NO : 2024/123 Esas" gibi) içtihat künyesi sanılıp TEYİTSİZ/teslim
engeli üretiyordu — bu bir içtihat atfı DEĞİL, dosyanın kendi kimliğidir.

Yeni sözleşme:
- DOSYA NO / ESAS NO / MERCİ etiketli satırlardaki esas-only ("NNNN/NNN Esas")
  desenler içtihat künyesi taramasından MUAF tutulur;
- muafiyet SESSİZ değildir: `_oa/defter/istisna-kayitlari.jsonl` dosyasına
  ortak şemayla (zaman/tur/ilgili/gerekce/onay/imza) bir kayıt düşülür ve
  rapora [BİLGİ] satırı basılır;
- GERÇEK içtihat künyeleri (daire adı ve/veya E.+K. çifti) — başlık satırında
  bile — aynen yakalanmaya devam eder (muafiyet daraltılmıştır, fail-closed).

Tüm veriler SENTETİKTİR (m.7 — gerçek dava no/kişi adı/klasör yolu yazılmaz).
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
          / "scripts" / "kunye_teyit.py")


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _iskele(tmp_path, taslak_metin):
    teyit = tmp_path / "_oa" / "teyit"
    (teyit / "dokum").mkdir(parents=True)
    (teyit / "kunye-teyit.md").write_text(
        "# Künye Teyit Kütüğü\n| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
        "|---|---|---|---|---|\n", encoding="utf-8")
    taslak = tmp_path / "taslak.md"
    taslak.write_text(taslak_metin, encoding="utf-8")
    return taslak


def _istisna_kayitlari(tmp_path):
    yol = tmp_path / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    if not yol.is_file():
        return []
    return [json.loads(s) for s in
            yol.read_text(encoding="utf-8").splitlines() if s.strip()]


BASLIK_BLOKLU_TASLAK = (
    "T.C. ÖRNEK NÖBETÇİ İŞ MAHKEMESİNE\n\n"
    "DOSYA NO : 2024/123 Esas\n\n"
    "## AÇIKLAMALAR\n"
    "Bu taslakta başka hiçbir hukuki atıf bulunmamaktadır.\n"
)


def test_kendi_dosya_no_satiri_muaf_ve_istisna_kaydi_duser(tmp_path):
    _iskele(tmp_path, BASLIK_BLOKLU_TASLAK)
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "TEYİTSİZ" not in cikti
    assert "MUAF" in cikti.upper()

    kayitlar = _istisna_kayitlari(tmp_path)
    assert len(kayitlar) == 1, kayitlar
    k = kayitlar[0]
    assert k["tur"] == "kunye-istisna"
    assert k["onay"] == "otomatik-kural"
    assert "kunye_teyit" in k["imza"]
    assert "2024/123" in k["ilgili"]
    assert k["gerekce"]
    assert "T" in k["zaman"]  # ISO tarih-saat


def test_esas_no_etiketli_satir_da_muaf(tmp_path):
    _iskele(tmp_path, "ESAS NO: 2025/45 Esas\n\nAçıklama: başka atıf yok.\n")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert len(_istisna_kayitlari(tmp_path)) == 1


def test_gercek_ictihat_kunyesi_yakalanmaya_devam_eder(tmp_path):
    """Muafiyet, aynı taslaktaki GERÇEK içtihat künyesini görünmez KILAMAZ:
    dosya-no satırı muaf düşer, teyitsiz gerçek künye yine TESLİM ENGELİ."""
    taslak_metin = (
        BASLIK_BLOKLU_TASLAK +
        "\nSomut olayda Yargıtay 9. HD, E. 2023/111, K. 2023/222 sayılı "
        "kararı emsal teşkil etmektedir.\n"
    )
    _iskele(tmp_path, taslak_metin)
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "TEYİTSİZ" in cikti
    assert "2023/111" in cikti
    # yalnız dosya-no satırı muaf — tek istisna kaydı
    assert len(_istisna_kayitlari(tmp_path)) == 1


def test_baslik_satirindaki_tam_kunye_muaf_degil(tmp_path):
    """Etiketli satırda bile DAİRE + E./K. çifti taşıyan bir metin gerçek
    içtihat künyesi olabilir — muafiyet DARALTILMIŞTIR, yakalanır."""
    _iskele(tmp_path,
            "ESAS NO: Yargıtay 4. HD, E. 2023/10, K. 2023/20 sayılı karar\n")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "TEYİTSİZ" in cikti
    assert _istisna_kayitlari(tmp_path) == []


def test_govde_metnindeki_esas_only_atif_muaf_degil(tmp_path):
    """Muafiyet yalnız DOSYA NO/ESAS NO/MERCİ etiketli satırlar içindir —
    gövde metnindeki esas-only bir atıf eskisi gibi TEYİTSİZ sayılır
    (aşırı-muafiyet yok, fail-closed)."""
    _iskele(tmp_path,
            "Karşı yan 2024/55 Esas sayılı dosyaya dayanmaktadır.\n")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "TEYİTSİZ" in cikti
    assert _istisna_kayitlari(tmp_path) == []
