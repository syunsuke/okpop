from pathlib import Path

from nicegui import run, ui

from okpop.app import actions

status = actions.get_database_status()

latest_archive: Path | None = None
custom_archive: Path | None = None


async def update_database():
    """データベースを更新する。"""

    update_button.disable()
    update_progress.visible = True

    ui.notify(
        "データベースの更新を開始します"
    )

    try:
        await run.io_bound(
            actions.update_database
        )

        status = actions.get_database_status()

        suikei_label.set_text(
            f"推計人口：{status['suikei']}"
        )

        kubun_label.set_text(
            "年齢区分："
            f"{status['population_age5_v002']}"
        )

        census_label.set_text(
            f"国勢調査：{status['census']}"
        )

        hosei_label.set_text(
            f"修正人口：{status['hosei']}"
        )

        ui.notify(
            "データベースの更新が完了しました",
            type="positive",
        )

    except Exception as e:
        ui.notify(
            f"更新に失敗しました: {e}",
            type="negative",
        )

    finally:
        update_progress.visible = False
        update_button.enable()


async def get_latest_report():
    """最新のレポートZIPを取得する。"""

    global latest_archive

    report_button.disable()
    report_progress.visible = True
    latest_download_button.visible = False

    ui.notify(
        "最新レポートを確認しています"
    )

    try:
        latest_archive = await run.io_bound(
            actions.get_latest_report_archive
        )

        latest_report_result.set_text(
            f"最新レポート：{latest_archive.name}"  # pyright: ignore[reportOptionalMemberAccess]
        )

        latest_download_button.visible = True

        ui.notify(
            "最新レポートを取得しました",
            type="positive",
        )

    except Exception as e:
        ui.notify(
            f"レポート取得に失敗しました: {e}",
            type="negative",
        )

    finally:
        report_progress.visible = False
        report_button.enable()


async def get_report_for_date():
    """指定した年月のレポートZIPを取得する。"""

    global custom_archive

    year = int(year_input.value)  # pyright: ignore[reportArgumentType]
    month = int(month_input.value)  # pyright: ignore[reportArgumentType]

    custom_report_button.disable()
    custom_report_progress.visible = True
    custom_download_button.visible = False

    ui.notify(
        f"{year}年{month}月のレポートを確認しています"
    )

    try:
        custom_archive = await run.io_bound(
            actions.create_report_archive_for_date,
            year,
            month,
        )

        custom_report_result.set_text(
            f"指定年月レポート：{custom_archive.name}"  # pyright: ignore[reportOptionalMemberAccess]
        )

        custom_download_button.visible = True

        ui.notify(
            "指定年月のレポートを取得しました",
            type="positive",
        )

    except Exception as e:
        ui.notify(
            f"レポート取得に失敗しました: {e}",
            type="negative",
        )

    finally:
        custom_report_progress.visible = False
        custom_report_button.enable()


def download_latest_report():
    """最新レポートZIPをダウンロードする。"""

    if latest_archive is not None:
        ui.download(latest_archive)


def download_custom_report():
    """指定年月レポートZIPをダウンロードする。"""

    if custom_archive is not None:
        ui.download(custom_archive)


# --------------------------------------------------
# Header
# --------------------------------------------------

ui.label(
    "🐙 OKPOP"
).classes(
    "text-4xl font-bold"
)

ui.label(
    "大阪府人口データベース"
).classes(
    "text-xl"
)


# --------------------------------------------------
# Database
# --------------------------------------------------

ui.separator()

ui.label(
    "データベースの状態"
).classes(
    "text-2xl font-bold"
)

suikei_label = ui.label(
    f"推計人口：{status['suikei']}"
)

kubun_label = ui.label(
    "年齢区分："
    f"{status['population_age5_v002']}"
)

census_label = ui.label(
    f"国勢調査：{status['census']}"
)

hosei_label = ui.label(
    f"修正人口：{status['hosei']}"
)

update_button = ui.button(
    "データベース更新",
    on_click=update_database,
)

with ui.row() as update_progress:
    ui.spinner(size="lg")
    ui.label("更新中...")

update_progress.visible = False


# --------------------------------------------------
# Report
# --------------------------------------------------

ui.separator()

ui.label(
    "レポート"
).classes(
    "text-2xl font-bold"
)


# --------------------------------------------------
# Latest report
# --------------------------------------------------

ui.label(
    "最新レポート"
).classes(
    "text-lg font-bold"
)

report_button = ui.button(
    "最新レポートを取得",
    on_click=get_latest_report,
)

with ui.row() as report_progress:
    ui.spinner(size="lg")
    ui.label(
        "最新レポートを確認中..."
    )

report_progress.visible = False

latest_report_result = ui.label()

latest_download_button = ui.button(
    "ZIPをダウンロード",
    on_click=download_latest_report,
)

latest_download_button.visible = False


# --------------------------------------------------
# Report for specified date
# --------------------------------------------------

ui.label(
    "指定年月のレポート"
).classes(
    "text-lg font-bold"
)

with ui.row():
    year_input = ui.number(
        label="年",
        value=2025,
        min=2000,
        max=2100,
        step=1,
    )

    month_input = ui.number(
        label="月",
        value=9,
        min=1,
        max=12,
        step=1,
    )

custom_report_button = ui.button(
    "指定年月でレポートを取得",
    on_click=get_report_for_date,
)

with ui.row() as custom_report_progress:
    ui.spinner(size="lg")
    ui.label(
        "指定年月のレポートを確認中..."
    )

custom_report_progress.visible = False

custom_report_result = ui.label()

custom_download_button = ui.button(
    "ZIPをダウンロード",
    on_click=download_custom_report,
)

custom_download_button.visible = False


ui.run()
