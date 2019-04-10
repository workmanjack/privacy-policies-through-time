# Privacy Policies Through Time

A collection of privacy policies organized by company and revision date

Begin exploring the dataset via [this notebook](/notebooks/privacy-policies-through-time.ipynb) and the [master-privacy-policies-index.csv](/privacy-policies-through-time/master-privacy-policies-index.csv) index.

## Objective

Studying how privacy policies have evolved over time can tell us about…

1. A company’s approach to privacy
2. The immediate and lasting impact of legislation
3. How to best form new legislation

Other privacy policy datasets cover only recent policies and do not connect revisions (source: https://usableprivacy.org/data)

## Dataset Metadata

* Number of Privacy Policies: 295
* Number of Companies: 21
* Date Range: June 9th, 1999 - January 1st, 2019

## Analyzing Key Privacy Events

We can use this data to review changes over time to privacy policies. Here we show examples of searching by keyword through past policies to observe the impact and effect of deprecating old or enacting new legislation.

For more examples, please view [this notebook](/notebooks/privacy-policies-through-time.ipynb). The heatmaps were generated with python's [seaborn](https://seaborn.pydata.org/).

### International Safe Harbor Privacy Principles

![safe_harbor_heatmap](https://github.com/workmanjack/privacy-policies-through-time/blob/master/report/figures/safe-harbor-heatmap.PNG)

### EU-US Privacy Shield

![eu-us-privacy-shield-heatmap](https://github.com/workmanjack/privacy-policies-through-time/blob/master/report/figures/eu-us-privacy-shield-heatmap.PNG)

## Notes On Policy Collection

Some sites are easier than others

* Glassdoor - from 2015 to about 2018, Glassdoor had its privacy policy split between two pages. The first page (we'll call it "the overview page"), and an updated revision date. The second page, the "full policy page", had a revision date as well, but this one was not kept up to_date. In these situations, you can add a second "date_url" to your config from which to retrieve a date. However, it doesn't quite work.
* LinkedIn - at a certain point after 2015, the archived versions of LinkedIn's privacy policy are no longer usable. It looks like cookies or something might have blocked the archive from collecting the webpages. See this as an example: https://web.archive.org/web/20180312014548/https://www.linkedin.com/legal/privacy-policy?trk=hb_ft_priv
* Oracle's website's privacy policy is not retrievable via the wayback machine from 2002-2008. The page is viewable but not scrapeable.
* Pinterest does not include a revision date on its privacy policy from 2012-2016
