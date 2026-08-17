# -*- coding: utf-8 -*-
"""v0.5.8.6 — G1 TRİYAJ-İÇE-AL + G2a sürtünme + G2b ham/ dizin tanıma.

777 saha dersi: model gerçek triyaj emeğini (ham dökümler + LEHE/ALEYHE
kararları) teyit-script formatının DIŞINDA, serbest bir okuma-muhakemesi
belgesine yazdı — [G6] triyaj kapısı bu emeği GÖREMEDİ (kütükte iz yok).

Kapsam:
- G1: `oa_hafiza.py triyaj-ice-al --dosya <okuma-muhakemesi.md>` serbest-format
  triyaj belgesini ayrıştırır; her karar için kütüğe teyit-formatında satır
  (DAMGA= tokenı + [ham dosya mevcut ∧ >2KB ise] DOKUM-SINIFI=tam-metin +
  döküm bağı) ekler; `ictihat_muhakeme_denetim` regexleriyle ROUND-TRIP
  doğrulanır. Ayrıştırılamayan bölüm SESSİZCE atlanmaz — "içe alınamadı:
  <neden>" raporlanır, çıkış kodu 0 kalır (araç kapı değildir).
- G2a: kütük başlığında kopyala-yapıştır tek-satır CLI örneği; teyit RET
  mesajlarında "Ne yapmalı" cümlesi.
- G2b: `_oa/teyit/ham/` (ve --ham-dizin) altındaki dosyalar da meşru döküm
  evreni sayılır (777'de dökümler ham/'a inmişti, sözleşme dokum/'du).

Tüm girdiler tmp_path + SENTETİK veridir (repo kuralı — gerçek dava numarası /
kişi adı / gerçek klasör yolu yazılmaz).
"""
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
KUNYE_ORTAK = SKILLS / "oa-kontrol" / "scripts" / "kunye_ortak.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(HAFIZA)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, str(yol))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _init(tmp_path):
    kod, cikti = _cli(["init", "--dosya", "Sentetik Dosya", "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti


def _kutuk_oku(tmp_path):
    return (tmp_path / "_oa" / "teyit" / "kunye-teyit.md").read_text(encoding="utf-8")


KUNYE_LEHE = "Yargıtay 9. HD, E. 2024/111, K. 2024/222"
KUNYE_ALEYHE = "Yargıtay 22. HD, E. 2023/333, K. 2023/444"

BUYUK_DOLGU = "Kararın gerekçe bölümü sentetik satırla sürer. " * 80  # > 2KB


def _ham_yaz(dizin, ad, kunye, buyuk=True):
    dizin.mkdir(parents=True, exist_ok=True)
    icerik = f"{kunye} sayılı kararın tam metni.\n"
    if buyuk:
        icerik += BUYUK_DOLGU
    (dizin / ad).write_text(icerik, encoding="utf-8")


TRIYAJ_BELGE = f"""# OKUMA MUHAKEMESİ — sentetik iş dosyası

Genel not: çekilen kararların tamamı baştan sona okundu.

## {KUNYE_LEHE}
TRİYAJ: LEHE
HAM: lehe-karar.md
Gerekçe: kıdem tazminatı unsurları dosyamızla birebir örtüşüyor.

## {KUNYE_ALEYHE}
KARAR: ALEYHE
HAM: aleyhe-karar.md
Gerekçe: benzer olguda tazminat reddedilmiş — cephaneliğe.
"""


# ── G1 — karışık LEHE+ALEYHE içe alma + ROUND-TRIP ──────────────────────────

def test_karisik_triyaj_belgesi_kutuge_alinir_ve_round_trip(tmp_path):
    """Sentetik okuma-muhakemesi (LEHE+ALEYHE karışık) → kütükte DAMGA= ve
    DOKUM-SINIFI= tokenlı satırlar; ictihat_muhakeme_denetim'in kütük
    okuyucusu (`_kutuk_kunye_bilgisi`) ve `kunye_ortak.kutukten_son_damga`
    satırları BİREBİR geri okuyabilmeli (round-trip)."""
    _init(tmp_path)
    ham = tmp_path / "_oa" / "teyit" / "ham"
    _ham_yaz(ham, "lehe-karar.md", KUNYE_LEHE)
    _ham_yaz(ham, "aleyhe-karar.md", KUNYE_ALEYHE)
    belge = tmp_path / "okuma-muhakemesi.md"
    belge.write_text(TRIYAJ_BELGE, encoding="utf-8")

    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge), "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    assert "İÇE ALINDI" in cikti, cikti

    kutuk = _kutuk_oku(tmp_path)
    assert "DAMGA=LEHE" in kutuk, kutuk
    assert "DAMGA=ALEYHE" in kutuk, kutuk
    assert kutuk.count("DOKUM-SINIFI=tam-metin") == 2, kutuk
    # G2b — ham/ altındaki dosya döküm bağı olarak kabul edilir
    assert "[döküm](_oa/teyit/ham/lehe-karar.md)" in kutuk, kutuk

    # ROUND-TRIP — kunye_ortak + ictihat_muhakeme_denetim okuyucularıyla
    ko = _modul(KUNYE_ORTAK, "rt_kunye_ortak")
    imd = _modul(DENETIM, "rt_imd")
    kutuk_yolu = str(tmp_path / "_oa" / "teyit" / "kunye-teyit.md")
    assert ko.kutukten_son_damga(kutuk_yolu, "2024/111", "2024/222", ("9", "HD")) == "LEHE"
    assert ko.kutukten_son_damga(kutuk_yolu, "2023/333", "2023/444", ("22", "HD")) == "ALEYHE"
    bilgi = imd._kutuk_kunye_bilgisi(kutuk_yolu, "2024/111", "2024/222", ("9", "HD"))
    assert bilgi["satir_var"] and bilgi["tam_metin"], bilgi
    bilgi2 = imd._kutuk_kunye_bilgisi(kutuk_yolu, "2023/333", "2023/444", ("22", "HD"))
    assert bilgi2["satir_var"] and bilgi2["tam_metin"], bilgi2


# ── G1 — ayrıştırılamayan bölüm SESSİZCE atlanmaz ───────────────────────────

def test_ayristirilamayan_bolumler_gorunur_raporlanir_exit_0(tmp_path):
    """Damgasız künye + künyesiz damga bölümleri 'içe alınamadı: <neden>' ile
    raporlanır; hiçbir kütük satırı yazılmaz; çıkış kodu 0 kalır (araç kapı
    değildir)."""
    _init(tmp_path)
    belge = tmp_path / "okuma-muhakemesi.md"
    belge.write_text(
        "# OKUMA MUHAKEMESİ\n\n"
        "## Yargıtay 4. HD, E. 2020/10, K. 2020/20\n"
        "(sadece not — karar sınıflandırılmamış)\n\n"
        "## Genel değerlendirme\n"
        "TRİYAJ: LEHE\n"
        "(bu bölümde künye yok)\n",
        encoding="utf-8")

    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge), "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    assert cikti.count("içe alınamadı") >= 2, cikti
    assert "damga" in cikti.lower(), cikti
    assert "künye" in cikti.lower(), cikti
    assert "DAMGA=" not in _kutuk_oku(tmp_path)


# ── G1 — 2KB altı ham dosya tam-metin SAYILMAZ (bağ yine kurulur) ───────────

def test_kucuk_ham_dosya_tam_metin_sayilmaz_bag_kurulur(tmp_path):
    _init(tmp_path)
    _ham_yaz(tmp_path / "_oa" / "teyit" / "ham", "kisa.md", KUNYE_LEHE, buyuk=False)
    belge = tmp_path / "okuma-muhakemesi.md"
    belge.write_text(
        f"## {KUNYE_LEHE}\nTRİYAJ: LEHE\nHAM: kisa.md\n", encoding="utf-8")

    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge), "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = _kutuk_oku(tmp_path)
    assert "DAMGA=LEHE" in kutuk
    assert "DOKUM-SINIFI=tam-metin" not in kutuk, kutuk
    assert "[döküm](_oa/teyit/ham/kisa.md)" in kutuk, kutuk


# ── G2b — --ham-dizin ile verilen dizin de meşru döküm evrenidir ────────────

def test_ham_dizin_bayragi_mesru_dokum_evreni(tmp_path):
    _init(tmp_path)
    _ham_yaz(tmp_path / "hamlar", "ozel-karar.md", KUNYE_LEHE)
    belge = tmp_path / "okuma-muhakemesi.md"
    belge.write_text(
        f"## {KUNYE_LEHE}\nTRİYAJ: LEHE\nHAM: ozel-karar.md\n", encoding="utf-8")

    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge),
                       "--ham-dizin", "hamlar", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    kutuk = _kutuk_oku(tmp_path)
    assert "DAMGA=LEHE" in kutuk
    assert "[döküm](hamlar/ozel-karar.md)" in kutuk, kutuk
    assert "DOKUM-SINIFI=tam-metin" in kutuk, kutuk


# ── G1 — künye no'ları dökümde geçmiyorsa bağ düşer (346 dersi) ────────────

def test_kunye_dokumde_gecmiyorsa_bag_dusurulur_gorunur(tmp_path):
    """Yanlış/alakasız bir ham dosyaya bağ kurulamaz — künye no'ları dökümde
    dize olarak geçmiyorsa döküm bağı ve tam-metin iddiası DÜŞER, satır yine
    de (bağsız) işlenir, düşüş GÖRÜNÜR raporlanır."""
    _init(tmp_path)
    ham = tmp_path / "_oa" / "teyit" / "ham"
    ham.mkdir(parents=True, exist_ok=True)
    (ham / "alakasiz.md").write_text(
        "Bambaşka bir kararın metni. " + BUYUK_DOLGU, encoding="utf-8")
    belge = tmp_path / "okuma-muhakemesi.md"
    belge.write_text(
        f"## {KUNYE_LEHE}\nTRİYAJ: LEHE\nHAM: alakasiz.md\n", encoding="utf-8")

    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge), "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    assert "geçmiyor" in cikti, cikti
    kutuk = _kutuk_oku(tmp_path)
    assert "DAMGA=LEHE" in kutuk
    assert "DOKUM-SINIFI=tam-metin" not in kutuk, kutuk
    assert "[döküm]" not in kutuk, kutuk


# ── G1 — kütükteki SON DAMGA farklıysa sessiz değişim YOK ──────────────────

def test_kutukteki_son_damga_farkliysa_ice_alinmaz(tmp_path):
    """P0-2(d) simetrisi: aynı künye için kütükteki son damgadan FARKLI bir
    damga triyaj-ice-al üzerinden de sessizce vurulamaz — görünür rapor +
    `--damga-degistir` ritüeline yönlendirme."""
    _init(tmp_path)
    ham = tmp_path / "_oa" / "teyit" / "ham"
    _ham_yaz(ham, "lehe-karar.md", KUNYE_LEHE)
    belge1 = tmp_path / "b1.md"
    belge1.write_text(f"## {KUNYE_LEHE}\nTRİYAJ: LEHE\nHAM: lehe-karar.md\n",
                      encoding="utf-8")
    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge1), "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti

    belge2 = tmp_path / "b2.md"
    belge2.write_text(f"## {KUNYE_LEHE}\nTRİYAJ: ALEYHE\nHAM: lehe-karar.md\n",
                      encoding="utf-8")
    kod, cikti = _cli(["triyaj-ice-al", "--dosya", str(belge2), "--kok", str(tmp_path)],
                      cwd=tmp_path)
    assert kod == 0, cikti
    assert "içe alınamadı" in cikti, cikti
    assert "SON DAMGA farklı" in cikti, cikti
    assert "damga-degistir" in cikti, cikti
    assert "DAMGA=ALEYHE" not in _kutuk_oku(tmp_path)


# ── G2a(a) — kütük başlığında kopyala-yapıştır CLI örneği ───────────────────

def test_kutuk_basliginda_cli_ornegi_var_ve_veri_sayilmaz(tmp_path):
    """`init` şablonundaki başlık, tek satırlık kopyala-yapıştır teyit örneği
    ve triyaj-ice-al yolunu içermeli; örnek satırları kütük okuyucularında
    GERÇEK VERİ sayılmamalı (kutuk_gercek_veri_var_mi False kalır)."""
    _init(tmp_path)
    kutuk = _kutuk_oku(tmp_path)
    assert "teyit --arac ictihat_getir" in kutuk, kutuk
    assert "--dokum-sinifi tam-metin" in kutuk, kutuk
    assert "triyaj-ice-al" in kutuk, kutuk
    # örnek, token/veri okuyucularına sızmaz
    assert "DAMGA=" not in kutuk
    assert "DOKUM-SINIFI=" not in kutuk
    ko = _modul(KUNYE_ORTAK, "rt_kunye_ortak_baslik")
    assert not ko.kutuk_gercek_veri_var_mi(
        str(tmp_path / "_oa" / "teyit" / "kunye-teyit.md"))


# ── G2a(b) — teyit RET mesajları "ne yapmalı" cümlesi taşır ─────────────────

def test_teyit_getir_damgasiz_ret_ne_yapmali_icerir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(["teyit", "--arac", "ictihat_getir", "--sorgu", "kidem",
                       "--sonuc", KUNYE_LEHE, "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "Ne yapmalı" in cikti, cikti


def test_teyit_uclu_eksik_ret_ne_yapmali_icerir(tmp_path):
    _init(tmp_path)
    kod, cikti = _cli(["teyit", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "Ne yapmalı" in cikti, cikti
