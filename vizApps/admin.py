from django.contrib import admin

from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
from vizApps.domain.Viz import VizEntity
from vizApps.domain.lumen.view import ViewEntity
from vizApps.domain.lumen.target import TargetEntity
from vizApps.domain.lumen.filter import FilterEntity
from vizApps.domain.lumen.transform import TransformEntity




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



class TargetEntityAdmin(admin.ModelAdmin):
    pass

admin.site.register(TargetEntity,TargetEntityAdmin)


class ViewEntityAdmin(admin.ModelAdmin):
    pass

admin.site.register(ViewEntity,ViewEntityAdmin)


class FilterEntityAdmin(admin.ModelAdmin):
    pass

admin.site.register(FilterEntity,FilterEntityAdmin)

class TransformEntityAdmin(admin.ModelAdmin):
    pass

admin.site.register(TransformEntity,TransformEntityAdmin)
