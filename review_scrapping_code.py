import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import time

product_reviews = []

def transform_to_review_url(product_url):
    parsed_url = urlparse(product_url)
    query_params = parse_qs(parsed_url.query)
 
    new_path = parsed_url.path.split('/p/')[0] + '/product-reviews/' + parsed_url.path.split('/p/')[1]
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        new_path,
        parsed_url.params,
        urlencode(query_params, doseq=True),
        parsed_url.fragment
    ))

    return new_url


def scrape_reviews(product_name, product_link, review_url):
    print(f"Scraping reviews for: {product_name}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(review_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching reviews: {e}")
        product_reviews.append({
            "Product Name": product_name,
            "Product Link": product_link,
            "Username": "N/A",
            "Title": "No Title",
            "Rating": None,
            "Comment": "No Comment",
            "Like Count": None,
            "Dislike Count": None
        })
        return

    soup = BeautifulSoup(response.text, "html.parser")

    product_name_div = soup.find("div", class_="Vu3-9u eCtPz5")
    if product_name_div:
        actual_product_name = product_name_div.text.strip()
    else:
        actual_product_name = product_name

    pagination = soup.find("div", class_="_1G0WLw mpIySA")
    if pagination:
        pages_text = pagination.find("span").text
        total_pages = int(pages_text.split()[-1])  
    else:
        total_pages = 1  

    reviews_found = False
  
    for page in range(1, total_pages + 1):
        paginated_url = review_url + f"&page={page}"
        try:
            response = requests.get(paginated_url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        review_container = soup.find_all("div", class_="col EPCmJX Ma1fCG")

        if len(review_container) > 0:
            reviews_found = True

        for review in review_container:
            username = review.find("p", class_="_2NsDsF AwS1CA").text if review.find("p", class_="_2NsDsF AwS1CA") else "N/A"
            title = review.find("p", class_="z9E0IG").text if review.find("p", class_="z9E0IG") else "No Title"
            rating = review.find("div", class_="XQDdHH Ga3i8K").text if review.find("div", class_="XQDdHH Ga3i8K") else None
            comment_div = review.find("div", class_='ZmyHeo')
            comment = comment_div.text.strip() if comment_div else "No Comment"

            # Extract like and dislike counts
            like_count = review.find("div", class_="_6kK6mk").find("span", class_="tl9VpF").text if review.find("div", class_="_6kK6mk") else None
            dislike_count = review.find("div", class_="_6kK6mk aQymJL").find("span", class_="tl9VpF").text if review.find("div", class_="_6kK6mk aQymJL") else None

            product_reviews.append({
                "Product Name": actual_product_name,
                "Product Link": product_link,
                "Username": username,
                "Title": title,
                "Rating": rating,
                "Comment": comment,
                "Like Count": like_count,
                "Dislike Count": dislike_count
            })

        time.sleep(2)  

        if not review_container:
            print(f"No reviews found on page {page}. Stopping the scrape.")
            break

    if not reviews_found:
        product_reviews.append({
            "Product Name": actual_product_name,
            "Product Link": product_link,
            "Username": "N/A",
            "Title": "No Title",
            "Rating": None,
            "Comment": "No Comment",
            "Like Count": None,
            "Dislike Count": None
        })


for index, row in df.iterrows():
    product_name = row['Product Name']
    product_link = row['Links']

    print(f"Product Name: {product_name}")
    print(f"Product Link: {product_link}")

    review_link = transform_to_review_url(product_link)
    print(f"Review Link: {review_link}")

    scrape_reviews(product_name, product_link, review_link)

new_df_reviews = pd.DataFrame(product_reviews)

new_df_reviews.to_csv('product_reviews.csv', index=False)
