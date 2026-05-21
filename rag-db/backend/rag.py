import db_queries
import kb_loader


def _format_article_list(articles):
    if not articles:
        return "No matching articles were found in the uploaded database."

    lines = []
    for article in articles:
        lines.append(
            f"- **{article['title']}** ({article['category']}, author: {article['author']}): "
            f"{article['content']}"
        )
    return "\n".join(lines)


def _format_user_table(users):
    if not users:
        return "No matching users were found in the uploaded database."

    lines = ["| Name | Email | Role |", "|---|---|---|"]
    for user in users:
        lines.append(f"| {user['full_name']} | {user['email']} | {user['role']} |")
    return "\n".join(lines)


def _user_answer(query):
    kb = kb_loader.load_knowledge_base()
    users = kb_loader.search_users(query)
    if not users:
        users = kb["users"]

    return f"""## Summary
I found {len(users)} user record(s) from the uploaded database.

## Details
{_format_user_table(users)}

## Graph Description
Not applicable

## Follow-up Questions
- Which articles did each author write?
- Show only Author role users.
- Who authored Python articles?"""


def _rating_graph_answer():
    rows = kb_loader.get_rating_rows()
    table = "\n".join(
        ["| Article | Rating | Comment |", "|---|---:|---|"]
        + [f"| {row['article']} | {row['rating']} | {row['comment']} |" for row in rows]
    )
    average = sum(row["rating"] for row in rows) / len(rows) if rows else 0

    return f"""## Summary
The uploaded database contains {len(rows)} article feedback records. The average rating is {average:.1f} out of 5.

## Details
{table}

## Graph Description
Bar chart comparing article ratings from the feedback table.

## Follow-up Questions
- Which article has the highest rating?
- Which articles need better examples?
- Show all feedback comments."""


def _fallback_answer(query, articles):
    if not articles:
        return f"""## Summary
I could not find a matching article in the uploaded database for: "{query}".

## Details
Try asking about SQL Server, Python automation, email automation, DevOps, or JWT security. The app is reading from `database.txt`.

## Graph Description
Not applicable

## Follow-up Questions
- Show all available articles.
- What topics are in the knowledge base?
- Compare article ratings in a graph."""

    return f"""## Summary
I found {len(articles)} relevant article(s) in the uploaded database. The strongest match is **{articles[0]['title']}**.

## Details
{_format_article_list(articles)}

## Graph Description
Not applicable

## Follow-up Questions
- Show related articles from the same category.
- Who authored these articles?
- Compare article ratings in a graph."""


def query_rag(user_query):
    wants_graph = any(word in user_query.lower() for word in ["graph", "chart", "plot", "rating"])
    if wants_graph and "rating" in user_query.lower():
        answer = _rating_graph_answer()
        db_queries.log_user_query(user_query, answer, "database-feedback")
        return answer

    if kb_loader.is_user_query(user_query):
        answer = _user_answer(user_query)
        db_queries.log_user_query(user_query, answer, "database-users")
        return answer

    articles = kb_loader.search_articles(user_query, limit=4)
    answer = _fallback_answer(user_query, articles)
    db_queries.log_user_query(user_query, answer, "database-rag")
    return answer


def query_general(user_query):
    if kb_loader.is_user_query(user_query):
        return _user_answer(user_query)

    articles = kb_loader.search_articles(user_query, limit=4)
    return _fallback_answer(user_query, articles)
