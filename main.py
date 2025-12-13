import streamlit as st
from scholarly import scholarly
import graphviz

# --- Page Configuration ---
st.set_page_config(
    page_title="Maryam Bandukda | UCL Research",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
# Your specific Google Scholar ID (Found via search)
# This ensures the map loads YOU immediately without searching.
MY_SCHOLAR_ID = "CpkUcT0AAAAJ" 
MY_NAME = "Maryam Bandukda"

# --- Helper Functions ---

@st.cache_data(show_spinner=False)
def fetch_my_profile():
    """
    Fetches Maryam's specific profile data and caches it 
    so it doesn't reload every time you click a button.
    """
    try:
        author = scholarly.search_author_id(MY_SCHOLAR_ID)
        author = scholarly.fill(author, sections=['basics', 'indices', 'publications', 'coauthors'])
        return author
    except Exception as e:
        return None

def create_mindmap(author):
    """
    Generates the research graph.
    """
    if not author: return None

    dot = graphviz.Digraph(comment='Research Landscape')
    dot.attr(rankdir='LR') 
    dot.attr('node', fontname='Helvetica', shape='box', style='rounded, filled', color='white')
    
    # Root Node
    dot.node('root', author.get('name'), fillcolor='#2b6cb0', fontcolor='white', fontsize='16', shape='doubleoctagon')

    # 1. Interests Branch
    interests = author.get('interests', [])
    if interests:
        dot.node('int_hub', 'Focus Areas', fillcolor='#edf2f7', color='#cbd5e0')
        dot.edge('root', 'int_hub')
        
        # Limit to top 5 interests to keep graph clean
        for i, interest in enumerate(interests[:6]):
            dot.node(f'int_{i}', interest, fillcolor='#e6fffa', color='#b2f5ea')
            dot.edge('int_hub', f'int_{i}')
    
    # 2. Stats Branch
    dot.node('stats', 'Impact', fillcolor='#edf2f7', color='#cbd5e0')
    dot.edge('root', 'stats')
    
    citations = author.get('citedby', 0)
    hindex = author.get('hindex', 0)
    
    dot.node('cit', f"Citations: {citations}", fillcolor='#fffff0', color='#fefcbf')
    dot.node('hin', f"h-index: {hindex}", fillcolor='#fffff0', color='#fefcbf')
    
    dot.edge('stats', 'cit')
    dot.edge('stats', 'hin')

    return dot

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Research Areas", "Publications", "Contact"])
 

st.sidebar.markdown("---")
st.sidebar.caption(f"© 2025 {MY_NAME}")
st.sidebar.caption("Global Disability Innovation Hub\nUniversity College London")

# --- Main Page Logic ---

if page == "Home":
    # Header Section
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Placeholder for your photo. In production, replace URL with your actual photo path.
        st.image("https://profiles.ucl.ac.uk/64376-maryam-bandukda/photo", width=200)
    
    with col2:
        st.title(MY_NAME)
        st.subheader("Senior Research Fellow")
        st.markdown("**Global Disability Innovation Hub | UCL**")
        st.markdown("""
        I am a researcher specializing in **Human-Computer Interaction (HCI)**, **Accessibility**, and **Assistive Technologies**.
        
        My work focuses on enabling and enhancing the experiences of blind and partially sighted people in open spaces through 
        participatory design and co-creation methods. I am currently leading research on mobile technologies to support inclusion 
        in the Global South.
        """)
        
        st.download_button(label="📄 Download CV", data="Placeholder content for CV", file_name="Maryam_Bandukda_CV.pdf")

    st.markdown("---")
    
    # Quick Stats Row
    with st.spinner("Loading latest impact stats..."):
        profile = fetch_my_profile()
    
    if profile:
        c1, c2, c3 = st.columns(3)
        c1.metric("Citations", profile.get('citedby', 0))
        c2.metric("h-index", profile.get('hindex', 0))
        c3.metric("i10-index", profile.get('i10index', 0))

elif page == "Research Landscape":
    st.title("🧠 Research Network")
    st.markdown("Interactive visualization of my research interests and impact.")
    
    with st.spinner("Generating Knowledge Graph..."):
        profile = fetch_my_profile()
        
        if profile:
            graph = create_mindmap(profile)
            st.graphviz_chart(graph, use_container_width=True)
            
            st.info("This map is generated dynamically from live Google Scholar data.")
        else:
            st.error("Could not load research data.")

elif page == "Publications":
    st.title("📚 Selected Publications")
    
    with st.spinner("Fetching publications..."):
        profile = fetch_my_profile()
        
    if profile:
        pubs = profile.get('publications', [])
        
        # 1. Sort by year (Newest -> Oldest)
        # We handle 'None' years by treating them as 0
        pubs.sort(key=lambda x: int(x['bib'].get('pub_year', 0) or 0), reverse=True)
        
        # 2. Variable to track the year headers
        current_year = None
        
        # Loop through ALL publications (removed the [:10] limit)
        for pub in pubs:
            bib = pub['bib']
            title = bib.get('title', 'Untitled')
            year = bib.get('pub_year', 'Unknown Year')
            
            # --- THE GROUPING LOGIC ---
            # If this paper's year is different from the last one we printed...
            if year != current_year:
                # ...print a new Big Year Heading
                st.markdown(f"### {year}")
                st.markdown("---") # Add a line for visual separation
                current_year = year
            # --------------------------
            
            # Display the paper under the year
            # We use a cleaner layout without expanders for a CV-style look
            st.markdown(f"**{title}**")
            
            # Helper to create the Google Scholar link
            if 'author_pub_id' in pub:
                link = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={MY_SCHOLAR_ID}&citation_for_view={pub['author_pub_id']}"
                st.caption(f"[View Details]({link})")
            else:
                st.caption("No link available")
            
            # precise spacing between papers
            st.write("") 

    else:
        st.write("Publications could not be loaded.")

elif page == "Contact":
    st.title("📬 Get in Touch")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Connect")
        st.markdown(f"""
        - **Email:** [m.bandukda@ucl.ac.uk](mailto:m.bandukda@ucl.ac.uk)
        - **LinkedIn:** [Maryam Bandukda](https://www.linkedin.com/search/results/all/?keywords=Maryam%20Bandukda)
        - **Twitter/X:** [@MaryamBandukda](https://twitter.com/)
        """)
    
    with c2:
        st.subheader("Office")
        st.markdown("""
        Global Disability Innovation Hub  
        University College London  
        Marshgate, London E20 2AE  
        United Kingdom
        """)
