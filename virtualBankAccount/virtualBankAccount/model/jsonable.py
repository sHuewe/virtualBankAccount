class jsonable:
    def toJsonData(self):
        return dict(vars(self))

    def toDisplayData(self):
        return self.toJsonData()