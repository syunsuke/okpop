"""OKPOP report page: single background job, separate downloads for each report type."""
from datetime import date
from pathlib import Path
from threading import Lock

from nicegui import run, ui
from okpop.app import actions

_guard = Lock()
_state = {
    'running': False,
    'running_kind': None,
    'latest_archive': None,
    'custom_archive': None,
    'latest_message': '未作成',
    'custom_message': '未作成',
}


def _snapshot() -> dict:
    with _guard:
        return _state.copy()


def _reserve(kind: str) -> bool:
    with _guard:
        if _state['running']:
            return False
        _state['running'] = True
        _state['running_kind'] = kind
        _state[f'{kind}_message'] = '作成中...'
        return True


def _build_report(kind: str, year: int | None = None, month: int | None = None) -> None:
    """Worker releases the busy flag even if the browser navigates away."""
    try:
        if kind == 'latest':
            archive = actions.get_latest_report_archive()
        else:
            archive = actions.create_report_archive_for_date(year, month)
        path = Path(archive)
        if not path.is_file():
            raise FileNotFoundError(f'ZIPが見つかりません: {path}')
        with _guard:
            _state[f'{kind}_archive'] = path
            _state[f'{kind}_message'] = f'作成完了: {path.name}'
    except Exception as exc:
        with _guard:
            _state[f'{kind}_message'] = f'作成失敗: {exc}'
    finally:
        with _guard:
            _state['running'] = False
            _state['running_kind'] = None


@ui.page('/report')
def report_page():
    from okpop.app.nav import navigation
    navigation('report')
    with ui.column().classes('w-full max-w-5xl mx-auto p-6 gap-5'):
        ui.label('レポート作成').classes('text-2xl font-bold')

        async def start(kind: str, year: int | None = None, month: int | None = None):
            if not _reserve(kind):
                ui.notify('別のレポートを作成中です。完了までお待ちください。', type='warning')
                return
            refresh()
            await run.io_bound(_build_report, kind, year, month)
            refresh()

        with ui.card().classes('w-full p-5 gap-3'):
            ui.label('最新レポート').classes('text-lg font-bold')
            ui.label('利用可能な最新月のレポートを作成します。')
            latest_button = ui.button('最新レポートを作成', icon='description',
                                      on_click=lambda: start('latest'))
            latest_status = ui.label('未作成').classes('text-sm')
            latest_download = ui.button('最新レポートのZIPをダウンロード', icon='download')
            latest_download.visible = False

        with ui.card().classes('w-full p-5 gap-3'):
            ui.label('指定年月のレポート').classes('text-lg font-bold')
            with ui.row().classes('gap-3 items-center'):
                year_input = ui.number('年', value=date.today().year, min=2000, max=2100, step=1).classes('w-32')
                month_input = ui.number('月', value=date.today().month, min=1, max=12, step=1).classes('w-28')

            async def start_custom():
                try:
                    year, month = int(year_input.value), int(month_input.value)
                    if not (2000 <= year <= 2100 and 1 <= month <= 12):
                        raise ValueError
                except (ValueError, TypeError):
                    ui.notify('有効な年月を指定してください', type='warning')
                    return
                await start('custom', year, month)

            custom_button = ui.button('指定年月でレポートを作成', icon='calendar_month',
                                      on_click=start_custom)
            custom_status = ui.label('未作成').classes('text-sm')
            custom_download = ui.button('指定年月レポートのZIPをダウンロード', icon='download')
            custom_download.visible = False

        def refresh():
            state = _snapshot()
            latest_button.set_enabled(not state['running'])
            custom_button.set_enabled(not state['running'])
            latest_status.set_text(state['latest_message'])
            custom_status.set_text(state['custom_message'])
            for kind, button in [('latest', latest_download), ('custom', custom_download)]:
                path = state[f'{kind}_archive']
                # A file being rewritten by an active job must not be downloaded.
                button.visible = (path is not None and path.is_file()
                                  and not state['running'])

        def download(kind: str):
            state = _snapshot()
            path = state[f'{kind}_archive']
            if not state['running'] and path is not None and path.is_file():
                ui.download(path)
            else:
                ui.notify('ダウンロード可能なZIPがありません', type='warning')

        latest_download.on('click', lambda: download('latest'))
        custom_download.on('click', lambda: download('custom'))
        ui.timer(0.5, refresh)
        refresh()
