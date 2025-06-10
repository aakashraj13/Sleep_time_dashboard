import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import numpy as np
from scipy import stats

# Custom CSS styling
def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Main theme colors */
        :root {
            --primary-100: #1F3A5F;
            --primary-200: #4d648d;
            --primary-300: #acc2ef;
            --accent-100: #3D5A80;
            --accent-200: #cee8ff;
            --text-100: #FFFFFF;
            --text-200: #e0e0e0;
            --bg-100: #0F1C2E;
            --bg-200: #1f2b3e;
            --bg-300: #374357;
        }
        
        /* Global styles */
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Main container */
        .main {
            background-color: var(--bg-100);
            color: var(--text-100);
        }
        
        /* Cards */
        .card {
            background-color: var(--bg-200);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            border: 1px solid var(--primary-200);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Headers */
        h1, h2, h3 {
            color: var(--text-100) !important;
            font-weight: 600 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Metrics */
        .stMetric {
            background-color: var(--bg-200);
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid var(--primary-200);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--primary-200);
            color: var(--text-100);
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: var(--primary-100);
            transform: translateY(-2px);
        }
        
        /* Input fields */
        .stTextInput>div>div>input {
            background-color: var(--bg-300);
            color: var(--text-100);
            border: 1px solid var(--primary-200);
            border-radius: 8px;
            padding: 0.5rem;
        }
        
        /* Slider */
        .stSlider>div>div>div {
            background-color: var(--primary-200);
        }
        
        /* Plotly charts */
        .js-plotly-plot {
            background-color: var(--bg-200) !important;
            border-radius: 15px;
            padding: 10px;
        }
        
        /* Success and error messages */
        .stSuccess {
            background-color: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stError {
            background-color: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff0000;
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Custom container for sleep entry */
        .sleep-entry {
            background-color: var(--bg-200);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid var(--primary-200);
        }
        </style>
    """, unsafe_allow_html=True)

# Configure Streamlit theme
def configure_theme():
    st.set_page_config(
        page_title="Sleep Monitor Dashboard",
        page_icon="🌙",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom plot theme
def apply_plot_theme(fig, height=400):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Poppins",
            size=12,
            color="#FFFFFF"
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        height=height,
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        )
    )
    return fig

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="sql8.freesqldatabase.com",
        user="sql8783645",
        password="bXwTUfpwue",
        database="sql8783645",
        port=3306
    )

# Update existing tables
def update_database_schema():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if sleep_quality column exists
    cursor.execute("SHOW COLUMNS FROM sleep_log LIKE 'sleep_quality'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE sleep_log ADD COLUMN sleep_quality INT CHECK (sleep_quality BETWEEN 1 AND 5)")
    
    # Check if notes column exists
    cursor.execute("SHOW COLUMNS FROM sleep_log LIKE 'notes'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE sleep_log ADD COLUMN notes TEXT")
    
    # Check if created_at column exists
    cursor.execute("SHOW COLUMNS FROM sleep_log LIKE 'created_at'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE sleep_log ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    conn.commit()
    cursor.close()
    conn.close()

# Create tables
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create sleep_log table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleep_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            date DATE NOT NULL,
            sleep_time TIME NOT NULL,
            wake_time TIME NOT NULL,
            sleep_quality INT CHECK (sleep_quality BETWEEN 1 AND 5),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Update existing tables with new columns
    update_database_schema()

# Calculate sleep duration
def calculate_sleep_duration(sleep_time, wake_time):
    sleep_dt = datetime.combine(date.today(), sleep_time)
    wake_dt = datetime.combine(date.today(), wake_time)
    
    if wake_dt < sleep_dt:
        wake_dt += timedelta(days=1)
    
    duration = wake_dt - sleep_dt
    return duration.total_seconds() / 3600  # Convert to hours

# Authenticate user
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Register user
def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return True
    except mysql.connector.errors.IntegrityError:
        return False
    finally:
        conn.close()

# Save sleep entry
def save_sleep_data(user_id, log_date, sleep_time, wake_time, sleep_quality, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sleep_log 
           (user_id, date, sleep_time, wake_time, sleep_quality, notes) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, log_date, sleep_time, wake_time, sleep_quality, notes)
    )
    conn.commit()
    conn.close()

# Load user sleep logs
def load_user_data(user_id):
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT 
            date,
            TIME_FORMAT(sleep_time, '%H:%i:%s') as sleep_time,
            TIME_FORMAT(wake_time, '%H:%i:%s') as wake_time,
            sleep_quality,
            notes,
            CASE 
                WHEN TIME_TO_SEC(wake_time) < TIME_TO_SEC(sleep_time) 
                THEN (TIME_TO_SEC(wake_time) + 86400 - TIME_TO_SEC(sleep_time)) / 3600
                ELSE (TIME_TO_SEC(wake_time) - TIME_TO_SEC(sleep_time)) / 3600
            END as duration
        FROM sleep_log 
        WHERE user_id = {user_id} 
        ORDER BY date DESC
    """, conn)
    
    # Convert time columns to proper datetime format
    df['sleep_time'] = pd.to_datetime(df['sleep_time'], format='%H:%M:%S').dt.time
    df['wake_time'] = pd.to_datetime(df['wake_time'], format='%H:%M:%S').dt.time
    
    conn.close()
    return df

# App Pages
def login_page():
    st.title("🛌 Sleep Monitor - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id = authenticate_user(username, password)
        if user_id:
            st.session_state["user_id"] = user_id
            st.session_state["username"] = username
            st.session_state["page"] = "dashboard"
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.markdown("Don't have an account?")
    if st.button("Sign Up"):
        st.session_state["page"] = "signup"
        st.rerun()

def signup_page():
    st.title("📝 Sign Up")
    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Register"):
        if register_user(username, password):
            st.success("Registration successful! Please log in.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("Username already exists.")

def calculate_sleep_metrics(df):
    """Calculate detailed sleep metrics"""
    metrics = {}
    
    # Basic metrics
    metrics['avg_duration'] = df['duration'].mean()
    metrics['avg_quality'] = df['sleep_quality'].mean()
    
    # Consistency metrics
    metrics['duration_std'] = df['duration'].std()
    metrics['quality_std'] = df['sleep_quality'].std()
    
    # Sleep schedule consistency
    df['sleep_hour'] = pd.to_datetime(df['sleep_time'].astype(str), format='%H:%M:%S').dt.hour
    metrics['sleep_time_std'] = df['sleep_hour'].std()
    
    # Sleep efficiency (assuming 8 hours is optimal)
    metrics['efficiency'] = (df['duration'] / 8).mean() * 100
    
    # Quality distribution
    quality_dist = df['sleep_quality'].value_counts(normalize=True) * 100
    metrics['quality_dist'] = quality_dist.reset_index()
    metrics['quality_dist'].columns = ['quality', 'percentage']
    
    # Weekly patterns
    df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
    weekly_avg = df.groupby('weekday')['duration'].mean()
    metrics['weekly_pattern'] = weekly_avg.reset_index()
    metrics['weekly_pattern'].columns = ['weekday', 'duration']
    
    return metrics

def create_sleep_heatmap(df):
    """Create a heatmap of sleep patterns by hour and weekday"""
    df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
    df['hour'] = pd.to_datetime(df['sleep_time'].astype(str), format='%H:%M:%S').dt.hour
    
    # Create pivot table for heatmap
    heatmap_data = pd.pivot_table(
        df,
        values='duration',
        index='weekday',
        columns='hour',
        aggfunc='mean'
    )
    
    # Reorder weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(weekday_order)
    
    return heatmap_data

def dashboard():
    st.title("🌙 Sleep Monitor Dashboard")
    
    # Load user data
    df = load_user_data(st.session_state['user_id'])
    
    # Create two columns for the main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sleep Entry Form
        with st.container():
            st.markdown("### Log Today's Sleep")
            today = date.today()
            
            # Set default times
            default_sleep_time = datetime.strptime("22:00", "%H:%M").time()
            default_wake_time = datetime.strptime("06:00", "%H:%M").time()
            
            time_col1, time_col2 = st.columns(2)
            with time_col1:
                sleep_time = st.time_input("Sleep Time", value=default_sleep_time)
            with time_col2:
                wake_time = st.time_input("Wake Time", value=default_wake_time)
            
            sleep_quality = st.slider("Sleep Quality (1-5)", 1, 5, 3)
            notes = st.text_area("Notes (optional)")
            
            if st.button("Submit Sleep Log"):
                duration = calculate_sleep_duration(sleep_time, wake_time)
                
                if duration <= 0:
                    st.error("Wake time must be after sleep time!")
                elif duration > 24:
                    st.error("Sleep duration cannot be more than 24 hours!")
                elif duration < 1:
                    st.error("Sleep duration seems too short. Please check your times.")
                else:
                    save_sleep_data(st.session_state['user_id'], today, sleep_time, wake_time, sleep_quality, notes)
                    st.success(f"Sleep data saved successfully! Duration: {duration:.1f} hours")
                    st.rerun()
    
    with col2:
        # Quick Stats
        if not df.empty:
            metrics = calculate_sleep_metrics(df)
            
            st.markdown("### Quick Stats")
            st.metric("Average Sleep Duration", f"{metrics['avg_duration']:.1f} hours")
            st.metric("Average Sleep Quality", f"{metrics['avg_quality']:.1f}/5")
            st.metric("Sleep Efficiency", f"{metrics['efficiency']:.1f}%")
            
            # Sleep Quality Distribution
            fig_quality = px.pie(df, names='sleep_quality', 
                               title='Sleep Quality Distribution',
                               color_discrete_sequence=px.colors.sequential.Plasma_r)
            fig_quality = apply_plot_theme(fig_quality, height=300)
            st.plotly_chart(fig_quality, use_container_width=True, config={'displayModeBar': False})
    
    # Main Content Area
    if not df.empty:
        st.markdown("### Sleep Analysis")
        
        # Date Range Filter
        date_range = st.date_input(
            "Select Date Range",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max()
        )
        
        if len(date_range) == 2:
            mask = (df['date'] >= date_range[0]) & (df['date'] <= date_range[1])
            filtered_df = df.loc[mask]
            metrics = calculate_sleep_metrics(filtered_df)
            
            # Detailed Metrics
            st.markdown("### Detailed Sleep Metrics")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Sleep Duration Consistency", 
                         f"{metrics['duration_std']:.1f} hours std",
                         delta=f"{metrics['avg_duration']:.1f} hours avg")
            
            with metric_col2:
                st.metric("Sleep Quality Consistency", 
                         f"{metrics['quality_std']:.1f} std",
                         delta=f"{metrics['avg_quality']:.1f} avg")
            
            with metric_col3:
                st.metric("Sleep Time Consistency", 
                         f"{metrics['sleep_time_std']:.1f} hours std")
            
            # Create two columns for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Sleep Duration Trend
                fig_duration = px.line(filtered_df, x='date', y='duration',
                                     title='Sleep Duration Trend',
                                     labels={'duration': 'Hours', 'date': 'Date'})
                fig_duration = apply_plot_theme(fig_duration, height=400)
                st.plotly_chart(fig_duration, use_container_width=True, config={'displayModeBar': False})
            
            with chart_col2:
                # Sleep Quality Trend
                fig_quality = px.line(filtered_df, x='date', y='sleep_quality',
                                    title='Sleep Quality Trend',
                                    labels={'sleep_quality': 'Quality (1-5)', 'date': 'Date'})
                fig_quality = apply_plot_theme(fig_quality, height=400)
                st.plotly_chart(fig_quality, use_container_width=True, config={'displayModeBar': False})
            
            # Weekly Pattern Analysis
            st.markdown("### Weekly Sleep Patterns")
            fig_weekly = px.bar(metrics['weekly_pattern'],
                              x='weekday', y='duration',
                              title='Average Sleep Duration by Day',
                              labels={'duration': 'Hours', 'weekday': 'Day of Week'})
            fig_weekly = apply_plot_theme(fig_weekly, height=400)
            st.plotly_chart(fig_weekly, use_container_width=True, config={'displayModeBar': False})
            
            # Sleep Duration Distribution
            st.markdown("### Sleep Patterns")
            fig_dist = px.histogram(filtered_df, x='duration',
                                  title='Sleep Duration Distribution',
                                  labels={'duration': 'Hours'},
                                  nbins=20)
            fig_dist = apply_plot_theme(fig_dist, height=400)
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
            
            # Quality Distribution Analysis
            st.markdown("### Sleep Quality Analysis")
            quality_col1, quality_col2 = st.columns(2)
            
            with quality_col1:
                # Quality Distribution
                fig_quality_dist = px.bar(metrics['quality_dist'],
                                        x='quality', y='percentage',
                                        title='Sleep Quality Distribution',
                                        labels={'quality': 'Quality Rating', 'percentage': 'Percentage'})
                fig_quality_dist = apply_plot_theme(fig_quality_dist, height=400)
                st.plotly_chart(fig_quality_dist, use_container_width=True, config={'displayModeBar': False})
            
            with quality_col2:
                # Quality vs Duration
                fig_quality_duration = px.scatter(filtered_df,
                                                x='duration', y='sleep_quality',
                                                title='Sleep Quality vs Duration',
                                                labels={'duration': 'Hours', 'sleep_quality': 'Quality'})
                fig_quality_duration = apply_plot_theme(fig_quality_duration, height=400)
                st.plotly_chart(fig_quality_duration, use_container_width=True, config={'displayModeBar': False})
            
            # Recent Notes
            if 'notes' in filtered_df.columns and not filtered_df['notes'].isna().all():
                st.markdown("### Recent Sleep Notes")
                recent_notes = filtered_df[filtered_df['notes'].notna()].head(5)
                for _, row in recent_notes.iterrows():
                    st.markdown(f"""
                        <div class="card">
                            <strong>{row['date']}</strong><br>
                            {row['notes']}
                        </div>
                    """, unsafe_allow_html=True)
    
    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# Initialize the app
configure_theme()
apply_custom_style()

# Main logic
initialize_database()

if "user_id" not in st.session_state:
    st.session_state["page"] = st.session_state.get("page", "login")

if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "signup":
    signup_page()
elif st.session_state["page"] == "dashboard":
    dashboard()
