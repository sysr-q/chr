# -*- coding: utf-8 -*-
""" Borrowed this from werkzeug commits since it's not on PyPI yet:
    https://github.com/mitsuhiko/werkzeug/commit/cdf680222af293a2c118d8d52eecfd7b0c566e14
"""

class ProxyFix(object):
    """This middleware can be applied to add HTTP proxy support to an
    application that was not designed with HTTP proxies in mind. It
    sets `REMOTE_ADDR`, `HTTP_HOST` from `X-Forwarded` headers.

    If you have more than one proxy server in front of your app, set
    `num_proxies` accordingly.

    Do not use this middleware in non-proxy setups for security reasons.

    The original values of `REMOTE_ADDR` and `HTTP_HOST` are stored in
    the WSGI environment as `werkzeug.proxy_fix.orig_remote_addr` and
    `werkzeug.proxy_fix.orig_http_host`.

    :param app: the WSGI application
    :param num_proxies: the number of proxy servers in front of the app.
    """

    def __init__(self, app, num_proxies=1):
        self.app = app
        self.num_proxies = num_proxies

    def get_remote_addr(self, forwarded_for):
        """Selects the new remote addr from the given list of ips in
        X-Forwarded-For. By default it picks the one that the `num_proxies`
        proxy server provides. Before 0.9 it would always pick the first.

        .. versionadded:: 0.8
        """
        if len(forwarded_for) >= self.num_proxies:
            return forwarded_for[-1 * self.num_proxies]

    def __call__(self, environ, start_response):
        getter = environ.get
        forwarded_proto = getter('HTTP_X_FORWARDED_PROTO', '')
        forwarded_for = getter('HTTP_X_FORWARDED_FOR', '').split(',')
        forwarded_host = getter('HTTP_X_FORWARDED_HOST', '')
        environ.update({
            'werkzeug.proxy_fix.orig_wsgi_url_scheme': getter('wsgi.url_scheme'),
            'werkzeug.proxy_fix.orig_remote_addr': getter('REMOTE_ADDR'),
            'werkzeug.proxy_fix.orig_http_host': getter('HTTP_HOST')
        })
        forwarded_for = [x for x in [x.strip() for x in forwarded_for] if x]
        remote_addr = self.get_remote_addr(forwarded_for)
        if remote_addr is not None:
            environ['REMOTE_ADDR'] = remote_addr
        if forwarded_host:
            environ['HTTP_HOST'] = forwarded_host
        if forwarded_proto:
            environ['wsgi.url_scheme'] = forwarded_proto
        return self.app(environ, start_response)
