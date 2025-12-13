import streamlit as st
from scholarly import scholarly
import graphviz
from datetime import date
from streamlit_option_menu import option_menu
import nltk
from nltk.corpus import stopwords
from collections import Counter
import re

# --- Constants ---
# Your specific Google Scholar ID (Found via search)
# This ensures the map loads YOU immediately without searching.
MY_SCHOLAR_ID = "CpkUcT0AAAAJ" 
MY_NAME = "Maryam Bandukda"
YEAR = date.today().year
THEME_COUNT=4
IMAGE_URL = "Maryam.jpg"

# --- FIX: DOWNLOAD NLTK DATA ---
# This forces the download to happen effectively both locally and on the cloud
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
# -------------------------------

# ... rest of your code ...


# --- Page Configuration ---
st.set_page_config(
    page_title="Maryam Bandukda | UCL Research",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Helper Functions ---

# Download necessary NLTK data (run once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def generate_ai_interests(publications):
    """
    Uses NLP to analyze publication titles and extract key research themes.
    """
    # 1. Harvest all titles
    titles = [pub['bib'].get('title', '').lower() for pub in publications]
    all_text = " ".join(titles)
    
    # 2. Clean Text (Remove numbers and punctuation)
    all_text = re.sub(r'[^a-z\s]', '', all_text)
    
    # 3. Define Stopwords (Words to ignore)
    stop_words = set(stopwords.words('english'))
    # Add academic "filler" words that aren't useful themes
    custom_stops = {'study', 'analysis', 'using', 'based', 'approach', 'review', 
                   'system', 'design', 'towards', 'understanding', 'evaluation', 
                   'exploring', 'impact', 'challenges', 'survey', 'framework'}
    stop_words.update(custom_stops)
    
    # 4. Tokenize
    words = [w for w in all_text.split() if w not in stop_words and len(w) > 3]
    
    # 5. Bigram Analysis (Find common 2-word phrases)
    # "Visual Impairment" is more useful than just "Visual" or "Impairment"
    bigrams = zip(words, words[1:])
    bigram_counts = Counter(bigrams)
    
    # Get top 7 themes
    top_themes = bigram_counts.most_common(THEME_COUNT)
    
    # Format as strings ("visual impairment")
    return [f"{t[0]} {t[1]}".title() for t, _ in top_themes]

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
    if not author: return None

    dot = graphviz.Digraph(comment='Research Areas')
    dot.attr(rankdir='LR')
    dot.attr('node', fontname='Helvetica', shape='box', style='rounded, filled', penwidth='0')
    
    # --- DATA PREP ---
    # 1. Try to get AI generated themes from publications first
    ai_themes = []
    if 'publications' in author:
        ai_themes = generate_ai_interests(author['publications'])
    
    # 2. Fallback to manual interests if AI found nothing (e.g. no papers listed)
    manual_interests = author.get('interests', [])
    
    # Decide which to show
    if ai_themes:
        display_interests = ai_themes
        hub_label = "AI-Generated Themes"
        hub_color = "#E8F5E9" # Green tint for AI

    if manual_interests:
        hub_label_manual = "Focus Areas"
        hub_color_manual = "#edf2f7" # Grey tint for manual

    # --- DRAWING ---
    # Root
    dot.node('root', f"<{author.get('name')}>", shape='box', fillcolor='#000000', fontcolor='white', width='1.5')

    # Interests Branch
    if display_interests:
        dot.node('ai_interests', hub_label, fontcolor='#000000')
        dot.edge('root', 'ai_interests', color='#00A3E0', penwidth='2')
        
        for i, topic in enumerate(ai_themes):
            dot.node(f'topic_{i}', topic, fillcolor=hub_color, fontcolor='#2D3748')
            dot.edge('ai_interests', f'topic_{i}', color='#cfd8dc')
        
    if manual_interests:
        dot.node('focus_areas', hub_label_manual, fontcolor='#000000')
        dot.edge('root', 'focus_areas', color='#00A3E0', penwidth='2')

        for i, topic in enumerate(manual_interests):
            dot.node(f'topic_{i}', topic, fillcolor=hub_color_manual, fontcolor='#2D3748')
            dot.edge('focus_areas', f'topic_{i}', color='#cfd8dc')

    # Stats Branch (Simplified for brevity)
    #citations = author.get('citedby', 0)
    #dot.node('stats', f"Citations\n{citations}", shape='rectangle', fillcolor='#E3F2FD', fontcolor='#1565C0')
    #dot.edge('root', 'stats', style='dashed')

    return dot

# --- Sidebar Navigation ---
with st.sidebar:
    # This creates a nice clean menu with icons
    page = option_menu(
        menu_title="Navigation",  # Title (keep empty for cleaner look)
        options=["Home", "Research Areas", "Publications", "Contact"],
        icons=["house", "diagram-3", "book", "envelope"], # Bootstrap icons
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#2b6cb0"},
        }
    )

st.sidebar.markdown("---")
st.sidebar.caption(f"© {YEAR} {MY_NAME}")
st.sidebar.caption("University College London")

# --- Main Page Logic ---

if page == "Home":
    # Header Section
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Placeholder for your photo. In production, replace URL with your actual photo path.
        st.image(IMAGE_URL)
    
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

elif page == "Research Areas":
    st.title("Research Areas")
    st.markdown("Interactive visualization of my research interests and impact.")
    
    with st.spinner("Generating Knowledge Graph..."):
        profile = fetch_my_profile()
        
        if profile:
            graph = create_mindmap(profile)
            st.graphviz_chart(graph)
            
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
            num_citations = pub['num_citations']
            year = bib.get('pub_year', 'Unknown Year')
            print(num_citations)
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
            #st.markdown(f"**{title}**")
            
            # Helper to create the Google Scholar link
            link = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={MY_SCHOLAR_ID}&citation_for_view={pub['author_pub_id']}"
            with st.expander(f"{title}"):
                st.write(f"Citations: {num_citations}")
                st.write(f"View Details: {link}")
            # precise spacing between papers
            st.write("") 

    else:
        st.write("Publications could not be loaded.")

elif page == "Projects":
    st.title("🚀 Ongoing Projects")
    
    st.markdown("""
    - **Inclusive Navigation for All:** Developing mobile applications to assist blind and partially sighted individuals in navigating urban environments.
    - **Assistive Technology in the Global South:** Researching affordable and effective assistive technologies tailored for low-resource settings.
    - **Participatory Design Workshops:** Engaging with communities to co-create solutions that address their unique accessibility challenges.
    """)

elif page == "Contact":
    st.title("📬 Get in Touch")
    st.markdown(f"""
    - **Email:** [m.bandukda@ucl.ac.uk](mailto:m.bandukda@ucl.ac.uk)
    - **LinkedIn:** [Maryam Bandukda](https://www.linkedin.com/search/results/all/?keywords=Maryam%20Bandukda)
    """)
