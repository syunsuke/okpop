"""Excel取得・DB更新と、月別の状態チェック。"""
import queue
import sys
import threading
from contextlib import contextmanager
from datetime import datetime

from nicegui import run, ui
from okpop.app import actions
from okpop.app.check import render_check

# stdout はプロセス共通なので、実行スレッドの出力だけを捕捉する。
# 他のスレッドからの出力は元の stdout に流す。
_STDOUT_LOCK = threading.Lock()

class _ThreadOutput:
    def __init__(self, original, thread_id, messages):
        self.original = original
        self.thread_id = thread_id
        self.messages = messages
        self.pending = ''

    def write(self, text):
        if threading.get_ident() != self.thread_id:
            return self.original.write(text)
        self.pending += text
        while '\n' in self.pending:
            line, self.pending = self.pending.split('\n', 1)
            if line.strip():
                self.messages.put(line.rstrip('\r'))
        return len(text)

    def flush(self):
        if threading.get_ident() != self.thread_id:
            return self.original.flush()
        if self.pending.strip():
            self.messages.put(self.pending)
        self.pending = ''

    def __getattr__(self, name):
        return getattr(self.original, name)

@contextmanager
def _capture_stdout(messages):
    # 同時に複数の更新処理を開始しない前提で stdout を一時差し替え。
    with _STDOUT_LOCK:
        original = sys.stdout
        proxy = _ThreadOutput(original, threading.get_ident(), messages)
        sys.stdout = proxy
        try:
            yield
        finally:
            proxy.flush()
            sys.stdout = original

def _run_update(messages):
    with _capture_stdout(messages):
        actions.update_database()

@ui.page('/database')
def database_page():
    from okpop.app.nav import navigation
    navigation('database')
    with ui.column().classes('w-full max-w-7xl mx-auto p-6 gap-4'):
        ui.label('データベース更新').classes('text-2xl font-bold')
        ui.label('大阪府のExcelをダウンロードし、そのままデータベースを更新します。')
        update_button = ui.button('データベース更新', icon='sync')
        progress = ui.spinner(size='lg')
        progress.visible = False
        status = ui.label('待機中').classes('text-gray-600')
        with ui.expansion('実行ログ', icon='terminal', value=True).classes('w-full'):
            log = ui.log(max_lines=1000).classes('w-full h-64 bg-gray-950 text-green-200 p-3 rounded')
        messages = queue.Queue()

        def drain():
            while True:
                try:
                    line = messages.get_nowait()
                except queue.Empty:
                    break
                log.push(f'{datetime.now():%H:%M:%S}  {line}')

        timer = ui.timer(0.15, drain, active=False)

        async def update():
            update_button.disable()
            progress.visible = True
            status.set_text('更新中...')
            log.clear()
            timer.active = True
            log.push('Excelの取得とデータベース更新を開始します。')
            succeeded = False
            try:
                await run.io_bound(_run_update, messages)
                succeeded = True
                log.push('更新完了')
                status.set_text('更新完了')
                ui.notify('データベースを更新しました', type='positive')
            except Exception as exc:
                log.push(f'エラー: {exc}')
                status.set_text('更新失敗')
                ui.notify(f'更新失敗: {exc}', type='negative')
            finally:
                drain()
                timer.active = False
                progress.visible = False
                update_button.enable()
            if succeeded:
                # 完了後にチェック結果もDBから読み直す。
                ui.navigate.to('/database')

        update_button.on('click', update)
        ui.separator()
        render_check()
