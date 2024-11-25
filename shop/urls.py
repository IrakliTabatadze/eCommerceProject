
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.ProductView.as_view(), name='index'),
    path('detail/<int:pk>/', views.ProductDetailView.as_view(), name='detail'),
    path('about/', views.AboutUsView.as_view(), name='about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)