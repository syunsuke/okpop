from datetime import date

from openpyxl import load_workbook

from okpop import report

DB_PATH = "sandbox/data/test.sqlite"
TEMPLATE_PATH = (
    "assets/templates/"
    "populaiton_report_template_0001.xlsx"
)


def test_read_report_data():
    df = report.read_report_data(
        area_name="大阪市福島区",
        start_date="2020-08-01",
        end_date="2025-08-01",
        db_path=DB_PATH,
    )

    assert not df.empty

    assert df["area_name"].eq(
        "大阪市福島区"
    ).all()

    # 新しい日付から古い日付への降順
    assert df["observation_date"].is_monotonic_decreasing

    # 2020年8月～2025年8月 = 61か月
    assert len(df) == 61

    assert df["observation_date"].iloc[0].strftime(
        "%Y-%m-%d"
    ) == "2025-08-01"

    assert df["observation_date"].iloc[-1].strftime(
        "%Y-%m-%d"
    ) == "2020-08-01"


def test_create_report(tmp_path):
    output_path = tmp_path / "report.xlsx"

    report.create_report(
        area_name="大阪市福島区",
        end_date="2025-08-01",
        output_path=output_path,
        template_path=TEMPLATE_PATH,
        db_path=DB_PATH,
    )

    # Excelファイルが作成された
    assert output_path.exists()

    wb = load_workbook(
        output_path,
        data_only=False,
    )

    ws_source = wb["source"]
    ws_report = wb["report"]

    # sourceの最初のデータが指定したend_date
    assert ws_source["A2"].value.date() == date(
        2025, 8, 1
    )

    # reportに作成日が入っている
    assert ws_report["BB1"].value.date() == date.today()

