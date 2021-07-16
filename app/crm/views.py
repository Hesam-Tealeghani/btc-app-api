from rest_framework import viewsets, mixins, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from core import models
from crm import serializers
from datetime import datetime


class BaseViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """Base ViewSet To create, delete and list"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """To assign the admin to the Serializer"""
        serializer.save(created_by=self.request.user)

class CountryViewSet(BaseViewSet):
    """Manage Countries"""
    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer

    def filter_queryset(self, queryset):
        """To order the queryset in alphabet order of abreviations"""
        return self.queryset.order_by('abreviation')


class POSCompanyViewSet(BaseViewSet):
    """Manage Companies"""
    serializer_class = (serializers.POSCompanySerializer)
    queryset = models.POSCompany.objects.all()
    
    def filter_queryset(self, queryset):
        """To order by name"""
        return self.queryset.order_by('name')


class POSModelViewset(BaseViewSet, mixins.UpdateModelMixin):
    """Manage pos models"""
    serializer_class = serializers.PosModelSerializer
    queryset = models.PosModel.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def filter_queryset(self, queryset):
        """To order by models"""
        return self.queryset.order_by('name')
    
    def perform_create(self, serializer):
        """To assing the pos Company"""
        pos_company = get_object_or_404(models.POSCompany, pk=self.request.data['company'])
        serializer.save(company=pos_company)


class PosModelCompanyList(generics.ListAPIView):
    """To retrieve models for a company"""
    serializer_class = serializers.PosModelSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """To return a filtered queryset"""
        pk = self.kwargs.get('pk')
        company = get_object_or_404(models.POSCompany, pk=pk)
        return models.PosModel.objects.filter(company=company)
    

class PosViewSet(BaseViewSet, mixins.UpdateModelMixin):
    """The view set to handle creating and listing poses"""
    queryset = models.POS.objects.all()
    serializer_class = serializers.PosSerializer

    def perform_create(self, serializer):
        """To assign the admin"""
        posModel = get_object_or_404(models.PosModel, pk=self.request.data['model'])
        serial_number_length = posModel.company.serial_number_length
        if len(serializer.validated_data['serial_number']) != serial_number_length:
            raise ValidationError('Invalid Serial Number Length')
        else:
            serializer.save(created_by=self.request.user, model=posModel)

    def filter_queryset(self, queryset):
        """To order by serial number"""
        return self.queryset.order_by('serial_number')
    
    def partial_update(self, request, pk=None):
        """To check the serial number length for updating"""
        pos = get_object_or_404(models.POS, pk=pk)
        if len(request.data['serial_number']) != pos.model.company.serial_number_length:
            raise ValidationError('Invalid Serial Number Length')
        else:
            return super().partial_update(request, pk)
    
    def update_items_status(self):
        """To Update status of poses (availablity)"""
        for i in models.POS.objects.all():
            found = False
            todayDate = datetime.now().date()
            for j in models.ContractPOS.objects.filter(pos=i.id):
                contract = models.Contract.objects.get(pk=j.contract.id)
                startDate = contract.live_date
                endDate = contract.end_date
                if startDate <= todayDate <= endDate:
                    i.status = False
                    found = True
                    break
            if not(found):
                i.status = True
            i.save()

    def list(self, request, *args, **kwargs):
        """To update items everytime in list returns"""
        self.update_items_status()
        return super().list(request, *args, **kwargs)


class ServiceViewSet(BaseViewSet, mixins.UpdateModelMixin):
    """The view set for virtual services"""
    queryset = models.VirtualService.objects.all()
    serializer_class = serializers.ServiceSerializer


class CountryIsUsed(APIView):
    """To check if the country is used"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """To return if the Country is used"""
        pk = kwargs.get('pk')
        country = get_object_or_404(models.Country, pk=pk)
        if (not(models.User.objects.filter(nationality=country).exists()) and 
           not(models.Costumer.objects.filter(country=country).exists()) and
           not(models.Costumer.objects.filter(director_nationality=country).exists()) and
           not(models.Costumer.objects.filter(partner_nationality=country).exists())):
            return Response(status=status.HTTP_200_OK, data={'used': False})
        else:
            return Response(status=status.HTTP_200_OK, data={'used': True})


class CompanyIsUsed(APIView):
    """To return if the poscompany is used"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """To return if the poscompany is used"""
        pk = kwargs.get('pk')
        company = get_object_or_404(models.POSCompany, pk=pk)
        if not(models.PosModel.objects.filter(company=company).exists()):
            return Response(status=status.HTTP_200_OK, data={'used': False})
        else:
            return Response(status=status.HTTP_200_OK, data={'used': True})


class PosModelIsUsed(APIView):
    """To return if the pos model is used"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """To return if the poscompany is used"""
        pk = kwargs.get('pk')
        model = get_object_or_404(models.PosModel, pk=pk)
        if not(models.POS.objects.filter(model=model).exists()):
            return Response(status=status.HTTP_200_OK, data={'used': False})
        else:
            return Response(status=status.HTTP_200_OK, data={'used': True})


class POSIsUsed(APIView):
    """To return if the pos is used"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """To return if the poscompany is used"""
        pk = kwargs.get('pk')
        pos = get_object_or_404(models.POS, pk=pk)
        if not(models.ContractPOS.objects.filter(pos=pos).exists()):
            return Response(status=status.HTTP_200_OK, data={'used': False})
        else:
            return Response(status=status.HTTP_200_OK, data={'used': True})


class ServiceIsUsed(APIView):
    """To return if the service is used"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """To return if the poscompany is used"""
        pk = kwargs.get('pk')
        service = get_object_or_404(models.VirtualService, pk=pk)
        if not(models.ContractService.objects.filter(service=service).exists()):
            return Response(status=status.HTTP_200_OK, data={'used': False})
        else:
            return Response(status=status.HTTP_200_OK, data={'used': True})


class ActivePos(APIView):
    """To handle activation of poses"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.PosSerializer

    def post(self, request, pk):
        pos = get_object_or_404(models.POS, pk=pk)
        pos.is_active = not(pos.is_active)
        pos.save()
        return Response(status=status.HTTP_200_OK)


class GoalViewSet(viewsets.ModelViewSet):
    """To manage marketing goals"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.GoalSerializer
    queryset = models.MarketingGoal.objects.all()

    def perform_create(self, serializer):
        """Create new Merketing Goal"""
        serializer.save(created_by=self.request.user, last_update=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate Serializer"""
        if self.action == "retrieve" or self.action == "update" or self.action == "create" or self.action == "partial_update":
            return serializers.GoalDetailSerializer
        return self.serializer_class
    
    def perform_update(self, serializer):
        """To update the marketing goal"""
        serializer.save(last_update=self.request.user)


class CostumerListViewSet(generics.ListAPIView):
    """The viewset to handle the mini-list of Costumers"""
    serializer_class = serializers.CostumerMiniSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Costumer.objects.all()


class CostumerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
    """The viewset to handle creating and updating Costumers"""
    serializer_class = serializers.CustomerCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Costumer.objects.all()

    def perform_create(self, serializer):
        """To assign the user"""
        serializer.save(created_by=self.request.user, last_updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """To assign the user who has updated"""
        serializer.save(last_update_by=self.request.user)
    
    def get_serializer_class(self):
        """To assign the right serializer class"""
        if self.action == 'retrieve':
            return serializers.CostumerSerializer
        else:
            return self.serializer_class


class ContractViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """The viewset to handle creating and showing contracts"""
    serializer_class = serializers.ContractSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Contract.objects.all()

    def perform_create(self, serializer):
        """To assign the user"""
        serializer.save(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ContractListSerializer
        if self.action == 'retrieve':
            return serializers.ContractDetailSerializer
        return self.serializer_class


class ContractPosViewSet(generics.ListCreateAPIView):
    """To see and add poses of a contract"""
    serializer_class = serializers.ContractPosSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.ContractPOS.objects.all()

    def get_queryset(self):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        return models.ContractPOS.objects.filter(contract=contract)
    
    def perform_create(self, serializer):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        serializer.save(created_by=self.request.user, contract=contract)


class ContractServiceViewSet(generics.ListCreateAPIView):
    """To see and add virtual services of a contract"""
    serializer_class = serializers.ContractServiceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.ContractService.objects.all()

    def get_queryset(self):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        return models.ContractService.objects.filter(contract=contract)
    
    def perform_create(self, serializer):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        serializer.save(created_by=self.request.user, contract=contract)


class CostumerPaperRollViewSet(generics.ListCreateAPIView, generics.DestroyAPIView):
    """To list, create and delete PaperRolls of a costumer"""
    serializer_class = serializers.CostumerPaperrollSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.PaperRoll.objects.all()

    def get_queryset(self):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        costumer = contract.costumer
        return models.PaperRoll.objects.filter(costumer=costumer)
    
    def perform_create(self, serializer):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        costumer = contract.costumer
        serializer.save(created_by=self.request.user, costumer=costumer)


class PaymentViewSet(generics.ListCreateAPIView, generics.DestroyAPIView):
    """To see and add virtual services of a contract"""
    serializer_class = serializers.PaymentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Payment.objects.all()

    def get_queryset(self):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        return models.Payment.objects.filter(contract=contract)
    
    def perform_create(self, serializer):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        serializer.save(created_by=self.request.user, contract=contract)


class MIDViewSet(generics.ListCreateAPIView, generics.DestroyAPIView):
    """To see and add virtual services of a contract"""
    serializer_class = serializers.MIDRevenueSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Payment.objects.all()

    def get_queryset(self):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        return models.MIDRevenue.objects.filter(contract=contract)
    
    def perform_create(self, serializer):
        contract_id = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=contract_id)
        serializer.save(created_by=self.request.user, contract=contract)


class ServiceAvailability(APIView):
    """The view to change the service availability"""
    serializer_class = serializers.ServiceSerializer
    authentication_classes = (TokenAuthentication,)
    prermission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        service = get_object_or_404(models.VirtualService, pk=pk)
        service.availability = not(service.availability)
        service.save()
        return Response(status=status.HTTP_200_OK)


class CountryCoverage(APIView):
    """The view to change the country is being covered"""
    serializer_class = serializers.CountrySerializer    
    authentication_classes = (TokenAuthentication,)
    prermission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        country = get_object_or_404(models.Country, pk=pk)
        country.is_covered = not(country.is_covered)
        country.save()
        return Response(status=status.HTTP_200_OK)


class TradingAddressCreate(APIView):
    """To create multiple addresses for one customer"""
    serializer_class = serializers.TradingAddressSerializer
    authentication_classes = (TokenAuthentication,)
    prermission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        customer = get_object_or_404(models.Costumer, pk=pk)
        for i in request.data:
            address = models.TradingAddress.objects.create(address=i['address'], costumer=customer)
            address.save()
        return Response(status=status.HTTP_201_CREATED)


class ContractSolutions(APIView):
    """To create and assign multiple services and poses to a contract"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        contract = get_object_or_404(models.Contract, pk=pk)
        for i in request.data['services']:
            service = get_object_or_404(models.VirtualService, pk=i['id'])
            serviceContract = models.ContractService.objects.create(contract=contract, service=service, 
                                                                    price=i['price'], cost=i['cost'],
                                                                    created_by=request.user)
            serviceContract.save()
        for i in request.data['poses']:
            pos = get_object_or_404(models.POS, pk=i['id'])
            posContract = models.ContractPOS.objects.create(contract=contract, pos=pos, 
                                                                    price=i['price'], hardware_cost=i['hardware_cost'],
                                                                    software_cost=i['software_cost'], created_by=request.user)
            posContract.save()
        return Response(status=status.HTTP_201_CREATED)


class CustomerFileAPIVIew(generics.UpdateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.CustomerFileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Costumer

    def get_object(self):
        """Retrieve and return the customer admin"""
        pk = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=pk)
        customer = get_object_or_404(models.Costumer, pk=contract.costumer.id)
        return customer


class ContractFileAPIVIew(generics.UpdateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.ContractFileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Costumer

    def get_object(self):
        """Retrieve and return the customer admin"""
        pk = self.kwargs.get('pk')
        contract = get_object_or_404(models.Contract, pk=pk)
        return contract


class ContractServiceUpdate(generics.UpdateAPIView):
    """To update the price or cost of a service in a contract"""
    serializer_class = serializers.ContractServiceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.ContractService

    def get_object(self):
        """Retrieve and return the contract-services"""
        pk = self.kwargs.get('pk')
        contractService = get_object_or_404(models.ContractService, pk=pk)
        return contractService


class ContractPosUpdate(generics.UpdateAPIView):
    """To update the price or cost of a service in a contract"""
    serializer_class = serializers.ContractPosSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.ContractPOS

    def get_object(self):
        """Retrieve and return the contract-pos"""
        pk = self.kwargs.get('pk')
        contractPos = get_object_or_404(models.ContractPOS, pk=pk)
        return contractPos
