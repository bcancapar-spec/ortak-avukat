# -*- coding: utf-8 -*-
"""v0.5.18 — B-23 kilidi: eklentinin KENDİLİĞİNDEN İLAN ETTİĞİ MCP sunucuları.

2026-10-06 ölçümü: v0.5.7.4'te ilan edilen yedek sunucunun (`yargi-mcp-yedek`) alan adı
ilgisiz bir sunucuya çözülüp başka bir alan adına verilmiş sertifika sunuyordu; kaynak depo
herkese açık değildi. Eklentinin ilan ettiği her uç nokta avukatın sorgularını okur ve
"içtihat" diye metin döndürür — bu liste ancak bilinçli bir kararla (bu test güncellenerek)
genişleyebilir. Ağ erişimi YOK: yalnız depo içeriği denetlenir.
"""
import json
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parents[1]
EKLENTI = KOK / "plugins" / "ortak-avukat"
IZINLI = {"yargi-pro": "https://yargi.betaspacestudio.com/mcp"}
SAHIPSIZ = "yargimcp.surucu.dev"
# Adres yalnız TARİHÇE kayıtlarında geçebilir (ne olduğunu ve neden kaldırıldığını anlatır)
TARIHCE = {"CHANGELOG.md", "degisiklik-gunlugu.md"}


def _json(yol):
    return json.loads(yol.read_text(encoding="utf-8"))


def test_ilan_edilen_sunucular_yalniz_izinli_liste():
    sunucular = _json(EKLENTI / ".claude-plugin" / "plugin.json").get("mcpServers") or {}
    assert {ad: s.get("url") for ad, s in sunucular.items()} == IZINLI
    for s in sunucular.values():
        assert s.get("type") == "http" and s["url"].startswith("https://")


def test_ikinci_ilan_kapisi_yok():
    assert not (EKLENTI / ".mcp.json").exists()
    assert not (KOK / ".mcp.json").exists()
    for p in _json(KOK / ".claude-plugin" / "marketplace.json").get("plugins", []):
        assert "mcpServers" not in p


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
    sk = (EKLENTI / "skills" / "oa-ictihat" / "SKILL.md").read_text(encoding="utf-8")
    assert not re.search(r"yargi-mcp-yedek`?\s+sunucusuna\s+geç", sk)
    assert "OTOMATİK GEÇİLMEZ" in sk and "teyit YAPILAMADI" in sk


def test_kutuk_sozlugu_yedek_adlari_damga_disiplininde_tutar(tmp_path):
    """Sözlükten çıkarmak bu adları 'serbest araç' yapıp damga kapısını gevşetirdi."""
    import importlib.util
    yol = EKLENTI / "skills" / "oa-pipeline" / "scripts" / "oa_hafiza.py"
    sp = importlib.util.spec_from_file_location("oa_hafiza_b23", yol)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    assert {"search_bedesten_unified", "search_anayasa_unified"} <= m.ARAMA_ARACLARI
    assert {"get_bedesten_document_markdown", "get_anayasa_document_unified"} <= m.GETIR_ARACLARI
