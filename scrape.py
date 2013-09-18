import argparse
import cStringIO
import os
import zipfile

import bs4
import requests

BASE_URL = 'http://www.mathworks.com/matlabcentral/fileexchange'
INDEX_URL = BASE_URL + '/index'


class Project(object):
    def __init__(self, url):
        self.url = url
        self.download_url = '%s?download=true' % self.url
        self.name = url.split('/')[-1]

    def __repr__(self):
        return '<Project: %s>' % self.name

    def download(self, path=None):
        if path is None:
            path = self.name
        response = requests.get(self.download_url)
        archive = zipfile.ZipFile(cStringIO.StringIO(response.content))
        archive.extractall(path)


def fetch_projects_from_fileindex(start_page=1, pages=10):
    for page in xrange(start_page, start_page + pages):
        params = dict(page=page, term='type:Function', sort='downloads_desc')
        page_html = requests.get(BASE_URL, params=params).text
        soup = bs4.BeautifulSoup(page_html)
        for title in soup.find_all('p', attrs={'class': 'file_title'}):
            yield Project(title.a['href'])


def parse_args():
    parser = argparse.ArgumentParser(
        description='download files from MatlabCentral')
    parser.add_argument('--dry_run', action='store_true',
        help='List found projects, without downloading.')
    parser.add_argument('--pages', default=1, type=int,
        help='Number of fileindex pages to crawl.')
    parser.add_argument('--to', default='',
        help='Directory to download projects to (default current).')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    for project in fetch_projects_from_fileindex(pages=args.pages):
        print 'Found %s.' % project.name
        if not args.dry_run:
            download_path = os.path.join(args.to, project.name)
            print 'Downloading to %s...' % download_path,
            project.download(download_path)
            print 'done.'
