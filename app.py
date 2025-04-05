from shiny import App, ui, render, reactive
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pathlib
import json
import collections

from metadata import OUR_TEAM_NUMBER, CURRENT_EVENT

from utils import statbotics_utils, tba_utils

# read in data
USE_LOCAL_VERSION = True

if USE_LOCAL_VERSION:
    script_directory = pathlib.Path(__file__).resolve().parent
    base_data_directory = script_directory / f"data/{CURRENT_EVENT}"
    print(f"Loading local data from: {base_data_directory}")

    df = pd.read_csv(base_data_directory / "match_scouting.csv")
    matches_df = tba_utils.load_event_matches(base_data_directory / "tba_matches.json")
    statbotics_df = statbotics_utils.load_statbotics_matches(base_data_directory / "statbotics_matches.json")
else:
    branch_name = "main"
    base_url = f"https://raw.githubusercontent.com/GirlsOfSteelRobotics/gos_scouting_report/refs/heads/{branch_name}/data/{CURRENT_EVENT}"
    print(f"Loading remote data from {base_url}")

    from pyodide.http import open_url

    scouted_csv = open_url(base_url + "/match_scouting.csv")
    tba_matches_json = json.load(open_url(base_url + "/tba_matches.json"))
    statbotics_matches_json = json.load(open_url(base_url + "/statbotics_matches.json"))
    
    df = pd.read_csv(scouted_csv)
    matches_df = tba_utils.event_matches_json_to_dataframe(tba_matches_json)
    statbotics_df = statbotics_utils.statbotics_matches_json_to_dataframe(statbotics_matches_json)

# add new columns
df["totalTeleopCoral"] = df["teleopCoralL1"] + df["teleopCoralL2"] + df["teleopCoralL3"] + df["teleopCoralL4"]
df["totalAutoCoral"] = df["autoCoralL1"] + df["autoCoralL2"] + df["autoCoralL3"] + df["autoCoralL4"]

df["totalTeleopCoralPoints"] = df["teleopCoralL1"]*2 + df["teleopCoralL2"]*3 + df["teleopCoralL3"]*4 + df["teleopCoralL4"]*5
df["totalTeleopAlgaePoints"] = df["teleopAlgaeNet"]*4 + df["teleopAlgaeProc"]*6
df["totalTeleopPoints"] = df["totalTeleopCoralPoints"] + df["totalTeleopAlgaePoints"]

df["totalAutoCoralPoints"] = df["autoCoralL1"]*3 + df["autoCoralL2"]*4 + df["autoCoralL3"]*6 + df["autoCoralL4"]*7
df["totalAutoAlgaePoints"] = df["autoAlgaeNet"]*4 + df["autoAlgaeProc"]*6
df["totalAutoPoints"] = df["totalAutoCoralPoints"] + df["totalAutoAlgaePoints"]

df["algaeTeleop"] = df["teleopAlgaeNet"] + df["teleopAlgaeProc"]
df["algaeAuto"] = df["autoAlgaeNet"] + df["autoAlgaeProc"]

df["totalPieces"] = df["totalTeleopCoral"] + df["totalAutoCoral"] + df["algaeTeleop"] + df["algaeAuto"] 

position = df["bargeStatus"]
df["endgamePoints"] = np.where(position == "Parked", 2, np.where(position == "Shallow Cage", 6, np.where(position == "Deep Cage", 12, 0)))

df["endgamePlusAuto"] = df["totalAutoPoints"] + df["totalEndgamePoints"]

df["totalPointsScored"] = df["totalTeleopPoints"] + df["totalAutoPoints"] + df["endgamePoints"]

# update team name
df["team_key"] = df["team_key"].str[3:]

def create_mock_data_for_missing_teams(teams_with_no_data):
    data = collections.defaultdict(list)

    for team in teams_with_no_data:
        for key in df.columns:
            data[key].append(0)
        data["team_key"][-1] = team
        data["bargeStatus"][-1] = "Not Parked"
    return pd.DataFrame(data)

df_unique_teams = df.drop_duplicates(subset=['team_key'], keep='first')
# print(df_unique_teams.keys())
# Define the UI
app_ui = ui.page_navbar(
ui.nav_panel(
    "Match Preview",
ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("match_or_team", "Select Match Number or 6 Teams",
        choices=["Match Number", "Select 6 Teams"], selected="Match Number"),
        ui.output_ui("our_matches_switch_ui"),
        ui.output_ui("match_list_combobox"),
    ),
    ui.page_navbar(
    ui.nav_panel(
        "General Data",
        ui.card(
            ui.output_ui("teleop_auto_points_scatter")
        ),
        ui.card(
            ui.output_ui("total_points_boxplot")
        ),
        ui.layout_column_wrap(
            ui.card(
                ui.output_ui("red_statbotics_prediction")
            ),
            ui.card(
                ui.output_ui("blue_statbotics_prediction")
            )    
        ),
        ui.layout_column_wrap(
            ui.card(
                ui.output_ui("avg_coral_red_box")
            ),
            ui.card(
                ui.output_ui("avg_coral_blue_box")
            ),
        ),
        ui.layout_column_wrap(
            ui.card(
                ui.output_ui("avg_endgame_red_box")
            ),
            ui.card(
                ui.output_ui("avg_endgame_blue_box")
            ),
        ),
        ui.card(
            ui.output_data_frame("statbotics_dataframe")
        ),
    ),
    ui.nav_panel(
        "Auto Data",
        ui.card(
            ui.output_ui("coral_algae_auto_scatter")
        ),
        ui.card(
            ui.output_ui("coral_level_distribution_auto_bar")
        ),
        ui.card(
            ui.output_ui("coral_point_distribution_auto_bar")
        ) 
             
    ),
    ui.nav_panel(
        "Teleop Data",
        ui.card(
            ui.output_ui("coral_algae_teleop_scatter")
        ),
        ui.card(
            ui.output_ui("net_processor_teleop")
        ),
         ui.card(
            ui.output_ui("coral_level_distribution_teleop_bar")
        ),
                 ui.card(
            ui.output_ui("coral_point_distribution_teleop_bar")
        )
    ),
    ui.nav_panel(
        "Endgame Data",
        ui.card(
            ui.output_ui("endgame_bar")
        )
    ),
    ),
),
),
    ui.nav_panel(
        "Alliance Selection",
        ui.card(
            ui.output_ui("statbotics_scatter")
        ),
        ui.card(
            ui.output_ui("statbotics_scatter2")
        ),
        
        ui.card(
            ui.output_ui("pieces_scatter")
        ),
        ui.card(
            ui.output_data_frame("key_stats_dt")
        ),
    ),

    ui.nav_panel(
        "Team Summary",
        ui.page_sidebar(
            ui.sidebar(
            ui.output_ui("team_list_combobox"),
            ),
            ui.card(
            ui.output_ui("team_piece_summary_teleop")
            ),
            ui.card(
            ui.output_ui("team_piece_summary_auto")
            ),
            ui.card(
            ui.output_data_frame("key_stats_by_team_dt")
            )
            
        )    
    
    ),
    title="GoS REEFSCAPE Data Science Report",
)

def server(input, output, session):
    # upcoming alliance lineup
    def color_picker(team_num):
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        if team_num in red_teams:
            return "red"
        else:
            return "blue"

    @reactive.calc
    def get_match_data():
        if input.match_or_team() == "Match Number":
            match_num = int(input.match_select())
            match_data = matches_df[matches_df["match_number"] == match_num].reset_index()
            red_teams = [match_data["red1"][0][3:], match_data["red2"][0][3:], match_data["red3"][0][3:]]
            blue_teams = [match_data["blue1"][0][3:], match_data["blue2"][0][3:], match_data["blue3"][0][3:]]
        else:
            red_teams = [input.red1(), input.red2(), input.red3()]
            blue_teams = [input.blue1(), input.blue2(), input.blue3()]


        all_teams = red_teams + blue_teams

        # filter df by team_key
        new_df = df.loc[df["team_key"].isin(all_teams)]
        teams_with_no_data = set(all_teams).difference(set(new_df["team_key"]))
        if teams_with_no_data:
            ui.notification_show(
                f"This match contains teams that have no scouting data",
                type="warning",
                duration=None,
            )
            new_df = pd.concat([new_df, create_mock_data_for_missing_teams(teams_with_no_data)])
        new_df["colorGroup"] = new_df["team_key"].apply(lambda x: "Red" if x in red_teams else "Blue")
        
        # averages df
        averages_by_team = new_df.groupby("team_key").mean(numeric_only=True).reset_index()
        averages_by_team_all = df.groupby("team_key").mean(numeric_only=True).reset_index()

        # Sort data
        averages_by_team = averages_by_team.set_index("team_key").loc[all_teams].reset_index()
        new_df = new_df.set_index("team_key").loc[all_teams].reset_index()

        color_map = {str(team): "#FF5733" for team in red_teams}  # Red teams
        color_map.update({str(team): "#1F77B4" for team in blue_teams})  # Blue teams

        return new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all

    @output
    @render.ui
    def total_points_boxplot():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        fig = px.box(new_df, 
                    x="team_key", 
                    y="totalPointsScored", 
                    color="team_key",
                    category_orders={"team_key": new_df["team_key"].tolist()},  # Ensure x-axis is ordered
                    color_discrete_map=color_map
                    )

        # Step 6: Update x-axis labels if needed
        fig.update_layout(
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=new_df["team_key"].tolist(),
                ticktext=new_df["team_key"].tolist(),
                tickfont=dict(size=14)
            )
        )
    
        return ui.HTML(fig.to_html(full_html=False))

    @output
    @render.ui
    def coral_algae_teleop_scatter():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        x = averages_by_team["algaeTeleop"]
        y = averages_by_team["totalTeleopCoral"]
        teams = averages_by_team["team_key"]

        fig = px.scatter(x=x, y=y, text=teams, labels={'x': "Avg Algae Scored", 'y': "Avg Coral Scored"},
                        title="Algae vs Coral TELEOP")

        colors = [color_picker(team) for team in teams]
        fig.update_traces(marker=dict(color=colors,
                                    symbol='circle', size=10),
                        textposition="middle left")

        return ui.HTML(fig.to_html(full_html=False))
    
    @output
    @render.ui
    def teleop_auto_points_scatter():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        teams = averages_by_team["team_key"]
        x = averages_by_team["totalTeleopPoints"]
        y = averages_by_team["totalAutoPoints"]

        # Create the plot
        fig = px.scatter(x=x, y=y, text=teams, labels={'x': "totalTeleopPoints", 'y': "totalAutoPoints"},
                        title="Teleop vs Auto Points")

        # Add custom color for each point based on the team_key
        colors = [color_picker(team) for team in teams]  # Apply color_picker correctly
        fig.update_traces(marker=dict(color=colors,
                                    symbol='circle', size=10),
                        textposition="middle left")
        
        return ui.HTML(fig.to_html(full_html=False))
    
    @output
    @render.ui
    def net_processor_teleop():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        # Step 1: Convert team_keys to string
        averages_by_team["team_key"] = averages_by_team["team_key"].astype(str)

        # Step 2: Sort teams by colorGroup (if needed)
        averages_by_team["colorGroup"] = averages_by_team["team_key"].apply(lambda x: "Red" if x in red_teams else "Blue")

        # Step 3: Define x-axis values
        x = averages_by_team["team_key"]
        y1 = averages_by_team["teleopAlgaeNet"]
        y2 = averages_by_team["teleopAlgaeProc"]

        # Step 4: Define colors for x-axis labels
        color_map = {str(team): "#FF5733" for team in red_teams}  # Red teams
        color_map.update({str(team): "#1F77B4" for team in blue_teams})  # Blue teams

        # Generate colored tick labels
        ticktext = [f'<span style="color:{color_map[team]};">{team}</span>' for team in x]

        # Step 5: Create the bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x,
            y=y1,
            name="Net",
            marker=dict(color="#83DCDD", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y2,
            name="Processor",
            marker=dict(color="#FFB480", line=dict(color="white", width=1))
        ))

        # Step 6: Update layout with grouped colored x-axis labels
        fig.update_layout(
            barmode="stack",
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=all_teams,
                ticktext=ticktext,  # Apply colored labels
                tickfont=dict(size=14)  # Adjust font size if needed
            ),
            yaxis_title="Avg Algae in Net / Processor",
            title="Algae in Processor and Net TELEOP",
            legend_title="Algae Type",
            template="plotly_white"
        )


        return ui.HTML(fig.to_html(full_html=False)) 

    @output
    @render.ui
    def coral_algae_auto_scatter():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        x = averages_by_team["algaeAuto"]
        y = averages_by_team["totalAutoCoral"]
        teams = averages_by_team["team_key"]

        fig = px.scatter(x=x, y=y, text=teams, labels={'x': "Avg Algae Scored", 'y': "Avg Coral Scored in Net"}, title="Coral vs Algae AUTO")

        colors = [color_picker(team) for team in teams]  # Apply color_picker correctly
        fig.update_traces(marker=dict(color=colors, symbol='circle', size=10), textposition="middle left") 
        return ui.HTML(fig.to_html(full_html=False)) 

    @output
    @render.ui
    def coral_level_distribution_teleop_bar():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        # coral level distribution -- stacked bar graph
        averages_by_team["team_key"] = averages_by_team["team_key"].astype(str)
        x = averages_by_team["team_key"]
        y1 = averages_by_team["teleopCoralL1"]
        y2 = averages_by_team["teleopCoralL2"]
        y3 = averages_by_team["teleopCoralL3"]
        y4 = averages_by_team["teleopCoralL4"]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x,
            y=y1,
            name="Coral L1",
            marker=dict(color="#9BE3DF", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y2,
            name="Coral L2",
            marker=dict(color="#F7898A", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y3,
            name="Coral L3",
            marker=dict(color="#FACE9F", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y4,
            name="Coral L4",
            marker=dict(color="#FFE493", line=dict(color="white", width=1))
        ))
        
        ticktext = [f'<span style="color:{color_map[team]};">{team}</span>' for team in x]

        fig.update_layout(
            barmode="stack",  # Stack the bars
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=all_teams,
                ticktext= ticktext,
                tickfont=dict(size=14)  # Adjust font size if needed
            ),
            yaxis_title="Avg Coral in L1, L2, L3, L4",
            title="Coral Level Distribution Teleop",
            legend_title="Coral Levels",
            template="plotly_white"
        )

        return ui.HTML(fig.to_html(full_html=False)) 
    @output
    @render.ui
    def coral_level_distribution_auto_bar():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        # coral level distribution -- stacked bar graph
        averages_by_team["team_key"] = averages_by_team["team_key"].astype(str)
        x = averages_by_team["team_key"]
        y1 = averages_by_team["autoCoralL1"]
        y2 = averages_by_team["autoCoralL2"]
        y3 = averages_by_team["autoCoralL3"]
        y4 = averages_by_team["autoCoralL4"]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x,
            y=y1,
            name="Coral L1",
            marker=dict(color="#9BE3DF", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y2,
            name="Coral L2",
            marker=dict(color="#F7898A", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y3,
            name="Coral L3",
            marker=dict(color="#FACE9F", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y4,
            name="Coral L4",
            marker=dict(color="#FFE493", line=dict(color="white", width=1))
        ))

        ticktext = [
        f"<span style='color:{'red' if team in red_teams else 'blue'}'>{team}</span>"
        for team in all_teams
        ]
        fig.update_layout(
            barmode="stack",  # Stack the bars
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=all_teams,
                ticktext= ticktext,
                tickfont=dict(size=14)  # Adjust font size if needed
            ),
            yaxis_title="Avg Coral in L1, L2, L3, L4",
            title="Coral Level Distribution Auto",
            legend_title="Coral Levels",
            template="plotly_white"
        )

        return ui.HTML(fig.to_html(full_html=False)) 

    @output
    @render.ui
    def coral_point_distribution_teleop_bar():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        # coral level distribution -- stacked bar graph
        averages_by_team["team_key"] = averages_by_team["team_key"].astype(str)
        x = averages_by_team["team_key"]
        y1 = averages_by_team["teleopCoralL1"]*2
        y2 = averages_by_team["teleopCoralL2"]*3
        y3 = averages_by_team["teleopCoralL3"]*4
        y4 = averages_by_team["teleopCoralL4"]*5

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x,
            y=y1,
            name="Coral L1",
            marker=dict(color="#9BE3DF", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y2,
            name="Coral L2",
            marker=dict(color="#F7898A", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y3,
            name="Coral L3",
            marker=dict(color="#FACE9F", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y4,
            name="Coral L4",
            marker=dict(color="#FFE493", line=dict(color="white", width=1))
        ))
        ticktext = [
        f"<span style='color:{'red' if team in red_teams else 'blue'}'>{team}</span>"
        for team in all_teams
        ]
        fig.update_layout(
            barmode="stack",  # Stack the bars
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=all_teams,
                ticktext= ticktext,
                tickfont=dict(size=14)  # Adjust font size if needed
            ),
            yaxis_title="Avg Coral in L1, L2, L3, L4",
            title="Coral Point Distribution by Level Teleop",
            legend_title="Coral Levels",
            template="plotly_white"
        )
        return ui.HTML(fig.to_html(full_html=False))

    @output
    @render.ui
    def coral_point_distribution_auto_bar():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        averages_by_team["team_key"] = averages_by_team["team_key"].astype(str)
        x = averages_by_team["team_key"]
        y1 = averages_by_team["autoCoralL1"]*3
        y2 = averages_by_team["autoCoralL2"]*4
        y3 = averages_by_team["autoCoralL3"]*6
        y4 = averages_by_team["autoCoralL4"]*7

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x,
            y=y1,
            name="Coral L1",
            marker=dict(color="#9BE3DF", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y2,
            name="Coral L2",
            marker=dict(color="#F7898A", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y3,
            name="Coral L3",
            marker=dict(color="#FACE9F", line=dict(color="white", width=1))
        ))

        fig.add_trace(go.Bar(
            x=x,
            y=y4,
            name="Coral L4",
            marker=dict(color="#FFE493", line=dict(color="white", width=1))
        ))
        ticktext = [
        f"<span style='color:{'red' if team in red_teams else 'blue'}'>{team}</span>"
        for team in all_teams
        ]
        fig.update_layout(
            barmode="stack",  # Stack the bars
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=all_teams,
                ticktext= ticktext,
                tickfont=dict(size=14)  # Adjust font size if needed
            ),
            yaxis_title="Avg Coral Points in L1, L2, L3, L4",
            title="Coral Point Distribution by Level Auto",
            legend_title="Coral Levels",
            template="plotly_white"
        )
        return ui.HTML(fig.to_html(full_html=False)) 
      
    @output
    @render.ui
    def endgame_bar():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        endgame_df = new_df.groupby('team_key')['bargeStatus'].value_counts().unstack(fill_value=0).reset_index()
        endgame_df = endgame_df.set_index("team_key").loc[all_teams].reset_index()
        
        # Populate data if the columns don't exist
        if 'Parked' not in endgame_df.columns:
            endgame_df['Parked'] = 0
        if 'Shallow Cage' not in endgame_df.columns:
            endgame_df['Shallow Cage'] = 0
        if 'Deep Cage' not in endgame_df.columns:
            endgame_df['Deep Cage'] = 0

        # Convert "team_key" to string if not already done
        endgame_df["team_key"] = endgame_df["team_key"].astype(str)
        x = endgame_df["team_key"]
        y1 = endgame_df["Parked"]
        y2 = endgame_df["Shallow Cage"]
        y3 = endgame_df["Deep Cage"]

        # Create the bar graph
        fig = go.Figure()

        # Add the first bar (Park)
        fig.add_trace(go.Bar(
            x=x,
            y=y1,
            name="Park",
            marker=dict(color="#EB89B5", line=dict(color="white", width=1))
        ))



        # Add the second bar (Shallow), stacked on top of Park
        fig.add_trace(go.Bar(
            x=x,
            y=y2,
            name="Shallow",
            marker=dict(color="#FFD7E9", line=dict(color="white", width=1))
        ))

        # Add the third bar (Deep), stacked on top of Park + Shallow
        fig.add_trace(go.Bar(
            x=x,
            y=y3,
            name="Deep",
            marker=dict(color="#FFF2AF", line=dict(color="white", width=1))
        ))

        ticktext = [
        f"<span style='color:{'red' if team in red_teams else 'blue'}'>{team}</span>"
        for team in all_teams
        ]
        # Update layout for stacking and aesthetics
        fig.update_layout(
            barmode="stack",  # Stack the bars
            xaxis=dict(
                title="Team",
                tickmode="array",
                tickvals=all_teams,
                ticktext= ticktext,
                tickfont=dict(size=14)  # Adjust font size if needed
            ),
            yaxis_title="Endgame Status",
            title="Endgame Status",
            legend_title="Status Levels",
            template="plotly_white"
        )
        return ui.HTML(fig.to_html(full_html=False)) 
    
    @output
    @render.data_frame
    def key_stats_dt():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()

        return render.DataGrid(averages_by_team_all.round(2), filters=True)
    
    @output
    @render.ui
    def our_matches_switch_ui():
        if input.match_or_team() == "Match Number":
            return ui.input_switch("our_matches_switch", "Filter Our Matches", False)
        else:
            return None

    @render.ui
    def match_list_combobox():
        if input.match_or_team() == "Match Number":
            if input.our_matches_switch():
            # Fix: Use .apply() to check if OUR_TEAM_NUMBER is in the list of team keys
                matches_df_copy = matches_df[
                    matches_df["alliances.blue.team_keys"].apply(lambda teams: any(str(OUR_TEAM_NUMBER) in team for team in teams)) |
                    matches_df["alliances.red.team_keys"].apply(lambda teams: any(str(OUR_TEAM_NUMBER) in team for team in teams))]
                match_numbers = matches_df_copy["match_number"]
            else:
                match_numbers = matches_df["match_number"]

            return (
                ui.input_select(
                    "match_select",
                    "Match",
                    {
                        str(match_number): str(match_number)
                        for match_number in sorted(match_numbers)
                    },
                ),
            )
        else: 
            team_numbers = df_unique_teams["team_key"].astype(str).tolist()
            return ui.div(
                ui.input_select("red1", "Red Alliance Teams", choices=team_numbers),
                ui.input_select("red2", "", choices=team_numbers),
                ui.input_select("red3", "", choices=team_numbers),
                ui.input_select("blue1", "Blue Alliance Teams", choices=team_numbers),
                ui.input_select("blue2", "", choices=team_numbers),
                ui.input_select("blue3", "", choices=team_numbers),
            )
        
    @output
    @render.ui
    def team_list_combobox():
        team_numbers = df_unique_teams["team_key"].astype(str).tolist()  # Ensure values are strings

        return ui.input_select(
            "team_select",  # Assign a unique ID to retrieve the selected value
            "Select a Team",  # Label for dropdown
            choices={team: team for team in sorted(team_numbers, key=lambda x: int(x))},  # Properly map values
            selected=str(OUR_TEAM_NUMBER),
        )
    
    @reactive.calc
    def filter_by_team():
        team_number = input.team_select()  # Get selected team from dropdown
        return df[df["team_key"] == team_number]

    @output
    @render.data_frame
    def key_stats_by_team_dt():
        return render.DataGrid(filter_by_team().round(2), filters=True)
    
    @output
    @render.ui
    def team_piece_summary_auto():
        team_data = filter_by_team()
        return px.bar(
            team_data,
            x="match_number",
            y=[
                "autoCoralL1",
                "autoCoralL2",
                "autoCoralL3",
                "autoCoralL4",
                "autoAlgaeNet",
                "autoAlgaeProc",
            ],
        )
    @output
    @render.ui
    def team_piece_summary_teleop():
        team_data = filter_by_team()
        return px.bar(
            team_data,
            x="match_number",
            y=[
                "teleopCoralL1",
                "teleopCoralL2",
                "teleopCoralL3",
                "teleopCoralL4",
                "teleopAlgaeNet",
                "teleopAlgaeProc"
        ],
    )
    # print(df.keys())
    @output
    @render.ui
    def statbotics_scatter():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        teams = averages_by_team_all["team_key"]
        
        x = averages_by_team_all["endgamePlusAuto"]
        y = averages_by_team_all["totalTeleopPoints"]

        # Create the plot
        fig = px.scatter(averages_by_team_all, x="endgamePlusAuto", y="totalTeleopPoints", text=teams, 
                         title="Auto & Endgame vs Teleop", color="totalPieces", hover_name="team_key", hover_data={
                            "team_key": "",
                            "totalPieces":":.2f", 

                            "totalAutoPoints":":.2f", 
                            "totalAutoCoral":":.2f",
                            "algaeAuto":":.2f",

                            "totalTeleopPoints":":.2f", 
                            "totalTeleopCoral":":.2f",
                            "algaeTeleop":":.2f",
                            
                            "endgamePoints":":.2f",
                            "endgamePlusAuto":":.2f",
                        })

        # Add custom color for each point based on the team_key
        fig.update_traces(marker=dict(
                                    symbol='circle', size=10),
                        textposition="middle left")
        
        return ui.HTML(fig.to_html(full_html=False))
        
    # print(df.keys())
    @output
    @render.ui
    def statbotics_scatter2():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        teams = averages_by_team_all["team_key"]
        
        x = averages_by_team_all["totalAutoPoints"]
        y = averages_by_team_all["totalTeleopPoints"]

        # Create the plot
        fig = px.scatter(averages_by_team_all, x="totalAutoPoints", y="totalTeleopPoints", text=teams, 
                         title="Auto vs Teleop", color="totalPieces", hover_name="team_key", hover_data={
                            "team_key": "",
                            "totalPieces":":.2f", 

                            "totalAutoPoints":":.2f", 
                            "totalAutoCoral":":.2f",
                            "algaeAuto":":.2f",

                            "totalTeleopPoints":":.2f", 
                            "totalTeleopCoral":":.2f",
                            "algaeTeleop":":.2f",
                            
                            "endgamePoints":":.2f",
                            "endgamePlusAuto":":.2f",
                        })

        # Add custom color for each point based on the team_key
        fig.update_traces(marker=dict(
                                    symbol='circle', size=10),
                        textposition="middle left")
        
        return ui.HTML(fig.to_html(full_html=False))
    
    @output
    @render.ui
    def pieces_scatter():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        teams = averages_by_team_all["team_key"]
        
        y = averages_by_team_all["algaeTeleop"] + averages_by_team_all["algaeAuto"]
        x = averages_by_team_all["totalTeleopCoral"] + averages_by_team_all["totalAutoCoral"]

        # Create the plot
        fig = px.scatter(averages_by_team_all, x=x, y=y, text=teams, 
                         title="Pieces", color="totalPieces", hover_name="team_key", hover_data={
                            "team_key": "",
                            "totalPieces":":.2f", 

                            "totalAutoPoints":":.2f", 
                            "totalAutoCoral":":.2f",
                            "algaeAuto":":.2f",

                            "totalTeleopPoints":":.2f", 
                            "totalTeleopCoral":":.2f",
                            "algaeTeleop":":.2f",
                            
                            "endgamePoints":":.2f",
                            "endgamePlusAuto":":.2f",
                        })

        # Add custom color for each point based on the team_key
        fig.update_traces(marker=dict(
                                    symbol='circle', size=10),
                        textposition="middle left")
        
        return ui.HTML(fig.to_html(full_html=False))


    @output
    @render.ui
    def avg_coral_red_box():
        
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        red_df = averages_by_team.loc[averages_by_team["team_key"].isin(red_teams)]
        avg_coral_pieces = red_df["totalTeleopCoral"].sum()+red_df["totalAutoCoral"].sum()
        
        return ui.value_box(
            title="Avg Coral Pieces RED",
            value=str(round(float(avg_coral_pieces), 1))
        )

    @output
    @render.ui
    def avg_coral_blue_box():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        blue_df = averages_by_team.loc[averages_by_team["team_key"].isin(blue_teams)]

        avg_coral_pieces = blue_df["totalTeleopCoral"].sum()+blue_df["totalAutoCoral"].sum()
        
        return ui.value_box(
            title="Avg Coral Pieces BLUE",
            value=str(round(float(avg_coral_pieces), 1))
        )

    @output
    @render.ui
    def avg_endgame_red_box():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        red_df = averages_by_team.loc[averages_by_team["team_key"].isin(red_teams)]

        endgame_avg = red_df["endgamePoints"].sum()
        
        return ui.value_box(
            title="Avg Endgame Points RED",
            value=str(round(float(endgame_avg), 1))
        )
    
    @output
    @render.ui
    def avg_endgame_blue_box():
        new_df, color_map, red_teams, blue_teams, all_teams, averages_by_team, averages_by_team_all = get_match_data()
        blue_df = averages_by_team.loc[averages_by_team["team_key"].isin(blue_teams)]

        endgame_avg = blue_df["endgamePoints"].sum()
        
        return ui.value_box(
            title="Avg Endgame Points BLUE",
            value=str(round(float(endgame_avg), 1))
        )
    # @reactive.calc
    # def filter_by_match():
    #     match_number = int(input.match_select())
    #     scouted_data = df[
    #         df["match_number"] == match_number
    #     ]
    #     statbotics_data = statbotics_df[
    #         statbotics_df.match_number == match_number
    #     ]

    #     return scouted_data, statbotics_data
    
    @render.text
    def red_statbotics_prediction():
        match_num = int(input.match_select())
        statbotics_data_filtered = statbotics_df.loc[
            (statbotics_df["match_number"] == match_num )
            & (statbotics_df["comp_level"] == "qm")
        ]
        return ui.value_box(
            title="Prediction RED",
            value=str(statbotics_data_filtered["pred.red_score"].sum())
        )

    @render.text
    def blue_statbotics_prediction():
        match_num = int(input.match_select())
        statbotics_data_filtered = statbotics_df.loc[
            (statbotics_df["match_number"] == match_num) 
            & (statbotics_df["comp_level"] == "qm")
        ]
        return ui.value_box(
            title="Prediction BLUE",
            value=str(statbotics_data_filtered["pred.blue_score"].sum())
        )
    
    @output
    @render.data_frame
    def statbotics_dataframe():
        return render.DataGrid(statbotics_df, filters=True)
    
    
app = App(app_ui, server)