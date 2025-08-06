import pandas as pd
import plotly.express as px
from shiny import reactive, render, module
from shiny import App, ui
from shinywidgets import output_widget, render_widget
from data_container import df


def teleop_tab_ui():
    return ui.page_fluid(
        output_widget("plot")
    )

def teleop_avg_pt(
    teams = ["frc3504", "frc4467", "frc10101", "frc5045", "frc538", "frc3966"]
    selected_teams = df[df["team_key"].isin(teams)]
    # print(selected_teams)
    avg = selected_teams.groupby("team_key").mean(numeric_only = True).reset_index()

    avg_by_point_teleop = avg[["team_key", "teleopCoralL4", "teleopCoralL3", "teleopCoralL2", "teleopCoralL1"]]
    avg_by_point_teleop["teleopCoralL4Points"] = avg["teleopCoralL4"] * 5
    avg_by_point_teleop["teleopCoralL3Points"] = avg["teleopCoralL3"] * 4
    avg_by_point_teleop["teleopCoralL2Points"] = avg["teleopCoralL2"] * 3
    avg_by_point_teleop["teleopCoralL1Points"] = avg["teleopCoralL1"] * 2

    # Avg TELEOP Coral by Team
    fig = px.bar(avg, x = "team_key", y = ["teleopCoralL4", "teleopCoralL3", "teleopCoralL2", "teleopCoralL1"], title = "Coral Distribution by Level Teleop")
    fig.update_layout(xaxis_title = "Teams", yaxis_title = "Avg Coral in L1, L2, L3, L4")

    return fig
    )