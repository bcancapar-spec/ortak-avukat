# -*- coding: utf-8 -*-
"""v0.5.8.5 — A1 TAM-OKUMA + TRİYAJ KAPISI [G6] + E-serisi yumuşatma/tutarlılık.

Kullanıcı direktifi (EN YÜKSEK EFOR maddesi): "Müvekkil aleyhine HİÇBİR yargı
kararı dilekçeye giremez; model çektiği TÜM kararları İSTİSNASIZ baştan sona
okur; LEHE ise dilekçeye, ALEYHE ise cephaneliğe."

Kapsam:
- A1a ÜRETİCİ (`oa_hafiza.py teyit`): --dokum-sinifi {tam-metin|ilgili-kisim}
  alanı kütük satırına (DOKUM-SINIFI= tokenı) ve muhakeme kaydına
  (**DÖKÜM-SINIFI:** satırı) yazılır; --duyulmus bayrağı kütüğe DUYULMUS=EVET
  olarak işlenir; sınıf beyanı olmadan GETİR+damga çağrısı UYARI ile
  'ilgili-kisim' sayılır (geriye uyum, sessiz düşme yasağı).
- A1c TRİYAJ KAPISI (`ictihat_muhakeme_denetim.py` [G6]): dilekçedeki HER
  künye için ÜÇ şart — (1) kütükte TAM-METİN sınıfı döküm, (2) muhakeme
  kaydı şablon alanları (RATIO/ÖRTÜŞME/FARKLAR = İLGİLİ-KISIM/DAVAYA-BAĞ/
  AYIRT-ETME, G2'de denetlenir), (3) DAMGA=LEHE. İSTİSNA: kütükte
  duyulmus=EVET işaretli VE dilekçede ayırt/çürütme bağlamındaki
  ALEYHE-AYIRT kayıt geçer — destek atfı olarak asla.
- TERS DENETİM: kütükte son damgası ALEYHE olan karar cephanelik ürününde
  (07-antitez*) anılmıyorsa "FARKINDALIK KAYBI" advisory uyarısı.
- E3 (`oa_hafiza.py`): --arac parantezli ek/boşluk toleranslı normalize;
  mevzuat kaydında --damga sessiz yok sayılmaz, açık [BİLGİ] satırı basılır.
- E4/E6 (`oa_hafiza.py oturum-kapat`): süre-nöbeti belgesi + boş süre flag'i
  uyarısı; dosya.md '[doldur]' kalıntısı uyarısı; B2-KİLİT — makbuzsuz
  "TESLİME HAZIR" ibareli kapanış notu REDDEDİLİR.

Tüm girdiler tmp_path + SENTETİK veridir (repo kuralı m.7 — gerçek dava
numarası / kişi adı / gerçek klasör yolu yazılmaz).
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"

KUNYE = "Yargıtay 9. HD, E. 2024/111, K. 2024/222, T. 01.02.2024"
KUNYE_ALEYHE_2 = "Yargıtay 9. HD, E. 2022/500, K. 2022/600, T. 03.04.2022"

DESTEK_TASLAK = (f"Somut olayda {KUNYE} sayılı karar emsal teşkil etmektedir.\n")
AYIRT_TASLAK = (f"Davalı tarafın dayandığı {KUNYE} sayılı karar somut olaydan "
                "AYIRT edilmelidir; olgusal zemin tamamen başkadır.\n")


def _cli(script, args, cwd):
    cp = subprocess.run(
        [sys.executable, str(script)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ───────────────────────── [G6] iskele yardımcıları ─────────────────────────

def _kutuk_satiri(kunye, damga=None, ek="", dokum="_oa/teyit/dokum/kaynak.md"):
    sonuc = kunye
    if damga:
        sonuc += f" DAMGA={damga}"
    if ek:
        sonuc += f" {ek}"
    return (f"| 2026-01-01T00:00:00 | ictihat_getir | sorgu | {sonuc} | "
            f"[döküm]({dokum}) |")


def _iskele(tmp_path, damga="LEHE", ayirt_etme="", kutuk_var=True,
            kutuk_ek="DOKUM-SINIFI=tam-metin", taslak_metin=None,
            ekstra_kutuk_satirlari=()):
    dokum = tmp_path / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True)
    (dokum / "kaynak.md").write_text(
        f"{KUNYE} sayılı kararın tam metni burada yer almaktadır...\n",
        encoding="utf-8")
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    satirlar = [
        "# 01 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
        f"**DAMGA:** {damga}", "",
        "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
        "## DAVAYA-BAĞ", "...davaya bağ açıklaması...", "",
        "## AYIRT-ETME", ayirt_etme, "",
    ]
    (cikti / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")
    if kutuk_var:
        kutuk = ["| Zaman | Araç | Sorgu | Sonuç | Döküm |", "|---|---|---|---|---|",
                 _kutuk_satiri(KUNYE, damga=damga, ek=kutuk_ek)]
        kutuk += list(ekstra_kutuk_satirlari)
        (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").write_text(
            "\n".join(kutuk) + "\n", encoding="utf-8")
    taslak = tmp_path / "taslak.md"
    taslak.write_text(taslak_metin or DESTEK_TASLAK, encoding="utf-8")
    return taslak


def _denetim(tmp_path):
    return _cli(DENETIM, ["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)


# ── (1) LEHE üç-şart-tam GEÇER ──────────────────────────────────────────────

def test_lehe_uc_sart_tam_gecer(tmp_path):
    _iskele(tmp_path, damga="LEHE", kutuk_ek="DOKUM-SINIFI=tam-metin")
    kod, cikti = _denetim(tmp_path)
    assert kod == 0, cikti
    assert "TESLİM ENGELİ" not in cikti


# ── (2) tam-metinsiz künye BLOK (sınıfsız eski kütük = ilgili-kisim) ───────

def test_tam_metinsiz_kunye_blok(tmp_path):
    """Kütük satırında hiç DOKUM-SINIFI tokenı yok (eski kayıt) — geriye
    uyumla 'ilgili-kisim' sayılır; triyaj şartı (1) sağlanmadığından BLOK."""
    _iskele(tmp_path, damga="LEHE", kutuk_ek="")
    kod, cikti = _denetim(tmp_path)
    assert kod == 1, cikti
    assert "[G6]" in cikti
    assert "tam-metin" in cikti.lower()
    assert "ilgili-kisim" in cikti.lower()  # geriye-uyum sınıflaması görünür


def test_dokum_sinifi_ilgili_kisim_acikca_da_blok(tmp_path):
    _iskele(tmp_path, damga="LEHE", kutuk_ek="DOKUM-SINIFI=ilgili-kisim")
    kod, cikti = _denetim(tmp_path)
    assert kod == 1, cikti
    assert "[G6]" in cikti


# ── (3) DAMGA=LEHE şartı: NOTR ve ALEYHE dilekçede BLOK ────────────────────

def test_notr_dilekcede_triyaj_blok(tmp_path):
    """v0.5.8.5 sözleşme değişikliği: NOTR eskiden yalnız UYARIydı — triyaj
    kapısı üç şartından (3) DAMGA=LEHE sağlanmadığından artık BLOK."""
    _iskele(tmp_path, damga="NOTR", kutuk_ek="DOKUM-SINIFI=tam-metin")
    kod, cikti = _denetim(tmp_path)
    assert kod == 1, cikti
    assert "[G6]" in cikti
    assert "NOTR" in cikti


def test_aleyhe_kunye_dilekcede_blok(tmp_path):
    _iskele(tmp_path, damga="ALEYHE", kutuk_ek="DOKUM-SINIFI=tam-metin")
    kod, cikti = _denetim(tmp_path)
    assert kod == 1, cikti
    assert "ALEYHE" in cikti
    assert "m.6" in cikti


# ── (4) İSTİSNA: duyulmuş + ayırt bağlamı → ALEYHE-AYIRT geçer ─────────────

def test_duyulmus_ve_ayirt_baglami_gecer(tmp_path):
    _iskele(tmp_path, damga="ALEYHE-AYIRT",
            ayirt_etme="Emsalde işçi ihbar süresine uymuş; dosyamızda uymamış — zemin farklı.",
            kutuk_ek="DOKUM-SINIFI=tam-metin DUYULMUS=EVET",
            taslak_metin=AYIRT_TASLAK)
    kod, cikti = _denetim(tmp_path)
    assert kod == 0, cikti
    assert "TESLİM ENGELİ" not in cikti


def test_duyulmus_isareti_yoksa_aleyhe_ayirt_blok(tmp_path):
    """Karşı tarafça fiilen İLERİ SÜRÜLMEMİŞ (duyulmamış) aleyhe karar, ayırt
    bağlamında bile dilekçeye giremez — sunulmamış antiteze preemptive ifşa
    yasağı (anayasa m.6)."""
    _iskele(tmp_path, damga="ALEYHE-AYIRT",
            ayirt_etme="Emsalde işçi ihbar süresine uymuş; dosyamızda uymamış — zemin farklı.",
            kutuk_ek="DOKUM-SINIFI=tam-metin",
            taslak_metin=AYIRT_TASLAK)
    kod, cikti = _denetim(tmp_path)
    assert kod == 1, cikti
    assert "[G6]" in cikti
    assert "DUYULMUS" in cikti


def test_ayirt_baglami_yoksa_destek_atfi_blok(tmp_path):
    """Duyulmuş olsa bile ALEYHE-AYIRT karar DESTEK atfı gibi kullanılamaz —
    dilekçede ayırt/çürütme bağlamı görünmüyorsa BLOK."""
    _iskele(tmp_path, damga="ALEYHE-AYIRT",
            ayirt_etme="Emsalde işçi ihbar süresine uymuş; dosyamızda uymamış — zemin farklı.",
            kutuk_ek="DOKUM-SINIFI=tam-metin DUYULMUS=EVET",
            taslak_metin=DESTEK_TASLAK)
    kod, cikti = _denetim(tmp_path)
    assert kod == 1, cikti
    assert "[G6]" in cikti
    assert "destek" in cikti.lower() or "bağlam" in cikti.lower()


# ── (5) TERS DENETİM — cephaneliksiz ALEYHE = FARKINDALIK KAYBI (advisory) ─

def test_cephaneliksiz_aleyhe_farkindalik_kaybi_uyarisi(tmp_path):
    _iskele(tmp_path, damga="LEHE", kutuk_ek="DOKUM-SINIFI=tam-metin",
            ekstra_kutuk_satirlari=[
                _kutuk_satiri(KUNYE_ALEYHE_2, damga="ALEYHE",
                              ek="DOKUM-SINIFI=tam-metin")])
    kod, cikti = _denetim(tmp_path)
    assert kod == 0, cikti  # advisory — bloklamaz
    assert "FARKINDALIK KAYBI" in cikti
    assert "2022/500" in cikti


def test_cephanelikte_anilan_aleyhe_uyari_uretmez(tmp_path):
    _iskele(tmp_path, damga="LEHE", kutuk_ek="DOKUM-SINIFI=tam-metin",
            ekstra_kutuk_satirlari=[
                _kutuk_satiri(KUNYE_ALEYHE_2, damga="ALEYHE",
                              ek="DOKUM-SINIFI=tam-metin")])
    (tmp_path / "_oa" / "cikti" / "07-antitez-cephanelik.md").write_text(
        f"## CEPHE 1\nKarşı taraf {KUNYE_ALEYHE_2} sayılı karara dayanabilir; "
        "çürütme: olgusal zemin farklı.\n", encoding="utf-8")
    kod, cikti = _denetim(tmp_path)
    assert kod == 0, cikti
    assert "FARKINDALIK KAYBI" not in cikti


# ── (6) kütük fiilen kullanılmıyorsa triyaj görünür BİLGİ ile atlanır ──────

def test_kutuk_kullanilmiyorsa_triyaj_bilgi_ile_atlanir(tmp_path):
    """Elle kurulmuş / kütüksüz kök (derin yol) — kütüğe bağlı şartlar (tam-
    metin sınıfı, duyulmuş) MEKANİK denetlenemez; sessiz atlama yasağı gereği
    görünür bir [BİLGİ] satırı basılır, LEHE zincir yine geçer (geriye uyum)."""
    _iskele(tmp_path, damga="LEHE", kutuk_var=False)
    kod, cikti = _denetim(tmp_path)
    assert kod == 0, cikti
    assert "[G6]" in cikti
    assert "denetlenemedi" in cikti.lower() or "kullanılmıyor" in cikti.lower()


# ═══════════════════════════════════════════════════════════════════════════
# A1a ÜRETİCİ — oa_hafiza.py teyit: --dokum-sinifi / --duyulmus
# ═══════════════════════════════════════════════════════════════════════════

DOKUM_METIN = (f"{KUNYE} sayılı kararın tam metni: davalının kusuru ile "
               "davacının zararı arasında illiyet bağı bulunmaktadır.\n")
ILGILI_KISIM = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"
BAG_METNI = ("Bu karar, dosyamızdaki olgusal örüntüyle aynı unsur setini "
             "içeriyor; büyük önermeyi somutlaştıran doğrudan emsaldir.")


def _init(tmp_path):
    _cli(HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)


def _teyit_getir(tmp_path, ekstra=(), damga="LEHE"):
    return _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_getir", "--sorgu", "kidem tazminati illiyet",
        "--sonuc", KUNYE, "--damga", damga, "--bag", BAG_METNI,
        "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
        "--kok", str(tmp_path)] + list(ekstra), cwd=tmp_path)


def _kutuk_oku(tmp_path):
    return (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")


def test_teyit_dokum_sinifi_tam_metin_kutuge_ve_muhakemeye_yazilir(tmp_path):
    _init(tmp_path)
    kod, cikti = _teyit_getir(tmp_path, ekstra=["--dokum-sinifi", "tam-metin"])
    assert kod == 0, cikti
    assert "DOKUM-SINIFI=tam-metin" in _kutuk_oku(tmp_path)
    muhakeme = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(
        encoding="utf-8")
    assert "**DÖKÜM-SINIFI:** tam-metin" in muhakeme


def test_teyit_dokum_sinifi_belirtilmezse_uyari_ve_ilgili_kisim(tmp_path):
    """Sınıf beyan edilmeden GETİR+damga çağrısı SESSİZCE tam-okuma sayılamaz:
    görünür UYARI basılır, kütüğe dürüst 'ilgili-kisim' sınıfı işlenir."""
    _init(tmp_path)
    kod, cikti = _teyit_getir(tmp_path)
    assert kod == 0, cikti
    assert "UYARI" in cikti and "dokum-sinifi" in cikti.lower()
    assert "DOKUM-SINIFI=ilgili-kisim" in _kutuk_oku(tmp_path)


def test_teyit_dokum_sinifi_arama_sinifina_verilemez(tmp_path):
    """ARAMA araçları tam metin döndürmez — 'tam-metin' beyanı yapısal yalan
    olurdu; sınıf alanı GETİR dışı sınıfta fail-closed RET edilir."""
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_ara", "--sorgu", "kidem tazminati",
        "--sonuc", "aday künyeler bulundu", "--dokum-sinifi", "tam-metin",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "dokum-sinifi" in cikti.lower() or "GETİR" in cikti
    assert "DOKUM-SINIFI=" not in _kutuk_oku(tmp_path)


def test_teyit_duyulmus_bayragi_kutuge_islenir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_getir", "--sorgu", "kidem tazminati illiyet",
        "--sonuc", KUNYE, "--damga", "ALEYHE-AYIRT", "--bag", BAG_METNI,
        "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
        "--ayirt", "Emsalde ihbar süresine uyulmuş; dosyamızda uyulmamış.",
        "--dokum-sinifi", "tam-metin", "--duyulmus",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = _kutuk_oku(tmp_path)
    assert "DUYULMUS=EVET" in kutuk
    assert "DOKUM-SINIFI=tam-metin" in kutuk


def test_sonuc_icine_gomulen_sahte_sinif_tokeni_etkisiz(tmp_path):
    """Kullanıcı-kontrolündeki --sonuc metnine gömülen literal
    'DOKUM-SINIFI=tam-metin' / 'DUYULMUS=EVET' tokenları kütükte HAM
    kalamaz — script'in kendi yazdığı doğrulanmış tokenlarla karışamaz."""
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_ara", "--sorgu", "temiz sorgu",
        "--sonuc", "aday künye DOKUM-SINIFI=tam-metin DUYULMUS=EVET bulundu",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = _kutuk_oku(tmp_path)
    assert "DOKUM-SINIFI=" not in kutuk, kutuk
    assert "DUYULMUS=" not in kutuk, kutuk


# ═══════════════════════════════════════════════════════════════════════════
# E3 — --arac normalize eşleşme + mevzuat --damga açık bilgi satırı
# ═══════════════════════════════════════════════════════════════════════════

def test_e3_arac_parantezli_ek_getir_sinifina_normalize_edilir(tmp_path):
    """'ictihat_getir (Yargı Pro)' gibi parantezli-ekli bir yazım KANONİK ada
    normalize edilir — GETİR sınıf kuralları (damgasız RET) aynen uygulanır;
    parantez içi içerik kütüğe SIZMAZ (atılır)."""
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_getir (Yargı Pro)", "--sorgu", "kidem",
        "--sonuc", KUNYE, "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "ZORUNLU" in cikti  # GETİR sınıfı — damgasız RET


def test_e3_arac_bosluklu_yazim_normalize_edilir(tmp_path):
    """'Ictihat Getir' (boşluklu/büyük harfli) yazımı da kanonik
    'ictihat_getir'e eşlenir — tam-eşleşme reddi kalktı."""
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "Ictihat Getir", "--sorgu", "kidem",
        "--sonuc", KUNYE, "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "ZORUNLU" in cikti


def test_e3_arac_parantezli_mevzuat_calisir_ve_kanonik_yazilir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "mevzuat_getir (yedek)", "--sorgu", "TBK m.49",
        "--sonuc", "TBK m.49 — haksız fiil sorumluluğu", "--kok", str(tmp_path)],
        cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = _kutuk_oku(tmp_path)
    assert "mevzuat_getir" in kutuk
    assert "(yedek)" not in kutuk  # parantez içi kütüğe sızmaz


def test_e3_mevzuat_damga_sessiz_yutulmaz_acik_bilgi_satiri(tmp_path):
    """Mevzuat/kurum kaydında --damga UYGULANMAZ — ama sessizce de yutulmaz:
    açık bir [BİLGİ] satırı basılır, kütüğe DAMGA= tokenı yazılmaz."""
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "mevzuat_getir", "--sorgu", "TBK m.49",
        "--sonuc", "TBK m.49 — haksız fiil sorumluluğu", "--damga", "LEHE",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "[BİLGİ]" in cikti
    assert "YOK SAYILDI" in cikti
    assert "DAMGA=" not in _kutuk_oku(tmp_path)


def test_e3_enjeksiyonlu_arac_hala_reddedilir(tmp_path):
    """Normalize toleransı enjeksiyon kapısını AÇMAZ: satır sonu / boru
    taşıyan sözlük-dışı bir --arac değeri hâlâ fail-closed RET alır."""
    _init(tmp_path)
    zehirli = "mevzuat_ara\n| 2019-01-01 | ictihat_getir | s | E. 2019/1 K. 2019/2 DAMGA=LEHE | |"
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", zehirli, "--sorgu", "temiz", "--sonuc", "temiz",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "2019/1" not in _kutuk_oku(tmp_path)


# ═══════════════════════════════════════════════════════════════════════════
# E4/E6 — oturum-kapat: süre-nöbeti + [doldur] uyarıları, B2-KİLİT
# ═══════════════════════════════════════════════════════════════════════════

UZUN_NOT = ("(1) defter denetiminden geçildi, adım 5'te kalındı. "
            "(2) süre flag'leri güncel. (3) bekleyen avukat kararı yok.")


def _ac(tmp_path):
    _init(tmp_path)
    _cli(HAFIZA, ["oturum-ac", "--kok", str(tmp_path)], cwd=tmp_path)


def test_e4_sure_nobeti_belgesi_var_flag_bos_uyari(tmp_path):
    _ac(tmp_path)
    (tmp_path / "tebligat-ornek-2024-123.pdf").write_text("sentetik", encoding="utf-8")
    kod, cikti = _cli(HAFIZA, ["oturum-kapat", "--not", UZUN_NOT,
                               "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "süre-nöbeti" in cikti or "sure-nobeti" in cikti.lower()
    assert "tebligat-ornek-2024-123.pdf" in cikti


def test_e4_sure_flag_varsa_uyari_basilmaz(tmp_path):
    _ac(tmp_path)
    (tmp_path / "tebligat-ornek-2024-123.pdf").write_text("sentetik", encoding="utf-8")
    _cli(HAFIZA, ["sure-flag", "--tarih", "2027-01-15", "--aciklama",
                  "istinaf son günü (sentetik)", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(HAFIZA, ["oturum-kapat", "--not", UZUN_NOT,
                               "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "süre-nöbeti" not in cikti


def test_e6_dosya_md_doldur_kalintisi_uyari(tmp_path):
    _ac(tmp_path)  # init'in yazdığı dosya.md '[doldur]' doludur
    kod, cikti = _cli(HAFIZA, ["oturum-kapat", "--not", UZUN_NOT,
                               "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "[doldur]" in cikti


def test_e6_dosya_md_tamamsa_doldur_uyarisi_yok(tmp_path):
    _ac(tmp_path)
    (tmp_path / "_oa" / "dosya.md").write_text(
        "# Dosya Kimliği — Test Dosyası\n- Talep: sentetik talep tamamlandı.\n",
        encoding="utf-8")
    kod, cikti = _cli(HAFIZA, ["oturum-kapat", "--not", UZUN_NOT,
                               "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "[doldur]" not in cikti


def test_b2_kilit_makbuzsuz_teslime_hazir_notu_reddedilir(tmp_path):
    _ac(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "oturum-kapat", "--not", UZUN_NOT + " Taslak TESLİME HAZIR durumda.",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "AÇIK UÇLU — MAKBUZ RED/YOK" in cikti
    # not diske YAZILMAMALI (yanlış iddia kalıcılaşmaz), kilit KALMALI
    oturum = tmp_path / "_oa" / "oturum"
    notlar = list(oturum.glob("*.md")) if oturum.is_dir() else []
    assert notlar == [], notlar
    assert (tmp_path / "_oa" / ".oturum-kilidi").exists()


def test_b2_kilit_makbuz_red_ise_de_reddedilir(tmp_path):
    _ac(tmp_path)
    makbuz = tmp_path / "_oa" / "defter" / "teslim-makbuz.json"
    makbuz.write_text(json.dumps({"exit_kodu": 1}), encoding="utf-8")
    kod, cikti = _cli(HAFIZA, [
        "oturum-kapat", "--not", UZUN_NOT + " TESLİME HAZIR.",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "AÇIK UÇLU — MAKBUZ RED/YOK" in cikti


def test_b2_kilit_gecerli_makbuzla_teslime_hazir_gecer(tmp_path):
    _ac(tmp_path)
    makbuz = tmp_path / "_oa" / "defter" / "teslim-makbuz.json"
    makbuz.write_text(json.dumps({"exit_kodu": 0, "taslak": "sentetik.md"}),
                      encoding="utf-8")
    kod, cikti = _cli(HAFIZA, [
        "oturum-kapat", "--not", UZUN_NOT + " Taslak TESLİME HAZIR durumda.",
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert not (tmp_path / "_oa" / ".oturum-kilidi").exists()


def test_b2_kilit_teslime_hazir_yoksa_makbuzsuz_normal_kapanis(tmp_path):
    """Kapanış notunda 'TESLİME HAZIR' iddiası yoksa B2-KİLİT hiç ateşlemez —
    makbuzsuz normal kapanış eskisi gibi geçer (geriye uyum)."""
    _ac(tmp_path)
    kod, cikti = _cli(HAFIZA, ["oturum-kapat", "--not", UZUN_NOT,
                               "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
