import json
import os
import re
from datetime import datetime


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE_FILE = os.path.join(BASE_DIR, "database.txt")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "query_logs.json")


def _split_sql_values(values_block):
    rows = []
    current = []
    token = []
    in_string = False
    depth = 0
    i = 0

    while i < len(values_block):
        char = values_block[i]
        next_char = values_block[i + 1] if i + 1 < len(values_block) else ""

        if char == "'" and next_char == "'":
            token.append("'")
            i += 2
            continue

        if char == "'":
            in_string = not in_string
            i += 1
            continue

        if not in_string and char == "(":
            depth += 1
            token = []
            current = []
            i += 1
            continue

        if not in_string and char == ")":
            value = "".join(token).strip()
            if value:
                current.append(_coerce_value(value))
            if depth == 1 and current:
                rows.append(current)
            depth -= 1
            token = []
            i += 1
            continue

        if not in_string and depth == 1 and char == ",":
            current.append(_coerce_value("".join(token).strip()))
            token = []
            i += 1
            continue

        if depth >= 1:
            token.append(char)
        i += 1

    return rows


def _coerce_value(value):
    if value.upper() == "NULL":
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _parse_insert(content, table_name):
    pattern = re.compile(
        rf"INSERT\s+INTO\s+{re.escape(table_name)}\s*\((.*?)\)\s*VALUES\s*(.*?);",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return []

    columns = [column.strip() for column in match.group(1).split(",")]
    rows = _split_sql_values(match.group(2))
    return [dict(zip(columns, row)) for row in rows if len(row) == len(columns)]


def load_knowledge_base():
    if not os.path.exists(DATABASE_FILE):
        raise FileNotFoundError(f"Database file not found: {DATABASE_FILE}")

    with open(DATABASE_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    categories = _parse_insert(content, "kb_categories")
    users = _parse_insert(content, "kb_users")
    articles = _parse_insert(content, "kb_articles")
    feedback = _parse_insert(content, "kb_article_feedback")

    for index, category in enumerate(categories, 1):
        category["category_id"] = index

    for index, user in enumerate(users, 1):
        user["user_id"] = index

    for index, article in enumerate(articles, 1):
        article["article_id"] = index
        article["category"] = _name_by_id(categories, "category_id", article.get("category_id"), "category_name")
        article["author"] = _name_by_id(users, "user_id", article.get("author_id"), "full_name")

    for index, item in enumerate(feedback, 1):
        item["feedback_id"] = index
        item["article_title"] = _name_by_id(articles, "article_id", item.get("article_id"), "title")

    return {
        "categories": categories,
        "users": users,
        "articles": articles,
        "feedback": feedback,
    }


def _name_by_id(items, id_key, value, name_key):
    for item in items:
        if item.get(id_key) == value:
            return item.get(name_key, "Unknown")
    return "Unknown"


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def search_articles(query, limit=4):
    kb = load_knowledge_base()
    query_terms = tokenize(query)
    scored = []

    for article in kb["articles"]:
        haystack = " ".join(
            [
                article.get("title", ""),
                article.get("content", ""),
                article.get("category", ""),
                article.get("author", ""),
            ]
        )
        article_terms = tokenize(haystack)
        overlap = len(query_terms & article_terms)
        title_overlap = len(query_terms & tokenize(article.get("title", "")))
        score = overlap + (title_overlap * 2)

        if query.lower() in haystack.lower():
            score += 5

        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [article for _, article in scored[:limit]]


def search_users(query, limit=5):
    kb = load_knowledge_base()
    query_terms = tokenize(query)
    scored = []

    for user in kb["users"]:
        haystack = " ".join(
            [
                user.get("full_name", ""),
                user.get("email", ""),
                user.get("role", ""),
            ]
        )
        user_terms = tokenize(haystack)
        overlap = len(query_terms & user_terms)
        name_overlap = len(query_terms & tokenize(user.get("full_name", "")))
        email_overlap = len(query_terms & tokenize(user.get("email", "")))
        score = overlap + (name_overlap * 2) + (email_overlap * 2)

        if query.lower() in haystack.lower():
            score += 5

        if score > 0:
            scored.append((score, user))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [user for _, user in scored[:limit]]


def is_user_query(query):
    terms = tokenize(query)
    user_words = {
        "user",
        "users",
        "author",
        "authors",
        "email",
        "emails",
        "gmail",
        "mail",
        "mails",
        "role",
        "roles",
        "name",
        "names",
    }
    return bool(terms & user_words)


def get_rating_rows():
    kb = load_knowledge_base()
    rows = []
    for item in kb["feedback"]:
        rows.append(
            {
                "article": item.get("article_title", "Unknown"),
                "rating": item.get("rating", 0),
                "comment": item.get("comment", ""),
            }
        )
    return rows


def save_query(question, answer, source):
    logs = get_logs(limit=None)
    logs.insert(
        0,
        {
            "question": question,
            "answer": answer[:220] + "..." if len(answer) > 220 else answer,
            "full_answer": answer,
            "source": source,
            "timestamp": datetime.now().isoformat(),
        },
    )

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs[:100], file, indent=2)


def get_logs(limit=20):
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if limit is None:
        return logs
    return logs[:limit]
