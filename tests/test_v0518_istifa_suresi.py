# -*- coding: utf-8 -*-
"""v0.5.18 — K1 (CANLI KUSUR): istifada vekâletin devam süresi, yaz aylarında müvekkile
GEÇ tarih veriyordu (oa-sure + oa-interview MK-2).

Kusur (Aşama 4 / T5-1, ana oturum teyidi 2026-10-07): `meslek-kurallari-kontrol.md`
MK-2/3'teki çağrı (`hesapla_sure.py --teblig … --sure 2 --birim hafta` / `--sure 15
--birim gun`, `--kural` YOK) rejimi `--yargi hukuk` varsayılanından alıyor → "HMK m.104,
teyitli" → tebliğ 2026-07-25'te ham bitiş 2026-08-08 / 2026-08-09 iken iki satırın da
manşeti 2026-09-07. Belgenin kendi ilkesi ("belirsizlikte erken tarih esas alınır";
müvekkile uyarı ERKEN tarihle) bu çağrıyla karşılanamıyordu: müvekkil 4 hafta
temsilsiz kalma riskiyle (HMK m.82/2 — tarafın yokluğu hükümleri) GEÇ tarihe güvenirdi.

Çözüm: iki ayrı kural, `hmk_tedbir_esas_dava` kalıbında — rejim "uygulanmaz",
teyitli=False, geç okuma (31 Ağu + 1 hafta) YALNIZ uyarı/alternatif satırında.
  * `hmk_istifa_vekalet_devam` — HMK m.82/1: iki hafta, müvekkile TEBLİĞDEN.
  * `avk_istifa_vekalet_devam` — Av.K. m.41/1: on beş gün, müvekkile TEBLİĞDEN.

Resmî metin teyidi (Yargı PRO MCP `mevzuat_getir`, 2026-10-07):
  HMK (6100) m.82 ("istifa eden vekilin vekâlet görevi, istifanın müvekkiline
  tebliğinden itibaren iki hafta süreyle devam eder"), m.103/3 ("Adli tatilde …
  her türlü tebligat … işlemleri de yapılır" → süre tatilde İŞLER), m.104 ("bu
  Kanunun tayin ettiği sürelerin bitmesi tatil zamanına rastlarsa … bir hafta");
  Av.K. (1136) m.41 ("isteği ile çekilen avukatın o işe ait vekâlet görevi, durumu
  müvekkiline tebliğinden itibaren onbeş gün süre ile devam eder").
İçtihat (ictihat_getir, tam metin, 2026-10-07): Y. 23. HD E.2013/8404 K.2013/7933
  — HMK m.104 "HMK dışındaki süreler bakımından uygulanmasının mümkün olmadığı"
  (İİK m.62 süresi için; Av.K. m.41'e uygulanması KIYASTIR). m.104'ün m.82/1'e
  uygulandığına ya da reddedildiğine dair karar BULUNAMADI → TEYİT BEKLİYOR.

Test vektörleri (brief, verbatim): tebliğ 2026-07-25 → hmk ham 2026-08-08, manşet
2026-08-10, geç okuma 2026-09-07; avk ham 2026-08-09, manşet 2026-08-10, geç okuma
2026-09-07. Tebliğ 2026-03-02 → hmk 2026-03-16, avk 2026-03-17. `--yargi idari` ile
manşet aynı. Testler ağsız ve deterministiktir; depoya yazmaz (--flagsiz / tmp_path).
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
SURE = SKILLS / "oa-sure"
SCRIPT = SURE / "scripts" / "hesapla_sure.py"
KURAL_JSON = SURE / "scripts" / "sure_kurallari.json"
SURE_SKILL_MD = SURE / "SKILL.md"
CIZELGE = SURE / "references" / "sure-cizelgesi.md"
SURE_GUNLUK = SURE / "references" / "degisiklik-gunlugu.md"
MK_REF = SKILLS / "oa-interview" / "references" / "meslek-kurallari-kontrol.md"
INTERVIEW_SKILL_MD = SKILLS / "oa-interview" / "SKILL.md"
INTERVIEW_GUNLUK = SKILLS / "oa-interview" / "references" / "degisiklik-gunlugu.md"

HMK = "hmk_istifa_vekalet_devam"
AVK = "avk_istifa_vekalet_devam"
IKI_KURAL = (HMK, AVK)

_SON_GUN_RE = re.compile(r"HESAPLANAN SON G[ÜU]N\s*:\s*(\d{4}-\d{2}-\d{2})")


def _yukle():
    spec = importlib.util.spec_from_file_location("v0518_istifa_hesapla_sure", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _yukle()


def _cli(*args):
    cp = subprocess.run([sys.executable, str(SCRIPT), *args, "--flagsiz"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(REPO), timeout=120)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _son(out):
    m = _SON_GUN_RE.search(out)
    assert m, "son gün satırı yok:\n" + out
    return m.group(1)


def _json_satiri(out):
    satir = next(s for s in out.splitlines() if s.startswith("[JSON] "))
    return json.loads(satir[len("[JSON] "):])


def _hesap(teblig, kural, yargi="hukuk", **kw):
    miktar, birim, _k = H.KURALLAR[kural]
    bilgi = {}
    son, rapor, uyarilar = H.hesapla(teblig, miktar, birim, yargi, "usul", kural=kural,
                                     _bilgi=bilgi, **kw)
    return son, "\n".join(rapor), uyarilar, bilgi


def _duz(s):
    return re.sub(r"\s+", " ", s)


def _bolum(txt, bas, son=None):
    i = txt.index(bas)
    j = txt.index(son, i) if son else len(txt)
    return _duz(txt[i:j])


# ══════════════════════════════════════════════════════════════════════════
# 1) Kural tabanı — JSON + gömülü ikiz, hmk_tedbir_esas_dava kalıbı
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("kural,miktar,birim,capa", [
    (HMK, 2, "hafta", "m.82/1"),
    (AVK, 15, "gun", "m.41"),
])
def test_istifa_kurali_json_ve_gomulu_tablolarda(kural, miktar, birim, capa):
    """İki süre EŞİTLENMEZ: HMK m.82/1 iki hafta, Av.K. m.41 on beş gün — ikisi de
    hem sure_kurallari.json'da hem gömülü ikizde (B-21 kilidi) ve yalnız TEBLİĞDEN."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    assert kural in j, "JSON'da yok: " + kural
    assert (j[kural]["miktar"], j[kural]["birim"]) == (miktar, birim)
    assert capa in j[kural]["kaynak"], j[kural]["kaynak"]
    assert j[kural].get("mcp_teyit_tarihi"), "teyitsiz kural eklenemez"
    assert j[kural]["izinli_baslangic_turleri"] == ["teblig"], "süre müvekkile TEBLİĞDEN işler"
    for tablo in (H._GOMULU_KURALLAR, H._GOMULU_TEYIT, H._GOMULU_BASLANGIC, H._GOMULU_REJIM):
        assert kural in tablo, "gömülü ikizde yok: " + kural
    assert H._GOMULU_KURALLAR[kural][:2] == (miktar, birim)
    assert H._GOMULU_KURALLAR[kural][2] == j[kural]["kaynak"], "kaynak metni ikizde farklı"
    assert H._GOMULU_TEYIT[kural] == j[kural]["mcp_teyit_tarihi"]
    assert H._GOMULU_BASLANGIC[kural] == ["teblig"]
    assert kural in H.KURALLAR and H.KURALLAR[kural][:2] == (miktar, birim)


@pytest.mark.parametrize("kural", IKI_KURAL)
def test_istifa_rejimi_uygulanmaz_teyitsiz_hmk_tedbir_kalibinda(kural):
    """`hmk_tedbir_esas_dava` kalıbı: adli_tatil 'uygulanmaz', adli_tatil_teyitli False
    (karar bulunamadı → TEYİT BEKLİYOR), son gün kayması var; dayanak sürenin tatilde
    İŞLEDİĞİNİ (HMK m.103/3) ve geç okumanın yalnız karşılaştırma olduğunu söyler.
    JSON ↔ gömülü rejim alanları birebir."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"][kural]
    r = H.KURAL_REJIM[kural]
    assert r["adli_tatil"] == "uygulanmaz"
    assert r["adli_tatil_teyitli"] is False
    assert r["son_gun_kaymasi"] is True
    assert r.get("turetildi") == "", "rejim JSON'dan okunmalı, türetilmemeli"
    d = r["adli_tatil_dayanak"]
    assert "TEYİT BEKLİYOR" in d and "m.103/3" in d and "m.104" in d, d
    assert "erken tarih" in d.lower(), d
    g = H._GOMULU_REJIM[kural]
    for alan in ("adli_tatil", "adli_tatil_dayanak", "adli_tatil_teyitli", "son_gun_kaymasi"):
        assert g[alan] == j[alan], "ikiz rejim alanı ayrıştı: %s.%s" % (kural, alan)


def test_avk_dayanagi_23HD_kiyasini_ve_hmk_dayanagi_m82_m104_iliskisini_soyler():
    """Av.K. m.41 HMK süresi DEĞİLDİR: HMK m.104 yalnız 'bu Kanunun tayin ettiği
    sürelere' (Y. 23. HD E.2013/8404 K.2013/7933 — İİK m.62 için; m.41'e KIYAS).
    HMK m.82/1 HMK süresidir: m.104 lafzen uygulanabilir görünür ama karar yok."""
    avk = H.KURAL_REJIM[AVK]["adli_tatil_dayanak"]
    assert "2013/8404" in avk and "2013/7933" in avk and "23. HD" in avk, avk
    assert "kıyas" in avk.lower(), "23. HD kararı İİK süresine ilişkindir — m.41'e uygulanması kıyastır"
    # KÜÇÜK-3: Av.K. süresi HMK süresi değilken Pazar→Pazartesi kayması HMK m.93 ile yapılır —
    # dayanak bunun KIYASEN olduğunu söylemeli (iç tutarsızlık görünür olmasın diye değil, doğru olsun diye)
    assert "kıyasen (HMK m.93)" in avk, avk
    hmk = H.KURAL_REJIM[HMK]["adli_tatil_dayanak"]
    assert "m.82/1" in hmk and "m.104" in hmk, hmk
    assert "bulunamadı" in hmk, "m.104'ün m.82/1'e uygulanması kararla teyit edilemedi — bu yazılmalı"


def test_avk_oneki_onek_tablolarinda_ve_kol_bagimsiz():
    """'avk' öneki KURAL_KOLU'da (kol-bağımsız: Av.K. her yargı kolunda — m.41
    'takipten veya savunmadan') ve _ONEK_REJIM'de ('uygulanmaz' — HMK süresi değil)."""
    assert "avk" in H.KURAL_KOLU and H.KURAL_KOLU["avk"] is None
    assert H._ONEK_REJIM.get("avk") == "uygulanmaz"
    assert H.kural_kolu(AVK) is None
    assert H.kural_kolu(HMK) == "hukuk"
    # kol-bağımsız kural ceza kolunda da hesaplanır; HMK kuralı ceza koluyla DURUR (A-1)
    assert H.kol_uyusmazligi(AVK, "ceza") is None
    assert H.kol_uyusmazligi(HMK, "ceza") is not None


# ══════════════════════════════════════════════════════════════════════════
# 2) Motor — yaz vektörü: manşet ERKEN, geç okuma yalnız uyarıda
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("kural,ham", [(HMK, "2026-08-08"), (AVK, "2026-08-09")])
def test_yaz_istifasi_manset_ERKEN_tarih_gec_okuma_yalniz_uyarida(kural, ham):
    """Tebliğ 2026-07-25 (Cumartesi): ham bitiş tatil içinde (08.08 / 09.08) →
    uzatma UYGULANMAZ, yalnız hafta sonu kayması → manşet 2026-08-10. Eski çağrı
    2026-09-07 veriyordu; o tarih artık YALNIZ alternatif/uyarı satırındadır."""
    son, rapor, uyarilar, bilgi = _hesap(date(2026, 7, 25), kural)
    assert son == date(2026, 8, 10), son
    assert re.search(r"Ham bitiş\s*:\s*%s" % ham, rapor), rapor
    assert "UZATMA UYGULANMAZ" in rapor, rapor
    assert "Adli tatil (HMK m.104)" not in rapor, "manşet m.104 ile uzatıldı — kusur geri geldi"
    assert "2026-09-07" not in rapor.split(">>> HESAPLANAN SON GÜN")[1].splitlines()[0]
    assert bilgi["alt_son"] == date(2026, 9, 7), bilgi
    assert bilgi["rejim"] == "uygulanmaz" and bilgi["rejim_teyitli"] is False
    assert bilgi["plan_son"] == date(2026, 8, 10)
    temkinli = [u for u in uyarilar if "TEMKİNLİ" in u]
    assert temkinli and "2026-09-07" in temkinli[0] and "2026-08-10" in temkinli[0], uyarilar


@pytest.mark.parametrize("kural,beklenen", [(HMK, date(2026, 3, 16)), (AVK, date(2026, 3, 17))])
def test_kis_istifasi_vektorleri_iki_okuma_birlesir(kural, beklenen):
    """Tebliğ 2026-03-02 (Pazartesi): tatil dışı → hmk 16.03, avk 17.03; geç okuma
    doğmaz (alternatif yok), TEMKİNLİ uyarısı basılmaz."""
    son, _rapor, uyarilar, bilgi = _hesap(date(2026, 3, 2), kural)
    assert son == beklenen
    assert bilgi["alt_son"] is None
    assert not any("TEMKİNLİ" in u for u in uyarilar), uyarilar


@pytest.mark.parametrize("kural", IKI_KURAL)
def test_istifa_uyarisi_iki_muhatap_muvekkile_erken_avukata_gec(kural):
    """Kurala özgü uyarı: müvekkile 'yeni vekil bu tarihten ÖNCE' uyarısı manşetteki
    ERKEN tarihle; istifa eden avukat takibi GEÇ okumaya kadar sürdürür; HMK m.82/2
    riski ve m.82/3 ihtaren bildirim; tebliğ belgeli (mahkemeye dilekçe ≠ tebliğ)."""
    _son, _rapor, uyarilar, _b = _hesap(date(2026, 7, 25), kural)
    istifa = [u for u in uyarilar if u.startswith("İSTİFA")]
    assert istifa, uyarilar
    u = istifa[0]
    for k in ("MÜVEKKİL", "ERKEN", "2026-08-10", "2026-09-07", "m.82/2", "m.82/3",
              "ihtaren", "EŞİTLENMEZ", "BELGELİ"):
        assert k in u, (k, u)
    assert u.index("2026-08-10") < u.index("2026-09-07"), "erken tarih önce, geç okuma sonra"


@pytest.mark.parametrize("kural", IKI_KURAL)
def test_istifa_uyarisi_tatil_disinda_gec_okumasiz_yazilir(kural):
    _son, _rapor, uyarilar, _b = _hesap(date(2026, 3, 2), kural)
    istifa = [u for u in uyarilar if u.startswith("İSTİFA")]
    assert istifa and "2026-09-07" not in istifa[0], istifa


@pytest.mark.parametrize("kural", IKI_KURAL)
def test_istifa_kurallarinda_kol_ozel_gurultu_yok(kural):
    """İstifa süresi kol-bağımsız bir görev-DEVAM süresidir: ceza/idari koluna özgü kanun
    yolu uyarıları (CMK m.272/286, İYUK m.20/A-B) ilgisizdir — iki kuralda da basılmaz
    (KÜÇÜK-1: dışlama yalnız 'avk' önekine değil kural adına da bakar)."""
    for yargi, kalip in (("ceza", "CEZA KANUN YOLU KAPILARI"), ("idari", "ÖZEL YARGILAMA USULÜ")):
        _son, _rapor, uyarilar, _b = _hesap(date(2026, 3, 2), kural, yargi=yargi)
        assert not any(kalip in u for u in uyarilar), (kural, yargi, uyarilar)


@pytest.mark.parametrize("kural", IKI_KURAL)
def test_istifa_gec_okuma_etiketi_yargi_koluna_gore_tarih_sabit(kural):
    """KÜÇÜK-2: İSTİFA uyarısındaki geç okuma etiketi sabit 'HMK m.104' değil, kullanılan
    alternatif rejimin REJIM_ETIKET'inden türer; idari kolda İYUK m.8/3 (1 Eylül'den 7 gün).
    Tarih değişmez: iki okuma da 2026-09-07."""
    _s, _r, uy_h, b_h = _hesap(date(2026, 7, 25), kural, yargi="hukuk")
    _s, _r, uy_i, b_i = _hesap(date(2026, 7, 25), kural, yargi="idari")
    ist_h = next(u for u in uy_h if u.startswith("İSTİFA"))
    ist_i = next(u for u in uy_i if u.startswith("İSTİFA"))
    assert H.REJIM_ETIKET["hmk104"] + " uygulanırsa" in ist_h, ist_h
    assert H.REJIM_ETIKET["iyuk8"] + " uygulanırsa" in ist_i, ist_i
    assert b_h["alt_son"] == b_i["alt_son"] == date(2026, 9, 7)


# ══════════════════════════════════════════════════════════════════════════
# 3) CLI — --yargi idari ile de manşet aynı; JSON; kesin dil kapısı
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("kural", IKI_KURAL)
@pytest.mark.parametrize("yargi", ["hukuk", "idari"])
def test_cli_yaz_vektoru_manset_ve_json_yargi_kolundan_bagimsiz(kural, yargi):
    rc, out = _cli("--teblig", "2026-07-25", "--kural", kural, "--yargi", yargi, "--json")
    assert rc == 0, out
    assert _son(out) == "2026-08-10"
    assert "TEYİT BEKLİYOR (temkinli: erken tarih)" in out and "kaynak: kural kaydı" in out, out
    js = _json_satiri(out)
    assert js["son_gun"] == "2026-08-10"
    assert js["alternatif_son_gun"] == "2026-09-07"
    assert js["plan_son_gun"] == "2026-08-10"
    assert js["adli_tatil_rejimi"] == "uygulanmaz" and js["rejim_teyitli"] is False


def test_cli_kis_vektoru_hmk_16_avk_17():
    rc, out = _cli("--teblig", "2026-03-02", "--kural", HMK)
    assert rc == 0 and _son(out) == "2026-03-16", out
    rc, out = _cli("--teblig", "2026-03-02", "--kural", AVK)
    assert rc == 0 and _son(out) == "2026-03-17", out


def test_cli_avk_ceza_kolunda_da_hesaplanir_hmk_kurali_durur():
    rc, out = _cli("--teblig", "2026-03-02", "--kural", AVK, "--yargi", "ceza")
    assert rc == 0 and _son(out) == "2026-03-17", out
    rc, out = _cli("--teblig", "2026-03-02", "--kural", HMK, "--yargi", "ceza")
    assert rc != 0 and "UYUŞMAZLIĞI" in out, out


@pytest.mark.parametrize("kural", IKI_KURAL)
def test_iki_okuma_arasindaki_isleme_karsi_tarafa_kesin_dil_kurulmaz(kural):
    """İşlem 20.08.2026: manşete (10.08) göre geç, geç okumaya (07.09) göre süresinde.
    Rejim teyitsiz → 'süre kaçırılmıştır' kesin dili YOK, ARA TESPİT."""
    rc, out = _cli("--teblig", "2026-07-25", "--kural", kural, "--islem", "2026-08-20")
    assert rc == 0, out
    assert "SÜRE KAÇIRILMIŞTIR" not in out
    assert "ARA TESPİT" in out and "KESİN DİL KULLANMA" in out, out


# ══════════════════════════════════════════════════════════════════════════
# 4) Talimat katmanı — MK-2 çağrısı, SKILL.md'ler, çizelge, günlükler
# ══════════════════════════════════════════════════════════════════════════

def test_mk2_cagrisi_yeni_kural_adlariyla_eski_kuralsiz_cagri_yok():
    """MK-2/3: `--kural hmk_istifa_vekalet_devam` / `--kural avk_istifa_vekalet_devam`;
    kuralsız `--sure 2 --birim hafta` / `--sure 15 --birim gun` çağrısı KALKTI (o çağrı
    --yargi hukuk varsayılanıyla HMK m.104 uzatması uygular → yazın GEÇ tarih)."""
    mk2 = _bolum(MK_REF.read_text(encoding="utf-8"), "## MK-2", "## MK-3")
    assert "--kural hmk_istifa_vekalet_devam" in mk2, mk2
    assert "--kural avk_istifa_vekalet_devam" in mk2, mk2
    assert "--sure 2 --birim hafta" not in mk2 and "--sure 15 --birim gun" not in mk2
    assert "ERKEN" in mk2 and "GEÇ" in mk2 and "**TEYİT BEKLİYOR**" in mk2
    # T5-1 bulgusu: süre tatilde İŞLER (m.103/3); m.104 uygulaması kararla teyit edilemedi;
    # Av.K. m.41 HMK süresi değil (23. HD, kıyas)
    for k in ("m.103/3", "2013/8404", "kıyas"):
        assert k in mk2, k


def test_ust_ilke_dokunulmadi():
    """Avukat emri: ÜST İLKE (meslek kurallarında otorite yoktur; öncelikle müvekkilin
    menfaati esastır) dosyanın başında AYNEN durur — bu paket ona dokunmaz."""
    txt = MK_REF.read_text(encoding="utf-8")
    bas = _duz(re.sub(r"(?m)^>[ \t]?", "", txt.split("**Fikir kaynağı:**")[0]))
    for k in ("ÜST İLKE", "Meslek kurallarında otorite yoktur", "müvekkilin menfaati esastır",
              "Avukatlık Kanunu gereği", "karar avukatındır"):
        assert k in bas, k


def test_interview_skill_md_c_maddesi_yeni_kural_adlarini_tasir():
    txt = INTERVIEW_SKILL_MD.read_text(encoding="utf-8")
    blok = _bolum(txt, "**(c) MESLEK KURALLARI", "1. **Meseleyi bir cümlede")
    assert HMK in blok and AVK in blok, blok
    assert "ERKEN" in blok, blok


def test_oa_sure_skill_md_ve_cizelge_istifa_kurallarini_anlatir():
    md = SURE_SKILL_MD.read_text(encoding="utf-8")
    assert HMK in md and AVK in md
    # KÜÇÜK-7: 4g başlığı "teyitli 2026-10-05" derken istifa satırı 2026-10-07 — başlık iki tarihi de söyler
    i = md.index("4g.")
    assert "2026-10-07" in md[i:i + 240], md[i:i + 240]
    c = CIZELGE.read_text(encoding="utf-8")
    assert HMK in c and AVK in c
    assert "m.82/1" in c and "Av.K. m.41" in c and "m.103/3" in c


def test_gunlukler_kusuru_ve_kural_sayisini_kaydeder():
    g = SURE_GUNLUK.read_text(encoding="utf-8")
    assert HMK in g and AVK in g
    assert "48 → 50" in g, "kural kataloğu 48 → 50 oldu; günlük bunu söylemeli"
    ig = INTERVIEW_GUNLUK.read_text(encoding="utf-8")
    assert HMK in ig and AVK in ig


def test_kural_katalogu_ikizleri_esit():
    """48 → 50 (iki istifa kuralı). Sayı testte KİLİTLENMEZ (KÜÇÜK-4; I5 notu: kural sayısını
    iki yerde tutmak B-35'in tersi); yalnız dört ikiz tablonun eşit büyüklükte olduğu ve iki
    yeni kuralı taşıdığı denetlenir."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    assert len(j) == len(H._GOMULU_KURALLAR) == len(H._GOMULU_REJIM) == len(H._GOMULU_TEYIT)
    assert set(IKI_KURAL) <= set(j)
