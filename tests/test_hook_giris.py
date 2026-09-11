# -*- coding: utf-8 -*-
"""hook_giris.py (v0.5.16.2 performans onarımı) testleri.

KÖK NEDEN: Python, `__main__` olarak koşturulan bir betiğin bytecode'unu ASLA
önbelleğe almaz — `__pycache__` yalnızca IMPORT edilen modüller için çalışır.
Hook ağı `pipeline_kayit.py`'yi (6300+ satır) doğrudan çağırdığı için o dosya
HER hook ateşlemesinde sıfırdan derleniyordu. `hook_giris.py` onu IMPORT
ederek çağırır; bytecode `__pycache__`'ten okunur.

BU TESTLERİN KİLİTLEDİĞİ ŞEY, bir hız sayısı DEĞİL, hızın karşılığında
hiçbir şeyin KAYBEDİLMEDİĞİdir:
  · çıkış kodları aynen geçer (`--denetle` exit 1 → teslim kapısı yaşar),
  · çıktı doğrudan çağrıyla BİREBİR aynıdır,
  · import katmanı çökerse eski yola (runpy) düşer — sessiz ölüm YOK,
  · `sys.path` kirletilmez (kardeş dosya stdlib'i gölgeleyemez),
  · sarmalayıcı, giriş betiği yoksa eski hedefe düşer.
Ayrıca kazancın KENDİSİ de kilitlenir (aksi hâlde bir gün sessizce kaybolur).
"""
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts"
GIRIS = SCRIPTS / "hook_giris.py"
KAYIT = SCRIPTS / "pipeline_kayit.py"
WRAP = REPO / "plugins" / "ortak-avukat" / "hooks" / "run-hook.cmd"


def _dava_klasoru():
    """Hook'un ateşlenmesi için dava klasörü görünümlü izole bir kök."""
    t = pathlib.Path(tempfile.mkdtemp())
    for i in ("001", "002", "003"):
        (t / f"{i}_evrak.pdf").write_bytes(b"x")
    return t


def _kos(betik, mod, kok, girdi=b"{}"):
    p = subprocess.run([sys.executable, str(betik), "--" + mod],
                       cwd=str(kok), input=girdi,
                       capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace")


# ── varlık ve bütünlük ─────────────────────────────────────────────────────

def test_giris_betigi_var_ve_derlenebilir():
    assert GIRIS.is_file(), "hook_giris.py yok — hook yolu eski hıza düşer"
    import py_compile
    py_compile.compile(str(GIRIS), doraise=True)     # sözdizimi kapısı


def test_giris_betigi_sys_path_kirletmez():
    """`sys.path.insert` deseni kardeş bir dosyanın (ör. ileride eklenen
    `json.py`) standart kütüphaneyi gölgelemesine yol açar. Giriş betiği
    bunu YAPMAMALI — importlib ile dosya yolundan yükler."""
    govde = GIRIS.read_text(encoding="utf-8")
    assert "sys.path.insert" not in govde and "sys.path.append" not in govde


# ── davranış eşitliği: hız, işlev karşılığında alınmadı ────────────────────

def test_cikti_dogrudan_cagriyla_birebir_ayni():
    kok = _dava_klasoru()
    kod_g, out_g = _kos(GIRIS, "hook-prompt", kok)
    kod_d, out_d = _kos(KAYIT, "hook-prompt", kok)
    assert kod_g == kod_d, f"çıkış kodu farkı: giriş={kod_g} doğrudan={kod_d}"
    assert out_g == out_d, "giriş betiği çıktıyı DEĞİŞTİRİYOR — kabul edilemez"
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in out_g       # hook gerçekten ateşlendi


def test_dava_disi_klasorde_sessiz():
    """Sessizlik sözleşmesi korunur: dava klasörü değilse gürültü/blok yok."""
    kod, out = _kos(GIRIS, "hook-prompt", pathlib.Path(tempfile.mkdtemp()))
    assert kod == 0 and out.strip() == ""


def test_cikis_kodu_gecer_denetle_kapisi_yasar():
    """`--denetle` boşluklu turda exit 1 döner (teslim kapısı). Giriş betiği
    `SystemExit`'i yutarsa bu kapı SESSİZCE ölür — en tehlikeli regresyon."""
    kok = pathlib.Path(tempfile.mkdtemp())
    kod_g, _ = _kos(GIRIS, "denetle", kok)
    kod_d, _ = _kos(KAYIT, "denetle", kok)
    assert kod_g == kod_d, "çıkış kodu aktarımı bozuldu — kapı sessizce ölür"


def test_tum_hook_modlari_cokmeden_gecer():
    """Mod geçişi jeneriktir; her modun giriş betiğinden geçtiği kilitlenir."""
    kok = _dava_klasoru()
    for mod in ("hook-prompt", "hook-pretool", "hook-postwrite",
                "hook-denetle", "hook-acilis"):
        girdi = b'{"tool_name":"Write","tool_input":{"file_path":"x.md"}}'
        kod, _ = _kos(GIRIS, mod, kok, girdi)
        assert kod in (0, 1), f"--{mod} beklenmeyen çıkış kodu: {kod}"


# ── asıl kazanç: bytecode önbelleği gerçekten kullanılıyor mu ──────────────

def test_bytecode_onbellegi_gercekten_yaziliyor():
    """Onarımın TA KENDİSİ: giriş betiği üzerinden çağrıda pipeline_kayit'in
    `.pyc`'si üretilmeli. Üretilmiyorsa kazanç yoktur (birisi `__main__`
    yoluna geri döndürmüş demektir)."""
    import importlib.util
    pyc = pathlib.Path(importlib.util.cache_from_source(str(KAYIT)))
    if pyc.exists():
        pyc.unlink()
    _kos(GIRIS, "hook-prompt", _dava_klasoru())
    if os.environ.get("PYTHONDONTWRITEBYTECODE"):
        return                     # ortam önbelleği kapatmış — betiğin suçu değil
    assert pyc.is_file(), (
        "pipeline_kayit .pyc üretilmedi — bytecode önbelleği devre dışı, "
        "hook başına ~41 ms kazanç kaybediliyor")


def test_giris_betigi_dogrudan_cagridan_HIZLI():
    """Kazanç sayısal olarak da kilitlenir. Eşik bilinçli olarak GEVŞEK
    (%25): amaç bir kıyaslama yarışı değil, kazancın bir gün sessizce
    kaybolmasını engellemek. Yavaş/gürültülü CI makinelerinde bile
    `__main__` yolu 6300 satırı yeniden derlediği için fark kalıcıdır."""
    import time
    kok = _dava_klasoru()
    _kos(GIRIS, "hook-prompt", kok)              # .pyc'yi ısıt

    def olc(betik, n=5):
        sureler = []
        for _ in range(n):
            t0 = time.perf_counter()
            _kos(betik, "hook-prompt", kok)
            sureler.append(time.perf_counter() - t0)
        return sorted(sureler)[len(sureler) // 2]      # ortanca

    giris = olc(GIRIS)
    dogrudan = olc(KAYIT)
    assert giris < dogrudan * 0.75, (
        f"giriş betiği beklenen kazancı vermiyor: {giris*1000:.1f} ms vs "
        f"doğrudan {dogrudan*1000:.1f} ms (eşik: %25 daha hızlı)")


# ── arıza emniyeti: hook ASLA sessizce ölmez ───────────────────────────────

def test_import_katmani_cokerse_eski_yola_duser():
    """`spec_from_file_location` None döndürürse (bozuk kurulum benzetimi)
    betik runpy ile eski yola düşmeli — çıktı yine üretilmeli."""
    kok = _dava_klasoru()
    kod_beklenen, out_beklenen = _kos(KAYIT, "hook-prompt", kok)
    sabotaj = (
        "import importlib.util as _iu, runpy, sys\n"
        "_iu.spec_from_file_location = lambda *a, **k: None\n"
        f"sys.argv = ['hook_giris.py', '--hook-prompt']\n"
        f"runpy.run_path({str(GIRIS)!r}, run_name='__main__')\n"
    )
    p = subprocess.run([sys.executable, "-c", sabotaj], cwd=str(kok),
                       input=b"{}", capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    assert "DEVİR YÜKÜMLÜLÜĞÜ" in out, (
        "import katmanı çökünce yedek yol ÇALIŞMADI — sessiz ölüm riski (447)")
    assert out == out_beklenen, "yedek yol farklı çıktı üretiyor"


def test_eksik_giris_betigi_sarmalayiciyi_oldurmez():
    """Sarmalayıcı, giriş betiği yoksa eski hedefe düşmeli: yarım/eski
    kurulumda işlev kaybı OLMAZ, yalnızca eski hız."""
    govde = WRAP.read_text(encoding="utf-8")
    assert "hook_giris.py" in govde, "sarmalayıcı giriş betiğine yönlenmiyor"
    assert "pipeline_kayit.py" in govde, "yedek hedef kaldırılmış — riskli"
    assert 'if not exist "%OA_SCRIPT%"' in govde, "cmd kolunda yedek kontrolü yok"
    assert 'if [ ! -f "$OA_SCRIPT" ]' in govde, "bash kolunda yedek kontrolü yok"
    # 447 dersi: yedek mantığı zincir operatörüyle (`||`) kurulmaz — kabuksuz
    # yürütmede `||` python'a ARGÜMAN olarak gider ve hook sessizce ölür.
    # Yalnızca YÜRÜTÜLEBİLİR satırlar denetlenir: dosyanın kendi açıklaması
    # zaten `||`'dan bahsediyor (yasağın gerekçesini anlatıyor).
    yurutulebilir = [
        s for s in govde.splitlines()
        if s.strip() and not s.strip().upper().startswith("REM")
        and not s.strip().startswith("#")
    ]
    assert not any("||" in s for s in yurutulebilir), (
        "447 dersi: sarmalayıcının YÜRÜTÜLEBİLİR satırlarında zincir "
        "operatörü YASAK — kabuksuz yürütmede sessiz ölüm üretir")
