import streamlit as st

class Sidebar: 
  def __init__(self): 
    pass 

  def render(self):
    with st.sidebar: 
      st.markdown(
          """
          <style>
              [data-testid=stSidebar] [data-testid=stImage]{
                  text-align: center;
                  display: block;
                  margin-left: auto;
                  margin-right: auto;
                  border-radius: 50%;
                  margin-top: -75px;
              }
          </style>
          """, unsafe_allow_html=True
      )
      
    st.header('Settings')

    # self.get_openai()
    self.get_github()

  def get_openai(self): 
    disabled = False 
    if st.session_state['OPENAI_API_KEY']:
      disabled = True
    key = st.sidebar.text_input('', placeholder ='Input your OpenAI API Key: ', type='password', label_visibility='hidden', key='api_key_input', disabled=disabled)
    
    if key: 
      st.session_state['api_key'] = key
      st.sidebar.success('API Key Successfully Added!')
  

  def get_github(self): 
    disabled = False 
    if st.session_state['GITHUB_AUTH_TOKEN']:
      disabled = True
    key = st.sidebar.text_input('', placeholder ='Input your Github PAT Key: ', type='password', label_visibility='hidden', key='token_input', disabled=disabled)
    
    if key: 
      st.session_state['GITHUB_AUTH_TOKEN'] = key
      st.sidebar.success('Token Successfully Added!')