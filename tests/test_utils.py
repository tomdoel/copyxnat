# coding=utf-8

"""utils tests"""

from copyxnat.xnat_backend.xnat_session import Utils


class TestUtils(object):
    def test_combine_dicts(self):
        d1 = {'aa': 'blue', 'bc': 'red', 'efg': 'green1'}
        d2 = {'jik': 'magenta', 'pok': 'grey'}
        d3 = {'hi': 'yellow'}
        d1_d2 = {'aa': 'blue', 'bc': 'red', 'efg': 'green1', 'jik': 'magenta',
                 'pok': 'grey'}
        d1_d3 = {'aa': 'blue', 'bc': 'red', 'efg': 'green1', 'hi': 'yellow'}

        assert Utils.combine_dicts(None, None) == {}
        assert Utils.combine_dicts(None, {}) == {}
        assert Utils.combine_dicts({}, None) == {}
        assert Utils.combine_dicts(None, d1) == d1
        assert Utils.combine_dicts(d1, None) == d1
        assert Utils.combine_dicts(d1, {}) == d1
        assert Utils.combine_dicts({}, d1) == d1
        assert Utils.combine_dicts(d1, d2) == d1_d2
        assert Utils.combine_dicts(d1, d3) == d1_d3

    def test_optional_params(self):
        assert Utils.optional_params({}) == {}
        assert Utils.optional_params({'aa': 'blu', 'bc': 'red', 'efg': 'grn1'})\
               == {'aa': 'blu', 'bc': 'red', 'efg': 'grn1'}
        assert Utils.optional_params({'aa': None, 'bc': 'red', 'efg': 'grn1'})\
               == {'bc': 'red', 'efg': 'grn1'}
        assert Utils.optional_params({'aa': 'blu', 'bc': None, 'efg': None})\
               == {'aa': 'blu'}
        assert Utils.optional_params({'aa': None, 'bc': None, 'efg': None})\
               == {}
