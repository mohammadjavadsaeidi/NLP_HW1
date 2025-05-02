import time

import requests
import json
from bs4 import BeautifulSoup

site_prefix = "Ghazaland"

cities_map = {
    "ardabil": [
        "https://ghazaland.com/recipe-cuisine/ardabil/",
    ],
    "kordestan": [
        "https://ghazaland.com/recipe-cuisine/kurdistan/",
        "https://ghazaland.com/recipe-cuisine/kurdistan/page/2"
    ],
    "zanjan": [
        "https://ghazaland.com/recipe-cuisine/zanjan/",
        "https://ghazaland.com/recipe-cuisine/zanjan/page/2/"
    ],
    "azerbaijan_west": [
        "https://ghazaland.com/recipe-cuisine/west-azerbaijan/"
    ],
    "azerbaijan_east": [
        "https://ghazaland.com/recipe-cuisine/east-azerbaijan/",
        "https://ghazaland.com/recipe-cuisine/east-azerbaijan/page/2/",

    ],
    "gilan": [
        "https://ghazaland.com/recipe-cuisine/gilan/",
        "https://ghazaland.com/recipe-cuisine/gilan/page/2/",
        "https://ghazaland.com/recipe-cuisine/gilan/page/3/",
        "https://ghazaland.com/recipe-cuisine/gilan/page/4/",
        "https://ghazaland.com/recipe-cuisine/gilan/page/5/"
    ]
}


def fetch_html_url(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Request failed with status code {response.status_code}")


def parse_recipe(html):

    soup = BeautifulSoup(html, "html.parser")

    def first_text(selector, *, root=soup):
        el = root.select_one(selector)
        return el.get_text(strip=True) if el else ""

    def many_text(selector, *, root=soup):
        return [li.get_text(strip=True) for li in root.select(selector)]

    get = lambda sel: (soup.select_one(sel) or {}).get_text(strip=True)
    lis = lambda sel: [li.get_text(strip=True) for li in soup.select(sel)]

    name = first_text("h1.article-title")

    city_anchor = soup.select_one('div.entry a[href*="/recipe-cuisine/"]')
    city = city_anchor.get_text(strip=True) if city_anchor else ""

    img_el = soup.select_one(".media-single-content img")
    image = img_el["src"] if img_el and img_el.has_attr("src") else ""

    grp_anchor = soup.select_one(
        '.single-category a[href*="/category/lunch/"],'
        '.single-category a[href*="/category/dinner/"]')
    group = grp_anchor.get_text(strip=True) if grp_anchor else ""

    ingredients = [ingredient for ingredient in lis(".ingredients-box li") if ingredient]
    instructions = lis(".cooking-steps-box li")
    instructions = [instruction for instruction in instructions[0].split(".") if instruction]
    notes = first_text(".recipe-notes, .notes-box")  # may be ""

    description = (first_text(".p-first-letter > p")
                   or first_text(".entry-content > p"))

    link_can = soup.find("link", rel="canonical")
    source = link_can["href"] if link_can and link_can.has_attr("href") else ""

    recipe = {
        "name": name,
        "city": city,
        "image": image,
        "group": group,
        "ingredients": ingredients,
        "instructions": instructions,
        "notes": notes,
        "description": description,
        "source": source,
    }
    return [recipe]


def parse_foods_urls(html):
    soup = BeautifulSoup(html, "html")
    second_links = []

    for div in soup.select('ul.grid_list.js-masonry li.post div.grid-content'):
        a_tags = div.find_all('a')
        if len(a_tags) >= 2:
            second_links.append(a_tags[1]['href'])

    return second_links


def main():
    cities_foods_urls = {}
    for city in cities_map.keys():
        foods_urls = []
        for city_url in cities_map[city]:
            html = fetch_html_url(city_url)
            foods_urls += parse_foods_urls(html)
        cities_foods_urls[city] = foods_urls

    for city in cities_foods_urls.keys():
        city_recipes = []
        for city_food_url in cities_foods_urls[city]:
            html = fetch_html_url(city_food_url)
            time.sleep(0.5)
            city_recipes += parse_recipe(html)

        with open(f'{site_prefix}_{city}_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(city_recipes, f, ensure_ascii=False, indent=2)
        print(f"Extracted {len(city_recipes)} recipes. Saved to {site_prefix}_{city}_recipes.json")


if __name__ == '__main__':
    main()
