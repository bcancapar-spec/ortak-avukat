#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
"""hook_doktor.py — HOOK KATMANI YEREL TEŞHİS ARACI (v0.5.7).

Denizli 754 dersi: hook katmanı SAĞLAM olduğu hâlde 50 dakikalık saha
oturumunda hiç ateşlemedi — masaüstü uygulaması eklenti güncellemesinden
ÖNCE açılmıştı ve hook kaydını bayat süreçten miras almıştı. Bu araç,
"hook'lar çalışır durumda mı" sorusunu beyandan ölçüme çevirir:

  [1] Kurulu eklenti kaydı  : installed_plugins.json + plugin.json `hooks`
  [2] hooks.json şeması     : üst `hooks` sarmalayıcısı + 4 olay
  [3] Komut sözleşmeleri    : 4 hook komutu FİİLEN koşturulur (ağsız,
                              sentetik dava klasöründe; enjeksiyon JSON'u
                              ve exit-0 sözleşmesi doğrulanır)
  [4] Canlı doğrulama tarifi: bayat-süreç tuzağına karşı insan adımları

Kullanım:  python tools/hook_doktor.py            (repo kökünden)
           python tools/hook_doktor.py --kurulu   (kurulu eklentiyi test et)
Çıkış: 0 = tüm mekanik kontroller geçti; 1 = en az biri düştü.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = pathlib.Path(__file__).resolve().parents[1]
OLAYLAR = ["UserPromptSubmit", "PostToolUse", "Stop", "SessionEnd"]


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
    ilk = komut.split("||")[0].strip()
    ilk = ilk.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_kok).replace("\\", "/"))
    parcalar = [p.strip('"') for p in ilk.split()]
    argv = [sys.executable] + parcalar[1:]
    cp = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(cwd), timeout=120)
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
    eksik = [o for o in OLAYLAR if o not in ic]
    if eksik:
        print("[2] hooks.json      : ✗ eksik olay(lar): %s" % ", ".join(eksik))
        hata = 1
    else:
        print("[2] hooks.json      : ✓ 4 olay kayıtlı (%s)" % ", ".join(OLAYLAR))

    # [3] sentetik dava klasöründe komutları fiilen koştur
    dava = pathlib.Path(tempfile.mkdtemp(prefix="oa-hookdoktor-"))
    for i in ("001", "002", "003"):
        (dava / ("%s_Test_Evraki.pdf" % i)).write_text("sentetik", encoding="utf-8")
    ok = True
    for olay in OLAYLAR:
        try:
            komut = ic[olay][0]["hooks"][0]["command"]
            kod, out = _komut_calistir(komut, plugin_kok, dava)
            if kod != 0:
                print("[3] %-16s: ✗ exit %d (bloklamama sözleşmesi İHLAL)" % (olay, kod))
                ok = False
                continue
            if olay == "UserPromptSubmit":
                j = json.loads(out)
                metin = j["hookSpecificOutput"]["additionalContext"]
                if "DEVİR YÜKÜMLÜLÜĞÜ" not in metin:
                    print("[3] %-16s: ✗ enjeksiyon metni beklenen değil" % olay)
                    ok = False
                    continue
                print("[3] %-16s: ✓ devir enjeksiyonu üretiliyor" % olay)
            else:
                print("[3] %-16s: ✓ exit 0" % olay)
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
