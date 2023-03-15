# Web Scraper
#### Carlos E. Ortega Summer 2019
#### Contact for questions: carlosortega@berkeley.edu
Dependencies:
- sklearn
- pickle
- pandas
- numpy
- scrapy

### Using the Web Scraper
1. From your terminal CD into the spiders folder `web_scraper/facilities/facilities/spiders`
2. Run the following command: `scrapy crawl facility_scraper`
3. Scraped data will be saved in the scraped folder `web_scraper/facilities/facilities/scraped`

To edit what sites are scraped edit the excel file in `web_scraper/facilities/facilities/spiders/targets/targets.csv`

### Training New Data
All training data is stored in `web_scraper/Training/training_data`
#### Getting New Data
1. From your terminal CD into the spiders folder `web_scraper/facilities/facilities/spiders`
2. Run the following command: `scrapy crawl get_training_data`
3. The scraped data will be saved to `web_scraper/facilities/facilities/scraped`. You can differentiate data from the facility_scraper and the get_training_data scraper as the training data scraper only has 2 columns and keeps html
4. Move the scraped files to `web_scraper/Training/training_data/clean_files`
5. In `web_scraper/Training` run `python process.py` this will process the files in the previously-mentioned 'clean_files' folder and save the processed files to `web_scraper/Training/training_data`
6. In this folder, run `python train.py`. Once you are satisfied with the results in console type `yes` and it will automatically update the models used in the facility_scraper.

To edit what sites are scraped edit the excel file in `web_scraper/facilities/facilities/spiders/targets/training_targets.csv`


## Public domain

Except where noted, this project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the CC0 1.0 Universal public domain dedication. Except where noted, all contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are affirming that the changes are yours to license and you are agreeing to comply with this waiver of copyright interest, or that the changes are already in the public domain.