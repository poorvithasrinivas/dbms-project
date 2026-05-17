from django.urls import path
from . import views

urlpatterns=[

path('',views.dashboard),

path('add/',views.add_customer),

path('delete/<int:id>/',views.delete_customer),

path('deposit/',views.deposit),

path('withdraw/',views.withdraw),

path('transfer/',views.transfer),

path('transactions/',views.transactions),

]