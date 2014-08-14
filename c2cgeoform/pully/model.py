from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    Date,
    ForeignKey
    )
from sqlalchemy.orm import relationship
import geoalchemy2

import colander
import deform
from pkg_resources import resource_filename
from translationstring import TranslationStringFactory

from c2cgeoform.schema import register_schema
from c2cgeoform.ext import colander_ext, deform_ext
from c2cgeoform.models import Base
from c2cgeoform import default_search_paths

_ = TranslationStringFactory('pully')


class District(Base):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class ContactPerson(Base):
    __tablename__ = 'contact_person'
    __colanderalchemy_config__ = {
        'title':
            _('Contact Person')
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})
    firstName = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('First name')
        }})
    lastName = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Last name')
        }})
    permissionId = Column(Integer, ForeignKey('excavations.id'), info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})


class ExcavationPermission(Base):
    __tablename__ = 'excavations'
    __colanderalchemy_config__ = {
        'title':
            _('Application form for permission to carry out excavation work')
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'title': _('Permission Number'),
            'widget': deform.widget.HiddenWidget()
        }})
    referenceNumber = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Reference Number'),
            'admin_only': True
        }})
    requestDate = Column(Date, nullable=True, info={
        'colanderalchemy': {
            'title': _('Request Date')
        }})

    description = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Description of the Work'),
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    motif = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Motive for the Work'),
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    contactPersons = relationship(
        ContactPerson,
        # make sure persons are deleted when removed from the relation
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': _('Contact Persons')
            }})
    locationDistrictId = Column(Integer, ForeignKey('district.id'), info={
        'colanderalchemy': {
            'title': _('District'),
            'widget': deform_ext.RelationSelect2Widget(
                District,
                'id',
                # for i18n create columns like 'name_fr' in 'District'
                # and set these column names in the translation files. then use
                # the label `_('name'))` instead of `name`.
                'name',
                order_by='name',
                default_value=('', _('- Select -')),
            )
        }})
    locationStreet = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Street')
        }})
    locationPostalCode = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Postal Code')
        }})
    locationTown = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Town')
        }})
    locationPosition = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True), info={
            'colanderalchemy': {
                'title': _('Position'),
                'typ':
                    colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})

    # Person in Charge for the Work
    responsibleTitle = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Title'),
            'validator': colander.OneOf(['mr', 'mrs']),
            'widget': deform.widget.SelectWidget(values=(
                ('', _('- Select -')),
                ('mr', _('Mr.')),
                ('mrs', _('Mrs.'))
            ))
        }})
    responsibleName = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Name')
        }})
    responsiblefFirstName = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('First Name')
        }})
    responsiblefMobile = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Mobile Phone')
        }})
    responsiblefMail = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Mail'),
            'validator': colander.Email()
        }})
    responsiblefCompany = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Company')
        }})

    validated = Column(Boolean, info={
        'colanderalchemy': {
            'title': _('Validation'),
            'label': _('Validated'),
            'admin_only': True
        }})


# overwrite the form template for the user view
pully_templates = resource_filename('c2cgeoform', 'pully/templates')
templates_user = (pully_templates,) + default_search_paths

register_schema(
    'fouille',
    ExcavationPermission,
    templates_user=templates_user
    )


def setup_test_data():
    from c2cgeoform.models import DBSession
    import transaction

    if DBSession.query(District).get(0) is not None:
        return

    DBSession.add(District(id=0, name="Pully"))
    DBSession.add(District(id=1, name="Paudex"))
    DBSession.add(District(id=2, name="Belmont-sur-Lausanne"))
    DBSession.add(District(id=3, name="Trois-Chasseurs"))
    DBSession.add(District(id=4, name="La Claie-aux-Moines"))
    DBSession.add(District(id=5, name="Savigny"))
    DBSession.add(District(id=6, name="Mollie-Margot"))

    transaction.commit()
