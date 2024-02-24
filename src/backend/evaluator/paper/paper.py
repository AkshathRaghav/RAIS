import arxiv
from scholarly import scholarly
from backend.tools.logger import LoggerSetup  
from backend.tools.depot import Depot
import os, json
from datetime import datetime

class Paper:
    def __init__(self, paper_url, depot: Depot):
        logging_setup = LoggerSetup('Paper')
        self.logger = logging_setup.get_logger()
        self.paper_url = paper_url
        if depot.mapping.get(paper_url):
            self.logger.info('Paper already processed. Skipping...')
            return
        self.paper_metadata = None
        self.author_metadata = None
        self.paper = None 
        self.logger.info('Paper object created with URL: %s', paper_url)
    
    def get_paper(self):
        self.logger.info('Extracting paper data...')
        self.paper_metadata = self.screen_paper(self.paper_url)
        self.logger.info('%s extracted.', self.paper_metadata['title'])
        self.author_metadata = {}
        for author in self.paper_metadata['authors']:
            self.logger.info('Processing author: %s', author)
            try:
                self.author_metadata[author] = self.stalk_author(author)
                self.logger.info('%s processed.', author)
            except Exception as e:
                self.author_metadata[author] = None
                self.logger.warning('%s could not be processed. Error: %s', author, e)
        self.logger.info('Extraction and processing completed.')

    def screen_paper(self, url):
        id = url.split('/')[-1]
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[id])))
        self.paper = paper
        data = {'title': paper.title, 
                'authors': [x.name for x in paper.authors], 
                'summary': paper.summary,  
                'published': paper.published.strftime("%m/%d/%Y"),
                'pdf_url': paper.pdf_url}
        return data

    def save(self, path): 
        sub_path = self.paper_url.split('/')[-1]
        sub_path = os.path.join(path, sub_path)
        os.makedirs(sub_path, exist_ok=True)

        self.logger.info('Downloading paper...')
        self.paper.download_pdf(dirpath=sub_path, filename=f'{self.paper.title.replace("/", "_")}.pdf')  
        self.logger.info('Downloaded.')

        self.logger.info('Saving paper metadata...')
        with open(os.path.join(sub_path, 'metadata.json'), 'w') as file:
            json.dump(self.paper_metadata, file)
        self.logger.info('Metadata saved.')

        self.logger.info('Saving author metadata...')
        for author in self.author_metadata:
            if self.author_metadata[author]:
                with open(os.path.join(path, 'authors', f'{author}.json'), 'w') as file:
                        json.dump(self.author_metadata[author], file)
            self.logger.info('Author metadata saved.')

        return { 
            'paper': os.path.join(sub_path, f'{self.paper.title.replace("/", "_")}.pdf'),
            'metadata': os.path.join(sub_path, 'metadata.json'),
            'authors': [os.path.join(path, 'authors', f'{author}.json') for author in self.author_metadata if self.author_metadata[author]]
        }


    def stalk_author(self, author):
        keys = ['name', 'affiliation', 'interests', 'citedby', 'citedby5y', 'hindex', 'hindex5y', 'i10index', 'i10index5y', 'cites_per_year']
        try:
            _author = scholarly.fill(next(scholarly.search_author(author)))
            data = {key: _author.get(key, 'N/A') for key in keys}  
            dat = {} 

            for paper in _author.get('publications', []):
                temp = {
                    'year': paper['bib'].get('pub_year', 'N/A'),
                    'citation': paper['bib'].get('citation', 'N/A'),
                    'citations': paper.get('num_citations', 'N/A')
                }
                title = paper['bib'].get('title', 'N/A')
                dat[title] = temp
                
                if title == self.paper_metadata['title']:
                    self.paper_metadata['citations'] = paper.get('num_citations', 'N/A')

            data['publications'] = dat
            self.logger.info('Data done')    
            return data
        except Exception as e:
            self.logger.error('Error processing author %s. Error: %s', author, e)
            return None
