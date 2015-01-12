"""
XPath selectors based on lxml
"""
from ants.utils.deprecate import create_deprecated_class
from .unified import Selector, SelectorList


__all__ = ['HtmlXPathSelector', 'XmlXPathSelector', 'XPathSelector',
           'XPathSelectorList']

def _xpathselector_css(self, *a, **kw):
    raise RuntimeError('.css() method not available for %s, '
                        'instantiate ants.Selector '
                        'instead' % type(self).__name__)

XPathSelector = create_deprecated_class(
    'XPathSelector',
    Selector,
    {
        '__slots__': (),
        '_default_type': 'html',
        'css': _xpathselector_css,
    },
    new_class_path='ants.Selector',
    old_class_path='ants.selector.XPathSelector',
)

XmlXPathSelector = create_deprecated_class(
    'XmlXPathSelector',
    XPathSelector,
    clsdict={
        '__slots__': (),
        '_default_type': 'xml',
    },
    new_class_path='ants.Selector',
    old_class_path='ants.selector.XmlXPathSelector',
)

HtmlXPathSelector = create_deprecated_class(
    'HtmlXPathSelector',
    XPathSelector,
    clsdict={
        '__slots__': (),
        '_default_type': 'html',
    },
    new_class_path='ants.Selector',
    old_class_path='ants.selector.HtmlXPathSelector',
)

XPathSelectorList = create_deprecated_class('XPathSelectorList', SelectorList)
