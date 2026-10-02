from okpop import report


def test_read_report_data():
    df = report.read_report_data(
        area_name="大阪市福島区",
        start_date="2020-08-01",
        end_date="2025-08-01",
        db_path="sandbox/data/test.sqlite",
    )

    assert not df.empty

    assert df["area_name"].eq(
        "大阪市福島区"
    ).all()

    assert df["observation_date"].is_monotonic_increasing
