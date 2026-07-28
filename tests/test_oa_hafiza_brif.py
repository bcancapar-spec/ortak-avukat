# -*- coding: utf-8 -*-
"""P0-1 (v0.5.5) — brif restorasyonu regresyon testleri.

Kapsam: `oa_hafiza.py ajan-brif` çıktısında (1) KURALLAR bloğu OKUMA DİSİPLİNİ
bloğundan ÖNCE gelir (v0.5.1→v0.5.4 arası sessizce tersine dönen sıra bir daha
kaymasın); (2) advisory dil ('SERBESTTİR'/'BLOKLAMAZ'/'ADVISORY') KURALLAR↔ANAYASA
diliminden çıkarılmıştır; (3) tek-komut içtihat örneği + TESLİM tanımı KURALLAR'da
gömülüdür; (4) okuma disiplini içeriği (harita.json, dosya-analiz.md, okuma_kapisi.py,
--tam-yukle-kaydet, --once-bak) kaybolmamıştır — muhakeme kaybı yok.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"
PIPELINE_SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _pipeline_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(PIPELINE_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _brif(tmp_path):
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["ajan-brif", "--parca", "oa-vakia", "--gorev", "kronoloji çıkar", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti
    return cikti


def _kurallar_anayasa_dilimi(cikti):
    """Yasak-kelime taraması yalnız KURALLAR..ANAYASA arasında yapılır —
    ANAYASA ÖZETİ bloğundaki 'yöntem serbest, ... serbestçe doğaçlanır' gibi
    anayasal ifadeler bu taramanın DIŞINDA kalmalı (yanlış-pozitif önleme).

    M1 düzeltmesi (Paket D sınav bulgusu) — `cikti.index('KURALLAR')` gibi
    İLK-EŞLEŞME dilimlemesi, M1'in brife enjekte ettiği ÖNCEKİ PAS gövdesi
    (disten okunan, keyfi içerikli md) 'KURALLAR' kelimesini taşırsa YANLIŞ
    yerden keser. Bunun yerine `oa_hafiza.py`nin bastığı makine-okur
    ayraçları (`<!-- oa:brif:KURALLAR-BAS -->` / `<!-- oa:brif:ANAYASA-BAS
    -->`) kullanılır — enjeksiyondan BAĞIMSIZ, deterministik dilimleme."""
    bas = cikti.index("<!-- oa:brif:KURALLAR-BAS -->")
    son = cikti.index("<!-- oa:brif:ANAYASA-BAS -->")
    assert bas < son
    return cikti[bas:son]


def test_kurallar_okuma_disiplininden_once_gelir(tmp_path):
    """Regresyon kilidi: 'KURALLAR' başlığının indeksi 'OKUMA DİSİPLİNİ'
    başlığından küçük olmalı — sıra bir daha sessizce değişemez."""
    cikti = _brif(tmp_path)
    assert cikti.index("KURALLAR") < cikti.index("OKUMA DİSİPLİNİ")


def test_advisory_dil_kurallar_anayasa_diliminde_yok(tmp_path):
    cikti = _brif(tmp_path)
    dilim = _kurallar_anayasa_dilimi(cikti)
    for yasak in ("SERBESTTİR", "BLOKLAMAZ", "ADVISORY"):
        assert yasak not in dilim, f"'{yasak}' KURALLAR/OKUMA diliminde geçmemeli:\n{dilim}"


def test_tek_komut_ve_teslim_tanimi_kurallarda(tmp_path):
    cikti = _brif(tmp_path)
    dilim = _kurallar_anayasa_dilimi(cikti)
    assert "--damga" in dilim
    assert "TESLİM tanımı" in dilim
    assert "teslim_paketi.py" in dilim
    assert "makbuz" in dilim.lower()


def test_dosya_analiz_yerine_gecmez_cumlesi(tmp_path):
    cikti = _brif(tmp_path)
    assert "dosya-analiz.md" in cikti
    assert "YERİNE GEÇMEZ" in cikti


# ── M1 düzeltmesi (Paket D sınav bulgusu) — dilimlemenin ENJEKSİYONDAN
# BAĞIMSIZ olduğunu kanıtlayan regresyon: ÖNCEKİ PAS gövdesi bilinçli olarak
# 'KURALLAR' ve 'BLOKLAMAZ' kelimelerini taşıyor — eski `cikti.index('KURALLAR')`
# (İLK eşleşme) mantığı burada YANLIŞ yerden keserdi.

def test_pas_govdesi_kurallar_ve_bloklamaz_icerse_bile_dilim_dogru_kesilir(tmp_path):
    _cli(["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, _c = _pipeline_cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, _c
    pas_dosya = tmp_path / "_oa" / "cikti" / "03-oa-ictihat-arastirma.md"
    pas_dosya.parent.mkdir(parents=True, exist_ok=True)
    pas_dosya.write_text(
        "TEZ: müvekkilin alacağı zamanaşımına uğramamıştır.\n"
        "Bu pasın gövdesinde bilinçli olarak KURALLAR kelimesi ve ADVISORY, "
        "BLOKLAMAZ gibi ifadeler geçer — dilimleme bu enjeksiyona rağmen "
        "gerçek '4) KURALLAR' başlığından kesmelidir.\n",
        encoding="utf-8")
    kod, cikti = _pipeline_cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "GEREKSIZ",
         "--gerekce", "test amaçlı GEREKSIZ statü, önkoşul kapısını devre dışı bırakır",
         "--pas-yolu", "_oa/cikti/03-oa-ictihat-arastirma.md", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0, cikti

    cikti = _brif(tmp_path)
    # Pas gövdesi (KURALLAR/BLOKLAMAZ/ADVISORY dahil) brife fiilen enjekte
    # edilmiş olmalı — senaryonun anlamlı olduğunun kanıtı.
    assert "ÖNCEKİ PAS" in cikti
    assert "bilinçli olarak KURALLAR kelimesi" in cikti

    dilim = _kurallar_anayasa_dilimi(cikti)
    # Doğru dilim gerçek KURALLAR bloğunu içermeli...
    assert "PAS PROTOKOLÜ" in dilim and "--damga" in dilim
    # ...ve enjekte edilen pas gövdesinin advisory kelimelerini İÇERMEMELİ —
    # bunlar anchor'dan ÖNCE, pas gövdesinde kalmalı.
    assert "BLOKLAMAZ" not in dilim
    assert "bilinçli olarak KURALLAR kelimesi" not in dilim


def test_okuma_disiplini_icerigi_kaybolmadi(tmp_path):
    """Muhakeme kaybı yok: okuma disiplini yoğunlaştırılırken çekirdek
    dizeler brifte KALIR (test assert — regresyon kilidi)."""
    cikti = _brif(tmp_path)
    assert "harita.json" in cikti
    assert "dosya-analiz.md" in cikti
    assert "okuma_kapisi.py" in cikti
    assert "--tam-yukle-kaydet" in cikti
    assert "--once-bak" in cikti
    assert "DERİNLİK ASLA KISILMAZ" in cikti or "DERİNLİK KISILMAZ" in cikti
