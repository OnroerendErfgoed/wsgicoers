# -*- encoding: utf-8 -*-
#
# This file is part of wsgicors
#
# wsgicors is a WSGI middleware that answers CORS preflight requests
#
# copyright 2014-2015 Norman Krämer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from webob import Request
from webob import Response
from wsgicoers import make_middleware as mw


deny = {"policy": "deny"}

free = {
    "policy": "pol",
    "pol_origin": "*",
    "pol_methods": "*",
    "pol_headers": "*",
    "pol_expose_headers": "*",
    "pol_credentials": "true",
    "pol_maxage": "100",
}

multi = {
    "policy": "pol2,pol1",
    "pol1_origin": "*",
    "pol1_methods": "*",
    "pol1_headers": "*",
    "pol1_expose_headers": "*",
    "pol1_credentials": "true",
    "pol1_maxage": "100",
    "pol2_origin": "*.woopy.com",
    "pol2_methods": "*",
    "pol2_headers": "*",
    "pol2_expose_headers": "*",
    "pol2_credentials": "true",
    "pol2_maxage": "100",
}

preflight_headers = {
    "REQUEST_METHOD": "OPTIONS",
    "Access-Control-Request-Method": "*",
    "Origin": "localhost",
}
request_headers = {
    "REQUEST_METHOD": "GET",
    "Access-Control-Request-Method": "*",
    "Origin": "localhost",
}


def getRequestHeaderName(k):
    if k == "ORIGIN":
        return "Origin"
    elif k == "METHOD":
        return "Access-Control-Request-Method"
    elif k == "HEADERS":
        return "Access-Control-Request-Headers"
    else:
        return k


def prepRequest(hdr, **kw):
    req = Request.blank("/")
    req.method = "GET" if "REQUEST_METHOD" not in hdr else hdr["REQUEST_METHOD"]

    for k, v in hdr.items():
        if k != "REQUEST_METHOD":
            req.headers[k] = v

    for k, v in kw.items():
        k = getRequestHeaderName(k)
        req.headers[k] = v

    return req


class TestWSGICoers:
    """Test the WSGIcoers CORS middleware"""

    def test_policy_selection_firstmatch(self):
        """Check whether correct policy is returned"""
        multi2 = multi.copy()
        multi2["policy"] = "pol2,pol1"
        multi2["matchstrategy"] = "firstmatch"
        corsed = mw(Response("this is not a preflight response"), multi2)

        policyname, ret_origin = corsed.selectPolicy("palim.woopy.com")
        assert policyname == "pol2", (
            "'pol2' should have been returned since "
            "it matches first (but result was: '%s')" % policyname
        )
        assert ret_origin == "palim.woopy.com", (
            "'palim.woopy.com' expected since its "
            "matched by pol2 (but result was: '%s')" % ret_origin
        )

        policyname, ret_origin = corsed.selectPolicy("palim.com")
        assert policyname == "pol1", (
            "'pol1' should have been returned since "
            "it matches first (but result was: '%s')" % policyname
        )
        assert ret_origin == "*", (
            "'*' expected since its matched by"
            " pol1 (but result was: '%s')" % ret_origin
        )

    def test_deny_policy(self):
        """Denied policy should not return CORS headers"""
        corsed = mw(Response("non preflight"), deny)
        preflight = prepRequest(preflight_headers)
        res = preflight.get_response(corsed)
        assert res.body.decode("utf-8") == "", (
            "Body must be empty but was:%s" % res.body
        )
        assert (
            "Access-Control-Allow-Origin" not in res.headers
        ), "Header should not be in response"
        assert (
            "Access-Control-Allow-Credentials" not in res.headers
        ), "Header should not be in response"
        assert (
            "Access-Control-Allow-Methods" not in res.headers
        ), "Header should not be in response"
        assert (
            "Access-Control-Allow-Headers" not in res.headers
        ), "Header should not be in response"
        assert (
            "Access-Control-Max-Age" not in res.headers
        ), "Header should not be in response"
        assert (
            "Access-Control-Expose-Headers" not in res.headers
        ), "Header should not be in response"

    @pytest.mark.parametrize(
        "drop_header", ["REQUEST_METHOD", "Access-Control-Request-Method", "Origin"]
    )
    def test_non_preflight_are_not_answered(self, drop_header):
        """Requests that don't match preflight criteria are ignored"""
        corsed = mw(Response("this is not a preflight response"), free)

        hdr = preflight_headers.copy()
        del hdr[drop_header]

        req = prepRequest(hdr)
        res = req.get_response(corsed)
        assert res.body.decode("utf-8") == "this is not a preflight response", (
            "No preflight should have been detected (body was: '%s')" % res.body
        )

    def test_origin_policy_wildcard(self):
        """Test origin policy with wildcard"""
        policy = free.copy()
        policy["pol_origin"] = "*"

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers, ORIGIN="localhost")
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Allow-Origin") == "*"

    def test_origin_policy_copy(self):
        """Test origin policy with copy"""
        policy = free.copy()
        policy["pol_origin"] = "copy"

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers, ORIGIN="localhost")
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Allow-Origin") == "localhost"

    def test_method_policy_wildcard(self):
        """Test method policy with wildcard"""
        policy = free.copy()
        policy["pol_methods"] = "*"

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers, METHOD="PUT")
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Allow-Methods") == "PUT"

    def test_method_policy_fixed(self):
        """Test method policy with fixed values"""
        policy = free.copy()
        policy["pol_methods"] = "PUT, GET"

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers, METHOD="PUT")
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Allow-Methods") == "PUT, GET"

    def test_headers_policy_wildcard(self):
        """Test headers policy with wildcard"""
        policy = free.copy()
        policy["pol_headers"] = "*"

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers, HEADERS="X-Custom-Header")
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Allow-Headers") == "X-Custom-Header"

    def test_credentials_policy_true(self):
        """Test credentials policy set to true"""
        policy = free.copy()
        policy["pol_credentials"] = "true"
        policy["pol_origin"] = "copy"  # Need specific origin for credentials

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers, ORIGIN="localhost")
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Allow-Credentials") == "true"

    def test_max_age_policy(self):
        """Test max age policy"""
        policy = free.copy()
        policy["pol_maxage"] = "300"

        corsed = mw(Response("non preflight response"), policy)

        # Test preflight request
        req = prepRequest(preflight_headers)
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Max-Age") == "300"

    def test_expose_headers_policy(self):
        """Test expose headers policy"""
        policy = free.copy()
        policy["pol_expose_headers"] = "X-Custom-Header"

        corsed = mw(Response("non preflight response"), policy)

        # Test actual request (not preflight)
        req = prepRequest(request_headers)
        res = req.get_response(corsed)
        assert res.headers.get("Access-Control-Expose-Headers") == "X-Custom-Header"

    def test_vary_header_on_get(self):
        """Test that Vary: Accept header is set on GET requests"""
        policy = free.copy()

        corsed = mw(Response("get response"), policy)

        # Test GET request
        req = prepRequest({"REQUEST_METHOD": "GET", "Origin": "localhost"})
        res = req.get_response(corsed)
        assert "Accept" in res.headers.get("Vary", "")
