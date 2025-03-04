from shiny import App, ui, render
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pathlib


# read in data
USE_LOCAL_VERSION = True
EVENT_KEY = "2025txwac"
script_directory = pathlib.Path(__file__).resolve().parent
data_file = f"data/{EVENT_KEY}/match_scouting.csv"
print(f"Loading local data from: {data_file}")
df = pd.read_csv(data_file)

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

position = df["bargeStatus"]
df["endgamePoints"] = np.where(position == "Parked", 2, np.where(position == "Shallow Cage", 6, np.where(position == "Deep  Cage", 12, 0)))


df["totalPointsScored"] = df["totalTeleopPoints"] + df["totalAutoPoints"] + df["endgamePoints"]

# update team name
df["team_key"] = df["team_key"].str[3:]

# upcoming alliance lineup
red_teams = ["8408", "2881", "2689"]
blue_teams = ["8507", "2950", "148"]
all_teams = red_teams + blue_teams

# filter df by team_key
new_df = df.loc[df["team_key"].isin(all_teams)]
new_df["colorGroup"] = new_df["team_key"].apply(lambda x: "Red" if x in red_teams else "Blue")

# averages df
averages_by_team = new_df.groupby("team_key").mean(numeric_only=True).reset_index()
averages_by_team_all = df.groupby("team_key").mean(numeric_only=True).reset_index()

teams = averages_by_team["team_key"]

# endgame df
endgame_df = new_df.groupby('team_key')['bargeStatus'].value_counts().unstack(fill_value=0).reset_index()

# color coding
ticktext = [
    f"<span style='color:{'red' if team in red_teams else 'blue'}'>{team}</span>"
    for team in all_teams
]

new_df = new_df.sort_values(["colorGroup", "team_key"], ascending=[True, True])

color_map = {str(team): "#FF5733" for team in red_teams}  # Red teams
color_map.update({str(team): "#1F77B4" for team in blue_teams})  # Blue teams

def color_picker(team_num):
            if team_num in red_teams:
                return "red"
            else:
                return "blue"

# Define the UI
app_ui = ui.page_navbar(
    ui.nav_panel(
        "General Data",
        ui.card(
            ui.output_ui("teleop_auto_points_scatter")
        ),
        ui.card(
            ui.output_ui("total_points_boxplot")
        )
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
    ui.nav_panel(
        "Alliance Selection",
        ui.card(
            ui.output_data_frame("key_stats_dt")
        )
    ),
    title="GoS REEFSCAPE Data Science Report",
)

# Define the server logic
def server(input, output, session):
    @output
    @render.ui
    def total_points_boxplot():
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

        def color_picker(team_num):
            if team_num in red_teams:
                return "red"
            else:
                return "blue"

        x = averages_by_team["totalTeleopCoral"]
        y = averages_by_team["algaeTeleop"]
        teams = averages_by_team["team_key"]

        fig = px.scatter(x=x, y=y, text=teams, labels={'x': "Avg Coral Scored", 'y': "Avg Algae Scored in Net"},
                        title="Coral vs Algae TELEOP")

        colors = [color_picker(team) for team in teams]
        fig.update_traces(marker=dict(color=colors,
                                    symbol='circle', size=10),
                        textposition="middle left")

        return ui.HTML(fig.to_html(full_html=False))
    
    @output
    @render.ui
    def teleop_auto_points_scatter():
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
        x = averages_by_team["totalAutoCoral"]
        y = averages_by_team["algaeAuto"]
        teams = averages_by_team["team_key"]

        fig = px.scatter(x=x, y=y, text=teams, labels={'x': "Avg Coral Scored", 'y': "Avg Algae Scored in Net"}, title="Coral vs Algae AUTO")

        colors = [color_picker(team) for team in teams]  # Apply color_picker correctly
        fig.update_traces(marker=dict(color=colors, symbol='circle', size=10), textposition="middle left") 
        return ui.HTML(fig.to_html(full_html=False)) 

    @output
    @render.ui
    def coral_level_distribution_teleop_bar():
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
    def endgame_bar():
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
        return averages_by_team_all  
    

app = App(app_ui, server)