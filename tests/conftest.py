# -*- coding: utf-8 -*-
"""Ortak pytest altyapısı.

Tek işi var: GERÇEK UDF yazıcısının bu ortamda bulunup bulunmadığını HER
KOŞUDA GÖRÜNÜR kılmak ve teslim-zinciri testlerine doğru argümanı vermek.
Gerekçenin tamamı `tests/oa_udf_ortam.py` başındadır.
"""
import pytest

import oa_udf_ortam


def pytest_report_header(config):
    """Sessiz atlama YASAK — durum her koşunun ilk satırlarında basılır."""
    return oa_udf_ortam.durum_metni()


@pytest.fixture(scope="session")
def udf_arglari():
    """teslim_paketi.py'ye eklenecek argümanlar.

    Yazıcı VARSA boş liste — avukatın kendi makinesinde test bugünkünün
    AYNISIDIR, TAM zincir (gerçek .udf üretimi dâhil) koşar.
    Yazıcı YOKSA ['--udf-yok'] — zincir mantığı yine uçtan uca denetlenir,
    yalnız son adım BİLİNÇLİ ve makbuza YAZILARAK atlanır.
    """
    return [] if oa_udf_ortam.gercek_udf_yazici_var() else ["--udf-yok"]
