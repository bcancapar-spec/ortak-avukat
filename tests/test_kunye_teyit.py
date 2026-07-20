# -*- coding: utf-8 -*-
"""oa-kontrol / kunye_teyit.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
Ayrıca uçtan uca (CLI/exit kodu) davranışı subprocess ile de doğrular, çünkü
gerçek "teslim engeli" garantisi exit kodunda yaşar (main() sys.exit çağırır).

REGRESYON (bkz. modül başındaki ESAS_RE/KARAR_RE notu — Fable 5 bulgusu, HIGH):
Standart 'E. 2023/1234 K. 2023/5678' künye biçiminde KARAR_RE'nin ters-etiket
alternatifi esas numarasını + 'K.' etiketini yutuyordu; gerçek karar numarasına
hiç sıra gelmiyordu (atif.karar=None). segment_eslesir yalnız ESAS'ı arayınca,
kütükte esas'ı bulunan ama KARAR NO'SU UYDURMA künye TEYİTLİ + exit 0 geçiyordu
— kapının hedeflediği asıl halüsinasyon sınıfında (esas doğru, karar uydurma)
yanlış-negatif. Bu dosya o deliği hem çıkarım hem uçtan-uca CLI seviyesinde kapatır.
"""
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts" / "kunye_teyit.py"


def _load():
    assert SCRIPT.is_file(), f"kunye_teyit.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("kunye_teyit", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kt = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ── ictihat_cikar(): düz künyede (E. X K. Y) esas VE karar İKİSİ DE çıkmalı ──

def test_duz_kunye_esas_ve_karar_ikisi_de_cikar():
    """REGRESYON: 'E. 2023/1234 K. 2023/5678' → esas=2023/1234, karar=2023/5678.
    Eski bug'da karar=None kalıyordu (ters alternatif esas'ı + 'K.' etiketini yutuyordu)."""
    metin = "Yargıtay 3. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı emsaldir."
    atiflar = kt.ictihat_cikar(metin)
    assert len(atiflar) == 1
    a = atiflar[0]
    assert a.esas == "2023/1234"
    assert a.karar == "2023/5678", "REGRESYON: düz künyede karar no çıkarılmadı (eski KARAR_RE yutma bug'ı)"


def test_ters_sirali_kunye_simetrik_yutma_yok():
    """Simetrik durum: 'K. X E. Y' → ESAS_RE'nin ters alternatifi karar no'yu
    yutmamalı; esas=Y, karar=X ayrı ayrı doğru çıkmalı."""
    metin = "K. 2023/5678 E. 2023/1234 sayılı karar."
    atiflar = kt.ictihat_cikar(metin)
    assert len(atiflar) == 1
    a = atiflar[0]
    assert a.esas == "2023/1234"
    assert a.karar == "2023/5678"


def test_ters_bicim_hala_calisiyor_REGRESYON():
    """Zaten çalışan ters (numara-önce) biçim ('2021/5967 E. 2022/1234 K.')
    fix sonrası bozulmamalı."""
    metin = "12. HD, 2021/5967 E. 2022/1234 K. sayılı kararında..."
    atiflar = kt.ictihat_cikar(metin)
    assert len(atiflar) == 1
    a = atiflar[0]
    assert a.esas == "2021/5967"
    assert a.karar == "2022/1234"


def test_iki_ayri_atif_metin_arasi_ile_karismaz():
    """İki ayrı düz künye, aralarında metinle ayrılmışsa her biri kendi
    esas/karar çiftini doğru bulmalı (çapraz-kontaminasyon yok)."""
    metin = ("3. HD'nin E. 2023/100 K. 2023/200 sayılı kararı ile "
             "4. HD'nin E. 2024/300 K. 2024/400 sayılı kararı birlikte değerlendirilmiştir.")
    atiflar = kt.ictihat_cikar(metin)
    ciftler = sorted((a.esas, a.karar) for a in atiflar)
    assert ciftler == [("2023/100", "2023/200"), ("2024/300", "2024/400")]


# ── Uçtan uca (CLI): kütükte doğru karar var, taslakta UYDURMA karar var ────

def test_uydurma_karar_no_teyitsiz_exit1(tmp_path):
    """ALTIN VAKA (Fable 5 bulgusu): kütükte 'E. 2023/1234 K. 2023/5678' var;
    taslakta AYNI esas ama FARKLI (uydurma) karar no 'E. 2023/1234 K. 2029/9999'
    var. Kapı bunu TEYİTSİZ görüp exit 1 vermeli (eskiden yanlışlıkla TEYİTLİ +
    exit 0 veriyordu, çünkü karar no hiç çıkarılamıyordu)."""
    kutuk_dizin = tmp_path / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True)
    kutuk = kutuk_dizin / "kunye-teyit.md"
    kutuk.write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 3. HD'nin E. 2023/1234 K. 2029/9999 sayılı "
        "kararı emsal teşkil etmektedir.\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["taslak.md", "--kutuk", str(kutuk), "--dokum-dizin", str(tmp_path / "_oa" / "teyit" / "dokum"),
         "--cikti-dizin", str(tmp_path / "_oa" / "cikti")],
        cwd=tmp_path,
    )
    assert kod == 1, f"uydurma karar no TEYİTSİZ/exit 1 vermeli; çıktı:\n{cikti}"
    assert "TEYİTSİZ" in cikti
    assert "TESLİM ENGELİ" in cikti


def test_dogru_karar_no_teyitli_exit0(tmp_path):
    """Kontrast: taslaktaki karar no kütükle BİREBİR aynıysa TEYİTLİ + exit 0."""
    kutuk_dizin = tmp_path / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True)
    kutuk = kutuk_dizin / "kunye-teyit.md"
    kutuk.write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 3. HD'nin E. 2023/1234 K. 2023/5678 sayılı "
        "kararı emsal teşkil etmektedir.\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["taslak.md", "--kutuk", str(kutuk), "--dokum-dizin", str(tmp_path / "_oa" / "teyit" / "dokum"),
         "--cikti-dizin", str(tmp_path / "_oa" / "cikti")],
        cwd=tmp_path,
    )
    assert kod == 0, f"doğru karar no TEYİTLİ/exit 0 vermeli; çıktı:\n{cikti}"
    assert "TEYİTLİ" in cikti


# ── EK-FİX: --kok (oa_hafiza.py/tam_tur.py simetrisi) ──────────────────────

def test_kok_ile_varsayilan_yollar_kok_altinda_cozulur(tmp_path):
    """--kok verilirse --kutuk/--dokum-dizin/--cikti-dizin AÇIKÇA verilmeden
    <KOK>/_oa/teyit/kunye-teyit.md vb. altında bulunmalı — cwd'den BAĞIMSIZ.
    Gerçek Denizli testinde bu eksiklik 'Failed to run citation gate'e yol açtı."""
    kok = tmp_path / "dava-klasoru"
    kutuk_dizin = kok / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True)
    (kutuk_dizin / "kunye-teyit.md").write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 3. HD'nin E. 2023/1234 K. 2023/5678 sayılı "
        "kararı emsal teşkil etmektedir.\n",
        encoding="utf-8",
    )
    # cwd BİLEREK farklı (tmp_path, kök klasörün kendisi DEĞİL) — --kok cwd'den
    # bağımsız çözülmeli; --kutuk/--dokum-dizin/--cikti-dizin hiç verilmiyor.
    kod, cikti = _cli(["taslak.md", "--kok", str(kok)], cwd=tmp_path)
    assert kod == 0, f"--kok ile kütük bulunup TEYİTLİ/exit 0 vermeli; çıktı:\n{cikti}"
    assert "TEYİTLİ" in cikti
    assert "KÜTÜK YOK" not in cikti


def test_kok_verilse_de_acik_kutuk_onceliklidir(tmp_path):
    """Açıkça verilen --kutuk, --kok'un türettiği varsayılanı EZER (geriye uyum)."""
    kok = tmp_path / "dava-klasoru"
    (kok / "_oa" / "teyit").mkdir(parents=True)
    # --kok altında KASITLI olarak kütük YOK; ayrı bir açık kütük dosyası veriyoruz.
    acik_kutuk = tmp_path / "baska-yer" / "kunye-teyit.md"
    acik_kutuk.parent.mkdir(parents=True)
    acik_kutuk.write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 3. HD'nin E. 2023/1234 K. 2023/5678 sayılı "
        "kararı emsal teşkil etmektedir.\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["taslak.md", "--kok", str(kok), "--kutuk", str(acik_kutuk)], cwd=tmp_path)
    assert kod == 0, f"açık --kutuk --kok'u ezmeli; çıktı:\n{cikti}"
    assert "TEYİTLİ" in cikti


def test_kok_verilmezse_davranis_eskisiyle_ayni(tmp_path):
    """--kok hiç verilmezse (geriye uyum) davranış CWD-göreli VARSAYILAN_* ile
    AYNI kalmalı — kütük yoksa KÜTÜK YOK + exit 1."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text("E. 2023/1234 K. 2023/5678 sayılı karar.\n", encoding="utf-8")
    kod, cikti = _cli(["taslak.md"], cwd=tmp_path)
    assert kod == 1
    assert "KÜTÜK YOK" in cikti


def test_cikti_izi_teyit_sayilmaz(tmp_path):
    """Kendi-kendini-teyit deliği kapalı kalmalı: uydurma karar no yalnız
    `_oa/cikti/` (model çalışma evrakı) içinde geçiyorsa bile TEYİT SAYILMAZ;
    kapı yine TEYİTSİZ + exit 1 vermeli, yalnız [BİLGİ] notu düşülmeli."""
    teyit_dizin = tmp_path / "_oa" / "teyit"
    teyit_dizin.mkdir(parents=True)
    kutuk = teyit_dizin / "kunye-teyit.md"
    kutuk.write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    (cikti_dizin / "03-taslak-antitez.md").write_text(
        "E. 2023/1234 K. 2029/9999 sayılı karara göre ...\n", encoding="utf-8",
    )
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 3. HD'nin E. 2023/1234 K. 2029/9999 sayılı "
        "kararı emsal teşkil etmektedir.\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["taslak.md", "--kutuk", str(kutuk), "--dokum-dizin", str(teyit_dizin / "dokum"),
         "--cikti-dizin", str(cikti_dizin)],
        cwd=tmp_path,
    )
    assert kod == 1, f"cikti-yalnız izi TEYİT SAYMAMALI; çıktı:\n{cikti}"
    assert "TEYİTSİZ" in cikti
    assert "TEYİT SAYILMAZ" in cikti, "kendi-kendini-teyit deliği notu görünmüyor"


def test_kutuk_yok_hepsi_teyitsiz_exit1(tmp_path):
    """Kütük dosyası hiç yoksa hiçbir atıf teyit edilemez — yapısal blok."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text("E. 2023/1234 K. 2023/5678 sayılı karar.\n", encoding="utf-8")
    kod, cikti = _cli(
        ["taslak.md", "--kutuk", str(tmp_path / "yok" / "kunye-teyit.md")],
        cwd=tmp_path,
    )
    assert kod == 1
    assert "KÜTÜK YOK" in cikti


def test_atif_yok_exit0(tmp_path):
    """Taslakta hiç hukuki atıf yoksa doğrulanacak bir şey yoktur — kapı açık."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Bu taslakta hiçbir içtihat veya mevzuat atfı yoktur.\n", encoding="utf-8")
    kod, cikti = _cli(["taslak.md", "--kutuk", str(tmp_path / "yok.md")], cwd=tmp_path)
    assert kod == 0
    assert "BULUNAMADI" in cikti


# ── F) KÜNYE TEYİT ÖNCE-BAK (--once-bak) — M2-3 ─────────────────────────────
# Advisory: teslim engeli DEĞİL, her hâlde exit 0 (usage hatası hariç). Amaç:
# kütükte ZATEN VAR olan bir künye için gereksiz tekrar MCP teyit turunu önlemek.

def test_once_bak_kutukte_var_ise_VAR_der(tmp_path):
    kok = tmp_path / "dava-klasoru"
    kutuk_dizin = kok / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True)
    (kutuk_dizin / "kunye-teyit.md").write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["--once-bak", "Yargıtay 3. HD, E. 2023/1234, K. 2023/5678", "--kok", str(kok)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "[VAR]" in cikti
    assert "GEREKSİZDİR" in cikti


def test_once_bak_kutukte_yok_ise_YOK_der(tmp_path):
    kok = tmp_path / "dava-klasoru"
    kutuk_dizin = kok / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True)
    (kutuk_dizin / "kunye-teyit.md").write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["--once-bak", "Yargıtay 3. HD, E. 2099/1, K. 2099/2", "--kok", str(kok)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "[YOK]" in cikti
    assert "MCP teyidi gerekli" in cikti


def test_once_bak_farkli_daire_uydurma_karar_YOK_der(tmp_path):
    """Aynı esas/karar no'su AMA farklı daire — merci katmanı 'celiski' bulur,
    yine de eşleşen segment izlendiği için TEYİTLİ/VAR sayılabilir; bu test
    esas/karar hiç bulunmayan bir uydurma karar no'nun kesin YOK dönmesini
    doğrular (regresyon: karar no'nun yutulmadığından emin ol)."""
    kok = tmp_path / "dava-klasoru"
    kutuk_dizin = kok / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True)
    (kutuk_dizin / "kunye-teyit.md").write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararında ...\n",
        encoding="utf-8",
    )
    kod, cikti = _cli(
        ["--once-bak", "Yargıtay 3. HD, E. 2023/1234, K. 2029/9999", "--kok", str(kok)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "[YOK]" in cikti


def test_once_bak_kutuk_yok_YOK_der_exit0(tmp_path):
    """Kütük hiç yoksa önce-bak yapılamaz ama bu bir kullanım hatası DEĞİLDİR
    (advisory) — MCP teyidinin gerektiğini bildirip exit 0 döner."""
    kod, cikti = _cli(
        ["--once-bak", "E. 2023/1234 K. 2023/5678",
         "--kutuk", str(tmp_path / "yok" / "kunye-teyit.md")],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "[YOK]" in cikti
    assert "Kütük dosyası yok" in cikti


def test_once_bak_kunye_parse_edilemezse_hata_exit1(tmp_path):
    """Verilen metinden esas/karar hiç çıkarılamıyorsa (kullanım hatası) exit 1."""
    kod, cikti = _cli(["--once-bak", "bu bir künye değil"], cwd=tmp_path)
    assert kod == 1, cikti
    assert "[HATA]" in cikti


def test_once_bak_taslak_argumani_gerekmez(tmp_path):
    """--once-bak modunda pozisyonel taslak argümanı HİÇ verilmese de çalışmalı."""
    kod, cikti = _cli(["--once-bak", "E. 2023/1234 K. 2023/5678"], cwd=tmp_path)
    assert kod == 0
    assert "[YOK]" in cikti  # kütük yok (varsayılan CWD-göreli yol)


def test_taslak_verilmezse_ve_once_bak_yoksa_kullanim_hatasi(tmp_path):
    """Ne taslak ne --once-bak verilmezse net bir kullanım hatası (exit != 0) döner."""
    kod, cikti = _cli([], cwd=tmp_path)
    assert kod != 0
    assert "taslak" in cikti.lower()
