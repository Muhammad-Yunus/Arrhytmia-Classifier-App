from . import AdminIndexView, expose, redirect, url_for

# Home views
class MyHomeView(AdminIndexView):

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose('/')
    def index(self):
        
        return redirect(url_for('dashboard.index')) 