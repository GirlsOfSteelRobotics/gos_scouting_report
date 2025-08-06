# Core
import pandas as pd
import plotly.express as px
from shiny import reactive, render, module
from shiny import App, ui
from shinywidgets import output_widget, render_widget
from data_container import df


@module.ui
def auto_tab_ui():
    return ui.page_fluid(
        output_widget("coral_vs_algae_plot"),
        output_widget("coral_by_level_plot"),
        output_widget("coral_points_by_level_plot")
    )

@module.server
def auto_tab_server(input, output, session):
    @render_widget
    def coral_vs_algae_plot():
        teams = ["frc3504", "frc4467", "frc10101", "frc5045", "frc538", "frc3966"]
        selected_teams = df[df["team_key"].isin(teams)]
        # Coral scored on reef vs. auto scored
        avg = selected_teams.groupby("team_key").mean(numeric_only=True).reset_index()
        fig = px.scatter(avg, x="totalAutoAlgae", y="totalAutoCoral", color="team_key",
                         title = "Coral vs. Algae AUTO")
        fig.update_layout(xaxis_title="Avg Algae Scored", yaxis_title="Avg Coral Scored on Reef")
        fig.update_traces(marker=dict(
            symbol="circle", size=10),
            textposition="middle left")

        return fig

    @render_widget
    def coral_by_level_plot():
        teams = ["frc3504", "frc4467", "frc10101", "frc5045", "frc538", "frc3966"]
        selected_teams = df[df["team_key"].isin(teams)]
        avg = selected_teams.groupby("team_key").mean(numeric_only=True).reset_index()
        # Avg Auto Coral by Team
        fig = px.bar(avg, x="team_key", y=["autoCoralL4", "autoCoralL3", "autoCoralL2", "autoCoralL1"],
                     title="Coral Distribution by Level Auto")
        fig.update_layout(xaxis_title="Teams", yaxis_title="Avg Coral in L1, L2, L3, L4")

        return fig

    @render_widget
    def coral_points_by_level_plot():
        teams = ["frc3504", "frc4467", "frc10101", "frc5045", "frc538", "frc3966"]
        selected_teams = df[df["team_key"].isin(teams)]
        avg = selected_teams.groupby("team_key").mean(numeric_only=True).reset_index()
        # Avg Auto Coral Points by Team
        fig = px.bar(avg, x="team_key",
                     y=["autoCoralL4Points", "autoCoralL3Points", "autoCoralL2Points", "autoCoralL1Points"],
                     title="Coral Point Distribution by Level Auto")
        fig.update_layout(xaxis_title="Teams", yaxis_title="Avg Coral Points in L1, L2, L3, L4")

        return fig