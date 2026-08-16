# -*- coding: utf-8 -*-
"""v0.5.8.5 HİJYEN PAKETİ testleri (E1 / E2 / E4a / E5).

Kapsam (saha karnesinden — tüm veriler SENTETİKTİR, tmp_path altında):
  E1  — oa_metrik: teslim-makbuz-RED.json AYRI sayaçla sayılır (red_makbuz);
        sahadaki "RED: 0" yanlış negatifi kapanır.
  E2  — gizlilik_tara bağlam istisnaları:
        (a) "rapor" tek başına sağlık deseni TETİKLEMEZ (bilirkişi raporu/ek
            rapor); sağlık-bağlamlı rapor (hastane/teşhis/doktor komşuluğu)
            YİNE tetikler (iki yönlü kanıt).
        (b) 16 haneli, 0 ile başlayan Mersis biçimli dizi kart uyarısından
            AYRIŞIR; gerçek kart (Luhn) yine MUTLAK DENY.
        (c) 10 haneli belge/doküman-id (documentId/evrak no komşuluğu) telefon
            uyarısından AYRIŞIR; gerçek telefon yine yakalanır.
        (d) DENY-OVERRIDE protokolü: parametresiz DENY = engel sürer (exit 2);
            --override-onay avukat + >=30 karakter gerekçe ile aşılır ve
            _oa/defter/istisna-kayitlari.jsonl'e kayıt düşer.
  E4a — hesapla_sure: hesap çıktısı üretilirken <kok>/_oa varsa son gün
        _oa/sureler.json'a OTOMATİK flag olarak işlenir (oa_hafiza sure-flag
        şeması; sure_nobetci aynı defteri okur); _oa yoksa yazılmaz; tekrar
        koşuda çoğalmaz.
  E5  — oa_ingest: aynı sha256 içerik ikinci bir ad altında görüldüğünde
        ikinci metin/harita ÜRETİLMEZ; künyeye "ayni_icerik" işareti düşer
        (kayıt SİLİNMEZ — kayıpsızlık); harita başlıklarında mojibake onarımı.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
GIZLILIK = SKILLS / "oa-gizlilik" / "scripts" / "gizlilik_tara.py"
METRIK = SKILLS / "oa-pipeline" / "scripts" / "oa_metrik.py"
INGEST = SKILLS / "oa-ingest" / "scripts" / "oa_ingest.py"
SURE = SKILLS / "oa-sure" / "scripts" / "hesapla_sure.py"
NOBETCI = SKILLS / "oa-sure" / "scripts" / "sure_nobetci.py"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


giz = _yukle("gizlilik_tara_v0585", GIZLILIK)
met = _yukle("oa_metrik_v0585", METRIK)


def _calistir(argv, cwd=None):
    return subprocess.run([sys.executable] + [str(a) for a in argv],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          cwd=str(cwd) if cwd else None)


# ═══════════════════ E1 — RED MAKBUZ AYRI SAYACI ═══════════════════

def _defter_kur(kok):
    d = kok / "_oa" / "defter"
    d.mkdir(parents=True, exist_ok=True)
    (d / "pipeline-durum.json").write_text(
        json.dumps({"dosya": "Sentetik 2024/123 Esas", "adimlar": {}, "katmanlar": {}}),
        encoding="utf-8")
    return d


def test_e1_red_makbuz_dosyasi_ayri_sayacla_sayilir(tmp_path):
    """teslim-makbuz-RED.json varken red_makbuz=1 — teslim-makbuz.json'a
    bakan eski sayaç 0 kalsa bile (sahadaki yanlış negatif)."""
    d = _defter_kur(tmp_path)
    (d / "teslim-makbuz-RED.json").write_text(
        json.dumps({"exit_kodu": 1, "sebep": "sentetik başarısız deneme"}),
        encoding="utf-8")
    m = met.hesapla(str(tmp_path))
    ov = m["override_sayaci"]
    assert ov["durum"] == "olculdu"
    assert ov["red_makbuz"] == 1
    # başarı-makbuz dosyası hiç yok → eski sayaç 0; RED artık ayrı görünür.
    assert ov["teslim_makbuz_red_sayisi"] == 0


def test_e1_red_makbuz_yokken_sifir(tmp_path):
    _defter_kur(tmp_path)
    m = met.hesapla(str(tmp_path))
    assert m["override_sayaci"]["red_makbuz"] == 0


def test_e1_red_makbuz_ozette_gorunur(tmp_path):
    """İnsan-okur özet RED-makbuz dosyasını da basar — 'RED: 0' tek satırıyla
    yanlış temiz-ışık verilmez."""
    d = _defter_kur(tmp_path)
    (d / "teslim-makbuz-RED.json").write_text(json.dumps({"exit_kodu": 1}),
                                              encoding="utf-8")
    m = met.hesapla(str(tmp_path))
    m["cikti"] = "(test)"
    ozet = met.ozet_yaz(m)
    assert "RED-makbuz" in ozet
    satir = next(s for s in ozet.splitlines() if "RED-makbuz" in s)
    assert "1" in satir


def test_e1_elden_parca_override_sayacina_girer(tmp_path):
    """C5 (v0.5.8.5) ELDEN statüsü uyumu: ELDEN'e düşen şerhli parça override
    sayacından KAYBOLMAZ (görünmez kaçış olmaz) — işlenmiş sayılır, ayrı da
    raporlanır."""
    d = tmp_path / "_oa" / "defter"
    d.mkdir(parents=True)
    (d / "pipeline-durum.json").write_text(json.dumps({
        "dosya": "Sentetik 2024/123 Esas",
        "adimlar": {
            "5": {"parcalar": {"oa-kiyas": {"durum": "ELDEN", "serh": "sentetik şerh"}}},
            "1": {"parcalar": {"oa-interview": {"durum": "UYGULANDI"}}},
        },
        "katmanlar": {}}), encoding="utf-8")
    ov = met.hesapla(str(tmp_path))["override_sayaci"]
    assert ov["toplam_uygulandi_parca"] == 2
    assert ov["serhli_uygulandi_parca"] == 1
    assert ov["elden_parca"] == 1


# ═══════════════════ E2(a) — SAĞLIK DESENİ BAĞLAM İSTER ═══════════════════

def test_e2a_bilirkisi_raporu_deny_uretmez():
    """'rapor' tek başına (bilirkişi raporu / ek rapor) sağlık verisi DEĞİLDİR
    — 95 tekrarlı sentetik metin strict modda bile DENY/ASK üretmez."""
    metin = ("Bilirkişi raporu ve ek rapor incelendi; kök raporda hesap "
             "yöntemi açıklanmıştır. ") * 95
    deny, ask = giz.tara(metin, "strict")
    assert not deny, f"bilirkişi raporu DENY üretmemeli: {deny}"
    assert not ask, f"bilirkişi raporu ASK da üretmemeli: {ask}"


def test_e2a_gercek_saglik_verisi_yine_deny():
    """İki yönlü kanıt: hastane/teşhis bağlamlı metin strict modda DENY."""
    metin = "Hastane kayıtlarındaki teşhis ve tedavi bilgisi rapora eklendi."
    deny, _ask = giz.tara(metin, "strict")
    assert any("Sağlık" in ad for _s, ad in deny)


def test_e2a_doktor_raporu_baglamla_yakalanir():
    """'rapor' sağlık-bağlam komşuluğunda (doktor/hekim) YİNE tetikler —
    istisna sağlık verisini köreltmez."""
    metin = "Doktor raporu dosyaya sunulmuştur."
    deny, _ask = giz.tara(metin, "strict")
    assert any("Sağlık" in ad for _s, ad in deny)


# ═══════════════════ E2(b) — MERSİS / KART AYRIMI ═══════════════════

def test_e2b_mersis_bicimli_dizi_kart_uyarisi_uretmez():
    """16 hane + 0 ile başlama = Mersis biçimi (kart IIN'i 0 ile başlamaz) —
    kart DENY/ASK üretmez."""
    metin = "Şirketin Mersis numarası 0123456789012345 olarak kayıtlıdır."
    deny, ask = giz.tara(metin, "strict")
    assert not any("Kart" in ad for _s, ad in deny)
    assert not any("Uzun sayı" in ad for _s, ad in ask)


def test_e2b_gercek_kart_yine_mutlak_deny():
    metin = "Ödeme karti 4111 1111 1111 1111 üzerinden yapılmıştır."
    deny, _ask = giz.tara(metin, "strict")
    assert any("Kart" in ad for _s, ad in deny)


# ═══════════════════ E2(c) — DOKÜMAN-ID / TELEFON AYRIMI ═══════════════════

def test_e2c_documentid_telefon_uyarisi_uretmez():
    metin = ("UYAP documentId: 2024123456 ile evrak no 1234567890 "
             "üzerinden doğrulama yapılabilir.")
    deny, ask = giz.tara(metin, "strict")
    assert not any("Telefon" in ad for _s, ad in deny)
    assert not any("Telefon" in ad for _s, ad in ask)


def test_e2c_gercek_telefon_yine_yakalanir():
    metin = "Tanığa 0532 123 45 67 numarasından ulaşılmıştır."
    deny, ask = giz.tara(metin, "strict")
    hepsi = list(deny) + list(ask)
    assert any("Telefon" in ad for _s, ad in hepsi)


# ═══════════════════ E2(d) — DENY-OVERRIDE PROTOKOLÜ ═══════════════════

DENY_METIN = "Hastane kayıtlarındaki teşhis ve tedavi bilgisi özetlenmiştir."
GEREKCE = ("Avukat metni bizzat inceledi; gönderim bilinçli ve gerekli "
           "olduğu için onaylandı (sentetik gerekçe).")


def _istisna_yolu(kok):
    return kok / "_oa" / "defter" / "istisna-kayitlari.jsonl"


def test_e2d_parametresiz_deny_engel_surer(tmp_path):
    dosya = tmp_path / "taslak.txt"
    dosya.write_text(DENY_METIN, encoding="utf-8")
    cp = _calistir([GIZLILIK, dosya], cwd=tmp_path)
    assert cp.returncode == 2, cp.stdout + cp.stderr
    assert not _istisna_yolu(tmp_path).exists()


def test_e2d_override_onayla_asilir_ve_deftere_islenir(tmp_path):
    dosya = tmp_path / "taslak.txt"
    dosya.write_text(DENY_METIN, encoding="utf-8")
    cp = _calistir([GIZLILIK, dosya, "--override-onay", "avukat",
                    "--override-gerekce", GEREKCE, "--kok", tmp_path],
                   cwd=tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    yol = _istisna_yolu(tmp_path)
    assert yol.is_file(), "istisna defteri satırı düşmeliydi"
    satirlar = [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]
    assert len(satirlar) == 1
    kayit = satirlar[0]
    assert kayit["tur"] == "gizlilik-deny-override"
    assert kayit["onay"] == "avukat"
    assert kayit["gerekce"] == GEREKCE
    assert kayit["zaman"] and kayit["ilgili"] and kayit["imza"]


def test_e2d_gerekcesiz_override_red(tmp_path):
    """--override-onay tek başına yetmez: >=30 karakter gerekçe yoksa DENY
    sürer (fail-closed), defter satırı düşmez."""
    dosya = tmp_path / "taslak.txt"
    dosya.write_text(DENY_METIN, encoding="utf-8")
    cp = _calistir([GIZLILIK, dosya, "--override-onay", "avukat",
                    "--kok", tmp_path], cwd=tmp_path)
    assert cp.returncode == 2, cp.stdout + cp.stderr
    assert not _istisna_yolu(tmp_path).exists()


def test_e2d_temiz_metinde_override_kayit_dusmez(tmp_path):
    """DENY yokken override parametresi verilse bile istisna kaydı düşmez
    (aşılacak bir engel yok)."""
    dosya = tmp_path / "taslak.txt"
    dosya.write_text("Sentetik temiz dilekçe metni.", encoding="utf-8")
    cp = _calistir([GIZLILIK, dosya, "--override-onay", "avukat",
                    "--override-gerekce", GEREKCE, "--kok", tmp_path],
                   cwd=tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert not _istisna_yolu(tmp_path).exists()


# ═══════════════════ E5 — INGEST SHA-DEDUP + MOJİBAKE ═══════════════════

def _ingest(klasor, *ek):
    return _calistir([INGEST, klasor] + list(ek))


def test_e5_sha_dedup_ikinci_ad_tek_metin(tmp_path):
    icerik = ("Sentetik dilekçe metni — 2024/123 Esas sayılı dosya hakkında "
              "açıklamalar içerir.\n") * 5
    (tmp_path / "01-dilekce.txt").write_text(icerik, encoding="utf-8")
    (tmp_path / "02-kopya.txt").write_text(icerik, encoding="utf-8")
    cp = _ingest(tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    kunye = json.loads((tmp_path / "_oa" / "metin" / "00-kunye.json")
                       .read_text(encoding="utf-8"))
    kayitlar = kunye["kayitlar"]
    assert len(kayitlar) == 2, "kayıpsızlık: iki kayıt da künyede kalmalı"
    ilk = next(k for k in kayitlar if k["kaynak"] == "01-dilekce.txt")
    iki = next(k for k in kayitlar if k["kaynak"] == "02-kopya.txt")
    assert ilk["md"], "ilk kayıt normal md üretir"
    assert not iki.get("md"), "ikinci metin ÜRETİLMEZ (aynı içerik)"
    assert iki["ayni_icerik"] == ilk["md"]
    mdler = [p.name for p in (tmp_path / "_oa" / "metin").glob("*.md")
             if p.name != "00-INDEX.md"]
    assert len(mdler) == 1, f"tek md beklenirdi: {mdler}"


def test_e5_sha_dedup_ikinci_kosuda_kararli(tmp_path):
    """Önbellekli ikinci koşu SEMANTİK olarak aynı künyeyi üretir (idempotens
    bozulmaz; önbellek sort_keys ile yazıldığından anahtar SIRASI değişebilir —
    byte değil içerik karşılaştırılır) ve dedup işareti kalıcıdır."""
    icerik = "Aynı sentetik içerik satırı.\n" * 3
    (tmp_path / "01-a.txt").write_text(icerik, encoding="utf-8")
    (tmp_path / "02-b.txt").write_text(icerik, encoding="utf-8")
    assert _ingest(tmp_path).returncode == 0
    kunye_yol = tmp_path / "_oa" / "metin" / "00-kunye.json"
    ilk_kunye = json.loads(kunye_yol.read_text(encoding="utf-8"))
    assert _ingest(tmp_path).returncode == 0
    iki_kunye = json.loads(kunye_yol.read_text(encoding="utf-8"))
    assert iki_kunye == ilk_kunye
    iki = next(k for k in iki_kunye["kayitlar"] if k["kaynak"] == "02-b.txt")
    assert iki["ayni_icerik"] and not iki["md"]


def test_e5_farkli_icerik_dedup_edilmez(tmp_path):
    (tmp_path / "01-a.txt").write_text("Birinci farklı sentetik metin.\n" * 3,
                                       encoding="utf-8")
    (tmp_path / "02-b.txt").write_text("İkinci bambaşka sentetik metin.\n" * 3,
                                       encoding="utf-8")
    assert _ingest(tmp_path).returncode == 0
    kunye = json.loads((tmp_path / "_oa" / "metin" / "00-kunye.json")
                       .read_text(encoding="utf-8"))
    assert all(k["md"] and not k.get("ayni_icerik") for k in kunye["kayitlar"])


def test_e5_harita_basligi_mojibake_onarilir(tmp_path):
    """Büyük evrağın harita başlığındaki UTF-8→cp1252 mojibake'i onarılır."""
    baslik_moji = "Dilekçe Başlığı Sentetik".encode("utf-8").decode("cp1252")
    icerik = baslik_moji + "\n" + ("Sentetik açıklama satırı devam ediyor.\n" * 50)
    (tmp_path / "03-buyuk.txt").write_text(icerik, encoding="utf-8")
    cp = _ingest(tmp_path, "--buyuk-esik", "100")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    haritalar = list((tmp_path / "_oa" / "metin").glob("*.harita.json"))
    assert haritalar, "büyük eşik aşıldı — harita üretilmeliydi"
    harita = json.loads(haritalar[0].read_text(encoding="utf-8"))
    assert harita["bolumler"][0]["baslik"].startswith("Dilekçe Başlığı Sentetik")


# ═══════════════════ E4a — SÜRE BAĞI (OTOMATİK FLAG) ═══════════════════

def test_e4a_sure_flag_otomatik_yazilir(tmp_path):
    (tmp_path / "_oa").mkdir()
    cp = _calistir([SURE, "--teblig", "2030-01-05", "--sure", "10",
                    "--birim", "gun", "--kok", tmp_path])
    assert cp.returncode == 0, cp.stdout + cp.stderr
    veri = json.loads((tmp_path / "_oa" / "sureler.json").read_text(encoding="utf-8"))
    fl = veri["flagler"]
    assert len(fl) == 1
    assert fl[0]["son_gun"] == "2030-01-15"
    assert fl[0]["tarih"] == "2030-01-15"   # geriye-uyum alanı (oa_hafiza şeması)
    assert fl[0]["tur"] == "usul"
    assert fl[0]["aciklama"]


def test_e4a_oa_yoksa_flag_yazilmaz(tmp_path):
    cp = _calistir([SURE, "--teblig", "2030-01-05", "--sure", "10",
                    "--birim", "gun", "--kok", tmp_path])
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert not (tmp_path / "_oa").exists(), \
        "_oa yoksa dava kökü değildir — defter icat edilmez"


def test_e4a_tekrar_kosuda_cogalmaz(tmp_path):
    (tmp_path / "_oa").mkdir()
    argv = [SURE, "--teblig", "2030-01-05", "--sure", "10",
            "--birim", "gun", "--kok", tmp_path]
    assert _calistir(argv).returncode == 0
    assert _calistir(argv).returncode == 0
    veri = json.loads((tmp_path / "_oa" / "sureler.json").read_text(encoding="utf-8"))
    assert len(veri["flagler"]) == 1, "aynı hesap ikinci koşuda çoğalmamalı"


def test_e4a_nobetci_ayni_defteri_okur(tmp_path):
    (tmp_path / "_oa").mkdir()
    assert _calistir([SURE, "--teblig", "2030-01-05", "--sure", "10",
                      "--birim", "gun", "--kok", tmp_path]).returncode == 0
    cp = _calistir([NOBETCI, "--kok", tmp_path])
    assert "2030-01-15" in cp.stdout
    assert cp.returncode == 0, cp.stdout   # ileri tarihli → acil yok
