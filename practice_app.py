# Core
import pandas as pd
from shiny import App, ui

from auto_practice_tab import auto_tab_ui, auto_tab_server

app_ui = ui.page_navbar(
    ui.nav_panel("Auto", auto_tab_ui("auto_tab"))
)

def server(input, output, session):
    auto_tab_server("auto_tab")

app = App(app_ui, server)
