def custom_auth(request):
    return {
        'session_authenticated': request.session.get('is_authenticated', False),
        'session_name': request.session.get('name'),
        'session_role': request.session.get('role'),
    }
