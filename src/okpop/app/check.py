"""OKPOP: ソース採用状況とレポート充足状況の確認（読み取り専用）。"""

import sqlite3
from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path

from nicegui import ui

from okpop.paths import DB_PATH
from okpop.area import AREA_NAME_V002_COL_NAME

# 旧形式93地域だけにある集計地域。レポート充足チェックから除外。
EXCLUDED_REPORT_AREAS = {
    '大阪府市部',
    '大阪府郡部',
    '三島郡',
    '豊能郡',
    '泉北郡',
    '泉南郡',
    '南河内郡',
}

SOURCES = ('census', 'hosei', 'suikei')
SOURCE_NAMES = {'census': '国調', 'hosei': '補正', 'suikei': '推計'}
AGE_BANDS = ('00_04', '05_09', '10_14', '15_19', '20_24', '25_29',
             '30_34', '35_39', '40_44', '45_49', '50_54', '55_59',
             '60_64', '65_69', '70_74', '75_79', '80_84', '85plus')
SEXES = ('total', 'male', 'female')
BASIC = ('total_population', 'male_population', 'female_population', 'total_households')
CHANGES = ('monthly_population_change', 'monthly_natural_change',
           'births_monthly', 'deaths_monthly', 'monthly_net_migration')
AGE = tuple(f'{sex}_age_{band}' for sex in SEXES for band in AGE_BANDS)


def previous_month(month: str) -> str:
    year, number = map(int, month.split('-'))
    return f'{year - 1:04d}-12' if number == 1 else f'{year:04d}-{number - 1:02d}'


def inspect_database(db_path: Path) -> tuple[list[dict], dict[str, list[dict]], str]:
    """86地域のレポート充足状況を月別に集計する（DBは読み取り専用）。"""
    if not db_path.is_file():
        return [], {}, f'DBファイルがありません: {db_path}'

    with closing(sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        objects = {r['name'] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
        required = {'view_excel_report_data', 'suikei'}
        if required - objects:
            return [], {}, '不足しているテーブル/View: ' + ', '.join(sorted(required - objects))

        columns = {r['name'] for r in conn.execute('PRAGMA table_info("view_excel_report_data")')}
        required_columns = {'observation_date', 'area_name', 'source'} | set(BASIC + CHANGES + AGE)
        if required_columns - columns:
            return [], {}, 'レポートViewの列が不足: ' + ', '.join(sorted(required_columns - columns))

        areas = set(AREA_NAME_V002_COL_NAME)
        suikei_keys = {(r['observation_date'], r['area_name']) for r in conn.execute(
            'SELECT observation_date, area_name FROM suikei') if r['area_name'] in areas}

        months: dict[str, dict] = defaultdict(lambda: {
            'dates': set(), 'seen': Counter(), 'basic': set(), 'change': set(),
            'age': set(), 'sources': Counter(), 'details': [],
        })
        for r in conn.execute('SELECT * FROM view_excel_report_data'):
            date, area = r['observation_date'], r['area_name']
            month = str(date)[:7]
            m = months[month]
            m['dates'].add(date)
            if area not in areas:
                m['details'].append({'area': area, 'issue': '対象外地域がレポートに含まれる'})
                continue
            key = (date, area)
            m['seen'][key] += 1
            m['sources'][r['source']] += 1
            if all(r[c] is not None for c in BASIC):
                m['basic'].add(key)
            if all(r[c] is not None for c in CHANGES):
                m['change'].add(key)
            if all(r[c] is not None for c in AGE):
                m['age'].add(key)

        latest_suikei = conn.execute(
            'SELECT MAX(substr(observation_date, 1, 7)) FROM suikei').fetchone()[0]
        # 基本Viewの欠落月を発見できるよう、推計データが存在する月も検査対象に含める。
        for date, area in suikei_keys:
            months[str(date)[:7]]['dates'].add(date)

        # 同月に複数の観測日がある場合も、その月の各日付ごとに86地域を期待する。
        expected_by_month = {
            month: {(date, area) for date in m['dates'] for area in areas}
            for month, m in months.items()
        }

        def complete_age(month: str) -> bool:
            keys = expected_by_month.get(month, set())
            return bool(keys and keys <= months[month]['age'])

        previous_complete = complete_age(previous_month(latest_suikei)) if latest_suikei else False
        rows = []
        details = {}
        for month in sorted(months, reverse=True):
            m = months[month]
            expected = expected_by_month[month]
            total = len(expected)
            existing = set(m['seen'])
            basic = len(expected & m['basic'])
            age = len(expected & m['age'])
            change_required = expected & suikei_keys
            change = len(change_required & m['change'])
            duplicate_keys = {k for k, n in m['seen'].items() if n > 1}
            pending = (month == latest_suikei and previous_complete and age == 0)
            has_basic_problem = (existing != expected or basic < total or bool(duplicate_keys)
                                 or bool(m['details']))
            if has_basic_problem or change < len(change_required):
                status = '要確認'
            elif pending:
                status = '公表待ち（推定）'
            elif age < total:
                status = '要確認'
            else:
                status = '正常'

            sources = '＋'.join(f'{SOURCE_NAMES.get(s, s)}{m["sources"][s]}'
                               for s in SOURCES if m['sources'][s]) or '—'
            rows.append({
                'month': month, 'areas': f'{len(existing)}/{total}',
                'sources': sources,
                'basic': f'{basic}/{total}',
                'change': f'{change}/{len(change_required)}' if change_required else '対象外',
                'age': f'{age}/{total}',
                'status': status,
            })
            problems = list(m['details'])
            for date, area in sorted(expected - existing):
                problems.append({'area': area, 'issue': f'{date}: 地域データなし'})
            for date, area in sorted(duplicate_keys):
                problems.append({'area': area, 'issue': f'{date}: 重複 {m["seen"][(date, area)]}件'})
            for date, area in sorted(expected & existing):
                missing = []
                if (date, area) not in m['basic']:
                    missing.append('基本人口')
                if (date, area) in change_required and (date, area) not in m['change']:
                    missing.append('月次増減')
                if (date, area) not in m['age']:
                    missing.append('5歳階級')
                if missing:
                    problems.append({'area': area, 'issue': f'{date}: ' + '・'.join(missing) + '不足'})
            details[month] = problems
        return rows, details, ''


COLUMNS = [
    {'name': 'month', 'label': '年月', 'field': 'month', 'sortable': True},
    {'name': 'areas', 'label': '地域', 'field': 'areas'},
    {'name': 'sources', 'label': '採用元', 'field': 'sources'},
    {'name': 'basic', 'label': '基本人口', 'field': 'basic'},
    {'name': 'change', 'label': '月次増減', 'field': 'change'},
    {'name': 'age', 'label': '5歳階級', 'field': 'age'},
    {'name': 'status', 'label': '判定', 'field': 'status'},
]
DETAIL_COLUMNS = [
    {'name': 'area', 'label': '地域', 'field': 'area', 'sortable': True},
    {'name': 'issue', 'label': '確認内容', 'field': 'issue'},
]


def render_check() -> None:
    with ui.column().classes('w-full max-w-7xl mx-auto p-6 gap-4'):
        ui.label('OKPOP レポートViewチェック').classes('text-2xl font-bold')
        ui.label('対象86地域・読み取り専用。行をクリックすると、その月の不足項目を表示します。').classes('text-gray-600')
        message = ui.label().classes('text-red-600')
        with ui.row().classes('items-center gap-4'):
            ui.button('再読み込み', icon='refresh', on_click=lambda: refresh())
            summary = ui.label()
        table = ui.table(columns=COLUMNS, rows=[], row_key='month', pagination=24).classes('w-full')
        ui.separator()
        detail_title = ui.label('月を選択してください').classes('text-lg font-semibold')
        detail_table = ui.table(columns=DETAIL_COLUMNS, rows=[], row_key='id', pagination=20).classes('w-full')
        ui.label('「公表待ち」はDB内の収録状況からの推定であり、公式公表日の確認ではありません。').classes('text-sm text-gray-500')
        cache: dict[str, list[dict]] = {}

        def show_month(month: str) -> None:
            problems = cache.get(month, [])
            detail_title.set_text(f'{month} の確認内容（{len(problems)}件）' if problems
                                  else f'{month}：不足・重複なし')
            detail_table.rows = [dict(id=i, **r) for i, r in enumerate(problems)]
            detail_table.update()

        table.on('rowClick', lambda e: show_month(e.args[1]['month']))

        def refresh() -> None:
            message.set_text('')
            try:
                rows, details, error = inspect_database(DB_PATH)
                message.set_text(error)
                table.rows = rows
                cache.clear()
                cache.update(details)
                bad = sum(r['status'] == '要確認' for r in rows)
                summary.set_text(f'{len(rows)}か月中、要確認 {bad}か月')
                detail_title.set_text('月を選択してください')
                detail_table.rows = []
            except (sqlite3.Error, OSError, ValueError) as exc:
                message.set_text(f'読み込みエラー: {exc}')
                table.rows = []
                detail_table.rows = []
            table.update()
            detail_table.update()

        refresh()


