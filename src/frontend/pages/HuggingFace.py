import streamlit as st
from frontend.components.Sidebar import Sidebar

class Home: 
  def __init__(self): 
    pass

  def render(self):  
    st.subheader('Github')
    hf_link = st.text_input(
        label='',
        placeholder="Enter the URL here:",
        label_visibility='collapsed',
        help="Ensure it's a valid link, and that you have access to the repository!",
        key="github"
    )
    if st.button(label="Send", use_container_width=True, type="primary", key="git_send"): 
      st.success(f'Beginning to process the repository {hf_link}!')    
        
class UI: 
  def __init__(self):
    if 'OPENAI_API_KEY' not in st.session_state: 
      st.session_state['OPENAI_API_KEY'] = None 
    if 'GITHUB_AUTH_TOKEN' not in st.session_state: 
      st.session_state['GITHUB_AUTH_TOKEN'] = None 

  def render(self):     
    Sidebar().render()
    Home().render()

if __name__ == "__main__":
    UI().render()
