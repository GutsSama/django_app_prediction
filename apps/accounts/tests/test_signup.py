from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupEmailTests(TestCase):

    def test_signup_with_existing_email_fails(self):
        # User déjà existant : on met username=email pour coller à ton choix
        User.objects.create_user(
            username="test@email.com",
            email="test@email.com",
            password="password123!",
            first_name="Jean",
            last_name="Dupont",
        )

        response = self.client.post(reverse("signup"), {
            "email": "test@email.com",  # ❌ déjà utilisé
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "password123!",
            "password2": "password123!",
        })

        # aucun nouvel user créé
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        # Vérifie que le form a une erreur email
        form = response.context["form"]
        self.assertIn("email", form.errors)

    def test_signup_with_email_without_at_fails(self):
        response = self.client.post(reverse("signup"), {
            "email": "testemail.com",  # ❌ pas de @
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "password123!",
            "password2": "password123!",
        })

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertIn("email", form.errors)

    def test_signup_with_email_without_domain_fails(self):
        response = self.client.post(reverse("signup"), {
            "email": "test@",  # ❌ pas de domaine
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "password123!",
            "password2": "password123!",
        })

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertIn("email", form.errors)

    def test_signup_with_different_passwords_fails(self):
        response = self.client.post(reverse("signup"), {
            "email": "test1@email.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password123!",
            "password2": "Password123?",  # ❌ différent
        })

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertIn("password2", form.errors)

    def test_signup_with_password_without_digit_fails(self):
        response = self.client.post(reverse("signup"), {
            "email": "test2@email.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password!",
            "password2": "Password!",
        })

        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())

    def test_signup_with_password_without_symbol_fails(self):
        response = self.client.post(reverse("signup"), {
            "email": "test4@email.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password123",
            "password2": "Password123",
        })

        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())

    def test_signup_redirects_if_user_already_authenticated(self):
        user = User.objects.create_user(
            username="test@email.com",
            email="test@email.com",
            password="Password123!",
            first_name="Jean",
            last_name="Dupont",
        )

        self.client.login(username="test@email.com", password="Password123!")

        response = self.client.get(reverse("signup"))
        self.assertRedirects(
            response,
            "/accueil",
            fetch_redirect_response=False
        )

    def test_signup_success_redirects_to_profile(self):
        response = self.client.post(reverse("signup"), {
            "email": "newuser@email.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password123!",
            "password2": "Password123!",
        })

        self.assertEqual(User.objects.count(), 1)
        self.assertRedirects(
            response,
            "/profile",
            fetch_redirect_response=False
        )

    def test_signup_page_loads(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_success_redirects_to_profile(self):
        response = self.client.post(reverse("signup"), {
            "email": "newuser@email.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password123!",
            "password2": "Password123!",
        })

        # ✅ 1 utilisateur créé
        self.assertEqual(User.objects.count(), 1)

        # ✅ l'utilisateur existe bien en base
        user = User.objects.get(email="newuser@email.com")

        # ✅ champs bien enregistrés
        self.assertEqual(user.first_name, "Paul")
        self.assertEqual(user.last_name, "Martin")
        self.assertEqual(user.email, "newuser@email.com")

        # ✅ mot de passe bien hashé (pas stocké en clair)
        self.assertTrue(user.check_password("Password123!"))

        # ✅ redirection vers profile
        self.assertRedirects(
            response,
            "/profile",
            fetch_redirect_response=False
        )
    def test_signup_page_contains_csrf_token(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_signup_post_without_csrf_is_forbidden(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("signup"), {
            "email": "csrf@test.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password123!",
            "password2": "Password123!",
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 0)
    def test_signup_double_submit_does_not_create_two_users(self):
        data = {
            "email": "double@click.com",
            "first_name": "Paul",
            "last_name": "Martin",
            "password1": "Password123!",
            "password2": "Password123!",
        }

        # 1er envoi
        r1 = self.client.post(reverse("signup"), data)
        self.assertEqual(User.objects.count(), 1)

        # 2e envoi (double clic / refresh / renvoi)
        r2 = self.client.post(reverse("signup"), data)

        # toujours 1 seul user en base
        self.assertEqual(User.objects.count(), 1)

        # et le 2e envoi doit être refusé (souvent status 200 avec erreurs form)
        self.assertIn(r2.status_code, (200, 302))
