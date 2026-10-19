"""OKPOP dashboard: yearly same-month comparisons and age composition."""
import sqlite3
from contextlib import closing

import math
from nicegui import ui
from okpop import database

AGE_CODES = [f'{i:02d}_{i+4:02d}' for i in range(0, 85, 5)] + ['85plus']
AGE_LABELS = [f'{i}–{i+4}' for i in range(0, 85, 5)] + ['85+']
COLORS = {'male': '#5b9bd5', 'female': '#ed83ac'}


def read_dashboard(area: str, month: int, years: int) -> dict:
    """Read report view only; do not fill missing age observations."""
    with closing(sqlite3.connect(database.DEFAULT_DB_PATH)) as con:
        con.row_factory = sqlite3.Row
        last = con.execute(
            'SELECT MAX(CAST(substr(observation_date,1,4) AS INTEGER)) '
            'FROM view_excel_report_data WHERE area_name=? '
            'AND CAST(substr(observation_date,6,2) AS INTEGER)=?',
            (area, month),
        ).fetchone()[0]
        if last is None:
            return {'years': [], 'rows': [], 'latest': None}
        # Do not load unnecessary columns from the wide report view.
        age_columns = [f'{sex}_age_{age}' for sex in ('male', 'female') for age in AGE_CODES]
        columns = ['observation_date', 'total_population', 'male_population',
                   'female_population', 'total_households'] + age_columns
        sql = (f'SELECT {", ".join(columns)} FROM view_excel_report_data '
               'WHERE area_name=? AND CAST(substr(observation_date,6,2) AS INTEGER)=? '
               'AND CAST(substr(observation_date,1,4) AS INTEGER) BETWEEN ? AND ? '
               'ORDER BY observation_date')
        rows = [dict(r) for r in con.execute(sql, (area, month, last-years+1, last))]
    # The source view should contain one row per region and date; report duplicates explicitly.
    unique = {}
    for row in rows:
        key = row['observation_date'][:4]
        if key in unique:
            raise ValueError(f'{area} {key}年{month}月のデータが重複しています')
        unique[key] = row
    return {'years': [str(y) for y in range(last-years+1, last+1)],
            'rows': unique, 'latest': last}


def pyramid_values(row: dict):
    male = [row[f'male_age_{code}'] for code in AGE_CODES]
    female = [row[f'female_age_{code}'] for code in AGE_CODES]
    if any(x is None for x in male + female):
        return None
    total = sum(male) + sum(female)
    if not total:
        return None
    # Percentage of the total population represented by the age data.
    return [-100*x/total for x in male], [100*x/total for x in female]


def pyramid_axis_limit(data):
    """比較期間の全年度から共通の横軸上限を求める。"""
    maximum = 0

    for row in data['rows'].values():
        values = pyramid_values(row)

        if values is None:
            continue

        male, female = values

        maximum = max(
            maximum,
            *(abs(v) for v in male + female)
        )

    return max(1, math.ceil(maximum))

def population_chart(data):
    """Population and household trends with clear, simple markers."""
    years = data['years']
    rows = data['rows']
    styles = [
        ('総人口', 'total_population', 0, '#0f766e', 5, 'solid', 'circle', 12),
        ('男性', 'male_population', 0, '#2563eb', 2.5, 'solid', 'circle', 9),
        ('女性', 'female_population', 0, '#e5484d', 2.5, 'solid', 'triangle', 11),
        ('世帯数', 'total_households', 1, '#d97706', 3, 'dashed', 'diamond', 12),
    ]
    series = [
        {
            'name': label,
            'type': 'line',
            'yAxisIndex': axis,
            'showSymbol': True,
            'showAllSymbol': True,
            'symbol': symbol,
            'symbolSize': size,
            'connectNulls': False,
            'lineStyle': {'color': color, 'width': width, 'type': line_type},
            'itemStyle': {'color': color},
            'data': [rows.get(y, {}).get(col) for y in years],
        }
        for label, col, axis, color, width, line_type, symbol, size in styles
    ]
    return {'tooltip': {'trigger': 'axis'}, 'legend': {'top': 0},
            'grid': {'left': 75, 'right': 75, 'top': 65, 'bottom': 45},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': [{'type': 'value', 'name': '人口（人）', 'scale': True},
                      {'type': 'value', 'name': '世帯数', 'scale': True}],
            'series': series}


def three_group_chart(data, mode: str = 'rate', stacked: bool = True):
    """Three age groups: stacked or grouped, percentages or persons."""
    years = data['years']
    values = [[], [], []]
    for y in years:
        row = data['rows'].get(y)
        if row is None:
            for group in values:
                group.append(None)
            continue
        counts = [row.get(f'{sex}_age_{code}')
                  for sex in ('male', 'female') for code in AGE_CODES]
        if any(v is None for v in counts):
            for group in values:
                group.append(None)
            continue
        combined = [counts[i] + counts[i + len(AGE_CODES)]
                    for i in range(len(AGE_CODES))]
        total = sum(combined)
        if total <= 0:
            for group in values:
                group.append(None)
            continue
        for i, indices in enumerate((range(0, 3), range(3, 13), range(13, 18))):
            count = sum(combined[j] for j in indices)
            values[i].append(round(count / total * 100, 3) if mode == 'rate' else count)

    rate = mode == 'rate'
    totals = [sum(v[i] for v in values) for i in range(len(years))
              if all(v[i] is not None for v in values)]
    # Specify an explicit maximum for BOTH modes: ECharts merges options and
    # otherwise retains the previous 100% ceiling after switching to counts.
    if stacked:
        upper = 100 if rate else max(1, math.ceil(max(totals, default=0) * 1.1))
    else:
        individual = [v for group in values for v in group if v is not None]
        upper = max(1, math.ceil(max(individual, default=0) * 1.1))
    return {
        'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
        'legend': {'top': 0},
        'grid': {'left': 85, 'right': 30, 'top': 65, 'bottom': 45},
        'xAxis': {'type': 'category', 'data': years},
        'yAxis': {'type': 'value', 'min': 0, 'max': upper,
                  'name': '割合（%）' if rate else '人口（人）'},
        'series': [
            {'name': label, 'type': 'bar',
             **({'stack': 'age'} if stacked else {}),
             'barMaxWidth': 48 if stacked else 24,
             'data': value, 'itemStyle': {'color': color}}
            for label, value, color in zip(
                ('0–14歳', '15–64歳', '65歳以上'), values,
                ('#70b7e5', '#70c4a7', '#efb86a'))],
    }


def pyramid_2d(data, year):
    """Adjacent age-class bars, with males to the left and females to the right."""
    row = data['rows'].get(str(year))
    values = pyramid_values(row) if row else None
    male, female = values if values else ([None] * len(AGE_CODES), [None] * len(AGE_CODES))
    limit = pyramid_axis_limit(data)
    return {
        'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
        'legend': {'top': 0},
        'grid': {'left': 70, 'right': 45, 'top': 55, 'bottom': 55},
        'xAxis': {
        'type': 'value',
        'name': '構成比（%）',
        'min': -limit,
        'max': limit,
        'interval': limit / 5,
        'axisLabel': {
            ':formatter':
                '(value) => Math.abs(value).toFixed(1) + "%"'
            },
        },

        'yAxis': {'type': 'category', 'data': AGE_LABELS, 'axisTick': {'show': False}},
        'series': [
            {'name': '男性', 'type': 'bar', 'stack': 'pyramid',
             'tooltip': {':valueFormatter': '(value) => Math.abs(value).toFixed(2) + "%"'},
             'barCategoryGap': '0%', 'barGap': '0%',
             'data': male, 'itemStyle': {'color': COLORS['male']}},
            {'name': '女性', 'type': 'bar', 'stack': 'pyramid',
             'tooltip': {':valueFormatter': '(value) => Math.abs(value).toFixed(2) + "%"'},
             'barCategoryGap': '0%', 'barGap': '0%',
             'data': female, 'itemStyle': {'color': COLORS['female']}},
        ],
    }


@ui.page('/')
def home_page():
    from okpop.app.nav import navigation
    navigation('home')
    # GitHub's raw URL allows the banner to display without adding a static route.
    banner_url = 'https://raw.githubusercontent.com/syunsuke/okpop/main/assets/okpop-banner.png'
    ui.query('body').style('background: #f5f8ff;')
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-6 gap-6'):
        # Show the complete banner edge-to-edge, without a gradient or side margins.
        with ui.card().classes('w-full overflow-hidden rounded-2xl shadow-md p-0'):
            ui.image(banner_url).classes('w-full block').props('fit=fill')

        with closing(sqlite3.connect(database.DEFAULT_DB_PATH)) as con:
            areas = [r[0] for r in con.execute(
                'SELECT DISTINCT area_name FROM view_excel_report_data ORDER BY area_name')]
        if not areas:
            ui.label('データがありません。データベース管理から更新してください。')
            return
        default_area = '大阪府全市町村' if '大阪府全市町村' in areas else areas[0]
        with ui.card().classes('w-full rounded-xl shadow-sm p-5'):
            with ui.row().classes('items-center gap-2 mb-2'):
                ui.icon('tune', color='indigo', size='sm')
                ui.label('表示条件').classes('text-lg font-bold text-slate-700')
            with ui.row().classes('w-full items-center gap-4 flex-wrap'):
                area = ui.select(areas, value=default_area, label='地域').classes('w-64').props('outlined')
                month = ui.select({m: f'{m}月' for m in range(1, 13)}, value=10,
                                  label='比較月').classes('w-32').props('outlined')
                period = ui.select({5: '5年間', 10: '10年間'}, value=10,
                                   label='比較期間').classes('w-32').props('outlined')
        error = ui.label('').classes('text-red-600')

        with ui.card().classes('w-full rounded-2xl shadow-sm p-5'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('show_chart', color='blue-7', size='md')
                ui.label('人口・世帯数の推移（毎年同じ月）').classes(
                    'text-xl font-bold text-blue-900'
                )
            ui.separator().classes('bg-blue-100')
            pop_chart = ui.echart({}).classes('w-full h-96')

        with ui.card().classes('w-full rounded-2xl shadow-sm p-5'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('diversity_3', color='pink-6', size='md')
                ui.label('人口ピラミッドの時系列変化').classes(
                    'text-xl font-bold text-pink-900'
                )
            ui.separator().classes('bg-pink-100')
            with ui.row().classes('items-center gap-3 flex-wrap'):
                play_button = ui.button('再生', icon='play_arrow', color='blue-7')
                stop_button = ui.button('停止', icon='stop', color='pink-5').props('outline')
                pyramid_year = ui.select({}, label='表示年').classes('w-36').props('outlined')
                speed = ui.select({0.5: '0.5秒', 1.0: '1秒', 2.0: '2秒'},
                                  value=1.0, label='再生間隔').classes('w-32').props('outlined')
            age_note = ui.label('').classes('text-sm text-slate-500')
            two_d = ui.echart({}).classes('w-full h-[540px]')

        with ui.card().classes('w-full rounded-2xl shadow-sm p-5'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('bar_chart', color='green-7', size='md')
                ui.label('年齢3区分の推移').classes('text-xl font-bold text-green-900')
            ui.separator().classes('bg-green-100')
            three_mode = ui.toggle({'rate': '割合（%）', 'count': '実数（人）'}, value='rate')
            ui.label('年齢3区分の比較（横並び）').classes('text-lg font-semibold text-slate-700')
            three_grouped = ui.echart({}).classes('w-full h-96')
            ui.separator().classes('bg-slate-100')
            ui.label('年齢3区分の積み上げ').classes('text-lg font-semibold text-slate-700')
            three_chart = ui.echart({}).classes('w-full h-96')
            ui.label('年齢データのない年は欠測として扱い、補間しません。').classes(
                'text-sm text-slate-500'
            )

        with ui.row().classes('w-full gap-5 flex-wrap'):
            with ui.link(target='/report').classes('flex-1 min-w-64 no-underline'):
                with ui.card().classes('w-full rounded-2xl p-7 items-center shadow-sm').style(
                    'background: linear-gradient(135deg, #dbeafe, #eff6ff);'
                ):
                    ui.icon('description', size='3rem', color='blue-7')
                    ui.label('レポート作成').classes('text-2xl font-bold text-blue-900')
                    ui.label('最新・指定年月のExcelレポート').classes('text-slate-600')
            with ui.link(target='/database').classes('flex-1 min-w-64 no-underline'):
                with ui.card().classes('w-full rounded-2xl p-7 items-center shadow-sm').style(
                    'background: linear-gradient(135deg, #d1fae5, #ecfdf5);'
                ):
                    ui.icon('storage', size='3rem', color='green-7')
                    ui.label('データベース管理').classes('text-2xl font-bold text-green-900')
                    ui.label('更新・状態チェック').classes('text-slate-600')

        current = {'data': None, 'years': [], 'playing': False,
                   'updating': False, 'elapsed': 0.0}

        def set_playing(value: bool):
            current['playing'] = value
            current['elapsed'] = 0.0
            play_button.set_enabled(not value and len(current['years']) > 1)
            stop_button.set_enabled(value)

        def refresh_pyramid():
            data = current['data']
            if data is None or current['updating']:
                return
            options = pyramid_2d(data, str(pyramid_year.value))
            two_d.options.clear()
            two_d.options.update(options)
            two_d.update()

        def select_year(year: str):
            current['updating'] = True
            try:
                pyramid_year.set_value(year)
            finally:
                current['updating'] = False
            refresh_pyramid()

        def refresh_three():
            data = current['data']
            if data is None:
                return
            three_grouped.options.clear()
            three_grouped.options.update(three_group_chart(data, three_mode.value, stacked=False))
            three_grouped.update()
            three_chart.options.clear()
            three_chart.options.update(three_group_chart(data, three_mode.value, stacked=True))
            three_chart.update()

        def refresh():
            set_playing(False)
            try:
                data = read_dashboard(area.value, int(month.value), int(period.value))
                current['data'] = data
                error.set_text('')
                pop_chart.options.clear()
                pop_chart.options.update(population_chart(data))
                pop_chart.update()
                refresh_three()
                years_with_ages = [y for y in data['years']
                                   if data['rows'].get(y)
                                   and pyramid_values(data['rows'][y]) is not None]
                current['years'] = years_with_ages
                current['updating'] = True
                try:
                    pyramid_year.set_options(
                        {y: f'{y}年' for y in years_with_ages},
                        value=years_with_ages[-1] if years_with_ages else None,
                    )
                finally:
                    current['updating'] = False
                age_note.set_text(
                    f'年齢階級データあり: {len(years_with_ages)}年 / {len(data["years"])}年'
                )
                refresh_pyramid()
            except Exception as exc:
                error.set_text(f'データの読み込みに失敗しました: {exc}')
            set_playing(False)

        def on_year_change(_):
            if current['updating']:
                return
            set_playing(False)  # Manual year selection pauses playback.
            refresh_pyramid()

        def play():
            years = current['years']
            if len(years) < 2:
                ui.notify('再生できる年が2つ以上必要です', type='warning')
                return
            # Begin at the oldest year if the last year is selected.
            if str(pyramid_year.value) == years[-1] or str(pyramid_year.value) not in years:
                select_year(years[0])
            set_playing(True)

        def tick():
            if not current['playing']:
                return
            current['elapsed'] += 0.1
            if current['elapsed'] + 1e-9 < float(speed.value):
                return
            current['elapsed'] = 0.0
            years = current['years']
            year = str(pyramid_year.value)
            if year not in years:
                set_playing(False)
                return
            index = years.index(year)
            if index + 1 >= len(years):
                set_playing(False)
                return
            select_year(years[index + 1])
            if index + 2 >= len(years):
                set_playing(False)

        play_button.on('click', play)
        stop_button.on('click', lambda: set_playing(False))
        pyramid_year.on_value_change(on_year_change)
        three_mode.on_value_change(lambda _: refresh_three())
        for selector in (area, month, period):
            selector.on_value_change(lambda _: refresh())
        ui.timer(0.1, tick)
        refresh()
