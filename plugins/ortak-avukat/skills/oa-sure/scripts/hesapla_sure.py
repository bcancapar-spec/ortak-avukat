#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
hesapla_sure.py — Türk usul hukuku için DETERMİNİSTİK süre hesaplayıcı (v2).

Felsefe (Ortak Avukat anayasası): Script yalnızca DATE ARİTMETİĞİNİ deterministik
yapar. Hukuki KURALI (sürenin kaç gün/hafta olduğunu) kullanıcı/Claude resmî
kaynaktan (Mevzuat MCP) teyit edip GİRER.

Deterministik: tebliğ+1, gün/hafta ekleme, hafta sonu, resmî tatiller
(scripts/tatiller.json — güncellenebilir), adli tatil/çalışmaya ara
(HMK m.102/104 ve İYUK m.61/m.8-3).
İŞARETLENEN (deterministik DEĞİL): tabloda tanımsız dini bayramlar, özel kanun
süreleri (7036/CMK vb.), parasal kesinlik. Çıktı bunları "ELLE TEYİT" uyarır.

v2: (1) Tatiller scripts/tatiller.json'dan okunur — yıllık güncellenebilir.
(2) İdari yargı çalışmaya ara mekaniği ayrı işlenir: süre araya rastlarsa, ara
bitişini (31 Ağu) İZLEYEN tarihten (1 Eylül) İTİBAREN 7 GÜN (1 Eylül dahil) → 7
Eylül (İYUK m.8/3; Danıştay'ın yerleşik uygulaması ve scriptin kendi gün-sayma
konvansiyonu — başlangıç günü 1. gün sayılır). Matematik olarak 31 Ağu + 7 gün
ile AYNI sonucu verir; HMK m.104 (hukuk: 31 Ağu + 1 hafta) ile de örtüşür.

v0.5.18: (1) ADLİ TATİL REJİMİNİ KURAL TAŞIR (`adli_tatil` alanı; Y-01) — eski
motor rejimi kuralın ön ekinden türetiyordu ve icra sürelerini HMK m.104 ile bir
hafta yanlış uzatıyordu. (2) CMK'da tatil İÇİNDE tebliğde süre tatilde işlemez
(Y-02; YCGK 2022/846). (3) Resmî dini bayram kaydı olmayan yılda "TATİL TAKVİMİ
EKSİK" görünür yazılır (Y-08). (4) BAŞLANGIÇ KAPISI (`--baslangic-kaniti`,
`--teblig-durumu`) ve karşı taraf için KESİN DİL KAPISI. Neden: yanlış olaya ya da
yanlış rejime bağlanan doğru aritmetik, yanlış son gündür.

Kullanım:
  python hesapla_sure.py --teblig 2026-05-20 --kural hmk_istinaf
  python hesapla_sure.py --teblig 2026-07-15 --kural iyuk_istinaf --yargi idari
  python hesapla_sure.py --teblig 2026-08-10 --kural iik_istinaf --yargi icra
  python hesapla_sure.py --teblig 2026-05-20 --sure 2 --birim hafta
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, datetime as _datetime, json, os, sys
from datetime import date, timedelta

ARA_BASLANGIC = (7, 20)   # HMK m.102 / İYUK m.61: 20 Temmuz
ARA_BITIS = (8, 31)       # 31 Ağustos

# GÖMÜLÜ (fallback) kural tablosu — sure_kurallari.json yoksa/bozuksa devreye girer.
# Süreler HUKUKİ kuraldır; resmî kaynaktan (Mevzuat MCP) teyit edilmelidir.
_GOMULU_KURALLAR = {
    "hmk_istinaf":         (2, "hafta",
                        "HMK m.345/1 — istinaf iki hafta; süre ilamın usulen taraflardan HER BİRİNE TEBLİĞİYLE işlemeye başlar (tefhim süreyi BAŞLATMAZ). İstinaf süresine ilişkin özel kanun hükümleri saklıdır."),
    "hmk_temyiz":          (2, "hafta",
                        "HMK m.361/1 — BAM nihai kararına temyiz iki hafta; TEBLİĞ tarihinden işler (tefhim süreyi BAŞLATMAZ)."),
    "hmk_cevap":           (2, "hafta",
                        "HMK m.127 — YAZILI yargılamada cevap iki hafta (dava dilekçesinin tebliğinden); ek süre bu süre içinde istenirse bir defaya mahsus ve EN ÇOK BİR AY. BASİT yargılamada (iş mahkemeleri dahil — 7036 m.7/1) kural hmk_cevap_basit'tir (HMK m.317/2: ek süre en çok iki hafta)."),
    "iik_istinaf":         (2, "hafta",
                        'İİK m.363 — icra mah. istinaf (ESKİ 10 GÜN DEĞİL) · 7499 s.K. (yür. 1/6/2024) süreyi iki haftaya çıkardı VE "tefhim veya" ibaresini metinden ÇIKARDI — süre artık YALNIZ tebliğden işler.'),
    "iik_sikayet":         (7, "gun",
                        "İİK m.16/1 — icra ve iflas dairelerinin işlemlerine şikâyet; işlemin ÖĞRENİLDİĞİ tarihten itibaren yedi gün (m.16/2: hakkın yerine getirilmemesi veya sebepsiz sürüncemede bırakılması hâlinde SÜRESİZ)."),
    "cmk_itiraz":          (2, "hafta",
                        "CMK m.268 — itiraz; ilgililerin kararı ÖĞRENDİĞİ günden itibaren iki hafta (m.35: yüze karşı açıklama; hazır bulunamayana tebliğ). Eski '7 gün' YÜRÜRLÜKTE DEĞİL. CMK m.263 (tutuklunun kurum müdürüne başvurusu — süreyi KESER) saklıdır."),
    "cmk_istinaf":         (2, "hafta",
                        "CMK m.273/1 — istinaf; hükmün GEREKÇESİYLE BİRLİKTE TEBLİĞ edildiği tarihten iki hafta. (Hazır bulunmayanlara ilişkin f.2, 7499 s.K. ile MÜLGA — tek başlangıç: gerekçeli karar tebliği. Savcı yönünden f.3: kararın başsavcılığa geliş tarihi. m.263 saklıdır.)"),
    "cmk_temyiz":          (2, "hafta",
                        "CMK m.291/1 — temyiz; hükmün GEREKÇESİYLE BİRLİKTE TEBLİĞ edildiği tarihten iki hafta (f.2 7499 ile MÜLGA; m.273 ile simetrik; m.263 saklıdır)."),
    "iyuk_dava_idare":     (60, "gun",
                        "İYUK m.7 — idare mah./Danıştay dava açma · 7331 s.K.'nın \"altmış→otuz\" değişikliği m.10/11/13 içindir; m.7 dava açma süresine DOKUNULMAMIŞTIR (sık karıştırılır)."),
    "iyuk_dava_vergi":     (30, "gun",
                        "İYUK m.7 — vergi mah. dava açma"),
    "iyuk_istinaf":        (30, "gun",
                        "İYUK m.45 — BİM istinaf"),
    "iyuk_temyiz":         (30, "gun",
                        "İYUK m.46 — Danıştay temyiz · Süre değişmedi; ANCAK 7589 s.K. (31/7/2026) kapsamı genişletti (yeni f.2; (c) bendi mülga) — geçici m.1/3: 31/7/2026 SONRASI BİM kararlarına uygulanır."),
    "iyuk_yd_itiraz":      (7, "gun",
                        "İYUK m.27/7 — yürütmenin durdurulması istemi hakkında verilen karara İTİRAZ; kararın tebliğini İZLEYEN günden itibaren yedi gün, BİR DEFAYA MAHSUS (itiraz üzerine verilen karar kesindir). İSTİSNA: m.20/A-2/e (ivedi yargılama) ve m.20/B-1/d (merkezî ve ortak sınav) davalarında YD kararlarına İTİRAZ EDİLEMEZ."),
    "iyuk_dava_ivedi":     (30, "gun",
                        "İYUK m.20/A-2/a — İVEDİ YARGILAMA usulünde dava açma; otuz gün. Katalog m.20/A-1: ihale işlemleri (yasaklama hariç), acele kamulaştırma, ÖYK kararları, 2634 turizm satış/tahsis/kiralama, ÇED kararları, 6306 CB kararları. m.20/A-2/b: m.11 UYGULANMAZ. m.45/8: istinaf yolu KAPALI."),
    "iyuk_temyiz_ivedi":   (15, "gun",
                        "İYUK m.20/A-2/g — ivedi yargılamada nihai karara karşı TEMYİZ; tebliğ tarihinden on beş gün (istinaf YOK — m.45/8; temyize cevap süresi m.20/A-2/ı on beş gün)."),
    "iyuk_dava_sinav":     (10, "gun",
                        "İYUK m.20/B-1/a — MEB ve ÖSYM'nin MERKEZÎ VE ORTAK SINAVLARINA ilişkin davalarda dava açma; on gün. m.20/B-1/b: m.11 UYGULANMAZ."),
    "iyuk_temyiz_sinav":   (5, "gun",
                        "İYUK m.20/B-1/f — merkezî ve ortak sınav davalarında nihai karara karşı TEMYİZ; tebliğ tarihinden beş gün (temyize cevap süresi m.20/B-1/ğ beş gün)."),
    "iyuk_temyiz_cevap":   (30, "gun",
                        "İYUK m.48/3 — temyiz dilekçesine CEVAP; tebliğ tarihini izleyen otuz gün. Cevap veren, kararı süresinde temyiz etmemiş olsa bile dilekçesinde temyiz isteminde bulunabilir (bu dilekçe temyiz dilekçesi yerine geçer)."),
    "iyuk_temyiz_ozel_7gun": (7, "gun",
                        "İYUK m.48/6 son cümle — temyiz isteminde bulunulmamış sayılmasına (m.48/2) ve temyiz isteminin reddine ilişkin kararlara karşı tebliğ tarihini İZLEYEN günden itibaren yedi gün; İYUK m.45/2 ek cümle (7524 s.K.) — BİM'in m.48/7 uyarınca verdiği kararlara karşı da yedi gün."),
    "amme_6183_m58":       (15, "gun",
                        "6183 m.58 — ödeme emrine karşı dava; tebliğ tarihinden itibaren 15 gün (7061 s.K. ile 7→15). Ödeme emri bir TAHSİLAT işlemidir: dava açılması tahsili KENDİLİĞİNDEN durdurmaz (İYUK m.27/4) — ayrıca yürütmenin durdurulması istenir."),
    "aym_bireysel":        (30, "gun",
                        "6216 m.47/5 — bireysel başvuru otuz gün: başvuru yollarının TÜKETİLDİĞİ tarihten; başvuru yolu öngörülmemişse ihlalin ÖĞRENİLDİĞİ tarihten (AYM İçtüzüğü m.64/1 aynı). Haklı mazerette mazeretin kalktığı tarihten on beş gün (aym_bireysel_mazeret); eksik evrak için verilen süre en çok on beş gün (m.47/6)."),
    # ── İŞ HUKUKU (2026-09-10, MCP teyitli) ────────────────────────────
    "is_ise_iade_arabulucu": (1, "ay",
                        "4857 m.20/1 (Değişik: 7036 s.K. m.11) — işe iade: iş sözleşmesi feshedilen işçi, fesih bildiriminde sebep gösterilmediği veya gösterilen sebebin geçerli olmadığı iddiasıyla FESİH BİLDİRİMİNİN TEBLİĞİ tarihinden itibaren BİR AY içinde işe iade talebiyle ARABULUCUYA BAŞVURMAK ZORUNDADIR. Dava değil, arabuluculuk başvurusudur (7036 m.3 dava şartı). HMK m.92: ay olarak belirlenen sürede son ayın SAYILI GÜNÜ esastır — Y. 9. HD E.2016/10425 K.2017/8620 (23.05.2017) ertesi günden hesaplamayı 'yasanın düzenlemesine AÇIKÇA AYKIRI' bulmuştur."),
    "is_ise_iade_dava":    (2, "hafta",
                        "4857 m.20/1 (Değişik: 7036 s.K. m.11) — arabuluculuk faaliyeti sonunda ANLAŞMAYA VARILAMAMASI hâlinde, SON TUTANAĞIN DÜZENLENDİĞİ tarihten itibaren İKİ HAFTA içinde iş mahkemesinde dava açılabilir (taraflar anlaşırsa aynı sürede ÖZEL HAKEME de gidilebilir). Süre HAK DÜŞÜRÜCÜdür, resen gözetilir. Başlangıç türü 'olay'dır: tebliğ değil, tutanağın DÜZENLENME anı. Başlangıç içtihatta TARTIŞMALIDIR — bkz. çıktıdaki BAŞLANGIÇ TARTIŞMALI uyarısı."),
    "is_ise_iade_arabulucu_ret": (2, "hafta",
                        "4857 m.20/1 son cümleler (Değişik: 7036 s.K. m.11) — arabulucuya başvurmaksızın DOĞRUDAN dava açılması sebebiyle davanın USULDEN REDDİ hâlinde ret kararı taraflara RESEN tebliğ edilir; KESİNLEŞEN ret kararının da resen tebliğinden itibaren İKİ HAFTA içinde arabulucuya başvurulabilir. Bu, dava şartı eksikliğini telafi eden İKİNCİ bir penceredir; kaçırılırsa işe iade yolu tümüyle kapanır."),
    "is_ise_baslatma_basvuru": (10, "isgunu",
                        "4857 m.21/5 — işçi, KESİNLEŞEN mahkeme veya özel hakem kararının TEBLİĞİNDEN itibaren ON İŞGÜNÜ içinde işe başlamak için İŞVERENE başvuruda bulunmak zorundadır. TAKVİM GÜNÜ DEĞİL İŞ GÜNÜdür (hafta sonu ve resmî tatiller sayılmaz). m.21/6: bu sürede başvurulmazsa işverence yapılmış fesih GEÇERLİ sayılır ve işveren yalnız onun sonuçlarından sorumlu olur — kazanılmış işe iade kararı işlevsizleşir."),
    "is_ise_baslatma_isveren": (1, "ay",
                        "4857 m.21/1 — feshin geçersizliğine karar verildiğinde işveren, işçiyi BİR AY içinde İŞE BAŞLATMAK zorundadır; işçiyi BAŞVURUSU ÜZERİNE bir ay içinde işe başlatmazsa en az DÖRT en çok SEKİZ aylık ücreti tutarında tazminat öder. Süre işçinin BAŞVURUSU (olay) ile başlar. İŞVEREN vekili için takvim; işçi vekili için karşı tarafın süresini denetleme kalemidir."),
    "is_zamanasimi_5yil":  (5, "yil",
                        "4857 Ek m.3 (Ek: 7036 s.K. m.15) — iş sözleşmesinden kaynaklanmak kaydıyla HANGİ KANUNA TABİ OLURSA OLSUN, YILLIK İZİN ÜCRETİ ile (a) kıdem tazminatı, (b) bildirim şartına uyulmaksızın fesihten kaynaklanan tazminat [ihbar], (c) kötüniyet tazminatı, (d) eşit davranma ilkesine uyulmaksızın fesihten kaynaklanan tazminat için ZAMANAŞIMI BEŞ YILDIR. MADDİ HUKUK süresidir: adli tatil uzatması UYGULANMAZ; zamanaşımı TBK m.153-158 uyarınca durur/kesilir — script bunu hesaplamaz. Ücret, fazla mesai, UBGT gibi diğer alacaklarda TBK m.147/1 beş yıllık süre ayrıca değerlendirilir."),
    # ── v0.5.18 (Y-04/Y-05, AYM/AİHM — 2026-10-05, MCP teyitli) ────────
    "iik_temyiz":          (2, "hafta",
                        "İİK m.364/2 (Değişik: 7499 s.K.) — icra mahkemesi işlerinde BAM kararına temyiz iki hafta; TEBLİĞ tarihinden işler, inceleme HMK'ya göre yapılır (m.364/1 miktar/değer eşiği — kullanım anında teyit et)."),
    "iik_odeme_emrine_itiraz": (7, "gun",
                        "İİK m.62/1 — genel haciz yoluyla takipte ödeme emrine itiraz yedi gün; ödeme emrinin TEBLİĞİNDEN itibaren icra dairesine dilekçeyle veya sözlü; imza itirazı ayrıca ve açıkça bildirilmezse imza kabul edilmiş sayılır (m.62/son). Süresinde itiraz edilmezse takip kesinleşir; mazeret hâlinde İİK m.65 (iik_gecikmis_itiraz)."),
    "iik_gecikmis_itiraz": (3, "gun",
                        "İİK m.65/2 — borçlu kusuru olmaksızın bir mani yüzünden süresinde itiraz edemediyse MANİİN KALKTIĞI günden itibaren üç gün içinde mazeret delilleriyle itiraz eder ve masrafı öder; dış sınır m.65/1: paraya çevirme işlemi bitinceye kadar."),
    "iik_itirazin_iptali": (1, "yil",
                        "İİK m.67/1 — itirazın iptali davası, itirazın alacaklıya TEBLİĞİNDEN itibaren bir yıl içinde genel mahkemede açılır; süre geçerse genel hükümlere göre dava hakkı saklıdır (m.67/son) ama takibin bu dava yoluyla sürdürülmesi ve icra inkâr tazminatı imkânı kaybedilir."),
    "iik_itirazin_kaldirilmasi": (6, "ay",
                        "İİK m.68/1 ve m.68/a-1 — itirazın kesin veya geçici kaldırılması, itirazın alacaklıya TEBLİĞİNDEN itibaren altı ay içinde icra mahkemesinden istenir; bu süre içinde istenmezse YENİDEN İLÂMSIZ TAKİP YAPILAMAZ (m.68/1 son cümle)."),
    "iik_borctan_kurtulma": (7, "gun",
                        "İİK m.69/2 — itirazın muvakkaten kaldırılması kararının TEFHİM veya TEBLİĞİNDEN itibaren yedi gün içinde borçtan kurtulma davası; dinlenebilmesi için alacağın yüzde on beşi ilk duruşmaya kadar depo/teminat edilmeli; süresinde açılmazsa kaldırma kararı ve muvakkat haciz kesinleşir (m.69/3)."),
    "iik_89_ihbarname_itiraz": (7, "gun",
                        "İİK m.89/2-3 — birinci ve ikinci haciz ihbarnamesine üçüncü şahsın itirazı: ihbarnamenin kendisine TEBLİĞİNDEN itibaren yedi gün içinde icra dairesine yazılı veya sözlü; itiraz edilmezse mal yedinde veya borç zimmetinde sayılır."),
    "iik_89_menfi_tespit": (15, "gun",
                        "İİK m.89/3 — üçüncü ihbarnameyi alan üçüncü şahıs on beş gün içinde parayı ödemek veya malı teslim etmek YA DA menfi tespit davası açmak zorundadır; dava açıldığına dair belge bildirimden itibaren yirmi gün içinde icra dairesine teslim edilirse cebri icra işlemleri durur."),
    "iik_ihalenin_feshi":  (7, "gun",
                        "İİK m.134/2 — ihalenin feshi, icra mahkemesinden şikâyet yoluyla İHALE TARİHİNDEN itibaren yedi gün içinde (talep hakkı maddede sayılan kişilere aittir); satış ilanı tebliğ edilmemişse veya esaslı hata/fesada sonradan vakıf olunmuşsa süre ITTILA tarihinden başlar, ancak ihale kararının elektronik satış portalında ilanından itibaren BİR YILI geçemez (iik_ihalenin_feshi_azami)."),
    "iik_ihalenin_feshi_azami": (1, "yil",
                        "İİK m.134 (ıttıla hâli) — ihalenin feshi şikâyetinde öğrenmeye bağlı süre, ihalenin yapıldığına ilişkin kararın elektronik satış portalında İLAN EDİLDİĞİ tarihten itibaren bir yılı geçemez (dış sınır)."),
    "iik_kambiyo_itiraz":  (5, "gun",
                        "İİK m.168/3-5 — kambiyo senetlerine dayalı takipte ödeme emrinin TEBLİĞİNDEN itibaren beş gün içinde icra mahkemesine: senedin kambiyo vasfına şikâyet (b.3), imza itirazı (b.4), borca veya yetkiye itiraz (b.5)."),
    "iik_ihtiyati_haciz_itiraz": (7, "gun",
                        "İİK m.265/1-2 — ihtiyati hacze itiraz yedi gün: borçlu için huzurunda yapılan hacizlerde HACZİN TATBİKİNDEN, aksi hâlde haciz TUTANAĞININ TEBLİĞİNDEN; menfaati ihlal edilen üçüncü kişi için ÖĞRENMEDEN; kararı veren mahkemeye."),
    "iik_icra_ceza_sikayet": (3, "ay",
                        "İİK m.347 — icra ceza bölümündeki fiillerden şikâyet hakkı fiilin ÖĞRENİLDİĞİ tarihten itibaren üç ay ve her hâlde fiilin işlendiği tarihten itibaren bir yıl geçmekle DÜŞER — iki sınır birlikte denetlenir (iik_icra_ceza_sikayet_azami)."),
    "iik_icra_ceza_sikayet_azami": (1, "yil",
                        "İİK m.347 — şikâyet hakkı her hâlde fiilin İŞLENDİĞİ tarihten itibaren bir yıl geçmekle düşer (dış sınır)."),
    "hmk_dosya_gonderme":  (2, "hafta",
                        "HMK m.20/1 — görevsizlik veya yetkisizlik kararından sonra dosyanın gönderilmesi talebi iki hafta: karar verildiği anda kesinse TEBLİĞDEN; kanun yoluna başvurulmayıp kesinleşmişse KESİNLEŞME tarihinden; kanun yoluna başvurulmuşsa başvurunun reddi kararının TEBLİĞİNDEN; aksi hâlde dava AÇILMAMIŞ SAYILIR (resen)."),
    "hmk_cevap_basit":     (2, "hafta",
                        "HMK m.317/2 — BASİT yargılamada (iş mahkemeleri dahil — 7036 m.7/1) cevap süresi dava dilekçesinin TEBLİĞİNDEN itibaren iki hafta; ek süre ancak bu süre içinde istenirse, bir defaya mahsus ve EN ÇOK İKİ HAFTA (cevap süresinin bitiminden işler) — yazılı yargılamadaki bir aylık sınır (m.127) burada YOKTUR."),
    "hmk_on_inceleme_belge_sunma": (2, "hafta",
                        "HMK m.139/1-ç — ön inceleme davetiyesinin TEBLİĞİNDEN itibaren iki haftalık KESİN süre: dilekçede gösterilip sunulmayan belgeler sunulur, başka yerden getirtilecekler için gereken açıklama yapılır; m.140/5 — yerine getirilmezse o delile dayanmaktan VAZGEÇMİŞ sayılma kararı verilir."),
    "hmk_tedbir_itiraz":   (1, "hafta",
                        "HMK m.394/2-3 — karşı taraf dinlenmeden verilen ihtiyati tedbire itiraz bir hafta: uygulamada hazırsa UYGULAMADAN, değilse uygulama tutanağının TEBLİĞİNDEN; menfaati açıkça ihlal edilen üçüncü kişi için ÖĞRENMEDEN; itiraz kural olarak icrayı durdurmaz (m.394/1)."),
    "hmk_tedbir_esas_dava": (2, "hafta",
                        "HMK m.397/1 — dava açılmadan verilen ihtiyati tedbirde, kararın UYGULANMASINI TALEP ETTİĞİ tarihten itibaren iki hafta içinde esas dava açılmalı VE dava açıldığına dair evrak kararı uygulayan memura ibrazla dosyaya konup karşılığında belge alınmalıdır; aksi hâlde tedbir KENDİLİĞİNDEN kalkar."),
    # ── v0.5.18 K1 (T5-1 CANLI KUSUR — 2026-10-07, resmî metin teyitli) ─────────
    # İstifada vekâletin devam süresi: MK-2 kuralsız çağrısı (--sure/--birim) rejimi
    # --yargi hukuk'tan alıp HMK m.104 ile uzatıyor, yazın müvekkile GEÇ tarih veriyordu.
    "hmk_istifa_vekalet_devam": (2, "hafta",
                        "HMK m.82/1 — istifa eden vekilin vekâlet görevi, istifanın müvekkiline TEBLİĞİNDEN itibaren iki hafta süreyle devam eder; m.82/2 — vekâlet veren davayı takip etmez ve başka bir vekil de görevlendirmezse tarafın yokluğu hükümleri uygulanır; m.82/3 — bu hususlar istifa dilekçesiyle birlikte vekâlet verene İHTAREN bildirilir. Mahkemeye verilen istifa dilekçesi müvekkile tebliğ yerine geçmez (tebliğ tarihi belgeli olmalı). Av.K. m.41'deki on beş günle EŞİTLENMEZ — iki tarih ayrı satırda hesaplanır (avk_istifa_vekalet_devam); müvekkile 'yeni vekil bu tarihten ÖNCE' uyarısı ERKEN tarihle verilir."),
    "avk_istifa_vekalet_devam": (15, "gun",
                        "Av.K. m.41/1 — belli bir işi takipten veya savunmadan isteği ile çekilen avukatın o işe ait vekâlet görevi, durumu müvekkiline TEBLİĞİNDEN itibaren on beş gün süre ile devam eder (m.41/2: adli müzaheret bürosu ya da baro başkanınca tayin edilen avukat kaçınılmaz sebep veya haklı özür olmadıkça çekinemez; takdir tayin eden makamındır). HMK m.82/1'deki iki haftayla EŞİTLENMEZ — iki tarih ayrı satırda hesaplanır (hmk_istifa_vekalet_devam); müvekkile 'yeni vekil bu tarihten ÖNCE' uyarısı ERKEN tarihle verilir. Y. 13. HD E.2016/23630 K.2019/746 ve Y. 7. HD E.2013/26308 K.2013/21244: istifa müvekkile tebliğ edilmedikçe vekâlet görevi devam eder ve vekile yapılan tebligat süreyi başlatır."),
    "aym_bireysel_mazeret": (15, "gun",
                        "6216 m.47/5 (ikinci cümle) — haklı mazeret nedeniyle süresinde başvuramayan, MAZERETİN KALKTIĞI tarihten itibaren on beş gün içinde mazeretini belgeleyen delillerle başvurabilir; mazeretin kabulü Mahkemenin takdirindedir (AYM İçtüzüğü m.64/2)."),
    "aihm_basvuru":        (4, "ay",
                        "AİHS m.35/1 — 15 No'lu Protokol ile altı aydan DÖRT aya indirildi (HUDOC sınıflaması: 'Four-month period (former six-month)'); nihai iç hukuk kararından itibaren, iç hukukta yazılı tebliğ öngörülüyorsa TEBLİĞDEN işler (Sabri Güneş/Türkiye [BD] § 53 — Worm/Avusturya); son gün hafta sonu veya resmî tatile rastlasa da UZAMAZ (Sabri Güneş/Türkiye [BD], no. 27396/06, 29.06.2012, §§ 60-61)."),
}

# B-21 (v0.5.14) — teyit tarihi kaynak METNİNDEN AYRI alanda tutulur; böylece
# aynı bilginin iki kaynağı (metin içi şerh + JSON alanı) doğup ayrışamaz.
_GOMULU_TEYIT = {
    "hmk_istinaf":         "2026-10-05",
    "hmk_temyiz":          "2026-10-05",
    "hmk_cevap":           "2026-10-05",
    "iik_istinaf":         "2026-10-05",
    "iik_sikayet":         "2026-10-05",
    "cmk_itiraz":          "2026-08-31",
    "cmk_istinaf":         "2026-08-31",
    "cmk_temyiz":          "2026-08-31",
    "iyuk_dava_idare":     "2026-08-31",
    "iyuk_dava_vergi":     "2026-08-31",
    "iyuk_istinaf":        "2026-08-31",
    "iyuk_temyiz":         "2026-08-31",
    "iyuk_yd_itiraz":      "2026-08-31",
    "iyuk_dava_ivedi":     "2026-08-31",
    "iyuk_temyiz_ivedi":   "2026-08-31",
    "iyuk_dava_sinav":     "2026-08-31",
    "iyuk_temyiz_sinav":   "2026-08-31",
    "iyuk_temyiz_cevap":   "2026-08-31",
    "iyuk_temyiz_ozel_7gun": "2026-08-31",
    "amme_6183_m58":       "2026-08-31",
    "aym_bireysel":        "2026-10-05",
    "is_ise_iade_arabulucu": "2026-09-10",
    "is_ise_iade_dava":    "2026-09-10",
    "is_ise_iade_arabulucu_ret": "2026-09-10",
    "is_ise_baslatma_basvuru": "2026-09-10",
    "is_ise_baslatma_isveren": "2026-09-10",
    "is_zamanasimi_5yil":  "2026-09-10",
    "iik_temyiz":          "2026-10-05",
    "iik_odeme_emrine_itiraz": "2026-10-05",
    "iik_gecikmis_itiraz": "2026-10-05",
    "iik_itirazin_iptali": "2026-10-05",
    "iik_itirazin_kaldirilmasi": "2026-10-05",
    "iik_borctan_kurtulma": "2026-10-05",
    "iik_89_ihbarname_itiraz": "2026-10-05",
    "iik_89_menfi_tespit": "2026-10-05",
    "iik_ihalenin_feshi":  "2026-10-05",
    "iik_ihalenin_feshi_azami": "2026-10-05",
    "iik_kambiyo_itiraz":  "2026-10-05",
    "iik_ihtiyati_haciz_itiraz": "2026-10-05",
    "iik_icra_ceza_sikayet": "2026-10-05",
    "iik_icra_ceza_sikayet_azami": "2026-10-05",
    "hmk_dosya_gonderme":  "2026-10-05",
    "hmk_cevap_basit":     "2026-10-05",
    "hmk_on_inceleme_belge_sunma": "2026-10-05",
    "hmk_tedbir_itiraz":   "2026-10-05",
    "hmk_tedbir_esas_dava": "2026-10-05",
    "hmk_istifa_vekalet_devam": "2026-10-07",
    "avk_istifa_vekalet_devam": "2026-10-07",
    "aym_bireysel_mazeret": "2026-10-05",
    "aihm_basvuru":        "2026-10-05",
}

# B-20 (v0.5.14) — kuralın hukuken İZİN VERDİĞİ başlangıç türleri. Script
# NİTELENDİRME YAPMAZ: yalnız seçilen türün bu kümede olup olmadığına bakar.
_GOMULU_BASLANGIC = {
    "hmk_istinaf":            ["teblig"],
    "hmk_temyiz":             ["teblig"],
    "hmk_cevap":              ["teblig"],
    "iik_istinaf":            ["teblig"],
    "iik_sikayet":            ["ogrenme", "teblig"],
    "cmk_itiraz":             ["ogrenme", "teblig", "tefhim"],
    "cmk_istinaf":            ["teblig"],
    "cmk_temyiz":             ["teblig"],
    "iyuk_dava_idare":        ["teblig", "ogrenme"],
    "iyuk_dava_vergi":        ["teblig", "ogrenme"],
    "iyuk_istinaf":           ["teblig"],
    "iyuk_temyiz":            ["teblig"],
    "iyuk_yd_itiraz":         ["teblig"],
    "iyuk_dava_ivedi":        ["teblig", "ogrenme"],
    "iyuk_temyiz_ivedi":      ["teblig"],
    "iyuk_dava_sinav":        ["teblig", "ogrenme"],
    "iyuk_temyiz_sinav":      ["teblig"],
    "iyuk_temyiz_cevap":      ["teblig"],
    "iyuk_temyiz_ozel_7gun":  ["teblig"],
    "amme_6183_m58":          ["teblig"],
    "aym_bireysel":           ["teblig", "ogrenme"],
    "is_ise_iade_arabulucu":  ["teblig"],
    "is_ise_iade_dava":       ["olay"],
    "is_ise_iade_arabulucu_ret": ["teblig"],
    "is_ise_baslatma_basvuru": ["teblig"],
    "is_ise_baslatma_isveren": ["olay"],
    "is_zamanasimi_5yil":     ["olay", "ogrenme"],
    "iik_temyiz":             ["teblig"],
    "iik_odeme_emrine_itiraz": ["teblig"],
    "iik_gecikmis_itiraz":    ["olay"],
    "iik_itirazin_iptali":    ["teblig"],
    "iik_itirazin_kaldirilmasi": ["teblig"],
    "iik_borctan_kurtulma":   ["teblig", "tefhim"],
    "iik_89_ihbarname_itiraz": ["teblig"],
    "iik_89_menfi_tespit":    ["teblig"],
    "iik_ihalenin_feshi":     ["olay", "ogrenme"],
    "iik_ihalenin_feshi_azami": ["olay"],
    "iik_kambiyo_itiraz":     ["teblig"],
    "iik_ihtiyati_haciz_itiraz": ["olay", "teblig", "ogrenme"],
    "iik_icra_ceza_sikayet":  ["ogrenme"],
    "iik_icra_ceza_sikayet_azami": ["olay"],
    "hmk_dosya_gonderme":     ["teblig", "olay"],
    "hmk_cevap_basit":        ["teblig"],
    "hmk_on_inceleme_belge_sunma": ["teblig"],
    "hmk_tedbir_itiraz":      ["olay", "teblig", "ogrenme"],
    "hmk_tedbir_esas_dava":   ["olay"],
    "hmk_istifa_vekalet_devam": ["teblig"],
    "avk_istifa_vekalet_devam": ["teblig"],
    "aym_bireysel_mazeret":   ["olay"],
    "aihm_basvuru":           ["teblig", "ogrenme"],
}

# >>> v0.5.18 REJİM TABLOSU (sure_kurallari.json ile BİREBİR ikiz — tests/test_v0518_sure.py)
# ADLİ TATİL REJİMİ KURAL DÜZEYİNDEDİR (Y-01/Y-02, 2026-10-03 denetimi). Rejim artık
# kuralın ön ekinden (KURAL_KOLU) TÜRETİLMEZ: icra kuralları 'hukuk' koluna bağlıydı
# ve HMK m.104 ile bir hafta YANLIŞ uzatılıyordu (10.08 tebliğ → 07.09; doğrusu
# istinaf 24.08, şikâyet 17.08). Değerler: hmk104 | iyuk8 | cmk331 | uygulanmaz.
# teyitli=False → resmî kaynakla teyit edilemedi; motor TEMKİNLİ (erken) tarihi seçer
# ve karşı tarafa kesin dil kurmaz. son_gun_kaymasi=False → yalnız AİHM (Sabri Güneş).
_RD_HMK104 = ("HMK m.104 — adli tatile tabi dava ve işlerde HMK'nın tayin ettiği sürenin bitimi "
              "tatile rastlarsa süre tatilin bittiği günden itibaren BİR HAFTA uzar; HMK m.103 "
              "kapsamındaki işte (ör. işçinin açtığı dava, nafaka, ivedi iş) uzatma YOKTUR → "
              "--adli-tatil-istisna")
_RD_IYUK8 = ("İYUK m.8/3 — İYUK'ta yazılı sürenin bitimi çalışmaya ara vermeye rastlarsa ara "
             "vermenin sona erdiği günü izleyen tarihten itibaren YEDİ GÜN uzar; İYUK m.62 nöbetçi "
             "işlerinde uzatma YOKTUR → --adli-tatil-istisna")
_RD_CMK331 = ("CMK m.331/4 — adli tatile rastlayan süreler İŞLEMEZ ve tatilin bittiği günden "
              "itibaren ÜÇ GÜN uzar; tatil İÇİNDE tebliğde süre tatilde işlemez, TAM süre tatil "
              "bitiminden sonra işler (YCGK 26.11.2013 E.2013/2-272 K.2013/524; YCGK 27.12.2022 "
              "E.2021/319 K.2022/846; 14.02.1934 t. 47/1 s. İBK); tutuklu işlerde de aynıdır (YCGK "
              "E.2021/319 K.2022/846; AYM Ramazan Seçen, B. No: 2021/37483, 6/1/2026)")
_RD_ICRA = ("İİK m.18/1 — icra mahkemesine arz edilen hususlar İVEDİ işlerdendir (HMK m.103/1-h); "
            "icra dairelerinde ve icra mahkemelerinde adli tatil hükümleri (HMK m.102/104) "
            "uygulanmaz: son gün ADLİ TATİLE rastlasa da süre UZAMAZ (resmî tatil/hafta sonu "
            "kayması ayrıca İİK m.19/3 ile yapılır) — Y. 12. HD E.2025/7548 K.2025/7898; "
            "E.2024/7040 K.2024/10869; E.2022/11578 K.2022/11538")
_RD_ICRA_ITIRAZ = ("İİK m.18/1 — icra mahkemesine arz edilen hususlar İVEDİ işlerdendir (HMK m.103/1-h); "
                   "icra dairelerinde ve icra mahkemelerinde adli tatil hükümleri (HMK m.102/104) "
                   "uygulanmaz: son gün ADLİ TATİLE rastlasa da süre UZAMAZ (resmî tatil/hafta sonu "
                   "kayması ayrıca İİK m.19/3 ile yapılır) — Y. 12. HD E.2025/7548 K.2025/7898; "
                   "E.2024/7040 K.2024/10869; E.2022/11578 K.2022/11538; ödeme emrine itiraz süresi için "
                   "ayrıca Y. 23. HD E.2013/8404 K.2013/7933 (HMK m.104 HMK dışındaki sürelere "
                   "uygulanmaz)")
_RD_ICRA_DAVA = ("İİK'nın koyduğu süre (HMK'nın değil) — HMK m.104 yalnız HMK'nın tayin ettiği "
                 "sürelere uygulanır (Y. 23. HD E.2013/8404 K.2013/7933, İİK m.62 için); bu gerekçenin "
                 "genel mahkemede açılan dava süresine aynen uygulanacağı ayrıca TEYİT EDİLMEDİ → "
                 "TEMKİNLİ: uzatma YOK (erken tarih)")
_RD_ICRA_IHTIYATI = ("HMK m.103/1-a — ihtiyati haciz talepleri ile bunlara karşı itiraz ve diğer "
                     "başvurular adli tatilde GÖRÜLÜR (adli tatile tabi iş değildir); HMK m.104 uzatması "
                     "yalnız adli tatile tabi işlerdeki sürelere uygulanır — İİK m.265 itiraz süresi "
                     "uzamaz")
_RD_ICRA_CEZA = ("TEYİT BEKLİYOR — İİK m.347 süresi geçmekle şikâyet hakkı DÜŞER (hak düşürücü); HMK "
                 "m.104 yalnız HMK'nın tayin ettiği sürelere ilişkindir, CMK m.331/4'ün bu hak "
                 "düşürücü süreye uygulanıp uygulanmayacağı resmî kaynakla teyit edilemedi → TEMKİNLİ: "
                 "uzatma YOK (erken tarih)")
_RD_TEDBIR = ("HMK m.103/1-a — ihtiyati tedbir, ihtiyati haciz ve delil tespiti talepleri ile "
              "bunlara karşı itiraz ve diğer başvurular adli tatilde görülür; HMK m.104 uzatması "
              "uygulanmaz")
_RD_TEDBIR_DAVA = ("TEYİT BEKLİYOR — HMK m.397/1 HMK'nın kendi süresidir; esas dava adli tatile tabiyse "
                   "HMK m.104 lafzen uygulanabilir görünür, ancak tedbirin kendisi HMK m.103/1-a işidir "
                   "ve uzatmanın bu süreye uygulanıp uygulanmayacağı resmî kaynakla teyit edilemedi → "
                   "TEMKİNLİ: uzatma YOK (erken tarih); geç okuma (31 Ağu + 1 hafta) güçlü olduğundan "
                   "karşı tarafa kesin dil kurulmaz")
# v0.5.18 K1 (T5-1) — İSTİFA SÜRELERİ: `hmk_tedbir_esas_dava` kalıbı. NEDEN VAR: müvekkile
# giden tarih ERKEN olmalı (hak kaybı önleme); geç okuma yalnız avukatın takip sınırı.
# Metinler Yargı PRO mevzuat_getir ile okundu (2026-10-07): HMK m.82, m.103/3, m.104;
# Av.K. m.41. Kararlar ictihat_getir tam metin: Y. 23. HD E.2013/8404 K.2013/7933;
# Y. 13. HD E.2016/23630 K.2019/746; Y. 7. HD E.2013/26308 K.2013/21244.
_RD_ISTIFA_HMK = ("TEYİT BEKLİYOR — HMK m.82/1 HMK'nın kendi süresidir; esas dava adli tatile tabiyse "
                  "HMK m.104 lafzen uygulanabilir görünür, ancak m.104'ün m.82/1 süresine uygulandığına "
                  "ya da reddedildiğine dair karar bulunamadı (Yargı PRO ictihat_ara, 2026-10-07; Y. 13. HD "
                  "E.2016/23630 K.2019/746 ve Y. 7. HD E.2013/26308 K.2013/21244 m.41/m.82'yi uygular, "
                  "tatil uzamasına girmez). Süre tatilde İŞLER: HMK m.103/3 — adli tatilde her türlü "
                  "tebligat yapılır, istifa tebliği tatilde geçerlidir → TEMKİNLİ: uzatma YOK (erken tarih) "
                  "— müvekkile 'yeni vekil bu tarihten ÖNCE' uyarısı bu tarihle verilir; geç okuma (31 Ağu "
                  "+ 1 hafta) yalnız istifa eden avukatın kendi takip sınırıdır, karşı tarafa kesin dil "
                  "kurulmaz")
_RD_ISTIFA_AVK = ("TEYİT BEKLİYOR — Av.K. m.41 süresi HMK'nın tayin ettiği bir süre DEĞİLDİR; HMK m.104 "
                  "yalnız 'bu Kanunun tayin ettiği sürelere' uygulanır (Y. 23. HD E.2013/8404 K.2013/7933, "
                  "İİK m.62 süresi için — Av.K. m.41'e uygulanması kıyastır); m.104'ün bu süreye "
                  "uygulandığına dair karar bulunamadı (Yargı PRO ictihat_ara, 2026-10-07). Süre tatilde "
                  "İŞLER: HMK m.103/3 — adli tatilde her türlü tebligat yapılır → TEMKİNLİ: uzatma YOK "
                  "(erken tarih) — müvekkile 'yeni vekil bu tarihten ÖNCE' uyarısı bu tarihle verilir; geç "
                  "okuma (31 Ağu + 1 hafta) yalnız istifa eden avukatın kendi takip sınırıdır, karşı tarafa "
                  "kesin dil kurulmaz; son gün hafta sonu/resmî tatile rastlarsa kayma kıyasen (HMK m.93) "
                  "yapılır")
_RD_IS = ("4857 süresi (HMK'nın değil) — HMK m.104 uygulanmaz; işçinin açtığı iş davası HMK "
          "m.103/1-ç ile adli tatilde görülür ve işe iade süresinde m.104 uzatması uygulanamaz "
          "(Y. 9. HD E.2016/1261 K.2016/22196)")
_RD_IS_MADDI = ("maddi hukuk süresi (zamanaşımı) — adli tatil uzatması yok; durma/kesilme TBK "
                "m.153-158 (script hesaplamaz)")
_RD_AYM = ("TEYİT BEKLİYOR — 6216 sayılı Kanun ve AYM İçtüzüğünde adli tatil/süre uzatması hükmü "
           "yok (Mevzuat MCP içinde-ara 'tatil' → yalnız 6216 m.8, üye seçimi); 6216 m.49/7 "
           "hüküm bulunmayan hâllerde ilgili usul kanunlarının 'bireysel başvurunun niteliğine "
           "uygun' hükümlerine yollasa da uzatmaya GÜVENME → TEMKİNLİ: uzatma YOK (erken tarih)")
_RD_AIHM = ("AİHS m.35/1 — süre Sözleşme ölçütleriyle hesaplanır, iç hukukun tatil ve uzatma "
            "kuralları dikkate alınmaz (Sabri Güneş/Türkiye [BD], no. 27396/06, 29.06.2012, §§ "
            "48-49, 60-61): adli tatil uzatması YOK, son gün kayması YOK")
_RD_AMME = ("İYUK m.8/3 uzatmasının ÖZEL KANUN süresine uygulanması TARTIŞMALIDIR (Danıştay 7. D. "
            "E.2000/5685 K.2002/3522 oyçokluğu — A-20); motor uzatır ama GÜVENLİ PLAN ham "
            "bitiştir")
_GOMULU_REJIM_SATIRLARI = {
    # kural:                      (adli_tatil,   teyitli, son_gun_kaymasi, dayanak)
    "hmk_istinaf":                 ("hmk104",     True, True, _RD_HMK104),
    "hmk_temyiz":                  ("hmk104",     True, True, _RD_HMK104),
    "hmk_cevap":                   ("hmk104",     True, True, _RD_HMK104),
    "iik_istinaf":                 ("uygulanmaz", True, True, _RD_ICRA),
    "iik_sikayet":                 ("uygulanmaz", True, True, _RD_ICRA),
    "cmk_itiraz":                  ("cmk331",     True, True, _RD_CMK331),
    "cmk_istinaf":                 ("cmk331",     True, True, _RD_CMK331),
    "cmk_temyiz":                  ("cmk331",     True, True, _RD_CMK331),
    "iyuk_dava_idare":             ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_dava_vergi":             ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_istinaf":                ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_temyiz":                 ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_yd_itiraz":              ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_dava_ivedi":             ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_temyiz_ivedi":           ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_dava_sinav":             ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_temyiz_sinav":           ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_temyiz_cevap":           ("iyuk8",      True, True, _RD_IYUK8),
    "iyuk_temyiz_ozel_7gun":       ("iyuk8",      True, True, _RD_IYUK8),
    "amme_6183_m58":               ("iyuk8",      False, True, _RD_AMME),
    "aym_bireysel":                ("uygulanmaz", False, True, _RD_AYM),
    "is_ise_iade_arabulucu":       ("uygulanmaz", True, True, _RD_IS),
    "is_ise_iade_dava":            ("uygulanmaz", True, True, _RD_IS),
    "is_ise_iade_arabulucu_ret":   ("uygulanmaz", True, True, _RD_IS),
    "is_ise_baslatma_basvuru":     ("uygulanmaz", True, True, _RD_IS),
    "is_ise_baslatma_isveren":     ("uygulanmaz", True, True, _RD_IS),
    "is_zamanasimi_5yil":          ("uygulanmaz", True, True, _RD_IS_MADDI),
    "iik_temyiz":                  ("uygulanmaz", True, True, _RD_ICRA),
    "iik_odeme_emrine_itiraz":     ("uygulanmaz", True, True, _RD_ICRA_ITIRAZ),
    "iik_gecikmis_itiraz":         ("uygulanmaz", True, True, _RD_ICRA),
    "iik_itirazin_iptali":         ("uygulanmaz", False, True, _RD_ICRA_DAVA),
    "iik_itirazin_kaldirilmasi":   ("uygulanmaz", True, True, _RD_ICRA),
    "iik_borctan_kurtulma":        ("uygulanmaz", False, True, _RD_ICRA_DAVA),
    "iik_89_ihbarname_itiraz":     ("uygulanmaz", True, True, _RD_ICRA),
    "iik_89_menfi_tespit":         ("uygulanmaz", False, True, _RD_ICRA_DAVA),
    "iik_ihalenin_feshi":          ("uygulanmaz", True, True, _RD_ICRA),
    "iik_ihalenin_feshi_azami":    ("uygulanmaz", True, True, _RD_ICRA),
    "iik_kambiyo_itiraz":          ("uygulanmaz", True, True, _RD_ICRA),
    "iik_ihtiyati_haciz_itiraz":   ("uygulanmaz", True, True, _RD_ICRA_IHTIYATI),
    "iik_icra_ceza_sikayet":       ("uygulanmaz", False, True, _RD_ICRA_CEZA),
    "iik_icra_ceza_sikayet_azami": ("uygulanmaz", False, True, _RD_ICRA_CEZA),
    "hmk_dosya_gonderme":          ("hmk104",     True, True, _RD_HMK104),
    "hmk_cevap_basit":             ("hmk104",     True, True, _RD_HMK104),
    "hmk_on_inceleme_belge_sunma": ("hmk104",     True, True, _RD_HMK104),
    "hmk_tedbir_itiraz":           ("uygulanmaz", True, True, _RD_TEDBIR),
    "hmk_tedbir_esas_dava":        ("uygulanmaz", False, True, _RD_TEDBIR_DAVA),
    "hmk_istifa_vekalet_devam":    ("uygulanmaz", False, True, _RD_ISTIFA_HMK),
    "avk_istifa_vekalet_devam":    ("uygulanmaz", False, True, _RD_ISTIFA_AVK),
    "aym_bireysel_mazeret":        ("uygulanmaz", False, True, _RD_AYM),
    "aihm_basvuru":                ("uygulanmaz", True, False, _RD_AIHM),
}
_GOMULU_REJIM = {k: {"adli_tatil": r, "adli_tatil_teyitli": t, "son_gun_kaymasi": s,
                     "adli_tatil_dayanak": d}
                 for k, (r, t, s, d) in _GOMULU_REJIM_SATIRLARI.items()}
# <<< v0.5.18 REJİM TABLOSU

# ── v0.5.16 / I5 (P1-3 / A-10) — AŞAMA TETİKLİ SÜRE SINIFI ───────────────
# Bazı usul "süreleri" takvimle değil yargılamanın bir AŞAMASIYLA kapanır: ilk
# itiraz cevap dilekçesiyle birlikte, delil bildirimi dilekçeler aşamasında,
# ıslah tahkikat bitene kadar, katılma hüküm verilinceye kadar. Bunlar için
# "tebliğ + N gün" aritmetiği YOKTUR; tarih üretmek YANLIŞ TARİH üretmektir
# (nöbetçi onu otorite sayar, defter kalıcılaştırır). Bu yüzden aşama kuralı
# `hesapla()`ya HİÇ GİRMEZ: script yalnız aşamayı, bağlı pipeline adımını ve
# dayanağı basar. Ceza kolundaki katılma anı deseni (v0.5.13, oa-musteki-vekili
# "olay tetikli kırmızı bayrak", CMK m.237) hukuk koluna genellendi.
# Tablo `sure_kurallari.json` → "asama_kurallari" bölümüyle BİREBİR aynıdır
# (ikiz kilit: tests/test_v0516_I5.py::test_asama_kurallari_json_ve_gomulu_BIREBIR);
# tarih kuralları tablosu (`_GOMULU_KURALLAR`) bu paketle DEĞİŞMEMİŞTİ;
# 2026-09-10'da iş hukuku kurallarıyla 21 → 27'ye çıktı (B7).
# Alanlar: asama (hangi aşama kapatır), pipeline_adimi (oa-pipeline ADIMLAR
# 0-10; bu adım TAMAMLANMADAN işlem yapılmalı), kaynak (MCP teyitli madde),
# aciklama (saha dersi), mcp_teyit_tarihi. miktar/birim YOK.
_GOMULU_ASAMA_KURALLAR = {
    "hmk_ilk_itiraz": {
        "asama": "cevap dilekçesi (dilekçeler aşaması)",
        "pipeline_adimi": 8,
        "kaynak": "HMK m.117/1 — ilk itirazların HEPSİ cevap dilekçesinde ileri sürülmek zorundadır; aksi hâlde DİNLENEMEZ. Katalog m.116/1: (a) kesin yetki kuralı bulunmayan hâllerde yetki itirazı, (b) tahkim itirazı; (c) bendi 7251 s.K. ile MÜLGA. m.117/2-3: dava şartlarından sonra, ön sorun gibi incelenir ve karara bağlanır.",
        "aciklama": "İlk itiraz takvimle değil CEVAP DİLEKÇESİNİN VERİLMESİYLE kapanır: adım 8 (YAZIM) kapanmadan cevap dilekçesine yazılmış olmalı. Cevap dilekçesinin KENDİ süresi tarih kuralıdır (hmk_cevap, HMK m.127).",
        "mcp_teyit_tarihi": "2026-09-07",
    },
    "hmk_delil_bildirimi": {
        "asama": "dilekçeler aşaması (dava/cevap dilekçesi)",
        "pipeline_adimi": 8,
        "kaynak": "HMK m.119/1-f (dava dilekçesi: iddia edilen her vakıanın hangi delillerle ispat edileceği) · m.129/1-e (cevap dilekçesi: savunmanın her vakıası için aynı) · m.145/1 — Kanunda belirtilen süreden sonra delil gösterilemez; İSTİSNA: sonradan ileri sürme yargılamayı geciktirme amacı taşımıyorsa VEYA süresinde sunulamaması tarafın kusurundan kaynaklanmıyorsa mahkeme İZİN VEREBİLİR (takdir).",
        "aciklama": "Delil bildirimi dilekçeler aşamasında kapanır; sonradan delil m.145 istisnasına ve mahkeme takdirine bağlıdır — ona GÜVENME. Delil listesi adım 4'te (OLGU/DELİL, oa-vakia) kurulur, adım 8 (YAZIM) kapanmadan dilekçeye eksiksiz girer.",
        "mcp_teyit_tarihi": "2026-09-07",
    },
    "hmk_on_inceleme_belge": {
        "asama": "ön inceleme (davetiye ihtarı → belge sunma kesin süresi)",
        "pipeline_adimi": 4,
        "kaynak": "HMK m.139/1-ç — ön inceleme davetiyesinin tebliğinden itibaren İKİ HAFTALIK KESİN SÜRE içinde dilekçede gösterilip henüz sunulmayan belgeler sunulur / getirtilecek belgeler için gereken açıklama yapılır; m.140/5 (7251 s.K.) — ihtara rağmen yerine getirilmezse o delile dayanmaktan VAZGEÇMİŞ SAYILMA kararı verilir.",
        "aciklama": "Aşama tetikli ÇATAL: davetiye tebliğ edilene kadar tarih YOKTUR; davetiye tebliğ edilince tarih kuralına dönüşür — o an `--kural hmk_on_inceleme_belge_sunma --teblig <davetiye tebliği>` ile hesapla (m.139/1-ç kesin süre; v0.5.18). Belgeler adım 4 (OLGU/DELİL) kapanmadan toplanmış ve MANİFEST'e bağlanmış olmalı.",
        "mcp_teyit_tarihi": "2026-09-07",
    },
    "hmk_islah": {
        "asama": "tahkikat (sona erene kadar)",
        "pipeline_adimi": 6,
        "kaynak": "HMK m.177/1 — ıslah, tahkikatın sona ermesine kadar yapılabilir; m.177/2 (7251 s.K.) — bozma/kaldırma sonrası ilk derece mahkemesi tahkikata ilişkin işlem yaparsa tahkikat sona erinceye kadar yine yapılabilir (bozmaya uymakla oluşan hukuki durum kaldırılamaz); m.177/3 — sözlü veya yazılı; karşı tarafa bildirilir.",
        "aciklama": "Islah takvimle değil TAHKİKATIN KAPANMASIYLA kapanır; ıslah gerekip gerekmediği adım 6 (STRATEJİ) kapanmadan karara bağlanır — TEK HAK: aynı davada taraflar ancak BİR KEZ ıslah yoluna başvurabilir (m.176/2), yanlış anda harcanan ıslah geri gelmez.",
        "mcp_teyit_tarihi": "2026-09-07",
    },
    "cmk_katilma": {
        "asama": "ilk derece kovuşturması (hüküm verilinceye kadar)",
        "pipeline_adimi": 1,
        "kaynak": "CMK m.237/1 — mağdur, suçtan zarar gören gerçek/tüzel kişiler ve malen sorumlular, ilk derece mahkemesindeki kovuşturma evresinin her aşamasında HÜKÜM VERİLİNCEYE KADAR katılabilir; m.237/2 — kanun yolu muhakemesinde katılma İSTENEMEZ; ilk derecede ileri sürülüp reddolunan/karara bağlanmayan istek kanun yolu başvurusunda AÇIKÇA belirtilmişse incelenir.",
        "aciklama": "Ceza kolu deseni (v0.5.13, oa-musteki-vekili 'olay tetikli kırmızı bayrak'): kovuşturma açıldı → katılma talebi öncelikli işlem; adım 1 (ALIM) kapanmadan talep edilip edilmediği tespit edilir. Talep yoksa müşteki istinaf/temyiz hakkını telafisiz kaybeder.",
        "mcp_teyit_tarihi": "2026-09-07",
    },
}

# Aşama kaydının defter/JSON şeması — `oa_hafiza.py sure-flag` kaydıyla aynı
# defterde (`_oa/sureler.json` → "flagler") yaşar; son_gun/tarih alanı YOKTUR.
ASAMA_TUR = "asama"

# B-21 (v0.5.14) — JSON okunamazsa artık SESSİZ düşülmez: sebep burada saklanır
# ve hesabın BAŞINDA görünür şekilde raporlanır ("gömülüye düşüldü, çünkü ...").
_KURAL_TABLO_SEBEP = ""
_ASAMA_TABLO_SEBEP = ""
# Kuralın izin verdiği başlangıç türleri (JSON'dan okunur; yoksa gömülüden).
KURAL_BASLANGIC = {}

# v0.5.18 (Y-01/Y-02) — kuralın ADLİ TATİL REJİMİ. Sıra: JSON alanları → (alan
# yoksa/bozuksa) gömülü ikiz → (kural gömülüde de yoksa) ön ekten TÜRETME. Her
# türetme hesapta GÖRÜNÜR yazılır; ön ekten türetilen rejim teyitsizdir ve en
# temkinli değeri (uzatma YOK = erken tarih) alır — sessiz varsayılan yasak.
KURAL_REJIM = {}
ADLI_TATIL_REJIMLERI = ("hmk104", "iyuk8", "cmk331", "uygulanmaz")
# Kural verilmeden (--sure/--birim) hesapta rejimi beyan edilen yargı kolu belirler.
YARGI_REJIMI = {"hukuk": "hmk104", "idari": "iyuk8", "ceza": "cmk331", "icra": "uygulanmaz"}
_YARGI_REJIM_DAYANAK = {"hukuk": _RD_HMK104, "idari": _RD_IYUK8, "ceza": _RD_CMK331,
                        "icra": _RD_ICRA}
# Ön ekin DOĞAL rejimi — yalnız türetme notunda ve TEMKİNLİ alternatif tarihte kullanılır.
_ONEK_REJIM = {"hmk": "hmk104", "iik": "uygulanmaz", "cmk": "cmk331", "iyuk": "iyuk8",
               "amme": "iyuk8", "is": "uygulanmaz", "aym": "uygulanmaz", "aihm": "uygulanmaz",
               # v0.5.18 K1 — Avukatlık Kanunu süresi HMK'nın tayin ettiği süre değildir
               "avk": "uygulanmaz"}
REJIM_ETIKET = {"hmk104": "HMK m.104 (31 Ağu + 1 hafta)",
                "iyuk8": "İYUK m.8/3 (1 Eylül'den itibaren 7 gün)",
                "cmk331": "CMK m.331/4 (tatilde işlemez; tatil bitiminden itibaren +3 gün)",
                "uygulanmaz": "UYGULANMAZ (adli tatil uzatması yok)"}


def _rejim_alanlari(v):
    """JSON kaydındaki rejim alanlarını mekanik denetler; eksik/geçersizse None."""
    if not isinstance(v, dict):
        return None
    r, t = v.get("adli_tatil"), v.get("adli_tatil_teyitli")
    s, d = v.get("son_gun_kaymasi"), v.get("adli_tatil_dayanak")
    if (r not in ADLI_TATIL_REJIMLERI or not isinstance(t, bool) or not isinstance(s, bool)
            or not str(d or "").strip()):
        return None
    return {"adli_tatil": r, "adli_tatil_teyitli": t, "son_gun_kaymasi": s,
            "adli_tatil_dayanak": str(d), "turetildi": ""}


def _rejim_turet(kural):
    """Rejim alanı olmayan kural için: önce gömülü ikiz, o da yoksa ön ek (teyitsiz)."""
    if kural in _GOMULU_REJIM:
        r = dict(_GOMULU_REJIM[kural])
        r["turetildi"] = "gömülü tablodan"
        return r
    onek = str(kural).split("_", 1)[0]
    dogal = _ONEK_REJIM.get(onek, "bilinmiyor")
    return {"adli_tatil": "uygulanmaz", "adli_tatil_teyitli": False,
            "son_gun_kaymasi": onek != "aihm",
            "adli_tatil_dayanak": ("TÜRETİLDİ — kural kaydında rejim alanı yok; ön ek '%s' "
                                   "doğal rejimi '%s', ancak teyit edilmeden uzatma UYGULANMADI "
                                   "(temkinli: erken tarih). Resmî kaynakla TEYİT ET ve JSON'a "
                                   "işle." % (onek, dogal)),
            "turetildi": "ön ekten"}


def kurallari_yukle():
    """sure_kurallari.json varsa oradan (kural, teyit, başlangıç, rejim) oku; yoksa/bozuksa
    gömülüye düş — ve DÜŞME SEBEBİNİ `_KURAL_TABLO_SEBEP`e yaz (B-21: sessiz
    fallback, kullanıcıya birbirini yalanlayan iki satır gösteriyordu)."""
    global _KURAL_TABLO_SEBEP, KURAL_BASLANGIC, KURAL_REJIM
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sure_kurallari.json")
    if not os.path.exists(yol):
        _KURAL_TABLO_SEBEP = "sure_kurallari.json BULUNAMADI"
    else:
        try:
            with open(yol, encoding="utf-8") as f:
                data = json.load(f)
            kurallar, teyit, baslangic, rejim = {}, {}, {}, {}
            for k, v in data.get("kurallar", {}).items():
                kurallar[k] = (v["miktar"], v["birim"], v.get("kaynak", ""))
                teyit[k] = v.get("mcp_teyit_tarihi", "") or ""
                bt = v.get("izinli_baslangic_turleri") or []
                baslangic[k] = [str(x) for x in bt] if isinstance(bt, list) else []
                rejim[k] = _rejim_alanlari(v) or _rejim_turet(k)
            if kurallar:
                KURAL_BASLANGIC = baslangic
                KURAL_REJIM = rejim
                return kurallar, teyit, False
            _KURAL_TABLO_SEBEP = "sure_kurallari.json 'kurallar' bölümü BOŞ"
        except Exception as e:
            _KURAL_TABLO_SEBEP = ("sure_kurallari.json OKUNAMADI/BOZUK "
                                  "(%s: %s)" % (type(e).__name__, e))
    KURAL_BASLANGIC = {k: list(v) for k, v in _GOMULU_BASLANGIC.items()}
    KURAL_REJIM = {k: dict(v, turetildi="") for k, v in _GOMULU_REJIM.items()}
    return dict(_GOMULU_KURALLAR), dict(_GOMULU_TEYIT), True

KURALLAR, KURAL_TEYIT, _KURAL_TABLO_YOK = kurallari_yukle()


def asama_kurallarini_yukle():
    """v0.5.16 / I5 — `sure_kurallari.json` → "asama_kurallari" bölümünü oku;
    yoksa/bozuksa gömülüye düş ve sebebi `_ASAMA_TABLO_SEBEP`e yaz (B-21
    disiplini: sessiz fallback yok). Şema denetimi mekaniktir: her kayıtta
    `asama` (str) ve `pipeline_adimi` (int 0-10) olmalı; olmayan kayıt
    ATLANMAZ — bölüm bütünüyle bozuk sayılır (fail-closed: yarım tablo,
    eksik tablodan tehlikelidir)."""
    global _ASAMA_TABLO_SEBEP
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sure_kurallari.json")
    if not os.path.exists(yol):
        _ASAMA_TABLO_SEBEP = "sure_kurallari.json BULUNAMADI"
    else:
        try:
            with open(yol, encoding="utf-8") as f:
                data = json.load(f)
            bolum = data.get("asama_kurallari")
            if not isinstance(bolum, dict) or not bolum:
                _ASAMA_TABLO_SEBEP = "sure_kurallari.json 'asama_kurallari' bölümü YOK/BOŞ"
            else:
                cikan = {}
                for k, v in bolum.items():
                    if (not isinstance(v, dict) or not str(v.get("asama") or "").strip()
                            or not isinstance(v.get("pipeline_adimi"), int)
                            or isinstance(v.get("pipeline_adimi"), bool)
                            or not 0 <= v["pipeline_adimi"] <= 10):
                        raise ValueError("'%s' kaydında asama/pipeline_adimi eksik veya geçersiz" % k)
                    cikan[k] = {"asama": str(v["asama"]),
                                "pipeline_adimi": int(v["pipeline_adimi"]),
                                "kaynak": str(v.get("kaynak") or ""),
                                "aciklama": str(v.get("aciklama") or ""),
                                "mcp_teyit_tarihi": str(v.get("mcp_teyit_tarihi") or "")}
                return cikan, False
        except Exception as e:
            _ASAMA_TABLO_SEBEP = ("sure_kurallari.json 'asama_kurallari' OKUNAMADI/BOZUK "
                                  "(%s: %s)" % (type(e).__name__, e))
    return {k: dict(v) for k, v in _GOMULU_ASAMA_KURALLAR.items()}, True

ASAMA_KURALLAR, _ASAMA_TABLO_YOK = asama_kurallarini_yukle()

# ── A-1 (P0, v0.5.14) — KURAL ↔ YARGI KOLU MUTABAKATI ─────────────────────
# Ceza sürelerinde adli tatil rejimi HMK m.104 (bir hafta) DEĞİL, CMK m.331/4
# (ÜÇ GÜN) uyarınca işler. Kural ile kol uyuşmazsa hesap SESSİZCE yanlış bir
# son gün üretiyordu (denetim A-1: dört gün GEÇ → süreden ret → kesinleşme).
# Sessiz yanlış varsayılan YASAK: uyuşmazlıkta hesap DURUR (aşağıda main/
# _pencere_kontrol), çünkü uyarı basılsa dahi ">>> HESAPLANAN SON GÜN" satırı
# ve otomatik `_oa/sureler.json` flag'i yanlış tarihi kalıcılaştırırdı.
# v0.5.18 (Y-01): "iik" artık "icra" koludur (eskiden "hukuk" → HMK m.104 ile yanlış
# uzatma). AYM/AİHM kol-bağımsızdır (None). Adli tatil rejimini artık KOL değil
# KURAL taşır (KURAL_REJIM); kol, kayma dayanağı/kurtarma kapısı/uyarılar ve
# "kural ile beyan edilen kol birbirini yalanlıyor mu" denetimi içindir.
# v0.5.18 K1: "avk" (Avukatlık Kanunu) kol-bağımsızdır — m.41 "takipten veya savunmadan"
# çekilen avukat için her yargı kolunda işler (oa-usul [G9] bu sözlüğü AST ile okur).
KURAL_KOLU = {"cmk": "ceza", "hmk": "hukuk", "iik": "icra", "is": "hukuk",
              "iyuk": "idari", "amme": "idari", "aym": None, "aihm": None, "avk": None}
# İcra ceza şikâyeti (İİK m.347) icra CEZA mahkemesine yapılır: ceza koluyla da çelişmez.
_KOL_EK_IZIN = {"iik_icra_ceza_sikayet": {"ceza"}, "iik_icra_ceza_sikayet_azami": {"ceza"}}


def kural_kolu(kural):
    """Kuralın ait olduğu yargı kolunu ön ekinden döndürür; bilinmiyorsa None."""
    if not kural:
        return None
    return KURAL_KOLU.get(str(kural).split("_", 1)[0])


def etkin_kol(kural, yargi):
    """Kuralın kendi kolu; kol-bağımsız kuralda (AYM/AİHM) ya da kuralsız hesapta --yargi."""
    return kural_kolu(kural) or yargi


def etkin_rejim(kural, yargi):
    """v0.5.18 — hesapta uygulanacak ADLİ TATİL REJİMİ: kural verildiyse KURALIN KENDİ
    rejimi (KURAL_REJIM), değilse beyan edilen yargı kolunun rejimi."""
    if kural and kural in KURAL_REJIM:
        r = dict(KURAL_REJIM[kural])
        r["kaynak"] = "kural"
        return r
    if kural:
        # Tabloda olmayan kural (doğrudan API çağrısı): kol rejimine SESSİZCE
        # düşülmez — gömülüden/ön ekten türetilir ve teyitsiz sayılır (fail-closed).
        r = _rejim_turet(str(kural))
        r["kaynak"] = "kural"
        return r
    return {"adli_tatil": YARGI_REJIMI[yargi], "adli_tatil_teyitli": True,
            "son_gun_kaymasi": True, "adli_tatil_dayanak": _YARGI_REJIM_DAYANAK[yargi],
            "turetildi": "", "kaynak": "yargi"}


def kol_uyusmazligi(kural, yargi):
    """(A-1) Kural ↔ yargı kolu uyuşmazlığında insan-okur gerekçe döndürür; yoksa None.

    Bloklanan hâller (kural ile beyan edilen kol birbirini yalanlıyor — ya kural ya
    kol yanlış seçildi; sessiz devam yanlış dayanaklı tarih üretir):
      · ceza kuralı ile ceza-dışı kol · ceza-dışı kural ile ceza kolu
    v0.5.18: adli tatil rejimini kural kendisi taşıdığından (KURAL_REJIM) yanlış
    uzatma artık kol seçiminden doğamaz; AYM/AİHM gibi kol-bağımsız kurallar ceza
    dosyasında da hesaplanır. İYUK ↔ HMK / icra ↔ hukuk arası bilgi notudur.
    """
    if yargi in _KOL_EK_IZIN.get(kural, ()):
        return None
    beklenen = kural_kolu(kural)
    if beklenen is None:
        if yargi == "ceza" and kural not in KURAL_REJIM:
            return ("'%s' kuralı ceza yargısına ait değil ve kendi adli tatil rejimini "
                    "taşımıyor; --yargi ceza ile koşulursa CMK m.331/4 (üç gün) uygulanır ve "
                    "süre YANLIŞ KISALIR." % kural)
        return None
    if beklenen == "ceza" and yargi != "ceza":
        return ("'%s' bir CEZA kanun yolu kuralıdır; --yargi %s beyanı kuralı yalanlıyor "
                "(denetim A-1: eski motor bu durumda HMK m.104/İYUK m.8-3 uygulayıp son günü "
                "CMK m.331/4'e göre dört gün GEÇ veriyordu). Doğru kullanım: --yargi ceza"
                % (kural, yargi))
    if beklenen != "ceza" and yargi == "ceza":
        return ("'%s' ceza yargısına ait bir kural DEĞİLDİR (kolu: %s); --yargi ceza beyanı "
                "kuralı yalanlıyor — ya kural ya kol yanlış seçildi. Doğru kullanım: --yargi %s"
                % (kural, beklenen, beklenen))
    return None


# B-16 / B-22 (v0.5.14) — miktar için akla uygun üst sınır: bunun ötesi
# hesaplanabilir bir usul/maddi süre değil, girdi hatasıdır (yıl biriminde
# date aritmetiği 9999'u aşınca ham OverflowError/ValueError veriyordu).
MIKTAR_UST_SINIR = {"gun": 36525, "isgunu": 26000, "hafta": 5217,
                    "ay": 1200, "yil": 100}


def miktar_dogrula(miktar, birim):
    """Geçersiz miktarda insan-okur gerekçe döndürür; geçerliyse None."""
    if not isinstance(miktar, int) or isinstance(miktar, bool):
        return "süre miktarı tam sayı olmalı (verilen: %r)" % (miktar,)
    if miktar < 0:
        return ("süre NEGATİF olamaz (verilen: %d). Negatif süre, tebliğden ÖNCEKİ "
                "bir tarihi 'son gün' diye üretir — bu bir hesap değil, girdi hatasıdır."
                % miktar)
    if miktar == 0:
        return ("süre SIFIR olamaz (verilen: 0). Sıfır uzunlukta bir usul süresi yoktur; "
                "başlangıç tarihini mi kastettiniz?")
    ust = MIKTAR_UST_SINIR.get(birim)
    if ust is not None and miktar > ust:
        return ("süre miktarı akla uygun üst sınırı aşıyor (%d %s > %d %s). "
                "Girdi hatası olmadığından emin olun." % (miktar, birim, ust, birim))
    return None
_GUNLER = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
def _gun_adi(g): return _GUNLER[g.weekday()]

def _ay_ekle(d, ay):
    """Tarihe ay ekler; hedef ayda gün yoksa ayın son gününe sabitler (TBK m.92 mantığı)."""
    y = d.year + (d.month - 1 + ay) // 12
    m = (d.month - 1 + ay) % 12 + 1
    # ayın son günü
    if m == 12:
        son_gun = 31
    else:
        son_gun = (date(y, m+1, 1) - timedelta(days=1)).day
    return date(y, m, min(d.day, son_gun))


def _is_gunu_ekle(d, n):
    """Tarihe n İŞ GÜNÜ ekler; başlangıç günü SAYILMAZ (4857 m.21/5 "on işgünü").

    İş günü = hafta sonu DEĞİL + resmî tatil DEĞİL (`is_gunu_mu`). Takvim
    gününden farkı şudur: aradaki cumartesi/pazar ve resmî tatiller süreye
    DAHİL EDİLMEZ, atlanır. 10 takvim günü ile 10 iş günü arasında iki haftalık
    fark doğabilir — bu fark, işe başlatma başvurusunda hakkın kendisidir
    (süresinde başvurmayan işçi bakımından fesih GEÇERLİ sayılır, 4857 m.21/6).

    Not: idari izin günleri iş günü sayılır (2429 anlamında resmî tatil
    değildir) — `is_gunu_mu` onları atlamaz; `hesapla()` ayrıca uyarır.
    """
    g = d
    kalan = n
    while kalan > 0:
        g += timedelta(days=1)
        if is_gunu_mu(g):
            kalan -= 1
    return g

def tatilleri_yukle():
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tatiller.json")
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sabit":[{"ay":1,"gun":1,"ad":"Yılbaşı"},{"ay":4,"gun":23,"ad":"23 Nisan"},
            {"ay":5,"gun":1,"ad":"1 Mayıs"},{"ay":5,"gun":19,"ad":"19 Mayıs"},
            {"ay":7,"gun":15,"ad":"15 Temmuz"},{"ay":8,"gun":30,"ad":"30 Ağustos"},
            {"ay":10,"gun":29,"ad":"29 Ekim"}],"dini":{},"_tablo_yok":True}

TATILLER = tatilleri_yukle()
SABIT = {(t["ay"],t["gun"]): t["ad"] for t in TATILLER.get("sabit",[])}
DINI = {y: set(g for g in gs if isinstance(g,str) and g[:4].isdigit())
        for y,gs in TATILLER.get("dini",{}).items() if y.isdigit()}
# İDARİ İZİN — CB tasarrufu (Cumhurbaşkanlığı Kararnamesi / CB Kararı / CB Genelgesi):
# hangi formda ilan edilirse edilsin 2429 anlamında resmî tatil DEĞİLDİR.
# Süreyi UZATMAZ, süreden sayılır → yalnızca UYARI üretir, son günü asla kaydırmaz.
IDARI = {y: set(g for g in gs if isinstance(g,str) and g[:4].isdigit())
         for y,gs in TATILLER.get("idari_izin",{}).items() if y.isdigit()}
def idari_izin_mi(g): return g.isoformat() in IDARI.get(str(g.year),set())
def idari_tanimli_mi(y): return str(y) in IDARI and len(IDARI[str(y)])>0
def dini_yakin_mi(g, esik=4):
    return any(abs((date.fromisoformat(d)-g).days) <= esik for d in DINI.get(str(g.year), set()))

# ── ARİTMETİK HİCRİ TAKVİM (tabular/civil — gelecek yıllar için TAHMİN) ─────
# Diyanet'in rüyet-esaslı resmî takviminden ±1-2 gün SAPABİLİR. Bu hesap yalnızca
# UYARI üretmek ve hangi tarihlerin teyit edileceğini göstermek içindir; tahmine
# dayanarak son gün ASLA kaydırılmaz/kaydırılmamazlık edilmez — teyit + tablo şarttır.
def _g2jdn(y, m, d):
    a = (14 - m) // 12; yy = y + 4800 - a; mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045
def _jdn2g(j):
    a = j + 32044; b = (4 * a + 3) // 146097; c = a - 146097 * b // 4
    dd = (4 * c + 3) // 1461; e = c - 1461 * dd // 4; mm = (5 * e + 2) // 153
    gun = e - (153 * mm + 2) // 5 + 1; ay = mm + 3 - 12 * (mm // 10)
    return date(100 * b + dd - 4800 + mm // 10, ay, gun)
def _hicri2jdn(hy, hm, hd):
    onceki = ((hm - 1) // 2) * 59 + ((hm - 1) % 2) * 30
    return hd + onceki + (hy - 1) * 354 + (3 + 11 * hy) // 30 + 1948439
def tahmini_bayramlar(gy):
    """Verilen miladi yıl için TAHMİNİ bayram günleri: {ad: [date, ...]}."""
    sonuc = {}
    hy0 = int((gy - 622) * 33 / 32)
    for hy in range(hy0 - 1, hy0 + 3):
        for ad, hm, hd0, n in (("Ramazan Bayramı", 10, 1, 3), ("Kurban Bayramı", 12, 10, 4)):
            gunler = [_jdn2g(_hicri2jdn(hy, hm, hd0) + i) for i in range(n)]
            gunler = [g for g in gunler if g.year == gy]
            if gunler:
                sonuc.setdefault(f"{ad} ~{hy}H (TAHMİNİ ±1-2 gün)", []).extend(gunler)
    return sonuc

def resmi_tatil_mi(g):
    if (g.month,g.day) in SABIT: return SABIT[(g.month,g.day)]
    if g.isoformat() in DINI.get(str(g.year),set()): return "Dini bayram (tabloda tanımlı)"
    return None
def hafta_sonu_mu(g): return g.weekday()>=5
def is_gunu_mu(g): return not hafta_sonu_mu(g) and resmi_tatil_mi(g) is None
def sonraki_is_gunu(g):
    while not is_gunu_mu(g): g += timedelta(days=1)
    return g
def aralik_icinde_mi(g):
    return date(g.year,*ARA_BASLANGIC) <= g <= date(g.year,*ARA_BITIS)
def dini_tanimli_mi(y): return str(y) in DINI and len(DINI[str(y)])>0


def dini_tam_mi(y):
    """v0.5.18 / Y-08 — yılın dini bayram kaydı TAM mı? Tek bir girişle yılı "tanımlı"
    saymak, yarım girilmiş yılda (ör. yalnız Ramazan) takvim kapısını sessizce kapatır.
    Ölçüt mekaniktir: kayıtlı gün sayısı, aritmetik hicri tahminin o yıla düşürdüğü
    bayram günü sayısının en az (tahmin − 2)'si olmalı (tahmin ±1-2 gün sapabilir;
    yıl sınırına taşan bayramlar da böylece doğru sayılır)."""
    if not dini_tanimli_mi(y):
        return False
    try:
        beklenen = sum(len(g) for g in tahmini_bayramlar(int(y)).values())
    except Exception:
        return True   # tahmin üretilemezse kayıt varlığı yeter (kapıyı kilitleme)
    return len(DINI[str(y)]) >= max(1, beklenen - 2)

# v0.5.13 — BAŞLANGIÇ TÜRÜ (pratikçi hakem heyeti tez 1; MCP teyitli gerekçe):
# aynı dosyada iki farklı başlangıç rejimi yaşayabilir — CMK m.268 itiraz
# *öğrenme gününden*, m.273/291 istinaf-temyiz *gerekçeli kararın tebliğinden*
# işler. Bu alan ARİTMETİĞİ DEĞİŞTİRMEZ; hangi olayın süreyi başlattığını
# çıktıda GÖRÜNÜR kılar (yanlış olaya bağlanan doğru hesap, yanlış hesaptır).
# Opsiyoneldir: verilmezse davranış birebir eskisi gibidir.
BASLANGIC_TURLERI = {
    "teblig": "tebliğ (evrakın usulüne uygun tebliği)",
    "tefhim": "tefhim (duruşmada yüze karşı açıklama)",
    "ogrenme": "öğrenme (fiilen öğrenildiği gün)",
    # NOT (2026-09-10): "olay" YALNIZ maddi hukuka ait değildir. Tebliğe değil
    # bir OLAYA bağlanan USUL süreleri de vardır — en belirgini 4857 m.20/1:
    # işe iade davasının iki haftalık süresi arabuluculuk son tutanağının
    # DÜZENLENDİĞİ (tebliğ edildiği değil) tarihten işler.
    "olay": ("olay/fiil tarihi — maddi hukuk süreleri VE tebliğe değil bir olaya "
             "bağlanan usul süreleri (ör. arabuluculuk son tutanağının düzenlenmesi, "
             "4857 m.20/1; işçinin işverene başvurusu, m.21/1)"),
    "belirsiz": "BELİRSİZ — iki senaryo hesaplanmalı",
}


def _kurtarma_kapisi_notu(yargi, kural=None):
    """A-10 (v0.5.14) — kaçırılan süre için gösterilecek kurtarma kapısı YARGI
    KOLUNA GÖRE değişir. Eski kod idari dosyada da HMK m.95'i öneriyordu; oysa
    2577'de 'eski hale getirme'/'mazeret' geçmiyor (MCP içinde-ara 2026-08-31 →
    0 eşleşme) ve ailenin kendi kuralı 'bu satır idari dosyaya ASLA basılmaz'
    diyordu. Var olmayan bir kapı, gerçek kapıların aranmasını engeller.
    v0.5.18: icra kolunun kapısı İİK'nın kendisindedir (m.65); AYM'de 6216 m.47/5
    mazeret penceresi; AİHM'de iç hukuk kurumlarına güvenilmez."""
    _onek = str(kural or "").split("_", 1)[0]
    if str(kural or "").startswith("iik_icra_ceza"):
        return ("İcra ceza şikâyet süresi geçmekle şikâyet hakkı DÜŞER (İİK m.347): eski hâle getirme/"
                "mazeret kapısına GÜVENME — şikâyeti son güne bırakma.")
    if str(kural or "").endswith("_istifa_vekalet_devam"):
        # v0.5.18 K1 — bu bir başvuru süresi değil, görevin DEVAM süresidir: kaçırılan
        # süre için kurtarma kapısı yoktur; HMK m.95 önermek yanlış yere baktırır.
        return ("Bu süre bir görev DEVAM süresidir (HMK m.82/1 / Av.K. m.41) — eski hâle getirme/"
                "mazeret kapısı YOKTUR: müvekkil ve yeni vekil işlemlerini bu güne bırakmaz; istifa "
                "eden avukat idari izin gününde de takibi sürdürür.")
    if _onek == "aym":
        return ("İşlem o gün fiilen imkânsızlaştıysa: 6216 m.47/5 — haklı mazeret hâlinde mazeretin "
                "kalktığı tarihten itibaren ON BEŞ GÜN içinde mazereti belgeleyen delillerle başvuru "
                "(kural aym_bireysel_mazeret); kabul AYM'nin takdirindedir — buna güvenerek bekleme.")
    if _onek == "aihm":
        return ("AİHM süresi Sözleşme ölçütleriyle hesaplanır (Sabri Güneş/Türkiye [BD]): iç "
                "hukuktaki eski hâle getirme/mazeret kurumlarına GÜVENME — başvuruyu son güne bırakma.")
    if yargi == "idari":
        return ("İşlem o gün fiilen imkânsızlaştıysa: İYUK'ta ESKİ HÂLE GETİRME KURUMU YOKTUR "
                "(2577'de 'eski hale getirme'/'mazeret' hükmü bulunmaz) — HMK m.95'e GÜVENME. "
                "Bakılacak gerçek yerler: AY m.40/2 (başvuru yolu, mercii ve süresinin işlemde "
                "bildirilmemesi), İYUK m.10 (idari makama başvuru) ve vergide düzeltme-şikâyet "
                "(YALNIZ vergi hatası varsa — VUK m.116-126). Hangisinin açık olduğunu teyit et.")
    if yargi == "ceza":
        return ("İşlem o gün fiilen imkânsızlaştıysa CMK m.40 (eski hâle getirme) değerlendirilir: "
                "'Kusuru olmaksızın bir süreyi geçirmiş olan kişi, eski hale getirme isteminde "
                "bulunabilir'; kanun yoluna başvuru hakkı bildirilmemişse kişi KUSURSUZ sayılır "
                "(m.40/2). Ayrıca tutukluda CMK m.263 kanalı ayrıca kontrol edilir — buna güvenerek "
                "bekleme, süresinde işlem yap.")
    if yargi == "icra":
        return ("İşlem o gün fiilen imkânsızlaştıysa: ödeme emrine itirazda İİK m.65 (gecikmiş "
                "itiraz — mânî kalktıktan itibaren ÜÇ GÜN içinde mazeret delilleriyle; dış sınır "
                "paraya çevirme işlemi bitinceye kadar; kural iik_gecikmis_itiraz); diğer icra "
                "sürelerinde eski hâle getirme imkânı ayrıca ve ihtiyatla değerlendirilir — buna "
                "güvenerek bekleme.")
    return ("İşlem o gün fiilen imkânsızlaştıysa eski hâle getirme (HMK m.95 vd.; süre m.96 — "
            "engelin kalkmasından iki hafta) ayrıca ve ihtiyatla değerlendirilir — buna güvenerek bekleme.")


# ── v0.5.18 — BAŞLANGIÇ KAPISI (Yargı PRO 12-2/12-3 FİKRİNİN OA uyarlaması) ──────
# Motor tarihi doğru sayar; ama süreyi başlatan OLAY ya da onun KANITI yanlışsa
# doğru hesap yanlış sonuç verir. Kapı NİTELENDİRME YAPMAZ: kanıt türünün işaret
# ettiği başlangıç türünü kuralın izinli türleriyle karşılaştırır, kanıtsız ya da
# şüpheli başlangıcı GÖRÜNÜR kılar ve karşı tarafa kesin dili keser. Aritmetiği
# değiştirmez. Ayrıntı ve normlar: references/baslangic-kapisi.md (Mevzuat MCP
# teyitli 2026-10-05: 7201 s. TK m.7/a, 11, 21, 31, 32, 35, 36).
BASLANGIC_KANITLARI = {
    "mazbata": ("teblig", "tebliğ mazbatası / şerhi (7201 s. TK m.21 ve m.35 hâlleri dahil)"),
    "uets-kaydi": ("teblig", "UETS / e-tebligat kaydı (7201 s. TK m.7/a: ulaştığı tarihi izleyen "
                             "beşinci günün sonunda tebliğ sayılır)"),
    "kalem-tevdi": ("teblig", "kalemde/duruşmada imza karşılığı tevdi (7201 s. TK m.36 — tebliğ "
                              "hükmünde)"),
    "ilan": ("teblig", "ilanen tebligat (7201 s. TK m.31 — son ilandan yedi gün sonra tebliğ sayılır)"),
    "tefhim-tutanagi": ("tefhim", "tefhim tutanağı / duruşma zaptı"),
    "uyap-erisim-kaydi": ("ogrenme", "UYAP erişim / öğrenme kaydı"),
    "kesinlesme-serhi": ("olay", "kesinleşme şerhi"),
    "beyan": (None, "yalnız BEYAN — belge yok"),
    "yok": (None, "kanıt YOK"),
}
TEBLIG_DURUMLARI = {
    "gecerli": "geçerli (usulüne uygun)",
    "usulsuz": "USULSÜZ (7201 s. TK m.32 — muttali olunan tarih tebliğ tarihi sayılır)",
    "supheli": "ŞÜPHELİ (tarih okunamıyor / mazbata eksik / kayıtlar çelişkili)",
}


def _baslangic_kapisi(kural, tur_anahtari, kanit, durum, rapor, uyarilar):
    """Kanıt + tebliğ durumunu kural/başlangıç türüyle karşılaştırır (uyarı üretir).
    Dönüş: {"kanitsiz": bool, "supheli": bool} — karşı taraf kesin dil kapısı için."""
    sonuc = {"kanitsiz": False, "supheli": False}
    izinli = ([str(x).strip().lower() for x in (KURAL_BASLANGIC.get(kural) or [])]
              if kural else [])
    if kanit is not None:
        k = str(kanit).strip().lower()
        if k not in BASLANGIC_KANITLARI:
            sonuc["kanitsiz"] = True
            uyarilar.append("TANINMAYAN BAŞLANGIÇ KANITI: %r — kanıtsız sayıldı; geçerli değerler: %s"
                            % (kanit, ", ".join(sorted(BASLANGIC_KANITLARI))))
        else:
            isaret, ad = BASLANGIC_KANITLARI[k]
            rapor.append("Başlangıç kanıtı      : %s — %s" % (k, ad))
            if isaret is None:
                sonuc["kanitsiz"] = True
                uyarilar.append(
                    "KANITSIZ BAŞLANGIÇ: süreyi başlatan olay BELGEYE bağlanmadı (%s). Hesap yalnız "
                    "İHTİYAT amaçlıdır: bizim süremizde plan, belgeyle bağlanabilecek EN ERKEN olaya "
                    "göre yapılır; karşı tarafa 'süre kaçırılmıştır' kesin dili tebliğ mazbatası / "
                    "UETS / UYAP kaydı bulunup teyit edilmeden KURULAMAZ (UYAP tebligat sorgusu, PTT "
                    "barkod kaydı)." % k)
            else:
                if tur_anahtari and tur_anahtari not in ("belirsiz", isaret):
                    uyarilar.append(
                        "KANIT ↔ BAŞLANGIÇ TÜRÜ ÇELİŞKİSİ: kanıt '%s' süreyi '%s' olayına bağlıyor; "
                        "beyan edilen başlangıç türü '%s'. Hangisi doğruysa belgeyle sabitle — iki "
                        "farklı olay iki farklı son gün demektir." % (k, isaret, tur_anahtari))
                if izinli and isaret not in izinli:
                    uyarilar.append(
                        "KANIT ↔ KURAL ÇELİŞKİSİ: kanıt '%s' süreyi '%s' olayına bağlıyor; '%s' kuralı "
                        "kayıtlı olarak yalnız (%s) ile işler. Ör. HMK m.345/361 ve İİK m.363/364 "
                        "süreleri tefhimden değil TEBLİĞDEN işler — o hâlde süreyi başlatan tebliğ "
                        "belgesini bul." % (k, isaret, kural, ", ".join(izinli)))
                if k == "uets-kaydi":
                    uyarilar.append(
                        "UETS KANITI (7201 s. TK m.7/a): tebliğ, elektronik adrese ULAŞTIĞI tarihi "
                        "izleyen beşinci günün sonunda yapılmış sayılır — ulaşma günü ile tebliğ-sayılma "
                        "gününü karıştırma; iki senaryo hesaplanır (CLI'da --baslangic-kaniti uets-kaydi "
                        "--uets'i kendiliğinden açar). BİZİM süremizde plan ERKEN senaryodur.")
                if k == "ilan":
                    uyarilar.append(
                        "İLANEN TEBLİGAT (7201 s. TK m.31): --teblig olarak SON İLAN tarihinden yedi "
                        "gün sonrası (merci daha uzun süre tayin ettiyse o) girilmiş olmalı — son ilan "
                        "tarihinin kendisi tebliğ tarihi DEĞİLDİR.")
    if durum is not None:
        d = str(durum).strip().lower()
        if d not in TEBLIG_DURUMLARI:
            uyarilar.append("TANINMAYAN TEBLİĞ DURUMU: %r — geçerli değerler: %s"
                            % (durum, ", ".join(TEBLIG_DURUMLARI)))
        else:
            rapor.append("Tebliğ durumu         : %s" % TEBLIG_DURUMLARI[d])
            if d == "usulsuz" and tur_anahtari == "ogrenme":
                uyarilar.append(
                    "USULSÜZ TEBLİĞ (7201 s. TK m.32): muhatap tebliğe muttali olmuşsa tebliğ muteberdir "
                    "ve muhatabın beyan ettiği ÖĞRENME tarihi tebliğ tarihi sayılır — hesap öğrenme "
                    "tarihine göre yapıldı; öğrenmeyi belgeye bağla (dilekçe tarihi, UYAP erişim kaydı).")
            elif d == "usulsuz":
                uyarilar.append(
                    "USULSÜZ TEBLİĞ (7201 s. TK m.32): usulsüzlük süreyi kendiliğinden sınırsız bırakmaz — "
                    "muhatabın tebliğe muttali olduğu (ÖĞRENDİĞİ) tarih tebliğ tarihi sayılır. --teblig "
                    "öğrenme tarihi olmalı ve --baslangic-turu ogrenme verilmeli; usulsüzlüğü ileri "
                    "sürüyorsan öğrenme tarihini dilekçede AÇIKÇA beyan et.")
            elif d == "supheli":
                sonuc["supheli"] = True
                uyarilar.append(
                    "ŞÜPHELİ TEBLİĞ: tebliğ tarihi kesin değil — motor TEK KESİN TARİH ÜRETMEZ; aşağıdaki "
                    "tarih yalnız İHTİYAT HEDEFİdir ve deftere öyle yazılır. Okunamayan tarihi TAHMİN "
                    "ETME: olası EN ERKEN tebliğ tarihini gir, gerçek tarihi UYAP tebligat sorgusu / PTT "
                    "barkod kaydıyla teyit edip yeniden hesapla. Karşı tarafa kesin dil kurulmaz.")
    return sonuc


# Teyitsiz rejimli kuralda KARŞILAŞTIRMA için kullanılan "diğer okuma". Varsayılan
# HMK m.104 (31 Ağu + 1 hafta — en geniş okuma); icra ceza şikâyetinde (İİK m.347,
# icra ceza mahkemesi) doğal alternatif CMK m.331/4'tür: öğrenme tatil İÇİNDEYSE süre
# tatilde hiç işlemeyebilir (tam süre 31 Ağu'dan sonra) — v0.5.18 karşı-tez incelemesi.
_TEMKINLI_ALTERNATIF = {"iik_icra_ceza_sikayet": "cmk331", "iik_icra_ceza_sikayet_azami": "cmk331"}


def _sure_ekle(bas, miktar, birim):
    """Takvim birimli süreyi `bas` tarihine ekler (gün/hafta/ay/yıl — iş günü hariç)."""
    if birim == "hafta":
        return bas + timedelta(weeks=miktar)
    if birim == "gun":
        return bas + timedelta(days=miktar)
    if birim == "ay":
        return _ay_ekle(bas, miktar)
    return _ay_ekle(bas, miktar * 12)


def _alternatif_bitis(rejim, teblig, ham, miktar, birim):
    """Teyitsiz/sınır hâlde KARŞILAŞTIRMA için diğer okumanın son günü (kaymasız); yoksa None."""
    bitis = date(ham.year, *ARA_BITIS)
    if rejim in ("hmk104", "iyuk8"):
        return bitis + timedelta(days=7) if aralik_icinde_mi(ham) else None
    if rejim == "cmk331":
        if aralik_icinde_mi(teblig) or aralik_icinde_mi(teblig + timedelta(days=1)):
            return _sure_ekle(date(teblig.year, *ARA_BITIS), miktar, birim)
        return bitis + timedelta(days=3) if aralik_icinde_mi(ham) else None
    return None


def hesapla(teblig, miktar, birim, yargi, tur="usul", adli_tatil_istisna=False,
            baslangic_turu=None, kural=None, baslangic_kaniti=None, teblig_durumu=None,
            _bilgi=None):
    """Deterministik son gün hesabı → (son, rapor, uyarilar).

    v0.5.18: adli tatil rejimini KURAL taşır (etkin_rejim — Y-01); CMK'da tatil
    İÇİNDE tebliğde süre tatilde işlemez (Y-02); dini bayram tablosu eksik yıl
    GÖRÜNÜR yazılır (Y-08); başlangıç kapısı (kanıt/tebliğ durumu) yalnız uyarı
    üretir. `_bilgi` (dict) verilirse makine-okur ayrıntı ona yazılır (rejim,
    rejim_teyitli, alt_son, ihtiyat_son, takvim_eksik, kanitsiz, supheli, kol)."""
    rapor, uyarilar = [], []
    # B-16 (v0.5.14) — negatif/sıfır/aşırı miktar SESSİZCE kabul edilemez:
    # eskiden `--sure -5` tebliğden ÖNCEKİ bir tarihi ">>> HESAPLANAN SON GÜN"
    # diye basıp exit 0 dönüyordu (ve --kok verilirse deftere de yazıyordu).
    _mh = miktar_dogrula(miktar, birim)
    if _mh:
        raise ValueError(_mh)
    if yargi not in YARGI_REJIMI:
        raise ValueError("tanınmayan yargı kolu %r — geçerli: %s (sessizce bir adli tatil "
                         "rejimine bağlanmaz)" % (yargi, ", ".join(sorted(YARGI_REJIMI))))
    rj = etkin_rejim(kural, yargi)
    rejim = rj["adli_tatil"]
    _kol = etkin_kol(kural, yargi)
    _onek = str(kural or "").split("_", 1)[0]
    bas = teblig + timedelta(days=1)
    anahtar = None
    if baslangic_turu is not None:
        anahtar = str(baslangic_turu).strip().lower()
        if anahtar in BASLANGIC_TURLERI:
            rapor.append("Başlangıç türü        : %s" % BASLANGIC_TURLERI[anahtar])
            if anahtar == "belirsiz":
                uyarilar.append(
                    "BAŞLANGIÇ BELİRSİZ: süre hangi olaydan işlediği kesin değil "
                    "— İKİ senaryo ayrı ayrı hesaplanmalı ve plan ERKEN tarihe "
                    "göre yapılmalıdır (geç senaryoya güvenmek hak kaybettirir).")
            # B-20 (v0.5.14) — seçilen başlangıç türü kuralın hukuken izin
            # verdiği türlerden değilse çelişki SESSİZ kalamaz. Script
            # NİTELENDİRME yapmaz: yalnız alanın kapalı kümede olup olmadığına
            # bakar; hukuki hüküm avukata aittir (kural metni ekrandadır).
            _izinli = [str(x).strip().lower()
                       for x in (KURAL_BASLANGIC.get(kural) or [])] if kural else []
            # v0.5.18 — usulsüz tebliğde muttali olunan (öğrenme) tarih tebliğ tarihi
            # sayılır (7201 s. TK m.32): tebliğe bağlı kuralda bu bir çelişki değildir.
            _tk32 = (str(teblig_durumu or "").strip().lower() == "usulsuz"
                     and anahtar == "ogrenme" and "teblig" in _izinli)
            if _izinli and anahtar not in _izinli and anahtar != "belirsiz" and not _tk32:
                uyarilar.append(
                    "BAŞLANGIÇ TÜRÜ ÇELİŞKİSİ: '%s' kuralının kayıtlı başlangıç türleri "
                    "(%s) arasında '%s' YOK. Kural satırındaki dayanağı oku ve hangi "
                    "olayın süreyi başlattığını Mevzuat MCP'den teyit et — yanlış olaya "
                    "bağlanan doğru hesap, yanlış hesaptır." % (
                        kural, ", ".join(_izinli), anahtar))
        else:
            uyarilar.append(
                "TANINMAYAN BAŞLANGIÇ TÜRÜ: %r — sessizce 'tebliğ' sayılmadı; "
                "geçerli değerler: %s" % (baslangic_turu,
                                          ", ".join(sorted(BASLANGIC_TURLERI))))
    _kapi = _baslangic_kapisi(kural, anahtar if anahtar in BASLANGIC_TURLERI else None,
                              baslangic_kaniti, teblig_durumu, rapor, uyarilar)
    rapor.append(f"Tebliğ/öğrenme tarihi : {teblig.isoformat()} ({_gun_adi(teblig)})")
    rapor.append(f"Süre başlangıcı       : {bas.isoformat()} (tebliğ günü sayılmaz)")
    if birim=="hafta":
        ham = teblig + timedelta(weeks=miktar); rapor.append(f"Süre                  : {miktar} hafta")
    elif birim=="gun":
        ham = teblig + timedelta(days=miktar); rapor.append(f"Süre                  : {miktar} gün")
    elif birim=="isgunu":
        ham = _is_gunu_ekle(teblig, miktar)
        _takvim = teblig + timedelta(days=miktar)
        rapor.append(f"Süre                  : {miktar} İŞ GÜNÜ (hafta sonu ve resmî tatiller "
                     f"SAYILMAZ; aynı sayıda takvim günü {_takvim.isoformat()} ederdi)")
    elif birim=="ay":
        ham = _ay_ekle(teblig, miktar); rapor.append(f"Süre                  : {miktar} ay (TBK m.92 tarzı: sayılı güne denk gelen gün)")
    elif birim=="yil":
        ham = _ay_ekle(teblig, miktar*12); rapor.append(f"Süre                  : {miktar} yıl")
    else:
        raise ValueError("birim 'gun', 'hafta', 'ay' veya 'yil' olmalı")
    rapor.append(f"Ham bitiş             : {ham.isoformat()} ({_gun_adi(ham)})")
    son = ham
    alt_son = None       # teyitsiz rejimde DİĞER rejime göre son gün (karşılaştırma için)
    ihtiyat_son = None   # CMK tatil içi tebliğde eski daire uygulamasına göre son gün
    if rj.get("turetildi"):
        uyarilar.append(
            "REJİM TÜRETİLDİ: '%s' kaydında adli tatil alanları (adli_tatil, adli_tatil_teyitli, "
            "son_gun_kaymasi, adli_tatil_dayanak) YOK veya geçersiz — rejim %s TÜRETİLDİ (%s). "
            "sure_kurallari.json'u onar; türetilmiş rejimle karşı tarafa kesin dil kurma."
            % (kural, rj["turetildi"], REJIM_ETIKET[rejim]))
    # v0.5.18 / Y-02 — CMK m.331/4 "Adlî tatile rastlayan süreler İŞLEMEZ": tebliğ
    # TATİL İÇİNDEYSE süre tatilde hiç işlemez; tam süre tatilin bittiği günden
    # sonra işler (YCGK E.2013/2-272 K.2013/524; YCGK E.2021/319 K.2022/846 —
    # tutuklu işlerde de; AYM Ramazan Seçen: aksi uygulama erişim hakkı ihlali).
    # Eski kod süreyi tatilde işletiyordu (25.08 → 08.09; doğrusu 14.09).
    tatilde_teblig = (tur == "usul" and birim != "isgunu" and rejim == "cmk331"
                      and not adli_tatil_istisna and aralik_icinde_mi(teblig))
    # Adli tatil/çalışmaya ara YALNIZCA USUL sürelerine uygulanır.
    # Maddi hukuk süreleri (zamanaşımı, hak düşürücü) usul süresi DEĞİLDİR → uzamaz.
    # İŞ GÜNÜ biriminde adli tatil UZATMASI uygulanmaz: (a) sayım zaten tatilleri
    # atlayarak yapılır, (b) bu birimin tek kullanım yeri olan 4857 m.21/5 süresi
    # MAHKEMEYE değil İŞVERENE yapılan bir başvurunun süresidir ve HMK m.104'ün
    # "bu Kanunun tayin ettiği süreler" kapsamında değildir. Uzatma uygulamak
    # GEÇ tarih üretirdi; geç tarih hak kaybettirir (güvenli taraf erken tarihtir).
    if tur=="usul" and birim=="isgunu" and aralik_icinde_mi(son):
        uyarilar.append(
            "İŞ GÜNÜ + ADLİ TATİL: Son gün adli tatil aralığına (20 Tem–31 Ağu) düşüyor ancak "
            "UZATMA UYGULANMADI. Gerekçe: iş günü sayımı tatilleri zaten atlar ve 4857 m.21/5 "
            "süresi mahkemeye değil İŞVERENE başvuru süresidir (HMK m.104 'bu Kanunun tayin "
            "ettiği süreler' kapsamı dışında). Aksi bir dayanak teyit edilirse tarih yeniden "
            "hesaplanmalıdır — bu hesap GÜVENLİ (erken) taraftadır.")
    if tatilde_teblig:
        _bitis = date(teblig.year, *ARA_BITIS)
        if birim == "hafta":
            son = _bitis + timedelta(weeks=miktar)
        elif birim == "gun":
            son = _bitis + timedelta(days=miktar)
        elif birim == "ay":
            son = _ay_ekle(_bitis, miktar)
        else:
            son = _ay_ekle(_bitis, miktar * 12)
        rapor.append(f"Adli tatil (CMK m.331/4) — TATİL İÇİNDE TEBLİĞ: süre tatilde İŞLEMEZ; TAM süre "
                     f"tatilin bittiği günden (31 Ağu) sonra işler → {son.isoformat()} "
                     f"(YCGK E.2013/2-272 K.2013/524; YCGK E.2021/319 K.2022/846)")
        # İHTİYAT = eski daire okuması: süre tatilde de işler; bitiş tatile rastlarsa
        # 31 Ağu + üç gün, rastlamazsa ham bitiş (Y. 11. CD E.2017/14079 K.2018/2400:
        # 07.08.2014 tebliğ, bir haftalık süre tatilde bitti → 01.09'dan üç gün).
        _ih = (_bitis + timedelta(days=3)) if aralik_icinde_mi(ham) else ham
        if _ih < son:
            ihtiyat_son = _ih
    elif tur=="usul" and birim!="isgunu" and aralik_icinde_mi(son) and not adli_tatil_istisna:
        if rejim == "cmk331":
            # A-1 (P0, v0.5.14 — MCP teyitli 2026-08-31, CMK m.331/4):
            # "Adlî tatile rastlayan süreler işlemez. Bu süreler tatilin bittiği
            # günden itibaren ÜÇ GÜN uzatılmış sayılır." Bu, hukuk yargısının
            # bir haftalık uzatmasından (HMK m.104) DÖRT GÜN kısadır; eski kod
            # ceza dosyasına hukuk rejimini uyguluyor ve dört gün GEÇ tarih
            # veriyordu (süreden ret → hüküm kesinleşir).
            son = date(son.year,*ARA_BITIS) + timedelta(days=3)
            rapor.append(f"Adli tatil (CMK m.331/4): ham bitiş 20 Tem–31 Ağu arasında; süre İŞLEMEZ ve "
                         f"tatilin bittiği günden (31 Ağu) itibaren ÜÇ GÜN uzatılmış sayılır → {son.isoformat()}")
            uyarilar.append(
                "CEZA ADLİ TATİLİ (CMK m.331): (1) f.4 uyarınca uzatma ÜÇ GÜNDÜR — hukuk yargısının "
                "HMK m.104 bir haftalık uzatmasıyla KARIŞTIRMA. (2) f.2: soruşturma ile TUTUKLU işlere "
                "ilişkin kovuşturmaların ve ivedi sayılacak diğer hususların tatil süresi içinde ne "
                "suretle yerine getirileceğini HSK belirler. (3) f.3: tatil süresince BAM ve Yargıtay "
                "yalnız TUTUKLU hükümlere ilişkin veya Meşhud Suçların Muhakeme Usulü Kanunu gereğince "
                "görülen işlerin incelemelerini yapar. f.2-3 hangi İŞLERİN görüleceğine dairdir; süre "
                "uzaması her hâlde f.4'e tabidir — tutuklu dosyada işin fiilen yürüyecek olması sürenin "
                "uzamadığı anlamına GELMEZ. Tutuklu sanıkta ayrıca CMK m.263 (ceza infaz kurumu "
                "müdürüne başvuru süreyi KESER) değerlendirilir.")
        elif rejim == "hmk104":
            son = date(son.year,*ARA_BITIS) + timedelta(weeks=1)
            rapor.append(f"Adli tatil (HMK m.104): ham bitiş 20 Tem–31 Ağu arasında; 31 Ağu + 1 hafta → {son.isoformat()}")
        elif rejim == "iyuk8":
            son = date(son.year,*ARA_BITIS) + timedelta(days=7)
            rapor.append(f"Çalışmaya ara (İYUK m.8/3): ham bitiş 20 Tem–31 Ağu arasında; ara bitimini izleyen "
                         f"1 Eylül'den itibaren 7 gün (1 Eylül dahil) → {son.isoformat()}")
            if not rj["adli_tatil_teyitli"]:
                alt_son = ham   # uzamasız (ham) bitiş — karşı taraf denetiminde karşılaştırılır
            # A-20 (v0.5.14) — İYUK m.8/3 uzatmasının ÖZEL KANUN sürelerine
            # (ör. 6183 m.58) uygulanması TARTIŞMALIDIR. Danıştay 7.D.
            # E.2000/5685 K.2002/3522 (13.11.2002, MCP tam metin) çoğunluğu
            # uzamadan yana — script bu tarafta — ANCAK karar OYÇOKLUĞU ile
            # verilmiştir; tetkik hâkimi, Danıştay savcısı ve ayrışık oy aksi
            # yöndedir. Tarih kesin bilgi gibi sunulamaz.
            if kural and kural_kolu(kural) == "idari" and not str(kural).startswith("iyuk"):
                uyarilar.append(
                    "TARTIŞMALI UZATMA (A-20): Son gün, İYUK m.8/3 çalışmaya ara uzatmasının ÖZEL "
                    "KANUNDAKİ ('%s') süreye de uygulanmasıyla bulundu. Danıştay 7. Daire "
                    "E.2000/5685 K.2002/3522 (13.11.2002) çoğunluğu bu yönde ('bu düzenleme özel bir "
                    "düzenlemedir… özel kanunlarda öngörülen dava açma süresi olması hâlinde de "
                    "uzayacağı açıktır') — ancak karar OYÇOKLUĞU ile verilmiştir; tetkik hâkimi, "
                    "Danıştay savcısı ve AYRIŞIK OY aksi yöndedir (özel süre 2577'de yazılı olmadığı "
                    "için uzamaz). Karşı taraf ayrışık oya dayanarak süre aşımı def'i ileri sürebilir: "
                    "GÜVENLİ PLAN HAM BİTİŞ tarihidir (%s) — işlemi ona göre yap, uzamış süreyi yalnız "
                    "ikincil savunma olarak tut." % (kural, ham.isoformat()))
        else:
            # v0.5.18 / Y-01 — kuralın kendi rejimi: uzatma YOK (icra İİK m.18/1;
            # tedbire itiraz HMK m.103/1-a; 4857 süreleri; AYM/AİHM — dayanak satırda).
            rapor.append(f"Adli tatil: UZATMA UYGULANMAZ — ham bitiş {son.isoformat()} ({_gun_adi(son)}) "
                         f"20 Tem–31 Ağu arasında olsa da UZATILMADI. Dayanak: {rj['adli_tatil_dayanak']}")
    elif tur=="usul" and aralik_icinde_mi(son) and adli_tatil_istisna:
        # A-7 (v0.5.14) — İSTİSNA GEREKÇESİ REJİME GÖRE DALLANIR (v0.5.18: kolun değil
        # KURALIN rejimi). İdari yargının nöbetçi mahkeme kataloğu İYUK m.62'dir ve
        # HMK m.103'ten tamamen farklıdır (MCP teyitli 2026-08-31). Sayılan işler adli
        # tatilde GÖRÜLÜR → süre UZAMAZ; ham bitiş korunur, yalnız son gün kayması yapılır.
        if rejim == "iyuk8":
            rapor.append(f"İYUK m.62 nöbetçi mahkeme işi — çalışmaya ara uzatması uygulanmadı: ham bitiş "
                         f"{son.isoformat()} ({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI. "
                         f"İYUK m.62: nöbetçi mahkeme ara verme süresi içinde (a) yürütmenin durdurulmasına "
                         f"ve delillerin tespitine ait işleri, (b) kanunen belli süre içinde karara "
                         f"bağlanması gereken işleri görür. Yalnız hafta sonu/tatil kayması yapılır.")
            uyarilar.append(
                "İYUK m.62 İSTİSNASI seçildi: İdari yargının ara verme kataloğu HMK m.103 DEĞİL, "
                "İYUK m.62'dir (iki katalog birbirinden tamamen farklıdır). Bu işin gerçekten m.62 "
                "kapsamında olduğunu TEYİT ET — kapsam dışı bir işte istisnayı uygulamak süreyi 14 GÜN "
                "YANLIŞ KISALTIR. Ayrıca İYUK m.61/1 c.2: yargı çevresine dâhil olduğu BİM'in bulunduğu "
                "il merkezi dışında kalan ve SADECE BİR idare veya bir vergi mahkemesi bulunan yerlerdeki "
                "idari yargı mercileri çalışmaya ara vermeden YARARLANAMAZ — dosyanın mahkemesi buysa "
                "m.8/3 uzamasının işleyip işlemediği ayrıca değerlendirilir. TEREDDÜTTE İKİ HESAP "
                "(v0.5.18): kendi işlemini bu ERKEN tarihe göre planla, ama bu tarih geçti diye hakkı "
                "terk etme (bayraksız tarihi de hesapla); karşı tarafa kesin dili ancak bayraksız (GEÇ) "
                "tarih de aşılmışsa kur.")
        elif rejim == "cmk331":
            rapor.append(f"CEZA KOLUNDA İSTİSNA BAYRAĞI — uzatma uygulanmadı: ham bitiş {son.isoformat()} "
                         f"({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI. Yalnız hafta "
                         f"sonu/tatil kayması yapılır.")
            uyarilar.append(
                "DİKKAT — CMK m.331/4 LAFZINDA İSTİSNA YOKTUR: 'Adlî tatile rastlayan süreler işlemez. "
                "Bu süreler tatilin bittiği günden itibaren üç gün uzatılmış sayılır.' Madde, sürenin "
                "uzamayacağı bir iş kategorisi saymaz; m.331/2-3 hangi İŞLERİN tatilde görüleceğini "
                "belirler (soruşturma, tutuklu işlere ilişkin kovuşturma, ivedi işler; BAM/Yargıtay'da "
                "tutuklu hükümler) — bu, sürenin uzamadığı anlamına GELMEZ. `--adli-tatil-istisna` "
                "bayrağı HMK m.103 için tasarlanmıştır; ceza dosyasında kullanmak süreyi ÜÇ GÜN "
                "KISALTIR ve dayanağı YOKTUR. Aksi bir dayanak teyit edilmedikçe bayrağı KALDIR.")
        elif rejim == "uygulanmaz":
            rapor.append(f"Adli tatil: UZATMA UYGULANMAZ (kuralın kendi rejimi) — ham bitiş {son.isoformat()} "
                         f"({_gun_adi(son)}) UZATILMADI; --adli-tatil-istisna bayrağı bu kuralda sonucu "
                         f"DEĞİŞTİRMEZ. Dayanak: {rj['adli_tatil_dayanak']}")
        else:
            rapor.append(f"HMK m.103 istisna işi — adli tatil uzatması uygulanmadı: ham bitiş {son.isoformat()} "
                         f"({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI. HMK m.103/1 bentleri: "
                         f"(a) ihtiyati tedbir/ihtiyati haciz/delil tespiti gibi geçici hukuki koruma, deniz "
                         f"raporu ve dispeçci atanması talepleri ile bunlara karşı itiraz ve başvurular; "
                         f"(b) her çeşit nafaka davaları ile soybağı, velayet ve vesayete ilişkin dava/işler; "
                         f"(c) nüfus kayıtlarının düzeltilmesi; (ç) hizmet akdi veya iş sözleşmesi sebebiyle "
                         f"İŞÇİLERİN AÇTIKLARI davalar; (d) ticari defter kaybı/kıymetli evrak iptali; "
                         f"(e) iflas, konkordato ve yeniden yapılandırma; (f) adli tatilde yapılmasına karar "
                         f"verilen keşifler; (g) tahkim; (ğ) çekişmesiz yargı işleri; (h) kanunen ivedi olan "
                         f"veya mahkemece ivedi görülmesine karar verilen dava/işler. Yalnız hafta sonu/tatil "
                         f"kayması yapılır.")
            uyarilar.append("HMK m.103 ADLİ TATİL İSTİSNASI seçildi: Bu işin gerçekten m.103 kapsamında (adli tatilde "
                "görülen iş) olduğunu TEYİT ET — kapsam dışı bir işte istisnayı uygulamak süreyi YANLIŞ KISALTIR ve "
                "hak kaybına yol açar. DAVACI SIFATINI TEYİT ET: m.103/1-ç istisnası 'işçilerin AÇTIKLARI davalar' "
                "lafzıyla davacı sıfatına bağlıdır — İŞVERENİN açtığı iş davası bu bende girmez. Aynı şekilde "
                "m.103/1-b nafakanın yanında soybağı, velayet ve vesayeti sayar; m.103/2 uyarınca tarafların "
                "anlaşmasıyla bu işlerin görülmesi tatil sonrasına bırakılabilir. TEREDDÜTTE İKİ HESAP "
                "(v0.5.18): kendi işlemini bu ERKEN tarihe göre planla, ama bu tarih geçti diye hakkı "
                "terk etme (bayraksız tarihi de hesapla); karşı tarafa kesin dili ancak bayraksız (GEÇ) "
                "tarih de aşılmışsa kur.")
    elif tur=="maddi" and aralik_icinde_mi(son):
        rapor.append("ⓘ Maddi hukuk süresi (zamanaşımı/hak düşürücü) — adli tatil UZATMASI UYGULANMADI "
                     "(usul süresi değildir). Yalnız son gün tatile rastlarsa kayar (aşağıda).")
    # v0.5.18 — SINIR HÂLİ: tebliğ 19 Temmuz → süre tatilin İLK günü işlemeye başlar,
    # tatil öncesinde hiç işlemez. Tatil içi tebliğe ilişkin YCGK çizgisi buraya da
    # taşınabilir (tam süre 31 Ağu'dan sonra). Doğrudan karar bulunamadı: manşet ERKEN
    # tarih kalır, diğer okuma karşı taraf kesin dil kapısına (alt_son) girer — ham
    # bitişin tatilde olup olmamasından bağımsız (uzun sürelerde de).
    if (tur == "usul" and birim != "isgunu" and not adli_tatil_istisna and rejim == "cmk331"
            and not tatilde_teblig and aralik_icinde_mi(bas) and alt_son is None):
        _sinir = sonraki_is_gunu(_sure_ekle(date(teblig.year, *ARA_BITIS), miktar, birim))
        if _sinir > son:
            alt_son = _sinir
            uyarilar.append(
                "SINIR HÂLİ — TEYİT BEKLİYOR (CMK m.331/4): tebliğ tatilin bir gün öncesinde; süre "
                "tatilin ilk günü işlemeye başladığından tatil öncesinde HİÇ işlemedi. Tatil içi "
                "tebliğe ilişkin YCGK çizgisi (E.2021/319 K.2022/846) buraya da uygulanırsa tam süre "
                "31 Ağu'dan sonra işler → %s. Doğrudan karar bulunamadı: kendi işlemini yukarıdaki "
                "ERKEN tarihe göre yap; karşı tarafın işlemi iki tarih arasındaysa kesin dil kurulmaz."
                % alt_son.isoformat())
    # v0.5.18 — rejimi TEYİTSİZ "uygulanmaz" kuralda diğer okumanın son günü (yalnız
    # KARŞILAŞTIRMA: TEMKİNLİ uyarısı + karşı taraf kesin dil kapısı). Ham bitiş tatil
    # dışında olsa bile hesaplanır (ör. İİK m.347'de öğrenme tatil içindeyse CMK okuması).
    _alt_rejim = None    # alt_son'u üreten "diğer okuma" rejimi (etiket için — KÜÇÜK-2)
    if (tur == "usul" and birim != "isgunu" and not adli_tatil_istisna and rejim == "uygulanmaz"
            and not rj["adli_tatil_teyitli"] and alt_son is None):
        _dogal = (_ONEK_REJIM.get(_onek, "hmk104") if rj.get("turetildi") == "ön ekten"
                  else _TEMKINLI_ALTERNATIF.get(kural, "hmk104"))
        # v0.5.18 K1 (KÜÇÜK-2): istifa süresinde idari dosyada "diğer okuma" İYUK m.8/3'tür —
        # aritmetik aynıdır (1 Eylül'den 7 gün ≡ 31 Ağu + 1 hafta), yalnız etiket --yargi'ye uyar.
        if str(kural or "").endswith("_istifa_vekalet_devam") and yargi == "idari":
            _dogal = "iyuk8"
        _alt_rejim = _dogal
        alt_son = _alternatif_bitis(_dogal, teblig, ham, miktar, birim)
    if not is_gunu_mu(son):
        if hafta_sonu_mu(son):
            sebep = ("hafta sonu — Pazar 2429 s.K. genel tatil; Cumartesi yerleşik kabul/içtihatla tatil sayılır"
                     if son.weekday()==5 else "hafta sonu — Pazar (2429 s.K. genel tatil)")
        else:
            sebep = f"resmî tatil ({resmi_tatil_mi(son)}, 2429 s.K.)"
        if not rj["son_gun_kaymasi"]:
            # v0.5.18 — AİHM: süre Sözleşme ölçütüyle işler; iç hukuktaki kayma kuralı
            # uygulanmaz (Sabri Güneş/Türkiye [BD] §§ 60-61: Pazar günü dolan süre).
            rapor.append(f"Son gün kayması YOK   : {son.isoformat()} {sebep} — süre UZAMAZ. "
                         f"Dayanak: {rj['adli_tatil_dayanak']}")
        else:
            eski = son; son = sonraki_is_gunu(son)
            # A-7/A-1 (v0.5.14) — kayma dayanağı da kola göre yazılır: hukuk HMK m.93,
            # idari İYUK m.8/2, ceza CMK m.39/4 (MCP teyitli 2026-08-31); v0.5.18: icra
            # İİK m.19/3 (Y. 12. HD E.2009/1886 K.2009/10134), AYM için uygulama örneği.
            if _onek == "aym":
                _kayma_capa = ("AYM uygulaması — Ramazan Seçen, B. No: 2021/37483 § 2, 9: otuzuncu gün "
                               "Cumartesi, Pazartesi başvurusu incelendi; genel dayanak TEYİT BEKLİYOR")
            else:
                _kayma_capa = {"ceza": "CMK m.39/4", "idari": "İYUK m.8/2",
                               "icra": "İİK m.19/3"}.get(_kol, "HMK m.93")
            rapor.append(f"Tatil günü düzeltmesi : {eski.isoformat()} {sebep} → ilk iş günü {son.isoformat()} "
                         f"({_kayma_capa}: yalnız SON GÜN tatile rastlarsa uzar; aradaki tatil günleri süreye DAHİLDİR)")
    if rj["son_gun_kaymasi"]:
        if ihtiyat_son is not None and not is_gunu_mu(ihtiyat_son):
            ihtiyat_son = sonraki_is_gunu(ihtiyat_son)
        if alt_son is not None and not is_gunu_mu(alt_son):
            alt_son = sonraki_is_gunu(alt_son)
    if ihtiyat_son is not None and ihtiyat_son >= son:
        ihtiyat_son = None
    if alt_son is not None and alt_son == son:
        alt_son = None
    if tatilde_teblig:
        if ihtiyat_son is not None:
            rapor.append(f"İhtiyat planı         : {ihtiyat_son.isoformat()} ({_gun_adi(ihtiyat_son)}) — eski "
                         f"daire uygulaması (tatil bitiminden itibaren üç gün); işlemi mümkünse buna göre yap")
        uyarilar.append(
            "CEZA ADLİ TATİLİ — TATİL İÇİNDE TEBLİĞ (CMK m.331/4): 'Adlî tatile rastlayan süreler "
            "işlemez.' Tebliğ (%s) tatil içinde olduğundan süre tatilde İŞLEMEDİ; TAM süre tatilin "
            "bittiği günden sonra işler → %s (YCGK E.2013/2-272 K.2013/524; YCGK E.2021/319 "
            "K.2022/846 — TUTUKLU işlerde de aynı; 14.02.1934 t. 47/1 s. İBK; AYM Ramazan Seçen, "
            "B. No: 2021/37483: süreyi tatilde işletmek mahkemeye erişim hakkını İHLAL eder). "
            "İHTİYAT PLANI: bazı eski daire kararları tatil içi tebliğde de 'tatil bitiminden itibaren "
            "üç gün' uygulamıştır (ör. Y. 11. CD E.2017/14079 K.2018/2400)%s — %s tarihine güvenmen "
            "gerekirse YCGK 2022/846'yı dilekçede an. Tutuklu sanıkta CMK m.263 kanalı ayrıca "
            "değerlendirilir." % (
                teblig.isoformat(), son.isoformat(),
                (" → mümkünse %s tarihine kadar başvur" % ihtiyat_son.isoformat())
                if ihtiyat_son else "", son.isoformat()))
    if alt_son is not None and rejim == "uygulanmaz":
        uyarilar.append(
            "TEMKİNLİ REJİM — TEYİT BEKLİYOR: '%s' için adli tatil rejimi resmî kaynakla teyit "
            "EDİLEMEDİ; motor uzatma UYGULAMADI ve ERKEN tarihi verdi (%s). Diğer okumada (adli "
            "tatil uzatması ya da süre tatilde işlemezse) son gün %s olurdu — bu GEÇ tarihe GÜVENME "
            "(yalnız ikincil savunma). Karşı tarafın işlemi iki tarih arasındaysa kesin dil kurulmaz "
            "(ARA TESPİT). Dayanak: %s" % (
                kural or "--sure", son.isoformat(), alt_son.isoformat(), rj["adli_tatil_dayanak"]))
    # ── v0.5.18 K1 (T5-1) — İSTİFA SÜRESİ İKİ MUHATAPLIDIR ────────────────────
    # NEDEN VAR: eski MK-2 çağrısı (kuralsız --sure/--birim) manşeti HMK m.104 ile uzatıp
    # yazın müvekkile 2026-09-07 gibi GEÇ tarih veriyordu (doğrusu 2026-08-10). Manşet
    # (erken tarih) MÜVEKKİLE söylenen tarihtir; geç okuma (alt_son) yalnız istifa eden
    # avukatın kendi takip sınırıdır — iki tarih iki ayrı muhataba gider, karıştırılmaz.
    if str(kural or "").endswith("_istifa_vekalet_devam"):
        _gec = (("geç okumaya (%s — %s uygulanırsa) kadar"
                 % (alt_son.isoformat(), REJIM_ETIKET.get(_alt_rejim or "hmk104", "HMK m.104")))
                if alt_son is not None else
                "en az bu tarihe kadar (ham bitiş adli tatil dışında: iki okuma aynı güne düşer)")
        uyarilar.append(
            "İSTİFA — İKİ TARİH, İKİ MUHATAP (HMK m.82 / Av.K. m.41): MÜVEKKİLE 'yeni vekil bu "
            "tarihten ÖNCE' uyarısı manşetteki ERKEN tarihle (%s) verilir — belirsizlikte erken tarih "
            "esastır; geç okumaya güvenip müvekkil temsilsiz bırakılmaz (HMK m.82/2: vekâlet veren "
            "davayı takip etmez ve başka vekil görevlendirmezse tarafın yokluğu hükümleri uygulanır). "
            "İSTİFA EDEN AVUKAT süre ve duruşma takibini %s sürdürür; bu arada vekile yapılan tebligat "
            "süreyi başlatır (Y. 13. HD E.2016/23630 K.2019/746; Y. 7. HD E.2013/26308 K.2013/21244). "
            "İki süre EŞİTLENMEZ: HMK m.82/1 iki hafta (hmk_istifa_vekalet_devam) ve Av.K. m.41 on beş "
            "gün (avk_istifa_vekalet_devam) ayrı satırda hesaplanır. Başlangıç müvekkile TEBLİĞ "
            "tarihidir (HMK m.82/3: istifa dilekçesiyle birlikte ihtaren bildirim) — mahkemeye dilekçe "
            "vermek müvekkile tebliğ yerine geçmez; tebliğ tarihi BELGELİ olmalı."
            % (son.isoformat(), _gec))
    # ── İDARİ İZİN KATMANI (uyarı — KAYDIRMA YAPILMAZ) ─────────────────────
    # Hukuki kural: idari izin (CB tasarrufu — Kararname/Karar/Genelge) 2429 anlamında resmî tatil
    # değildir; süreyi UZATMAZ, SÜREDEN SAYILIR. Riski görünür kılar, son günü değiştirmez.
    if idari_izin_mi(son):
        rapor.append(f"ⓘ Son gün {son.isoformat()} İDARİ İZİN gününe denk geliyor — son gün KAYDIRILMADI (idari izin süreden sayılır).")
        uyarilar.append("İDARİ İZİN: Son gün, Cumhurbaşkanlığı tasarrufuyla (Kararname/Karar/Genelge) ilan edilmiş idari izin gününe denk. "
            "İdari izin 2429 s.K. anlamında resmî tatil DEĞİLDİR — SÜREYİ UZATMAZ, SÜREDEN SAYILIR. "
            "Kamu birimleri (vergi dairesi, tapu, kalem, vezne) fiilen kapalı/eksik çalışıyor olabilir: "
            "fiziki işlem veya harç/vezne gerektiren adımı ÖNCEDEN tamamla; UYAP elektronik kanalı 23:59'a kadar açıktır. "
            + _kurtarma_kapisi_notu(_kol, kural))
    elif not idari_tanimli_mi(son.year) and dini_yakin_mi(son):
        uyarilar.append(f"İDARİ İZİN TARAMASI: Son gün bir dini bayrama bitişik ve {son.year} için tabloda idari izin kaydı yok. "
            "O yıl köprü günü idari izni ilan edilmiş olabilir — Mevzuat MCP'den ÜÇ enstrümanı birden "
            "(search_cbk + search_cbbaskankarar + search_cbgenelge, yıl + 'idari izin') tara; ilan edilmişse tatiller.json'a işle. "
            "NOT: idari izin süreyi UZATMAZ; bu tarama yalnızca fiilî erişim riskini görmek içindir.")
    if TATILLER.get("_tablo_yok"):
        uyarilar.append("tatiller.json bulunamadı; yalnızca sabit ulusal tatiller kullanıldı.")
    # ── v0.5.18 / Y-08 — TATİL TAKVİMİ EKSİK: sessiz yanlış hesap yok ────────
    # Dini bayram tarihleri tahmin edilmez (yalnız resmî kaynaktan tabloya işlenir).
    # Tablo eksikse motor bayram gününü iş günü sanar: takvim günü süresinde son gün
    # kaymaz, iş günü sayımında bayram günleri sayılır → tarih ERKEN tarafta kalır
    # (bizim işlemimiz için güvenli) ama karşı tarafa kesin dil KURULAMAZ (main()).
    _yillar = (set(range(teblig.year, son.year + 1)) if birim == "isgunu"
               else {ham.year, son.year})
    for _ek_tarih in (ihtiyat_son, alt_son):
        if _ek_tarih is not None:
            _yillar.add(_ek_tarih.year)
    takvim_eksik = sorted(y for y in _yillar if not dini_tam_mi(y))
    if takvim_eksik:
        _yl = ", ".join(str(y) + (" (KISMİ kayıt)" if dini_tanimli_mi(y) else "")
                        for y in takvim_eksik)
        rapor.append(f"⚠ TATİL TAKVİMİ EKSİK : {_yl} — tatiller.json'da resmî dini bayram kaydı yok/eksik; "
                     "son gün bayrama rastlıyorsa kayma YAPILAMADI (tarih erken tarafta kalır); TEYİT ET.")
        if birim == "isgunu":
            uyarilar.append(
                f"TATİL TAKVİMİ EKSİK — TEYİT ET (Y-08): İŞ GÜNÜ sayımı {_yl} yılı dini bayram günlerini "
                "BİLMİYOR ve onları iş günü saydı — gerçek son gün bu hesaptan DAHA GEÇ olabilir. Bizim "
                "işlemimiz için bu tarih güvenli (erken) taraftır; karşı tarafın süresini denetlerken "
                "bayram günlerini Diyanet/Resmî Gazete'den teyit edip tatiller.json'a işlemeden kesin "
                "dil kurma ve yeniden hesapla.")
        else:
            uyarilar.append(
                f"TATİL TAKVİMİ EKSİK — TEYİT ET (Y-08): {_yl} — tatiller.json'da resmî dini bayram "
                "tarihleri yok ya da eksik (tahmin YAZILMAZ). Son gün bir bayram gününe rastlıyorsa motor onu iş günü "
                "sandı ve KAYDIRMADI — gerçek son gün daha geç olabilir. Bizim işlemimiz için bu tarih "
                "güvenli (erken) taraftır; karşı tarafa kesin dil kurmadan önce Diyanet/Resmî Gazete'den "
                "teyit edip tatiller.json'a işle ve YENİDEN HESAPLA.")
    if not dini_tanimli_mi(son.year) or not dini_tanimli_mi(ham.year):
        yakin = []
        for yy in {son.year, ham.year}:
            if not dini_tanimli_mi(yy):
                for ad, gunler in tahmini_bayramlar(yy).items():
                    for g in gunler:
                        if abs((g - son).days) <= 3 or abs((g - ham).days) <= 3:
                            yakin.append(f"{g.isoformat()} [{ad}]")
        if yakin:
            uyarilar.append("TAHMİNİ DİNİ BAYRAM PENCERESİ: Bu yıl için tabloda resmî dini bayram yok; aritmetik hicri "
                "hesap, son günün şu TAHMİNİ bayram günlerine bitişik/denk olduğunu gösteriyor: "
                + "; ".join(sorted(set(yakin))) +
                ". Tahmin Diyanet'in rüyet-esaslı takviminden ±1-2 gün sapabilir. Kesin tarihleri Diyanet/Resmî Gazete'den "
                "teyit edip tatiller.json'a işle ve YENİDEN HESAPLA — tahmine dayanarak son günü kaydırma/sabitleme kararı VERME.")
        else:
            uyarilar.append(f"DİNİ BAYRAM: {ham.year}/{son.year} için tabloda resmî dini bayram tanımlı değil. "
                "Aritmetik hicri tahmin, son güne ±3 gün içinde bayram GÖSTERMİYOR (tahmin ±1-2 gün sapabilir). "
                "Yıl yaklaşınca Diyanet/RG tarihlerini tatiller.json'a yine de işle; o yılın tüm tahminleri için: --bayram YYYY.")
    if tur=="maddi":
        uyarilar.append("MADDİ HUKUK SÜRESİ: Bu bir zamanaşımı/hak düşürücü süre olabilir. (a) Hangisi olduğunu "
            "ve başlangıç anını (muacceliyet/öğrenme/fiil tarihi) Mevzuat MCP'den teyit et — başlangıç çoğu kez "
            "tebliğ değildir. (b) Zamanaşımı KESİLİR/DURUR (TBK m.153-158), hak düşürücü süre kural olarak durmaz/kesilmez. "
            "(c) Bu durum/kesilme olaylarını script HESAPLAMAZ — elle değerlendir.")
    else:
        uyarilar.append("PARASAL KESİNLİK: Süre işlese de karar parasal sınırın altındaysa kanun yolu KAPALI "
            "olabilir. Sınırı o yıl için Mevzuat MCP'den teyit et.")
    # Kol-özel uyarılar AYM/AİHM/Av.K. kuralında ve istifa süresi kurallarında basılmaz
    # (kol-bağımsız yollar / görev-devam süresi; v0.5.18 K1: kanun yolu kapısı uyarısı
    # ilgisiz gürültüdür — dışlama öneke VE kural adına bakar, KÜÇÜK-1).
    _kol_ozel = (_onek not in ("aym", "aihm", "avk")
                 and not str(kural or "").endswith("_istifa_vekalet_devam"))
    if _kol_ozel and _kol=="idari" and tur=="usul":
        # A-5 (v0.5.14) — eski uyarı ("özel kanun süreleri olabilir") avukatı
        # YANLIŞ yöne bakmaya sevk ediyordu: en sık ıskalanan kısa süreler özel
        # kanunlarda değil, İYUK'un KENDİSİNDEDİR (m.20/A, m.20/B — MCP teyitli
        # 2026-08-31). Bir dosyada 60 gün sanılan süre gerçekte 30 veya 10 olabilir.
        uyarilar.append(
            "ÖZEL YARGILAMA USULÜ (İYUK'UN KENDİSİNDE): Dava İYUK m.20/A (İVEDİ YARGILAMA) veya "
            "m.20/B (MERKEZÎ VE ORTAK SINAV) kapsamındaysa süreler bu hesabın varsayılanından çok "
            "daha KISADIR. m.20/A-1 katalog: ihale işlemleri (yasaklama hariç), ACELE KAMULAŞTIRMA, "
            "ÖYK kararları, 2634 turizm satış/tahsis/kiralama, ÇED kararları, 6306 CB kararları → "
            "dava 30 gün (m.20/A-2/a), temyiz 15 gün (/g), İSTİNAF YOLU KAPALI (m.45/8), m.11 "
            "UYGULANMAZ (/b), YD kararına İTİRAZ EDİLEMEZ (/e). m.20/B (MEB-ÖSYM merkezî ve ortak "
            "sınavlar) → dava 10 gün (/a), temyiz 5 gün (/f), m.11 UYGULANMAZ (/b), YD kararına "
            "itiraz edilemez (/d). İlgili kural adları: iyuk_dava_ivedi, iyuk_temyiz_ivedi, "
            "iyuk_dava_sinav, iyuk_temyiz_sinav. Ayrıca özel kanunlarda (memur disiplin, ihale vb.) "
            "başka süreler de olabilir — uygulanan kuralı Mevzuat MCP'den teyit et.")
    if _kol_ozel and _kol=="ceza" and tur=="usul":
        uyarilar.append(
            "CEZA KANUN YOLU KAPILARI: Başvuru süresi işlese de yol KAPALI olabilir — istinafta "
            "CMK m.272/3 (parasal sınır ve kesin hükümler), temyizde m.286 sınırlamaları kullanım "
            "anında Mevzuat MCP'den teyit edilir. Tutuklu sanıkta CMK m.263 (ceza infaz kurumu "
            "müdürüne başvuru) süreyi KESER — müvekkile bu kanal ayrıca söylenir.")
    # ── İŞ HUKUKU KATMANI (2026-09-10, MCP teyitli) ────────────────────────
    # İş mahkemesi süreleri, tarih aritmetiğinin DIŞINDA üç mekanizmaya bağlıdır
    # ve hiçbiri script tarafından hesaplanamaz: (a) zorunlu arabuluculuk bir
    # DAVA ŞARTIdır, (b) arabuluculuk süreci hak düşürücü süreyi DURDURUR,
    # (c) işe iade davasında iki haftalık sürenin başlangıcı içtihatta
    # TARTIŞMALIDIR. Bunlar görünür kılınmazsa doğru aritmetik yanlış tarihe
    # götürür — "yanlış olaya bağlanan doğru hesap, yanlış hesaptır".
    if str(kural or "").startswith("is_"):
        uyarilar.append(
            "ZORUNLU ARABULUCULUK (DAVA ŞARTI): 7036 s.K. m.3/1 — kanuna, bireysel veya toplu iş "
            "sözleşmesine dayanan İŞÇİ veya İŞVEREN alacağı ve tazminatı ile İŞE İADE talebiyle "
            "açılan davalarda arabulucuya başvurulmuş olması DAVA ŞARTIDIR (7445 s.K. m.41 ek "
            "cümlesiyle: bu alacak ve tazminatla ilgili İTİRAZIN İPTALİ, MENFİ TESPİT ve İSTİRDAT "
            "davaları da kapsamdadır). m.3/2: anlaşmaya varılamadığına ilişkin SON TUTANAĞIN ASLI "
            "veya arabulucunun onayladığı örneği dava dilekçesine EKLENİR. Şart yerine "
            "getirilmeden açılan dava USULDEN REDDEDİLİR.")
        uyarilar.append(
            "ARABULUCULUK SÜRECİ SÜREYİ DURDURUR (6325 s.K. m.18/A-15): 'Arabuluculuk bürosuna "
            "başvurulmasından SON TUTANAĞIN DÜZENLENDİĞİ TARİHE kadar geçen sürede zamanaşımı "
            "DURUR ve hak düşürücü süre İŞLEMEZ.' Bu script durma/kesilme olaylarını HESAPLAMAZ: "
            "yukarıdaki tarih, arabuluculukta geçen günleri DIŞARIDA BIRAKMAZ. Arabuluculuk "
            "başvurusu ile son tutanak arasındaki gün sayısını ELLE ekleyin ve sonucu ayrıca "
            "deftere işleyin.")
        # v0.5.18 — 4857 süreleri HMK'nın tayin ettiği süre değildir: kural rejimi
        # "uygulanmaz" (Y. 9. HD E.2016/1261 K.2016/22196). Eski metin uzatmanın
        # yalnız --adli-tatil-istisna ile kalkacağını söylüyordu (bayraksız GEÇ tarih).
        uyarilar.append(
            "ADLİ TATİL — İŞ HUKUKU SÜRELERİ: Bu tablodaki 4857 süreleri HMK'nın tayin ettiği süreler "
            "DEĞİLDİR; kuralın rejimi gereği HMK m.104 uzatması UYGULANMADI (Y. 9. HD E.2016/1261 "
            "K.2016/22196: işe iade süresinde m.104 uzatması usul ve yasaya aykırı). Dava açıldıktan "
            "sonraki HMK süreleri için: HMK m.103/1-ç, 'hizmet akdi veya iş sözleşmesi sebebiyle "
            "İŞÇİLERİN AÇTIKLARI davalar'ı adli tatilde görülen işler arasında sayar — bu davalarda "
            "HMK süreleri de UZAMAZ (`--adli-tatil-istisna`). Bent DAVACI SIFATINA bağlıdır — "
            "İŞVERENİN açtığı iş davası bu bende GİRMEZ ve orada HMK sürelerine uzatma işler. "
            "Sıfatı teyit et.")
    if kural == "is_ise_iade_dava":
        uyarilar.append(
            "BAŞLANGIÇ TARTIŞMALI (işe iade, iki hafta): 4857 m.20/1 süreyi 'son tutanağın "
            "DÜZENLENDİĞİ tarihten' başlatır; ancak BAM daireleri arasında ayrılık SÜRMEKTEDİR. "
            "İstanbul BAM 31. HD (2020/2741 E., 2021/10 K.): düzenlenme tarihi esastır, imza "
            "tarihi ve telekonferansla katılım önemsizdir, süre hak düşürücüdür ve resen "
            "gözetilir. İstanbul BAM 29. HD (2024/502 E., 2024/919 K.): tutanakta imza/imza "
            "tarihi yoksa TÜM İMZALARIN TAMAMLANDIĞI tarih düzenlenme tarihi sayılır. Yargıtay "
            "9. HD (E.2024/10170, K.2024/14797, 18.11.2024) uyuşmazlığın giderilmesine YER "
            "OLMADIĞINA karar verdiği için ayrılık giderilmemiştir. GÜVENLİ PLAN: DÜZENLENME "
            "tarihi (erken senaryo — yukarıdaki hesap budur); imza tamamlanma/tebliğ tarihine "
            "dayanan geç senaryo yalnız İKİNCİL SAVUNMA olarak tutulur.")
    if kural == "is_ise_baslatma_basvuru":
        uyarilar.append(
            "SÜRESİNDE BAŞVURMAMANIN SONUCU (4857 m.21/6): işçi on işgünü içinde işverene "
            "başvurmazsa 'işverence yapılmış olan fesih GEÇERLİ BİR FESİH SAYILIR ve işveren "
            "sadece bunun hukuki sonuçları ile sorumlu olur' — kazanılmış işe iade kararı bu "
            "sürede işlevsizleşir. Başvuru İŞVERENE yapılır (mahkemeye değil) ve ULAŞTIĞI an "
            "esastır; ispat için iadeli taahhütlü/noter kanalını kullan.")
    # ── v0.5.18 — AYM / AİHM başlangıç notları (başlangıç kapısının yol-özel ayağı) ──
    if _onek == "aym":
        uyarilar.append(
            "AYM BAŞLANGIÇ (6216 m.47/5; İçtüzük m.64/1): otuz gün başvuru yollarının TÜKETİLDİĞİ, "
            "yol yoksa ihlalin öğrenildiği tarihten işler. AYM kararlarında nihai kararın UYAP'tan "
            "öğrenildiği tarih olay olarak kaydedilmektedir (ör. Ramazan Seçen, B. No: 2021/37483, "
            "6/1/2026, § 9) — tebliğden ÖNCE öğrenme süreyi başlatabilir; genel ilke TEYİT BEKLİYOR. "
            "Erken öğrenme kanıtı varsa --teblig olarak onu gir (plan ERKEN tarih). Son günün hafta "
            "sonuna rastlaması hâlinde izleyen iş günü başvurusu incelenmiştir (aynı karar § 2, 9) — "
            "yine de mümkünse hafta sonundan önce başvur.")
    if _onek == "aihm":
        uyarilar.append(
            "AİHM BAŞLANGIÇ (AİHS m.35/1): süre nihai iç hukuk kararından işler; iç hukukta kararın "
            "yazılı tebliği öngörülüyorsa TEBLİĞ tarihi esastır (Sabri Güneş/Türkiye [BD], no. "
            "27396/06, § 53 — Worm/Avusturya'ya atıfla). AYM'nin 'UYAP'tan öğrenme' yaklaşımını "
            "AİHM'e otomatik taşıma. Süre Sözleşme ölçütleriyle hesaplanır: son gün hafta sonu/resmî "
            "tatile rastlasa da UZAMAZ (aynı karar §§ 60-61) — başvuruyu son güne bırakma.")
        # R7 (v0.5.18) — 1.2.2022 öncesi altı ay geçişi KAPSAM DIŞI (avukat kararı
        # 2026-10-06): süre dört aydır; oa-usul [G11] de yalnız dört ay der.

    # B-16 (v0.5.14) — SON SAĞLIK KONTROLÜ: son gün hiçbir koşulda başlangıç
    # tarihinden önce olamaz. Bu satır bir daha ASLA geçmeyecek olsa bile durur:
    # bu motorun tek işi tarih aritmetiğidir ve geçmişe düşen bir "son gün"
    # deftere yazılıp nöbetçi tarafından "GEÇMİŞ süre" diye alarma dönüşür.
    if son < teblig:
        raise ValueError(
            "İÇ TUTARSIZLIK: hesaplanan son gün (%s) başlangıç tarihinden (%s) ÖNCE — "
            "sonuç kullanılamaz." % (son.isoformat(), teblig.isoformat()))
    rapor.append("")
    if _kapi["supheli"]:
        # v0.5.18 — şüpheli tebliğde tek kesin tarih YOK: satır bilinçli olarak farklıdır
        # (">>> HESAPLANAN SON GÜN" ayrıştıran araçlar bunu kesin tarih sanmasın).
        rapor.append(f">>> İHTİYAT HEDEFİ (ŞÜPHELİ TEBLİĞ — tek kesin tarih DEĞİL): {son.isoformat()} "
                     f"({_gun_adi(son)}) — mesai bitimi <<<")
    else:
        rapor.append(f">>> HESAPLANAN SON GÜN  : {son.isoformat()} ({_gun_adi(son)}) — mesai bitimi <<<")
    # v0.5.18 — PLAN tarihi: kendi işlemimiz için EN ERKEN makul son gün (ihtiyat planı,
    # tartışmalı uzatmanın uzamasız hâli). Manşet hukuki son günü korur; plan ayrı yazılır.
    plan_son = min([son] + [g for g in (ihtiyat_son, alt_son) if g is not None])
    if plan_son < son:
        rapor.append(f"    ↳ PLAN (kendi işlemin için ERKEN tarih): {plan_son.isoformat()} "
                     f"({_gun_adi(plan_son)}) — gerekçe uyarılarda")
    if isinstance(_bilgi, dict):
        _bilgi.update({"rejim": rejim, "rejim_teyitli": bool(rj["adli_tatil_teyitli"]),
                       "rejim_kaynagi": rj.get("kaynak"), "rejim_turetildi": rj.get("turetildi") or "",
                       "rejim_dayanak": rj["adli_tatil_dayanak"], "kol": _kol,
                       "alt_son": alt_son, "ihtiyat_son": ihtiyat_son,
                       "takvim_eksik": takvim_eksik, "kanitsiz": _kapi["kanitsiz"],
                       "supheli": _kapi["supheli"], "plan_son": plan_son})
    return son, rapor, uyarilar


def _pencere_kontrol(json_yol, cikti_yol=None):
    """M5 (Paket D, v0.5.5) — SÜRE PENCERE BİNDİRME KONTROLÜ: birden çok süre
    kaydını (`{ad, teblig, kural | (sure+birim), [yargi, tur, adli_tatil_istisna]}`)
    OKUYUP her birini `hesapla()` ile (TEK mantık — kod tekrarı yok) çözer, her
    kaydın [teblig+1, son_gün] PENCERESİNİ çıkarır ve pencerelerin PAIRWISE
    ÇAKIŞIP çakışmadığını (bindirme) raporlar. Amaç: illiyet/kronoloji
    katmanındaki (oa-illiyet zaman katmanı) birden fazla süre AYNI ANDA
    işlerken biri gözden kaçabilir — bu kontrol o körlüğü kapatır. Hukuki
    öncelik/hangi sürenin daha kritik olduğu MUHAKEMEDİR; script yalnız
    ÇAKIŞMAYI (tarih aritmetiği) tespit eder."""
    try:
        with open(json_yol, encoding="utf-8") as f:
            kayitlar = json.load(f)
    except Exception as e:
        print(f"HATA: pencereler JSON okunamadı: {e}")
        sys.exit(1)

    # M5 düzeltmesi (Paket D sınav bulgusu, KUCUK) — kök nesne bir LİSTE
    # olmalı (ör. {"kayitlar": [...]} gibi makul bir kullanıcı hatası
    # KORUMASIZ TRACEBACK yerine nazik bir HATA mesajıyla durmalı; diğer tüm
    # hata dalları zaten '⚠ … atlandı' ile nazikçe geçiyor — şema hatası da
    # aynı disipline tabi olmalı).
    if not isinstance(kayitlar, list):
        print("HATA: --pencereler JSON kök nesnesi bir LİSTE olmalı "
              '([{ad,teblig,...}, ...]) — bulunan: ' + type(kayitlar).__name__)
        sys.exit(1)

    pencereler = []
    atlanan = []  # DÜZELTME (Ş13, v0.5.5 şerh turu): düşen HER kayıt burada iz bırakır
    asama = []    # v0.5.16 / I5: aşama tetikli kayıtlar — pencere DEĞİL, ama görünür
    for k in kayitlar:
        if not isinstance(k, dict):
            sebep = f"liste öğesi sözlük değil ({type(k).__name__})"
            print(f"  ⚠ {sebep} — atlandı")
            atlanan.append({"ad": "(bilinmiyor)", "sebep": sebep})
            continue
        ad = k.get("ad") or "(adsız)"
        # v0.5.16 / I5 — AŞAMA TETİKLİ kural: tarih penceresi YOKTUR; kayıt
        # SESSİZCE düşmez ("atlandı" da denmez — düşen değil, başka sınıf), ayrı
        # listede görünür ve bindirme aritmetiğine KATILMAZ (tarih üretilmez).
        if k.get("kural") in ASAMA_KURALLAR:
            ak = ASAMA_KURALLAR[k["kural"]]
            print(f"  ≡ '{ad}': AŞAMA TETİKLİ kural '{k['kural']}' — {ak['asama']}; "
                  f"pipeline adım {ak['pipeline_adimi']} tamamlanmadan yapılmalı; "
                  f"tarih penceresi yok, bindirmeye katılmadı")
            asama.append({"ad": ad, "kural": k["kural"], "asama": ak["asama"],
                          "pipeline_adimi": ak["pipeline_adimi"]})
            continue
        teblig_str = k.get("teblig")
        if not teblig_str:
            sebep = "'teblig' alanı eksik"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        try:
            teblig = date.fromisoformat(teblig_str)
        except Exception:
            sebep = f"geçersiz teblig tarihi '{teblig_str}'"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        yargi = k.get("yargi", "hukuk")
        tur = k.get("tur", "usul")
        adli_tatil_istisna = bool(k.get("adli_tatil_istisna"))
        if k.get("kural"):
            if k["kural"] not in KURALLAR:
                sebep = f"bilinmeyen kural '{k['kural']}'"
                print(f"  ⚠ '{ad}': {sebep} — atlandı")
                atlanan.append({"ad": ad, "sebep": sebep})
                continue
            # A-1 (v0.5.14) — kural ↔ yargı kolu uyuşmazlığı burada da SESSİZ
            # geçemez: pencere defteri de son gün üretir ve bindirme hükmü verir.
            _ku = kol_uyusmazligi(k["kural"], yargi)
            if _ku:
                sebep = "kural/yargı kolu uyuşmazlığı — %s" % _ku
                print(f"  ⚠ '{ad}': {sebep} — atlandı")
                atlanan.append({"ad": ad, "sebep": sebep})
                continue
            miktar, birim, _kaynak = KURALLAR[k["kural"]]
        # DÜZELTME (Ş13, v0.5.5 şerh turu): eski `k.get("sure") and k.get("birim")`
        # falsy kontrolü `sure: 0`ı 'alan eksik' sayıp SESSİZCE düşürüyordu (0
        # sayısal olarak geçerli bir süre DEĞİLSE bile — ör. yanlışlıkla girilen
        # bir 0 — en azından 'alan eksik' YALANINI SÖYLEMEMELİ). `is not None`
        # ile yalnız GERÇEKTEN eksik/None alan 'eksik' sayılır.
        elif k.get("sure") is not None and k.get("birim"):
            miktar, birim = k["sure"], k["birim"]
        else:
            sebep = "'kural' VEYA 'sure'+'birim' eksik"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        try:
            son, _rapor, _uyarilar = hesapla(teblig, miktar, birim, yargi, tur,
                                             adli_tatil_istisna, None, k.get("kural"))
        except Exception as e:
            sebep = f"hesaplama hatası ({e})"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        bas = teblig + timedelta(days=1)
        pencereler.append({"ad": ad, "bas": bas.isoformat(), "son": son.isoformat()})

    print("=" * 68)
    print("  SÜRE PENCERE BİNDİRME KONTROLÜ (M5, Paket D — v0.5.5)")
    print("=" * 68)
    for pe in pencereler:
        print(f"  {pe['ad']}: {pe['bas']} .. {pe['son']}")
    if asama:
        print("  --- AŞAMA TETİKLİ (tarih penceresi yok; pipeline adımına bağlı) ---")
        for ak in asama:
            print(f"  ≡ {ak['ad']}: {ak['asama']} — adım {ak['pipeline_adimi']} "
                  f"tamamlanmadan yapılmalı ({ak['kural']})")

    bindirmeler = []
    for i in range(len(pencereler)):
        for j in range(i + 1, len(pencereler)):
            a_, b_ = pencereler[i], pencereler[j]
            bas_a, son_a = date.fromisoformat(a_["bas"]), date.fromisoformat(a_["son"])
            bas_b, son_b = date.fromisoformat(b_["bas"]), date.fromisoformat(b_["son"])
            if bas_a <= son_b and bas_b <= son_a:
                bindirmeler.append((a_["ad"], b_["ad"]))

    # DÜZELTME (Ş13, v0.5.5 şerh turu BLOKER — fail-open yanlış temiz-ışık):
    # eskiden hayatta kalan pencere sayısına HİÇ BAKILMADAN `bindirmeler`
    # boşsa '>>> Bindirme yok — pencereler ayrık. <<<' basılıyordu — bu,
    # SIFIR kayıt çözülse (ör. tüm kayıtlar bozuk/eksikse) ya da yalnız TEK
    # kayıt hayatta kalsa (bindirme yapısal olarak İMKÂNSIZ) bile AYNI 'temiz'
    # OLGU BEYANINI üretiyordu — 'mekanik körlüğü olgu beyanına ÇEVİRME'
    # doktrininin (bkz. dilekce_denetim.py) bu sürümdeki ihlaliydi. Üç ayrı
    # hüküm: (a) 0 pencere → DENETLENEMEDİ + exit != 0 (girdi verilmişken
    # sessiz 'başarı' YOK); (b) 1 pencere → yapısal olarak denetlenemez
    # (bindirme TANIM GEREĞİ yoktur, ama bu bir 'ayrık' KANITI DEĞİLDİR);
    # (c) ≥2 pencere → mevcut hükme (varsa) düşen-kayıt şerhi eklenir.
    print()
    if not pencereler:
        _asama_notu = (f"; {len(asama)} aşama tetikli kayıt tarih penceresi üretmez"
                       if asama else "")
        print(f">>> BİNDİRME DENETLENEMEDİ — hiçbir tarih penceresi çözülemedi "
              f"({len(atlanan)} kayıt düştü{_asama_notu}); bu sonuç KANIT SAYILMAZ. <<<")
        denetlenemedi = True
    elif len(pencereler) == 1:
        print(f">>> Tek pencere ('{pencereler[0]['ad']}') — bindirme yapısal olarak "
              "denetlenemez (karşılaştırılacak ikinci bir pencere yok). <<<")
        denetlenemedi = False
    else:
        denetlenemedi = False
        if bindirmeler:
            print("--- BİNDİRME (üst üste binen pencereler) ---")
            for x, y in bindirmeler:
                print(f"  ⚠ '{x}' ile '{y}' PENCERELERİ ÇAKIŞIYOR — aynı dönemde iki ayrı "
                      "süre birden işliyor; önceliklendirme/çakışan iş yükü avukat "
                      "gözüyle değerlendirilmeli.")
        else:
            ek = f" (NOT: {len(atlanan)} kayıt DÜŞTÜ — kapsam eksik, bu hüküm yalnız " \
                 "hayatta kalan pencerelere dayanır.)" if atlanan else ""
            print(">>> Bindirme yok — pencereler ayrık. <<<" + ek)
    print("=" * 68)

    if cikti_yol:
        with open(cikti_yol, "w", encoding="utf-8") as f:
            json.dump({"pencereler": pencereler,
                      "bindirmeler": [{"a": x, "b": y} for x, y in bindirmeler],
                      "atlanan": atlanan,
                      "asama": asama,
                      "denetlenen_kayit": len(pencereler)},
                     f, ensure_ascii=False, indent=2)
        print(f"[JSON] {cikti_yol}")

    if denetlenemedi:
        sys.exit(1)


def _sure_flagini_yaz(kok, son_gunler, aciklama_taban, kural, tur, ek_alanlar=None):
    """E4a (v0.5.8.5) — SÜRE BAĞI: hesaplanan son gün(ler) <kok>/_oa varsa
    `_oa/sureler.json`a OTOMATİK flag olarak işlenir (halüsinasyon çıpası —
    hesap yapıldı ama deftere hiç yazılmadı boşluğu kapanır). Kayıt biçimi
    oa_hafiza.py `cmd_sure_flag` ŞEMASIYLA BİREBİR aynıdır (son_gun kanonik +
    geriye-uyumlu tarih alanı; sure_nobetci.py aynı defteri okur) — subprocess
    AÇILMAZ, doğrudan İN-PROCESS json yazımı yapılır (kapı-kapıyı-subprocess'le-
    çağırmaz kuralıyla simetrik). <kok>/_oa YOKSA hiçbir şey yazılmaz (dava
    kökü değildir; defter İCAT EDİLMEZ) — dönüş (None, sebep). Aynı
    (son_gun, aciklama) çifti defterde zaten varsa TEKRAR eklenmez (tekrar
    koşu defteri şişirmez). Dönüş: (yeni_eklenen_listesi, defter_yolu|sebep).
    v0.5.18: `ek_alanlar` (ör. {"takvim_eksik": [2027]}) her yeni kayda eklenir —
    nöbetçi tatil takvimi eksik son günü işaretler (Y-08)."""
    oa = os.path.join(kok, "_oa")
    if not os.path.isdir(oa):
        return None, f"{oa} yok — otomatik flag yazılmadı (dava kökü değil)"
    syol = os.path.join(oa, "sureler.json")
    try:
        with open(syol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = {"flagler": []}
    if not isinstance(d, dict):
        d = {"flagler": []}
    if not isinstance(d.get("flagler"), list):
        d["flagler"] = []
    yeni = []
    for tarih_iso, acik in son_gunler:
        acik = acik or aciklama_taban
        if any((f.get("son_gun") or f.get("tarih")) == tarih_iso
               and f.get("aciklama") == acik
               for f in d["flagler"] if isinstance(f, dict)):
            continue   # aynı hesap ikinci koşuda çoğalmaz
        kayit = {"son_gun": tarih_iso, "tarih": tarih_iso, "aciklama": acik,
                 "kural": kural,
                 "kayit": _datetime.datetime.now().isoformat(timespec="seconds"),
                 "tur": tur}
        if ek_alanlar:
            kayit.update(ek_alanlar)
        d["flagler"].append(kayit)
        yeni.append(tarih_iso)
    if yeni:
        d["flagler"].sort(key=lambda x: (x.get("son_gun") or x.get("tarih") or "")
                          if isinstance(x, dict) else "")
        with open(syol, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    return yeni, syol


def _asama_flagini_yaz(kok, kural, ak):
    """v0.5.16 / I5 — aşama kaydını `<kok>/_oa/sureler.json`a yazar (E4a süre
    bağının aşama kolu). Kayıt şeması: {"tur":"asama","asama","pipeline_adimi",
    "aciklama","kural","kayit"} — son_gun/tarih alanı YOKTUR (tarih yok demek,
    boş tarih yazmak değil). `_oa` yoksa defter İCAT EDİLMEZ; aynı (kural, asama)
    çifti zaten kayıtlıysa tekrar eklenmez. Dönüş: (eklendi_mi|None, bilgi)."""
    oa = os.path.join(kok, "_oa")
    if not os.path.isdir(oa):
        return None, f"{oa} yok — aşama flag'i yazılmadı (dava kökü değil)"
    syol = os.path.join(oa, "sureler.json")
    try:
        with open(syol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = {"flagler": []}
    if not isinstance(d, dict):
        d = {"flagler": []}
    if not isinstance(d.get("flagler"), list):
        d["flagler"] = []
    for f_ in d["flagler"]:
        if (isinstance(f_, dict) and f_.get("tur") == ASAMA_TUR
                and f_.get("kural") == kural and f_.get("asama") == ak["asama"]):
            return False, syol
    d["flagler"].append({
        "tur": ASAMA_TUR, "asama": ak["asama"], "pipeline_adimi": ak["pipeline_adimi"],
        "aciklama": ak["aciklama"] or ak["kaynak"], "kural": kural,
        "kayit": _datetime.datetime.now().isoformat(timespec="seconds")})
    with open(syol, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    return True, syol


def _asama_raporu(a):
    """v0.5.16 / I5 — AŞAMA TETİKLİ kural çıktısı: TARİH ARİTMETİĞİ YAPILMAZ.
    `hesapla()` hiç çağrılmaz; ">>> HESAPLANAN SON GÜN" satırı üretilmez;
    --teblig/--islem/--uets girildiyse KULLANILMADIĞI görünür yazılır (sessiz
    yutma yok). `--json` ile {"tur":"asama", ...} basılır (son_gun: null)."""
    ak = ASAMA_KURALLAR[a.kural]
    kullanilmayan = [b for b, v in (("--teblig", a.teblig), ("--islem", a.islem),
                                    ("--uets", a.uets), ("--sure", a.sure),
                                    ("--baslangic-turu", getattr(a, "baslangic_turu", None)),
                                    ("--baslangic-kaniti", getattr(a, "baslangic_kaniti", None)),
                                    ("--teblig-durumu", getattr(a, "teblig_durumu", None)),
                                    ("--adli-tatil-istisna", a.adli_tatil_istisna)) if v]
    _kaynak_adi = "gömülü tablo" if _ASAMA_TABLO_YOK else "sure_kurallari.json"
    if a.json:
        veri = {"tur": ASAMA_TUR, "kural": a.kural, "asama": ak["asama"],
                "pipeline_adimi": ak["pipeline_adimi"], "kaynak": ak["kaynak"],
                "aciklama": ak["aciklama"], "mcp_teyit_tarihi": ak["mcp_teyit_tarihi"],
                "son_gun": None, "tarih_aritmetigi": False,
                "kural_kaynagi": _kaynak_adi, "kullanilmayan_girdiler": kullanilmayan}
        print(json.dumps(veri, ensure_ascii=False, indent=2))
        return
    print("=" * 66); print("  SÜRE HESABI — AŞAMA TETİKLİ KURAL (tarih aritmetiği YOK)"); print("=" * 66)
    if _ASAMA_TABLO_YOK:
        print("⚠ AŞAMA TABLOSU: gömülü (fallback) tabloya düşüldü — sebep: %s"
              % (_ASAMA_TABLO_SEBEP or "bilinmiyor"))
    print(f"Kural                 : {a.kural}  →  {ak['kaynak']}")
    print(f"Kural kaynağı/teyit   : {_kaynak_adi}; mcp_teyit_tarihi = "
          f"{ak['mcp_teyit_tarihi'] or 'BOŞ → kuralı Mevzuat MCP ile TEYİT ET'}")
    print(f"Süre türü             : asama  (aşama tetikli — takvim süresi DEĞİL)")
    print()
    print(f">>> AŞAMA TETİKLİ: {ak['asama']} — pipeline adım {ak['pipeline_adimi']}'e bağlı; "
          f"tarih yok <<<")
    print(f"    Adım {ak['pipeline_adimi']} tamamlanmadan bu işlem yapılmalı.")
    if ak["aciklama"]:
        print(f"    {ak['aciklama']}")
    if kullanilmayan:
        print(f"ⓘ Girilen {', '.join(kullanilmayan)} KULLANILMADI: aşama kuralında tarih "
              "aritmetiği yapılmaz — bir 'son gün' üretmek yanlış tarih üretmek olurdu.")
    print("\n--- UYARILAR (deterministik DEĞİL — elle teyit) ---")
    print("  ! Aşamanın kapanıp kapanmadığını (cevap verildi mi / tahkikat bitti mi / hüküm "
          "verildi mi) DOSYADAN teyit et; script aşamayı bilmez, yalnız kuralı söyler.")
    print("  ! Aşama bir tebliğle takvime bağlanırsa (ör. ön inceleme davetiyesi, HMK m.139/1-ç → "
          "--kural hmk_on_inceleme_belge_sunma) o an tarih kuralına geç: --kural <tarih kuralı> "
          "--teblig <tebliğ> (tabloda yoksa --sure N --birim ...) ile hesapla.")
    print("=" * 66)
    if a.flagsiz:
        print("ⓘ --flagsiz: otomatik sureler.json flag yazımı istekle KAPALI.")
    else:
        try:
            _yeni, _bilgi = _asama_flagini_yaz(a.kok, a.kural, ak)
        except Exception as _e:
            print(f"UYARI: aşama flag'i yazılamadı ({_e}) — deftere elle işle.")
        else:
            if _yeni is None:
                print(f"ⓘ SÜRE BAĞI: {_bilgi}; dava kökünde `--kok <klasör>` ile koş.")
            elif _yeni:
                print(f"AŞAMA FLAG'İ OTOMATİK İŞLENDİ (tur=asama, son_gun YOK): {_bilgi}")
                print("(sure_nobetci.py --kok . bu kaydı AYRI blokta gösterir; tarih sayımına katmaz.)")
            else:
                print(f"ⓘ SÜRE BAĞI: aynı aşama kaydı defterde ZATEN kayıtlı — tekrar eklenmedi ({_bilgi}).")
    print("NOT: event_create/reminder_create ÇAĞRILMAZ; aşama takibi pipeline defteri "
          "(pipeline_kayit.py) ve _oa/dosya.md üzerinden AVUKAT tarafından yürütülür.")


# v0.5.18 — KESİN DİL KAPISI (karşı taraf denetimi). "Süre kaçırılmıştır" kesin
# dili ancak şu üçü birlikteyken kurulur: başlangıç BELGELİ, tebliğ şüphesiz,
# adli tatil rejimi ve tatil takvimi TEYİTLİ (references/baslangic-kapisi.md §3).
# Takvim belirsizliği eşiği: en uzun dini bayram (Kurban: arife yarım + dört gün)
# hafta sonu ve olası köprü idari izniyle birleşince ~9 güne çıkar; 10 gün marj.
TAKVIM_BELIRSIZLIK_GUN = 10


def _kesin_dil_engelleri(islem, son_ref, bilgi_ref, fark_ref, bilgi_ana):
    """Kesin dilin eksik ŞARTLARINI insan-okur liste olarak döndürür (boş = engel yok).
    son_ref/fark_ref: kesin dil için aşılması gereken en geç son gün ve işlemin ondan farkı."""
    engel = []
    if bilgi_ana.get("kanitsiz"):
        engel.append("başlangıç BELGEYE bağlanmadı (--baslangic-kaniti beyan/yok/tanınmayan)")
    if bilgi_ana.get("supheli") or bilgi_ref.get("supheli"):
        engel.append("tebliğ ŞÜPHELİ (--teblig-durumu supheli) — tek kesin tarih yok")
    if bilgi_ana.get("rejim_turetildi"):
        engel.append("adli tatil rejimi TÜRETİLDİ (kural kaydında rejim alanı yok)")
    _alt = bilgi_ref.get("alt_son")
    if _alt is not None and min(son_ref, _alt) < islem <= max(son_ref, _alt):
        engel.append("adli tatil rejimi TEYİTSİZ/TARTIŞMALI — diğer okumada son gün %s"
                     % _alt.isoformat())
    _te = sorted(set(bilgi_ana.get("takvim_eksik") or []) | set(bilgi_ref.get("takvim_eksik") or []))
    if _te and 0 < fark_ref <= TAKVIM_BELIRSIZLIK_GUN:
        engel.append("tatil takvimi EKSİK (%s) ve fark %d gün — son gün bayrama rastlıyorsa kayma "
                     "eksik kalmış olabilir" % (", ".join(str(y) for y in _te), fark_ref))
    return engel


def _ara_tespit_yaz(rapor, uyarilar, son_ref, fark_ref, engeller):
    rapor.append(f">>> ARA TESPİT — KESİN DİL KULLANMA: İşlem hesaplanan son günden ({son_ref.isoformat()}) "
                 f"{fark_ref} gün SONRA görünüyor; ancak kesinlik şartları EKSİK:")
    for _e in engeller:
        rapor.append(f"    · {_e}")
    rapor.append("    Eksikler giderilmeden 'süre kaçırılmıştır' kesin dili kullanılmaz; tespit "
                 "'teyit kaydıyla' ara tespit olarak yazılır, teyitten sonra kesinleşir.")
    uyarilar.append("KESİN DİL KULLANMA — KESİNLİK ŞARTI EKSİK: " + "; ".join(engeller) + ". Karşı "
                    "tarafın süre aşımı ihtimali GİZLENMEZ (aktif usul itirazı malzemesidir) ama "
                    "eksik şart belgelenip giderilmeden kesin dille yazılmaz.")


def main():
    p = argparse.ArgumentParser(description="Deterministik Türk usul/maddi süre hesaplayıcı (v3)")
    p.add_argument("--teblig", help="Başlangıç tarihi: usulde tebliğ/öğrenme; maddi hukukta muacceliyet/öğrenme/fiil (YYYY-MM-DD)")
    p.add_argument("--sure", type=int); p.add_argument("--birim", choices=["gun","isgunu","hafta","ay","yil"],
                   help="isgunu: hafta sonu ve resmî tatiller SAYILMAZ (4857 m.21/5 'on işgünü')")
    p.add_argument("--kural", choices=list(KURALLAR.keys()) + list(ASAMA_KURALLAR.keys()),
                   help="tarih kuralı (%d adet; gün/İŞ GÜNÜ/hafta/ay/yıl) VEYA aşama tetikli "
                        "kural (%s — tarih aritmetiği YAPILMAZ, --teblig gerekmez)"
                        % (len(KURALLAR), ", ".join(ASAMA_KURALLAR)))
    p.add_argument("--json", action="store_true",
                   help="v0.5.16 — makine-okur çıktı: aşama kuralında YALNIZ JSON "
                        "({\"tur\":\"asama\",...}); tarih kuralında raporun sonuna "
                        "'[JSON] {...}' satırı eklenir.")
    p.add_argument("--yargi", choices=["hukuk","idari","ceza","icra"], default="hukuk",
                   help="Yargı kolu. --kural VERİLDİYSE adli tatil rejimini KURALIN KENDİSİ "
                        "taşır (v0.5.18; ör. iik_* = uzatma yok, İİK m.18/1). --kural yoksa "
                        "rejimi kol belirler: hukuk = HMK m.104 (31 Ağu + 1 hafta); idari = "
                        "İYUK m.8/3 (1 Eylül'den 7 gün); ceza = CMK m.331/4 (tatilde işlemez, "
                        "bitiminden ÜÇ GÜN); icra = uzatma YOK (İİK m.18/1, HMK m.103/1-h). "
                        "cmk_* kuralları YALNIZ --yargi ceza ile koşulur (aksi hâlde hesap DURUR).")
    p.add_argument("--tur", choices=["usul","maddi"], default="usul",
                   help="usul = kanun yolu/başvuru süresi (adli tatil uygulanır); "
                        "maddi = zamanaşımı/hak düşürücü (TBK/TMK/TTK/6183 vb. — adli tatil uygulanmaz)")
    p.add_argument("--baslangic-turu", dest="baslangic_turu",
                   choices=["teblig", "tefhim", "ogrenme", "olay", "belirsiz"],
                   default=None,
                   help="v0.5.13 — süreyi başlatan OLAYIN türü (opsiyonel; aritmetiği "
                        "DEĞİŞTİRMEZ, çıktıda görünür kılar). Aynı dosyada iki rejim "
                        "yaşayabilir: CMK m.268 itiraz ÖĞRENME gününden, m.273/291 "
                        "istinaf-temyiz GEREKÇELİ KARARIN TEBLİĞİNDEN işler. "
                        "'belirsiz' verilirse iki senaryo uyarısı düşer ve plan ERKEN "
                        "tarihe göre yapılır.")
    p.add_argument("--baslangic-kaniti", dest="baslangic_kaniti",
                   choices=sorted(BASLANGIC_KANITLARI), default=None,
                   help="v0.5.18 BAŞLANGIÇ KAPISI — süreyi başlatan olayın KANITI: mazbata, "
                        "uets-kaydi (7201 s. TK m.7/a; iki senaryoyu kendiliğinden açar), "
                        "kalem-tevdi (m.36), ilan (m.31), tefhim-tutanagi, uyap-erisim-kaydi, "
                        "kesinlesme-serhi, beyan/yok (belgesiz → hesap ihtiyat amaçlı, karşı "
                        "tarafa kesin dil KAPALI). Kanıtın işaret ettiği olay kuralın izinli "
                        "başlangıç türüyle çelişirse uyarı basılır. Aritmetiği değiştirmez.")
    p.add_argument("--teblig-durumu", dest="teblig_durumu",
                   choices=sorted(TEBLIG_DURUMLARI), default=None,
                   help="v0.5.18 — gecerli | usulsuz (7201 s. TK m.32: muttali olunan tarih "
                        "tebliğ tarihi sayılır → --baslangic-turu ogrenme) | supheli (tarih "
                        "okunamıyor/çelişkili → tek kesin tarih ÜRETİLMEZ, 'İHTİYAT HEDEFİ').")
    p.add_argument("--islem", metavar="YYYY-MM-DD",
                   help="Fiilî işlem/başvuru tarihi (özellikle KARŞI TARAF denetimi): hesaplanan son günle "
                        "karşılaştırılır; süre kaçırılmışsa NET ve KESİN tespit üretilir (çalışmaya eklenecek dille)")
    p.add_argument("--bayram", type=int, metavar="YYYY",
                   help="Süre hesabı yerine: verilen miladi yıl için TAHMİNİ dini bayram günlerini yazdır "
                        "(aritmetik hicri hesap, ±1-2 gün; Diyanet/RG teyidi ŞART — teyitliyi tatiller.json'a işle)")
    p.add_argument("--adli-tatil-istisna", action="store_true",
                   help="HMK m.103 istisna işi (nafaka, ihtiyati tedbir/haciz, delil tespiti, çekişmesiz yargı, "
                        "iş mahkemesi/iş hukuku uyuşmazlıkları vb.): adli tatil UZATMASI UYGULANMAZ — ham bitiş korunur, "
                        "yalnız hafta sonu/tatil kayması yapılır. Bayraksız (varsayılan) davranış aynen kalır.")
    p.add_argument("--uets", action="store_true",
                   help="E-tebligat (UETS): 7201 m.7/a — elektronik adrese ulaştığı tarihi izleyen 5. günün sonunda "
                        "tebliğ edilmiş sayılır. İki senaryoyu (ulaşma/okunma günü esas VE ulaşma+5. gün karinesi) "
                        "çift hesaplar ve gösterir. --teblig = elektronik adrese ULAŞMA/okunma günüdür.")
    p.add_argument("--pencereler", metavar="JSON",
                   help="M5 (Paket D): SÜRE PENCERE BİNDİRME kontrolü — birden çok "
                        "{ad,teblig,(kural|sure+birim),[yargi,tur,adli_tatil_istisna]} kaydı "
                        "taşıyan bir JSON dosyasını okur, her birini hesapla() ile çözer ve "
                        "[teblig+1, son_gün] pencerelerinin PAIRWISE çakışıp çakışmadığını raporlar.")
    p.add_argument("--pencereler-json", dest="pencereler_json_cikti", metavar="YOL",
                   help="--pencereler ile: sonucu makine-okur JSON olarak bu yola da yaz")
    p.add_argument("--kok", default=".",
                   help="E4a SÜRE BAĞI: çalışma kökü — <kok>/_oa VARSA hesaplanan son gün "
                        "_oa/sureler.json'a OTOMATİK flag olarak işlenir (oa_hafiza sure-flag "
                        "şeması; sure_nobetci.py aynı defteri okur). _oa yoksa yazılmaz.")
    p.add_argument("--aciklama", default=None,
                   help="otomatik süre flag'i açıklaması (verilmezse kural/süre metninden türetilir)")
    p.add_argument("--flagsiz", action="store_true",
                   help="otomatik sureler.json flag yazımını kapat (yalnız hesap yap)")
    a = p.parse_args()
    if a.pencereler:
        _pencere_kontrol(a.pencereler, a.pencereler_json_cikti)
        return
    if a.bayram:
        print(f"TAHMİNİ dini bayram günleri — {a.bayram} (aritmetik hicri hesap; Diyanet rüyet takviminden ±1-2 gün sapabilir):")
        th = tahmini_bayramlar(a.bayram)
        if not th: print("  (bu yıl için tahmin üretilemedi)")
        for ad, gunler in sorted(th.items()):
            print(f"  {ad}: {gunler[0].isoformat()} .. {gunler[-1].isoformat()} ({len(gunler)} gün)")
        if str(a.bayram) in DINI and DINI[str(a.bayram)]:
            print(f"  ⓘ Tabloda {a.bayram} için RESMÎ kayıt zaten var: {sorted(DINI[str(a.bayram)])}")
        print("UYARI: Bunlar TAHMİNDİR — süre hesabında kullanılmaz. Diyanet/Resmî Gazete'den teyit edip")
        print("tatiller.json 'dini' bölümüne salt-ISO işle; idari izin (CBK/Karar/Genelge) ilanlarını da ayrıca tara.")
        return
    # v0.5.16 / I5 — AŞAMA TETİKLİ kural: --teblig zorunluluğundan ve kol
    # uyuşmazlığı kapısından ÖNCE ayrılır; hesapla() hiç çağrılmaz.
    if a.kural in ASAMA_KURALLAR:
        _asama_raporu(a)
        return
    if not a.teblig:
        p.error("--teblig zorunlu (ya da --bayram YYYY kullan)")
    # B-22 (v0.5.14) — gg.aa.yyyy alışkanlığı ve tipografik hatalar ham
    # ValueError/traceback üretiyordu; avukat hatanın kendisinde mi araçta mı
    # olduğunu ayırt edemiyordu. Artık argparse'ın kendi temiz hata yolu.
    try:
        teblig = date.fromisoformat(a.teblig)
    except ValueError as e:
        p.error("--teblig geçersiz tarih: %r (%s). Beklenen biçim YYYY-AA-GG "
                "(ör. 2026-05-20) — gg.aa.yyyy KABUL EDİLMEZ." % (a.teblig, e))
    kaynak=None
    if a.kural:
        # A-1 (P0) — SESSİZ YANLIŞ VARSAYILAN YASAK: kural ile yargı kolu
        # uyuşmuyorsa hesap hiç yapılmaz. Uyarı basıp devam etmek yetmez;
        # ">>> HESAPLANAN SON GÜN" satırı ve otomatik defter flag'i yanlış
        # tarihi kalıcılaştırır (ve sure_nobetci onu otorite sayar).
        _uyusmazlik = kol_uyusmazligi(a.kural, a.yargi)
        if _uyusmazlik:
            p.error("KURAL ↔ YARGI KOLU UYUŞMAZLIĞI — hesap DURDURULDU (yanlış son gün "
                    "üretilmedi, deftere hiçbir şey yazılmadı).\n  %s" % _uyusmazlik)
        miktar,birim,kaynak = KURALLAR[a.kural]
        if a.kural.startswith("iyuk") and a.yargi!="idari":
            print("ⓘ Not: İYUK kuralı; --yargi idari önerilir (çalışmaya ara mekaniği). "
                  "Uzatma aritmetiği hukuk koluyla aynı sonucu verdiği için hesap DURDURULMADI.")
        if a.kural.startswith("iik") and a.yargi == "hukuk":
            print("ⓘ Not: İİK kuralı — adli tatil rejimini kural kendisi taşır (v0.5.18: uzatma "
                  "YOK); --yargi icra önerilir (kayma dayanağı İİK m.19/3, kurtarma kapısı İİK m.65).")
    elif a.sure is not None and a.birim:
        # B-16 — eski `a.sure and a.birim` kontrolü `--sure 0`ı falsy görüp
        # "alan eksik" YALANINI söylüyordu (kullanıcı alanı VERMİŞTİ).
        miktar,birim = a.sure,a.birim
        _mh = miktar_dogrula(miktar, birim)
        if _mh:
            p.error("--sure geçersiz: %s" % _mh)
    else:
        p.error("Ya --kural ver ya da --sure + --birim birlikte ver.")
    # v0.5.18 — UETS kaydı kanıt olarak verildiyse iki senaryo ZORUNLUDUR (7201 s. TK
    # m.7/a): ulaşma günü ile tebliğ-sayılma günü karıştırılmasın diye --uets açılır.
    _uets_kendiliginden = bool(getattr(a, "baslangic_kaniti", None) == "uets-kaydi" and not a.uets)
    if _uets_kendiliginden:
        a.uets = True
    bilgi = {}
    try:
        son,rapor,uyarilar = hesapla(teblig,miktar,birim,a.yargi,a.tur,a.adli_tatil_istisna,
                                     getattr(a, "baslangic_turu", None), a.kural,
                                     baslangic_kaniti=getattr(a, "baslangic_kaniti", None),
                                     teblig_durumu=getattr(a, "teblig_durumu", None),
                                     _bilgi=bilgi)
    except (ValueError, OverflowError) as e:
        # B-22 — uç tarih/miktarda ham traceback yerine temiz mesaj.
        p.error("hesap yapılamadı: %s" % e)
    # ── E-TEBLİGAT / UETS (7201 m.7/a): ulaşma+5. gün karine senaryosunu çift hesapla ─
    son_karine = None
    bilgi_k = {}
    if a.uets:
        # A-4 (v0.5.14) — E-TEBLİĞ DAYANAĞI KURALA GÖRE SEÇİLİR. Aritmetik her iki
        # rejimde de aynıdır (beşinci günün sonu), bu yüzden dayanak hatası sessiz
        # kalıyordu — ama dilekçeye yanlış norm giriyordu. MCP teyitli 2026-08-31:
        #   7201 m.7/a  : "...elektronik adresine ULAŞTIĞI tarihi izleyen beşinci günün sonunda..."
        #   VUK m.107/A : "...bu sistem ile muhatabına İLETİLDİĞİ tarihi izleyen beşinci günün
        #                  sonunda..." (Değişik: 24/6/2026-7587/9 md.)
        _vergi_kanadi = a.kural in ("iyuk_dava_vergi", "amme_6183_m58")
        if _vergi_kanadi:
            _dayanak = ("VUK m.107/A (vergi idaresinin elektronik tebligatı; Değişik: 24/6/2026-7587 s.K.) "
                        "— tebliğ, sistemle muhatabına İLETİLDİĞİ tarihi izleyen 5. günün sonunda yapılmış sayılır")
            _dayanak_kisa = "VUK m.107/A"
        else:
            _dayanak = ("7201 s.K. m.7/a (UETS üzerinden adli/idari tebligat) — tebligat, muhatabın "
                        "elektronik adresine ULAŞTIĞI tarihi izleyen 5. günün sonunda yapılmış sayılır")
            _dayanak_kisa = "7201 m.7/a"
        karine_teblig = teblig + timedelta(days=5)
        son_karine, _rk, uyarilar_karine = hesapla(karine_teblig, miktar, birim, a.yargi,
                                                   a.tur, a.adli_tatil_istisna, None, a.kural,
                                                   teblig_durumu=getattr(a, "teblig_durumu", None),
                                                   _bilgi=bilgi_k)
        rapor.append("")
        rapor.append("── E-TEBLİGAT (UETS/e-tebligat) — İKİ SENARYO (çift hesap) ─────────")
        if _uets_kendiliginden:
            rapor.append("ⓘ --baslangic-kaniti uets-kaydi → iki senaryo KENDİLİĞİNDEN açıldı (--uets).")
        rapor.append(f"Dayanak               : {_dayanak}.")
        if _vergi_kanadi:
            rapor.append("    (Adli tebligat 7201 m.7/a'ya tabidir; burada VERGİ kanadı kuralı seçildiği için")
            rapor.append("     VUK m.107/A gösterildi — dosyada fiilen hangi rejimin uygulandığını TEYİT ET.)")
        rapor.append(f"UETS Senaryo-1 (ulaşma/iletilme günü esas): teblig={teblig.isoformat()} "
                     f"→ son gün {son.isoformat()} ({_gun_adi(son)})")
        rapor.append(f"UETS Senaryo-2 (karine: ulaşma+5. gün sonu): teblig={karine_teblig.isoformat()} "
                     f"→ son gün {son_karine.isoformat()} ({_gun_adi(son_karine)})")
        rapor.append("    GÜVENLİ TARAF — AMACA GÖRE AYRILIR (tek tanım):")
        rapor.append(f"    · BİZİM süremizde (kanun yolu/başvuru): güvenli taraf ERKEN son gündür — {son.isoformat()}")
        rapor.append("      (Senaryo-1). Karine senaryosu tanım gereği 5 gün DAHA GEÇtir; ona güvenip beklemek,")
        rapor.append(f"      girilen tarih zaten TEBLİĞ-SAYILMA tarihiyse süreyi 5 gün AŞMAK demektir. İşlemi")
        rapor.append(f"      {son.isoformat()} tarihine göre planla.")
        rapor.append("    · KARŞI TARAFA kesin dil kurarken: 'süre kaçırılmıştır' YALNIZ her iki senaryo da")
        rapor.append("      aşılmışsa yazılır (karine hukuken geçerli tebliğ tarihidir) — bkz. --islem denetimi.")
        rapor.append(f"    Ayrım: ULAŞMA/İLETİLME tarihi ≠ TEBLİĞ-SAYILMA tarihi. Hangisinin girildiğini")
        rapor.append(f"    UYAP/UETS kaydından BELGELİ teyit et; {_dayanak_kisa} metnini kullanım anında MCP'den doğrula.")
        uyarilar.append(
            "UETS/E-TEBLİGAT (%s): İki son gün üretildi. BİZİM süremizde güvenli taraf ERKEN "
            "olan son gündür (%s) — geç senaryoya (karine, %s) güvenmek hak kaybettirir. Karşı tarafa "
            "yönelik KESİN dil ise ancak HER İKİ senaryo da aşılmışsa kurulur. Süre başlangıç anını "
            "(ulaşma/iletilme tarihini) UYAP/UETS kaydından BELGELİ teyit et; ulaşma günü ile 5. gün "
            "karinesini karıştırma." % (_dayanak_kisa, min(son, son_karine).isoformat(),
                                        max(son, son_karine).isoformat()))
        # Senaryo-2 (karine) hesabının KENDİ uyarılarından Senaryo-1'den farklı olanları da rapora taşı
        # (ör. karine tebliğ tarihi farklı bir idari izin/bayram penceresine düşebilir — sessizce atılmaz).
        _farkli_uk = [u for u in uyarilar_karine if u not in uyarilar]
        if _farkli_uk:
            rapor.append("    Senaryo-2 (karine) hesabına özgü ek uyarı(lar) — aşağıya işlendi.")
            for _u in _farkli_uk:
                uyarilar.append(f"[UETS Senaryo-2/karine] {_u}")
    # ── SÜRE DENETİMİ (--islem): süresinde mi, kaçırıldı mı (özellikle KARŞI TARAF) ──
    if a.islem:
        try:   # B-22 — --islem de temiz hata versin
            islem = date.fromisoformat(a.islem)
        except ValueError as e:
            p.error("--islem geçersiz tarih: %r (%s). Beklenen biçim YYYY-AA-GG."
                    % (a.islem, e))
        fark = (islem - son).days
        rapor.append("")
        rapor.append("── SÜRE DENETİMİ (fiilî işlem tarihi karşılaştırması) ──────────────")
        rapor.append(f"Fiilî işlem tarihi    : {islem.isoformat()} ({_gun_adi(islem)})")
        if a.uets and son_karine is not None:
            # --uets ile birlikte: 7201 m.7/a karine senaryosu hukuken GEÇERLİ tebliğ
            # tarihidir (ulaşma+5. gün). Yalnız Senaryo-1'e (okunma günü) karşı denetim
            # kesin/net dil için YETERSİZDİR — iki senaryoyu da ayrı ayrı denetle.
            fark_karine = (islem - son_karine).days
            gecti_s1 = fark > 0
            gecti_s2 = fark_karine > 0
            rapor.append(f"    Senaryo-1 (okunma esas) son gün  : {son.isoformat()} → fark {fark:+d} gün")
            rapor.append(f"    Senaryo-2 (karine, ulaşma+5) son gün: {son_karine.isoformat()} → fark {fark_karine:+d} gün")
            # v0.5.18 — kesin dil için aşılması gereken EN GEÇ son gün karine senaryosudur.
            _engeller = _kesin_dil_engelleri(islem, son_karine, bilgi_k, fark_karine, bilgi)
            if gecti_s1 and gecti_s2 and _engeller:
                _ara_tespit_yaz(rapor, uyarilar, son_karine, fark_karine, _engeller)
            elif gecti_s1 and gecti_s2:
                rapor.append(f">>> TESPİT — SÜRE KAÇIRILMIŞTIR (HER İKİ SENARYODA DA): İşlem, Senaryo-1 son gününden "
                             f"{fark} gün, Senaryo-2 (karine) son gününden {fark_karine} gün SONRA yapılmıştır.")
                rapor.append("    Süresinden sonra yapılan işlem usul hukuku bakımından sonuç doğurmaz; süreye")
                rapor.append("    ilişkin itiraz/ret talebi DERHÂL ileri sürülür.")
                uyarilar.append("SÜRE KAÇIRMA TESPİTİ (UETS — İKİ SENARYO DA AŞILMIŞ) — ÇALIŞMAYA EKLE (net/kesin dil): "
                    "Karşı tarafa ait süre kaçırması GİZLİ CEPHANELİKTE SAKLANMAZ — bu bir savunma değil AKTİF usul "
                    "itirazıdır, derhâl ve açıkça ileri sürülür. Tebliğ-sayılma tarihini (ulaşma tarihi) UETS kaydından BELGELE.")
            elif gecti_s1 or gecti_s2:
                gec = "Senaryo-1 (okunma günü esas)" if gecti_s1 else "Senaryo-2 (karine, ulaşma+5. gün)"
                sureli = "Senaryo-2 (karine, ulaşma+5. gün)" if gecti_s1 else "Senaryo-1 (okunma günü esas)"
                rapor.append(f">>> ARA TESPİT — SENARYOYA GÖRE DEĞİŞİYOR: {gec} son gününü geçmiştir; ANCAK "
                             f"{sureli} esas alınırsa işlem SÜRESİ İÇİNDEDİR.")
                uyarilar.append(f"KESİN DİL KULLANMA — SENARYOLAR ÇELİŞİYOR (UETS): İşlem yalnız {gec} göre süre "
                    f"kaçırmış görünüyor; {sureli} göre süresindedir (7201 m.7/a — ulaşma+5. gün karinesi hukuken "
                    "GEÇERLİ tebliğ tarihidir). Kesin/net 'süre kaçırılmıştır' dili YALNIZ her iki senaryo da aşıldığında "
                    "kullanılır; aksi hâlde 'tebliğ-sayılma tarihini (ulaşma tarihini) UETS kaydından teyit et' şerhiyle "
                    "ara tespit yazılır — teyide göre kesinleşir.")
            else:
                rapor.append(">>> TESPİT: İşlem SÜRESİ İÇİNDE yapılmıştır (her iki UETS senaryosunda da).")
        elif fark <= 0:
            rapor.append(f">>> TESPİT: İşlem SÜRESİ İÇİNDE yapılmıştır ({'son günde' if fark==0 else f'son günden {-fark} gün önce'}).")
            # v0.5.18 — süresinde görünen işlem başka bir okumada geç olabilir: GÖRÜNÜR yaz
            # (kesin dil değil; ikincil itiraz malzemesi — karar avukatın).
            _alt = bilgi.get("alt_son")
            if _alt is not None and _alt < islem:
                rapor.append(f"    ⓘ Rejim teyitsiz/tartışmalı: diğer okumada son gün {_alt.isoformat()} — "
                             "işlem ona göre GEÇ; yalnız ARA TESPİT / ikincil süre itirazı malzemesidir.")
            _ih = bilgi.get("ihtiyat_son")
            if _ih is not None and _ih < islem:
                rapor.append(f"    ⓘ Eski daire uygulamasına göre (tatil bitiminden üç gün: {_ih.isoformat()}) "
                             "geç sayılabilirdi; YCGK E.2021/319 K.2022/846 ve AYM Ramazan Seçen uyarınca "
                             "SÜRESİNDEDİR — bu farka dayalı süre itirazı en fazla ikincildir.")
        elif _kesin_dil_engelleri(islem, son, bilgi, fark, bilgi):
            # v0.5.18 — KESİN DİL KAPISI: şartlardan biri eksikse ARA TESPİT.
            _ara_tespit_yaz(rapor, uyarilar, son, fark,
                            _kesin_dil_engelleri(islem, son, bilgi, fark, bilgi))
        else:
            rapor.append(f">>> TESPİT — SÜRE KAÇIRILMIŞTIR: İşlem, sürenin dolduğu {son.isoformat()} tarihinden")
            rapor.append(f"    {fark} GÜN SONRA yapılmıştır. Süresinden sonra yapılan işlem usul hukuku")
            rapor.append(f"    bakımından sonuç doğurmaz; süreye ilişkin itiraz/ret talebi DERHÂL ileri sürülür.")
            uyarilar.append("SÜRE KAÇIRMA TESPİTİ — ÇALIŞMAYA EKLE (net/kesin dil): Karşı tarafa ait süre kaçırması "
                "GİZLİ CEPHANELİKTE SAKLANMAZ — bu bir savunma değil AKTİF usul itirazıdır, derhâl ve açıkça ileri "
                "sürülür (ör. istinaf/temyizin SÜREDEN REDDİ; süresinde verilmeyen cevapta HMK m.128 inkâr sonucu; "
                "süresinde sürülmeyen ilk itirazın m.117/2 dinlenmemesi; itiraz edilmeyen bilirkişi raporu m.281). "
                "KESİNLİK ŞARTI: net/kesin dil ancak tebliğ tarihi BELGELİ (tebliğ şerhi/UYAP kaydı/mazbata) ise "
                "kullanılır; teyitsizse tespit 'tebliğ şerhinin teyidi kaydıyla' yazılır. Hesap dayanağı rapor "
                "satırlarındadır (HMK m.92/93/104) — bu satırlar dilekçedeki süre paragrafının iskeletidir (oa-dilekce).")
    print("="*66); print("  SÜRE HESABI — KARAR-MALZEMESİ, NİHAİ TEYİT KULLANICININDIR"); print("="*66)
    if _KURAL_TABLO_YOK:
        # B-21 (v0.5.14) — eskiden bu düşüş SESSİZDİ: kullanıcı "teyit BOŞ" satırı
        # ile kaynak metnindeki "(MCP teyit ...)" şerhini aynı ekranda görüp hangisine
        # inanacağını bilemiyordu. Artık düşüşün SEBEBİ ilk satırda yazılı.
        print("⚠ KURAL TABLOSU: gömülü (fallback) tabloya düşüldü — sebep: %s"
              % (_KURAL_TABLO_SEBEP or "bilinmiyor"))
        print("  Gömülü tablo ile sure_kurallari.json BİREBİR aynı tutulur (test kilidi:")
        print("  test_v0514_sure.py::test_B21_gomulu_ve_json_kural_tablosu_BIREBIR_ayni),")
        print("  ancak JSON güncellemeleri bu koşuda GÖRÜLMEMİŞTİR — dosyayı onar.")
    if kaynak:
        print(f"Kural                 : {a.kural}  →  {kaynak}")
        teyit = KURAL_TEYIT.get(a.kural, "")
        _kaynak_adi = "gömülü tablo" if _KURAL_TABLO_YOK else "sure_kurallari.json"
        print(f"Kural kaynağı/teyit   : {_kaynak_adi}; mcp_teyit_tarihi = "
              f"{teyit or 'BOŞ → kuralı resmî kaynaktan/Mevzuat MCP ile TEYİT ET (süreler değişebilir)'}")
    if a.tur == "usul" and birim == "isgunu":
        _tur_notu = "usul — İŞ GÜNÜ sayımı; adli tatil UZATMASI uygulanmaz (tatiller zaten atlanır)"
    elif a.tur == "usul":
        _tur_notu = "usul — adli tatil rejimi aşağıda"
    else:
        _tur_notu = "maddi hukuk — zamanaşımı/hak düşürücü, adli tatil uygulanmaz"
    print(f"Süre türü             : {a.tur}  ({_tur_notu})")
    _kural_kolu = kural_kolu(a.kural) if a.kural else None
    print(f"Yargı kolu            : {a.yargi}"
          + (f"  (kuralın kendi kolu: {_kural_kolu})" if _kural_kolu and _kural_kolu != a.yargi else ""))
    if a.tur == "usul" and birim != "isgunu" and bilgi.get("rejim"):
        # v0.5.18 (Y-01) — rejimin NEREDEN geldiği görünür: kural kaydı mı, --yargi mı.
        print(f"Adli tatil rejimi     : {REJIM_ETIKET[bilgi['rejim']]} — kaynak: "
              + ("kural kaydı" if bilgi.get("rejim_kaynagi") == "kural" else "--yargi " + a.yargi)
              + ("" if bilgi.get("rejim_teyitli") else " · TEYİT BEKLİYOR (temkinli: erken tarih)")
              + (" · TÜRETİLDİ (%s)" % bilgi["rejim_turetildi"] if bilgi.get("rejim_turetildi") else ""))
    for s in rapor: print(s)
    print("\n--- UYARILAR (deterministik DEĞİL — elle teyit) ---")
    for u in uyarilar: print(f"  ! {u}")
    print("="*66)
    # ── E4a SÜRE BAĞI (v0.5.8.5): hesap çıktısı üretilirken flag OTOMATİK yazılır ──
    # Boşluk sahada ölçüldü: hesap yapılıyor ama sureler.json'a işleme adımı (elle
    # oa_hafiza sure-flag) atlanıyordu → nöbetçi hiç görmüyordu. Artık <kok>/_oa
    # varsa son gün deftere İN-PROCESS işlenir; --uets'te karine senaryosu da ayrı
    # kayıt olur (kayıpsızlık: iki son gün de görünür). Yazım BLOKLAMAZ: defter
    # hatası hesabı düşürmez, açıkça raporlanır.
    if a.flagsiz:
        print("ⓘ --flagsiz: otomatik sureler.json flag yazımı istekle KAPALI.")
    else:
        # v0.5.18 — şüpheli tebliğde kayıt "İHTİYAT HEDEFİ" etiketiyle yazılır (tek kesin
        # tarih yok); CMK tatil-içi tebliğde eski daire uygulamasına göre ERKEN tarih ayrı
        # kayıt olur (nöbetçi önce onu uyarır; avukat bilinçli kararla --iptal eder);
        # tatil takvimi eksik yıl kayda işlenir (nöbetçi işaretler — Y-08).
        _on_ek = "[İHTİYAT HEDEFİ — ŞÜPHELİ TEBLİĞ] " if bilgi.get("supheli") else ""
        _acik_taban = _on_ek + (a.aciklama or ((kaynak or f"{miktar} {birim} süre") + " — son gün"))
        _adaylar = [(son.isoformat(), (_on_ek + a.aciklama) if a.aciklama else None)]
        if bilgi.get("ihtiyat_son") is not None:
            _adaylar.append((bilgi["ihtiyat_son"].isoformat(),
                             _acik_taban + " [ihtiyat planı: eski daire uygulaması, tatil bitiminden "
                             "itibaren üç gün; YCGK 2022/846'ya göre son gün %s]" % son.isoformat()))
        if son_karine is not None:
            _adaylar.append((son_karine.isoformat(),
                             _acik_taban + " [UETS karine: ulaşma+5. gün]"))
        _te = sorted(set(bilgi.get("takvim_eksik") or []) | set(bilgi_k.get("takvim_eksik") or []))
        try:
            _yeni, _bilgi = _sure_flagini_yaz(a.kok, _adaylar, _acik_taban, a.kural, a.tur,
                                              {"takvim_eksik": _te} if _te else None)
        except Exception as _e:   # yazım hesabı ASLA düşürmez — açık rapor, sessiz değil
            print(f"UYARI: süre flag'i yazılamadı ({_e}) — oa_hafiza.py sure-flag ile ELLE işle.")
        else:
            if _yeni is None:
                print(f"ⓘ SÜRE BAĞI: {_bilgi}; dava kökünde `--kok <klasör>` ile koş "
                      "ya da oa_hafiza.py sure-flag ile elle işle.")
            elif _yeni:
                print(f"SÜRE FLAG'İ OTOMATİK İŞLENDİ ({', '.join(_yeni)}): {_bilgi}")
                print("(sure_nobetci.py --kok . bu deftere göre GEÇMİŞ/YAKLAŞAN son günü tarar.)")
            else:
                print(f"ⓘ SÜRE BAĞI: aynı son gün + açıklama defterde ZATEN kayıtlı — tekrar eklenmedi ({_bilgi}).")
    print("NOT: event_create/reminder_create ÇAĞRILMAZ; dış takvim/hatırlatıcı eşgüdümü AVUKAT")
    print("tarafından ELLE yapılır — araç yoksa/kurulamıyorsa bu açıkça raporlanır (disk pasiftir,")
    print("kimseyi dürtmez). _oa/dosya.md süre özetini de güncelle.")
    if a.json:
        # v0.5.16 / I5 — tarih kuralında makine-okur özet (insan-okur rapor korunur;
        # aşama kuralıyla simetrik alan adları: tur / kural / son_gun).
        def _iso(g):
            return g.isoformat() if g is not None else None
        print("[JSON] " + json.dumps(
            {"tur": a.tur, "kural": a.kural, "yargi": a.yargi, "teblig": teblig.isoformat(),
             "son_gun": son.isoformat(),
             "son_gun_uets_karine": son_karine.isoformat() if son_karine else None,
             # v0.5.18 — rejim, temkinli/ihtiyat tarihleri ve başlangıç kapısı alanları
             "adli_tatil_rejimi": bilgi.get("rejim"),
             "rejim_teyitli": bilgi.get("rejim_teyitli"),
             "alternatif_son_gun": _iso(bilgi.get("alt_son")),
             "ihtiyat_son_gun": _iso(bilgi.get("ihtiyat_son")),
             "plan_son_gun": _iso(bilgi.get("plan_son")),
             "takvim_eksik": sorted(set(bilgi.get("takvim_eksik") or [])
                                    | set(bilgi_k.get("takvim_eksik") or [])),
             "baslangic_kaniti": getattr(a, "baslangic_kaniti", None),
             "teblig_durumu": getattr(a, "teblig_durumu", None),
             "kesin_tarih": not bilgi.get("supheli"),
             "uyarilar": uyarilar}, ensure_ascii=False))

if __name__=="__main__":
    try: main()
    except BrokenPipeError: sys.stderr.close()
