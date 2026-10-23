from eqar_backend.admin import admin_site, DEQARModelAdmin
from lists.models import Language, QFEHEALevel, Association, EQARDecisionType, IdentifierResource, \
    CrossBorderPossibility, CrossBorderApproval, CrossBorderRequirement, CrossBorderCriteria, CrossBorderDecision, \
    EuropeanApproachPossibility, TnePossible, TneApprovalOutgoing, TneQaOutgoing, TneOriginGroup, TneApprovalIncoming, \
    TneQaIncoming, McQa


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
    def get_readonly_fields(self, request, obj):
        if obj:
            return ['resource']
        else:
            return []


class ControlledListAdmin(DEQARModelAdmin):
    list_display = ('id', 'title', 'uri')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    fields = ('title', 'uri', 'description')

admin_site.register(Language, LanguageAdmin)
admin_site.register(QFEHEALevel, QFEHEALevelAdmin)
admin_site.register(Association, AssociationAdmin)
admin_site.register(EQARDecisionType, EQARDecisionTypeAdmin)
admin_site.register(IdentifierResource, IdentifierResourceAdmin)

for controlled_list in (CrossBorderPossibility, CrossBorderApproval, CrossBorderRequirement, CrossBorderCriteria,
                        CrossBorderDecision, EuropeanApproachPossibility, TnePossible, TneApprovalOutgoing,
                        TneQaOutgoing, TneOriginGroup, TneApprovalIncoming, TneQaIncoming, McQa):
    admin_site.register(controlled_list, ControlledListAdmin)
