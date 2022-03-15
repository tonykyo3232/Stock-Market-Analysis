import sys
import yfinance as yf
from company_list import companies


# format the input for downloading the stock info
def format_date(year, month, day):
	return year + "-" + month + "-" + day

# dowload the stock info for the companies
# for example, from date 2022-02-01 to 2022-03-04
def download_stock(START_DATE, END_DATE):
	df_list = list()
	item = list()

	for i in companies:
	    item = []
	    print("Downloading " + companies[i] + "...")
	    df = yf.download(companies[i], start=START_DATE, end=END_DATE)
	    item.append(companies[i])
	    item.append(df)
	    df_list.append(item)

	return df_list

def save_files(stock_info_list):
	for i in range(0,len(stock_info_list)):
	    print("Saving " + stock_info_list[i][0] + ".csv...")
	    stock_info_list[i][1].to_csv("downloaded_stock/" + stock_info_list[i][0] + ".csv")

if __name__ == '__main__':

	# inputs for start date
	year1 = sys.argv[1]
	month1 = sys.argv[2]
	day1 = sys.argv[3]

	# input for end date
	year2 = sys.argv[4]
	month2 = sys.argv[5]
	day2 = sys.argv[6]

	# format the input for downloading the stock info
	START_DATE = format_date(year1, month1, day1)
	END_DATE = format_date(year2, month2, day2)

	# download stock
	stock_info_list = download_stock(START_DATE, END_DATE)

	# save into .csv files
	save_files(stock_info_list)