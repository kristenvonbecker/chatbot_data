import pandas as pd
import re
from unidecode import unidecode

from dotenv import load_dotenv
load_dotenv()


apos_pattern = r"(\w+)'S"
p_pattern = r"(\((?!born).+?\)), "
pl_pattern = r"(plural .+?), "
alias_pattern = r"(?:also called|also spelled) (.+?), "
cat_pattern = r"(?!in full)(?:in|In) (.+?), (?:or (.+?), (.+?), )?"
aka_pattern = r"(?:Latin in full|in full|byname of|original name) (.+?), "
bd_pattern = r"\(born (\w+ \d{1,2}, \d{4})(?:, )(.*?)(?:—died (\w+ \d{1,2}, \d{4})(?:, )(.*?))?\), "


def clean_articles(articles):
    id = []
    title_fixed = []
    text_fixed = []
    alt_title = []
    grouping = []
    is_person = []  # 0 = not person, 1 = living person, 2 = deceased person

    for article in articles:
        id.append(article["article_id"])
        title = article["title"].strip(' ,')  # strip commas and extra whitespace from titles
        title = title.replace(u"\u2019", "'")  # replace unicode single smart quote in title
        text = article["text"].replace(u"\u2019", "'").strip()  # replace unicode single smart quote in text

        # title = unidecode(title)
        # text = unidecode(text)

        title_split = title.split()
        if len(title_split) > 1:
            title_tc = ' '.join([title_split[0].title()] + title_split[1:])
        else:
            title_tc = title.title()

        title_comma = re.escape(title) + r'(\s)*,(\s)*'
        title_colon = title_tc + r': '
        text = re.sub(title_comma, title_colon, text)

        prefix = title_colon
        contents = []

        apos_title = re.search(apos_pattern, title)
        if apos_title:
            title = title.replace(apos_title.group(0), apos_title.group(1))

        apos_text = re.search(apos_pattern, text)
        if apos_text:
            text = text.replace(apos_text.group(0), apos_text.group(1))

        # p = prefix.replace(r'(', r'\(').replace(r')', r'\)') + re.escape(p_pattern)
        paren_info = re.search(re.escape(prefix) + p_pattern, text)
        if paren_info:
            contents.append(paren_info.group(1).strip('()'))
            paren = '(' + '; '.join(contents) + ')'
            prefix = ' '.join([title_tc, paren]) + ': '
            text = text.replace(paren_info.group(0), prefix, 1)

        plural = re.search(re.escape(prefix) + pl_pattern, text)
        if plural:
            contents.append(plural.group(1))
            paren = '(' + '; '.join(contents) + ')'
            prefix = ' '.join([title_tc, paren]) + ': '
            text = text.replace(plural.group(0), prefix, 1)

        alias_name = re.search(re.escape(prefix) + alias_pattern, text)
        if alias_name:
            contents.append('or ' + alias_name.group(1).strip())
            paren = '(' + '; '.join(contents) + ')'
            prefix = ' '.join([title_tc, paren]) + ': '
            text = text.replace(alias_name.group(0), prefix, 1)
            alt_title.append([x.strip() for x in alias_name.group(1).split(' or ')])
        else:
            alt_title.append([])

        category = re.search(re.escape(prefix) + cat_pattern, text)
        if category:
            if category.group(3):
                cat_name = category.group(1) + '/' + category.group(2) + ' ' + category.group(3)
                contents.append('in ' + cat_name)
            else:
                cat_name = category.group(1)
                contents.append('in ' + cat_name)
            paren = '(' + '; '.join(contents) + ')'
            prefix = ' '.join([title_tc, paren]) + ': '
            text = text.replace(category.group(0), prefix, 1)
            grouping.append([x.strip() for x in cat_name.split(' and ')])
        else:
            grouping.append([])

        aka_name = re.search(re.escape(prefix) + aka_pattern, text)
        if aka_name:
            contents.append('aka ' + aka_name.group(1))
            paren = '(' + '; '.join(contents) + ')'
            prefix = ' '.join([title_tc, paren]) + ': '
            text = text.replace(aka_name.group(0), prefix, 1)

        birth_death = re.search(re.escape(prefix) + bd_pattern, text)
        if birth_death:
            contents.append('born ' + birth_death.group(1) + ' in ' + birth_death.group(2))
            if birth_death.group(3):
                contents.append('died ' + birth_death.group(3) + ' in ' + birth_death.group(4))
                is_person.append(2)
            else:
                is_person.append(1)
            paren = '(' + '; '.join(contents) + ')'
            prefix = ' '.join([title_tc, paren]) + ': '
            text = text.replace(birth_death.group(0), prefix, 1)
        else:
            is_person.append(0)

        paren_pattern = '\(.+?\)'
        paren_text = re.search(paren_pattern, title)
        if paren_text:
            title = title.replace(paren_text.group(0), '').strip()

        title_fixed.append(title)
        text_fixed.append(text)

    df = pd.DataFrame(
        {
            # "article_id": id,
            "Title": title_fixed,
            "Alt Title": alt_title,
            "Field": grouping,
            "Is Person": is_person,
            "Text": text_fixed
        },
        index=id
    )

    return df

