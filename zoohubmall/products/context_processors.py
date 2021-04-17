from .models import Category

# make categories available sitewide
def product_categories(request):
	return {
	    'categories' : Category.objects.all().order_by('name'),
	}
