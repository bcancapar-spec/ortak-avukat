"""RESMİ OKUYUCU TANIĞI — geçerlilik kapısının kör noktasını kapatan 5. denetim.

2026/307 saha oturumunun bildirdiği reçetenin 3. adımı. Gerekçe: `udf_dogrula`nın
ilk dört denetimi dosyayı BİZİM okuyucumuzun (udf_metin.py) beklentisine göre
sınar. Sahada bizi yakan hata sınıfı tam olarak buydu — eski hand-rolled zip
çıktısı BİZİM round-trip'imizi GEÇİYOR ama UYAP Doküman Editörü onu AÇMIYORDU.
Kendi varsayımıyla kendini doğrulamak kanıt değildir; bu yüzden dosyayı ÜRETEN
aracın kendi okuyucusu (`udf-cli udf2md`) dışarıdan tanık olarak çağrılır.

Testler AĞSIZ koşar: dış süreç `okuyucu_fn` ile enjekte edilir.
"""
import importlib.util
import io
import os
import pathlib
import sys
import zipfile

import pytest

BETIK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "ortak-avukat", "skills", "oa-dilekce", "scripts", "udf_yaz.py")


@pytest.fixture(scope="module")
def uy():
    spec = importlib.util.spec_from_file_location("_test_resmi_udf_yaz", BETIK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_test_resmi_udf_yaz"] = mod
    spec.loader.exec_module(mod)
    return mod


# v0.5.18 (G-6, anayasa m.10): resmî okuyucu artık Layer 0'dan SONRA çağrılır; bu fikstür
# okuyucu bacağını YALITTIĞI için taraf bağlamı ("Müvekkil" + E/K no — strict ASK) taşımaz.
# Süzgecin okuyucuyu durdurduğu hâl tests/test_v0518_anayasa_onarimlari.py'dedir.
GOVDE = ("T.C. DENİZLİ 8. ASLİYE HUKUK MAHKEMESİ'NE\n"
         "CEVAP DİLEKÇESİ\n"
         "Açılan davanın reddi gerekmektedir.\n"
         "Yargıtay 17. Hukuk Dairesi 2019/1234 E. 2021/5678 K. sayılı kararı uyarınca.\n"
         "NETİCE-İ TALEP: Davanın reddine karar verilmesini talep ederiz.\n")


def _gecerli_udf_yaz(yol, govde=GOVDE):
    """İlk DÖRT denetimden geçen (bizim ayrıştırıcımızın kabul ettiği) bir UDF
    üretir — resmî okuyucu bacağını yalıtarak sınayabilmek için."""
    paragraflar = [s + "\n" for s in govde.split("\n") if s] or [govde]
    tam = "".join(paragraflar)
    parcalar, imlec = [], 0
    for p in paragraflar:
        u = len(p.encode("utf-16-le")) // 2
        parcalar.append('<paragraph><content startOffset="%d" length="%d"/></paragraph>'
                        % (imlec, u))
        imlec += u
    # v0.5.8.4: hvl-default STİL TANIMI eklendi — udf_dogrula artık tanımsız
    # dosyayı 'elle-üretim imzası' ile geçersiz sayar; bu fixture'ın amacı
    # resmî-okuyucu bacağını YALITMAK olduğundan ilk denetimlerden geçmelidir.
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<template format_id="1.8">'
           '<content><![CDATA[%s]]></content>'
           '<elements resolver="hvl-default">%s</elements>'
           '<styles><style name="hvl-default" family="Times New Roman" size="12"/></styles>'
           '</template>' % (tam, "".join(parcalar)))
    with zipfile.ZipFile(yol, "w") as zf:
        zf.writestr("content.xml", xml)
    return tam


def _sahte_okuyucu(calisti=True, basarili=True, metin=None, hata=None):
    def _fn(_yol, **_kw):
        return {"calisti": calisti, "basarili": basarili,
                "metin": metin if metin is not None else GOVDE, "hata": hata}
    return _fn


# ── (1) Üç durum ayrı tutulur ────────────────────────────────────────────────

def test_resmi_okuyucu_okuduysa_OK_ve_gecerli(tmp_path, uy):
    yol = str(tmp_path / "a.udf")
    _gecerli_udf_yaz(yol)
    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu())
    assert s["resmi_okuyucu"] == "OK"
    assert s["gecerli"] is True
    assert s["resmi_okuyucu_karakter"] == len(GOVDE)


def test_resmi_okuyucu_REDDEDERSE_gecersiz(tmp_path, uy):
    """ASIL KAZANIM: bizim dört denetimimiz GEÇSE BİLE, dosyayı üreten aracın
    okuyucusu reddediyorsa dosya GEÇERSİZDİR — sahadaki hata sınıfı budur."""
    yol = str(tmp_path / "b.udf")
    _gecerli_udf_yaz(yol)
    kontrol = uy.udf_dogrula(yol, resmi_okuyucu=False)
    assert kontrol["gecerli"] is True, "ön koşul: ilk dört denetim geçmeli"

    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(
        calisti=True, basarili=False, hata="udf2md exit 1: bozuk belge"))

    assert s["resmi_okuyucu"] == "RET"
    assert s["gecerli"] is False
    assert any("RESMİ OKUYUCU REDDETTİ" in h for h in s["hatalar"])


def test_arac_yoksa_YAPILAMADI_ve_BLOKLAMAZ(tmp_path, uy):
    """Ağ/oturum/Node yokluğu ORTAM koşuludur, dosyanın kusuru değil — çevrimdışı
    çalışma imkânsızlaşmasın diye bloklamaz. Ama 'doğrulandı' da SAYILMAZ."""
    yol = str(tmp_path / "c.udf")
    _gecerli_udf_yaz(yol)
    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(
        calisti=False, basarili=False, hata="npx bulunamadı"))

    assert s["resmi_okuyucu"] == "YAPILAMADI"
    assert s["gecerli"] is True, "ortam eksikliği dosyayı geçersiz kılmaz"
    assert "npx bulunamadı" in s["resmi_okuyucu_not"]
    assert not any("RESMİ OKUYUCU" in h for h in s["hatalar"])


def test_YAPILAMADI_hali_STDOUT_ta_GORUNUR(tmp_path, uy):
    """Sessiz atlama yasağının simetriği: doğrulanmamış bir dosyayı doğrulanmış
    sanmak, hiç doğrulamamaktan tehlikelidir — bu hâl susturulamaz."""
    tampon = io.StringIO()
    uy._resmi_okuyucu_bas(
        {"resmi_okuyucu": "YAPILAMADI", "resmi_okuyucu_not": "oturum yok"}, akis=tampon)
    cikti = tampon.getvalue()
    assert "YAPILAMADI" in cikti
    assert "AÇILDIĞI DOĞRULANMADI" in cikti


# ── (2) "Açılıyor ama boş/kırpık" — içerik kaybı ─────────────────────────────

def test_resmi_okuyucu_icerik_kaybini_yakalar(tmp_path, uy):
    """Dosya açılıyor ama gövdenin önemli kısmı okunamıyorsa GEÇERSİZ — 'açıldı'
    tek başına yeterli kanıt değildir."""
    yol = str(tmp_path / "d.udf")
    tam = _gecerli_udf_yaz(yol)
    kirpik = tam[:int(len(tam) * 0.2)]

    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(metin=kirpik))

    assert s["resmi_okuyucu"] == "RET"
    assert s["gecerli"] is False
    assert any("İÇERİK KAYBI" in h for h in s["hatalar"])


def test_markdown_imleri_yuzunden_UZUN_metin_kusur_sayilmaz(tmp_path, uy):
    """udf2md markdown imleri ekler (## , **, | ) — çıktının UZUN olması
    NORMALDİR; yalnız KISALIK içerik kaybı işaretidir."""
    yol = str(tmp_path / "e.udf")
    tam = _gecerli_udf_yaz(yol)
    zengin = "## " + tam.replace("\n", "\n\n**") + "\n\n| a | b |\n"

    s = uy.udf_dogrula(yol, okuyucu_fn=_sahte_okuyucu(metin=zengin))

    assert s["resmi_okuyucu"] == "OK"
    assert s["gecerli"] is True


# ── (3) Ortam hatası ile GERÇEK RET birbirine karışmaz ──────────────────────

@pytest.mark.parametrize("stderr_metni", [
    "Error: login required", "Oturum bulunamadı", "quota exceeded",
    "fetch failed", "ETIMEDOUT",
])
def test_oturum_ag_hatasi_RET_degil_YAPILAMADI(tmp_path, uy, monkeypatch, stderr_metni):
    """Login'i unutmuş bir avukatın GEÇERLİ dilekçesi 'bozuk' ilan edilemez —
    ortam hatası dosya hakkında hüküm DEĞİLDİR."""
    class _P:
        returncode = 1
        stdout = ""
        stderr = stderr_metni

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is False, f"{stderr_metni!r} ortamsal sayılmalıydı"
    assert r["basarili"] is False


@pytest.mark.parametrize("stderr_metni", [
    "'udf-cli' is not recognized as an internal or external command,\r\n"
    "operable program or batch file.",
    # Türkçe Windows: cmd iletisi OEM kod sayfasında gelir, utf-8 çözümünde Türkçe harfler
    # bozulur — ASCII parçası ("program ya da toplu") bozulmadan kalır.
    "'udf-cli' i� ya da d�� komut, �al��t�r�labilir "
    "program ya da toplu i� dosyas� olarak tan�nm�yor.",
    "sh: 1: udf-cli: not found",
    "bash: udf-cli: command not found",
    "npm error could not determine executable to run",
])
def test_baslatici_hatasi_RET_degil_YAPILAMADI(tmp_path, uy, monkeypatch, stderr_metni):
    """NEDEN VAR (CI, PR #8, windows-latest / py3.14): paralel test işçileri aynı anda
    `npx -y udf-cli@…` çağırınca Windows'ta npx önbelleği yarışa girdi ve cmd "'udf-cli' is
    not recognized…" dedi. Bu, udf2md'nin dosya hakkında verdiği bir hüküm DEĞİL, aracın hiç
    koşamadığı bir ORTAM hâlidir; RET sayılınca geçerli UDF GEÇERSİZ ilan edildi (dört test
    kırmızı). Avukatın makinesinde de (bozuk npx önbelleği, eşzamanlı iki teslim) aynı yanlış
    ret teslimi durdururdu. İleti oturum talimatı DEĞİL, başlatma sorununu söylemeli."""
    class _P:
        returncode = 1
        stdout = ""
        stderr = stderr_metni

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is False, f"{stderr_metni!r} başlatıcı (ortam) hatası sayılmalıydı"
    assert r["basarili"] is False
    assert "başlatılamadı" in r["hata"], r["hata"]


@pytest.mark.parametrize("donus,stderr_metni", [
    # CI, PR #8 ubuntu-latest / py3.12 — CI çıktısı (koşucu yolu ~ ile kısaltıldı, B-38): errno -39 → çıkış 217
    (217, "npm error code ENOTEMPTY\nnpm error syscall rmdir\nnpm error path ~/.npm/_npx/"
          "12165089bad8f415/node_modules/pako/lib/zlib\nnpm error errno -39\nnpm error ENOTEMPTY: directory "
          "not empty, rmdir '~/.npm/_npx/12165089bad8f415/node_modules/pako/lib/zlib'"),
    # CI, PR #8 windows-latest / py3.12-3.13 — birebir: libuv -4051 işaretsiz 32 bit döner
    (4294963245, "npm warn cleanup Failed to remove some directories [\nnpm warn cleanup   [\nnpm warn cleanup"
                 "     '\\\\?\\C:\\npm\\cache\\_npx\\12165089bad8f415\\node_modules\\zod',\nnpm warn cleanup "
                 "    [Error: ENOTEMPTY: directory not empty, rmdir 'C:\\npm\\cache\\_npx\\12165089bad8f415"
                 "\\node_modules\\zod\\v4\\locales'] {"),
    (-9, ""),                                       # POSIX: süreç sinyalle öldürüldü — hüküm yok
    (3221225477, "Segmentation fault"),             # Windows: node.exe yerel çöküşü (0xC0000005)
    # CI, PR #8 ubuntu-latest / py3.13 — yarım kalan npx önbelleğinde aracın KENDİ bağımlılığı yok
    # (çıkış 1 ama hüküm değil: udf2md hiç yüklenemedi). Koşucu yolu ~ ile kısaltıldı (B-38).
    (1, "node:internal/modules/esm/resolve:205\n  const resolvedOption = FSLegacyMainResolve(pkgPath, "
        "packageConfig.main, baseStringified);\n\nError: Cannot find package '~/.npm/_npx/12165089bad8f415/"
        "node_modules/zod/index.js' imported from ~/.npm/_npx/12165089bad8f415/node_modules/udf-cli/dist/"
        "index.js\n    at legacyMainResolve (node:internal/modules/esm/resolve:205:26) {\n  code: "
        "'ERR_MODULE_NOT_FOUND'\n}"),
    (1, "Error: Cannot find module 'zod'\nRequire stack:\n- ~/.npm/_npx/x/node_modules/udf-cli/dist/cli.js\n"
        "    at Module._resolveFilename (node:internal/modules/cjs/loader:1225:15) {\n  code: "
        "'MODULE_NOT_FOUND'\n}"),
])
def test_npm_altyapi_hatasi_RET_degil_YAPILAMADI(tmp_path, uy, monkeypatch, donus, stderr_metni):
    """NEDEN VAR (CI, PR #8, 2026-10-08 — üç bacak): paralel test işçilerinin eşzamanlı `npx -y`
    çağrıları npm'in KENDİ önbellek temizliğini ENOTEMPTY ile düşürdü; udf2md dosya hakkında hiç hüküm
    vermeden süreç bitti ve bu "resmî okuyucu REDDETTİ" sayılıp geçerli UDF GEÇERSİZ ilan edildi. npm'in
    sistem çağrısı hatası (`npm error code E…`, `npm error syscall`, `npm warn cleanup`) ile olağan dışı
    çıkış kodu (Windows'ta 255 üstü işaretsiz errno/çöküş, POSIX'te sinyal) ORTAM hâlidir."""
    class _P:
        returncode = donus
        stdout = ""
        stderr = stderr_metni

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is False, f"exit {donus} / {stderr_metni[:60]!r} ortam hâli sayılmalıydı"
    assert r["basarili"] is False and "başlatılamadı" in r["hata"], r["hata"]


def test_npm_komut_basarisizligi_hukum_sayilir_RET(tmp_path, uy, monkeypatch):
    """İmler DAR kalmalı: çalıştırılan aracın KENDİ başarısızlığı (`npm error code 1` — sayısal kod,
    errno değil; `command failed`) dosya hakkında bir hükümdür → RET. Geniş bir "npm error" imi gerçek
    reddi YAPILAMADI'ya çevirip kapıyı açardı (fail-open)."""
    class _P:
        returncode = 1
        stdout = ""
        stderr = ("Error: invalid UDF structure — unexpected element\nnpm error code 1\nnpm error path /tmp\n"
                  "npm error command failed\nnpm error command sh -c udf-cli udf2md yok.udf")

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is True and r["basarili"] is False, r
    assert "OKUYAMADI" in r["hata"]


def test_aracin_calisma_hatasi_hukum_sayilir_RET(tmp_path, uy, monkeypatch):
    """Modül imleri de DAR: ESM ana modülünde fırlayan gerçek bir çalışma hatasının yığını
    `node:internal/modules/esm/module_job` çerçevesi taşır — bu bir HÜKÜMDÜR (araç yüklendi, dosyayı
    okudu, reddetti) ve RET kalmalı. Yalnız çözümleme hatası (ERR_MODULE_NOT_FOUND, esm/resolve)
    ortam hâlidir."""
    class _P:
        returncode = 1
        stdout = ""
        stderr = ("file:///x/node_modules/udf-cli/dist/index.js:120\n    throw new Error(\"Geçersiz UDF: content."
                  "xml yok\");\n          ^\n\nError: Geçersiz UDF: content.xml yok\n    at udf2md (file:///x/"
                  "node_modules/udf-cli/dist/index.js:120:11)\n    at ModuleJob.run (node:internal/modules/esm/"
                  "module_job:271:25)\n    at async onImport.tracePromise.__proto__ (node:internal/modules/esm/"
                  "loader:547:26)")

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is True and r["basarili"] is False, r


def test_ci_npx_onbellegi_testlerden_once_tek_kaynakli_surumle_isitilir():
    """Yarışın kaynağı CI'da kapatılır: `npx` önbelleği testlerden ÖNCE bir kez ısıtılır (paralel
    işçiler paketi aynı anda kurmaya çalışmasın). Sürüm TEK kaynaktan okunur (kopya `udf-cli@0.5.6`
    yasak); ısıtma başarısızsa iş düşmez — ürün kodu ortam hâlini zaten YAPILAMADI diye işler."""
    ci = (pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8")
    isit = ci.find("- name: npx önbelleğini ısıt (udf-cli)")
    assert isit >= 0, "ci.yml'de npx ısıtma adımı yok"
    assert isit < ci.find("- name: Run tests"), "ısıtma testlerden ÖNCE olmalı"
    adim = ci[isit:ci.find("- name: Run tests")]
    assert "UDF_CLI_SURUM" in adim and "udf_yaz.py" in adim, "sürüm tek kaynaktan okunmalı"
    assert "udf-cli@0." not in ci, "udf-cli sürümü ci.yml'ye KOPYALANMAMALI"
    assert "|| echo" in adim, "ısıtma başarısızlığı işi düşürmemeli"


def test_gercek_bozukluk_RET_olarak_isaretlenir(tmp_path, uy, monkeypatch):
    class _P:
        returncode = 1
        stdout = ""
        stderr = "Error: invalid UDF structure — unexpected element"

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", lambda *a, **k: _P())

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is True, "yapısal hata bir HÜKÜMDÜR, ortam koşulu değil"
    assert r["basarili"] is False
    assert "OKUYAMADI" in r["hata"]


def test_npx_yoksa_calisti_False(tmp_path, uy, monkeypatch):
    monkeypatch.setattr(uy.shutil, "which", lambda _a: None)
    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))
    assert r["calisti"] is False and "npx bulunamadı" in r["hata"]


def test_zaman_asimi_ortam_sayilir(tmp_path, uy, monkeypatch):
    def _patla(*_a, **_k):
        raise uy.subprocess.TimeoutExpired(cmd="udf2md", timeout=1)
    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", _patla)

    r = uy.npx_ile_udf_oku(str(tmp_path / "yok.udf"))

    assert r["calisti"] is False and "zaman aşımı" in r["hata"]


# ── (4) Hat bütünlüğü: md2udf'e dönüş yok ───────────────────────────────────

def test_okuyucu_udf2md_cagirir_md2udf_DEGIL(tmp_path, uy, monkeypatch):
    cagrilar = []

    class _P:
        returncode = 0
        stdout = GOVDE
        stderr = ""

    def _yakala(args, **_k):
        cagrilar.append(args)
        return _P()

    monkeypatch.setattr(uy.shutil, "which", lambda _a: "npx")
    monkeypatch.setattr(uy.subprocess, "run", _yakala)
    uy.npx_ile_udf_oku(str(tmp_path / "x.udf"))

    assert cagrilar, "dış süreç çağrılmalıydı"
    komut = cagrilar[0]
    assert "udf2md" in komut
    assert "md2udf" not in komut
    # v0.5.18: sabitlenmiş sürüm (udf_yaz.py UDF_CLI_SURUM) — `@latest` yok.
    assert uy.UDF_CLI_PAKET in komut
    assert not any("latest" in str(a) for a in komut), komut
