# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — MESLEK KURALLARI KONTROL LİSTELERİ (oa-interview).

Kapsam: oa-interview/references/meslek-kurallari-kontrol.md (MK-1 vekâlet
kapsamı ve özel yetki · MK-2 istifa/azil/devir · MK-3 müvekkil teyit-onam
notu · MK-4 ücret sözleşmesi), SKILL.md adım 0 "(c)" bağlantısı ve soru
bankası 9-10.

Fikir kaynağı Yargı PRO 15-3, 17-4, 13-9, 13-8 — metin/kod ALINMADI (telif ve
"fikri koruyarak" talimatı: bu test ayrıca kalıp ifadelerin kopyalanmadığını
kilitler). Resmî metin teyidi (Yargı PRO MCP mevzuat_getir, 2026-10-05): HMK
m.29, 55, 73, 74, 77, 81, 82, 83; Av.K. m.27, 36, 38, 39, 41, 56, 163, 164, 165,
166, 174; TBK m.504, 512, 513; KVKK m.5, 6, 9, 10; AAÜT m.1/3. Fable 5.1 karşı-tez
turu (salt okunur) eklemeleri: MK-0 çapraz atıf, ahzu kabz satırı, onaylı örnek,
azil tarihleri, evrak saklama/hapis, kendiliğinden sona erme, m.163/2, m.165-166. Önceki doğrulama kaydı: HMK m.82/1 + Av.K. m.41
(iki hafta / on beş gün) ve Av.K. m.164/2-3 doğru bulunmuştu.

Testler yalnız depo metnini okur; ağsız ve deterministiktir.
"""
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
INTERVIEW = SKILLS / "oa-interview"
REF = INTERVIEW / "references" / "meslek-kurallari-kontrol.md"
SKILL_MD = INTERVIEW / "SKILL.md"
SORU = INTERVIEW / "references" / "soru-bankasi.md"
BENIM_SKILLER = ("oa-interview", "oa-strateji", "oa-vakia", "oa-antitez", "oa-pipeline")


def _oku(p):
    return p.read_text(encoding="utf-8")


def _duz(s):
    return re.sub(r"\s+", " ", s)


def _bolum(txt, bas, son=None):
    i = txt.index(bas)
    j = txt.index(son, i) if son else len(txt)
    return _duz(txt[i:j])


def _alinti_duz(s):
    """Blok alıntının ("> ") satır başı işaretlerini atıp boşlukları tekler:
    satır kırılan bir ifade de tek parça aranabilsin."""
    return _duz(re.sub(r"(?m)^>[ \t]?", "", s))


def test_ust_ilke_meslek_kurallarinda_otorite_yok_muvekkil_menfaati_esas():
    """Avukat talimatı (Av. Bayram Can Çapar, 2026-10-07): "meslek kurallarında
    otorite yoktur. Öncelikle müvekkilimizin menfaati esastır avukatlık kanunu
    gereği." Üst ilke dosyanın EN BAŞINDA durur (fikir kaynağından ve listelerden
    önce). Dayanaklar resmî metinden okundu (Yargı PRO mevzuat_getir, 2026-10-07):
    Av.K. m.1/2, m.38/1-b, m.135/2-l, m.135/2-m, m.135/3-a (7571 s.K.); TBK m.506/2."""
    txt = _oku(REF)
    assert "**Fikir kaynağı:**" in txt
    bas = _alinti_duz(txt.split("**Fikir kaynağı:**")[0])
    for k in ("ÜST İLKE", "Meslek kurallarında otorite yoktur", "müvekkilin menfaati esastır",
              "Avukatlık Kanunu gereği", "2026-10-07",
              "Av.K. m.1/2", "bağımsız savunmayı serbestçe temsil eder", "Av.K. m.38/1-b",
              "m.135/2-l", "m.135/2-m", "m.135/3-a", "7571",
              "TBK m.506/2", "haklı menfaatlerini gözeterek, sadakat ve özenle",
              "GİZLEMEZ", "karar avukatındır"):
        assert k in bas, k
    # "otorite" sözcüğü artık resmî metne yüklenmez: madde metninin hukuki ÖLÇÜTÜ resmî metindir
    duz = _alinti_duz(txt)
    assert "otorite resmî metindir" not in duz
    assert "hukuki ölçüt resmî metindir" in duz


def test_skill_md_c_maddesi_ust_ilkeyi_tasir():
    """Model referans dosyasını açmadan önce SKILL.md'yi okur: üst ilke (c)
    maddesinin içinde, listelere yönlendiren satırla birlikte görünmelidir."""
    blok = _bolum(_oku(SKILL_MD), "**(c) MESLEK KURALLARI", "1. **Meseleyi bir cümlede")
    for k in ("ÜST İLKE", "otorite yoktur", "müvekkilin menfaati esastır", "TBK m.506/2", "karar avukatındır"):
        assert k in blok, k


def test_dort_liste_ve_ortak_ilke():
    txt = _oku(REF)
    for b in ("## MK-1", "## MK-2", "## MK-3", "## MK-4"):
        assert b in txt, b
    duz = _duz(txt)
    assert "taslak izni ≠ işlem izni" in duz
    assert "Belirsizlik = eksik sayılır (fail-closed)" in duz
    assert "`belgeli`" in txt and "`beyan`" in txt
    assert "mevzuat_getir" in duz and "2026-10-05" in duz


def test_mk1_hmk74_ozel_yetki_kalemlerinin_tamami():
    mk1 = _bolum(_oku(REF), "## MK-1", "## MK-2")
    for kalem in ("sulh olmak", "hâkimi reddetmek", "davanın tamamını ıslah", "yemin teklif etmek",
                  "başkasını tevkil", "haczi kaldırmak", "iflasını istemek", "tahkim ve hakem sözleşmesi",
                  "konkordato", "alternatif uyuşmazlık çözüm", "kanun yollarından feragat", "ibra etmek",
                  "davasını kabul", "yargılamanın iadesi", "Devlet aleyhine tazminat", "kişiye sıkı sıkıya bağlı"):
        assert kalem in mk1, f"HMK m.74 kalemi eksik: {kalem}"
    for dayanak in ("HMK m.73", "HMK m.74", "HMK m.77/1", "TBK m.504/3", "Av.K. m.27/3", "Av.K. m.56/5", "oa-usul"):
        assert dayanak in mk1, dayanak
    assert "YETKİ GÖRÜLMEDİ" in mk1 and "BELİRSİZ, gerçek işlem için YOK sayılır" in mk1
    assert "dava açılmamış ya da işlemler yapılmamış sayılır" in mk1
    # ahzu kabz HMK m.74'te ayrıca sayılmaz; uygulama dayanağı TEYİT BEKLİYOR
    assert "ahzu kabz" in mk1 and "**TEYİT BEKLİYOR**" in mk1
    assert "Av.K. m.56/1" in mk1 and "m.56/3" in mk1 and "resmi örnek hükmündedir" in mk1


def test_mk2_iki_sure_esitlenmez_ve_temkin_kurali():
    mk2 = _bolum(_oku(REF), "## MK-2", "## MK-3")
    for k in ("HMK m.82/1", "**iki hafta**", "Av.K. m.41", "**on beş gün**", "EŞİTLENMEZ", "**tebliğinden**",
              "HMK m.82/3", "**ihtaren**", "HMK m.83", "HMK m.77/4", "Av.K. m.174", "TBK m.512",
              "HMK m.81", "Av.K. m.41/2", "Av.K. m.36", "oa-sure/scripts/hesapla_sure.py"):
        assert k in mk2, k
    assert "ERKEN tarih" in mk2 and "GEÇ tarihe" in mk2
    assert "**TEYİT BEKLİYOR**" in mk2, "adli tatil etkisi doğrulanmadı — TEYİT BEKLİYOR kalmalı"
    # m.77/4'ün istisnası yalnız dosyanın incelenmemiş olmasına ilişkindir (lafzı aşma yok)
    assert "yalnız dosyanın incelenmemiş olması geçerli bir özre dayanıyorsa" in mk2
    # Fable karşı-tezi: azilde iki tarih, evrak saklama/hapis, kendiliğinden sona erme
    for k in ("azlin avukata ulaştığı tarih", "HMK m.81 bildiriminin", "**OA kuralı:**",
              "Av.K. m.39", "üç yıl", "üç ayın sonunda", "m.39/2", "TBK m.513", "m.513/2",
              "HMK m.55", "kayyım"):
        assert k in mk2, k


def test_mk3_kvkk_karar_sirasi_ve_imza_kaydi():
    mk3 = _bolum(_oku(REF), "## MK-3", "## MK-4")
    for k in ("HMK m.29", "m.5/2-e", "m.6/3-d", "m.5/2-c", "KVKK aydınlatması — m.10", "KVKK m.9",
              "**arızi olmak kaydıyla**", "Av.K. m.36", "İMZALANMADI", "yüzde yok", "oa-gizlilik"):
        assert k in mk3, k
    assert "açık rıza **aranmaz**" in mk3
    assert "m.11'de sayılan diğer hakları (m.10/1-a…d)" in mk3
    assert "geri alınabilir" in mk3
    assert "**TEYİT BEKLİYOR**" in mk3, "YZ bildiriminin kanuni şart olup olmadığı doğrulanmadı"


def test_mk4_ucret_sinirlari_ve_rakam_yok():
    mk4 = _bolum(_oku(REF), "## MK-4")
    for k in ("Av.K. m.163", "**yüzde yirmi beşi**", "m.164/3", "aynen avukata ait", "m.164/4", "AAÜT m.1/3",
              "m.164/son", "takas ve mahsup edilemez, haczedilemez", "m.174", "oa-sozlesme"):
        assert k in mk4, k
    assert "**TEYİT BEKLİYOR**" in mk4
    for k in ("İfa edilmiş sözleşmenin geçersizliği ileri sürülemez", "tümünü geçersiz kılmaz",
              "baro yönetim kuruluna bildirilir", "m.165", "müteselsil borçlu", "m.166", "rüçhan"):
        assert k in mk4, k
    tum = _oku(REF)
    assert not re.search(r"\d[\d.]*(?:,\d{2})?\s*TL\b", tum), "kontrol listesinde parasal tutar yazılamaz"


def test_mk0_is_kabulu_capraz_atfi():
    """Listeler iş kabulünden SONRA koşar: işin reddi zorunluluğu (Av.K. m.38)
    SKILL.md adım 0 ÇATIŞMA TARAMASI'ndadır; referans dosyası oraya bağlanır."""
    bas = _duz(_oku(REF).split("## MK-1")[0])
    assert "MK-0" in bas and "Av.K. m.38" in bas and "ÇATIŞMA TARAMASI" in bas
    assert "Av.K. m.38" in _oku(SKILL_MD)


def test_yargi_pro_kalip_ifadeleri_kopyalanmadi():
    """Fikir alındı, metin alınmadı: Yargı PRO'nun kalıp başlık/işaretleri yok."""
    for p in (REF, SKILL_MD, SORU):
        txt = _oku(p)
        for kalip in ("IRON LAW", "RED FLAGS", "DÜĞÜM SÖZLEŞMESİ", "GRAFTAN-URETILDI", "yargi-skill",
                      "Kalkan", "taslak_izni", "islem_izni"):
            assert kalip not in txt, f"{p.name}: Yargı PRO kalıbı '{kalip}'"


def test_skill_md_adim0_c_baglantisi_ve_description_siniri():
    txt = _oku(SKILL_MD)
    blok = _bolum(txt, "**(c) MESLEK KURALLARI", "1. **Meseleyi bir cümlede")
    for k in ("references/meslek-kurallari-kontrol.md", "MK-1", "MK-2", "MK-3", "MK-4", "EŞİTLENMEZ",
              "taslak izni ≠ işlem izni", "fail-closed", "oa-sure/scripts/hesapla_sure.py", "2026-10-05"):
        assert k in blok, k
    # adım 0 çatışma taraması önce gelir; (c) onun içindedir
    assert txt.index("0. **ÇATIŞMA TARAMASI") < txt.index("**(c) MESLEK KURALLARI") < txt.index("1. **Meseleyi")
    fm = txt.split("---")[1]
    aciklama = fm.split("description:", 1)[1]
    assert len(" ".join(aciklama.split())) <= 850


def test_soru_bankasi_9_ve_10():
    bank = _oku(SORU)
    blok = bank[bank.index("## Her alanda ortak çekirdek"):bank.index("## İş hukuku")]
    assert "7. **Masraf gücü" in blok and "8. **Risk toleransı" in blok
    assert "9. **Vekâlet ve özel yetki" in blok and "10. **Önceki vekil" in blok
    assert "HMK m.74" in blok and "HMK m.82" in blok and "Av.K. m.41" in blok
    # azilde tebliğ değil ulaşma + m.81 bildirimi sorulur; kendiliğinden sona erme de
    assert "azil ise avukata ne zaman ulaştı" in blok and "HMK m.81" in blok and "TBK m.513" in blok


def test_aile_dogrula_benim_skillerimde_hata_yok():
    """Yalnız bu paketin dokunduğu skill'ler süzülür: başka ajanların süren
    işleri bu testi kırmasın; tam aile temizliği test_skill_doktrin'de."""
    cp = subprocess.run([sys.executable, str(SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"), str(SKILLS)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    cikti = cp.stdout + cp.stderr
    benim = [s for s in cikti.splitlines()
             if any(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(sk), s) for sk in BENIM_SKILLER)
             and re.search(r"HATA|anıyor ama dosya yok|hayalet|description \d+ karakter|YASAK", s)]
    assert not benim, "\n".join(benim)
