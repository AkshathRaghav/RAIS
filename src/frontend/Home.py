import streamlit as st 
from frontend.components.Sidebar import Sidebar

st.set_page_config(page_title="RAIS", page_icon="🧊", layout="wide", initial_sidebar_state="expanded")

class Home: 
  def __init__(self):
    pass

  def render(self):
    st.markdown( '''<style>
    @import url('https://fonts.googleapis.com/css2?family=Lusitana:wght@400;700&display=swap'); 
    html, body, [class*="css"] {
        font-family: 'Lusitana', sans-serif; 
        font-size: 18px;
        font-weight: 500;
        color: #091747;
    }
    </style>''' , unsafe_allow_html= True)
    st.markdown("<h1 style='text-align: center;'> <i> Reproducible </i>  Artificial Intelligence Software</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,9,1])

    # st.markdown('''<style>
    #   body {
    #       background-color: #eee;
    #   }

    #   .fullScreenFrame > div {
    #       display: flex;
    #       justify-content: center;
    #   }
    #   </style>''', unsafe_allow_html=True)

    # st.image('https://drive.google.com/file/d/1uJgJ9iTV1ZUtSjR9FtLMXW5eYRsrIoUN/view?usp=sharing', caption='Overview of the pipeline', use_column_width=True, output_format = "PNG")

    st.markdown("<h2 style='text-align: left;'>Abstract</h2>", unsafe_allow_html=True)
    st.markdown('''Software written for Artificial Intelligence (AI), more specifically machine learning (ML), has become
      integral parts of many systems. For example, face recognition is widely adopted at airports; voice is used
      to verify customers; computer vision is used by autonomous vehicles. Unfortunately, there is no well-
      established methodology that can ensure the results from AI software is reproducible. In fact, many creators
      of AI software cannot reproduce the results reported by themselves. Prior studies have demonstrated that
      releasing source code alone is insufficient to ensure reproducibility. This project will investigate the methodologies to create Reproducible AI Software (dubbed RAIS). This project's goal is to identify a list of essential
      factors that may contribute (or hurt) reproducibility.''')

class UI: 
  def __init__(self):
    if 'OPENAI_API_KEY' not in st.session_state: 
      st.session_state['OPENAI_API_KEY'] = None 
    if 'GITHUB_AUTH_TOKEN' not in st.session_state: 
      st.session_state['GITHUB_AUTH_TOKEN'] = None 
  


  def render(self):
    st.markdown( '''<style>
    @import url('https://fonts.googleapis.com/css2?family=Lusitana:wght@400;700&display=swap'); 
    html, body, [class*="css"] {z
        font-family: 'Lusitana', sans-serif; 
        font-size: 18px;
        font-weight: 500;
        color: #091747;
    }
    </style>''' , unsafe_allow_html= True)

    st.title('Reproducible Artificial Intelligence Software')
    st.header('*Uncomment all figures and clear .gitignore"s MD files to see the full thing*')
    Sidebar().render()
    
if __name__ == "__main__":
    UI().render()
