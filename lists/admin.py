from eqar_backend.admin import admin_site, DEQARModelAdmin
from lists.models import Language, QFEHEALevel, Association, EQARDecisionType, IdentifierResource


class LanguageAdmin(DEQARModelAdmin):
    list_display = ('language_name_en', 'iso_639_1', 'iso_639_2')
    search_fields = ('language_name_en', 'iso_639_1', 'iso_639_2')


class QFEHEALevelAdmin(DEQARModelAdmin):
    pass


class AssociationAdmin(DEQARModelAdmin):
    pass


class EQARDecisionTypeAdmin(DEQARModelAdmin):
    pass


class IdentifierResourceAdmin(DEQARModelAdmin):
    pass


admin_site.register(Language, LanguageAdmin)
admin_site.register(QFEHEALevel, QFEHEALevelAdmin)
admin_site.register(Association, AssociationAdmin)
admin_site.register(EQARDecisionType, EQARDecisionTypeAdmin)
admin_site.register(IdentifierResource, IdentifierResourceAdmin)
