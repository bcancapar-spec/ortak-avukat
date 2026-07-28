# -*- coding: utf-8 -*-
"""P0-8 (v0.5.5) — pipeline_kayit.py'nin _oa/DURUM.md türetimi için testler.

DURUM.md HER olayda (baslat/isle/katman/denetle/hook-denetle) fiziksel
kanıttan ATOMİK türetilir: "elle düzenlenmez" damgası taşır, adım tablosu +
kapı durumu + kütük-vs-dilekçe sayacı + sözleşme-dışı dizin uyarısı + bayat-md
uyarısı + AVUKAT KARARI BEKLEYEN + SIRADAKİ bölümlerini içerir.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def test_baslat_durum_md_uretir_elle_duzenlenmez_damgasi(tmp_path):
    kod, _c = _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    durum_md = tmp_path / "_oa" / "DURUM.md"
    assert durum_md.is_file()
    icerik = durum_md.read_text(encoding="utf-8")
    assert "ELLE DÜZENLENMEZ" in icerik
    assert "Test Dosyası" in icerik
    assert "## Sıradaki" in icerik
    assert "## Avukat Kararı Bekleyen" in icerik


def test_isle_sonrasi_durum_md_adim_tablosunu_gunceller(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    # İNGEST-ÖNCE önkoşulunu karşıla (P0-6) — adım 0 manifest ingest-öncesi muaf.
    kod, cikti = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "UYGULANDI",
         "--kanit", "manifest script koşuldu, çıktı üretildi.", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "adım 0 (MANİFEST) / manifest: UYGULANDI" in icerik


def test_bilgi_eksik_avukat_karari_bekleyende_gorunur(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "BILGI-EKSIK",
         "--eksik", "müvekkilden ek bilgi bekleniyor.", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "BİLGİ EKSİK" in icerik
    # "Avukat Kararı Bekleyen" bölümü boş değil.
    bolum = icerik.split("## Avukat Kararı Bekleyen")[1].split("## Sıradaki")[0]
    assert "(yok)" not in bolum


def test_sozlesme_disi_dizin_uyarisi(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    (tmp_path / "_oa" / "hizli").mkdir(parents=True, exist_ok=True)
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "_oa/hizli" in icerik
    assert "Sözleşme-Dışı Dizin" in icerik


def test_sozlesme_ici_metin_ve_analiz_dizinleri_yanlis_alarm_uretmez(tmp_path):
    """P1-9(b) sinav düzeltmesi: beyaz liste 'metin' ve 'analiz'i İÇERMELİ —
    bu iki gerçek üretici dizin YANLIŞ ALARM üretmemeli."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    (tmp_path / "_oa" / "metin").mkdir(parents=True, exist_ok=True)
    (tmp_path / "_oa" / "analiz").mkdir(parents=True, exist_ok=True)
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "_oa/metin" not in icerik.split("## Sıradaki")[0].replace("Kütük satırı", "")
    assert "Sözleşme-Dışı Dizin" not in icerik


def test_kutuk_dilekce_sayaci_bolumu_var(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "Kütük-vs-Dilekçe Künye Sayacı" in icerik
    assert "Kütük satırı" in icerik


def test_siradaki_ilk_bekliyor_adimi_gosterir(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    bolum = icerik.split("## Sıradaki")[1]
    assert "adım 0 (MANİFEST)" in bolum


def test_defter_yoksa_durum_md_uretilmez(tmp_path):
    """Defter kullanmayan (--baslat hiç yapılmamış) bir kökte DURUM.md
    üretilmemeli — defter kapısıyla simetrik davranış."""
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0
    assert not (tmp_path / "_oa" / "DURUM.md").exists()


# ── M7 (Paket D, v0.5.5) — AVUKAT KARARI: --avukat-karari kayıt komutu ─────

def test_avukat_karari_gerekcesiz_reddedilir(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--avukat-karari", "Seçenek A seçildi", "--adim", "0", "--parca", "manifest",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "GEREKÇESİZ" in cikti or "gerekçesiz" in cikti.lower()


def test_avukat_karari_bilgi_eksigi_cozer_ve_bekleyenden_cikarir(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "BILGI-EKSIK",
         "--eksik", "evrak sayısı belirsiz, ek tarama gerek", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik_once = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "adım 0 (MANİFEST) / manifest: BİLGİ EKSİK" in icerik_once

    kod, cikti = _cli(
        ["--avukat-karari", "Seçenek A: mevcut evrakla devam edilsin",
         "--adim", "0", "--parca", "manifest",
         "--gerekce", "Ek tarama süre kaybına yol açar, mevcut evrak yeterli görülmüştür.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "AVUKAT KARARI KAYDEDİLDİ" in cikti

    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    bekleyen_bolum = icerik.split("## Avukat Kararı Bekleyen")[1].split("##")[0]
    assert "manifest" not in bekleyen_bolum, "çözülmüş çatal hâlâ BEKLEYEN listesinde"
    assert "Avukat Kararları (Kayıtlı" in icerik
    assert "Seçenek A: mevcut evrakla devam edilsin" in icerik
    assert "Ek tarama süre kaybına yol açar" in icerik


def test_avukat_karari_sonrasi_yeni_ve_farkli_bilgi_eksigi_bekleyende_kalir(tmp_path):
    """Paket D sınav bulgusu (M7 düzeltmesi) — bir çatal `--avukat-karari` ile
    çözüldükten SONRA aynı adım/parça için düşülen YENİ ve İLGİSİZ bir
    BİLGİ-EKSİK kaydı, eski kararın gölgesinde SESSİZCE bastırılmamalı;
    'Avukat Kararı Bekleyen' bölümünde GÖRÜNMELİ (zaman kıyaslı çözüm)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "BILGI-EKSIK",
         "--eksik", "Bilirkişi raporu dosyada yok", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    kod, cikti = _cli(
        ["--avukat-karari", "Rapor celbi talep edilmeyecek",
         "--adim", "4", "--parca", "oa-vakia",
         "--gerekce", "Mevcut delillerle karar verilebilecek yeterlilikte görülmüştür.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    bekleyen_bolum = icerik.split("## Avukat Kararı Bekleyen")[1].split("##")[0]
    assert "oa-vakia" not in bekleyen_bolum, "çözülmüş çatal hâlâ BEKLEYEN listesinde görünmemeli"

    # Kararın ZAMANINDAN SONRAKİ, TAMAMEN FARKLI bir eksik olayını doğrudan
    # jsonl'e (gerçek üretim yolunda --isle'nin yazacağı biçimle) ekliyoruz —
    # yalnız `zaman`ı bilinçli olarak kararın çok sonrasına sabitliyoruz, bu
    # yüzden wall-clock çözünürlüğüne (saniye) bağlı olmayan deterministik bir
    # regresyon testi elde ediyoruz.
    import sys as _sys
    _sys.path.insert(0, str(SCRIPT.parent))
    import pipeline_kayit as pk
    olaylar_yol, _durum_yol = pk._yollar(
        type("A", (), {"kok": str(tmp_path), "yol": None})())
    pk.olay_ekle(olaylar_yol, {
        "zaman": "2099-01-01T00:00:00", "tip": "adim", "adim": 4, "parca": "oa-vakia",
        "durum": "BILGI-EKSIK", "kanit": "EKSİK: tanıkların adresleri bulunamadı",
    })
    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    bekleyen_bolum = icerik.split("## Avukat Kararı Bekleyen")[1].split("##")[0]
    assert "oa-vakia" in bekleyen_bolum, (
        "karardan SONRAKİ yeni ve ilgisiz BİLGİ-EKSİK, eski kararın gölgesinde "
        "sessizce bastırılmış (M7 çürütücü bulgusu tekrar canlanmış)")
    assert "tanıkların adresleri bulunamadı" in bekleyen_bolum


def test_avukat_karari_ile_ayni_saniyede_dusen_yeni_eksik_bekleyende_kalir(tmp_path):
    """YENİ-3 (Paket D DÜZELTME) — canlı kanıt (scratchpad/p2): karar VE onun
    ÜZERİNE düşen yeni/ilgisiz bir BİLGİ-EKSİK kaydı AYNI SANİYE damgasını
    taşıyabilir (ardışık CLI çağrıları `simdi()`nin saniye çözünürlüğüyle
    kolayca çakışır). Eski `_zaman_once_mi` (`<=`) bunu 'karar sonra geldi'
    sayıp kalemi SESSİZCE BEKLEYEN'den düşürüyordu (fail-OPEN). Artık gerçeğin
    kaynağı append-only defterin SIRASI (`_sira`) — zaman damgası AYNI olsa
    bile karardan SONRA (append sırasında) gelen kalem GÖRÜNÜR kalmalı."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)

    import sys as _sys
    _sys.path.insert(0, str(SCRIPT.parent))
    import pipeline_kayit as pk
    olaylar_yol, _durum_yol = pk._yollar(
        type("A", (), {"kok": str(tmp_path), "yol": None})())

    AYNI_SANIYE = "2026-07-28T14:00:00"
    # (1) İlk BİLGİ-EKSİK.
    pk.olay_ekle(olaylar_yol, {
        "zaman": AYNI_SANIYE, "tip": "adim", "adim": 4, "parca": "oa-vakia",
        "durum": "BILGI-EKSIK", "kanit": "EKSİK: bilirkişi raporu dosyada yok",
    })
    # (2) Avukat kararı — AYNI SANİYE damgası (append sırasıyla SONRA).
    pk.olay_ekle(olaylar_yol, {
        "zaman": AYNI_SANIYE, "tip": "avukat-karari", "adim": 4, "parca": "oa-vakia",
        "katman": None, "karar": "Rapor celbi talep edilmeyecek",
        "gerekce": "Mevcut delillerle karar verilebilecek yeterlilikte görülmüştür.",
    })
    # (3) YENİ ve İLGİSİZ bir BİLGİ-EKSİK — AYNI SANİYE, ama append sırasıyla
    # kararın DA SONRASINDA (defterdeki 3. satır).
    pk.olay_ekle(olaylar_yol, {
        "zaman": AYNI_SANIYE, "tip": "adim", "adim": 4, "parca": "oa-vakia",
        "durum": "BILGI-EKSIK", "kanit": "EKSİK: yeni ve ilgisiz eksik (AYNI SANIYE)",
    })

    kod, cikti = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    bekleyen_bolum = icerik.split("## Avukat Kararı Bekleyen")[1].split("##")[0]
    assert "oa-vakia" in bekleyen_bolum, (
        "aynı-saniye beraberliğinde karardan SONRA düşen yeni/ilgisiz kalem "
        "sessizce bastırılmış (YENİ-3 çürütücü bulgusu)")
    assert "yeni ve ilgisiz eksik (AYNI SANIYE)" in bekleyen_bolum


def test_avukat_karari_katman_hedefler(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _cli(["--katman", "oa-gizlilik", "--durum", "BILGI-EKSIK",
          "--eksik", "gizlilik taraması netleşmedi", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--avukat-karari", "Katman gözden geçirildi, risk yok",
         "--katman", "oa-gizlilik",
         "--gerekce", "Evrakta kişisel veri unsuru bulunmadığı avukatça teyit edilmiştir.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    bekleyen_bolum = icerik.split("## Avukat Kararı Bekleyen")[1].split("##")[0]
    assert "oa-gizlilik" not in bekleyen_bolum
    assert "Katman gözden geçirildi, risk yok" in icerik


def test_avukat_karari_var_olmayan_hedefe_uyari_ile_kaydedilir(tmp_path):
    """Ş14 (v0.5.5 şerh turu, KUCUK) — canlı kanıt: `--avukat-karari` hedefin
    (--adim/--parca/--katman) defterde GERÇEKTEN AÇIK bir çatal olup
    olmadığını hiç denetlemiyordu — yazım hatalı bir parça adı/adım no bile
    KOŞULSUZ 'AVUKAT KARARI KAYDEDİLDİ' başarı mesajı alıyordu (yanıltıcı
    teyit). DÜZELTME sonrası: hedef bulunamadığında olay YİNE DE kaydedilir
    (fail-closed BLOK değil — kayıpsızlık/append-only bozulmaz, meşru 'önden
    karar' senaryosu kapanmaz) ama çıktı 'bulunamadı' uyarısıyla nitelenir."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--avukat-karari", "Talep edilmeyecek", "--adim", "9", "--parca", "oa-OLMAYAN-PARCA",
         "--gerekce", "yeterince uzun bir gerekçe metni buraya yazılmıştır.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti  # fail-closed BLOK değil — yalnız uyarı
    assert "AVUKAT KARARI KAYDEDİLDİ" in cikti
    assert "bulunamadı" in cikti
    assert "Avukat Kararı Bekleyen" in cikti


def test_avukat_karari_gercek_bekleyen_cataliyla_uyari_uretmez(tmp_path):
    """Simetrik negatif kontrol: hedef defterde GERÇEKTEN açık bir çatalsa
    (BILGI-EKSIK) 'bulunamadı' uyarısı YANLIŞLIKLA basılmamalı."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "BILGI-EKSIK",
         "--eksik", "bilirkişi raporu dosyada yok", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    kod, cikti = _cli(
        ["--avukat-karari", "Rapor celbi talep edilmeyecek",
         "--adim", "4", "--parca", "oa-vakia",
         "--gerekce", "Mevcut delillerle karar verilebilecek yeterlilikte görülmüştür.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    assert "AVUKAT KARARI KAYDEDİLDİ" in cikti
    assert "bulunamadı" not in cikti


def test_avukat_karari_hedef_eksikse_hata(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--avukat-karari", "karar metni", "--gerekce", "yeterince uzun bir gerekçe metni",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "--adim" in cikti or "--katman" in cikti


# ── M4 (Paket D, v0.5.5) — UNSUR ŞABLONLARI: delilsiz unsur DURUM'da kırmızı ─

def test_delilsiz_unsur_vakia_json_ispat_boslugu_durum_mdde_kirmizi(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "04-vakia.json").write_text(
        json.dumps({"ispat_bosluklari": ["U2"], "saglikli": False}, ensure_ascii=False),
        encoding="utf-8")
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "Delilsiz Unsur Uyarısı" in icerik
    assert "U2" in icerik
    assert "🔴" in icerik


def test_vakia_json_ispat_bosluğu_yoksa_bolum_gorunmez(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "04-vakia.json").write_text(
        json.dumps({"ispat_bosluklari": [], "saglikli": True}, ensure_ascii=False),
        encoding="utf-8")
    _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "Delilsiz Unsur Uyarısı" not in icerik


def test_ocr_bos_kunye_kaydi_durum_mdde_kirmizi(tmp_path):
    """P0-9 OCR-NÖBETÇİSİ — `_oa/metin/00-kunye.json`'daki 'ocr_durum' damgalı
    bir kayıt DURUM.md'de görünür bir 🔴 uyarısına dönüşür (mekanik render;
    DURUM.md salt-okur, oa_ingest'in kendi künyesini TEKRAR HESAPLAMAZ)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"kayitlar": [
            {"kaynak": "005-bos-tarama.pdf", "md": "005-bos-tarama.md",
             "ocr_durum": "OCR-BOŞ → GÖRSEL İNCELEME GEREK",
             "ocr_bos_sayfalar": [1, 2], "gorsel_klasor": "gorsel/005-bos-tarama"},
            {"kaynak": "006-saglikli.pdf", "md": "006-saglikli.md", "ocr_durum": None,
             "ocr_bos_sayfalar": [], "gorsel_klasor": ""},
        ]}, ensure_ascii=False), encoding="utf-8")
    kod, _c = _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "OCR-BOŞ Uyarısı" in icerik
    assert "005-bos-tarama.pdf" in icerik
    assert "gorsel/005-bos-tarama" in icerik
    assert "006-saglikli.pdf" not in icerik
    assert "🔴" in icerik


def test_ocr_bos_kunye_kaydi_yoksa_bolum_gorunmez(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"kayitlar": [
            {"kaynak": "006-saglikli.pdf", "md": "006-saglikli.md", "ocr_durum": None,
             "ocr_bos_sayfalar": [], "gorsel_klasor": ""},
        ]}, ensure_ascii=False), encoding="utf-8")
    _cli(["--goster", "--kok", str(tmp_path)], cwd=tmp_path)
    icerik = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "OCR-BOŞ Uyarısı" not in icerik
