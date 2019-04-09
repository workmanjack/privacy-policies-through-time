import re
import dateparser
from wayback_search import get_update_date, REGEX_POLICY_DATE_LIST


#with open('20110902041958_check_date.txt', 'r') as f:
with open('20091001221035_check_date.txt', 'r') as f:
    page = f.read()

# This policy was last updated on July 21, 2011 ("Effective Date").
# Last updated on July 21, 2011

update_date = get_update_date(page, regex_list=REGEX_POLICY_DATE_LIST)
print(update_date)

#regex = re.compile(r'Effective: (\w+ \d+, \d+)', flags=re.IGNORECASE)

# match = regex.search(page)
# print(match)
# print(match.group(1))
# update_date = dateparser.parse(match.group(1))
# print(update_date)
