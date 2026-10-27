"""Parse JSON or the exact native Gemma argument wrapper observed at the class proxy.

This is data parsing, never evaluation. The compatibility path accepts exactly one
string field for one of two allowed tools; extra fields or trailing bytes fail.
"""
import json
import re

_NATIVE = re.compile(r'<\|tool_call>call:(search_knowledge|get_article)\{(query|article_id):<\|"\|>([^<>\x00-\x1f]{1,300})<\|"\|>\}<tool_call\|>')
_FIELDS = {'search_knowledge':'query', 'get_article':'article_id'}


def parse_arguments(raw: str, tool_name: str) -> tuple[dict, str]:
    try:
        value = json.loads(raw)
        if not isinstance(value,dict):
            raise ValueError('Tool arguments must be an object')
        return value, 'json'
    except json.JSONDecodeError:
        match = _NATIVE.fullmatch(raw)
        if not match or match[1] != tool_name or _FIELDS[match[1]] != match[2]:
            raise ValueError('Unrecognized native tool arguments') from None
        return {match[2]:match[3]}, 'gemma-native'
