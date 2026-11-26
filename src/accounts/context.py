from .permissions import role_for

def role_context(request):
    return {"business_role": role_for(request.user)}
