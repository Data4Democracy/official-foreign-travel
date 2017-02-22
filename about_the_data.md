---
title: 'Foreign Travel: About the Data'
author: '@ryanes'
date: "February 17, 2017"
output: html_document
---

If you haven't already, please review our [readme](https://github.com/Data4Democracy/official-foreign-travel/blob/master/README.md) to learn more about this project and how to contribute.

The purpose of this document is to provide links to the original sources of data that are used in the [Data for Democracy/ProPublica repository](https://github.com/Data4Democracy/official-foreign-travel) `official-foreign-travel`. It also provides descriptions and context for each dataset, including information about the data cleaning methods used. This document will be updated as new datasets are introduced.

## Dataset: Foreign Travel Reports

The original datasets can be downloaded from the [Office of the Clerk](http://clerk.house.gov/public_disc/foreign/index.aspx).

_From Derek Willis of ProPublica:_ 

>House Official Foreign travel reports, which are published quarterly by the House Clerk, are produced either by committees or delegations that are not committee-sponsored. They contain the name of each traveler, arrival and departure dates, the destination, three spending categories (per diem, transportation and other) along with a grand total of money spent (usually in US dollars).

>For committee trips, the name of the committee is in the line beginning `REPORT OF EXPENDITURES FOR OFFICIAL FOREIGN TRAVEL` in the files. Those without a committee might contain `DELEGATION` or an individual's name.

>Caveats: in some cases, the destination is a continent, not a country. This usually happens for trips paid for by the Intelligence Committee. Lawmakers are typically identified by the prefix "Hon" before their names. There could be amended reports, meaning substantially duplicative information would occur. To the extent we can identify those cases, we want to retain the most recent report.

The script to clean this data is an ongoing process.  [`scraper_report_text.py`](https://github.com/Data4Democracy/official-foreign-travel/blob/master/scraper_report_text.py) pulls down the text files from the server.  [`scraper.py`](https://github.com/Data4Democracy/official-foreign-travel/blob/master/scraper.py) cleans and outputs the data, which is stored on our [data.world page](https://data.world/data4democracy/propublica-foreign-travel) or can be read in using [this link](https://query.data.world/s/9a8mas5oqrayibt2i30wznwug). 

To keep things consistent, please use links to our data.world page in your scripts whenever possible.