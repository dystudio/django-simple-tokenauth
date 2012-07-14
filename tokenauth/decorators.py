# coding=utf-8
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs
from functools import wraps
from propane.datastructures import CaseInsensitiveDict
from urlparse import parse_qs

def token_required(view_func):
    """
    A view decorator that checks the query string parameters of a request for resource IDs and access tokens,
    extracts them, and authenticates the user if needed.
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'GET':
            qsp = parse_qs(request.META['QUERY_STRING'], keep_blank_values=True)
            qsp = CaseInsensitiveDict(qsp)
            kw = CaseInsensitiveDict(kwargs)
            try:
                provided_token = qsp['access_token'][0]
                if 'id' in kw.keys():
                    resource_id = kw['id']
                elif 'file_id' in kw.keys():
                    resource_id = kw['file_id']
                elif 'resource_id' in kw.keys():
                    resource_id = kw['resource_id']
                else:
                    return HttpResponseForbidden()
            except KeyError:
                return HttpResponseForbidden()

            user = authenticate(access_token=provided_token, resource_id=resource_id)
            if user:
                login(request, user)
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()

    return _wrapped_view
