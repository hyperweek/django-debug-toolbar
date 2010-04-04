"""Requires pytidylib and optionally pygments"""
from debug_toolbar.panels import DebugPanel
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import escape
import logging
try:
    import tidylib
except:
    tidylib = None
import re

error_re = re.compile(r'line (?P<line>\d+) column (?P<column>\d+) - (?P<message>.*)\n')
content_type_re = re.compile(r'text\/html|application\/xhtml\+xml')

class ValidatorPanel(DebugPanel):
    has_content = True
    has_tiny_content = True
    name = 'Validator'
    
    def __init__(self):
        self.errors = []
        self.source = None
        
    def title(self):
        title = 'Validator'
        if self.errors:
            title += " (%s)" % len(self.errors)
        return title
    
    def nav_title(self):
        return self.title()

    def url(self):
        return ''

    def init_stats(self):
        self.source = self.response.content.decode('utf-8')
        if tidylib:
            document, errors = tidylib.tidy_document(self.source, options={'numeric-entities':1})
        else:
            errors = ""
        if errors:
            self.errors = [e.groupdict() for e in error_re.finditer(errors)]

    def tiny_content(self):
        self.init_stats()
        if self.errors:
            return "%s V" % len(self.errors)
        return ""
        
    def process_response(self, request, response):
        self.request = request
        self.response = response
        if not content_type_re.search(self.response['content-type']):
            return 
        self.init_stats()
            
    def content(self):
        try:
            from pygments import highlight
            from pygments.lexers import HtmlLexer
            from pygments.formatters import HtmlFormatter
            
            formatter = HtmlFormatter(linenos='inline', lineanchors='validator')
            self.source = highlight(self.source, HtmlLexer(), formatter)
            self.source += '<style>'
            self.source += HtmlFormatter().get_style_defs('.highlight')
            self.source += '</style>'
            
        except ImportError:
            self.source = '<pre>%s</pre>' % escape(self.source)
            
        self.source = mark_safe(self.source)
        context = { 'errors': self.errors, 'source': self.source }
        return render_to_string('debug_toolbar/panels/validator.html', context)
        
        
    
        
