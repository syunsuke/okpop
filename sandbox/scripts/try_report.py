from okpop import report


report.create_report(
    area_name="大阪市福島区",
    end_date="2026-08-01",
    output_path="sandbox/data/test_report.xlsx",
    template_path=(
        "assets/templates/"
        "populaiton_report_template_0001.xlsx"
    ),
    db_path="sandbox/data/test.sqlite",
)

print("sandbox/data/test_report.xlsx を作成しました")
