from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    sender = forms.EmailField()
    receiver = forms.EmailField()
    body = forms.Textarea()

    class Meta:
        fields = ('sender', 'receiver', 'body',)
        model = Message

class MessageInlineForm(forms.ModelForm):
    sender = forms.EmailField()
    receiver = forms.EmailField()

    class Meta:
        fields = ('sender', 'receiver', 'body',)
        model = Message
        widgets = {
            'sender': forms.Textarea(attrs={'cols': 20, 'rows': 2}),
            'receiver': forms.Textarea(attrs={'cols': 20, 'rows': 2}),
            'body': forms.Textarea(attrs={'cols': 80, 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super(MessageInlineForm, self).clean()
        if self.instance and self.instance.id is not None:
            for key in ['sender', 'receiver']:
                try:
                    del self.errors[key]
                except KeyError:
                    pass
        return cleaned_data
