import streamlit as st
from frontend.components.Sidebar import Sidebar
from backend.evaluator.repository.github.github import Github

@st.cache
def get_stuff(owner, repo, branch, _git):
  return { 
    'repo_data': _git.repo_data,
    'file_tree': _git.file_tree
  }

class Home: 
  def __init__(self): 
    self.git = None 

  def render(self):  
    st.subheader('Github')
    st.markdown('Specify the branch!')
    col1, col2 = st.columns(2)
    with col1: 
      github_link = st.text_input(
          label='',
          placeholder="Enter the URL here:",
          label_visibility='collapsed',
          help="Ensure it's a valid link, and that you have access to the repository!",
          key="github"
      )
    with col2:
      branch = st.text_input(
          label='',
          placeholder="Enter the branch here:",
          label_visibility='collapsed',
          help="Ensure it's a valid branch!",
          key="branch"
      )
    
    if st.button(label="Send", use_container_width=True, type="primary", key="git_send") and github_link and branch: 
      if st.session_state['GITHUB_AUTH_TOKEN']:
        st.success(f'Beginning to process the repository {github_link} on {branch}!')   
        self.process(github_link, branch) 
      
        st.download_button(
            label="Download Github Metadata",
            data=csv,
            file_name='meta.json',
            mime='application/json',
        )
      else: 
        st.error('Please enter your Github `Personal Access Token`')

  def process(self, link, branch): 
    owner, repo = link.split('/')[3], link.split('/')[4]
    print(owner, repo, branch)
    self.git = Github(owner=owner, repo=repo, branch=branch)  
    st.write('Making File Tree..')
    self.git.get_tree() 
    with st.expander('File Tree', expanded=False): 
      st.write(str(self.git.tree))
    st.write('Enriching File Tree..')
    self.git.enrich_tree()
    with st.expander('Enriched File Tree', expanded=False): 
      st.write(str(self.git.tree))
    st.write('Getting Metadata..')
    self.git.get_meta()
    with st.expander('Meta', expanded=False): 
      st.write(str(self.git.meta))
  
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
