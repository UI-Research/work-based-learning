# Supporting Pathways to Careers - A Study of Work-Based Learning
This repository contains the code needed to scrape course descriptions from the Florida Department of Education's website: https://flscns.fldoe.org/Default.aspx

## Web Scraping
FLDOE provides a database of all postsecondary courses offered by public vocational-technical centers, community colleges, and universities. We are interested in course descriptions from a subset of these institutions - a list of community colleges from the National Center for Education Statistics [IPEDS database](https://nces.ed.gov/ipeds/). This list can be found under `data/school_metadata.csv`.

- `fldoe-selenium-by-school.py` provides the code to scrape all course information (including course descriptions) from these community colleges and return them as individual `.json` files.
- `site_monitor.py` provides code from the Urban Institute's SiteMonitor tool for responsible web scraping - original repo [here](https://github.com/UrbanInstitute/SiteMonitor).
- `run_site_monitor.py` tracks the response times of the website's landing page to ensure we are not overburdening the site through repeated calls.
