import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import io

# Set page configuration for better layout
st.set_page_config(layout="wide", page_title="IPL Deliveries Dashboard", page_icon="�")

# --- Helper Functions ---

@st.cache_data
def load_data(uploaded_file):
    """
    Loads data from an uploaded CSV file or a default CSV file.
    Caches the data to avoid reloading on every rerun.
    """
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Custom CSV file loaded successfully!")
            return df
        except Exception as e:
            st.error(f"Error loading uploaded file: {e}. Please ensure it's a valid CSV.")
            return None
    else:
        # Load default IPL deliveries dataset
        try:
            # Assuming 'deliveries.csv' is in the same directory as the script
            # In a deployed environment, you might fetch this from a URL or a fixed path
            df = pd.read_csv("deliveries.csv")
            return df
        except FileNotFoundError:
            st.error("Default 'deliveries.csv' not found. Please upload a file.")
            return None
        except Exception as e:
            st.error(f"Error loading default dataset: {e}")
            return None

def get_table_download_link(df, filename="filtered_data.csv", text="Download Filtered Data as CSV"):
    """
    Generates a link to download the given DataFrame as a CSV file.
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# --- Main Application Layout ---

st.title("🏏 IPL Deliveries Data Visualization Dashboard")
st.markdown("""
    Explore detailed ball-by-ball data from IPL matches.
    Use the sidebar filters to refine your view and visualize key statistics.
""")

# File Uploader
st.sidebar.header("Upload Your Own Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

df = load_data(uploaded_file)

if df is not None:
    st.info(f"**Columns detected in your loaded dataset:** {', '.join(df.columns.tolist())}")

    # --- Data Preprocessing ---
    # Define truly required columns for the dashboard's core functionality
    # 'total_runs' is crucial for all run calculations.
    # 'player_dismissed' for wickets.
    # Others for filtering and grouping.
    required_cols = ['inning', 'batting_team', 'bowling_team', 'batsman', 'bowler', 'over', 'total_runs', 'player_dismissed']
    
    # Column Renaming (Optional - Uncomment and Adjust as Needed)
    # The image shows 'batter' exists but 'batsman' is missing.
    # We will rename 'batter' to 'batsman' to resolve this.
    if 'batter' in df.columns and 'batsman' not in df.columns:
        df.rename(columns={'batter': 'batsman'}, inplace=True)
        st.success("Renamed 'batter' column to 'batsman'.")
    
    # You might need to add more renames for other columns if they differ from required_cols.
    # Example: df.rename(columns={'Your_Runs_Column': 'total_runs'}, inplace=True)
    # df.rename(columns={'current_col_name1': 'expected_col_name1', 'current_col_name2': 'expected_col_name2'}, inplace=True)

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"The loaded dataset is missing key columns required for some functionalities: {', '.join(missing_cols)}.")
        st.info(f"Please ensure your CSV has columns named: {', '.join(required_cols)}. If your columns have different names, use the `df.rename` function in the code.")
        
        # If crucial columns like 'total_runs' are missing, we might need to stop or warn severely.
        if 'total_runs' not in df.columns:
            st.error("Cannot proceed: 'total_runs' column is essential but missing from the dataset. Please upload a CSV with a 'total_runs' column or rename an existing column to 'total_runs'.")
            st.stop() # Stop the execution if a critical column is missing

    # Fill NaN in 'player_dismissed' for consistent filtering and wicket counting
    if 'player_dismissed' in df.columns:
        df['player_dismissed'] = df['player_dismissed'].fillna('Not Dismissed')
    else:
        # If 'player_dismissed' itself is missing, create it with 'Not Dismissed'
        df['player_dismissed'] = 'Not Dismissed' 

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Data")

    # Team Filter
    # Check if 'batting_team' exists before trying to get unique values
    if 'batting_team' in df.columns:
        all_teams = sorted(df['batting_team'].unique().tolist())
        selected_teams = st.sidebar.multiselect("Select Batting Team(s)", all_teams, default=all_teams)
    else:
        st.sidebar.warning("Batting Team filter not available (column 'batting_team' missing).")
        selected_teams = [] # Empty list to avoid errors later

    # Bowler Filter (conditional on selected teams to avoid too many options)
    # Check if 'bowler' exists
    if 'bowler' in df.columns:
        # Filter the DataFrame for bowler options based on selected teams if 'batting_team' exists
        if 'batting_team' in df.columns and selected_teams:
            filtered_by_team_for_bowlers = df[df['batting_team'].isin(selected_teams)]
        else:
            filtered_by_team_for_bowlers = df # Use full df if no team filter or column missing

        all_bowlers = sorted(filtered_by_team_for_bowlers['bowler'].unique().tolist())
        selected_bowlers = st.sidebar.multiselect("Select Bowler(s)", all_bowlers, default=all_bowlers[:5] if all_bowlers else [])
    else:
        st.sidebar.warning("Bowler filter not available (column 'bowler' missing).")
        selected_bowlers = [] # Empty list to avoid errors later

    # Inning Filter
    if 'inning' in df.columns:
        all_innings = sorted(df['inning'].unique().tolist())
        selected_innings = st.sidebar.multiselect("Select Inning(s)", all_innings, default=all_innings)
    else:
        st.sidebar.warning("Inning filter not available (column 'inning' missing).")
        selected_innings = []

    # Over Slider
    if 'over' in df.columns:
        min_over = int(df['over'].min())
        max_over = int(df['over'].max())
        selected_over_range = st.sidebar.slider(
            "Select Over Range",
            min_value=min_over,
            max_value=max_over,
            value=(min_over, max_over)
        )
    else:
        st.sidebar.warning("Over Range slider not available (column 'over' missing).")
        selected_over_range = (0, 999) # Broad range to not filter out data if 'over' is missing

    # Apply Filters
    # Build filter conditions dynamically based on column availability and selection
    filter_conditions = []
    if 'batting_team' in df.columns and selected_teams:
        filter_conditions.append(df['batting_team'].isin(selected_teams))
    if 'bowler' in df.columns and selected_bowlers:
        filter_conditions.append(df['bowler'].isin(selected_bowlers))
    if 'inning' in df.columns and selected_innings:
        filter_conditions.append(df['inning'].isin(selected_innings))
    if 'over' in df.columns: # Over range is always applied if 'over' exists
        filter_conditions.append((df['over'] >= selected_over_range[0]) & (df['over'] <= selected_over_range[1]))

    # Combine all filter conditions
    if filter_conditions:
        combined_filter = filter_conditions[0]
        for condition in filter_conditions[1:]:
            combined_filter = combined_filter & condition
        filtered_df = df[combined_filter]
    else:
        filtered_df = df # No filters applied, use original df

    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.")
    else:
        # --- Summary Statistics ---
        st.header("📊 Key Statistics")
        col1, col2, col3, col4 = st.columns(4)

        # Check for 'total_runs' and 'player_dismissed' before calculating
        total_runs = filtered_df['total_runs'].sum() if 'total_runs' in filtered_df.columns else 0
        total_deliveries = len(filtered_df)
        total_wickets = filtered_df[filtered_df['player_dismissed'] != 'Not Dismissed'].shape[0] if 'player_dismissed' in filtered_df.columns else 0

        col1.metric("Total Runs Scored", f"{total_runs:,.0f}")
        col2.metric("Total Deliveries", f"{total_deliveries:,.0f}")
        col3.metric("Total Wickets Fallen", f"{total_wickets:,.0f}")
        
        # Calculate average runs per over for filtered data
        # Ensure 'match_id' and 'over' are present for this calculation
        avg_runs_per_over = 0
        if 'match_id' in filtered_df.columns and 'over' in filtered_df.columns and 'total_runs' in filtered_df.columns:
            runs_per_over_df = filtered_df.groupby(['match_id', 'over'])['total_runs'].sum().reset_index()
            avg_runs_per_over = runs_per_over_df['total_runs'].mean() if not runs_per_over_df.empty else 0
        else:
            st.info("Match ID, Over, or Total Runs column missing for Average Runs Per Over calculation.")
        col4.metric("Avg. Runs Per Over", f"{avg_runs_per_over:.2f}")

        st.markdown("---")

        # --- Visualizations ---
        st.header("📈 Data Visualizations")

        # 1. Bar Chart: Runs by Batting Team
        st.subheader("Runs Scored by Batting Team")
        if 'batting_team' in filtered_df.columns and 'total_runs' in filtered_df.columns:
            runs_by_team = filtered_df.groupby('batting_team')['total_runs'].sum().reset_index()
            fig_bar = px.bar(
                runs_by_team,
                x='batting_team',
                y='total_runs',
                title='Total Runs Scored by Each Selected Batting Team',
                labels={'batting_team': 'Batting Team', 'total_runs': 'Total Runs'},
                color='batting_team'
            )
            fig_bar.update_layout(xaxis_title="Batting Team", yaxis_title="Total Runs", template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Bar Chart 'Runs by Batting Team' not available (missing 'batting_team' or 'total_runs').")


        # 2. Line Chart: Runs progression per over
        st.subheader("Runs Progression Over Overs")
        if 'over' in filtered_df.columns and 'total_runs' in filtered_df.columns:
            runs_per_over_summary = filtered_df.groupby('over')['total_runs'].sum().reset_index()
            fig_line = px.line(
                runs_per_over_summary,
                x='over',
                y='total_runs',
                title='Total Runs Scored Across Overs',
                labels={'over': 'Over Number', 'total_runs': 'Total Runs'},
                markers=True
            )
            fig_line.update_layout(xaxis_title="Over Number", yaxis_title="Total Runs", template="plotly_white")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Line Chart 'Runs Progression Over Overs' not available (missing 'over' or 'total_runs').")

        # 3. Bar Chart: Distribution of Batsman Runs
        st.subheader("Distribution of Batsman Runs (Top 10 Batsmen)")
        if 'batsman' in filtered_df.columns and 'total_runs' in filtered_df.columns:
            # Get top 10 batsmen based on total runs in the filtered data
            batsman_runs = filtered_df.groupby('batsman')['total_runs'].sum().reset_index()
            top_batsmen = batsman_runs.nlargest(10, 'total_runs')['batsman'].tolist()
            
            if top_batsmen:
                filtered_df_top_batsmen = filtered_df[filtered_df['batsman'].isin(top_batsmen)]
                # Group by batsman and calculate total runs for histogram
                top_batsmen_runs_data = filtered_df_top_batsmen.groupby('batsman')['total_runs'].sum().reset_index()
                fig_hist = px.bar(
                    top_batsmen_runs_data,
                    x='batsman',
                    y='total_runs',
                    title=f'Total Runs by Top {len(top_batsmen)} Batsmen',
                    labels={'batsman': 'Batsman', 'total_runs': 'Total Runs'},
                    color='batsman'
                )
                fig_hist.update_layout(xaxis_title="Batsman", yaxis_title="Total Runs", template="plotly_white")
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Not enough data or unique batsmen to show top batsmen distribution for selected filters.")
        else:
            st.info("Bar Chart 'Distribution of Batsman Runs' not available (missing 'batsman' or 'total_runs').")


        st.markdown("---")
        # --- Download Filtered Data ---
        st.header("⬇️ Download Data")
        st.markdown(get_table_download_link(filtered_df), unsafe_allow_html=True)

else:
    st.info("Please upload a CSV file or ensure 'deliveries.csv' is available in the script's directory to proceed.")