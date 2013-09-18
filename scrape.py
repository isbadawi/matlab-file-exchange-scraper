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

    # The way downloads work on MatlabCentral is that the download link
    # redirects you to the url of the actual file you're downloading.
    # Instead of following the redirect automatically, we manually get
    # the value of the Location: header; this lets us get at the name of
    # the downloaded file (and so we can tell whether it's a zip, etc.)
    def download(self, path, extract_archives=True):
        response = requests.head(self.download_url, allow_redirects=False)
        real_download_url = response.headers['Location']
        download_filename = real_download_url.split('/')[-1]
        response = requests.get(real_download_url)
        if extract_archives and download_filename.endswith('.zip'):
            archive = zipfile.ZipFile(cStringIO.StringIO(response.content))
            archive.extractall(path)
        else:
            with open(os.path.join(path, download_filename), 'w') as f:
                f.write(response.text)

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
    parser.add_argument('--extract_archives', type=bool, default=True,
        help='If true, automatically extract archives.')
    parser.add_argument('--to', default='',
        help='Directory to download projects to (default current).')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    for project in fetch_projects_from_fileindex(pages=args.pages):
        print 'Found %s.' % project.name
        if not args.dry_run:
            download_path = os.path.join(args.to, project.name)
            os.makedirs(download_path)
            print 'Downloading to %s...' % download_path,
            project.download(download_path, extract_archives=args.extract_archives)
            print 'done.'
