from datetime import date, timedelta
import requests
import re


# these are strings that signal the start/end of the wayback inserted html/js material in an
# archived webpage - we use them to strip out the company's part of the archived page
WAYBACK_HEADER_END = '<!-- END WAYBACK TOOLBAR INSERT -->'
WAYBACK_FOOTER_START = '<div id="footer">'
POLICY_BOOKENDS = [
    ('<div id="main">', '<div id="footer">'),
    ('</head>', '<footer'),
]
REGEX_DUP_WHITESPACE = re.compile(r'  +', re.IGNORECASE)
REGEX_DUP_NEWLINE = re.compile(r'\s*\n\s+')
REGEX_LINK_TAG = re.compile(r'<link.*>')
REGEX_SCRIPT_TAG = re.compile(r'\<script.*\</script\>', re.DOTALL)
REGEX_STYLE_TAG = re.compile(r'\<style.*\</style\>', re.DOTALL)
REGEX_TAGS = re.compile('<[^<]+?>')


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
    footer_start_index = page.find(WAYBACK_FOOTER_START)
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
    for start, end in policy_bookends:
        start_index = page.find(start)
        end_index = page.find(end)
        if start_index == -1:
            print('policy start "{}" not found'.format(start))
            start_index = 0
        if end_index == -1:
            print('policy end "{}" not found'.format(end))
            end_index = len(page)

        page = page[start_index:end_index]

    # remove timestamps as they are unique and inserted by wayback
    page = page.replace(timestamp, '')

    # remove all <script> and <style> blocks
    page = REGEX_SCRIPT_TAG.sub('', page)
    page = REGEX_STYLE_TAG.sub('', page)


    # remove all tags because we want only the text
    page = REGEX_TAGS.sub('', page)

    # replace duplicate whitespace
    page = REGEX_DUP_WHITESPACE.sub(' ', page)

    # replace duplicate newlines
    page = REGEX_DUP_NEWLINE.sub('\n', page)

    pretty = page

    # remove all newlines for comparison
    compare = page.replace('\n', '')

    return compare, pretty


def main():

    policy_url = 'http://www.fitbit.com/privacy'
    year = 2010
    month = 2
    day = 1

    start_date = date(2010, 2, 1)
    start_date = date(2012, 2, 1)
    end_date = date.today()

    # iterate through dates, query wayback, retrieve snapshots
    # if snapshot is new, then get page source; else, continue
    snapshots = list()
    last = ''
    for year, month in month_year_iter(start_date.month, start_date.year, end_date.month, end_date.year):

        check_date = date(year, month, 1)
        # check if snapshot exists for this date
        timestamp = check_date.strftime('%Y%m%d')
        request_url = 'http://archive.org/wayback/available?url={}&timestamp={}'.format(policy_url, timestamp)
        data = api_query(request_url)

        archive = data.get('archived_snapshots', {}).get('closest', None)
        if archive and archive.get('available'):

            # check if the returned nearest snapshot has been looked at already
            archive_url = archive.get('url')
            archive_timestamp = archive.get('timestamp')
            if archive_timestamp in snapshots:
                print('{} -> {}'.format(timestamp, archive_timestamp))
                continue

            snapshots.append(archive_timestamp)

            #print('archive_url: ', archive_url)
            resp = requests.get(url=archive_url)
            if resp.status_code != 200:
                print('failed to retrieve data from {0}'.format(url))
            else:
                page = resp.text

                # it is debatable if this provides value
                #page = remove_wayback(page)

                # trim policy
                page_compare, page_pretty = make_policy_comparable(page, POLICY_BOOKENDS, archive_timestamp)

                # compare policies
                if page_compare == last:
                    print('{} no change'.format(archive_timestamp))
                else:
                    last = page_compare
                    out = '{}.txt'.format(archive_timestamp)
                    with open(out, 'wb') as f:
                        f.write(page_pretty.encode('UTF-8'))

                    print('{} written to {}'.format(archive_timestamp, out))


    return


if __name__ == '__main__':
    main()
