"""Shared page navigation."""
from nicegui import ui


def navigation(active: str) -> None:
    with ui.header().classes('bg-white text-slate-800 shadow-sm'):
        with ui.row().classes('w-full max-w-7xl mx-auto items-center gap-5 flex-wrap'):
            ui.link('OKPOP', '/').classes('text-xl font-bold no-underline')
            for key, label, target in (
                ('home', 'ホーム', '/'),
                ('database', '更新・確認', '/database'),
                ('report', 'レポート作成', '/report'),
            ):
                link = ui.link(label, target).classes('no-underline')
                if active == key:
                    link.classes('font-bold text-purple-700')
