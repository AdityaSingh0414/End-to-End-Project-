import re

def is_safe_sql(query):
    """Blocks dangerous SQL commands."""
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'INSERT', 'UPDATE', 'CREATE', 'GRANT', 'REVOKE']
    query_upper = query.upper()
    
    # Check if the query starts with a disallowed keyword or contains them
    for keyword in dangerous_keywords:
        if re.search(rf'\b{keyword}\b', query_upper):
            return False, f"Dangerous operation detected: {keyword}. Only SELECT statements are allowed."
            
    if not query_upper.strip().startswith('SELECT'):
        return False, "Query must start with SELECT."
        
    return True, "Safe"
