from django import forms

class UserInputForm(forms.Form):
    recent_reads = forms.CharField(max_length=80, required=False)
    desired_feeling = forms.CharField(max_length=80, required=False)
    character_plot_preferences = forms.CharField(max_length=80, required=False)
    pacing_narrative_style = forms.CharField(max_length=80, required=False)

    action = forms.CharField(widget=forms.HiddenInput(), initial='by_answers')

    