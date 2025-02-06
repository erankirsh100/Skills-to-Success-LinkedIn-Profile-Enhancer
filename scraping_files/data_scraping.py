import time

from selenium import webdriver
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd
from tqdm import tqdm
import re
import urllib.parse
import os

job_listings = []
current_job_listings = []

def save_data(save_path = 'job_listings.pkl', company_counter = 0, companies_collected = []):
    # load previous data if it exists
    previous_data = None
    try:
        previous_data = pd.read_pickle(save_path)
    except:
        pass

    # creating a dataframe from the job_listings list
    df = pd.DataFrame([vars(job_listing) for job_listing in current_job_listings])
    # printing the amount of data we have collected
    print(f'Total number of job listings collected: {len(df)}')
    print(f'Total number of companies collected: {company_counter}')
    print(f'Companies collected: {companies_collected}')

    # if there is previous data, we append the new data to it
    if previous_data is not None:
        df = pd.concat([previous_data, df], ignore_index=True)

    # clear file in save_path
    open(save_path, 'w').close()
    
    # saving the dataframe to pickle file
    df.to_pickle(save_path)

class JobListing:
    def __init__(self, company_name, title, url, location, salary=None, type=None, description=None):
        self.company_name = company_name
        self.title = title
        self.url = url
        self.location = location
        self.salary = salary
        self.type = type
        self.description = description

    def __str__(self):
        return f'Company: {self.company_name}\nTitle: {self.title}\nURL: {self.url}\nLocation: {self.location}\nSalary: {self.salary}\nType: {self.type}\nDescription: {self.description}'


def scrape(sbr_webdriver, companies_file = 'companies.csv', additional_companies = [], lim  = float('inf'), save_path = 'job_listings.pkl'):
    
    print('Connecting to Scraping Browser...')
    # measuring the time of connection
    start_time = time.time()
    print('using driver: '+ sbr_webdriver)
    sbr_connection = ChromiumRemoteConnection(sbr_webdriver, 'goog', 'chrome')
    driver = Remote(sbr_connection, options=ChromeOptions())

    if not os.path.exists('running_index.txt'):
        with open('running_index.txt', 'w') as f:
            f.write('0')
        starting_index = 0
    else:
        with open('running_index.txt', 'r') as f:
            starting_index = int(f.read())
    
    running_index = starting_index
    # reading the list of companies to scrape
    companies_df = pd.read_csv(companies_file)
    company_list = companies_df['company'].tolist()[starting_index:]

    if len(additional_companies) > 0:
        company_list = list(set(set(company_list).union(set(additional_companies))))

    company_counter = 0
    error_counter = 0
    companies_collected = []
    for company in tqdm(company_list):
        current_job_listings.clear()
        # for test purposes, we will only scrape 5 companies
        if company_counter >= lim:
            with open('running_index.txt', 'w') as f:
                f.write(str(running_index))
            break
        elif error_counter >= 3:
            print('Too many errors. Exiting...')
            with open('running_index.txt', 'w') as f:
                f.write(str(running_index))
            break

        job_listing_titles = []
        job_listing_urls = []

        print(f'Starting to scrape job listings for company: {company}')

        try:
            # before adding the company to the link, we need to encode it
            driver.get(f"https://indeed.com/jobs?q={urllib.parse.quote_plus(company)}")
        except Exception as e:
            print(f'Error: {e}')
            error_counter += 1
            continue
        time.sleep(5)

        # scrolling the page a few times to load more posts
        print('Collecting Job Listing Placeholders')
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # finding all containers with job listings
        job_listing_containers = BeautifulSoup(driver.page_source, 'html.parser').find_all('div', class_='job_seen_beacon')
        if len(job_listing_containers) == 0:
            print('No job listings found for this company')
            error_counter += 1
            continue
        for job_container in job_listing_containers:
            # find the job title, where it is h2 and its class contains jobTitle
            title_box = job_container.find_all_next('h2', class_='jobTitle')
            # the title is the element in the span tag
            title = title_box[0].find_all_next('span')[0].text

            # find the URL of the job listing, in the link received from the title box href, remove everything before the jk= and add it to the URL
            url = f'https://indeed.com/viewjob?{title_box[0].find_all_next('a')[0]["href"].split("?")[1]}'
            print(f'Job title: {title}')
            print(f'Job URL: {url}\n')

            job_listing_titles.append(title)
            job_listing_urls.append(url)

        print('Loading properties for each job listing')

        # we collect a number of job listings, which is 6 if there are 6 or more job listings, otherwise we collect all of them
        job_listings_to_collect = 6 if len(job_listing_titles) >= 6 else len(job_listing_titles)
        listings_collected = 0
        for i in tqdm(range(len(job_listing_titles)), desc='Collecting Job Listings'):
            if listings_collected >= job_listings_to_collect:
                break
            try:
                driver.get(job_listing_urls[i])
            except Exception as e:
                print(f'Error: {e}')
                continue
            time.sleep(5)
            try:
                JobHeaderContainer = BeautifulSoup(driver.page_source, 'html.parser').find_all('div', class_='jobsearch-InfoHeaderContainer')[0]
            except:
                print(f'Error: Could not find Job Header Container for job listing: {job_listing_titles[i]}')
                print('Probably Captcha. Skipping...')
                continue
            # company_location is stored in text of div with data-testid='inlineHeader-companyLocation'
            company_location = JobHeaderContainer.find_all_next('div', attrs={'data-testid': 'inlineHeader-companyLocation'})
            if len(company_location) > 0:
                company_location = company_location[0].text
            else:
                try:
                    JobInfoContainer = BeautifulSoup(driver.page_source, 'html.parser').find_all('div',
                                                                                                 class_='jobsearch-CompanyInfoContainer')[0]
                    company_location = JobInfoContainer.find_all_next('div')
                    company_location = company_location[-1].text
                except:
                    company_location = 'Unknown'

            JobOtherDetails = BeautifulSoup(driver.page_source, 'html.parser').find_all('div', attrs={'data-testid': 'jobsearch-OtherJobDetailsContainer'})
            # if JobOtherDetails is not empty, we can take the job info and type from it
            job_salary = None
            job_type = None
            if len(JobOtherDetails) > 0:
                job_info = JobOtherDetails[0].find_all_next('div', attrs={'id': 'salaryInfoAndJobType'})
                if len(job_info) > 0:
                    job_info = job_info[0]
                    # job_info contains 2 span tags, one for salary and one for type
                    job_info_content_size = len(job_info.contents)
                    job_info = job_info.find_all_next('span')

                    # if the job_info is not empty, and contains 2 elements, we can take the salary and type
                    if job_info_content_size == 2:
                        job_salary = job_info[0].text
                        job_type = job_info[1].text
                    # If job_info contains only one element, we need to infer whether it is salary or type
                    elif job_info_content_size == 1:
                        job_info_text = job_info[0].text
                        # if the job_info_text contains $, it is salary
                        if '$' in job_info_text:
                            job_salary = job_info_text
                        else:
                            job_type = job_info_text

            try:
                JobBodyContainer = BeautifulSoup(driver.page_source, 'html.parser').find_all('div', class_='jobsearch-BodyContainer')[0]
            except:
                print(f'Unexpected error: Could not find Job Body Container for job listing: {job_listing_titles[i]}')
                continue
            job_description = JobBodyContainer.find_all_next('div', attrs={'id': 'jobDescriptionText'})
            if len(job_description) > 0:
                job_description = job_description[0].text
            else:
                job_description = 'No Description'
            # job_description contains many <p> tags, and list tags, we want to remove them and get the text
            job_description = job_description.replace('<p>', '').replace('</p>', '').replace('<li>', '').replace('</li>', '')
            job_description = job_description.replace('<ul>', '').replace('</ul>', '').replace('<ol>', '').replace('</ol>', '')
            job_description = job_description.replace('<div>', '').replace('</div>', '')
            # stripping the leading, trailing, and extra whitespaces
            job_description = job_description.strip()
            # removing more than 2 newlines in a row
            job_description = re.sub('(\n\n)\n*|\n', r'\1', job_description)

            job_listing = JobListing(company, job_listing_titles[i], job_listing_urls[i], company_location, job_salary, job_type, job_description)
            job_listings.append(job_listing)
            current_job_listings.append(job_listing)
            listings_collected += 1
            # for testing purposes
            # print(job_listing)

        print(f'Total number of job listings collected for {company}: {listings_collected}')
        company_counter += 1
        companies_collected.append(company)

        # saving the data to a pickle file
        save_data(save_path, company_counter, companies_collected)
        running_index += 1
        with open('running_index.txt', 'w') as f:
            f.write(str(running_index))        

        # time elapsed from the start of the script
        elapsed_time = time.time() - start_time
        print(f'Time elapsed: {elapsed_time/60:.2f} minutes')

    driver.quit()

if __name__ == '__main__':
    scrape()

