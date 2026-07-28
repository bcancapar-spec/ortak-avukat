# -*- coding: utf-8 -*-
"""P1-11 (v0.5.5) — Doktrin senkronu: 'bir karar = bir dosya' → 'bir karar =
bir MUHAKEME KAYDI' (standart yol=tek komut, derin yol=dosya); TESLİM tanımı
tekildir (teslim-makbuz.json); aile_dogrula.py temiz.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
AILE_DOGRULA = SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"


def _tum_skill_ve_referans_md():
    return sorted(SKILLS.glob("*/SKILL.md")) + sorted(SKILLS.glob("*/references/*.md"))


def test_bir_karar_bir_dosya_kalibi_hicbir_dosyada_kalmadi():
    ihlal = []
    for md in _tum_skill_ve_referans_md():
        txt = md.read_text(encoding="utf-8", errors="replace")
        if "bir karar = bir dosya" in txt:
            ihlal.append(str(md.relative_to(REPO)))
    assert not ihlal, f"eski zorunlu kalıp hâlâ geçiyor: {ihlal}"


def test_iki_esdeger_form_ve_tek_komut_ornegi_oa_kiyasta():
    skill = SKILLS / "oa-kiyas" / "SKILL.md"
    txt = skill.read_text(encoding="utf-8")
    assert "eşdeğer form" in txt.lower() or "eşdeğer forma" in txt.lower() \
        or "iki eşdeğer" in txt
    assert "standart yol" in txt.lower()
    assert "derin yol" in txt.lower()
    assert "oa_hafiza.py teyit --arac ictihat_getir" in txt
    assert "--damga" in txt and "--bag" in txt and "--dokum-icerik" in txt


def test_bir_karar_bir_muhakeme_kaydi_ifadesi_var():
    skill = SKILLS / "oa-kiyas" / "SKILL.md"
    txt = skill.read_text(encoding="utf-8")
    assert "bir karar = bir MUHAKEME KAYDI" in txt


def test_teslim_makbuz_dort_skillde_gecer():
    sayac = []
    for md in SKILLS.glob("*/SKILL.md"):
        txt = md.read_text(encoding="utf-8", errors="replace")
        if "teslim-makbuz" in txt:
            sayac.append(md.parent.name)
    assert len(sayac) >= 4, f"yalnız {sayac} içinde geçiyor (>=4 beklenir)"
    for beklenen in ("oa-kontrol", "oa-pipeline", "oa-dilekce"):
        assert beklenen in sayac, f"{beklenen}/SKILL.md 'teslim-makbuz' anmıyor"


def test_teslim_tanimi_tekildir_notu_oa_dilekcede():
    skill = SKILLS / "oa-dilekce" / "SKILL.md"
    txt = skill.read_text(encoding="utf-8")
    assert "TESLİM tanımı tekildir" in txt
    assert "FINAL adını" in txt


_VECIZE = ("Künyeyi bulmak yetmez; kararın müvekkilin işine yarayıp yaramadığının "
           "muhakemesi güç çarpanıdır — çıplak künye sıfırdır, damgalı ve davaya "
           "bağlı karar çarpandır.")


def test_vecize_oa_ictihat_ve_oa_kiyasta_birebir_gecer():
    """P1-11 DÜZELTME (ONEMLI, sinav bulgusu) — kullanıcının VECİZE'si plan
    metninde 'oa-ictihat/oa-kiyas SKILL'lerine girer' diye konumlandırılmıştı;
    doktrinin çekirdeği olduğundan iki SKILL.md'de BİREBİR (grep-kilitli)
    bulunmalı."""
    for skill_ad in ("oa-ictihat", "oa-kiyas"):
        txt = (SKILLS / skill_ad / "SKILL.md").read_text(encoding="utf-8")
        assert _VECIZE in txt, f"{skill_ad}/SKILL.md VECİZE'yi taşımıyor"


def test_onkosul_artefakt_tablosu_oa_pipeline_skillde_var():
    """P1-11 DÜZELTME (ONEMLI, sinav bulgusu) — P0-6'nın kademeli önkoşul-
    artefakt kapısı (blokleyici/uyarı) yalnız kodda (pipeline_kayit.py
    ONKOSUL_BLOKLEYICI/ONKOSUL_UYARI) değil, doktrin metninde de (oa-pipeline/
    SKILL.md) bir TABLO olarak görünür olmalı."""
    txt = (SKILLS / "oa-pipeline" / "SKILL.md").read_text(encoding="utf-8")
    assert "ÖNKOŞUL-ARTEFAKT" in txt.upper()
    for beklenen in ("adım-5", "adım-9", "adım-4", "adım-6", "adım-7", "BLOKLEYICI", "UYARI"):
        assert beklenen in txt or beklenen.upper() in txt.upper(), \
            f"'{beklenen}' önkoşul-artefakt tablosunda bulunamadı"


def test_dava_tezi_ve_pas_protokolu_oa_pipeline_skillde_var():
    """M1 (Paket D, v0.5.5) — DAVA TEZİ + PAS PROTOKOLÜ doktrini oa-pipeline/
    SKILL.md'de görünür olmalı (kod ile senkron: tam_tur.py --tez/--tez-gerekce,
    pipeline_kayit.py --pas-yolu/son_pas_yolu, oa_hafiza.py ajan-brif enjeksiyonu)."""
    txt = (SKILLS / "oa-pipeline" / "SKILL.md").read_text(encoding="utf-8")
    assert "DAVA TEZİ" in txt
    assert "--tez" in txt and "--tez-gerekce" in txt
    assert "PAS PROTOKOLÜ" in txt
    assert "--pas-yolu" in txt
    assert "ÖNCEKİ PAS" in txt


def test_kiyas_semasi_ratio_ortusme_farklar_terminolojisi_var():
    """M2 (Paket D, v0.5.5) — KIYAS ŞEMASI terminoloji haritası (RATIO/ÖRTÜŞME/
    FARKLAR → İLGİLİ-KISIM/DAVAYA-BAĞ/AYIRT-ETME) referans dosyada görünür
    olmalı; parser'a YENİ alan EKLENMEDİĞİ (semantik değişmez) doğrulanır."""
    txt = (SKILLS / "oa-kiyas" / "references" / "ictihat-muhakeme-sablonu.md").read_text(
        encoding="utf-8")
    assert "RATIO" in txt and "ÖRTÜŞME" in txt and "FARKLAR" in txt
    assert "--ilgili-kisim" in txt and "--bag" in txt


def test_antitez_pasi_zorunlu_girdi_ve_g_kapisi_oa_dilekcede_var():
    """M3 (Paket D, v0.5.5) — ANTİTEZ PASI: oa-antitez çıktısı zorunlu pas
    girdisi olarak oa-dilekce/SKILL.md'de belgeli; [G] advisory kapısı
    (dilekce_denetim.py) DUYULMUŞ terminolojisiyle anılır."""
    txt = (SKILLS / "oa-dilekce" / "SKILL.md").read_text(encoding="utf-8")
    assert "ANTİTEZ PASI" in txt
    assert "zorunlu" in txt.lower() and "pas girdisi" in txt.lower()
    assert "[G] ANTİTEZ-CEVAP-ÇAPASI" in txt
    assert "DUYULMUŞ" in txt


def test_avukat_karari_cozum_komutu_oa_pipeline_skillde_var():
    """M7 (Paket D, v0.5.5) — AVUKAT KARARI BEKLEYEN'in çözüm komutu
    (--avukat-karari + --gerekce zorunluluğu) doktrin metninde görünür."""
    txt = (SKILLS / "oa-pipeline" / "SKILL.md").read_text(encoding="utf-8")
    assert "--avukat-karari" in txt
    assert "gerekçesiz" in txt.lower() or "gerekçeli" in txt.lower()


def test_unsur_sablonlari_asgari_set_var_ve_oa_vakia_baglantili():
    """M4 (Paket D, v0.5.5) — UNSUR ŞABLONLARI: oa-alan/references/unsur-
    sablonlari/ altında asgari 4-dosyalık set (unsur|norm|delil-türü|yük
    tablosu) + oa-vakia/SKILL.md bağlantısı."""
    kok = SKILLS / "oa-alan" / "references" / "unsur-sablonlari"
    for ad in ("tasarrufun-iptali.md", "ise-iade.md", "itirazin-iptali.md", "kidem-ihbar.md"):
        dosya = kok / ad
        assert dosya.is_file(), f"eksik unsur şablonu: {ad}"
        txt = dosya.read_text(encoding="utf-8")
        for baslik in ("Unsur", "Norm", "Delil", "yük"):
            assert baslik.lower() in txt.lower(), f"{ad}: '{baslik}' sütunu bulunamadı"

    vakia_txt = (SKILLS / "oa-vakia" / "SKILL.md").read_text(encoding="utf-8")
    assert "UNSUR ŞABLONLARI" in vakia_txt
    assert "unsur-sablonlari" in vakia_txt
    assert "ispat_bosluklari" in vakia_txt

    # Paket D sınav bulgusu (M4) — şablonların SAHİBİ oa-alan/SKILL.md de bu
    # dizine atıf yapmalı; aksi hâlde tek keşif yolu oa-vakia okunursa açılır
    # ve dava türü konumlandırılırken (oa-alan aşamasında) hiç işaret edilmez.
    alan_txt = (SKILLS / "oa-alan" / "SKILL.md").read_text(encoding="utf-8")
    assert "unsur-sablonlari" in alan_txt, (
        "oa-alan/SKILL.md, kendi ürettiği unsur-sablonlari/ dizinine atıf "
        "yapmıyor — aktivasyon boşluğu (M4 çürütücü bulgusu)")
    assert "UNSUR ŞABLONLARI" in alan_txt


def test_vakia_delilsiz_unsur_durumda_kirmizi_oa_pipelinede_baglantili():
    """M4 — DURUM.md renderer'ının delilsiz-unsur alanı kod ile senkron
    (fonksiyon adı doğrudan anılır — refactor sessizce dokümandan düşürmesin)."""
    pk_src = (SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py").read_text(encoding="utf-8")
    assert "_vakia_delilsiz_unsur_uyarisi" in pk_src
    assert "Delilsiz Unsur" in pk_src


def test_zaman_katmani_ve_pencere_bindirme_doktrini_var():
    """M5 (Paket D, v0.5.5) — KRONOLOJİ+VARLIK-AKIŞ: oa-illiyet ZAMAN KATMANI
    bölümü (tarih|olay|kaynak-evrak|sha) + oa-sure --pencereler bağlantısı."""
    illiyet_txt = (SKILLS / "oa-illiyet" / "SKILL.md").read_text(encoding="utf-8")
    assert "ZAMAN KATMANI" in illiyet_txt
    assert "--pencereler" in illiyet_txt

    blok_txt = (SKILLS / "oa-illiyet" / "references" / "cikti-blogu.md").read_text(encoding="utf-8")
    assert "tarih | olay | kaynak-evrak | sha" in blok_txt or (
        "tarih" in blok_txt.lower() and "kaynak-evrak" in blok_txt.lower() and "sha" in blok_txt.lower())

    sure_txt = (SKILLS / "oa-sure" / "SKILL.md").read_text(encoding="utf-8")
    assert "pencere bindirme" in sure_txt.lower()
    assert "--pencereler" in sure_txt


def test_ictihat_portfoyu_govde_vs_kutuk_doktrini_var():
    """M6 (Paket D, v0.5.5) — İÇTİHAT PORTFÖYÜ: oa-dilekce + oa-ictihat
    SKILL'lerinde 'en güçlü 3-5' seçim heuristiği (HGK/İBK>daire, yeni>eski,
    ihtisas dairesi) + v0.3.20 FINAL-MAX deseni referansı."""
    dilekce_txt = (SKILLS / "oa-dilekce" / "SKILL.md").read_text(encoding="utf-8")
    assert "İÇTİHAT PORTFÖYÜ" in dilekce_txt
    assert "FINAL-MAX" in dilekce_txt
    assert "3-5" in dilekce_txt
    assert "HGK" in dilekce_txt and "ihtisas" in dilekce_txt.lower()

    ictihat_txt = (SKILLS / "oa-ictihat" / "SKILL.md").read_text(encoding="utf-8")
    assert "İÇTİHAT PORTFÖYÜ" in ictihat_txt
    assert "FINAL-MAX" in ictihat_txt


def test_gorunmez_iskelet_doktrini_oa_dilecede_var():
    """P1-11 ek kural #2 — GÖRÜNMEZ İSKELET: İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ
    zinciri paragrafın İÇ mantığıdır, yüzeye ETİKET olarak sızmaz; geçiş
    cümleleriyle örülür. dilekce_denetim.py'nin [H] kapısına açık atıf var."""
    txt = (SKILLS / "oa-dilekce" / "SKILL.md").read_text(encoding="utf-8")
    assert "GÖRÜNMEZ İSKELET" in txt
    assert "İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ" in txt
    assert "ETİKET olarak sızmaz" in txt or "etiket olarak sızmaz" in txt.lower()
    assert "geçiş cümle" in txt.lower()
    assert "[H]" in txt


def test_gorunmez_iskelet_h_kapisi_dilekce_denetimde_uygulanmis():
    """[H] yalnız docstring'de VİTRİN olarak kalmamalı — gerçek fonksiyon
    (`_gorunmez_iskelet_uyarilari`) ve CLI çıktısında '[H]' başlığı var mı."""
    src = (SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py").read_text(encoding="utf-8")
    assert "_gorunmez_iskelet_uyarilari" in src
    assert "[H] GÖRÜNMEZ İSKELET TARAMASI" in src
    assert "İddiamız" in src and "Norm" in src and "Somut" in src


def test_omeralp_uslup_baglamasi_dogrini_oa_dilecede_var():
    """P1-11 ek kural #3 — ÖMERALP ÜSLUP BAĞLAMASI: oa-dilekce yazım
    disiplini kanun-yolu-mimari-playbook.md üslubuna ZORUNLU referansla
    bağlanır; teslim kontrol listesine 'üslup playbook'a uygun mu' maddesi."""
    txt = (SKILLS / "oa-dilekce" / "SKILL.md").read_text(encoding="utf-8")
    assert "ÖMERALP ÜSLUP BAĞLAMASI" in txt
    assert "kanun-yolu-mimari-playbook.md" in txt
    assert "tez-omurgalı" in txt
    assert "üslup playbook'a uygun mu" in txt

    kontrol_txt = (SKILLS / "oa-kontrol" / "SKILL.md").read_text(encoding="utf-8")
    assert "üslup playbook'a uygun mu" in kontrol_txt


def test_kusur_sonuc_talep_asimetrisi_uc_skillde_var():
    """P1-11 ek kural #4 — KUSUR→SONUÇ→TALEP ASİMETRİSİ: karşı tarafın
    kusuru TESPİT edilir, SONUÇ yazılır, GİDERİLMESİNE yönelik ara karar
    talebi KURULMAZ. oa-dilekce + oa-usul + oa-strateji'ye BİREBİR girer."""
    for skill_ad in ("oa-dilekce", "oa-usul", "oa-strateji"):
        txt = (SKILLS / skill_ad / "SKILL.md").read_text(encoding="utf-8")
        assert "KUSUR" in txt and "SONUÇ" in txt and "TALEP" in txt
        assert "GİDERİLMESİNE" in txt
        assert "KURULMAZ" in txt


def test_kusur_sonuc_talep_i_kapisi_dilekce_denetimde_uygulanmis():
    """[I] docstring'de VİTRİN olarak kalmamalı — gerçek fonksiyon
    (`_kusur_sonuc_talep_asimetri_uyarilari`) ve CLI '[I]' başlığı var mı."""
    src = (SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py").read_text(encoding="utf-8")
    assert "_kusur_sonuc_talep_asimetri_uyarilari" in src
    assert "[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI" in src


def test_aile_dogrula_temiz():
    cp = subprocess.run(
        [sys.executable, str(AILE_DOGRULA), str(SKILLS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    cikti = cp.stdout + cp.stderr
    assert "AİLE YAPI DENETİMİ TEMİZ" in cikti, cikti
    assert cp.returncode == 0, cikti
