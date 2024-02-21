import arxiv
from scholarly import scholarly
from backend.tools.logger import LoggerSetup
import os

class Paper:
    def __init__(self, paper_url):
        self.paper_url = paper_url
        self.paper_metadata = None 
        self.author_metadata = None
        logging_setup = LoggerSetup('Paper')
        self.logger = logging_setup.get_logger()
        self.logger.info('Paper object created with URL: %s', paper_url)
    
    def get_paper(self, download=False):
        self.logger.info('Extracting paper data...')
        self.paper_metadata = self.screen_paper(self.paper_url, download=download)
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

    def screen_paper(self, url, download=False):
        id = url.split('/')[-1]
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[id])))
        data = {'title': paper.title, 
            'authors': [x.name for x in paper.authors], 
            'summary': paper.summary,  
            'published': paper.published,
            'pdf_url': paper.pdf_url,  
        }
        if download:
            self.logger.info('Downloading paper...')
            try:
                os.mkdir('./papers')
            except FileExistsError:
                pass
            paper.download_pdf(dirpath=f"{os.environ['TMP']}", filename=paper.title.replace('/', '_'))  # Adjusted to handle titles with slashes
            self.logger.info('%s downloaded.', data['title'])
        return data

    def stalk_author(self, author):
        keys = ['name', 'affiliation', 'interests', 'citedby', 'citedby5y', 'hindex', 'hindex5y', 'i10index', 'i10index5y', 'cites_per_year']
        # try:
        _author = scholarly.fill(next(scholarly.search_author(author)))
        data = {key: _author.get(key, 'N/A') for key in keys}  # Use get to avoid KeyError if a key doesn't exist
        if 'publications' in _author:
            dat = {} 

            for paper in _author.get('publications', []):
                temp = {} 
                temp['year']  = paper['bib'].get('pub_year', 'N/A')
                temp['citation'] = paper['bib'].get('citation', 'N/A')
                temp['citations'] = paper['num_citations']
                dat[paper['bib'].get('title', 'N/A')] = temp 
                
                if paper['bib'].get('title', 'N/A') == self.paper_metadata['title']:
                    self.paper_metadata['citations'] = paper['num_citations']

        data['publications'] = dat
        self.logger.info('Data done: %s', str(data))    
        return data
        # except Exception as e:
        #     self.logger.error('Error processing author %s', author)
        #     return None 
        #     pass 


