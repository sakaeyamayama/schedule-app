import re
from django import template

register = template.Library()

_PHASE_LABELS = ['設計', '製造', 'レビュー', 'テスト', 'その他']
_STRIP_RE = re.compile(
    r'^(?:' + '|'.join(re.escape(l) for l in _PHASE_LABELS) + r')[：: 　\-/_\s]+'
)


@register.filter
def strip_phase(name):
    return _STRIP_RE.sub('', name).strip()
