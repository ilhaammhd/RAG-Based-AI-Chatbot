import kb_loader


def get_all_articles():
    return kb_loader.load_knowledge_base()["articles"]


def get_all_users():
    return kb_loader.load_knowledge_base()["users"]


def get_all_categories():
    return kb_loader.load_knowledge_base()["categories"]


def get_all_feedback():
    return kb_loader.load_knowledge_base()["feedback"]


def log_user_query(question, answer, source):
    kb_loader.save_query(question, answer, source)


def get_recent_queries(limit=20):
    return kb_loader.get_logs(limit=limit)
