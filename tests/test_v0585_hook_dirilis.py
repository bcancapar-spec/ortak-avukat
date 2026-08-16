# -*- coding: utf-8 -*-
"""v0.5.8.5 HOOK DİRİLİŞİ — UserPromptSubmit üç sahada üç farklı nedenle öldü.

Son ölüm nedeni (saha): `_dosya_klasoru_mu` Yargı PRO klon kökünü tanımıyor
(klon kökünde NNN_ evrak deseni yok; uyap-project.json + evraklar/ + INDEX.md
var) VE hook_prompt/hook_pretool kök keşfi hook_denetle ile ASİMETRİKTİ
(stdin payload'ındaki cwd hiç okunmuyordu → süreç CWD'si dava klasörünün
dışındayken hook sessiz no-op'a düşüyordu).

Bu dosya dirilişin kanıtlarını kilitler:
  C1 — KLON İMZASI: uyap-project.json / evraklar/ / (INDEX.md ∧ dava-analiz.md)
       ve 4-haneli yıl önekli evrak deseni (^\\d{3,4}[_-]).
  C2 — KÖK SİMETRİSİ: hook-prompt/hook-pretool stdin payload cwd okur.
  C3 — HOOK NABZI: .hook-son-iz.json olay-başına ISO damga + ölü-prompt uyarısı.
  C4 — AÇILIŞ ENVANTERİ: SessionStart → hook-acilis envanter enjeksiyonu.
  C5 — ELDEN statüsü: script'li parça, kanıtta _oa/ artefakt yolu yoksa
       UYGULANDI yerine ELDEN yazılır; denetle tek özet satırı basar.
  B3 — mühürsüz UDF'de udf_dogrula İN-PROCESS advisory + denetle-udf olayı.
  B5 — bayat mühür (.prov.json sha uyumsuz) otomatik tazelenir
       (was_derived_from=eski-sha); sign.sgn'li ürün BAYAT sayılmaz.
  A4.8b — teslim-makbuz-RED.json varken RED satırı gizlenemez.

Tüm testler tmp_path + sentetik desenler kullanır (repo kuralı m.7 —
gerçek dava numarası/kişi adı/klasör yolu ASLA yazılmaz).
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
PK = PLUGIN / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"


@pytest.fixture(scope="module")
def pk():
    spec = importlib.util.spec_from_file_location("_test_v0585_pk", PK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_v0585_pk"] = mod
    spec.loader.exec_module(mod)
    return mod


def _temiz_env():
    """CLAUDE_PROJECT_DIR test makinesinde dolu olabilir — deterministik kök
    keşfi için alt süreç ortamından çıkarılır."""
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
    """Klasik UYAP indirmesi: 3 adet NNN_ evrak."""
    for i in ("001", "002", "003"):
        (kok / f"{i}_Sentetik_Evrak.pdf").write_text("sentetik", encoding="utf-8")
    if defterli:
        (kok / "_oa" / "defter").mkdir(parents=True, exist_ok=True)


def _klon_koku_kur(kok):
    """Sentetik Yargı PRO klon kökü: NNN_ deseni YOK — eski imza kör kalırdı.
    Kökte uyap-project.json + evraklar/ + INDEX.md durur."""
    (kok / "uyap-project.json").write_text(
        json.dumps({"dosya": "2024/123 Esas", "kaynak": "sentetik"}),
        encoding="utf-8")
    (kok / "evraklar").mkdir(exist_ok=True)
    (kok / "evraklar" / "2024_Sentetik_Dilekce.pdf").write_text(
        "sentetik", encoding="utf-8")
    (kok / "INDEX.md").write_text("# İndeks (sentetik)", encoding="utf-8")


def _defter_ac(kok):
    """--baslat + İNGEST-ÖNCE fikstürü (adım>=1 UYGULANDI için 00-kunye.json)."""
    kod, _out, err = _kos(["--baslat", "2024/123 Esas — sentetik dosya",
                           "--kok", str(kok)], kok)
    assert kod == 0, err
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


_ELLE_UDF_ICERIK = (
    "import zipfile\n"
    "with zipfile.ZipFile('taslak.udf', 'w') as z:\n"
    "    z.writestr('content.xml', '<template/>')\n")


# ── C1 — KLON İMZASI ────────────────────────────────────────────────────────

def test_klon_koku_uyap_project_json_ile_taninir(tmp_path, pk):
    (tmp_path / "uyap-project.json").write_text("{}", encoding="utf-8")
    assert pk._dosya_klasoru_mu(str(tmp_path)) is True


def test_klon_koku_evraklar_dizini_ile_taninir(tmp_path, pk):
    (tmp_path / "evraklar").mkdir()
    assert pk._dosya_klasoru_mu(str(tmp_path)) is True


def test_klon_koku_index_ve_dava_analiz_cifti_ile_taninir(tmp_path, pk):
    (tmp_path / "INDEX.md").write_text("# indeks", encoding="utf-8")
    (tmp_path / "dava-analiz.md").write_text("# analiz", encoding="utf-8")
    assert pk._dosya_klasoru_mu(str(tmp_path)) is True


def test_tek_basina_index_md_dava_klasoru_sayilmaz(tmp_path, pk):
    """INDEX.md tek başına (dava-analiz.md olmadan) yeterli DEĞİL — her
    markdown deposu dava klasörü sanılmasın (yanlış-pozitif disiplini)."""
    (tmp_path / "INDEX.md").write_text("# sıradan depo indeksi", encoding="utf-8")
    assert pk._dosya_klasoru_mu(str(tmp_path)) is False


def test_dort_haneli_yil_onekli_evraklar_taninir(tmp_path, pk):
    """Evrak deseni ^\\d{3}[_-] → ^\\d{3,4}[_-]: 4 haneli yıl önekleri."""
    for ad in ("2023_Sentetik_Esas.pdf", "2024-Sentetik_Karar.pdf",
               "2025_Sentetik_Teblig.pdf"):
        (tmp_path / ad).write_text("sentetik", encoding="utf-8")
    assert pk._dosya_klasoru_mu(str(tmp_path)) is True


def test_duz_klasor_hala_taninmaz(tmp_path, pk):
    (tmp_path / "notlar.md").write_text("alışveriş listesi", encoding="utf-8")
    assert pk._dosya_klasoru_mu(str(tmp_path)) is False


# ── C2 — KÖK SİMETRİSİ (dirilişin kanıtı) ──────────────────────────────────

def test_hook_prompt_klon_kokunde_stdin_cwd_ile_enjekte_eder(tmp_path):
    """SAHA ÖLÜMÜNÜN BİREBİR TAKLİDİ: süreç CWD'si dava klasörünün DIŞINDA,
    --kok verilmiyor (hooks.json vermez); yalnız stdin payload'ındaki `cwd`
    klon kökünü gösteriyor → enjeksiyon YİNE basılır (diriliş kanıtı)."""
    klon = tmp_path / "klon"
    klon.mkdir()
    _klon_koku_kur(klon)
    baska_yer = tmp_path / "baska-yer"
    baska_yer.mkdir()
    payload = json.dumps({"cwd": str(klon)})
    kod, out, _e = _kos(["--hook-prompt"], baska_yer, payload)
    assert kod == 0, "hook ASLA bloklamaz"
    veri = json.loads(out.strip())
    ozgu = veri["hookSpecificOutput"]
    assert ozgu["hookEventName"] == "UserPromptSubmit"
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in ozgu["additionalContext"]


def test_hook_pretool_klon_kokunde_ask_basar(tmp_path):
    """Klon kökünde (NNN_ deseni YOK) elle-UDF girişimi 'ask' kararına düşer —
    hook_pretool da klon imzasını + stdin cwd'yi tanır."""
    klon = tmp_path / "klon"
    klon.mkdir()
    _klon_koku_kur(klon)
    baska_yer = tmp_path / "baska-yer"
    baska_yer.mkdir()
    payload = json.dumps({"cwd": str(klon),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool"], baska_yer, payload)
    assert kod == 0
    veri = json.loads(out.strip())
    assert veri["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_hook_pretool_acik_kok_davranisi_korunur(tmp_path):
    """Mevcut sözleşme: --kok AÇIKÇA verilmişse yalnız o kök denetlenir
    (test_v0584_hook_katmani sözleşmesinin regresyon kilidi)."""
    _dava_klasoru_kur(tmp_path)
    payload = json.dumps({"cwd": str(tmp_path),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0
    assert json.loads(out.strip())["hookSpecificOutput"]["permissionDecision"] == "ask"


# ── C3 — HOOK NABZI ─────────────────────────────────────────────────────────

def _nabiz_oku(kok):
    yol = kok / "_oa" / "defter" / ".hook-son-iz.json"
    if not yol.is_file():
        return {}
    return json.loads(yol.read_text(encoding="utf-8"))


def test_nabiz_damgalari_olay_basina_yazilir(tmp_path):
    """.hook-son-iz.json şeması olay-başına genişler: prompt/denetle ISO
    damgaları AYNI dosyada birlikte yaşar (hash alanı da korunur)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, _out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    nabiz = _nabiz_oku(tmp_path)
    assert nabiz.get("prompt"), "prompt damgası yazılmadı"
    kod, _out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    nabiz = _nabiz_oku(tmp_path)
    assert nabiz.get("prompt"), "denetle koşusu prompt damgasını SİLMEMELİ (merge)"
    assert nabiz.get("denetle"), "denetle damgası yazılmadı"
    # ISO biçim: datetime.fromisoformat çözebilmeli
    import datetime as _dt
    _dt.datetime.fromisoformat(nabiz["prompt"])
    _dt.datetime.fromisoformat(nabiz["denetle"])


def test_hook_denetle_olu_prompt_uyarisi_basar(tmp_path):
    """Kapanış-sınıfı koşuda prompt damgası hiç yoksa görünür uyarı basılır —
    'prompt kancası bu oturumda/dönemde hiç ateşlemedi' sınıfı."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, "Stop hook ASLA bloklamaz"
    assert "HOOK NABZI" in out and "prompt" in out.lower()


def test_prompt_atesledikten_sonra_olu_prompt_uyarisi_susar(tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "HOOK NABZI" not in out, "taze prompt damgası varken uyarı gürültüdür"


# ── C4 — AÇILIŞ ENVANTERİ (SessionStart → hook-acilis) ─────────────────────

def test_hook_acilis_dava_klasorunde_envanter_enjekte_eder(tmp_path):
    _dava_klasoru_kur(tmp_path)
    kod, out, _e = _kos(["--hook-acilis", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, "SessionStart hook'u ASLA bloklamaz"
    veri = json.loads(out.strip())
    ozgu = veri["hookSpecificOutput"]
    assert ozgu["hookEventName"] == "SessionStart"
    metin = ozgu["additionalContext"]
    for script in ("oa_ingest", "tam_tur", "oa_hafiza", "teslim_paketi",
                   "dilekce_denetim", "udf_yaz", "muhur_yaz", "kaynak_blogu",
                   "grafik_denetim", "vakia_matris", "gizlilik_tara"):
        assert script in metin, f"envanterde eksik script: {script}"
    assert "udf_yaz.py üzerinden" in metin
    assert "npx" in metin and "makbuz" in metin


def test_hook_acilis_dava_disi_klasorde_sessiz(tmp_path):
    (tmp_path / "notlar.md").write_text("sıradan depo", encoding="utf-8")
    kod, out, _e = _kos(["--hook-acilis", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0 and out.strip() == ""


def test_hooks_json_sessionstart_hook_acilis_kayitli():
    veri = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
    assert "SessionStart" in veri, "SessionStart hook'u kayıtlı değil"
    komut = json.dumps(veri["SessionStart"], ensure_ascii=False)
    assert "hook-acilis" in komut
    assert "run-hook.cmd" in komut
    assert "||" not in komut


# ── C5 — ELDEN STATÜSÜ ─────────────────────────────────────────────────────

def test_scriptli_parca_yolsuz_kanit_ELDEN_dusurulur(tmp_path):
    """Kanıtta _oa/ altı artefakt yolu YOK → UYGULANDI yerine ELDEN yazılır."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, out, err = _kos(["--isle", "--adim", "1", "--parca", "oa-sure",
                          "--durum", "UYGULANDI",
                          "--kanit", "sure_hesapla.py script fiilen koşuldu, sonuç konsola yazıldı",
                          "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    assert "ELDEN" in out
    durum = json.loads((tmp_path / "_oa" / "defter" / "pipeline-durum.json")
                       .read_text(encoding="utf-8"))
    assert durum["adimlar"]["1"]["parcalar"]["oa-sure"]["durum"] == "ELDEN"


def test_scriptli_parca_diskte_olmayan_yol_ELDEN_dusurulur(tmp_path):
    """Kanıtta yol VAR ama diskte YOK → yine ELDEN (hayalet yol kanıt değildir)."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, out, _err = _kos(["--isle", "--adim", "1", "--parca", "oa-sure",
                           "--durum", "UYGULANDI",
                           "--kanit", "sure_hesapla.py koştu; çıktı: _oa/cikti/01-sure-hayalet.md",
                           "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    durum = json.loads((tmp_path / "_oa" / "defter" / "pipeline-durum.json")
                       .read_text(encoding="utf-8"))
    assert durum["adimlar"]["1"]["parcalar"]["oa-sure"]["durum"] == "ELDEN"


def test_scriptli_parca_gecerli_artefakt_yolu_UYGULANDI_kalir(tmp_path):
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "01-sure-hesap.md").write_text(
        "TEZ: süre hesabı deterministik yapıldı (sentetik).", encoding="utf-8")
    kod, out, _err = _kos(["--isle", "--adim", "1", "--parca", "oa-sure",
                           "--durum", "UYGULANDI",
                           "--kanit", "sure_hesapla.py koştu; çıktı: _oa/cikti/01-sure-hesap.md",
                           "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "→ UYGULANDI" in out
    durum = json.loads((tmp_path / "_oa" / "defter" / "pipeline-durum.json")
                       .read_text(encoding="utf-8"))
    assert durum["adimlar"]["1"]["parcalar"]["oa-sure"]["durum"] == "UYGULANDI"


def test_scriptsiz_parca_ELDEN_dusurulmez(tmp_path):
    """SCRIPTLI kümesinde olmayan parça (ör. oa-ictihat) yol şartı taşımaz."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, _out, _err = _kos(["--isle", "--adim", "3", "--parca", "oa-ictihat",
                            "--durum", "UYGULANDI",
                            "--kanit", "ictihat_ara 'sentetik sorgu' → 3 künye teyitli, kütüğe işlendi",
                            "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    durum = json.loads((tmp_path / "_oa" / "defter" / "pipeline-durum.json")
                       .read_text(encoding="utf-8"))
    assert durum["adimlar"]["3"]["parcalar"]["oa-ictihat"]["durum"] == "UYGULANDI"


def test_elden_denetle_tek_ozet_satiri(tmp_path):
    """Birden çok ELDEN adım için 'script izi yok' çoklu uyarısı YOK — tek
    özet satırı var (uyum maliyeti = uyum; gürültü tek satıra iner)."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    for adim, parca in (("1", "oa-sure"), ("4", "oa-vakia")):
        kod, _o, err = _kos(["--isle", "--adim", adim, "--parca", parca,
                             "--durum", "UYGULANDI",
                             "--kanit", "script elden koşuldu, artefakt yolu kaydedilmedi (sentetik)",
                             "--kok", str(tmp_path)], tmp_path)
        assert kod == 0, err
    kod, out, _err = _kos(["--denetle", "--kok", str(tmp_path)], tmp_path)
    # (diğer adımlar BEKLIYOR — exit 1 beklenir; ELDEN bunun sebebi DEĞİL)
    assert "script izi yok" not in out, "ELDEN kalemleri tek özete inmeliydi"
    ozet_satirlari = [s for s in out.splitlines() if "ELDEN" in s]
    assert len(ozet_satirlari) == 1, f"tek özet satırı beklenirdi: {ozet_satirlari}"
    assert "1/oa-sure" in ozet_satirlari[0] and "4/oa-vakia" in ozet_satirlari[0]


def test_elden_durum_md_ayri_sayilir(tmp_path):
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, _o, err = _kos(["--isle", "--adim", "1", "--parca", "oa-sure",
                         "--durum", "UYGULANDI",
                         "--kanit", "script elden koşuldu, artefakt yolu kaydedilmedi (sentetik)",
                         "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    durum_md = (tmp_path / "_oa" / "DURUM.md").read_text(encoding="utf-8")
    assert "ELDEN" in durum_md
    assert "ELDEN sayacı: 1" in durum_md


# ── B3 — ZİNCİR-DIŞI GÖRÜNÜRLÜK (denetle-udf advisory) ─────────────────────

def test_muhursuz_udf_denetle_advisory_ve_hook_olayi(tmp_path):
    """Mühürsüz UDF bulununca udf_dogrula İN-PROCESS advisory koşar; sonuç
    çıktıya VE deftere {tip:hook, olay:denetle-udf} olarak düşer."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "taslak.udf").write_bytes(b"PK\x03\x04bozuk-sentetik")
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "UDF DOĞRULAMA" in out
    assert "taslak.udf" in out
    jsonl = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    assert jsonl.is_file()
    olaylar = [json.loads(s) for s in jsonl.read_text(encoding="utf-8").splitlines()
               if s.strip()]
    assert any(o.get("tip") == "hook" and o.get("olay") == "denetle-udf"
               for o in olaylar), "denetle-udf hook olayı deftere düşmedi"


def test_udf_kenar_kontrolu_dort_kenar_4252(tmp_path, pk):
    """pageFormat 4x42.52 kontrolü: uyumlu içerik temiz (None), eksik kenar
    metinli bulgu döndürür."""
    uyumlu = tmp_path / "uyumlu.udf"
    with zipfile.ZipFile(uyumlu, "w") as z:
        z.writestr("content.xml",
                   '<template><properties><pageFormat mediaSizeName="1" '
                   'leftMargin="42.52" rightMargin="42.52" topMargin="42.52" '
                   'bottomMargin="42.52" paperOrientation="1"/></properties>'
                   "</template>")
    assert pk._udf_kenar_kontrol(str(uyumlu)) is None
    aykiri = tmp_path / "aykiri.udf"
    with zipfile.ZipFile(aykiri, "w") as z:
        z.writestr("content.xml",
                   '<template><properties><pageFormat leftMargin="70.87" '
                   'rightMargin="42.52" topMargin="42.52" bottomMargin="42.52"/>'
                   "</properties></template>")
    bulgu = pk._udf_kenar_kontrol(str(aykiri))
    assert bulgu is not None and "leftMargin" in bulgu


# ── B5 — BAYAT MÜHÜR ───────────────────────────────────────────────────────

def test_bayat_muhur_otomatik_tazelenir_was_derived_from(tmp_path):
    """.prov.json sha güncel ürünle uyuşmuyor → BAYAT işaretiyle listeye girer
    ve otomatik mühür was_derived_from=eski-sha ile tazeler."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    urun = cikti / "dilekce.udf"
    urun.write_bytes(b"PK\x03\x04yeni-icerik-sentetik")
    eski_sha = "0" * 64
    (cikti / "dilekce.udf.prov.json").write_text(
        json.dumps({"artifact_sha256": eski_sha, "prov_schema": "oa-muhur/1.0"}),
        encoding="utf-8")
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "BAYAT" in out
    kayit = json.loads((cikti / "dilekce.udf.prov.json").read_text(encoding="utf-8"))
    guncel_sha = hashlib.sha256(urun.read_bytes()).hexdigest()
    assert kayit["artifact_sha256"] == guncel_sha, "mühür tazelenmedi"
    assert kayit["was_derived_from"] == eski_sha, "eski sha zinciri kopmamalı"


def test_sign_sgn_li_urun_bayat_sayilmaz(tmp_path, pk):
    """sign.sgn'li (e-imzalı) ürün BAYAT sayılmaz — mühür tazelenmez, yalnız
    bilgi satırı basılır (teslim_paketi/muhur_yaz kuralına bırakılır)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    urun = cikti / "imzali.udf"
    with zipfile.ZipFile(urun, "w") as z:
        z.writestr("content.xml", "<template/>")
        z.writestr("sign.sgn", "sentetik-imza")
    eski_sha = "1" * 64
    (cikti / "imzali.udf.prov.json").write_text(
        json.dumps({"artifact_sha256": eski_sha}), encoding="utf-8")
    kayitlar = pk._muhursuz_teslim_listesi(str(tmp_path))
    assert any(k["durum"] == "imzali-bilgi" and k["yol"] == "cikti/imzali.udf"
               for k in kayitlar), kayitlar
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "sign.sgn" in out, "e-imzalı türev için bilgi satırı basılmalı"
    kayit = json.loads((cikti / "imzali.udf.prov.json").read_text(encoding="utf-8"))
    assert kayit["artifact_sha256"] == eski_sha, (
        "sign.sgn'li ürünün mührü OTOMATİK tazelenmemeli")


def test_muhursuz_liste_yeni_sema_muhursuz_kaydi(tmp_path, pk):
    """Şema: liste artık {yol, durum, eski_sha} kayıtları taşır; mühürsüz ürün
    durum='muhursuz' ile girer (uyarı + otomatik mühür AYNI listeden okur)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "taslak.udf").write_bytes(b"PK\x03\x04x")
    kayitlar = pk._muhursuz_teslim_listesi(str(tmp_path))
    assert kayitlar == [{"yol": "cikti/taslak.udf", "durum": "muhursuz",
                         "eski_sha": None}]


def test_sign_sgn_istisna_defterine_dogrulama_toleransi_yazilir(tmp_path):
    """İstisna defteri (ortak şema): sign.sgn toleransı append-only
    istisna-kayitlari.jsonl'e tur=dogrulama-toleransi olarak işlenir."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    urun = cikti / "imzali.udf"
    with zipfile.ZipFile(urun, "w") as z:
        z.writestr("content.xml", "<template/>")
        z.writestr("sign.sgn", "sentetik-imza")
    (cikti / "imzali.udf.prov.json").write_text(
        json.dumps({"artifact_sha256": "2" * 64}), encoding="utf-8")
    _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    defter = tmp_path / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    assert defter.is_file(), "istisna defteri doğmadı"
    kayitlar = [json.loads(s) for s in defter.read_text(encoding="utf-8").splitlines()
                if s.strip()]
    tolerans = [k for k in kayitlar if k.get("tur") == "dogrulama-toleransi"]
    assert tolerans, "dogrulama-toleransi kaydı yok"
    k = tolerans[0]
    assert k.get("ilgili") == "cikti/imzali.udf"
    assert k.get("onay") == "otomatik-kural"
    assert k.get("zaman") and k.get("imza") and k.get("gerekce")
    # İkinci koşu defteri ŞİŞİRMEZ (aynı tur+ilgili tekrar yazılmaz).
    _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    kayitlar2 = [json.loads(s) for s in defter.read_text(encoding="utf-8").splitlines()
                 if s.strip()]
    assert len(kayitlar2) == len(kayitlar)


# ── A4.8b — RED GİZLENEMEZ ─────────────────────────────────────────────────

def test_teslim_makbuz_red_satiri_basilir(tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "_oa" / "defter" / "teslim-makbuz-RED.json").write_text(
        json.dumps({"exit_kodu": 1, "sebep": "sentetik RED"}), encoding="utf-8")
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "TESLİM MAKBUZU: RED (sebep-kapısı)" in out


def test_red_dosyasi_yoksa_red_satiri_basilmaz(tmp_path):
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, out, _e = _kos(["--hook-denetle", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    assert "TESLİM MAKBUZU: RED" not in out


# ── TÜM HOOK GÖVDELERİ exit 0 ──────────────────────────────────────────────

@pytest.mark.parametrize("mod", ["--hook-prompt", "--hook-pretool",
                                 "--hook-postwrite", "--hook-denetle",
                                 "--hook-acilis"])
def test_tum_hook_govdeleri_dava_klasorunde_exit_0(tmp_path, mod):
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, _out, _e = _kos([mod, "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, f"{mod} bloklamaz sözleşmesini bozdu"


@pytest.mark.parametrize("mod", ["--hook-prompt", "--hook-pretool",
                                 "--hook-postwrite", "--hook-denetle",
                                 "--hook-acilis"])
def test_tum_hook_govdeleri_bozuk_stdin_ile_exit_0(tmp_path, mod):
    _dava_klasoru_kur(tmp_path)
    kod, _out, _e = _kos([mod], tmp_path, "{{{bu json değil")
    assert kod == 0, f"{mod} bozuk stdin'de bile exit 0 olmalı"
