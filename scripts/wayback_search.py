from datetime import date, timedelta, datetime
import urllib.parse
import dateparser
import requests
import argparse
import json
import csv
import re
import os


DEBUG = 0


POLICY_DIR = '../privacy-policies-through-time/'
# these are strings that signal the start/end of the wayback inserted html/js material in an
# archived webpage - we use them to strip out the company's part of the archived page
WAYBACK_HEADER_END = '<!-- END WAYBACK TOOLBAR INSERT -->'
WAYBACK_FOOTER_START = '<div id="footer">'
POLICY_BOOKENDS = [
    ('<div id="main">', '<div id="footer">'),
    ('</head>', '<footer'),
]
REGEX_DUP_WHITESPACE = re.compile(r'  +', flags=re.IGNORECASE)
REGEX_DUP_NEWLINE = re.compile(r'\s*\n\s+')
REGEX_LINK_TAG = re.compile(r'<link.*?>')
REGEX_SCRIPT_TAG = re.compile(r'\<script.*?\</script\>', flags=re.DOTALL)
REGEX_STYLE_TAG = re.compile(r'\<style.*?\</style\>', flags=re.DOTALL)
REGEX_TAGS = re.compile('<[^<]+?>')
REGEX_POLICY_DATE_LIST = [
    re.compile(r'Last Revision: (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last Revised: (\w+ \d+, \d+)'),
    re.compile(r'posted as of:? (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last modified: (\w+ \d+, \d+)'),
    re.compile(r'(\d+-\d+-\d+) privacy policy'),
    re.compile(r'effective as of (\w+ \d+, \d+)'),
    re.compile(r'last modified on (\w+ \d+, \d+)'),
    re.compile(r'Effective Date: (\w+ \d+\w+ \d+)'),
    re.compile(r'Effective Date: (\w+ \d+, \d+)'),
    re.compile(r'Last Updated: *(\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last Updated: *(\d+ \w+ \d+)', flags=re.IGNORECASE),
    re.compile(r'Last revised on (\w+ \d+, \d+)'),
    re.compile(r'Revised: (\w+ \d+, \d+)'),
    re.compile(r'Revised ([^\.]*)'),
    re.compile(r'last updated in ([^\.]*)'),
    re.compile(r'last updated on (.*) \('),
    re.compile(r'last updated on (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'last updated on ([^\.]*)', flags=re.IGNORECASE),
    re.compile(r'Privacy Policy dated (.*)\n'),
    re.compile(r'Last update:? (\w+ \d+, \d+)'),
    re.compile(r'LAST UPDATED (\w+ \d+, \d+)\n', flags=re.IGNORECASE),
    re.compile(r'Updated: (.*)\n', flags=re.IGNORECASE),
    re.compile(r'Effective:? (.*)\n', flags=re.IGNORECASE),
    re.compile(r'Effective: (\w+ \d+, \d+)', flags=re.IGNORECASE)
]


def print_debug(msg):
    if DEBUG:
        print(msg)
    return


# https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# https://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
def month_year_iter(start_month, start_year, end_month, end_year):
    ym_start = 12 * start_year + start_month - 1
    ym_end = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m + 1


def api_query(url):
    #print('api_query: {}'.format(url))
    #resp = requests.get(url=url, auth=(self.user, self.pw), verify=False)
    resp = requests.get(url=url)
    data = None
    if resp.status_code != 200:
        print('failed to retrieve data from {0}'.format(url))
        print('status_code={0}'.format(resp.status_code))
    else:
        data = resp.json()
    return data


def remove_wayback(page):
    """
    Given a wayback archive url, this function will remove all wayback inserted
    text from the html and return just the original page

    Args:
        page: str, text of webpage to process

    Returns:
        str
    """
    # if retrieved via api, wayback header/toolbar is not present
    header_end_index = page.find(WAYBACK_HEADER_END)
    if header_end_index >= 0:
        page = page[header_end_index + len(WAYBACK_HEADER_END):]
    else:
        print('wayback header not found')
    footer_start_index = page.rfind(WAYBACK_FOOTER_START)
    if footer_start_index >= 0:
        page = page[:footer_start_index]
    else:
        print('wayback footer not found')
    return page


def make_policy_comparable(page, policy_bookends, timestamp):
    """
    Returns:
        str, specially formatted for comparison
        str, formatted for printing
    """

    # trim by start and end
    print_debug('make_policy_comparable: {}'.format(timestamp))
    print_debug('start = {}'.format(len(page)))
    for start, end in policy_bookends:
        start_index = page.find(start)
        end_index = page.rfind(end)
        if start_index == -1:
            #print('policy start "{}" not found'.format(start))
            start_index = 0
        if end_index == -1:
            #print('policy end "{}" not found'.format(end))
            end_index = len(page)

        page = page[start_index:end_index]

    print_debug('after bookends = {}'.format(len(page)))

    # remove timestamps as they are unique and inserted by wayback
    page = page.replace(timestamp, '')
    print_debug('after timestamp = {}'.format(len(page)))

    # remove all <script> and <style> blocks
    page = REGEX_SCRIPT_TAG.sub('', page)
    print_debug('after <script> = {}'.format(len(page)))
    page = REGEX_STYLE_TAG.sub('', page)
    print_debug('after <style> = {}'.format(len(page)))

    # remove all tags because we want only the text
    page = REGEX_TAGS.sub('', page)
    print_debug('after tags = {}'.format(len(page)))

    # replace duplicate whitespace
    page = REGEX_DUP_WHITESPACE.sub(' ', page)
    print_debug('after whitespace = {}'.format(len(page)))

    # replace duplicate newlines
    page = REGEX_DUP_NEWLINE.sub('\n', page)
    print_debug('after newlines = {}'.format(len(page)))

    return page
    pretty = page

    # remove all newlines for comparison
    compare = page.replace('\n', '')

    return compare, pretty


def get_update_date(page, regex_list):
    for regex in regex_list:
        m = regex.search(page)
        update_date = None
        if m and len(m.group()) > 1:
            try:
                # print(m.group(1))
                update_date = dateparser.parse(m.group(1))
                # print(update_date)
            except RecursionError as exc:
                print(exc)
            break
    if not update_date:
        print('update date not found!')
    return update_date


def read_config_file(path):
    data = None
    with open(path) as f:
        data = json.load(f)
    return data


def go_wayback(url, timestamp):

    url = urllib.parse.quote(url)
    request_url = 'http://archive.org/wayback/available?url={}&timestamp={}'.format(url, timestamp)
    data = api_query(request_url)
    update_date = None
    out = None

    archive = data.get('archived_snapshots', {}).get('closest', {})
    archive_url = archive.get('url', None)
    archive_timestamp = archive.get('timestamp', None)

    return archive_url, archive_timestamp


def make_policy_file_name(company, update_date):
    out_date = update_date.strftime('%Y-%m-%d')
    out = '{}/{}-{}.txt'.format(company, company, out_date)
    out_path = os.path.join(POLICY_DIR, out)
    return out_path, out


def process_policy(company, archive_url, archive_timestamp, last_date, write=True):
    """
    """
    update_date = None
    out = None

    resp = requests.get(url=archive_url)
    if resp.status_code != 200:
        print('failed to retrieve data from {0}'.format(url))
    else:
        page = resp.text

        # it is debatable if this provides value
        #page = remove_wayback(page)

        # trim policy
        page = make_policy_comparable(page, POLICY_BOOKENDS, archive_timestamp)
        update_date = get_update_date(page, regex_list=REGEX_POLICY_DATE_LIST)

        # check dates
        if update_date and last_date and update_date == last_date:
            print('{} no change'.format(archive_timestamp))
        else:
            last_date = update_date
            if update_date:
                out_path, out = make_policy_file_name(company, update_date)
            else:
                out = '{}_check_date.txt'.format(archive_timestamp)
                out_path = out
            if write:
                with open(out_path, 'wb') as f:
                    f.write(page.encode('UTF-8'))

                print('{} ({}) written to {}'.format(archive_timestamp, update_date, out))

    return update_date, out


def parse_args():

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', type=str, required=True, help='Company config file for searching')
    parser.add_argument('-a', '--abort', action='store_true', required=False, help='Aborts config if cannot find date')
    args = parser.parse_args()

    # arg sanity check
    if not os.path.exists(args.config):
        raise ValueError('Config {} does not exist!'.format(args.config))

    return args


def main():

    args = parse_args()
    config = read_config_file(args.config)
    print(config)
    rows = list()
    company = config.get('company')
    os.makedirs(os.path.join(POLICY_DIR, company), exist_ok=True)

    links = config.get('links', None)
    if links:
        # for when we have the direct links to previous policies
        for link in links:
            policy_date, policy_path = process_policy(company, link, 'linked', None)
            if not policy_date:
                # failed to read date from document, do we have it in config?
                dates = config.get('dates', list())
                for d in dates:
                    if link == d[0]:
                        policy_date = dateparser.parse(d[1])
                        print('Found date in config: {}'.format(policy_date))
                        out_path, out = make_policy_file_name(company, policy_date)
                        os.rename(policy_path, out_path)
                        print('Moved _check_date to {}'.format(out_path))
            row = [policy_date, link, policy_path]
            rows.append(row)

    configs = config.get('configs', None)
    if configs:

        for cfg in config['configs']:

            policy_url = cfg.get('url')
            date_url = cfg.get('date_url', None)
            ignores = cfg.get('ignore', list())
            print('Searching {}'.format(policy_url))
            start_cfg = cfg.get('start')
            start_date = date(start_cfg.get('year'), start_cfg.get('month'), start_cfg.get('day'))
            print('Starting with {}'.format(start_date))
            end_cfg = cfg.get('end', None)
            if end_cfg:
                end_date = date(end_cfg.get('year'), end_cfg.get('month'), end_cfg.get('day'))
            else:
                end_date = date.today()
            print('Ending with {}'.format(end_date))

            # iterate through dates, query wayback, retrieve snapshots
            # if snapshot is new, then get page source; else, continue
            snapshots = list()
            last_page = ''
            last_date = None
            for year, month in month_year_iter(start_date.month, start_date.year, end_date.month, end_date.year):

                row = [company]

                check_date = date(year, month, 1)
                # check if snapshot exists for this date
                timestamp = check_date.strftime('%Y%m%d')

                if timestamp in ignores:
                    print('Ignoring {}'.format(timestamp))
                    continue

                archive_url, archive_timestamp = go_wayback(policy_url, timestamp)

                if archive_timestamp in snapshots:
                    print('{} -> {}'.format(timestamp, archive_timestamp))
                    continue

                policy_date, policy_path = process_policy(company, archive_url, archive_timestamp, last_date)

                if date_url:
                    # some websites have the update date on a different page than the privacy policy, we handle that here
                    _, _, policy_date, _ = process_policy(company, date_url, timestamp, snapshots, last_date, write=True)

                if not policy_date:
                    print('Check date (timestamp={}, archive={})'.format(timestamp, archive_timestamp))

                # a bit hacky but this is how we know if we are done or not
                if policy_path and '_check_date' not in policy_path:
                    # no need to save if we skip due to snapshots
                    last_date = policy_date
                    snapshots.append(archive_timestamp)
                    row.append(policy_date)
                    row.append(archive_url)
                    row.append(policy_path)
                    rows.append(row)
                elif args.abort and policy_path and '_check_date' in policy_path:
                    # we couldn't detect the date... abort
                    break

    csv_out = '{}-privacy-policies-index.csv'.format(company)
    csv_path = os.path.join(POLICY_DIR, csv_out)
    with open(csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['company', 'policy_date', 'policy_url', 'policy_path'])
        for row in rows:
            csvwriter.writerow(row)
    print('csv index written to {}'.format(csv_out))

    return


if __name__ == '__main__':
    main()
