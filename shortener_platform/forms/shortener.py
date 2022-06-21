from django import forms

from shortener_platform.models import Link


class LinkForm(forms.ModelForm):
    url = forms.URLField(widget=forms.URLInput(attrs={'required': True, 'placeholder': 'Enter URL to Shorten'}))

    class Meta:
        model = Link
        fields = ['url']

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
