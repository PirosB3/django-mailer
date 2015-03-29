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
        fields = ('sender', 'receiver', 'snippet',)
        model = Message
        widgets = {
            'sender': forms.Textarea(attrs={'cols': 20, 'rows': 2}),
            'receiver': forms.Textarea(attrs={'cols': 20, 'rows': 2}),
            'snippet': forms.Textarea(attrs={'cols': 80, 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(MessageInlineForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for field_name in self._meta.fields:
                if field_name is 'thread':
                    continue
                self.fields[field_name].widget.attrs['readonly'] = True
