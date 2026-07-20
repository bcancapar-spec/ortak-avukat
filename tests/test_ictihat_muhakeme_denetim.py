# -*- coding: utf-8 -*-
"""oa-kontrol / ictihat_muhakeme_denetim.py için ALTIN VAKA testleri (M2-2).

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
Ana garanti uçtan-uca (CLI/exit kodu) davranışında yaşar (main() sys.exit çağırır),
bu yüzden testler subprocess ile CLI'yi de doğrular; ayrıca paylaşımlı
`kunye_ortak.py` yardımcısının çıkarım/normalizasyon davranışı doğrudan da
doğrulanır (M2-3'te `kunye_teyit.py` bu modülü kullanacağı için sözleşmesi
burada sabitlenir).
"""
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
SCRIPT = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"
KUNYE_ORTAK = SKILLS / "oa-kontrol" / "scripts" / "kunye_ortak.py"


def _load(yol, ad):
    assert yol.is_file(), f"dosya yok: {yol}"
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


imd = _load(SCRIPT, "ictihat_muhakeme_denetim")
ko = _load(KUNYE_ORTAK, "kunye_ortak")


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
TASLAK_METIN = (
    "Somut olayda Yargıtay 4. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı "
    "emsal teşkil etmektedir.\n"
)


def _bos_iskelet(tmp_path):
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    return dokum_dizin, cikti_dizin


def _kur(tmp_path, damga="LEHE", ayirt_etme="", kaynak_izi_var=True,
         kaynak_dosya_ad="kaynak.md", ilgili_kisim="...ilgili kısım metni...",
         illiyet="...illiyet açıklaması...", damga_satiri=True, kaynak_icerik=None,
         kaynak_izi_deger_override=None):
    """Tek atıflı, tek muhakeme kayıtlı bir _oa iskeleti + taslak kurar; taslak
    dosya yolunu döndürür (CLI'ye cwd-göreli 'taslak.md' olarak verilir)."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)

    kaynak_izi_deger = kaynak_izi_deger_override
    if kaynak_izi_var and kaynak_izi_deger_override is None:
        kaynak_yol = dokum_dizin / kaynak_dosya_ad
        icerik = kaynak_icerik if kaynak_icerik is not None else (
            "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni "
            "burada yer almaktadır...\n"
        )
        kaynak_yol.write_text(icerik, encoding="utf-8")
        kaynak_izi_deger = "_oa/teyit/dokum/" + kaynak_dosya_ad

    satirlar = ["# 01 — İçtihat Muhakeme Kaydı", "", f"**KUNYE:** {KUNYE}"]
    if kaynak_izi_deger:
        satirlar.append(f"**KAYNAK-IZI:** {kaynak_izi_deger}")
    if damga_satiri:
        satirlar.append(f"**DAMGA:** {damga}")
    satirlar.append("")
    if ilgili_kisim:
        satirlar += ["## İLGİLİ-KISIM", ilgili_kisim, ""]
    if illiyet:
        satirlar += ["## İLLİYET", illiyet, ""]
    satirlar += ["## AYIRT-ETME", ayirt_etme or "", ""]

    (cikti_dizin / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")

    taslak = tmp_path / "taslak.md"
    taslak.write_text(TASLAK_METIN, encoding="utf-8")
    return taslak


# ── POZİTİF: temiz zincir geçer ─────────────────────────────────────────────

def test_temiz_lehe_zincir_gecer_exit0(tmp_path):
    _kur(tmp_path, damga="LEHE")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "TESLİM ENGELİ" not in cikti
    assert "OK 1" in cikti


def test_aleyhe_ayirt_dolu_ayirt_etme_ile_gecer(tmp_path):
    _kur(tmp_path, damga="ALEYHE-AYIRT",
         ayirt_etme="Emsal kararda davacı %70 kusurlu; dosyamızda davacı kusuru yok — "
                    "olgusal zemin farklı olduğundan emsal karar uygulanmaz.")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti


# ── NEGATİF: çıplak atıf — hiçbir muhakeme kaydı yok ────────────────────────

def test_ciplak_atif_kayit_yok_engel(tmp_path):
    _bos_iskelet(tmp_path)
    taslak = tmp_path / "taslak.md"
    taslak.write_text(TASLAK_METIN, encoding="utf-8")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "çıplak" in cikti.lower()
    assert "TESLİM ENGELİ" in cikti


# ── NEGATİF: DAMGA=ALEYHE — teslim engeli (anayasa m.6) ────────────────────

def test_aleyhe_teslim_engeli(tmp_path):
    _kur(tmp_path, damga="ALEYHE")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "ALEYHE" in cikti
    assert "m.6" in cikti


# ── NEGATİF: DAMGA=ALEYHE-AYIRT ama AYIRT-ETME boş → fail-closed engel ─────

def test_aleyhe_ayirt_eksik_ayirt_etme_engel(tmp_path):
    _kur(tmp_path, damga="ALEYHE-AYIRT", ayirt_etme="")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "AYIRT-ETME" in cikti


# ── NEGATİF: DAMGA yok (damgasız kayıt) → fail-closed engel ────────────────

def test_damgasiz_fail_closed_engel(tmp_path):
    _kur(tmp_path, damga_satiri=False)
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "muhakeme edilmemiş" in cikti.lower()


# ── NEGATİF: DAMGA geçersiz enum değeri → fail-closed engel ────────────────

def test_damga_gecersiz_deger_fail_closed_engel(tmp_path):
    _kur(tmp_path, damga="BILINMEYEN-DEGER")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "geçersiz" in cikti.lower()
    assert "muhakeme edilmemiş" in cikti.lower()


# ── NEGATİF: KAYNAK-IZI dosyası dökum dizininde yok ─────────────────────────

def test_kaynak_izi_dosyasi_yok_engel(tmp_path):
    _kur(tmp_path, kaynak_izi_var=False)
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "KAYNAK-IZI" in cikti


# ── NEGATİF: KAYNAK-IZI var ama içeriğinde künye (esas/karar) geçmiyor ─────

def test_kaynak_izi_kunye_icermiyor_engel(tmp_path):
    _kur(tmp_path, kaynak_icerik="Bambaşka bir kararın tam metni; hiçbir esas/karar no yok.\n")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "dize olarak geçmiyor" in cikti


# ── NEGATİF: KAYNAK-IZI dökum dizini DIŞINDA bir yola işaret ediyor ────────

def test_kaynak_izi_dokum_disinda_engel(tmp_path):
    taslak = _kur(tmp_path, kaynak_izi_deger_override="_oa/cikti/sahte-kaynak.md")
    # dökum dışında (ör. _oa/cikti içinde) bir "sahte" kaynak dosyası
    disarida = tmp_path / "_oa" / "cikti" / "sahte-kaynak.md"
    disarida.write_text("Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 ...\n", encoding="utf-8")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "dökum dizini dışında" in cikti.lower() or "dokum dizini dışında" in cikti.lower()


# ── NEGATİF: İLGİLİ-KISIM / İLLİYET alanları boş → G2 engeli ───────────────

def test_ilgili_kisim_bos_engel(tmp_path):
    _kur(tmp_path, ilgili_kisim="")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "İLGİLİ-KISIM" in cikti


def test_illiyet_bos_engel(tmp_path):
    _kur(tmp_path, illiyet="")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "İLLİYET" in cikti


# ── KRİTİK — çok-daireli çakışma: esas/karar no'su AYNI, DAİRE FARKLI ──────
# Türk yargı sisteminde esas/karar no'ları HER dairede yılda sıfırdan başlar;
# aynı numaralar onlarca farklı dairede aynı anda var olabilir. Bu testler
# daire-farkında eşleştirmenin ALEYHE bir kaydın yanlışlıkla "temiz" başka
# bir dairenin kaydı arkasına saklanarak sızmasını engellediğini doğrular.

def _coklu_kunye_kur(tmp_path, kayitlar, taslak_metin=TASLAK_METIN):
    """Birden fazla muhakeme kaydı (farklı daire/damga, AYNI esas/karar) +
    tek taslak kurar. `kayitlar`: [{"kunye":..., "damga":..., ...}, ...]."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    for i, k in enumerate(kayitlar, start=1):
        kaynak_dosya_ad = k.get("kaynak_dosya_ad", f"kaynak{i}.md")
        kaynak_yol = dokum_dizin / kaynak_dosya_ad
        kaynak_icerik = k.get(
            "kaynak_icerik",
            f"{k['kunye']} sayılı kararın tam metni burada yer almaktadır...\n",
        )
        kaynak_yol.write_text(kaynak_icerik, encoding="utf-8")
        satirlar = [
            f"# {i:02d} — İçtihat Muhakeme Kaydı", "",
            f"**KUNYE:** {k['kunye']}",
            f"**KAYNAK-IZI:** _oa/teyit/dokum/{kaynak_dosya_ad}",
            f"**DAMGA:** {k['damga']}", "",
            "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
            "## İLLİYET", "...illiyet açıklaması...", "",
            "## AYIRT-ETME", k.get("ayirt_etme", ""), "",
        ]
        (cikti_dizin / f"{i:02d}-ictihat-muhakeme.md").write_text(
            "\n".join(satirlar), encoding="utf-8")
    taslak = tmp_path / "taslak.md"
    taslak.write_text(taslak_metin, encoding="utf-8")
    return taslak


def test_coklu_daire_dogru_daireye_eslesir_aleyhe_baska_dairenin_lehesi_arkasina_saklanamaz(tmp_path):
    """PoC (denetçi bulgusu): 11. HD/LEHE ve 4. HD/ALEYHE aynı esas/karar
    no'suna sahip; dilekçe AÇIKÇA 'Yargıtay 4. HD'yi anıyor (TASLAK_METIN).
    Script YANLIŞLIKLA 11. HD/LEHE kaydına eşleşip 'temiz' dönmemeli — doğru
    (4. HD/ALEYHE) kayda eşleşip TESLİM ENGELİ vermelidir."""
    _coklu_kunye_kur(tmp_path, [
        {"kunye": "Yargıtay 11. HD, E. 2023/1234, K. 2023/5678, T. 05.03.2023",
         "damga": "LEHE"},
        {"kunye": "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023",
         "damga": "ALEYHE"},
    ])
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "TESLİM ENGELİ" in cikti
    assert "ALEYHE" in cikti
    assert "OK 0" in cikti
    assert "BLOK 1" in cikti
    # doğru (ALEYHE) kayıt eşleşmiş olmalı — yanlış (LEHE) dosyaya değil
    assert "02-ictihat-muhakeme.md" in cikti


def test_coklu_daire_dogru_daire_lehe_ise_diger_dairenin_aleyhesi_engellemez(tmp_path):
    """Simetrik pozitif kontrol: dilekçenin açıkça andığı daireye (4. HD) ait
    kayıt LEHE ve temizse, esas/karar no'su aynı olan AMA FARKLI bir daireye
    (11. HD) ait ALEYHE kayıt bu atfı bloklamamalıdır — daireler bağımsızdır."""
    _coklu_kunye_kur(tmp_path, [
        {"kunye": "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023",
         "damga": "LEHE"},
        {"kunye": "Yargıtay 11. HD, E. 2023/1234, K. 2023/5678, T. 05.03.2023",
         "damga": "ALEYHE"},
    ])
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "OK 1" in cikti


def test_coklu_daire_atif_daire_belirtmiyorsa_belirsizlik_fail_closed_engeli(tmp_path):
    """Dilekçe atfı hiçbir daire/merci belirtmiyor (yalnız esas/karar no) VE
    aynı esas/karar no'suna sahip birden fazla FARKLI daireye ait kayıt varsa:
    hangisinin geçerli olduğu belirlenemez — fail-closed ENGEL (sessizce ilk
    'temiz' adaya kayıp ALEYHE kaydın arkasına saklanması engellenir)."""
    daire_belirtmeyen_metin = (
        "Somut olayda E. 2023/1234 K. 2023/5678 sayılı karar emsal teşkil "
        "etmektedir.\n"
    )
    _coklu_kunye_kur(tmp_path, [
        {"kunye": "Yargıtay 11. HD, E. 2023/1234, K. 2023/5678, T. 05.03.2023",
         "damga": "LEHE"},
        {"kunye": "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023",
         "damga": "ALEYHE"},
    ], taslak_metin=daire_belirtmeyen_metin)
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "TESLİM ENGELİ" in cikti
    assert "belirlenemiyor" in cikti.lower() or "belirsiz" in cikti.lower()


def test_taslaktaki_atiflari_ayni_esas_karar_farkli_daire_ayri_atif_sayilir():
    """Aynı esas/karar no'suyla FARKLI dairelere ait iki atıf tek bir atıfmış
    gibi birleştirilip biri sessizce kaybolmamalı (dedup anahtarı daire'yi de
    içerir)."""
    metin = (
        "Yargıtay 4. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı ile "
        "Yargıtay 11. HD'nin E. 2023/1234 K. 2023/5678 sayılı kararı birlikte "
        "değerlendirilmiştir."
    )
    atiflar = imd.taslaktaki_atiflari_bul(metin)
    assert len(atiflar) == 2
    daireler = {a["daire_key"] for a in atiflar}
    assert daireler == {("4", "HD"), ("11", "HD")}


# ── UYARI (bloklamaz): DAMGA=NOTR ───────────────────────────────────────────

def test_notr_uyarir_bloklamaz(tmp_path):
    _kur(tmp_path, damga="NOTR")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "NOTR" in cikti
    assert "⚠" in cikti


# ── UYARI (bloklamaz): G1 — dilekçede hiç ictihat atfı yok ─────────────────

def test_g1_atif_yoksa_uyarir_bloklamaz(tmp_path):
    _bos_iskelet(tmp_path)
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Bu dilekçe hiçbir içtihat atfı içermemektedir.\n", encoding="utf-8")
    kod, cikti = _cli(["taslak.md", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "emsal içtihat yok" in cikti.lower() or "emsal ictihat yok" in cikti.lower()


# ── kunye_ortak.py — paylaşımlı yardımcının sözleşmesi ─────────────────────

def test_kunye_normalize_esas_ve_karari_ayirir():
    esas, karar = ko.kunye_normalize(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023")
    assert esas == "2023/1234"
    assert karar == "2023/5678"


def test_kunye_normalize_bosluklu_no_normalize_edilir():
    esas, karar = ko.kunye_normalize("E. 2021 / 1234 K. 2022 / 9999")
    assert esas == "2021/1234"
    assert karar == "2022/9999"


def test_kunye_normalize_esas_yoksa_none():
    esas, karar = ko.kunye_normalize("bu metinde esas/karar no yok")
    assert esas is None
    assert karar is None


def test_esas_karar_atiflari_iki_ayri_atif_karismaz():
    metin = ("3. HD'nin E. 2023/100 K. 2023/200 sayılı kararı ile "
             "4. HD'nin E. 2024/300 K. 2024/400 sayılı kararı birlikte değerlendirilmiştir.")
    atiflar = ko.esas_karar_atiflari(metin)
    ciftler = sorted((a["esas"], a["karar"]) for a in atiflar)
    assert ciftler == [("2023/100", "2023/200"), ("2024/300", "2024/400")]


def test_sayi_var_komsu_rakami_izole_eder():
    assert ko.sayi_var("... 2023/1234 ...", "2023/1234") is True
    assert ko.sayi_var("... 2023/12349 ...", "2023/1234") is False
