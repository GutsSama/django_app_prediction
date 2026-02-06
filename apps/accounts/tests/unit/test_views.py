"""
Tests UNITAIRES des vues
Focus : permissions, redirections, templates, messages
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from apps.accounts.models import AccountUser

User = get_user_model()


class SignupViewTests(TestCase):
    """Tests pour SignupView"""
    
    def test_signup_page_loads(self):
        """Test : page d'inscription s'affiche"""
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
    
    def test_signup_redirects_authenticated_user(self):
        """Test : utilisateur connecté redirigé vers /accueil"""
        # Crée et connecte un utilisateur
        user = User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
        )
        self.client.login(username="test@test.com", password="Password123!")
        
        # Tente d'accéder à signup
        response = self.client.get(reverse("signup"))
        
        # Doit rediriger vers /accueil
        self.assertRedirects(response, "/accueil", fetch_redirect_response=False)
    
    def test_signup_success_creates_user(self):
        """Test : inscription réussie crée un utilisateur"""
        # Compte initial
        initial_count = User.objects.count()
        
        # Soumet le formulaire d'inscription
        response = self.client.post(reverse("signup"), {
            "email": "newuser@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        })
        
        # Vérifie la redirection vers /profile
        self.assertRedirects(response, "/profile", fetch_redirect_response=False)
        
        # Vérifie qu'un utilisateur a été créé
        self.assertEqual(User.objects.count(), initial_count + 1)
        
        # Vérifie que l'utilisateur existe
        user = User.objects.get(email="newuser@test.com")
        self.assertEqual(user.username, "newuser@test.com")
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Dupont")
        self.assertTrue(user.check_password("Password123!"))
    
    def test_signup_success_logs_in_user(self):
        """Test : inscription réussie connecte automatiquement l'utilisateur"""
        response = self.client.post(reverse("signup"), {
            "email": "newuser@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }, follow=True)  # follow=True pour suivre la redirection
        
        # Vérifie que l'utilisateur est connecté
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].email, "newuser@test.com")
    
    def test_signup_success_shows_message(self):
        """Test : inscription réussie affiche un message de succès"""
        response = self.client.post(reverse("signup"), {
            "email": "newuser@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }, follow=True)
        
        # Récupère les messages
        messages_list = list(get_messages(response.wsgi_request))
        
        # Vérifie qu'il y a un message
        self.assertEqual(len(messages_list), 1)
        
        # Vérifie le contenu
        self.assertEqual(str(messages_list[0]), "Inscription réussie. Vous êtes maintenant connecté.")
        self.assertEqual(messages_list[0].tags, "success")
    
    def test_signup_invalid_form_shows_errors(self):
        """Test : formulaire invalide affiche les erreurs"""
        # Email manquant
        response = self.client.post(reverse("signup"), {
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        })
        
        # Doit rester sur la page (200)
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que le formulaire a des erreurs
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
    
    def test_signup_password_mismatch_fails(self):
        """Test : mots de passe différents échouent"""
        response = self.client.post(reverse("signup"), {
            "email": "test@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password456!",  # Différent
        })
        
        # Doit rester sur la page
        self.assertEqual(response.status_code, 200)
        
        # Vérifie l'erreur
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
    
    def test_signup_email_already_exists_fails(self):
        """Test : email déjà utilisé échoue"""
        # Crée un utilisateur existant
        User.objects.create_user(
            username="existing@test.com",
            email="existing@test.com",
            password="Password123!",
        )
        
        # Tente de s'inscrire avec le même email
        response = self.client.post(reverse("signup"), {
            "email": "existing@test.com",  # Déjà utilisé
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        })
        
        # Doit rester sur la page
        self.assertEqual(response.status_code, 200)
        
        # Vérifie l'erreur
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class CustomLoginViewTests(TestCase):
    """Tests pour CustomLoginView"""
    
    def setUp(self):
        """Crée un utilisateur pour les tests de login"""
        User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
        )
    
    def test_login_page_loads(self):
        """Test : page de login s'affiche"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
    
    def test_login_redirects_authenticated_user(self):
        """Test : utilisateur connecté redirigé vers /accueil"""
        # Connecte l'utilisateur
        self.client.login(username="test@test.com", password="Password123!")
        
        # Tente d'accéder à login
        response = self.client.get(reverse("login"))
        
        # Doit rediriger vers /accueil
        self.assertRedirects(response, "/accueil", fetch_redirect_response=False)
    
    def test_login_success_redirects_to_accueil(self):
        """Test : login réussi redirige vers /accueil"""
        response = self.client.post(reverse("login"), {
            "username": "test@test.com",
            "password": "Password123!",
        })
        
        # Doit rediriger vers /accueil
        self.assertRedirects(response, "/accueil", fetch_redirect_response=False)
    
    def test_login_success_logs_in_user(self):
        """Test : login réussi connecte l'utilisateur"""
        response = self.client.post(reverse("login"), {
            "username": "test@test.com",
            "password": "Password123!",
        }, follow=True)
        
        # Vérifie que l'utilisateur est connecté
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].email, "test@test.com")
    
    def test_login_success_shows_message(self):
        """Test : login réussi affiche un message de succès"""
        response = self.client.post(reverse("login"), {
            "username": "test@test.com",
            "password": "Password123!",
        }, follow=True)
        
        # Récupère les messages
        messages_list = list(get_messages(response.wsgi_request))
        
        # Vérifie qu'il y a un message
        self.assertEqual(len(messages_list), 1)
        
        # Vérifie le contenu
        self.assertEqual(str(messages_list[0]), "Vous êtes maintenant connecté.")
        self.assertEqual(messages_list[0].tags, "success")
    
    def test_login_invalid_credentials_fails(self):
        """Test : identifiants invalides échouent"""
        response = self.client.post(reverse("login"), {
            "username": "test@test.com",
            "password": "WrongPassword!",  # Mauvais mot de passe
        })
        
        # Doit rester sur la page (200)
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que l'utilisateur n'est PAS connecté
        self.assertFalse(response.context["user"].is_authenticated)
    
    def test_login_invalid_email_fails(self):
        """Test : email invalide échoue"""
        response = self.client.post(reverse("login"), {
            "username": "nonexistent@test.com",  # Email inexistant
            "password": "Password123!",
        })
        
        # Doit rester sur la page (200)
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que l'utilisateur n'est PAS connecté
        self.assertFalse(response.context["user"].is_authenticated)


class ProfileViewTests(TestCase):
    """Tests pour ProfileView"""
    
    def setUp(self):
        """Crée des utilisateurs pour les tests"""
        # Utilisateur normal
        self.user = User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
            first_name="Jean",
            last_name="Dupont",
        )
        
        # Utilisateur conseiller
        self.conseiller = User.objects.create_user(
            username="conseiller@test.com",
            email="conseiller@test.com",
            password="Password123!",
            first_name="Marie",
            last_name="Martin",
            is_conseiller=True,
        )
        
        # Données valides pour le formulaire
        self.valid_profile_data = {
            "age": 35,
            "children": 2,
            "taille": 175,
            "poids": 75,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
    
    # ===== TESTS D'AUTHENTIFICATION =====
    
    def test_profile_redirects_anonymous_user(self):
        """Test : utilisateur non connecté redirigé vers login"""
        response = self.client.get(reverse("profile"))
        
        # Doit rediriger vers login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
    
    def test_profile_accessible_to_authenticated_user(self):
        """Test : utilisateur connecté peut accéder à la page"""
        self.client.login(username="test@test.com", password="Password123!")
        
        response = self.client.get(reverse("profile"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
    
    # ===== TESTS DE PERMISSIONS (CONSEILLER) =====
    
    def test_profile_redirects_conseiller_to_accueil(self):
        """Test : conseiller redirigé vers /accueil"""
        self.client.login(username="conseiller@test.com", password="Password123!")
        
        response = self.client.get(reverse("profile"))
        
        # Doit rediriger vers /accueil
        self.assertRedirects(response, "/accueil", fetch_redirect_response=False)
    
    def test_profile_post_blocked_for_conseiller(self):
        """Test : conseiller ne peut pas soumettre le formulaire"""
        self.client.login(username="conseiller@test.com", password="Password123!")
        
        # Compte initial d'AccountUser
        initial_count = AccountUser.objects.count()
        
        # Tente de soumettre le formulaire
        response = self.client.post(reverse("profile"), self.valid_profile_data)
        
        # Doit rediriger vers /accueil
        self.assertRedirects(response, "/accueil", fetch_redirect_response=False)
        
        # Vérifie qu'aucun AccountUser n'a été créé
        self.assertEqual(AccountUser.objects.count(), initial_count)
    
    # ===== TESTS CREATION AUTO AccountUser =====
    
    def test_profile_creates_accountuser_if_not_exists(self):
        """Test : AccountUser créé automatiquement s'il n'existe pas"""
        self.client.login(username="test@test.com", password="Password123!")
        
        # Vérifie qu'aucun AccountUser n'existe avant
        self.assertEqual(AccountUser.objects.count(), 0)
        
        # Accède à la page de profil
        response = self.client.get(reverse("profile"))
        
        # Vérifie qu'un AccountUser a été créé
        self.assertEqual(AccountUser.objects.count(), 1)
        
        # Récupère l'AccountUser créé
        account_user = AccountUser.objects.get(user=self.user)
        
        # Vérifie les valeurs par défaut
        self.assertEqual(account_user.is_fumeur, "no")
        self.assertEqual(account_user.sex, "male")
        self.assertEqual(account_user.region, "northeast")
        self.assertEqual(account_user.children, 0)
        # age, taille, poids sont None car pas de default
    
    def test_profile_uses_existing_accountuser(self):
        """Test : si AccountUser existe → utilisé (pas de doublon)"""
        # Crée un AccountUser avant l'accès
        existing_account = AccountUser.objects.create(
            user=self.user,
            age=30,
            children=1,
            taille=170,
            poids=70,
            sex="male",
            is_fumeur="no",
            region="northeast",
        )
        
        # Connecte l'utilisateur
        self.client.login(username="test@test.com", password="Password123!")
        
        # Compte initial
        initial_count = AccountUser.objects.count()
        
        # Accède à la page
        response = self.client.get(reverse("profile"))
        
        # Vérifie qu'il n'y a toujours qu'un seul AccountUser
        self.assertEqual(AccountUser.objects.count(), initial_count)
        
        # Vérifie que c'est le même objet
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.id, existing_account.id)
        
        # Vérifie que les valeurs originales sont conservées
        self.assertEqual(account_user.age, 30)
    
    # ===== TESTS MISE A JOUR PROFIL =====
    
    def test_profile_update_success_with_valid_data(self):
        """Test : mise à jour du profil avec données valides"""
        self.client.login(username="test@test.com", password="Password123!")
        
        # Crée un AccountUser existant
        AccountUser.objects.create(
            user=self.user,
            age=30,
            children=0,
            taille=170,
            poids=70,
            sex="male",
            is_fumeur="no",
            region="northeast",
        )
        
        # Soumet le formulaire avec de nouvelles données
        response = self.client.post(reverse("profile"), self.valid_profile_data)
        
        # Vérifie la redirection
        self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
        
        # Récupère l'AccountUser mis à jour
        account_user = AccountUser.objects.get(user=self.user)
        
        # Vérifie chaque champ
        self.assertEqual(account_user.age, 35)
        self.assertEqual(account_user.children, 2)
        self.assertEqual(account_user.taille, 175)
        self.assertEqual(account_user.poids, 75)
        self.assertEqual(account_user.sex, "male")
        self.assertEqual(account_user.is_fumeur, "no")
        self.assertEqual(account_user.region, "northeast")
    
    def test_profile_update_shows_success_message(self):
        """Test : message de succès s'affiche après mise à jour"""
        self.client.login(username="test@test.com", password="Password123!")
        
        AccountUser.objects.create(
            user=self.user,
            age=30,
            children=0,
            taille=170,
            poids=70,
            sex="male",
            is_fumeur="no",
            region="northeast",
        )
        
        response = self.client.post(
            reverse("profile"),
            self.valid_profile_data,
            follow=True
        )
        
        # Récupère les messages
        messages_list = list(get_messages(response.wsgi_request))
        
        # Vérifie qu'il y a un message
        self.assertEqual(len(messages_list), 1)
        
        # Vérifie le contenu
        self.assertEqual(str(messages_list[0]), "Votre profil a été mis à jour avec succès.")
        self.assertEqual(messages_list[0].tags, "success")
    
    # ===== TESTS VALIDATION =====
    
    def test_profile_update_fails_with_invalid_age(self):
        """Test : mise à jour échoue avec age invalide"""
        self.client.login(username="test@test.com", password="Password123!")
        
        AccountUser.objects.create(
            user=self.user,
            age=30,
            children=0,
            taille=170,
            poids=70,
            sex="male",
            is_fumeur="no",
            region="northeast",
        )
        
        # Données avec age invalide
        invalid_data = self.valid_profile_data.copy()
        invalid_data["age"] = 15  # Moins de 18 ans
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        # Vérifie qu'on reste sur la page (200)
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que les données n'ont PAS été modifiées
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.age, 30)  # Toujours 30, pas 15
        
        # Vérifie que le formulaire a des erreurs
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)
    
    def test_profile_update_fails_with_invalid_bmi(self):
        """Test : mise à jour échoue avec BMI incohérent"""
        self.client.login(username="test@test.com", password="Password123!")
        
        AccountUser.objects.create(
            user=self.user,
            age=30,
            children=0,
            taille=170,
            poids=70,
            sex="male",
            is_fumeur="no",
            region="northeast",
        )
        
        # Données avec BMI trop bas
        invalid_data = self.valid_profile_data.copy()
        invalid_data["taille"] = 200
        invalid_data["poids"] = 30
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        # Vérifie qu'on reste sur la page
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que les données n'ont PAS été modifiées
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.taille, 170)
        self.assertEqual(account_user.poids, 70)
        
        # Vérifie l'erreur de validation BMI
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)  # Erreur globale