# -*- coding: utf-8 -*-
"""oa-pipeline / tam_tur.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
cmd_* fonksiyonları sys.exit ÇAĞIRMAZ (yalnız main() çağırır) — bu yüzden
doğrudan import edilip int dönüş değeriyle test edilebilir (tmp_path izolasyonu).

Odak: (1) sha tabanlı delta tespiti — künye içeriği DEĞİŞTİĞİNDE (aynı dosya
adı, farklı sha) delta YENİ turda YAKALANMALI; (2) yutma denetimi — bekleyen
delta hiçbir GELİŞME kaydında anılmadan ikinci `--kaydet` ile snapshot'a
sessizce yutulamaz (--zorla olmadan RET).
"""
import hashlib
import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "tam_tur.py"


def _load():
    assert SCRIPT.is_file(), f"tam_tur.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("tam_tur", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tt = _load()


def _sha(icerik):
    return hashlib.sha256(icerik.encode("utf-8")).hexdigest()[:16]


def _kunye_yaz(kok, kayitlar):
    """_oa/metin/00-kunye.json yaz (tam_tur'un beklediği minimal şema).

    Ayrıca her `kaynak` için kökte BOŞ bir plasöy-holder dosya dokunur:
    tam_tur'un "KÜNYE BAYAT" denetimi (_bayat_kunye), künyede anılan kaynağın
    fiziken diskte VAR olup olmadığını ayrıca kontrol eder — asıl test
    konusu olan sha-tabanlı delta mantığına ulaşmadan önce bu ayrı denetim
    'silinmiş/taşınmış' diye erken exit 3 verir. Dosyanın GERÇEK içeriği
    ilgisizdir: delta motoru içerik imzasını YALNIZ künyedeki `sha` alanından
    okur (bkz. _evrak_imzalari), diskteki dosyayı yeniden hashlemez."""
    metin_dizin = kok / "_oa" / "metin"
    metin_dizin.mkdir(parents=True, exist_ok=True)
    kunye = {"toplam_evrak": len(kayitlar), "kayitlar": kayitlar}
    (metin_dizin / "00-kunye.json").write_text(
        json.dumps(kunye, ensure_ascii=False), encoding="utf-8")
    for k in kayitlar:
        kaynak = k.get("kaynak")
        if not kaynak:
            continue
        yol = kok / kaynak
        if not yol.exists():
            yol.parent.mkdir(parents=True, exist_ok=True)
            yol.write_text("plasöy-holder", encoding="utf-8")


def _cikti_birak(kok, ad="01-parca.md", icerik="çalışma evrakı"):
    cikti_dizin = kok / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / ad).write_text(icerik, encoding="utf-8")


# ── sha tabanlı delta: aynı ad, DEĞİŞEN içerik → 2. döngüde YAKALANIR ───────

def test_sha_delta_ikinci_dongude_yakalanir(tmp_path):
    ilk_icerik = "dilekçe metni v1"
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha(ilk_icerik)}])
    _cikti_birak(tmp_path)

    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    # Hemen ardından delta YOK olmalı (snapshot güncel).
    assert tt.cmd_delta(str(tmp_path)) == 0

    # İçerik DEĞİŞİYOR (aynı dosya adı, farklı sha) — bu, sha-tabanlı imzanın
    # yakalaması gereken TAM senaryo: karakter sayısı aynı kalsa bile içerik
    # hash'i değişmişse "değişen evrak" sayılmalı.
    yeni_icerik = "dilekçe metni v2"  # aynı uzunlukta, farklı içerik
    assert len(yeni_icerik) == len(ilk_icerik)
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha(yeni_icerik)}])

    kod = tt.cmd_delta(str(tmp_path))
    assert kod == 3, "sha değiştiği halde delta YOK dendi (2. döngü regresyonu)"

    yeni, degisen, silinen = tt._delta_hesapla(str(tmp_path), tt._durum_oku(str(tmp_path)))
    assert degisen == ["dilekce.pdf"], f"DEĞİŞEN evrak listesi yanlış: {degisen}"
    assert yeni == [] and silinen == []


def test_yeni_evrak_delta_yakalanir(tmp_path):
    _kunye_yaz(tmp_path, [{"kaynak": "ilk.pdf", "sha": _sha("a")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0
    assert tt.cmd_delta(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [
        {"kaynak": "ilk.pdf", "sha": _sha("a")},
        {"kaynak": "ikinci.pdf", "sha": _sha("b")},
    ])
    kod = tt.cmd_delta(str(tmp_path))
    assert kod == 3
    yeni, degisen, silinen = tt._delta_hesapla(str(tmp_path), tt._durum_oku(str(tmp_path)))
    assert yeni == ["ikinci.pdf"]
    assert degisen == [] and silinen == []


# ── Yutma denetimi (2. döngü): bekleyen delta GELİŞME'de anılmadan yutulamaz ─

def test_islenmemis_delta_gelisme_olmadan_kaydete_yutulamaz(tmp_path):
    """İKİNCİ tam tur döngüsü: bir önceki snapshot'tan sonra evrak değişti
    (bekleyen delta var) ama hiçbir `--ekle` ile işlenmedi. `--kaydet` bunu
    --zorla OLMADAN sessizce yutmamalı (exit 1, RET)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    # İçerik değişti ama hiç `--ekle` ile işlenmedi (yutma senaryosu).
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])

    kod = tt.cmd_kaydet(str(tmp_path))
    assert kod == 1, "işlenmemiş delta GELİŞME'de anılmadan --zorla olmadan yutulmamalı"


def test_islenmis_delta_gelisme_ile_kaydete_gecer(tmp_path):
    """Kontrast: bekleyen delta `--ekle` ile GELİŞME günlüğüne işlenmişse
    ikinci `--kaydet` sorunsuz geçmeli (exit 0)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])
    assert tt.cmd_ekle(str(tmp_path), "dilekce.pdf güncellendi, gözden geçirildi") == 0

    kod = tt.cmd_kaydet(str(tmp_path))
    assert kod == 0, "GELİŞME'de anılmış bekleyen delta ikinci kaydet'i engellememeli"


# ── Gate G — KALICILIK KAPISI: --durum mekanik "tamamlandi/tamamlanmadi" ────

def test_durum_kaydet_sonrasi_mekanik_tamamlandi(tmp_path, capsys):
    """--kaydet başarıyla bittikten sonra --durum'un mekanik Gate G satırı
    'tamamlandi' demeli ve genel dönüş 0 olmalı."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    capsys.readouterr()
    kod = tt.cmd_durum(str(tmp_path))
    cikti = capsys.readouterr().out
    assert kod == 0
    assert "Analiz kaydı" in cikti and "tamamlandi" in cikti


def test_durum_analiz_md_silinirse_mekanik_tamamlanmadi(tmp_path, capsys):
    """durum.json 'TAMAM' + delta temiz görünse bile dosya-analiz.md fiziken
    SİLİNMİŞSE, --durum bunu MODEL BEYANINA değil DİSKE bakarak yakalamalı.
    M3-0 (Gate G+ + kendini-onarma): --durum md'yi birincil kaynaklardan
    YENİDEN KURAR (GÖRÜNÜR uyarıyla) ama bu onarım TAMAM işaretçisi ÜRETMEZ —
    dolayısıyla sonuç yine 'tamamlanmadi' kalır (fail-closed korunur)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    assert analiz_md.exists()
    analiz_md.unlink()

    capsys.readouterr()
    kod = tt.cmd_durum(str(tmp_path))
    yakalanan = capsys.readouterr()
    cikti = yakalanan.out
    assert kod == 3, "dosya-analiz.md silinmişken --durum yine de 'güncel/tamam' demeli değildi"
    assert "tamamlanmadi" in cikti
    assert "TAMAM işaretçisi yok" in cikti
    assert "UYARI" in yakalanan.err and "yeniden kuruldu" in yakalanan.err
    # Kendini-onarma: md fiilen YENİDEN KURULMUŞ olmalı (DAİMA MEVCUT garantisi).
    assert analiz_md.exists()


def test_durum_analiz_md_bos_ise_mekanik_tamamlanmadi(tmp_path, capsys):
    """dosya-analiz.md VAR ama BOŞ (0 bayt) — mekanik kapı yine 'tamamlanmadi'
    demeli; M3-0 kendini-onarma burada da tetiklenir (boş = bozuk)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    analiz_md.write_text("", encoding="utf-8")

    capsys.readouterr()
    kod = tt.cmd_durum(str(tmp_path))
    yakalanan = capsys.readouterr()
    cikti = yakalanan.out
    assert kod == 3
    assert "tamamlanmadi" in cikti
    assert "UYARI" in yakalanan.err and "eksik/bozuktu" in yakalanan.err
    assert analiz_md.stat().st_size > 0, "kendini-onarma boş dosyayı yeniden kurmalıydı"


def test_durum_yeniden_baslat_sonrasi_kaydetmeden_bayat_kayit(tmp_path, capsys):
    """Tam tur --kaydet ile TAMAM'landıktan sonra --baslat TEKRAR çağrılıp
    (tur yeniden açılıp) --kaydet ile TAZELENMEDEN bırakılırsa, eski
    dosya-analiz.md artık YENİ başlangıçtan ESKİ sayılmalı (bayat kayıt)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    durum = tt._durum_oku(str(tmp_path))
    fiziksel_tamam, _ = tt._analiz_kaydi_fiziksel_tamam(str(tmp_path), durum)
    assert fiziksel_tamam

    # Yapay olarak ileri bir "baslatildi" zamanı yazarak yeniden-açılma simüle edilir
    # (gerçek zamanlı testte dakika çözünürlüğü nedeniyle mtime farkı garanti olmayabilir).
    durum["baslatildi"] = "2099-01-01 00:00"
    durum["tam_tur_durumu"] = "DEVAM"
    tt._durum_yaz(str(tmp_path), durum)

    fiziksel_tamam2, sebep2 = tt._analiz_kaydi_fiziksel_tamam(str(tmp_path), durum)
    assert not fiziksel_tamam2
    assert "ESKİ" in sebep2 or "eski" in sebep2.lower()

    capsys.readouterr()
    kod = tt.cmd_durum(str(tmp_path))
    cikti = capsys.readouterr().out
    assert kod == 3
    assert "tamamlanmadi" in cikti


def test_zorla_ile_yutma_serh_dusulerek_gecer(tmp_path):
    """--zorla ile yutma engellenmez ama ŞERH düşülür (sessiz geçiş yok)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])
    kod = tt.cmd_kaydet(str(tmp_path), zorla=True)
    assert kod == 0
    analiz_md = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert "ŞERH" in analiz_md
    assert "dilekce.pdf" in analiz_md


# ── M1-4 GATE E — --brif (ARTIMLI MOD BRİFİ / TAM TUR DELTA ZORLAMA) ────────

def test_brif_tam_tur_hic_yapilmamissa_kapali_der(tmp_path, capsys):
    kod = tt.cmd_brif(str(tmp_path))
    cikti = capsys.readouterr().out
    assert kod == 3
    assert "ARTIMLI MOD: KAPALI" in cikti
    assert "ZORUNLU TAM TUR" in cikti


def test_brif_delta_yokken_tam_acik_ve_talimat_verir(tmp_path, capsys):
    """Tam tur TAMAM + bekleyen delta yok → --brif 'TAM AÇIK' der ve ajanı
    HAM evrağı toplu yeniden okumaması yönünde açıkça talimatlandırır."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0
    tt.cmd_ekle(str(tmp_path), "ilk gelişme kaydı")

    capsys.readouterr()
    kod = tt.cmd_brif(str(tmp_path))
    cikti = capsys.readouterr().out
    assert kod == 0
    assert "ARTIMLI MOD: TAM AÇIK" in cikti
    assert "TOPLU yeniden OKUMASIN" in cikti
    assert "dosya-analiz.md" in cikti
    assert "ilk gelişme kaydı" in cikti  # son gelişmeler listelenmiş


def test_brif_bekleyen_delta_varsa_kismi_der_ve_evraki_listeler(tmp_path, capsys):
    """Yeni evrak eklenip henüz --ekle ile işlenmemişse --brif 'KISMİ' der ve
    yalnız bekleyen evrakların tek tek işlenmesini talimatlandırır."""
    _kunye_yaz(tmp_path, [{"kaynak": "ilk.pdf", "sha": _sha("a")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    _kunye_yaz(tmp_path, [
        {"kaynak": "ilk.pdf", "sha": _sha("a")},
        {"kaynak": "ikinci.pdf", "sha": _sha("b")},
    ])

    capsys.readouterr()
    kod = tt.cmd_brif(str(tmp_path))
    cikti = capsys.readouterr().out
    assert kod == 3
    assert "ARTIMLI MOD: KISMİ" in cikti
    assert "ikinci.pdf" in cikti
    assert "TOPLU yeniden OKUMA" in cikti


def test_brif_durum_ile_ayni_donus_kodunu_paylasir(tmp_path):
    """--brif ve --durum aynı mekanik sinyale dayanır: ikisi de aynı anda
    aynı yönde (0/3) dönmeli — iki ayrı gerçek icat edilmemiş olmalı."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0

    assert tt.cmd_brif(str(tmp_path)) == tt.cmd_durum(str(tmp_path)) == 0


# ── M3-0 — DOĞUM-ANI KALICILIK: iskelet doğumu / --senkron / Gate G+ ────────

def test_baslat_iskeleti_atomik_dogurur_ve_idempotenttir(tmp_path):
    """`--baslat` dosya-analiz.md YOKKEN 15 bölüm ayracını (0-14) taşıyan bir
    İSKELET doğurur; TAMAM işaretçisi ASLA içermez. İkinci `--baslat` çağrısı
    gövdeye DOKUNMAZ (idempotent) — yalnız başlık gerekiyorsa tazelenir."""
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    assert analiz_md.exists() and analiz_md.stat().st_size > 0
    icerik = analiz_md.read_text(encoding="utf-8")
    for n, slug, _ in tt.BOLUM_TANIMLARI:
        assert f"<!-- oa:bolum:{n:02d}-{slug} -->" in icerik, f"bölüm {n} ayracı eksik"
    assert not tt._tamam_isaretci_var_mi(icerik), "--baslat TAMAM işaretçisi ÜRETMEMELİ"

    ilk_mtime = analiz_md.stat().st_mtime
    ilk_icerik = icerik
    # aynı dosya adıyla ikinci --baslat: gövde AYNI kalmalı (idempotent, dokunma).
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    assert analiz_md.read_text(encoding="utf-8") == ilk_icerik


def test_baslat_farkli_dosya_adiyla_basligi_tazeler_govdeye_dokunmaz(tmp_path):
    """`--baslat` md VARKEN çağrılırsa yalnız başlık satırı (dosya adı farklıysa)
    tazelenir; bölüm gövdesi/markerları bozulmaz."""
    assert tt.cmd_baslat(str(tmp_path), "İlk Ad") == 0
    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    assert "İlk Ad" in analiz_md.read_text(encoding="utf-8")

    assert tt.cmd_baslat(str(tmp_path), "Yeni Ad") == 0
    icerik = analiz_md.read_text(encoding="utf-8")
    assert icerik.splitlines()[0].endswith("Yeni Ad")
    assert tt._iskelet_saglam_mi(icerik)
    assert not tt._tamam_isaretci_var_mi(icerik)


def test_senkron_cikti_dosyasini_kayipsiz_turetir(tmp_path):
    """`--senkron`, `_oa/cikti/NN-*` dosyasının içeriğini (okunabilirse TAM gömülü)
    doğru bölüme yerleştirir; NN=00-09 → bölüm NN+1 eşlemesi ve CATCH-ALL (14,
    eşlenmeyen dosya adı) birlikte doğrulanır — hiçbir çalışma evrakı düşmez."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    _cikti_birak(tmp_path, ad="04-vakia.json", icerik='{"olgu": "örnek olgu içeriği"}')
    _cikti_birak(tmp_path, ad="capraz-denetim.json", icerik='{"eslesme": true}')

    kod = tt.cmd_senkron(str(tmp_path))
    assert kod == 0
    icerik = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert not tt._tamam_isaretci_var_mi(icerik), "--senkron TAMAM işaretçisi ÜRETMEMELİ"
    # 04-vakia.json → OLGU/DELİL (bölüm 5) NN+1 eşlemesiyle.
    bolum5_idx = icerik.index("<!-- oa:bolum:05-Olgu-delil -->")
    bolum6_idx = icerik.index("<!-- oa:bolum:06-Kiyas -->")
    assert bolum5_idx < icerik.index("04-vakia.json") < bolum6_idx
    assert "örnek olgu içeriği" in icerik
    # NN-öneki taşımayan dosya → CATCH-ALL (bölüm 14).
    bolum14_idx = icerik.index("<!-- oa:bolum:14-Diger-calisma-evraklari -->")
    assert bolum14_idx < icerik.index("capraz-denetim.json")
    assert "eslesme" in icerik


def test_buyuk_muhakeme_ciktisi_ozetlenmeden_tam_gomulur(tmp_path):
    """M3-0 DÜZELTMESİ (Gate G+ — muhakeme kaybı denetçi bulgusu): eski davranışta
    KUCUK_ESIK=4000 karakter üzerindeki HER `_oa/cikti/*` dosyası (bölüm ayrımı
    yapılmadan) yalnız ilk ~300 karakterlik bir 'Öz' ile temsil ediliyordu — bu,
    07-Strateji/08-Antitez gibi SAF MUHAKEME bölümlerinde gerçek gerekçelendirmeyi
    ARTIMLI MOD'da (yalnız dosya-analiz.md okunur) görünmez kılardı. Bu test 4000
    karakteri AÇIKÇA aşan okunabilir bir muhakeme çıktısının TAM (özetlenmeden)
    gömüldüğünü doğrular — 'Öz:' özetleme deseni ARTIK üretilmemeli."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    # 08-antitez → bölüm 9 (Antitez, NN+1) — eski eşiğin çok üzerinde (>4000 kar.).
    uzun_muhakeme = "KARŞI TARAF ARGÜMANI VE ÇÖKERTME GEREKÇESİ. " * 200  # ~9000+ kar.
    assert len(uzun_muhakeme) > 4000
    _cikti_birak(tmp_path, ad="08-antitez.md", icerik=uzun_muhakeme)

    kod = tt.cmd_senkron(str(tmp_path))
    assert kod == 0
    icerik = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert uzun_muhakeme.rstrip("\n") in icerik, (
        "büyük muhakeme çıktısı TAM gömülmedi — muhakeme kaybı regresyonu")
    assert "> Öz:" not in icerik, "eski özetleme deseni ('> Öz:') hâlâ üretiliyor"


def test_ikili_icerik_hala_oz_temsille_gosterilir(tmp_path):
    """Gerçekten ikili/okunamayan (utf-8 çözülemeyen) bir `_oa/cikti/*` dosyası
    TAM metin olarak gömülmez (gömülemez) — yol+sha ile temsil edilmeye devam
    eder; bu bir 'özetleme' değildir çünkü ikili veri zaten düzyazı muhakeme
    taşımaz (kayıpsızlık: tam içerik diskte, sha ile doğrulanabilir kalır)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "09-ek-gorsel.bin").write_bytes(b"\xff\xfe\x00\x01ikili-veri\x80\x81")

    kod = tt.cmd_senkron(str(tmp_path))
    assert kod == 0
    icerik = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert "09-ek-gorsel.bin" in icerik
    assert "ikili/okunamayan içerik" in icerik
    assert "sha ile doğrulanır" in icerik


def test_senkron_kaydet_sonrasi_tamam_isaretcisini_dusurur_ve_uyarir(tmp_path, capsys):
    """Yan-bulgu düzeltmesi: `--kaydet` sonrası (TAMAM damgalı) bir dosya-analiz.md
    üzerinde `--senkron` çağrılırsa TAMAM işaretçisi bu render'da düşer (yalnız
    `--kaydet` işaretçi yazar) — veri kaybı YOK ama sessiz olursa şaşırtıcıdır;
    script bunu artık AÇIKÇA (stderr) bildirir."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    assert tt.cmd_kaydet(str(tmp_path)) == 0
    icerik_kaydet = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert tt._tamam_isaretci_var_mi(icerik_kaydet)

    capsys.readouterr()
    kod = tt.cmd_senkron(str(tmp_path))
    yakalanan = capsys.readouterr()
    assert kod == 0
    assert "TAMAM işaretçisini ASLA yazmaz" in yakalanan.err
    assert "damga bu render'da DÜŞTÜ" in yakalanan.err

    icerik_senkron = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert not tt._tamam_isaretci_var_mi(icerik_senkron)


def test_gate_g_plus_isaretcisiz_iskelet_tamamlanmadi_sayar(tmp_path, capsys):
    """ZORUNLU iskelet↔Gate G+ etkileşimi: yalnız `--baslat` (VAR+dolu+taze
    iskelet, eski Gate G'yi GEÇERDİ) çalıştıktan sonra `--durum` YİNE DE
    'tamamlanmadi' demeli — işaretçisiz iskelet asla 'tamamlandi' sayılmaz."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    assert analiz_md.exists() and analiz_md.stat().st_size > 0  # eski Gate G'nin 3 koşulu GEÇERDİ

    capsys.readouterr()
    kod = tt.cmd_durum(str(tmp_path))
    cikti = capsys.readouterr().out
    assert kod == 3
    assert "tamamlanmadi" in cikti
    assert "TAMAM işaretçisi yok" in cikti

    # Gerçek --kaydet sonrası aynı sinyal 'tamamlandi'ya döner (kontrast).
    _cikti_birak(tmp_path)
    assert tt.cmd_kaydet(str(tmp_path)) == 0
    capsys.readouterr()
    kod2 = tt.cmd_durum(str(tmp_path))
    cikti2 = capsys.readouterr().out
    assert kod2 == 0
    assert "tamamlandi" in cikti2


def test_senkron_kendini_onarma_bozuk_iskeleti_yeniden_kurar(tmp_path, capsys):
    """`--senkron` de (tıpkı `--durum` gibi) md bozuksa (bölüm ayraçları eksik/
    elle bozulmuş) birincil kaynaklardan YENİDEN KURAR + GÖRÜNÜR uyarı basar;
    onarım TAMAM üretmez."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    assert tt.cmd_baslat(str(tmp_path), "Test Dosyası") == 0
    analiz_md = tmp_path / "_oa" / "analiz" / "dosya-analiz.md"
    analiz_md.write_text("# eski biçim, bölüm ayraçsız içerik\n", encoding="utf-8")

    capsys.readouterr()
    kod = tt.cmd_senkron(str(tmp_path))
    yakalanan = capsys.readouterr()
    assert kod == 0
    assert "UYARI" in yakalanan.err and "eksik/bozuktu" in yakalanan.err
    icerik = analiz_md.read_text(encoding="utf-8")
    assert tt._iskelet_saglam_mi(icerik)
    assert not tt._tamam_isaretci_var_mi(icerik)


def test_serh_tarihcesi_senkron_sonrasi_da_kaybolmaz(tmp_path):
    """Şerh (durum.json `serh_tarihcesi`) KALICIDIR — md sonradan `--senkron` ile
    yeniden türetilse bile bölüm 13'te GÖRÜNÜR kalmaya devam eder (kayıpsızlık:
    md şerh bilgisinin TEK nüshası değildir, durum.json'dan yeniden basılır)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    _cikti_birak(tmp_path)
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    assert tt.cmd_kaydet(str(tmp_path)) == 0
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v2")}])
    assert tt.cmd_kaydet(str(tmp_path), zorla=True) == 0

    assert tt.cmd_senkron(str(tmp_path)) == 0
    icerik = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert "ŞERH" in icerik
    assert "dilekce.pdf" in icerik


def test_gomulu_marker_sahte_tamam_uretmez(tmp_path):
    """Gate G+ DELİNME KAPATMA (Fable K CONFIRMED smoke): --kaydet HİÇ koşmadan bir
    _oa/cikti/*.md İÇİNE TAMAM marker metni (örnek/backtick olarak) yazılırsa, --senkron
    onu gömse bile --durum SAHTE 'tamamlandı' DEMEMELİDİR (exit 3). Ayrıca gömülü
    muhakeme metni KAYBOLMAMALIDIR (kayıpsızlık)."""
    _kunye_yaz(tmp_path, [{"kaynak": "dilekce.pdf", "sha": _sha("v1")}])
    tt.cmd_baslat(str(tmp_path), "Test Dosyası")
    cikti_dir = tmp_path / "_oa" / "cikti"
    cikti_dir.mkdir(parents=True, exist_ok=True)
    marker = tt._tamam_marker("2099-01-01 00:00")
    (cikti_dir / "04-arastirma.md").write_text(
        f"# Araştırma\n\nÖrnek marker (belge): {marker}\n\nMUHAKEME METNI burada — kaybolmamalı.\n",
        encoding="utf-8")
    assert tt.cmd_senkron(str(tmp_path)) == 0
    assert tt.cmd_durum(str(tmp_path)) == 3, "gömülü marker SAHTE-TAMAM üretti — Gate G+ delindi"
    icerik = (tmp_path / "_oa" / "analiz" / "dosya-analiz.md").read_text(encoding="utf-8")
    assert "MUHAKEME METNI burada" in icerik


def test_tamam_isaretci_yalniz_son_satirda_ve_notrleme(tmp_path):
    """Birim: TAMAM yalnız SON boş-olmayan satırda tam-satır sayılır; nötrleme
    muhakeme metnini silmeden marker'ı son-satır eşleşmesinden çıkarır."""
    m = tt._tamam_marker("2026-07-20 03:00")
    assert tt._tamam_isaretci_var_mi(f"x\n\n{m}\n") is True        # gerçek son satır → TAMAM
    assert tt._tamam_isaretci_var_mi(f"{m}\n\ndevam\n") is False   # belge ortası → değil
    assert tt._tamam_isaretci_var_mi("iskelet\n") is False         # marker yok → değil
    notr = tt._marker_etkisizlestir(f"muhakeme\n{m}")
    assert tt._tamam_isaretci_var_mi(notr + "\n") is False and "muhakeme" in notr
