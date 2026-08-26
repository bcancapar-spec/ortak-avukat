# -*- coding: utf-8 -*-
"""v0.5.11 — KİT GÜVENLİK KATMANI (1865 karnesi T1-T7).

Saha kanıtı (Danıştay 1865, çok-oturumlu koşu, elle doğrulanmış):
  T1 — rpm bulaşması: onarılan kit, masaüstü uygulamasının rpm anlık-görüntü
       yolundan (local-agent-mode-sessions) 9 dk sonra ESKİ nesille geri
       ezildi (777'den beri 3. nüks).
  T3 — söz-müdahalesi ezildi; dosya-düzeyi koruma (salt-okunur) tuttu.
  T5 — bayat karşılaştırıcı yön bilmiyor: kit kanaldan YENİYKEN de
       "bayat" bağırdı (12 uyarının ~4'ü yanlış yönlü gürültü).
  T4a — makbuz/defter hangi oturumun ürünü bilinmiyor (5 paralel oturum).
  T6 — 'metin-sororn' typo dizini sessizce doğdu.
  T7 — künye kurulmadan araştırma derinleşti.

v0.5.11 sözleşmesi (bu testlerin kilitlediği):
  P0-1 RPM KARANTİNASI: rpm yolundan _oa/araclar'a kopya girişimi 'ask'.
  P0-2 KİLİTLİ ÇEKİRDEK: tam-nesil çekirdek scriptler salt-okunur; çekirdeğe
       Write/Edit girişimi 'ask'. Bayat kit KİLİTLENMEZ (çöp mühürlenmez).
  P1-3 YÖNLÜ TAZELİK: bayat / kanaldan-yeni / özdeş üç ayrı hüküm.
  P1-4a OTURUM DAMGASI: hook olayları payload session_id taşır; son-iz
       köprüsü Bash-koşulan scriptlere 'oturum_izi' verir; taze komşu
       oturum izi görünür uyarı üretir.
  P2-5/6: sözleşme-dışı dizin + MANİFEST-önce uyarıları prompt kanalında.

Tamamen ağsız/deterministik; tüm veriler sentetiktir (tmp_path).
"""
import importlib.util
import json
import os
import pathlib
import stat
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"


def _yukle(gorece, modul_adi):
    yol = SK / gorece
    spec = importlib.util.spec_from_file_location(modul_adi, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pk():
    return _yukle("oa-pipeline/scripts/pipeline_kayit.py", "v0511_pk")


@pytest.fixture(scope="module")
def teslim():
    return _yukle("oa-kontrol/scripts/teslim_paketi.py", "v0511_teslim")


def _defterli_kok(tmp_path):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    return tmp_path


# ────────────── P0-1 · RPM KARANTİNASI (T1) ──────────────

RPM = r"C:\Users\pc\AppData\Roaming\Claude\local-agent-mode-sessions\abc\plugin_X\skills"


def test_rpm_karantina_deseni(pk):
    """rpm yolu + _oa/araclar hedefi BİRLİKTE → karantina; tek başına değil."""
    kopya = 'cp "%s/udf_yaz.py" "_oa/araclar/"' % RPM.replace("\\", "/")
    assert pk._pretool_rpm_karantina_mi(kopya) is True
    assert pk._pretool_rpm_karantina_mi(
        'ls "%s"' % RPM) is False                    # hedef araclar değil
    assert pk._pretool_rpm_karantina_mi(
        'cp "C:/x/skills/oa-dilekce/scripts/udf_yaz.py" "_oa/araclar/"'
    ) is False                                       # meşru kaynak
    assert pk._pretool_rpm_karantina_mi("") is False


def test_rpm_karantina_hook_ask(pk, tmp_path, monkeypatch, capsys):
    """Hook düzeyi: rpm→araclar kopyası payload'ı 'ask' kararı üretir."""
    kok = _defterli_kok(tmp_path)
    veri = {"tool_name": "Bash", "session_id": "S-test",
            "cwd": str(kok),
            "tool_input": {"command":
                'cp "%s/teslim_paketi.py" "%s/_oa/araclar/"'
                % (RPM.replace("\\", "/"), str(kok).replace("\\", "/"))}}
    monkeypatch.setattr(pk, "_hook_stdin_payload_oku", lambda: veri)
    rc = pk.hook_pretool()
    cikti = capsys.readouterr().out
    assert rc == 0
    assert '"ask"' in cikti and "rpm" in cikti.lower()


# ────────────── P0-2 · KİLİTLİ ÇEKİRDEK (T3) ──────────────

def _cekirdek_kur(kok, tam=True):
    a = kok / "_oa" / "araclar"
    a.mkdir(parents=True, exist_ok=True)
    icerik = {
        "pipeline_kayit.py": "# cekirdek\n",
        "teslim_paketi.py": "# teslim-makbuz.json uretir\n" if tam else "# bos\n",
        "udf_yaz.py": ("# _sayfa_kenari_yonetmelik + hvl-default + "
                       "udf-uretim-makbuz\n") if tam else "# bos\n",
        "oa_hafiza.py": "# --damga\n" if tam else "# bos\n",
    }
    for ad, met in icerik.items():
        (a / ad).write_text(met, encoding="utf-8")
    return a


def test_cekirdek_kilitle_tam_nesilde(pk, tmp_path):
    kok = _defterli_kok(tmp_path)
    a = _cekirdek_kur(kok, tam=True)
    kilitlenen = pk._cekirdek_kilitle(str(kok))
    assert kilitlenen >= 2   # en az teslim_paketi + udf_yaz
    for ad in ("teslim_paketi.py", "udf_yaz.py"):
        assert not (os.stat(a / ad).st_mode & stat.S_IWRITE), ad


def test_cekirdek_bayat_kit_kilitlenmez(pk, tmp_path):
    """Çöp mühürlenmez: parmak izi eksik kit salt-okunur YAPILMAZ."""
    kok = _defterli_kok(tmp_path)
    a = _cekirdek_kur(kok, tam=False)
    pk._cekirdek_kilitle(str(kok))
    assert os.stat(a / "udf_yaz.py").st_mode & stat.S_IWRITE


def test_pretool_cekirdege_write_ask(pk, tmp_path, monkeypatch, capsys):
    kok = _defterli_kok(tmp_path)
    _cekirdek_kur(kok, tam=True)
    hedef = kok / "_oa" / "araclar" / "udf_yaz.py"
    veri = {"tool_name": "Write", "session_id": "S-test", "cwd": str(kok),
            "tool_input": {"file_path": str(hedef), "content": "# taklit"}}
    monkeypatch.setattr(pk, "_hook_stdin_payload_oku", lambda: veri)
    rc = pk.hook_pretool()
    cikti = capsys.readouterr().out
    assert rc == 0
    assert '"ask"' in cikti and "çekirdek" in cikti.lower()


# ────────────── P1-3 · YÖNLÜ TAZELİK (T5) ──────────────

def _kanal_udf_yaz_icerigi():
    """Gerçek yüklü-kanal (repo) udf_yaz.py içeriği — 'özdeş' senaryosu için."""
    return (SK / "oa-dilekce" / "scripts" / "udf_yaz.py").read_text(
        encoding="utf-8")


def test_yonlu_tazelik_kanaldan_yeni(pk, tmp_path):
    """Parmak izi TAM + bayt farklı → 'kanaldan farklı/yeni' mesajı;
    BAYAT NESİL metni KULLANILMAZ (yanlış-yön gürültüsü ölür)."""
    kok = _defterli_kok(tmp_path)
    a = kok / "_oa" / "araclar"
    a.mkdir(parents=True)
    # tam parmak izli ama kanal baytlarından farklı kopya
    (a / "udf_yaz.py").write_text(
        _kanal_udf_yaz_icerigi() + "\n# yerel-fark\n", encoding="utf-8")
    metin = pk._bayat_arac_uyarisi(str(kok)) or ""
    assert "BAYAT NESİL" not in metin
    assert ("YENİ" in metin.upper() or "FARKLI" in metin.upper())
    assert "kurulum" in metin.lower() or "güncelle" in metin.lower()


def test_yonlu_tazelik_gercek_bayat(pk, tmp_path):
    """Parmak izi EKSİK → BAYAT NESİL metni aynen sürer."""
    kok = _defterli_kok(tmp_path)
    a = kok / "_oa" / "araclar"
    a.mkdir(parents=True)
    (a / "udf_yaz.py").write_text("# eski nesil, imzasiz\n", encoding="utf-8")
    metin = pk._bayat_arac_uyarisi(str(kok)) or ""
    assert "BAYAT NESİL" in metin


def test_yonlu_tazelik_ozdes_sessiz(pk, tmp_path):
    kok = _defterli_kok(tmp_path)
    a = kok / "_oa" / "araclar"
    a.mkdir(parents=True)
    (a / "udf_yaz.py").write_text(_kanal_udf_yaz_icerigi(), encoding="utf-8")
    assert pk._bayat_arac_uyarisi(str(kok)) is None


# ────────────── P1-4a · OTURUM DAMGASI (T4a) ──────────────

def test_hook_olayinda_oturum_alani(pk, tmp_path):
    kok = _defterli_kok(tmp_path)
    pk._hook_olay_yaz(str(kok), "test-olay", "not", oturum="S-123")
    satir = (kok / "_oa" / "defter" / "pipeline-olaylar.jsonl").read_text(
        encoding="utf-8").strip().splitlines()[-1]
    d = json.loads(satir)
    assert d["oturum"] == "S-123"


def test_son_oturum_koprusu(pk, tmp_path):
    """Nabız damgası son_oturum'u yazar; Bash-koşulan scriptler oradan okur."""
    kok = _defterli_kok(tmp_path)
    pk._hook_nabiz_damgala(str(kok), "pretool", oturum="S-abc")
    assert pk._son_oturum_oku(str(kok)) == "S-abc"
    assert pk._son_oturum_oku(str(tmp_path / "yok")) is None


def test_makbuz_oturum_izi(pk, teslim, tmp_path):
    """Makbuz, son-iz köprüsünden 'oturum_izi' alır (kesinlik iddiasız)."""
    kok = _defterli_kok(tmp_path)
    taslak = kok / "t.md"
    taslak.write_text("x", encoding="utf-8")
    pk._hook_nabiz_damgala(str(kok), "pretool", oturum="S-mkbz")

    class A:
        tip = "genel"; taraf = None; udf_yok = True
    veri = teslim._makbuz_taban(A(), str(taslak), str(kok), [], 0, None, None)
    assert veri.get("oturum_izi") == "S-mkbz"


def test_taze_oturum_uyarisi(pk, tmp_path):
    td = tmp_path / "proj"
    td.mkdir()
    benim = td / "ben.jsonl"
    benim.write_text("{}", encoding="utf-8")
    for ad in ("komsu1.jsonl", "komsu2.jsonl"):
        (td / ad).write_text("{}", encoding="utf-8")
    eski = td / "eski.jsonl"
    eski.write_text("{}", encoding="utf-8")
    simdi = time.time()
    os.utime(eski, (simdi - 7200, simdi - 7200))     # 2 saat — taze DEĞİL
    metin = pk._taze_oturum_uyarisi(str(benim)) or ""
    assert "2" in metin and "oturum" in metin.lower()
    # tek başına → sessiz
    tek = tmp_path / "tek"
    tek.mkdir()
    yalniz = tek / "ben.jsonl"
    yalniz.write_text("{}", encoding="utf-8")
    assert pk._taze_oturum_uyarisi(str(yalniz)) is None


# ────────────── P2-5 / P2-6 · BEKÇİLER (T6, T7) ──────────────

def test_sozlesme_disi_dizin_prompt_uyarisi(pk, tmp_path):
    kok = _defterli_kok(tmp_path)
    (kok / "_oa" / "metin-sororn").mkdir()
    metin = pk._sozlesme_disi_uyarisi(str(kok)) or ""
    assert "metin-sororn" in metin
    # temiz kökte sessiz
    kok2 = _defterli_kok(tmp_path / "b")
    assert pk._sozlesme_disi_uyarisi(str(kok2)) is None


def test_manifest_once_uyarisi(pk, tmp_path):
    kok = _defterli_kok(tmp_path)
    teyit = kok / "_oa" / "teyit"
    teyit.mkdir(parents=True)
    (teyit / "kunye-teyit.md").write_text(
        "| satir | DAMGA=LEHE |\n", encoding="utf-8")
    metin = pk._manifest_once_uyarisi(str(kok)) or ""
    assert "MANİFEST" in metin or "sayım" in metin.lower()
    # künye varsa sessiz
    metin_d = kok / "_oa" / "metin"
    metin_d.mkdir()
    (metin_d / "00-kunye.json").write_text("{}", encoding="utf-8")
    assert pk._manifest_once_uyarisi(str(kok)) is None
