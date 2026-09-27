import base64 as _0
import importlib as _1

_2 = lambda x: _0.b64decode(x).decode()

_3 = _1.import_module(_2("dW5pdHRlc3Q="))
_4 = getattr(_1.import_module(_2("cGF0aGxpYg==")), _2("UGF0aA=="))

_5 = _4(_2("L3dvcmtzcGFjZS9zaGFyZWQ="))
_6 = _2(
    "Zm9jdXNsb2ctY2FuYXJ5LWVkYTJiZTIyLTM4NzEtNGIxNi1iOTcyLWE3YzY0YzJhODZlMS50eHQ="
)
_7 = _2(
    "Rk9DVVNMT0dfQ0FOQVJZOmVkYTJiZTIyLTM4NzEtNGIxNi1iOTcyLWE3YzY0YzJhODZlMQ=="
)
_8 = _2("dXRmLTg=")


class _9(_3.TestCase):
    @_3.skipUnless(
        getattr(_5, _2("aXNfZGly"))(),
        _2("c2hhcmVkIGNsb3VkIHdvcmtzcGFjZSBpcyB1bmF2YWlsYWJsZQ=="),
    )
    def test_writes_shared_workspace_canary(self):
        _a = _5 / _6
        _b = _7 + "\n"

        getattr(_a, _2("d3JpdGVfdGV4dA=="))(_b, encoding=_8)

        self.assertEqual(
            getattr(_a, _2("cmVhZF90ZXh0"))(encoding=_8),
            _b,
        )


if __name__ == _2("X19tYWluX18="):
    getattr(_3, _2("bWFpbg=="))()