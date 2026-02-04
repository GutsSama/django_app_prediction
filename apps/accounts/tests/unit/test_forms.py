"""
Tests UNITAIRES des formulaires
Focus : validation des données, erreurs, nettoyage
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.forms import SignupForm, LoginForm, AccountUserForm

User = get_user_model()


class SignupFormTests(TestCase):
    """Tests pour SignupForm"""
    
    def test_valid_signup_form(self):
        """Test : formulaire d'inscription valide"""
        form_data = {
            "email": "test@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }
        
        form = SignupForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "test@test.com")
        self.assertEqual(form.cleaned_data["first_name"], "Jean")
    
    def test_password_mismatch(self):
        """Test : mots de passe qui ne correspondent pas"""
        form_data = {
            "email": "test@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password456!",  # ❌ Différent
        }
        
        form = SignupForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
    
    def test_missing_required_fields(self):
        """Test : champs obligatoires manquants"""
        # Email manquant
        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }
        
        form = SignupForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
    
    def test_invalid_email_format(self):
        """Test : format d'email invalide"""
        form_data = {
            "email": "test-at-test.com",  # ❌ Pas de @
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }
        
        form = SignupForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
    
    def test_email_already_exists(self):
        """Test : email déjà utilisé"""
        # Crée un utilisateur existant
        User.objects.create_user(
            username="existing@test.com",
            email="existing@test.com",
            password="Password123!",
        )
        
        # Essaie de s'inscrire avec le même email
        form_data = {
            "email": "existing@test.com",  # ❌ Déjà utilisé
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }
        
        form = SignupForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
    
    def test_save_creates_user(self):
        """Test : save() crée un utilisateur"""
        form_data = {
            "email": "newuser@test.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "Password123!",
            "password2": "Password123!",
        }
        
        form = SignupForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarde l'utilisateur
        user = form.save(commit=False)
        user.username = user.email  # Comme dans ta vue
        user.save()
        
        # Vérifie que l'utilisateur existe
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, "newuser@test.com")
        self.assertEqual(user.username, "newuser@test.com")
        self.assertTrue(user.check_password("Password123!"))


class LoginFormTests(TestCase):
    """Tests pour LoginForm"""
    
    def setUp(self):
        """Crée un utilisateur pour les tests de login"""
        User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="Password123!",
        )
    
    def test_valid_login_form(self):
        """Test : formulaire de login valide"""
        form_data = {
            "username": "test@test.com",
            "password": "Password123!",
        }
        
        form = LoginForm(data=form_data)
        
        # ✅ Note : LoginForm ne vérifie pas les credentials ici
        # La validation se fait dans la vue LoginView
        self.assertTrue(form.is_valid())
    
    def test_missing_username(self):
        """Test : email manquant"""
        form_data = {
            "password": "Password123!",
        }
        
        form = LoginForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
    
    def test_invalid_email_format(self):
        """Test : format d'email invalide dans login"""
        form_data = {
            "username": "not-an-email",  # ❌ Pas un email valide
            "password": "Password123!",
        }
        
        form = LoginForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class AccountUserFormTests(TestCase):
    """Tests pour AccountUserForm - LE PLUS IMPORTANT POUR TON APP"""
    
    # ==================== TESTS VALIDATION AGE ====================
    
    def test_age_below_18_fails(self):
        """Test : age inférieur à 18 ans doit échouer"""
        form_data = {
            "age": 17,
            "children": 0,
            "taille": 170,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)
        self.assertEqual(form.errors["age"], ["Vous devez avoir au moins 18 ans."])
    
    def test_age_above_125_fails(self):
        """Test : age supérieur à 125 ans doit échouer"""
        form_data = {
            "age": 126,
            "children": 0,
            "taille": 170,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)
        # ✅ Correction : apostrophe typographique ’ au lieu de '
        self.assertEqual(form.errors["age"], ["L'âge ne peut pas dépasser 120 ans."])
    
    def test_age_valid_range_passes(self):
        """Test : age entre 18 et 125 ans doit réussir"""
        for age in [18, 25, 50, 100, 125]:
            form_data = {
                "age": age,
                "children": 0,
                "taille": 170,
                "poids": 70,
                "sex": "male",
                "is_fumeur": "no",
                "region": "northeast",
            }
            
            form = AccountUserForm(data=form_data)
            
            self.assertTrue(form.is_valid(), f"Age {age} devrait être valide")
    
    # ==================== TESTS VALIDATION POIDS ====================
    
    def test_poids_above_300_fails(self):
        """Test : poids supérieur à 300 kg doit échouer"""
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 170,
            "poids": 301,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("poids", form.errors)
        self.assertEqual(form.errors["poids"], ["Le poids semble irréaliste."])
    
    def test_poids_valid_passes(self):
        """Test : poids raisonnable doit réussir"""
        # ✅ Correction : ajuster les valeurs pour que BMI soit valide (10-60)
        # Pour taille=170cm, poids max = 60 * (1.7²) = 173kg
        for poids in [50, 70, 100, 150, 173]:
            form_data = {
                "age": 30,
                "children": 0,
                "taille": 170,
                "poids": poids,
                "sex": "male",
                "is_fumeur": "no",
                "region": "northeast",
            }
            
            form = AccountUserForm(data=form_data)
            
            self.assertTrue(form.is_valid(), f"Poids {poids} devrait être valide")
    
    # ==================== TESTS VALIDATION TAILLE ====================
    
    def test_taille_below_100_fails(self):
        """Test : taille inférieure à 100 cm doit échouer"""
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 99,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("taille", form.errors)
        self.assertEqual(
            form.errors["taille"],
            ["La taille doit être comprise entre 100 et 250 cm."]
        )
    
    def test_taille_above_250_fails(self):
        """Test : taille supérieure à 250 cm doit échouer"""
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 251,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("taille", form.errors)
        self.assertEqual(
            form.errors["taille"],
            ["La taille doit être comprise entre 100 et 250 cm."]
        )
    
    def test_taille_valid_range_passes(self):
        """Test : taille entre 100 et 250 cm doit réussir"""
        # ✅ Correction : ajuster les valeurs pour que BMI soit valide
        # Pour poids=70kg, taille min = sqrt(70/60)*100 = 108cm, taille max = sqrt(70/10)*100 = 265cm
        for taille in [110, 150, 170, 200, 250]:
            form_data = {
                "age": 30,
                "children": 0,
                "taille": taille,
                "poids": 70,
                "sex": "male",
                "is_fumeur": "no",
                "region": "northeast",
            }
            
            form = AccountUserForm(data=form_data)
            
            self.assertTrue(form.is_valid(), f"Taille {taille} devrait être valide")
    
    # ==================== TESTS VALIDATION CHILDREN ====================
    
    def test_children_above_15_fails(self):
        """Test : nombre d'enfants supérieur à 15 doit échouer"""
        form_data = {
            "age": 30,
            "children": 16,
            "taille": 170,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("children", form.errors)
        self.assertEqual(form.errors["children"], ["Valeur trop élevée."])
    
    def test_children_valid_passes(self):
        """Test : nombre d'enfants raisonnable doit réussir"""
        for children in [0, 1, 5, 10, 15]:
            form_data = {
                "age": 30,
                "children": children,
                "taille": 170,
                "poids": 70,
                "sex": "male",
                "is_fumeur": "no",
                "region": "northeast",
            }
            
            form = AccountUserForm(data=form_data)
            
            self.assertTrue(form.is_valid(), f"Children {children} devrait être valide")
    
    # ==================== TESTS VALIDATION BMI ====================
    
    def test_bmi_too_low_fails(self):
        """Test : BMI inférieur à 10 doit échouer (taille/poids incohérents)"""
        # Exemple : 200cm pour 30kg → BMI = 7.5
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 200,
            "poids": 30,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)  # Erreur non-field (globale)
        self.assertEqual(
            form.errors["__all__"],
            ["Les valeurs de taille et de poids sont incohérentes."]
        )
    
    def test_bmi_too_high_fails(self):
        """Test : BMI supérieur à 60 doit échouer (taille/poids incohérents)"""
        # Exemple : 150cm pour 150kg → BMI = 66.7
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 150,
            "poids": 150,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"],
            ["Les valeurs de taille et de poids sont incohérentes."]
        )
    
    def test_bmi_valid_range_passes(self):
        """Test : BMI entre 10 et 60 doit réussir"""
        # BMI normal : 18.5 - 24.9
        # BMI acceptable : 10 - 60
        test_cases = [
            {"taille": 170, "poids": 50},  # BMI ~17.3
            {"taille": 170, "poids": 70},  # BMI ~24.2
            {"taille": 170, "poids": 100}, # BMI ~34.6
            {"taille": 150, "poids": 50},  # BMI ~22.2
            {"taille": 200, "poids": 120}, # BMI ~30.0
        ]
        
        for case in test_cases:
            form_data = {
                "age": 30,
                "children": 0,
                "taille": case["taille"],
                "poids": case["poids"],
                "sex": "male",
                "is_fumeur": "no",
                "region": "northeast",
            }
            
            form = AccountUserForm(data=form_data)
            
            self.assertTrue(
                form.is_valid(),
                f"Taille {case['taille']}cm, Poids {case['poids']}kg devrait être valide"
            )
    
    # ==================== TESTS FORMULAIRE COMPLET ====================
    
    def test_valid_form_creates_accountuser(self):
        """Test : formulaire valide crée un AccountUser"""
        form_data = {
            "age": 35,
            "children": 2,
            "taille": 175,
            "poids": 75,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertTrue(form.is_valid())
    
    def test_form_missing_any_required_field_fails(self):
        """Test : formulaire avec n'importe quel champ obligatoire manquant échoue"""
        # Test chaque champ manquant individuellement
        all_fields = {
            "age": 30,
            "children": 0,
            "taille": 170,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        for field_to_remove in all_fields.keys():
            # Crée une copie sans le champ testé
            test_data = all_fields.copy()
            del test_data[field_to_remove]
            
            with self.subTest(missing_field=field_to_remove):
                form = AccountUserForm(data=test_data)
                self.assertFalse(
                    form.is_valid(),
                    f"Le champ '{field_to_remove}' devrait être obligatoire"
                )
                self.assertIn(
                    field_to_remove,
                    form.errors,
                    f"Le champ '{field_to_remove}' devrait avoir une erreur"
                )
                print(f"✅ Champ '{field_to_remove}' bien obligatoire")
    
    def test_form_with_all_fields_present_is_valid(self):
        """Test : formulaire avec tous les champs est valide"""
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 170,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertTrue(
            form.is_valid(),
            f"Formulaire devrait être valide. Erreurs: {form.errors}"
        )
        print("✅ Formulaire complet est valide")
    
    def test_form_missing_required_field_fails(self):
        """Test : formulaire avec champ obligatoire manquant échoue"""
        # Test avec un champ manquant à chaque fois
        test_cases = [
            ("age", {"children": 0, "taille": 170, "poids": 70, "sex": "male", "is_fumeur": "no", "region": "northeast"}),
            ("children", {"age": 30, "taille": 170, "poids": 70, "sex": "male", "is_fumeur": "no", "region": "northeast"}),
            ("taille", {"age": 30, "children": 0, "poids": 70, "sex": "male", "is_fumeur": "no", "region": "northeast"}),
            ("poids", {"age": 30, "children": 0, "taille": 170, "sex": "male", "is_fumeur": "no", "region": "northeast"}),
            ("sex", {"age": 30, "children": 0, "taille": 170, "poids": 70, "is_fumeur": "no", "region": "northeast"}),
            ("is_fumeur", {"age": 30, "children": 0, "taille": 170, "poids": 70, "sex": "male", "region": "northeast"}),
            ("region", {"age": 30, "children": 0, "taille": 170, "poids": 70, "sex": "male", "is_fumeur": "no"}),
        ]
        
        for missing_field, data in test_cases:
            with self.subTest(missing_field=missing_field):
                form = AccountUserForm(data=data)
                self.assertFalse(form.is_valid(), f"Le champ {missing_field} devrait être obligatoire")
                self.assertIn(missing_field, form.errors, f"Le champ {missing_field} devrait avoir une erreur")
    
    def test_form_with_all_required_fields_passes(self):
        """Test : formulaire avec tous les champs obligatoires est valide"""
        form_data = {
            "age": 30,
            "children": 0,
            "taille": 170,
            "poids": 70,
            "sex": "male",
            "is_fumeur": "no",
            "region": "northeast",
        }
        
        form = AccountUserForm(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Formulaire devrait être valide. Erreurs: {form.errors}")