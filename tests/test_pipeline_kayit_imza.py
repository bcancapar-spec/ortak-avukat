# -*- coding: utf-8 -*-
"""GÖREV A (v0.5.5 devamı) — DEFTER BÜTÜNLÜĞÜ + DURUM.md FİZİKSEL TÜRETİM.

B1 (kök sebep): model pipeline_kayit.py CLI'sini hiç çağırmadan
`_oa/defter/pipeline-olaylar.jsonl`e DOĞRUDAN bir satır ekleyebilir — bu
BLOKLANMAZ (append-only/kayıpsızlık invaryantı bozulmaz; kullanıcı kabul
kuralı: "tek-yazar ilkesi MÜVEKKİL LEHİNE delindiyse KABULÜMÜZDÜR"), ama artık
GÖRÜNMEZ de KALMAZ:

  1) ARAÇ İMZASI — pipeline_kayit.py'nin CLI'sinden (--baslat/--isle/--katman/
     --arac-hata/--avukat-karari) geçen HER olaya deterministik bir 'imza'
     alanı eklenir. İmza yok/tutmuyorsa olay "model-beyanlı" sayılır.
  2) DURUM.md artık defterin BEYANINA değil FİZİKSEL KANITA (disk) bakarak
     her (adım,parça) için dört hâli (beyan+artefakt / beyan var-artefakt yok
     / artefakt var-beyan yok / ikisi de yok) — TANIMLI olduğu adımlarda —
     gösterir; ayrıca "defter: N araç-imzalı, M model-beyanlı" sayacı +
     döküm/muhakeme/makbuz sayaçları basılır.
  3) HİÇBİR SENARYODA BLOKLAMA YOKTUR (exit kodu her zaman 0 / mevcut kapı
     davranışıyla aynı) — yalnız AYIRT EDİLİR.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."

sys.path.insert(0, str(SCRIPT.parent))
import pipeline_kayit as pk  # noqa: E402  (test-only in-process erişim)


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _baslat(tmp_path):
    kod, cikti = _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti


def _olaylar_yol(tmp_path):
    olaylar_yol, _durum_yol = pk._yollar(type("A", (), {"kok": str(tmp_path), "yol": None})())
    return olaylar_yol


def _durum_md(tmp_path):
    return (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")


# ── (1) ARAÇ İMZASI — CLI yazımı vs elle/doğrudan jsonl yazımı ─────────────

def test_cli_ile_yazilan_baslat_arac_imzali_sayilir(tmp_path):
    _baslat(tmp_path)
    icerik = _durum_md(tmp_path)
    assert "Defter Bütünlüğü" in icerik
    assert "1 araç-imzalı, 0 model-beyanlı" in icerik


def test_durum_md_imza_sinirini_belgeler(tmp_path):
    """KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 1) — imza algoritması
    anahtarsızdır/kaynak kodda açıktır; bu SINIR artık DURUM.md'de KOŞULSUZ
    (her zaman) görünür — yalnız kod yorumunda değil."""
    _baslat(tmp_path)
    icerik = _durum_md(tmp_path)
    assert "ZAYIF" in icerik
    assert "kasıtlı taklidi engellemez" in icerik


def test_cli_ile_yazilan_isle_olayi_arac_imzali_etiketlenir(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = _durum_md(tmp_path)
    assert "adım 0 (MANİFEST) / manifest: UYGULANDI" in icerik
    satir = [s for s in icerik.splitlines() if "adım 0 (MANİFEST) / manifest:" in s][0]
    assert "[araç-imzalı]" in satir
    assert "2 araç-imzalı, 0 model-beyanlı" in icerik  # baslat + isle


def test_elle_jsonle_dogrudan_eklenen_olay_model_beyanli_sayilir_ve_bloklanmaz(tmp_path):
    """B1'in tam kendisi: model CLI'yi ATLAYIP deftere doğrudan satır ekliyor.
    Sonuç BLOKLANMAZ (append-only bozulmaz) ama DURUM.md'de görünür kalır."""
    _baslat(tmp_path)
    olaylar_yol = _olaylar_yol(tmp_path)
    pk.olay_ekle(olaylar_yol, {
        "zaman": pk.simdi(), "tip": "adim", "adim": 0, "parca": "manifest",
        "durum": "UYGULANDI", "kanit": "elle deftere düşürülmüş sahte kanıt metni.",
    })
    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti  # BLOKLAMA YOK
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 0 (MANİFEST) / manifest:" in s][0]
    assert "[model-beyanlı]" in satir
    assert "1 araç-imzalı, 1 model-beyanlı" in icerik
    assert "imzasız/elle düşürülmüş satır var" in icerik


def test_uydurma_imza_alani_yeniden_hesaplananla_uyusmuyorsa_yine_model_beyanli(tmp_path):
    """İmza alanı VAR ama tutmuyorsa (uydurma/bozuk) yine model-beyanlı sayılır
    — yalnız 'imza anahtarı var mı' sorulmaz, DOĞRULANIR."""
    _baslat(tmp_path)
    olaylar_yol = _olaylar_yol(tmp_path)
    pk.olay_ekle(olaylar_yol, {
        "zaman": pk.simdi(), "tip": "adim", "adim": 0, "parca": "manifest",
        "durum": "UYGULANDI", "kanit": "elle düşürülmüş ama sahte imzalı kanıt.",
        "imza": "0000000000000000",
    })
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 0 (MANİFEST) / manifest:" in s][0]
    assert "[model-beyanlı]" in satir


# ── (2) DURUM.md FİZİKSEL DÖRT-HÂL SINIFLANDIRMASI (adım-5 KIYAS örneği) ───

def test_elle_yazilan_beyan_var_artefakt_yok_fiziksel_etiketi_gorunur(tmp_path):
    """B4 saha bulgusunun testi: adım-5 (KIYAS) deftere 'UYGULANDI' diye elle
    düşürülmüş ama '_oa/cikti/05-kiyas*' VE '*ictihat-muhakeme*' diskte YOK.
    DURUM.md bunu 'beyan VAR / artefakt YOK' olarak GÖSTERİR — BLOKLAMAZ."""
    _baslat(tmp_path)
    olaylar_yol = _olaylar_yol(tmp_path)
    pk.olay_ekle(olaylar_yol, {
        "zaman": pk.simdi(), "tip": "adim", "adim": 5, "parca": "oa-kiyas",
        "durum": "UYGULANDI", "kanit": "elle deftere düşürülmüş, artefaktsız kanıt metni.",
    })
    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti  # BLOKLAMA YOK (bu yalnız DURUM.md türetimi, --isle DEĞİL)
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 5 (KIYAS) / oa-kiyas:" in s][0]
    assert "[model-beyanlı]" in satir
    assert "beyan VAR / artefakt YOK" in satir
    # KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/bulgu 3) — etiket artık
    # HANGİ ayağın eksik olduğunu (05-kiyas* VE muhakeme kaydı ikisi de yok)
    # da söylüyor.
    assert "eksik:" in satir
    assert "05-kiyas" in satir
    assert "ictihat-muhakeme" in satir


def test_yalniz_muhakeme_kaydi_eksikken_eksik_metni_bunu_belirtir(tmp_path):
    """Saha bulgusu B4'ün TAM olayı: '_oa/cikti/05-kiyas*' diskte VAR (avukat
    onu görüyor) ama '*ictihat-muhakeme*' YOK. Eksik metni yalnız EKSİK olan
    ayağı ('ictihat-muhakeme') anmalı, mevcut olan (05-kiyas) hakkında yanlış
    eksik iddiası ÜRETMEMELİ."""
    _baslat(tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "05-kiyas.md").write_text("Kıyas gövdesi " * 10, encoding="utf-8")
    olaylar_yol = _olaylar_yol(tmp_path)
    pk.olay_ekle(olaylar_yol, {
        "zaman": pk.simdi(), "tip": "adim", "adim": 5, "parca": "oa-kiyas",
        "durum": "UYGULANDI", "kanit": "elle deftere düşürülmüş kanıt.",
    })
    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 5 (KIYAS) / oa-kiyas:" in s][0]
    assert "eksik:" in satir
    assert "ictihat-muhakeme" in satir
    assert "05-kiyas* yok/boş" not in satir


def test_gercek_artefaktli_cli_isle_beyan_artefakt_ve_arac_imzali_gosterir(tmp_path):
    """Pozitif kontrol: hem artefakt (05-kiyas* + *ictihat-muhakeme*) hem CLI
    üzerinden (araç-imzalı) --isle çağrısı varsa DURUM.md 'temiz' gösterir:
    beyan+artefakt VE araç-imzalı."""
    _baslat(tmp_path)
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "05-kiyas.md").write_text("Kıyas gövdesi " * 10, encoding="utf-8")
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text("Muhakeme gövdesi " * 10, encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 5 (KIYAS) / oa-kiyas:" in s][0]
    assert "[araç-imzalı]" in satir
    assert "beyan+artefakt" in satir
    assert "artefakt YOK" not in satir


def test_artefakt_var_ama_hic_beyan_edilmemis_gorunur(tmp_path):
    """Ters durum: fiziksel artefakt DİSKTE VAR ama defterde hiçbir olay YOK
    (adım hâlâ BEKLIYOR) — 'artefakt VAR / beyan YOK' etiketiyle görünür."""
    _baslat(tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "05-kiyas.md").write_text("Kıyas gövdesi " * 10, encoding="utf-8")
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text("Muhakeme gövdesi " * 10, encoding="utf-8")
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 5 (KIYAS) / oa-kiyas:" in s][0]
    assert "BEKLIYOR" in satir
    assert "[araç-imzalı]" not in satir and "[model-beyanlı]" not in satir  # hiç beyan yok
    assert "artefakt VAR / beyan YOK" in satir


def test_tanimsiz_artefaktli_adimda_fiziksel_etiket_basilmaz(tmp_path):
    """adım-2 (oa-alan/KONUMLAMA) için P0-6 artefakt tanımı yok — FİZİKSEL
    etiketi basılmamalı (yanlış-pozitif üretmeme ilkesi)."""
    _baslat(tmp_path)
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    kod, cikti = _cli(
        ["--isle", "--adim", "2", "--parca", "oa-alan", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if "adım 2 (KONUMLAMA) / oa-alan:" in s][0]
    assert "FİZİKSEL" not in satir


# ── (3) Döküm / Muhakeme / Makbuz sayaçları ─────────────────────────────────

def test_dokum_muhakeme_makbuz_sayaclari_bolumu_var_ve_dogru_sayar(tmp_path):
    _baslat(tmp_path)
    dokum = tmp_path / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True, exist_ok=True)
    (dokum / "01.md").write_text("x", encoding="utf-8")
    (dokum / "02.md").write_text("x", encoding="utf-8")
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "ornek-ictihat-muhakeme.md").write_text("Muhakeme " * 5, encoding="utf-8")
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = _durum_md(tmp_path)
    assert "Döküm / Muhakeme / Makbuz Sayaçları" in icerik
    assert "Döküm (_oa/teyit/dokum/): 2 dosya" in icerik
    assert "İçtihat muhakeme kaydı (_oa/cikti/*ictihat-muhakeme*): 1 dosya" in icerik
    assert "Teslim makbuzu: YOK" in icerik


def test_makbuz_varsa_exit_kodu_ile_gosterilir(tmp_path):
    _baslat(tmp_path)
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = _durum_md(tmp_path)
    assert "Teslim makbuzu: VAR (exit_kodu=0)" in icerik


# ── (4) Katman satırları da imza etiketi taşır ──────────────────────────────

def test_katman_cli_isle_arac_imzali_gorunur(tmp_path):
    _baslat(tmp_path)
    kod, cikti = _cli(
        ["--katman", "oa-gizlilik", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if s.startswith("- oa-gizlilik:")][0]
    assert "[araç-imzalı]" in satir


def test_katman_elle_eklenen_olay_model_beyanli_gorunur(tmp_path):
    _baslat(tmp_path)
    olaylar_yol = _olaylar_yol(tmp_path)
    pk.olay_ekle(olaylar_yol, {
        "zaman": pk.simdi(), "tip": "katman", "katman": "oa-gizlilik",
        "durum": "UYGULANDI", "kanit": "elle deftere düşürülmüş katman kanıtı.",
    })
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = _durum_md(tmp_path)
    satir = [s for s in icerik.splitlines() if s.startswith("- oa-gizlilik:")][0]
    assert "[model-beyanlı]" in satir
