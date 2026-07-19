# Yeni oa- Parçası İskeleti — oa-usta referansı

Damıtılan her yeni skill bu iskeleti izler. Aile tutarlılığını korur.

## SKILL.md iskeleti

```markdown
---
name: oa-XXX
description: >
  Ortak Avukat sisteminin [ROL] parçası. [Ne yaptığı — 1-2 cümle].
  "[tetik cümlesi 1]", "[tetik cümlesi 2]", "[tetik cümlesi 3]" türü her işte —
  kullanıcı açıkça istemese bile [bağlam] olduğunda — tetikle. Bağımsız çalışır;
  [ilgili oa- parçaları] ile takım oynar.
  # NOT: description < 1024 karakter olmalı (paketleme limiti).
---

# oa-XXX — [Tam ad]

[Parçanın neden var olduğu — 2-3 cümle. Hangi boşluğu doldurur.]

## İş bölümü (varsa script)
- Modelin işi (muhakeme): ...
- Scriptin işi (garantör): ... `scripts/XXX.py`
- Yine modelin işi (yorum): ...
# Sahte kesinlikten kaçın: script karar VERMEZ, yapısal/hesaplanabilir kontrolü yapar.

## Akış
1. ...
2. ... (varsa: `python scripts/XXX.py girdi.json`)
3. ...

## Diğer parçalara entegrasyon
- oa-YYY → ...

## Anayasal süzgeç
Çıktı karar materyalidir, karar değildir. Norm/içtihat resmî kaynaktan (Yargı/Mevzuat
MCP) teyitlidir. Nihai karar ve sorumluluk Av. Bayram Can Çapar'a aittir.
```

## Dizin yapısı
```
oa-XXX/
├── SKILL.md          (zorunlu)
├── scripts/          (deterministik garanti gerekiyorsa)
│   └── XXX.py
└── references/       (doktrin, şema, şablon)
    └── XXX-rehberi.md
```

## Script yazım disiplini
- Başına felsefe yorumu: "script karar vermez, yapısal/hesaplanabilir kontrolü yapar."
- Türkçe, okunur çıktı; otomasyon için anlamlı çıkış kodu.
- Girdi JSON şeması references'ta belgeli.
- Test: gerçek bir dosya senaryosuyla çalıştır, çıktının hukuken anlamlı olduğunu doğrula.

## Paketleme
```bash
# skill-creator'ı yazılabilir yere kopyala, sonra:
python -m scripts.package_skill /path/oa-XXX
```
Description 1024 karakteri aşarsa paketleme reddeder — kısalt.

## Kontrol
Paketlemeden önce oa-kontrol skill-güvenlik denetimi: injection deseni yok, yetki
iddiası yok, izinsiz dosya/shell erişimi yok, anayasal süzgeç var.
