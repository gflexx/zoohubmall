from django.conf import settings

def shop(request):
    return{
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'site_description': settings.META_DESCRIPTION,
    } 
