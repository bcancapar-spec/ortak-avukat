# -*- coding: utf-8 -*-
"""2026-10-15 avukat kararı (hibrit teyit kanalı) — test yardımcısı.

NEDEN VAR: `oa_hafiza.py teyit` tam metin çeken araçlarda (GETİR sınıfı + `mevzuat_getir` /
`resmi_gazete_getir`) `--kaynak-url` ister ve adresi resmî kaynak beyaz listesiyle
karşılaştırır; `ictihat_muhakeme_denetim.py` [G7] dilekçeye dayanak olan kaydın adresi yoksa
teslim engeli sayar (kapıların kendisi: tests/test_teyit_kanali.py). Kanal değişmeden önce
yazılmış testler o kapıyı değil damga / döküm / akıbet / enjeksiyon disiplinini sınar;
sınadıkları kapıya ulaşabilmeleri için GETİR sınıfı çağrılara beyaz listeli SENTETİK bir adres,
elle yazılmış muhakeme kayıtlarına `**KAYNAK-URL:**` satırı buradan eklenir. Adres sentetiktir,
hiçbir adrese gidilmez (ağsız); üçüncü taraf ad ya da adres taşımaz.
"""
import re

RESMI_URL = "https://karararama.yargitay.gov.tr/karar/sentetik-1"
KAYNAK_URL_SATIRI = "**KAYNAK-URL:** " + RESMI_URL
# oa_hafiza.URL_ZORUNLU_ARACLAR ile aynı küme (casefold); E3 normalize toleransı burada da uygulanır.
URL_ZORUNLU = {"ictihat_getir", "kurum_karari_getir", "webfetch", "mevzuat_getir",
               "resmi_gazete_getir"}
_PARANTEZ_EK = re.compile(r"\s*\([^)]*\)\s*$")


def kaynak_url_ekle(args):
    """`teyit` çağrısı tam metin çeken bir araçla yapılıyorsa ve `--kaynak-url` verilmemişse
    beyaz listeli sentetik adresi ekler; başka her çağrıyı olduğu gibi (dize listesi) döndürür."""
    args = [str(a) for a in args]
    if not args or args[0] != "teyit" or "--kaynak-url" in args or "--arac" not in args:
        return args
    try:
        arac = args[args.index("--arac") + 1]
    except IndexError:
        return args
    kanonik = _PARANTEZ_EK.sub("", arac).strip().casefold().replace(" ", "_")
    if kanonik in URL_ZORUNLU:
        args += ["--kaynak-url", RESMI_URL]
    return args
