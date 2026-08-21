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
        cp = subprocess.run([b, "-c", ilk], input="{}", capture_output=True,
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
    print()
    print("SONUÇ: %s" % ("TÜM MEKANİK KONTROLLER GEÇTİ ✓" if hata == 0 else "ARIZA VAR ✗"))
    sys.exit(hata)


if __name__ == "__main__":
    main()
