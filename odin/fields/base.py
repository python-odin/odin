
class BaseField(object):
    # These track each time an instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, verbose_name=None, verbose_name_plural=None, name=None, doc_text=''):
        self.verbose_name, self.verbose_name_plural = verbose_name, verbose_name_plural
        self.name = name
        self.doc_text = doc_text

        self.creation_counter = BaseField.creation_counter
        BaseField.creation_counter += 1

    def __hash__(self):
        return self.creation_counter

    def __repr__(self):
        """
        Displays the module, class and name of the field.
        """
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, 'name', None)
        if name is not None:
            return '<%s: %s>' % (path, name)
        return '<%s>' % path

    def set_attributes_from_name(self, attname):
        if not self.name:
            self.name = attname
        self.attname = attname
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')
        if self.verbose_name_plural is None and self.verbose_name:
            self.verbose_name_plural = "%ss" % self.verbose_name
