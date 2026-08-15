# -*- coding: utf-8 -*-
"""v0.5.8.4 — 372 karnesinden üç desenin BAĞLANMASI (desen SİLİNMEZ, BAĞLANIR):

1) [G5] ÜRETİCİ: `oa_hafiza.py teyit` artık --asan-kaynak / --asilma-tarihi /
   --gecerlilik-bitis alır; üretilen muhakeme kaydı satırları
   ictihat_muhakeme_denetim.py'nin ASAN_KAYNAK_LINE_RE / ASILMA_TARIHI_LINE_RE /
   GECERLILIK_BITIS_LINE_RE regexleriyle BİREBİR parse edilir (round-trip) ve
   LEHE+aşılmış+atıfta senaryosu [G5] TESLİM ENGELİ üretir. (372 karnesi:
   kapı kuruluydu ama alanları DOLDURAN üretici adım yoktu → 2 sahada %0;
   risk gerçek — koşu elle yakaladı: mülga HMK m.107, onamayla aşılan karar.)

2) --zincir VARSAYILAN: grafik_denetim.py zincir analizini (bölüm 8 +
   json 'zincirler') bayraksız üretir; --zincirsiz kapatır; --zincir
   geriye-uyum için kabul edilen NO-OP'tur. (372: grafik_denetim 2 kez koştu,
   bayrak 0 kez verildi → analiz hiç üretilmedi.)

3) ÖZNE TETİĞİ: vakia_matris.py matris kurarken taraf/özne yazım
   varyantlarını toplar ve ozne_eslestirici'nin jaro_winkler + eşikleriyle
   (BAGLA >= 0.92 / AVUKATA-SOR 0.80-0.92) çıktı json'a 'ozne_eslestirme'
   bölümü yazar; varyant yoksa boş liste (sessiz). (372: ozne_eslestirici'yi
   hiçbir akış çağırmıyordu — kullanıcı kararı: tetik oa-vakia'ya bağlandı.)

Tüm girdiler tmp_path + SENTETİK veridir (repo kuralı m.7 + sabit-yol-sızıntısı
dersi — gerçek dava klasörü yolu / kişi adı / TC yazılmaz).
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
HAFIZA = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
DENETIM = SKILLS / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py"
GRAFIK = SKILLS / "oa-illiyet" / "scripts" / "grafik_denetim.py"
VAKIA = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"


def _load(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cli(script, args, cwd=None):
    cp = subprocess.run(
        [sys.executable, str(script)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd) if cwd else None,
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ═══════════════════════════════════════════════════════════════════════════
# 1) [G5] ÜRETİCİ — teyit --asan-kaynak/--asilma-tarihi/--gecerlilik-bitis
# ═══════════════════════════════════════════════════════════════════════════

KUNYE = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
ASAN = "Yargıtay İBK, E. 2025/2, K. 2026/1, T. 15.03.2026"
ASILMA_TARIHI = "15.03.2026"
GECERLILIK_BITIS = "15.03.2026"
DOKUM_METIN = (
    "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni: "
    "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır; "
    "TBK m.49 uyarınca tazminat sorumluluğu doğar.\n"
)
ILGILI_KISIM = "davalının kusuru ile davacının zararı arasında illiyet bağı bulunmaktadır"
BAG_METNI = ("Bu karar, dosyamızdaki trafik kazası olgusuyla aynı unsur setini "
             "içeriyor; TBK m.49'un büyük önermesini somutlaştıran doğrudan emsaldir.")
ATIFLI_TASLAK = ("İstinaf sebeplerimiz Yargıtay 4. HD E. 2023/1234 K. 2023/5678 "
                 "sayılı kararına dayanmaktadır.\n")


def _init(tmp_path):
    _cli(HAFIZA, ["init", "--dosya", "Test Dosyası", "--kok", str(tmp_path)],
         cwd=tmp_path)


def _teyit_asilmis(tmp_path, damga="LEHE"):
    return _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_getir", "--sorgu", "TBK m.49 illiyet",
        "--sonuc", KUNYE, "--damga", damga, "--bag", BAG_METNI,
        "--ilgili-kisim", ILGILI_KISIM, "--dokum-icerik", DOKUM_METIN,
        "--asan-kaynak", ASAN, "--asilma-tarihi", ASILMA_TARIHI,
        "--gecerlilik-bitis", GECERLILIK_BITIS, "--kok", str(tmp_path)],
        cwd=tmp_path)


def test_g5_uretici_tek_komutla_uc_alan_round_trip(tmp_path):
    """Tek `teyit` komutu üç aşılmışlık alanını birden yazar; üretilen satırlar
    ictihat_muhakeme_denetim.py'nin regexleriyle BİREBİR parse edilir
    (round-trip) — MuhakemeKaydi alanları da aynı değeri okur."""
    _init(tmp_path)
    kod, cikti = _teyit_asilmis(tmp_path)
    assert kod == 0, cikti

    metin = (tmp_path / "_oa" / "cikti" / "03-ictihat-muhakeme.md").read_text(
        encoding="utf-8")
    imd = _load(DENETIM, "imd_v0584_roundtrip")

    m = imd.ASAN_KAYNAK_LINE_RE.search(metin)
    assert m and m.group(1).strip() == ASAN, metin
    m = imd.ASILMA_TARIHI_LINE_RE.search(metin)
    assert m and m.group(1).strip() == ASILMA_TARIHI, metin
    m = imd.GECERLILIK_BITIS_LINE_RE.search(metin)
    assert m and m.group(1).strip() == GECERLILIK_BITIS, metin

    kayit = imd.MuhakemeKaydi("test-bolum", metin)
    assert kayit.asan_kaynak == ASAN
    assert kayit.asilma_tarihi == ASILMA_TARIHI
    assert kayit.gecerlilik_bitis == GECERLILIK_BITIS
    assert kayit.damga == "LEHE"


def test_g5_lehe_asilmis_atifta_teslim_engeli(tmp_path):
    """Uçtan uca lehe-denetim akışı: üretici komut → kütük/muhakeme kaydı →
    ictihat_muhakeme_denetim → DAMGA=LEHE + aşılmış + atıfta → [G5] BLOK."""
    _init(tmp_path)
    kod, cikti = _teyit_asilmis(tmp_path)
    assert kod == 0, cikti

    taslak = tmp_path / "taslak.md"
    taslak.write_text(ATIFLI_TASLAK, encoding="utf-8")
    dkod, dcikti = _cli(DENETIM, ["taslak.md", "--kok", str(tmp_path)],
                        cwd=tmp_path)
    assert dkod == 1, dcikti
    assert "[G5]" in dcikti
    assert "KALAMAZ" in dcikti


def test_g5_uretici_lehe_asilmis_gorunur_uyari_basar(tmp_path):
    """LEHE damga + aşılmışlık alanı ÇELİŞKİLİDİR (aşılmış karar lehte dayanak
    olamaz) — üretici bunu yazar (bloklamaz; kütük hijyeni avukatındır) ama
    SESSİZ geçmez: görünür uyarı basar."""
    _init(tmp_path)
    kod, cikti = _teyit_asilmis(tmp_path, damga="LEHE")
    assert kod == 0, cikti
    assert "UYARI" in cikti
    assert "AŞILMIŞ" in cikti.upper()


def test_g5_alanlar_damgasiz_ret(tmp_path):
    """Aşılmışlık alanları muhakeme kaydında yaşar; kayıt yalnız --damga ile
    yazıldığından damgasız çağrıda alanlar SESSİZCE düşerdi (sessiz atlama
    yasağı) → fail-closed RET."""
    _init(tmp_path)
    kod, cikti = _cli(HAFIZA, [
        "teyit", "--arac", "ictihat_ara", "--sorgu", "TBK m.49 illiyet",
        "--sonuc", "aday künyeler bulundu", "--asan-kaynak", ASAN,
        "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "--damga" in cikti


# ═══════════════════════════════════════════════════════════════════════════
# 2) --zincir VARSAYILAN — grafik_denetim.py
# ═══════════════════════════════════════════════════════════════════════════

_GRAF = {
    "dugumler": [{"id": "a", "tip": "olay", "ad": "A"},
                 {"id": "b", "tip": "olay", "ad": "B"}],
    "kenarlar": [{"kaynak": "a", "hedef": "b", "kategori": "illiyet",
                  "tur": "fiil_netice", "illiyet_tipi": "dogal",
                  "guc": "guclu", "dayanak_delil": ["tutanak"],
                  "dogrulama": "delil"}],
}


def _graf_yaz(tmp_path):
    yol = tmp_path / "graf.json"
    yol.write_text(json.dumps(_GRAF, ensure_ascii=False), encoding="utf-8")
    return yol


def test_zincir_analizi_bayraksiz_varsayilan_uretilir(tmp_path):
    """v0.5.8.4 sözleşme değişikliği (bilinçli — 372'de 0 ateşleme kanıtı):
    zincir güven analizi artık BAYRAKSIZ üretilir; json'a 'zincirler' düşer."""
    graf = _graf_yaz(tmp_path)
    out_json = tmp_path / "out.json"
    kod, cikti = _cli(GRAFIK, [graf, "--json", out_json])
    assert kod == 0, cikti
    assert "ZİNCİR GÜVEN" in cikti
    r = json.loads(out_json.read_text(encoding="utf-8"))
    assert r["zincirler"] and r["zincirler"][0]["guven"] == 0.9


def test_zincirsiz_bayragi_kapatir(tmp_path):
    graf = _graf_yaz(tmp_path)
    out_json = tmp_path / "out.json"
    kod, cikti = _cli(GRAFIK, [graf, "--zincirsiz", "--json", out_json])
    assert kod == 0, cikti
    assert "ZİNCİR GÜVEN" not in cikti
    r = json.loads(out_json.read_text(encoding="utf-8"))
    assert "zincirler" not in r


def test_zincir_bayragi_geriye_uyum_noop(tmp_path):
    """--zincir kabul edilir ama NO-OP'tur — varsayılanla aynı çıktı
    (geriye uyum: eski çağrı kalıpları kırılmaz)."""
    graf = _graf_yaz(tmp_path)
    out_json = tmp_path / "out.json"
    kod, cikti = _cli(GRAFIK, [graf, "--zincir", "--json", out_json])
    assert kod == 0, cikti
    assert "ZİNCİR GÜVEN" in cikti
    r = json.loads(out_json.read_text(encoding="utf-8"))
    assert r["zincirler"] and r["zincirler"][0]["guven"] == 0.9


# ═══════════════════════════════════════════════════════════════════════════
# 3) ÖZNE TETİĞİ — vakia_matris.py 'ozne_eslestirme' bölümü
# ═══════════════════════════════════════════════════════════════════════════

def _vakia_kur(tmp_path, taraflar=None, olay_ozne=None):
    veri = {
        "iddialar": [{"id": "I1", "metin": "Sozlesme kuruldu"}],
        "olaylar": [{"tarih": "2025-01-10", "olgu": "Sozlesme imzalandi",
                     "belge": "yazili sozlesme", "destekler": ["I1"],
                     "ispat_durumu": "belgeli"}],
    }
    if taraflar is not None:
        veri["taraflar"] = taraflar
    if olay_ozne is not None:
        veri["olaylar"][0]["ozne"] = olay_ozne
    yol = tmp_path / "vakia.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _vakia_dogrula(tmp_path, yol):
    hedef = tmp_path / "sonuc.json"
    kod, cikti = _cli(VAKIA, ["--dogrula", yol, "--json", hedef])
    assert kod == 0, cikti
    return cikti, json.loads(hedef.read_text(encoding="utf-8"))


def test_ozne_iki_yazimli_sentetik_ozne_avukata_sor(tmp_path):
    """0.80-0.92 bandındaki iki yazım (akraba adı olabilir) otomatik
    BAĞLAnamaz — AVUKATA-SOR damgasıyla yüzeye çıkar (karar avukatta)."""
    yol = _vakia_kur(tmp_path, taraflar=["Osman Balcı", "Orhan Balcı"])
    cikti, sonuc = _vakia_dogrula(tmp_path, yol)
    assert len(sonuc["ozne_eslestirme"]) == 1, sonuc["ozne_eslestirme"]
    b = sonuc["ozne_eslestirme"][0]
    assert set(b["varyantlar"]) == {"Osman Balcı", "Orhan Balcı"}
    assert b["karar"] == "AVUKATA-SOR"
    assert 0.80 <= b["skor"] < 0.92
    assert "ÖZNE EŞLEŞTİRME" in cikti  # görünürlük — sessiz gömülmez


def test_ozne_yuksek_benzerlikte_bagla(tmp_path):
    """>= 0.92 (OCR ı/i varyantı) → BAGLA; özne adı hem `taraflar` hem
    olayın `ozne` alanından toplanır (iki kaynak birden)."""
    yol = _vakia_kur(tmp_path, taraflar=["Mehmet Demir"],
                     olay_ozne="Mehmet Demır")
    cikti, sonuc = _vakia_dogrula(tmp_path, yol)
    assert len(sonuc["ozne_eslestirme"]) == 1, sonuc["ozne_eslestirme"]
    b = sonuc["ozne_eslestirme"][0]
    assert set(b["varyantlar"]) == {"Mehmet Demir", "Mehmet Demır"}
    assert b["karar"] == "BAGLA"
    assert b["skor"] >= 0.92


def test_ozne_tek_yazimda_bos_liste_sessiz(tmp_path):
    """Tek yazım (birebir aynı dize varyant DEĞİLDİR) → boş liste, stdout'ta
    özne bloğu YOK (sessizlik sözleşmesi)."""
    yol = _vakia_kur(tmp_path, taraflar=["Mehmet Demir"],
                     olay_ozne="Mehmet Demir")
    cikti, sonuc = _vakia_dogrula(tmp_path, yol)
    assert sonuc["ozne_eslestirme"] == []
    assert "ÖZNE EŞLEŞTİRME" not in cikti


def test_ozne_alakasiz_adlar_esik_alti_sessiz(tmp_path):
    """Eşik altı (< 0.80) çiftler AYRI öznedir — sessiz kalır."""
    yol = _vakia_kur(tmp_path, taraflar=["Nihat Yılmaz", "Zeynep Kaya"])
    cikti, sonuc = _vakia_dogrula(tmp_path, yol)
    assert sonuc["ozne_eslestirme"] == []
    assert "ÖZNE EŞLEŞTİRME" not in cikti


def test_ozne_alani_hic_yokken_json_anahtari_yine_var(tmp_path):
    """Geriye uyum: taraflar/ozne alanı hiç olmayan eski vakia.json'da da
    'ozne_eslestirme' anahtarı boş liste olarak bulunur (şema kararlılığı)."""
    yol = _vakia_kur(tmp_path)
    cikti, sonuc = _vakia_dogrula(tmp_path, yol)
    assert sonuc["ozne_eslestirme"] == []
