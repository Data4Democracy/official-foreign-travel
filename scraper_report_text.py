## For getting full text of all reports

import re
import requests
from os import listdir
from bs4 import BeautifulSoup

## Collects all report URLs and text
def get_quarterly_urls(url):
    urls = []
    
    years = range(1994, 2018)
    quarters = [1,2,3,4]
    
    for year in years:
        for quarter in quarters:
            url = re.sub('ddlYearField=[0-9]{4}','ddlYearField=%i' % year, url)
            url = re.sub('ddlQuartField=q[0-9]','ddlQuartField=q%i' % quarter, url)
            
            urls.append({'y':year, 'q': quarter, 'url': url})
    
    return urls

def get_report_urls(quarterly_urls):
    report_urls = [] 
    
    for quarter in quarterly_urls:
        y   = quarter['y']
        q   = quarter['q']
        url = quarter['url']
        
        print ">>> Getting %i Q%i" % (y, q)
        
        r = requests.get(url)
        
        soup  = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        reports = [ l['href'] for l in links if re.match('^/foreign/reports/[A-Za-z0-9]+.txt$',l['href']) ]
        entries = [ {'year': y, 'quarter': q, 'report_url': r} for r in reports ]
        
        report_urls += entries
    
    return report_urls

def get_report_text(report):
    ROOT  = 'http://clerk.house.gov'
    url   = report['report_url']
    r     = requests.get(ROOT + url)
    text  = r.text.encode('utf-8')
    
    file_name = url[::-1].split('/')[0][::-1]
    
    with open('report_text/%s' % file_name, 'w') as f:
        f.write(text)

## You have to get this from your browser when making a request for quarterly reports.
## Go to Network tab > Submit request for reports > look at the request for index.aspx > view source of form data
url = 'http://clerk.house.gov/public_disc/foreign/index.aspx?__VIEWSTATE=LcCYaWgr%2FRHIHVjN3iaAdAB8y%2FjzWc1l1NRAsXRwgRARiNPYhQKiBKKhCoElQSwz9EBmwDApKfnNeMjt07qkc7gWEamvCh1zC5qdiuF06lqbyDhPnkO7GY5po4Shp97BhqjyRp5L028gQyVNM0mGnBNcq9NGUJRfZqYX7Ljzr1EN56tfI3PrhSdHSMWSZGR8UWuRqHGVV4k5u%2BY6O%2FLYGredDMPmMH27J5f5O5kXVSP2o8taPY5oExshjGZVXsaUZ6rQXHoGdGBv%2BvsG%2BghboSnzRt%2BiO%2BF%2BWCPNXavzsBbPW9hx%2FrIqv0kog%2Bhc4KNso12AxoF1NSMdAkGYvmJ2gSCdc5jC9ai%2FHcaKSCZgu9LQUYumZRnc8xe4vVpE14lR2NAnksSTR%2FdYkvmcC%2BStzjmEtP%2Bf%2FJtJEF99WRugMOdlGz6SoQjDqZUmq5nWrMjNCkALnqSVPprDgixG%2Fw%2BvtU73vRPd1zaAZctbVIHeP1Ui83C3MGMAynfB%2BvQyWj%2Bms%2FZrmWQ0dY9TkiQ5LxEDBGHvo%2FYLrnFpThD94Dv30oDWJ5GFNo9V9tQCkMO9%2Fp9%2FpVKErn5B77Dl4v0GXtDd%2BuWFJ%2BN64DER9%2FeYTYLOCr6ze08YWznh8rqek%2BDiEZ%2FW8JqQJ6h9cByzExTuIhsA716ox4%2F6mVljxbDTmiobYg6mzUv39WbdT2fA97anmQ8fou%2BHQE9k4BCqIC6Qy4%2FKI6B%2BIbhaK9ZXMs7pKeKQAUHvnoOYD9aqAQKOQ3cUxsnKtnoKb%2Fp3OxjxOeowvIOct%2BqPOioifoxtebth3B25PPgGsJ23NJ%2FUwbKVYfc5ZlgU%2FUzUGA%3D%3D&__VIEWSTATEGENERATOR=E19C725B&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION=PRPv2D%2F1w%2FFyLtifsL16NOTPrElLLBuuSzDQPFfZ73EGb6xA739xVch2RWiGqc%2FZIfkkmVwaf4sIVOMeSUIDrIpBv0NpRTt1c%2BAE8kvuS9m2%2BQ4qzZfBqJdyVjyX6mMwMDgrSqqhAXynifkNhTI3aS6anp%2FcHIsKssLn9E4Ok4i5MrYYCtfY%2FThEgBMrMqabGSbeeKxf5gm%2BJsfsjMXW8vfGX97fESzNYF8ZL21LIWELKg4PeuPeAcBVIuDWJCHttAuIMKBOzqSV8mgyXykHXhQkpepvHoMedWxgqi5v8F5oeV82ce3yc2K960SEISX4QVNt%2FsslPsmFsu36WTWSROW7Q%2BFF5b%2BPxmSN7QuzQEZxMU%2BjA5Nx5Co%2F0aqdBjBbdOCCMcquSFrrLTwXakHXODIVM5gpDwP%2B6bwI%2FDCkQEAxWhKybvwpmN%2BvIfifzCYvt9waeD5CD18gRtC0j%2FCAAkrkqcL58XH2kbgXpzx9pooYzsAc3asz2Fz3oHoUEZv1mtwZpSdCwr%2BA9LFxGSB8BxpUh1Tk74kWUy3evOVPmfGpr04j%2B90aM5va7x3a9fGax1sR1y2QGbMfeoO5wpETl0yXY3FZArhFFXj%2BLFm36oScQrlT7%2Fg%2Bgpn0cuRyldI9kHXL4QxE3BUccIP26FhAYeGWaRhCqCFQgP5M5hQqe%2BmgosKaLPCcelb7ccqdrs83vhnWjHNJXdYafWeaMavkUyoYlXPWW37ADGX%2FUcGNwN82%2FDcZJNX3X5AOck7vspPY0dW8mg%3D%3D&ctl00%24txbSearchBox=&ctl00%24cphMain%24ddlYearField=2017&ctl00%24cphMain%24ddlQuartField=q1&ctl00%24cphMain%24btnSearch=Search'

quarterly_urls = get_quarterly_urls(url)
report_urls    = get_report_urls(quarterly_urls)

with open('report_urls.txt', 'a') as f:
    for url in report_urls:
        f.write('%s\n' % url['report_url'])

for report in report_urls:
    url = report['report_url']
    
    file_name = url[::-1].split('/')[0][::-1]
    files_collected = [f for f in listdir('report_text')]
    
    if file_name not in files_collected:
        try:
            get_report_text(report)
        except Exception as e:
            print e
            print report