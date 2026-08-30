# -*- coding: utf-8 -*-
"""v0.5.14 — CEZA + GİZLİLİK + ALAN ŞABLONLARI paketi.

Kapsam (DENETIM-CELISKI-KIRIK.md bulgu kimlikleri + PLAN-SEMA-PAKETI.md T10):

  B-15 (P0) — gizlilik_tara Layer 0: IBAN deseni TR + 24 karakter (toplam 26)
              gerçeğine göre düzeltilir; eski desen TR sonrası 18 hane beklediği
              için GEÇERLİ HİÇBİR Türk IBAN'ında ateşleyemiyordu.
  A-22      — Layer 0 künye yanlış-pozitifi: kamuya açık yerleşik içtihat
              künyesi (merci adı var, taraf bağlamı yok) ASK üretmez; desen
              doktrine (`gizlilik-desenleri.md`: "Esas/Karar no + taraf
              bağlamı") hizalanır. Mercisiz çıplak künye FAIL-CLOSED kalır.
  A-2  (P0) — savunma-kontrol-listesi.md CMK m.268 itiraz süresi "yedi gün"
              yanlışı + dosyadaki tüm süre çıpalarının MCP teyidi.
  A-8       — katılma anı oa-musteki-vekili/SKILL.md içinde iki zıt biçimde
              yazılıydı; tek doğru metne indirilir (m.237/1-2).
  A-11      — HAGB: CMK m.231/12 16/7/2026-7589 ile değişti; m.272/3 istisnası.
  A-12      — CMK m.263 (tutuklunun kanun yollarına başvurması — süre kesen).
  A-13      — Av.K. m.38 (işin reddi) + m.135/1-p (karşı tarafla temas)
              alım mülakatının ilk kalemi olarak.
  A-14      — tasarrufun-iptali.md: m.281 usul maddesidir, şüpheli döneme
              çıpa değildir; m.280/1 ileri yönlü takip şartı ayrı eksendir.
  A-15      — kidem-ihbar.md zamanaşımı "Mahkemece resen" yanlışı (TBK m.161).
  A-16      — itirazin-iptali.md icra inkâr tazminatı ↔ kötüniyet tazminatı.
  B-40      — ceza aynalarında iki adım da "10." numaralıydı (KAPANIŞ = 11).
  T10       — `amme-odeme-emri.md` unsur şablonu (6183 m.55/58 + İYUK m.27 YD).

Tüm veriler SENTETİKTİR. Testlerdeki IBAN, mod-97 doğrulaması geçen ama
tamamı sıfırlardan oluşan bir kalıptır — hiçbir gerçek hesaba karşılık gelmez.
"""
import importlib.util
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
GIZLILIK = SKILLS / "oa-gizlilik" / "scripts" / "gizlilik_tara.py"

MUDAFII = SKILLS / "oa-mudafii" / "SKILL.md"
KONTROL_LISTESI = SKILLS / "oa-mudafii" / "references" / "savunma-kontrol-listesi.md"
MUSTEKI = SKILLS / "oa-musteki-vekili" / "SKILL.md"
INTERVIEW = SKILLS / "oa-interview" / "SKILL.md"
STRATEJI = SKILLS / "oa-strateji" / "SKILL.md"
SABLONLAR = SKILLS / "oa-alan" / "references" / "unsur-sablonlari"
DESENLER = SKILLS / "oa-gizlilik" / "references" / "gizlilik-desenleri.md"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


giz = _yukle("gizlilik_tara_v0514", GIZLILIK)


def _oku(yol):
    return yol.read_text(encoding="utf-8", errors="replace")


# SENTETİK IBAN — mod-97 geçerli, gövdesi tamamen sıfır (gerçek hesap DEĞİL).
IBAN_SENTETIK = "TR200000000000000000000001"
IBAN_SENTETIK_BOSLUKLU = "TR20 0000 0000 0000 0000 0000 01"
# Aynı biçim, checksum BOZUK — fail-closed davranışın kanıtı.
IBAN_BOZUK_CHECKSUM = "TR990000000000000000000001"


# ═══════════════════ B-15 — IBAN DESENİ (P0) ═══════════════════

def _iban_deny_var(deny):
    return any("IBAN" in ad for _s, ad in deny)


def test_b15_bosluksuz_gercek_bicimli_iban_mutlak_deny():
    """B-15: TR + 24 karakter (toplam 26) — eski desen TR sonrası 18 hane
    beklediği için geçerli hiçbir Türk IBAN'ında ateşleyemiyordu."""
    deny, _ask = giz.tara(f"Havale {IBAN_SENTETIK} hesabına yapılmıştır.", "balanced")
    assert _iban_deny_var(deny), f"IBAN MUTLAK_DENY üretmeliydi: {deny}"


def test_b15_bosluklu_gercek_bicimli_iban_mutlak_deny():
    deny, _ask = giz.tara(f"Hesap: {IBAN_SENTETIK_BOSLUKLU}", "balanced")
    assert _iban_deny_var(deny), f"boşluklu IBAN MUTLAK_DENY üretmeliydi: {deny}"


def test_b15_checksum_bozuk_iban_da_deny_fail_closed():
    """Mod-97 tutmayan ama IBAN BİÇİMİNDE olan dizi de engellenir: OCR ile
    bozulmuş gerçek bir IBAN kaçmasın (ailenin fail-closed doktrini)."""
    deny, _ask = giz.tara(f"IBAN {IBAN_BOZUK_CHECKSUM}", "balanced")
    assert _iban_deny_var(deny)


def test_b15_kisa_dizi_iban_sayilmaz():
    """TR + 18 hane (eski hatalı desenin beklediği uzunluk) geçerli bir Türk
    IBAN'ı DEĞİLDİR; IBAN etiketiyle raporlanmaz."""
    deny, _ask = giz.tara("Referans TR200000000000000000", "balanced")
    assert not _iban_deny_var(deny)


def test_b15_iban_mod97_dogrulamasi():
    """Yardımcı doğrulayıcı: gövde aynı, yalnız kontrol hanesi farklı."""
    assert giz.iban_gecerli(IBAN_SENTETIK) is True
    assert giz.iban_gecerli(IBAN_SENTETIK_BOSLUKLU) is True
    assert giz.iban_gecerli(IBAN_BOZUK_CHECKSUM) is False
    assert giz.iban_gecerli("TR20") is False


def test_b15_iban_maskelenir():
    cikti = giz.maskele(f"Ödeme {IBAN_SENTETIK_BOSLUKLU} hesabına yapıldı.")
    assert IBAN_SENTETIK_BOSLUKLU not in cikti
    assert "[IBAN-MASKELİ]" in cikti


def test_b15_desen_yorumu_algoritmik_dogrulamayi_yalan_soylemiyor():
    """Eski yorum 'IBAN ayrıca algoritmik doğrulanır' diyordu ama dosyada
    checksum yoktu. Artık doğrulayıcı GERÇEKTEN var."""
    assert hasattr(giz, "iban_gecerli")


# ═══════════════════ A-22 — KÜNYE YANLIŞ-POZİTİFİ ═══════════════════

def _kunye_ask_var(ask):
    return any("Esas/Karar" in ad or "künye" in ad.lower() for _s, ad in ask)


def test_a22_kamuya_acik_ictihat_kunyesi_strict_modda_ask_uretmez():
    """A-22: merci adı taşıyan, taraf bağlamı olmayan yerleşik künye kamuya
    açık bir atıftır — gizlilik kapısı onu ASK'a düşürmez."""
    metin = "Yargıtay 9. Hukuk Dairesi E. 2020/1111, K. 2021/2222 sayılı kararı."
    deny, ask = giz.tara(metin, "strict")
    assert not deny
    assert not _kunye_ask_var(ask), f"kamuya açık künye ASK üretmemeliydi: {ask}"


def test_a22_kamuya_acik_kunye_bilgi_kanalinda_gorunur():
    """Görünürlük kaybolmaz: künye BİLGİ kanalına düşer (exit kodunu etkilemez)."""
    bilgi = []
    metin = "Danıştay 8. Daire E. 2019/1234 K. 2020/5678 kararına atıf yapılmıştır."
    giz.tara(metin, "strict", bilgi)
    assert any("künye" in ad.lower() for _s, ad in bilgi), bilgi


def test_a22_taraf_baglamli_kunye_strict_modda_ask_kalir():
    """Doktrinin dediği desen ('Esas/Karar no + TARAF BAĞLAMI') aynen ateşler."""
    metin = "Davacı vekilinin 2024/123 E. sayılı dosyadaki beyanı."
    _deny, ask = giz.tara(metin, "strict")
    assert _kunye_ask_var(ask), f"taraf bağlamlı künye ASK üretmeliydi: {ask}"


def test_a22_mercisiz_ciplak_kunye_fail_closed_ask_kalir():
    """Merci ile nitelenmemiş çıplak künye, müvekkilin kendi esas numarası
    olabilir → beyaz listeye ALINMAZ (fail-closed)."""
    _deny, ask = giz.tara("E. 2020/1111 K. 2021/2222", "strict")
    assert _kunye_ask_var(ask)


def test_a22_ilk_derece_mahkeme_kunyesi_beyaz_listeye_girmez():
    """'... Mahkemesi' ibaresi tek başına yerleşik içtihat mercii değildir;
    dava dosyası künyesi kamuya açık atıf sayılmaz."""
    metin = "Denizli 3. İş Mahkemesi 2025/354 E. sayılı dosya."
    _deny, ask = giz.tara(metin, "strict")
    assert _kunye_ask_var(ask)


def test_a22_desen_tablosu_ile_kod_ayni_seyi_soyluyor():
    """İkiz liste kayması nöbetçisi: doktrin dosyası beyaz listeyi anmalı."""
    txt = _oku(DESENLER)
    assert "taraf bağlamı" in txt
    assert "beyaz liste" in txt.lower()


# ═══════════════════ A-2 (P0) — SAVUNMA KONTROL LİSTESİ SÜRELERİ ═══════════

def test_a2_kural_yedi_gun_ibaresi_kalmadi():
    """A-2 (P0): CMK m.268 itiraz süresi iki haftadır; 'kural yedi gün' satırı
    süreyi OLDUĞUNDAN KISA gösteriyordu (telafisiz)."""
    txt = _oku(KONTROL_LISTESI)
    assert "kural yedi gün" not in txt
    assert "yedi gün" not in txt.lower().replace("yedi günlük", "")


def test_a2_itiraz_satiri_m268_iki_hafta_ve_ogrenme_gunu():
    txt = _oku(KONTROL_LISTESI)
    satir = next(s for s in txt.splitlines() if "m.267-271" in s)
    assert "iki hafta" in satir
    assert "öğrendiği" in satir or "öğrenme" in satir


def test_a2_kanun_yolu_sureleri_tek_kaynaga_baglandi():
    """Süre değerleri iki yerde tutulmaz: referans dosya `sure_kurallari.json`
    /`oa-sure` tek kaynağına açıkça yönlendirir."""
    txt = _oku(KONTROL_LISTESI)
    assert "sure_kurallari.json" in txt or "oa-sure" in txt
    assert "hesapla_sure" in txt


def test_a2_adli_tatil_cmk_m331_capasi_var():
    """Ceza sürelerinde adli tatil rejimi CMK m.331/4'tür (üç gün) — hukuk
    yargısının HMK m.104 rejimi DEĞİL."""
    txt = _oku(KONTROL_LISTESI)
    assert "m.331" in txt
    assert "üç gün" in txt
    assert "HMK m.104" in txt  # yanlış rejime karşı açık uyarı


def test_a2_istinaf_ve_temyiz_sureleri_iki_hafta():
    txt = _oku(KONTROL_LISTESI)
    istinaf = next(s for s in txt.splitlines() if "m.272-281" in s)
    temyiz = next(s for s in txt.splitlines() if "m.286-307" in s)
    assert "iki hafta" in istinaf and "m.273" in istinaf
    assert "iki hafta" in temyiz and "m.291" in temyiz


# ═══════════════════ A-11 — HAGB (m.231/12 · 7589) ═══════════════════

def test_a11_hagb_7589_capasi_iki_dosyada_da_var():
    for yol in (MUDAFII, KONTROL_LISTESI):
        txt = _oku(yol)
        assert "7589" in txt, f"{yol.name}: 7589 s.K. çıpası yok"
        assert "m.272/3" in txt or "272 nci maddenin üçüncü" in txt, \
            f"{yol.name}: m.272/3 istisnası anılmıyor"


def test_a11_hagb_istinaf_yolu_kosulsuz_acik_denmiyor():
    """m.272/3 kapsamındaki hükümlerde istinaf KAPALIDIR; 'istinaf yolu
    açıktır' mutlak cümlesi kapalı yola başvuru (süre + harç kaybı) üretir."""
    for yol in (MUDAFII, KONTROL_LISTESI):
        txt = _oku(yol)
        assert "istinaf açık, BAM usul+esas inceler (7499 s.K.)" not in txt
        assert "**istinaf** yolu açıktır ve BAM" not in txt


# ═══════════════════ A-12 — CMK m.263 (TUTUKLU) ═══════════════════

def test_a12_m263_tutuklu_kanun_yolu_kalemi_var():
    txt = _oku(MUDAFII)
    assert "m.263" in txt
    assert "ceza infaz kurumu" in txt
    assert "kesilmiş sayılır" in txt


def test_a12_tutuklu_kipinde_adli_tatil_istisnasi_anildi():
    """CMK m.331/2-3: tutuklu işler tatilde de yürür."""
    txt = _oku(MUDAFII)
    assert "m.331/2" in txt


# ═══════════════════ A-8 — KATILMA ANI (tek doğru metin) ═══════════════════

def test_a8_katilma_her_asamada_ibaresi_kalmadi():
    txt = _oku(MUSTEKI)
    assert "kovuşturmada her aşamada talep edilebilir" not in txt


def test_a8_sure_nobeti_bolumu_ilk_derece_ve_hukum_verilinceye_kadar_diyor():
    txt = _oku(MUSTEKI)
    satirlar = txt.splitlines()
    i = next(i for i, s in enumerate(satirlar) if s.startswith("## 4."))
    blok = "\n".join(satirlar[i:i + 30])
    assert "**Katılma" in blok
    assert "ilk derece" in blok
    assert "hüküm verilinceye kadar" in blok.lower()
    assert "m.237/2" in blok


# ═══════════════════ A-13 — MESLEK KURALLARI (Av.K. m.38 / m.135/1-p) ══════

def test_a13_isin_reddi_ve_temas_kurali_alimda():
    txt = _oku(INTERVIEW)
    assert "m.38" in txt
    assert "m.135/1-p" in txt
    assert "işin reddi" in txt.lower()


def test_a13_catisma_taramasi_alimin_ilk_kalemi():
    """Çatışma taraması, karar-kritik çekirdeğin ÖNÜNDE olmalı: vekâleti
    sakatlayan bir işin farkına analiz bittikten sonra varılmaz."""
    txt = _oku(INTERVIEW)
    assert txt.index("m.38") < txt.index("Karar-kritik çekirdeği topla")


# ═══════════════════ A-14 — TASARRUFUN İPTALİ ═══════════════════

def test_a14_u3_supheli_donem_satirinda_m281_yok():
    """İİK m.281 'İptal davalarında yargılama usulü'dür; şüpheli döneme
    çıpa yapılırsa dilekçede dayanaksız kalır."""
    txt = _oku(SABLONLAR / "tasarrufun-iptali.md")
    u3 = next(s for s in txt.splitlines() if s.startswith("| U3"))
    assert "m.281" not in u3


def test_a14_m281_usul_satirinda_anildi():
    txt = _oku(SABLONLAR / "tasarrufun-iptali.md")
    assert "m.281" in txt
    assert "basit yargılama usulü" in txt


def test_a14_m280_ileri_takip_sarti_ucuncu_eksen():
    """m.280/1: işlemin gerçekleştiği tarihten itibaren beş yıl içinde
    takipte bulunulmuş olmalıdır — geri değil İLERİ yönlü şart."""
    txt = _oku(SABLONLAR / "tasarrufun-iptali.md")
    assert "Takip şartı" in txt
    assert "m.280/1" in txt
    eksen_satirlari = [s for s in txt.splitlines()
                       if s.startswith("| **") and "İLERİ" in s.upper()]
    assert len(eksen_satirlari) >= 2, f"iki ayrı ileri eksen beklenir: {eksen_satirlari}"


def test_a14_kapi_m277_m278_lafzina_cekildi():
    txt = _oku(SABLONLAR / "tasarrufun-iptali.md")
    assert "aciz belgesi / kesinleşmiş takip" not in txt
    assert "aciz vesikası" in txt
    assert "m.277" in txt


# ═══════════════════ A-15 — KIDEM/İHBAR ZAMANAŞIMI ═══════════════════

def test_a15_zamanasimi_resen_degil_defidir():
    """TBK m.161: 'Zamanaşımı ileri sürülmedikçe, hâkim bunu kendiliğinden
    göz önüne alamaz.'"""
    txt = _oku(SABLONLAR / "kidem-ihbar.md")
    u6 = next(s for s in txt.splitlines() if s.startswith("| U6"))
    assert "Mahkemece resen" not in u6
    assert "def'i" in u6
    assert "TBK m.161" in u6


def test_a15_arabuluculuk_dava_sarti_resen_kalir():
    """Rejim ayrımı: dava şartı gerçekten resen gözetilir — sütun toptan
    değiştirilmez."""
    txt = _oku(SABLONLAR / "kidem-ihbar.md")
    u7 = next(s for s in txt.splitlines() if s.startswith("| U7"))
    assert "resen" in u7


# ═══════════════════ A-16 — İCRA İNKÂR / KÖTÜNİYET TAZMİNATI ═══════════════

def test_a16_iki_tazminat_ayri_satirda():
    txt = _oku(SABLONLAR / "itirazin-iptali.md")
    assert "icra inkâr tazminatı" in txt
    assert "kötüniyet tazminatı" in txt
    u6 = next(s for s in txt.splitlines() if s.startswith("| U6"))
    u7 = next(s for s in txt.splitlines() if s.startswith("| U7"))
    assert "borçlu" in u6.lower()
    assert "alacaklı" in u7.lower()


def test_a16_talep_sarti_ve_sabit_oran_yazimi_yok():
    """m.67/2: yaptırım 'diğer tarafın talebi üzerine' hükmolunur ve oran
    ASGARİdir — '(%20)' sabit yazımı hem talebi hem asgariliği gizliyordu."""
    txt = _oku(SABLONLAR / "itirazin-iptali.md")
    assert "%20" not in txt and "% 20" not in txt
    assert "talep" in txt.lower()
    assert "asgari" in txt.lower()


# ═══════════════════ B-40 (ceza) — ADIM NUMARALANDIRMA ═══════════════════

def test_b40_kapanis_adimi_11_numarali():
    for yol in (MUDAFII, MUSTEKI):
        txt = _oku(yol)
        assert "11. KAPANIŞ" in txt, f"{yol.parent.name}: KAPANIŞ hâlâ 10."
        onlu = [s for s in txt.splitlines() if s.startswith("10. ")]
        assert len(onlu) == 1, f"{yol.parent.name}: iki adım da '10.' numaralı: {onlu}"


# ═══════════════════ T10 — AMME ÖDEME EMRİ ŞABLONU ═══════════════════

SABLON = SABLONLAR / "amme-odeme-emri.md"

_CIPLAK_SURE = re.compile(r"(?<!m\.)\b\d+\s*(?:gün|hafta|ay|yıl)\b")
_CIPLAK_ORAN = re.compile(r"%\s*\d+")


def test_t10_sablonu_var_ve_dort_sutunlu():
    assert SABLON.is_file(), "amme-odeme-emri.md eklenmedi"
    txt = _oku(SABLON)
    for baslik in ("Unsur", "Norm", "Delil", "yük"):
        assert baslik.lower() in txt.lower()
    unsurlar = [s for s in txt.splitlines() if re.match(r"^\| U\d+", s)]
    assert len(unsurlar) >= 8, f"U1-U10 beklenir, bulunan: {len(unsurlar)}"
    for s in unsurlar:
        assert s.count("|") == 5, f"dört sütun bozuk: {s}"


def test_t10_budanmayacak_dort_hat_metinde_var():
    """Ödeme emri davasının sınırlılığı MUTLAK DEĞİLDİR — dört hat pozitif
    kilitle korunur (aksi hâlde şablon savunmayı daraltır)."""
    txt = _oku(SABLON)
    for hat in ("tebliğ", "yok hükmünde", "şekil", "tahakkuk"):
        assert hat in txt.lower(), f"budanmayacak hat eksik: {hat}"


def test_t10_ciplak_sure_oran_rakami_gecmiyor():
    """Şablon rakam HALÜSİNASYONU üretmez: süre/oran rakamı yazılmaz, madde
    numarası serbesttir."""
    txt = _oku(SABLON)
    assert not _CIPLAK_SURE.findall(txt), _CIPLAK_SURE.findall(txt)
    assert not _CIPLAK_ORAN.findall(txt), _CIPLAK_ORAN.findall(txt)


def test_t10_yd_kavsagi_otomatik_durma_yanilgisini_kiriyor():
    """İYUK m.27/4: tahsilat işlemlerinden dolayı açılan davalar tahsil
    işlemini DURDURMAZ; ödeme emri bir tahsilat işlemidir."""
    txt = _oku(SABLON)
    assert "İYUK m.27" in txt
    assert "kendiliğinden durmaz" in txt
    assert "yürütmenin durdurulması" in txt.lower()
    assert "e-haciz" in txt.lower()


def test_t10_yd_ret_kisaltmasi_metne_girmedi():
    """'YD-RET' kısaltması nöbet defterinde de metinde de kullanılmaz."""
    txt = _oku(SABLON)
    assert "YD-RET" not in txt
    assert "reddi" in txt


def test_t10_yd_nobeti_tarihli_kayit_ve_komut_ornegi():
    txt = _oku(SABLON)
    assert "hesapla_sure.py" in txt
    assert "--aciklama" in txt
    assert "m.27/7" in txt


def test_t10_muvekkil_bilgilendirmesi_advisory_kalir():
    """Şablon bir markdown referansıdır; mekanik kapı iddia etmez."""
    txt = _oku(SABLON)
    assert "exit 1" not in txt
    assert "zorunlu kapı" not in txt


def test_t10_teyit_listesi_bolumu_var():
    txt = _oku(SABLON)
    assert "TEYİT LİSTESİ" in txt
    for norm in ("6183", "2577", "m.55", "m.58", "m.27"):
        assert norm in txt


def test_t10_asgari_set_readme_yeni_sablonla_senkron():
    """M4 aktivasyon dersi: keşif listesi bayat kalırsa şablon hiç açılmaz."""
    readme = _oku(SABLONLAR / "README.md")
    assert "amme-odeme-emri.md" in readme
    diskteki = {p.name for p in SABLONLAR.glob("*.md")} - {"README.md"}
    for ad in diskteki:
        assert ad in readme, f"README asgari setinde eksik: {ad}"


def test_t10_iik_m60_odeme_emriyle_karistirma_notu():
    """Aynı klasördeki `itirazin-iptali.md` U1'i 'ödeme emri | İİK m.58-60'
    diyor — iki ayrı kurum aynı adı taşıyor."""
    assert "İİK" in _oku(SABLON)
    assert "amme" in _oku(SABLONLAR / "README.md").lower()


# ═══════════════════ KORPUS KAPISI — alt dizin (T10-D6 eşdeğeri) ═══════════

def test_unsur_sablonlari_alt_dizini_korpus_kapilarina_tabi():
    """`SKILLS.glob('*/references/*.md')` alt dizini yakalamıyor; şablonlar
    doktrin taramalarının DIŞINDA kalıyordu. Bu test aynı iki yasağı
    `unsur-sablonlari/` için doğrudan uygular."""
    cagri_re = re.compile(r"teyit[^`\n]{0,400}?--arac[ \t]+ictihat_getir[^`\n]{0,400}", re.M)
    for md in sorted(SABLONLAR.glob("**/*.md")):
        txt = _oku(md)
        assert "bir karar = bir dosya" not in txt, md.name
        for m in cagri_re.finditer(txt):
            assert "--damga" in m.group(0), f"{md.name}: damgasız ictihat_getir örneği"


# ═══════════════════ STRATEJİ — TAHSİLAT ÇIPASI (T10 Kavşak B köprüsü) ═════

def test_strateji_amme_tahsilat_capasi_yd_yolunu_isaret_ediyor():
    txt = _oku(STRATEJI)
    assert "yürütmenin durdurulması" in txt.lower()
    assert "6183" in txt
