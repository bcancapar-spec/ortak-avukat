# -*- coding: utf-8 -*-
"""GÖREV C (v0.5.6 hazırlığı) — ARTEFAKT GERÇEKLİĞİ + PAS testleri.

Kapsam:
(1) ADIM-PARÇA/DAL UYUŞMAZLIĞI — hukuk dosyasında oa-mudafii/oa-musteki-vekili,
    ceza dosyasında oa-sozlesme UYARIR (bloklamaz); dal belirsizse UYARI YOK.
(2) ARTEFAKT-BEYAN AYRIMI — kanıt metninde kendine-atıf kalıbı ("taslağın X
    bölümünde") varsa özel bir uyarı eklenir; bloklama kümesi (5, 9) DEĞİŞMEZ.
(3) devir/ boşsa oturum-kapat / tam_tur --kaydet GÖRÜNÜR uyarı basar
    (bkz. test_oa_hafiza.py / test_tam_tur.py — bu dosyada YALNIZ (1)+(2)).
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _baslat(tmp_path, ceza=None):
    args = ["--baslat", "Test Dosyası", "--kok", str(tmp_path)]
    if ceza:
        args += ["--ceza", ceza]
    kod, cikti = _cli(args, cwd=tmp_path)
    assert kod == 0, cikti


def _kunye_kur(tmp_path):
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def _dosya_md_yaz(tmp_path, dal_satiri):
    dosya_md = tmp_path / "_oa" / "dosya.md"
    dosya_md.parent.mkdir(parents=True, exist_ok=True)
    dosya_md.write_text(
        "# Dosya Kimliği — Test Dosyası\n\n"
        "- Müvekkil sıfatı / karşı taraf: davacı\n"
        "- Talep (somut, ölçülebilir): alacak\n"
        f"- Dokunduğu hukuk dalları: {dal_satiri}\n",
        encoding="utf-8",
    )


# ── (1) DAL UYUŞMAZLIĞI ──────────────────────────────────────────────────

def test_hukuk_dosyasinda_oa_mudafii_katmani_uyarir(tmp_path):
    """ceza_dali YOK + dosya.md dalı 'İş Hukuku' (hukuk) iken --katman
    oa-mudafii UYGULANDI yazılırsa GÖRÜNÜR bir DAL UYUŞMAZLIĞI uyarısı
    basılmalı — ama BLOKLANMAMALI (exit 0)."""
    _baslat(tmp_path)  # --ceza verilmedi → hukuk davası varsayımı dosya.md'den
    _dosya_md_yaz(tmp_path, "İş Hukuku")
    kod, cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "UYGULANDI", "--kanit", UZUN_KANIT,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, f"dal uyuşmazlığı BLOKLAMAMALI:\n{cikti}"
    assert "DAL UYUŞMAZLIĞI" in cikti
    assert "oa-mudafii" in cikti


def test_ceza_dosyasinda_oa_mudafii_katmani_uyarmaz(tmp_path):
    """Kontrast: ceza_dali='mudafii' iken --katman oa-mudafii UYUM İÇİNDEDİR
    — DAL UYUŞMAZLIĞI uyarısı BASILMAMALI."""
    _baslat(tmp_path, ceza="mudafii")
    kod, cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "UYGULANDI", "--kanit", UZUN_KANIT,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "DAL UYUŞMAZLIĞI" not in cikti


def test_ceza_dosyasinda_oa_sozlesme_uyarir(tmp_path):
    """ceza_dali='musteki' (KESİN ceza) iken --isle ile bir adıma oa-sozlesme
    parçası yazılırsa DAL UYUŞMAZLIĞI uyarısı basılmalı (bloklamaz)."""
    _baslat(tmp_path, ceza="musteki")
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "1", "--parca", "oa-sozlesme", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "DAL UYUŞMAZLIĞI" in cikti
    assert "oa-sozlesme" in cikti


def test_dal_belirsizken_uyari_basilmaz(tmp_path):
    """ceza_dali YOK + dosya.md hâlâ dolgu ([doldur ...]) iken dal BELİRSİZ
    sayılır — hiçbir DAL UYUŞMAZLIĞI uyarısı ÜRETİLMEMELİ (kural: belirsizse
    UYARI YOK)."""
    _baslat(tmp_path)  # dosya.md hiç yazılmadı (belirsiz)
    kod, cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "UYGULANDI", "--kanit", UZUN_KANIT,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "DAL UYUŞMAZLIĞI" not in cikti


def test_gereksiz_durumunda_dal_uyusmazligi_uyarmaz(tmp_path):
    """KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/bulgu 2): hukuk
    dosyasında oa-mudafii'ni GEREKSIZ işaretlemek DOĞRU davranıştır — DAL
    UYUŞMAZLIĞI uyarısı ÜRETİLMEMELİ (kontrast: aynı senaryoda UYGULANDI
    hâlâ uyarır — bkz. test_hukuk_dosyasinda_oa_mudafii_katmani_uyarir)."""
    _baslat(tmp_path)
    _dosya_md_yaz(tmp_path, "İş Hukuku")
    kod, cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "GEREKSIZ",
         "--gerekce", "bu dosya hukuk davası — ceza müdafiliği gereksiz.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "DAL UYUŞMAZLIĞI" not in cikti


def test_dosya_md_yokken_klasor_adindan_mahkeme_ipucu_dal_tahmin_eder(tmp_path):
    """KUCUK-DÜZELTME (hakem düzeltme turu 1, madde 2/bulgu 1): `_oa/
    dosya.md`'deki dal satırı hiç yazılmamışken (sahadaki gerçek durum) dava
    kökü klasör adındaki mahkeme adı (saha örneğine sadık, alt çizgili:
    '..._Is_Mahkemesi') dal tahminini CANLANDIRMALI."""
    dava_koku = tmp_path / "2025_354_Denizli_3._Is_Mahkemesi"
    dava_koku.mkdir(parents=True, exist_ok=True)
    _baslat(dava_koku)  # dosya.md YOK — dal satırı ipucu yok
    kod, cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "UYGULANDI", "--kanit", UZUN_KANIT,
         "--kok", str(dava_koku)],
        cwd=dava_koku,
    )
    assert kod == 0, cikti
    assert "DAL UYUŞMAZLIĞI" in cikti
    assert "oa-mudafii" in cikti


def test_dal_belirsizken_rastgele_klasor_adi_yanlis_pozitif_uretmez(tmp_path):
    """Kontrast: `tmp_path` rastgele (mahkeme adı İÇERMEYEN) bir klasör
    adına sahip olduğundan yeni üçüncül ipucu kaynağı burada YİNE None
    dönmeli — belirsizse uyarı yok kuralı korunur."""
    _baslat(tmp_path)
    kod, cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "UYGULANDI", "--kanit", UZUN_KANIT,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "DAL UYUŞMAZLIĞI" not in cikti


def test_dal_uyusmazligi_durum_md_de_gorunur(tmp_path):
    """Mesaj yalnız anlık çıktıda değil, _oa/DURUM.md'de de KALICI görünmeli
    (--goster/--denetle her ikisi de aynı kaynaktan türetir)."""
    _baslat(tmp_path)
    _dosya_md_yaz(tmp_path, "İş Hukuku")
    kod, _cikti = _cli(
        ["--katman", "oa-mudafii", "--durum", "UYGULANDI", "--kanit", UZUN_KANIT,
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0

    durum_md = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "DAL UYUŞMAZLIĞI" in durum_md

    kod_g, cikti_g = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod_g == 0
    # --goster kendi STDOUT'unda basmasa da _denetle_hesapla üzerinden
    # DURUM.md'yi tazeler; burada DOĞRUDAN --denetle çıktısını da kontrol edelim.
    _kod_d, cikti_d = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert "DAL UYUŞMAZLIĞI" in cikti_d


# ── (2) ARTEFAKT-BEYAN AYRIMI (kendine-atıf kalıbı) ─────────────────────

def test_kendine_atif_kalibi_uyari_kumesinde_ozel_not_ekler(tmp_path):
    """adım-4 (oa-vakia, UYARI kümesi) artefaktsızken, kanıt metninde
    'taslağın X bölümünde' kalıbı varsa KENDİNE-ATIF notu eklenmeli —
    UYARI kümesi hâlâ BLOKLAMAZ (exit 0)."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kanit = ("Vakıa analizi tatbik edildi; bkz. taslağın II-III bölümlerinde "
             "anlatılan olgular (ayrı bir çalışma evrakı üretilmedi).")
    kod, cikti = _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "UYGULANDI",
         "--kanit", kanit, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, f"UYARI kümesi bloklamamalı:\n{cikti}"
    assert "KENDİNE-ATIF" in cikti
    assert "04-vakia" in cikti


def test_kendine_atif_kalibi_olmadan_uyari_ozel_not_tasimaz(tmp_path):
    """Kontrast: normal (kendine-atıf İÇERMEYEN) bir UYGULANDI kanıtında
    KENDİNE-ATIF notu EKLENMEMELİ."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0
    assert "KENDİNE-ATIF" not in cikti


def test_kendine_atif_kalibi_bloklayici_kumede_bloklamayi_kaldirmaz(tmp_path):
    """adım-5 (oa-kiyas, BLOKLEYICI küme) — kendine-atıf kalıbı taşıyan bir
    kanıt dahi bloklamayı KALDIRMAZ (bloklama kümesi DEĞİŞMEZ); yalnız
    RET mesajına KENDİNE-ATIF notu eklenir."""
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kanit = ("Kıyas tatbik edildi; bkz. taslağın II-III bölümlerinde yapılan "
             "değerlendirme (ayrı bir 05-kiyas dosyası üretilmedi).")
    kod, cikti = _cli(
        ["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
         "--kanit", kanit, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0, "bloklama kümesi (adım-5) kendine-atıf ile GEÇİLMEMELİ"
    assert "KENDİNE-ATIF" in cikti
