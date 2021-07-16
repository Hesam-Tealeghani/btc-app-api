from django.urls import path, include
from rest_framework.routers import DefaultRouter
from crm import views

router = DefaultRouter()
router.register('countries', views.CountryViewSet)
router.register('companies', views.POSCompanyViewSet)
router.register('poses', views.PosViewSet)
router.register('services', views.ServiceViewSet)
router.register('goals', views.GoalViewSet)
router.register('customers', views.CostumerViewSet)
router.register('contracts', views.ContractViewSet)
router.register('posmodels', views.POSModelViewset)

app_name = 'crm'

urlpatterns = [
    path('', include(router.urls), name='countries'),
    path('company/<int:pk>/models/', views.PosModelCompanyList.as_view(), name='company-models'),
    path('is-used/country/<int:pk>/', views.CountryIsUsed.as_view(), name='country-used'),
    path('is-used/company/<int:pk>/', views.CompanyIsUsed.as_view(), name='company-used'),
    path('is-used/model/<int:pk>/', views.PosModelIsUsed.as_view(), name='model-used'),
    path('is-used/pos/<int:pk>/', views.POSIsUsed.as_view(), name='pos-used'),
    path('is-used/service/<int:pk>/', views.ServiceIsUsed.as_view(), name='service-used'),
    path('pos-active/<int:pk>/', views.ActivePos.as_view(), name='pos-active'),
    path('allcustomers/', views.CostumerListViewSet.as_view(), name='all-custumors'),
    path('contracts/<int:pk>/pos/', views.ContractPosViewSet.as_view(), name='contract-pos'),
    path('contracts/<int:pk>/service/', views.ContractServiceViewSet.as_view(), name='contract-service'),
    path('contracts/<int:pk>/paperroll/', views.CostumerPaperRollViewSet.as_view(), name='contract-paperroll'),
    path('contracts/<int:pk>/payment/', views.PaymentViewSet.as_view(), name='contract-payment'),
    path('contracts/<int:pk>/mid/', views.MIDViewSet.as_view(), name='contract-mid'),
    path('services/<int:pk>/availability/', views.ServiceAvailability.as_view(), name='service-availability'),
    path('countries/<int:pk>/coverage/', views.CountryCoverage.as_view(), name='country-coverage'),
    path('customer/<int:pk>/address/', views.TradingAddressCreate.as_view(), name='create-address'),
    path('customer/<int:pk>/files/', views.CustomerFileAPIVIew.as_view(), name='customer-files'), 
    path('contract/<int:pk>/files/', views.ContractFileAPIVIew.as_view(), name='customer-files'), 
    path('contract/<int:pk>/solutions/', views.ContractSolutions.as_view(), name='contract-solutions'),
    path('contract-serivce/<int:pk>/', views.ContractServiceUpdate.as_view(), name='contract-service-update'),
    path('contract-pos/<int:pk>/', views.ContractPosUpdate.as_view(), name='contract-pos-update'), 
]
