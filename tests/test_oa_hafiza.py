# -*- coding: utf-8 -*-
"""oa-pipeline / oa_hafiza.py için ALTIN VAKA testleri.

CLI çağrıları subprocess ile yapılır (main() argparse kullanıyor); her test
kendi tmp_path kökünü kullanarak izole çalışır.

Odak: `oturum-kapat` (KAPANIŞ ritüeli) — ajan-brif kural #4'ün ('her üretim
_oa/cikti'ya çalışma evrakı') MEKANİK denetimi: _oa/cikti boşsa görünür bir
UYARI basılmalı (bloklamaz), doluysa basılmamalı.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


UZUN_NOT = ("(1) defter --denetle'den geçildi, adım 5'te kalındı. "
            "(2) süre flag'leri güncel. (3) bekleyen avukat kararı yok.")


def test_oturum_kapat_cikti_bossa_uyarir(tmp_path):
    """_oa/cikti hiç dosya içermiyorsa oturum-kapat, kural #4 UYARISI basmalı
    (KAPANIŞ bloklanmaz — yalnız görünür kılınır)."""
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _cli(["oturum-ac", "--kok", str(tmp_path)], cwd=tmp_path)

    kod, cikti = _cli(["oturum-kapat", "--not", UZUN_NOT, "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"boş cikti kapanışı BLOKLAMAMALI, yalnız uyarmalı:\n{cikti}"
    assert "UYARI" in cikti
    assert "kural #4" in cikti or "kural" in cikti.lower()
    # Kilit her hâlde kaldırılmış olmalı (uyarı engel değil).
    assert not (tmp_path / "_oa" / ".oturum-kilidi").exists()


def test_oturum_kapat_cikti_doluysa_uyarmaz(tmp_path):
    """_oa/cikti'da en az bir çalışma evrakı varsa kural #4 uyarısı basılmamalı
    (pozitif kontrast vaka)."""
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _cli(["oturum-ac", "--kok", str(tmp_path)], cwd=tmp_path)

    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "01-parca.md").write_text("çalışma evrakı", encoding="utf-8")

    kod, cikti = _cli(["oturum-kapat", "--not", UZUN_NOT, "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    assert "UYARI: _oa/cikti boş" not in cikti


# ── GATE B — ajan-brif OKUMA DİSİPLİNİ maddesi ─────────────────────────────

def test_ajan_brif_okuma_disiplini_blogu_var(tmp_path):
    """`ajan-brif` çıktısı, GATE B okuma_kapisi.py'ye ve tam-yükleme dedup
    defterine atıf yapan bir OKUMA DİSİPLİNİ maddesi içermeli — büyük evrağı
    haritadan okuma + gerektiğinde tam yükleme + deftere loglama advisory'si."""
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["ajan-brif", "--parca", "oa-vakia", "--gorev", "kronoloji çıkar",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "OKUMA DİSİPLİNİ" in cikti
    assert "okuma_kapisi.py" in cikti
    assert "--tam-yukle-kaydet" in cikti
    assert "DERİNLİK ASLA KISILMAZ" in cikti or "DERİNLİK KISILMAZ" in cikti
