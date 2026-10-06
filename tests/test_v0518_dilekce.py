# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — İCRA DİLEKÇE AİLESİ + Y-06 DİLEKÇE KAPISI SIKILAŞTIRMASI.

Saha kanıtı / gerekçe:
  * 3 Ekim 2026 yetenek denetimi (Yargı PRO ile), bulgu Y-06: dava değeri ayrı
    unsur değil; bileşik unsurda tek desen yetiyor; idari dava (İYUK m.3/2) ve
    ceza istinafı tipi yok.
  * 5 Ekim 2026 Yargı PRO 107-skill analizi: OA'nın dilekçe kapısında icra tipi
    YOK (3-3 takip başlatma, 3-4 takibe itiraz, 3-5 haciz/satış, 3-8 icra ceza,
    3-9 usul işlemleri "yok"; 3-1, 3-6, 3-7 "kısmen"). Fikir alındı, metin/kod
    alınmadı; her madde Yargı PRO MCP `mevzuat_getir` ile resmî metinden
    2026-10-05'te okundu (künyeler: oa-dilekce/references/icra-dilekce-ailesi.md,
    references/idari-ceza-tipleri.md).

Kilitlenen sözleşmeler:
  1. Her yeni tip için TAM sentetik taslak [A]'dan ve [D]'den TEMİZ geçer (CLI
     exit 0); bir zorunlu unsuru eksik taslak RED alır (CLI exit 1) ve eksik
     unsur adıyla raporlanır.
  2. Bileşik unsurda her parça ayrı aranır; eksik parça adıyla görünür.
  3. Yakınlık parçası: alacaklının adresi borçlunun adres eksiğini örtmez.
  4. Yeni taraf sıfatları (alacakli/borclu/ucuncu-kisi) birinci ağızdan icra
     ikrarlarını yakalar; olumsuz/amaç cümlesi sinyal üretmez; menfi tespitte
     borçlu DAVACI konumunda taranır.
  5. [S] SÜRE BAĞLANTISI süre HESAPLAMAZ; oa-sure kural kimliğini çalışma
     anında bulur, yoksa TEYİT BEKLİYOR der; asla bloklamaz.
  6. Eski `dava` tipinde dava değeri ve taraf adres/TCKN'si İSTİŞARİDİR (exit
     kodu değişmez — mevcut kilit testler korunur).
  7. Süre başlangıcının TARİHİ olayın yanında aranır (imza tarihi tebliğ
     tarihini örtmez); süre İFADESİ zorunlu değildir; "tebliğ edilmemiştir"
     beyanı tarih unsurunu kaldırır (Fable 5.1 salt okunur incelemesi).
  8. `(?#kesin)` kalıplar çekimli olumlu ikrarı NEG penceresine rağmen
     yakalar; ortaç/olumsuz çekim yakalanmaz. Kambiyoda kısmi kabul ayrıca
     taranır (İİK m.170/a-3); haciz ihbarnamesine itirazda üçüncü kişinin
     dürüst borç beyanı BLOK değil uyarıdır (İİK m.89/4, m.338/1).

Testler deterministiktir: bugünün tarihine, ağa/MCP'ye, rastgeleliğe, yerel
yola ve süre ölçümüne bağlı doğrulama YOKTUR (tarihler sabit, metinler kurgu).

Anayasa m.7: bütün kişi, unvan, dosya numarası ve adresler kurgudur.
"""
import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
SCRIPT = SKILL / "scripts" / "dilekce_denetim.py"
REF_ICRA = SKILL / "references" / "icra-dilekce-ailesi.md"
REF_IDARI = SKILL / "references" / "idari-ceza-tipleri.md"


def _load():
    assert SCRIPT.is_file(), f"dilekce_denetim.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("dilekce_denetim_v0518", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()

YENI_TIPLER = [
    "takip-talebi", "odeme-emrine-itiraz", "kambiyo-itiraz", "gecikmis-itiraz",
    "itirazin-kaldirilmasi", "itirazin-iptali", "menfi-tespit", "haciz-talebi",
    "satis-talebi", "haciz-ihbarnamesi-itiraz", "kiymet-takdiri-sikayet",
    "ihalenin-feshi", "icra-sikayet", "istihkak-davasi", "icra-ceza-sikayet",
    "icra-usul", "idari-dava", "yd-talebi", "ceza-istinaf",
]


def _imza(tarih, sifat):
    return f"\n{tarih}\n{sifat} Vekili Av. Test Vekil\nimza\n"


# ═══════════════════════════════════════════════════════════════════════════
# SENTETİK TAM TASLAKLAR — her biri tipinin bütün zorunlu unsurlarını taşır
# ═══════════════════════════════════════════════════════════════════════════
TAM = {
    "takip-talebi": (
        "# ÖRNEK 3. İCRA DAİRESİ'NE\n\n"
        "TAKİP TALEBİ\n\n"
        "ALACAKLI : Örnek Ticaret A.Ş., VKN: [sentetik], Adres: Örnek Mah. Deneme Sok. No:1 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil, Örnek Barosu\n"
        "ÖDEME HESABI : Örnek Bankası, IBAN: [sentetik] (alacaklı vekili adına)\n"
        "BORÇLU : Mehmet Örnek, Adres: Deneme Mah. Örnek Cad. No:2 Örnekşehir\n\n"
        "ALACAK : 10.000,00 TL asıl alacak; asıl alacağa takip tarihinden itibaren işleyecek yasal faiz.\n"
        "BORCUN SEBEBİ : 01.01.2026 tarihli sözleşmeden doğan hizmet bedeli.\n"
        "TAKİP YOLU : İlamsız takip (genel haciz yolu).\n\n"
        "## TALEP\n"
        "Yukarıda gösterilen alacak için borçlu hakkında ilamsız takip yapılmasını ve ödeme emri "
        "gönderilmesini talep ederim.\n\n"
        "EKLER: 1- Sözleşme aslı ve borçlu sayısından bir fazla onaylı örneği\n"
        + _imza("01.02.2026", "Alacaklı")),
    "odeme-emrine-itiraz": (
        "# ÖRNEK 3. İCRA DAİRESİ'NE\n\n"
        "DOSYA NO : 2024/123 Esas\n"
        "BORÇLU (İTİRAZ EDEN) : Mehmet Örnek, yurt içi adres: Deneme Mah. Örnek Cad. No:2 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "ALACAKLI : Örnek Ticaret A.Ş.\n"
        "KONU : Ödeme emrine itirazlarımızdır.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Müvekkile 10.01.2026 tarihinde tebliğ edilen ödeme emrine yasal yedi günlük süre içinde "
        "itiraz ediyoruz.\n"
        "2. Müvekkilin alacaklıya herhangi bir borcu bulunmamaktadır; borca, faize ve tüm ferilerine "
        "itiraz ediyoruz.\n\n"
        "## SONUÇ VE İSTEM\n"
        "Süresinde yapılan itirazımız gereğince takibin durdurulmasını saygıyla talep ederiz.\n"
        + _imza("15.01.2026", "Borçlu")),
    "kambiyo-itiraz": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "İTİRAZ EDEN (BORÇLU) : Mehmet Örnek, Adres: Deneme Mah. No:2 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "KARŞI TARAF (ALACAKLI) : Örnek Ticaret A.Ş.\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : Kambiyo senetlerine mahsus haciz yoluyla başlatılan takipte borca itiraz ve takibin "
        "geçici olarak durdurulması istemidir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Müvekkile 10.01.2026 tarihinde tebliğ edilen ödeme emrine beş günlük süre içinde borca "
        "itiraz ediyoruz.\n"
        "2. Takibe konu bono bedeli 05.01.2026 tarihinde ödenmiştir; ödeme dekontu ve alacaklının "
        "imzasını taşıyan makbuz ektedir.\n"
        "3. İtiraz satış dışındaki takip işlemlerini kendiliğinden etkilemediğinden, ekli belgeler "
        "karşısında takibin geçici olarak durdurulmasına karar verilmesi gerekir.\n\n"
        "## DELİLLER\nÖdeme dekontu, imzalı makbuz, takip dosyası.\n\n"
        "## SONUÇ VE İSTEM\n"
        "1. Takibin itirazımız hakkında karar verilinceye kadar geçici olarak durdurulmasına,\n"
        "2. Borca itirazımızın kabulü ile takibin iptaline,\n"
        "3. Alacaklının kötü niyet tazminatına mahkûm edilmesine karar verilmesini talep ederiz.\n"
        + _imza("16.01.2026", "Borçlu")),
    "gecikmis-itiraz": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "DAVACI (BORÇLU) : Mehmet Örnek, Adres: Deneme Mah. No:2 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI (ALACAKLI) : Örnek Ticaret A.Ş.\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : İİK m.65 uyarınca gecikmiş itirazımızdır.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Müvekkil, ödeme emrinin tebliğ edildiği dönemde hastanede yatmış olup itirazı süresinde "
        "yapamaması kendi kusuru olmaksızın gerçekleşmiştir.\n"
        "2. Bu mazeret 20.01.2026 tarihinde taburcu olmasıyla sona ermiş; işbu itiraz maninin "
        "kalktığı günden itibaren üç gün içinde yapılmaktadır.\n"
        "3. Müvekkilin alacaklıya borcu bulunmamaktadır; borca ve tüm ferilerine itiraz ediyoruz.\n"
        "4. Duruşmaya ilişkin harç ve masraflar işbu dilekçe ile birlikte yatırılmıştır.\n\n"
        "## DELİLLER\nHastane epikriz raporu, taburcu belgesi.\n\n"
        "## SONUÇ VE İSTEM\n"
        "Mazeretin kabulü ile takibin durdurulmasına ve itirazımızın kabulüne karar verilmesini "
        "talep ederiz.\n"
        + _imza("22.01.2026", "Borçlu")),
    "itirazin-kaldirilmasi": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "DAVACI (ALACAKLI) : Örnek Ticaret A.Ş., Adres: Örnek Mah. No:1 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI (BORÇLU) : Mehmet Örnek, Adres: Deneme Mah. No:2 Örnekşehir\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : İİK m.68 uyarınca itirazın kesin olarak kaldırılması istemidir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Borçlunun ödeme emrine itirazı müvekkile 10.02.2026 tarihinde tebliğ edilmiş olup işbu "
        "istem altı aylık süre içindedir.\n"
        "2. Takip, noterce onaylanmış borç ikrarını içeren senede dayanmaktadır; borçlu itirazını "
        "haklı gösterecek hiçbir belge sunmamıştır.\n\n"
        "## DELİLLER\nNoter onaylı borç ikrarı senedi, takip dosyası.\n\n"
        "## SONUÇ VE İSTEM\n"
        "1. Borçlunun itirazının kesin olarak kaldırılmasına ve takibin devamına,\n"
        "2. Borçlunun alacağın yüzde yirmisinden aşağı olmamak üzere icra inkâr tazminatına mahkûm "
        "edilmesine,\n"
        "3. Yargılama giderleri ve vekâlet ücretinin borçluya yükletilmesine karar verilmesini talep "
        "ederiz.\n"
        + _imza("20.02.2026", "Alacaklı")),
    "itirazin-iptali": (
        "# ÖRNEK 4. ASLİYE TİCARET MAHKEMESİ'NE\n\n"
        "DAVACI : Örnek Ticaret A.Ş., VKN: [sentetik], Adres: Örnek Mah. No:1 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI : Mehmet Örnek, Adres: Deneme Mah. No:2 Örnekşehir\n"
        "DAVA DEĞERİ : 10.000,00 TL\n"
        "KONU : İİK m.67 uyarınca itirazın iptali ve icra inkâr tazminatı istemidir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Müvekkil tarafından davalı aleyhine Örnek 3. İcra Dairesi 2024/123 Esas sayılı dosyasıyla "
        "ilamsız takip başlatılmıştır.\n"
        "2. Davalının itirazı müvekkile 10.02.2026 tarihinde tebliğ edilmiş olup dava bir yıllık süre "
        "içinde açılmıştır.\n"
        "3. Taraflar arasındaki ticari ilişki faturalarla sabittir; zorunlu arabuluculuk görüşmesi "
        "anlaşmazlıkla sonuçlanmış, son tutanak ektedir.\n\n"
        "## HUKUKİ SEBEPLER\nİİK m.67, TTK m.5/A ve ilgili mevzuat.\n\n"
        "## DELİLLER\nFaturalar, ticari defterler, arabuluculuk son tutanağı, takip dosyası.\n\n"
        "## NETİCE-İ TALEP\n"
        "1. Davalının itirazının iptali ile takibin devamına,\n"
        "2. Davalının alacağın yüzde yirmisinden az olmamak üzere icra inkâr tazminatına mahkûm "
        "edilmesine,\n"
        "3. Yargılama giderleri ve vekâlet ücretinin davalıya yükletilmesine karar verilmesini talep "
        "ederiz.\n"
        + _imza("01.03.2026", "Davacı")),
    "menfi-tespit": (
        "# ÖRNEK 5. ASLİYE HUKUK MAHKEMESİ'NE\n\n"
        "DAVACI : Mehmet Örnek, T.C. Kimlik No: [sentetik], Adres: Deneme Mah. No:2 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI : Ayşe Örnek, Adres: Örnek Mah. No:3 Örnekşehir\n"
        "DAVA DEĞERİ : 10.000,00 TL\n"
        "KONU : İİK m.72 uyarınca borçlu olunmadığının tespiti istemidir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Davalı tarafından Örnek 3. İcra Dairesi 2024/123 Esas sayılı dosyasıyla müvekkil aleyhine "
        "takip yapılmıştır.\n"
        "2. Takibe dayanak gösterilen senet bedelsiz olup müvekkil davalıya borçlu değildir.\n\n"
        "## HUKUKİ SEBEPLER\nİİK m.72 ve ilgili mevzuat.\n\n"
        "## DELİLLER\nBanka kayıtları, tanık, yemin.\n\n"
        "## NETİCE-İ TALEP\n"
        "1. Davanın kabulü ile takip konusu senet nedeniyle müvekkilin davalıya borçlu olmadığının "
        "tespitine,\n"
        "2. Yüzde on beş teminat karşılığında icra veznesindeki paranın davalıya ödenmemesi yönünde "
        "ihtiyati tedbir kararı verilmesine,\n"
        "3. Davalının kötü niyet tazminatına mahkûm edilmesine,\n"
        "4. Yargılama giderleri ve vekâlet ücretinin davalıya yükletilmesine karar verilmesini talep "
        "ederiz.\n"
        + _imza("01.03.2026", "Davacı")),
    "haciz-talebi": (
        "ÖRNEK 3. İCRA DAİRESİ'NE\n\n"
        "DOSYA NO : 2024/123 Esas\n"
        "ALACAKLI : Örnek Ticaret A.Ş.\n"
        "VEKİLİ : Av. Test Vekil\n"
        "BORÇLU : Mehmet Örnek\n\n"
        "KONU : Haciz talebimizdir.\n\n"
        "Takip kesinleşmiştir. Borçlunun adına kayıtlı taşınmazlar ile bankalardaki hak ve "
        "alacakları üzerine haciz konulmasını talep ederim.\n"
        + _imza("01.04.2026", "Alacaklı")),
    "satis-talebi": (
        "ÖRNEK 3. İCRA DAİRESİ'NE\n\n"
        "DOSYA NO : 2024/123 Esas\n"
        "ALACAKLI : Örnek Ticaret A.Ş.\n"
        "VEKİLİ : Av. Test Vekil\n"
        "BORÇLU : Mehmet Örnek\n\n"
        "KONU : Satış talebimizdir.\n\n"
        "Borçlu adına kayıtlı sentetik plakalı araç üzerine 01.03.2026 tarihinde haciz konulmuştur. "
        "Aracın muhafaza altına alınmasını, kıymet takdirinin yapılmasını ve satışının yapılmasını "
        "talep ederim. Muhafaza, kıymet takdiri ve satış giderleri peşin olarak yatırılmıştır.\n"
        + _imza("01.04.2026", "Alacaklı")),
    "haciz-ihbarnamesi-itiraz": (
        "ÖRNEK 3. İCRA DAİRESİ'NE\n\n"
        "DOSYA NO : 2024/123 Esas\n"
        "İTİRAZ EDEN (ÜÇÜNCÜ KİŞİ) : Örnek Lojistik Ltd. Şti.\n"
        "VEKİLİ : Av. Test Vekil\n\n"
        "KONU : Birinci haciz ihbarnamesine itirazımızdır.\n\n"
        "Müvekkile 05.04.2026 tarihinde tebliğ edilen birinci haciz ihbarnamesine yedi günlük süre "
        "içinde itiraz ediyoruz. Müvekkilin borçluya herhangi bir borcu bulunmamaktadır; borçluya ait "
        "hiçbir mal da müvekkilin yedinde bulunmamaktadır.\n\n"
        "İtirazımızın kabulü ile kayda alınmasını talep ederiz.\n"
        + _imza("08.04.2026", "Üçüncü Kişi")),
    "kiymet-takdiri-sikayet": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "ŞİKÂYET EDEN (BORÇLU) : Mehmet Örnek, Adres: Deneme Mah. No:2 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "KARŞI TARAF (ALACAKLI) : Örnek Ticaret A.Ş.\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : Kıymet takdirine şikâyetimizdir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Haczedilen taşınmaza ilişkin kıymet takdiri raporu müvekkile 10.04.2026 tarihinde tebliğ "
        "edilmiş olup şikâyet yedi günlük süre içindedir.\n"
        "2. Raporda belirlenen değer, bölgedeki emsal satışların ve gerçek piyasa değerinin çok "
        "altındadır; düşük takdir müvekkili zarara uğratacaktır.\n"
        "3. Yeniden bilirkişi incelemesi yapılması için gereken masraf ve ücret, şikâyet tarihinden "
        "itibaren yedi gün içinde mahkeme veznesine yatırılacaktır.\n\n"
        "## SONUÇ VE İSTEM\n"
        "Şikâyetimizin kabulü ile yeniden bilirkişi incelemesi yaptırılarak yeniden kıymet takdiri "
        "yapılmasına karar verilmesini talep ederiz.\n"
        + _imza("14.04.2026", "Borçlu")),
    "ihalenin-feshi": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "ŞİKÂYET EDEN (BORÇLU) : Mehmet Örnek, yurt içi adres: Deneme Mah. No:2 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "KARŞI TARAF : Örnek Ticaret A.Ş. (satış isteyen alacaklı) ve ihale alıcısı\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : 20.04.2026 tarihli ihalenin feshi istemidir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Müvekkil, takibin borçlusu sıfatıyla ihalenin feshini istemeye yetkilidir; işbu şikâyet "
        "ihale tarihinden itibaren yedi gün içinde yapılmaktadır.\n"
        "2. Satış ilanı müvekkile tebliğ edilmemiştir; ayrıca kıymet takdiri güncel değildir. Bu "
        "yolsuzluklar nedeniyle taşınmaz muhammen bedelin çok altında satılmış, müvekkilin menfaati "
        "zarara uğramıştır.\n\n"
        "## DELİLLER\nTakip dosyası, tebligat mazbataları.\n\n"
        "## SONUÇ VE İSTEM\nİhalenin feshine karar verilmesini talep ederiz.\n"
        + _imza("24.04.2026", "Borçlu")),
    "icra-sikayet": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "ŞİKÂYET EDEN (ALACAKLI) : Örnek Ticaret A.Ş., Adres: Örnek Mah. No:1 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : İcra dairesinin haciz talebimizi reddeden işlemine şikâyetimizdir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. İcra dairesinin 01.05.2026 tarihli işlemiyle haciz talebimiz reddedilmiştir; işlem "
        "müvekkile 03.05.2026 tarihinde tebliğ edilmiş olup şikâyet yedi günlük süre içindedir.\n"
        "2. İşlem kanuna aykırıdır.\n\n"
        "## SONUÇ VE İSTEM\nŞikâyet konusu işlemin iptaline karar verilmesini talep ederiz.\n"
        + _imza("06.05.2026", "Alacaklı")),
    "istihkak-davasi": (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "DAVACI (ÜÇÜNCÜ KİŞİ) : Ayşe Örnek, T.C. Kimlik No: [sentetik], Adres: Örnek Mah. No:3 "
        "Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI : Örnek Ticaret A.Ş. (alacaklı)\n"
        "DAVA DEĞERİ : 50.000,00 TL\n"
        "KONU : İİK m.97 uyarınca istihkak davamızdır.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Örnek 3. İcra Dairesi 2024/123 Esas sayılı dosyada 01.05.2026 tarihli haciz tutanağıyla "
        "müvekkile ait mallar haczedilmiştir.\n"
        "2. İcra mahkemesinin takibin devamına ilişkin kararı müvekkile 05.05.2026 tarihinde tebliğ "
        "edilmiş olup dava yedi günlük süre içinde açılmıştır.\n"
        "3. Mallar müvekkil tarafından faturayla satın alınmış olup borçlunun işyerinde emanet olarak "
        "bulunmaktadır.\n\n"
        "## DELİLLER\nSatış faturaları, emanet sözleşmesi, tanık.\n\n"
        "## SONUÇ VE İSTEM\n"
        "1. Davanın kabulü ile istihkak iddiamızın kabulüne ve haczin kaldırılmasına,\n"
        "2. Dava sonuna kadar takibin talikına karar verilmesini talep ederiz.\n"
        + _imza("08.05.2026", "Davacı")),
    "icra-ceza-sikayet": (
        "# ÖRNEK İCRA CEZA MAHKEMESİ'NE\n\n"
        "ŞİKÂYETÇİ (ALACAKLI) : Örnek Ticaret A.Ş.\n"
        "VEKİLİ : Av. Test Vekil\n"
        "SANIK (BORÇLU) : Mehmet Örnek, Adres: Deneme Mah. No:2 Örnekşehir\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n"
        "KONU : İİK m.340 uyarınca ödeme şartını ihlal eden borçlu hakkında şikâyetimizdir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Borçlu, icra dairesinde verdiği taahhütle borcu aylık taksitlerle ödemeyi üstlenmiştir.\n"
        "2. 15.04.2026 vadeli taksit ödenmemiş, böylece taahhüt ihlal edilmiştir; ihlal müvekkil "
        "tarafından 20.04.2026 tarihinde dosyanın incelenmesiyle öğrenilmiştir.\n\n"
        "## DELİLLER\nTaahhüt tutanağı, icra dosyası hesap dökümü.\n\n"
        "## SONUÇ VE İSTEM\nBorçlunun İİK m.340 uyarınca tazyik hapsine karar verilmesini talep "
        "ederiz.\n"
        + _imza("25.04.2026", "Alacaklı")),
    "icra-usul": (
        "ÖRNEK 3. İCRA DAİRESİ'NE\n\n"
        "DOSYA NO : 2024/123 Esas\n"
        "BORÇLU : Mehmet Örnek\n"
        "VEKİLİ : Av. Test Vekil\n"
        "KONU : İİK m.36 uyarınca tehir-i icra için süre talebimizdir.\n\n"
        "İlama karşı istinaf yoluna başvurulmuş olup hükmolunan para tutarında teminat mektubu "
        "dosyaya sunulmuştur. İİK m.36 uyarınca icranın geri bırakılması kararı alınmak üzere uygun "
        "süre tanınmasını talep ederiz.\n"
        + _imza("10.05.2026", "Borçlu")),
    "idari-dava": (
        "# ÖRNEK İDARE MAHKEMESİ BAŞKANLIĞI'NA\n\n"
        "DAVACI : Ayşe Örnek, T.C. Kimlik No: [sentetik], Adres: Örnek Mah. No:3 Örnekşehir\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI : Örnek Belediye Başkanlığı\n"
        "KONU : Yıkım kararının iptali ve yürütmenin durdurulması istemidir.\n"
        "DAVA KONUSU İŞLEMİN TEBLİĞ TARİHİ : 01.05.2026\n\n"
        "## AÇIKLAMALAR\n"
        "1. Dava konusu işlem yetki ve sebep yönlerinden hukuka aykırıdır.\n"
        "2. İşlem açıkça hukuka aykırı olup uygulanması hâlinde telafisi güç veya imkânsız zararlar "
        "doğacaktır.\n\n"
        "## HUKUKİ SEBEPLER\nİYUK m.2, m.27 ve ilgili mevzuat.\n\n"
        "## DELİLLER\nİdari dosya, keşif, bilirkişi incelemesi.\n\n"
        "## SONUÇ VE İSTEM\n"
        "1. Teminat alınmaksızın yürütmenin durdurulmasına,\n"
        "2. Dava konusu işlemin iptaline karar verilmesini talep ederiz.\n\n"
        "EKLER: 1- Dava konusu işlem örneği\n"
        + _imza("10.05.2026", "Davacı")),
    "yd-talebi": (
        "# ÖRNEK İDARE MAHKEMESİ BAŞKANLIĞI'NA\n\n"
        "DOSYA NO : 2026/45 Esas\n"
        "DAVACI : Ayşe Örnek\n"
        "VEKİLİ : Av. Test Vekil\n"
        "DAVALI : Örnek Belediye Başkanlığı\n"
        "KONU : Dava konusu işlem hakkında yürütmenin durdurulması istemimizdir.\n\n"
        "## AÇIKLAMALAR\n"
        "1. Dava konusu yıkım kararı açıkça hukuka aykırıdır.\n"
        "2. İşlemin uygulanması hâlinde yapı yıkılacağından telafisi güç veya imkânsız zararlar "
        "doğacaktır; zarar ekli keşif raporuyla sabittir.\n"
        "3. Davacı adli yardımdan yararlandığından teminat alınmaması gerekir.\n\n"
        "## SONUÇ VE İSTEM\n"
        "Teminatsız olarak yürütmenin durdurulmasına karar verilmesini talep ederiz.\n"
        + _imza("12.05.2026", "Davacı")),
    "ceza-istinaf": (
        "# ÖRNEK 2. AĞIR CEZA MAHKEMESİ'NE\n"
        "Gönderilmek üzere\n"
        "# ÖRNEK BÖLGE ADLİYE MAHKEMESİ İLGİLİ CEZA DAİRESİ'NE\n\n"
        "DOSYA : Esas No: 2025/10 — Karar No: 2026/20\n"
        "İSTİNAF EDEN (SANIK) : Mehmet Örnek\n"
        "MÜDAFİİ : Av. Test Vekil\n"
        "HÜKÜM : 10.03.2026 tarihli mahkûmiyet hükmü\n"
        "TEBLİĞ TARİHİ : 01.04.2026 (gerekçeli hükmün tebliği)\n\n"
        "## GİRİŞ\nHüküm iki dayanağa indirgenmektedir; ikisi de dosya kapsamıyla çelişmektedir.\n\n"
        "## İSTİNAF SEBEPLERİ\n"
        "1. Hükme esas alınan deliller hukuka aykırı biçimde elde edilmiştir.\n"
        "2. Eksik inceleme ile hüküm kurulmuştur.\n\n"
        "## SONUÇ VE İSTEM\n"
        "1. Hükmün kaldırılmasına,\n"
        "2. Sanığın beraatine karar verilmesini talep ederiz.\n"
        "\n10.04.2026\nSanık Müdafii Av. Test Vekil\nimza\n"),
}

TARAF = {
    "takip-talebi": "alacakli", "odeme-emrine-itiraz": "borclu", "kambiyo-itiraz": "borclu",
    "gecikmis-itiraz": "borclu", "itirazin-kaldirilmasi": "alacakli",
    "itirazin-iptali": "alacakli", "menfi-tespit": "borclu", "haciz-talebi": "alacakli",
    "satis-talebi": "alacakli", "haciz-ihbarnamesi-itiraz": "ucuncu-kisi",
    "kiymet-takdiri-sikayet": "borclu", "ihalenin-feshi": "borclu", "icra-sikayet": "alacakli",
    "istihkak-davasi": "ucuncu-kisi", "icra-ceza-sikayet": "alacakli", "icra-usul": "borclu",
    "idari-dava": "davaci", "yd-talebi": "davaci", "ceza-istinaf": "sanik",
}


def _cikar(metin, *parcalar):
    """Taslaktan verilen parçaları siler — her parça taslakta BULUNMALI
    (test, mutasyonun gerçekten uygulandığını kendisi kanıtlar)."""
    for p in parcalar:
        assert p in metin, f"mutasyon parçası taslakta yok (test kurgusu bozuk): {p!r}"
        metin = metin.replace(p, "")
    return metin


def _degistir(metin, eski, yeni):
    assert eski in metin, f"mutasyon parçası taslakta yok (test kurgusu bozuk): {eski!r}"
    return metin.replace(eski, yeni)


# Her yeni tip için: (bir zorunlu unsuru eksik taslak, eksik listesinde beklenen ad parçası)
EKSIK = {
    "takip-talebi": (
        _cikar(TAM["takip-talebi"],
               "ÖDEME HESABI : Örnek Bankası, IBAN: [sentetik] (alacaklı vekili adına)\n"),
        "Ödeme hesabı"),
    "odeme-emrine-itiraz": (
        _cikar(TAM["odeme-emrine-itiraz"],
               ", yurt içi adres: Deneme Mah. Örnek Cad. No:2 Örnekşehir"),
        "Borçlu + yurt içi adresi"),
    "kambiyo-itiraz": (
        _degistir(TAM["kambiyo-itiraz"],
                  "1. Müvekkile 10.01.2026 tarihinde tebliğ edilen ödeme emrine beş günlük süre "
                  "içinde borca itiraz ediyoruz.",
                  "1. Ödeme emrine borca itiraz ediyoruz."),
        "Ödeme emrinin tebliğ (ya da öğrenme) tarihi"),
    "gecikmis-itiraz": (
        _cikar(TAM["gecikmis-itiraz"],
               "4. Duruşmaya ilişkin harç ve masraflar işbu dilekçe ile birlikte yatırılmıştır.\n"),
        "Harç ve masraf"),
    "itirazin-kaldirilmasi": (
        _degistir(TAM["itirazin-kaldirilmasi"],
                  "1. Borçlunun ödeme emrine itirazı müvekkile 10.02.2026 tarihinde tebliğ edilmiş "
                  "olup işbu istem altı aylık süre içindedir.",
                  "1. Borçlu ödeme emrine itiraz etmiştir."),
        "İtirazın tebliğ tarihi"),
    "itirazin-iptali": (
        _cikar(TAM["itirazin-iptali"], "DAVA DEĞERİ : 10.000,00 TL\n"),
        "Dava değeri"),
    "menfi-tespit": (
        _cikar(TAM["menfi-tespit"], "DAVA DEĞERİ : 10.000,00 TL\n"),
        "Dava değeri"),
    "haciz-talebi": (
        _cikar(TAM["haciz-talebi"], "Takip kesinleşmiştir. "),
        "Takibin kesinleştiği"),
    "satis-talebi": (
        _cikar(TAM["satis-talebi"],
               " Muhafaza, kıymet takdiri ve satış giderleri peşin olarak yatırılmıştır."),
        "satış giderlerinin peşin yatırılması"),
    "haciz-ihbarnamesi-itiraz": (
        _degistir(TAM["haciz-ihbarnamesi-itiraz"],
                  "Müvekkile 05.04.2026 tarihinde tebliğ edilen birinci haciz ihbarnamesine yedi "
                  "günlük süre içinde itiraz ediyoruz.",
                  "Birinci haciz ihbarnamesine itiraz ediyoruz."),
        "eksik parça: tebliğ tarihi"),
    "kiymet-takdiri-sikayet": (
        _cikar(TAM["kiymet-takdiri-sikayet"],
               "3. Yeniden bilirkişi incelemesi yapılması için gereken masraf ve ücret, şikâyet "
               "tarihinden itibaren yedi gün içinde mahkeme veznesine yatırılacaktır.\n"),
        "eksik parça: masraf/ücret"),
    "ihalenin-feshi": (
        _cikar(TAM["ihalenin-feshi"],
               " Bu yolsuzluklar nedeniyle taşınmaz muhammen bedelin çok altında satılmış, "
               "müvekkilin menfaati zarara uğramıştır."),
        "Menfaat ihlali"),
    "icra-sikayet": (
        _degistir(TAM["icra-sikayet"],
                  "; işlem müvekkile 03.05.2026 tarihinde tebliğ edilmiş olup şikâyet yedi günlük "
                  "süre içindedir.", "."),
        "Öğrenme/tebliğ tarihi"),
    "istihkak-davasi": (
        _degistir(_cikar(TAM["istihkak-davasi"],
                         "3. Mallar müvekkil tarafından faturayla satın alınmış olup borçlunun "
                         "işyerinde emanet olarak bulunmaktadır.\n"),
                  "Satış faturaları, emanet sözleşmesi, tanık.", "Tanık."),
        "Mülkiyet karinesine karşı"),
    "icra-ceza-sikayet": (
        _cikar(TAM["icra-ceza-sikayet"],
               "## DELİLLER\nTaahhüt tutanağı, icra dosyası hesap dökümü.\n\n"),
        "Deliller — şikâyetçi"),
    "icra-usul": (
        _cikar(TAM["icra-usul"],
               " olup hükmolunan para tutarında teminat mektubu dosyaya sunulmuştur"),
        "eksik parça: depo/teminat"),
    "idari-dava": (
        _cikar(TAM["idari-dava"], "DAVA KONUSU İŞLEMİN TEBLİĞ TARİHİ : 01.05.2026\n"),
        "yazılı bildirim tarihi"),
    "yd-talebi": (
        _cikar(TAM["yd-talebi"], "1. Dava konusu yıkım kararı açıkça hukuka aykırıdır.\n"),
        "eksik parça: açıkça hukuka aykırılık"),
    "ceza-istinaf": (
        _cikar(TAM["ceza-istinaf"], "TEBLİĞ TARİHİ : 01.04.2026 (gerekçeli hükmün tebliği)\n"),
        "Gerekçeli hükmün tebliğ tarihi"),
}


def _main_kos(argv):
    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py"] + argv
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek
    return exc.value.code


def _cli(tmp_path, monkeypatch, metin, tip, taraf, capsys=None):
    monkeypatch.chdir(tmp_path)
    taslak = tmp_path / "taslak.md"
    taslak.write_text(metin, encoding="utf-8")
    argv = [str(taslak), "--tip", tip, "--kok", str(tmp_path), "--ictihat-muhakeme-yok"]
    if taraf:
        argv += ["--taraf", taraf]
    return _main_kos(argv)


# ── 0. Kapsam ve yapı kilitleri ──────────────────────────────────────────────

def test_kapsam_her_yeni_tip_icin_tam_ve_eksik_taslak_var():
    """Kapı yeni bir tip kazanırsa testi de kazanmalı (gerekçesiz tip olmaz)."""
    assert sorted(TAM) == sorted(YENI_TIPLER)
    assert sorted(EKSIK) == sorted(YENI_TIPLER)
    for tip in YENI_TIPLER:
        assert tip in dd.TIPLER, f"{tip} kapı sözlüğünde yok"


def test_cli_tip_ve_taraf_secenekleri_yeni_degerleri_kabul_eder():
    kaynak = SCRIPT.read_text(encoding="utf-8")
    assert "sorted(set(_ICRA_TIPLERI) | set(_IDARI_CEZA_TIPLERI))" in kaynak
    m = re.search(r'add_argument\(\s*"--taraf".*?choices=\[(.*?)\]', kaynak, re.S)
    secenekler = {x.strip().strip('"\'') for x in m.group(1).split(",")}
    assert {"alacakli", "borclu", "ucuncu-kisi"} <= secenekler
    for t in ("alacakli", "borclu", "ucuncu-kisi"):
        _setler, kismi, _ = dd.aleyhe_kapsami(t)
        assert not kismi, f"{t} kalıp kapsamı yok — tarama sessizce körleşir"


def test_tum_unsur_tanimlari_yapisal_olarak_gecerli():
    """Her desen derlenir; bileşik unsur en az iki parçalıdır; koşullu unsurun
    hem koşulu hem deseni geçerlidir (bozuk tanım kapıyı sessizce düşürmesin)."""
    def desen(d):
        if isinstance(d, dd.Yakin):
            assert d.capa and d.hedef and d.pencere > 0 and d.geri >= 0
            for x in d.capa + d.hedef:
                re.compile(x)
            return
        assert isinstance(d, list) and d
        for x in d:
            assert isinstance(x, str)
            re.compile(x)

    def unsur(u, bilesik_icinde=False):
        if isinstance(u, dd.Kosullu):
            if u.kosul is not None:
                desen(u.kosul)
            if u.istisna:
                desen(u.istisna)
            unsur(u.desen, bilesik_icinde)
        elif isinstance(u, dd.Bilesik):
            assert not bilesik_icinde, "iç içe bileşik desteklenmez"
            assert len(u) >= 2
            for etiket, d in u:
                assert isinstance(etiket, str) and etiket
                unsur(d, bilesik_icinde=True)
        else:
            desen(u)

    for tip, unsurlar in dd.TIPLER.items():
        for ad, des in unsurlar:
            unsur(des)
    for kurallar in dd.TIP_UYARILARI.values():
        for k in kurallar:
            for alan in ("kosul", "yoksa", "varsa"):
                if k.get(alan) is not None:
                    desen(k[alan])


def test_her_yeni_tip_referans_cetvelinde_belgeli():
    """Kod ile insan-okur cetvel ayrışmasın: her yeni --tip değeri references
    altında adıyla anlatılır (gerekçesiz tip yaşayamaz)."""
    metin = REF_ICRA.read_text(encoding="utf-8") + REF_IDARI.read_text(encoding="utf-8")
    for tip in YENI_TIPLER:
        assert tip in metin, f"{tip} referans cetvelinde anlatılmıyor"


# ── 1. Her yeni tip: TAM taslak geçer, EKSİK taslak RED ──────────────────────

@pytest.mark.parametrize("tip", YENI_TIPLER)
def test_tam_taslak_zorunlu_unsurlardan_ve_aleyhe_taramasindan_temiz_gecer(tip):
    eksik, _duzen, ocr, aleyhe, _notu = dd.denetle(TAM[tip], tip, TARAF[tip])
    assert eksik == [], f"{tip}: tam taslakta beklenmedik eksik: {eksik}"
    assert aleyhe == [], f"{tip}: tam taslakta sahte aleyhe sinyali: {aleyhe}"
    assert ocr is False


@pytest.mark.parametrize("tip", YENI_TIPLER)
def test_eksik_taslak_unsur_adiyla_yakalanir(tip):
    metin, beklenen = EKSIK[tip]
    eksik, _d, _o, _a, _n = dd.denetle(metin, tip, TARAF[tip])
    assert any(beklenen in e for e in eksik), (
        f"{tip}: eksik unsur yakalanmadı — beklenen '{beklenen}', bulunan {eksik}")


@pytest.mark.parametrize("tip", YENI_TIPLER)
def test_cli_tam_taslak_exit_0(tip, tmp_path, monkeypatch, capsys):
    kod = _cli(tmp_path, monkeypatch, TAM[tip], tip, TARAF[tip])
    cikti = capsys.readouterr().out
    assert kod == 0, cikti
    assert "[S] SÜRE BAĞLANTISI" in cikti


@pytest.mark.parametrize("tip", YENI_TIPLER)
def test_cli_eksik_taslak_RED_exit_1(tip, tmp_path, monkeypatch, capsys):
    metin, beklenen = EKSIK[tip]
    kod = _cli(tmp_path, monkeypatch, metin, tip, TARAF[tip])
    cikti = capsys.readouterr().out
    assert kod == 1, cikti
    assert "[EKSİK]" in cikti and beklenen in cikti


# ── 2. Bileşik / yakınlık / koşullu unsur davranışı ──────────────────────────

def test_yakinlik_alacakli_adresi_borclu_adres_eksigini_ORTMEZ():
    """İİK m.58/2-2: borçlunun adresi taraf başına aranır — belgede başka bir
    'adres' (alacaklınınki) bulunması borçlu unsurunu karşılamaz."""
    metin = _cikar(TAM["takip-talebi"], ", Adres: Deneme Mah. Örnek Cad. No:2 Örnekşehir")
    eksik, *_ = dd.denetle(metin, "takip-talebi", "alacakli")
    assert any("Borçlu kimliği" in e and "eksik parça: borçlu adresi" in e for e in eksik), eksik


def test_kismi_itirazda_cihet_ve_miktar_kosulu_dogar():
    """İİK m.62 (kısmi itiraz fıkrası): cihet ve miktar gösterilmezse itiraz
    edilmemiş sayılır — koşul doğunca unsur zorunlu olur, doğmadıkça aranmaz."""
    kismi = _degistir(TAM["odeme-emrine-itiraz"],
                      "2. Müvekkilin alacaklıya herhangi bir borcu bulunmamaktadır; borca, faize "
                      "ve tüm ferilerine itiraz ediyoruz.",
                      "2. Borcun bir kısmına itiraz ediyoruz.")
    eksik, *_ = dd.denetle(kismi, "odeme-emrine-itiraz", "borclu")
    assert any("Kısmi itirazda cihet + miktar" in e for e in eksik), eksik
    tamam = _degistir(TAM["odeme-emrine-itiraz"],
                      "2. Müvekkilin alacaklıya herhangi bir borcu bulunmamaktadır; borca, faize "
                      "ve tüm ferilerine itiraz ediyoruz.",
                      "2. Borcun 2.500,00 TL'lik işlemiş faiz kısmına itiraz ediyoruz.")
    eksik2, *_ = dd.denetle(tamam, "odeme-emrine-itiraz", "borclu")
    assert not any("Kısmi itiraz" in e for e in eksik2), eksik2


def test_ticari_itirazin_iptalinde_arabuluculuk_dava_sarti_aranir():
    """TTK m.5/A-1 itirazın iptalini açıkça sayar; ticari sinyal varken
    arabuluculuk anılmıyorsa [A] eksik (usulden ret riski)."""
    metin = _cikar(TAM["itirazin-iptali"],
                   "; zorunlu arabuluculuk görüşmesi anlaşmazlıkla sonuçlanmış, son tutanak ektedir",
                   "arabuluculuk son tutanağı, ", ", TTK m.5/A")
    eksik, *_ = dd.denetle(metin, "itirazin-iptali", "alacakli")
    assert any("arabuluculuk" in e for e in eksik), eksik


def test_sikayet_suresiz_hallerde_sure_unsuru_aranmaz():
    """İİK m.16/2: hakkın yerine getirilmemesi / sürüncemede bırakılması
    hâlinde her zaman şikâyet — süre unsuru istisnayla kalkar."""
    metin = _degistir(EKSIK["icra-sikayet"][0], "2. İşlem kanuna aykırıdır.",
                      "2. Talebimiz sebepsiz sürüncemede bırakılmıştır; işlem kanuna aykırıdır.")
    eksik, *_ = dd.denetle(metin, "icra-sikayet", "alacakli")
    assert not any("Öğrenme/tebliğ" in e for e in eksik), eksik


def test_idari_davada_yd_istenmisse_iki_kosul_ayri_aranir():
    """İYUK m.27/2: iki koşul BİRLİKTE — soyut tek cümle yetmez."""
    metin = _cikar(TAM["idari-dava"],
                   " olup uygulanması hâlinde telafisi güç veya imkânsız zararlar doğacaktır")
    eksik, *_ = dd.denetle(metin, "idari-dava", "davaci")
    assert any("eksik parça: telafisi güç veya imkânsız zarar" in e for e in eksik), eksik


def test_satista_motorlu_aracta_muhafaza_kosulu():
    metin = _degistir(TAM["satis-talebi"], "Aracın muhafaza altına alınmasını, ", "")
    metin = _degistir(metin, "Muhafaza, kıymet takdiri ve satış giderleri",
                      "Kıymet takdiri ve satış giderleri")
    eksik, *_ = dd.denetle(metin, "satis-talebi", "alacakli")
    assert any("Motorlu araçta" in e and "eksik parça: muhafaza" in e for e in eksik), eksik


# ── 3. Y-06 — eski tiplerin sıkılaşması ve dürüst sınırı ─────────────────────

AYM_TAM = (
    "# ANAYASA MAHKEMESİ BAŞKANLIĞI'NA\n\n"
    "BAŞVURUCU : Ayşe Örnek, T.C. Kimlik No: [sentetik], Adres: Örnek Mah. No:3 Örnekşehir\n"
    "VEKİLİ : Av. Test Vekil\n\n"
    "## İHLAL EDİLEN HAKLAR\n"
    "Anayasa'nın 36. maddesinde güvence altına alınan adil yargılanma hakkı ihlal edilmiştir.\n\n"
    "## BAŞVURU YOLLARININ TÜKETİLMESİ\n"
    "Kanun yolları tüketilmiş, karar 01.06.2026 tarihinde kesinleşmiştir; başvuru otuz gün "
    "içindedir.\n\n"
    "## TALEP\nİhlalin tespitine ve yeniden yargılama yapılmasına karar verilmesini talep ederiz.\n\n"
    "EKLER: Karar örneği, harç makbuzu, vekâletname.\n"
)


def test_aym_ihlal_hak_ile_anayasa_maddesi_ayri_parca():
    """6216 m.47/3: 'hak' kelimesi tek başına Anayasa hükmü unsurunu artık
    KARŞILAMAZ (Y-06: bileşik unsurda tek desen yetiyordu)."""
    eksik, *_ = dd.denetle(AYM_TAM, "aym_bireysel", "")
    assert eksik == [], eksik
    madde_yok = _degistir(AYM_TAM, "Anayasa'nın 36. maddesinde güvence altına alınan ",
                          "Güvence altındaki ")
    eksik2, *_ = dd.denetle(madde_yok, "aym_bireysel", "")
    assert any("eksik parça: Anayasa maddesi" in e for e in eksik2), eksik2


def test_aym_ekler_ve_vekaletname():
    """6216 m.47/3 son cümle + m.47/4."""
    metin = _degistir(AYM_TAM, "EKLER: Karar örneği, harç makbuzu, vekâletname.\n",
                      "EKLER: Karar örneği.\n")
    eksik, *_ = dd.denetle(metin, "aym_bireysel", "")
    assert any("harç belgesi" in e for e in eksik), eksik
    assert any("Vekâletname" in e for e in eksik), eksik


ISTINAF_TEBLIGSIZ = (
    "# Bölge Adliye Mahkemesi Başkanlığına\n\n"
    "İstinaf eden: Ahmet Örnek\n\n"
    "İlk derece esas no: 2024/1 karar no: 2024/2\n\n"
    "İstinaf sebepleri: hukuka aykırı karar verilmiştir.\n\n"
    "Netice-i talep: süresi içinde kaldırılmasını talep ederiz.\n\n"
    "01.01.2026\nimza\nAv. Vekil\n"
)


def test_istinafta_teblig_tarihi_artik_sure_kelimesiyle_karsilanamaz():
    """HMK m.342/2-ç: kararın tebliğ tarihi ZORUNLU içerik; eskiden 'süre'
    kelimesi tek başına bu unsuru karşılıyordu (Y-06)."""
    eksik, *_ = dd.denetle(ISTINAF_TEBLIGSIZ, "istinaf", "davaci")
    assert any("tebliğ tarihi" in e for e in eksik), eksik
    tebligli = ISTINAF_TEBLIGSIZ.replace("01.01.2026\nimza", "Tebliğ tarihi: 15.12.2025\n\n01.01.2026\nimza")
    eksik2, *_ = dd.denetle(tebligli, "istinaf", "davaci")
    assert not any("tebliğ tarihi" in e for e in eksik2), eksik2


def test_istinafta_karar_sayisi_mahkemeyle_birlikte_aranir():
    """HMK m.342/2-c: kararın mahkemesi ile SAYISI birlikte."""
    sayisiz = ISTINAF_TEBLIGSIZ.replace("İlk derece esas no: 2024/1 karar no: 2024/2",
                                        "İlk derece kararı")
    eksik, *_ = dd.denetle(sayisiz, "istinaf", "davaci")
    assert any("eksik parça: sayı" in e for e in eksik), eksik


def test_istinafta_karar_tarihi_istisari_uyari():
    """HMK m.342/2-c kararın 'tarihi ile sayısı'nı birlikte ister; eski tipte
    kilit testleri bozmamak için istişari (exit kodu değişmez)."""
    u = dd.tip_ozel_uyarilari(ISTINAF_TEBLIGSIZ, "istinaf")
    assert any("m.342/2-c" in x for x in u), u
    tarihli = ISTINAF_TEBLIGSIZ.replace("karar no: 2024/2", "karar no: 2024/2, karar tarihi: 10.12.2025")
    assert not any("m.342/2-c" in x for x in dd.tip_ozel_uyarilari(tarihli, "istinaf"))


def test_temyizde_ilamin_teblig_tarihi_ayri_unsur():
    """HMK m.364/2-d."""
    metin = ("# Yargıtay ilgili Hukuk Dairesi Başkanlığına\n\nBölge adliye esas no: 2025/1 karar no: "
             "2025/2\nTemyiz sebepleri: hukuka aykırılık.\nNetice-i talep: bozulmasını talep "
             "ederiz.\n01.01.2026\nimza\n")
    eksik, *_ = dd.denetle(metin, "temyiz", "davaci")
    assert any("İlamın tebliğ tarihi" in e for e in eksik), eksik


# ── 3a. Süre başlangıcının TARİHİ — olayın yanında; süre ifadesi aranmaz ────
# Fable 5.1 salt okunur incelemesi (2026-10-05): 'tebliğ' kelimesi ile imza
# tarihinin belgede AYRI AYRI geçmesi tebliğ tarihini "var" saydırıyordu;
# 'yedi gün içinde' gibi süre İFADESİ ise yasal içerik değildi ama BLOK
# üretiyordu. Kanunun istediği tarihtir (HMK m.342/2-ç, m.364/2-d; İYUK m.3/2-c).

def test_teblig_tarihi_teblig_olayinin_yaninda_aranir():
    uzak = ISTINAF_TEBLIGSIZ.replace(
        "01.01.2026\nimza", "Karar müvekkile tebliğ edilmiştir.\n" + ("Ayrıntılı açıklama. " * 15)
        + "\n\n01.01.2026\nimza")
    eksik, *_ = dd.denetle(uzak, "istinaf", "davaci")
    assert any("tebliğ tarihi" in e for e in eksik), "imza tarihi tebliğ tarihini örtmemeli"
    once = ISTINAF_TEBLIGSIZ.replace(
        "01.01.2026\nimza", "Karar müvekkile 15.12.2025 tarihinde tebliğ edilmiştir.\n\n01.01.2026\nimza")
    eksik2, *_ = dd.denetle(once, "istinaf", "davaci")
    assert not any("tebliğ tarihi" in e for e in eksik2), "fiilden ÖNCE gelen tarih tutmalı"
    ay_adi = ISTINAF_TEBLIGSIZ.replace("01.01.2026\nimza", "Tebliğ: 15 Aralık 2025\n\n01.01.2026\nimza")
    eksik3, *_ = dd.denetle(ay_adi, "istinaf", "davaci")
    assert not any("tebliğ tarihi" in e for e in eksik3), eksik3


@pytest.mark.parametrize("cumle,eksik_beklenir", [
    ("Gerekçeli karar henüz tebliğ edilmemiştir.", False),
    ("Karar tebliğ edilmeden istinaf yoluna başvuruyoruz.", False),
    ("Kararın tebliğ edilmesi beklenmektedir.", True),      # ad-fiil OLUMLU — istisna değil
    ("Tebligat gideri 01.01.2026 tarihinde yatırılmıştır.", True),  # 'tebligat' olay değil
])
def test_teblig_edilmemis_beyani_tarih_unsurunu_kaldirir(cumle, eksik_beklenir):
    """Tebliğden önce başvurmak müvekkilin hakkıdır; tarih yazılamayan hâlde
    kapı sahte BLOK üretmemeli — ama olumlu ad-fiil istisna sayılmamalı.
    (Cümle başlık bloğuna konur: imza tarihi yakınlık penceresinin DIŞINDA kalsın.)"""
    metin = ISTINAF_TEBLIGSIZ.replace("İstinaf eden: Ahmet Örnek\n\n",
                                      "İstinaf eden: Ahmet Örnek\n\n" + cumle + "\n\n")
    assert cumle in metin
    eksik, *_ = dd.denetle(metin, "istinaf", "davaci")
    assert any("tebliğ tarihi" in e for e in eksik) is eksik_beklenir, eksik


def test_usulsuz_teblige_ogrenme_tarihi_karsilar():
    """Tebligat K. m.32: muhatabın tebliğe muttali olduğunu beyan ettiği tarih
    tebliğ tarihi sayılır — icra itirazında öğrenme tarihi unsuru karşılar."""
    metin = _degistir(TAM["odeme-emrine-itiraz"],
                      "1. Müvekkile 10.01.2026 tarihinde tebliğ edilen ödeme emrine yasal yedi günlük "
                      "süre içinde itiraz ediyoruz.",
                      "1. Ödeme emri usulsüz tebliğ edilmiş olup müvekkil takibi 12.01.2026 tarihinde "
                      "öğrenmiştir; ödeme emrine itiraz ediyoruz.")
    eksik, *_ = dd.denetle(metin, "odeme-emrine-itiraz", "borclu")
    assert eksik == [], eksik


def test_sure_ifadesi_artik_zorunlu_unsur_degil():
    """'yedi günlük süre içinde' yasal içerik değildir — tarihi olan taslak
    süre cümlesi olmadan da temiz geçer (süre [S] satırındadır)."""
    metin = _degistir(TAM["odeme-emrine-itiraz"], " yasal yedi günlük süre içinde", "")
    eksik, *_ = dd.denetle(metin, "odeme-emrine-itiraz", "borclu")
    assert eksik == [], eksik
    metin2 = _degistir(TAM["ihalenin-feshi"],
                       "; işbu şikâyet ihale tarihinden itibaren yedi gün içinde yapılmaktadır", "")
    eksik2, *_ = dd.denetle(metin2, "ihalenin-feshi", "borclu")
    assert eksik2 == [], eksik2


def test_gecikmis_itirazda_maninin_kalktigi_gun_tarihiyle_aranir():
    metin = _degistir(TAM["gecikmis-itiraz"], "Bu mazeret 20.01.2026 tarihinde taburcu olmasıyla",
                      "Bu mazeret taburcu olmasıyla")
    eksik, *_ = dd.denetle(metin, "gecikmis-itiraz", "borclu")
    assert any("Maninin kalktığı gün" in e for e in eksik), eksik


def test_istirdatta_odeme_tarihi_odeme_olayinin_yaninda():
    """İİK m.72/7: istirdat süresi ödemeden işler; ödeme EMRİNİN tarihi bu
    unsuru karşılamaz."""
    istirdat = _degistir(
        TAM["menfi-tespit"], "2. Takibe dayanak gösterilen senet bedelsiz olup",
        "2. Müvekkil takip baskısı altında 05.02.2026 tarihinde ödeme yapmıştır; senet bedelsiz olup")
    istirdat = _degistir(istirdat, "borçlu olmadığının tespitine,",
                         "borçlu olmadığının tespitine ve ödenen paranın istirdadına,")
    eksik, *_ = dd.denetle(istirdat, "menfi-tespit", "borclu")
    assert not any("İstirdatta ödeme tarihi" in e for e in eksik), eksik
    emir = _degistir(istirdat, "takip baskısı altında 05.02.2026 tarihinde ödeme yapmıştır",
                     "aleyhine 05.02.2026 tarihli ödeme emri gönderilmiştir")
    eksik2, *_ = dd.denetle(emir, "menfi-tespit", "borclu")
    assert any("İstirdatta ödeme tarihi" in e for e in eksik2), eksik2


# ── 3b. Fable 5.1 incelemesiyle [A]'dan istişariye inen ya da daralan kalemler ──

def test_kambiyo_dayanak_belge_yalniz_odeme_itfa_iddiasinda_aranir():
    """İİK m.169/a-1: borçlu olmama/itfa/imhal resmî ya da imzası ikrar edilmiş
    belgeyle ispatlanır; zamanaşımı itirazında belge koşulu yoktur."""
    zamanasimi = (
        "# ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE\n\n"
        "İTİRAZ EDEN (BORÇLU) : Mehmet Örnek\nVEKİLİ : Av. Test Vekil\n"
        "KARŞI TARAF (ALACAKLI) : Örnek Ticaret A.Ş.\n"
        "TAKİP DOSYASI : Örnek 3. İcra Dairesi 2024/123 Esas\n\n"
        "1. Müvekkile 10.01.2026 tarihinde tebliğ edilen ödeme emrine zamanaşımı itirazında "
        "bulunuyoruz; bononun vadesinden itibaren üç yıl geçmiştir.\n\n"
        "## SONUÇ VE İSTEM\nİtirazımızın kabulü ile takibin iptaline karar verilmesini talep ederiz.\n"
        + _imza("12.01.2026", "Borçlu"))
    eksik, *_ = dd.denetle(zamanasimi, "kambiyo-itiraz", "borclu")
    assert eksik == [], eksik
    odendi = _degistir(zamanasimi, "zamanaşımı itirazında bulunuyoruz; bononun vadesinden itibaren "
                                   "üç yıl geçmiştir", "borca itiraz ediyoruz; bono bedeli ödenmiştir")
    eksik2, *_ = dd.denetle(odendi, "kambiyo-itiraz", "borclu")
    assert any("Dayanak belge" in e for e in eksik2), eksik2


def test_kambiyo_takip_talebinde_vade_aranmaz():
    """TTK m.777/2: vadesi gösterilmemiş bono görüldüğünde ödenecek sayılır —
    'vade' kelimesini aramak sahte BLOK üretirdi."""
    metin = _degistir(TAM["takip-talebi"],
                      "BORCUN SEBEBİ : 01.01.2026 tarihli sözleşmeden doğan hizmet bedeli.",
                      "BORCUN SEBEBİ : 01.01.2026 düzenleme tarihli bono.")
    metin = _degistir(metin, "EKLER: 1- Sözleşme aslı", "EKLER: 1- Bono aslı")
    assert "vade" not in metin.lower()
    eksik, *_ = dd.denetle(metin, "takip-talebi", "alacakli")
    assert eksik == [], eksik


def test_takip_talebinde_tckn_vkn_varsa_hukmuyle_istisari():
    """İİK m.58/2-1 'varsa', m.58/2-2 'biliniyorsa' — zorunlu parça değil."""
    metin = _degistir(TAM["takip-talebi"], ", VKN: [sentetik]", "")
    eksik, *_ = dd.denetle(metin, "takip-talebi", "alacakli")
    assert eksik == [], eksik
    assert any("varsa" in u for u in dd.tip_ozel_uyarilari(metin, "takip-talebi"))


@pytest.mark.parametrize("ticari_cumle,arabuluculuk_aranir", [
    ("3. Takip, müvekkile verilen bonoya dayanmaktadır.", True),        # TTK m.4/1-a
    ("3. Takip bonoya dayanmakla birlikte uyuşmazlık tüketici işleminden doğmaktadır.",
     False),                                                              # istisna
    ("3. Taraflar arasındaki ilişki bir kira ilişkisidir.", False),     # sinyal yok
])
def test_ticari_dava_sarti_dar_kosul_ve_istisna(ticari_cumle, arabuluculuk_aranir):
    """TTK m.5/A-1 dava şartı BLOK kalır ama koşulu dardır: tek bir 'A.Ş.' ya da
    'fatura' davayı ticari yapmaz; kambiyo senedi ise ticari davadır."""
    metin = _degistir(TAM["itirazin-iptali"],
                      "3. Taraflar arasındaki ticari ilişki faturalarla sabittir; zorunlu "
                      "arabuluculuk görüşmesi anlaşmazlıkla sonuçlanmış, son tutanak ektedir.",
                      ticari_cumle)
    metin = _cikar(metin, ", TTK m.5/A", "arabuluculuk son tutanağı, ", "Faturalar, ticari defterler, ")
    eksik, *_ = dd.denetle(metin, "itirazin-iptali", "alacakli")
    assert any("arabuluculuk" in e for e in eksik) is arabuluculuk_aranir, eksik


DAVA_PARA_DEGERSIZ = (
    "# Örnek 1. Asliye Hukuk Mahkemesi Başkanlığına\n\n"
    "Davacı: Ayşe Örnek, Adres: Örnek Mah.\nDavalı: Örnek A.Ş., Adres: Örnek Cad.\n"
    "Vekil: Av. Test Vekil\n\n## Konu\nAlacak.\n\n## Açıklamalar\n1. Birinci vakıa.\n\n"
    "## Hukuki Sebepler\nTBK.\n\n## Deliller\nTanık.\n\n## Netice-i Talep\n"
    "1. 10.000,00 TL alacağın dava tarihinden itibaren yasal faiziyle tahsiline,\n"
    "2. Yargılama giderleri ve vekâlet ücretinin davalıya yükletilmesine karar verilmesini talep "
    "ederiz.\n\n01.01.2026\nAv. Test Vekil\nimza\n"
)


def test_eski_dava_tipinde_dava_degeri_istisari_uyari_exit_degismez(tmp_path, monkeypatch, capsys):
    """Y-06 dürüst sınırı: eski 'dava' tipinde dava değeri BLOKLAMAZ (mevcut kilit
    testler değer satırsız para talepli taslağın temiz geçmesini bekliyor) ama
    [A] altında GÖRÜNÜR uyarı basılır."""
    u = dd.tip_ozel_uyarilari(DAVA_PARA_DEGERSIZ, "dava")
    assert any("dava değeri" in x for x in u), u
    eksik, *_ = dd.denetle(DAVA_PARA_DEGERSIZ, "dava", "davaci")
    assert not any("değer" in e.lower() for e in eksik), eksik
    kod = _cli(tmp_path, monkeypatch, DAVA_PARA_DEGERSIZ, "dava", "davaci")
    cikti = capsys.readouterr().out
    assert kod == 0, cikti
    assert "[UYARI] dava değeri" in cikti
    degerli = DAVA_PARA_DEGERSIZ.replace("## Konu", "DAVA DEĞERİ : 10.000,00 TL\n\n## Konu")
    assert not any("dava değeri" in x for x in dd.tip_ozel_uyarilari(degerli, "dava"))


def test_eski_dava_tipinde_tckn_eksikligi_istisari_uyari():
    """HMK m.119/1-c — eksiklikte bir haftalık kesin süre (m.119/2); uyarı
    görünür, exit kodu değişmez."""
    u = dd.tip_ozel_uyarilari(DAVA_PARA_DEGERSIZ, "dava")
    assert any("TCKN" in x for x in u), u


# ── 4. Müvekkil-aleyhi tarama — icra sıfatları (anayasa m.6) ─────────────────

@pytest.mark.parametrize("tip,taraf,metin", [
    ("odeme-emrine-itiraz", "borclu", "Ödeme emrine itiraz etmiyoruz."),
    ("odeme-emrine-itiraz", "borclu", "İtirazımızdan vazgeçiyoruz."),
    ("odeme-emrine-itiraz", "borclu", "Itirazimizdan vazgeciyoruz."),   # OCR/Türkçesiz
    ("kambiyo-itiraz", "borclu", "Borcun bir kısmını kabul ediyoruz."),  # İİK m.170/a-3
    ("kambiyo-itiraz", "borclu", "İmza itirazımızdan vazgeçiyoruz."),
    ("takip-talebi", "alacakli", "Alacağımız tahsil edilmiştir."),
    ("icra-usul", "alacakli", "İstihkak iddiasını kabul ediyoruz."),    # İİK m.96/2
    ("icra-ceza-sikayet", "alacakli", "Şikâyetimizden vazgeçiyoruz."),
    ("istihkak-davasi", "ucuncu-kisi",
     "Müvekkilin borçluya olan borcu bulunmaktadır."),
    ("haciz-ihbarnamesi-itiraz", "ucuncu-kisi", "İtirazımızdan vazgeçiyoruz."),  # İİK m.89/3
])
def test_icra_ikrari_yakalanir(tip, taraf, metin):
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, tip, taraf)
    assert aleyhe, f"icra ikrarı yakalanmadı: {metin!r} ({taraf})"


@pytest.mark.parametrize("tip,taraf,metin", [
    ("takip-talebi", "alacakli",
     "Alacağımızın tahsil edilmesi için takip yapılmasını talep ederiz."),   # amaç cümlesi
    ("itirazin-iptali", "alacakli", "Alacağımız zamanaşımına uğramamıştır."),
    ("odeme-emrine-itiraz", "borclu", "İtirazımızdan vazgeçmediğimizi bildiririz."),
    ("haciz-ihbarnamesi-itiraz", "ucuncu-kisi", "Müvekkilin borçluya borcu bulunmamaktadır."),
    ("icra-usul", "alacakli", "İstihkak iddiasını kabul etmiyoruz."),
])
def test_lehe_ya_da_olumsuz_cumle_sinyal_uretmez(tip, taraf, metin):
    """Yanlış alarm da kusurdur — kapıya güveni aşındırır."""
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, tip, taraf)
    assert not aleyhe, f"yanlış alarm: {metin!r} → {aleyhe}"


@pytest.mark.parametrize("tip,taraf,metin,beklenen", [
    # Türkçe olumsuzluk: -me/-ma ve -miyor/-mıyor dışlanır; -miş (evidential) OLUMLUDUR.
    ("icra-ceza-sikayet", "alacakli", "Şikâyetimizden vazgeçmiyoruz.", False),
    ("icra-ceza-sikayet", "alacakli", "Şikâyetimizden vazgeçmiş bulunmaktayız.", True),
    ("odeme-emrine-itiraz", "borclu", "İtirazımızı geri almıyoruz.", False),
    ("odeme-emrine-itiraz", "borclu", "İtirazımızı geri almış bulunuyoruz.", True),
    ("itirazin-iptali", "alacakli", "Alacağımız zamanaşımına uğramıyor.", False),
    ("itirazin-iptali", "alacakli", "Alacağımız zamanaşımına uğramıştır.", True),
    # Eski davacı/müşteki 'vazgeç' kalıplarında aynı kusur vardı: müvekkil LEHİNE
    # 'vazgeçmiyoruz' cümlesi teslimi BLOKLUYORDU (NEG penceresi -miyor'u tanımaz).
    ("dava", "davaci", "Davacı olarak iddiamızdan vazgeçmiyoruz.", False),
    ("dava", "davaci", "Davacı olarak iddiamızdan vazgeçiyoruz.", True),
    ("genel", "musteki", "Şikayetten vazgeçmiyoruz, cezalandırılmasını istiyoruz.", False),
    ("genel", "musteki", "Şikayetten vazgeçiyoruz.", True),
])
def test_olumsuz_cekim_sinyal_degil_evidential_ikrar_sinyal(tip, taraf, metin, beklenen):
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, tip, taraf)
    assert bool(aleyhe) is beklenen, f"{metin!r} → {aleyhe}"


def test_menfi_tespitte_borclu_DAVACI_konumunda_taranir():
    """Menfi tespitte borçlu davacıdır; davalı kalıbı 'davanın kabul' onun kendi
    talep cümlesidir. Konum çevrilmeseydi tam taslak sahte BLOK alırdı."""
    setler, kismi, _ = dd.aleyhe_kapsami("borclu", "menfi-tespit")
    assert setler[0] == "borclu@davaci" and not kismi
    _e, _d, _o, aleyhe, _n = dd.denetle(TAM["menfi-tespit"], "menfi-tespit", "borclu")
    assert aleyhe == [], aleyhe
    _e, _d, _o, aleyhe_genel, _n = dd.denetle(TAM["menfi-tespit"], "genel", "borclu")
    assert aleyhe_genel, "çevrim olmadan 'davanın kabul' borçluda sinyal üretmeliydi (kontrast)"
    _e, _d, _o, aleyhe2, _n = dd.denetle("Borçlu olduğumuzu kabul ediyoruz.", "menfi-tespit",
                                         "borclu")
    assert aleyhe2, "çevrilmiş eksende de borçlu ikrarı yakalanmalı"


def test_aleyhe_kapsami_tek_argumanli_eski_cagri_aynen_calisir():
    assert dd.aleyhe_kapsami("davali") == (["davali", "genel"], False, "")
    assert dd.aleyhe_kapsami("borclu")[0] == ["borclu", "genel"]


@pytest.mark.parametrize("tip,taraf,metin,beklenen", [
    # Olumlu -mek/-mekte çekimleri ikrardır (kaba '(?!me)' bunları düşürüyordu).
    ("odeme-emrine-itiraz", "borclu", "İtirazımızdan vazgeçmek istiyoruz.", True),
    ("odeme-emrine-itiraz", "borclu", "Müvekkil itirazından vazgeçmektedir.", True),
    ("odeme-emrine-itiraz", "borclu", "İtirazımızdan vazgeçmeyeceğiz.", False),
    ("odeme-emrine-itiraz", "borclu", "İtirazımızdan vazgeçmemekteyiz.", False),
    ("dava", "davaci", "İddiamızdan vazgeçmekteyiz.", True),
    # Birinci ağız 'kabul' çekimleri ('-mekte', geçmiş zaman) — borçlu ekseni.
    ("odeme-emrine-itiraz", "borclu", "İmzanın müvekkile ait olduğunu kabul etmekteyiz.", True),
    # Kanunun kendi terimi ('imzası ikrar edilmiş belge') ikrar DEĞİLDİR.
    ("kambiyo-itiraz", "borclu", "Borcun ödendiği, imzası ikrar edilmiş makbuz ile sabittir.", False),
])
def test_turkce_cekim_ve_kanun_terimi_ayrimi(tip, taraf, metin, beklenen):
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, tip, taraf)
    assert bool(aleyhe) is beklenen, f"{metin!r} → {aleyhe}"


def test_kesin_kalip_NEG_penceresinden_muaf_ve_tek_satirda_raporlanir():
    """Çekimli olumlu ikrar, komşu 'aksi/değil' sözcüğü yüzünden BİLGİ'ye
    düşmemeli; aynı cümle hem [UYARI] hem 'olumsuzlanmış' görünmemeli."""
    metin = "Borcun tamamını kabul ediyoruz; aksi düşünülemez."
    _e, _d, _o, aleyhe, notu = dd.denetle(metin, "odeme-emrine-itiraz", "borclu")
    assert any("Borcun tamamını kabul ediyoruz" in a for a in aleyhe), aleyhe
    assert not any("tamamını kabul" in n for n in notu), notu
    # Ortaç ve olumsuz çekim kesin kalıba girmez → NEG koruması aynen işler.
    for guvenli in ("Bu beyanımız borcun tamamını kabul ettiğimiz anlamına gelmez.",
                    "Borcun tamamını kabul etmiyoruz."):
        _e, _d, _o, aleyhe2, _n = dd.denetle(guvenli, "odeme-emrine-itiraz", "borclu")
        assert aleyhe2 == [], f"{guvenli!r} → {aleyhe2}"


def test_kambiyoda_kismi_kabul_ayrica_taranir_ilamsizda_taranmaz():
    """İİK m.170/a-3: kambiyo takibinde borcun kısmen kabulü vasfın re'sen
    gözetilmesini kapatır; ilamsız takipte kısmi itiraz meşru stratejidir."""
    metin = "Borcun 5.000,00 TL'lik kısmını kabul etmekle birlikte kalanına itiraz ediyoruz."
    assert dd.aleyhe_kapsami("borclu", "kambiyo-itiraz")[0][0] == "borclu@kambiyo"
    _e, _d, _o, kambiyo, _n = dd.denetle(metin, "kambiyo-itiraz", "borclu")
    assert kambiyo, "kambiyo takibinde kısmi kabul yakalanmalı"
    _e, _d, _o, ilamsiz, _n = dd.denetle(metin, "odeme-emrine-itiraz", "borclu")
    assert ilamsiz == [], ilamsiz


def test_ucuncu_kisinin_durust_borc_beyani_89da_blok_degil_uyari():
    """İİK m.89/4 + m.338/1: hakikate aykırı itiraz hapis ve tazminat doğurur —
    üçüncü kişinin dürüst borç beyanı haciz ihbarnamesine itirazda BLOK değil
    istişari uyarıdır; istihkak davasında aynı cümle müvekkili bitirir (BLOK)."""
    metin = "Müvekkilin borçluya olan borcu bulunmaktadır; vadesi henüz gelmemiştir."
    _e, _d, _o, aleyhe, _n = dd.denetle(metin, "haciz-ihbarnamesi-itiraz", "ucuncu-kisi")
    assert aleyhe == [], aleyhe
    u = dd.tip_ozel_uyarilari(metin, "haciz-ihbarnamesi-itiraz")
    assert any("m.338/1" in x and "m.89/4" in x for x in u), u
    _e, _d, _o, aleyhe2, _n = dd.denetle(metin, "istihkak-davasi", "ucuncu-kisi")
    assert aleyhe2, "istihkak davasında üçüncü kişinin borç ikrarı BLOK kalmalı"


# ── 5. [S] SÜRE BAĞLANTISI — hesap yok, kural kimliği çalışma anında ────────

def test_sure_baglantisi_kurali_bulursa_kimligini_bulamazsa_teyit_bekliyor(monkeypatch):
    """Kural kimliği koda gömülmez: oa-sure tablosu çalışma anında aranır."""
    monkeypatch.setitem(dd._SURE_TABLO_ONBELLEK, "v",
                        {"sahte_iik62": "İİK m.62/1 — ödeme emrine itiraz; 7 gün"})
    satirlar = dd.sure_baglantisi("odeme-emrine-itiraz")
    assert any("sahte_iik62" in s for s in satirlar), satirlar
    assert any("TEYİT BEKLİYOR" in s and "m.269" in s for s in satirlar), satirlar


def test_sure_baglantisi_tablo_okunamazsa_gorunur(monkeypatch):
    monkeypatch.setitem(dd._SURE_TABLO_ONBELLEK, "v", None)
    satirlar = dd.sure_baglantisi("kambiyo-itiraz")
    assert satirlar and all("OKUNAMADI" in s for s in satirlar), satirlar


def test_sure_baglantisi_gercek_tabloda_mevcut_kurallari_bulur(monkeypatch):
    """Entegrasyon: depodaki gerçek oa-sure tablosu okunur ve İİK m.16 (şikâyet)
    ile CMK m.273 (ceza istinafı) kuralları bulunur. Kural KİMLİĞİ bilinçli
    olarak sabitlenmez (kardeş ajan kural yeniden adlandırsa da test kararlı
    kalsın — kimlik koda gömülmez ilkesinin test yüzü); yalnız bağın kurulduğu
    ve kimliğin tablodaki bir anahtar olduğu doğrulanır."""
    monkeypatch.delitem(dd._SURE_TABLO_ONBELLEK, "v", raising=False)
    tablo = dd._sure_kurallari_kaynaklari()
    assert tablo, "oa-sure kural tablosu okunamadı"
    for tip in ("icra-sikayet", "ceza-istinaf"):
        satir = dd.sure_baglantisi(tip)[0]
        assert "oa-sure kuralı:" in satir, satir
        kimlikler = satir.split("oa-sure kuralı:")[1].strip().split(", ")
        assert kimlikler and all(k in tablo for k in kimlikler), satir


@pytest.mark.parametrize("kaynak,beklenen", [
    ("İİK m.62/1 — ödeme emrine itiraz", True),
    ("İİK md. 62 — ödeme emrine itiraz", True),
    ("İİK madde 62", True),
    ("İİK 62/1", True),
    ("İİK m.621", False),      # başka madde — sınır kelimesi
    ("İİK m.162", False),
    ("HMK m.62", False),       # başka kanun
])
def test_madde_deseni_yazim_bicimine_toleransli(kaynak, beklenen):
    """Kardeş ajanın 'kaynak' yazım tercihi (m. / md. / madde / çıplak numara)
    bağı sessizce koparmasın; ama komşu madde ya da başka kanun eşleşmesin."""
    assert bool(re.search(dd._md("İİK", "62"), kaynak, re.I)) is beklenen


def test_sure_baglantisi_her_yeni_tip_icin_tanimli():
    for tip in YENI_TIPLER:
        assert dd.TIP_SURE.get(tip), f"{tip}: süre bağlantısı tanımsız"


def test_sure_baglantisi_tanimsiz_tipte_bilgi_etiketi_basmaz(tmp_path, monkeypatch, capsys):
    """Süre bağlantısı tanımsız tip (ör. 'genel') bir atlama DEĞİLDİR: '[BİLGİ]'
    etiketi teslim zincirinde 'kapı koşulmadı' diye okunur (teslim_paketi.py (a)
    bölümünde [BİLGİ] yasağı — tests/test_teslim_paketi.py). Satır görünür ama
    etiketsizdir."""
    _cli(tmp_path, monkeypatch, DAVA_PARA_DEGERSIZ, "genel", "davaci")
    cikti = capsys.readouterr().out
    s_bolumu = cikti.split("[S] SÜRE BAĞLANTISI")[1].split("[C] OCR")[0]
    assert "tanımlı süre bağlantısı yok" in s_bolumu
    assert "[BİLGİ]" not in s_bolumu


# ── 6. İstişari kalemler ve gürültü kontrolü ─────────────────────────────────

def test_form_nitelikli_icra_taleplerinde_delil_bolumu_B_uyarisi_uretmez():
    """Takip/haciz/satış talebi form niteliğindedir; [B]'de 'Deliller' gürültüsü
    gerçek uyarıyı gömer (alarm yorgunluğu)."""
    _e, duzen, *_ = dd.denetle(TAM["haciz-talebi"], "haciz-talebi", "alacakli")
    assert "Deliller" not in duzen
    _e, duzen_genel, *_ = dd.denetle(TAM["haciz-talebi"], "genel", "alacakli")
    assert "Deliller" in duzen_genel, "kontrast: genel tipte aynı kalem uyarılmalı"


def test_icra_kisaltmalari_ciplak_kisaltma_sayilmaz():
    u = dd.ciplak_kisaltma_uyarilari("Alacaklı IBAN ve VKN bilgisi aşağıdadır; BİM kararı da var.\n")
    assert not any(t in x for x in u for t in ("'IBAN'", "'VKN'", "'BİM'")), u


@pytest.mark.parametrize("tip,metin,beklenen", [
    ("takip-talebi", TAM["takip-talebi"].replace(
        "; asıl alacağa takip tarihinden itibaren işleyecek yasal faiz", ""), "faiz istemi"),
    ("kambiyo-itiraz", TAM["kambiyo-itiraz"].replace(
        "3. Alacaklının kötü niyet tazminatına mahkûm edilmesine karar", "3. Gereğine karar"),
     "kötü niyet tazminatı"),
    ("menfi-tespit", TAM["menfi-tespit"].replace("ihtiyati tedbir kararı", "karar"),
     "ihtiyati tedbir"),
    ("yd-talebi", TAM["yd-talebi"].replace(
        "3. Davacı adli yardımdan yararlandığından teminat alınmaması gerekir.\n", "").replace(
        "Teminatsız olarak ", ""), "teminat"),
    # Fable 5.1 incelemesiyle [A]'dan istişariye inen kalemler (exit 0 kalır):
    ("kambiyo-itiraz", TAM["kambiyo-itiraz"].replace(
        " ve takibin geçici olarak durdurulması", "").replace(
        "3. İtiraz satış dışındaki takip işlemlerini kendiliğinden etkilemediğinden, ekli belgeler "
        "karşısında takibin geçici olarak durdurulmasına karar verilmesi gerekir.\n", "").replace(
        "1. Takibin itirazımız hakkında karar verilinceye kadar geçici olarak durdurulmasına,\n", ""),
     "m.169/a-6"),
    ("itirazin-kaldirilmasi", TAM["itirazin-kaldirilmasi"].replace(
        "2. Borçlunun alacağın yüzde yirmisinden aşağı olmamak üzere icra inkâr tazminatına "
        "mahkûm edilmesine,\n", ""), "inkâr tazminatı"),
    ("itirazin-iptali", TAM["itirazin-iptali"].replace(
        " ve icra inkâr tazminatı", "").replace(
        "2. Davalının alacağın yüzde yirmisinden az olmamak üzere icra inkâr tazminatına mahkûm "
        "edilmesine,\n", ""), "m.67/2"),
])
def test_tipe_ozel_istisari_uyarilar_exit_koduna_dokunmaz(tip, metin, beklenen, tmp_path,
                                                          monkeypatch, capsys):
    u = dd.tip_ozel_uyarilari(metin, tip)
    assert any(beklenen in x for x in u), u
    kod = _cli(tmp_path, monkeypatch, metin, tip, TARAF[tip])
    cikti = capsys.readouterr().out
    assert kod == 0, cikti


def test_itirazin_iptalinde_icra_mahkemesi_basligi_uyarilir():
    metin = TAM["itirazin-iptali"].replace("ÖRNEK 4. ASLİYE TİCARET MAHKEMESİ'NE",
                                           "ÖRNEK 2. İCRA HUKUK MAHKEMESİ'NE")
    u = dd.tip_ozel_uyarilari(metin, "itirazin-iptali")
    assert any("genel mahkemede" in x for x in u), u
    assert not any("genel mahkemede" in x
                   for x in dd.tip_ozel_uyarilari(TAM["itirazin-iptali"], "itirazin-iptali"))


def test_tip_ozel_uyarilari_bozuk_girdide_cokmez_ve_sessiz_kalmaz():
    """İstişari kalem ana akışı ASLA öldürmez, ama koşamadığını da GİZLEMEZ:
    str olmayan girdi tek görünür 'KOŞAMADI' satırı üretir (boş liste 'uyarı
    yok' demektir, 'bakılamadı' değil — sessiz atlama yasağı). None boş metin
    gibi işlenir; kuralı olmayan tip için boş liste doğrudur."""
    u = dd.tip_ozel_uyarilari(12345, "dava")
    assert len(u) == 1 and "KOŞAMADI" in u[0], u
    assert isinstance(dd.tip_ozel_uyarilari(None, "takip-talebi"), list)
    assert dd.tip_ozel_uyarilari(TAM["takip-talebi"], "boyle-bir-tip-yok") == []
