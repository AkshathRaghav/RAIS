import os 
import requests
import json
import streamlit as st

ROOT_REPO_DATA_SPECS = [
    {
        'url': 'https://api.github.com/repos/{org}/{repo}/contributors',
        'type': list,
        'data_specs': {
            'members': {'action': 'count'},  # Count the number of items in the response
            'member': {'action': 'extract', 'key': 'login'},  # Extract login from each item (if needed)
        }
    },
    {
        'url': 'https://api.github.com/repos/{org}/{repo}/commits',
        'type': list,
        'data_specs': {
            'commits': {'action': 'count'}, 
            'commit_data': {'action': 'extract', 'key': ['commit']},
        }
    }, 
    {
        'url': 'https://api.github.com/repos/{org}/{repo}/releases',
        'type': list,
        'data_specs': {
            'releases': {'action': 'count'}, 
            'name': {'action': 'extract', 'key': ['name']},
            'tags': {'action': 'extract', 'key': ['tag_name']},
            'body': {'action': 'extract', 'key': ['body']},
        }
    },  
    {
        'url': 'https://api.github.com/repos/{org}/{repo}',
        'type': dict,
        'data_specs': {
            'description': {'action': 'extract', 'key': 'description'},
            'stars': {'action': 'extract', 'key': 'stargazers_count'},
            'watchers': {'action': 'extract', 'key': 'subscribers_count'}, # Seems to be a bug in the API
            'forks': {'action': 'extract', 'key': 'forks_count'},
            'issues': {'action': 'extract', 'key': 'open_issues_count'},
            'default_branch': {'action': 'extract', 'key': 'default_branch'},
            'owner_type': {'action': 'extract', 'key': ['owner', 'type']},
            'organization_type': {'action': 'extract', 'key': ['organization', 'type']},
            'owner': {'action': 'extract', 'key': ['owner', 'login']},
            'organization': {'action': 'extract', 'key': ['organization', 'login']},
            'has_wiki': {'action': 'extract', 'key': 'has_wiki'},
        }
    }, 
    {
        'url': 'https://api.github.com/repos/{org}/{repo}/pulls',
        'type': list,
        'data_specs': {
            'prs': {'action': 'count'}
        }
    }
]

MEMBER_REPO_DATA_SPECS = [ 
    {
        'url': 'https://api.github.com/repos/{org}/{repo}',
        'type': dict,
        'data_specs': {
            'stars': {'action': 'extract', 'key': 'stargazers_count'},
            'forks': {'action': 'extract', 'key': 'forks_count'},
            'issues': {'action': 'extract', 'key': 'open_issues_count'},
            'watchers': {'action': 'extract', 'key': 'subscribers_count'},
        }
    }, 
    {
        'url': 'https://api.github.com/repos/{org}/{repo}/pulls',
        'type': list,
        'data_specs': {
            'prs': {'action': 'count'},
        }
    }
]

MEMBER_DATA_SPECS = [
    {
        'url': 'https://api.github.com/users/{user}/followers',
        'type': list,  # Asserting that the response should be a list
        'data_specs': {
            'followers': {'action': 'count_followers'},  # Count the number of items in the response
        }
    },
    {
        'url': 'https://api.github.com/users/{user}/repos',
        'type': list,  # Assuming that the response should be a list based on the API endpoint
        'data_specs': {
            'repos': {'action': 'extract', 'key': 'full_name'},  
            'repo_count': {'action': 'count'},  # Count the number of items in the response
        }
    }
]


def extract_key(data, key):
    """Extracts a value from a nested dictionary using a key or a list of keys."""
    if isinstance(key, list):
        # Handle nested keys
        for part in key:
            if data is not None and part in data:
                data = data[part]
            else:
                return None
    else:
        # Handle single key
        data = data.get(key, None)
    return data

def count(data):
    """Counts the number of items in a list or keys in a dictionary."""
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        return len(data.keys())
    else:
        return None


def fetch_git_api(url):
    try: 
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer { st.session_state['GITHUB_AUTH_TOKEN']}",
        }
    except: 
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GITHUB_AUTH_TOKEN')}",
        }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def process_repo_data(repo_data_specs, **formattable_vars):
    try: 
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer { st.session_state['GITHUB_AUTH_TOKEN']}",
        }
    except: 
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GITHUB_AUTH_TOKEN')}",
        }
    results = {} 

    for spec in repo_data_specs:
        url = spec['url'].format(**formattable_vars)
        
        if spec['type'] == list: 
            i = 1
            url += "?state=all&page={i}&per_page=100"


            for key in spec['data_specs']:
                if spec['data_specs'][key]['action'] == 'count':
                    results[key] = 0
                elif spec['data_specs'][key]['action'] == 'extract':
                    results[key] = []

            print(url.format(i=i))
            response = fetch_git_api(url.format(i=i))

            if not response:
                response = [] 

            while len(response):
                if not response: 
                    response = [] 
                    
                for tag, detail in spec['data_specs'].items():
                    if detail['action'] == 'count':
                        results[tag] += count(response)
                    elif detail['action'] == 'extract':
                        if spec['type'] == list and isinstance(response, list):
                            results[tag] += [extract_key(item, detail['key']) for item in response]
                        else:
                            results[tag] += [extract_key(response, detail['key'])]

                
                i += 1
                print(url.format(i=i))
                response = fetch_git_api(url.format(i=i))

            print(results)

        else: 
            print(url)
            response = fetch_git_api(url)

            # Ensure the response type matches the expected type
            try: 
                assert isinstance(response, spec['type']), f"Expected response type {spec['type'].__name__}, got {type(response).__name__} for url {url}."
            except: 
                pass 

            if response is None or not isinstance(response, spec['type']):
                continue

            for tag, detail in spec['data_specs'].items():
                if detail['action'] == 'extract':
                    if spec['type'] == list and isinstance(response, list):
                        results[tag] = [extract_key(item, detail['key']) for item in response]
                    else:
                        results[tag] = extract_key(response, detail['key'])

    return results

def process_user_repo_data(repos: list): 
  if len(repos) <= 30:
    count_repo_metadata = {} 
    for repo in repos:
        temp = process_repo_data(MEMBER_REPO_DATA_SPECS, org=repo.split('/')[0], repo=repo.split('/')[1])
        if count_repo_metadata:
            for key in temp: 
                if key not in count_repo_metadata:
                    print('key missing')
                    print(temp)
                    print(count_repo_metadata)
                    print(key)
                    count_repo_metadata[key] = 0 
                count_repo_metadata[key] += temp[key]
        else: 
            count_repo_metadata = temp

        count_repo_metadata = {key: count_repo_metadata[key] + temp[key] for key in temp} if count_repo_metadata else temp
    return count_repo_metadata
  else: 
    return '30+ Repos; Not parsing to save resources.'


class Metadata:
    def __init__(self, **repo_data):
        self.repo_data = repo_data
        self.root_metadata = self.get_root_metadata()
        print(self.root_metadata)
        print('Root metadata done')
        self.organization_metadata = self.get_organization_metadata()
        print('Organization metadata done')
        self.owner_metadata = self.get_owner_metadata()
        print('Owner metadata done')
        self.member_metadata = self.get_member_metadata() 
        print('Member metadata done')

    def get_root_metadata(self):
        return process_repo_data(ROOT_REPO_DATA_SPECS, org=self.repo_data['owner'], repo=self.repo_data['repo'])

    def get_organization_metadata(self):
      organization_metadata = {}
      organization_metadata['name'] = self.root_metadata['organization']
      organization_metadata.update(process_repo_data(MEMBER_DATA_SPECS, user=self.root_metadata['organization']))

      organization_metadata['metadata'] = process_user_repo_data(organization_metadata['repos'])
      return organization_metadata

    def get_owner_metadata(self):
      owner_metadata = {}
      if self.root_metadata['owner_type'] != 'Organization':
          owner_metadata['name'] = self.root_metadata['owner']
          owner_metadata.update(process_repo_data(MEMBER_DATA_SPECS, user=self.root_metadata['owner']))
          organization_metadata['metadata'] = process_user_repo_data(organization_metadata['repos'])
      else: 
        owner_metadata = self.organization_metadata
      return owner_metadata

    def get_member_metadata(self):
      member_metadata = {}
      if int(self.root_metadata['members']) < 31:
        for member in self.root_metadata['member']: 
          member_metadata[member] = process_repo_data(MEMBER_DATA_SPECS, user=member)

        temp = {}
        for member in member_metadata: 
            
          temp[member] = process_user_repo_data(member_metadata[member]['repos'])
        for member in temp: 
          member_metadata[member]['metadata'] = temp[member]

      else: 
        member_metadata['members'] = self.root_metadata['members']
        member_metadata['metadata'] = {key: '30+ Members; Not parsing to save resources.' for key in sub_dict['data_specs'] for sub_dict in MEMBER_REPO_DATA_SPECS}
      return member_metadata
      