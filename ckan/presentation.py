import ckan.model as model


# Todo: Use ckan.forms here?

class RegisterPresenter(list):

    modelClass = None
    keyName = 'id'
    
    def __init__(self, entities):
        super(RegisterPresenter, self).__init__()
        self.entities = None
        entities_type = type(entities)
        if issubclass(entities_type, list):
            self.init_from_list(entities)
        else:
            raise Exception, "Can't init presenter with '%s': %s" % (
                entities_type, entity
            )

    def init_from_list(self, entities):
        self.entities = entities
        for e in entities:
            if issubclass(type(e), self.modelClass):
                self.append(self.get_entity_key(e))
            else:
                msg = "Entity %s is not a %s." % (e, self.modelClass)
                raise Exception, msg

    def get_entity_key(self, entity):
        return getattr(entity, self.keyName)


class TagRegisterPresenter(RegisterPresenter):

    modelClass = model.Tag
    keyName = 'name'


class PackageRegisterPresenter(RegisterPresenter):

    modelClass = model.Package
    keyName = 'name'


class EntityPresenter(dict):

    modelClass = None
    keyName = 'id'

    def __init__(self, entity, register=None):
        self.register = register
        self.entity = None
        entity_type = type(entity)
        if issubclass(entity_type, self.modelClass):
            self.init_from_model(entity)
        elif issubclass(entity_type, dict):
            self.init_from_request_data(entity)
        else:
            raise Exception, "Can't init presenter with '%s': %s" % (
                entity_type, entity
            )

    def init_from_model(self, entity):
        self.entity = entity

    def init_from_request_data(self, kwds):
        pass

    def as_constructor_kwds(self):
        kwds = {}
        return kwds

    def as_entity(self):
        if self.entity != None:
            pass
        elif self.is_update():
            self.update_entity()
        else:
            self.construct_entity()
        return self.entity

    def is_update(self):
        return self.keyName in self

    def construct_entity(self):
        kwds = self.as_constructor_kwds()
        self.entity = self.modelClass(**kwds)

    def update_entity(self):
        entity_key = self[self.keyName]
        kwds = {self.keyName: entity_key}
        if self.register != None:
            self.entity = self.register.get(entity_key)
        else:
            self.entity = self.modelClass.selectBy(**kwds)


class TagPresenter(EntityPresenter):

    modelClass = model.Tag
    keyName = 'name'

    def init_from_model(self, entity):
        super(TagPresenter, self).init_from_model(entity)
        self['name'] = entity.name

    def init_from_request_data(self, kwds):
        super(TagPresenter, self).init_from_request_data(kwds)
        self['name'] = kwds['name']

    def as_constructor_kwds(self):
        kwds = super(TagPresenter, self).as_constructor_kwds()
        kwds['name'] = self['name']
        return kwds

    def update_entity(self):
        super(TagPresenter, self).update_entity()
        if self.entity:
            self.entity.name = self['name']


class PackagePresenter(EntityPresenter):

    modelClass = model.Package
    keyName = 'name'

    def init_from_model(self, entity):
        super(PackagePresenter, self).init_from_model(entity)
        self['name'] = entity.name
        self['title'] = entity.title
        self['url'] = entity.url
        self['download_url'] = entity.download_url
        self['tags'] = [f.tag.name for f in entity.tags]

    def init_from_request_data(self, kwds):
        super(PackagePresenter, self).init_from_request_data(kwds)
        if 'name' in kwds:
            self['name'] = kwds['name']
        if 'title' in kwds:
            self['title'] = kwds['title']
        if 'url' in kwds:
            self['url'] = kwds['url']
        if 'download_url' in kwds:
            self['download_url'] = kwds['download_url']
        if 'tags' in kwds:
            self['tags'] = kwds['tags'][:]  # Take a copy.
    
    def as_constructor_kwds(self):
        kwds = super(PackagePresenter, self).as_constructor_kwds()
        if 'name' in kwds:
            kwds['name'] = self['name']
        if 'title' in kwds:
            kwds['title'] = self['title']
        if 'url' in kwds:
            kwds['url'] = self['url']
        if 'download_url' in kwds:
            kwds['download_url'] = self['download_url']
        if 'tags' in kwds:
            tags = [model.Tag.get(name) for name in self['tags']]
            kwds['tags'] = tags
        return kwds
    
    def update_entity(self):
        super(PackagePresenter, self).update_entity()
        if self.entity:
            if 'name' in self:
                self.entity.name = self['name']
            if 'title' in self:
                self.entity.title = self['title']
            if 'url' in self:
                self.entity.url = self['url']
            if 'download_url' in self:
                self.entity.download_url = self['download_url']
            if 'tags' in self:
                tags = [model.Tag.get(name) for name in self['tags']]
                self.entity.tags = tags

