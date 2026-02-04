from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from ..models import AccountUser
from ..forms import AccountUserForm

User = get_user_model()


class ProfileViewTests(TestCase):
    """Tests pour la vue ProfileView"""

    def setUp(self):
        """Crée des utilisateurs pour les tests"""
        # Utilisateur normal
        self.user = User.objects.create_user(
            username="testuser@email.com",
            email="testuser@email.com",
            password="Password123!",
            first_name="Jean",
            last_name="Dupont",
        )
        
        # Utilisateur conseiller
        self.conseiller = User.objects.create_user(
            username="conseiller@email.com",
            email="conseiller@email.com",
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

    # ==================== TESTS D'AUTHENTIFICATION ====================

    def test_profile_redirects_anonymous_user_to_login(self):
        """Test : utilisateur non connecté est redirigé vers login"""
        response = self.client.get(reverse("profile"))
        
        # Doit rediriger vers la page de login
        self.assertEqual(response.status_code, 302)
        # L'URL de redirection devrait contenir 'login'
        self.assertIn("/login", response.url)

    def test_profile_accessible_to_authenticated_user(self):
        """Test : utilisateur connecté peut accéder à la page de profil"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        response = self.client.get(reverse("profile"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    # ==================== TESTS POUR CONSEILLERS ====================

    def test_profile_redirects_conseiller_to_accueil(self):
        """Test : conseiller est redirigé vers /accueil"""
        self.client.login(username="conseiller@email.com", password="Password123!")
        
        response = self.client.get(reverse("profile"))
        
        # Doit rediriger vers /accueil
        self.assertRedirects(
            response,
            "/accueil",
            fetch_redirect_response=False
        )

    def test_profile_post_redirects_conseiller_to_accueil(self):
        """Test : conseiller ne peut pas mettre à jour le profil via POST"""
        self.client.login(username="conseiller@email.com", password="Password123!")
        
        response = self.client.post(reverse("profile"), self.valid_profile_data)
        
        # Doit rediriger vers /accueil, pas traiter le formulaire
        self.assertRedirects(
            response,
            "/accueil",
            fetch_redirect_response=False
        )
        
        # Aucun AccountUser ne devrait être créé pour le conseiller
        self.assertEqual(AccountUser.objects.count(), 0)

    # ==================== TESTS CREATION AUTO AccountUser ====================

    def test_profile_creates_accountuser_if_not_exists(self):
        """Test : AccountUser est créé automatiquement si n'existe pas"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        # Avant l'accès, aucun AccountUser
        self.assertEqual(AccountUser.objects.count(), 0)
        
        response = self.client.get(reverse("profile"))
        
        # Après l'accès, AccountUser devrait exister
        self.assertEqual(AccountUser.objects.count(), 1)
        
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.user, self.user)
        
        # Vérifie les valeurs par défaut
        self.assertEqual(account_user.is_fumeur, "no")
        self.assertEqual(account_user.sex, "male")
        self.assertEqual(account_user.region, "northeast")
        self.assertEqual(account_user.children, 0)

    def test_profile_uses_existing_accountuser(self):
        """Test : si AccountUser existe déjà, il est utilisé (pas de doublon)"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        initial_count = AccountUser.objects.count()
        
        response = self.client.get(reverse("profile"))
        
        # Le compte devrait toujours être 1 (pas de doublon)
        self.assertEqual(AccountUser.objects.count(), initial_count)
        
        # L'objet retourné devrait être le même
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.id, existing_account.id)
        self.assertEqual(account_user.age, 30)  # Valeurs originales conservées

    # ==================== TESTS MISE A JOUR PROFIL ====================

    def test_profile_update_success_with_valid_data(self):
        """Test : mise à jour du profil avec données valides réussit"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Soumet le formulaire de mise à jour
        response = self.client.post(reverse("profile"), self.valid_profile_data)
        
        # Doit rediriger vers la page de profil
        self.assertRedirects(
            response,
            reverse("profile"),
            fetch_redirect_response=False
        )
        
        # Vérifie que les données ont été mises à jour
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.age, 35)
        self.assertEqual(account_user.children, 2)
        self.assertEqual(account_user.taille, 175)
        self.assertEqual(account_user.poids, 75)
        self.assertEqual(account_user.sex, "male")
        self.assertEqual(account_user.is_fumeur, "no")
        self.assertEqual(account_user.region, "northeast")

    def test_profile_update_shows_success_message(self):
        """Test : message de succès s'affiche après mise à jour"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
            follow=True  # Suivre la redirection pour voir le message
        )
        
        # Vérifie que le message de succès est présent
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Votre profil a été mis à jour avec succès.")
        self.assertEqual(messages[0].tags, "success")

    def test_profile_update_fails_with_invalid_age(self):
        """Test : mise à jour échoue avec age invalide"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Age invalide (< 18)
        invalid_data = self.valid_profile_data.copy()
        invalid_data["age"] = 15
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        # Doit rester sur la page (200) avec erreurs
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que les données n'ont PAS été modifiées
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.age, 30)  # Toujours 30, pas 15
        
        # Vérifie que le formulaire contient des erreurs
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)

    def test_profile_update_fails_with_invalid_bmi(self):
        """Test : mise à jour échoue avec BMI incohérent"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # BMI trop bas (taille 200cm, poids 30kg → BMI ~7.5)
        invalid_data = self.valid_profile_data.copy()
        invalid_data["taille"] = 200
        invalid_data["poids"] = 30
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        # Doit rester sur la page avec erreurs
        self.assertEqual(response.status_code, 200)
        
        # Données non modifiées
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.taille, 170)
        self.assertEqual(account_user.poids, 70)
        
        # Erreur de validation BMI
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_profile_update_fails_with_invalid_taille(self):
        """Test : mise à jour échoue avec taille invalide"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Taille invalide (> 250)
        invalid_data = self.valid_profile_data.copy()
        invalid_data["taille"] = 300
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        self.assertEqual(response.status_code, 200)
        
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.taille, 170)  # Non modifié
        
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("taille", form.errors)

    def test_profile_update_fails_with_invalid_poids(self):
        """Test : mise à jour échoue avec poids invalide"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Poids invalide (> 300)
        invalid_data = self.valid_profile_data.copy()
        invalid_data["poids"] = 350
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        self.assertEqual(response.status_code, 200)
        
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.poids, 70)  # Non modifié
        
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("poids", form.errors)

    def test_profile_update_fails_with_invalid_children(self):
        """Test : mise à jour échoue avec nombre d'enfants invalide"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Children invalide (> 15)
        invalid_data = self.valid_profile_data.copy()
        invalid_data["children"] = 20
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        self.assertEqual(response.status_code, 200)
        
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.children, 0)  # Non modifié
        
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("children", form.errors)

    # ==================== TESTS FORMULAIRE ====================

    def test_profile_form_is_accountuserform(self):
        """Test : le formulaire utilisé est bien AccountUserForm"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        response = self.client.get(reverse("profile"))
        
        form = response.context["form"]
        self.assertIsInstance(form, AccountUserForm)

    def test_profile_form_contains_all_fields(self):
        """Test : le formulaire contient tous les champs attendus"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        response = self.client.get(reverse("profile"))
        
        form = response.context["form"]
        expected_fields = ["age", "children", "taille", "poids", "sex", "is_fumeur", "region"]
        
        for field in expected_fields:
            self.assertIn(field, form.fields)

    # ==================== TESTS GET_OBJECT ====================

    def test_get_object_creates_with_defaults(self):
        """Test : get_object crée AccountUser avec valeurs par défaut"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        # Aucun AccountUser n'existe
        self.assertEqual(AccountUser.objects.count(), 0)
        
        response = self.client.get(reverse("profile"))
        
        account_user = AccountUser.objects.get(user=self.user)
        
        # Vérifie les valeurs par défaut
        self.assertEqual(account_user.is_fumeur, "no")
        self.assertEqual(account_user.sex, "male")
        self.assertEqual(account_user.region, "northeast")
        self.assertEqual(account_user.children, 0)
        # age et poids peuvent être None selon ton model

    def test_get_object_returns_existing_object(self):
        """Test : get_object retourne l'objet existant sans le modifier"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        # Crée un AccountUser avec des valeurs personnalisées
        custom_account = AccountUser.objects.create(
            user=self.user,
            age=40,
            children=3,
            taille=180,
            poids=80,
            sex="female",
            is_fumeur="yes",
            region="southwest",
        )
        
        response = self.client.get(reverse("profile"))
        
        # L'objet retourné devrait être le même
        returned_account = response.context["object"]
        self.assertEqual(returned_account.id, custom_account.id)
        
        # Les valeurs personnalisées devraient être conservées
        self.assertEqual(returned_account.age, 40)
        self.assertEqual(returned_account.sex, "female")
        self.assertEqual(returned_account.is_fumeur, "yes")

    # ==================== TESTS EDGE CASES ====================

    def test_profile_update_with_partial_data_fails(self):
        """Test : mise à jour avec données partielles échoue"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Données partielles (manque des champs requis)
        partial_data = {
            "age": 35,
            # "children" manquant
            # "taille" manquant
            # etc.
        }
        
        response = self.client.post(reverse("profile"), partial_data)
        
        # Doit échouer (selon les champs requis de ton model)
        self.assertEqual(response.status_code, 200)
        
        # Données non modifiées
        account_user = AccountUser.objects.get(user=self.user)
        self.assertEqual(account_user.age, 30)

    def test_profile_multiple_users_independent(self):
        """Test : chaque utilisateur a son propre AccountUser"""
        # Crée un deuxième utilisateur
        user2 = User.objects.create_user(
            username="user2@email.com",
            email="user2@email.com",
            password="Password123!",
        )
        
        # Connecte user1 et crée son profil
        self.client.login(username="testuser@email.com", password="Password123!")
        self.client.post(reverse("profile"), self.valid_profile_data)
        self.client.logout()
        
        # Connecte user2 et crée son profil
        self.client.login(username="user2@email.com", password="Password123!")
        user2_data = self.valid_profile_data.copy()
        user2_data["age"] = 40
        self.client.post(reverse("profile"), user2_data)
        
        # Vérifie que chaque utilisateur a son propre profil
        account_user1 = AccountUser.objects.get(user=self.user)
        account_user2 = AccountUser.objects.get(user=user2)
        
        self.assertNotEqual(account_user1.id, account_user2.id)
        self.assertEqual(account_user1.age, 35)
        self.assertEqual(account_user2.age, 40)

    def test_profile_update_preserves_unchanged_fields(self):
        """Test : les champs non modifiés sont préservés"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
        # Crée un AccountUser avec des valeurs spécifiques
        AccountUser.objects.create(
            user=self.user,
            age=30,
            children=2,
            taille=170,
            poids=70,
            sex="female",
            is_fumeur="yes",
            region="southwest",
        )
        
        # Met à jour seulement l'age
        update_data = {
            "age": 35,
            "children": 2,  # inchangé
            "taille": 170,  # inchangé
            "poids": 70,    # inchangé
            "sex": "female",  # inchangé
            "is_fumeur": "yes",  # inchangé
            "region": "southwest",  # inchangé
        }
        
        self.client.post(reverse("profile"), update_data)
        
        account_user = AccountUser.objects.get(user=self.user)
        
        # Age modifié
        self.assertEqual(account_user.age, 35)
        # Autres champs inchangés
        self.assertEqual(account_user.children, 2)
        self.assertEqual(account_user.sex, "female")
        self.assertEqual(account_user.is_fumeur, "yes")
        self.assertEqual(account_user.region, "southwest")

    # ==================== TESTS MESSAGES ====================

    def test_profile_update_no_message_on_get(self):
        """Test : pas de message lors de l'accès GET à la page"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        response = self.client.get(reverse("profile"), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        # Aucun message de succès ne devrait être présent
        success_messages = [m for m in messages if m.tags == "success"]
        self.assertEqual(len(success_messages), 0)

    def test_profile_update_shows_error_message_on_invalid_data(self):
        """Test : message d'erreur s'affiche avec données invalides"""
        self.client.login(username="testuser@email.com", password="Password123!")
        
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
        
        # Données invalides
        invalid_data = self.valid_profile_data.copy()
        invalid_data["age"] = 150
        
        response = self.client.post(reverse("profile"), invalid_data)
        
        # Le formulaire devrait avoir des erreurs
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        
        # Pas de redirection, donc pas de message via messages framework
        # Les erreurs sont dans le formulaire
        self.assertIn("age", form.errors)