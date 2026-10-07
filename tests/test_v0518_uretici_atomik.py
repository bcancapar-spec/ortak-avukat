# -*- coding: utf-8 -*-
"""v0.5.18 — ZİNCİR ÜRETİCİLERİ · S3 ATOMİK JSON YAZIMI (B-4, üretici ayağı).

NEDEN VAR: Fable tutarlılık raporu (2026-10-07) B-4 — K2 graf kapısı
`_oa/cikti/*.json` içinden okunamayan (yarım yazılmış / kesilmiş) denetim
JSON'unu SESSİZCE atlıyor ve adım-1 UYGULANDI yazılıyordu (deneyle
doğrulandı: yarım JSON'da `_graf_kapisi_sorunu` None döndü — fail-open).
Tüketici tarafı (okunamadı → görünür uyarı) Görev 1'in işi; üretici tarafı
bu dosyanın kilitlediği şeydir: dört motor (vakia_matris · grafik_denetim ·
kiyas_denetim · antitez_matris) ve grafik_denetim'in `denetim_coktu` çökme
kaydı denetim JSON'unu `open(yol, "w")` ile DOĞRUDAN hedefe YAZMAZ; aynı
dizinde geçici dosyaya yazar ve `os.replace` ile hedefe taşır (aynı birim →
atomik yeniden adlandırma; CLAUDE.md "Atomik replace" sınıfı). Böylece
hedef dosya HİÇBİR anda yarım hâlde görünmez: ya eski tam içerik, ya yeni
tam içerik. Yazım yarıda kesilirse (serileştirme hatası, disk dolu…) eski
dosya olduğu gibi kalır ve geçici dosya artığı bırakılmaz.

Yöntem: motorlar in-process yüklenir (tests/README.md §1 — benzersiz modül
adı); `os.replace` KAYDEDİCİ bir sarmalla izlenir (asıl işlevi yine koşar —
sahte değil, gözlemci). Kesinti senaryosu gerçek bir serileştirme hatasıyla
(JSON'a çevrilemeyen nesne) üretilir, mock yok.
Bütün veriler kurgudur (anayasa m.7).
"""
import importlib.util
import inspect
import json
import os
import pathlib
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
MOTORLAR = {
    "vakia": SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py",
    "illiyet": SKILLS / "oa-illiyet" / "scripts" / "grafik_denetim.py",
    "kiyas": SKILLS / "oa-kiyas" / "scripts" / "kiyas_denetim.py",
    "antitez": SKILLS / "oa-antitez" / "scripts" / "antitez_matris.py",
}
ARAC = {"vakia": "vakia_matris", "illiyet": "grafik_denetim",
        "kiyas": "kiyas_denetim", "antitez": "antitez_matris"}


def _modul(etiket):
    yol = MOTORLAR[etiket]
    spec = importlib.util.spec_from_file_location(f"v0518_uretici_atomik_{etiket}", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _yaz(yol, nesne):
    yol.write_text(json.dumps(nesne, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(yol)


GRAF = {
    "dugumler": [{"id": "FIIL", "tip": "olay", "ad": "Fiil (kurgu)"},
                 {"id": "ZARAR", "tip": "olay", "ad": "Zarar (kurgu)"}],
    "kenarlar": [{"kaynak": "FIIL", "hedef": "ZARAR", "kategori": "illiyet",
                  "tur": "sebep_zarar", "illiyet_tipi": "uygun", "guc": "guclu",
                  "dogrulama": "teyitli", "dayanak_delil": ["D1"], "norm": "çıpa (kurgu)"}],
}
VAKIA = {"iddialar": [{"id": "I1", "metin": "Kurgu iddia", "tur": "vakia"}],
         "olaylar": [{"tarih": "2025-01-10", "olgu": "Kurgu olay", "belge": "Kurgu belge",
                      "destekler": ["I1"], "ispat_durumu": "belgeli"}]}
KIYAS = {"buyuk_onerme": {"norm": "TBK m.49 (kurgu)", "ictihat": [], "unsurlar": [{"id": "fiil", "ad": "Fiil"}]},
         "kucuk_onerme": {"vakialar": [{"metin": "Kurgu vakıa", "karsilar": ["fiil"], "dayanak_delil": ["x"]}]},
         "sonuc": "Kurgu sonuç."}
ANTITEZ = {"tez": "Kurgu tez", "cepheler": [{"cephe": "usul", "guc": "yok"}]}


def _motoru_calistir(etiket, mod, dizin, hedef):
    """Her motorun kendi --json yazım yolunu in-process tetikler."""
    if etiket == "vakia":
        mod.dogrula(_yaz(dizin / "vakia.json", VAKIA), json_yol=str(hedef))
    elif etiket == "illiyet":
        assert mod.rapor(_yaz(dizin / "graf.json", GRAF), json_yol=str(hedef)) == 0
    elif etiket == "kiyas":
        mod.main(_yaz(dizin / "kiyas.json", KIYAS), json_yol=str(hedef))
    elif etiket == "antitez":
        mod.dogrula(_yaz(dizin / "antitez.json", ANTITEZ), json_yol=str(hedef))
    elif etiket == "illiyet-coktu":
        # dosya YOK → DENETİM ÇÖKTÜ (exit 2) — çökme kaydı da atomik yazılır
        assert mod.rapor(str(dizin / "yok.json"), json_yol=str(hedef)) == 2
    else:
        raise AssertionError(etiket)


@pytest.fixture
def replace_kaydi(monkeypatch):
    """`os.replace` gözlemcisi: (kaynak, hedef, kaynak_vardi) kaydeder, asıl
    işlevi aynen koşturur."""
    cagrilar = []
    orijinal = os.replace

    def _sarmal(src, dst, *a, **kw):
        cagrilar.append((os.path.abspath(src), os.path.abspath(dst), os.path.exists(src)))
        return orijinal(src, dst, *a, **kw)

    monkeypatch.setattr(os, "replace", _sarmal)
    return cagrilar


@pytest.mark.parametrize("etiket", ["vakia", "illiyet", "kiyas", "antitez", "illiyet-coktu"])
def test_json_yazimi_atomik_tmp_os_replace(tmp_path, replace_kaydi, etiket):
    """Dört motorun `--json` yazımı + grafik_denetim çökme kaydı: hedef dosya
    AYNI DİZİNDEKİ bir geçici dosyadan `os.replace` ile oluşur; geçici dosya
    geride kalmaz; hedef geçerli ve damgalı JSON'dur."""
    mod = _modul(etiket.split("-")[0])
    hedef = tmp_path / "denetim.json"
    _motoru_calistir(etiket, mod, tmp_path, hedef)

    hedefe = [c for c in replace_kaydi if c[1] == os.path.abspath(hedef)]
    assert len(hedefe) == 1, f"hedefe tam BİR os.replace bekleniyor; kayıt: {replace_kaydi}"
    src, dst, vardi = hedefe[0]
    assert vardi, "geçici dosya replace anında diskte olmalı (önce yaz, sonra taşı)"
    assert src != dst
    assert os.path.dirname(src) == os.path.dirname(dst), "geçici dosya hedefle AYNI dizinde (aynı birim → atomik)"
    assert not os.path.exists(src), "geçici dosya artığı kaldı"
    d = json.loads(hedef.read_text(encoding="utf-8"))
    assert d["arac"] == ARAC[etiket.split("-")[0]]
    girdi_dosyasi = {"vakia": {"vakia.json"}, "illiyet": {"graf.json"}, "kiyas": {"kiyas.json"},
                     "antitez": {"antitez.json"}, "illiyet-coktu": set()}[etiket]
    assert {p.name for p in tmp_path.iterdir()} == {"denetim.json"} | girdi_dosyasi, \
        "dizinde girdi + hedef dışında dosya (geçici artık) kalmamalı"


@pytest.mark.parametrize("etiket", ["vakia", "illiyet", "kiyas", "antitez"])
def test_json_yazimi_yarida_kesilirse_eski_dosya_korunur_ve_gecici_kalmaz(tmp_path, etiket):
    """Kesinti senaryosu (gerçek serileştirme hatası — mock yok): hedefte eski
    tam JSON varken yazım yarıda kesilirse eski içerik BAYT BAYT korunur ve
    dizinde geçici dosya artığı kalmaz. Doğrudan `open(yol, "w")` bu testi
    geçemez: hedefi önce sıfırlar, sonra çöker — yarım dosya kalır."""
    mod = _modul(etiket)
    hedef = tmp_path / "denetim.json"
    eski = '{"arac": "eski", "saglikli": true}'
    hedef.write_text(eski, encoding="utf-8")

    with pytest.raises(TypeError):
        mod._atomik_json_yaz(str(hedef), {"arac": "yeni", "bozuk": object()})

    assert hedef.read_text(encoding="utf-8") == eski
    assert sorted(p.name for p in tmp_path.iterdir()) == ["denetim.json"]


@pytest.mark.parametrize("etiket", ["vakia", "illiyet", "kiyas", "antitez"])
def test_atomik_yazim_sort_keys_ve_utf8(tmp_path, etiket):
    """Yardımcı, dört motorun bugüne kadar kullandığı biçimi aynen üretir:
    ensure_ascii=False (Türkçe karakter ham), indent=2, sort_keys=True —
    determinizm süiti bayt-özdeşliği buna dayanır."""
    mod = _modul(etiket)
    hedef = tmp_path / "s.json"
    mod._atomik_json_yaz(str(hedef), {"z": 1, "a": "şğü"})
    assert hedef.read_text(encoding="utf-8") == '{\n  "a": "şğü",\n  "z": 1\n}'


# ── K-4 (inceleme, düzeltme turu 1): Windows'ta kilitli hedef ───────────────
# Hedef JSON başka bir süreçte açıkken (okuyucu, Defender taraması) `os.replace`
# `PermissionError` verir; eski `open(yol, "w")` bu durumda yazabiliyordu.
# Sözleşme: PermissionError'da 3 KISA yeniden deneme (toplam < 300 ms), sonra
# istisna AYNEN yeniden fırlatılır; geçici dosya temizliği her iki yolda korunur.

def _kilitli_replace(monkeypatch, basarisiz_deneme):
    """İlk `basarisiz_deneme` çağrıda PermissionError, sonra asıl os.replace.
    `None` → hep PermissionError (kalıcı kilit). `time.sleep` kaydedilir, uyunmaz."""
    orijinal = os.replace
    kayit = {"deneme": 0, "bekleme": []}

    def _sahte(src, dst, *a, **kw):
        kayit["deneme"] += 1
        if basarisiz_deneme is None or kayit["deneme"] <= basarisiz_deneme:
            raise PermissionError(13, "başka süreç tarafından kullanılıyor (sahte Windows kilidi)")
        return orijinal(src, dst, *a, **kw)

    monkeypatch.setattr(os, "replace", _sahte)
    monkeypatch.setattr(time, "sleep", lambda s: kayit["bekleme"].append(s))
    return kayit


@pytest.mark.parametrize("etiket", ["vakia", "illiyet", "kiyas", "antitez"])
def test_os_replace_permission_error_kisa_yeniden_deneme_ile_asilir(tmp_path, monkeypatch, etiket):
    """İlk iki denemede PermissionError, üçüncüde başarı → dosya yazılır,
    bekleme toplamı 300 ms altında, geçici artık yok."""
    mod = _modul(etiket)
    kayit = _kilitli_replace(monkeypatch, basarisiz_deneme=2)
    hedef = tmp_path / "s.json"
    mod._atomik_json_yaz(str(hedef), {"a": 1})

    assert kayit["deneme"] == 3
    assert json.loads(hedef.read_text(encoding="utf-8")) == {"a": 1}
    assert len(kayit["bekleme"]) == 2 and 0 < sum(kayit["bekleme"]) < 0.3
    assert {p.name for p in tmp_path.iterdir()} == {"s.json"}


@pytest.mark.parametrize("etiket", ["vakia", "illiyet", "kiyas", "antitez"])
def test_os_replace_kalici_permission_error_yeniden_firlatilir_eski_dosya_korunur(tmp_path, monkeypatch, etiket):
    """Kilit kalkmazsa: 1 + 3 yeniden deneme (toplam bekleme < 300 ms), sonra
    PermissionError AYNEN fırlar (fail-closed); eski hedef bayt bayt durur,
    geçici dosya silinir."""
    mod = _modul(etiket)
    kayit = _kilitli_replace(monkeypatch, basarisiz_deneme=None)
    hedef = tmp_path / "s.json"
    eski = '{"arac": "eski"}'
    hedef.write_text(eski, encoding="utf-8")

    with pytest.raises(PermissionError):
        mod._atomik_json_yaz(str(hedef), {"a": 1})

    assert kayit["deneme"] == 4
    assert sum(kayit["bekleme"]) < 0.3
    assert hedef.read_text(encoding="utf-8") == eski
    assert {p.name for p in tmp_path.iterdir()} == {"s.json"}


# ── K-5 (inceleme, düzeltme turu 1): kaynak-metin sürüklenme kilidi ─────────

def test_ortak_yardimcilar_dort_modulde_kaynak_metin_ozdes():
    """Dört kopya yardımcı (paket yok, ortak modül brief'çe yasak) sessizce
    ayrışabilir: biri `[:8]`i değiştirir ya da `OA_DISI_NOTU` farklılaşır →
    tazelik tüketicisi bir motoru yanlış etiketler. Davranış testleri ana yolu
    kilitler; bu test METNİ kilitler: `inspect.getsource` üç fonksiyonda ve iki
    sabit dört modülde bayt bayt eşit olmalı."""
    modlar = {e: _modul(e) for e in ("vakia", "illiyet", "kiyas", "antitez")}
    for ad in ("kaynak_beyani", "_atomik_json_yaz", "_oa_dizini_bul"):
        kaynaklar = {e: inspect.getsource(getattr(m, ad)) for e, m in modlar.items()}
        farkli = {e for e, k in kaynaklar.items() if k != kaynaklar["vakia"]}
        assert not farkli, f"`{ad}` kaynak metni ayrıştı — vakia ≠ {sorted(farkli)}"
    for sabit in ("OA_DISI_NOTU", "KUNYE_GORELI"):
        degerler = {getattr(m, sabit) for m in modlar.values()}
        assert len(degerler) == 1, (sabit, degerler)
