import streamlit as st  # Streamlit for building web dashboards
import pandas as pd      # Pandas for data loading and manipulation
import plotly.express as px  # Plotly Express for interactive charts

# Set dashboard page title, icon, and layout
st.set_page_config(
    page_title="Global Steel Plants Dashboard",
    page_icon="🏭",
    layout="wide"  # Wide layout to fit multiple charts side by side
)

# Function to load and cache data for better performance
@st.cache_data
def load_data():
    df = pd.read_csv('processed_data/steel_plants_cleaned.csv')  # Main dataset with plant details
    capacity_by_region = pd.read_csv('processed_data/capacity_by_region.csv', index_col=0)  # Aggregated capacity per region
    capacity_by_company = pd.read_csv('processed_data/capacity_by_company.csv', index_col=0)  # Aggregated capacity per company
    plants_by_country = pd.read_csv('processed_data/plants_by_country.csv', index_col=0)  # Count of plants by country
    return df, capacity_by_region, capacity_by_company, plants_by_country

# Load all datasets into variables
df, capacity_by_region, capacity_by_company, plants_by_country = load_data()

# Dashboard title and subtitle
st.title("🏭 Global Steel Plants Dashboard")
st.markdown("**Interactive visualization of operating steel plants worldwide**")
st.markdown("---")  # Horizontal separator

# Sidebar section for interactive filters
with st.sidebar:
    st.header("Filters")

    # Filter by region
    regions = st.multiselect(
        "Select Region(s)",
        options=sorted(df['Region'].unique()),  # Unique regions in dataset
        default=[]
    )

    # Filter by country
    countries = st.multiselect(
        "Select Country(ies)",
        options=sorted(df['Country/Area'].unique()),  # Unique countries
        default=[]
    )

    # Filter by company/owner
    companies = st.multiselect(
        "Select Company(ies)",
        options=sorted(df['Owner'].unique()),  # Unique owners
        default=[]
    )

    # Get min and max capacity for slider range
    capacity_min = float(df['Nominal crude steel capacity (ttpa)'].min())
    capacity_max = float(df['Nominal crude steel capacity (ttpa)'].max())

    # Slider to filter by plant capacity
    capacity_range = st.slider(
        "Capacity Range (ttpa)",
        min_value=capacity_min,
        max_value=capacity_max,
        value=(capacity_min, capacity_max)  # Default full range
    )

    st.markdown("---")
    st.markdown("**Data Source:**")
    st.markdown("Global Iron and Steel Tracker (Sept 2025)")  # Source reference

# Apply selected filters to the dataframe
filtered_df = df.copy()  # Start with full dataset

if regions:  # Filter by selected regions if any
    filtered_df = filtered_df[filtered_df['Region'].isin(regions)]

if countries:  # Filter by selected countries if any
    filtered_df = filtered_df[filtered_df['Country/Area'].isin(countries)]

if companies:  # Filter by selected companies if any
    filtered_df = filtered_df[filtered_df['Owner'].isin(companies)]

# Filter by capacity range
filtered_df = filtered_df[
    (filtered_df['Nominal crude steel capacity (ttpa)'] >= capacity_range[0]) &
    (filtered_df['Nominal crude steel capacity (ttpa)'] <= capacity_range[1])
]

# Display key metrics in four columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Plants", f"{len(filtered_df):,}")  # Count of filtered plants

with col2:
    total_capacity = filtered_df['Nominal crude steel capacity (ttpa)'].sum()
    st.metric("Total Capacity", f"{total_capacity:,.0f} ttpa")  # Sum of capacities

with col3:
    avg_capacity = filtered_df['Nominal crude steel capacity (ttpa)'].mean()
    st.metric("Average Capacity", f"{avg_capacity:,.0f} ttpa")  # Mean capacity

with col4:
    num_countries = filtered_df['Country/Area'].nunique()
    st.metric("Countries", f"{num_countries}")  # Number of countries represented

st.markdown("---")

# Global map showing plant locations with size representing capacity
st.subheader("Global Distribution Map")

fig_map = px.scatter_geo(
    filtered_df,
    lat='latitude',
    lon='longitude',
    size='Nominal crude steel capacity (ttpa)',  # Bubble size proportional to capacity
    color='Region',  # Color by region
    hover_name='Plant name (English)',  # Show plant name on hover
    hover_data={
        'Owner': True,  # Show owner
        'Nominal crude steel capacity (ttpa)': ':.0f',  # Show capacity rounded
        'Country/Area': True,  # Show country
        'latitude': False,  # Hide lat/lon to reduce clutter
        'longitude': False
    },
    title='Steel Plants by Location and Capacity',
    projection='natural earth',
    size_max=20  # Maximum bubble size
)

fig_map.update_layout(
    height=500,
    geo=dict(
        showland=True,
        landcolor='rgb(243, 243, 243)',  # Light gray land
        coastlinecolor='rgb(204, 204, 204)',
        showocean=True,
        oceancolor='rgb(230, 245, 255)',  # Soft blue ocean
        showcountries=True,
        countrycolor='rgb(204, 204, 204)'  # Gray country borders
    )
)

st.plotly_chart(fig_map, use_container_width=True)  # Render map chart

st.markdown("---")

# Top countries and companies by number of plants
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 15 Countries")
    top_countries = filtered_df['Country/Area'].value_counts().head(15)  # Top countries by plant count
    fig_countries = px.bar(
        x=top_countries.values,
        y=top_countries.index,
        orientation='h',
        title='Number of Plants by Country',
        labels={'x': 'Number of Plants', 'y': 'Country'},
        color=top_countries.values,  # Color intensity based on count
        color_continuous_scale='Blues'
    )
    fig_countries.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=500)
    st.plotly_chart(fig_countries, use_container_width=True)

with col2:
    st.subheader("Top 15 Companies")
    top_companies = filtered_df['Owner'].value_counts().head(15)  # Top companies by number of plants
    fig_companies = px.bar(
        x=top_companies.values,
        y=top_companies.index,
        orientation='h',
        title='Number of Plants by Company',
        labels={'x': 'Number of Plants', 'y': 'Company'},
        color=top_companies.values,
        color_continuous_scale='Greens'
    )
    fig_companies.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=500)
    st.plotly_chart(fig_companies, use_container_width=True)

st.markdown("---")

# Regional capacity distribution and top companies by capacity
col1, col2 = st.columns(2)

with col1:
    st.subheader("Regional Capacity Distribution")
    region_capacity = filtered_df.groupby('Region')['Nominal crude steel capacity (ttpa)'].sum().reset_index()  # Sum by region
    fig_region = px.pie(
        region_capacity,
        values='Nominal crude steel capacity (ttpa)',
        names='Region',
        title='Capacity by Region',
        hole=0.3  # Donut chart
    )
    fig_region.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.subheader("Top 10 Companies by Capacity")
    company_capacity = filtered_df.groupby('Owner')['Nominal crude steel capacity (ttpa)'].sum().sort_values(ascending=False).head(10)  # Top companies by capacity
    fig_cap = px.bar(
        x=company_capacity.values,
        y=company_capacity.index,
        orientation='h',
        title='Total Capacity by Company',
        labels={'x': 'Capacity (ttpa)', 'y': 'Company'},
        color=company_capacity.values,  # Color intensity by capacity
        color_continuous_scale='Oranges'
    )
    fig_cap.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    st.plotly_chart(fig_cap, use_container_width=True)

st.markdown("---")

# Display detailed plant data in a table for further exploration
st.subheader("Plant Data")
display_columns = [
    'Plant name (English)',
    'Owner',
    'Country/Area',
    'Region',
    'Nominal crude steel capacity (ttpa)',
    'Plant age (years)'
]
st.dataframe(
    filtered_df[display_columns].sort_values('Nominal crude steel capacity (ttpa)', ascending=False),
    use_container_width=True,
    height=400  # Fixed height to avoid excessive scrolling
)

st.markdown("---")
st.markdown("*Dashboard created for Research and Emerging Topics Lab 1*")  # Footer note
