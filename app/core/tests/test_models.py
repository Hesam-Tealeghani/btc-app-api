from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core import models


def sample_user(username='testuser', email='test@admin.com', password='testpassword'):
    """Creates a sample user"""
    return get_user_model().objects.create_user(username, email, password)

def sample_country(admin):
    """Creates a sample country by the given user"""
    return models.Country.objects.create(created_by=admin, name='test', code='000', 
                                         abreviation='TST', is_covered=True)

class ModelTest(TestCase):
    """ Test class for core app"""

    # def setUp(self):
    #     self.admin = sample_user()
    #     self.country = models.Country.objects.create(created_by=self.admin, name='test', code='000', 
    #                                      abreviation='TST', is_covered=True)

    def test_creat_user(self):
        """testing to creat e user is successful using email, username, country and password."""
        email = "test@test.com"
        username = "testusercreate"
        password = "Test1234"
        user = get_user_model().objects.create_user(
            email = email,
            username = username,
            password = password,
            nationality = sample_country(admin=sample_user())
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_requiered_username_field(self):
        """Testing that users can not be created without username"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="test@test.com", username=None, password="12345678")

    def test_creat_superuser(self):
        """Testing to create a new superuser using the commandline."""
        user = get_user_model().objects.create_superuser(
            "superusertst",
            email = "superuser@test.com",
            password = "passwordforsuperuser"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
    def test_country_creation(self):
        """Test that creating a new country works"""
        country = models.Country.objects.create(
            created_by = sample_user(),
            name='test',
            code='010',
            abreviation='TST',
            is_covered=True
        )

        self.assertEqual(country.name, 'test')
        self.assertEqual(str(country), 'test')
    
    def test_VirtualService_creation(self):
        """To Test creating virtual services, with and without price and cost"""
        service = models.VirtualService.objects.create(
            name = 'test service',
            price = 67.99,
            cost = 54,
            created_by = sample_user()
        )

        self.assertEqual(service.price, 67.99)
        self.assertEqual(service.cost, 54)
        self.assertEqual(str(service), 'test service')

    def test_goal_creation(self):
        """Test that the marketing goals are created successfully"""
        goal = models.MarketingGoal.objects.create(
            trading_name='test goal',
            legal_name='test name',
            trading_address='test address',
            postal_code='1234567',
            land_line='44332211',
            business_field='test field',
            created_by=sample_user()
        )
        self.assertEqual(goal.trading_name, 'test goal')
        self.assertEqual(goal.created_by.username, 'testuser')
        self.assertEqual(goal.get_status_display(), 'In Waiting Queue')
    
    def test_pos_create(self):
        """Test to create a compoany, model, and a pos related to them, 
           1. Test to create a company, 2. Test to create a model for company,
           3. Test to create a pos with large serial number to get validation error
           4. Test a validate data for pos"""
        admin = sample_user()
        company = models.POSCompany.objects.create(
            name = 'testCompany',
            serial_number_length = 8,
            created_by = admin
        )
        self.assertEqual(company.name, 'testCompany')
        self.assertEqual(company.serial_number_length, 8)
        model = models.PosModel.objects.create(
            name='testModel',
            company=company,
            hardware_cost=25,
            software_cost=25,
            price=79.99,
            created_by=admin
        )
        self.assertEqual(model.name, 'testModel')
        self.assertEqual(model.price, 79.99)
        self.assertEqual(str(model), 'testModel')
        with self.assertRaises(ValidationError):
            models.POS.objects.create(serial_number='1234567890',
                                      type="D",
                                      model=model,
                                      created_by=admin)
        pos = models.POS.objects.create(
                serial_number='12345678',
                type="D",
                model=model,
                created_by=admin  
        )
        self.assertEqual(str(pos), '12345678')
        self.assertEqual(pos.get_type_display(), 'Desktop')
        self.assertEqual(pos.serial_number, '12345678')
    
    def test_costumer_bank_name_legal_name(self):
        """To Test that the bank name and legal name should be equal"""
        admin = sample_user()
        country = sample_country(admin)
        with self.assertRaises(ValidationError):
            costumer = models.Costumer.objects.create(
                trading_name="test costumer",
                legal_name="test costumer",
                business_type="Pet",
                legal_entity="PuLC",
                business_date="2020-12-12",
                registered_address="test address",
                registered_postal_code="12345678",
                country=country,
                business_postal_code="4321",
                company_number="02112345678",
                land_line="09123456789",
                business_email="test@email.com",
                director_name="test director",
                director_phone="09312345678",
                director_email="director@test.email",
                director_address="where director lives",
                director_postal_code="000000",
                director_nationality=country,
                sort_code="1221",
                issuing_bank="test bank",
                account_number="0000-0000-0000-0000",
                business_bank_name="test costumer1",
                partner_name="partner",
                partner_address="where partner lives",
                partner_nationality=country,
                created_by=admin,
                last_updated_by=admin
            )

    def test_contract_create(self):
        """Test to create a costumer and create a contract
        1. Create a service.
        2. Create a POS.
        3. Create (Test) a costumer and a trading address.
        4. Create (Test) a contract for the costumer and services and POS.
        5. Create (Test) a PaperRoll Order for the costumer.
        6. Create (Test) a payment and an MID Revenue for the contract."""
        admin = sample_user()
        country = sample_country(admin)
        service = models.VirtualService.objects.create(
            name='test service',
            price=67.99,
            cost=54,
            created_by=admin,
        )
        company = models.POSCompany.objects.create(
            name='testCompany',
            serial_number_length=8,
            created_by=admin
        )
        model = models.PosModel.objects.create(
            name='testModel',
            company=company,
            hardware_cost=25,
            software_cost=25,
            price=79.99,
            created_by=admin
        )
        pos = models.POS.objects.create(
                serial_number='12345678',
                type="D",
                model=model,
                created_by=admin  
        )

        costumer = models.Costumer.objects.create(
            trading_name="test costumer",
            legal_name="test costumer",
            business_type="Pet",
            legal_entity="PuLC",
            business_date="2020-12-12",
            registered_address="test address",
            registered_postal_code="12345678",
            country=country,
            business_postal_code="4321",
            company_number="02112345678",
            land_line="09123456789",
            business_email="test@email.com",
            director_name="test director",
            director_phone="09312345678",
            director_email="director@test.email",
            director_address="where director lives",
            director_postal_code="000000",
            director_nationality=country,
            sort_code="1221",
            issuing_bank="test bank",
            account_number="0000-0000-0000-0000",
            business_bank_name="test costumer",
            partner_name="partner",
            partner_address="where partner lives",
            partner_nationality=country,
            created_by=admin,
            last_updated_by=admin
        )

        self.assertEqual(costumer.trading_name, "test costumer")
        self.assertEqual(costumer.get_business_type_display(), "Pet Services")
        self.assertEqual(costumer.country, country)
        self.assertEqual(str(costumer), "test costumer test costumer")

        contract = models.Contract.objects.create(
            costumer=costumer,
            face_to_face_saled=75,
            atv=23.12,
            annual_card_turnover=123.21,
            annual_total_turnover=1234.56,
            interchange=0.5,
            authorizathion_fee=0.5,
            pci_dss=0.5,
            acquire_name="EP",
            start_date="2020-12-12",
            end_date="2021-12-12",
            total_cost=210.00,
            total_price=270.00,
            created_by=admin
        )

        self.assertEqual(contract.costumer, costumer)
        self.assertEqual(contract.total_price - contract.total_cost, 60.00)
        self.assertEqual(str(contract), "test costumer test costumer Emerchant Pay")

        contract_pos = models.ContractPOS.objects.create(
            contract=contract,
            pos=pos,
            price=120.00,
            hardware_cost=25,
            software_cost=25,
            created_by=admin
        )

        self.assertEqual(contract_pos.contract, contract)
        self.assertEqual(contract_pos.pos, pos)
        self.assertEqual(contract_pos.price - (contract_pos.hardware_cost + contract_pos.software_cost), 70)

        contract_service = models.ContractService.objects.create(
            contract=contract,
            service=service,
            price=150.00,
            cost=110,
            created_by=admin
        )

        self.assertEqual(contract_service.contract, contract)
        self.assertEqual(contract_service.service, service)
        self.assertEqual(contract_service.price - contract_service.cost, 40)

        paper_roll = models.PaperRoll.objects.create(
            costumer=costumer,
            amount=10,
            cost=99.90,
            price=199.90,
            direct_debit_cost=12.00,
            ordered_date="2020-12-12 12:30:00",
            created_by=admin
        )

        self.assertEqual(paper_roll.costumer, costumer)
        self.assertEqual(paper_roll.price - paper_roll.cost - paper_roll.direct_debit_cost, 88)
        self.assertEqual(str(paper_roll), "test costumer test costumer 10 2020-12-12 12:30:00")

        payment = models.Payment.objects.create(
            contract=contract,
            date="2020-12-12",
            direct_debit_cost=12.00,
            created_by=admin
        )

        self.assertEqual(payment.contract, contract)
        self.assertEqual(payment.direct_debit_cost, 12.00)

        mid_revenue = models.MIDRevenue.objects.create(
            contract=contract,
            income=24.00,
            profit=4.00,
            date="2020-12-12",
            created_by=admin
        )

        self.assertEqual(mid_revenue.contract, contract)
        self.assertEqual(mid_revenue.profit, 4.00)

    @patch('uuid.uuid4')
    def test_user_image_file_name(self, mock_uuid):
        """Test that the image of the profile is uploaded in the current location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.profile_image_path(None, 'MyImage.jpg')
        excepted_path = f'uploads/user/{uuid}.jpg'
        self.assertEqual(file_path, excepted_path)