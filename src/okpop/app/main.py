from pathlib import Path
import sqlite3

from nicegui import run, ui

from okpop.app import actions
from okpop import database

TABLES = {
    "suikei": "推計人口",
    "population_age5_v002": "年齢区分",
    "census": "国勢調査",
    "hosei": "修正人口",
}


def get_date_ranges() -> dict[str, tuple[str | None, str | None]]:
    """各テーブルの最古・最新の観測日を取得する。"""
    with sqlite3.connect(database.DEFAULT_DB_PATH) as con:
        return {
            table: con.execute(
                f"SELECT MIN(observation_date), MAX(observation_date) FROM {table}"
            ).fetchone()
            for table in TABLES
        }


def format_date_range(value: tuple[str | None, str | None]) -> str:
    first, last = value
    return f"最古：{first or 'データなし'}\n最新：{last or 'データなし'}"


def get_population_areas() -> list[str]:
    with sqlite3.connect(database.DEFAULT_DB_PATH) as con:
        return [
            name for (name,) in con.execute(
                "SELECT DISTINCT area_name FROM suikei ORDER BY area_name"
            )
        ]


def get_population_overview(area_name: str) -> dict:
    """最新の人口と、直前の観測値との差を取得する。"""
    with sqlite3.connect(database.DEFAULT_DB_PATH) as con:
        rows = con.execute(
            """SELECT observation_date, total_population
               FROM suikei
               WHERE area_name = ? AND total_population IS NOT NULL
               ORDER BY observation_date DESC LIMIT 2""",
            (area_name,),
        ).fetchall()
    if not rows:
        return {"latest": None, "change": None, "date": None}
    return {
        "latest": rows[0][1],
        "change": rows[0][1] - rows[1][1] if len(rows) > 1 else None,
        "date": rows[0][0],
    }


def get_yearly_series(area_name: str, month: int, years: int) -> dict:
    """最新収録年までの指定月の年次データを取得する。"""
    with sqlite3.connect(database.DEFAULT_DB_PATH) as con:
        latest_year = con.execute(
            "SELECT MAX(CAST(substr(observation_date, 1, 4) AS INTEGER)) "
            "FROM suikei WHERE area_name = ?",
            (area_name,),
        ).fetchone()[0]
        if latest_year is None:
            return {"years": [], "series": [[], [], [], []]}
        rows = con.execute(
            """SELECT CAST(substr(observation_date, 1, 4) AS INTEGER),
                      total_population, male_population, female_population,
                      total_households
               FROM suikei
               WHERE area_name = ?
                 AND CAST(substr(observation_date, 6, 2) AS INTEGER) = ?
                 AND CAST(substr(observation_date, 1, 4) AS INTEGER) BETWEEN ? AND ?
               ORDER BY observation_date""",
            (area_name, month, latest_year - years + 1, latest_year),
        ).fetchall()
    values_by_year = {row[0]: row[1:] for row in rows}
    year_list = list(range(latest_year - years + 1, latest_year + 1))
    return {
        "years": [str(y) for y in year_list],
        "series": [
            [values_by_year.get(y, (None,) * 4)[i] for y in year_list]
            for i in range(4)
        ],
    }


def update_overview() -> None:
    area_name = area_select.value
    if not area_name:
        return
    data = get_population_overview(area_name)
    population_value.set_text(
        f"{data['latest']:,} 人" if data['latest'] is not None else "データなし"
    )
    change = data["change"]
    change_value.set_text(f"{change:+,} 人" if change is not None else "データなし")
    observation_label.set_text(f"最新観測日：{data['date'] or 'データなし'}")
    chart_data = get_yearly_series(area_name, int(month_select.value), int(years_select.value))
    population_chart.options["xAxis"]["data"] = chart_data["years"]
    for series, values in zip(population_chart.options["series"], chart_data["series"]):
        series["data"] = values
    population_chart.update()


def refresh_date_range_labels() -> None:
    date_ranges = get_date_ranges()
    for table, label in date_range_labels.items():
        label.set_text(format_date_range(date_ranges[table]))


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

        refresh_date_range_labels()
        update_overview()

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
# Pastel dashboard
# --------------------------------------------------

ui.add_head_html("""
<style>
  body { background: #FFF9F6; color: #354052; font-family: 'Noto Sans JP', sans-serif; }
  .ok-card { background: white; border: 1px solid #F1E9E8; border-radius: 24px;
             box-shadow: 0 9px 28px rgba(96, 78, 103, .07); }
  .ok-stat { border-radius: 20px; padding: 19px 20px; min-height: 112px; }
  .ok-title { color: #34364B; font-weight: 800; }
  .ok-muted { color: #7A8091; }
  .ok-btn { border-radius: 14px !important; font-weight: 700; padding: 9px 20px; }
  .ok-field { min-width: 125px; }
  .ok-progress { color: #7A8091; align-items: center; }
  .q-btn { text-transform: none; }
</style>
""")

ui.colors(primary='#A58AE5', secondary='#F4A9C6', accent='#71CDB8', positive='#4AAE90')

with ui.column().classes('w-full max-w-6xl mx-auto px-4 md:px-8 py-8 gap-7'):
    # Hero
    with ui.card().classes('w-full ok-card p-7 md:p-10').style(
        'background: linear-gradient(110deg, #FCE4ED 0%, #F1E8FF 52%, #E3F7F1 100%);'
    ):
        with ui.row().classes('items-center gap-3'):
            ui.label('🐙').classes('text-5xl')
            with ui.column().classes('gap-0'):
                ui.label('OKPOP').classes('text-4xl md:text-5xl ok-title tracking-wide')
                ui.label('Osaka Population Database').classes('text-sm ok-muted tracking-wide')
        ui.label('大阪府の人口データを、もっと楽しく、もっと便利に。').classes(
            'text-base md:text-lg mt-4 font-medium'
        )
        ui.label('データの更新からExcelレポートの作成まで、ここでまとめて操作できます。').classes(
            'text-sm ok-muted'
        )

    # Population dashboard
    ui.label('人口ダッシュボード').classes('text-2xl ok-title')
    areas = get_population_areas()
    default_area = "大阪府全市町村"

    with ui.card().classes('w-full ok-card p-6 gap-4'):
        with ui.row().classes('w-full items-center gap-4 flex-wrap'):
            area_select = ui.select(
                areas, value=default_area, label='地域', on_change=lambda e: update_overview()
            ).classes('w-64').props('outlined')
            month_select = ui.select(
                {i: f'{i}月' for i in range(1, 13)},
                value=10, label='比較する月', on_change=lambda e: update_overview()
            ).classes('w-32').props('outlined')
            years_select = ui.select(
                {5: '5年間', 10: '10年間'},
                value=5, label='比較期間', on_change=lambda e: update_overview()
            ).classes('w-32').props('outlined')

        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
            with ui.column().classes('ok-stat gap-2').style('background:#FDE7EF;'):
                ui.label('総人口（最新の観測日）').classes('font-bold')
                population_value = ui.label('—').classes('text-2xl font-bold')
            with ui.column().classes('ok-stat gap-2').style('background:#DFF6ED;'):
                ui.label('直前の観測値との差').classes('font-bold')
                change_value = ui.label('—').classes('text-2xl font-bold')
        observation_label = ui.label('').classes('text-sm ok-muted')
        ui.label('同月の年次推移：人口（左軸）・世帯数（右軸）').classes('text-lg ok-title')
        population_chart = ui.echart({
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['総人口', '男性', '女性', '世帯数'], 'top': 0},
            'grid': {'left': 75, 'right': 80, 'top': 60, 'bottom': 45},
            'xAxis': {'type': 'category', 'data': [], 'name': '年'},
            'yAxis': [
                {'type': 'value', 'name': '人口（人）', 'scale': True},
                {'type': 'value', 'name': '世帯数（世帯）', 'scale': True},
            ],
            'series': [
                {'name': name, 'type': 'line', 'yAxisIndex': axis,
                 'connectNulls': False, 'smooth': False,
                 'lineStyle': {'width': 3, 'color': color},
                 'itemStyle': {'color': color}, 'data': []}
                for name, color, axis in [
                    ('総人口', '#A58AE5', 0),
                    ('男性', '#69B9E5', 0),
                    ('女性', '#EE92B2', 0),
                    ('世帯数', '#59BFA6', 1),
                ]
            ],
        }).classes('w-full h-96')
        ui.label('※ 対象月にデータがない年は線が途切れます。').classes('text-xs ok-muted')

    if default_area is not None:
        update_overview()

    # Database date ranges
    with ui.column().classes('w-full gap-3'):
        ui.label('データベースの状態').classes('text-2xl ok-title')
        ui.label('各テーブルの最古・最新の観測日').classes('text-sm ok-muted')
        date_ranges = get_date_ranges()
        date_range_labels = {}
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full'):
            for table, title, color in [
                ('suikei', '🌸 推計人口', '#FDE7EF'),
                ('population_age5_v002', '🪻 年齢区分', '#E9E1FB'),
                ('census', '🍀 国勢調査', '#DFF6ED'),
                ('hosei', '☀️ 修正人口', '#FFF0C9'),
            ]:
                with ui.column().classes('ok-stat gap-2').style(f'background:{color};'):
                    ui.label(title).classes('font-bold')
                    date_range_labels[table] = ui.label(
                        format_date_range(date_ranges[table])
                    ).classes('text-sm whitespace-pre-line')

    # Update action
    with ui.card().classes('w-full ok-card p-6 gap-3'):
        with ui.row().classes('items-center gap-3'):
            ui.label('🔄').classes('text-2xl')
            ui.label('データベースを更新').classes('text-xl ok-title')
        ui.label('大阪府の公開データを取得し、SQLiteデータベースに反映します。').classes(
            'text-sm ok-muted'
        )
        update_button = ui.button('データベース更新', on_click=update_database, icon='sync').classes(
            'ok-btn text-white'
        ).style('background:#8CCFBD; color:#254A45;')
        with ui.row().classes('ok-progress gap-2') as update_progress:
            ui.spinner(size='md', color='accent')
            ui.label('更新中...')
        update_progress.visible = False

    ui.label('レポートセンター').classes('text-2xl ok-title')
    with ui.element('div').classes('grid grid-cols-1 md:grid-cols-2 gap-5 w-full'):
        # Latest report
        with ui.card().classes('ok-card p-6 gap-4 w-full'):
            ui.label('📊 最新レポート').classes('text-xl ok-title')
            ui.label('利用可能な最新月の全地域ExcelレポートをZIPで取得します。').classes(
                'text-sm ok-muted'
            )
            report_button = ui.button(
                '最新レポートを取得', on_click=get_latest_report, icon='auto_awesome'
            ).classes('ok-btn text-white').style('background:#A58AE5;')
            with ui.row().classes('ok-progress gap-2') as report_progress:
                ui.spinner(size='md')
                ui.label('最新レポートを確認中...')
            report_progress.visible = False
            latest_report_result = ui.label().classes('text-sm break-all')
            latest_download_button = ui.button(
                'ZIPをダウンロード', on_click=download_latest_report, icon='download'
            ).props('outline').classes('ok-btn')
            latest_download_button.visible = False

        # Custom report
        with ui.card().classes('ok-card p-6 gap-4 w-full'):
            ui.label('🗓️ 指定年月のレポート').classes('text-xl ok-title')
            ui.label('年と月を指定して、過去のレポートを作成できます。').classes(
                'text-sm ok-muted'
            )
            with ui.row().classes('gap-3 flex-wrap'):
                year_input = ui.number(
                    label='年', value=2025, min=2000, max=2100, step=1
                ).classes('ok-field')
                month_input = ui.number(
                    label='月', value=9, min=1, max=12, step=1
                ).classes('ok-field')
            custom_report_button = ui.button(
                '指定年月でレポートを取得',
                on_click=get_report_for_date,
                icon='calendar_month',
            ).classes('ok-btn').style('background:#F4B6CB; color:#623C52;')
            with ui.row().classes('ok-progress gap-2') as custom_report_progress:
                ui.spinner(size='md', color='secondary')
                ui.label('指定年月のレポートを確認中...')
            custom_report_progress.visible = False
            custom_report_result = ui.label().classes('text-sm break-all')
            custom_download_button = ui.button(
                'ZIPをダウンロード', on_click=download_custom_report, icon='download'
            ).props('outline').classes('ok-btn')
            custom_download_button.visible = False

    ui.label('OKPOP · Osaka Population Database').classes(
        'text-xs ok-muted self-center mt-3 mb-5'
    )

ui.run()
