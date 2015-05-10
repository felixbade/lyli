# -*- coding: utf-8 -*-

from urlparse import urlparse

from wtforms import Form, TextField, RadioField, ValidationError
from flask import g

from app import backend

def check_url(form, self):
    url = self.data
    if not url:
        g.notes['shortening'] = 'empty url'
        raise ValidationError(u'Tässä ei ole linkkiä.')
    parsed = urlparse(url)
    if not parsed.scheme in ['http', 'https']:
        g.notes['shortening'] = 'illegal scheme'
        raise ValidationError(u'Voit lyhentää vain http- ja https-linkkejä.')

def check_name(form, self):
    name = self.data

    #if name == 'kissa':
    if backend.exists(name):
        g.notes['shortening'] = 'name in use'
        raise ValidationError(u'lyli.fi/%s on jo käytössä.' % name)
    
    # TODO: control characters ('ohjausmerkkejä')
    forbidden_characters = {
            '.': u'pisteitä',
            '/': u'kauttaviivoja',
            '+': u'plussia',
            
            '%': u'prosenttimerkkejä',
            ' ': u'sanavälejä',
            '?': u'kysymysmerkkejä',
            '#': u'risuaitoja'
            }
    forbidden_characters_found = []
    for character in name:
        if character in forbidden_characters and character not in forbidden_characters_found:
            forbidden_characters_found.append(character)
    
    if forbidden_characters_found:
        g.notes['shortening'] = 'illegal name'
        forbidden_descriptions = [forbidden_characters[x] for x in forbidden_characters_found]
        raise ValidationError(u'Päätteessä ei saa olla %s.' % join_words(forbidden_descriptions))

def join_words(words):
    last = words.pop()
    if not words:
        return last
    else:
        return ', '.join(words) + u' eikä ' + last

duration_choices = [
        ('normal', u'Poista lyhennys kun sitä ei ole käytetty kahteen viikkoon'),
        ('brief', u'Poista lyhennys tunnin päästä'),
        ('once', u'Poista lyhennys ensimmäisen avauksen jälkeen')]

class ShorteningForm(Form):
    url = TextField('url', [check_url])
    #default_name
    name = TextField('name', [check_name])
    duration = RadioField('duration', choices=duration_choices, default='normal')
