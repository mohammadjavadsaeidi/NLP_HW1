import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_html(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def extract_list_from_element(elem):
    items = []
    if not elem:
        return items
    for tag in elem.find_all(['ul', 'ol'], recursive=False):
        for li in tag.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                items.append(text)
        if items:
            return items

    raw = elem.get_text(separator="\n")
    parts = [part.strip() for part in raw.split('\n') if part.strip()]
    return parts

def parse_recipe_page(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    title_tag = soup.find(['h1', 'h2'])
    title = title_tag.get_text(strip=True) if title_tag else ''

    content = soup.find('div', class_='mw-parser-output') or soup

    ingredients = []
    ing_header = content.find(lambda tag: tag.name in ['h2','h3','h4','p']
                                         and 'مواد لازم' in tag.get_text())
    if ing_header:
        target = ing_header.find_next_sibling()
        ingredients = extract_list_from_element(target)

    instructions = []
    instr_section = soup.find('section', id='content-collapsible-block-1')
    if instr_section:
        for p in instr_section.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                instructions.append(text)
    else:
        instr_header = content.find(lambda tag: tag.name in ['h2','h3','h4','p']
                                             and 'طرز تهیه' in tag.get_text())
        if instr_header:
            for sib in instr_header.find_next_siblings():
                if sib.name and re.match(r'h[1-6]', sib.name):
                    break
                if sib.name in ['ul','ol','p']:
                    instructions.extend(extract_list_from_element(sib))

    instructions = [
        inst for inst in instructions
        if not re.match(r'^(مواد لازم|طرز تهیه)', inst)
    ]

    return {
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions,
        'url': url
    }


def crawl_recipes(urls, output_file='kordestan_recipes.json'):
    results = []
    for url in urls:
        try:
            data = parse_recipe_page(url)
            results.append(data)
            print(f"✔ Crawled {url} → {len(data['instructions'])} instructions")
        except Exception as e:
            print(f"✖ Failed {url}: {e}")
            results.append({
                'url': url,
                'error': str(e),
                'title': '',
                'ingredients': [],
                'instructions': []
            })

    # ذخیره در JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ All done! Results saved to '{output_file}'")

if __name__ == '__main__':
    urls = [
    'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D8%A7%D9%88%D9%85%D8%A7%D8%AC',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D9%82%D9%88%D8%B1%D9%85%D9%87_%D8%A2%D8%B0%D8%B1%DB%8C',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D8%AF%D9%88%D8%BA',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%A8%DA%AF%D9%88%D8%B4%D8%AA_%D8%BA%D9%88%D8%B1%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D9%BE%D8%B1%D9%BE%D9%88%D9%84%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D8%AF%D8%A7%D9%86%D9%87_%DA%A9%D9%88%D9%84%D8%A7%D9%86%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D8%B9%D8%AF%D8%B3_%D8%A8%D9%84%D8%BA%D9%88%D8%B1',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D9%87%D8%A7%D9%84%D8%A7%D9%88',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A2%D8%B4_%D8%B3%D9%87_%D9%86%DA%AF%D9%87_%D8%B3%DB%8C%D8%B1',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%A8%D8%B1%D9%88%DB%8C%D8%B4%DB%8C%D9%86',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%AE%D9%88%D8%B1%D8%B4_%D8%AA%D8%B1%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%AE%D9%88%D8%B1%D8%B4_%D8%B1%DB%8C%D9%88%D8%A7%D8%B3',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%AF%D9%86%D8%AF%D9%87_%DA%A9%D8%A8%D8%A7%D8%A8',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%B4%D9%84%DA%A9%DB%8C%D9%86%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D8%B9%D8%AF%D8%B3%DB%8C_%D8%A8%D8%A7_%D8%B1%D8%B4%D8%AA%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%D9%82%D8%A7%DB%8C%D8%B1%D9%85%D9%87',
        'https://fa.m.wikibooks.org/wiki/%DA%A9%D8%AA%D8%A7%D8%A8_%D8%A2%D8%B4%D9%BE%D8%B2%DB%8C/%DA%A9%D9%87_%D9%84%D8%A7%D9%86%D9%87'
    ]

    crawl_recipes(urls)
