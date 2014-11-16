import argparse
import cStringIO
import errno
import itertools
import json
import os
import re
import shutil
import sys
import zipfile

import bs4
import requests

BASE_URL = 'http://www.mathworks.com/matlabcentral/fileexchange'
TAG_REGEX = re.compile(r'([\w\s]+)(?:\(\d+\))?')


def http_get(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 5
    try:
        return requests.get(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None


# From http://stackoverflow.com/a/600612/281108
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def extractall(archive, path):
    "A version of ZipFile.extractall that doesn't choke on utf-8 filenames."
    for filename in archive.namelist():
        dest_filename = os.path.join(path, filename.decode('cp437'))
        if dest_filename.endswith('/'):
            mkdir_p(dest_filename)
            continue
        mkdir_p(os.path.dirname(dest_filename))
        with archive.open(filename) as src, open(dest_filename, 'w') as dest:
            shutil.copyfileobj(src, dest)


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

    def download(self, path='.'):
        metadata = self.get_metadata()
        if metadata is None:
            return None

        response = http_get(self.url + '?download=true')
        if response is None:
            return None

        path = os.path.join(path, self.name)
        mkdir_p(path)
        download_filename = response.url.split('/')[-1]
        if download_filename.endswith('.zip'):
            try:
                with zipfile.ZipFile(cStringIO.StringIO(response.content)) as f:
                    extractall(f, path)
            except zipfile.BadZipfile:
                return None
        else:
            with open(os.path.join(path, download_filename), 'w') as f:
                f.write(response.text.encode('utf-8'))
        return dict(name=self.name, url=self.url, **metadata)

    def get_metadata(self):
        response = http_get(self.url)
        if response is None:
            return None
        soup = bs4.BeautifulSoup(response.text)

        metadata = {}
        tags_div = soup.find('div', id='all_tags')
        raw_tags = [a.get_text().strip() for a in tags_div.find_all('a')]
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
        metadata['date_updated'] = metadata['date_submitted']
        date_span = details.find('span', itemprop='datePublished')
        if date_span is not None:
            metadata['date_updated'] = date_span.text
        return metadata


def download_projects(dest_dir, num_projects, sort):
    def helper():
        for page in itertools.count(1):
            params = dict(page=page, term='type:Function', sort=sort)
            response = http_get(BASE_URL, params=params)
            if response is None:
                continue
            soup = bs4.BeautifulSoup(response.text)
            for title in soup.find_all('p', attrs={'class': 'file_title'}):
                project = Project(title.a['href'])
                print 'Downloading %s...' % project.name,
                sys.stdout.flush()
                project_json = project.download(dest_dir)
                if project_json is None:
                    print 'failed.'
                else:
                    print 'done.'
                    yield project_json
    return itertools.islice(helper(), num_projects)


def parse_args():
    parser = argparse.ArgumentParser(
        description='download files from MatlabCentral')
    parser.add_argument(
        '--num_projects', default=10, type=int,
        help='Number of projects to fetch.')
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


def main():
    args = parse_args()
    projects = list(download_projects(args.to, args.num_projects, args.sort))
    with open(os.path.join(args.to, 'manifest.json'), 'w') as f:
        json.dump({'projects': projects}, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()
