import requests
from bs4 import BeautifulSoup
import pandas as pd

Product_name = []
Prices = []
Description = []
Ratings = []
review_links = []


url = 'https://www.flipkart.com/search?q=laptop'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1"
}


r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")


total_pages = soup.find("div", class_="_1G0WLw")
if total_pages:
    total_pages = int(total_pages.span.text.split()[-1])
else:
    total_pages = 1  
print(f"Total number of pages: {total_pages}")

for i in range(1, total_pages + 1):
    page_url = f'https://www.flipkart.com/search?q=laptop&page={i}'
    r = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    box = soup.find("div", class_="DOjaWF gdgoEp")
    if box:
        names = box.find_all('div', class_='KzDlHZ')
        prices = box.find_all('div', class_='Nx9bqj _4b5DiR')
        desc = box.find_all('ul', class_='G4BRas')
        ratings = box.find_all('div', class_='XQDdHH')

        for j in range(max(len(names), len(prices), len(desc), len(ratings))):
            Product_name.append(names[j].text if j < len(names) else "")
            Prices.append(prices[j].text if j < len(prices) else "")
            Description.append(desc[j].text if j < len(desc) else "")
            Ratings.append(ratings[j].text if j < len(ratings) else "")
    else:
        print(f"No product box found on page {i}")

    review_containers = soup.find_all("div", class_="tUxRFH")
    for container in review_containers:
        link_tag = container.find("a", class_="CGtC98")
        if link_tag and link_tag.get("href"):
            review_url = "https://www.flipkart.com" + link_tag.get("href")
            review_links.append(review_url)

    print(f"Scraped page {i}/{total_pages}")

df = pd.DataFrame({
    "Product Name": Product_name,
    "Prices": Prices,
    "Description": Description,
    "Ratings": Ratings,
    "Links": review_links[:len(Product_name)]  # Adjust to match the product count
})

#print(df)
print("Completed")