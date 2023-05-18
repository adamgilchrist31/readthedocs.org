import functools

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect


def redirect_if_organization_unspecified(dispatch):
    """
    It is possible to share a URL to an organization page without specifying the organization slug.

    This decorates the dispatch() method of Class Based Views operating on the Organization model.

    In case the slug is specified as "_", we do the following:

    1. Check if there is only 1 organization available and redirect to this one
    2. Redirect to an "organization chooser", where the user will pick from a list of organizations.
    """

    @functools.wraps(dispatch)
    def inner(cbv_object, *args, **kwargs):
        slug = cbv_object.kwargs.get("slug", "_")
        if slug == "_":
            organizations = cbv_object.get_queryset()

            current_url_name = cbv_object.request.resolver_match.url_name
            current_url_kwargs = cbv_object.request.resolver_match.kwargs
            current_url_args = cbv_object.request.resolver_match.args

            # User controls exactly 1 organization, so we can redirect here.
            if organizations.count() == 1:
                current_url_kwargs["slug"] = organizations.first().slug
                return redirect(
                    current_url_name, *current_url_args, **current_url_kwargs
                )

            # TODO: Otherwise, here, we're going to redirect to a page where the user can
            # choose the organization.

        return dispatch(cbv_object, *args, **kwargs)

    return inner


def redirect_if_organizations_disabled(dispatch):
    """
    Return 404 if organizations aren't enabled.

    All organization views should decorate their view functions with this.

    The reason for implementing it this way is that
    the organization urls cannot be added conditionally on readthedocs/urls.py,
    as the file is evaluated only once, not per-test case.
    """

    @functools.wraps(dispatch)
    def inner(*args, **kwargs):
        if not settings.RTD_ALLOW_ORGANIZATIONS:
            raise Http404
        return dispatch(*args, **kwargs)

    return inner
