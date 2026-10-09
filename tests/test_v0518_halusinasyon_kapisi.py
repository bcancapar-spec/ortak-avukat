# -*- coding: utf-8 -*-
"""v0.5.18 — HALÜSİNASYON KAPISI: motorlar koşmadan zincir ilerlemez.

NEDEN VAR (v0.5.18 saha testi, gerçek bir icra hukuk dosyası — bu dosyada o
dosyadan HİÇBİR veri yoktur): vakia_matris, grafik_denetim, antitez_matris,
kiyas_denetim ve capraz_denetim kurulu ve sağlamdı (duman testi: beşi de exit 0,
damgalı çıktı) ama test oturumunda SIFIR kez koştu. Yazılım mühendisi + hukukçu
kimliğiyle danışılan Fable 5.1'in teşhisi: "zincirde motoru ÇAĞIRAN deterministik
hiçbir halka yok; bütün kapılar 'çıktı VAR mı' sorar, 'motor KOŞTU mu' sormaz."
Somut delikler:
  (1) C5 ELDEN düşürmesi kanıtta HERHANGİ bir `_oa/` yolu görünce susuyordu —
      modelin kendi yazdığı .md yeterliydi;
  (2) adım-8 kapısı yalnız adım-5'in BEKLIYOR olup olmadığına bakıyordu;
  (3) BILGI-EKSIK/GEREKSIZ ile geçiş her zaman serbestti (önkoşullar yalnız
      UYGULANDI'da sorulur); teslim (d) kapısı yalnız statünün VARLIĞINA bakar.
Bu dosya yeni sözleşmeyi kilitler:
  (a) motor parçasında UYGULANDI = motorun KENDİ damgası diskte, çökmemiş ve
      taze (BAYAT hükmünün tek kaynağı tazelik_denetim'dir); yoksa ELDEN;
  (b) adım-8 UYGULANDI dört damga yokken RET — yalnız `--serh-kapi
      halusinasyon` (ya da tumu) gerekçeli şerhle geçilir;
  (c) teslim (c2) kapısı statüye değil DİSKE bakar — BILGI-EKSIK onu geçemez;
      şerhli geçiş ortak istisna defterine yazılır;
  (d) motor_koprusu.py dört motoru tek komutla koşturur; damgayı MOTOR yazar,
      köprü hiçbir dosyaya damga koymaz ve doldurulmamış iskeleti doğrulatmaz.
Bütün veriler kurgudur (anayasa m.7); her şey tmp_path'te üretilir.
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

import oa_motor_damga as omd

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
PK = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
TP = SKILLS / "oa-kontrol" / "scripts" / "teslim_paketi.py"
KOPRU = SKILLS / "oa-pipeline" / "scripts" / "motor_koprusu.py"
VAKIA = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
ANTITEZ = SKILLS / "oa-antitez" / "scripts" / "antitez_matris.py"

UZUN_KANIT = "Fiilen script çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
SERH = "Avukat şerhi: bu dilekçe türünde motor denetimi gereksiz, gerekçe kayıtlı."

# test_teslim_makbuz.py'nin (a)-(c) kapılarından geçen kurgu taslağı.
TASLAK = """İSTANBUL 4. ASLİYE HUKUK MAHKEMESİ HAKİMLİĞİ'NE

DAVACI: Ayşe Yılmaz (T.C. Kimlik No: kurgu-maskeli)
Adres: Örnek Mahallesi No:1 İstanbul

DAVALI: Mehmet Kaya

KONU: Alacağın tahsili talebimizden ibarettir.

AÇIKLAMALAR (VAKIALAR):
1. Taraflar arasındaki ticari ilişkiden doğan alacak vakıası aşağıda özetlenmiştir.
2. Davalı, sözleşme kapsamındaki edimini yerine getirmemiştir.

HUKUKİ SEBEPLER:
İlgili mevzuat hükümleri ve genel hukuk kuralları dayanak alınmıştır.

DELİLLER:
Tanık beyanları, bilirkişi incelemesi ve yazılı belgeler ispat vasıtasıdır.

NETİCE-İ TALEP:
Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini saygılarımla talep ederim.

Tarih: 01.07.2026

Av. Ayşe Yılmaz
Vekil
İmza
"""

# Motor girdileri (kurgu) — test_grafik_denetim / test_v0518_zincir_capraz ile aynı biçim.
GRAF = {
    "dugumler": [
        {"id": "DAVALI", "tip": "gercek_kisi", "ad": "Davali Kisi", "usul_rolu": "davali"},
        {"id": "FIIL", "tip": "olay", "ad": "Trafik Kazasi"},
        {"id": "ZARAR", "tip": "olay", "ad": "Bedensel Zarar"},
    ],
    "kenarlar": [
        {"kaynak": "DAVALI", "hedef": "FIIL", "kategori": "iliski", "tur": "faili",
         "dogrulama": "delil", "dayanak_delil": ["kaza tutanagi"]},
        {"kaynak": "FIIL", "hedef": "ZARAR", "kategori": "illiyet", "tur": "sebep",
         "illiyet_tipi": "dogal", "guc": "guclu", "dogrulama": "delil",
         "dayanak_delil": ["bilirkisi raporu"]},
        {"kaynak": "DAVALI", "hedef": "ZARAR", "kategori": "iliski", "tur": "sorumlu",
         "dogrulama": "delil", "dayanak_delil": ["kusur raporu"]},
    ],
}
VAKIA_GIRDI = {
    "iddialar": [{"id": "iddia-1", "metin": "Taraflar sözleşme imzaladı"}],
    "olaylar": [{"tarih": "2024-03-12", "olgu": "Taraflar sözleşme imzaladı",
                 "belge": "Sözleşme örneği", "destekler": ["iddia-1"],
                 "ispat_durumu": "belgeli"}],
}
KIYAS_GIRDI = {
    "buyuk_onerme": {"unsurlar": [{"id": "unsur-1"}]},
    "kucuk_onerme": {"vakialar": [{"metin": "Taraflar sözleşme imzaladı",
                                    "karsilar": ["unsur-1"], "dayanak_delil": ["delil-1"]}]},
}


# ═══════════════════════════ düzenek ═══════════════════════════════════════

def _calistir(betik, args, cwd):
    cp = subprocess.run([sys.executable, str(betik)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _pk(args, kok):
    return _calistir(PK, list(args) + ["--kok", str(kok)], kok)


def _kok(tmp_path, defter=True):
    kok = tmp_path / "dava"
    (kok / "_oa" / "metin").mkdir(parents=True)
    (kok / "_oa" / "cikti").mkdir(parents=True)
    (kok / "_oa" / "metin" / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")
    if defter:
        kod, out = _pk(["--baslat", "Kurgu Dosya"], kok)
        assert kod == 0, out
    return kok


def _isle(kok, adim, parca, durum="UYGULANDI", kanit=UZUN_KANIT, ek=()):
    args = ["--isle", "--adim", str(adim), "--parca", parca, "--durum", durum]
    if durum in ("UYGULANDI", "ELDEN", "YUKLENEMEDI"):
        args += ["--kanit", kanit]
    elif durum == "GEREKSIZ":
        args += ["--gerekce", "kurgu gerekçe: bu adım bu dosyada kapsam dışı."]
    elif durum == "BILGI-EKSIK":
        args += ["--eksik", "kurgu eksik: müvekkilden belge bekleniyor."]
    return _pk(args + list(ek), kok)


def _olaylar(kok):
    yol = kok / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def _son_adim(kok, adim, parca):
    return [o for o in _olaylar(kok)
            if o.get("tip") == "adim" and str(o.get("adim")) == str(adim) and o.get("parca") == parca][-1]


def _yaz(kok, ad, veri):
    yol = kok / "_oa" / "cikti" / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")
    return yol


def _modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


def _teslim(kok):
    taslak = kok / "taslak.md"
    taslak.write_text(TASLAK, encoding="utf-8")
    return _calistir(TP, [taslak, "--tip", "genel", "--kok", kok, "--udf-yok"], kok)


def _makbuz(kok):
    """Bu koşunun makbuzu (yeşil ya da RED — hangisi yazıldıysa)."""
    defter = kok / "_oa" / "defter"
    adaylar = [defter / "teslim-makbuz.json", defter / "teslim-makbuz-RED.json"]
    var = [y for y in adaylar if y.is_file()]
    assert var, "makbuz yazılmamış"
    return json.loads(max(var, key=lambda y: y.stat().st_mtime_ns).read_text(encoding="utf-8"))


def _c2_kaydi(makbuz):
    kayit = [k for k in makbuz["kapilar"] if k["ad"].startswith("(c2)")]
    assert len(kayit) == 1, makbuz["kapilar"]
    return kayit[0]


def _iskelet(betik):
    """Motorun kendi şablonu (STDOUT yalnız JSON taşır — B-26)."""
    cp = subprocess.run([sys.executable, str(betik), "--iskelet"], capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout)


def _antitez_dolu():
    m = _iskelet(ANTITEZ)
    m["tez"] = "Kurgu tez: alacak sözleşmeden doğmuştur."
    for c in m["cepheler"]:
        c.update({"antitez": "değerlendirildi: saldırı zayıf", "guc": "dusuk",
                  "curutme": "sözleşme metni", "curutme_dayanak": "",
                  "dayanak_durum": "yok", "artik_risk": ""})
    return m


# ═══════════════════ (a) C5 — DAMGA KAPISI ═════════════════════════════════

def test_c5_motor_parcasi_damgasiz_md_kanitla_ELDEN_duser(tmp_path):
    """Saha deliği: modelin kendi yazdığı .md, `_oa/` yolu taşıdığı için C5'i
    susturuyordu. Betik adını anmak da motorun koştuğunu kanıtlamaz."""
    kok = _kok(tmp_path)
    (kok / "_oa" / "cikti" / "04-vakia.md").write_text("Olgu matrisi " * 20, encoding="utf-8")
    kod, out = _isle(kok, 4, "oa-vakia",
                     kanit="vakia_matris.py koştu, çıktı _oa/cikti/04-vakia.md dosyasında")
    assert kod == 0, out
    assert _son_adim(kok, 4, "oa-vakia")["durum"] == "ELDEN", out
    assert "arac=vakia_matris" in out and "motor_koprusu.py" in out, out


def test_c5_damgali_taze_json_varken_UYGULANDI_kanitta_yol_sart_degil(tmp_path):
    """Motor parçasında kanıtın kendisi DİSKTİR: damga varsa kanıt metninde
    `_oa/` yolu aranmaz."""
    kok = _kok(tmp_path)
    omd.damga_yaz(kok, "vakia_matris")
    kod, out = _isle(kok, 4, "oa-vakia")
    assert kod == 0, out
    assert _son_adim(kok, 4, "oa-vakia")["durum"] == "UYGULANDI", out


def test_c5_cokmus_denetim_damgasi_ELDEN(tmp_path):
    kok = _kok(tmp_path)
    yol = omd.damga_yaz(kok, "vakia_matris", denetim_coktu=True)
    kod, out = _isle(kok, 4, "oa-vakia", kanit=UZUN_KANIT + " " + str(yol))
    assert kod == 0, out
    assert _son_adim(kok, 4, "oa-vakia")["durum"] == "ELDEN", out
    assert "ÇÖKTÜ" in out, out


def test_c5_bayat_damga_ELDEN(tmp_path):
    """Motor koştu, sonra girdi değişti: damga artık o girdinin denetimi DEĞİLDİR
    (tazelik_denetim'in S1 kaynak beyanı hükmü — ikinci kural icat edilmez)."""
    kok = _kok(tmp_path)
    girdi = _yaz(kok, "04-vakia.json", VAKIA_GIRDI)
    cikti = kok / "_oa" / "cikti" / "04-vakia-denetim.json"
    kod, out = _calistir(VAKIA, ["--dogrula", girdi, "--json", cikti], kok)
    assert kod == 0 and cikti.is_file(), out
    degisen = dict(VAKIA_GIRDI, iddialar=VAKIA_GIRDI["iddialar"] + [{"id": "iddia-2", "metin": "Ek iddia"}])
    _yaz(kok, "04-vakia.json", degisen)
    kod, out = _isle(kok, 4, "oa-vakia", kanit=UZUN_KANIT + " _oa/cikti/04-vakia-denetim.json")
    assert kod == 0, out
    assert _son_adim(kok, 4, "oa-vakia")["durum"] == "ELDEN", out
    assert "BAYAT" in out, out


def test_c5_motor_disi_parca_eski_yol_kuralini_korur(tmp_path):
    """Kapsam yalnız dört motor parçasıdır; oa-sure gibi parçalarda C5'in yol kuralı aynen sürer."""
    kok = _kok(tmp_path)
    (kok / "_oa" / "cikti" / "sure.json").write_text("{}", encoding="utf-8")
    kod, out = _isle(kok, 1, "oa-sure", kanit=UZUN_KANIT + " _oa/cikti/sure.json")
    assert kod == 0, out
    assert _son_adim(kok, 1, "oa-sure")["durum"] == "UYGULANDI", out


# ═══════════════════ (b) ADIM-8 — HALÜSİNASYON KAPISI ══════════════════════

def test_adim8_damgasiz_RET_eksik_motorlari_ve_kopru_komutunu_soyler(tmp_path):
    kok = _kok(tmp_path)
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    kod, out = _isle(kok, 8, "oa-dilekce")
    assert kod != 0, out
    assert "HALÜSİNASYON KAPISI" in out, out
    for damga in omd.DAMGALAR:
        assert damga in out, (damga, out)
    assert "motor_koprusu.py" in out and "--serh-kapi halusinasyon" in out, out
    assert not [o for o in _olaylar(kok) if str(o.get("adim")) == "8"], "RET olay yazmamalı"


def test_adim8_dort_damga_varken_gecer(tmp_path):
    kok = _kok(tmp_path)
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    omd.dort_damga(kok)
    kod, out = _isle(kok, 8, "oa-dilekce")
    assert kod == 0, out
    assert _son_adim(kok, 8, "oa-dilekce")["durum"] == "UYGULANDI"


def test_adim8_tek_eksik_motor_yalniz_o_anilir(tmp_path):
    kok = _kok(tmp_path)
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    omd.dort_damga(kok, haric=("antitez_matris",))
    kod, out = _isle(kok, 8, "oa-dilekce")
    assert kod != 0, out
    assert "antitez_matris" in out, out
    for damga in ("vakia_matris", "grafik_denetim", "kiyas_denetim"):
        assert damga + " (" not in out, (damga, out)


def test_adim8_serh_halusinasyon_ile_gecer_ve_olayda_gorunur(tmp_path):
    kok = _kok(tmp_path)
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    kod, out = _isle(kok, 8, "oa-dilekce", ek=("--serh", SERH, "--serh-kapi", "halusinasyon"))
    assert kod == 0, out
    olay = _son_adim(kok, 8, "oa-dilekce")
    assert olay["serh"] is True and olay["serh_kapi"] == "halusinasyon"
    assert "HALÜSİNASYON KAPISI" in olay["serh_metni"]
    # "gerekçeli şerh"in GEREKÇESİ de kayda girer (eskiden yalnız kapı mesajı yazılıyordu)
    assert olay["serh_gerekce"] == SERH
    assert "ŞERHLİ" in out, out


def test_adim8_baska_kapiya_verilen_serh_halusinasyon_kapisini_gecemez(tmp_path):
    kok = _kok(tmp_path)
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    kod, out = _isle(kok, 8, "oa-dilekce", ek=("--serh", SERH, "--serh-kapi", "graf"))
    assert kod != 0, out
    assert "HALÜSİNASYON KAPISI" in out and "halusinasyon" in out, out


def test_serh_kapilari_halusinasyonu_tanir():
    pk = _modul(PK, "_v0518_halusinasyon_pk_serh")
    assert "halusinasyon" in pk.SERH_KAPILARI
    assert pk.SERH_KAPILARI[-1] == "tumu", "ipucu satırı son öğeyi 'tumu' sayar"


# ═══════════════════ (c) TESLİM (c2) KAPISI ═════════════════════════════════

def test_teslim_BILGI_EKSIK_statusu_halusinasyon_kapisini_gecemez(tmp_path):
    """Saha deseni (5 kez): motor parçaları BILGI-EKSIK yazılıp geçildi; (d) yalnız
    statünün varlığına baktığı için açıktı. (c2) diske bakar."""
    kok = _kok(tmp_path)
    for adim, parca in ((1, "oa-illiyet"), (4, "oa-vakia"), (5, "oa-kiyas"), (6, "oa-antitez")):
        assert _isle(kok, adim, parca, durum="BILGI-EKSIK")[0] == 0
    kod, out = _teslim(kok)
    assert kod != 0, out
    m = _makbuz(kok)
    assert _c2_kaydi(m)["durum"] == "BLOK", m["kapilar"]
    assert m["durdu"].startswith("(c2)"), m["durdu"]
    assert m["halusinasyon_kapisi"]["durum"] == "eksik"
    assert sorted(m["halusinasyon_kapisi"]["eksik"]) == sorted(omd.DAMGALAR)
    assert "motor_koprusu.py" in out, out


def test_teslim_dort_damga_varken_c2_acik(tmp_path):
    kok = _kok(tmp_path)
    omd.dort_damga(kok)
    _teslim(kok)
    m = _makbuz(kok)
    assert _c2_kaydi(m)["durum"] == "OK", m["kapilar"]
    assert m["halusinasyon_kapisi"]["durum"] == "tamam"
    assert m["halusinasyon_kapisi"]["eksik"] == []


def test_teslim_serhli_adim8_c2_gecer_ve_istisna_defterine_yazar(tmp_path):
    kok = _kok(tmp_path)
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    assert _isle(kok, 8, "oa-dilekce", ek=("--serh", SERH, "--serh-kapi", "halusinasyon"))[0] == 0
    kod, out = _teslim(kok)
    m = _makbuz(kok)
    assert _c2_kaydi(m)["durum"] == "OK", (m["kapilar"], out)
    assert m["halusinasyon_kapisi"]["durum"] == "serh"
    assert sorted(m["halusinasyon_kapisi"]["eksik"]) == sorted(omd.DAMGALAR)
    satirlar = (kok / "_oa" / "defter" / "istisna-kayitlari.jsonl").read_text(encoding="utf-8")
    kayit = [json.loads(s) for s in satirlar.splitlines() if s.strip()]
    hk = [k for k in kayit if k.get("tur") == "halusinasyon-kapisi"]
    assert hk and hk[-1]["onay"] == "avukat-serhi", kayit
    assert SERH in hk[-1]["gerekce"], hk[-1]
    assert m["halusinasyon_kapisi"]["serh_gerekce"] == SERH
    assert "ŞERH" in out, out


def test_teslim_defter_yokken_c2_BILGI_ve_gorunur(tmp_path):
    kok = _kok(tmp_path, defter=False)
    kod, out = _teslim(kok)
    m = _makbuz(kok)
    assert _c2_kaydi(m)["durum"] == "BILGI", m["kapilar"]
    assert m["halusinasyon_kapisi"]["durum"] == "defter-yok"
    assert "halüsinasyon" in out.lower(), out


# ═══════════════════ (d) MOTOR KÖPRÜSÜ ═════════════════════════════════════

def _damgali_dosyalar(kok):
    sonuc = {}
    for yol in sorted((kok / "_oa" / "cikti").glob("*.json")):
        try:
            veri = json.loads(yol.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(veri, dict) and veri.get("arac"):
            sonuc[yol.name] = veri["arac"]
    return sonuc


def test_kopru_girdi_yokken_exit2_damga_uretmez_ve_yol_gosterir(tmp_path):
    kok = _kok(tmp_path)
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 2, out
    assert _damgali_dosyalar(kok) == {}, "köprü damga üretmemeli"
    for ad in ("01-illiyet-graf.json", "04-vakia.json", "05-kiyas.json", "06-antitez-matris.json"):
        assert ad in out, (ad, out)
    assert "--iskelet" in out, out


def test_kopru_dort_motoru_kosturur_damgayi_motor_yazar(tmp_path):
    kok = _kok(tmp_path)
    _yaz(kok, "01-illiyet-graf.json", GRAF)
    _yaz(kok, "04-vakia.json", VAKIA_GIRDI)
    _yaz(kok, "05-kiyas.json", KIYAS_GIRDI)
    _yaz(kok, "06-antitez-matris.json", _antitez_dolu())
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 0, out
    damgali = _damgali_dosyalar(kok)
    for ad, damga in (("01-illiyet-denetim.json", "grafik_denetim"),
                      ("04-vakia-denetim.json", "vakia_matris"),
                      ("05-kiyas-denetim.json", "kiyas_denetim"),
                      ("06-antitez-denetim.json", "antitez_matris"),
                      ("capraz-denetim.json", "capraz_denetim")):
        assert damgali.get(ad) == damga, (ad, damgali, out)
    # zincir artık açık: dilekçe adımı damgalarla geçer
    assert _isle(kok, 5, "oa-kiyas", durum="GEREKSIZ")[0] == 0
    kod, out = _isle(kok, 8, "oa-dilekce")
    assert kod == 0, out


def test_kopru_eksik_sablonu_motorun_kendi_iskeletiyle_utf8_yazar(tmp_path):
    """Windows PowerShell 5.1'de `--iskelet > dosya` UTF-16 yazar ve motor okuyamaz;
    köprü şablonu motorun KENDİ çıktısıyla, UTF-8, damgasız yazar. İkinci koşu
    doldurulmamış şablonu doğrulatmaz."""
    kok = _kok(tmp_path)
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 2, out
    for ad, betik in (("04-vakia.json", VAKIA), ("06-antitez-matris.json", ANTITEZ)):
        yol = kok / "_oa" / "cikti" / ad
        veri = json.loads(yol.read_bytes().decode("utf-8"))
        assert veri == _iskelet(betik), ad
        assert "arac" not in veri, ad
    assert not (kok / "_oa" / "cikti" / "01-illiyet-graf.json").exists(), "graf şablonu icat edilmez"
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 2 and out.count("doldurulmamış") == 2, out
    assert _damgali_dosyalar(kok) == {}, out


def test_kopru_var_olan_dosyanin_uzerine_sablon_yazmaz(tmp_path):
    kok = _kok(tmp_path)
    yol = _yaz(kok, "04-vakia.json", {"arac": "vakia_matris", "not": "eski denetim çıktısı"})
    once = yol.read_bytes()
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 2, out
    assert yol.read_bytes() == once, "var olan dosyaya dokunulmamalı"
    assert "damgalı bir denetim ÇIKTISI" in out, out


def test_kopru_tek_girdide_capraz_kosmaz(tmp_path):
    """Tek dosyalı çapraz denetim 'tutarlı' der ama hiçbir şeyi kıyaslamamıştır."""
    kok = _kok(tmp_path)
    _yaz(kok, "04-vakia.json", VAKIA_GIRDI)
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 2, out
    assert (kok / "_oa" / "cikti" / "04-vakia-denetim.json").is_file(), out
    assert not (kok / "_oa" / "cikti" / "capraz-denetim.json").exists(), out
    assert "en az iki motor girdisi" in out, out


def test_kopru_doldurulmamis_iskeleti_dogrulatmaz(tmp_path):
    kok = _kok(tmp_path)
    _yaz(kok, "04-vakia.json", _iskelet(VAKIA))
    kod, out = _calistir(KOPRU, ["--kok", kok], kok)
    assert kod == 2, out
    assert not (kok / "_oa" / "cikti" / "04-vakia-denetim.json").exists(), out
    assert "doldurulmamış" in out, out


def test_kopru_duz_kit_duzeninde_motoru_kendi_dizininde_bulur(tmp_path):
    """Saha gerçeği: model araç çantasını `_oa/araclar/`a DÜZ kopyalar
    (alt dizinsiz). Köprü motoru önce eklenti düzeninde, yoksa kendi dizininde arar."""
    kit = tmp_path / "dava" / "_oa" / "araclar"
    kit.mkdir(parents=True)
    shutil.copy2(KOPRU, kit / "motor_koprusu.py")
    (kit / "vakia_matris.py").write_text("# kurgu\n", encoding="utf-8")
    mod = _modul(kit / "motor_koprusu.py", "_v0518_halusinasyon_kopru_duz")
    assert pathlib.Path(mod.motor_betigi("oa-vakia", "vakia_matris.py")) == kit / "vakia_matris.py"
    assert mod.motor_betigi("oa-kiyas", "kiyas_denetim.py") is None


def test_kopru_komutu_var_olan_betigi_gosterir(tmp_path):
    pk = _modul(PK, "_v0518_halusinasyon_pk_kopru")
    komut = pk._kopru_komutu(str(tmp_path))
    assert str(KOPRU) in komut and str(tmp_path) in komut, komut
    assert KOPRU.is_file()


# ═══════════════════ kilit ═════════════════════════════════════════════════

def test_motor_damga_fikstur_listesi_uretimle_ayni():
    pk = _modul(PK, "_v0518_halusinasyon_pk_kilit")
    assert tuple(sorted(set(pk._MOTOR_DAMGALARI.values()))) == omd.DAMGALAR
    assert set(pk._MOTOR_DAMGALARI) == {"oa-illiyet", "oa-vakia", "oa-kiyas", "oa-antitez"}
