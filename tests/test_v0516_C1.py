# -*- coding: utf-8 -*-
"""v0.5.16 GRUP C1 — oa-dilekce: [F] HAFİF KİP + [P] NETİCE-İ TALEP +
[N] taraf/rol beyaz listesi + UDF kesinti planı (K3 / P0-4·A-22 / H2 / B-6·P2-12).

Sözleşme:
  * [F] HAFİF KİP (`hizli_denetim` içinde, in-process, yalnız yerel dosya):
    taslaktaki künyeler `kunye_ortak.esas_karar_atiflari` ile çıkarılır,
    `<kok>/_oa/teyit/kunye-teyit.md` kütüğünde SON DAMGA okunur;
    ALEYHE → "[F] ALEYHE künye taslakta", NOTR → "[F] NÖTR künye",
    kütükte satır yok → "[F] kütükte izi yok"; LEHE/ALEYHE-AYIRT → satır yok.
    Kütük dosyası yoksa / kunye_ortak yüklenemezse GÖRÜNÜR bilgi satırı
    (sessiz atlama yasağı). [F] satırları bulgu listesinin EN BAŞINDA gelir
    (pipeline_kayit inline hook ilk 5 bulguyu gösterir). `kok` yoksa
    koşulmaz ([T] ile aynı ilke: hızlı kip dosya sistemine CWD'den tırmanmaz).
  * [P] NETİCE-İ TALEP (`netice_talep_uyarilari(metin)`, advisory — ASLA
    bloklamaz): talep bloğunu bulur; para varken faiz türü/başlangıcı,
    kısmi-dava/şimdilik varken 'fazlaya ilişkin', yargılama gideri/vekâlet
    ücreti yokluğunu uyarır; blok yoksa 'bulunamadı' (yalnız CLI'da —
    hızlı kip yarım taslakta gürültü üretmez).
  * [N] taraf/rol etiketleri (SANIK, DAVACI, VEKİLİ, İDARE, MADDE …) çıplak
    kısaltma SAYILMAZ.
  * references/udf-hatti-kesinti-plani.md mevcut ve SKILL.md'den işaretli.

GİZLİLİK (m.7): tüm künyeler/kişiler sentetiktir (E. 2099/1, Ayşe Örnek).
Testler tmp_path'te koşar, depo dosyalarına yazmaz.
"""
import importlib.util
import pathlib
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
SCRIPT = SKILL_DIR / "scripts" / "dilekce_denetim.py"


def _load():
    assert SCRIPT.is_file(), f"dilekce_denetim.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("dilekce_denetim_v0516_c1", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()

TEMIZ = (
    "<!-- kaynaklar: taslak.md@12ab34cd · analiz.md@abcd1234 -->\n"
    "# SENTETİK MAHKEME BAŞKANLIĞINA\n"
    "1. Olay şu şekilde gelişmiştir.\n"
    "2. Talebimiz aşağıda açıklanmıştır.\n"
)
KUNYE = "Yargıtay 9. HD, E. 2099/1, K. 2099/2"
KUNYELI = TEMIZ + f"\nEmsal: {KUNYE} kararı bu yöndedir.\n"

KUTUK_BASLIK = (
    "# Künye teyit kütüğü (sentetik)\n\n"
    "| Zaman | Araç | Sorgu | Sonuç (künye/madde + lehe/aleyhe) | Döküm |\n"
    "|---|---|---|---|---|\n"
)


def _kutuk_yaz(kok, satirlar):
    teyit = kok / "_oa" / "teyit"
    teyit.mkdir(parents=True, exist_ok=True)
    govde = "".join(
        f"| 2099-01-0{i + 1}T10:00:00 | ictihat_getir | sentetik sorgu | {s} | "
        f"[döküm](_oa/teyit/dokum/d{i}.md) |\n"
        for i, s in enumerate(satirlar))
    (teyit / "kunye-teyit.md").write_text(KUTUK_BASLIK + govde, encoding="utf-8")


def _f(bulgular):
    return [b for b in bulgular if b.startswith("[F]")]


# ── [F] HAFİF KİP ──────────────────────────────────────────────────────────

def test_f_aleyhe_kunye_kutukte_uyari(tmp_path):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE DOKUM-SINIFI=tam-metin"])
    bulgular = dd.hizli_denetim(KUNYELI, kok=str(tmp_path))
    f = _f(bulgular)
    assert len(f) == 1, bulgular
    assert "ALEYHE" in f[0] and "2099/1" in f[0] and "m.6" in f[0], f


def test_f_lehe_kunye_satir_uretmez(tmp_path):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=LEHE DOKUM-SINIFI=tam-metin"])
    assert _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path))) == []


def test_f_aleyhe_ayirt_satir_uretmez(tmp_path):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE-AYIRT DUYULMUS=EVET"])
    assert _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path))) == []


def test_f_notr_kunye_giremez_uyarisi(tmp_path):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=NOTR"])
    f = _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path)))
    assert len(f) == 1 and "NÖTR" in f[0] and "giremez" in f[0], f


def test_f_kutukte_izi_yok_ciplak_kunye_adayi(tmp_path):
    _kutuk_yaz(tmp_path, ["Yargıtay 3. HD, E. 2098/7, K. 2098/8 DAMGA=LEHE"])
    f = _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path)))
    assert len(f) == 1 and "izi yok" in f[0] and "çıplak künye" in f[0], f


def test_f_son_damga_gecerli(tmp_path):
    """Append-only kütükte aynı künyenin SON damgası geçerlidir (oa_hafiza
    --damga-degistir ritüeli): ALEYHE → LEHE'ye değişmişse satır üretilmez."""
    _kutuk_yaz(tmp_path, [
        f"{KUNYE} DAMGA=ALEYHE",
        f"{KUNYE} DAMGA=LEHE (DEĞİŞTİRİLDİ — önceki: ALEYHE; gerekçe: sentetik gerekçe metni kırk karakterden uzun)",
    ])
    assert _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path))) == []


def test_f_farkli_daire_ayni_numara_eslesmez(tmp_path):
    """Esas/karar no'ları her dairede sıfırdan başlar — 9. HD'nin ALEYHE
    satırı 11. HD'nin aynı numaralı kararına damga saymaz (kütükte izi yok)."""
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE"])
    metin = TEMIZ + "\nEmsal: Yargıtay 11. HD, E. 2099/1, K. 2099/2 kararı.\n"
    f = _f(dd.hizli_denetim(metin, kok=str(tmp_path)))
    assert len(f) == 1 and "izi yok" in f[0], f


def test_f_damgasiz_satir_muhakeme_edilmemis(tmp_path):
    """Kütükte satır var ama DAMGA yok (ARAMA sınıfı) → çıplak künye adayı."""
    _kutuk_yaz(tmp_path, [f"{KUNYE} [ARAMA — tam metin çekilmedi]"])
    f = _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path)))
    assert len(f) == 1 and "damgasız" in f[0], f


def test_f_kutuk_dosyasi_yoksa_bilgi_satiri(tmp_path):
    (tmp_path / "_oa").mkdir()
    f = _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path)))
    assert len(f) == 1 and "kütük" in f[0] and "tam kapı" in f[0], f


def test_f_kunyesiz_taslakta_sessiz(tmp_path):
    """Künye yoksa kütük de olmasa gürültü yok (yarım taslaklar)."""
    assert _f(dd.hizli_denetim(TEMIZ, kok=str(tmp_path))) == []


def test_f_kok_verilmemisse_kosulmaz():
    assert _f(dd.hizli_denetim(KUNYELI)) == []


def test_f_kunye_ortak_yuklenemezse_gorunur_bilgi(tmp_path, monkeypatch):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE"])
    monkeypatch.setattr(dd, "_kunye_ortak_modulu", lambda: None)
    f = _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path)))
    assert len(f) == 1 and "kunye_ortak yüklenemedi" in f[0], f


def test_f_satirlari_en_basta(tmp_path):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE"])
    metin = (
        "# BAŞLIK (kaynak bloğu bilerek yok)\n"
        'Kararda "borç ödenmemiştir ..."\n\n'
        "Taslak TESLİME HAZIR durumdadır.\n"
        f"Emsal: {KUNYE} kararı.\n"
        "Bu işlemde GKT belgesi esas alınmıştır.\n"
    )
    bulgular = dd.hizli_denetim(metin, kok=str(tmp_path))
    etiketler = [b.split()[0] for b in bulgular]
    assert etiketler[0] == "[F]", etiketler
    assert "[T]" in etiketler and "[Y]" in etiketler, etiketler


def test_f_ayni_kunye_tekillestirilir(tmp_path):
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE"])
    metin = KUNYELI + f"\nYine {KUNYE} anılmıştır.\n"
    assert len(_f(dd.hizli_denetim(metin, kok=str(tmp_path)))) == 1


def test_f_agir_bacaklara_girmez(tmp_path, monkeypatch):
    def _yasak(*a, **k):
        raise AssertionError("hafif kip ağır bacağa girdi (subprocess/zip)")
    monkeypatch.setattr(dd.subprocess, "run", _yasak)
    monkeypatch.setattr(dd.zipfile, "ZipFile", _yasak)
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE"])
    assert _f(dd.hizli_denetim(KUNYELI, kok=str(tmp_path)))


def test_f_50kb_taslakta_2sn_altinda(tmp_path):
    _kutuk_yaz(tmp_path, [f"Yargıtay 9. HD, E. 2099/{i}, K. 2099/{i + 500} DAMGA=ALEYHE"
                          for i in range(1, 40)])
    paragraf = (
        "12. Sentetik vakıa: sözleşme uyarınca 1.000 TL bedel kararlaştırılmış, "
        "Yargıtay 9. HD, E. 2099/%d, K. 2099/%d kararı bu yöndedir. "
        "Davalı taraf buna itiraz edebilir.\n\n")
    metin = TEMIZ + "".join(paragraf % (i % 60 + 1, i % 60 + 501) for i in range(400))
    assert len(metin.encode("utf-8")) >= 50 * 1024
    dd.hizli_denetim(TEMIZ, kok=str(tmp_path))       # ısınma
    t0 = time.perf_counter()
    bulgular = dd.hizli_denetim(metin, kok=str(tmp_path))
    sure = time.perf_counter() - t0
    assert _f(bulgular), bulgular
    assert sure < 2.0, f"hafif kip {sure:.3f} sn (şart: 50KB'de < 2 sn)"


def test_f_kaynakca_blogu_denetim_girdisi_degil(tmp_path):
    """B-18 ile simetrik: makine üretimi '## İÇTİHAT KAYNAKÇASI' bloğundaki
    künye [F] hafif kipte taranmaz (gövde metni değildir)."""
    ko = dd._kunye_ortak_modulu()
    if ko is None or not hasattr(ko, "makine_blogu_maskele"):
        pytest.skip("kunye_ortak.makine_blogu_maskele yok")
    _kutuk_yaz(tmp_path, [f"{KUNYE} DAMGA=ALEYHE"])
    govde = TEMIZ + "\nGövdede künye yok.\n"
    blok = (f"\n{ko.KAYNAKCA_BLOK_BAS}\n{ko.KAYNAKCA_BASLIK}\n- {KUNYE}\n"
            f"{ko.KAYNAKCA_BLOK_SON}\n")
    if ko.makine_blogu_maskele(govde + blok) == govde + blok:
        pytest.skip("maskeleyici bu blok biçimini tanımıyor — test anlamsız")
    assert _f(dd.hizli_denetim(govde + blok, kok=str(tmp_path))) == []


# ── [P] NETİCE-İ TALEP ────────────────────────────────────────────────────

TAM_TALEP = (
    "## NETİCE-İ TALEP\n"
    "1. Davanın KABULÜ ile 10.000,00 TL alacağın dava tarihinden itibaren "
    "işleyecek yasal faiziyle davalıdan tahsiline,\n"
    "2. Fazlaya ilişkin haklarımız saklı kalmak kaydıyla,\n"
    "3. Yargılama giderleri ve vekâlet ücretinin davalıya yükletilmesine\n"
    "karar verilmesini saygıyla talep ederiz.\n"
)


def _p(bulgular):
    return [b for b in bulgular if b.startswith("[P]")]


def test_p_fonksiyon_var_ve_tam_blok_temiz():
    assert hasattr(dd, "netice_talep_uyarilari")
    assert dd.netice_talep_uyarilari(TEMIZ + TAM_TALEP) == []


def test_p_blok_yoksa_bulunamadi():
    u = dd.netice_talep_uyarilari(TEMIZ)
    assert len(u) == 1 and "bulunamadı" in u[0], u


@pytest.mark.parametrize("baslik", [
    "## SONUÇ VE İSTEM", "## NETİCE VE TALEP", "**NETİCE-İ TALEP:**",
    "SONUÇ VE İSTEM", "## TALEP", "## Netice-i Talep",
])
def test_p_baslik_varyantlari_taninir(baslik):
    metin = TEMIZ + baslik + "\n" + "\n".join(TAM_TALEP.splitlines()[1:]) + "\n"
    assert dd.netice_talep_uyarilari(metin) == [], baslik


def test_p_para_var_faiz_turu_yok():
    metin = TEMIZ + TAM_TALEP.replace("işleyecek yasal faiziyle ", "işleyecek faiziyle ")
    u = dd.netice_talep_uyarilari(metin)
    assert any("faiz türü" in x for x in u), u


def test_p_para_var_faiz_baslangici_yok():
    metin = TEMIZ + TAM_TALEP.replace("dava tarihinden itibaren ", "")
    u = dd.netice_talep_uyarilari(metin)
    assert any("başlangı" in x for x in u), u
    assert not any("faiz türü" in x for x in u), u


def test_p_faiz_baslangici_tarih_biciminde_kabul():
    metin = TEMIZ + TAM_TALEP.replace("dava tarihinden itibaren", "01.02.2099 tarihinden itibaren")
    assert dd.netice_talep_uyarilari(metin) == []
    metin2 = TEMIZ + TAM_TALEP.replace("dava tarihinden itibaren", "01.02.2099'dan itibaren")
    assert dd.netice_talep_uyarilari(metin2) == []


def test_p_para_yoksa_faiz_aranmaz():
    metin = TEMIZ + TAM_TALEP.replace(
        "10.000,00 TL alacağın dava tarihinden itibaren işleyecek yasal faiziyle davalıdan tahsiline",
        "işe iadesine")
    assert dd.netice_talep_uyarilari(metin) == []


def test_p_kismi_dava_var_fazlaya_iliskin_yok():
    metin = (TEMIZ + "\nBu dava kısmi dava olarak açılmıştır.\n"
             + TAM_TALEP.replace("2. Fazlaya ilişkin haklarımız saklı kalmak kaydıyla,\n", ""))
    u = dd.netice_talep_uyarilari(metin)
    assert any("fazlaya ilişkin" in x for x in u), u


def test_p_simdilik_var_fazlaya_iliskin_yok():
    metin = TEMIZ + TAM_TALEP.replace("10.000,00 TL", "şimdilik 10.000,00 TL").replace(
        "2. Fazlaya ilişkin haklarımız saklı kalmak kaydıyla,\n", "")
    u = dd.netice_talep_uyarilari(metin)
    assert any("fazlaya ilişkin" in x for x in u), u


def test_p_belirsiz_alacak_m107_mulga_isaretcisi():
    """HMK m.107 mülga (7589/19, RG 31.07.2026 — Mevzuat MCP teyit 2026-09-06);
    'belirsiz alacak' geçen taslakta uyarı bu işaretçiyi taşır."""
    metin = TEMIZ + "\nBelirsiz alacak davası olarak açılmıştır.\n" + TAM_TALEP.replace(
        "2. Fazlaya ilişkin haklarımız saklı kalmak kaydıyla,\n", "")
    u = dd.netice_talep_uyarilari(metin)
    assert any("107" in x and "mülga" in x for x in u), u


def test_p_yargilama_gideri_vekalet_ucreti_yok():
    metin = TEMIZ + TAM_TALEP.replace(
        "3. Yargılama giderleri ve vekâlet ücretinin davalıya yükletilmesine\n", "")
    u = dd.netice_talep_uyarilari(metin)
    assert any("yargılama gider" in x for x in u), u


def test_p_vekalet_sapkasiz_yazim_kabul():
    metin = TEMIZ + TAM_TALEP.replace("vekâlet", "vekalet")
    assert dd.netice_talep_uyarilari(metin) == []


def test_p_blok_metnin_sonuna_kadar():
    """Talep bloğu başlıktan METNİN SONUNA kadardır — imza bloğundaki
    tarih faiz başlangıcı SAYILMAMALI değil; ama gider kalemi imza
    altında değil blokta aranır (blok = başlıktan sona kadar, dahil)."""
    metin = TEMIZ + TAM_TALEP + "\n01.01.2099\nAv. Örnek Vekil\n"
    assert dd.netice_talep_uyarilari(metin) == []


def test_p_hizli_kipte_blok_yoksa_gurultu_yok():
    assert _p(dd.hizli_denetim(TEMIZ)) == []


def test_p_hizli_kipte_blok_kusurlu_ise_satir():
    metin = TEMIZ + TAM_TALEP.replace("işleyecek yasal faiziyle ", "işleyecek faiziyle ")
    p = _p(dd.hizli_denetim(metin))
    assert p and all(x.startswith("[P] ") for x in p), p


def test_p_cli_bolum_basar_ve_exit_koduna_dokunmaz(tmp_path, capsys):
    taslak_metin = (
        "# Örnek 1. İş Mahkemesi Başkanlığına\n\n"
        "## Taraflar\nDavacı: Ayşe Örnek, Adres: Örnek Mah.\n"
        "Davalı: Örnek A.Ş., Adres: Örnek Cad.\nVekil: Av. Örnek Vekil\n\n"
        "## Konu\nAlacak (2099/1 Esas).\n\n"
        "## Açıklamalar\n1. Birinci vakıa.\n2. İkinci vakıa.\n\n"
        "## Hukuki Sebepler\nİlgili hukuki dayanaklar.\n\n"
        "## Deliller\nTanık, bilirkişi.\n\n"
        + TAM_TALEP.replace("işleyecek yasal faiziyle ", "işleyecek faiziyle ")
        + "\n01.01.2099\nAv. Örnek Vekil\nimza\n"
    )
    taslak = tmp_path / "taslak.md"
    taslak.write_text(taslak_metin, encoding="utf-8")
    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py", str(taslak), "--tip", "dava", "--taraf", "davaci",
                "--kok", str(tmp_path)]
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek
    cikti = capsys.readouterr().out
    assert "[P] NETİCE-İ TALEP" in cikti
    assert "faiz türü" in cikti
    assert exc.value.code == 0, cikti


# ── [N] taraf/rol etiketleri beyaz liste (H2) ─────────────────────────────

@pytest.mark.parametrize("etiket", [
    "SANIK", "ŞÜPHELİ", "HÜKÜMLÜ", "MAĞDUR", "MÜŞTEKİ", "KATILAN", "MÜDAHİL",
    "DAVACI", "DAVALI", "ALACAKLI", "BORÇLU", "VEKİLİ", "VEKİL", "MÜVEKKİL",
    "TANIK", "İDARE", "DAVA", "KARAR", "ESAS", "MADDE",
])
def test_n_taraf_rol_etiketi_ciplak_kisaltma_degil(etiket):
    metin = f"{etiket} : Ayşe Örnek, Örnek Mah. No: 1\nAçıklamalar aşağıdadır.\n"
    uyarilar = dd.ciplak_kisaltma_uyarilari(metin)
    assert not any(etiket in u for u in uyarilar), uyarilar


def test_n_para_birimi_tl_kisaltma_degil():
    """'5.000,00 TL' her para talepli taslakta [N] üretiyordu — para birimi
    simgesinin açılımı beklenmez (H2 ile aynı sınıf: etiket, kısaltma değil)."""
    metin = "Davacı 5.000,00 TL alacağın tahsilini talep etmiştir.\n"
    assert not any("'TL'" in u for u in dd.ciplak_kisaltma_uyarilari(metin))


def test_n_beyaz_liste_gercek_kisaltmayi_gizlemez():
    metin = "SANIK : Ayşe Örnek\nBu işlemde GKT belgesi esas alınmıştır.\n"
    uyarilar = dd.ciplak_kisaltma_uyarilari(metin)
    assert any("GKT" in u for u in uyarilar), uyarilar
    assert not any("SANIK" in u for u in uyarilar), uyarilar


# ── B-6: UDF hattı kesinti planı ───────────────────────────────────────────

def test_udf_kesinti_plani_mevcut_ve_isaretli():
    plan = SKILL_DIR / "references" / "udf-hatti-kesinti-plani.md"
    assert plan.is_file(), plan
    metin = plan.read_text(encoding="utf-8")
    for anahtar in ("udf_html2pdf.py", "--udf-yok", "UYAP", "pin", "avukat"):
        assert anahtar in metin, anahtar
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "references/udf-hatti-kesinti-plani.md" in skill


def test_skill_netice_talep_playbook_bolumu():
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "NETİCE-İ TALEP PLAYBOOK" in skill
    for anahtar in ("3095", "m.107", "m.109", "7589", "fazlaya ilişkin",
                    "Mevzuat MCP teyit 2026-09-06"):
        assert anahtar in skill, anahtar
