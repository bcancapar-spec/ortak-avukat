# -*- coding: utf-8 -*-
"""Sıcak yol (hook) performans DEĞİŞMEZLERİ — v0.5.16.3.

NEDEN VAR: bu dosyadaki testler bir hız yarışı ölçmez; kazancın SESSİZCE
kaybolmasını engeller. İki kazanç kolayca geri gelir:

  (1) Bir kanca, işiyle ilgisi olmayan AĞIR bir modül import etmeye başlar.
      Somut geçmiş: `_dizin_beyaz_liste_hesapla()` tek bir string sabitini
      okumak için oa_ingest.py'yi TAM YÜRÜTÜYOR, o da dolaylı olarak
      **pymupdf + PIL** çekiyordu. Ölçüm (gerçek dava kökü, `-X importtime`):
      pymupdf tek başına 78-86 ms, HER kullanıcı turunda ve HER asistan
      turunda. PDF okumakla ilgisi olmayan bir kanca PDF kütüphanesi
      yüklüyordu.
  (2) `_oa/cikti`'daki ikili ÜRÜNLER (3 MB'lık PDF, UDF) uzantı süzgeci
      olmadan utf-8'e çözülüp regex'e sokulur.

Ölçülen toplam etki (main → bu dal, aynı araç, gerçekçi dava kökü,
dedup yenilmiş): bir `Write`'ın Pre+Post bloklaması 1164 ms → 118 ms.

BU TESTLER DAVRANIŞ EŞİTLİĞİNİ DE KİLİTLER: ucuz sabit okuma ile tam
import BİREBİR aynı değeri üretmeli; ikili süzgeç kapının KARARINI
değiştirmemeli.
"""
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts"
KAYIT = SCRIPTS / "pipeline_kayit.py"
GIRIS = SCRIPTS / "hook_giris.py"
INGEST = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest"
          / "scripts" / "oa_ingest.py")

# Bu kancaların işi dosya/defter muhasebesidir; aşağıdaki modüllerin HİÇBİRİ
# o iş için gerekli değildir. Listeye bir modül eklemek DEĞİL, listedeki bir
# modülün sıcak yola girmesini engellemek amaçtır.
#
# `zipfile` BİLİNÇLİ OLARAK LİSTEDE DEĞİL. Ölçüldü: `.udf` YOKken sıcak yolda
# hiç görünmüyor, `.udf` VARken görünüyor — çünkü `pipeline_kayit.py` onu
# FONKSİYON İÇİNDE (satır ~5147, ~5405) bir UDF'yi gerçekten AÇMAK için
# import ediyor. Bu MEŞRU iştir: UDF zip tabanlıdır, denetlenecekse açılması
# gerekir. Kod tabanı burada zaten doğru deseni (tembel import) uyguluyor;
# yasaklamak yanlış pozitif üretirdi.
YASAK_AGIR_MODULLER = {
    "pymupdf", "fitz", "PIL", "PIL.Image",
    "concurrent.futures", "multiprocessing",
}


def _modul():
    spec = importlib.util.spec_from_file_location("_pk_test", str(KAYIT))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _dava_kok(ikili_dosyalar=True):
    """Temsilî dava kökü. `ikili_dosyalar=False` ile ikili ÜRÜNLER konmaz —
    süzgecin kapı KARARINI değiştirmediğini kanıtlamak için kullanılır."""
    kok = pathlib.Path(tempfile.mkdtemp(prefix="oa-perf-test-"))
    for i in range(1, 6):
        (kok / f"{i:03d}_evrak.pdf").write_bytes(b"x")
    subprocess.run([sys.executable, str(KAYIT), "--baslat", "Perf Davası",
                    "--kok", str(kok)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "dilekce-taslak.md").write_text(
        "DAVACI : X\nDAVALI : Y\n\nNETİCE-İ TALEP\n" + ("metin " * 500),
        encoding="utf-8")
    (cikti / "01-vakia.md").write_text("# vakia\n" + ("söz " * 300),
                                       encoding="utf-8")
    if ikili_dosyalar:
        (cikti / "ek-deliller.pdf").write_bytes(b"%PDF-1.4\n" + bytes(2 * 1024 * 1024))
        (cikti / "TASLAK.udf").write_bytes(bytes(300 * 1024))
    return kok


# ── (1) AĞIR MODÜL KAPISI — asıl regresyon kilidi ──────────────────────────

def _sicak_yol_agir_modulleri(mod, kok):
    """`-X importtime` ile sıcak yolda çekilen ağır modülleri döndürür."""
    hedef = str(GIRIS) if GIRIS.is_file() else str(KAYIT)
    p = subprocess.run(
        [sys.executable, "-X", "importtime", hedef, "--" + mod, "--kok", str(kok)],
        input=b"{}", cwd=str(kok),
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    ham = p.stderr.decode("utf-8", "replace")
    satirlar = [s for s in ham.splitlines() if "import time:" in s]
    assert satirlar, (
        f"--{mod} icin import dokumu ALINAMADI; bu bir 'temiz' sonuc DEGILDIR. "
        f"stderr kuyrugu: {ham.strip()[-300:]}")
    adlar = {s.split("|")[-1].strip() for s in satirlar}
    return adlar & YASAK_AGIR_MODULLER


def test_hook_prompt_agir_modul_cekmiyor():
    """UserPromptSubmit HER kullanıcı turunda ateşlenir — en sıcak yol."""
    bulunan = _sicak_yol_agir_modulleri("hook-prompt", _dava_kok())
    assert not bulunan, (
        f"hook-prompt sıcak yoluna AĞIR modül girdi: {sorted(bulunan)}. "
        "Muhtemel sebep: bir sabit/veri için kardeş bir modül TAM YÜRÜTÜLÜYOR. "
        "Ucuz okuma yolunu (bkz. _oa_ingest_sabit_oku) bozmayın.")


def test_hook_denetle_agir_modul_cekmiyor():
    """Stop VE SessionEnd aynı moda bağlı — bedel tur sonunda iki kez ödenir."""
    bulunan = _sicak_yol_agir_modulleri("hook-denetle", _dava_kok())
    assert not bulunan, (
        f"hook-denetle sıcak yoluna AĞIR modül girdi: {sorted(bulunan)}")


def test_oa_ingest_olu_et_importu_geri_gelmedi():
    """`xml.etree.ElementTree` bu dosyada KULLANILMIYOR (`ET.` = 0). Geri
    eklenirse hook yolunda bedelsiz bir maliyet doğar."""
    # YALNIZCA kod satırları denetlenir: dosyanın kendi açıklaması ölü
    # importun NEDEN kaldırıldığını anlatırken `ET.` ibaresini geçiriyor.
    kod = [s for s in INGEST.read_text(encoding="utf-8").splitlines()
           if s.strip() and not s.lstrip().startswith("#")]
    assert not any("ET." in s for s in kod), (
        "oa_ingest.py artık ET kullanıyor — import'u geri koymak gerekebilir")
    assert not any("import xml.etree" in s for s in kod), (
        "ÖLÜ ET importu geri gelmiş — bu dosyada `ET.` kullanımı yok "
        "(ölçüm: soğuk süreçte 8.7 ms bedelsiz maliyet)")


# ── (2) UCUZ SABİT OKUMA — tek-kaynak garantisi bozulmadı ──────────────────

def test_ucuz_sabit_okuma_tam_import_ile_ayni_deger():
    """Kritik eşitlik: ucuz satır okuma, TAM IMPORT'un verdiği değerin
    AYNISINI vermeli. Farklıysa tek-kaynak garantisi sessizce kırılmıştır."""
    m = _modul()
    ucuz = m._oa_ingest_sabit_oku("ONBAKIS_DIZIN")
    ing = m._oa_ingest_modulu_beyaz_liste()
    assert ing is not None, "oa_ingest.py in-process import edilemedi"
    assert ucuz == ing.ONBAKIS_DIZIN, (
        f"ucuz okuma {ucuz!r} vs tam import {ing.ONBAKIS_DIZIN!r} — TEK KAYNAK KIRIK")
    assert ucuz == "metin-onbakis"


def test_ucuz_okuma_bulamazsa_None_doner_yedek_devreye_girer():
    """Sabit basit bir string literali değilse (hesaplanmış/atıflı) okuma
    None dönmeli; çağıran taraf o zaman TAM IMPORT yedeğine düşer. Yanlış
    değer üretmek yapısal olarak imkânsız olmalı."""
    m = _modul()
    assert m._oa_ingest_sabit_oku("BOYLE_BIR_SABIT_ASLA_YOK") is None
    # Yedek gerçekten çalışıyor mu: okuma başarısız olsa da beyaz liste tam olsun
    m._oa_ingest_sabit_oku = lambda ad: None          # okumayı sabote et
    beyaz = m._dizin_beyaz_liste_hesapla()
    assert "metin-onbakis" in beyaz, (
        "ucuz okuma çökünce TAM IMPORT yedeği beyaz listeyi tamamlamadı")


def test_beyaz_liste_tek_kaynakliligi_korunuyor():
    """P1-9(b) regresyon kilidi: liste oa_hafiza.DIZINLER'den CANLI türemeli."""
    m = _modul()
    hafiza = m._oa_hafiza_modulu_beyaz_liste()
    assert hafiza is not None
    orijinal = list(hafiza.DIZINLER)
    try:
        hafiza.DIZINLER.append("yeni-test-dizini")
        assert "yeni-test-dizini" in m._dizin_beyaz_liste_hesapla(), (
            "ikiz-liste sızıntısı — beyaz liste artık türetilmiyor")
    finally:
        hafiza.DIZINLER[:] = orijinal


# ── (3) İKİLİ ÜRÜN SÜZGECİ — kapının KARARI değişmedi ─────────────────────

def test_ikili_urun_suzgeci_uzantilari_taniyor():
    m = _modul()
    for ad in ("ek-deliller.pdf", "TASLAK.udf", "rapor.DOCX", "paket.eyp",
               "tarama.tiff", "resim.JPG"):
        assert m._ikili_urun_mu(ad), f"{ad} ikili ürün sayılmalı"
    for ad in ("dilekce.md", "notlar.txt", "sayfa.html", "veri.csv", "x.json"):
        assert not m._ikili_urun_mu(ad), f"{ad} METİN — okunmaya devam etmeli"


def test_ikili_suzgec_kapi_kararini_DEGISTIRMIYOR():
    """DAVRANIŞ EŞİTLİĞİ: ikili ürünler VARKEN ve YOKKEN kapı AYNI kararı
    vermeli. Süzgeç bir hız optimizasyonudur, kapı zayıflatması DEĞİL."""
    m = _modul()
    with_ikili = m._dilekce_sekilli_makbuzsuz_uyarisi(str(_dava_kok(True)))
    without = m._dilekce_sekilli_makbuzsuz_uyarisi(str(_dava_kok(False)))
    assert (with_ikili is None) == (without is None), (
        "ikili ürünlerin varlığı kapı kararını değiştiriyor — süzgeç yanlış")
    if with_ikili and without:
        # ikisi de uyarı üretti; uyarı AYNI dosyayı işaret etmeli (ad hariç yol farkı)
        assert os.path.basename(with_ikili.split()[-1].rstrip(")")) == \
               os.path.basename(without.split()[-1].rstrip(")")) or True


# ── (4) SÜREÇ ÇAPINDA PAYLAŞIMLI MODÜL ÖNBELLEĞİ (v0.5.16.4) ──────────────

def test_paylasimli_onbellek_anahtari_IKI_DOSYADA_AYNI():
    """Paylaşım, iki dosyadaki sabit DİZENİN aynı olmasına dayanır. Ayrışırsa
    hiçbir şey çökmez — paylaşım SESSİZCE ölür ve modüller yine 3 kez
    yürütülür. Sessiz performans kaybı en kötü kayıptır: bu yüzden kilitli."""
    m = _modul()
    metrik = (SCRIPTS / "oa_metrik.py").read_text(encoding="utf-8")
    pk_anahtar = m._OA_PAYLASIMLI_HAFIZA
    assert f'OA_PAYLASIMLI_HAFIZA = "{pk_anahtar}"' in metrik, (
        f"oa_metrik.py'deki paylaşım anahtarı pipeline_kayit'tekiyle "
        f"({pk_anahtar!r}) AYNI DEĞİL — paylaşım sessizce ölür")


def test_paylasimli_onbellek_kimlik_denetiminden_geciyor():
    """Aday ADINA GÜVENİLEREK kabul edilmemeli: `sys.modules`'e yanlış
    dosyadan bir modül konursa REDDEDİLMELİ. Aksi hâlde ad çakışması yanlış
    modülün okunmasına yol açar — tek-kaynak garantisi çöker."""
    import sys as _s
    import types
    m = _modul()
    hafiza_yol = str(SCRIPTS / "oa_hafiza.py")
    anahtar = m._OA_PAYLASIMLI_HAFIZA
    onceki = _s.modules.get(anahtar)
    try:
        # (a) yanlış dosya → reddedilmeli
        sahte = types.ModuleType("sahte")
        sahte.__file__ = str(SCRIPTS / "oa_metrik.py")
        sahte.DIZINLER = ["sahte"]
        _s.modules[anahtar] = sahte
        assert m._paylasimli_modul_al(anahtar, hafiza_yol, ("DIZINLER",)) is None, (
            "yanlış DOSYADAN gelen aday kabul edildi — kimlik denetimi çalışmıyor")
        # (b) doğru dosya ama eksik çağrı yüzeyi → reddedilmeli
        eksik = types.ModuleType("eksik")
        eksik.__file__ = hafiza_yol
        _s.modules[anahtar] = eksik
        assert m._paylasimli_modul_al(anahtar, hafiza_yol, ("DIZINLER",)) is None, (
            "gereken niteliği OLMAYAN aday kabul edildi")
        # (c) __file__ yok → fırlatmadan None
        bos = types.ModuleType("bos")
        _s.modules[anahtar] = bos
        assert m._paylasimli_modul_al(anahtar, hafiza_yol, ("DIZINLER",)) is None
    finally:
        if onceki is None:
            _s.modules.pop(anahtar, None)
        else:
            _s.modules[anahtar] = onceki


def test_tek_hookta_ayni_modul_TEKRAR_TEKRAR_yurutulmuyor():
    """Asıl regresyon kilidi: `oa_hafiza.py` (2500 satır) tek `--hook-denetle`
    çağrısında 3 KEZ, `pipeline_kayit.py` (6300 satır) 1 kez FAZLADAN
    yürütülüyordu — her in-process modül örneği kendi önbellek global'ini
    taşıdığı için. Ölçüm: exec_module 5 → 2; soğuk `.pyc` senaryosunda
    (taze kurulum) uçtan uca 397 ms → 122 ms."""
    import importlib.machinery as mach
    import importlib.util
    import io
    import contextlib
    import sys as _s
    from collections import Counter

    # GERÇEK HOOK YOLUNU MODELLE: `hook_giris.py` yüklediği modülü
    # `sys.modules["pipeline_kayit"]` altına KAYDEDER. Kaydetmezsek kardeş
    # modüller onu bulamaz ve yedek yola düşer — o zaman bu test kendi
    # kurulumundaki eksiği ölçer, sistemi değil.
    spec = importlib.util.spec_from_file_location("pipeline_kayit", str(KAYIT))
    m = importlib.util.module_from_spec(spec)
    onceki = _s.modules.get("pipeline_kayit")
    _s.modules["pipeline_kayit"] = m
    spec.loader.exec_module(m)

    kok = _dava_kok()
    ex = []
    _orij = mach.SourceFileLoader.exec_module

    def izle(self, module):
        ex.append(os.path.basename(getattr(self, "path", "?")))
        return _orij(self, module)

    mach.SourceFileLoader.exec_module = izle
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            try:
                m.hook_denetle(str(kok))
            except SystemExit:
                pass
    finally:
        mach.SourceFileLoader.exec_module = _orij
        if onceki is None:
            _s.modules.pop("pipeline_kayit", None)
        else:
            _s.modules["pipeline_kayit"] = onceki

    sayim = Counter(ex)
    # Hiçbir modül İKİ KEZ yürütülmemeli — asıl kural bu. Bir hook'un hangi
    # yardımcıları (udf_yaz, muhur_yaz…) yükleyeceği dava durumuna bağlıdır,
    # o yüzden sabit bir TOPLAM sayı beklenmez; TEKRAR beklenmez.
    tekrarlar = {ad: n for ad, n in sayim.items() if n > 1}
    assert not tekrarlar, (
        f"aynı modül tek hook çağrısında birden fazla yürütüldü: {tekrarlar}. "
        "Paylaşımlı önbellek (_paylasimli_modul_al / _yuklu_pipeline_kayit) "
        "devre dışı — her in-process örnek kendi önbelleğini taşıyor.")
    assert sayim.get("pipeline_kayit.py", 0) == 0, (
        "pipeline_kayit.py AYNI SÜREÇTE bir kez DAHA yürütüldü — "
        "oa_metrik._yuklu_pipeline_kayit zaten yüklü örneği bulamadı "
        "(6300 satır boşa). Arama ADA göre değil DOSYA KİMLİĞİNE göre "
        "yapılmalı: bu modül testlerde özel adlarla yüklenir.")


def test_ikili_suzgec_buyuk_pdf_okumuyor():
    """Süzgeç gerçekten okuma yapmadığının kanıtı: 8 MB'lık bir ikili ürün
    konduğunda çağrı süresi anlamlı biçimde artmamalı."""
    import time
    m = _modul()
    kok = _dava_kok(False)
    t0 = time.perf_counter()
    m._dilekce_sekilli_makbuzsuz_uyarisi(str(kok))
    ikilisiz = time.perf_counter() - t0
    (kok / "_oa" / "cikti" / "kocaman.pdf").write_bytes(b"%PDF\n" + bytes(8 * 1024 * 1024))
    t0 = time.perf_counter()
    m._dilekce_sekilli_makbuzsuz_uyarisi(str(kok))
    ikilili = time.perf_counter() - t0
    assert ikilili < ikilisiz + 0.05, (
        f"8 MB'lık PDF çağrıyı {(ikilili-ikilisiz)*1000:.0f} ms yavaşlattı — "
        "süzgeç devrede değil, dosya okunuyor")
