#!/usr/bin/python
# -*- coding: utf-8 -*-

from json import dumps

from django.conf import settings
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseNotFound

from models import AlbumProxy, PhotoProxy, Photo

DEFAULT_USER_WALL = getattr(settings, "DEFAULT_USER_WALL", "heynemann")

def load_username(func):
    def _load_username(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            username = DEFAULT_USER_WALL
        else:
            username = request.user.email.split('@')[0]
        kwargs['username'] = kwargs.get('username', username)
        return func(*args, **kwargs)
    return _load_username

@load_username
def index(request, username=None):
    return render(request, 'wall/index.html', {'username': username})

@load_username
def albums(request, username=None, extension="json"):
    data = []
    for album in AlbumProxy.objects.load(username):
        album_data = {
            'identifier': album.identifier,
            'url': album.url,
            'title': album.title,
            'photos': []
        }
        for photo in PhotoProxy.objects.load(album):
            album_data['photos'].append({
                'url': photo.url,
                'title': photo.title,
                'thumbnail': photo.thumbnail,
                'width': photo.width,
                'height': photo.height
            })
        data.append(album_data)
    data = dumps(data)

    if extension == "json":
        return HttpResponse(data, mimetype="application/json")
    elif extension == "jsonp":
        return HttpResponse('albums_loaded(%s)' % data, mimetype="application/json")
    else:
        raise Http404

def show_photo(request, photo_id):
    return TemplateResponse(request, 'wall/photo.html', 
            {"photo": get_object_or_404(Photo, id=photo_id) })
