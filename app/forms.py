# -*- coding: utf-8 -*-

from urllib.parse import urlparse

from wtforms import Form, TextField, RadioField, HiddenField, ValidationError
from flask import g

from app import backend
from app.urlshortener.url import encodeURL

def check_url(form, self):
    url = self.data
    if not url:
        g.notes['shortening'] = 'empty url'
        raise ValidationError(u'Tässä ei ole linkkiä.')
    if len(url) > 2000:
        g.notes['shortening'] = 'too long url'
        raise ValidationError(u'Liian pitkä linkki.')
    try:
        url = encodeURL(url)
    except:
        raise ValidationError(u'Linkissä on jotain outoa')
    parsed = urlparse(url)
    if not parsed.scheme in ['http', 'https']:
        g.notes['shortening'] = 'illegal scheme'
        raise ValidationError(u'Voit lyhentää vain http- ja https-linkkejä.')

def check_name(form, self):
    name = self.data

    if name == '':
        name = form._fields['default_name'].data # ugly

    if len(name) > 100:
        g.notes['shortening'] = 'too long name'
        raise ValidationError(u'Liian pitkä pääte.')

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
            '#': u'risuaitoja',
            '\\': u'kenoviivoja'
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
        ('normal', u'Poista lyhennys kun sitä ei ole käytetty kolmeen viikkoon'),
        ('brief', u'Poista lyhennys tunnin päästä'),
        ('once', u'Poista lyhennys ensimmäisen avauksen jälkeen')]

class ShorteningForm(Form):
    url = TextField('url', [check_url])
    default_name = HiddenField('default_name')
    name = TextField('name', [check_name])
    duration = RadioField('duration', choices=duration_choices, default='once')
