# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — REVİZYON FARKI: oa-pipeline/scripts/revizyon_farki.py

Saha kanıtı (derlem denetimi bulguları B-08/B-18/B-20):
  B-08  teslimden sonra çalışma nüshası UYAP editöründe değişti; genel inkâr
        cümlesi başka bir cümleye dönüştü — hangi nüshanın verildiği kayıttan
        kurulamadı.
  B-18  mahkemeye giden nüshaya iç izleme verisi (HTML yorumu, betik adı,
        `_oa/` yolu) sızdı.
  B-20  makbuz taslağı onaylıyor, verilen metni değil; kaynakça bloğunun teslim
        nüshasında olup olmayacağı avukat kararı.
Fikir kaynağı Yargı PRO 10-9 (kod/metin alınmadı).

Sözleşme: salt okur (dosya yazmaz), ikili girdide FAIL-CLOSED (çıkış 2), biçim
gürültüsü kritik alarm üretmez (alarm yorgunluğu da zarardır), dava açısından
kritik sınıflar ayrıca işaretlenir; çıkış 0 aynı / 1 fark / 3 kritik.

Tüm fikstürler sentetiktir (Anayasa m.7): kişi/şirket adları kurgu, numaralar
algoritmaya uygun ÜRETİLMİŞ test değerleridir; testler tmp_path'te koşar.
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
SCRIPT = SKILLS / "oa-pipeline" / "scripts" / "revizyon_farki.py"
PIPELINE_MD = SKILLS / "oa-pipeline" / "SKILL.md"


def _load():
    spec = importlib.util.spec_from_file_location("v0518_revizyon_farki", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _cli(*args, cwd=None):
    cp = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(cwd or REPO))
    return cp.returncode, cp.stdout, cp.stderr


def _yaz(yol, metin):
    yol.write_text(metin, encoding="utf-8")
    return str(yol)


def _json(tmp_path, eski, yeni, *ek):
    e = _yaz(tmp_path / "eski.md", eski)
    y = _yaz(tmp_path / "yeni.md", yeni)
    rc, out, err = _cli("--eski", e, "--yeni", y, "--json", *ek)
    return rc, json.loads(out)


TASLAK = """<!-- kaynaklar: _oa/metin/00-kunye.json@aaaa1111 -->
# ÖRNEK ASLİYE HUKUK MAHKEMESİ'NE

**DOSYA NO** : 2024/123 Esas

**DAVACI** : Kurgu Kişi A

**DAVALI** : Kurgu Şirket B

## AÇIKLAMALAR

1. Taraflar arasında 12.03.2025 tarihli sözleşme imzalanmıştır. Davalı bedeli ödememiştir.

2. Davacının dava dilekçesindeki iddialarını kabul etmiyoruz. Şöyle ki ihtarname 05.04.2025 tarihinde tebliğ edilmiştir.

3. Sonuç olarak davalının temerrüdü sabittir.

## SONUÇ VE İSTEM

Fazlaya ilişkin haklarımız saklı kalmak kaydıyla 150.000,00 TL alacağın tahsiline karar verilmesini saygılarımızla talep ederiz.

EKLER: Sözleşme örneği.
"""


def _degistir(metin, eski, yeni):
    assert eski in metin, eski
    return metin.replace(eski, yeni, 1)


# ═══════════════════════════ biçim gürültüsü ═══════════════════════════════

def test_ayni_icerik_bicim_farki_AYNI_exit0(tmp_path):
    """İngest başlığı, sayfa ayracı, hiza notu, kalın/başlık işareti, satır
    kırılımı ve noktalama öncesi boşluk içerik farkı DEĞİLDİR → AYNI, çıkış 0."""
    yeni = ("# 040 · verilen.udf\n\n- Kaynak evrak: `kurgu/verilen.udf`\n- Çıkarım yöntemi: **udf**\n\n---\n\n"
            + TASLAK.replace("**", "").replace("## ", "").replace("DAVACI :", "DAVACI:")
            .replace("imzalanmıştır. Davalı", "imzalanmıştır.\nDavalı")
            .replace("ÖRNEK ASLİYE", "<!--hiza:orta-->ÖRNEK ASLİYE")
            .replace("## SONUÇ", "<!-- --- sayfa 2 --- -->\n\nSONUÇ"))
    rc, r = _json(tmp_path, TASLAK, yeni)
    assert rc == 0 and r["sonuc"] == "AYNI", r["farklar"]
    assert r["yeni"]["ingest_basligi"] is True and r["eski"]["ingest_basligi"] is False


def test_bicim_dahil_kipinde_isaretler_fark_sayilir(tmp_path):
    rc, r = _json(tmp_path, "Alacak **ödenmemiştir**.\n", "Alacak ödenmemiştir.\n", "--bicim-dahil")
    assert rc == 1 and r["sonuc"] == "FARK" and r["bicim_dahil"] is True


def test_tarih_ve_tutar_yazim_farki_kritik_alarm_uretmez(tmp_path):
    """5.04.2025 ile 05.04.2025 aynı tarih, 150.000,00 TL ile 150000 TL aynı
    tutardır: aynı cümlede başka bir kelime değişse de TARİH/TUTAR alarmı yok."""
    eski = "Bedel 150.000,00 TL olup 05.04.2025 tarihinde ödenmesi gerekirdi.\n"
    yeni = "Bedel 150000 TL olup 5.04.2025 tarihinde ödenmesi gerekmekteydi.\n"
    rc, r = _json(tmp_path, eski, yeni)
    assert rc == 1 and r["sonuc"] == "FARK"
    assert "TARİH" not in r["ozet"]["kritik_siniflar"]
    assert "TUTAR" not in r["ozet"]["kritik_siniflar"]


# ═══════════════════════════ kritik sınıflar ═══════════════════════════════

def test_tutar_degisimi_TUTAR_ve_TALEP_kritik_exit3(tmp_path):
    rc, r = _json(tmp_path, TASLAK, _degistir(TASLAK, "150.000,00 TL", "105.000,00 TL"))
    assert rc == 3 and r["sonuc"] == "KRİTİK FARK"
    tutar = [k for k in r["kritik"] if k["sinif"] == "TUTAR"]
    assert tutar and tutar[0]["silinen"] == ["150000.00 TL"] and tutar[0]["eklenen"] == ["105000.00 TL"]
    assert "TALEP SONUCU" in r["ozet"]["kritik_siniflar"]
    assert any("maliyet" in y for y in r["yeniden_denetim"])


def test_tarih_degisimi_TARIH_kritik_ve_sure_onerisi(tmp_path):
    rc, r = _json(tmp_path, TASLAK, _degistir(TASLAK, "05.04.2025", "06.04.2025"))
    assert rc == 3
    t = [k for k in r["kritik"] if k["sinif"] == "TARİH"][0]
    assert t["silinen"] == ["2025-04-05"] and t["eklenen"] == ["2025-04-06"]
    assert any("oa-sure" in y for y in r["yeniden_denetim"])


def test_B08_genel_inkar_cumlesi_silinirse_BAGLAYICI_BEYAN(tmp_path):
    """B-08'in birebir sınıfı: 'kabul etmiyoruz' cümlesi kalkıp 'Şöyle ki'
    cümlesi kalınca bağlayıcı beyan değişikliği KRİTİK olarak görünür."""
    yeni = _degistir(TASLAK, "Davacının dava dilekçesindeki iddialarını kabul etmiyoruz. ", "")
    rc, r = _json(tmp_path, TASLAK, yeni)
    assert rc == 3
    b = [k for k in r["kritik"] if k["sinif"] == "BAĞLAYICI BEYAN"]
    assert b and any("kabul etmiyoruz" in s for s in b[0]["silinen"])
    assert any("avukat onayı" in y for y in r["yeniden_denetim"])


def test_taraf_satiri_degisimi_TARAF(tmp_path):
    rc, r = _json(tmp_path, TASLAK, _degistir(TASLAK, "Kurgu Şirket B", "Kurgu Şirket C"))
    assert rc == 3
    t = [k for k in r["kritik"] if k["sinif"] == "TARAF"][0]
    assert "Kurgu Şirket B" in t["silinen"][0] and "Kurgu Şirket C" in t["eklenen"][0]


def test_sonuc_olarak_cumlesi_talep_bolumu_sayilmaz(tmp_path):
    """'Sonuç olarak …' gerekçe cümlesidir; değişmesi TALEP SONUCU alarmı vermez."""
    yeni = _degistir(TASLAK, "3. Sonuç olarak davalının temerrüdü sabittir.",
                     "3. Sonuç olarak davalının temerrüdü açıktır.")
    rc, r = _json(tmp_path, TASLAK, yeni)
    assert rc == 1 and "TALEP SONUCU" not in r["ozet"]["kritik_siniflar"]


def test_hukum_bolumu_karar_nushasinda_TALEP_kritik(tmp_path):
    karar = ("GEREKÇE: Dosya kapsamı incelendi.\n\nHÜKÜM: Gerekçesi yukarıda açıklandığı üzere;\n\n"
             "1- Davanın KABULÜNE,\n\n2- Yargılama giderinin davalıya yükletilmesine karar verildi.\n")
    yeni = karar.replace("KABULÜNE", "KISMEN KABULÜNE")
    rc, r = _json(tmp_path, karar, yeni)
    assert rc == 3 and "TALEP SONUCU" in r["ozet"]["kritik_siniflar"]


def test_yeni_kunye_eklenirse_KUNYE_ve_atif_kapisi_onerisi(tmp_path):
    """Yargı PRO 10-9 fikrinin OA karşılığı: elle eklenen künye doğrulanmamış
    sayılır → atıf kapısı yeniden koşar önerisi."""
    yeni = _degistir(TASLAK, "Davalı bedeli ödememiştir.",
                     "Davalı bedeli ödememiştir. Yargıtay 11. HD 2022/1 E. kararı ve HMK m.119 bu yöndedir.")
    rc, r = _json(tmp_path, TASLAK, yeni)
    assert rc == 3
    k = [x for x in r["kritik"] if x["sinif"] == "KÜNYE/ATIF"][0]
    assert "11. HD" in k["eklenen"] and "HMK m.119" in k["eklenen"]
    assert "ESAS/KARAR/DOSYA NO" in r["ozet"]["kritik_siniflar"]
    assert any("DOĞRULANMAMIŞ" in y for y in r["yeniden_denetim"])


def test_kanun_madde_atfi_iki_yazim_bicimi_ayni_sayilir(tmp_path):
    """'HMK m.119' ile 'HMK'nın 119. maddesi' aynı atıftır — yazım değişikliği
    künye alarmı üretmez (yalnız kelime farkı görünür)."""
    rc, r = _json(tmp_path, "Dilekçe HMK m.119 uyarınca eksiksizdir.\n",
                  "Dilekçe HMK'nın 119. maddesi uyarınca eksiksizdir.\n")
    assert rc == 1 and "KÜNYE/ATIF" not in r["ozet"]["kritik_siniflar"]


def _iban(bban):
    sayi = int("".join(str(int(c, 36)) for c in bban + "TR00"))
    return f"TR{98 - sayi % 97:02d}{bban}"


def test_tckn_ve_iban_degisimi_KIMLIK_IBAN_algoritma_notuyla(tmp_path):
    iban1, iban2 = _iban("0001000000000000000001"), _iban("0001000000000000000002")
    assert MOD._iban_gecerli(iban1) and MOD._iban_gecerli(iban2)
    assert MOD._tckn_gecerli("10000000146") and not MOD._tckn_gecerli("10000000147")
    eski = f"DAVACI: Kurgu A (TCKN 10000000146)\n\nÖdeme {iban1} hesabına yapılır.\n"
    yeni = f"DAVACI: Kurgu A (TCKN 10000000147)\n\nÖdeme {iban2} hesabına yapılır.\n"
    rc, r = _json(tmp_path, eski, yeni)
    assert rc == 3
    kimlik = [k for k in r["kritik"] if k["sinif"] == "KİMLİK"][0]
    assert "TCKN 10000000147 (algoritma: GEÇERSİZ)" in kimlik["eklenen"]
    assert [k for k in r["kritik"] if k["sinif"] == "IBAN"][0]["eklenen"] == [iban2]
    assert "TARAF" in r["ozet"]["kritik_siniflar"]


def test_esas_no_degisimi_ESAS_kritik(tmp_path):
    rc, r = _json(tmp_path, TASLAK, _degistir(TASLAK, "2024/123 Esas", "2024/132 Esas"))
    assert rc == 3
    e = [k for k in r["kritik"] if k["sinif"] == "ESAS/KARAR/DOSYA NO"][0]
    assert e["silinen"] == ["2024/123"] and e["eklenen"] == ["2024/132"]


def test_oran_degisimi_ORAN_kritik(tmp_path):
    rc, r = _json(tmp_path, "Alacağa yıllık %24 faiz uygulanır.\n", "Alacağa yıllık %9 faiz uygulanır.\n")
    assert rc == 3 and [k for k in r["kritik"] if k["sinif"] == "ORAN"][0]["eklenen"] == ["yüzde 9"]


def test_tasinan_cumle_TASINDI_kritik_degil(tmp_path):
    eski = "Birinci olgu yazıldı.\n\nİkinci olgu yazıldı.\n\nÜçüncü olgu yazıldı.\n"
    yeni = "İkinci olgu yazıldı.\n\nBirinci olgu yazıldı.\n\nÜçüncü olgu yazıldı.\n"
    rc, r = _json(tmp_path, eski, yeni)
    assert rc == 1 and r["sonuc"] == "FARK" and r["ozet"]["kritik"] == 0
    assert r["tasinanlar"] and r["ozet"]["tasindi"] >= 1


# ═══════════════════════════ iç iz (B-18) + kaynakça (B-20) ════════════════

def test_B18_teslim_kipinde_ic_iz_KRITIK(tmp_path):
    yeni = ("DAVACI: Kurgu A\n\n&lt;!-- kaynaklar: _oa/metin/00-kunye.json@x --&gt;\n\n"
            "Alacak ödenmemiştir.\n\nbu blok kaynakca_uret.py tarafından mekanik üretilir\n")
    rc, r = _json(tmp_path, "DAVACI: Kurgu A\n\nAlacak ödenmemiştir.\n", yeni, "--teslim")
    assert rc == 3 and r["teslim"] is True
    iz = [k for k in r["kritik"] if k["sinif"] == "İÇ İZ"][0]
    assert len(iz["eklenen"]) == 2


def test_taslak_taslak_ic_iz_alarm_uretmez_ama_uyarir(tmp_path):
    """Taslağın zorunlu kaynak satırı (sha'sı değişse de) iki taslak arasında
    KRİTİK değildir; teslim kipinde ise kritiktir (alarm yorgunluğu dengesi).
    v0.5.18 Fable karşı-tezi: içeriği değişen HTML yorumu artık GÖRÜNÜR bir
    YORUM farkıdır (çıkış 1) — gizli satır "AYNI" sonucunun arkasına saklanamaz."""
    yeni = TASLAK.replace("@aaaa1111", "@bbbb2222")
    rc, r = _json(tmp_path, TASLAK, yeni)
    assert rc == 1 and r["sonuc"] == "FARK" and r["ozet"]["kritik"] == 0
    assert r["ozet"]["yorum"] == 1 and [f["tur"] for f in r["farklar"]] == ["YORUM"]
    assert "@bbbb2222" in r["farklar"][0]["yeni"]
    assert any("iç iz" in u for u in r["uyarilar"])
    rc2, r2 = _json(tmp_path, TASLAK, yeni, "--teslim")
    assert rc2 == 3 and "İÇ İZ" in r2["ozet"]["kritik_siniflar"]
    rc3, r3 = _json(tmp_path, TASLAK, TASLAK.replace("<!-- kaynaklar: _oa/metin/00-kunye.json@aaaa1111 -->" + chr(10), ""))
    assert rc3 == 0 and r3["sonuc"] == "AYNI"     # silinen yorum temizliktir, fark sayılmaz


def test_B20_makine_kaynakca_blogu_karsilastirma_disi(tmp_path):
    blok = ("\n<!-- kaynakca:v1 -->\n\n## İÇTİHAT KAYNAKÇASI\n\n"
            "- Yargıtay 9. HD 2021/99 E., 2022/11 K.\n\n<!-- /kaynakca -->\n")
    rc, r = _json(tmp_path, TASLAK + blok, TASLAK)
    assert rc == 0 and r["sonuc"] == "AYNI", r["kritik"]
    assert r["eski"]["kaynakca_blogu"] == 1 and r["yeni"]["kaynakca_blogu"] == 0
    assert any("B-20" in u for u in r["uyarilar"])


# ═══════════════════════════ girdi sözleşmesi ══════════════════════════════

def test_ikili_girdi_fail_closed_exit2(tmp_path):
    a = _yaz(tmp_path / "a.md", "metin\n")
    udf = tmp_path / "b.udf"
    udf.write_bytes(b"PK\x03\x04sahte")
    rc, out, _ = _cli("--eski", a, "--yeni", str(udf))
    assert rc == 2 and "oa-ingest" in out and "Hiçbir karşılaştırma yapılmadı" in out
    zip_md = tmp_path / "gizli.md"
    zip_md.write_bytes(b"PK\x03\x04uzanti-yaniltici")
    rc, out, _ = _cli("--eski", a, "--yeni", str(zip_md))
    assert rc == 2 and "ikili imza" in out


def test_dosya_yok_exit2(tmp_path):
    a = _yaz(tmp_path / "a.md", "metin\n")
    rc, out, _ = _cli("--eski", a, "--yeni", str(tmp_path / "yok.md"))
    assert rc == 2 and "dosya yok" in out


def test_bos_nusha_DENETLENEMEDI_aynı_sayilmaz(tmp_path):
    rc, r = _json(tmp_path, "", "")
    assert rc == 1 and r["sonuc"] == "DENETLENEMEDİ"
    assert any("boş" in u for u in r["uyarilar"])


def test_salt_okur_hicbir_dosya_yazmaz(tmp_path):
    e = _yaz(tmp_path / "eski.md", TASLAK)
    y = _yaz(tmp_path / "yeni.md", _degistir(TASLAK, "150.000,00", "105.000,00"))
    once = {p.name: (p.stat().st_mtime_ns, p.read_bytes()) for p in tmp_path.iterdir()}
    for ek in ((), ("--json",), ("--teslim",)):
        _cli("--eski", e, "--yeni", y, *ek, cwd=tmp_path)
    sonra = {p.name: (p.stat().st_mtime_ns, p.read_bytes()) for p in tmp_path.iterdir()}
    assert once == sonra, "revizyon_farki bir dosya yazdı ya da değiştirdi"


def test_json_semasi_ve_sha256(tmp_path):
    rc, r = _json(tmp_path, TASLAK, _degistir(TASLAK, "Kurgu Şirket B", "Kurgu Şirket C"))
    for k in ("arac", "surum", "eski", "yeni", "sonuc", "ozet", "kritik", "farklar", "tasinanlar",
              "yeniden_denetim", "uyarilar", "cikis_kodu"):
        assert k in r, k
    assert r["arac"] == "revizyon_farki" and r["cikis_kodu"] == rc
    assert r["eski"]["sha256"] == hashlib.sha256((tmp_path / "eski.md").read_bytes()).hexdigest()


def test_ocr_kaynakli_nusha_gorunur_uyari(tmp_path):
    yeni = ("# 041 · tarama.pdf\n\n- Kaynak evrak: `kurgu/tarama.pdf`\n- Çıkarım yöntemi: **ocr**\n"
            "- ⚠ **OCR/zayıf çıkarım — künye ve sayısal veri için orijinalden TEYİT gerekir.**\n\n---\n\n"
            "Alacak 1.000 TL olup ödenmemiştir.\n")
    rc, r = _json(tmp_path, "Alacak 1.800 TL olup ödenmemiştir.\n", yeni)
    assert rc == 3 and any("OCR" in u and "orijinal" in u for u in r["uyarilar"])


def test_insan_raporu_kirpmasi_gorunur(tmp_path):
    """Birbirinden AYRIK değişiklikler ayrı bloklardır (bitişik değişiklik tek
    blokta birleşir); --en-cok sınırı aşılınca kırpma GÖRÜNÜR yazılır."""
    eski = "\n\n".join(f"Paragraf {i} birinci hâl." for i in range(1, 9)) + "\n"
    yeni = "\n\n".join(f"Paragraf {i} {'ikinci' if i % 2 else 'birinci'} hâl." for i in range(1, 9)) + "\n"
    e, y = _yaz(tmp_path / "e.md", eski), _yaz(tmp_path / "y.md", yeni)
    rc, out, _ = _cli("--eski", e, "--yeni", y, "--en-cok", "1")
    assert rc == 1 and "GÖSTERİLMEDİ" in out and "sessiz atlama değildir" in out


def test_buyuk_girdi_hizli_hizalama_gorunur_ve_fark_gizlenmez(tmp_path):
    """Kilitlenme koruması: ortak baş/son kırpıldıktan sonra eşik üstü orta kısım
    autojunk ile hizalanır; iki uçtaki değişiklik de raporda kalır (fark
    gizlenmez) ve durum görünür uyarıyla yazılır. Zaman ölçülmez (deterministik)."""
    n = MOD.HIZLI_HIZALAMA_ESIGI + 600
    eski = [f"Olgu {i} kurgu olarak kaydedildi." for i in range(n)]
    yeni = list(eski)
    yeni[5] = "Olgu 5 kurgu olarak değiştirildi."
    yeni[n - 5] = f"Olgu {n - 5} kurgu olarak değiştirildi."
    rc, r = _json(tmp_path, "\n\n".join(eski) + "\n", "\n\n".join(yeni) + "\n")
    assert rc == 1 and r["ozet"]["degisti"] == 2, r["ozet"]
    assert any("hizalama hızlandırıldı" in u for u in r["uyarilar"])


def test_cok_buyuk_dosya_reddedilir_exit2(tmp_path):
    a = _yaz(tmp_path / "a.md", "metin\n")
    b = tmp_path / "b.md"
    b.write_bytes(b"a" * (MOD.AZAMI_BAYT + 1))
    rc, out, _ = _cli("--eski", a, "--yeni", str(b))
    assert rc == 2 and "çok büyük" in out


def test_patolojik_kisaltma_dizisi_kilitlenmez(tmp_path):
    """'A. A. A. …' gibi bölünmeyen nokta dizisinde önceki sözcük sınırlı
    pencereden alınır — karesel tarama yok; sonuç deterministik."""
    p = "Başlangıç " + "A. " * 6000 + "son."
    assert MOD.cumlelere_bol(p) == [p.strip()]
    rc, r = _json(tmp_path, p + "\n", p.replace("son.", "bitiş.") + "\n")
    assert rc == 1 and r["ozet"]["degisti"] == 1


def test_cumle_bolucu_kisaltmada_bolmez():
    parcalar = MOD.cumlelere_bol("Yargıtay 3. HD ve HMK m. 119 uyarınca T.C. vatandaşı ödedi. Sonra itiraz etti.")
    assert parcalar == ["Yargıtay 3. HD ve HMK m. 119 uyarınca T.C. vatandaşı ödedi.", "Sonra itiraz etti."]


def test_utf8_guard_ve_ag_importu_yok():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "__OA_UTF8_GUARD__" in src
    assert "5846 sayılı FSEK" in src
    assert not re.search(r"^\s*(?:from|import)\s+(requests|httpx|urllib|socket|http\.client)", src, re.M)
    assert "open(" in src and not re.search(r"open\([^)]*['\"][wa]b?['\"]", src), "script yazma kipinde dosya açıyor"


def test_oa_pipeline_skill_md_kullanim_paragrafi():
    txt = PIPELINE_MD.read_text(encoding="utf-8")
    assert "scripts/revizyon_farki.py" in txt
    blok = txt[txt.index("REVİZYON FARKI"):]
    blok = blok[:blok.index("\n\n")]
    for k in ("SALT OKUR", "--teslim", "B-08", "oa-ingest", "avukat", "3"):
        assert k in blok, k
    assert "DENETLENEMEDİ" in blok and "YORUM" in blok   # çıkış 1'in iki anlamı ve yorum farkı yazılı


# ═══════════════════════════ Fable 5.1 karşı-tezi sonrası (v0.5.18) ═══════════

def test_gorunmez_yon_karakteri_teslimde_ve_artista_IC_IZ_kritik(tmp_path):
    """B-22: sıfır genişlikli/yön denetim karakteri metni görünenden farklı
    okutabilir. Atılıp "AYNI" denmez; yumuşak tire (U+00AD) zararsızdır."""
    rc, r = _json(tmp_path, "Alacak ödenmemiştir.\n", "Alacak öden\u202emiştir.\n", "--teslim")
    assert rc == 3 and "İÇ İZ" in r["ozet"]["kritik_siniflar"]
    assert r["yeni"]["gorunmez_karakter_tehlikeli"] == 1
    rc, r = _json(tmp_path, "Alacak ödenmemiştir.\n", "Alacak öden\u200bmemiştir.\n")
    assert rc == 3
    rc, r = _json(tmp_path, "Alacak ödenmemiştir.\n", "Alacak öden\u00admemiştir.\n", "--teslim")
    assert rc == 0 and r["sonuc"] == "AYNI" and r["yeni"]["gorunmez_karakter"] == 1


def test_ayni_degerlerin_yer_degistirmesi_SIRA_kritik(tmp_path):
    rc, r = _json(tmp_path, "Sözleşme 01.01.2025 başlangıçlı olup 01.06.2025 tarihinde sona erer.\n",
                  "Sözleşme 01.06.2025 başlangıçlı olup 01.01.2025 tarihinde sona erer.\n")
    assert rc == 3
    t = [k for k in r["kritik"] if k["sinif"] == "TARİH"][0]
    assert "SIRASI" in t["aciklama"] and t["silinen"] == ["2025-01-01", "2025-06-01"]
    assert t["eklenen"] == ["2025-06-01", "2025-01-01"]


def test_tutar_virgul_tire_yazimi_yakalanir(tmp_path):
    rc, r = _json(tmp_path, "Toplam 150.000,-TL talep edilir.\n", "Toplam 105.000,- TL talep edilir.\n")
    assert rc == 3
    t = [k for k in r["kritik"] if k["sinif"] == "TUTAR"][0]
    assert t["silinen"] == ["150000.00 TL"] and t["eklenen"] == ["105000.00 TL"]


def test_daire_kunyesi_bicim_farki_alarm_uretmez_numara_farki_uretir(tmp_path):
    rc, r = _json(tmp_path, "Yargıtay 3. Hukuk Dairesi kararı uygundur.\n", "Yargıtay 3. HD kararı uygundur.\n")
    assert rc == 1 and "KÜNYE/ATIF" not in r["ozet"]["kritik_siniflar"]
    rc, r = _json(tmp_path, "Yargıtay 3. H.D. kararı uygundur.\n", "Yargıtay 4. H.D. kararı uygundur.\n")
    k = [x for x in r["kritik"] if x["sinif"] == "KÜNYE/ATIF"][0]
    assert rc == 3 and k["silinen"] == ["3. HD"] and k["eklenen"] == ["4. HD"]


def test_vekil_ve_adres_satiri_TARAF(tmp_path):
    rc, r = _json(tmp_path, "DAVACI: Kurgu A\n\nVEKİLİ: Av. Kurgu B\n", "DAVACI: Kurgu A\n\nVEKİLİ: Av. Kurgu C\n")
    assert rc == 3 and "TARAF" in r["ozet"]["kritik_siniflar"]
    rc, r = _json(tmp_path, "ADRES: Kurgu Sokak 1\n", "ADRES: Kurgu Sokak 2\n")
    assert rc == 3 and "TARAF" in r["ozet"]["kritik_siniflar"]


def test_talep_basligi_ekli_bicim_ve_yapisik_paragraf(tmp_path):
    govde = "AÇIKLAMA metni.\n\nSONUÇ VE İSTEMLERİMİZ: Davanın kabulüne karar verilmesini talep ederiz.\n"
    rc, r = _json(tmp_path, govde, govde.replace("kabulüne", "reddine"))
    assert rc == 3 and "TALEP SONUCU" in r["ozet"]["kritik_siniflar"]
    # başlık önceki paragrafa boş satırsız yapışmış (OCR/PDF çıktısı) — yine talep bölümü
    yapisik = ("Davalı ödememiştir. SONUÇ VE İSTEM: Fazlaya ilişkin haklar saklı kalmak kaydıyla alacağın "
               "tahsiline karar verilsin.\n")
    rc, r = _json(tmp_path, yapisik, yapisik.replace("tahsiline", "tespitine"))
    assert rc == 3 and "TALEP SONUCU" in r["ozet"]["kritik_siniflar"]
    # tek başına "TALEP :" üst bilgi satırı bölüm açmaz (bütün gövde alarm olurdu)
    ust = "TALEP : İhtiyati tedbir.\n\nOlay kurgu biçimde gelişti.\n"
    rc, r = _json(tmp_path, ust, ust.replace("kurgu biçimde", "başka biçimde"))
    assert rc == 1 and "TALEP SONUCU" not in r["ozet"]["kritik_siniflar"]


def test_tasinan_adet_esleme_ikinci_silme_gizlenmez_ve_beyan_tasinmasi_kritik(tmp_path):
    rc, r = _json(tmp_path, "Aynı cümle.\n\nAra metin bir.\n\nAynı cümle.\n\nSon.\n",
                  "Ara metin bir.\n\nAynı cümle.\n\nSon.\n")
    assert rc == 1 and [(f["tur"], f["eski"]) for f in r["farklar"]] == [("SİLİNDİ", "Aynı cümle.")]
    rc, r = _json(tmp_path, "Birinci olgu.\n\nDavacının iddialarını kabul etmiyoruz.\n\nÜçüncü olgu.\n",
                  "Davacının iddialarını kabul etmiyoruz.\n\nBirinci olgu.\n\nÜçüncü olgu.\n")
    assert rc == 3 and "BAĞLAYICI BEYAN" in r["ozet"]["kritik_siniflar"]
    assert all(t["yeni_konum"].startswith("¶") for t in r["tasinanlar"])


def test_beyan_kokleri_genisledi(tmp_path):
    for eski, yeni in (("Bu hususu kabul etmekteyiz.", "Bu hususu tartışıyoruz."),
                       ("Ödemeyi taahhüt ederiz.", "Ödemeyi değerlendiririz."),
                       ("İhtirazi kayıtla ödendi.", "Ödendi.")):
        rc, r = _json(tmp_path, eski + "\n", yeni + "\n")
        assert rc == 3 and "BAĞLAYICI BEYAN" in r["ozet"]["kritik_siniflar"], eski
    # "kabul edilmesi gerekir" genel talep cümlesidir, bağlayıcı beyan değildir
    rc, r = _json(tmp_path, "Davanın kabul edilmesi gerekir.\n", "Davanın kabul edilmesi gerekmektedir.\n")
    assert "BAĞLAYICI BEYAN" not in r["ozet"]["kritik_siniflar"]


def test_isaret_rakam_onunde_madde_imi_sayilmaz_ve_br_satir_kirilimi(tmp_path):
    rc, r = _json(tmp_path, "Hesap:\n\n- 1.000 TL indirim\n", "Hesap:\n\n+ 1.000 TL indirim\n")
    assert rc == 1 and r["sonuc"] == "FARK"
    rc, r = _json(tmp_path, "Alacak<br>ödenmemiştir.\n", "Alacak ödenmemiştir.\n")
    assert rc == 0 and r["sonuc"] == "AYNI"


def test_kapanmayan_yorum_ve_kaynakca_isaretleri_dogrusal_ayiklanir():
    """Kilitlenme koruması: tembel '<!--.*?-->' taraması kapanmayan çok sayıda
    '<!--' içeren girdide karesel olabiliyordu; ayıklama doğrusaldır ve
    kapanmayan işaret metin olarak kalır (sonuç doğrulanır, süre ölçülmez)."""
    assert MOD._yorum_ayikla("a<!--x-->b<!--y") == ("ab<!--y", ["x"])
    temiz, sayi = MOD._kaynakca_ayikla("a<!-- kaynakca:v1 -->K<!-- /kaynakca -->b<!-- kaynakca:v1 -->c")
    assert (temiz, sayi) == ("a\nb<!-- kaynakca:v1 -->c", 1)
    patolojik = "<!--" * 50000 + "son"
    temiz, yorumlar = MOD._yorum_ayikla(patolojik)
    assert temiz == patolojik and yorumlar == []
    birimler, bilgi = MOD.birimlere_ayir("<!-- kaynakca:v1 -->" * 20000 + "\n\nAlacak ödenmemiştir.\n")
    assert bilgi["kaynakca_blogu"] == 0 and birimler[-1]["metin"] == "Alacak ödenmemiştir."
