# -*- coding: utf-8 -*-
"""Halüsinasyon motoru damga fikstürü (v0.5.18 saha testi — Fable teşhisi).

NEDEN VAR: v0.5.18 saha testinde vakıa, illiyet, antitez ve kıyas motorları kurulu
olduğu hâlde HİÇ koşmadı; kapılar "çıktı var mı" diye soruyordu, "motor koştu mu"
diye değil. Yeni sözleşmede `oa-vakia / oa-illiyet / oa-antitez / oa-kiyas`
UYGULANDI yazımı, adım-8 (oa-dilekce) ve teslim (c2) kapısı motorun KENDİ yazdığı
`arac` damgalı denetim JSON'unu ister. Zincirin BAŞKA bir halkasını sınayan eski
testler motorları gerçekten koşturmak zorunda değildir; motorların koştuğu dünyayı
bu fikstürle tek satırda kurar. Motorların GERÇEKTEN koştuğu yol
`tests/test_v0518_halusinasyon_kapisi.py` içindeki köprü testlerindedir.

DAMGALAR listesi `pipeline_kayit._MOTOR_DAMGALARI` ile aynı olmak ZORUNDADIR —
ayrışma `test_motor_damga_fikstur_listesi_uretimle_ayni` ile kırmızı yanar.
"""
import json
import pathlib

DAMGALAR = ("antitez_matris", "grafik_denetim", "kiyas_denetim", "vakia_matris")

# Belgelenmiş çıktı adları (SKILL.md'ler); kapı ad-bağımsızdır, ad yalnız okunurluk içindir.
_ADLAR = {
    "grafik_denetim": "01-illiyet-denetim.json",
    "vakia_matris": "04-vakia-denetim.json",
    "kiyas_denetim": "05-kiyas-denetim.json",
    "antitez_matris": "06-antitez-denetim.json",
}


def damga_yaz(kok, damga, **ek):
    """`<kok>/_oa/cikti/` altına `arac=<damga>` damgalı asgari denetim JSON'u yazar."""
    cikti = pathlib.Path(kok) / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    yol = cikti / _ADLAR.get(damga, "%s-denetim.json" % damga)
    veri = {"arac": damga}
    veri.update(ek)
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def dort_damga(kok, haric=()):
    """Dört motorun damgalı denetim çıktısını kurar (`haric` dışındakiler)."""
    return [damga_yaz(kok, d) for d in DAMGALAR if d not in haric]
