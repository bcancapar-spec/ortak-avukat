# -*- coding: utf-8 -*-
"""v0.5.19 — ÇAPRAZ DENETİM SONUÇ ÖNBELLEĞİ (türetilmiş, içerik özetine bağlı).

Ölçüm (PERFORMANS-STATUS §12.3): 3000 evraklık dosyayı temsil eden ölçek
kökünde Stop kancası (`--hook-denetle`) v0.5.17.1'de ~390 ms, v0.5.18'de
~469 ms (+79 ms). cProfile'a göre artışın neredeyse tamamı B-2 çapraz
denetimi: `_capraz_bosluk_uyarisi` → `_capraz_bosluk_hesapla` →
`capraz_denetim.caprazla_ayrintili`. Kanca gövdesi her Stop'ta TAM koşar;
çapraz denetimin girdileri ise çoğu turda değişmez.

Sözleşme (bu dosya kilitler):
- Girdiler değişmediyse ikinci çağrı `caprazla_ayrintili`yi ÇAĞIRMAZ.
- Anahtar İÇERİK özetidir (sha256): boyutu ve mtime'ı aynı bırakan tek
  baytlık değişiklik de yeniden hesaplatır. `capraz_denetim.py`,
  `pipeline_kayit.py`, ilgili damgalı denetim JSON'ları, yorumlayıcı ve
  önbellek şeması da anahtardadır.
- Önbellek TÜRETİLMİŞTİR (gerçeğin kaynağı değil): bozuk/eski/yabancı
  dosya ya da önbellek kodundaki herhangi bir hata ASLA yanlış "temiz"
  sonuç üretmez — şüphede hesaplanır (fail-closed).
- Append-only olay defterine dokunmaz; `_oa/defter` yoksa onu yaratmaz;
  önbellek dosyası `denetle` dedup parmak izine girmez; atomik yazılır.
- DURUM.md ve `--denetle` çıktısı önbellekli/önbelleksiz koşuda BİREBİR aynı.

Sentetik fikstür — gerçek müvekkil verisi yok (anayasa m.7).
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
CAPRAZ = SKILLS / "oa-pipeline" / "scripts" / "capraz_denetim.py"
PIPELINE = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pk():
    return _yukle("pk_v0519_capraz_onbellek", PIPELINE)


@pytest.fixture(scope="module")
def cd():
    return _yukle("cd_v0519_capraz_onbellek", CAPRAZ)


# Kasıtlı KOPUK üçlü. Tek-bayt değişiklik noktaları ASCII'dir ki dosya boyutu
# sabit kalsın: 'delil-1'→'delil-2' (graf düğüm kimliği), 'Fatura no 123'→
# 'Fatura no 124' (vakıa belgesi), 'unsur-99'→'unsur-98' (kıyas karşılığı).
GRAF = {"dugumler": [{"id": "delil-1", "tip": "delil", "ad": "Sözleşme örneği"}],
        "kenarlar": [{"dayanak_delil": ["delil-1"]}]}
VAKIA = {"iddialar": [{"id": "iddia-1", "metin": "Ödeme yapılmadı"}],
         "olaylar": [{"olgu": "Ödeme yapılmadı", "belge": "Fatura no 123",
                      "ispat_durumu": "belgeli"}]}
KIYAS = {"buyuk_onerme": {"unsurlar": [{"id": "unsur-1"}]},
         "kucuk_onerme": {"vakialar": [{"metin": "Taraflar hiç görüşmedi",
                                         "karsilar": ["unsur-99"],
                                         "dayanak_delil": ["delil-XYZ"]}]}}
GIRDI_ADLARI = {"graf": "01-illiyet-graf.json", "vakia": "04-vakia.json",
                "kiyas": "05-kiyas.json"}
BAYT_DEGISIMI = {"graf": (b'"id": "delil-1"', b'"id": "delil-2"'),
                 "vakia": (b"Fatura no 123", b"Fatura no 124"),
                 "kiyas": (b"unsur-99", b"unsur-98")}


def _yaz(kok, ad, veri):
    yol = kok / "_oa" / "cikti" / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _kok(tmp_path, defter=True, graf=GRAF, vakia=VAKIA, kiyas=KIYAS):
    kok = tmp_path / "dava"
    (kok / "_oa" / "cikti").mkdir(parents=True)
    if defter:
        (kok / "_oa" / "defter").mkdir(parents=True)
    _yaz(kok, GIRDI_ADLARI["graf"], graf)
    _yaz(kok, GIRDI_ADLARI["vakia"], vakia)
    _yaz(kok, GIRDI_ADLARI["kiyas"], kiyas)
    return kok


def _onbellek_yolu(pk, kok):
    return kok / "_oa" / "defter" / pk._CAPRAZ_ONBELLEK_ADI


def _casus(monkeypatch, mod):
    """`caprazla_ayrintili`yi GERÇEK gövdeye devreden sayaçla sarar: neyin
    yeniden HESAPLANDIĞI gözlenir, sonuç yine gerçek hesaptır."""
    asil = mod.caprazla_ayrintili
    cagri = []

    def sayan(*a, **k):
        cagri.append(1)
        return asil(*a, **k)

    monkeypatch.setattr(mod, "caprazla_ayrintili", sayan)
    return cagri


@pytest.fixture()
def sayac(pk, monkeypatch):
    return _casus(monkeypatch, pk._capraz_denetim_modulu())


def _beklenen(cd, kok):
    """Önbelleksiz referans: üç girdi diskten okunur, doğrudan hesaplanır."""
    girdi = {ad: json.loads((kok / "_oa" / "cikti" / dosya).read_text(encoding="utf-8"))
             for ad, dosya in GIRDI_ADLARI.items()}
    kopuk, belirsiz = cd.caprazla_ayrintili(girdi["graf"], girdi["vakia"], girdi["kiyas"])
    return list(kopuk), list(belirsiz)


def _ayni_boy_ayni_mtime_degistir(yol, eski, yeni):
    """İçeriği değiştir ama boyutu VE mtime'ı koru — anahtar stat'a değil
    İÇERİĞE bağlıysa yine yakalanmalı."""
    assert len(eski) == len(yeni)
    st = os.stat(yol)
    ham = yol.read_bytes()
    assert eski in ham, (eski, ham[:200])
    yol.write_bytes(ham.replace(eski, yeni, 1))
    os.utime(yol, ns=(st.st_atime_ns, st.st_mtime_ns))
    st2 = os.stat(yol)
    assert (st2.st_size, st2.st_mtime_ns) == (st.st_size, st.st_mtime_ns)


# ═══════════════ 1. İsabet: girdiler değişmeden yeniden hesap yok ═══════════

def test_girdiler_degismeden_ikinci_cagri_caprazla_ayrintiliyi_CAGIRMAZ(pk, cd, tmp_path, sayac):
    kok = _kok(tmp_path)
    beklenen = _beklenen(cd, kok)
    assert beklenen[0], "fikstür kasıtlı KOPUK olmalı"
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    assert len(sayac) == 1                                   # ilk çağrı hesaplar
    assert _onbellek_yolu(pk, kok).is_file()
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    assert len(sayac) == 1, "girdiler değişmedi — caprazla_ayrintili yeniden ÇAĞRILMAMALI"


# ═══════════════ 2. Anahtar İÇERİK özetidir ════════════════════════════════

@pytest.mark.parametrize("rol", ["graf", "vakia", "kiyas"])
def test_girdi_bayti_degisince_yeniden_hesaplanir(pk, cd, tmp_path, sayac, rol):
    kok = _kok(tmp_path)
    ilk = pk._capraz_bosluk_hesapla(str(kok))
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 1, "girdiler değişmedi — isabet beklenirdi"
    eski, yeni = BAYT_DEGISIMI[rol]
    _ayni_boy_ayni_mtime_degistir(kok / "_oa" / "cikti" / GIRDI_ADLARI[rol], eski, yeni)
    sonra = pk._capraz_bosluk_hesapla(str(kok))
    assert len(sayac) == 2, f"{rol} girdisinde tek bayt değişti — yeniden hesaplanmalıydı"
    assert sonra == _beklenen(cd, kok)
    assert sonra != ilk, "bayt değişimi sonucu değiştirmeliydi (fikstür denetimi)"


def test_capraz_denetim_py_ozeti_degisince_yeniden_hesaplanir(pk, tmp_path, monkeypatch):
    """Kod değişince eski sonuç geçersizdir. Depodaki dosyaya dokunulmaz:
    kardeş betiğin geçici KOPYASI yüklenir ve kopya değiştirilir."""
    kopya = tmp_path / "kod" / "capraz_denetim.py"
    kopya.parent.mkdir()
    shutil.copyfile(CAPRAZ, kopya)
    mod = _yukle("cd_v0519_onbellek_kopya", kopya)
    cagri = _casus(monkeypatch, mod)
    monkeypatch.setattr(pk, "_capraz_denetim_modulu", lambda: mod)
    kok = _kok(tmp_path)
    ilk = pk._capraz_bosluk_hesapla(str(kok))
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(cagri) == 1, "girdiler değişmedi — isabet beklenirdi"
    with open(kopya, "a", encoding="utf-8") as f:
        f.write("\n# sentetik kod değişikliği (v0.5.19 önbellek testi)\n")
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(cagri) == 2, "capraz_denetim.py özeti değişti — yeniden hesaplanmalıydı"


@pytest.mark.parametrize("parca", ["pipeline_kayit", "yorumlayici", "sema"])
def test_kod_ve_ortam_parcasi_degisince_yeniden_hesaplanir(pk, tmp_path, monkeypatch, sayac, parca):
    """Sonucu belirleyen diğer etkenler de anahtardadır: pipeline_kayit.py'nin
    kendisi (seçim/ayrıştırma mantığı), yorumlayıcı (str/Unicode
    semantiği: `lower`, `isalnum`, `\\w`) ve önbellek şeması."""
    kok = _kok(tmp_path)
    gercek_mod = pk._capraz_denetim_modulu()
    monkeypatch.setattr(pk, "_capraz_denetim_modulu", lambda: gercek_mod)
    if parca == "pipeline_kayit":
        kopya = tmp_path / "pk" / "pipeline_kayit.py"
        kopya.parent.mkdir()
        shutil.copyfile(PIPELINE, kopya)
        monkeypatch.setattr(pk, "__file__", str(kopya))
    ilk = pk._capraz_bosluk_hesapla(str(kok))
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 1, "girdiler değişmedi — isabet beklenirdi"
    if parca == "pipeline_kayit":
        with open(kopya, "a", encoding="utf-8") as f:
            f.write("\n# sentetik kod değişikliği (v0.5.19 önbellek testi)\n")
    elif parca == "yorumlayici":
        monkeypatch.setattr(pk, "_capraz_onbellek_yorumlayici", lambda: "sentetik-9.99")
    else:
        monkeypatch.setattr(pk, "_CAPRAZ_ONBELLEK_SEMA", pk._CAPRAZ_ONBELLEK_SEMA + 1000)
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 2, f"{parca} değişti — yeniden hesaplanmalıydı"


def test_damgali_denetim_jsonu_anahtara_girer(pk, tmp_path, sayac):
    """S1 seçimini besleyen damgalı denetim JSON'u (grafik_denetim /
    vakia_matris / kiyas_denetim) eklenince ve içeriği değişince — seçim
    aynı kalsa bile — yeniden hesaplanır."""
    kok = _kok(tmp_path)
    ilk = pk._capraz_bosluk_hesapla(str(kok))
    assert len(sayac) == 1
    damga = _yaz(kok, "01-illiyet-denetim.json", {
        "arac": "grafik_denetim", "cevrimler": [],
        "kaynaklar": [{"rol": "girdi", "yol": "cikti/01-illiyet-graf.json", "sha8": "00000000"}]})
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 2, "damgalı denetim JSON'u eklendi — yeniden hesaplanmalıydı"
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 2, "girdiler değişmedi — isabet beklenirdi"
    veri = json.loads(damga.read_text(encoding="utf-8"))
    veri["not"] = "yeniden koşuldu"
    damga.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 3, "damgalı denetim JSON'u değişti — yeniden hesaplanmalıydı"


def test_ilgisiz_calisma_evraki_onbellegi_gecersiz_kilmaz(pk, tmp_path, sayac):
    """Etkinlik kilidi: model `_oa/cikti`ya dilekçe taslağı yazdıkça (her
    PostToolUse) önbellek düşseydi kazanç sahada sıfır olurdu."""
    kok = _kok(tmp_path)
    ilk = pk._capraz_bosluk_hesapla(str(kok))
    (kok / "_oa" / "cikti" / "08-dilekce-taslak.md").write_text(
        "NETİCE-İ TALEP\nsentetik taslak\n", encoding="utf-8")
    assert pk._capraz_bosluk_hesapla(str(kok)) == ilk
    assert len(sayac) == 1


# ═══════════════ 3. Fail-closed: önbellek hatası asla "temiz" üretmez ═══════

def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _boz(yol, tur):
    ham = yol.read_bytes()
    bas, ayrac, _govde = ham.partition(b"\n")
    assert ayrac, "önbellek biçimi: başlık satırı + gövde"
    anahtar = json.loads(bas)["anahtar"]
    temiz = json.dumps({"kopuk": [], "belirsiz": []}).encode("utf-8")

    def baslik(a, g):
        return json.dumps({"anahtar": a, "govde": _sha(g)}).encode("ascii") + b"\n" + g

    if tur == "cop":
        yol.write_bytes(b"\x00\xff\xfe cop \x00" * 16)
    elif tur == "kesik":
        yol.write_bytes(ham[: len(ham) // 2])
    elif tur == "bos":
        yol.write_bytes(b"")
    elif tur == "govde_temizlenmis":           # elle düzenleme: uyarılar silinmiş
        yol.write_bytes(bas + b"\n" + temiz)
    elif tur == "anahtar_yabanci":             # kendi içinde tutarlı ama başka girdilerin
        yol.write_bytes(baslik("0" * 64, temiz))
    elif tur == "govde_json_degil":
        yol.write_bytes(baslik(anahtar, b"{bozuk"))
    elif tur == "govde_tip_yanlis":
        yol.write_bytes(baslik(anahtar, json.dumps({"kopuk": "x", "belirsiz": []}).encode()))
    elif tur == "dizin":
        yol.unlink()
        yol.mkdir()
    else:
        raise AssertionError(tur)


@pytest.mark.parametrize("tur", ["cop", "kesik", "bos", "govde_temizlenmis", "anahtar_yabanci",
                                 "govde_json_degil", "govde_tip_yanlis", "dizin"])
def test_bozuk_onbellek_yanlis_sonuc_uretmez_yeniden_hesaplanir(pk, cd, tmp_path, sayac, tur):
    kok = _kok(tmp_path)
    beklenen = _beklenen(cd, kok)
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    yol = _onbellek_yolu(pk, kok)
    assert yol.is_file()
    _boz(yol, tur)
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen, f"bozuk önbellek ({tur}) sonucu çarpıttı"
    assert len(sayac) == 2, f"bozuk önbellek ({tur}) kullanılmamalı — yeniden hesaplanmalıydı"
    if tur != "dizin":                         # kendini onarır: sonraki çağrı yine isabet
        assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
        assert len(sayac) == 2


def test_okunamayan_girdide_onbellek_kullanilmaz_ve_yazilmaz(pk, cd, tmp_path, monkeypatch, sayac):
    """Seçilen bir girdi okunamıyorsa (ör. başka süreç kilitli tutuyor) içeriği
    bilinmez: önbellek ne okunur ne yazılır (şüphede hesapla); sonuç eski
    davranışla — o girdi yok sayılarak — hesaplanır."""
    kok = _kok(tmp_path)
    kilitli = os.path.realpath(kok / "_oa" / "cikti" / GIRDI_ADLARI["vakia"])
    gercek_open = open

    def secici_open(yol, *a, **k):
        kip = a[0] if a else k.get("mode", "r")
        if "b" in kip and os.path.realpath(str(yol)) == kilitli:
            raise PermissionError("sentetik: dosya başka süreçte kilitli")
        return gercek_open(yol, *a, **k)

    monkeypatch.setattr(pk, "open", secici_open, raising=False)
    cikti = kok / "_oa" / "cikti"
    graf = json.loads((cikti / GIRDI_ADLARI["graf"]).read_text(encoding="utf-8"))
    kiyas = json.loads((cikti / GIRDI_ADLARI["kiyas"]).read_text(encoding="utf-8"))
    kopuk, belirsiz = cd.caprazla_ayrintili(graf, None, kiyas)
    beklenen = (list(kopuk), list(belirsiz))
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    assert len(sayac) == 2, "okunamayan girdiyle önbellek kullanılmamalı"
    assert not _onbellek_yolu(pk, kok).exists(), "okunamayan girdiyle önbellek yazılmamalı"


def test_isabet_iskanin_dondurdugunden_farkli_sey_donduremez(pk, tmp_path, monkeypatch):
    """JSON gidiş-dönüşü her Python değerini korumaz (tuple → list, sayı
    anahtar → dize). Bugünkü öğeler {tip: str, mesaj: str}; ama
    capraz_denetim ileride başka biçim döndürürse isabet, ıskanın
    döndüreceğinden FARKLI değer döndürmemeli → böyle sonuç önbelleğe
    yazılmaz, her koşuda hesaplanır."""
    kok = _kok(tmp_path)
    mod = pk._capraz_denetim_modulu()
    cagri = []

    def sahte(*a, **k):
        cagri.append(1)
        return [{"tip": "SENTETIK", "mesaj": "m", "konum": (1, 2)}], []

    monkeypatch.setattr(mod, "caprazla_ayrintili", sahte)
    ilk = pk._capraz_bosluk_hesapla(str(kok))
    ikinci = pk._capraz_bosluk_hesapla(str(kok))
    assert ikinci == ilk, "isabet, ıskanın döndürdüğünden farklı değer döndürdü"
    assert len(cagri) == 2
    assert not _onbellek_yolu(pk, kok).exists()


@pytest.mark.parametrize("adim", ["_capraz_onbellek_anahtari", "_capraz_onbellek_oku",
                                  "_capraz_onbellek_yaz"])
def test_onbellek_kodu_cokerse_sonuc_yine_dogru(pk, cd, tmp_path, monkeypatch, adim):
    """`_capraz_bosluk_hesapla`nın dış `except`i ([], []) döner — önbellek
    adımının istisnası oraya sızsaydı çapraz bölüm SESSİZCE "temiz" görünürdü."""
    kok = _kok(tmp_path)

    def patla(*a, **k):
        raise RuntimeError("sentetik önbellek arızası")

    monkeypatch.setattr(pk, adim, patla)
    assert pk._capraz_bosluk_hesapla(str(kok)) == _beklenen(cd, kok)


# ═══════════════ 4. Yan etki sınırları ═════════════════════════════════════

def test_onbellek_dedup_parmak_izine_girmez(pk, tmp_path):
    """`denetle` dedup ayırt edicisi `_oa/defter` içeriğini özetler; önbellek
    dosyası oraya girseydi ilk koşunun kendi yazımı izi değiştirir ve aynı
    saniyedeki çift-kanal kopyası kısa devre yapamazdı (dedup ölü kod)."""
    kok = _kok(tmp_path)
    iz = pk._hook_denetle_ayirt(str(kok))
    pk._capraz_bosluk_hesapla(str(kok))
    yol = _onbellek_yolu(pk, kok)
    assert yol.is_file()
    assert pk._hook_denetle_ayirt(str(kok)) == iz
    (yol.parent / (yol.name + ".tmp.424242")).write_bytes(b"yarim kalmis yazim")
    assert pk._hook_denetle_ayirt(str(kok)) == iz


def test_defter_yoksa_onbellek_yazilmaz_ve_defter_yaratilmaz(pk, cd, tmp_path):
    """`_oa/defter`in varlığı "hat açık" anlamı taşır (nabız, dedup, HAT
    ATLANDI nöbetçisi). Türetilmiş bir önbellek o dizini yaratamaz."""
    kok = _kok(tmp_path, defter=False)
    beklenen = _beklenen(cd, kok)
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    assert pk._capraz_bosluk_hesapla(str(kok)) == beklenen
    assert not (kok / "_oa" / "defter").exists()


def test_append_only_olay_defterine_dokunmaz(pk, tmp_path):
    kok = _kok(tmp_path)
    defter = kok / "_oa" / "defter"
    jsonl = defter / "pipeline-olaylar.jsonl"
    jsonl.write_bytes(b'{"tip": "sentetik-olay", "n": 1}\n')
    once = jsonl.read_bytes()
    pk._capraz_bosluk_hesapla(str(kok))
    pk._capraz_bosluk_hesapla(str(kok))
    assert jsonl.read_bytes() == once
    assert sorted(os.listdir(defter)) == sorted(["pipeline-olaylar.jsonl", pk._CAPRAZ_ONBELLEK_ADI])


def test_onbellek_atomik_yazilir_basarisiz_yazim_eskiyi_bozmaz(pk, cd, tmp_path, monkeypatch, sayac):
    """tmp + os.replace: yer değiştirme başarısız olursa eski (geçerli)
    önbellek dosyası BAYT BAYT yerinde kalır, tmp artığı kalmaz, sonuç doğru."""
    kok = _kok(tmp_path)
    pk._capraz_bosluk_hesapla(str(kok))
    yol = _onbellek_yolu(pk, kok)
    eski = yol.read_bytes()
    eski_, yeni_ = BAYT_DEGISIMI["vakia"]
    _ayni_boy_ayni_mtime_degistir(kok / "_oa" / "cikti" / GIRDI_ADLARI["vakia"], eski_, yeni_)

    def reddet(*a, **k):
        raise PermissionError("sentetik: hedef başka süreçte açık")

    monkeypatch.setattr(pk.os, "replace", reddet)
    assert pk._capraz_bosluk_hesapla(str(kok)) == _beklenen(cd, kok)
    assert len(sayac) == 2
    assert yol.read_bytes() == eski
    assert [a for a in os.listdir(yol.parent) if ".tmp." in a] == []


# ═══════════════ 5. Çıktı önbellekli/önbelleksiz BİREBİR aynı ═══════════════

def _cli(args, cwd):
    cp = subprocess.run([sys.executable, str(PIPELINE)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _durum_md(kok):
    return (kok / "_oa" / "DURUM.md").read_text(encoding="utf-8")


def _cok_uyarili_kok(tmp_path):
    """Tavanı (`_ADVISORY_TAVAN`) aşan uyarı sayısı: «… +N uyarı daha» satırı
    da karşılaştırmaya girer. 30 belgesiz olay → 30 OLGU_EVRAKSIZ."""
    vakia = {"iddialar": [{"id": "iddia-1", "metin": "Ödeme yapılmadı"}],
             "olaylar": [{"olgu": f"Sentetik olgu {i}", "belge": "", "ispat_durumu": "tanik"}
                         for i in range(30)]
             + [{"olgu": "Ödeme yapılmadı", "belge": "Fatura no 123", "ispat_durumu": "belgeli"}]}
    kok = tmp_path / "dava"
    (kok / "_oa" / "metin").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    (kok / "_oa" / "metin" / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    kod, out = _cli(["--baslat", "Sentetik Önbellek Davası", "--kok", kok], cwd=kok)
    assert kod == 0, out
    _yaz(kok, GIRDI_ADLARI["graf"], GRAF)
    _yaz(kok, GIRDI_ADLARI["vakia"], vakia)
    _yaz(kok, GIRDI_ADLARI["kiyas"], KIYAS)
    return kok


def test_DURUM_md_ve_denetle_ciktisi_onbellekli_onbelleksiz_BIREBIR(pk, tmp_path, monkeypatch, sayac):
    kok = _cok_uyarili_kok(tmp_path)
    monkeypatch.setattr(pk, "simdi", lambda: "2026-01-01T00:00:00")
    _, cikti1 = pk.denetle_calistir(str(kok))            # ıska: hesaplar, yazar
    md1 = _durum_md(kok)
    assert len(sayac) == 1
    _, cikti2 = pk.denetle_calistir(str(kok))            # isabet: hesaplamaz
    md2 = _durum_md(kok)
    assert len(sayac) == 1
    yol = _onbellek_yolu(pk, kok)
    yol.unlink()
    yol.mkdir()                                          # önbellek KULLANILAMAZ: önbelleksiz yol
    _, cikti3 = pk.denetle_calistir(str(kok))
    md3 = _durum_md(kok)
    assert len(sayac) == 2
    assert "## 🔴 Çapraz Denetim Uyarısı" in md1 and "uyarı daha" in md1
    assert md1 == md2 == md3
    assert cikti1 == cikti2 == cikti3


def test_cli_ikinci_kosu_isabet_DURUM_md_ayni_onbellek_yeniden_yazilmaz(pk, tmp_path):
    """Süreçler arası: kanca her Stop'ta YENİ süreçtir. İlk `--denetle`
    önbelleği yazar; ikincisi isabet eder ve dosyayı yeniden YAZMAZ."""
    kok = _cok_uyarili_kok(tmp_path)
    kod1, out1 = _cli(["--denetle", "--kok", kok], cwd=kok)
    md1 = _durum_md(kok)
    yol = _onbellek_yolu(pk, kok)
    assert yol.is_file(), "ilk --denetle önbelleği yazmalıydı"
    st1, ham1 = os.stat(yol), yol.read_bytes()
    kod2, out2 = _cli(["--denetle", "--kok", kok], cwd=kok)
    md2 = _durum_md(kok)

    def zamansiz(md):
        return "\n".join(s for s in md.splitlines() if not s.startswith("_Türetim zamanı:"))

    assert (kod1, out1) == (kod2, out2)
    assert zamansiz(md1) == zamansiz(md2)
    assert "## 🔴 Çapraz Denetim Uyarısı" in md2
    assert yol.read_bytes() == ham1 and os.stat(yol).st_mtime_ns == st1.st_mtime_ns


# ═══════════════ 6. Ayrıştırma `capraz_denetim._yukle` ile eşdeğer ═══════════

_AYRISTIRMA_ORNEKLERI = {
    "gecerli": json.dumps(VAKIA, ensure_ascii=False).encode("utf-8"),
    "crlf": json.dumps(VAKIA, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8"),
    "bom": b"\xef\xbb\xbf" + json.dumps(VAKIA).encode("utf-8"),
    "gecersiz_utf8": b'{"olgu": "\xff\xfe"}',
    "utf16": json.dumps(VAKIA).encode("utf-16"),
    "dize_icinde_cr": b'{"olgu": "a\rb"}',
    "liste": b"[1, 2, 3]",
    "bos": b"",
}


@pytest.mark.parametrize("ad", sorted(_AYRISTIRMA_ORNEKLERI))
def test_bayttan_ayristirma_capraz_denetim_yukle_ile_ESDEGER(pk, cd, tmp_path, ad):
    """Önbellek anahtarı ile hesaplanan içerik AYNI baytlardan gelsin diye
    girdi bir kez okunur ve o baytlardan ayrıştırılır. Ayrıştırma kuralının
    tek kaynağı `capraz_denetim._yukle`dur; bu kilit iki yolun her girdide
    aynı sonuca (ya da aynı redde) vardığını doğrular."""
    ham = _AYRISTIRMA_ORNEKLERI[ad]
    yol = tmp_path / "girdi.json"
    yol.write_bytes(ham)
    coz = pk._capraz_girdi_coz          # yoksa AttributeError — "ret" sayılmasın

    def sonuc(f):
        try:
            return ("tamam", f())
        except Exception:
            return ("ret",)

    assert sonuc(lambda: coz(ham)) == sonuc(lambda: cd._yukle(str(yol)))
