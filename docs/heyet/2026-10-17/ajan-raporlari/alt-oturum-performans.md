# Ajan raporu — performans alt oturumu: v0.5.19 adayı çapraz denetim sonuç önbelleği

**Commit'ler:** `d996f62` (ad66357'nin `61b8e14` üzerine yeniden temellendirilmişi; yazar, tarih, mesaj aynen) ve
`6801ac7` (kayıtlar) · **Model:** Opus 5.5 (commit trailer buna göre) · **Push/PR:** alt oturum onaya bıraktı; orkestra
dalı doğrudan denetim dalına birleştirdi (`66b5d09`), alt oturumun worktree'si ve yerel dalı kaldırıldı. Bu dosya alt
oturumun dönüş raporundan çıkarılmış beyandır.

## Ne

`pipeline_kayit.py`: Stop kancasındaki B-2 çapraz denetiminin sonucu (`_capraz_bosluk_hesapla`) türetilmiş bir
önbellekte, `_oa/defter/.capraz-onbellek.json`'da tutulur; anahtar sha256 (üç girdi, damgalı denetim JSON'ları,
`capraz_denetim.py` ve `pipeline_kayit.py` özeti, yorumlayıcı küçük sürümü, şema). Fail-closed: önbellek hatası boş
"temiz" sonuç üretemez; bozuk/yabancı anahtarlı dosya ıska; dedup parmak izine girmez; `_oa/defter` yaratılmaz;
append-only deftere dokunulmaz; yazım tmp + `os.replace`. `tests/test_v0519_capraz_onbellek.py` (37; önce kırmızı:
eski motorla 36 kırmızı / 1 yeşil — `test_defter_yoksa_onbellek_yazilmaz_ve_defter_yaratilmaz`; dosya bayt-özdeş geri
yüklendi). `docs/PERFORMANS-STATUS.md` §14 (bu dalda §13 v0.5.18 eksikler turuna aitti; taşınan commit'in mesajındaki
"§13" artık §14'tür — §14.9 ve CHANGELOG'da not), CLAUDE.md değişmez #7.

## Çatışma çözümü (rebase)

İki README künyesi ve `tests/README.md` → `61b8e14` sürümü alınıp `--continue` öncesi yeniden türetildi; satır
sonları korundu (çalışma ağacı CRLF, indeks LF). `CLAUDE.md` ve `pipeline_kayit.py` otomatik birleşti
(`py_compile` temiz; değişiklik kümesi ad66357 ile satır satır aynı).

## Kapılar (alt oturum worktree'si, Python 3.14.8, HEAD `6801ac7`)

| Kapı | Sonuç |
|---|---|
| Hedefli (37 + 18 + 12) | 67 geçti |
| Tam süit `-n auto -m "not perf"` | 3840 geçti · 12 atlandı · 0 kırmızı (`d996f62`'de de aynı) |
| perf | 1 geçti, 3852 seçim dışı |
| ruff | All checks passed! |
| aile_dogrula | TEMİZ (20 parça) |
| OA-SUIT-SAYISI | 3816 → 3853 (collect-only 3853); künye test 61.000+, toplam 126.000+, 3.853 test |
| `hook_olc --gercekci --tekrar 3 --karsilastir --import-dokumu` (compileall sonrası, tek ağaç, A/B tabanı yok) | ortanca ms: prompt 71,2 (doğrudan 111,0) · pretool 64,0 (106,5) · postwrite 94,6 (136,2) · denetle 96,0 (138,2) · açılış 67,4 (106,2); bileşik 158,6 ms; ağır modül YOK (102 import) |

## Doğrulanamayanlar (alt oturum)

UDF yazıcısına bağlı 11 test ve saha referansına bağlı 1 test koşmadı; Python 3.12 koşulmadı; ölçek kökü ABBA ölçümü
(§14.3–14.6) ve 21/21 mutasyon kanıtı bu dalda tekrarlanmadı; hook_doktor ve CI görülmedi. Kural dışı tek adım: bir
kez `git ls-remote` (salt okuma; uzak dal yoktu).
