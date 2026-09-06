# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP C2 (oa-kontrol): ATIF TANIYICI (K4) + AKIBET TÜKETİCİSİ (K5)
+ ÖRTÜŞME SAYACI (G11) + HÂKİM LENSİ / İLK SAYFA (A-21, P2-7) — belge.

Kapatılan bulgular (2026-09-06 denetim raporları, Hamle 3/4/11; Kararlar #3-#4):

  K4 (Hamle 3)  `kunye_ortak` üç yeni desen görür: (a) TARİH-ONLY
                («<merci> … dd.mm.yyyy tarihli kararı/ilamı»), (b) K-ONLY /
                E-ONLY («<merci>'nin YYYY/N sayılı kararı»), (c) BİRLEŞİK
                («YYYY/N-N sayılı», «YYYY/N-YYYY/N», «YYYY/N E., YYYY/N K.»).
                (c) esas+karar'a AYRIŞTIRILIR; (a)/(b) `ayristirilamayan_
                atiflar`'da yeni «EKSİK KÜNYE» sınıfıdır (Karar #3: tarih-only
                BLOK) → `ictihat_muhakeme_denetim` G2'de BLOK, `kunye_teyit`te
                TEYİTSİZ + exit 1. HGK/CGK esas biçimi («2020/9-111») tek sayı
                olarak korunur. Kendi-dosya-no istisnası korunur; mevzuat tarihi
                («28.02.2018 tarihli Resmî Gazete») BLOK üretmez (yanlış-BLOK
                yasağı — merci anılan satırla sınırlı).
  K5 (Hamle 4)  `akibet_denetimi`: D grubunun yazacağı «**AKIBET:**» /
                «**AKIBET-KAYNAK:**» satırları + kütük «AKIBET=» hücresi
                OKUNUR. LEHE+{bozuldu,kaldirildi}+atıf → [G5-AKIBET] BLOK;
                LEHE+kesinlesmedi → UYARI; ALEYHE+bozuldu → UYARI (cephanelik);
                AKIBET yoksa kapı ateşlemez (geriye uyum).
  G11 (Hamle 11) `ortusme_zenginligi_uyarisi` «(1)…;(2)…;(3)…» biçimini ve
                «;» ayraçlı iç sıralamayı sayar — üç maddelik parantezli
                örtüşme «yüzeysel» uyarısı üretmez; tek cümle yine üretir.
  A-21/P2-7     SKILL.md: C2 hakem brifine hâkim lensi ikinci pası; B listesine
                «İLK SAYFA + UZUNLUK testi» (bant, sayı değil).

Tüm fikstürler SENTETİKTİR (m.7); tempfile ile izole dizinlerde koşar,
depo dosyalarına yazılmaz.
"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
KONTROL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
SCRIPTS = KONTROL / "scripts"
SKILL_MD = KONTROL / "SKILL.md"


def _yukle(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ko = _yukle(SCRIPTS / "kunye_ortak.py", "v0516_kunye_ortak")
imd = _yukle(SCRIPTS / "ictihat_muhakeme_denetim.py", "v0516_ictihat_muhakeme_denetim")


def _cli(script, args, cwd):
    cp = subprocess.run(
        [sys.executable, str(script)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ═══════════════════════════ K4 — ATIF TANIYICI ═══════════════════════════

# 9 biçim — her biri TEK TEK tanınmalı. TAM olanlar `esas_karar_atiflari`
# ile (esas+karar), EKSİK olanlar `ayristirilamayan_atiflar` ile ("EKSİK
# KÜNYE" sınıfı) GÖRÜLÜR; hiçbiri "atıf yok — kapı AÇIK" ile geçemez.
K4_TAM = [
    ("e_nokta_k_nokta", "Yargıtay 9. HD, E. 2020/1111, K. 2021/2222 sayılı kararı",
     "2020/1111", "2021/2222"),
    ("e_iki_nokta", "Yargıtay 9. HD, E: 2020/1111, K: 2021/2222 sayılı kararı",
     "2020/1111", "2021/2222"),
    ("esas_karar_kucuk", "Yargıtay 9. hd esas 2020/1111 karar 2021/2222",
     "2020/1111", "2021/2222"),
    ("ek_birlesik_iki_yil", "Yargıtay 9. HD'nin 2020/1111-2021/2222 sayılı kararı",
     "2020/1111", "2021/2222"),
    ("ek_birlesik_ayni_yil", "Yargıtay 9. HD'nin 2019/4444-5555 sayılı kararı",
     "2019/4444", "2019/5555"),
    ("ek_sonek_virgul", "Yargıtay 9. HD'nin 2020/1111 E., 2021/2222 K. sayılı kararı",
     "2020/1111", "2021/2222"),
    ("hgk_daire_sira", "Yargıtay HGK, E. 2020/9-111, K. 2021/222 sayılı kararı",
     "2020/9-111", "2021/222"),
]


@pytest.mark.parametrize("ad,metin,esas,karar", K4_TAM, ids=[t[0] for t in K4_TAM])
def test_k4_tam_kunye_bicimleri_esas_karar_ayristirilir(ad, metin, esas, karar):
    atiflar = ko.esas_karar_atiflari(metin)
    assert atiflar, f"{ad}: künye hiç görülmedi"
    assert atiflar[0]["esas"] == esas, f"{ad}: esas → {atiflar}"
    assert atiflar[0]["karar"] == karar, f"{ad}: karar → {atiflar}"
    assert ko.ayristirilamayan_atiflar(metin) == [], f"{ad}: tam künye EKSİK sanıldı"


def test_k4_aym_basvuru_no_taninir():
    atiflar = ko.esas_karar_atiflari("AYM, B. No: 2019/12345, 12/03/2021 tarihli kararı")
    assert atiflar and atiflar[0]["kunye_turu"] == "aym_bb"
    assert atiflar[0]["esas"] == "2019/12345"
    assert ko.ayristirilamayan_atiflar(
        "AYM, B. No: 2019/12345, 12/03/2021 tarihli kararı") == []


def test_k4_aihm_application_no_taninir():
    metin = "AİHM, Örnek/Türkiye, Application no. 1234/05, 12.03.2019 tarihli kararı"
    atiflar = ko.esas_karar_atiflari(metin)
    assert atiflar and atiflar[0]["kunye_turu"] == "aihm_basvuru"
    assert ko.ayristirilamayan_atiflar(metin) == []


K4_EKSIK = [
    ("tarih_only_karar", "Yargıtay 9. HD'nin 12.03.2019 tarihli kararı bu yöndedir.", "tarih-only"),
    ("tarih_only_ilam", "Yargıtay 9. HD'nin 12.03.2019 tarihli ilamı bu yöndedir.", "tarih-only"),
    ("gunlu_karar", "Yargıtay HGK'nın 05.06.2018 günlü kararı uygulanmalıdır.", "tarih-only"),
    ("k_only_etiketli", "Yargıtay 9. HD'nin K. 2021/2222 sayılı kararı emsaldir.", "K-only"),
    ("e_only_etiketli", "Yargıtay 9. HD'nin E. 2020/1111 sayılı kararı emsaldir.", "E-only"),
    ("tek_sayi_etiketsiz", "Danıştay 8. Daire'nin 2019/4444 sayılı kararı emsaldir.", "E/K belirsiz"),
    ("hgk_etiketsiz_birlesik", "Yargıtay HGK'nın 2019/4-123 sayılı kararı emsaldir.", "E/K belirsiz"),
]


@pytest.mark.parametrize("ad,metin,alt", K4_EKSIK, ids=[t[0] for t in K4_EKSIK])
def test_k4_eksik_kunye_sinifi(ad, metin, alt):
    """(a) tarih-only ve (b) K-only/E-only → «EKSİK KÜNYE» sınıfı (Karar #3).
    Yapı mevcut sınıflarla AYNIDIR (satir_no/metin/sebep) + «sinif» alanı."""
    izler = ko.ayristirilamayan_atiflar(metin)
    assert izler, f"{ad}: EKSİK künye görülmedi (fail-OPEN)"
    iz = izler[0]
    assert iz["satir_no"] == 1
    assert set(iz) >= {"satir_no", "metin", "sebep", "sinif"}
    assert iz["sinif"] == "EKSİK KÜNYE", iz
    assert alt in iz["sebep"], iz


def test_k4_ardisik_satirlarda_birlesik_ve_hgk_kunye_karismaz():
    """Regresyon (K4 entegrasyonu, 2026-09-07 saha koşusu): birleşik künye
    satırının hemen ardından gelen HGK künyesi, 70 karakterlik merci
    geri-bakış penceresi satır sonunu aştığı için önceki satırın «9. HD»
    mercisini alıyor, spanı önceki satıra taşıyor ve birleşik künyeyi örtüp
    onu sahte «EKSİK KÜNYE» yapıyordu. Pencere artık SATIRLA sınırlı: iki
    künye ayrı ayrı, doğru daire ile ayrışır; hiçbiri EKSİK değildir."""
    metin = ("Yargıtay 9. HD'nin 2020/1111-2021/2222 sayılı kararı emsaldir.\n"
             "Yargıtay HGK, E. 2020/9-111, K. 2021/222 sayılı kararı da aynı yöndedir.")
    atiflar = ko.esas_karar_atiflari(metin)
    assert [(a["esas"], a["karar"], a["satir_no"]) for a in atiflar] == [
        ("2020/1111", "2021/2222", 1), ("2020/9-111", "2021/222", 2)], atiflar
    assert atiflar[0]["daire_key"] == ("9", "HD")
    assert atiflar[1]["daire_key"] is None          # HGK — daire yok, «9. HD» sızmaz
    assert ko.ayristirilamayan_atiflar(metin) == []
    # ters sıra da simetrik
    ters = metin.split("\n")[1] + "\n" + metin.split("\n")[0]
    assert [(a["esas"], a["karar"]) for a in ko.esas_karar_atiflari(ters)] == [
        ("2020/9-111", "2021/222"), ("2020/1111", "2021/2222")]
    assert ko.ayristirilamayan_atiflar(ters) == []


def test_k4_ardisik_satir_kunye_teyit_ikisi_de_teyitli(tmp_path):
    """Uçtan uca: iki ardışık künye kütükte varsa ikisi de TEYİTLİ, exit 0."""
    _teyit_iskelesi(
        tmp_path,
        "Yargıtay 9. HD'nin 2020/1111-2021/2222 sayılı kararı emsaldir.\n"
        "Yargıtay HGK, E. 2020/9-111, K. 2021/222 sayılı kararı da aynı yöndedir.\n",
        kutuk_satiri="| 2026-09-06T10:00:00 | ictihat_getir | s | Yargıtay 9. HD E. 2020/1111 "
                     "K. 2021/2222 DAMGA=LEHE | [döküm](_oa/teyit/dokum/k.md) |\n"
                     "| 2026-09-06T10:01:00 | ictihat_getir | s | Yargıtay HGK E. 2020/9-111 "
                     "K. 2021/222 DAMGA=LEHE | [döküm](_oa/teyit/dokum/h.md) |")
    kod, cikti = _cli(SCRIPTS / "kunye_teyit.py", ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, cikti
    assert "TEYİTLİ 2" in cikti and "EKSİK KÜNYE" not in cikti


def test_k4_hgk_etiketsiz_birlesik_e_k_diye_bolunmez():
    """Kurul (HGK/CGK/İBK…) mercisinde «YYYY/N-N» daire-sıra biçimli TEK esas
    numarasıdır; E-K birleşik sanılıp bölünmez (yanlış-teyit yasağı)."""
    assert ko.esas_karar_atiflari("Yargıtay HGK'nın 2019/4-123 sayılı kararı") == []


K4_TEMIZ = [
    ("rg_tarihi_merci_ile", "Yargıtay 9. HD'nin yerleşik içtihadı, 28.02.2018 tarihli "
                            "Resmî Gazete'de yayımlanan 7101 sayılı Kanun'la uyumludur."),
    ("rg_tarihi_mercisiz", "28.02.2018 tarihli Resmî Gazete'de yayımlanan Yönetmelik m.8."),
    ("tarihli_ihtarname", "Davalı 05.12.2024 tarihli ihtarnameyi tebliğ almıştır."),
    ("merci_var_iddia_yok", "Yargıtay'ın yerleşik içtihadı bu yöndedir."),
    ("kendi_dosya_no", "MERCİ: Ankara BAM 10. HD\nDOSYA NO: 2024/123"),
    ("kendi_esas_no_esas_etiketli", "ESAS NO: 2025/354 Esas — Örnek 3. İş Mahkemesi"),
]


@pytest.mark.parametrize("ad,metin", K4_TEMIZ, ids=[t[0] for t in K4_TEMIZ])
def test_k4_yanlis_blok_uretmez(ad, metin):
    """«tarihli» kelimesi mevzuat/RG/ihtarname tarihiyle karışmaz; merci
    anılmayan satır ve dilekçenin KENDİ künye bloğu asla EKSİK KÜNYE değildir."""
    assert ko.ayristirilamayan_atiflar(metin) == [], f"{ad}: yanlış-BLOK"


# ── K4 uçtan uca: kunye_teyit + ictihat_muhakeme_denetim ────────────────────

def _teyit_iskelesi(tmp_path, taslak_metin, kutuk_satiri=None):
    teyit = tmp_path / "_oa" / "teyit"
    (teyit / "dokum").mkdir(parents=True)
    govde = ("# Künye Teyit Kütüğü\n| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
             "|---|---|---|---|---|\n")
    if kutuk_satiri:
        govde += kutuk_satiri + "\n"
    (teyit / "kunye-teyit.md").write_text(govde, encoding="utf-8")
    taslak = tmp_path / "taslak.md"
    taslak.write_text(taslak_metin, encoding="utf-8")
    return taslak


def test_k4_kunye_teyit_tarih_only_teyitsiz_exit1(tmp_path):
    _teyit_iskelesi(tmp_path, "Yargıtay 9. HD'nin 12.03.2019 tarihli kararı bu yöndedir.\n")
    kod, cikti = _cli(SCRIPTS / "kunye_teyit.py", ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1, cikti
    assert "EKSİK KÜNYE" in cikti
    assert "TEYİTSİZ" in cikti


def test_k4_kunye_teyit_k_only_kutukte_izi_olsa_bile_exit1(tmp_path):
    """K-only atıf, kütükte karar no'su geçse bile TEYİTLİ sayılamaz —
    esas+karar tamamlanmadan mekanik teyit YAPILAMAZ (fail-closed)."""
    _teyit_iskelesi(
        tmp_path, "Yargıtay 9. HD'nin K. 2021/2222 sayılı kararı emsaldir.\n",
        kutuk_satiri="| 2026-09-06T10:00:00 | ictihat_getir | sorgu | Yargıtay 9. HD "
                     "E. 2020/1111 K. 2021/2222 DAMGA=LEHE | [döküm](_oa/teyit/dokum/k.md) |")
    kod, cikti = _cli(SCRIPTS / "kunye_teyit.py", ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1, cikti
    assert "EKSİK KÜNYE" in cikti


def test_k4_kunye_teyit_rg_tarihi_blok_degil(tmp_path):
    _teyit_iskelesi(tmp_path, "Yargıtay 9. HD'nin yerleşik içtihadı, 28.02.2018 tarihli "
                              "Resmî Gazete'de yayımlanan değişiklikle uyumludur.\n")
    kod, cikti = _cli(SCRIPTS / "kunye_teyit.py", ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, cikti
    assert "EKSİK KÜNYE" not in cikti


def test_k4_kunye_teyit_kendi_dosya_no_istisnasi_korunur(tmp_path):
    _teyit_iskelesi(tmp_path, "DOSYA NO : 2024/123 Esas\n\nBaşka atıf yok.\n")
    kod, cikti = _cli(SCRIPTS / "kunye_teyit.py", ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, cikti
    assert "MUAF" in cikti.upper()


def test_k4_muhakeme_denetim_g2_eksik_kunye_blok(tmp_path):
    """ictihat_muhakeme_denetim G2: EKSİK KÜNYE → BLOK; mesaj «esas+karar
    tamamlanmalı»yı ve Yargıtay birleşik biçimi ipucunu taşır."""
    (tmp_path / "_oa" / "cikti").mkdir(parents=True)
    (tmp_path / "_oa" / "teyit" / "dokum").mkdir(parents=True)
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Yargıtay 9. HD'nin 12.03.2019 tarihli kararı bu yöndedir.\n",
                      encoding="utf-8")
    kod, cikti = _cli(SCRIPTS / "ictihat_muhakeme_denetim.py",
                      ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1, cikti
    assert "EKSİK KÜNYE" in cikti and "esas+karar tamamlanmalı" in cikti
    assert "birleşik" in cikti


def test_k4_muhakeme_denetim_rg_tarihi_blok_degil(tmp_path):
    (tmp_path / "_oa" / "cikti").mkdir(parents=True)
    (tmp_path / "_oa" / "teyit" / "dokum").mkdir(parents=True)
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Yargıtay'ın içtihadı 28.02.2018 tarihli Resmî Gazete'deki "
                      "değişiklikle uyumludur.\n", encoding="utf-8")
    kod, cikti = _cli(SCRIPTS / "ictihat_muhakeme_denetim.py",
                      ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, cikti
    assert "EKSİK KÜNYE" not in cikti


# ═══════════════════════════ K5 — AKIBET TÜKETİCİSİ ═══════════════════════

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
ATIFLI = ("İstinaf sebeplerimiz Yargıtay 4. HD E. 2023/1234 K. 2023/5678 "
          "sayılı kararına dayanmaktadır.\n")
ATIFSIZ = "Bu dilekçede içtihat atfı bulunmamaktadır.\n"


def _akibet_koku(damga="LEHE", akibet=None, akibet_kaynak=None, kutuk_akibet=None):
    """D grubunun `oa_hafiza.py teyit --akibet` biçimi — satırı burada kendimiz
    yazıyoruz: muhakeme kaydına «**AKIBET:**»/«**AKIBET-KAYNAK:**», kütük
    sonuç hücresine «AKIBET=<enum>» (DAMGA= hücresi gibi)."""
    kok = pathlib.Path(tempfile.mkdtemp())
    dokum = kok / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True)
    (dokum / "kaynak.md").write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 tam metni...\n", encoding="utf-8")
    hucre = f"Yargıtay 4. HD E. 2023/1234 K. 2023/5678 DAMGA={damga} DOKUM-SINIFI=tam-metin"
    if kutuk_akibet:
        hucre += f" AKIBET={kutuk_akibet}"
    (kok / "_oa" / "teyit" / "kunye-teyit.md").write_text(
        "# Künye Teyit Kütüğü\n| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
        "|---|---|---|---|---|\n"
        f"| 2026-09-06T10:00:00 | ictihat_getir | sorgu | {hucre} | "
        "[döküm](_oa/teyit/dokum/kaynak.md) |\n", encoding="utf-8")
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    satirlar = ["# 01 — İçtihat Muhakeme Kaydı", "",
                f"**KUNYE:** {KUNYE}",
                "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
                f"**DAMGA:** {damga}"]
    if akibet:
        satirlar.append(f"**AKIBET:** {akibet}")
    if akibet_kaynak:
        satirlar.append(f"**AKIBET-KAYNAK:** {akibet_kaynak}")
    satirlar += ["", "## İLGİLİ-KISIM", "...ilgili kısım...", "",
                 "## DAVAYA-BAĞ",
                 "(1) aynı sözleşme türü; (2) aynı kusur dağılımı; (3) aynı zarar kalemleri.",
                 "", "## AYIRT-ETME", "", ""]
    (cikti / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")
    return kok


def _muhakeme_cli(kok, taslak_metin):
    t = kok / "taslak.md"
    t.write_text(taslak_metin, encoding="utf-8")
    return _cli(SCRIPTS / "ictihat_muhakeme_denetim.py", [t, "--kok", kok], kok)


def test_k5_muhakeme_kaydi_akibet_alanlari_okunur():
    kok = _akibet_koku(akibet="bozuldu", akibet_kaynak="Yargıtay 4. HD, E. 2024/1, K. 2025/2")
    kayitlar, _ = imd.muhakeme_kayitlarini_yukle(str(kok / "_oa" / "cikti"))
    assert kayitlar[0].akibet == "bozuldu"
    assert "2024/1" in kayitlar[0].akibet_kaynak


def test_k5_lehe_bozuldu_atifta_blok():
    kok = _akibet_koku(damga="LEHE", akibet="bozuldu", akibet_kaynak="Yargıtay HGK 2024/1-2")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert kod == 1, out
    assert "[G5-AKIBET]" in out
    assert "LEHE dayanak olamaz" in out


def test_k5_lehe_kaldirildi_kutuk_hucresinden_blok():
    """AKIBET yalnız kütük «AKIBET=» hücresinde olsa bile (muhakeme kaydında
    satır yok) LEHE+kaldirildi+atıf → BLOK — kütük append-only tek kaynaktır."""
    kok = _akibet_koku(damga="LEHE", kutuk_akibet="kaldirildi")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert kod == 1, out
    assert "[G5-AKIBET]" in out and "kaldırılmış" in out


def test_k5_lehe_kesinlesmedi_uyari_bloklamaz():
    kok = _akibet_koku(damga="LEHE", akibet="kesinlesmedi")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert kod == 0, out
    assert "[G5-AKIBET]" in out
    assert "kanun yolu açık" in out


def test_k5_aleyhe_bozuldu_cephanelik_uyarisi_bloklamaz():
    kok = _akibet_koku(damga="ALEYHE", akibet="bozuldu")
    kod, out = _muhakeme_cli(kok, ATIFSIZ)
    assert "[G5-AKIBET]" in out and "cephanelik" in out
    assert "SONUÇ-EK: TESLİM ENGELİ — bozulmuş" not in out
    assert kod == 0, out


def test_k5_akibet_yoksa_kapi_ateslemez_geriye_uyum():
    kok = _akibet_koku(damga="LEHE")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert "[G5-AKIBET]" not in out
    assert kod == 0, out


def test_k5_lehe_kesinlesti_sessiz():
    kok = _akibet_koku(damga="LEHE", akibet="kesinlesti")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert "[G5-AKIBET]" not in out
    assert kod == 0, out


def test_k5_lehe_bozuldu_atifsiz_yalniz_uyari():
    kok = _akibet_koku(damga="LEHE", akibet="bozuldu")
    kod, out = _muhakeme_cli(kok, ATIFSIZ)
    assert "[G5-AKIBET]" in out
    assert "SONUÇ-EK: TESLİM ENGELİ — bozulmuş" not in out


def test_k5_taninmayan_akibet_degeri_gorunur_uyari_bloklamaz():
    """Enum dışı değer sessizce yutulmaz (görünür uyarı) ama uydurma bir
    kesinlik de üretilmez — BLOK değil (script hukuki yorum yapmaz)."""
    kok = _akibet_koku(damga="LEHE", akibet="belirsiz-deger")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert "[G5-AKIBET]" in out and "tanınmayan" in out
    assert kod == 0, out


def test_k5_akibet_denetimi_fonksiyon_sozlesmesi():
    """`akibet_denetimi(atiflar, kayitlar, kutuk)` → (bloklar, uyarilar)."""
    kok = _akibet_koku(damga="LEHE", akibet="bozuldu")
    kayitlar, _ = imd.muhakeme_kayitlarini_yukle(str(kok / "_oa" / "cikti"))
    atiflar = imd.taslaktaki_atiflari_bul(ATIFLI)
    bloklar, uyarilar = imd.akibet_denetimi(
        atiflar, kayitlar, str(kok / "_oa" / "teyit" / "kunye-teyit.md"))
    assert len(bloklar) == 1 and uyarilar == []
    bloklar, uyarilar = imd.akibet_denetimi([], kayitlar, None)
    assert bloklar == [] and len(uyarilar) == 1


def test_k5_kutukten_son_akibet_daire_ve_cift_no():
    kok = _akibet_koku(damga="LEHE", kutuk_akibet="kesinlesmedi")
    kutuk = str(kok / "_oa" / "teyit" / "kunye-teyit.md")
    assert ko.kutukten_son_akibet(kutuk, "2023/1234", "2023/5678", ("4", "HD")) == "kesinlesmedi"
    # farklı daire → eşleşmez; hiç yok → None
    assert ko.kutukten_son_akibet(kutuk, "2023/1234", "2023/5678", ("11", "HD")) is None
    assert ko.kutukten_son_akibet(kutuk, "2099/1", "2099/2") is None
    # DAMGA okuyucusu AKIBET eklemesinden etkilenmedi (geriye uyum)
    assert ko.kutukten_son_damga(kutuk, "2023/1234", "2023/5678", ("4", "HD")) == "LEHE"


# ═══════════════════════════ G11 — ÖRTÜŞME SAYACI ═════════════════════════

def _kayit(bag):
    class _K:
        davaya_bag = bag
    return _K()


def test_g11_parantezli_uc_madde_uyari_uretmez():
    bag = ("(1) her iki olayda da eser sözleşmesi var; (2) ayıp ihbarı süresinde "
           "yapılmış; (3) zarar kalemleri aynı biçimde tasnif edilmiş.")
    assert imd.ortusme_zenginligi_uyarisi(_kayit(bag)) is None


def test_g11_noktali_virgul_ayracli_uc_parca_uyari_uretmez():
    bag = ("aynı sözleşme türü; aynı kusur dağılımı; aynı zarar kalemleri "
           "ve aynı ispat düzeni")
    assert imd.ortusme_zenginligi_uyarisi(_kayit(bag)) is None


def test_g11_parantezli_iki_madde_yine_uyarir():
    bag = "(1) aynı sözleşme türü; (2) aynı kusur dağılımı."
    assert imd.ortusme_zenginligi_uyarisi(_kayit(bag)) is not None


def test_g11_tek_cumle_yine_uyarir():
    assert imd.ortusme_zenginligi_uyarisi(
        _kayit("Bu karar somut olaya uygulanır.")) is not None


def test_g11_eski_bicimler_korunur():
    assert imd.ortusme_zenginligi_uyarisi(_kayit("Nokta bir. Nokta iki. Nokta üç.")) is None
    assert imd.ortusme_zenginligi_uyarisi(_kayit("- a\n- b\n- c")) is None
    assert imd.ortusme_zenginligi_uyarisi(_kayit("")) is None


def test_g11_uctan_uca_parantezli_ortusme_uyarisiz():
    kok = _akibet_koku(damga="LEHE")   # DAVAYA-BAĞ: «(1)…;(2)…;(3)…»
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert kod == 0, out
    assert "DAVAYA-BAĞ (ÖRTÜŞME)" not in out


# ═══════════════════════════ BELGE — SKILL.md ═════════════════════════════

def _skill():
    return SKILL_MD.read_text(encoding="utf-8")


def test_skill_k4_eksik_kunye_sinifi_yazili():
    s = _skill()
    assert "EKSİK KÜNYE" in s
    assert "tarih-only" in s and "K-only" in s


def test_skill_g5_akibet_bolumu_yazili():
    s = _skill()
    assert "[G5-AKIBET]" in s
    assert "AKIBET" in s and "kesinlesmedi" in s and "bozuldu" in s


def test_skill_g11_ortusme_notu_yazili():
    assert "(1)" in _skill() and "ortusme_zenginligi_uyarisi" in _skill()


def test_skill_hakim_lensi_ikinci_pas_c2_brifte():
    s = _skill()
    c2 = s[s.index("## C2."):]
    assert "İKİNCİ PAS" in c2 or "ikinci pas" in c2.lower()
    c2l = c2.replace("İ", "i").lower()   # Türkçe İ → str.lower() 'i̇' üretir
    assert "on dakika" in c2l and "talep bloğu" in c2l
    assert "daire eğilimi" in c2l and "iş yükü" in c2l
    assert "lens" in c2l and "kapı değil" in c2l


def test_skill_ilk_sayfa_uzunluk_testi_b_listesinde():
    s = _skill()
    b = s[s.index("## B."):s.index("## C.")]
    assert "İLK SAYFA" in b and "UZUNLUK" in b
    assert "KB" in b and "bölüm sayısı" in b.lower()
    assert "bant" in b.lower()


# ═══════════════════ ONARIM TURU (hakem bulguları, 2026-09-07) ═════════════
#
# K4 REGRESYON (KRİTİK): `_YN`'nin kurul tire soneki «(?:-\d{1,6}(?!\s*/))?»
# lookahead'i GERİ İZLEMEYLE kısmi eşleşiyordu — «E. 2020/1111-2021/2222»
# girdisinde esas «2020/1111-202» (bozuk), karar kaybı, sahte EKSİK KÜNYE.
# Taban (80ac847) aynı girdide TAM künye veriyordu → geriye gidiş. Düzeltme:
# «-\d{1,6}\b(?!\s*/)» — kelime sınırı geri izlemeyi keser. Aşağıdaki iki test
# etiketli birleşik biçimi (K. etiketli / etiketsiz) kilitler.

def test_k4_onarim_etiketli_birlesik_e_k_noktali_tam_kunye():
    """«E. 2020/1111-2021/2222 K.» — Yargıtay'ın etiketli birleşik biçimi (sahada
    gerçek varyant). Taban bunu (2020/1111, 2021/2222) diye TAM ayrıştırıyordu;
    onarım öncesi dal «2020/1111-202» üretiyordu. Kanonik değer tabanla aynı."""
    metin = "Yargıtay 9. HD E. 2020/1111-2021/2222 K. sayılı kararı emsaldir."
    atiflar = ko.esas_karar_atiflari(metin)
    assert [(a["esas"], a["karar"]) for a in atiflar] == [("2020/1111", "2021/2222")], atiflar
    assert atiflar[0]["daire_key"] == ("9", "HD")
    assert ko.ayristirilamayan_atiflar(metin) == []


def test_k4_onarim_etiketli_birlesik_k_etiketsiz_tam_kunye():
    """«E. 2020/1111-2021/2222 sayılı» (K. etiketi yok) — esas tabanla aynı
    («2020/1111», kesik değil); tire sonrası «2021/2222» artık KARAR olarak
    tamamlanır (etiketli-birleşik yükseltmesi: esas-only atıf + hemen ardında
    «-YYYY/N» → tam künye; kurul dışı satır)."""
    metin = "Yargıtay 9. HD, E. 2020/1111-2021/2222 sayılı kararı emsaldir."
    atiflar = ko.esas_karar_atiflari(metin)
    assert len(atiflar) == 1, atiflar
    assert atiflar[0]["esas"] == "2020/1111", atiflar        # taban değeri — kesik DEĞİL
    assert atiflar[0]["karar"] == "2021/2222", atiflar
    assert ko.ayristirilamayan_atiflar(metin) == []


def test_k4_onarim_kurul_tire_soneki_korunur_cumle_sonu():
    """Düzeltme kurul biçimini bozmaz: «E. 2020/9-111» tek esas; cümle sonu
    noktası ve virgülle de."""
    for metin in ("Yargıtay HGK E. 2020/9-111 K. 2021/222.",
                  "Yargıtay CGK, E. 2020/9-111, K. 2021/222, T. 01.01.2021"):
        atiflar = ko.esas_karar_atiflari(metin)
        assert [(a["esas"], a["karar"]) for a in atiflar] == [("2020/9-111", "2021/222")], metin


# Yanlış-BLOK adayı (hakem notu): «Yerel mahkemenin 05.06.2024 tarihli kararı
# Yargıtay'ın yerleşik içtihadına aykırıdır.» istinaf/temyiz dilekçesinde ÇOK
# sık cümledir; tarih KENDİ dosyasının kararına aittir, merci yalnız genel
# içtihat anımıdır. Tarih-only tetiği artık «tarihi merciye ait» ise ateşler:
# merci tarihten ÖNCE aynı satırda anılmalı ve aradaki metinde başka bir
# mahkeme iyeliği («yerel mahkemenin», «ilk derece mahkemesinin») olmamalı.
K4_YEREL_TARIH_TEMIZ = [
    ("yerel_sonra_merci", "Yerel mahkemenin 05.06.2024 tarihli kararı Yargıtay'ın yerleşik "
                          "içtihadına aykırıdır."),
    ("ilk_derece_sonra_daire", "İlk derece mahkemesinin 05.06.2024 tarihli kararı Yargıtay "
                               "9. HD içtihadıyla bağdaşmaz."),
    ("merci_once_ama_yerel_arada", "Yargıtay 9. HD'nin bozma ilamına uyan yerel mahkemenin "
                                   "05.06.2024 tarihli kararı usule aykırıdır."),
]


@pytest.mark.parametrize("ad,metin", K4_YEREL_TARIH_TEMIZ, ids=[t[0] for t in K4_YEREL_TARIH_TEMIZ])
def test_k4_onarim_yerel_mahkeme_tarihli_karari_blok_degil(ad, metin):
    assert ko.ayristirilamayan_atiflar(metin) == [], f"{ad}: yanlış-BLOK"


def test_k4_onarim_merciye_ait_tarih_only_yine_blok():
    """Karşı kontrol: tarih GERÇEKTEN merciye aitse EKSİK KÜNYE kalır (Karar #3)."""
    for metin in ("Yargıtay 9. HD'nin 05.06.2024 tarihli kararı bu yöndedir.",
                  "İstanbul BAM 12. HD'nin 05.06.2024 tarihli kararı emsaldir.",
                  "Danıştay 8. Daire'nin 05.06.2024 günlü ilamı uygulanmalıdır."):
        izler = ko.ayristirilamayan_atiflar(metin)
        assert izler and izler[0]["sinif"] == "EKSİK KÜNYE" and "tarih-only" in izler[0]["sebep"], metin


def test_k4_onarim_yerel_tarih_kunye_teyit_ve_muhakeme_exit0(tmp_path):
    """Uçtan uca: iki kapı da bu cümleyi BLOK etmez."""
    cumle = "Yerel mahkemenin 05.06.2024 tarihli kararı Yargıtay'ın yerleşik içtihadına aykırıdır.\n"
    _teyit_iskelesi(tmp_path, cumle)
    kod, cikti = _cli(SCRIPTS / "kunye_teyit.py", ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, cikti
    assert "EKSİK KÜNYE" not in cikti
    (tmp_path / "_oa" / "cikti").mkdir(parents=True)
    kod, cikti = _cli(SCRIPTS / "ictihat_muhakeme_denetim.py",
                      ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, cikti
    assert "EKSİK KÜNYE" not in cikti


# K5 (hakem notu): kütükten okunan AKIBET tokenı da `_akibet_normalize`'dan
# geçmeli — D grubu Türkçe harfli («kesinleşti», «Geri-Çevrildi») yazarsa enum
# dışı sayılıp sahte «tanınmayan» uyarısı basılmasın; kayıt/kütük çapraz
# kontrolü de aynı normalizasyonla karşılaştırılsın.

def test_k5_onarim_kutuk_akibet_turkce_harfli_normalize_sessiz():
    kok = _akibet_koku(damga="LEHE", akibet="kesinleşti", kutuk_akibet="kesinleşti")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert "tanınmayan" not in out and "uyuşmuyor" not in out, out
    assert "[G5-AKIBET]" not in out
    assert kod == 0, out


def test_k5_onarim_kutuk_akibet_tireli_buyuk_harf_normalize_uyari():
    kok = _akibet_koku(damga="LEHE", kutuk_akibet="Geri-Çevrildi")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert "tanınmayan" not in out, out
    assert "[G5-AKIBET]" in out and "geri_cevrildi" in out
    assert kod == 0, out


def test_k5_onarim_kutuk_turkce_bozuldu_blok():
    """Normalize, BLOK yolunda da çalışır: kütük «AKIBET=Bozuldu» + LEHE + atıf → BLOK."""
    kok = _akibet_koku(damga="LEHE", kutuk_akibet="Bozuldu")
    kod, out = _muhakeme_cli(kok, ATIFLI)
    assert kod == 1, out
    assert "LEHE dayanak olamaz" in out
