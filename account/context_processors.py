def user_name_context(request):
    if request.user.is_authenticated:
        return {'user_name': request.user.get_username()}
    return {}