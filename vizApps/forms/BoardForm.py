from django import forms
import json

class boardForm(forms.Form):
    attrs = {'class': 'special', 'size': '40'}
    jsonfield = forms.CharField()

    def clean_jsonfield(self):
        jdata = self.cleaned_data['jsonfield']
        try:
            json_data = json.loads(jdata)  # loads string as json
            # validate json_data
        except:
            raise forms.ValidationError("Invalid data in jsonfield")
        # if json data not valid:
        # raise forms.ValidationError("Invalid data in jsonfield")
        return jdata