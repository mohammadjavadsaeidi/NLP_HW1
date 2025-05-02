import requests
import re
import json
from bs4 import BeautifulSoup

cities_url = {
    "zanjan": "https://roostanet.ir/fa/6124",
    "azerbaijan_west": "https://roostanet.ir/fa/6079",
    "azerbaijan_east": "https://roostanet.ir/fa/5837",
    "kordestan": "https://roostanet.ir/fa/6170",
    "ardabil": "https://roostanet.ir/fa/6080",
    "gilan": 'https://roostanet.ir/fa/6186'
}


def fetch_recipe_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_recipes(html):
    soup = BeautifulSoup(html, 'html.parser')

    text = soup.get_text(separator='\n')

    blocks = text.split('نام غذا')[1:]
    recipes = []
    for block in blocks:
        block = 'نام غذا' + block

        name = re.search(r'نام غذا\s*(.*?)\s*(?:شهر)', block)
        city = re.search(r'شهر\s*(.*?)\s*(?:گروه)', block)
        group = re.search(r'گروه\s*(.*?)\s*(?:مواد لازم)', block)
        ingredients = re.search(r'مواد لازم\s*(.*?)\s*(?:طرز تهیه)', block, re.DOTALL)
        instructions = re.search(r'طرز تهیه\s*(.*?)\s*(?:نکات)', block, re.DOTALL)
        notes = re.search(r'نکات\s*(.*?)\s*(?:توضیحات)', block)
        description = re.search(r'توضیحات\s*(.*?)\s*(?:منبع)', block)
        source = re.search(r'منبع\s*(.*)', block)

        recipe = {
            'name': name.group(1).strip() if name else None,
            'city': city.group(1).strip() if city else None,
            'group': group.group(1).strip() if group else None,
            'ingredients': [ing.replace('\xa0', '').strip() for ing in ingredients.group(1).strip().split('\n') if ing.strip().replace('\xa0', '')] if ingredients else None,
            'instructions': instructions.group(1).strip() if instructions else None,
            'notes': notes.group(1).strip() if notes else None,
            'description': description.group(1).strip() if description else None,
            'source': source.group(1).strip() if source else None,
        }
        recipes.append(recipe)
    return recipes


def main():
    for city in cities_url.keys():
        html = fetch_recipe_page(cities_url[city])
        recipes = parse_recipes(html)

        with open(f'{city}_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"Extracted {len(recipes)} recipes. Saved to {city}_recipes.json")


if __name__ == '__main__':
    main()
