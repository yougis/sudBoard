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

admin.site.register(VizEntity, VizEntityAdmin)


class TraceEntityAdmin(admin.ModelAdmin):
    list_display = ('name','dataConnectorParam','board','get_vizListe')

    def get_vizListe(self, obj):
        return ";\n".join([v.title for v in obj.vizListe.all()])


admin.site.register(TraceEntity,TraceEntityAdmin)
