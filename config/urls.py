from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='schedule:index'), name='home'),
    path('master/', include('master.urls', namespace='master')),
    path('schedule/', include('schedule.urls', namespace='schedule')),
    path('actual/', include('actual.urls', namespace='actual')),
    path('comparison/', include('comparison.urls', namespace='comparison')),
    path('import/', include('importer.urls', namespace='importer')),
]
