# -*- coding: utf-8 -*-
"""v0.5.17.1 — B-23 kilidi: eklentinin KENDİLİĞİNDEN İLAN ETTİĞİ MCP sunucuları.

2026-10-06 ölçümü: v0.5.7.4'te ilan edilen yedek sunucunun (`yargi-mcp-yedek`) alan adı
ilgisiz bir sunucuya çözülüp başka bir alan adına verilmiş sertifika sunuyordu; kaynak depo
herkese açık değildi. Eklentinin ilan ettiği her uç nokta avukatın sorgularını okur ve
"içtihat" diye metin döndürür — bu yüzden ilan listesi ancak bilinçli bir kararla genişler.

2026-10-15 AVUKAT KARARI (hibrit teyit kanalı; `tests/test_teyit_kanali.py`): izinli ilan
listesi BOŞALDI — eklenti HİÇBİR MCP sunucusu ilan etmez; içtihat/mevzuat teyidinin kanıtı
resmî portalın adresi (beyaz liste) + diske inmiş tam metindir. İki eski test o kararla
çevrildi, gerekçesi burada:
  - `test_ilan_edilen_sunucular_yalniz_izinli_liste` (tek izinli sunucu + https şartı) →
    `test_izinli_ilan_listesi_bos_ve_plugin_json_anahtari_hic_yok`: `IZINLI = {}`; `plugin.json`
    `mcpServers` anahtarını HİÇ taşımaz (boş sözlük bile ikinci bir ilan kapısı olurdu).
    İlanın TAM kapısı (marketplace.json, `.mcp.json`, manifestlerde alan adı) test_teyit_kanali
    (e) `test_eklenti_hicbir_mcp_sunucusu_ilan_etmez`tedir — burada YİNELENMEZ (çift kilit
    yok; bu dosya yalnız B-23'ün "izinli liste" sorusunu taşır). Eski `test_ikinci_ilan_kapisi_yok`
    aynı gerekçeyle o teste devredildi.
  - `test_kutuk_sozlugu_yedek_adlari_damga_disiplininde_tutar` SİLİNDİ: üçüncü taraf araç adları
    `oa_hafiza` sözlüğünden çıkarıldı (test_teyit_kanali (c)); damga disiplini artık araç adına
    değil [G7] resmî adres kapısına dayanır (dayanak kaydının adresi yoksa teslim engeli).
Kalan üç test B-23 dersinin kendisidir: sahipsiz adres tarihçe dışında geçmez; `oa-ictihat`
otomatik yedeğe geçmeyi öğretmez; eski yedek proje "alternatif" diye önerilmez (STATUS.md dahil —
`test_kanal_bagimsiz_metin` STATUS'u tarihli bölümleri yüzünden taramaz, bu yüzden burada durur).
Ağ erişimi YOK: yalnız depo içeriği denetlenir.
"""
import json
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parents[1]
EKLENTI = KOK / "plugins" / "ortak-avukat"
IZINLI = {}   # 2026-10-15: eklenti hiçbir MCP sunucusu ilan etmez
SAHIPSIZ = "yargimcp.surucu.dev"
# Adres yalnız TARİHÇE kayıtlarında geçebilir (ne olduğunu ve neden kaldırıldığını anlatır)
TARIHCE = {"CHANGELOG.md", "degisiklik-gunlugu.md"}


def _json(yol):
    return json.loads(yol.read_text(encoding="utf-8"))


def test_izinli_ilan_listesi_bos_ve_plugin_json_anahtari_hic_yok():
    """B-23'ün izinli listesi 2026-10-15'ten beri boştur; `plugin.json` `mcpServers` anahtarını
    hiç taşımaz. Tam ilan kapısı: tests/test_teyit_kanali.py (e)."""
    pj = _json(EKLENTI / ".claude-plugin" / "plugin.json")
    assert "mcpServers" not in pj, "plugin.json mcpServers anahtarı taşıyor: %r" % pj.get("mcpServers")
    assert {ad: s.get("url") for ad, s in (pj.get("mcpServers") or {}).items()} == IZINLI


def test_sahipsiz_adres_tarihce_disinda_gecmiyor():
    bulunan = []
    for yol in list(EKLENTI.rglob("*")) + [KOK / "README.md", KOK / "STATUS.md", KOK / "docs"]:
        if yol.is_dir() and yol.name == "docs":
            adaylar = [y for y in yol.rglob("*") if y.is_file()]
        elif yol.is_file():
            adaylar = [yol]
        else:
            continue
        for y in adaylar:
            if y.name in TARIHCE or y.suffix.lower() not in {".md", ".json", ".py", ".txt", ".yml", ".yaml"}:
                continue
            if SAHIPSIZ in y.read_text(encoding="utf-8", errors="replace"):
                bulunan.append(str(y.relative_to(KOK)))
    assert bulunan == []


def test_ictihat_parcasi_otomatik_yedege_gecmeyi_ogretmiyor():
    """Resmî portala ulaşılamayınca başka sunucuya/özel siteye OTOMATİK GEÇİLMEZ, çıktıya
    'teyit YAPILAMADI' yazılır (2026-10-15'te 'Pro düşerse' → 'resmî portala ulaşılamazsa')."""
    sk = (EKLENTI / "skills" / "oa-ictihat" / "SKILL.md").read_text(encoding="utf-8")
    assert not re.search(r"yedek\s+sunucu\w*\s+geç(?!ilmez|İLMEZ)", sk, re.I), "yedeğe geçmeyi öğretiyor"
    assert "OTOMATİK GEÇİLMEZ" in sk and "teyit YAPILAMADI" in sk


def test_sahipsiz_yedek_proje_alternatif_diye_onerilmiyor():
    """Bağımsız inceleme (D): ilan kaldırılsa da belgeler kaynak deposu artık herkese açık
    olmayan yedek projeyi "alternatif" diye öneriyordu — kullanıcıyı ele geçirilebilir bir
    kanala yönlendirmek. Proje bağlantısı yalnız tarihçe kayıtlarında geçebilir."""
    proje = "github.com/saidsurucu/yargi-mcp"
    bulunan = []
    for yol in [KOK / "README.md", KOK / "SOZLUK.md", KOK / "STATUS.md"] + list(EKLENTI.rglob("*.md")):
        if yol.is_file() and yol.name not in TARIHCE and proje in yol.read_text(encoding="utf-8", errors="replace"):
            bulunan.append(str(yol.relative_to(KOK)))
    assert bulunan == []
