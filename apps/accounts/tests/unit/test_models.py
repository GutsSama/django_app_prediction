"""
Tests UNITAIRES des modèles
Focus : logique métier, méthodes, relations
"""

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from apps.accounts.models import AccountUser, CounselorProfile

User = get_user_model()


class CustomUserModelTests(TestCase):
    """Tests pour CustomUser"""
    
    def test_create_regular_user(self):
        """Test : création d'un utilisateur normal"""
        user = User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
            first_name="Jean",
            last_name="Dupont",
        )
        
        # Vérifie les champs de base
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.username, "test@test.com")
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Dupont")
        
        # Vérifie que ce n'est pas un conseiller
        self.assertFalse(user.is_conseiller)
        
        # Vérifie que le mot de passe est hashé
        self.assertTrue(user.check_password("Password123!"))
        self.assertNotEqual(user.password, "Password123!")  # Pas en clair
    
    def test_create_conseiller(self):
        """Test : création d'un conseiller"""
        conseiller = User.objects.create_user(
            username="conseiller@test.com",
            email="conseiller@test.com",
            password="Password123!",
            is_conseiller=True,
        )
        
        self.assertTrue(conseiller.is_conseiller)
    
    def test_email_unique_constraint(self):
        """Test : contrainte d'unicité de l'email"""
        # Crée un utilisateur
        User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
        )
        
        # Le test vérifie que le même email ne peut pas être utilisé deux fois
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="test@test.com",  # Même username (car username=email)
                email="test@test.com",     # Même email
                password="Password456!",
            )
    
    def test_user_string_representation(self):
        """Test : représentation en chaîne du User"""
        user = User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
            first_name="Jean",
            last_name="Dupont",
        )
        
        # AbstractUser.__str__() retourne le username
        self.assertEqual(str(user), "test@test.com")


class AccountUserModelTests(TestCase):
    """Tests pour AccountUser"""
    
    def setUp(self):
        """Crée un utilisateur avant chaque test"""
        self.user = User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
        )
    
    def test_create_account_user_with_all_fields(self):
        """Test : création d'un AccountUser avec tous les champs"""
        account = AccountUser.objects.create(
            user=self.user,
            age=35,
            children=2,
            taille=175,
            poids=75,
            sex="male",
            is_fumeur="no",
            region="northeast",
        )
        
        # Vérifie tous les champs
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.age, 35)
        self.assertEqual(account.children, 2)
        self.assertEqual(account.taille, 175)
        self.assertEqual(account.poids, 75)
        self.assertEqual(account.sex, "male")
        self.assertEqual(account.is_fumeur, "no")
        self.assertEqual(account.region, "northeast")
    
    def test_account_user_str_method(self):
        """Test : méthode __str__"""
        account = AccountUser.objects.create(user=self.user)
        
        # Devrait retourner le username de l'utilisateur
        self.assertEqual(str(account), "test@test.com")
    
    def test_default_values(self):
        """Test : valeurs par défaut"""
        account = AccountUser.objects.create(user=self.user)
        
        # Champs avec null=True SANS default → None
        self.assertIsNone(account.age)
        self.assertIsNone(account.taille)
        self.assertIsNone(account.poids)
        
        # Champs avec default → valeur par défaut
        self.assertEqual(account.children, 0)           # default=0
        self.assertEqual(account.sex, "male")           # default='male'
        self.assertEqual(account.is_fumeur, "no")       # default='no'
        self.assertEqual(account.region, "northeast")   # default='northeast'
    
    def test_one_to_one_relationship(self):
        """Test : relation OneToOne avec CustomUser"""
        account = AccountUser.objects.create(user=self.user)
        
        # Accès depuis User vers AccountUser
        self.assertEqual(self.user.account_profile, account)
        
        # Accès depuis AccountUser vers User
        self.assertEqual(account.user, self.user)
    
    def test_cascade_delete(self):
        """Test : suppression en cascade"""
        account = AccountUser.objects.create(user=self.user)
        
        # Compte initial
        self.assertEqual(AccountUser.objects.count(), 1)
        
        # Supprime l'utilisateur
        self.user.delete()
        
        # AccountUser devrait être supprimé automatiquement
        self.assertEqual(AccountUser.objects.count(), 0)
    
    def test_sex_choices(self):
        """Test : choix du sexe"""
        account = AccountUser.objects.create(
            user=self.user,
            sex="female",
        )
        
        self.assertEqual(account.sex, "female")
        
        # Test avec "male"
        account2 = AccountUser.objects.create(
            user=User.objects.create_user(
                username="test2@test.com",
                email="test2@test.com",
                password="Password123!",
            ),
            sex="male",
        )
        
        self.assertEqual(account2.sex, "male")
    
    def test_is_fumeur_choices(self):
        """Test : choix fumeur/non-fumeur"""
        account_yes = AccountUser.objects.create(
            user=self.user,
            is_fumeur="yes",
        )
        self.assertEqual(account_yes.is_fumeur, "yes")
        
        account_no = AccountUser.objects.create(
            user=User.objects.create_user(
                username="test2@test.com",
                email="test2@test.com",
                password="Password123!",
            ),
            is_fumeur="no",
        )
        self.assertEqual(account_no.is_fumeur, "no")
    
    def test_region_choices(self):
        """Test : choix des régions"""
        regions = ['northeast', 'northwest', 'southeast', 'southwest']
        
        for region in regions:
            user = User.objects.create_user(
                username=f"test_{region}@test.com",
                email=f"test_{region}@test.com",
                password="Password123!",
            )
            account = AccountUser.objects.create(
                user=user,
                region=region,
            )
            self.assertEqual(account.region, region)


class CounselorProfileModelTests(TestCase):
    """Tests pour CounselorProfile"""
    
    def test_create_counselor_profile(self):
        """Test : création d'un CounselorProfile (vide pour l'instant)"""
        profile = CounselorProfile.objects.create()
        
        self.assertIsNotNone(profile.id)
        self.assertIsInstance(profile, CounselorProfile)