from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from apps.accounts.models import AccountUser, CounselorProfile, Appointment

CustomUser = get_user_model()

class CustomUserModelTest(TestCase):
    """Tests pour le modèle CustomUser"""
    
    def setUp(self):
        """Création des données de test"""
        # Créer un conseiller
        self.conseiller_user = CustomUser.objects.create_user(
            username='conseiller_test',
            email='conseiller@test.com',
            password='testpass123',
            is_conseiller=True
        )
        
        # Créer un conseiller profile
        self.conseiller_profile = CounselorProfile.objects.create(
            user=self.conseiller_user,
            description="Conseiller test pour les tests"
        )
        
        # Créer un client normal
        self.client_user = CustomUser.objects.create_user(
            username='client_test',
            email='client@test.com',
            password='testpass123'
        )
    
    def test_create_custom_user(self):
        """Test de création d'un utilisateur personnalisé"""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertFalse(user.is_conseiller)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test de création d'un superutilisateur"""
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
    
    def test_user_with_conseiller(self):
        """Test de l'association d'un conseiller à un utilisateur"""
        client = CustomUser.objects.create_user(
            username='client_avec_conseiller',
            email='client_conseiller@test.com',
            password='testpass123'
        )
        client.conseiller = self.conseiller_profile
        client.save()
        
        self.assertEqual(client.conseiller, self.conseiller_profile)
        self.assertIn(client, self.conseiller_profile.clients.all())
    
    def test_email_unique_constraint(self):
        """Test de l'unicité de l'email"""
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                username='duplicate',
                email='client@test.com',  # Email déjà utilisé
                password='testpass123'
            )


class AccountUserModelTest(TestCase):
    """Tests pour le modèle AccountUser"""
    
    def setUp(self):
        """Création des données de test"""
        self.user = CustomUser.objects.create_user(
            username='test_account',
            email='account@test.com',
            password='testpass123'
        )
    
    def test_create_account_user(self):
        """Test de création d'un profil utilisateur"""
        account = AccountUser.objects.create(
            user=self.user,
            age=30,
            children=2,
            taille=175,
            poids=70,
            sex='male',
            is_fumeur='no',
            region='northeast'
        )
        
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.age, 30)
        self.assertEqual(account.children, 2)
        self.assertEqual(account.taille, 175)
        self.assertEqual(account.poids, 70)
        self.assertEqual(account.sex, 'male')
        self.assertEqual(account.is_fumeur, 'no')
        self.assertEqual(account.region, 'northeast')
    
    def test_account_user_defaults(self):
        """Test des valeurs par défaut"""
        account = AccountUser.objects.create(
            user=self.user
        )
        
        self.assertIsNone(account.age)
        self.assertEqual(account.children, 0)
        self.assertIsNone(account.taille)
        self.assertIsNone(account.poids)
        self.assertEqual(account.sex, 'male')  # default
        self.assertEqual(account.is_fumeur, 'no')  # default
        self.assertEqual(account.region, 'northeast')  # default
    
    def test_account_user_str(self):
        """Test de la méthode __str__"""
        account = AccountUser.objects.create(user=self.user)
        self.assertEqual(str(account), 'test_account')
    
    def test_account_user_relationship(self):
        """Test de la relation OneToOne avec CustomUser"""
        account = AccountUser.objects.create(user=self.user)
        self.assertEqual(self.user.account_profile, account)
        self.assertEqual(account.user.username, 'test_account')


class CounselorProfileModelTest(TestCase):
    """Tests pour le modèle CounselorProfile"""
    
    def setUp(self):
        """Création des données de test"""
        self.conseiller_user = CustomUser.objects.create_user(
            username='conseiller_profile',
            email='conseiller_profile@test.com',
            password='testpass123',
            is_conseiller=True
        )
    
    def test_create_counselor_profile(self):
        """Test de création d'un profil conseiller"""
        profile = CounselorProfile.objects.create(
            user=self.conseiller_user,
            description="Expert en assurance santé avec 10 ans d'expérience"
        )
        
        self.assertEqual(profile.user, self.conseiller_user)
        self.assertEqual(profile.description, "Expert en assurance santé avec 10 ans d'expérience")
        self.assertEqual(profile.user.username, 'conseiller_profile')
    
    def test_counselor_profile_str(self):
        """Test de la méthode __str__"""
        profile = CounselorProfile.objects.create(
            user=self.conseiller_user,
            description="Description test"
        )
        self.assertEqual(str(profile), 'Conseiller: conseiller_profile')
    
    def test_counselor_profile_relationship(self):
        """Test de la relation OneToOne avec CustomUser"""
        profile = CounselorProfile.objects.create(user=self.conseiller_user)
        self.assertEqual(self.conseiller_user.profile, profile)
    
    def test_counselor_with_clients(self):
        """Test de la relation inverse avec les clients"""
        profile = CounselorProfile.objects.create(user=self.conseiller_user)
        
        # Créer des clients associés à ce conseiller
        client1 = CustomUser.objects.create_user(
            username='client1',
            email='client1@test.com',
            password='testpass123'
        )
        client1.conseiller = profile
        client1.save()
        
        client2 = CustomUser.objects.create_user(
            username='client2',
            email='client2@test.com',
            password='testpass123'
        )
        client2.conseiller = profile
        client2.save()
        
        self.assertEqual(profile.clients.count(), 2)
        self.assertIn(client1, profile.clients.all())
        self.assertIn(client2, profile.clients.all())


class AppointmentModelTest(TestCase):
    """Tests pour le modèle Appointment"""
    
    def setUp(self):
        """Création des données de test"""
        # Créer un conseiller
        self.conseiller_user = CustomUser.objects.create_user(
            username='conseiller_app',
            email='conseiller_app@test.com',
            password='testpass123',
            is_conseiller=True
        )
        self.conseiller_profile = CounselorProfile.objects.create(
            user=self.conseiller_user,
            description="Conseiller pour tests de rendez-vous"
        )
        
        # Créer un client
        self.client_user = CustomUser.objects.create_user(
            username='client_app',
            email='client_app@test.com',
            password='testpass123'
        )
        
        # Date de rendez-vous future
        self.future_date = timezone.now() + timedelta(days=1)
        # Date de rendez-vous passée
        self.past_date = timezone.now() - timedelta(days=1)
    
    def test_create_appointment(self):
        """Test de création d'un rendez-vous"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date,
            status='pending'
        )
        
        self.assertEqual(appointment.client, self.client_user)
        self.assertEqual(appointment.conseiller, self.conseiller_profile)
        self.assertEqual(appointment.status, 'pending')
        self.assertEqual(appointment.appointment_date, self.future_date)
    
    def test_appointment_str(self):
        """Test de la méthode __str__"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date,
            status='pending'
        )
        
        expected_str = f"Rendez-vous de {self.client_user.username} avec {self.conseiller_user.username} à {self.future_date}"
        self.assertEqual(str(appointment), expected_str)
    
    def test_appointment_default_status(self):
        """Test du statut par défaut"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date
        )
        self.assertEqual(appointment.status, 'pending')
    
    def test_appointment_status_choices(self):
        """Test des choix de statut valides"""
        valid_statuses = ['pending', 'confirmed', 'completed', 'canceled']
        
        for status in valid_statuses:
            appointment = Appointment.objects.create(
                client=self.client_user,
                conseiller=self.conseiller_profile,
                appointment_date=self.future_date,
                status=status
            )
            self.assertEqual(appointment.status, status)
    
    def test_appointment_relationships(self):
        """Test des relations avec client et conseiller"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date
        )
        
        # Test relation client -> appointments
        self.assertIn(appointment, self.client_user.appointments.all())
        
        # Test relation conseiller -> appointments
        self.assertIn(appointment, self.conseiller_profile.appointments.all())
    
    def test_is_past_due_future_appointment(self):
        """Test is_past_due pour un rendez-vous futur"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date,
            status='pending'
        )
        self.assertFalse(appointment.is_past_due())
    
    def test_is_past_due_past_appointment_pending(self):
        """Test is_past_due pour un rendez-vous passé avec statut pending"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.past_date,
            status='pending'
        )
        self.assertTrue(appointment.is_past_due())
    
    def test_is_past_due_past_appointment_confirmed(self):
        """Test is_past_due pour un rendez-vous passé avec statut confirmed"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.past_date,
            status='confirmed'
        )
        self.assertTrue(appointment.is_past_due())
    
    def test_is_past_due_completed_appointment(self):
        """Test is_past_due pour un rendez-vous terminé (ne devrait pas être en retard)"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.past_date,
            status='completed'
        )
        self.assertFalse(appointment.is_past_due())
    
    def test_is_past_due_canceled_appointment(self):
        """Test is_past_due pour un rendez-vous annulé (ne devrait pas être en retard)"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.past_date,
            status='canceled'
        )
        self.assertFalse(appointment.is_past_due())
    
    def test_multiple_appointments_same_client(self):
        """Test de plusieurs rendez-vous pour le même client"""
        appointment1 = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date,
            status='pending'
        )
        
        appointment2 = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date + timedelta(days=1),
            status='confirmed'
        )
        
        self.assertEqual(self.client_user.appointments.count(), 2)
        self.assertIn(appointment1, self.client_user.appointments.all())
        self.assertIn(appointment2, self.client_user.appointments.all())
    
    def test_multiple_appointments_same_conseiller(self):
        """Test de plusieurs rendez-vous pour le même conseiller"""
        # Créer un deuxième client
        client2 = CustomUser.objects.create_user(
            username='client2_app',
            email='client2_app@test.com',
            password='testpass123'
        )
        
        appointment1 = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date,
            status='pending'
        )
        
        appointment2 = Appointment.objects.create(
            client=client2,
            conseiller=self.conseiller_profile,
            appointment_date=self.future_date + timedelta(days=1),
            status='confirmed'
        )
        
        self.assertEqual(self.conseiller_profile.appointments.count(), 2)
        self.assertIn(appointment1, self.conseiller_profile.appointments.all())
        self.assertIn(appointment2, self.conseiller_profile.appointments.all())


class ModelIntegrationTest(TestCase):
    """Tests d'intégration entre les modèles"""
    
    def setUp(self):
        """Création des données de test"""
        # Créer un conseiller avec son profil
        self.conseiller_user = CustomUser.objects.create_user(
            username='conseiller_int',
            email='conseiller_int@test.com',
            password='testpass123',
            is_conseiller=True
        )
        self.conseiller_profile = CounselorProfile.objects.create(
            user=self.conseiller_user,
            description="Conseiller pour tests d'intégration"
        )
        
        # Créer un client avec son profil
        self.client_user = CustomUser.objects.create_user(
            username='client_int',
            email='client_int@test.com',
            password='testpass123'
        )
        self.client_account = AccountUser.objects.create(
            user=self.client_user,
            age=35,
            children=1,
            taille=180,
            poids=75,
            sex='male',
            is_fumeur='no',
            region='southeast'
        )
        
        # Associer le client au conseiller
        self.client_user.conseiller = self.conseiller_profile
        self.client_user.save()
    
    def test_complete_user_flow(self):
        """Test du flux complet utilisateur"""
        # Vérifier que le client a bien un conseiller
        self.assertEqual(self.client_user.conseiller, self.conseiller_profile)
        
        # Vérifier que le conseiller a bien le client dans sa liste
        self.assertIn(self.client_user, self.conseiller_profile.clients.all())
        
        # Vérifier que le client a un profil AccountUser
        self.assertEqual(self.client_user.account_profile, self.client_account)
        
        # Créer un rendez-vous
        appointment_date = timezone.now() + timedelta(days=2)
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=appointment_date,
            status='confirmed'
        )
        
        # Vérifier le rendez-vous
        self.assertEqual(appointment.client, self.client_user)
        self.assertEqual(appointment.conseiller, self.conseiller_profile)
        self.assertEqual(appointment.status, 'confirmed')
        
        # Vérifier les relations inverses
        self.assertIn(appointment, self.client_user.appointments.all())
        self.assertIn(appointment, self.conseiller_profile.appointments.all())
    
    def test_cascade_delete_user(self):
        """Test de la suppression en cascade d'un utilisateur"""
        # Créer un rendez-vous
        appointment_date = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=appointment_date
        )
        
        # Supprimer le client
        client_id = self.client_user.id
        self.client_user.delete()
        
        # Vérifier que le profil AccountUser est supprimé
        with self.assertRaises(AccountUser.DoesNotExist):
            AccountUser.objects.get(user_id=client_id)
        
        # Vérifier que le rendez-vous est supprimé (CASCADE)
        with self.assertRaises(Appointment.DoesNotExist):
            Appointment.objects.get(id=appointment.id)
    
    def test_set_null_conseiller(self):
        """Test de SET_NULL quand un profil conseiller est supprimé"""
        # Créer un rendez-vous
        appointment_date = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(
            client=self.client_user,
            conseiller=self.conseiller_profile,
            appointment_date=appointment_date
        )
        
        # Supprimer le PROFL CONSEILLER (pas l'utilisateur !)
        profile_id = self.conseiller_profile.id
        self.conseiller_profile.delete()  # ← On supprime le profil, pas l'user
        
        # Vérifier que le profil conseiller est bien supprimé
        with self.assertRaises(CounselorProfile.DoesNotExist):
            CounselorProfile.objects.get(id=profile_id)
        
        # Vérifier que le client a maintenant conseiller = None
        self.client_user.refresh_from_db()
        self.assertIsNone(self.client_user.conseiller)
        
        # Vérifier que le rendez-vous est aussi supprimé (car CASCADE sur Appointment.conseiller)
        with self.assertRaises(Appointment.DoesNotExist):
            Appointment.objects.get(id=appointment.id)