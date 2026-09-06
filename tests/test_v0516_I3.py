# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP I3: oa-mudafii MÜZAKERELİ ÇIKIŞLAR + BEYAN PROTOKOLÜ (P1-6/A-25)
ve oa-musteki-vekili CEZA↔HUKUK KÖPRÜSÜ (P1-7/A-26).

Bulgu kimlikleri (2026-09-06 denetimleri):
  P1-6 / A-25 — oa-mudafii savunma akışı unsur denetiminden doğrudan stratejiye
                geçiyordu; müzakereli/alternatif çıkışlar (uzlaştırma, etkin
                pişmanlık, seri muhakeme, basit yargılama, erteleme, HAGB, seçenek
                yaptırım) tek tabloda karşılaştırılmıyor, susma/beyan zamanlaması
                protokolü yoktu. "Müvekkilin en avantajlı sonucu çoğu dosyada beraat
                değildir" dersi metne girer; karar avukatındır (sistem karar VERMEZ).
  P1-7 / A-26 — oa-musteki-vekili ceza yolunu hukuk davasından kopuk ele alıyordu;
                "ceza yolu ne için?" stratejik sorusu (bekletici mesele, ceza hükmünün
                hukuk hâkimini bağlaması/bağlamaması, tazminat zamanaşımına etkisi,
                delil fabrikası, uzlaştırma masasında pazarlık/vazgeçmenin fiyatı) ilk
                adım olarak eklenir.

Bu grup HUKUKİ İÇERİK yazar; script yoktur ("model kurar, script denetler" — burada
script yalnız YAPISAL denetim yapar: başlık var mı, MCP teyit notu var mı, description
sınırı aşılmadı mı, aile_dogrula temiz mi). Hukuki yorum denetlenmez; sahte kesinlik
üretilmez. Tüm örnekler sentetiktir; hiçbir gerçek kişi/dosya anılmaz.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
MUDAFII = SKILLS / "oa-mudafii" / "SKILL.md"
MUSTEKI = SKILLS / "oa-musteki-vekili" / "SKILL.md"
AILE_DOGRULA = SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"

TEYIT_NOTU = "(Mevzuat MCP teyit 2026-09-06)"


def _oku(yol):
    return yol.read_text(encoding="utf-8", errors="replace")


def _description(txt):
    """Frontmatter description bloğunu (>- katlanmış) tek metin olarak döndürür —
    aile_dogrula.py ile aynı ölçüm mantığı (satırlar birleştirilir)."""
    import re
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    assert m, "frontmatter yok"
    dm = re.search(r"^description:\s*>-?\n((?:[ \t]+.*\n?)+)", m.group(1), re.M)
    assert dm, "description bloğu yok"
    return " ".join(s.strip() for s in dm.group(1).splitlines())


def _bolum(txt, baslik, sonraki_baslik_oneki="## "):
    """`baslik`ı içeren '## ' satırından bir sonraki '## ' satırına kadar olan bloğu
    döndürür."""
    satirlar = txt.splitlines()
    i = next(i for i, s in enumerate(satirlar)
             if s.startswith(sonraki_baslik_oneki) and baslik in s)
    j = next((k for k in range(i + 1, len(satirlar))
              if satirlar[k].startswith(sonraki_baslik_oneki)), len(satirlar))
    return "\n".join(satirlar[i:j])


# ═══════════════════ P1-6 / A-25 — EN AVANTAJLI SONUÇ HARİTASI ═══════════════════

def test_a25_en_avantajli_sonuc_haritasi_basligi_var():
    txt = _oku(MUDAFII)
    assert "EN AVANTAJLI SONUÇ HARİTASI" in txt


def test_a25_harita_unsur_denetiminden_sonra_strateji_akisindan_once():
    """Şartname: savunma akışında suçun unsur denetiminden (§2) SONRA, strateji
    (§6 akış / oa-strateji adımı) ÖNCE."""
    txt = _oku(MUDAFII)
    i_unsur = txt.index("## 2. Unsur denetimi")
    i_harita = txt.index("EN AVANTAJLI SONUÇ HARİTASI")
    i_akis = txt.index("## 6. Ceza savunması akışı")
    assert i_unsur < i_harita < i_akis


def test_a25_sekiz_cikis_yolu_ve_capalari_tabloda():
    """Sekiz yol: beraat / uzlaştırma / etkin pişmanlık / seri muhakeme / basit
    yargılama / erteleme / HAGB / seçenek yaptırım — her biri norm çıpasıyla."""
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    for yol, capa in (
        ("Beraat", "m.223"),
        ("Uzlaştırma", "m.253"),
        ("Etkin pişmanlık", "suç tipine göre madde teyit edilir"),
        ("Seri muhakeme", "m.250"),
        ("Basit yargılama", "m.251"),
        ("Erteleme", "TCK m.51"),
        ("HAGB", "m.231"),
        ("seçenek yaptırım", "TCK m.50"),
    ):
        assert yol.lower() in blok.lower(), f"yol eksik: {yol}"
        assert capa in blok, f"{yol}: çıpa eksik ({capa})"


def test_a25_tablo_bes_sutunlu_kim_ne_zaman_kosul_sonuc_maliyet():
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    baslik = next(s for s in blok.splitlines() if s.startswith("| Yol"))
    for sutun in ("Kim", "Ne zaman", "Koşul", "Sonuç", "maliyet"):
        assert sutun.lower() in baslik.lower(), f"sütun eksik: {sutun}"
    satirlar = [s for s in blok.splitlines() if s.startswith("| ") and "---" not in s]
    assert len(satirlar) >= 9, f"başlık + 8 yol beklenir, bulunan {len(satirlar)}"
    for s in satirlar:
        assert s.count("|") == 7, f"altı sütun bozuk: {s[:60]}"


def test_a25_beraat_cogu_dosyada_en_avantajli_degildir_cumlesi():
    """Saha dersi: müvekkilin en avantajlı sonucu çoğu dosyada beraat değildir."""
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    assert "çoğu dosyada beraat değildir" in blok


def test_a25_hagb_guncel_rejim_7589_ve_uygulama_aninda_teyit():
    """HAGB m.231 — 7589 s.K. (2026) rejimi MCP metninden okundu: ceza sınırı
    (iki yıl veya daha az hapis / adlî para), denetim süresi (beş yıl), zararın
    giderilmesi koşulu (m.231/6-c), erteleme/seçenek yaptırım yasağı (m.231/7),
    kanun yolu istinaf (m.272/3 saklı). Metinde sanığın kabulü şartı GÖRÜNMÜYOR —
    'uygulama anında teyit' şerhi zorunlu."""
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    assert "7589" in blok
    assert "beş yıl" in blok
    assert "m.231/6" in blok
    assert "m.231/7" in blok
    assert "m.272/3" in blok
    assert "uygulama anında teyit" in blok
    assert "7499" in blok  # eski rejimle karıştırmaya karşı açık uyarı


def test_a25_uzlastirma_kapsam_ve_sonuclari():
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    assert "m.253/3" in blok          # kapsam dışı (cinsel dokunulmazlık, ısrarlı takip, hakaret)
    assert "m.253/20" in blok         # müzakere beyanı delil olamaz
    assert "m.254" in blok            # kovuşturma evresinde uzlaşma → düşme
    assert "m.255" in blok            # yalnız uzlaşan yararlanır


def test_a25_seri_muhakeme_ve_basit_yargilama_ayirt_edildi():
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    assert "m.250/10" in blok         # kabul beyanı sonraki soruşturmada delil olamaz
    assert "yarı oranında" in blok    # seri muhakeme indirimi (m.250/4)
    assert "dörtte bir" in blok       # basit yargılama indirimi (m.251/3)
    assert "m.251/4" in blok          # basit yargılamada HAGB: yazılı karşı çıkmama


def test_a25_her_yol_icin_mcp_teyit_notu_var():
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    assert TEYIT_NOTU in blok
    assert blok.count("Mevzuat MCP teyit") >= 8, \
        "her yolun normu ayrı teyit notu taşımalı (>=8)"


def test_a25_harita_karar_materyali_karar_avukatin():
    blok = _bolum(_oku(MUDAFII), "EN AVANTAJLI SONUÇ HARİTASI")
    assert "karar materyali" in blok.lower()
    assert "karar avukat" in blok.lower()


# ═══════════════════ P1-6 / A-25 — SUSMA / BEYAN ZAMANLAMASI ═══════════════════

def test_a25_susma_beyan_zamanlamasi_basligi_var():
    txt = _oku(MUDAFII)
    assert "SUSMA / BEYAN ZAMANLAMASI" in txt


def test_a25_susma_hakki_m147_1_e_capasi():
    blok = _bolum(_oku(MUDAFII), "SUSMA / BEYAN ZAMANLAMASI")
    assert "m.147/1-e" in blok
    assert TEYIT_NOTU in blok


def test_a25_sistem_karar_vermez_secenek_ve_riskleri_listeler():
    """Erken beyan = kilitlenme; geç beyan = inandırıcılık — iki kutup da yazılı;
    sistem KARAR VERMEZ; DURUM «Avukat Kararı Bekleyen»."""
    blok = _bolum(_oku(MUDAFII), "SUSMA / BEYAN ZAMANLAMASI")
    assert "KARAR VERMEZ" in blok
    assert "kilitlen" in blok.lower()
    assert "inandırıcılık" in blok.lower()
    assert "Avukat Kararı Bekleyen" in blok


def test_a25_susma_aleyhe_yorumlanamaz_ve_layer0_sinir():
    """Beyanın bizzat verilmesi avukata/müvekkile aittir (Layer 0); protokol beyan
    metni YAZMAZ, karar materyali üretir."""
    blok = _bolum(_oku(MUDAFII), "SUSMA / BEYAN ZAMANLAMASI")
    assert "aleyhine yorumlanamaz" in blok or "aleyhine yorumlanmaz" in blok
    assert "Layer 0" in blok or "oa-gizlilik" in blok


# ═══════════════════ P1-7 / A-26 — CEZA YOLU NE İÇİN? ═══════════════════

def test_a26_ceza_yolu_ne_icin_basligi_var_ve_ilk_adim():
    """Şartname: stratejik soru İLK adımdır — §1 iddia duruşundan ÖNCE gelir."""
    txt = _oku(MUSTEKI)
    assert "CEZA YOLU NE İÇİN?" in txt
    assert txt.index("CEZA YOLU NE İÇİN?") < txt.index("## 1. İddia/müşteki duruşu")


def test_a26_bes_eksen_ve_capalari():
    blok = _bolum(_oku(MUSTEKI), "CEZA YOLU NE İÇİN?")
    assert "HMK m.165" in blok and "bekletici" in blok.lower()          # (a)
    assert "TBK m.74" in blok                                            # (b)
    assert "TBK m.72" in blok                                            # (c)
    assert "delil fabrikası" in blok.lower()                             # (d)
    assert "TCK m.73" in blok and "m.253" in blok                        # (e)


def test_a26_tbk_m74_dogru_yonde_yazildi():
    """TBK m.74 metni: hukuk hâkimi ceza hukukunun sorumluluk hükümleriyle ve
    BERAAT kararıyla BAĞLI DEĞİLDİR; kusur değerlendirmesi ve zarar belirlemesi de
    bağlamaz. Yerleşik içtihat: kesinleşen MAHKÛMİYET hükmüyle saptanan MADDİ OLGU
    bağlar (Yargı MCP künye teyidi, snippet düzeyi). Ters yönde yazılırsa müşteki
    yanlış beklentiyle ceza yoluna sokulur."""
    blok = _bolum(_oku(MUSTEKI), "CEZA YOLU NE İÇİN?")
    assert "bağlı değildir" in blok or "bağlamaz" in blok
    assert "beraat" in blok.lower()
    assert "maddi olgu" in blok.lower()
    assert "mahkûmiyet" in blok.lower()
    # yanlış yön: "ceza hükmü hukuk hâkimini her hâlde bağlar" türü mutlak cümle yok
    assert "her hâlde bağlar" not in blok
    assert "kesinlikle bağlar" not in blok


def test_a26_tbk_m72_uzun_ceza_zamanasimi_yonu_dogru():
    """TBK m.72/1 son cümle: tazminat ceza kanunlarının daha uzun zamanaşımı
    öngördüğü bir fiilden doğmuşsa O zamanaşımı uygulanır."""
    blok = _bolum(_oku(MUSTEKI), "CEZA YOLU NE İÇİN?")
    assert "daha uzun" in blok
    assert "iki yıl" in blok and "on yıl" in blok


def test_a26_vazgecmenin_fiyati_tck_m73_sonuclari():
    """TCK m.73/4-7: vazgeçme davayı düşürür; kesinleşme sonrası vazgeçme infaza
    engel değil; iştirakte diğerlerini kapsar; kabul etmeyen sanığı etkilemez;
    şahsi haklardan da vazgeçildiği açıklanmışsa hukuk davası açılamaz."""
    blok = _bolum(_oku(MUSTEKI), "CEZA YOLU NE İÇİN?")
    assert "düşürür" in blok
    assert "infaz" in blok.lower()
    assert "şahsi hak" in blok.lower()
    assert "m.73/7" in blok
    assert "m.253/19" in blok   # uzlaşma → tazminat davası açılamaz / ilam niteliği


def test_a26_her_norm_teyitli_tarihli():
    blok = _bolum(_oku(MUSTEKI), "CEZA YOLU NE İÇİN?")
    assert TEYIT_NOTU in blok
    assert blok.count("Mevzuat MCP teyit") >= 5, "beş eksenin her normu teyit notu taşımalı"


def test_a26_karar_materyali_karar_avukatin():
    blok = _bolum(_oku(MUSTEKI), "CEZA YOLU NE İÇİN?")
    assert "karar materyali" in blok.lower()
    assert "karar avukat" in blok.lower() or "karar Av." in blok


# ═══════════════════ ORTAK — description sınırı, gövde kuralı, aile_dogrula ══════

def test_description_850_karakter_altinda_iki_skillde():
    """aile_dogrula Fable tıraş sınırı (>850 = HATA). Yeni içerik GÖVDEYE eklenir."""
    for yol in (MUDAFII, MUSTEKI):
        d = _description(_oku(yol))
        assert len(d) <= 850, f"{yol.parent.name}: description {len(d)} karakter"


def test_yeni_basliklar_descriptiona_sizmadi():
    for yol, baslik in ((MUDAFII, "EN AVANTAJLI SONUÇ HARİTASI"),
                        (MUDAFII, "SUSMA / BEYAN ZAMANLAMASI"),
                        (MUSTEKI, "CEZA YOLU NE İÇİN?")):
        d = _description(_oku(yol))
        assert baslik not in d, f"{yol.parent.name}: '{baslik}' description'a yazılmış"


def test_script_yok_model_kurar_ayrimi_korundu():
    """Bu parçalarda script yoktur; SKILL.md'ler yeni bölümde script anmaz
    (aile_dogrula 'anılan script var mı' kapısına takılmasın; karar materyali
    üretilir, karar avukatın)."""
    for yol, baslik in ((MUDAFII, "EN AVANTAJLI SONUÇ HARİTASI"),
                        (MUDAFII, "SUSMA / BEYAN ZAMANLAMASI"),
                        (MUSTEKI, "CEZA YOLU NE İÇİN?")):
        blok = _bolum(_oku(yol), baslik)
        assert "scripts/" not in blok, f"{yol.parent.name}/{baslik}: script anılıyor"
        assert "exit 1" not in blok


def test_anonimlik_yeni_bolumlerde_gercek_kunye_yok():
    """m.7: gerçek esas/karar no ve kişi adı yok; içtihat künyesi yalnız Yargıtay
    daire+E/K biçiminde (kamuya açık) anılabilir, dosya no anılamaz."""
    import re
    for yol, baslik in ((MUDAFII, "EN AVANTAJLI SONUÇ HARİTASI"),
                        (MUDAFII, "SUSMA / BEYAN ZAMANLAMASI"),
                        (MUSTEKI, "CEZA YOLU NE İÇİN?")):
        blok = _bolum(_oku(yol), baslik)
        assert not re.search(r"\bT\.?C\.?\s*\d{11}\b", blok)
        assert "Mahkemesi 20" not in blok  # 'X Mahkemesi 2024/1 E.' dosya künyesi yok


def test_aile_dogrula_temiz():
    r = subprocess.run([sys.executable, str(AILE_DOGRULA), str(SKILLS)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(REPO))
    assert r.returncode == 0, r.stdout + r.stderr
