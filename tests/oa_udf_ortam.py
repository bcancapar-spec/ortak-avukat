# -*- coding: utf-8 -*-
"""GERÇEK UDF yazıcısı BU ORTAMDA kullanılabilir mi? (test altyapısı)

NEDEN VAR (CI bulgusu, 2026-08-06):
  v0.5.5.1'de UDF hattı bilinçli olarak `npx udf-cli html2udf` TEK YOLUNA
  kilitlendi ve `--yerel-motor` KALDIRILDI (B5 saha bulgusu: o motorun
  ürettiği .udf UYAP'ta açılmıyordu). `udf_yaz.py` artık FAIL-CLOSED'dur:
  ağ + oturum yoksa HİÇBİR .udf yazmaz ve exit 1 döner. Bu DOĞRU davranıştır.

  Sonucu şu oldu: GitHub Actions koşucularında `npx` VAR ama `udf-cli`
  OTURUMU YOK. Zinciri sonuna kadar koşturan 15 test bu yüzden v0.5.5.1'den
  beri CI'da KIRMIZI kaldı — kod hatası değil, ORTAM eksikliği. On bir koşu
  boyunca `aile_dogrula` adımı da hiç çalışamadı (pytest önce patlıyordu) ve
  "release kapısı" fiilen ortadan kalktı. Sürekli kırmızı bir kapı, olmayan
  kapıdır.

ÇÖZÜM — İKİ KATMAN, "hepsini sustur" DEĞİL:
  (A) Zincir MANTIĞINI test edenler (kapı sırası, makbuz şeması, sha bağı,
      dairesel bağımlılık): `udf_arglari` fixture'ı ile koşar. Yazıcı VARSA
      fixture BOŞ liste döner — yani avukatın kendi makinesinde testler
      bugünkünün AYNISI, TAM zinciri koşar. Yazıcı YOKSA `--udf-yok` geçer;
      bu bayrak uydurma değildir, teslim_paketi.py'de zaten vardır ve
      makbuza `udf_atlandi_istekle: true` diye YAZILIR.
  (B) GERÇEK bir .udf üretildiğini İDDİA edenler: `gercek_udf_yazici_gerekli`
      ile işaretlenir; yazıcı yoksa GÖRÜNÜR gerekçeyle atlanır.

TEK KAYNAK (ikiz-liste yasağı):
  Yoklamanın kendisi burada YENİDEN YAZILMAZ. Yetkili merci üretim kodudur:
  `oa-dilekce/scripts/udf_yaz.py :: npx_kullanilabilir_mi()`. Bu modül onu
  çağırır ve sonucu OTURUM BOYUNCA ÖNBELLEKLER. (Önceden aynı soru
  test_udf_yaz.py'de 5, test_udf_metin.py'de 1 kez SORULUYORDU — her biri
  ayrı bir `npx ... whoami` ağ çağrısı. Artık koşu başına TEK çağrı.)

DİSİPLİN NOTU (sessiz atlama DEĞİL):
  - Atlama gerekçesi yazılıdır ve her koşuda başlık satırında BASILIR.
  - Oturum GERÇEKTEN sınanır (jeton dosyasına bakıp tahmin edilmez); süresi
    dolmuş bir oturum "var" sayılmaz.
  - Atlanan tek durum "bu ortamda o kapı fiziken denenemez" durumudur —
    anayasa m.8'in "fiziken yüklenemedi diye açıkça yazılır" kuralının test
    karşılığı.
  - Bu modül YALNIZ testleri etkiler. Eklentinin çalışma zamanı kodunda
    hiçbir kapıyı gevşetmez, hiçbir bypass açmaz.

YEŞİL CI NE DEMEK: "yapı ve zincir mantığı sağlam" — "UDF hattı çalışıyor"
DEĞİL. UDF hattı yalnız avukatın kendi makinesinde ve sahada doğrulanır.
"""
import functools
import importlib.util
import os
import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
UDF_YAZ = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
           / "scripts" / "udf_yaz.py")

# Test-ONLY override. Yalnız bu yoklamayı zorlar; eklenti kodunu ETKİLEMEZ.
# CI'ı yerelde taklit etmek için kullanılır (avukatın gerçek oturumuna
# DOKUNMADAN): OA_TEST_UDF_YAZICI=0 python -m pytest ...
ZORLA_DEGISKENI = "OA_TEST_UDF_YAZICI"

_EVET = ("1", "var", "true", "evet")
_HAYIR = ("0", "yok", "false", "hayir", "hayır")


@functools.lru_cache(maxsize=1)
def _udf_yaz_modulu():
    """udf_yaz.py'yi dosya yolundan yükler (skill dizinleri paket değildir)."""
    spec = importlib.util.spec_from_file_location("_oa_ortam_udf_yaz", UDF_YAZ)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_oa_ortam_udf_yaz"] = mod
    spec.loader.exec_module(mod)
    return mod


@functools.lru_cache(maxsize=1)
def _yoklama():
    """(uygun mu, açıklama) — koşu başına TEK kez sorulur."""
    zorla = os.environ.get(ZORLA_DEGISKENI, "").strip().lower()
    if zorla in _HAYIR:
        return False, "%s ile kapatildi" % ZORLA_DEGISKENI
    if zorla in _EVET:
        return True, "%s ile acildi" % ZORLA_DEGISKENI
    # Ucuz kısa devre: npx yoksa ağa hiç çıkma.
    if not shutil.which("npx"):
        return False, "npx bulunamadi (Node.js kurulu olmayabilir)"
    try:
        return _udf_yaz_modulu().npx_kullanilabilir_mi()
    except Exception as e:  # üretim yoklaması yüklenemedi/patladı
        return False, "yoklama calistirilamadi: %s" % e


def gercek_udf_yazici_var():
    """`npx udf-cli html2udf` bu ortamda FİİLEN kullanılabilir mi?"""
    return _yoklama()[0]


def durum_metni():
    """Her koşuda başlıkta basılan GÖRÜNÜR durum satırı."""
    uygun, aciklama = _yoklama()
    if uygun:
        return ("oa | GERCEK UDF yazicisi: VAR -- teslim zinciri TAM kosuyor, "
                "UDF testleri atlanmiyor.")
    return ("oa | GERCEK UDF yazicisi: YOK (%s) -- zincir testleri '--udf-yok' "
            "kipinde kosar; GERCEK .udf uretimini iddia eden testler ATLANIR. "
            "KAPSAM EKSIKTIR: bu ortamda yesil CI 'yapi + zincir mantigi saglam' "
            "demektir, 'UDF hatti calisiyor' DEMEZ. Acmak icin: "
            "npx -y udf-cli@latest login" % aciklama)


# (B) grubu için işaret — GERÇEK .udf artefaktı iddia eden testler.
gercek_udf_yazici_gerekli = pytest.mark.skipif(
    not gercek_udf_yazici_var(),
    reason=("GERCEK UDF yazicisi/oturumu yok (`npx -y udf-cli@latest login`). "
            "udf_yaz.py FAIL-CLOSED oldugu icin bu testin iddia ettigi .udf "
            "artefakti bu ortamda URETILEMEZ. Kod hatasi degil, ortam "
            "eksikligi -- bkz. tests/oa_udf_ortam.py"),
)
