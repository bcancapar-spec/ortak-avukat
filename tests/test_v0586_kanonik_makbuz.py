# -*- coding: utf-8 -*-
"""v0.5.8.6 — KANONİK MAKBUZ + ham/ DÖKÜM TANIMA (777 saha dersleri).

H3b — [T] GENİŞLETME (dilekce_denetim.py): [T] denetimi yalnız 'TESLİME
  HAZIR' ibaresini değil 'YEŞİL MAKBUZ' iddiasını da arar: _oa yaşayan
  belgelerinde YEŞİL MAKBUZ iddiası VAR ama _oa/defter/teslim-makbuz.json
  (exit_kodu=0) YOK ise BLOK sınıfı 'kanonik olmayan makbuz beyanı' bulgusu.
  Tarihçe muafiyeti (oturum/devir/dersler/arsiv-yerel) AYNEN geçerli.
  Saha kanıtı: bayat teslim_paketi stdout'u TESLIM-MAKBUZU.txt'ye
  yönlendirilip 'yeşil makbuz' beyan edildi — kanonik defter/teslim-makbuz.json
  hiç yoktu.

H3c — KANONİK TANIM CÜMLESİ: her [T] bulgu metni tek-cümle tanımı taşır:
  'yeşil makbuz = YALNIZ _oa/defter/teslim-makbuz.json (exit_kodu=0); stdout
  dökümü/txt makbuz DEĞİLDİR'.

K1 — KUNYE_TEYIT ham/ TANIMA (kunye_teyit.py): kütük Döküm sütunundaki
  bağlar `_oa/teyit/ham/` altını gösteriyorsa geçerli döküm sayılır (dokum/
  ile eşdeğer). YOL GÜVENLİĞİ korunur: kök dışına çıkan bağ yine RET.
  Saha kanıtı: model gerçek triyaj emeğini (ham dökümler + LEHE/ALEYHE)
  teyit-script formatı dışında ham/ altına yazdı, kapı göremedi.

GİZLİLİK (m.7): tüm senaryolar tmp_path + sentetik desenler; gerçek dava
no / kişi adı / gerçek yol YOKTUR.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DD_SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
             / "scripts" / "dilekce_denetim.py")
KT_SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol"
             / "scripts" / "kunye_teyit.py")


def _yukle(yol, ad):
    assert yol.is_file(), f"script bulunamadı: {yol}"
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _yukle(DD_SCRIPT, "dilekce_denetim_v0586")

TANIM_CUMLESI = ("yeşil makbuz = YALNIZ _oa/defter/teslim-makbuz.json "
                 "(exit_kodu=0); stdout dökümü/txt makbuz DEĞİLDİR")


def _makbuz_yaz(kok, veri):
    defter = kok / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps(veri, ensure_ascii=False), encoding="utf-8")


# ── H3b: YEŞİL MAKBUZ iddiası — kanonik olmayan makbuz beyanı ──────────────

def test_h3b_yesil_makbuz_iddiasi_json_yok_blok(tmp_path):
    """_oa yaşayan belgesinde 'YEŞİL MAKBUZ' iddiası var, kanonik
    defter/teslim-makbuz.json YOK → BLOK sınıfı bulgu."""
    oa = tmp_path / "_oa"
    oa.mkdir()
    (oa / "00-TESLIM.md").write_text(
        "Paket koştu, YEŞİL MAKBUZ alındı — teslim edilebilir.\n",
        encoding="utf-8")
    ihlaller = dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path))
    assert ihlaller, "kanonik makbuz yokken YEŞİL MAKBUZ iddiası BLOK olmalı"
    assert any("kanonik olmayan makbuz beyanı" in u for u in ihlaller), ihlaller
    assert any("00-TESLIM.md" in u for u in ihlaller), ihlaller


def test_h3b_yesil_makbuz_json_yesilse_gecer(tmp_path):
    """Kanonik makbuz (exit_kodu=0) fiilen varsa iddia meşrudur — bulgu yok."""
    _makbuz_yaz(tmp_path, {"exit_kodu": 0, "zaman": "2026-01-01T00:00:00"})
    oa = tmp_path / "_oa"
    (oa / "00-TESLIM.md").write_text(
        "Paket koştu, YEŞİL MAKBUZ alındı.\n", encoding="utf-8")
    assert dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path)) == []


def test_h3b_tarihcedeki_iddia_muaf(tmp_path):
    """Tarihçe muafiyeti AYNEN geçerli: oturum/devir/dersler/arsiv-yerel
    altındaki YEŞİL MAKBUZ iddiası geçmiş koşu kaydıdır, beyan değildir."""
    for dizin in ("oturum", "devir", "dersler", "arsiv-yerel"):
        alt = tmp_path / "_oa" / dizin
        alt.mkdir(parents=True)
        (alt / "kayit.md").write_text(
            "O koşuda YEŞİL MAKBUZ beyan edilmişti (tarihçe).\n",
            encoding="utf-8")
    assert dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path)) == []


def test_h3b_taslaktaki_iddia_da_yakalanir(tmp_path):
    """İddia denetlenen taslağın kendisinde de olsa aynı BLOK sınıfıdır."""
    metin = "Gövde.\n\nDenetimler bitti, YEŞİL MAKBUZ hazır.\n"
    ihlaller = dd.teslime_hazir_ihlalleri(metin, str(tmp_path))
    assert any("kanonik olmayan makbuz beyanı" in u for u in ihlaller), ihlaller


def test_h3b_olumsuzlanmis_gecis_beyan_sayilmaz(tmp_path):
    """'henüz YEŞİL MAKBUZ yok' bir İDDİA değildir — sahte pozitif üretmez."""
    oa = tmp_path / "_oa"
    oa.mkdir()
    (oa / "DURUM.md").write_text(
        "Adımlar sürüyor; henüz YEŞİL MAKBUZ yok.\n", encoding="utf-8")
    assert dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path)) == []


def test_h3b_iki_ibare_sinifi_ayri_bulgu(tmp_path):
    """Aynı kökte hem makbuzsuz 'TESLİME HAZIR' hem 'YEŞİL MAKBUZ' varsa iki
    sınıf da görünür kalır (biri diğerini yutmaz)."""
    oa = tmp_path / "_oa"
    oa.mkdir()
    (oa / "00-TESLIM.md").write_text(
        "Durum: TESLİME HAZIR. Kanıt: YEŞİL MAKBUZ alındı.\n", encoding="utf-8")
    ihlaller = dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path))
    assert any("makbuzsuz hazır-beyanı" in u for u in ihlaller), ihlaller
    assert any("kanonik olmayan makbuz beyanı" in u for u in ihlaller), ihlaller


# ── H3c: kanonik tanım cümlesi her [T] bulgusunda ──────────────────────────

def test_h3c_tanim_cumlesi_yesil_makbuz_bulgusunda(tmp_path):
    oa = tmp_path / "_oa"
    oa.mkdir()
    (oa / "00-TESLIM.md").write_text("YEŞİL MAKBUZ alındı.\n", encoding="utf-8")
    ihlaller = dd.teslime_hazir_ihlalleri("İbaresiz taslak.\n", str(tmp_path))
    assert ihlaller and all(TANIM_CUMLESI in u for u in ihlaller), ihlaller


def test_h3c_tanim_cumlesi_teslime_hazir_bulgusunda(tmp_path):
    metin = "Gövde.\n\nDurum: TESLİME HAZIR.\n"
    ihlaller = dd.teslime_hazir_ihlalleri(metin, str(tmp_path))
    assert ihlaller and all(TANIM_CUMLESI in u for u in ihlaller), ihlaller


# ── K1: kütük Döküm sütunu ham/ bağları ────────────────────────────────────

def _kt_cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(KT_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


_KUTUK_BASLIK = (
    "| Zaman | Araç | Sorgu | Sonuç (künye/madde + lehe/aleyhe) | Döküm |\n"
    "|---|---|---|---|---|\n")


def _k1_kok_kur(tmp_path, dokum_bagi, ham_dosya_yolu=None):
    """Sentetik kök: kütük satırının Sonuç hücresi künye numarası TAŞIMAZ —
    teyit ancak bağlı döküm dosyası okunursa mümkün olur (deney tasarımı)."""
    kok = tmp_path / "dava-klasoru"
    teyit = kok / "_oa" / "teyit"
    teyit.mkdir(parents=True)
    (teyit / "kunye-teyit.md").write_text(
        _KUTUK_BASLIK
        + "| 2026-01-01T00:00:00 | ictihat_getir | emsal | Yargıtay üçüncü "
          "hukuk dairesi kararı (bkz. döküm) DAMGA=LEHE | "
        + dokum_bagi + " |\n",
        encoding="utf-8")
    if ham_dosya_yolu is not None:
        ham_dosya_yolu.parent.mkdir(parents=True, exist_ok=True)
        ham_dosya_yolu.write_text(
            "HAM MCP DÖKÜMÜ — Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 "
            "sayılı kararının tam metni ...\n", encoding="utf-8")
    taslak = kok / "taslak.md"
    taslak.write_text(
        "Somut olayda Yargıtay 3. HD'nin E. 2023/1234 K. 2023/5678 sayılı "
        "kararı emsaldir.\n", encoding="utf-8")
    return kok


def test_k1_ham_bagli_dokum_teyit_sayilir(tmp_path):
    """Kütük Döküm sütunu `_oa/teyit/ham/` altını gösteriyor ve dosya künyeyi
    taşıyorsa → dokum/ ile eşdeğer TEYİT kaynağıdır (exit 0)."""
    kok = _k1_kok_kur(
        tmp_path, "_oa/teyit/ham/karar-tam-metin.md",
        ham_dosya_yolu=tmp_path / "dava-klasoru" / "_oa" / "teyit" / "ham"
        / "karar-tam-metin.md")
    kod, cikti = _kt_cli(["taslak.md", "--kok", str(kok)], cwd=kok)
    assert kod == 0, f"ham/ bağlı döküm teyit sayılmalıydı; çıktı:\n{cikti}"
    assert "TEYİTLİ" in cikti


def test_k1_kok_disina_cikan_bag_ret(tmp_path):
    """Yol güvenliği: Döküm bağı kök dışına çıkıyorsa (../) dosya künyeyi
    taşısa bile OKUNMAZ — künye TEYİTSİZ kalır (RET)."""
    disari = tmp_path / "disari" / "ham" / "gizli.md"
    kok = _k1_kok_kur(tmp_path, "../../disari/ham/gizli.md",
                      ham_dosya_yolu=disari)
    kod, cikti = _kt_cli(["taslak.md", "--kok", str(kok)], cwd=kok)
    assert kod == 1, f"kök dışına çıkan bağ RET edilmeliydi; çıktı:\n{cikti}"
    assert "TEYİTSİZ" in cikti
    assert "RET" in cikti, f"kök dışı bağ için görünür RET uyarısı yok:\n{cikti}"


def test_k1_mutlak_kok_disi_bag_ret(tmp_path):
    """Mutlak yolla kök dışına işaret eden bağ da RET edilir."""
    disari = tmp_path / "baska-yer" / "ham" / "kacak.md"
    kok = _k1_kok_kur(tmp_path, str(disari).replace("\\", "/"),
                      ham_dosya_yolu=disari)
    kod, cikti = _kt_cli(["taslak.md", "--kok", str(kok)], cwd=kok)
    assert kod == 1, f"mutlak kök-dışı bağ RET edilmeliydi; çıktı:\n{cikti}"
    assert "TEYİTSİZ" in cikti


def test_k1_bagsiz_ham_dosyasi_teyit_sayilmaz(tmp_path):
    """ham/ dizini TOPTAN yüklenmez: kütükte Döküm bağı olmayan bir ham
    dosyası teyit kaynağı DEĞİLDİR (yalnız bağlı dökümler dokum/ ile eşdeğer)."""
    kok = _k1_kok_kur(
        tmp_path, "(bağ yok)",
        ham_dosya_yolu=tmp_path / "dava-klasoru" / "_oa" / "teyit" / "ham"
        / "bagsiz-dokum.md")
    kod, cikti = _kt_cli(["taslak.md", "--kok", str(kok)], cwd=kok)
    assert kod == 1, f"bağsız ham dosyası teyit sayılmamalıydı; çıktı:\n{cikti}"
    assert "TEYİTSİZ" in cikti


def test_k1_dokum_dizini_regresyon(tmp_path):
    """dokum/ hattı AYNEN çalışır: künye izi klasik `_oa/teyit/dokum/`
    dosyasındaysa TEYİTLİ (ham/ tanıma dokum/ davranışını bozmaz)."""
    kok = _k1_kok_kur(tmp_path, "(bağ yok)", ham_dosya_yolu=None)
    dokum = kok / "_oa" / "teyit" / "dokum"
    dokum.mkdir(parents=True)
    (dokum / "d1.md").write_text(
        "Yargıtay 3. HD, E. 2023/1234 K. 2023/5678 sayılı kararı ...\n",
        encoding="utf-8")
    kod, cikti = _kt_cli(["taslak.md", "--kok", str(kok)], cwd=kok)
    assert kod == 0, f"dokum/ hattı regresyona uğradı; çıktı:\n{cikti}"
    assert "TEYİTLİ" in cikti
