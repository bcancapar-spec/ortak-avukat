# Yapısal Sıçrama Notu — dava-başına alet mi, hafızalı büro mu?

**Durum: FİKİR KAYDI. Uygulanmadı, v0.5.10'a girmedi.** Bu belge ileride
yapılabilecek bir mimari değişikliği ve — daha önemlisi — bugün neden
*yapılmadığını* kayda geçirir. Depoda uygulanan işler için
[YOL-HARITASI.md](YOL-HARITASI.md) ve [STATUS.md](STATUS.md) geçerlidir.

---

## 1. Soru

v0.5.9'a gelindiğinde sistemin mekanik iskeleti tamamlanmıştı: deterministik
kapılar ateşliyor, hook katmanı altı kanalda canlı, teslim zinciri yeşil makbuz
kesiyor, içtihat tam metin okunup damgalanıyor. Bunun üzerine soru şu oldu:
**sıradaki adım bir onarım listesi mi, yoksa sistemin şeklini değiştiren bir
sıçrama mı?**

"Yapısal" ölçütü baştan sert tutuldu: yeni bir kapı, yeni bir bayrak veya bir
hata düzeltmesi yapısal sayılmaz. Yapısal olan, **aletin ne olduğunu**
değiştirendir.

## 2. Tespit — ölçülmüş, tahmin değil

Bugünkü şekil: **dava başına çalışan bir alet.** Klasör gösterilir, hat koşar,
dilekçe çıkar, iş biter. Sonraki dava sıfırdan başlar. Biriken tek şey depodaki
koddur; avukatın kendi ürettiği muhakeme hiçbir yerde birikmez.

İki ölçülmüş olgu bu tespiti besledi:

- **Kalite ölçülmüyor.** Bir saha koşusunda bütün mekanik kapılar geçtiği hâlde
  avukat çıktıyı reddetti. Kapılar biçim, künye, unsur ve iz denetler; hiçbiri
  içeriğin iyi olup olmadığını ölçmez — ölçemez de, çünkü doktrin "hüküm veren
  makine" yasaklar. Sonuç: **ret gerekçesi hiçbir artefakta yazılmadı ve
  kayboldu.** Bu geri döndürülemez bir kayıptır; aynı ret bir daha üretilemez.
- **Muhakeme kapanışta buharlaşıyor.** Bir başka koşuda 45 Yargıtay kararı tam
  metin okunup damgalandı, yaklaşık 500 bin token harcandı, güçlü bir cephe
  seti kuruldu — hepsi dava klasöründe kaldı. Aynı türden bir sonraki dava aynı
  okumayı sıfırdan yapar ve aynı bağlantıları yeniden keşfetmek zorundadır.

## 3. Panel — beş bağımsız lens, tek fikir

Fikir tek bir kafadan çıkmasın diye beş bağımsız hakem, beş ayrı lensten
(avukat pratiği, mimari şekil, ölçüm/kalibrasyon, kapı ekleyerek çözülemeyen
sınıf, ölçek kırılması) sıçrama önerdi; her öneri ayrıca adversaryal denetimden
geçirildi ve bir hakem hepsini sentezledi.

Beş lens **aynı fikrin beş anlatımına** çıktı: *dava-başına amnezik hattan,
hafızası ve geri besleme döngüsü olan büroya geçiş.* Ama sentez fikri dört ayrı
bileşene ayırdı ve ikisini eledi:

| Bileşen | Panel hükmü |
|---|---|
| **(A) Avukat hükmü sensörü** — teslimden sonra KABUL / REVİZYONLA-KABUL / RET kaydı | **Yapısal — kalır.** Makine kalite skoru üretemeyeceğine göre, meşru tek kalite sinyali avukatın kayıt altına alınmış hükmüdür. |
| **(B) Muhakeme cephaneliği** — damga gerekçelerinin ve soyut örüntülerin davalar-arası taşınması | **Yapısal — ama aşağıdaki karara takılır.** |
| **(C) Sonuç defteri** — mahkeme kararının argüman karnesine dönmesi | **Elendi.** Gerekçeli karar aylar/yıllar sonra gelir, çok nedenlidir; tek kişilik büroda hücreler yıllarca n=1 kalır. |
| **(D) İçtihat kasası** — ham tam metin önbelleği | **Elendi.** Tam okuma ve yeniden teyit korunduğunda kazanç yalnız ağ gecikmesidir; buna karşılık deponun en tanıdık arıza sınıfını (bayat kopya) büro ölçeğine taşır. |

## 4. Avukatın kararı — sıfırdan başlamak bilinçli tercihtir

Panelin (B) bileşeni, yani önceki davanın muhakemesini yenisine taşımak,
**avukat kararıyla park edildi.** Gerekçesi şudur ve teknik değil, mesleki bir
gerekçedir:

> Dil modelleri henüz optimum seviyede değil. Model hazır bir cephanelikle
> başlatılırsa, yeni dosyanın kendi olgusundan muhakeme etmek yerine önceki
> davanın çerçevesini bu dosyaya giydirme riski taşır — desen eşleştirme,
> muhakemenin yerine geçer. Her dosya kendi vakıası, kendi delili ve kendi usul
> durumuyla değerlendirilmelidir.

Bu, sistemin bir eksiği olarak değil, **korunan bir tercih** olarak kayda
geçmiştir. Model güvenilirliği bu riski taşıyacak düzeye geldiğinde yeniden
değerlendirilecektir.

Not: panelin (B) için saydığı iki bağımsız risk bu kararı ayrıca destekler —
süzgecin tek yanlış-negatifi müvekkil verisini kalıcı bir köke yazar, ve
"geçen dava lehimizeydi" refleksi taze teyidi atlatabilir.

## 5. Süzgeçten geçen tek halka

Panelin (A) bileşeni park kararının dışında kalır, çünkü **ölçüm yapar,
enjeksiyon yapmaz.** Avukatın kendi hükmünü kaydetmek, yeni bir dosyaya
önceki davadan hiçbir şey taşımaz; yalnız bugün kaybolan bir sinyali tutar.

Panelin tarif ettiği hâliyle: teslimden sonra taslağın özetine bağlı tek bir
satır — kabul mü, revizyonla mı, ret mi; ve kapalı listeden bir sebep (olgu,
üslup, strateji, eksik, fazla). **Kapı değildir**; hükümsüz kapanış
engellenmez, yalnız görünür bir sayaç düşer.

Panelin bu öneriye kendi koyduğu şart, deponun geçmiş dersleriyle birebir
örtüştüğü için burada aynen korunur: eğer avukat refleksle "kabul" basmaya
başlarsa sinyal ölür ve alan, ateşlemeyen kapı kuralı gereği **silinmeyi hak
eder.** O yüzden başarı ölçütü baştan tektir: kaç teslime gerçekten hüküm
düştüğü. Oran düşükse üstüne hiçbir katman inşa edilmez.

## 6. Bu belge ne değildir

Bir taahhüt değildir. (A) halkasının de bir sürüme girip girmeyeceği ayrı bir
karardır. (B), (C) ve (D) bugün için kapalıdır. Belge, ileride aynı soru
sorulduğunda tartışmanın sıfırdan başlamaması için vardır — ve özellikle
**neden yapılmadığının** kaydı olduğu için değerlidir.
