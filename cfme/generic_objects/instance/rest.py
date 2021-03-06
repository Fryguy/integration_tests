# -*- coding: utf-8 -*-

from cfme.generic_objects.definition.associations import get_rest_resource
from cfme.generic_objects.instance import (
    GenericObjectInstance,
    GenericObjectInstanceCollection
)
from cfme.utils.appliance.implementations.rest import ViaREST
from cfme.utils.rest import assert_response, create_resource


def _get_associations_dict(appliance, associations, definition):
    assoc_dict = {}
    for key in associations:
        # association type, e.g. "Service"
        assoc_type = definition.associations[key]
        assoc_dict[key] = []
        for resource in associations[key]:
            # get the REST representation of the resource
            rest_resource = get_rest_resource(appliance, assoc_type, resource)[0]
            assoc_dict[key].append({'href': rest_resource.href})
    return assoc_dict


@GenericObjectInstanceCollection.create.external_implementation_for(ViaREST)
def create(self, name, definition, attributes=None, associations=None):
    definition_rest = self.appliance.rest_api.collections.generic_object_definitions.get(
        name=definition.name)

    body = {'name': name, 'generic_object_definition': {'href': definition_rest.href}}

    if attributes:
        body['property_attributes'] = attributes
    if associations:
        body['associations'] = _get_associations_dict(self.appliance, associations, definition)

    create_resource(self.appliance.rest_api, 'generic_objects', [body])
    assert_response(self.appliance)
    rest_response = self.appliance.rest_api.response

    entity = self.instantiate(
        name=name, definition=definition, attributes=attributes, associations=associations
    )
    entity.rest_response = rest_response
    return entity


@GenericObjectInstance.update.external_implementation_for(ViaREST)
def update(self, updates):
    instance = self.appliance.rest_api.collections.generic_objects.find_by(
        name=self.name)

    if not instance:
        self.rest_response = None
        return

    instance = instance[0]

    name = updates.get('name')
    attributes = updates.get('attributes')
    associations = updates.get('associations')

    body = {}
    if name:
        body['name'] = name
    if attributes:
        body['property_attributes'] = attributes
    if associations:
        body['associations'] = _get_associations_dict(self.appliance, associations, self.definition)

    instance.action.edit(**body)
    assert_response(self.appliance)
    self.rest_response = self.appliance.rest_api.response


@GenericObjectInstance.delete.external_implementation_for(ViaREST)
def delete(self):
    instance = self.appliance.rest_api.collections.generic_objects.find_by(
        name=self.name)

    if not instance:
        self.rest_response = None
        return

    instance = instance[0]
    instance.action.delete()
    assert_response(self.appliance)
    self.rest_response = self.appliance.rest_api.response


@GenericObjectInstance.exists.external_getter_implemented_for(ViaREST)
def exists(self):
    return bool(
        self.appliance.rest_api.collections.generic_objects.find_by(name=self.name))
