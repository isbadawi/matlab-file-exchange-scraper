import argparse
import cStringIO
import itertools
import json
import os
import re
import zipfile

import bs4
import requests

BASE_URL = 'http://www.mathworks.com/matlabcentral/fileexchange'
TAG_REGEX = re.compile(r'([\w\s]+)(?:\(\d+\))?')


def get_soup(*args, **kwargs):
    return bs4.BeautifulSoup(requests.get(*args, **kwargs).text)


class Project(object):
    def __init__(self, url):
        self.url = url
        self.name = url.split('/')[-1]

    def __repr__(self):
        return '<Project: %s>' % self.name

    # The way downloads work on MatlabCentral is that the download link
    # redirects you to the url of the actual file you're downloading.
    # Instead of following the redirect automatically, we manually get
    # the value of the Location: header; this lets us get at the name of
    # the downloaded file (and so we can tell whether it's a zip, etc.)
    def download(self, path, extract_archives=True):
        download_url = '%s?download=true' % self.url
        response = requests.head(download_url, allow_redirects=False)
        real_download_url = response.headers['Location']
        download_filename = real_download_url.split('/')[-1]
        response = requests.get(real_download_url)
        if extract_archives and download_filename.endswith('.zip'):
            archive = zipfile.ZipFile(cStringIO.StringIO(response.content))
            archive.extractall(path)
        else:
            with open(os.path.join(path, download_filename), 'w') as f:
                f.write(response.text)

    def get_tags(self):
        soup = get_soup(self.url)
        tags_div = soup.find('div', id='all_tags')
        raw_tags = tags_div.get_text().strip().split('\n\n')[0].split(', ')
        tags = []
        for tag in raw_tags:
            match = TAG_REGEX.match(tag)
            if match:
                tags.append(match.group(1))
        return tags

    def get_json(self):
        return dict(name=self.name, url=self.url, tags=self.get_tags())


def fileindex_projects():
    for page in itertools.count(1):
        params = dict(page=page, term='type:Function', sort='downloads_desc')
        soup = get_soup(BASE_URL, params=params)
        for title in soup.find_all('p', attrs={'class': 'file_title'}):
            yield Project(title.a['href'])


def parse_args():
    parser = argparse.ArgumentParser(
        description='download files from MatlabCentral')
    parser.add_argument(
        '--num_projects', default=10, type=int,
        help='Number of projects to fetch.')
    parser.add_argument(
        '--extract_archives', type=bool, default=True,
        help='If true, automatically extract archives.')
    parser.add_argument(
        '--to', default='',
        help='Directory to download projects to (default current).')
    return parser.parse_args()


def main():
    args = parse_args()
    projects = []
    for project in itertools.islice(fileindex_projects(), args.num_projects):
        download_path = os.path.join(args.to, project.name)
        os.makedirs(download_path)
        print 'Downloading %s to %s...' % (project.name, download_path),
        project.download(download_path, args.extract_archives)
        print 'done.'
        projects.append(project.get_json())
    with open(os.path.join(args.to, 'manifest.json'), 'w') as f:
        json.dump({'projects': projects}, f, indent=2)

if __name__ == '__main__':
    main()
