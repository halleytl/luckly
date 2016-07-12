class BaseEngine():

    def get_conn(self):
        pass

    def show(self, inf_name, **params):
        pass

    def search(self, inf_name, **params):
        pass

    def debug(self, inf_name, **params):
        return self.show(inf_name, **params)

    def struct(self, show_type, **kwargs):
        pass
