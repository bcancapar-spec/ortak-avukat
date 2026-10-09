# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — DÖRT PARÇANIN DETERMİNİZM KİLİDİ: oa-vakia · oa-kiyas ·
oa-antitez · oa-illiyet.

NEDEN VAR: Avukatın (karar verici) talimatı: "hook yapısı semantica graf vb
kısımları tutarlı olmalı gerekirse test edilmeli özellikle oa-vakia, oa-kiyas,
oa-antitez, oa-illiyet deterministik yapıları korunarak geliştirilmeli".
Ortak Avukat'ın iş bölümü "model kurar, script denetler"dir: model matrisi,
grafı, kıyası yazar; bu sekiz script onu mekanik olarak denetler ve çıktıları
pipeline'a, DURUM.md'ye ve teslim kapılarına girdi olur. Bir kapı ancak
DETERMİNİSTİKSE güvenilirdir: aynı girdiye iki koşuda iki ayrı hüküm veren
denetim hangi koşunun "doğru" olduğunu söyleyemez, dilekçeye giren sıra
tesadüfe kalır ve iki oturumun çıktısı birbiriyle kıyaslanamaz.

NEYİ KİLİTLER: aşağıdaki sekiz scriptin her biri AYNI kurgu girdiyle iki kez
koşar — AYRI alt süreçte, AYRI tmp dizininde (farklı derinlik → farklı mutlak
yol), FARKLI `PYTHONHASHSEED` (0 / 12345) ve FARKLI `TZ` (UTC−11 / UTC+12)
ile. Çıkış kodu, stdout, stderr ve koşu dizinindeki HER dosya (üretilen JSON,
göç çıktısı dahil) BAYT BAYT aynı olmalıdır.
  oa-vakia   : vakia_matris.py · ozne_eslestirici.py · delil_plani.py · tanik_plani.py
  oa-kiyas   : kiyas_denetim.py
  oa-antitez : antitez_matris.py · zapt_denetim.py
  oa-illiyet : grafik_denetim.py (≤200 düğüm Johnson yolu + >200 geri-kenar yolu)

Her ortam farkı bir kırılma sınıfını yakalar:
  * hash tohumu → `set`/`frozenset` yineleme sırasının çıktıya sızması (ör.
    `sorted()`'ı düşürülmüş bir küme birleştirmesi, kümeyle yapılmış bir
    tekilleştirme, komşuluk KÜMESİ üzerinde dolaşan DFS'in keşif sırası);
  * ayrı dizin → mutlak yolun çıktıya sızması (ör. `girdi` alanına
    `os.path.abspath`);
  * ayrı TZ → yerel saat damgası. Kod tabanının yerleşik damga deyimi
    `datetime.now().isoformat(timespec="seconds")` yerel saattir ve saniye
    çözünürlüklüdür: iki koşu aynı saniyeye düşerse fark görünmez, test ARA
    SIRA kırmızı yanardı. 23 saatlik TZ farkı yerel damgayı her koşuda farklı
    kılar → sızıntı DETERMİNİSTİK olarak kırmızı yakar (ölçüldü: rapora
    saniye/dakika damgası ekleyen bozulma aynı TZ ile 10 denemenin 10'unda
    YAKALANMADI, farklı TZ ile her denemede yakalandı);
  * ayrı süreç → aynı süreçteki önbellek/global durumun iki koşuyu
    yapay olarak eşitlemesi engellenir.

NORMALİZASYON: YOK. Çıktıdaki yol taşıyan alanlar (`girdi`, "[JSON] …
yazildi: <yol>" satırı, grafik_denetim `--kok` notu, `--goc` özeti) komut
satırında verilen yolun AYNEN yankısıdır; testler göreli yol + `cwd` ile
koştuğundan iki dizinde bayt-özdeş kalır. Zaman damgası ya da makineye özgü
değer bugün hiçbir çıktıda YOK. Eklenirse bu dosya kırmızı yanar; o gün damga
belgelenir ve YALNIZ o alan, gerekçesi yorumda yazılarak burada normalize
edilir (değişiklik keşif değil KARAR olur).

FİKSTÜR SÖZLEŞMESİ: her testin sonundaki birkaç assert determinizmi değil,
fikstürün kümeye/sıraya duyarlı kod yolunu GERÇEKTEN çalıştırdığını doğrular
(ör. üç türlü özne bileşeni, köprüler arasında DFS kökü, iç içe çevrimler).
İki koşu aynı girdi hatasıyla aynı biçimde düşseydi "bayt-özdeş" boş bir
zafer olurdu. Düzeneğin kendisi de denetlenir: ilk test iki ortamın küme
sırasını ve yerel saati GERÇEKTEN değiştirdiğini kanıtlar.

TOHUM GÜCÜ — ölçülmüş kural: sıraya duyarlı her listede EN AZ DÖRT öğe
bulunur. Sabit iki tohum her kümenin sırasını değiştirmez; rastgele dizgi
kümelerinde iki tohumun AYNI sırayı verme oranı ölçüldü (3.12 = 3.14):
k=2 öğede %49, k=3'te %16, k=4'te %3,5, k=5'te %1,3 (üç tohumla k=3 %3,5,
k=4 %0,3). Ölçüm mutasyon sınavında da görüldü: iki öğeli ("tanınmayan tür"
notları) ve üç öğeli (caizliksiz tanık notları) listeyi kümeye çeviren
bozulmalar YAKALANMADI, dört öğeyle yakalandı. Daha fazla güç gerekirse
KOSU_ORTAMLARI'na üçüncü bir ortam eklemek yeter (düzenek N koşuyu destekler).

Bu bir NİTELİK KİLİDİDİR: mevcut deterministik davranışı korur, bugün geçer.
Bütün veriler kurgudur (anayasa m.7); ağ yok, gerçek dava verisi yok; her şey
tmp_path'te üretilir, depoya yazılmaz.
"""
import difflib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
VAKIA_MATRIS = SKILLS / "oa-vakia" / "scripts" / "vakia_matris.py"
OZNE = SKILLS / "oa-vakia" / "scripts" / "ozne_eslestirici.py"
DELIL = SKILLS / "oa-vakia" / "scripts" / "delil_plani.py"
TANIK = SKILLS / "oa-vakia" / "scripts" / "tanik_plani.py"
KIYAS = SKILLS / "oa-kiyas" / "scripts" / "kiyas_denetim.py"
ANTITEZ = SKILLS / "oa-antitez" / "scripts" / "antitez_matris.py"
ZAPT = SKILLS / "oa-antitez" / "scripts" / "zapt_denetim.py"
GRAFIK = SKILLS / "oa-illiyet" / "scripts" / "grafik_denetim.py"

# Koşular arasında (cwd dışında) değişen YALNIZ bunlardır. TZ POSIX işaretiyle
# yazılır: "AAA+11" = UTC−11, "BBB-12" = UTC+12 (Windows CRT ve glibc aynı okur).
# Her koşu birinciyle karşılaştırılır; üçüncü bir ortam eklemek güç katar.
KOSU_ORTAMLARI = (
    {"PYTHONHASHSEED": "0", "TZ": "AAA+11"},
    {"PYTHONHASHSEED": "12345", "TZ": "BBB-12"},
)


# ═══════════════════════════ düzenek ═══════════════════════════════════════

def _modul(yol):
    """Script sabitini okumak için süreç içi yükleme (tests/README.md §1:
    dosyaya özgü benzersiz modül adı)."""
    spec = importlib.util.spec_from_file_location(f"determinizm_dort_parca_{yol.stem}", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ortam(fark):
    ortam = dict(os.environ)
    ortam.update(fark)
    return ortam


def _etiket(fark):
    return " ".join(f"{k}={v}" for k, v in sorted(fark.items()))


def _girdileri_yaz(dizin, girdiler):
    """Girdi: {göreli yol: dict|list|str|bytes}. JSON nesneleri tek biçimde
    serileştirilir — iki koşunun girdisi bayt düzeyinde aynıdır."""
    for goreli, icerik in girdiler.items():
        yol = dizin / goreli
        yol.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(icerik, (dict, list)):
            icerik = json.dumps(icerik, ensure_ascii=False, indent=2)
        if isinstance(icerik, str):
            icerik = icerik.encode("utf-8")
        yol.write_bytes(icerik)


def _komutlari_kos(dizin, komutlar, fark):
    kayit = []
    for script, argumanlar in komutlar:
        cp = subprocess.run([sys.executable, str(script), *argumanlar], cwd=str(dizin),
                            env=_ortam(fark), stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=120)
        kayit.append({"komut": " ".join([script.name, *argumanlar]), "cikis": cp.returncode,
                      "stdout": cp.stdout, "stderr": cp.stderr})
    return kayit


def _dizin_goruntusu(dizin):
    return {p.relative_to(dizin).as_posix(): p.read_bytes()
            for p in sorted(dizin.rglob("*")) if p.is_file()}


def _fark(a, b, etiket_a, etiket_b):
    """İlk farkın okunur özeti (teşhis için — karşılaştırma BAYT düzeyindedir)."""
    sa = a.decode("utf-8", "replace").splitlines()
    sb = b.decode("utf-8", "replace").splitlines()
    satirlar = list(difflib.unified_diff(sa, sb, etiket_a, etiket_b, lineterm="", n=1))
    return "\n".join(satirlar[:60]) or "(çözülmüş metin aynı — fark satır sonu/kodlama düzeyinde)"


def _iki_kosu(tmp_path, girdiler, komutlar):
    """Aynı girdiyi her KOSU_ORTAMLARI öğesi için AYRI dizinde (her koşu bir kat
    daha derinde → farklı mutlak yol) ve AYRI alt süreçlerde koşturur; her
    koşuyu birinciyle bayt bayt karşılaştırır. Döner: 1. koşunun (kayıt,
    dosyalar) çifti — fikstür sözleşmesi denetimi için."""
    sonuclar = []
    for n, fark in enumerate(KOSU_ORTAMLARI):
        dizin = tmp_path.joinpath(*(["ic"] * n), f"kosu-{n + 1}")
        dizin.mkdir(parents=True)
        _girdileri_yaz(dizin, girdiler)
        kayit = _komutlari_kos(dizin, komutlar, fark)
        for k in kayit:   # çöken koşu "bayt-özdeş" sayılmaz (boş zafer yasağı)
            assert b"Traceback" not in k["stderr"], (
                f"{k['komut']} [{_etiket(fark)}]: script ÇÖKTÜ — fikstür hiçbir şeyi denetlemiyor\n"
                + k["stderr"].decode("utf-8", "replace")[-1500:])
        sonuclar.append((fark, kayit, _dizin_goruntusu(dizin)))

    fark1, kayit1, dosya1 = sonuclar[0]
    for fark2, kayit2, dosya2 in sonuclar[1:]:
        e1, e2 = _etiket(fark1), _etiket(fark2)
        for a, b in zip(kayit1, kayit2):
            assert a["cikis"] == b["cikis"], (
                f"{a['komut']}: çıkış kodu koşudan koşuya değişti ({e1}: {a['cikis']} ≠ {e2}: {b['cikis']})")
            for akim in ("stdout", "stderr"):
                assert a[akim] == b[akim], (
                    f"{a['komut']}: {akim} koşular arasında BAYT-ÖZDEŞ DEĞİL — determinizm bozuk\n"
                    + _fark(a[akim], b[akim], e1, e2))
        assert sorted(dosya1) == sorted(dosya2), (
            f"koşu dizinlerindeki dosya KÜMESİ farklı — yalnız {e1}: {sorted(set(dosya1) - set(dosya2))}; "
            f"yalnız {e2}: {sorted(set(dosya2) - set(dosya1))}")
        for ad in sorted(dosya1):
            assert dosya1[ad] == dosya2[ad], (
                f"{ad}: dosya koşular arasında BAYT-ÖZDEŞ DEĞİL — determinizm bozuk\n"
                + _fark(dosya1[ad], dosya2[ad], e1, e2))
    return kayit1, dosya1


def test_duzenek_iki_kosu_ortami_kume_sirasini_ve_yerel_saati_gercekten_degistirir(tmp_path):
    """Denetçinin denetimi: aşağıdaki kilitlerin GÜCÜ koşu ortamlarının
    farkına dayanır. Ortam farkı alt sürece ulaşmazsa ya da tohumlar aynı küme
    sırasını üretirse kilitler sessizce dişsiz kalır ama YEŞİL görünür.

    KIRAN DEĞİŞİKLİK: `_ortam` ortam farkını alt sürece geçirmeyi bırakırsa;
    KOSU_ORTAMLARI özdeş tohumlara/TZ'lere indirilirse; yorumlayıcı karma
    algoritmasını değiştirip tohumlar bu kümelerde aynı sırayı üretmeye
    başlarsa (o gün tohumlar yeniden seçilir). Kümeler üretimdeki değerlerdir:
    özne türleri (ozne_eslestirici) ve kanonik `guc` kümesi (grafik_denetim)."""
    betik = ("import sys, time\n"
             "sys.stdout.write('|'.join({'gercek_kisi', 'tuzel_kisi', 'kamu'}) + '\\n')\n"
             "sys.stdout.write('|'.join({'dispozitif', 'guclu', 'zayif', 'tartismali'}) + '\\n')\n"
             "sys.stdout.write(time.strftime('%z') + '\\n')\n")
    goruntu = []
    for fark in KOSU_ORTAMLARI:
        cp = subprocess.run([sys.executable, "-c", betik], cwd=str(tmp_path), env=_ortam(fark),
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
        assert cp.returncode == 0, cp.stderr.decode("utf-8", "replace")
        goruntu.append(cp.stdout.decode("utf-8").splitlines())
    turler, gucler, utc = zip(*goruntu)
    assert len(KOSU_ORTAMLARI) >= 2
    assert len(set(turler)) > 1, f"tohumlar özne türü kümesini AYNI sırada dolaşıyor ({turler[0]}) — tohumları değiştir"
    assert len(set(gucler)) > 1, f"tohumlar kanonik guc kümesini AYNI sırada dolaşıyor ({gucler[0]}) — tohumları değiştir"
    assert len(set(utc)) == len(KOSU_ORTAMLARI), f"TZ alt sürece ulaşmıyor ya da TZ'ler çakışıyor ({utc})"


# ═══════════════════════════ oa-vakia ══════════════════════════════════════

VAKIA_GIRDI = {
    "taraflar": [
        {"ad": "Ahmet Yılmaz", "tur": "gercek_kisi"},
        "AHMET YILMAZ",
        {"ad": "Ahmet Yılmaz İnşaat Ltd. Şti.", "tur": "tuzel_kisi"},
        {"ad": "YILMAZ Ahmet", "tur": "kamu"},
        # aynı yazım iki ayrı türle → görünür "tür çelişkisi" notu
        {"ad": "Veli Kaya", "tur": "gercek_kisi"}, {"ad": "Veli Kaya", "tur": "tuzel_kisi"},
        {"ad": "Ayşe Demir", "tur": "gercek_kisi"}, {"ad": "Ayşe Demir", "tur": "kamu"},
        {"ad": "Can Ak", "tur": "tuzel_kisi"}, {"ad": "Can Ak", "tur": "kamu"},
        # usul rolü tür değildir → görünür "tanınmadı" notu (dört örnek)
        {"ad": "Gülşen Kaya", "tur": "davacı"}, {"ad": "Zeynep Ak", "tur": "davalı"},
        {"ad": "Selin Er", "tur": "müdahil"}, {"ad": "Kemal Öz", "tur": "vekil"},
        "Gülsen Kaya",
    ],
    "iddialar": [
        {"id": "I1", "metin": "Mal kurgu tarihte teslim edildi", "tur": "vakia"},
        {"id": "I2", "metin": "Davalı ayıbı süresinde bildirmedi", "tur": "vakia"},
        {"id": "I3", "metin": "Sözleşme eser sözleşmesidir", "tur": "hukuki"},
        {"id": "I4", "metin": "Bedel kurgu tarihte ödendi"},                    # tur yok → [BİLGİ]
        {"id": "I5", "metin": "Ayıp gizli ayıptır", "tur": "nitelendirme"},     # kapalı küme dışı
        {"id": "I6", "metin": "Ayıp ihbarı süresinde yapıldı"},                 # tur yok
        {"id": "I7", "metin": "Davalı tacirdir", "tur": ""},                    # boş tur
        {"id": "I10", "metin": "Davacı tüketicidir"},                           # tur yok, delilsiz
        "sözlük olmayan iddia kaydı",
    ],
    "olaylar": [
        # Tarihler bilerek KARIŞIK sırada; 2025-03-12'de ÜÇ olay: kronoloji sıralaması +
        # eşit anahtarda girdi sırasının korunması kilitlenir.
        {"tarih": "2025-04-01", "olgu": "Tanık T1 ayıbı gördü", "belge": "Tanık T1 beyanı (kurgu)",
         "destekler": ["I2"], "ispat_durumu": "tanik", "ozne": "YILMAZ Ahmet"},
        {"tarih": "2025-03-12", "olgu": "Teslim", "belge": "İrsaliye (kurgu)", "destekler": ["I1"],
         "ispat_durumu": "belgeli", "ozne": "Ahmet Yılmaz"},
        {"tarih": "2025-03-12", "olgu": "Fatura kesildi", "belge": "Fatura (kurgu)",
         "destekler": ["I1", "I9"], "ispat_durumu": "belgeli"},
        {"tarih": "2025-03-12", "olgu": "Sevk irsaliyesi düzenlendi", "belge": "Sevk irsaliyesi (kurgu)",
         "destekler": ["I1", "I8"], "ispat_durumu": "belgeli"},
        {"tarih": "2025-05-20", "olgu": "Ödeme karinesi", "belge": "", "destekler": ["I4"],
         "ispat_durumu": "karine"},
        {"tarih": "2025-06-01", "olgu": "Bilirkişi raporu", "belge": "Rapor (kurgu)", "destekler": ["I3"],
         "ispat_durumu": "bilirkisi"},
        # tarihsiz (dört biçim: boş, alan yok, bozuk, ISO dışı)
        {"tarih": "", "olgu": "Tarihsiz görüşme", "belge": "Görüşme notu (kurgu)", "destekler": ["I4"],
         "ispat_durumu": "beyan"},
        {"olgu": "Tarih alanı olmayan yazışma", "belge": "E-posta (kurgu)", "destekler": ["I7"],
         "ispat_durumu": "beyan"},
        {"tarih": "2025-13-45", "olgu": "Bozuk tarihli kayıt", "destekler": [], "ispat_durumu": "video"},
        {"tarih": "12.03.2025", "olgu": "Yerel biçimli tarihli kayıt", "belge": "Ek listesi (kurgu)",
         "destekler": ["I1", "I0"], "ispat_durumu": "belgeli"},
        # yetim / geçersiz ispat_durumu (dörder)
        {"tarih": "2025-07-01", "olgu": "Ses kaydı", "destekler": [], "ispat_durumu": "ses_kaydi"},
        {"tarih": "2025-07-02", "olgu": "Fotoğraf", "destekler": ["I7"], "ispat_durumu": "fotograf"},
        {"tarih": "2025-07-03", "olgu": "Kargo takip kaydı", "belge": "Kargo kaydı (kurgu)",
         "ispat_durumu": "belgeli"},
        {"tarih": "2025-07-04", "olgu": "Noter tespiti", "belge": "Tespit tutanağı (kurgu)", "destekler": [],
         "ispat_durumu": "noter"},
        # tanık caizliği: caiz değil · geçersiz etiket (dört) · etiketsiz (dört)
        {"tarih": "2025-04-02", "olgu": "Tanık T2 beyanı", "belge": "Tanık T2 (kurgu)", "destekler": ["I2"],
         "ispat_durumu": "tanik", "caizlik": "caiz_degil"},
        {"tarih": "2025-04-03", "olgu": "Tanık T3 beyanı", "belge": "Tanık T3 (kurgu)", "destekler": ["I4"],
         "ispat_durumu": "tanik", "caizlik": "belki"},
        {"tarih": "2025-04-04", "olgu": "Tanık T4 beyanı", "belge": "Tanık T4 (kurgu)", "destekler": ["I6"],
         "ispat_durumu": "tanik"},
        {"tarih": "2025-04-05", "olgu": "Tanık T5 beyanı", "belge": "Tanık T5 (kurgu)",
         "destekler": ["I6", "I7x"], "ispat_durumu": "tanik", "caizlik": "evet"},
        {"tarih": "2025-04-06", "olgu": "Tanık T6 beyanı", "belge": "Tanık T6 (kurgu)", "destekler": ["I2"],
         "ispat_durumu": "tanik", "caizlik": "kismen"},
        {"tarih": "2025-04-07", "olgu": "Tanık T7 beyanı", "belge": "", "destekler": ["I5"],
         "ispat_durumu": "tanik"},
        {"tarih": "2025-04-08", "olgu": "Tanık T8 beyanı", "belge": "Tanık T8 (kurgu)", "destekler": ["I4"],
         "ispat_durumu": "tanik", "caizlik": ""},
        {"tarih": "2025-04-09", "olgu": "Tanık T9 beyanı", "belge": "Tanık T9 (kurgu)", "destekler": ["I5"],
         "ispat_durumu": "tanik", "caizlik": "muhtemelen"},
        {"tarih": "2025-02-28", "olgu": "Sözleşme imzalandı", "belge": "Sözleşme (kurgu)",
         "destekler": ["I3", "I1"], "ispat_durumu": "ikrar", "ozne": "Gülsen Kaya"},
        7,
    ],
}


def test_vakia_matris_iskelet_ve_denetim_iki_kosuda_bayt_ozdes(tmp_path):
    """`--iskelet` (model bu şablonu doldurur) ve `--dogrula … --json`
    (kronoloji + iddia↔delil matrisi + özne varyant taraması) her koşuda aynı.

    KIRAN DEĞİŞİKLİK: kronolojide eşit tarihli olayların sırası kümeden ya da
    kararsız bir anahtardan gelirse; `_ozne_adlarini_topla`, tanınmayan-tür
    notları (`taninmayan`) ya da caizlik notları (`_caizsiz`) kümeyle
    tekilleştirilirse; tarihsiz / ispat boşluğu / yetim delil / geçersiz
    referans listesi kümeden kurulursa; JSON `girdi` alanına mutlak yol
    (`os.path.abspath`) ya da üretim zamanı yazılırsa."""
    kayit, dosyalar = _iki_kosu(tmp_path, {"vakia.json": VAKIA_GIRDI}, [
        (VAKIA_MATRIS, ["--iskelet"]),
        (VAKIA_MATRIS, ["--dogrula", "vakia.json", "--json", "sonuc.json"]),
    ])
    # fikstür sözleşmesi: sıralama, ÜÇ TÜRLÜ özne bileşeni ve ≥4 öğeli bulgu listeleri çalıştı
    assert [k["cikis"] for k in kayit] == [0, 0]
    sonuc = json.loads(dosyalar["sonuc.json"])
    assert len(sonuc["kronoloji"]) >= 5 and len(sonuc["ozne_eslestirme"]) >= 3
    assert any(b["kural"].endswith("+tur-belirsiz") for b in sonuc["ozne_eslestirme"])
    for alan in ("tarihsiz", "yetim_deliller", "gecersiz_referans", "gecersiz_ispat_durumu",
                 "ispat_bosluklari"):
        assert len(sonuc[alan]) >= 4, (alan, sonuc[alan])


OZNE_GIRDI = [
    {"id": "T1", "ad": "Ahmet Yılmaz", "tur": "gercek_kisi"},
    "AHMET YILMAZ",
    {"id": "S1", "ad": "Ahmet Yılmaz İnşaat Ltd. Şti.", "tur": "tuzel_kisi"},
    {"id": "K1", "ad": "YILMAZ Ahmet", "tur": "kamu"},
    "Mehmet Yılmaz", "YILMAZ Mehmet", "M. Yılmaz", "Mehmet Y.lmaz",
    "Ayşegül Kaya", "Ayşe Gül Kaya", "Serkan Yıldız", "Serhan Yıldız",
    {"ad": "Yılmaz İnşaat A.Ş.", "tur": "anonim şirket"}, "Yılmaz İnşaat Ltd. Şti.",
    {"ad": "Gülşen Kaya", "tur": "davacı"}, "Gülsen Kaya",
]


def test_ozne_eslestirici_cli_iki_kosuda_bayt_ozdes(tmp_path):
    """Özne varyant motoru (`--json` ve insan raporu) her koşuda aynı çift
    sırasını, aynı kararları ve aynı gerekçe/neden dizgilerini üretir.

    KIRAN DEĞİŞİKLİK: `_liste_denetimi`ndeki `"/".join(sorted(tset))`
    sıralaması düşerse (tür kümesi tohum sırasıyla yazılır); çift dolaşımı ya da
    BAGLA birleşim-bul kökü kümeden seçilirse; `eslestir` girdi sırasını
    korumayı bırakırsa."""
    kayit, _ = _iki_kosu(tmp_path, {"ozneler.json": OZNE_GIRDI}, [
        (OZNE, ["--girdi", "ozneler.json", "--json"]),
        (OZNE, ["--girdi", "ozneler.json"]),
    ])
    # fikstür sözleşmesi: tür koruması ÜÇ türlü bir bileşende ateşlendi (sıralanan küme ≥3 öğe)
    assert [k["cikis"] for k in kayit] == [0, 0]
    r = json.loads(kayit[0]["stdout"])
    nedenler = [n for e in r["eslesmeler"] for n in e["nedenler"]]
    assert any(n.startswith("tur_belirsiz=") and n.count("/") == 2 for n in nedenler), nedenler
    assert {e["karar"] for e in r["eslesmeler"]} == {"BAGLA", "AVUKATA-SOR"}


@pytest.fixture(scope="module")
def vakia_matrisi(tmp_path_factory):
    """delil_plani / tanik_plani girdisi GERÇEK vakia_matris çıktısıdır
    (tests/test_v0518_meslek_delil.py deseni). Bir kez üretilir ve iki koşuya
    AYNI baytlarla kopyalanır: koşular arasındaki fark yalnız denetlenen
    scriptten doğabilir."""
    dizin = tmp_path_factory.mktemp("vakia_matrisi")
    _girdileri_yaz(dizin, {"vakia.json": VAKIA_GIRDI})
    cp = subprocess.run([sys.executable, str(VAKIA_MATRIS), "--dogrula", "vakia.json",
                         "--json", "matris.json"], cwd=str(dizin), stdin=subprocess.DEVNULL,
                        capture_output=True, timeout=120)
    assert cp.returncode == 0, cp.stdout.decode("utf-8", "replace")[-1500:]
    bayt = (dizin / "matris.json").read_bytes()
    m = json.loads(bayt)
    # I2'yi plan kapsar; I4-I7 ve I10 tedariksiz kalır (≥4 öğe — sıraya duyarlı liste)
    assert {"I2", "I4", "I5", "I6", "I7", "I10"} <= set(m["ispat_bosluklari"]), (
        "fikstür sözleşmesi: I2, I4-I7 ve I10 ispat boşluğu olmalı", m["ispat_bosluklari"])
    return bayt


DELIL_PLANI = {"satirlar": [
    # kaybolabilir delil (dört satır)
    {"iddia_id": "I2", "hedef_delil": "Site güvenlik kamera kaydı (kurgu)", "kaynak": "Site yönetimi (kurgu)",
     "yontem": "Yazılı saklama talebi ve delil tespiti değerlendirmesi", "kim": "AVUKAT",
     "aciliyet": "KAYBOLUYOR", "son_gun": "2026-11-02", "dayanak": "HMK m.400", "durum": "PLANLANDI"},
    {"iddia_id": "I2", "hedef_delil": "Baz istasyonu kayıtları (kurgu)", "kaynak": "GSM işletmecisi (kurgu)",
     "yontem": "Müzekkere yazılması talebi", "kim": "MAHKEME", "aciliyet": "KAYBOLUYOR",
     "son_gun": "2026-11-05", "dayanak": "HMK m.400", "durum": "TALEP_EDILDI"},
    {"iddia_id": "I1", "hedef_delil": "Sunucu erişim kayıtları (kurgu)", "kaynak": "Barındırma firması (kurgu)",
     "yontem": "Yazılı saklama talebi", "kim": "KURUM", "aciliyet": "KAYBOLUYOR",
     "son_gun": "2026-11-09", "dayanak": "HMK m.400", "durum": "GELDI"},
    {"iddia_id": "I3", "hedef_delil": "Şantiye fotoğrafları (kurgu)", "kaynak": "Müvekkil",
     "yontem": "Orijinal dosyaların teslim alınması", "kim": "MUVEKKIL", "aciliyet": "KAYBOLUYOR",
     "son_gun": "2026-11-03", "dayanak": "HMK m.400", "durum": "PLANLANDI"},
    {"iddia_id": "I2", "hedef_delil": "Tanık T1 (kurgu)", "kaynak": "Müvekkil",
     "yontem": "Tanık listesine yazılması", "kim": "MUVEKKIL", "aciliyet": "SURELI",
     "son_gun": "BELIRLENEMEDI", "dayanak": "HMK m.240", "durum": "GELMEDI"},
    {"iddia_id": "I3", "hedef_delil": "Tanık T4 (kurgu)", "kaynak": "Müvekkil", "yontem": "Tanık dinletilmesi",
     "kim": "MAHKEME", "aciliyet": "NORMAL", "son_gun": "2026-12-01", "dayanak": "TEYIDE MUHTAC",
     "durum": "TALEP_EDILDI"},
    {"iddia_id": "I1", "hedef_delil": "Ödeme belgesi (kurgu)", "kaynak": "", "yontem": "", "kim": "KARSI_TARAF",
     "aciliyet": "NORMAL", "son_gun": "2026-12-15", "dayanak": "HMK m.190", "durum": "PLANLANDI"},
    {"iddia_id": "I9", "hedef_delil": "Sair deliller", "kaynak": "İlgili yerler", "yontem": "Bilahare bildirilecek",
     "kim": "BİZ", "aciliyet": "ACİL", "son_gun": "yarın", "dayanak": "", "durum": "BEKLIYOR"},
    "nesne olmayan satır",
]}


def test_delil_plani_iskelet_ve_denetim_iki_kosuda_bayt_ozdes(tmp_path, vakia_matrisi):
    """Delil tedarik planı: `--iskelet`, `--plan --json` ve insan raporu her
    koşuda aynı (tedariksiz boşluk, kaybolan delil, hata/uyarı/hatırlatma
    listelerinin SIRASI dahil).

    KIRAN DEĞİŞİKLİK: `tedariksiz` listesi `set(bosluklar) - kapsanan` gibi
    küme farkıyla kurulursa; hata/uyarı listeleri kümeyle tekilleştirilirse;
    hatırlatmaların sırası bir kümeden gelirse."""
    kayit, _ = _iki_kosu(tmp_path, {"matris.json": vakia_matrisi, "plan.json": DELIL_PLANI}, [
        (DELIL, ["--matris", "matris.json", "--iskelet"]),
        (DELIL, ["--matris", "matris.json", "--plan", "plan.json", "--json"]),
        (DELIL, ["--matris", "matris.json", "--plan", "plan.json"]),
    ])
    # fikstür sözleşmesi: iskelet geçerli; plan EKSİK (1); sıraya duyarlı listeler ≥4 öğe
    assert [k["cikis"] for k in kayit] == [0, 1, 1]
    r = json.loads(kayit[1]["stdout"])
    for alan in ("tedariksiz", "kaybolan", "hatalar", "uyarilar"):
        assert len(r[alan]) >= 4, (alan, r[alan])
    assert len(r["hatirlatmalar"]) >= 3   # kaybolan · avans · tanık hatırlatmalarının hepsi basıldı


TANIK_PLANI = {"rejim": "hmk", "taniklar": [
    {"tanik": "T1 (komşu — kurgu)", "yan": "biz", "listede": "evet", "dinleme": "istinabe",
     "sorular": [
         {"soru": "Teslim günü olay yerinde miydiniz?", "vakia_id": "I1", "ispat_yonu": "ispat",
          "risk": "dusuk"},
         {"soru": "Davalı size ayıptan şöyle söylemiş miydi?", "vakia_id": "I2", "ispat_yonu": "ispat",
          "risk": "orta"},
         {"soru": "Sözleşmenin niteliği nedir?", "vakia_id": "I3", "ispat_yonu": "ispat", "risk": "orta"},
     ]},
    {"tanik": "T2 (karşı tanık — kurgu)", "yan": "karsi", "listede": "hayir",
     "sorular": [{"soru": "Ödeme günü işyerinde miydiniz?", "vakia_id": "I4", "ispat_yonu": "curutme",
                  "risk": "yuksek"}]},
    {"tanik": "T3 (kurgu)", "yan": "biz", "listede": "bilinmiyor", "dinleme": "telefon",
     "ifade_taslagi": "kurgu metin",
     "sorular": [
         {"soru": "Mahkemede teslimi gördüğünüzü söyleyin.", "vakia_id": "I1", "ispat_yonu": "ispat",
          "risk": "dusuk", "beklenen_cevap": "Evet"},
         {"soru": "Genel olarak ne biliyorsunuz?", "vakia_id": "", "ispat_yonu": "genel", "risk": "belirsiz"},
         {"soru": "", "vakia_id": "I9", "ispat_yonu": "ispat", "risk": "dusuk"},
         "nesne olmayan soru",
     ]},
    {"tanik": "T4 (kurgu)", "yan": "biz", "listede": "evet", "sorular": []},
    7,
]}


def test_tanik_plani_denetimi_iki_kosuda_bayt_ozdes(tmp_path, vakia_matrisi):
    """Tanık soru planı denetimi (`--json` ve insan raporu) her koşuda aynı:
    soruyla kapsanan vakıalar, hata (tanık cevabı, vakıasız soru, enum) ve
    uyarı/bilgi listeleri aynı sırada.

    KIRAN DEĞİŞİKLİK: `kapsanan_vakialar` için `sorted(kapsanan)` yerine
    `list(kapsanan)` yazılırsa; `_cevap_alani` sıralamayı bırakıp bir kümeden
    dönerse; uyarı/bilgi listeleri kümeyle tekilleştirilirse."""
    kayit, _ = _iki_kosu(tmp_path, {"matris.json": vakia_matrisi, "soru.json": TANIK_PLANI}, [
        (TANIK, ["--matris", "matris.json", "--plan", "soru.json", "--json"]),
        (TANIK, ["--matris", "matris.json", "--plan", "soru.json"]),
    ])
    # fikstür sözleşmesi: plan GEÇERSİZ (1); kapsanan vakıa kümesi ≥4 öğe (sıralanan küme)
    assert [k["cikis"] for k in kayit] == [1, 1]
    r = json.loads(kayit[0]["stdout"])
    assert len(r["kapsanan_vakialar"]) >= 4 and len(r["hatalar"]) >= 4 and len(r["uyarilar"]) >= 4


# ═══════════════════════════ oa-kiyas ══════════════════════════════════════

KIYAS_GIRDI = {
    "buyuk_onerme": {"norm": "Eski tekil alan (kurgu) — liste varken yok sayılır"},
    "buyuk_onermeler": [
        {"norm": "TBK m.49 — haksız fiil (kurgu çıpa)", "zamanasimi": "2 yıl / 10 yıl",
         "kusur_sarti": "var", "ispat_kolayligi": "zor — kusur davacıda", "faiz": "olay tarihi"},
        {"norm": "TBK m.112 — sözleşmeye aykırılık (kurgu çıpa)", "secili": True,
         "secim_gerekcesi": "Uzun zamanaşımı ve kusur karinesi (kurgu gerekçe)",
         "zamanasimi": "10 yıl", "kusur_sarti": "karine", "ispat_kolayligi": "kolay", "faiz": "temerrüt",
         "ictihat": [
             {"kunye": "Yargıtay 3. HD 2099/1 E. 2099/2 K. (kurgu)", "dogrulama": "teyitli"},
             {"kunye": "Yargıtay HGK 2099/3 E. (kurgu)", "dogrulama": "beklemede"},
             {"dogrulama": "teyitsiz"},
             {"kunye": "BAM 1. HD 2099/4 E. (kurgu)"},
             {"kunye": "Yargıtay 11. HD 2099/5 E. (kurgu)", "dogrulama": "iddia"},
             "sözlük olmayan içtihat kaydı",
         ],
         "unsurlar": [
             {"id": "ihlal", "ad": "Sözleşmeye aykırılık"},
             {"id": "zarar", "ad": "Zarar"},
             {"id": "illiyet", "ad": "İlliyet bağı", "ispat_yuku": "karsi_taraf",
              "ispat_yuku_kaynak": "TBK m.112 kusur karinesi (kurgu)",
              "curutme_hazirligi": ["Kusursuzluk savunmasına karşı yazışmalar (kurgu)", "  "]},
             {"id": "ifa", "ad": "İfanın gerçekleşmediği", "ispat_yuku": "karsi_taraf",
              "ispat_yuku_kaynak": "TBK m.97 (kurgu çıpa)",
              "curutme_hazirligi": ["Teslim tutanağı (kurgu)", "Kargo kaydı (kurgu)", "Tanık listesi (kurgu)"]},
             {"id": "ayip", "ad": "Ayıbın bulunmadığı", "ispat_yuku": "karsi_taraf",
              "ispat_yuku_kaynak": "TBK m.223 (kurgu çıpa)", "curutme_hazirligi": ["Muayene raporu (kurgu)"]},
             {"id": "odeme", "ad": "Ödemenin yapıldığı", "ispat_yuku": "karsi_taraf",
              "ispat_yuku_kaynak": "TBK m.89 (kurgu çıpa)", "curutme_hazirligi": ["Banka hesap dökümü (kurgu)"]},
             {"id": "kusur", "ad": "Kusur", "ispat_yuku": "karsi_taraf"},
             {"id": "temerrut", "ad": "Temerrüt", "ispat_yuku": "belki"},
             "ihtar",
         ]},
        {"norm": "TBK m.77 — sebepsiz zenginleşme (kurgu çıpa)", "secili": True},
        "sözlük olmayan aday",
    ],
    "kucuk_onerme": {"vakialar": [
        {"metin": "Davalı teslimi geciktirdi (kurgu)", "karsilar": ["ihlal"],
         "dayanak_delil": ["sözleşme (kurgu)"]},
        {"metin": "Davacı kira ödedi (kurgu)", "karsilar": ["zarar"], "dayanak_delil": []},
        {"metin": "İhtarname gönderildi (kurgu)", "karsilar": ["ihtar"],
         "dayanak_delil": ["ihtarname (kurgu)"]},
        {"metin": "Davalının aracı kırmızıydı (kurgu)", "dayanak_delil": ["fotoğraf (kurgu)"]},
        {"metin": "Davalı başka şehre taşındı (kurgu)", "karsilar": [], "dayanak_delil": []},
        {"metin": "Davacı yeni araç aldı (kurgu)", "dayanak_delil": ["fatura (kurgu)"]},
        {"metin": "Tanımsız unsurlara bağlı vakıa (kurgu)",
         "karsilar": ["hayalet_unsur", "tanimsiz_unsur", "olmayan_unsur", "kayip_unsur"]},
        "sözlük olmayan vakıa",
    ]},
    "sonuc": "TBK m.112 uyarınca tazminat sorumluluğu doğar (kurgu).",
}


def test_kiyas_denetim_iki_kosuda_bayt_ozdes(tmp_path):
    """Silojizm denetimi (rapor + `--json`): yarışan normlar tablosu, teyitsiz
    içtihat, unsur↔vakıa eşleşmesi (ispat yükü carve-out dahil) ve yetim vakıa
    listeleri her koşuda aynı.

    KIRAN DEĞİŞİKLİK: tanımsız unsur referanslarının birleştirilmesi
    (`', '.join(... ks)`) kümeden yapılırsa; teyitsiz içtihat / yetim vakıa
    listesi kümeyle tekilleştirilirse; yarışan aday sırası ya da boş
    karşılaştırma alanları bir kümeden gelirse; `girdi` mutlak yola çevrilirse."""
    kayit, dosyalar = _iki_kosu(tmp_path, {"kiyas.json": KIYAS_GIRDI}, [
        (KIYAS, ["kiyas.json", "--json", "sonuc.json"]),
    ])
    # fikstür sözleşmesi: yarışma, carve-out ve tanımsız-unsur yetimi çalıştı; listeler ≥4 öğe
    assert [k["cikis"] for k in kayit] == [0]
    veri = json.loads(dosyalar["sonuc.json"])
    assert len(veri["buyuk_onerme"]["yarisan_normlar"]) >= 3 and len(veri["teyitsiz_ictihat"]) >= 4
    durumlar = [u["durum"] for u in veri["unsur_vakia_eslesme"]]
    assert durumlar.count("ispat_yuku_karsida") >= 4 and len(veri["yetim_vakialar"]) >= 4


# ═══════════════════════════ oa-antitez ════════════════════════════════════

ANTITEZ_MATRISI = {
    "tez": "Davalı kurgu sözleşmeden doğan bedeli ödemekle yükümlüdür",
    "cepheler": [
        # çürütülmüş ama dayanağı TEYİTSİZ (dört)
        {"cephe": "usul", "antitez": "Yetki itirazı", "guc": "dusuk", "curutme": "Yetki şartı var (kurgu)",
         "curutme_dayanak": "HMK m.17", "dayanak_durum": "teyitsiz", "duyulmus": True},
        {"cephe": "ispat_delil", "antitez": "Tanık caiz değil", "guc": "orta", "curutme": "Delil başlangıcı var",
         "curutme_dayanak": "Yargıtay kurgu karar A", "dayanak_durum": "teyitsiz"},
        {"cephe": "zamanasimi", "antitez": "Talep zamanaşımına uğradı", "guc": "orta",
         "curutme": "Kesilme sebebi var (kurgu)", "curutme_dayanak": "TBK m.154", "dayanak_durum": "teyitsiz",
         "artik_risk": "Kesilme tarihi tartışmalı"},
        {"cephe": "ictihat", "antitez": "Daire kayması", "guc": "dusuk", "curutme": "Güncel hat lehe (kurgu)",
         "curutme_dayanak": "Yargıtay kurgu karar B", "dayanak_durum": "teyitsiz"},
        # güçlü antiteze DAYANAKSIZ çürütme (dört)
        {"cephe": "maddi_vakia", "antitez": "Teslim yapılmadı", "guc": "yuksek", "curutme": "İrsaliye (kurgu)",
         "artik_risk": "İrsaliye imzasına itiraz gelebilir"},
        {"cephe": "maddi_vakia", "antitez": "Ayıp teslimden sonra doğdu", "guc": "yuksek",
         "curutme": "Muayene kaydı (kurgu)"},
        {"cephe": "ek_cephe", "antitez": "Yazışma aleyhe yorumlanabilir", "guc": "yuksek",
         "curutme": "Yazışmanın bağlamı farklı (kurgu)", "artik_risk": "Yazışma bilirkişiye gidebilir"},
        {"cephe": "ek_cephe_2", "antitez": "Ödeme kısmen yapıldı", "guc": "yuksek",
         "curutme": "Dekont tutarı eksik (kurgu)", "artik_risk": "Kısmi ödeme mahsup edilebilir"},
        # ÇÜRÜTÜLMEMİŞ — ne çürütme ne artık risk (dört)
        {"cephe": "ictihat", "antitez": "Aleyhe içtihat", "guc": "orta", "curutme": "", "artik_risk": ""},
        {"cephe": "niteleme_ek", "antitez": "Eser değil satım sözleşmesi", "guc": "dusuk"},
        {"cephe": "ozel_cephe", "antitez": "Standart dışı ama güçlü saldırı", "guc": "yuksek"},
        {"cephe": "ozel_cephe_2", "antitez": "Karşı tarafın yeni vakıası", "guc": "orta"},
        # şema hataları (dört)
        {"cephe": "diger", "antitez": "Standart dışı cephe", "guc": "cok", "dayanak_durum": "belki"},
        {"cephe": "diger_2", "antitez": "Yazım hatalı güç", "guc": "Yüksek!"},
        "sözlük olmayan cephe",
    ],
}
# Matriste bilerek BULUNMAYAN standart cepheler (AÇIK CEPHE listesine düşer — dört).
ANTITEZ_EKSIK = ("hukuki_niteleme", "defi_karsi_talep", "muvekkil_zaaf", "bilirkisi_teknik")


def test_antitez_matris_iskelet_ve_denetim_iki_kosuda_bayt_ozdes(tmp_path):
    """Antitez motorunun iki yüzü: `--iskelet` (cephe omurgası "her seferinde
    aynı sırada" — script docstring'i) ve `--dogrula` (açık cephe, çürütülmemiş
    antitez, teyitsiz/dayanaksız çürütme, şema hatası, artık risk blokları)
    her koşuda aynı.

    KIRAN DEĞİŞİKLİK: `eksik_cepheler` `set(STANDART_CEPHELER) - verilen` ile
    kurulursa; iskelet cepheleri bir kümeden dolaşılırsa; bulgu listeleri
    kümeyle tekilleştirilirse."""
    kayit, _ = _iki_kosu(tmp_path, {"matris.json": ANTITEZ_MATRISI}, [
        (ANTITEZ, ["--iskelet"]),
        (ANTITEZ, ["--dogrula", "matris.json"]),
    ])
    # fikstür sözleşmesi: dört açık cephe gerçekten listelendi (sıraya duyarlı blok)
    assert [k["cikis"] for k in kayit] == [0, 0]
    rapor = kayit[1]["stdout"].decode("utf-8")
    assert all(c in rapor for c in ANTITEZ_EKSIK), rapor


ZAPT_KARTI = """⚠ DAHİLİ — DOSYAYA EKLENMEZ / UYAP'A YÜKLENMEZ

# Celse kartı (kurgu)

## (a) Hedefler
- Keşif kararı

## (c) Tutanağa geçirilmesi şart olan beyanlar
- Tanık T1'in dinlenmesi talebimiz
- Bilirkişi raporuna itirazımız
- Banka kayıtlarının celbi talebimiz
- Keşif talebimiz

## (d) Ara karar talepleri
- Keşif
"""

ZAPT_METNI = """# 051 · durusma-zapti.pdf

- Kaynak evrak: `kurgu/zapt.pdf`
- Çıkarım yöntemi: **metin**

---

ÖRNEK ASLİYE HUKUK MAHKEMESİ DURUŞMA TUTANAĞI Tarih: 05.10.2026

HAKİM: Kurgu Hâkim KATİP: Kurgu Kâtip

Açık yargılamaya devam olundu. Davacı vekili tanık T1'in dinlenmesini talep etti.

<!-- --- sayfa 2 --- -->

Davacı vekili bilirkişi raporuna itiraz etti. Davacı vekili keşif talep etti.

GEREĞİ DÜŞÜNÜLDÜ: 1- Davacı vekilinin tanık dinletme talebinin reddine, 2- Bilirkişi raporuna karşı beyan için davacı vekiline iki haftalık kesin süre verilmesine, 3- Keşif talebinin, vakıanın keşifle ispatı mümkün olmadığından reddine, 4- Duruşmanın ertelenmesine karar verildi.
"""

# Başlık/hâkim/kâtip/tarih/ara karar ipuçları YOK → "unsur ipucu bulunamadı"
# listesi çok öğeli olur (sırası kilitlenir).
ZAPT_KISA = "Davacı vekili banka kayıtlarının celbini istedi. Bilirkişi raporu okundu.\n"

ZAPT_KARTI_JSON = {"kalemler": [
    {"id": "T9", "tur": "talep", "metin": "Banka kayıtları", "anahtar": ["banka", "kayıt"]},
    {"id": "T10", "tur": "itiraz", "metin": "Bilirkişi raporuna itiraz", "anahtar": ["bilirkişi rapor", "itiraz"]},
    {"tur": "bilinmeyen", "metin": "Keşif talebi"},
]}


def test_zapt_denetim_iki_kosuda_bayt_ozdes(tmp_path):
    """Celse kartı ↔ zabıt karşılaştırması (md kart `--json` + insan raporu,
    json kart + ipucusuz kısa zabıt) her koşuda aynı: kalem durumları, en
    yakın paragraf, ara kararlar (süre / gerekçesiz ret) ve eksik HMK m.154/3
    ipuçları aynı sırada.

    KIRAN DEĞİŞİKLİK: `eksik_ipucu` ya da ara karar kalemleri bir kümeden
    kurulursa; eşit skorlu paragraflar arasında seçim kümeden yapılırsa;
    kart kalemleri kümeyle tekilleştirilirse."""
    kayit, _ = _iki_kosu(tmp_path, {"kart.md": ZAPT_KARTI, "kart.json": ZAPT_KARTI_JSON,
                                    "zapt.md": ZAPT_METNI, "zapt-kisa.md": ZAPT_KISA}, [
        (ZAPT, ["--kart", "kart.md", "--zapt", "zapt.md", "--json"]),
        (ZAPT, ["--kart", "kart.md", "--zapt", "zapt.md"]),
        (ZAPT, ["--kart", "kart.json", "--zapt", "zapt-kisa.md", "--json"]),
    ])
    # fikstür sözleşmesi: ara karar bölgesi, ≥4 kalem ve ≥4 öğeli eksik-ipucu listesi çalıştı
    assert [k["cikis"] for k in kayit] == [0, 0, 0]
    tam, kisa = json.loads(kayit[0]["stdout"]), json.loads(kayit[2]["stdout"])
    assert len(tam["kalemler"]) >= 4 and len(tam["ara_kararlar"]) >= 4
    assert len(kisa["unsur_ipucu_bulunamadi"]) >= 4


# ═══════════════════════════ oa-illiyet ════════════════════════════════════

def _ill(a, b, **ek):
    """İlliyet kenarı; `alan=None` o alanı kenardan DÜŞÜRÜR."""
    k = {"kaynak": a, "hedef": b, "kategori": "illiyet", "tur": "sebep_zarar",
         "illiyet_tipi": "uygun", "guc": "guclu", "dogrulama": "teyitli",
         "dayanak_delil": ["D1"], "norm": "çıpa (kurgu)"}
    k.update(ek)
    return {alan: v for alan, v in k.items() if v is not None}


def _ils(a, b, **ek):
    """İlişki kenarı; `alan=None` o alanı kenardan DÜŞÜRÜR."""
    k = {"kaynak": a, "hedef": b, "kategori": "iliski", "tur": "ortaklik",
         "dogrulama": "teyitli", "dayanak_delil": ["D1"], "norm": "çıpa (kurgu)"}
    k.update(ek)
    return {alan: v for alan, v in k.items() if v is not None}


def _zengin_graf():
    """Dokuz bölümün hepsini dolduran kurgu graf. Köprü hesabının DFS kökü
    (`MERKEZ`, ilk düğüm) üç köprü yönünün KESİŞİMİNDEDİR: hangi köprünün önce
    keşfedileceği komşuluk KÜMESİNİN yineleme sırasına — yani hash tohumuna —
    bağlıdır. Çıktı bu sıraya bağımlı hâle gelirse iki koşu ayrışır."""
    dugumler = [
        {"id": "MERKEZ", "tip": "olay", "ad": "Teslim olayı"},
        {"id": "SOL", "tip": "gercek_kisi", "ad": "Ortak müdür (kurgu)", "usul_rolu": "davali"},
        {"id": "SAG", "tip": "olay", "ad": "Ödeme olayı"},
        {"id": "SIRKET_A", "tip": "tuzel_kisi", "ad": "Kurgu A Ltd. Şti."},
        {"id": "ORTAK_A", "tip": "gercek_kisi", "ad": "Ortak A (kurgu)", "usul_rolu": "tanik"},
        {"id": "SIRKET_B", "tip": "tuzel_kisi", "ad": "Kurgu B A.Ş."},
        {"id": "ORTAK_B", "tip": "gercek_kisi", "ad": "Ortak B (kurgu)", "rol": "davaci"},
        {"id": "HASAR", "tip": "olay", "ad": "Hasar"},
        {"id": "ZARAR", "tip": "olay", "ad": "Maddi zarar"},
        {"id": "TEDAVI", "tip": "olay", "ad": "Tedavi gideri"},
        {"id": "KAYIP", "tip": "olay", "ad": "Kazanç kaybı"},
        {"id": "MANEVI", "tip": "olay", "ad": "Manevi zarar"},
        {"id": "DONGU_1", "tip": "olay", "ad": "Döngü bir"},
        {"id": "DONGU_2", "tip": "olay", "ad": "Döngü iki"},
        {"id": "DONGU_3", "tip": "olay", "ad": "Döngü üç"},
        {"id": "K1", "tip": "karar", "ad": "İlk derece kararı (kurgu)"},
        {"id": "K2", "tip": "karar", "ad": "BAM kararı (kurgu)"},
        {"id": "K3", "tip": "karar", "ad": "Yargıtay kararı (kurgu)"},
        {"id": "K4", "tip": "mahkeme", "ad": "Yeniden yargılama mahkemesi (kurgu)"},
        {"id": "D1", "tip": "delil", "ad": "Bilirkişi raporu (kurgu)"},
        {"id": "D2", "tip": "delil", "ad": "Banka dekontu (kurgu)"},
        {"id": "D3", "tip": "delil", "ad": "Kamera kaydı (kurgu)"},          # bağlanmamış delil (dört)
        {"id": "D4", "tip": "delil", "ad": "Keşif tutanağı (kurgu)"},
        {"id": "D5", "tip": "delil", "ad": "Tanık beyanı (kurgu)"},
        {"id": "D6", "tip": "delil", "ad": "Ticari defter kayıtları (kurgu)"},
        {"id": "K6", "tip": "karar", "ad": "İkinci ilk derece kararı (kurgu)"},
        {"id": "YETIM", "tip": "sirket", "ad": "Bağsız kayıt"},              # yetim düğüm (dört)
        {"id": "YETIM_2", "tip": "olay", "ad": "Bağsız olay"},
        {"id": "YETIM_3", "tip": "hak", "ad": "Bağsız hak"},
        {"id": "YETIM_4", "tip": "nesne", "ad": "Bağsız nesne"},
        {"id": "SIRKET_A", "tip": "tuzel_kisi", "ad": "Mükerrer kayıt"},
        "sözlük olmayan düğüm",
    ]
    kenarlar = [
        # orta üçgen + iki kanat üçgeni → SOL ("perde") ve SAG ("yapisal") köprü
        _ils("MERKEZ", "SOL"), _ils("SOL", "SAG"), _ils("SAG", "MERKEZ"),
        _ils("SOL", "SIRKET_A"), _ils("SIRKET_A", "ORTAK_A"), _ils("ORTAK_A", "SOL"),
        _ils("SAG", "SIRKET_B"), _ils("SIRKET_B", "ORTAK_B", dogrulama=None),
        _ils("ORTAK_B", "SAG", dayanak="D2", dayanak_delil=None),
        # illiyet zinciri MERKEZ → HASAR → {ZARAR → TEDAVI → KAYIP, MANEVI}
        _ill("MERKEZ", "HASAR", dayanak_delil=["banka dekontu"]),
        _ill("HASAR", "ZARAR", guc="cok_guclu", kesme_flag="ceza:magdur_kusuru"),
        _ill("ZARAR", "TEDAVI", guc=None, norm=None, kesme_flag="mucbir_sebep"),
        _ill("TEDAVI", "KAYIP", guc="zayif", dogrulama="iddia", dayanak_delil=[],
             kesme_flag="ceza:magdur_kusur"),
        _ill("HASAR", "MANEVI", guc="tartismali", dogrulama="kesin"),
        # ayrı bileşende iç içe çevrimler + öz-döngü (Johnson yolu: blocked/B kümeleri)
        _ill("DONGU_1", "DONGU_2"), _ill("DONGU_2", "DONGU_3"), _ill("DONGU_3", "DONGU_1"),
        _ill("DONGU_2", "DONGU_1"), _ill("DONGU_3", "DONGU_2"), _ill("DONGU_3", "DONGU_3"),
        # kanun yolu (G12) — iki kök (K1, K6) × K2'den iki dal = dört zincir
        _ils("K1", "K2", tur="kanun_yolu", sonuc="esastan_ret"),
        _ils("K2", "K3", tur="kanun_yolu", sonuc="bozdu"),
        _ils("K2", "K4", tur="kanun_yolu", sonuc="kaldirdi"),
        _ils("K6", "K2", tur="kanun_yolu", sonuc="geri_cevirdi"),
        _ils("ZARAR", "HAYALET"),
        7,
    ]
    return {"dugumler": dugumler, "kenarlar": kenarlar}


def test_grafik_denetim_zengin_graf_ve_goc_iki_kosuda_bayt_ozdes(tmp_path):
    """İlliyet graf denetimi (rapor + `--json`, `--kok` defterinden taraf) ve
    `--goc` çıktısı her koşuda aynı: şema/sözlük uyarıları, yetim düğüm,
    bağlanmamış delil, köprü düğümler, çevrimler, kesme adayları, yük taşıyan
    kenar, zincir güveni ve kanun yolu zinciri aynı sırada.

    KIRAN DEĞİŞİKLİK: kanonik değer listesindeki `sorted(kume)` düşerse;
    `kopru_dugumler` düğüm sırası yerine `kesme` sözlüğünün (DFS keşif
    sırası, komşuluk kümesine bağlı) sırasıyla dolaşırsa; yetim düğüm ya da
    bağlanmamış delil listesi küme farkıyla kurulursa; Johnson alt grafı
    komşuları kümeden alır VE son çevrim sıralaması kalkarsa; `girdi` mutlak
    yola çevrilirse. (Yalnız son sıralamanın kalkması determinizmi BOZMAZ —
    liste tabanlı dolaşım yine aynı sırayı verir — ve bu test onu yakalamaz:
    bu bir sıra karakterizasyonu değil, determinizm kilididir.)"""
    kayit, dosyalar = _iki_kosu(tmp_path, {
        "graf.json": _zengin_graf(),
        "_oa/defter/pipeline-durum.json": {"dosya": "E. 2099/1 (kurgu)", "ceza_dali": "mudafii",
                                           "adimlar": {}, "katmanlar": {}},
    }, [
        (GRAFIK, ["graf.json", "--json", "denetim.json", "--kok", "."]),
        (GRAFIK, ["--goc", "graf.json", "--dal", "medeni", "--cikti", "yeni.json"]),
    ])
    # fikstür sözleşmesi: şema+çevrim kapısı (3), göç (0); kümeye/sıraya duyarlı bölümler ≥4 öğe
    assert [k["cikis"] for k in kayit] == [3, 0]
    d = json.loads(dosyalar["denetim.json"])
    for alan in ("kopru_dugumler", "cevrimler", "kanun_yolu_zinciri", "yetim_dugumler",
                 "baglanmamis_deliller"):
        assert len(d[alan]) >= 4, (alan, d[alan])
    assert len(d["kesme_adaylari"]) >= 3
    assert {k["etiket"] for k in d["kopru_dugumler"]} == {"perde", "yapisal"}
    assert d["yon"] == "curut" and d["yuk_tasiyan_kenarlar"]
    rapor = kayit[0]["stdout"].decode("utf-8")
    assert "dispozitif" in rapor, "kanonik değer listesi (sıralanan küme) basılmadı"
    assert "yeni.json" in dosyalar


def _buyuk_graf(n=240):
    """>200 illiyet düğümü → Johnson yerine geri-kenar örneklemi; ayrıca norm
    uyarısı 40 satır tavanını aşar ("… +N daha" yolu)."""
    ids = [f"N{i:03d}" for i in range(n)]
    dugumler = [{"id": d, "tip": "olay", "ad": f"Olay {d} (kurgu)"} for d in ids]
    kenarlar = [_ill(ids[i], ids[i + 1], guc=("zayif" if i % 7 == 0 else "guclu"), norm=None)
                for i in range(n - 1)]
    kenarlar += [_ill(ids[a], ids[b], norm=None) for a, b in ((60, 50), (130, 100), (200, 190), (235, 5))]
    return {"dugumler": dugumler + [{"id": "D1", "tip": "delil", "ad": "Bilirkişi raporu (kurgu)"}],
            "kenarlar": kenarlar}


def test_grafik_denetim_200_ustu_graf_geri_kenar_yolu_iki_kosuda_bayt_ozdes(tmp_path):
    """>200 düğümlü grafta ayrı çevrim algoritması (renkli DFS, geri-kenar
    örneklemi) ve stdout tavanları devrededir; bu yol da her koşuda aynı.

    KIRAN DEĞİŞİKLİK: `_geri_kenar_cevrimler` komşuları bir kümeden dolaşırsa
    ya da örneklemin sonuç sırası kümeden gelirse; tavanlı listelerin dilimi
    kararsız bir sıradan alınırsa."""
    graf = _buyuk_graf()
    kayit, dosyalar = _iki_kosu(tmp_path, {"graf.json": graf}, [
        (GRAFIK, ["graf.json", "--json", "denetim.json"]),
    ])
    # fikstür sözleşmesi: çevrim kapısı (3); illiyet düğümü sayısı scriptin GERÇEK Johnson
    # tavanının üstünde (tavan yükselirse bu satır fikstürü büyütmeyi hatırlatır)
    assert [k["cikis"] for k in kayit] == [3]
    illiyet_dugumu = {k[uc] for k in graf["kenarlar"] for uc in ("kaynak", "hedef")}
    assert len(illiyet_dugumu) > _modul(GRAFIK).JOHNSON_DUGUM_TAVANI
    d = json.loads(dosyalar["denetim.json"])
    assert len(d["cevrimler"]) >= 4 and len(d["kopru_dugumler"]) >= 4
