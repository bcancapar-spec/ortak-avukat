# -*- coding: utf-8 -*-
"""v0.5.18 — R1 kilidi: belge güvenlik kapısının ESNEK ARAMASI üstel geri izlemeye girmez.

Bulgu (2026-10-06, ölçüldü): `_bul(esnek=True)` gizli parçanın her karakteri arasına
`_ARA_ARALIK` (boşluk, `*`, `_`, `\\`, `<u>`, `<br>`) koyuyordu. Parçanın KENDİSİ bu
ayraçlardan içerdiğinde (ör. alt çizgili form satırı) desen kendi kendisiyle çakışıyor:
parçada 10 alt çizgi + gövdede 30 alt çizgi → 3,7 sn; gövdede 60 alt çizgi → dakikalarca.
Kasıt gerekmez — beyaz alt çizgili bir form satırı tek başına evrak okumayı kilitler.

Düzeltme ilkesi (davranış en az değişsin):
- Ayraç İÇERMEYEN parça: desen BİREBİR aynı (eski algoritmayla eşdeğerlik testi aşağıda).
- Yalnız ayraçtan oluşan parça: gövdedeki ayraç koşusunda doğrusal arama; eski greedy
  eşleşmeyle aynı aralık (koşudaki ilk eşleşen ayraçtan son eşleşen ayraca).
- Harf + ayraç karışık parça: parçanın ayraçları iki yanda zaten atlanabilir sayıldığından
  çekirdek harflerle aranır; arama gevşediği için geçiş sırası eşlemesi güvenilmez →
  TÜM geçişler damgalanır (fazla damga zararsız, eksik damga enjeksiyondur).

Kilitlenme testleri alt süreçte, cömert zaman aşımıyla koşar (süre İDDİASI yoktur:
yalnız "bitti mi" sorulur). Fikstürler kurgudur; ağ yok.
"""
import importlib.util
import pathlib
import random
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
BG_YOL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "belge_guvenlik.py"


def _yukle():
    sp = importlib.util.spec_from_file_location("belge_guvenlik_esnek", BG_YOL)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


bg = _yukle()


def _alt_surecte_bul(metin_ifadesi, parca_ifadesi, sure=60):
    """`_bul(esnek=True)` çağrısını ayrı süreçte koşar; asılırsa test kırmızı olur."""
    kod = (
        "import importlib.util, sys\n"
        "sp = importlib.util.spec_from_file_location('bg', sys.argv[1])\n"
        "m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)\n"
        "print(m._bul(%s, %s, esnek=True))\n" % (metin_ifadesi, parca_ifadesi))
    r = subprocess.run([sys.executable, "-c", kod, str(BG_YOL)], capture_output=True,
                       text=True, encoding="utf-8", timeout=sure)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


# ------------------------------------------------------------ kilitlenmeme (R1)
def test_alt_cizgili_parca_uzun_alt_cizgi_kosusunda_kilitlenmez():
    assert _alt_surecte_bul("'x' + '_' * 400 + 'y'", "'x' + '_' * 30 + 'z'") == "[]"


def test_yalniz_alt_cizgi_parcasi_kisa_kosuda_kilitlenmez():
    assert _alt_surecte_bul("'a ' + '_' * 25 + ' b'", "'_' * 30") == "[]"


def test_yildizli_parca_yildiz_kosusunda_kilitlenmez():
    assert _alt_surecte_bul("'k' + '*' * 300 + 'm'", "'k' + '*' * 28 + 'n'") == "[]"


# ------------------------------------------------------------ eski davranışın korunması
def test_yalniz_ayrac_parcasi_kosunun_ilk_ve_son_ayraci_arasini_bulur():
    assert bg._bul("Ad: ________ Soyad", "______", esnek=True) == [(4, 12)]
    assert bg._bul("a _<u>__</u>_ b", "___", esnek=True) == [(2, 13)]


def test_yalniz_ayrac_parcasi_yetersiz_kosuda_bulunmaz():
    assert bg._bul("Ad: ___ Soyad", "______", esnek=True) == []


def test_karisik_parca_alt_cizgisi_ayni_olan_gecisleri_bulur():
    assert bg._bul("x talimat_metni y talimat__metni", "talimat_metni", esnek=True) == [(2, 15), (18, 32)]


def _eski_bul(metin, parca, bas=0, son=None, esnek=False):
    """v0.5.18 adayındaki R1 öncesi algoritma (eşdeğerlik referansı)."""
    son = len(metin) if son is None else min(son, len(metin))
    p = (parca or "").strip()
    if not p or bas >= son:
        return []
    out = []
    if not esnek:
        i = metin.find(p, bas, son)
        while i >= 0:
            out.append((i, i + len(p)))
            i = metin.find(p, i + len(p), son)
        if out:
            return out
    harfler = [c for c in p if not c.isspace()]
    if not harfler or len(harfler) > 300:
        return out
    aralik = r"(?:\s|\*|_|\\|</?u>|<br\s*/?>)*"
    rx = re.compile(aralik.join(re.escape(c) for c in harfler))
    return [(m.start(), m.end()) for m in rx.finditer(metin, bas, son)]


def test_ayrac_icermeyen_parcada_sonuc_eski_algoritmayla_birebir_ayni():
    rnd = random.Random(20261006)
    govde_alfabe = ["a", "b", "c", "ç", "ş", " ", "\n", "*", "_", "\\", "<u>", "</u>", "<br/>", ".", "1"]
    parca_alfabe = ["a", "b", "c", "ç", "ş", " ", ".", "1"]
    for _ in range(400):
        metin = "".join(rnd.choice(govde_alfabe) for _ in range(rnd.randint(0, 60)))
        parca = "".join(rnd.choice(parca_alfabe) for _ in range(rnd.randint(1, 8)))
        for esnek in (False, True):
            assert bg._bul(metin, parca, esnek=esnek) == _eski_bul(metin, parca, esnek=esnek), (metin, parca, esnek)


# ------------------------------------------------------------ gevşeyen aramanın bedeli
def test_karisik_parca_ayrac_farkli_yazilsa_da_bulunur():
    assert bg._bul("talimat metni burada", "talimat_metni", esnek=True) == [(0, 13)]


def test_karisik_ayracli_kisa_parcada_tum_gecisler_damgalanir():
    assert bg._sec([(0, 5), (9, 14)], 0, "ab_cd") == [(0, 5), (9, 14)]


def test_ayracsiz_kisa_parcada_sira_eslemesi_korunur():
    assert bg._sec([(0, 5), (9, 14)], 1, "abxcd") == [(9, 14)]
