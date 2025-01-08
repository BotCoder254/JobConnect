from flask import abort, request
from flask_login import current_user
from math import ceil

def check_role(required_role):
    if not current_user.is_authenticated or current_user.role != required_role:
        abort(403)

def paginate(collection_or_cursor, page=None, per_page=None):
    if page is None:
        page = int(request.args.get('page', 1))
    if per_page is None:
        per_page = int(request.args.get('per_page', 10))
    
    # Convert cursor to list if needed
    if hasattr(collection_or_cursor, 'collection'):
        # It's a cursor
        total = collection_or_cursor.collection.count_documents(collection_or_cursor._Cursor__spec or {})
        items = list(collection_or_cursor.skip((page - 1) * per_page).limit(per_page))
    else:
        # It's a collection
        total = collection_or_cursor.count_documents({})
        items = list(collection_or_cursor.find().skip((page - 1) * per_page).limit(per_page))
    
    total_pages = ceil(total / per_page)
    
    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
