from rest_framework import serializers
from core.models import Country, POSCompany, PosModel, POS, VirtualService, MarketingGoal, \
     Costumer, Contract, ContractPOS, ContractService, PaperRoll, Payment, MIDRevenue, TradingAddress
from django.core.exceptions import ValidationError
from datetime import datetime
from admins.serializers import CreatingAdminSerializer


def dateToString(date):
    """Change the date format"""
    year = date.year
    month = date.month 
    day = date.day

    if month < 10:
        month = '0' + str(month)

    if day < 10:
        day = '0' + str(day)

    return str(year) + '-' + str(month) + '-' + str(day)


def dateTimeToString(datetime):
    """Change the date time format"""
    year = datetime.year
    month = datetime.month
    day = datetime.day
    hour = datetime.hour
    minute = datetime.minute

    if month < 10:
        month = '0' + str(month)

    if day < 10:
        month = '0' + str(day)

    return str(year) + '-' + str(month) + '-' + str(day) + '   ' + str(hour) + ':' + str(minute)


class CountrySerializer(serializers.ModelSerializer):
    """The Country serializer"""

    class Meta:
        model = Country
        verbose_name_plural = 'Countries'
        fields = ('id', 'name', 'code', 'abreviation', 'is_covered')
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }


class NationalitySerializer(serializers.ModelSerializer):
    """The minima serializer for other models using nationality field"""
    class Meta:
        model = Country
        fields = ['id', 'name', 'abreviation']
        read_only_fields = ['id', 'name', 'abreviation']


class POSCompanySerializer(serializers.ModelSerializer):
    """The pos company serializer"""
    model_count = serializers.SerializerMethodField()
    class Meta:
        model = POSCompany
        verbose_name_plural = 'Pos Companies'
        fields = ('id', 'name', 'serial_number_length', 'created_by', 'model_count')
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'model_count': {
                'read_only': True
            }
        }
    
    def get_model_count(self, instance):
        """To get the amount of models for a specific pos company"""
        return instance.pos_models.count()

    

class PosModelSerializer(serializers.ModelSerializer):
    """The POS model serializer"""
    company = POSCompanySerializer(read_only=True)
    class Meta:
        model = PosModel
        fields = ('id', 'name', 'hardware_cost', 'software_cost','price', 'created_by', 'company')
        extra_kwargs = {
            'id': {
                'read_only': True
            }, 
            'company': {
                'required': False
            }
        }


class PosSerializer(serializers.ModelSerializer):
    """The pos serializer"""
    created_by = CreatingAdminSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    model = PosModelSerializer(read_only=True)
    contract_id = serializers.SerializerMethodField()
    class Meta:
        model = POS
        fields = ['id', 'created_at', 'created_by', 'serial_number', 'type', 'note',
                  'ownership', 'is_active', 'status', 'type_name', 'model', 'contract_id']
        read_only_fields = ['id', 'created_at', 'created_by', 'contract_id']
    
    def get_created_at(self, obj):
        return dateToString(obj.created_at)

    def get_type_name(self,obj):
        return obj.get_type_display()

    def get_contract_id(self, obj):
        todayDate = datetime.now().date()
        for i in ContractPOS.objects.filter(pos=obj.id):
            contract = Contract.objects.get(pk=i.contract.id)
            startDate = contract.live_date
            endDate = contract.end_date
            if startDate <= todayDate <= endDate:
                return contract.id
        return 0


class ServiceSerializer(serializers.ModelSerializer):
    """The virtual services serializer"""
    class Meta:
        model = VirtualService
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'created_by']


class GoalSerializer(serializers.ModelSerializer):
    """The Marketing goal serializer"""
    updated_at = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    last_update = CreatingAdminSerializer(read_only=True)
    class Meta:
        model = MarketingGoal
        fields = ['id', 'trading_name', 'created_at', 'status', 'last_update', 'updated_at', 'business_field']
        read_only_fields = ['id', 'created_at', 'last_update', 'updated_at']
    
    def get_updated_at(self, obj):
        return dateToString(obj.updated_at)

    def get_created_at(self, obj):
        return dateToString(obj.created_at)
    
    def get_status(self, obj):
        return obj.get_status_display()


class GoalDetailSerializer(serializers.ModelSerializer):
    """The Serializer for goal's Details"""
    updated_at = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    last_update = CreatingAdminSerializer(read_only=True)
    status_name = serializers.SerializerMethodField()
    class Meta:
        model = MarketingGoal
        fields = ['id', 'trading_name', 'created_at', 'status', 'last_update', 'updated_at', 'business_field', 'legal_name', 
                  'land_line', 'trading_address', 'postal_code', 'decision_maker', 'mobile', 'status_name',
                  'email', 'website', 'note']
        read_only_fields = ['id', 'created_at', 'last_update', 'updated_at', 'status_name']

    def get_updated_at(self, obj):
        return dateToString(obj.updated_at)
    def get_created_at(self, obj):
        return dateToString(obj.created_at)
    def get_status_name(self, obj):
        return obj.get_status_display()


class CostumerMiniSerializer(serializers.ModelSerializer):
    """The serializer for Costumer Suggestions"""
    class Meta:
        model = Costumer
        fields = ['id', 'legal_name', 'trading_name']
        read_only_fields = ['id']
    

class TradingAddressSerializer(serializers.ModelSerializer):
    """The serializer for managing Costumers' Trading Adresses"""
    class Meta:
        model = TradingAddress
        fields = ['address', 'id']
        read_only_fields = ['id']


class CostumerSerializer(serializers.ModelSerializer):
    """The serializer for managing Costumers"""
    country = NationalitySerializer()
    partner_nationality = NationalitySerializer()
    director_nationality = NationalitySerializer()
    registered_country = NationalitySerializer()
    trading_addresses = serializers.SerializerMethodField()
    business_type = serializers.SerializerMethodField()
    legal_entity = serializers.SerializerMethodField()
    class Meta:
        model = Costumer
        exclude = ['created_by', 'created_at', 'updated_at', 'last_updated_by', 'pob', 'kyc1_id', 
                   'kyc2_address_proof', 'kyb_peremises_photo', 'kyb_trading_address_proof'
                   ]
        read_only_fields = ['id']
    
    def get_trading_addresses(self, obj):
        tradingAddresses = TradingAddress.objects.filter(costumer=obj)
        if tradingAddresses.exists():
            serializer = TradingAddressSerializer(tradingAddresses, many=True)
            return serializer.data
        else:
            return []
    
    def get_business_type(self, obj):
        return obj.get_business_type_display()
    
    def get_legal_entity(self, obj):
        return obj.get_legal_entity_display()


class CustomerCreateSerializer(serializers.ModelSerializer):
    """To Manage Creating Customers"""
    class Meta:
        model = Costumer
        exclude = ['created_at', 'updated_at', 'last_updated_by', 'pob', 'kyc1_id', 
                   'kyc2_address_proof', 'kyb_peremises_photo', 'kyb_trading_address_proof'
                   ]
        read_only_fields = ['id', 'created_by']


class ContractSerializer(serializers.ModelSerializer):
    """The Serializer for creating Contracts"""
    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at']


class ContractDetailSerializer(serializers.ModelSerializer):
    """The Serializer for managing Contracts and showin costumers"""
    created_at = serializers.SerializerMethodField()
    costumer = CostumerSerializer(read_only=True)
    class Meta:
        model = Contract
        exclude = ['created_by']
        read_only_fields = ['id', 'created_at']

    def get_created_at(self, obj):
        return dateToString(obj.created_at)


class ContractListSerializer(serializers.ModelSerializer):
    """The serializer for listing contracts"""
    costumer = CostumerSerializer(read_only=True)
    business_type = serializers.SerializerMethodField()
    class Meta:
        model = Contract
        fields = ['id', 'm_id', 'live_date', 'end_date', 'costumer', 'business_type']

    def get_legal_name(self, obj):
        return obj.costumer.legal_name

    def get_trading_name(self, obj):
        return obj.costumer.trading_name
    
    def get_business_type(self, obj):
        return obj.costumer.get_business_type_display()
       

class PosConSerializer(serializers.ModelSerializer):
    """The pos serializer fro contracts"""
    model_name = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    class Meta:
        model = POS
        fields = ['id', 'serial_number', 'type_name', 'model_name', 'company_name']
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def get_type_name(self,obj):
        return obj.get_type_display()
    
    def get_model_name(self, obj):
        return obj.model.name
    
    def get_company_name(self, obj):
        return obj.model.company.name


class ContractPosSerializer(serializers.ModelSerializer):
    """To Provide poses of a contract"""
    pos_detail = serializers.SerializerMethodField()
    class Meta:
        model = ContractPOS
        fields = ['pos', 'id', 'price', 'hardware_cost', 'software_cost', 'pos_detail']
        read_only_fields = ['id']
    
    def get_pos_detail(self, obj):
        return PosSerializer(obj.pos).data


class ContractServiceSerializer(serializers.ModelSerializer):
    """To Provide services of a contract"""
    service_name = serializers.SerializerMethodField()
    class Meta:
        model = ContractService
        fields = ['service', 'id', 'price', 'cost', 'service_name']
        read_only_fields = ['id']
    
    def get_service_name(self, obj):
        return obj.service.name


class CostumerPaperrollSerializer(serializers.ModelSerializer):
    """To Manage paper rolls of a costumer"""
    date = serializers.SerializerMethodField()
    class Meta:
        model = PaperRoll
        fields = ['amount', 'cost', 'price', 'direct_debit_cost', 'ordered_date', 'id', 'date']
        read_only_fields = ['id']
    
    def get_date(self, obj):
        return dateTimeToString(obj.ordered_date)


class PaymentSerializer(serializers.ModelSerializer):
    """To manage Payments"""
    class Meta:
        model = Payment
        fields = ['id', 'date', 'direct_debit_cost']
        read_only_fields = ['id']


class MIDRevenueSerializer(serializers.ModelSerializer):
    """To manage mid revenues"""
    class Meta:
        model = MIDRevenue
        fields = ['id', 'income', 'profit', 'date']
        read_only_fields = ['id']


class CustomerFileSerializer(serializers.ModelSerializer):
    """To manage uploading files"""
    class Meta:
        model = Costumer
        fields = ['pob', 'kyc1_id', 'kyc2_address_proof', 'kyb_peremises_photo', 'kyb_trading_address_proof']


class ContractFileSerializer(serializers.ModelSerializer):
    """To manage uploading files"""
    class Meta:
        model = Contract
        fields = ['acquire_application', 'financial_report', 'vat_return', 'fd_consent', 'credit_search']
