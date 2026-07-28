# -*- coding: utf-8 -*-
"""P1-7 (v0.5.5) — [F] İçtihat Muhakeme Zinciri kapısı dilekce_denetim.py'de
VARSAYILAN AÇIK; AKILLI FAIL-OPEN (DAR) ile kırılmaz.

Kapsam:
1. Bayraksız çağrı + içtihatli (esas/karar künyeli) taslak + kayıtsız kök
   (_oa var ama muhakeme kaydı yok) → [F] koşar ve BLOK üretir (çıplak atıf).
2. --ictihat-muhakeme-yok → [F] atlanır VE raporda AÇIKÇA görünür.
3. _oa'sız kök → [F] [BİLGİ] ile atlanır, exit'e etkisiz (diğer unsurlar
   tamamsa exit 0).
4. Künyesiz VE anlatımsız taslak → [F] [BİLGİ] ile atlanır, bloklamaz.
5. Künyesiz AMA "Yargıtay/emsal karar" anlatımlı taslak + _oa var → [F]
   ATLANMAZ, rapora GÖRÜNÜR "künyesiz içtihat anlatımı" uyarısı düşer.
6. Mevcut test_dilekce_denetim*.py testleri DEĞİŞMEDEN geçer (regresyon).
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"

TEMIZ_TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: 12345678901)
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

ICTIHATLI_TASLAK = TEMIZ_TASLAK.replace(
    "HUKUKİ SEBEPLER:",
    "HUKUKİ SEBEPLER:\nYargıtay 4. Hukuk Dairesi'nin E. 2023/1234, K. 2023/5678 sayılı "
    "kararında da aynı ilkeye işaret edilmiştir.",
)

ANLATIM_KUNYESIZ_TASLAK = TEMIZ_TASLAK.replace(
    "HUKUKİ SEBEPLER:",
    "HUKUKİ SEBEPLER:\nYargıtay'ın yerleşik içtihadı da bu yöndedir; emsal karar bu "
    "görüşü doğrulamaktadır.",
)


def _cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )


def test_bayraksiz_cagri_icithatli_taslak_kayitsiz_kok_blok(tmp_path):
    (tmp_path / "_oa").mkdir()
    taslak = tmp_path / "taslak.md"
    taslak.write_text(ICTIHATLI_TASLAK, encoding="utf-8")
    cp = _cli([str(taslak), "--tip", "dava", "--taraf", "davaci", "--kok", str(tmp_path)],
              tmp_path)
    assert cp.returncode == 1, cp.stdout + cp.stderr
    assert "[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI (ictihat_muhakeme_denetim.py" in cp.stdout
    assert "çıplak" in cp.stdout.lower() or "BLOK" in cp.stdout


def test_ictihat_muhakeme_yok_atlanir_ve_gorunur(tmp_path):
    (tmp_path / "_oa").mkdir()
    taslak = tmp_path / "taslak.md"
    taslak.write_text(ICTIHATLI_TASLAK, encoding="utf-8")
    cp = _cli([str(taslak), "--tip", "dava", "--taraf", "davaci", "--kok", str(tmp_path),
               "--ictihat-muhakeme-yok"], tmp_path)
    assert "--ictihat-muhakeme-yok ile AÇIKÇA" in cp.stdout
    # opt-out edildiği için [F] blok üretmemeli (diğer unsurlar temiz → exit 0)
    assert cp.returncode == 0, cp.stdout + cp.stderr


def test_oa_siz_kok_bilgi_ile_atlanir_exit_etkisiz(tmp_path):
    taslak = tmp_path / "taslak.md"
    taslak.write_text(ICTIHATLI_TASLAK, encoding="utf-8")
    # --kok VERİLMİYOR ve cwd'de _oa yok → "no_oa" fail-open yolu.
    cp = _cli([str(taslak), "--tip", "dava", "--taraf", "davaci"], tmp_path)
    assert "[BİLGİ] atlandı: _oa/ bulunamadı" in cp.stdout
    assert cp.returncode == 0, cp.stdout + cp.stderr


def test_kunyesiz_ve_anlatimsiz_taslak_bloklamaz(tmp_path):
    (tmp_path / "_oa").mkdir()
    taslak = tmp_path / "taslak.md"
    taslak.write_text(TEMIZ_TASLAK, encoding="utf-8")
    cp = _cli([str(taslak), "--tip", "dava", "--taraf", "davaci", "--kok", str(tmp_path)],
              tmp_path)
    assert "[BİLGİ] atlandı" in cp.stdout
    assert "içtihat künyesi/anlatımı hiç yok" in cp.stdout or "içtihat künyesi" in cp.stdout
    assert cp.returncode == 0, cp.stdout + cp.stderr


def test_kunyesiz_anlatim_var_taslak_atlanmaz_gorunur_uyari(tmp_path):
    (tmp_path / "_oa").mkdir()
    taslak = tmp_path / "taslak.md"
    taslak.write_text(ANLATIM_KUNYESIZ_TASLAK, encoding="utf-8")
    cp = _cli([str(taslak), "--tip", "dava", "--taraf", "davaci", "--kok", str(tmp_path)],
              tmp_path)
    assert "künyesiz içtihat anlatımı" in cp.stdout
    assert "[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI (ictihat_muhakeme_denetim.py" in cp.stdout
    # Anlatım var ama esas/karar no'lu atıf yok → G2/G3 hiç tetiklenmez,
    # yalnız G1 uyarısı (bloklamaz) — bu kapı tek başına exit'i 1 yapmaz.
    assert cp.returncode == 0, cp.stdout + cp.stderr
