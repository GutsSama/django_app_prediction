from django import forms
from apps.accounts.models import AccountUser


class PredictionForm(forms.ModelForm):
    """Formulaire pour la prédiction"""
    
    class Meta:
        model = AccountUser
        fields = ['age', 'sex', 'taille', 'poids', 'children', 'is_fumeur', 'region']
        
        labels = {
            'age': 'Âge',
            'sex': 'Sexe',
            'taille': 'Taille',
            'poids': 'Poids',
            'children': 'Nombre d\'enfants',
            'is_fumeur': 'Fumeur ?',
            'region': 'Région',
        }

        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Âge'
            }),
            'sex': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'taille': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Taille (cm)'
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Poids (kg)'
            }),
            'children': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre d\'enfants'
            }),
            'is_fumeur': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'choices': [('yes', 'Oui'), ('no', 'Non')]
            }),
            'region': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }


    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age < 18:
            raise forms.ValidationError("Vous devez avoir au moins 18 ans")

        if age > 125:
            raise forms.ValidationError("L’âge ne peut pas dépasser 120 ans")

        return age
    

    def clean_poids(self):
        poids = self.cleaned_data.get('poids')

        if poids > 300:
            raise forms.ValidationError("Le poids semble irréaliste")

        return poids

    def clean_taille(self):
        taille = self.cleaned_data.get('taille')

        if taille < 100 or taille > 250:
            raise forms.ValidationError("La taille doit être comprise entre 100 et 250 cm")

        return taille

    def clean_children(self):
        children = self.cleaned_data.get('children')

        if children > 15:
            raise forms.ValidationError("Valeur trop élevée")

        return children


    def clean(self):
        cleaned_data = super().clean()

        taille = cleaned_data.get('taille')
        poids = cleaned_data.get('poids')

        if taille and poids:
            taille_m = taille / 100
            bmi = poids / (taille_m ** 2)

            if bmi < 10 or bmi > 60:
                raise forms.ValidationError(
                    "Les valeurs de taille et de poids sont incohérentes"
                )

        return cleaned_data