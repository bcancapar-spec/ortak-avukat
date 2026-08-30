# -*- coding: utf-8 -*-
"""v0.5.14 — USUL + NÖBET paketi (denetim bulguları B-9 ve B-17).

B-9  `usul_matris.py` `son_gun`'e körlemesine güveniyordu: şablonda DURAN
     `sure_kurali` / `yargi_kolu` alanları HİÇ okunmadığı hâlde "kesin dil"
     izni veriliyordu. Yeni [G9] kapısı bu alanların DOLU ve TUTARLI olduğunu
     denetler. Script hukuki NİTELENDİRME YAPMAZ: hangi kuralın uygulanacağına
     karar vermez, yalnız "kural adı ile beyan edilen yargı kolu birbirini
     yalanlıyor mu" bakar (kapalı önek konvansiyonu; tanınmayan önek
     "bilinmiyor" sayılır ve boşluk üretmez).

B-17 Süre nöbet defterinde düzeltme/silme yolu yoktu; yanlış tebliğ tarihi
     düzeltilince eski HAYALET süre defterde kalıyor ve gerçek alarmlarla eşit
     ağırlıkta [!!!] ile listeleniyordu. Çözüm APPEND-ONLY ilkesini korur:
     silme YOK — deftere bir 'iptal/düzeltildi' KAYDI eklenir, nöbetçi
     kapatılan kaydı saymaz. `GEÇMİŞ` alt dizesi ve exit-3 sözleşmesi AYNEN
     korunur (çelişki de aynı DİKKAT sınıfında exit 3 verir).

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; repo dosyalarına
dokunulmaz. Nöbetçi BUGÜNÜ `date.today()` ile okuduğu için tarihler göreli
üretilir (kırılgan sabit takvim yok).
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
USUL = SKILLS / "oa-usul" / "scripts" / "usul_matris.py"
NOBETCI = SKILLS / "oa-sure" / "scripts" / "sure_nobetci.py"

KIMLIK_RE = re.compile(r"#([0-9a-f]{8})")


# ════════════════════════════════════════════════════════════════════════════
#  B-9 — usul_matris [G9]: sure_kurali / yargi_kolu tutarlılık kapısı
# ════════════════════════════════════════════════════════════════════════════

def _usul_cli(*args):
    return subprocess.run(
        [sys.executable, str(USUL), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def _usul_denetle(islemler, **ust):
    kok = pathlib.Path(tempfile.mkdtemp())
    yol = kok / "dosya_usul.json"
    veri = {"dosya": "Test 2026/999", "islemler": islemler}
    veri.update(ust)
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    cp = _usul_cli("--girdi", str(yol))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _karsi_kesin(**ek):
    """Karşı taraf +5 gün kaçırmış, kesin dil TALEP EDİLMİŞ taban işlem.
    G2/G4 boşlukları doğmasın diye sonuç+kapı+belgeli tebliğ verilir; böylece
    testte YALNIZ [G9] izole edilir."""
    i = {"id": "I1", "taraf": "karsi", "islem": "istinaf",
         "teblig": "2026-04-01", "teblig_belgeli": True,
         "son_gun": "2026-04-15", "fiili_tarih": "2026-04-20",
         "sonuc_norm": "HMK m.346 — süreden ret", "sonuc_ictihat_teyit": True,
         "kapi_kapatma": [{"kapi": "K-1", "kapatma": "mazeret yok"}],
         "kesin_dil": True}
    i.update(ek)
    return i


def test_g9_kesin_dil_sure_kurali_yoksa_bosluk_exit1():
    """B-9 çekirdeği: son_gun'ün hangi kurala dayandığı yazılmadan kesin dil
    izni verilemez — halüsine bir son gün aksi hâlde onaylanmış olur."""
    kod, cikti = _usul_denetle([_karsi_kesin()], yargi_kolu="hukuk")
    assert kod == 1
    assert "TESLİM EDİLEMEZ" in cikti
    assert "[G9] I1" in cikti
    assert "sure_kurali" in cikti


def test_g9_kesin_dil_yargi_kolu_yoksa_bosluk_exit1():
    kod, cikti = _usul_denetle([_karsi_kesin(sure_kurali="hmk_istinaf")])
    assert kod == 1
    assert "[G9] I1" in cikti
    assert "yargi_kolu" in cikti


def test_g9_kural_oneki_yargi_koluyla_celisirse_bosluk_exit1():
    """cmk_* kuralı 'hukuk' kolunda beyan edilmiş — gerçek çelişki.
    Script hangisinin doğru olduğunu SÖYLEMEZ, yalnız çelişkiyi açar."""
    kod, cikti = _usul_denetle(
        [_karsi_kesin(sure_kurali="cmk_istinaf")], yargi_kolu="hukuk")
    assert kod == 1
    assert "[G9] I1" in cikti
    assert "cmk_istinaf" in cikti
    assert "hukuk" in cikti
    assert "nitelendirme yapmaz" in cikti


def test_g9_tutarli_kural_ve_kol_ile_kesin_dil_gecer_exit0():
    kod, cikti = _usul_denetle(
        [_karsi_kesin(sure_kurali="hmk_istinaf")], yargi_kolu="hukuk")
    assert kod == 0, f"tutarlı kural/kol ile temiz beklenir; çıktı:\n{cikti}"
    assert "[G9]" not in cikti
    assert "✓ Boşluk yok" in cikti


def test_g9_islem_duzeyi_yargi_kolu_ust_duzeyi_ezer():
    """İşlem kendi `yargi_kolu`'nu taşıyorsa üst düzey değer değil o geçerlidir
    (aynı dosyada karma kollu işlem — ör. ceza + hukuk — mümkündür)."""
    kod, cikti = _usul_denetle(
        [_karsi_kesin(sure_kurali="cmk_istinaf", yargi_kolu="ceza")],
        yargi_kolu="hukuk")
    assert kod == 0, f"işlem düzeyi kol geçerli olmalı; çıktı:\n{cikti}"
    assert "[G9]" not in cikti


def test_g9_celiskili_alanlar_kesin_dil_olmadan_da_bosluk_uretir():
    """Çelişki GERÇEK bir çelişkidir: kesin dil talep edilmese de raporlanır
    (bu dal eski dosyaları düşürmez — çelişki ancak İKİ alan da doluysa doğar)."""
    kod, cikti = _usul_denetle(
        [_karsi_kesin(sure_kurali="iyuk_istinaf", kesin_dil=False)],
        yargi_kolu="hukuk")
    assert kod == 1
    assert "[G9] I1" in cikti
    assert "iyuk_istinaf" in cikti


def test_g9_taninmayan_kural_oneki_nitelendirilmez_bosluk_uretmez():
    """'model kurar, script denetler' kilidi: kapalı önek tablosunda olmayan
    bir kural adı NİTELENDİRİLMEZ — çelişki iddia edilmez, yalnız bilgi satırı."""
    kod, cikti = _usul_denetle(
        [_karsi_kesin(sure_kurali="ozel_kanun_x")], yargi_kolu="hukuk")
    assert kod == 0, f"tanınmayan önek boşluk üretmemeli; çıktı:\n{cikti}"
    assert "bilinmiyor" in cikti


def test_g9_aym_bireysel_kurali_kol_bagimsizdir():
    """AYM bireysel başvuru bir yargı KOLU değildir — hiçbir kolla çelişmez."""
    for kol in ("hukuk", "ceza", "idari"):
        kod, cikti = _usul_denetle(
            [_karsi_kesin(sure_kurali="aym_bireysel")], yargi_kolu=kol)
        assert kod == 0, f"aym_* kol-bağımsız olmalı ({kol}); çıktı:\n{cikti}"
        assert "[G9]" not in cikti


def test_g9_taninmayan_kol_degeri_nitelendirilmez():
    """Kapalı küme dışı yargı kolu değeri de nitelendirilmez (aynı ilke)."""
    kod, cikti = _usul_denetle(
        [_karsi_kesin(sure_kurali="hmk_istinaf")], yargi_kolu="deniz hukuku")
    assert kod == 0, f"tanınmayan kol değeri boşluk üretmemeli; çıktı:\n{cikti}"
    assert "bilinmiyor" in cikti


def test_g9_eski_dosya_alansiz_kesin_dilsiz_calisir_exit0():
    """Geriye uyum kilidi (CLAUDE.md kuralı 9): alanları HİÇ taşımayan eski
    artefakt kapıda DÜŞMEZ — [G9] yalnız kesin dil talebinde ya da fiilî
    çelişkide ateşler."""
    kod, cikti = _usul_denetle([{
        "id": "I9", "taraf": "karsi", "islem": "istinaf",
        "teblig": "2026-04-01", "teblig_belgeli": True,
        "son_gun": "2026-04-15", "fiili_tarih": "2026-04-10",
    }])
    assert kod == 0, f"eski şemalı artefakt temiz kalmalı; çıktı:\n{cikti}"
    assert "[G9]" not in cikti


def test_g9_ornek_sablon_hala_temiz_gecer_exit0():
    """Regresyon: --ornek şablonu [G9] eklendikten sonra da kendi denetiminden
    temiz geçmeli (şablon zaten sure_kurali + yargi_kolu taşır)."""
    ornek = _usul_cli("--ornek")
    assert ornek.returncode == 0
    kok = pathlib.Path(tempfile.mkdtemp())
    yol = kok / "ornek.json"
    yol.write_text(ornek.stdout, encoding="utf-8")
    cp = _usul_cli("--girdi", str(yol))
    cikti = (cp.stdout or "") + (cp.stderr or "")
    assert cp.returncode == 0, f"örnek şablon temiz geçmeli; çıktı:\n{cikti}"
    assert "✓ Boşluk yok" in cikti


# ════════════════════════════════════════════════════════════════════════════
#  B-17 — sure_nobetci: append-only düzeltme/iptal + çelişki uyarısı
# ════════════════════════════════════════════════════════════════════════════

def _nobet_cli(kok, *ek):
    cp = subprocess.run(
        [sys.executable, str(NOBETCI), "--kok", str(kok), *ek],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole_kok():
    return pathlib.Path(tempfile.mkdtemp())


def _defter_yaz(kok, kayitlar):
    oa = kok / "_oa"
    oa.mkdir(parents=True, exist_ok=True)
    (oa / "sureler.json").write_text(
        json.dumps(kayitlar, ensure_ascii=False), encoding="utf-8")


def _defter_oku(kok):
    return json.loads((kok / "_oa" / "sureler.json").read_text(encoding="utf-8"))


def _ileri(gun):
    return (date.today() + timedelta(days=gun)).isoformat()


def _kimlik(cikti, aciklama):
    """Verilen açıklamayı taşıyan satırın kayıt kimliğini çıkarır."""
    for satir in cikti.splitlines():
        if aciklama in satir:
            m = KIMLIK_RE.search(satir)
            if m:
                return m.group(1)
    raise AssertionError(f"'{aciklama}' satırında kimlik bulunamadı:\n{cikti}")


def test_her_sure_satiri_kayit_kimligi_tasir(izole_kok):
    """Düzeltme ancak adreslenebilir kayıtla mümkündür — nöbetçi her satırda
    deterministik bir kimlik basar."""
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(200), "aciklama": "Ileri sure", "tur": "maddi",
         "kural": "hmk_istinaf"},
    ])
    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 0
    assert KIMLIK_RE.search(cikti), f"kayıt kimliği basılmıyor:\n{cikti}"


def test_ayni_kural_iki_farkli_son_gun_celiski_uyarisi_exit3(izole_kok):
    """B-17'nin görünür yüzü: aynı kural için iki çelişik aktif son gün
    HAYALET süredir — nöbetçi artık sessiz kalmaz."""
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(150), "aciklama": "Yanlis teblig ile", "tur": "usul",
         "kural": "hmk_istinaf"},
        {"son_gun": _ileri(160), "aciklama": "Duzeltilmis teblig ile",
         "tur": "usul", "kural": "hmk_istinaf"},
    ])
    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 3, f"çelişkide DİKKAT/exit 3 beklenir; çıktı:\n{cikti}"
    assert "ÇELİŞKİ" in cikti
    assert "hmk_istinaf" in cikti
    assert "DİKKAT" in cikti


def test_uets_karine_cifti_celiski_sayilmaz(izole_kok):
    """Yanlış-pozitif kilidi: `hesapla_sure.py --uets` 7201 m.7/a karine
    senaryosunu BİLİNÇLİ olarak ayrı kayıt yazar (kayıpsızlık). Aynı kural
    altında iki son gün olması burada ÇELİŞKİ DEĞİLDİR — nöbetçi bu çifti
    çelişki taramasının dışında tutar ama listeden düşürmez."""
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(150), "aciklama": "istinaf son gunu", "tur": "usul",
         "kural": "iyuk_istinaf"},
        {"son_gun": _ileri(155),
         "aciklama": "istinaf son gunu [UETS karine: ulasma+5. gun]",
         "tur": "usul", "kural": "iyuk_istinaf"},
    ])
    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 0, f"UETS karine çifti çelişki sayılmamalı; çıktı:\n{cikti}"
    assert "ÇELİŞKİ" not in cikti
    assert "2 İLERİ" in cikti  # her iki kayıt da görünür kalır (kayıpsızlık)


def test_iptal_edilmis_kayit_sayilmaz_ve_ayri_listelenir(izole_kok):
    """Append-only düzeltme: iptal KAYDI eklenir, hayalet süre nöbetten düşer."""
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(150), "aciklama": "Yanlis teblig ile", "tur": "usul",
         "kural": "hmk_istinaf"},
        {"son_gun": _ileri(160), "aciklama": "Duzeltilmis teblig ile",
         "tur": "usul", "kural": "hmk_istinaf"},
    ])
    _, ilk = _nobet_cli(izole_kok)
    hayalet = _kimlik(ilk, "Yanlis teblig ile")

    kayitlar = _defter_oku(izole_kok)
    kayitlar.append({"iptal_eder": hayalet, "kayit_turu": "iptal",
                     "gerekce": "tebliğ tarihi yanlış girilmişti"})
    _defter_yaz(izole_kok, kayitlar)

    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 0, f"tek aktif ileri süre kaldı, exit 0 beklenir; çıktı:\n{cikti}"
    assert "ÇELİŞKİ" not in cikti
    assert "İPTAL" in cikti or "DÜZELTİLDİ" in cikti
    assert "Duzeltilmis teblig ile" in cikti
    # hayalet kayıt hâlâ görünür (denetim izi) ama SAYILMAZ
    assert "1 İLERİ" in cikti


def test_iptal_kaydinin_kendisi_bozuk_sayilmaz(izole_kok):
    """Saf düzeltme kaydının son_gun'ü yoktur — 'BOZUK/TARİHSİZ' listesine
    düşüp yanlış yere exit 3 tetiklememelidir."""
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(200), "aciklama": "Aktif sure", "tur": "usul",
         "kural": "hmk_temyiz"},
    ])
    _, ilk = _nobet_cli(izole_kok)
    hedef = _kimlik(ilk, "Aktif sure")
    kayitlar = _defter_oku(izole_kok)
    kayitlar.append({"iptal_eder": "ffffffff", "kayit_turu": "iptal",
                     "gerekce": "baska bir kaydi iptal eder"})
    _defter_yaz(izole_kok, kayitlar)

    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 0, f"düzeltme kaydı bozuk sayılmamalı; çıktı:\n{cikti}"
    assert "OKUNAMADI" not in cikti
    assert hedef  # kimlik üretimi çalışıyor


def test_kayit_ici_durum_alani_da_iptal_sayilir(izole_kok):
    """Elle düzeltilen ya da başka bir yazıcı tarafından işaretlenen kayıt:
    `durum: "duzeltildi"` / `iptal: true` de nöbetten düşürür."""
    _defter_yaz(izole_kok, [
        {"son_gun": (date.today() - timedelta(days=5)).isoformat(),
         "aciklama": "Hayalet gecmis sure", "tur": "usul",
         "kural": "hmk_istinaf", "durum": "duzeltildi"},
        {"son_gun": _ileri(200), "aciklama": "Dogru sure", "tur": "usul",
         "kural": "hmk_istinaf"},
    ])
    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 0, f"iptalli geçmiş süre exit 3 üretmemeli; çıktı:\n{cikti}"
    assert "0 GEÇMİŞ" in cikti
    assert "Hayalet gecmis sure" in cikti  # denetim izi korunur


def test_iptal_komutu_append_eder_hicbir_kaydi_silmez(izole_kok):
    """`--iptal <kimlik> --gerekce ...` APPEND-ONLY'dir: defterdeki kayıt
    sayısı ARTAR, mevcut kayıtlar birebir korunur."""
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(150), "aciklama": "Yanlis kayit", "tur": "usul",
         "kural": "hmk_istinaf"},
        {"son_gun": _ileri(160), "aciklama": "Dogru kayit", "tur": "usul",
         "kural": "hmk_istinaf"},
    ])
    onceki = _defter_oku(izole_kok)
    _, ilk = _nobet_cli(izole_kok)
    hayalet = _kimlik(ilk, "Yanlis kayit")

    kod, cikti = _nobet_cli(izole_kok, "--iptal", hayalet,
                            "--gerekce", "tebliğ tarihi yanlış girilmişti")
    assert kod == 0, f"iptal komutu başarılı olmalı; çıktı:\n{cikti}"

    sonraki = _defter_oku(izole_kok)
    assert len(sonraki) == len(onceki) + 1, "append-only ihlali"
    for k in onceki:
        assert k in sonraki, f"mevcut kayıt korunmadı: {k}"

    kod2, cikti2 = _nobet_cli(izole_kok)
    assert kod2 == 0
    assert "ÇELİŞKİ" not in cikti2


def test_iptal_komutu_gerekcesiz_reddeder(izole_kok):
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(150), "aciklama": "Kayit", "tur": "usul"},
    ])
    _, ilk = _nobet_cli(izole_kok)
    kimlik = _kimlik(ilk, "Kayit")
    kod, cikti = _nobet_cli(izole_kok, "--iptal", kimlik)
    assert kod != 0
    assert "--gerekce" in cikti
    assert len(_defter_oku(izole_kok)) == 1, "reddedilen iptal deftere yazmamalı"


def test_iptal_komutu_bulunamayan_kimligi_sessizce_gecmez(izole_kok):
    _defter_yaz(izole_kok, [
        {"son_gun": _ileri(150), "aciklama": "Kayit", "tur": "usul"},
    ])
    kod, cikti = _nobet_cli(izole_kok, "--iptal", "deadbeef",
                            "--gerekce", "yanlış tebliğ tarihi düzeltildi")
    assert kod == 1
    assert "bulunamadı" in cikti
    assert len(_defter_oku(izole_kok)) == 1, "başarısız iptal deftere yazmamalı"


def test_gecmis_alt_dizesi_ve_exit3_sozlesmesi_korunur(izole_kok):
    """Sözleşme kilidi: 'GEÇMİŞ' alt dizesi ve exit 3 AYNEN korunur."""
    _defter_yaz(izole_kok, [
        {"son_gun": (date.today() - timedelta(days=3)).isoformat(),
         "aciklama": "Gercek gecmis sure", "tur": "usul"},
    ])
    kod, cikti = _nobet_cli(izole_kok)
    assert kod == 3
    assert "GEÇMİŞ" in cikti
    assert "1 GEÇMİŞ" in cikti
    assert "DİKKAT" in cikti
