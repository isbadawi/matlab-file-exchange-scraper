import argparse
import contextlib
import cStringIO
import itertools
import json
import os
import re
import sys
import zipfile

import bs4
import requests

BASE_URL = 'http://www.mathworks.com/matlabcentral/fileexchange'
TAG_REGEX = re.compile(r'([\w\s]+)(?:\(\d+\))?')


def get_soup(*args, **kwargs):
    return bs4.BeautifulSoup(requests.get(*args, **kwargs).text)


class Project(object):
    def __init__(self, url_or_name):
        if url_or_name.startswith(BASE_URL):
            self.url = url_or_name
        else:
            self.url = '%s/%s' % (BASE_URL, url_or_name)

    def __repr__(self):
        return '<Project: %s>' % self.name

    @property
    def name(self):
        return self.url.split('/')[-1]

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
                f.write(response.text.encode('utf-8'))

    def get_metadata(self):
        metadata = {}
        soup = get_soup(self.url)

        tags_div = soup.find('div', id='all_tags')
        raw_tags = tags_div.get_text().strip().split('\n\n')[0].split(', ')
        tags = []
        for tag in raw_tags:
            match = TAG_REGEX.match(tag)
            if match:
                tags.append(match.group(1))
        metadata['tags'] = tags

        details = soup.find('div', id='details')

        metadata['title'] = details.h1.text
        metadata['summary'] = details.find('p', id='summary').text

        author_link = details.find('p', id='author').a
        metadata['author'] = author_link.text
        metadata['author_url'] = author_link['href']

        metadata['date_submitted'] = details.find(
            'span', id='submissiondate').text.strip()
        date_span = details.find('span', id='date_updated')
        if date_span is not None:
            metadata['date_updated'] = date_span.text[len('(Updated '):-1]
        return metadata

    def get_json(self):
        data = dict(name=self.name, url=self.url)
        data.update(self.get_metadata())
        return data


def fileindex_projects(num_projects, sort):
    def helper():
        for page in itertools.count(1):
            params = dict(page=page, term='type:Function', sort=sort)
            soup = get_soup(BASE_URL, params=params)
            for title in soup.find_all('p', attrs={'class': 'file_title'}):
                yield Project(title.a['href'])
    return itertools.islice(helper(), num_projects)


def parse_args():
    parser = argparse.ArgumentParser(
        description='download files from MatlabCentral')
    parser.add_argument(
        '--num_projects', default=10, type=int,
        help='Number of projects to fetch.')
    parser.add_argument(
        '--extract_archives', type=bool, default=True,
        help='If true, automatically extract archives.')
    SORT_CHOICES = ('downloads_desc', 'downloads_asc',
                    'date_desc_updated', 'date_asc_updated',
                    'date_desc_submitted', 'date_asc_submitted',
                    'comments_desc', 'comments_asc',
                    'ratings_desc', 'ratings_asc')
    parser.add_argument(
        '--sort', choices=SORT_CHOICES, default='downloads_desc',
        help='Sorting criteria.')
    parser.add_argument(
        '--to', default='',
        help='Directory to download projects to (default current).')
    return parser.parse_args()


@contextlib.contextmanager
def status(message):
    print '%s...' % message,
    sys.stdout.flush()
    yield
    print 'done.'


def main():
    args = parse_args()
    projects = []
    for project in fileindex_projects(args.num_projects, args.sort):
        download_path = os.path.join(args.to, project.name)
        os.makedirs(download_path)
        with status('Downloading %s' % project.name):
            project.download(download_path, args.extract_archives)
        projects.append(project.get_json())
    with open(os.path.join(args.to, 'manifest.json'), 'w') as f:
        json.dump({'projects': projects}, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()
