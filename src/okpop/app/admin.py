"""OKPOP: homepage, database maintenance and report pages."""
from nicegui import ui
from okpop.app import home, database, report  # noqa: F401

if __name__ == '__main__':
    ui.run(title='OKPOP', port=8081, reload=False)
