# -*- coding: utf-8 -*-
"""v0.5.8.6 SÜRÜM KİLİDİ — 777 saha dersleri (bayat nesil araç + kanonik makbuz).

Saha bulgusu (777 filosu): masaüstü uygulama SKILL'leri bayat paketten servis
etti; model bayat kiti `_oa/araclar`a kopyalayıp koştu — eski udf_yaz açılamayan
UDF üretti; bayat teslim_paketi stdout'u `TESLIM-MAKBUZU.txt`ye yönlendirilip
"yeşil makbuz" BEYAN edildi (kanonik `defter/teslim-makbuz.json` hiç yoktu);
defter adım kayıtlarının 33/42'si elle (imzasız) düştü, 6 parçanın kanıtı
"ELDEN:" ile başladığı hâlde statü UYGULANDI kaldı.

Bu dosya dört kilidi doğrular:
  H2a — ÖZELLİK PARMAK İZİ: `_oa/araclar` kritik kopyalarında zorunlu dizge
        denetimi; eksik = "BAYAT NESİL ARAÇ — üretimde KULLANMA" sınıfı uyarı
        (hook-prompt enjeksiyonu + hook-denetle çıktısı + {tip:hook,
        olay:bayat-arac} defter olayı).
  H2b — VERSION DAMGASI: `_oa/araclar/VERSION.json` yok = damgasız çanta;
        sürüm farklı = bayat çanta; uyumlu = sessiz.
  G3a — --adim-batch: tek çağrıda çok adım kaydı, TÜMÜ araç-imzalı; mevcut
        kanıt/önkoşul kuralları AYNEN (kanıtsız UYGULANDI yine RET).
  G3b — ELDEN-TÜRETİLMİŞ GÖRÜNÜM: kanıtı "ELDEN" ile başlayan VEYA
        imzasız+script-artefaktsız UYGULANDI kayıtları DURUM.md'de
        "UYGULANDI (ELDEN-türetilmiş)" gösterilir + ayrı sayaç; kayıt
        DEĞİŞTİRİLMEZ (append-only).
  H3a — KANONİK OLMAYAN MAKBUZ: kökte makbuz-şekilli .txt var ama
        `defter/teslim-makbuz.json` (exit 0) yoksa görünür uyarı.

Tüm testler tmp_path + sentetik desenler kullanır (repo kuralı — gerçek dava
numarası/kişi adı/klasör yolu ASLA yazılmaz).
"""
import argparse
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
SKILLS = PLUGIN / "skills"
PK = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


@pytest.fixture(scope="module")
def pk():
    spec = importlib.util.spec_from_file_location("_test_v0586_pk", PK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_v0586_pk"] = mod
    spec.loader.exec_module(mod)
    return mod


def _temiz_env():
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    return env


def _kos(args, kok, stdin_metni=""):
    cp = subprocess.run([sys.executable, str(PK)] + args, capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        cwd=str(kok), input=stdin_metni, timeout=120,
                        env=_temiz_env())
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


def _dava_klasoru_kur(kok, defterli=False):
    for i in ("001", "002", "003"):
        (kok / f"{i}_Sentetik_Evrak.pdf").write_text("sentetik", encoding="utf-8")
    if defterli:
        (kok / "_oa" / "defter").mkdir(parents=True, exist_ok=True)


def _gercek_script(ad):
    """Yüklü eklentideki gerçek scripti bulur (skills/*/scripts/<ad>)."""
    adaylar = sorted(SKILLS.glob(f"*/scripts/{ad}"))
    assert adaylar, f"{ad} eklentide bulunamadı"
    return adaylar[0]


def _olaylar(kok):
    jsonl = kok / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    if not jsonl.is_file():
        return []
    return [json.loads(s) for s in jsonl.read_text(encoding="utf-8").splitlines()
            if s.strip()]


# ═══ H2a — ÖZELLİK PARMAK İZİ ══════════════════════════════════════════════

def test_parmak_izi_eski_udf_yaz_bayat_nesil(pk, tmp_path):
    """Parmak izi dizgeleri olmayan udf_yaz.py kopyası = BAYAT NESİL sınıfı
    uyarı (777: eski udf_yaz açılamayan UDF üretti)."""
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "udf_yaz.py").write_text(
        "# sentetik v1.1 nesli kopya — yonetmelik kenari / hvl stili / makbuz yok\n",
        encoding="utf-8")
    uyari = pk._bayat_arac_uyarisi(str(tmp_path))
    assert uyari is not None
    assert "BAYAT NESİL" in uyari
    assert "üretimde KULLANMA" in uyari
    assert "udf_yaz.py" in uyari


def test_parmak_izi_eksik_dizge_adiyla_soylenir(pk, tmp_path):
    """teslim_paketi.py'de teslim-makbuz.json, oa_hafiza.py'de --damga
    yoksa hangi dizgenin eksik olduğu uyarıda görünür."""
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "teslim_paketi.py").write_text(
        "# eski nesil: stdout'a yesil yazar, kanonik makbuz bilmez\n",
        encoding="utf-8")
    (araclar / "oa_hafiza.py").write_text(
        "# eski nesil: damga ritueli yok\n", encoding="utf-8")
    uyari = pk._bayat_arac_uyarisi(str(tmp_path))
    assert uyari is not None and "BAYAT NESİL" in uyari
    assert "teslim_paketi.py" in uyari and "teslim-makbuz.json" in uyari
    assert "oa_hafiza.py" in uyari and "--damga" in uyari


def test_parmak_izi_guncel_kopyalar_sessiz(pk, tmp_path):
    """Yüklü eklentiden bayt-özdeş alınan kritik kopyalar = SESSİZ (parmak
    izleri güncel kaynakta zaten var)."""
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    for ad in ("udf_yaz.py", "teslim_paketi.py", "oa_hafiza.py"):
        (araclar / ad).write_bytes(_gercek_script(ad).read_bytes())
    assert pk._bayat_arac_uyarisi(str(tmp_path)) is None


def test_parmak_izi_kritik_olmayan_dosya_nesil_saymaz(pk, tmp_path):
    """Parmak izi yalnız kritik scriptlere bakar: alakasız sentetik bir .py
    kopyası BAYAT NESİL sınıfına GİRMEZ (bayt-kıyas uyarısı ayrı konudur)."""
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "sentetik_yardimci.py").write_text("print('x')\n", encoding="utf-8")
    uyari = pk._bayat_arac_uyarisi(str(tmp_path))
    assert uyari is None or "BAYAT NESİL" not in uyari


def test_bayat_nesil_hook_denetle_cikti_ve_defter_olayi(tmp_path):
    """--hook-denetle: BAYAT NESİL uyarısı stdout'ta görünür VE deftere
    {tip:hook, olay:bayat-arac} olayı düşer."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "udf_yaz.py").write_text("# eski nesil kopya\n", encoding="utf-8")
    kod, out, err = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    assert "BAYAT NESİL" in out
    olaylar = _olaylar(tmp_path)
    assert any(o.get("tip") == "hook" and o.get("olay") == "bayat-arac"
               for o in olaylar), "bayat-arac hook olayı deftere düşmedi"


def test_bayat_nesil_hook_prompt_enjeksiyonu(tmp_path):
    """--hook-prompt (hat açık): BAYAT NESİL uyarısı additionalContext
    enjeksiyonuna girer."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "udf_yaz.py").write_text("# eski nesil kopya\n", encoding="utf-8")
    kod, out, err = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    veri = json.loads(out)
    baglam = veri["hookSpecificOutput"]["additionalContext"]
    assert "BAYAT NESİL" in baglam and "üretimde KULLANMA" in baglam


# ═══ H2b — VERSION DAMGASI ═════════════════════════════════════════════════

def test_version_yoksa_damgasiz_canta_uyarisi(pk, tmp_path):
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "sentetik_arac.py").write_text("print('x')\n", encoding="utf-8")
    uyari = pk._arac_version_uyarisi(str(tmp_path))
    assert uyari is not None and "DAMGASIZ" in uyari and "VERSION.json" in uyari


def test_version_farkli_bayat_uyarisi(pk, tmp_path):
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "VERSION.json").write_text(
        json.dumps({"surum": "0.5.1"}), encoding="utf-8")
    uyari = pk._arac_version_uyarisi(str(tmp_path))
    assert uyari is not None and "BAYAT" in uyari
    assert "0.5.1" in uyari and pk.OA_SURUM in uyari


def test_version_uyumlu_sessiz(pk, tmp_path):
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "VERSION.json").write_text(
        json.dumps({"surum": pk.OA_SURUM}), encoding="utf-8")
    assert pk._arac_version_uyarisi(str(tmp_path)) is None


def test_version_araclar_yoksa_sessiz(pk, tmp_path):
    assert pk._arac_version_uyarisi(str(tmp_path)) is None


def test_version_uyarisi_hook_denetle_ciktisinda(tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    araclar = tmp_path / "_oa" / "araclar"
    araclar.mkdir(parents=True)
    (araclar / "sentetik_arac.py").write_text("print('x')\n", encoding="utf-8")
    kod, out, err = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    assert "DAMGASIZ" in out


# ═══ G3a — --adim-batch ════════════════════════════════════════════════════

def _defter_ac(kok):
    kod, out, err = _kos(["--baslat", "Sentetik Batch Dosyası",
                          "--kok", str(kok)], kok)
    assert kod == 0, err
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 3, "kaynak": "sentetik"}), encoding="utf-8")


def test_adim_batch_coklu_kayit_tumu_arac_imzali(pk, tmp_path):
    """Tek çağrıda iki adım kaydı; her ikisi de defterde ARAÇ-İMZALI durur."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    batch = tmp_path / "batch.json"
    batch.write_text(json.dumps([
        {"adim": 1, "parca": "oa-interview", "durum": "UYGULANDI",
         "kanit": "sentetik mülakat notları toplandı, hedef/süre soruldu (batch provası)"},
        {"adim": 2, "parca": "oa-alan", "durum": "UYGULANDI",
         "kanit": "sentetik alan konumlaması yapıldı, ihtisas dairesi not edildi (batch provası)"},
    ], ensure_ascii=False), encoding="utf-8")
    kod, out, err = _kos(["--adim-batch", str(batch), "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err + out
    adim_olaylar = [o for o in _olaylar(tmp_path) if o.get("tip") == "adim"]
    assert len(adim_olaylar) == 2
    assert all(pk._olay_arac_imzali_mi(o) for o in adim_olaylar), \
        "batch kayıtları araç-imzalı değil"
    assert {o["parca"] for o in adim_olaylar} == {"oa-interview", "oa-alan"}


def test_adim_batch_kanitsiz_uygulandi_ret(tmp_path):
    """Batch yolu kanıt kapısını GEVŞETMEZ: kanıtsız UYGULANDI yine RET."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    batch = tmp_path / "batch.json"
    batch.write_text(json.dumps([
        {"adim": 1, "parca": "oa-interview", "durum": "UYGULANDI"},
    ]), encoding="utf-8")
    kod, out, err = _kos(["--adim-batch", str(batch), "--kok", str(tmp_path)], tmp_path)
    assert kod != 0
    assert "RET" in (out + err)
    assert not [o for o in _olaylar(tmp_path) if o.get("tip") == "adim"]


def test_adim_batch_onkosul_kapisi_aynen(tmp_path):
    """Önkoşul kuralları AYNEN: 00-kunye.json yokken adım 1+ UYGULANDI
    batch üzerinden de yazılamaz (İNGEST-ÖNCE)."""
    _dava_klasoru_kur(tmp_path)
    kod, _o, err = _kos(["--baslat", "Sentetik Batch Dosyası",
                         "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    batch = tmp_path / "batch.json"
    batch.write_text(json.dumps([
        {"adim": 1, "parca": "oa-interview", "durum": "UYGULANDI",
         "kanit": "sentetik mülakat notları toplandı, hedef/süre soruldu (batch provası)"},
    ], ensure_ascii=False), encoding="utf-8")
    kod, out, err = _kos(["--adim-batch", str(batch), "--kok", str(tmp_path)], tmp_path)
    assert kod != 0
    assert "İNGEST-ÖNCE" in (out + err)


def test_adim_batch_bozuk_dosya_hata(tmp_path):
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    batch = tmp_path / "batch.json"
    batch.write_text("{bozuk json", encoding="utf-8")
    kod, out, err = _kos(["--adim-batch", str(batch), "--kok", str(tmp_path)], tmp_path)
    assert kod != 0
    assert "HATA" in (out + err)


# ═══ G3b — ELDEN-TÜRETİLMİŞ GÖRÜNÜM ════════════════════════════════════════

def _elle_satir_dus(kok, olay):
    """İmzasız (model-beyanlı) satırı deftere DOĞRUDAN yazar — saha deseni."""
    jsonl = kok / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    with open(jsonl, "a", encoding="utf-8") as f:
        f.write(json.dumps(olay, ensure_ascii=False) + "\n")


def test_elden_onekli_kanit_turetilmis_gosterilir(pk, tmp_path):
    """Kanıtı 'ELDEN' ile başlayan UYGULANDI kaydı DURUM.md'de
    'UYGULANDI (ELDEN-türetilmiş)' görünür; jsonl kaydı DEĞİŞMEZ."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    _elle_satir_dus(tmp_path, {
        "zaman": "2026-08-17T10:00:00", "tip": "adim", "adim": 1,
        "parca": "oa-interview", "durum": "UYGULANDI",
        "kanit": "ELDEN: mülakat elden yürütüldü, script koşulmadı (sentetik)"})
    pk._durum_md_yaz(str(tmp_path))
    durum_md = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "UYGULANDI (ELDEN-türetilmiş)" in durum_md
    assert "ELDEN-türetilmiş sayacı: 1" in durum_md
    # append-only: kayıt diskte hâlâ ham UYGULANDI olarak durur
    ham = [o for o in _olaylar(tmp_path) if o.get("tip") == "adim"]
    assert ham and ham[-1]["durum"] == "UYGULANDI"


def test_imzasiz_scriptli_artefaktsiz_turetilmis(pk, tmp_path):
    """İmzasız + script-artefaktsız UYGULANDI (SCRIPT'li parça) da
    ELDEN-türetilmiş sayılır (777: 33/42 elle satır)."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    _elle_satir_dus(tmp_path, {
        "zaman": "2026-08-17T10:00:00", "tip": "adim", "adim": 4,
        "parca": "oa-vakia", "durum": "UYGULANDI",
        "kanit": "vakia matrisi kuruldu diyorum ama diskte iz yok (sentetik)"})
    pk._durum_md_yaz(str(tmp_path))
    durum_md = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "UYGULANDI (ELDEN-türetilmiş)" in durum_md
    assert "ELDEN-türetilmiş sayacı: 1" in durum_md


def test_arac_imzali_artefaktli_kayit_turetilmez(pk, tmp_path):
    """CLI'den geçen, kanıtı ELDEN'siz kayıt DÜZ UYGULANDI kalır — sayaç yok."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, out, err = _kos(["--isle", "--adim", "1", "--parca", "oa-interview",
                          "--durum", "UYGULANDI",
                          "--kanit", "sentetik mülakat notları toplandı, hedef soruldu",
                          "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    pk._durum_md_yaz(str(tmp_path))
    durum_md = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "ELDEN-türetilmiş sayacı" not in durum_md
    assert "(ELDEN-türetilmiş)" not in durum_md


# ═══ H3a — KANONİK OLMAYAN MAKBUZ ══════════════════════════════════════════

def test_kanonik_olmayan_makbuz_txt_var_json_yok(pk, tmp_path):
    """Kökte TESLIM-MAKBUZU.txt var, kanonik json yok → görünür uyarı
    (777: bayat teslim_paketi stdout'u dosyaya yönlendirilip yeşil beyan)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "TESLIM-MAKBUZU.txt").write_text(
        "TESLİME HAZIR (sentetik sahte yeşil)", encoding="utf-8")
    uyari = pk._kanonik_olmayan_makbuz_uyarisi(str(tmp_path))
    assert uyari is not None
    assert "KANONİK OLMAYAN MAKBUZ" in uyari
    assert "teslim-makbuz.json" in uyari
    assert "TESLIM-MAKBUZU.txt" in uyari


def test_kanonik_olmayan_makbuz_yildizli_desen(pk, tmp_path):
    """*makbuz*.txt sınıfı da yakalanır (ad değiştirip kaçma yok)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "yesil-makbuz-ozeti.txt").write_text("sentetik", encoding="utf-8")
    uyari = pk._kanonik_olmayan_makbuz_uyarisi(str(tmp_path))
    assert uyari is not None and "KANONİK OLMAYAN MAKBUZ" in uyari


def test_kanonik_makbuz_yesilse_sessiz(pk, tmp_path):
    """Kanonik defter/teslim-makbuz.json exit_kodu=0 varsa .txt zararsız —
    uyarı YOK (tek ölçüt kanonik makbuzdur; txt yalnız fazlalıktır)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "TESLIM-MAKBUZU.txt").write_text("sentetik", encoding="utf-8")
    (tmp_path / "_oa" / "defter" / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    assert pk._kanonik_olmayan_makbuz_uyarisi(str(tmp_path)) is None


def test_kanonik_makbuz_red_ise_uyari_var(pk, tmp_path):
    """json var ama exit_kodu != 0 → txt yine dayanak OLAMAZ, uyarı sürer."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "TESLIM-MAKBUZU.txt").write_text("sentetik", encoding="utf-8")
    (tmp_path / "_oa" / "defter" / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 1}), encoding="utf-8")
    assert pk._kanonik_olmayan_makbuz_uyarisi(str(tmp_path)) is not None


def test_makbuz_txt_yoksa_sessiz(pk, tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    assert pk._kanonik_olmayan_makbuz_uyarisi(str(tmp_path)) is None


def test_kanonik_olmayan_makbuz_hook_denetle_ciktisinda(tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "TESLIM-MAKBUZU.txt").write_text("sentetik", encoding="utf-8")
    kod, out, err = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    assert "KANONİK OLMAYAN MAKBUZ" in out


def test_kanonik_olmayan_makbuz_hook_prompt_enjeksiyonu(tmp_path):
    """Hat açıkken hook-prompt enjeksiyonuna girer."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "TESLIM-MAKBUZU.txt").write_text("sentetik", encoding="utf-8")
    kod, out, err = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    veri = json.loads(out)
    assert "KANONİK OLMAYAN MAKBUZ" in veri["hookSpecificOutput"]["additionalContext"]


def test_kanonik_olmayan_makbuz_hook_prompt_hat_kapaliyken(tmp_path):
    """Defter hiç açılmamışken de (777'nin ta kendisi) devir metnine eklenir."""
    _dava_klasoru_kur(tmp_path, defterli=False)
    (tmp_path / "_oa").mkdir()  # dava klasörü sayılır, defter YOK
    (tmp_path / "TESLIM-MAKBUZU.txt").write_text("sentetik", encoding="utf-8")
    kod, out, err = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    veri = json.loads(out)
    assert "KANONİK OLMAYAN MAKBUZ" in veri["hookSpecificOutput"]["additionalContext"]
