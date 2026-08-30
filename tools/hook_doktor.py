#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
"""hook_doktor.py — HOOK KATMANI YEREL TEŞHİS ARACI (v0.5.7).

Denizli 754 dersi: hook katmanı SAĞLAM olduğu hâlde 50 dakikalık saha
oturumunda hiç ateşlemedi — masaüstü uygulaması eklenti güncellemesinden
ÖNCE açılmıştı ve hook kaydını bayat süreçten miras almıştı. Bu araç,
"hook'lar çalışır durumda mı" sorusunu beyandan ölçüme çevirir:

  [1] Kurulu eklenti kaydı  : installed_plugins.json + plugin.json `hooks`
  [2] hooks.json şeması     : üst `hooks` sarmalayıcısı + olay envanteri
                              (DİNAMİK — olaylar hooks.json'dan okunur;
                              yarın 7. olay eklense bu kod değişmez)
  [3] Komut sözleşmeleri    : her olayın hook komutu FİİLEN koşturulur
                              (ağsız, sentetik dava klasöründe; sarmalayıcı
                              run-hook.cmd DÜŞÜRÜLMEDEN bash ile TAM komut,
                              stdin'e boş JSON; enjeksiyon ve exit-0
                              sözleşmesi doğrulanır)
  [4] Canlı doğrulama tarifi: bayat-süreç tuzağına karşı insan adımları

v0.5.9 T1 onarımı: eski sürüm sarmalayıcı yolunu düşürüyordu
(`[sys.executable] + parcalar[1:]` fiilen `python hook-prompt` koşuyordu,
exit 2) → katman sağlamken 4 olayda SAHTE ARIZA basıyordu.

Kullanım:  python tools/hook_doktor.py            (repo kökünden)
           python tools/hook_doktor.py --kurulu   (kurulu eklentiyi test et)
Çıkış: 0 = tüm mekanik kontroller geçti; 1 = en az biri düştü.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = pathlib.Path(__file__).resolve().parents[1]


def hooks_olaylari(hooks_yol=None):
    """hooks.json'daki olayları DİNAMİK okur (v0.5.9 T2 — sabit liste YOK).

    Envanterin tek kaynağı hooks.json'dur: yarın yeni bir olay eklendiğinde
    bu kod değişmeden onu da teşhis eder. aile_dogrula.py hook-kapsam kapısı
    da bu fonksiyonu çağırarak envanter eşitliğini doğrular."""
    if hooks_yol is None:
        hooks_yol = REPO / "plugins" / "ortak-avukat" / "hooks" / "hooks.json"
    veri = json.loads(pathlib.Path(hooks_yol).read_text(encoding="utf-8"))
    return list(veri.get("hooks", {}).keys())


# ═══════════ B-1 (v0.5.14) — SERVİS EDİLEN NESİL ≠ DENETLENEN NESİL ════════
# Denetimde ölçüldü (2026-08): depo plugin.json 0.5.13, kurulu önbellek
# 0.5.9.1, masaüstü uygulamasının rpm anlık görüntüsü **0.5.0** — üç ayrı
# nesil aynı anda diskteydi ve `hook_doktor --kurulu` "TÜM MEKANİK KONTROLLER
# GEÇTİ ✓" + exit 0 basıyordu. Kodda depo↔servis sürüm karşılaştırması YOKTU;
# yani araç, koştuğu nesli değil BAŞKA bir nesli denetleyip yeşil veriyordu.
# Bu, ailenin üç kez nükseden en pahalı arızasının (bayat araç nesli) denetim
# körlüğüdür: "depoda düzelttim" bu mekanizma altında doğrulanamaz bir
# iddiadır. Onarım fail-closed'dır — servis edilen nesil DENETLENEMİYORSA ya
# da depodan FARKLIYSA yeşil basılmaz.
_ARAC_SURUM_RE = re.compile(
    r"""^\s*OA_SURUM\s*=\s*["']([0-9][0-9A-Za-z.\-]*)["']""", re.M)

_DAMGALI_SCRIPTLER = (
    ("oa-pipeline", "pipeline_kayit.py"),
    ("oa-kontrol", "teslim_paketi.py"),
)


def plugin_surumu(plugin_kok):
    """Bir eklenti kökünün `.claude-plugin/plugin.json` sürümü (yoksa None).
    ASLA fırlatmaz."""
    try:
        pj = pathlib.Path(plugin_kok) / ".claude-plugin" / "plugin.json"
        return json.loads(pj.read_text(encoding="utf-8")).get("version")
    except Exception:
        return None


def plugin_adi(plugin_kok):
    try:
        pj = pathlib.Path(plugin_kok) / ".claude-plugin" / "plugin.json"
        return json.loads(pj.read_text(encoding="utf-8")).get("name")
    except Exception:
        return None


def oa_surum_damgalari(plugin_kok):
    """Eklenti ağacındaki makine-okur `OA_SURUM` damgaları {script: sürüm}.
    Bu damgalar 'denetlenen nesil'in tek maddi kanıtıdır. ASLA fırlatmaz."""
    damgalar = {}
    for parca, ad in _DAMGALI_SCRIPTLER:
        yol = pathlib.Path(plugin_kok) / "skills" / parca / "scripts" / ad
        try:
            m = _ARAC_SURUM_RE.search(yol.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if m:
            damgalar[ad] = m.group(1)
    return damgalar


def _rpm_plugin_json_adaylari():
    """Masaüstü uygulamasının anlık-görüntü (rpm) köklerindeki plugin.json
    yolları. Sınırlı derinlikte glob; ASLA fırlatmaz."""
    adaylar = []
    kokler = []
    for env in ("APPDATA", "XDG_CONFIG_HOME"):
        v = os.environ.get(env)
        if v:
            kokler.append(pathlib.Path(v) / "Claude" / "local-agent-mode-sessions")
    kokler.append(pathlib.Path.home() / "AppData" / "Roaming" / "Claude"
                  / "local-agent-mode-sessions")
    gorulen = set()
    for kok in kokler:
        try:
            anahtar = str(kok).lower()
            if anahtar in gorulen or not kok.is_dir():
                continue
            gorulen.add(anahtar)
            for desen in ("*/*/rpm/plugin_*/.claude-plugin/plugin.json",
                          "*/*/*/.claude-plugin/plugin.json"):
                adaylar.extend(kok.glob(desen))
        except Exception:
            continue
    return adaylar


def servis_kokleri():
    """SERVİS EDİLEN ortak-avukat kurulumlarını keşfeder.

    Döner: `[(etiket, yol, sürüm|None, hata|None), ...]` — sürüm okunamayan
    kök de listeye GİRER (bilinmezlik gizlenmez). Kaynaklar:
      · `CLAUDE_PLUGIN_ROOT` (hook süreçlerinde fiilen servis edilen kök)
      · `installed_plugins.json` kaydı (kurulu önbellek)
      · masaüstü uygulamasının rpm anlık-görüntüleri (skill gövdelerinin
        geldiği ağaç — 0.5.0 bu kanaldan çıktı)
    ASLA fırlatmaz."""
    bulunan, gorulen = [], set()

    def _ekle(etiket, yol):
        try:
            anahtar = os.path.normcase(str(pathlib.Path(yol).resolve()))
        except Exception:
            anahtar = str(yol)
        if anahtar in gorulen:
            return
        gorulen.add(anahtar)
        ad, surum = plugin_adi(yol), plugin_surumu(yol)
        if ad is not None and ad != "ortak-avukat":
            return
        hata = None if surum else "plugin.json okunamadı/sürümsüz"
        bulunan.append((etiket, pathlib.Path(yol), surum, hata))

    try:
        cpr = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if cpr and plugin_adi(cpr) == "ortak-avukat":
            _ekle("CLAUDE_PLUGIN_ROOT", cpr)
    except Exception:
        pass
    try:
        kurulu, _not = _kurulu_kok()
        if kurulu is not None:
            _ekle("kurulu", kurulu)
    except Exception:
        pass
    for pj in _rpm_plugin_json_adaylari():
        try:
            if json.loads(pj.read_text(encoding="utf-8")).get("name") != "ortak-avukat":
                continue
        except Exception:
            continue
        _ekle("anlık görüntü", pj.parent.parent)
    return bulunan


def servis_mutabakati_raporu(depo_surum, kokler):
    """`(satırlar, hata)` — servis edilen her nesli depo sürümüyle karşılaştırır.

    FAIL-CLOSED: sürümü FARKLI ya da OKUNAMAYAN her servis kökü hatadır.
    Hiç kurulum bulunamaması bir bilinmezlik DEĞİL belirli bir cevaptır
    (bu makineden bayat nesil servis edilmiyor) — yeşil kalır ama açıkça
    yazılır. ASLA fırlatmaz."""
    satirlar, hata = [], False
    if not kokler:
        satirlar.append(
            "    servis edilen ortak-avukat kurulumu bulunamadı — yalnız depo "
            "ağacı denetlendi (temiz klon/CI)")
        return satirlar, hata
    for etiket, yol, surum, kok_hata in kokler:
        if kok_hata or not surum:
            satirlar.append("    ✗ %-18s %s → DENETLENEMEDİ (%s)"
                            % (etiket, yol, kok_hata or "sürüm yok"))
            hata = True
        elif surum != depo_surum:
            satirlar.append("    ⛔ %-18s %s → %s (depo %s) — BAYAT NESİL SERVİS EDİLİYOR"
                            % (etiket, yol, surum, depo_surum))
            hata = True
        else:
            satirlar.append("    ✓ %-18s %s → %s" % (etiket, yol, surum))
    if hata:
        satirlar.append(
            "    ÇARE: `/plugin` ile eklentiyi güncelleyin, Claude Code'u TAM "
            "kapatıp açın (anlık görüntü ancak böyle tazelenir).")
    return satirlar, hata


def _gercek_bash():
    """Git Bash'i AÇIK yoldan ara (tests/test_hook_sarmalayici._gercek_bash
    deseni): PATH'teki `bash` Windows'ta WSL stub'ına (System32) çözülüp WSL
    kurulu değilse patlar. Ubuntu-CI'da shutil.which normal bash'i bulur."""
    for aday in (r"C:\Program Files\Git\bin\bash.exe",
                 r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if pathlib.Path(aday).is_file():
            return aday
    b = shutil.which("bash")
    if b and "system32" not in b.lower():
        return b
    return None


def _kurulu_kok():
    kayit = pathlib.Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not kayit.is_file():
        return None, "installed_plugins.json yok"
    veri = json.loads(kayit.read_text(encoding="utf-8"))
    girdiler = veri.get("plugins", {}).get("ortak-avukat@ortak-avukat")
    if not girdiler:
        return None, "ortak-avukat@ortak-avukat kaydı yok"
    e = girdiler[0]
    return pathlib.Path(e["installPath"]), "sürüm %s" % e.get("version")


def _komut_calistir(komut, plugin_kok, cwd):
    """Hook komutunu SARMALAYICIYI DÜŞÜRMEDEN koşturur (v0.5.9 T1 onarımı).

    run-hook.cmd sarmalayıcılı komut bash ile TAM olarak koşulur — eski
    sürüm `[sys.executable] + parcalar[1:]` ile fiilen `python hook-prompt`
    koşup exit 2 basıyordu (sahte arıza). stdin'e boş JSON {} verilir:
    hook-pretool payload'ı bu kanaldan okur, boş girdi asla bloklamaz."""
    ilk = komut.split("||")[0].strip()
    ilk = ilk.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_kok).replace("\\", "/"))
    if "run-hook.cmd" in ilk:
        b = _gercek_bash()
        if b is None:
            return None, "gerçek bash bulunamadı — sarmalayıcı koşulamadı"
        # bash -c "<yol> <mod>" DEĞİL: ubuntu'da dosyanın exec biti yoksa
        # exit 126 (permission denied) döner — CI bunu yakaladı. bash'e
        # dosyayı YORUMLATMAK (bash <yol> <mod>) exec biti gerektirmez ve
        # sarmalayıcının bash-kolu iki çağrı biçiminde de aynı çalışır.
        import shlex
        parcalar = shlex.split(ilk)
        cp = subprocess.run([b] + parcalar, input="{}", capture_output=True,
                            text=True, encoding="utf-8", errors="replace",
                            cwd=str(cwd), timeout=120)
        return cp.returncode, cp.stdout or ""
    parcalar = [p.strip('"') for p in ilk.split()]
    argv = [sys.executable] + parcalar[1:]
    cp = subprocess.run(argv, input="{}", capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(cwd),
                        timeout=120)
    return cp.returncode, cp.stdout or ""


def main():
    ap = argparse.ArgumentParser(description="Ortak Avukat hook katmanı teşhisi")
    ap.add_argument("--kurulu", action="store_true",
                    help="Depo yerine KURULU eklentiyi (cache) test et")
    ap.add_argument("--servis-atla", action="store_true", dest="servis_atla",
                    help="[5] SERVİS EDİLEN NESİL kapısını atla — yalnız depo "
                         "katmanı denetlenir (temiz klon/CI; B-1 kapısı devre dışı)")
    a = ap.parse_args()

    hata = 0
    if a.kurulu:
        plugin_kok, not_ = _kurulu_kok()
        if plugin_kok is None:
            print("[1] KURULU EKLENTİ  : ✗ %s" % not_)
            sys.exit(1)
        print("[1] KURULU EKLENTİ  : ✓ %s (%s)" % (plugin_kok, not_))
    else:
        plugin_kok = REPO / "plugins" / "ortak-avukat"
        print("[1] DEPO EKLENTİSİ  : %s" % plugin_kok)

    # [1b] SÜRÜM MUTABAKATI (B-1) — denetlenen ağacın kendi içinde tutarlılığı:
    #      plugin.json ↔ makine-okur OA_SURUM damgaları. Ayrışırsa "hangi nesli
    #      denetlediğimiz" sorusunun cevabı yoktur → yeşil basılamaz.
    depo_surum = plugin_surumu(REPO / "plugins" / "ortak-avukat")
    denetlenen_surum = plugin_surumu(plugin_kok)
    damgalar = oa_surum_damgalari(plugin_kok)
    print("[1b] SÜRÜM MUTABAKATI: denetlenen ağaç %s · depo %s · OA_SURUM %s"
          % (denetlenen_surum or "?", depo_surum or "?",
             ", ".join("%s=%s" % (k, v) for k, v in sorted(damgalar.items()))
             or "damga YOK"))
    if not denetlenen_surum or not damgalar:
        print("     ✗ sürüm damgası okunamadı — DENETLENEN NESİL BELİRSİZ")
        hata = 1
    elif set(damgalar.values()) != {denetlenen_surum}:
        print("     ✗ plugin.json ↔ OA_SURUM damgaları AYRIŞIK")
        hata = 1
    elif a.kurulu and depo_surum and denetlenen_surum != depo_surum:
        print("     ⛔ KURULU nesil (%s) depodan (%s) FARKLI — bu denetimin "
              "yeşili depo için geçerli DEĞİLDİR" % (denetlenen_surum, depo_surum))
        hata = 1

    pj = json.loads((plugin_kok / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    if pj.get("hooks"):
        print("    plugin.json hooks: ✓ %s" % pj["hooks"])
    else:
        print("    plugin.json hooks: ✗ YOK — hook katmanı hiç kaydolmaz (v0.5.6 arızası)")
        hata = 1

    hooks_yol = plugin_kok / "hooks" / "hooks.json"
    veri = json.loads(hooks_yol.read_text(encoding="utf-8"))
    ic = veri.get("hooks", {})
    olaylar = hooks_olaylari(hooks_yol)  # DİNAMİK envanter (v0.5.9 T2)
    if not olaylar:
        print("[2] hooks.json      : ✗ hiç olay kayıtlı değil")
        hata = 1
    else:
        print("[2] hooks.json      : ✓ %d olay kayıtlı (%s)"
              % (len(olaylar), ", ".join(olaylar)))

    # [3] sentetik dava klasöründe komutları fiilen koştur — her olay için:
    #     sarmalayıcı komut + exit + tek satır sonuç
    dava = pathlib.Path(tempfile.mkdtemp(prefix="oa-hookdoktor-"))
    for i in ("001", "002", "003"):
        (dava / ("%s_Test_Evraki.pdf" % i)).write_text("sentetik", encoding="utf-8")
    ok = True
    for olay in olaylar:
        try:
            komut = ic[olay][0]["hooks"][0]["command"]
            kisa = komut.replace("${CLAUDE_PLUGIN_ROOT}/hooks/", "").strip('"').replace('" ', " ")
            kod, out = _komut_calistir(komut, plugin_kok, dava)
            if kod is None:
                print("[3] %-16s: ✗ %s · %s" % (olay, out, kisa))
                ok = False
                continue
            if kod != 0:
                print("[3] %-16s: ✗ exit %d (bloklamama sözleşmesi İHLAL) · %s"
                      % (olay, kod, kisa))
                ok = False
                continue
            if olay == "UserPromptSubmit":
                j = json.loads(out)
                metin = j["hookSpecificOutput"]["additionalContext"]
                if "DEVİR YÜKÜMLÜLÜĞÜ" not in metin:
                    print("[3] %-16s: ✗ enjeksiyon metni beklenen değil · %s" % (olay, kisa))
                    ok = False
                    continue
                print("[3] %-16s: ✓ exit 0 — devir enjeksiyonu üretiliyor · %s" % (olay, kisa))
            else:
                print("[3] %-16s: ✓ exit 0 · %s" % (olay, kisa))
        except Exception as e:
            print("[3] %-16s: ✗ %s" % (olay, e))
            ok = False
    if not ok:
        hata = 1

    print()
    print("[4] CANLI DOĞRULAMA (bayat-süreç tuzağına karşı — mekanik test bunu")
    print("    İKAME EDEMEZ; Denizli 754'te katman sağlamdı ama süreç bayattı):")
    print("    1. Eklenti güncellemesinden sonra Claude Code'u TAM kapatıp açın")
    print("       (ya da oturum içinde /reload-plugins).")
    print("    2. Bir dava klasöründe YENİ oturum açın; İLK mesajınızdan sonra")
    print("       modelin bağlamında DEVİR YÜKÜMLÜLÜĞÜ metninin etkisini görün")
    print("       (model kendiliğinden oa-pipeline'a devrediyorsa katman canlı).")
    print("    3. Şüphede: oturumda /hooks yazın — kayıtlı hook listesi açılır;")
    print("       ya da `claude --debug` çıktısında hook kayıt satırlarını arayın.")
    # [5] SERVİS EDİLEN NESİL (B-1) — bu makinede FİİLEN servis edilen ağaç(lar)
    #     depo neslini mi taşıyor? Denetlenen ağaç ile servis edilen ağaç ayrı
    #     şeylerdir; ayrıştığında "düzelttim" iddiası doğrulanamaz.
    print()
    if a.servis_atla:
        print("[5] SERVİS EDİLEN NESİL: ATLANDI (--servis-atla) — bu koşunun "
              "yeşili yalnız DEPO katmanı içindir.")
    else:
        print("[5] SERVİS EDİLEN NESİL (B-1 — fail-closed):")
        satirlar, servis_hata = servis_mutabakati_raporu(depo_surum, servis_kokleri())
        for s in satirlar:
            print(s)
        if servis_hata:
            hata = 1

    print()
    print("SONUÇ: %s" % ("TÜM MEKANİK KONTROLLER GEÇTİ ✓" if hata == 0 else "ARIZA VAR ✗"))
    sys.exit(hata)


if __name__ == "__main__":
    main()
