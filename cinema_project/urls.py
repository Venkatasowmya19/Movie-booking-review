from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize Admin site headers for cinema theme
admin.site.site_header = "CineSphere Portal Admin"
admin.site.site_title = "CineSphere Admin Portal"
admin.site.index_title = "Cinema Booking & Reviews Management"
