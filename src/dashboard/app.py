"""
Streamlit Dashboard for Political Alignment Analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data.data_manager import DataManager
from src.analysis.alignment_analyzer import AlignmentAnalyzer
from src.api.congress_client import CongressClient

# Page configuration
st.set_page_config(
    page_title="Alignator - Political Alignment Analysis",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize data components"""
    return DataManager(), AlignmentAnalyzer(), CongressClient()

data_manager, analyzer, client = init_components()

# Sidebar
st.sidebar.title("🏛️ Alignator")
st.sidebar.markdown("Political Alignment Analysis Dashboard")

# Navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Overview", "Member Analysis", "Party Analysis", "Data Explorer", "Settings"]
)

# Main content
if page == "Overview":
    st.title("Political Alignment Analysis Dashboard")
    st.markdown("Analyze political alignment of Congress members through bills and voting patterns")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        members = data_manager.get_members()
        st.metric("Total Members", len(members))
    
    with col2:
        bills = data_manager.get_bills()
        st.metric("Total Bills", len(bills))
    
    with col3:
        # Count analyzed members
        analyzed_count = 0
        for member in members:
            analysis = data_manager.get_alignment_analysis(member.get('id'))
            if analysis:
                analyzed_count += 1
        st.metric("Analyzed Members", analyzed_count)
    
    with col4:
        # Average alignment score
        alignment_scores = []
        for member in members:
            analysis = data_manager.get_alignment_analysis(member.get('id'))
            if analysis and 'alignment_score' in analysis:
                alignment_scores.append(analysis['alignment_score'])
        
        avg_alignment = np.mean(alignment_scores) if alignment_scores else 0
        st.metric("Avg Alignment Score", f"{avg_alignment:.3f}")
    
    # Alignment distribution chart
    st.subheader("Political Alignment Distribution")
    
    if alignment_scores:
        fig = px.histogram(
            x=alignment_scores,
            nbins=20,
            title="Distribution of Political Alignment Scores",
            labels={'x': 'Alignment Score', 'y': 'Count'},
            color_discrete_sequence=['#1f77b4']
        )
        fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Center")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Show recent bills
    if bills:
        recent_bills = bills[-10:]  # Last 10 bills
        bill_df = pd.DataFrame([
            {
                'Title': bill.get('title', 'N/A'),
                'Sponsor': bill.get('sponsorId', 'N/A'),
                'Type': bill.get('billType', 'N/A'),
                'Number': bill.get('billNumber', 'N/A')
            }
            for bill in recent_bills
        ])
        st.dataframe(bill_df, use_container_width=True)

elif page == "Member Analysis":
    st.title("Individual Member Analysis")
    
    # Member selection
    members = data_manager.get_members()
    member_options = {f"{m.get('name', 'Unknown')} ({m.get('party', 'Unknown')})": m.get('id') 
                     for m in members}
    
    selected_member_name = st.selectbox("Select Member", list(member_options.keys()))
    selected_member_id = member_options[selected_member_name]
    
    if selected_member_id:
        # Get member analysis
        analysis = data_manager.get_alignment_analysis(selected_member_id)
        
        if not analysis:
            st.info("No analysis available for this member. Running analysis...")
            with st.spinner("Analyzing member..."):
                analysis = analyzer.analyze_member(selected_member_id)
        
        if analysis:
            # Member info
            member_info = analysis.get('member_info', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Name", member_info.get('name', 'N/A'))
                st.metric("Party", member_info.get('party', 'N/A'))
            
            with col2:
                st.metric("State", member_info.get('state', 'N/A'))
                st.metric("Chamber", member_info.get('chamber', 'N/A'))
            
            with col3:
                alignment_score = analysis.get('alignment_score', 0)
                ideology = analysis.get('ideology_score', 'Unknown')
                st.metric("Alignment Score", f"{alignment_score:.3f}")
                st.metric("Ideology", ideology)
            
            # Alignment visualization
            st.subheader("Political Alignment")
            
            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = alignment_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Political Alignment"},
                delta = {'reference': 0},
                gauge = {
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [-1, -0.3], 'color': "lightcoral"},
                        {'range': [-0.3, 0.3], 'color': "lightyellow"},
                        {'range': [0.3, 1], 'color': "lightblue"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Text Analysis")
                text_analysis = analysis.get('text_analysis', {})
                
                st.metric("Sentiment", f"{text_analysis.get('sentiment', 0):.3f}")
                st.metric("Liberal Score", f"{text_analysis.get('liberal_score', 0):.3f}")
                st.metric("Conservative Score", f"{text_analysis.get('conservative_score', 0):.3f}")
            
            with col2:
                st.subheader("Voting Analysis")
                voting_analysis = analysis.get('voting_analysis', {})
                
                st.metric("Party Alignment", f"{voting_analysis.get('party_alignment', 0):.3f}")
                st.metric("Vote Consistency", f"{voting_analysis.get('vote_consistency', 0):.3f}")
                st.metric("Total Votes", voting_analysis.get('total_votes', 0))
            
            # Topic analysis
            st.subheader("Topic Analysis")
            topic_scores = analysis.get('topic_scores', {})
            
            if topic_scores:
                topic_data = []
                for topic_name, topic_info in topic_scores.items():
                    topic_data.append({
                        'Topic': topic_name,
                        'Top Words': ', '.join(topic_info.get('words', [])),
                        'Weight': topic_info.get('weight', 0)
                    })
                
                topic_df = pd.DataFrame(topic_data)
                st.dataframe(topic_df, use_container_width=True)
            else:
                st.info("No topic analysis available")

elif page == "Party Analysis":
    st.title("Party Analysis")
    
    # Run party analysis
    if st.button("Analyze All Parties"):
        with st.spinner("Analyzing parties..."):
            party_analysis = analyzer.get_party_analysis()
        
        if party_analysis:
            # Party comparison chart
            st.subheader("Party Alignment Comparison")
            
            party_data = []
            for party, data in party_analysis.items():
                party_data.append({
                    'Party': party,
                    'Member Count': data['member_count'],
                    'Avg Alignment Score': data['avg_alignment_score'],
                    'Avg Ideology Score': data['avg_ideology_score']
                })
            
            party_df = pd.DataFrame(party_data)
            
            # Alignment score comparison
            fig = px.bar(
                party_df,
                x='Party',
                y='Avg Alignment Score',
                title="Average Alignment Score by Party",
                color='Avg Alignment Score',
                color_continuous_scale='RdBu'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Member count by party
            fig2 = px.pie(
                party_df,
                values='Member Count',
                names='Party',
                title="Member Distribution by Party"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Detailed party breakdown
            st.subheader("Detailed Party Breakdown")
            st.dataframe(party_df, use_container_width=True)

elif page == "Data Explorer":
    st.title("Data Explorer")
    
    # Data type selection
    data_type = st.selectbox("Select Data Type", ["Members", "Bills", "Votes"])
    
    if data_type == "Members":
        members = data_manager.get_members()
        if members:
            member_df = pd.DataFrame([
                {
                    'ID': m.get('id'),
                    'Name': m.get('name'),
                    'Party': m.get('party'),
                    'State': m.get('state'),
                    'Chamber': m.get('chamber'),
                    'District': m.get('district')
                }
                for m in members
            ])
            st.dataframe(member_df, use_container_width=True)
    
    elif data_type == "Bills":
        bills = data_manager.get_bills()
        if bills:
            bill_df = pd.DataFrame([
                {
                    'ID': b.get('id'),
                    'Title': b.get('title'),
                    'Type': b.get('billType'),
                    'Number': b.get('billNumber'),
                    'Sponsor': b.get('sponsorId'),
                    'Congress': b.get('congress')
                }
                for b in bills
            ])
            st.dataframe(bill_df, use_container_width=True)

elif page == "Settings":
    st.title("Settings")
    
    st.subheader("API Configuration")
    
    # Check API key
    api_key = os.getenv('CONGRESS_API_KEY')
    if api_key:
        st.success("✓ API key configured")
        st.text(f"Key: {api_key[:10]}...")
    else:
        st.error("✗ API key not found")
        st.info("Please set CONGRESS_API_KEY in your .env file")
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Fetch Members"):
            with st.spinner("Fetching members..."):
                try:
                    members = client.get_members()
                    data_manager.save_members(members)
                    st.success(f"Fetched {len(members)} members")
                except Exception as e:
                    st.error(f"Error fetching members: {e}")
        
        if st.button("Fetch Bills"):
            with st.spinner("Fetching bills..."):
                try:
                    bills = client.get_bills()
                    data_manager.save_bills(bills)
                    st.success(f"Fetched {len(bills)} bills")
                except Exception as e:
                    st.error(f"Error fetching bills: {e}")
    
    with col2:
        if st.button("Clear All Data"):
            if st.checkbox("I understand this will delete all data"):
                # This would need to be implemented in DataManager
                st.warning("Data clearing not implemented yet")
        
        if st.button("Export Data"):
            st.info("Export functionality not implemented yet")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Data from Congress.gov API")
