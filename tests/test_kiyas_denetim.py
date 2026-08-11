# -*- coding: utf-8 -*-
"""Fable-tespitli TESTSİZ release-kapısı scriptlerinden biri olan
oa-kiyas / kiyas_denetim.py için KARAKTERİZASYON testleri.

Bu dosya scriptin MEVCUT davranışını olduğu gibi KİLİTLER, değiştirmez:
hukuki silojizmin (büyük önerme → küçük önerme → sonuç) yapısal denetimini
yapan bu mekanizmayı hiçbir test doğrulamıyordu. Testler davranışı koddan
çıkarıldığı hâliyle sabitler; "tuhaf" görünen davranışlar da (aşağıda) mevcut
tasarım olarak belgelenir.

EN KRİTİK karakterizasyon: script KRİTİK BOŞLUK tespit ettiğinde bile
exit 0 döner — main() içinde sys.exit yoktur; rapor "kapı değil
karar-malzemesi" olarak tasarlanmıştır. Bu bilinçli mevcut tasarımdır —
kapıya çevirme kararı Can'a sorulacak (bkz. _gorus/semantica-uyarlama.md).

Diğer kilitlenen mevcut davranışlar:
- Argümansız çağrı: kullanım mesajı (stdout) + exit 1.
- Var olmayan girdi dosyası / bozuk JSON: script ÇÖKER (yakalanmamış
  FileNotFoundError / JSONDecodeError traceback'i, returncode != 0) —
  karakterizasyon: mevcut tasarımda girdi hatası yakalanmaz.
- Sonuç yazılmamış olması ve içtihat yokluğu yalnız ⚠ uyarıdır, kritik
  boşluk SAYILMAZ ("Yapı bütün" basılır).
- Unsurlar hem {"id","ad"} sözlük hem düz-string biçiminde kabul edilir.

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; repo dosyalarına
dokunulmaz.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kiyas"
          / "scripts" / "kiyas_denetim.py")


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


@pytest.fixture
def izole_dizin():
    return pathlib.Path(tempfile.mkdtemp())


def _kiyas_yaz(dizin, veri):
    yol = dizin / "kiyas.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _tam_kiyas():
    """Mutlu yol örneği: üç bileşen dolu, içtihat teyitli, her unsur
    delilli vakıayla karşılanmış, yetim vakıa yok."""
    return {
        "buyuk_onerme": {
            "norm": "TBK m.49 — haksız fiil sorumluluğu",
            "ictihat": [
                {"kunye": "Yargıtay 4. HD 2020/1234 E. 2021/5678 K.",
                 "dogrulama": "teyitli"},
            ],
            "unsurlar": [
                {"id": "fiil", "ad": "Hukuka aykırı fiil"},
                {"id": "zarar", "ad": "Zarar"},
            ],
        },
        "kucuk_onerme": {
            "vakialar": [
                {"metin": "Davalı aracıyla yaya geçidinde çarptı",
                 "karsilar": ["fiil"],
                 "dayanak_delil": ["kaza tespit tutanağı"]},
                {"metin": "Davacı 3 ay iş göremedi",
                 "karsilar": ["zarar"],
                 "dayanak_delil": ["sağlık raporu"]},
            ],
        },
        "sonuc": "TBK m.49 uyarınca tazminat sorumluluğu doğar.",
    }


def test_script_mevcut():
    assert SCRIPT.is_file(), f"kiyas_denetim.py bulunamadı: {SCRIPT}"


# ── mutlu yol: tam kıyas → yapı bütün, exit 0 ───────────────────────────────

def test_mutlu_yol_tam_kiyas_yapi_butun_exit0(izole_dizin):
    yol = _kiyas_yaz(izole_dizin, _tam_kiyas())
    kod, out, err = _cli(yol)

    assert kod == 0, f"tam kıyasta exit 0 beklenir; stderr:\n{err}"
    assert "OA-KIYAS — DETERMİNİSTİK SİLOJİZM DENETİM RAPORU" in out
    assert "✓ Norm: TBK m.49" in out
    assert "✓ Küçük önerme: 2 vakıa" in out
    assert "✓ Sonuç var" in out
    assert "[teyitli]" in out
    assert "✓ [Hukuka aykırı fiil] ← vakıa var, delil var" in out
    assert "✓ [Zarar] ← vakıa var, delil var" in out
    assert "✓ Her vakıa bir unsura bağlı." in out
    assert "SONUÇ: Yapı bütün." in out
    assert "AVUKAT muhakemesidir" in out
    assert "KRİTİK BOŞLUK" not in out


# ── EN KRİTİK karakterizasyon: kritik boşlukta bile exit 0 ──────────────────

def test_kritik_boslukta_bile_exit0_doner_kapi_degil_karar_malzemesi(izole_dizin):
    """KARAKTERİZASYON — mevcut tasarım: main() içinde sys.exit yok;
    kritik boşlukta (burada norm + vakıa eksik) rapor 'KRİTİK BOŞLUK var'
    dese de süreç exit 0 ile biter. Script 'kapı değil karar-malzemesi'
    olarak tasarlanmıştır. Bu bilinçli mevcut tasarımdır — kapıya çevirme
    kararı Can'a sorulacak (bkz. _gorus/semantica-uyarlama.md)."""
    yol = _kiyas_yaz(izole_dizin, {})  # tamamen boş kıyas: her şey eksik
    kod, out, err = _cli(yol)

    assert "KRİTİK BOŞLUK var" in out
    assert "Bu boşluk kapanmadan sonuç güvenilir değildir." in out
    assert kod == 0, ("karakterizasyon: kritik boşlukta bile exit 0 döner "
                      f"(mevcut tasarım); kod={kod} stderr:\n{err}")


# ── üçlü yapı eksikleri ─────────────────────────────────────────────────────

def test_norm_eksik_kritik_isaretlenir(izole_dizin):
    k = _tam_kiyas()
    del k["buyuk_onerme"]["norm"]
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0  # karakterizasyon: kritikte de exit 0
    assert "✗ Büyük önerme: norm eksik" in out
    assert "KRİTİK BOŞLUK var" in out


def test_vakia_eksik_kritik_isaretlenir(izole_dizin):
    k = _tam_kiyas()
    k["kucuk_onerme"]["vakialar"] = []
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "✗ Küçük önerme: vakıa eksik" in out
    assert "KRİTİK BOŞLUK var" in out


def test_sonuc_yazilmamis_yalniz_uyari_kritik_sayilmaz(izole_dizin):
    """Karakterizasyon — mevcut tasarım: sonuç eksikliği ⚠ uyarıdır,
    kritik boşluk SAYILMAZ; diğer her şey tamsa 'Yapı bütün' basılır."""
    k = _tam_kiyas()
    del k["sonuc"]
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "⚠ Sonuç henüz yazılmamış" in out
    assert "SONUÇ: Yapı bütün." in out
    assert "KRİTİK BOŞLUK" not in out


# ── büyük önerme: içtihat yok / teyitsiz içtihat ────────────────────────────

def test_ictihat_yok_uyari_oa_ictihata_yonlendirir(izole_dizin):
    k = _tam_kiyas()
    k["buyuk_onerme"]["ictihat"] = []
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "⚠ Normu somutlaştıran içtihat yok → oa-ictihat ile emsal ara" in out
    assert "SONUÇ: Yapı bütün." in out  # içtihat yokluğu kritik sayılmaz


def test_teyitsiz_ictihat_uyari_ve_json_listesine_girer(izole_dizin):
    k = _tam_kiyas()
    k["buyuk_onerme"]["ictihat"] = [
        {"kunye": "Yargıtay 4. HD 2019/111 E. 2020/222 K.",
         "dogrulama": "teyitli"},
        {"kunye": "Yargıtay HGK 2018/999 E.", "dogrulama": "beklemede"},
        {"dogrulama": "teyitsiz"},  # künyesiz kayıt
    ]
    yol = _kiyas_yaz(izole_dizin, k)
    json_yol = izole_dizin / "sonuc.json"
    kod, out, _ = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "✓ Yargıtay 4. HD 2019/111 E. 2020/222 K. [teyitli]" in out
    assert "⚠ Yargıtay HGK 2018/999 E. [beklemede]" in out
    assert "⚠ (künye yok) [teyitsiz]" in out
    assert out.count("→ resmî kaynaktan (Yargı/Mevzuat MCP) teyit et") == 2

    veri = json.loads(json_yol.read_text(encoding="utf-8"))
    assert veri["teyitsiz_ictihat"] == ["Yargıtay HGK 2018/999 E.", "(künye yok)"]


def test_dogrulama_alani_yoksa_soru_isareti_ile_teyitsiz_sayilir(izole_dizin):
    """Karakterizasyon: 'dogrulama' alanı hiç yoksa '?' olarak raporlanır
    ve teyitsiz muamelesi görür."""
    k = _tam_kiyas()
    k["buyuk_onerme"]["ictihat"] = [{"kunye": "BAM 1. HD 2022/5 E."}]
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "⚠ BAM 1. HD 2022/5 E. [?]" in out
    assert "→ resmî kaynaktan (Yargı/Mevzuat MCP) teyit et" in out


# ── unsur ↔ vakıa eşleşmesinin üç durumu ────────────────────────────────────

def test_unsur_vakia_eslesmesi_uc_durum_ve_json_durumlari(izole_dizin):
    k = {
        "buyuk_onerme": {
            "norm": "TBK m.49",
            "ictihat": [{"kunye": "X", "dogrulama": "teyitli"}],
            "unsurlar": [
                {"id": "fiil", "ad": "Hukuka aykırı fiil"},      # delilli
                {"id": "kusur", "ad": "Kusur"},                  # delilsiz
                {"id": "illiyet", "ad": "İlliyet bağı"},         # karşılanmamış
            ],
        },
        "kucuk_onerme": {
            "vakialar": [
                {"metin": "Çarpma olayı", "karsilar": ["fiil"],
                 "dayanak_delil": ["tutanak"]},
                {"metin": "Alkollü sürüş iddiası", "karsilar": ["kusur"],
                 "dayanak_delil": []},
            ],
        },
        "sonuc": "Taslak sonuç",
    }
    yol = _kiyas_yaz(izole_dizin, k)
    json_yol = izole_dizin / "sonuc.json"
    kod, out, _ = _cli(yol, "--json", json_yol)

    assert kod == 0  # karşılanmamış unsur kritik ama exit yine 0
    assert "✓ [Hukuka aykırı fiil] ← vakıa var, delil var" in out
    assert "⚠ [Kusur] ← vakıa var ama DELİLSİZ → oa-vakia" in out
    assert "✗ [İlliyet bağı] ← KARŞILANMAMIŞ unsur (boşluk: ispat veya hukuki dayanak)" in out
    assert "KRİTİK BOŞLUK var" in out

    veri = json.loads(json_yol.read_text(encoding="utf-8"))
    assert veri["unsur_vakia_eslesme"] == [
        {"unsur_id": "fiil", "unsur_ad": "Hukuka aykırı fiil",
         "durum": "karsilanan_delilli"},
        {"unsur_id": "kusur", "unsur_ad": "Kusur",
         "durum": "karsilanan_delilsiz"},
        {"unsur_id": "illiyet", "unsur_ad": "İlliyet bağı",
         "durum": "karsilanmamis"},
    ]
    assert veri["kritik_bosluk"] is True


def test_unsurlar_duz_string_bicimi_de_kabul_edilir(izole_dizin):
    """Karakterizasyon: unsurlar {'id','ad'} sözlüğü yerine düz string de
    olabilir; string hem kimlik hem ad olarak kullanılır."""
    k = _tam_kiyas()
    k["buyuk_onerme"]["unsurlar"] = ["fiil", "zarar"]
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "✓ [fiil] ← vakıa var, delil var" in out
    assert "✓ [zarar] ← vakıa var, delil var" in out
    assert "SONUÇ: Yapı bütün." in out


def test_unsurlar_hic_yoksa_eslesme_denetimi_atlanir_kritik_sayilmaz(izole_dizin):
    """Karakterizasyon — mevcut tasarım: unsurlara ayrılmamış norm yalnız
    ⚠ uyarı alır; eşleşme denetimi yapılamadığı hâlde kritik SAYILMAZ."""
    k = _tam_kiyas()
    k["buyuk_onerme"]["unsurlar"] = []
    yol = _kiyas_yaz(izole_dizin, k)
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "⚠ Norm unsurlarına ayrılmamış — eşleşme denetimi yapılamıyor." in out
    assert "Normu unsurlara böl" in out
    assert "SONUÇ: Yapı bütün." in out


# ── yetim vakıa ─────────────────────────────────────────────────────────────

def test_yetim_vakia_uyari_ve_jsona_yazilir(izole_dizin):
    k = _tam_kiyas()
    k["kucuk_onerme"]["vakialar"].append(
        {"metin": "Davalının şapkası kırmızıydı", "dayanak_delil": ["fotoğraf"]})
    yol = _kiyas_yaz(izole_dizin, k)
    json_yol = izole_dizin / "sonuc.json"
    kod, out, _ = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert "⚠ 'Davalının şapkası kırmızıydı' — hangi unsuru karşılıyor? bağla veya çıkar" in out
    assert "✓ Her vakıa bir unsura bağlı." not in out

    veri = json.loads(json_yol.read_text(encoding="utf-8"))
    assert veri["yetim_vakialar"] == ["Davalının şapkası kırmızıydı"]


# ── --json çıktısı: şema anahtarları + içerik ───────────────────────────────

def test_json_cikti_sema_anahtarlari_ve_icerik(izole_dizin):
    yol = _kiyas_yaz(izole_dizin, _tam_kiyas())
    json_yol = izole_dizin / "sonuc.json"
    kod, out, _ = _cli(yol, "--json", json_yol)

    assert kod == 0
    assert f"[JSON] Makine-okur sonuc yazildi: {json_yol}" in out
    assert json_yol.is_file()

    veri = json.loads(json_yol.read_text(encoding="utf-8"))
    assert set(veri.keys()) == {
        "arac", "buyuk_onerme", "kucuk_onerme", "sonuc",
        "teyitsiz_ictihat", "unsur_vakia_eslesme", "yetim_vakialar",
        "kritik_bosluk", "girdi",
    }
    assert veri["arac"] == "kiyas_denetim"
    assert veri["girdi"] == str(yol)
    assert veri["kritik_bosluk"] is False
    assert set(veri["buyuk_onerme"].keys()) == {"norm", "ictihat", "unsurlar"}
    assert veri["buyuk_onerme"]["norm"].startswith("TBK m.49")
    assert set(veri["kucuk_onerme"].keys()) == {"vakialar"}
    assert len(veri["kucuk_onerme"]["vakialar"]) == 2
    assert veri["teyitsiz_ictihat"] == []
    assert veri["yetim_vakialar"] == []
    assert veri["sonuc"] == "TBK m.49 uyarınca tazminat sorumluluğu doğar."


def test_json_bayragi_verilmezse_json_dosyasi_yazilmaz(izole_dizin):
    yol = _kiyas_yaz(izole_dizin, _tam_kiyas())
    kod, out, _ = _cli(yol)

    assert kod == 0
    assert "[JSON]" not in out
    assert not (izole_dizin / "sonuc.json").exists()


# ── argümansız çağrı: kullanım mesajı + exit 1 ──────────────────────────────

def test_argumentsiz_cagri_kullanim_mesaji_exit1():
    kod, out, err = _cli()
    assert kod == 1
    assert "Kullanım: python kiyas_denetim.py kiyas.json [--json out.json]" in out


# ── bozuk/eksik girdi: script ÇÖKER (karakterizasyon) ───────────────────────

def test_var_olmayan_dosya_cokus_traceback(izole_dizin):
    """Karakterizasyon — mevcut tasarım: girdi dosyası yoksa yukle()
    yakalanmamış FileNotFoundError fırlatır; traceback + returncode != 0."""
    kod, out, err = _cli(izole_dizin / "yok-boyle-dosya.json")
    assert kod != 0
    assert "Traceback" in err
    assert "FileNotFoundError" in err


def test_bozuk_json_girdi_cokus_traceback(izole_dizin):
    """Karakterizasyon — mevcut tasarım: geçersiz JSON'da json.load
    yakalanmamış JSONDecodeError fırlatır; traceback + returncode != 0."""
    yol = izole_dizin / "kiyas.json"
    yol.write_text("{ gecersiz json", encoding="utf-8")
    kod, out, err = _cli(yol)
    assert kod != 0
    assert "Traceback" in err
    assert "JSONDecodeError" in err
