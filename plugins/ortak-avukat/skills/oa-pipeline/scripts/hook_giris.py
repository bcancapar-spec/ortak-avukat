#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
hook_giris.py — HOOK GİRİŞ BETİĞİ (bytecode önbelleği kapısı)

NEDEN VAR (v0.5.16.2 performans onarımı)
----------------------------------------
Python, `__main__` olarak koşturulan bir betiğin bytecode'unu ASLA önbelleğe
almaz. `__pycache__` yalnızca IMPORT EDİLEN modüller için çalışır. Hook ağı
`pipeline_kayit.py`'yi (6300+ satır) doğrudan `python pipeline_kayit.py
--hook-...` diye çağırdığı için, o dosya HER hook ateşlemesinde SIFIRDAN
DERLENİYORDU. Bir tur içinde onlarca kez.

ÖLÇÜM (Python 3.12, 20 çağrı, çıplak yorumlayıcı başlığı çıkarılmış net yük):
  doğrudan `__main__`  (derleme her seferinde) :  67.6 ms
  bu betik üzerinden   (.pyc önbelleğinden)    :  26.3 ms
  → ~41 ms / hook kazanç.

NASIL ÇALIŞIR
-------------
`pipeline_kayit.py`'yi `importlib.util.spec_from_file_location` ile IMPORT
eder (deponun `_oa_hafiza_modulu_beyaz_liste` deseninin aynısı) ve `main()`'i
çağırır. Import olduğu için Python bytecode'u `__pycache__/` içine yazar ve
sonraki çağrılarda oradan okur. Bytecode geçerliliğini Python kaynağın
mtime+boyutundan KENDİ doğrular — bayat `.pyc` mümkün değildir, eklenti
güncellendiğinde otomatik yeniden derlenir.

`sys.path` KİRLETİLMEZ: dizin `sys.path`'e eklenmez, bu yüzden kardeş bir
dosya ileride bir standart kütüphane adını (`json.py`, `time.py`…) gölgeleyip
sistemi gizemli biçimde bozamaz.

`pipeline_kayit.py` DOĞRUDAN da koşmaya devam eder (`__main__` kapısı
yerinde): 90'dan fazla test onu yol ile çağırıyor, CLI kullanımı değişmedi.
Bu betik yalnızca hook yolunun önüne konan bir GİRİŞTİR.

ARIZA EMNİYETİ (447 dersinin gereği: hook ASLA sessizce ölmez, ASLA bloklamaz)
-----------------------------------------------------------------------------
Import yolu herhangi bir sebeple çökerse (bozuk `__pycache__`, salt-okunur
dizin, beklenmeyen importlib davranışı) betik SESSİZCE ESKİ YOLA döner:
`runpy` ile `pipeline_kayit.py`'yi `__main__` olarak koşturur. Yani en kötü
durumda ESKİ HIZ elde edilir, işlev KAYBEDİLMEZ. O da olmazsa çıkış kodu 0'dır
— bir performans katmanı, hukuki iş akışını asla durdurmaz.

ÇIKIŞ KODLARI KORUNUR: `main()` içindeki `sys.exit(...)` çağrıları `SystemExit`
fırlatır; `except Exception` bunu YAKALAMAZ (SystemExit BaseException'dır).
`--denetle`'nin exit 1'i ve PreToolUse kapılarının bloklama sinyali aynen geçer.

Kullanım (run-hook.cmd tarafından çağrılır; elle çağırmaya gerek yok):
  python hook_giris.py --hook-prompt
"""
import sys as _sys

# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler.
# (pipeline_kayit.py de aynısını yapar; burada da olması, import'tan ÖNCE
# oluşabilecek bir hata mesajının konsolu çökertmemesini sağlar.)
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import importlib.util
import os
import sys

_BETIK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_kayit.py")


def _eski_yol():
    """YEDEK: pipeline_kayit.py'yi `__main__` olarak koştur (v0.5.16.2 öncesi
    davranış). Yavaş ama BİREBİR aynı işlev — performans katmanı çökse bile
    hukuki iş akışı kesintisiz sürer."""
    try:
        import runpy
        runpy.run_path(_BETIK, run_name="__main__")
    except SystemExit:
        raise                      # çıkış kodu KORUNUR (--denetle exit 1 vb.)
    except Exception:
        sys.exit(0)                # hook ASLA bloklamaz


def main():
    if not os.path.isfile(_BETIK):
        sys.exit(0)                # eklenti yarım kurulmuş — sessizce çık, blokla

    # ÇİFT YAN ETKİ KAPISI (v0.5.16.3)
    # ---------------------------------
    # `exec_module` modül gövdesini YARIDA bırakan bir istisna atarsa
    # (bozuk __pycache__, disk hatası), yedek yol aynı dosyayı `runpy` ile
    # BAŞTAN koşturur. O zaman gövde KISMEN bir kez + TAM bir kez yürür.
    # BUGÜN bu güvenlidir, çünkü pipeline_kayit.py'nin modül seviyesi
    # YAN-ETKİSİZDİR (v0.5.16.2 ile DIZIN_BEYAZ_LISTE ataması tembel
    # erişimciye çevrildi; modül seviyesinde dosya yazımı yok). Ama bu
    # SESSİZ bir varsayımdı. Artık açık: yedek yola YALNIZCA gövde HİÇ
    # başlamadan çöken hatalarda düşülür. Gövde başladıktan sonraki bir
    # çökme, çift yan etki riskini almamak için OLDUĞU GİBİ yukarı bırakılır
    # (davranış eski yolla aynı: pipeline_kayit doğrudan koşarken de aynı
    # istisna aynı şekilde çıkardı).
    govde_basladi = False
    try:
        spec = importlib.util.spec_from_file_location("pipeline_kayit", _BETIK)
        if spec is None or spec.loader is None:
            return _eski_yol()
        mod = importlib.util.module_from_spec(spec)
        # exec_module'dan ÖNCE kaydet: modülün kendine referanslı import'ları
        # ve `sys.modules` bekleyen kodu doğru çalışsın.
        sys.modules["pipeline_kayit"] = mod
        govde_basladi = True
        spec.loader.exec_module(mod)      # <- burada __pycache__ okunur/yazılır
        govde = getattr(mod, "main", None)
        if not callable(govde):
            return _eski_yol()            # gövde bitti, yan etki yok — güvenli
    except SystemExit:
        raise                      # modül gövdesi sys.exit çağırdıysa: koru
    except Exception:
        if govde_basladi:
            # Gövde çalışmaya başlamıştı: runpy ile TEKRAR koşturmak yan
            # etkileri ikiye katlayabilir. Bunu YAPMA — hatayı olduğu gibi
            # bırak. sys.modules'ü de temizle ki yarım modül geride kalmasın.
            sys.modules.pop("pipeline_kayit", None)
            raise
        return _eski_yol()         # import katmanı hiç başlamadan çöktü
    govde()                        # SystemExit buradan doğal olarak yayılır


if __name__ == "__main__":
    main()
