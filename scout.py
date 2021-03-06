#!/usr/bin/env python3.5

# Webcrawler based on the asyncio and aiohttp libraries
# Keeps track of links between domains
# (i.e. cnn.com -> cnn.com/news does not count)
# Dumps graph into output file

# NOTE: Occasionally when the queue is large and the number of
# workers is high, the aiohttp library will throw and error
# which I was unable to catch. Overall the error is not something
# to be concerned with since it is rare, but the crawler will
# miss the url that was being requested at that time. The crawler
# will then continue as normal without any real complications

import sys, signal, shutil, lxml
from urllib.parse import urlparse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.request import build_opener

class Scout:
    '''Class for webcrawler'''
    logFile = open('scout.log', 'w')

    ignored = set([ #Ignore some domains to avoid bad links in results
        'ad.doubleclick.net',
        't.co',
        'bit.ly',
        'cs.pn',
        'twitter.com',
        'zh-cn.messenger.com',
        'zh-cn.facebook.com',
        'ar-ar.facebook.com',
        'osf.io'
    ])

    def __init__(self, root, max_workers=10, max_links=100):
        '''Constructor takes in number of links and workers and prepares crawler'''

        self.max_links = max_links
        self.max_workers = max_workers
        self.links_left = max_links
        self.links_hit = 0
        self.visited = set()

        self.graph = dict()

        # Session for which all async http requests will be made
        self.session = aiohttp.ClientSession()

        # Queue each worker will be able to access asynchronously
        self.to_visit = asyncio.Queue()
        if type(root) == type([]): # Root is list
            for link in root:
                self.to_visit.put_nowait((link, True))
                self.links_left -= 1
        else: # Root is string
            self.to_visit.put_nowait((root, True))
            self.links_left -= 1

    @asyncio.coroutine
    def buzz(self):
        '''Creates worker bees to venture into the fields in search of pollen'''

        # Create workers
        tasks = []
        for i in range(self.max_workers):
            tasks.append(asyncio.Task(self.make_request()))

        # Called when all tasks are removed from queue and completed
        yield from self.to_visit.join()
        self.session.close()
        for t in tasks:
            t.cancel()

    @asyncio.coroutine
    def make_request(self):
        '''Each worker grabs a url from the queue and makes the request'''

        while True:
            url, unique = yield from self.to_visit.get()

            yield from self.fetch(url, unique)
            self.to_visit.task_done()

    @asyncio.coroutine
    def fetch(self, url, new_hit):
        '''Worker asynchronously gets page and parses it, then adds new links to queue'''

        self.progress('getting {}'.format(url))
        headers = { 'User-Agent' : 'Mozilla/5.0' } # Need user agent for some sites

        try:
            with aiohttp.Timeout(7):
                response = yield from self.session.get(url, headers=headers, allow_redirects=False)
                body = yield from response.text()

                links = set()
                soup = BeautifulSoup(body, "lxml")

                # Extract all links from body of html
                for tag in soup.find_all('a', href=True):
                    links.add(tag['href'])
                for link in links.difference(self.visited):
                    # Ignore invalid links
                    if self.links_left > 0 and self.is_valid_link(link):
                        unique = self.add_to_graph(url, link)
                        if unique:
                            self.links_left -= 1
                        self.progress('adding {}'.format(link))
                        # Add link to queue
                        self.to_visit.put_nowait((link, unique))
                        self.visited.add(link)
                    elif self.links_left <= 0:
                        break
                yield from response.release()
        except asyncio.TimeoutError as e:
            self.progress('Timed out {}'.format(url))
            self.logFile.write('Timed out {}\n'.format(url))
            pass
        except Exception as e:
            self.progress('Exception {}'.format(e))
            self.logFile.write('Exception in {}: {}\n'.format(url, e))
            pass
        except:
            self.logFile.write('Unexpected error in {}\n'.format(url))
        finally:

            if new_hit: # Only increments when links is between unique domains
                self.links_hit += 1
            self.progress('done with {}'.format(url))



    def progress(self, suffix=''):
        '''Prints progress bar in terminal'''
        try:
            # Calculate width of bar based on terminal size
            t_width = int(shutil.get_terminal_size().columns)
            bar_len = int(t_width) / 3

            # Amount bar is filled
            filled_len = int(round(bar_len * self.links_hit / float(self.max_links)))
            percents = round(100.0 * self.links_hit / float(self.max_links), 1)

            # Create string for bar
            bar = '#' * int(filled_len) + '.' * int(bar_len - filled_len)
            progress = '[' + bar + '] ' + str(percents) + '% {}/{}...'.format(self.links_hit, self.max_links)
            suffix_len = t_width - len(progress) - 1
            progress += suffix[:suffix_len]
            space_len = t_width - len(progress) - 1
            progress += ' ' * space_len + '\r' # Carriage return doesn't make new link, keeps bar in same place

            sys.stdout.write(progress)
            sys.stdout.flush()
        except Exception as e:
            self.logFile.write('Exception printing status {}'.format(e))

    def is_valid_link(self, link):
        '''Determines if links is invalid or in the ignored set'''
        if urlparse(link).scheme is '' or urlparse(link).netloc is '':
            return False
        elif urlparse(link).netloc.replace('www.','') in self.ignored:
            return False
        else:
            return True

    def add_to_graph(self, src, dest):
        '''Add link to the graph if unique domains'''
        src = urlparse(src).netloc.strip('w.')
        dest = urlparse(dest).netloc.strip('w.')
        if src not in self.graph:
            self.graph[src] = [dest]
        elif src == dest:
            return False
        else:
            self.graph[src].append(dest)

        return True

    def dump(self, outFile='output.txt'):
        '''Dump output to file'''
        outFile = open(outFile, 'w')
        for src, links in self.graph.items():
            for link in links:
                outFile.write('{}\t{}\n'.format(src, link))


import getopt

def usage():
    print('''Usage: honey.py [-w WORKERS] [-n LINKS] [-o OUTPUT]

    OPTIONS:

        -w  WORKERS         The number of workers the crawler will utilize

        -l  LINKS           The number of unique links the crawler will follow

        -o  OUTPUT          The output file for the crawler

        -h                  Shows this usage message
    ''')


def main():
    # Parse command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hw:l:o:", ["help"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr)
        usage()
        sys.exit(2)

    max_links = 100
    max_workers = 10
    outFile = 'output.txt'
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o == '-l':
            max_links = int(a)
        elif o == '-w':
            max_workers = int(a)
        elif o == '-o':
            outFile = a
        else:
            assert False, "unhandled option"

    # Get async event loop instance
    loop = asyncio.get_event_loop()
    root = [
            'http://www.cnn.com',
            'http://www.washingtonpost.com',
            'http://www.cbs.com',
            'http://reddit.com',
            'http://buzzfeed.com',
            'http://lolcats.com',
            'http://espn.com',
            'http://att.yahoo.com',
            'http://yahoo.com',
            'http://vox.com',
            'http://nytimes.com',
            'http://wikipedia.org',
            'http://wsj.com',
            'http://usatoday.com',
            'http://fox.com',
            'http://youtube.com',
            'http://linkedin.com',
            'http://msn.com',
            'http://imdb.com',\
            'http://stackoverflow.com',
            'http://wikia.com'
           ]

    scout = Scout(root, max_workers=max_workers, max_links=max_links)
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        loop.run_until_complete(scout.buzz()) # Loop until scout completes
        print('\n')
    except KeyboardInterrupt:
        print('\nExiting gracefully like a bee')
    finally:
        scout.dump(outFile)

if __name__ == '__main__':
    main()

# VIM: let g:syntastic_python_python_exec = '/usr/bin/python3.5'
