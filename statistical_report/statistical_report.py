import json

with open("../output/aggregated_with_id.json", encoding="utf-8") as f:
    data = json.load(f)


def count_words(text):
    if text is None:
        return 0
    return len(str(text).split())


total_records = len(data)
total_word_count = 0
char_lengths = {}
word_lengths = {}


for record in data:
    title = str(record.get("title", "") or "")
    total_word_count += count_words(title)
    char_lengths.setdefault("title", []).append(len(title))
    word_lengths.setdefault("title", []).append(count_words(title))


    province = str(record.get("location", {}).get("province", "") or "")
    city = str(record.get("location", {}).get("city", "") or "")
    char_lengths.setdefault("location.province", []).append(len(province))
    word_lengths.setdefault("location.province", []).append(count_words(province))
    char_lengths.setdefault("location.city", []).append(len(city))
    word_lengths.setdefault("location.city", []).append(count_words(city))
    total_word_count += count_words(province) + count_words(city)

    for ing in record.get("ingredients", []):
        name = str(ing.get("name", "") or "")
        unit = str(ing.get("unit", "") or "")
        amount = ing.get("amount", "")
        amount_str = str(amount) if amount is not None else ""

        for field_name, value in [("ingredients.name", name), ("ingredients.unit", unit), ("ingredients.amount", amount_str)]:
            char_lengths.setdefault(field_name, []).append(len(value))
            word_lengths.setdefault(field_name, []).append(count_words(value))
            total_word_count += count_words(value)

    for instr in record.get("instructions", []):
        instr_str = str(instr or "")
        char_lengths.setdefault("instructions", []).append(len(instr_str))
        word_lengths.setdefault("instructions", []).append(count_words(instr_str))
        total_word_count += count_words(instr_str)

    for mt in record.get("meal_type", []):
        mt_str = str(mt or "")
        char_lengths.setdefault("meal_type", []).append(len(mt_str))
        word_lengths.setdefault("meal_type", []).append(count_words(mt_str))
        total_word_count += count_words(mt_str)

    for oc in record.get("occasion", []):
        oc_str = str(oc or "")
        char_lengths.setdefault("occasion", []).append(len(oc_str))
        word_lengths.setdefault("occasion", []).append(count_words(oc_str))
        total_word_count += count_words(oc_str)

avg_char_lengths = {field: sum(lengths) / len(lengths) for field, lengths in char_lengths.items()}
avg_word_lengths = {field: sum(lengths) / len(lengths) for field, lengths in word_lengths.items()}

with open("statistical_report.txt", "w", encoding="utf-8") as report:
    report.write(f"Total number of records: {total_records}\n")
    report.write(f"Total word count (including numbers): {total_word_count}\n\n")

    report.write("Average lengths per field:\n")
    for field in sorted(avg_char_lengths.keys()):
        report.write(f"- {field}:\n")
        report.write(f"    • Average characters: {avg_char_lengths[field]:.2f}\n")
        report.write(f"    • Average words:      {avg_word_lengths[field]:.2f}\n")

print("Full report saved to 'statistical_report.txt'")