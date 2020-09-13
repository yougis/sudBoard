from django.contrib import admin

from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
from vizApps.domain.Viz import VizEntity


class BoardAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(BoardEntity, BoardAdmin)



class VizEntityAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    def save_model(self, request, obj, form, change):
        #VizEntity.objects.addVizAppInstance(obj.createVizAppFromJsonParameters(initSession=True))
       #if (obj._viz['vizApp'] == None):
       #    obj._viz['vizApp'] = obj.createVizFromJsonParameters(initSession=True)
        super().save_model(request, obj, form, change)

admin.site.register(VizEntity, VizEntityAdmin)


class TraceEntityAdmin(admin.ModelAdmin):
    list_display = ('name','dataConnectorParam')


admin.site.register(TraceEntity,TraceEntityAdmin)
