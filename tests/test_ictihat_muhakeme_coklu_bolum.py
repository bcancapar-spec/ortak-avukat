# -*- coding: utf-8 -*-
"""P0-3 (v0.5.5) — çok-bölümlü muhakeme dosyası desteği.

`oa_hafiza.py teyit --damga` (P0-2) `_oa/cikti/03-ictihat-muhakeme.md`'ye
bölüm APPEND eder (bir dosya = N kayıt); bu paket `ictihat_muhakeme_denetim.py`
+ `kunye_ortak.bolumlere_ayir`'ın bu biçimi G1/G2/G3 semantiğini BİT DÜZEYİNDE
DEĞİŞTİRMEDEN doğru ayrıştırdığını doğrular. Ayrıca P0-2 DÜZELTME (d) — kütük
(append-only) SON DAMGA'sı ile muhakeme bölümü DAMGA'sının çapraz kontrolünü
kapsar.
"""
import importlib.util
import pathlib
import subprocess
import sys

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


imd = _load(SCRIPT, "ictihat_muhakeme_denetim_cb")
ko = _load(KUNYE_ORTAK, "kunye_ortak_cb")


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _bos_iskelet(tmp_path):
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    return dokum_dizin, cikti_dizin


def _bolum_yaz(kunye, damga, ayirt_etme="", ilgili_kisim="...ilgili kısım...",
               davaya_bag="...davaya bağ...", damga_satiri=True):
    satirlar = [f"# İçtihat Muhakeme Kaydı — {kunye}", "", f"**KUNYE:** {kunye}",
                f"**KAYNAK-IZI:** {{KAYNAK}}"]
    if damga_satiri:
        satirlar.append(f"**DAMGA:** {damga}")
    satirlar.append("")
    satirlar += ["## İLGİLİ-KISIM", ilgili_kisim, ""]
    satirlar += ["## DAVAYA-BAĞ", davaya_bag, ""]
    satirlar += ["## AYIRT-ETME", ayirt_etme, ""]
    return "\n".join(satirlar)


def _kaynak_yaz(dokum_dizin, ad, kunye):
    (dokum_dizin / ad).write_text(f"{kunye} sayılı kararın tam metni burada...\n",
                                   encoding="utf-8")
    return f"_oa/teyit/dokum/{ad}"


KUNYE_A = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
KUNYE_B = "Yargıtay 5. HD, E. 2022/100, K. 2022/200, T. 01.02.2022"
KUNYE_C = "Yargıtay 6. HD, E. 2021/500, K. 2021/900, T. 03.04.2021"


def _taslak_yaz(tmp_path, kunyeler):
    metin = " ".join(f"{k} sayılı karar emsal teşkil etmektedir." for k in kunyeler)
    taslak = tmp_path / "taslak.md"
    taslak.write_text(metin, encoding="utf-8")
    return taslak


# ── (1) tek dosyada 3 bölüm, hepsi tam → OK 3 ──────────────────────────────

def test_uc_bolum_hepsi_tam_ok_3(tmp_path):
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    kaynak_b = _kaynak_yaz(dokum_dizin, "b.md", KUNYE_B)
    kaynak_c = _kaynak_yaz(dokum_dizin, "c.md", KUNYE_C)
    icerik = "\n".join([
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a),
        _bolum_yaz(KUNYE_B, "LEHE").replace("{KAYNAK}", kaynak_b),
        _bolum_yaz(KUNYE_C, "ALEYHE-AYIRT", ayirt_etme="ayırt edici gerekçe metni").replace("{KAYNAK}", kaynak_c),
    ])
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(icerik, encoding="utf-8")
    # v0.5.8.5 [G6]: ALEYHE-AYIRT künye (KUNYE_C) dilekçede yalnız AYIRT/
    # ÇÜRÜTME bağlamında anılabilir — destek cümlesi artık BLOK olurdu.
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        f"{KUNYE_A} sayılı karar emsal teşkil etmektedir. "
        f"{KUNYE_B} sayılı karar emsal teşkil etmektedir. "
        f"Davalı tarafın dayandığı {KUNYE_C} sayılı karar somut olaydan AYIRT "
        "edilmelidir; olgusal zemin başkadır.", encoding="utf-8")
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "OK 3" in cikti


# ── (2) 3 bölümden biri damgasız → yalnız o karar BLOK ─────────────────────

def test_uc_bolumden_biri_damgasiz_yalniz_o_blok(tmp_path):
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    kaynak_b = _kaynak_yaz(dokum_dizin, "b.md", KUNYE_B)
    kaynak_c = _kaynak_yaz(dokum_dizin, "c.md", KUNYE_C)
    icerik = "\n".join([
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a),
        _bolum_yaz(KUNYE_B, "LEHE", damga_satiri=False).replace("{KAYNAK}", kaynak_b),
        _bolum_yaz(KUNYE_C, "LEHE").replace("{KAYNAK}", kaynak_c),
    ])
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(icerik, encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A, KUNYE_B, KUNYE_C])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "OK 2" in cikti
    assert "BLOK 1" in cikti
    assert "muhakeme edilmemiş" in cikti.lower()


# ── (3) bölümde ALEYHE → ENGEL, aynı dosyada LEHE+bağ → OK ─────────────────

def test_bir_bolum_aleyhe_engel_digeri_lehe_ok(tmp_path):
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    kaynak_b = _kaynak_yaz(dokum_dizin, "b.md", KUNYE_B)
    icerik = "\n".join([
        _bolum_yaz(KUNYE_A, "ALEYHE").replace("{KAYNAK}", kaynak_a),
        _bolum_yaz(KUNYE_B, "LEHE").replace("{KAYNAK}", kaynak_b),
    ])
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(icerik, encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A, KUNYE_B])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "OK 1" in cikti
    assert "BLOK 1" in cikti
    assert "ALEYHE" in cikti


# ── (4) aynı künye eski (tek-bölüm) dosyada ALEYHE + yeni bölümde LEHE ─────
# → ÇELİŞEN DAMGA uyarısı (bölümler arası, dosyalar arası da çalışır)

def test_eski_dosya_aleyhe_yeni_bolum_lehe_celisen_damga_uyarir(tmp_path):
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_eski = _kaynak_yaz(dokum_dizin, "eski.md", KUNYE_A)
    (cikti_dizin / "01-ictihat-muhakeme.md").write_text(
        _bolum_yaz(KUNYE_A, "ALEYHE").replace("{KAYNAK}", kaynak_eski), encoding="utf-8")

    kaynak_b = _kaynak_yaz(dokum_dizin, "b.md", KUNYE_B)
    kaynak_a_yeni = _kaynak_yaz(dokum_dizin, "a-yeni.md", KUNYE_A)
    icerik_append = "\n".join([
        _bolum_yaz(KUNYE_B, "LEHE").replace("{KAYNAK}", kaynak_b),
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a_yeni),
    ])
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(icerik_append, encoding="utf-8")

    taslak = _taslak_yaz(tmp_path, [KUNYE_A, KUNYE_B])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    # v0.5.5 son sınav düzeltmesi: eski dosyadaki ALEYHE ile yeni bölümdeki LEHE
    # SINIF-ÖTESİ çelişkidir (giremez × girebilir) — lehe olan sessizce seçilip
    # OK dönemez, m.6 kaçağı olurdu. Artık TESLİM ENGELİ; çözüm --damga-degistir.
    assert kod == 1, f"ALEYHE ikizi gölgelendi — m.6 kaçağı:\n{cikti}"
    assert "ÇELİŞEN DAMGA" in cikti


# ── (5) mevcut geniş test seti değişmeden geçer — ayrı invoke ile doğrulanır
# (bkz. tests/test_ictihat_muhakeme_denetim.py + test_ictihat_muhakeme_sema.py)


# ── (6) gövde metninde geçen serbest 'KUNYE' kelimesi bölüm başlatmaz ──────

def test_govde_metninde_kunye_kelimesi_yanlis_bolum_baslatmaz():
    metin = (
        "# 01 — İçtihat Muhakeme Kaydı\n\n"
        "**KUNYE:** " + KUNYE_A + "\n"
        "**KAYNAK-IZI:** _oa/teyit/dokum/a.md\n"
        "**DAMGA:** LEHE\n\n"
        "## İLGİLİ-KISIM\n"
        "Bu pasajda KUNYE kelimesi serbestçe geçmektedir ama satır başında "
        "kalın (**KUNYE:**) biçiminde değildir, bu yüzden yeni bölüm başlatmaz.\n\n"
        "## DAVAYA-BAĞ\n...davaya bağ...\n\n"
        "## AYIRT-ETME\n\n"
    )
    bolumler = ko.bolumlere_ayir(metin)
    assert len(bolumler) == 1


def test_bolumlere_ayir_iki_gercek_bolum():
    metin = (
        "**KUNYE:** " + KUNYE_A + "\n**KAYNAK-IZI:** x\n**DAMGA:** LEHE\n\n"
        "## İLGİLİ-KISIM\nA\n\n"
        "**KUNYE:** " + KUNYE_B + "\n**KAYNAK-IZI:** y\n**DAMGA:** LEHE\n\n"
        "## İLGİLİ-KISIM\nB\n\n"
    )
    bolumler = ko.bolumlere_ayir(metin)
    assert len(bolumler) == 2
    assert KUNYE_A in bolumler[0]
    assert KUNYE_B in bolumler[1]
    assert KUNYE_A not in bolumler[1]


def test_bolumlere_ayir_bos_veya_tek_eslesme_tum_metni_doner():
    assert ko.bolumlere_ayir("hiç künye yok") == ["hiç künye yok"]
    tek = "**KUNYE:** " + KUNYE_A + "\ngövde...\n"
    assert ko.bolumlere_ayir(tek) == [tek]


# ── P0-2 DÜZELTME (d) — kütük (append-only) SON DAMGA çapraz kontrolü ──────

def _kutuk_satiri_yaz(kutuk_yolu, kunye, damga, dokum_ad="x",
                      sinif="DOKUM-SINIFI=tam-metin"):
    # v0.5.8.5 [G6]: dürüst-akış satırları TAM-METİN sınıfı taşır (A1a) —
    # sınıfsız satır geriye-uyumla 'ilgili-kisim' sayılıp triyajda bloklanır.
    ek = f" {sinif}" if sinif else ""
    with open(kutuk_yolu, "a", encoding="utf-8") as f:
        f.write(f"| 2026-01-01T00:00:00 | ictihat_getir | sorgu | {kunye} DAMGA={damga}{ek} | "
                f"[döküm]({dokum_ad}) |\n")


def test_kutuk_son_damga_farkli_ise_engel(tmp_path):
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    teyit_dizin = tmp_path / "_oa" / "teyit"
    kutuk_yolu = teyit_dizin / "kunye-teyit.md"
    kutuk_yolu.write_text("| Zaman | Araç | Sorgu | Sonuç | Döküm |\n|---|---|---|---|---|\n",
                           encoding="utf-8")
    _kutuk_satiri_yaz(kutuk_yolu, KUNYE_A, "ALEYHE")

    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a), encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "elle değiştirilmiş" in cikti


def test_kutuk_son_damga_ayni_ise_ok(tmp_path):
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    teyit_dizin = tmp_path / "_oa" / "teyit"
    kutuk_yolu = teyit_dizin / "kunye-teyit.md"
    kutuk_yolu.write_text("| Zaman | Araç | Sorgu | Sonuç | Döküm |\n|---|---|---|---|---|\n",
                           encoding="utf-8")
    # DÜZELTME (v0.5.5 düzeltme turu — Ş2/t3-B): `kutuk_dayanagi_denetle`
    # artık kütük satırının DAMGA'sı VE döküm hücresinin bölümün KAYNAK-IZI
    # dosyasıyla EŞLEŞMESİNİ arıyor (bkz. `kunye_ortak.kutukte_damgali_
    # dayanak_satiri_var_mi`) — dürüst-akış testinin kütük satırı bu yüzden
    # gerçek KAYNAK-IZI'yi ("_oa/teyit/dokum/a.md") göstermeli.
    _kutuk_satiri_yaz(kutuk_yolu, KUNYE_A, "LEHE", dokum_ad="_oa/teyit/dokum/a.md")

    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a), encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "elle değiştirilmiş" not in cikti


def test_kutuk_yoksa_denetim_sessizce_atlanir_geriye_uyum(tmp_path):
    """Kütük dosyası hiç yoksa (eski/elle kurulmuş test iskeleti) DAMGA çapraz
    kontrolü SESSİZCE ATLANIR — bu geriye uyumun kalbidir (478+152 satırlık
    mevcut test seti hiç kütük kurmaz)."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a), encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti


# DÜZELTME (v0.5.5 düzeltme turu — Ş2, ÖNEMLİ, SESSİZ FAIL-OPEN GÖRÜNÜRLÜĞÜ):
# yukarıdaki testin doğruladığı SESSİZCE ATLAMA artık GERÇEKTEN sessiz değil —
# avukat, HAYALET MUHAKEME denetiminin (kütük dayanağı) bu koşuda hiç
# çalışmadığını [BİLGİ] satırından görür (bloklamaz — yalnız görünürlük).

def test_kutuk_kullanilmiyorsa_atlama_gorunur_bilgi_satirina_dusar(tmp_path):
    """Ş2 (ÖNEMLİ) çürütücü bulgusu: `kutuk_dayanagi_denetle`nin taze/kütüksüz
    kökte SESSİZCE atlanması (geriye uyum — bir önceki test) artık görünür bir
    [BİLGİ] satırıyla raporlanır; kapı yine BLOKLAMAZ (exit hâlâ 0)."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a), encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "HAYALET MUHAKEME denetimi" in cikti and "ÇALIŞMADI" in cikti, cikti


def test_kutuk_kullaniliyorsa_atlama_bilgi_satiri_basilmaz(tmp_path):
    """Simetrik negatif: kütük FİİLEN kullanılıyorken (en az bir gerçek satır)
    'ÇALIŞMADI' bilgi satırı basılmamalı — denetim gerçekten çalışıyor."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(
        _bolum_yaz(KUNYE_A, "LEHE").replace("{KAYNAK}", kaynak_a), encoding="utf-8")
    kutuk_dizin = tmp_path / "_oa" / "teyit"
    kutuk_dizin.mkdir(parents=True, exist_ok=True)
    kutuk_yolu = kutuk_dizin / "kunye-teyit.md"
    kutuk_yolu.write_text(
        "| Zaman | Araç | Sorgu | Sonuç | Döküm |\n|---|---|---|---|---|\n"
        f"| 2026-01-01T00:00:00 | ictihat_getir | sorgu | {KUNYE_A} DAMGA=LEHE "
        f"DOKUM-SINIFI=tam-metin | [döküm]({kaynak_a}) |\n",
        encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "ÇALIŞMADI" not in cikti, cikti


# ── P0-3 DÜZELTME (BLOKER regresyon) — ilk bölümün AYIRT-ETME/DAVAYA-BAĞ'ı ─
# SONRAKİ bölümün `# İçtihat Muhakeme Kaydı — <ts>` başlığıyla KİRLENMEMELİ.
# `_bolum_yaz` HER bölümün başına (KUNYE'den ÖNCE) tam da bu tek-`#` başlığı
# koyar — sablonun kanonik `# 01 — İçtihat Muhakeme Kaydı` biçimiyle bit-aynı.
# Eski `_bolum_al` yalnız `^##\s+` ile durduğundan, bir sonraki kaydın bu
# tek-`#` başlığı ÖNCEKİ bölümün SON alanına (AYIRT-ETME) sızıyor ve boş
# AYIRT-ETME'yi 'dolu' gösteriyordu — yalnız bu alan SON bölümdeyse (dosyada
# ondan sonra başka kayıt yoksa) sızacak metin olmadığından bug GİZLENİYORDU;
# bu yüzden dosyanın SON bölümü DEĞİL, İLKİ test edilir.

def test_ilk_bolum_bos_ayirt_etme_ikinci_bolum_varken_yine_blok(tmp_path):
    """DAMGA=ALEYHE-AYIRT + boş AYIRT-ETME olan bölüm dosyanın SONUNDA değil
    BAŞINDA (arkasında başka bir kayıt varken) — fail-closed BLOK kırılmamalı."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    kaynak_b = _kaynak_yaz(dokum_dizin, "b.md", KUNYE_B)
    icerik = "\n".join([
        _bolum_yaz(KUNYE_A, "ALEYHE-AYIRT", ayirt_etme="").replace("{KAYNAK}", kaynak_a),
        _bolum_yaz(KUNYE_B, "LEHE").replace("{KAYNAK}", kaynak_b),
    ])
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(icerik, encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A, KUNYE_B])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "OK 1" in cikti
    assert "BLOK 1" in cikti
    assert "boş AYIRT-ETME" in cikti


def test_ilk_bolum_bos_davaya_bag_ikinci_bolum_varken_yine_blok(tmp_path):
    """DAVAYA-BAĞ alanı boş olan bölüm dosyanın BAŞINDA (arkasında başka bir
    kayıt varken) — G2 alan-bütünlüğü denetimi hâlâ BLOK vermeli (aynı sızma
    sınıfı AYIRT-ETME dışındaki `_bolum_al` tüketicileri için de geçerlidir)."""
    dokum_dizin, cikti_dizin = _bos_iskelet(tmp_path)
    kaynak_a = _kaynak_yaz(dokum_dizin, "a.md", KUNYE_A)
    kaynak_b = _kaynak_yaz(dokum_dizin, "b.md", KUNYE_B)
    icerik = "\n".join([
        _bolum_yaz(KUNYE_A, "LEHE", davaya_bag="").replace("{KAYNAK}", kaynak_a),
        _bolum_yaz(KUNYE_B, "LEHE").replace("{KAYNAK}", kaynak_b),
    ])
    (cikti_dizin / "03-ictihat-muhakeme.md").write_text(icerik, encoding="utf-8")
    taslak = _taslak_yaz(tmp_path, [KUNYE_A, KUNYE_B])
    kod, cikti = _cli([str(taslak.name), "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, cikti
    assert "OK 1" in cikti
    assert "BLOK 1" in cikti
    assert "DAVAYA-BAĞ alanı boş" in cikti
