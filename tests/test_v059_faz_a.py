# -*- coding: utf-8 -*-
"""v0.5.9 FAZ A — dört ilkenin hook katmanı infazı (A1 + A2 + A4).

Çekirdek (v0.5.9): "çıktı tüm süreçten FİZİKSEL geçmeden avukata SUNULMAZ".
Dört ilke: DETERMİNİSTİK (halka artefakta bağlanır) · TAMAMLAYICI (script
denetler, muhakemeyi üretmez) · KESİNTİSİZ (zincirdeki yer her turda akar) ·
SÜRTÜNMESİZ (sessiz ret yasak; hata ne-yapmalıyı söyler).

  A1 — SUNUM KİLİDİ (hook_pretool): SendUserFile ile makbuzsuz teslim-sınıfı
       ürün gönderimi 'ask' kararına düşer (yeşil makbuz = TEK ÖLÇÜT:
       _oa/defter/teslim-makbuz.json exit_kodu==0 → sessiz). Elle-UDF deseni
       AYNI gövdede ve ÖNCELİKLİDİR (v0.5.8.4 davranışı aynen).
  A2 — İNLİNE ZİNCİR (hook_postwrite): dilekçe-taslak sınıfı yazımda
       dilekce_denetim.hizli_denetim İN-PROCESS (subprocess YASAK) + 2sn
       zaman sınırıyla koşar; bulgu özeti PostToolUse çıktısıyla modele geri
       akar; temizse TEK satır "inline denetim: temiz"; defter varsa
       {tip:hook, olay:inline-denetim} olayı düşer.
  A4 — ZİNCİR DURUMU (hook_prompt): defter VARKEN (pipeline-durum.json
       derlenmişken) enjeksiyona 2-3 satırlık mekanik zincir özeti eklenir;
       defter yokken tam devir bloğu AYNEN.

Tüm testler tmp_path + sentetik desenler kullanır (repo kuralı m.7 —
gerçek dava numarası/kişi adı/klasör yolu ASLA yazılmaz).
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import time
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
PK = PLUGIN / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
DD = PLUGIN / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


@pytest.fixture(scope="module")
def pk():
    spec = importlib.util.spec_from_file_location("_test_v059_faz_a_pk", PK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_v059_faz_a_pk"] = mod
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
    """Sentetik UYAP indirmesi: 3 adet NNN_ evrak → `_dosya_klasoru_mu` True."""
    for i in ("001", "002", "003"):
        (kok / f"{i}_Sentetik_Evrak.pdf").write_text("sentetik", encoding="utf-8")
    if defterli:
        (kok / "_oa" / "defter").mkdir(parents=True, exist_ok=True)


def _defter_ac(kok):
    """--baslat (pipeline-durum.json derlenir) + İNGEST-ÖNCE fikstürü."""
    kod, _out, err = _kos(["--baslat", "2024/123 Esas — sentetik dosya",
                           "--kok", str(kok)], kok)
    assert kod == 0, err
    metin = kok / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def _olaylar(kok):
    jsonl = kok / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    if not jsonl.is_file():
        return []
    return [json.loads(s) for s in jsonl.read_text(encoding="utf-8").splitlines()
            if s.strip()]


def _sendfile_payload(kok, dosyalar):
    return json.dumps({"tool_name": "SendUserFile", "cwd": str(kok),
                       "tool_input": {"files": [str(d) for d in dosyalar]}})


_ELLE_UDF_ICERIK = (
    "import zipfile\n"
    "with zipfile.ZipFile('taslak.udf', 'w') as z:\n"
    "    z.writestr('content.xml', '<template/>')\n")


# ════════════════════════════════════════════════════════════════════════════
# A1 — SUNUM KİLİDİ (hook_pretool → SendUserFile)
# ════════════════════════════════════════════════════════════════════════════

def test_a1_makbuzsuz_teslim_urunu_gonderimi_ask_basar(tmp_path):
    """Teslim-sınıfı ürün (.udf, _oa/cikti altında) + makbuz YOK → 'ask'
    kararı; gerekçe ne-yapmalıyı söyler (SÜRTÜNMESİZ: sessiz ret yasak)."""
    _dava_klasoru_kur(tmp_path)
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"
    urun.parent.mkdir(parents=True, exist_ok=True)
    urun.write_bytes(b"PK\x03\x04sentetik")
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, _sendfile_payload(tmp_path, [urun]))
    assert kod == 0, "PreToolUse hook'u ASLA bloklamaz (exit 0 şart)"
    veri = json.loads(out.strip())
    ozgu = veri["hookSpecificOutput"]
    assert ozgu["hookEventName"] == "PreToolUse"
    assert ozgu["permissionDecision"] == "ask"
    gerekce = ozgu["permissionDecisionReason"]
    assert "SUNUM KİLİDİ" in gerekce
    assert "teslim-makbuz.json" in gerekce, "tek ölçüt gerekçede adıyla geçmeli"
    assert "teslim_paketi" in gerekce, "ne-yapmalı (zinciri yeşile bağla) söylenmeli"
    assert "avukatın kararı" in gerekce, "ask bir devir, engel değil"


def test_a1_yesil_makbuzla_sessiz(tmp_path):
    """Yeşil makbuz (exit_kodu==0) VARSA kapı SESSİZ — çıktı yok, exit 0
    (DETERMİNİSTİK: halka makbuz ARTEFAKTINA bağlanır, beyana değil)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"
    urun.parent.mkdir(parents=True, exist_ok=True)
    urun.write_bytes(b"PK\x03\x04sentetik")
    (tmp_path / "_oa" / "defter" / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, _sendfile_payload(tmp_path, [urun]))
    assert kod == 0
    assert out.strip() == "", f"yeşil makbuzla sessiz olmalıydı: {out!r}"


def test_a1_kirmizi_makbuz_ask_basar(tmp_path):
    """Makbuz VAR ama exit_kodu != 0 (RED) → yeşil değildir, kilit çalışır."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"
    urun.parent.mkdir(parents=True, exist_ok=True)
    urun.write_bytes(b"PK\x03\x04sentetik")
    (tmp_path / "_oa" / "defter" / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 1}), encoding="utf-8")
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, _sendfile_payload(tmp_path, [urun]))
    assert kod == 0
    assert json.loads(out.strip())["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_a1_dava_disi_klasorde_sessiz(tmp_path):
    """Sıradan klasörden dosya göndermek meşru iştir — kilit yalnız dava
    klasöründe nöbet tutar."""
    (tmp_path / "notlar.md").write_text("sıradan depo", encoding="utf-8")
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"  # yol var ama dava klasörü değil
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, _sendfile_payload(tmp_path, [urun]))
    assert kod == 0 and out.strip() == ""


def test_a1_teslim_sinifi_olmayan_gonderim_sessiz(tmp_path):
    """Teslim-sınıfı olmayan dosya (rapor.png / not.md) gönderimi kilide
    takılmaz — gürültü disiplini."""
    _dava_klasoru_kur(tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    kod, out, _e = _kos(
        ["--hook-pretool", "--kok", str(tmp_path)], tmp_path,
        _sendfile_payload(tmp_path, [cikti / "rapor.png", cikti / "not.md"]))
    assert kod == 0 and out.strip() == ""


def test_a1_orijinal_uyap_evraki_gonderimi_sessiz(tmp_path):
    """UYAP indirme evrakı (NNN_ önekli orijinal .pdf) TESLİM ÜRÜNÜ değildir
    — orijinal evrak göndermek kilide takılmaz (yanlış-pozitif disiplini)."""
    _dava_klasoru_kur(tmp_path)
    kod, out, _e = _kos(
        ["--hook-pretool", "--kok", str(tmp_path)], tmp_path,
        _sendfile_payload(tmp_path, [tmp_path / "001_Sentetik_Evrak.pdf"]))
    assert kod == 0 and out.strip() == ""


def test_a1_elle_udf_deseni_onceligi_korunur(tmp_path):
    """Aynı payload'da HEM elle-UDF deseni HEM makbuzsuz SendUserFile varsa
    gerekçe ELLE-UDF olmalı (kural sırası: elle-UDF deseni ÖNCE)."""
    _dava_klasoru_kur(tmp_path)
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"
    urun.parent.mkdir(parents=True, exist_ok=True)
    urun.write_bytes(b"PK\x03\x04sentetik")
    payload = json.dumps({"tool_name": "SendUserFile", "cwd": str(tmp_path),
                          "tool_input": {"files": [str(urun)],
                                         "content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0
    gerekce = json.loads(out.strip())["hookSpecificOutput"]["permissionDecisionReason"]
    assert "ELLE-UDF" in gerekce, "öncelik elle-UDF deseninde olmalı"
    assert "SUNUM KİLİDİ" not in gerekce


def test_a1_mevcut_elle_udf_davranisi_regresyonsuz(tmp_path):
    """v0.5.8.4 sözleşmesi: SendUserFile OLMAYAN klasik elle-UDF içerik
    girişimi hâlâ aynı 'ask' gerekçesiyle yakalanır (iki kural aynı gövdede)."""
    _dava_klasoru_kur(tmp_path)
    payload = json.dumps({"cwd": str(tmp_path),
                          "tool_input": {"content": _ELLE_UDF_ICERIK}})
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0
    gerekce = json.loads(out.strip())["hookSpecificOutput"]["permissionDecisionReason"]
    assert "ELLE-UDF" in gerekce and "udf_yaz.py" in gerekce


def test_a1_ask_karari_deftere_hook_olayi_dusurur(tmp_path):
    """Defter varsa 'ask' kararı {tip:hook, olay:pretool-ask} olarak iz
    bırakır (372 dersi: hook nöbetinin izi defterde görünür olmalı)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"
    urun.parent.mkdir(parents=True, exist_ok=True)
    urun.write_bytes(b"PK\x03\x04sentetik")
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, _sendfile_payload(tmp_path, [urun]))
    assert kod == 0 and "PreToolUse" in out
    hook_olaylar = [o for o in _olaylar(tmp_path) if o.get("tip") == "hook"]
    assert hook_olaylar and hook_olaylar[-1]["olay"] == "pretool-ask"
    assert "SUNUM KİLİDİ" in hook_olaylar[-1].get("not", "")


def test_a1_nabiz_damgasi_her_cagrida(tmp_path):
    """Nabız pretool damgası HER çağrıda düşer (mevcut C3 davranışı korunur
    — sessiz-yeşil geçişte bile)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    (tmp_path / "_oa" / "defter" / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    urun = tmp_path / "_oa" / "cikti" / "dilekce.udf"
    urun.parent.mkdir(parents=True, exist_ok=True)
    urun.write_bytes(b"PK\x03\x04sentetik")
    kod, out, _e = _kos(["--hook-pretool", "--kok", str(tmp_path)],
                        tmp_path, _sendfile_payload(tmp_path, [urun]))
    assert kod == 0 and out.strip() == ""
    iz = json.loads((tmp_path / "_oa" / "defter" / ".hook-son-iz.json")
                    .read_text(encoding="utf-8"))
    assert iz.get("pretool"), "sessiz geçişte bile nabız damgası düşmeli"


def test_a1_teslim_sinifi_taniyici_birim(tmp_path, pk):
    """`_sunum_teslim_sinifi_mi` sınır çizgileri: _oa altı her teslim
    uzantısı ürün; kökte yalnız ürün-adlı dosya; orijinal evrak asla."""
    kok = str(tmp_path)
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "_oa" / "cikti" / "dilekce.udf")) is True
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "_oa" / "teslim" / "sentetik.pdf")) is True
    assert pk._sunum_teslim_sinifi_mi(kok, "_oa/cikti/taslak.docx") is True  # göreli yol
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "istinaf-dilekcesi.pdf")) is True
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "001_Sentetik_Evrak.pdf")) is False
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "2024_Sentetik_Karar.pdf")) is False
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "notlar.docx")) is False
    assert pk._sunum_teslim_sinifi_mi(kok, str(tmp_path / "_oa" / "cikti" / "rapor.md")) is False


# ════════════════════════════════════════════════════════════════════════════
# A2 — İNLİNE ZİNCİR (hook_postwrite → dilekce_denetim.hizli_denetim)
# ════════════════════════════════════════════════════════════════════════════

def _taslak_kur(kok, ad="01-dilekce-taslak.md",
                icerik="sentetik taslak metni — inline denetim provası"):
    """_oa/cikti altında dilekçe-taslak sınıfı dosya. İçerik BİLEREK
    _DILEKCE_DESEN'e uymaz — ağır postwrite gövdesi tetiklenmesin (inline
    katman tek başına ölçülür)."""
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    taslak = cikti / ad
    taslak.write_text(icerik, encoding="utf-8")
    return taslak


def _payload(taslak):
    return {"tool_input": {"file_path": str(taslak)}}


def test_a2_taslak_yaziminda_bulgu_ozeti_ve_defter_olayi(tmp_path, pk,
                                                         monkeypatch, capsys):
    """Bulgular stdout'a özet olarak basılır (PostToolUse çıktısı modele geri
    akar — 777 kanıtı) VE defter {tip:hook, olay:inline-denetim, not:'N
    bulgu'} olayını alır."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)
    sahte = types.SimpleNamespace(hizli_denetim=lambda metin, kok: [
        "[M] madde numarası künyeyle uyuşmuyor (sentetik)",
        "[K] cephanelik ifşası sinyali (sentetik)"])
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD", sahte)
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(taslak))
    out = capsys.readouterr().out
    assert "İNLİNE DENETİM" in out and "2 bulgu" in out
    assert "[M]" in out and "[K]" in out
    olaylar = [o for o in _olaylar(tmp_path)
               if o.get("tip") == "hook" and o.get("olay") == "inline-denetim"]
    assert olaylar and olaylar[-1]["not"] == "2 bulgu"


def test_a2_temiz_taslakta_tek_satir_temiz(tmp_path, pk, monkeypatch, capsys):
    """Bulgu yoksa TEK satır 'inline denetim: temiz' — sessiz-yeşil ölçümü
    (temiz ile hiç-koşmadı ayrımı görünür kalır)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)
    sahte = types.SimpleNamespace(hizli_denetim=lambda metin, kok: [])
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD", sahte)
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(taslak))
    out = capsys.readouterr().out
    assert out.strip() == "inline denetim: temiz"
    olaylar = [o for o in _olaylar(tmp_path)
               if o.get("tip") == "hook" and o.get("olay") == "inline-denetim"]
    assert olaylar and olaylar[-1]["not"] == "0 bulgu"


def test_a2_hizli_denetim_yoksa_sessiz_atlanir(tmp_path, pk, monkeypatch, capsys):
    """Eski sürüm uyumu: dilekce_denetim modülünde `hizli_denetim` YOKSA
    inline katman SESSİZCE atlanır (getattr sözleşmesi — hook çökmez)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD", types.SimpleNamespace())
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(taslak))
    assert capsys.readouterr().out == ""


def test_a2_zaman_asiminda_vazgecer_bloklamaz(tmp_path, pk, monkeypatch, capsys):
    """Timeout koruması: hızlı kip çağrısı sınırı aşarsa VAZGEÇİLİR — çıktı
    yok, hook bloklanmaz (yavaş fonksiyon mock'u sınırın üstünde uyur)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)

    def _yavas(metin, kok):
        time.sleep(0.8)
        return ["[M] bu bulgu asla basılmamalı"]

    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD",
                        types.SimpleNamespace(hizli_denetim=_yavas))
    baslangic = time.monotonic()
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(taslak),
                                    zaman_siniri_sn=0.1)
    gecen = time.monotonic() - baslangic
    assert capsys.readouterr().out == "", "zaman aşımında çıktı basılmamalı"
    assert gecen < 0.7, "vazgeçiş sınırda olmalı — fonksiyon beklenmemeli"


def test_a2_cokme_sessiz_yutulur(tmp_path, pk, monkeypatch, capsys):
    """hizli_denetim istisna fırlatırsa hook SESSİZ vazgeçer (asla çökmez)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)

    def _patlak(metin, kok):
        raise RuntimeError("sentetik çökme")

    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD",
                        types.SimpleNamespace(hizli_denetim=_patlak))
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(taslak))
    assert capsys.readouterr().out == ""


def test_a2_taslak_sinifi_disi_dosyada_koşmaz(tmp_path, pk, monkeypatch, capsys):
    """Ad deseni tutmayan (_oa/cikti/rapor.md) yazımda inline denetim HİÇ
    koşmaz — her Write'a denetim gürültüsü bağlanmaz."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    dosya = _taslak_kur(tmp_path, ad="rapor.md")
    sahte = types.SimpleNamespace(
        hizli_denetim=lambda metin, kok: ["[M] basılmamalı"])
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD", sahte)
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(dosya))
    assert capsys.readouterr().out == ""


def test_a2_alti_bulgu_ustu_kirpilir(tmp_path, pk, monkeypatch, capsys):
    """Özet en çok 6 satırdır (başlık + 5 bulgu): 9 bulguda toplam sayı
    başlıkta görünür, satırlar kırpılır (bağlam maliyeti disiplini)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)
    bulgular = [f"[N] sentetik bulgu {i}" for i in range(9)]
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD",
                        types.SimpleNamespace(hizli_denetim=lambda m, k: bulgular))
    pk._hook_inline_dilekce_denetim(str(tmp_path), _payload(taslak))
    satirlar = capsys.readouterr().out.splitlines()
    assert len(satirlar) <= 6, f"özet 6 satırı aşmamalı: {satirlar}"
    assert "9 bulgu" in satirlar[0]


def test_a2_taslak_sinifi_taniyici_birim(tmp_path, pk):
    kok = str(tmp_path)
    cikti = tmp_path / "_oa" / "cikti"
    assert pk._dilekce_taslak_sinifi_mi(kok, str(cikti / "01-dilekce-v2.md")) is True
    assert pk._dilekce_taslak_sinifi_mi(kok, str(cikti / "taslak-istinaf.md")) is True
    assert pk._dilekce_taslak_sinifi_mi(kok, str(cikti / "rapor.md")) is False
    assert pk._dilekce_taslak_sinifi_mi(kok, str(cikti / "dilekce.udf")) is False
    assert pk._dilekce_taslak_sinifi_mi(kok, str(tmp_path / "dilekce.md")) is False  # _oa/cikti dışı


def test_a2_hook_postwrite_govdesi_inline_katmani_cagirir(tmp_path, pk,
                                                          monkeypatch, capsys):
    """Kablolama kanıtı: hook_postwrite payload'ı BİR KEZ okur ve inline
    katmanı koşturur (exit 0 sözleşmesi bozulmadan)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)
    monkeypatch.setattr(pk, "_hook_stdin_payload_oku", lambda: _payload(taslak))
    monkeypatch.setattr(pk, "_DILEKCE_DENETIM_MOD",
                        types.SimpleNamespace(hizli_denetim=lambda m, k: []))
    sonuc = pk.hook_postwrite(str(tmp_path))
    assert sonuc == 0, "PostToolUse hook'u ASLA bloklamaz"
    assert "inline denetim: temiz" in capsys.readouterr().out


def test_a2_gercek_hatla_uctan_uca_subprocess(tmp_path):
    """Uçtan uca (subprocess): gerçek dilekce_denetim.hizli_denetim ile
    taslak yazımı sonrası hook ya bulgu özeti ya 'temiz' satırı basar.
    (Kardeş ajan hizli_denetim'i henüz eklemediyse atlanır — eski sürüm
    uyumu zaten test_a2_hizli_denetim_yoksa_sessiz_atlanir ile kilitli.)"""
    if "def hizli_denetim" not in DD.read_text(encoding="utf-8"):
        pytest.skip("dilekce_denetim.hizli_denetim henüz yok (kardeş ajan)")
    _dava_klasoru_kur(tmp_path, defterli=True)
    taslak = _taslak_kur(tmp_path)
    payload = json.dumps(_payload(taslak))
    kod, out, _e = _kos(["--hook-postwrite", "--kok", str(tmp_path)],
                        tmp_path, payload)
    assert kod == 0, "PostToolUse hook'u ASLA bloklamaz"
    assert ("inline denetim: temiz" in out) or ("İNLİNE DENETİM" in out), (
        f"inline katman hiç konuşmadı: {out!r}")


def test_a2_subprocess_yasagi_kaynakta_yok(pk):
    """test_gate_g_dongu kilidiyle simetrik: inline zincir subprocess
    AÇMAZ — kaynakta 'import subprocess' yoktur, importlib kullanılır."""
    kaynak = PK.read_text(encoding="utf-8")
    assert "import subprocess" not in kaynak
    assert "_oa_pipeline_dilekce_denetim_inproc" in kaynak


# ════════════════════════════════════════════════════════════════════════════
# A4 — ZİNCİR DURUMU (hook_prompt → kesintisiz akış özeti)
# ════════════════════════════════════════════════════════════════════════════

def test_a4_defterli_kokte_zincir_durumu_enjekte_edilir(tmp_path):
    """Defter + derlenmiş durum → enjeksiyonda ZİNCİR DURUMU: son UYGULANDI
    halka + sıradaki adım + makbuz durumu (model zincirdeki yerini bilir)."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, _o, err = _kos(["--isle", "--adim", "3", "--parca", "oa-ictihat",
                         "--durum", "UYGULANDI",
                         "--kanit", "ictihat_ara 'sentetik sorgu' → 3 künye teyitli, kütüğe işlendi",
                         "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    metin = json.loads(out.strip())["hookSpecificOutput"]["additionalContext"]
    assert "ZİNCİR DURUMU" in metin
    assert "son UYGULANDI" in metin and "adım 3" in metin and "oa-ictihat" in metin
    assert "sıradaki" in metin
    assert "teslim makbuzu: YOK" in metin
    assert "DEVİR YÜKÜMLÜLÜĞÜ" not in metin, "hat açık — devir bloğu basılmaz"


def test_a4_bekleyen_avukat_karari_sayilir(tmp_path):
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    kod, _o, err = _kos(["--isle", "--adim", "1", "--parca", "oa-sure",
                         "--durum", "BILGI-EKSIK",
                         "--eksik", "tebliğ tarihi belgede yok (sentetik)",
                         "--kok", str(tmp_path)], tmp_path)
    assert kod == 0, err
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    metin = json.loads(out.strip())["hookSpecificOutput"]["additionalContext"]
    assert "bekleyen avukat kararı: 1" in metin


def test_a4_yesil_makbuz_ve_muhursuz_sayisi_gorunur(tmp_path):
    """Makbuz yeşilse 'YEŞİL' yazar; mühürsüz teslim-sınıfı ürün sayısı da
    aynı satırda akar (makbuzsuz/mühürsüz kısa durumu)."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    (tmp_path / "_oa" / "defter" / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 0}), encoding="utf-8")
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "dilekce.udf").write_bytes(b"PK\x03\x04sentetik")
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    metin = json.loads(out.strip())["hookSpecificOutput"]["additionalContext"]
    assert "teslim makbuzu: YEŞİL" in metin
    assert "mühürsüz teslim ürünü: 1" in metin


def test_a4_defter_yokken_devir_blogu_aynen(tmp_path):
    """Defter YOK → mevcut tam devir bloğu AYNEN; ZİNCİR DURUMU basılmaz."""
    _dava_klasoru_kur(tmp_path)
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0
    metin = json.loads(out.strip())["hookSpecificOutput"]["additionalContext"]
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in metin
    assert "ZİNCİR DURUMU" not in metin


def test_a4_bos_defter_dizini_sessiz_kalir(tmp_path):
    """Durum dosyası derlenmemiş boş kabuk defter dizini → mevcut sessizlik
    sözleşmesi AYNEN (test_hat_ACIKSA_sessiz_kalir'ın v0.5.9 kilidi)."""
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0 and out.strip() == ""


def test_a4_rutin_zincir_enjeksiyonu_defteri_sisirmez(tmp_path):
    """ZİNCİR DURUMU her turda akar ama TEK BAŞINA deftere olay YAZMAZ —
    append-only defter turda-bir satırla şişmez (gürültü disiplini);
    {olay:prompt} yalnız gerçek uyarı enjeksiyonlarında düşer."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    once = len(_olaylar(tmp_path))
    kod, out, _e = _kos(["--hook-prompt", "--kok", str(tmp_path)], tmp_path)
    assert kod == 0 and "ZİNCİR DURUMU" in out
    sonra = _olaylar(tmp_path)
    assert len(sonra) == once, "rutin zincir özeti defteri şişirmemeli"
    assert not any(o.get("tip") == "hook" and o.get("olay") == "prompt"
                   for o in sonra)


def test_a4_ozet_uc_satiri_asmaz(tmp_path, pk):
    """Özet 2-3 satırdır (kısa ve gürültüsüz) — birim seviyesinde kilit."""
    _dava_klasoru_kur(tmp_path)
    _defter_ac(tmp_path)
    ozet = pk._zincir_durumu_ozeti(str(tmp_path))
    assert ozet is not None
    assert len(ozet.splitlines()) <= 3


def test_a4_durum_dosyasi_yoksa_none(tmp_path, pk):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    assert pk._zincir_durumu_ozeti(str(tmp_path)) is None


def test_a4_bozuk_durum_dosyasinda_none(tmp_path, pk):
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "pipeline-durum.json").write_text("{{{bozuk", encoding="utf-8")
    assert pk._zincir_durumu_ozeti(str(tmp_path)) is None


# ── FAZ A ORTAK SÖZLEŞME: hiçbir hook gövdesi bloklamaz ─────────────────────

@pytest.mark.parametrize("mod", ["--hook-prompt", "--hook-pretool",
                                 "--hook-postwrite"])
def test_faz_a_hook_govdeleri_bozuk_payloadda_exit_0(tmp_path, mod):
    _dava_klasoru_kur(tmp_path, defterli=True)
    kod, _out, _e = _kos([mod, "--kok", str(tmp_path)], tmp_path,
                         "{{{json değil")
    assert kod == 0, f"{mod} bozuk payload'da bile exit 0 olmalı"
