"""Kiểm thử trạng thái lỗi dữ liệu thẩm định ML."""

from src import api


def test_ml_enrichment_reports_unavailable_when_oof_file_is_missing(monkeypatch, tmp_path):
    """Không được ngầm trả Value Gap 0% khi không thể đọc tệp OOF."""
    monkeypatch.setattr(api, "ML_OOF_FILE", tmp_path / "missing_oof.json")
    monkeypatch.setattr(api, "ML_METRICS_FILE", tmp_path / "missing_metrics.json")

    predictions, _, available = api.get_ml_enrichment()

    assert predictions == {}
    assert available is False
